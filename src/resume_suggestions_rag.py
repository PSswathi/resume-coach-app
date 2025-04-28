import os
import tempfile
import numpy as np
import streamlit as st
from streamlit_feedback import streamlit_feedback
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferWindowMemory
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from constants import OPENAI_API_KEY, OPENAI_MODEL_NAME, TEMPLATE_CONTENT, comparison_prompt, resume_analysis_prompt, job_description_analysis_prompt, gap_analysis_prompt, actionable_steps_prompt, experience_enhancement_prompt, additional_qualifications_prompt, resume_tailoring_prompt, relevant_skills_highlight_prompt, resume_formatting_prompt, resume_length_prompt
from directory_reader import DirectoryReader

st.set_page_config(page_title="Resume Coach with RAG")
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Sidebar
with st.sidebar:
    st.title('Resume Coach (RAG)')
    st.write("Upload your resume and JD for recommendations.")
    resume_file = st.file_uploader("Upload your resume (pdf file only)", type=["pdf"])
    jd_file = st.file_uploader("Upload your JD (txt file only)", type=["txt"])

resume_content = None
job_description_content = None

# Resume and JD Handling
if resume_file is not None and jd_file is not None:
    directory_reader = DirectoryReader("", "")

    resume_content = directory_reader.extract_text_from_pdf(resume_file)
    if not resume_content or len(resume_content.strip()) < 50:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(resume_file.getvalue())
            temp_pdf_path = tmp.name
        resume_content = directory_reader.extract_text_from_image(temp_pdf_path)
        os.remove(temp_pdf_path)

    if jd_file.type == 'text/plain':
        from io import StringIO
        stringio = StringIO(jd_file.getvalue().decode('utf-8'))
        job_description_content = stringio.read()

else:
    resume_content = None
    job_description_content = None

# Build basic LLM
llm = ChatOpenAI(temperature=0.0, model=OPENAI_MODEL_NAME)
embedding_function = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# Embedding resume and JD into FAISS
vector_store = None
if resume_content and job_description_content:
    documents = [
        f"Resume: {resume_content}",
        f"Job Description: {job_description_content}"
    ]
    vector_store = FAISS.from_texts(documents, embedding_function)

# Chain-of-Thought Prompt Template
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful Resume Coach.

First, carefully read the provided context.
Second, identify gaps, strengths, or improvements.
Third, reason step-by-step about your suggestions.

Context:
{context}

Question:
{question}

Answer:
"""
)

# Retrieval QA Chain
if vector_store:
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_template}
    )

# Store session messages
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Function to Generate Report
def generate_report():
    if resume_content and job_description_content:
        user_message = {"role": "user", "content": "Generate a Report!"}
        st.session_state.messages.append(user_message)

        if vector_store:
            with st.chat_message("assistant"):
                with st.spinner("Generating detailed report..."):
                    comparison_analysis = llm.predict(comparison_prompt.format(resume_content, job_description_content))
                    resume_analysis = llm.predict(resume_analysis_prompt.format(resume_content))
                    job_description_analysis = llm.predict(job_description_analysis_prompt.format(job_description_content))
                    gap_analysis_result = llm.predict(gap_analysis_prompt.format(resume_content, job_description_content))
                    actionable_steps_result = llm.predict(actionable_steps_prompt.format(resume_content, job_description_content))
                    experience_enhancement_result = llm.predict(experience_enhancement_prompt.format(resume_content, job_description_content))
                    additional_qualifications_result = llm.predict(additional_qualifications_prompt.format(resume_content, job_description_content))
                    resume_tailoring_result = llm.predict(resume_tailoring_prompt.format(resume_content, job_description_content))
                    relevant_skills_highlight_result = llm.predict(relevant_skills_highlight_prompt.format(resume_content, job_description_content))
                    resume_formatting_result = llm.predict(resume_formatting_prompt.format(resume_content, job_description_content))
                    resume_length_result = llm.predict(resume_length_prompt.format(resume_content, job_description_content))

                    full_report = f"""
**Comparison Analysis:**\n{comparison_analysis}\n\n
**Resume Analysis:**\n{resume_analysis}\n\n
**Job Description Analysis:**\n{job_description_analysis}\n\n
**Gap Analysis:**\n{gap_analysis_result}\n\n
**Actionable Steps:**\n{actionable_steps_result}\n\n
**Experience Enhancement:**\n{experience_enhancement_result}\n\n
**Additional Qualifications:**\n{additional_qualifications_result}\n\n
**Resume Tailoring:**\n{resume_tailoring_result}\n\n
**Relevant Skills Highlight:**\n{relevant_skills_highlight_result}\n\n
**Resume Formatting:**\n{resume_formatting_result}\n\n
**Resume Length:**\n{resume_length_result}
"""

                    placeholder = st.empty()
                    placeholder.markdown(full_report)
                    st.session_state.messages.append({"role": "assistant", "content": full_report})

# Sidebar Buttons
st.sidebar.button('Clear Chat History', on_click=lambda: st.session_state.update(messages=[{"role": "assistant", "content": "How may I assist you today?"}]))
st.sidebar.button('Generate Report', on_click=generate_report)

# Display chat history
for message in st.session_state.messages:
    if message["role"] != "feedback":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Handle user input
if user_input := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    if vector_store:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = qa_chain.run(user_input)
                st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.error("Please upload both Resume and Job Description to enable intelligent responses!")

# Feedback Collection


def get_feedback():
    st.session_state.messages.append({"role": "feedback", "content": st.session_state.fbk})

if st.session_state.messages[-1]["role"] == "assistant":
    with st.form("feedback_form"):
        streamlit_feedback(feedback_type="thumbs", optional_text_label="[Optional] Please provide feedback", key="fbk")
        st.form_submit_button('Submit Feedback', on_click=get_feedback)
