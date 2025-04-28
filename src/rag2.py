### Full Name : Swathi Subramanyam Pabbathi
### Email - Id : swanpsswathi@gmail.com
### Problem Statement : Project-5: Resume Coach - AI-Powered Job Application Coach using RAG implementation

import os
import tempfile
import numpy as np
import streamlit as st
from streamlit_feedback import streamlit_feedback
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from constants import OPENAI_API_KEY, OPENAI_MODEL_NAME, TEMPLATE_CONTENT, comparison_prompt, resume_analysis_prompt, job_description_analysis_prompt, gap_analysis_prompt, actionable_steps_prompt, experience_enhancement_prompt, additional_qualifications_prompt, resume_tailoring_prompt, relevant_skills_highlight_prompt, resume_formatting_prompt, resume_length_prompt, RESUME_EMBEDDINGS_FILENAME, JD_EMBEDDINGS_FILENAME
from directory_reader import DirectoryReader
from embedding_model import EmbeddingModel
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# Settings
st.set_page_config(page_title="Resume Coach with RAG")
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
JD_FOLDER_PATH = "jd_data/"  # Path where all your JD .txt files are

# Utility function to clean jd_name
def clean_jd_name(name):
    name = name.replace("\\", "/")
    if name.startswith("jd_data/"):
        name = name[len("jd_data/"):]
    return name

# Load embeddings
embedding_model = EmbeddingModel()
jd_embeddings = embedding_model.read_embeddings(JD_EMBEDDINGS_FILENAME)
resume_embeddings = embedding_model.read_embeddings(RESUME_EMBEDDINGS_FILENAME)

# Load JD text files into a dictionary {filename: content}
def load_jd_texts(jd_folder_path):
    jd_texts = {}
    for filename in os.listdir(jd_folder_path):
        if filename.endswith('.txt'):
            with open(os.path.join(jd_folder_path, filename), 'r', encoding='utf-8') as file:
                jd_texts[filename.replace('.txt', '')] = file.read()
    return jd_texts

jd_texts = load_jd_texts(JD_FOLDER_PATH)

# Sidebar - Upload resume
with st.sidebar:
    st.title('Resume Coach (RAG)')
    st.write("Upload your Resume (PDF). JD matching happens automatically.")
    resume_file = st.file_uploader("Upload your resume (pdf file only)", type=["pdf"])

resume_content = None

# Extract resume text
if resume_file is not None:
    directory_reader = DirectoryReader("", "")
    resume_content = directory_reader.extract_text_from_pdf(resume_file)
    if not resume_content or len(resume_content.strip()) < 50:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(resume_file.getvalue())
            temp_pdf_path = tmp.name
        resume_content = directory_reader.extract_text_from_image(temp_pdf_path)
        os.remove(temp_pdf_path)

# Build vector store
vector_store = None
top_k_jd_contents = []

if resume_content:
    # Embed uploaded resume
    uploaded_resume_embedding = embedding_model.embedding_model.embed_documents([resume_content])[0]

    # Find Top-K Matching JDs
    top_k = 3  # You can change Top K value here
    jd_scores = []

    for jd_name, jd_emb in jd_embeddings.items():
        score = cosine_similarity(
            np.array(uploaded_resume_embedding).reshape(1, -1),
            np.array(jd_emb).reshape(1, -1)
        )[0][0]
        jd_scores.append((jd_name, score))

    jd_scores = sorted(jd_scores, key=lambda x: x[1], reverse=True)
    top_k_jd_names = [name for name, _ in jd_scores[:top_k]]

    # Get JD contents
    for jd_name in top_k_jd_names:
        cleaned_jd_name = clean_jd_name(jd_name)
        if cleaned_jd_name in jd_texts:
            top_k_jd_contents.append(f"Job Description: {jd_texts[cleaned_jd_name]}")
        else:
            st.error(f"JD text not found for {cleaned_jd_name}")

    # Prepare documents for FAISS
    documents = [f"Resume: {resume_content}"] + top_k_jd_contents
    embedding_function = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vector_store = FAISS.from_texts(documents, embedding_function)

# Build LLM
llm = ChatOpenAI(temperature=0.0, model=OPENAI_MODEL_NAME)

# Prompt Template
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

# Build Retrieval QA Chain
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
    if resume_content and vector_store:
        user_message = {"role": "user", "content": "Generate a Report!"}
        st.session_state.messages.append(user_message)

        with st.chat_message("assistant"):
            with st.spinner("Generating detailed report..."):
                combined_context = "\n".join(top_k_jd_contents)
                comparison_analysis = llm.predict(comparison_prompt.format(resume_content, combined_context))
                resume_analysis = llm.predict(resume_analysis_prompt.format(resume_content))
                job_description_analysis = llm.predict(job_description_analysis_prompt.format(combined_context))
                gap_analysis_result = llm.predict(gap_analysis_prompt.format(resume_content, combined_context))
                actionable_steps_result = llm.predict(actionable_steps_prompt.format(resume_content, combined_context))
                experience_enhancement_result = llm.predict(experience_enhancement_prompt.format(resume_content, combined_context))
                additional_qualifications_result = llm.predict(additional_qualifications_prompt.format(resume_content, combined_context))
                resume_tailoring_result = llm.predict(resume_tailoring_prompt.format(resume_content, combined_context))
                relevant_skills_highlight_result = llm.predict(relevant_skills_highlight_prompt.format(resume_content, combined_context))
                resume_formatting_result = llm.predict(resume_formatting_prompt.format(resume_content, combined_context))
                resume_length_result = llm.predict(resume_length_prompt.format(resume_content, combined_context))

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
        st.error("Please upload Resume to proceed!")

# Feedback Collection
def get_feedback():
    st.session_state.messages.append({"role": "feedback", "content": st.session_state.fbk})

if st.session_state.messages[-1]["role"] == "assistant":
    with st.form("feedback_form"):
        streamlit_feedback(feedback_type="thumbs", optional_text_label="[Optional] Please provide feedback", key="fbk")
        st.form_submit_button('Submit Feedback', on_click=get_feedback)