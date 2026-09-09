# =============================================================================
# Module 14: Dockerfile - AI Email Intelligence Platform
# Fulfills Page 26-28 of docs_ai_email_classification.pdf
# =============================================================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Download required NLP models (spaCy small English model & NLTK resources)
RUN python -m spacy download en_core_web_sm && \
    python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('stopwords')"

# Copy models directory, static web UI, and application codebase
COPY models/ /app/models/
COPY static/ /app/static/
COPY *.py /app/
COPY README*.md /app/

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Healthcheck probe against FastAPI
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/health || exit 1

# Default command: launch the FastAPI REST API
CMD ["uvicorn", "app_api:app", "--host", "0.0.0.0", "--port", "8000"]
