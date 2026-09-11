# CogniMail AI — Cloud Production Deployment Package

CogniMail AI is an enterprise AI operations platform that provides autonomous inbound email triage, multi-class category and intent classification, sentiment and emotion analysis, priority and SLA prediction, entity extraction, executive summarization, and context-aware smart replies across 7 calibrated tones.

This repository package is **optimized for cloud platforms (Render.com, Railway, Hugging Face Spaces, Fly.io)**:
- **Lightweight (~24.5 MB total)**: Excludes multi-gigabyte training CSVs.
- **Pre-trained Model Artifacts**: Includes all 29 production models in `models/`.
- **Integrated Web Cockpit**: Modern HTML5/CSS3/JavaScript responsive interface served at `/`.
- **Memory Optimized**: Configured with `MALLOC_ARENA_MAX=2` and single-worker execution to run reliably within Render's free tier (<512 MB RAM).

---

## 🚀 1-Click Deploy to Render.com

### Method 1: Deploy with Blueprint (`render.yaml`) — Recommended

1. Push this directory to your GitHub account as a new repository (e.g., `cognimail-ai`).
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** in the top right and select **Blueprint**.
4. Connect your GitHub repository.
5. Render will automatically read `render.yaml` and configure:
   - **Service Name**: `cognimail-ai`
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt && python -m spacy download en_core_web_sm && python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"`
   - **Start Command**: `uvicorn app_api:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Environment Variable**: `MALLOC_ARENA_MAX=2`
6. Click **Apply**. Render will build and deploy your app. Within 2–3 minutes, you will get a live public URL (e.g., `https://cognimail-ai.onrender.com`).

---

### Method 2: Manual Web Service on Render

If you prefer configuring the Web Service manually:
1. On [Render](https://dashboard.render.com), click **New +** -> **Web Service**.
2. Select your repository.
3. Configure the following settings:
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm && python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
     ```
   - **Start Command**: 
     ```bash
     uvicorn app_api:app --host 0.0.0.0 --port $PORT --workers 1
     ```
   - **Instance Type**: `Free`
   - **Environment Variables**:
     - `PYTHON_VERSION` = `3.11.9`
     - `MALLOC_ARENA_MAX` = `2`
4. Click **Create Web Service**.

---

## 🌐 Live Web Cockpit & Endpoints

Once deployed, your service provides:

| Route | Description |
| :--- | :--- |
| `/` | **CogniMail AI Web Cockpit** (Interactive dashboard for triage, smart replies, history, and analytics) |
| `/docs` | **Swagger Interactive API Documentation** |
| `/redoc` | **ReDoc API Documentation** |
| `/api/health` | **System Health & Model Status Check** |
| `/api/email/process` | **Full 17-Step Unified AI Pipeline Inference** |
| `/api/history` | **Audit Vault Ticket History** |
| `/api/analytics` | **Live KPI Analytics & Category/Priority Breakdown** |
| `/api/governance/action` | **Human-in-the-Loop Review Audit Vault** |

---

## 💻 Local Execution

To run locally before pushing to the cloud:

```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"

# Launch Web Cockpit server
python run_web.py
```
Open [http://localhost:8000](http://localhost:8000) in your web browser.
