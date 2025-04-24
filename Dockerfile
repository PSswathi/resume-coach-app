# Official Python base image
FROM python:3.10-slim

# Install OS-level dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_HOME="/app" \
    PYTHONPATH="/app/src"

# Expose Streamlit default port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "src/resume_suggestions.py", "--server.port=8501", "--server.enableCORS=false"]
