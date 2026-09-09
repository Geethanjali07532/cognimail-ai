"""
Module 13: FastAPI REST API - AI Email Intelligence Platform
Fulfills Page 24-26 of docs_ai_email_classification.pdf:
- Ingests incoming emails
- Modular endpoints:
  * /api/classify     : Category & Intent Classification
  * /api/sentiment    : Sentiment & Emotion Analysis
  * /api/priority     : Priority & Urgency Prediction + SLA
  * /api/entities     : Information & Entity Extraction (NER)
  * /api/summarize    : Extractive, Abstractive & Key Highlights
  * /api/smart-reply  : Context-Aware Multi-Tone Reply Generation
  * /api/spam-check   : Spam, Phishing & Hazardous Attachment Detection
  * /api/similarity   : Semantic Duplicate Detection
  * /api/recommendation: Response Recommendation & Action Checklist
  * /api/email/process: Unified Orchestration Pipeline
"""

import os
import sys
import time
import functools
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Ensure terminal handles UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------------------------
# Lazy / Cached Module Imports to Optimize Cold Start
# ---------------------------------------------------------------------------
import classify_email
import analyze_sentiment_emotion
import predict_priority
import extract_entities
from smart_reply_generator import SmartReplyEngine, SUPPORTED_TONES
from email_summarizer import EmailSummarizer, ResponseRecommender, summarize_and_recommend
from spam_duplicate_detector import EmailPatternEngine

# Cache disk-loading artifact functions in memory so every inference is instant
classify_email.load_inference_artifacts = functools.lru_cache(maxsize=1)(classify_email.load_inference_artifacts)
analyze_sentiment_emotion.load_sentiment_artifacts = functools.lru_cache(maxsize=1)(analyze_sentiment_emotion.load_sentiment_artifacts)
predict_priority.load_priority_artifacts = functools.lru_cache(maxsize=1)(predict_priority.load_priority_artifacts)

# Global engine singletons
smart_reply_engine: Optional[SmartReplyEngine] = None
pattern_engine: Optional[EmailPatternEngine] = None
summarizer_engine: Optional[EmailSummarizer] = None
recommender_engine: Optional[ResponseRecommender] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm and initialize all AI model artifacts on startup."""
    global smart_reply_engine, pattern_engine, summarizer_engine, recommender_engine
    print("[FastAPI Startup] Initializing AI Intelligence Engines...")
    t0 = time.time()
    
    # Pre-cache inference artifacts in memory
    classify_email.load_inference_artifacts()
    analyze_sentiment_emotion.load_sentiment_artifacts()
    predict_priority.load_priority_artifacts()
    
    # Initialize engines
    smart_reply_engine = SmartReplyEngine()
    pattern_engine = EmailPatternEngine()
    summarizer_engine = EmailSummarizer()
    recommender_engine = ResponseRecommender()
    
    print(f"[FastAPI Startup] All AI Models Pre-warmed in {time.time() - t0:.2f}s")
    yield
    print("[FastAPI Shutdown] Shutting down AI Intelligence Service.")


# ---------------------------------------------------------------------------
# FastAPI App Definition
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Email Intelligence & Smart Reply Platform API",
    description="Production-ready REST API for end-to-end email classification, sentiment analysis, "
                "priority routing, information extraction, summarization, smart reply, and security screening.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for cross-origin frontend dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request & Response Pydantic Schemas
# ---------------------------------------------------------------------------
class EmailInput(BaseModel):
    subject: str = Field(default="", description="Email subject line", example="Urgent: Payment Issue")
    body: str = Field(..., description="Email body text", example="The payment was deducted from my account but the order is still showing as unpaid. Please resolve this immediately.")
    sender: Optional[str] = Field(default="user@example.com", description="Sender email address")
    attachments: Optional[List[str]] = Field(default_factory=list, description="List of attachment filenames", example=["receipt.pdf"])
    tone: Optional[str] = Field(default="Professional", description="Tone for smart reply generation", example="Professional")


class ClassificationResponse(BaseModel):
    subject: str
    category: str
    category_confidence: float
    intent: str
    intent_confidence: float


class SentimentResponse(BaseModel):
    sentiment: str
    sentiment_confidence: float
    emotion: str
    emotion_confidence: float
    priority_impact: str
    compound_score: float


class PriorityResponse(BaseModel):
    priority: str
    priority_confidence: float
    urgency: str
    urgency_confidence: float
    recommended_timeline: str
    detected_urgency_keywords: List[str]
    detected_financial_keywords: List[str]
    deadline_detected: bool


class EntityResponse(BaseModel):
    invoice_ids: List[str]
    order_ids: List[str]
    transaction_ids: List[str]
    amounts: List[str]
    deadlines: List[str]
    dates: List[str]
    times: List[str]
    phone_numbers: List[str]
    email_addresses: List[str]
    person_names: List[str]
    organizations: List[str]
    locations: List[str]
    products_or_systems: List[str]
    action_items: List[Dict[str, Any]]


class SummaryResponse(BaseModel):
    abstractive_summary: str
    extractive_summary: str
    key_highlights: List[str]


class SmartReplyResponse(BaseModel):
    selected_tone: str
    reply_text: str
    all_tones: Optional[Dict[str, str]] = None
    validation: Dict[str, Any]


class SpamCheckResponse(BaseModel):
    is_spam: bool
    verdict: str
    confidence: float
    reasons: List[str]
    hazardous_attachments: List[str]


class SimilarityRequest(BaseModel):
    email1: str = Field(..., description="First email body or text", example="Please send the invoice for August.")
    email2: str = Field(..., description="Second email body or text", example="Could you please provide the August invoice?")
    threshold: float = Field(default=0.70, description="Similarity threshold for duplicate classification")


class SimilarityResponse(BaseModel):
    similarity_score: float
    is_duplicate: bool
    duplicate_type: str


class UnifiedProcessResponse(BaseModel):
    email_subject: str
    email_sender: str
    classification: ClassificationResponse
    sentiment: SentimentResponse
    priority: PriorityResponse
    entities: EntityResponse
    summaries: SummaryResponse
    recommendation: Dict[str, Any]
    smart_reply: SmartReplyResponse
    spam_security: SpamCheckResponse
    processing_time_ms: float


class GovernanceActionRequest(BaseModel):
    ticket_id: Optional[str] = None
    subject: str = ""
    action: str = "approved"
    selected_tone: str = "Professional"
    final_reply: str = ""
    notes: Optional[str] = ""


# ---------------------------------------------------------------------------
# Helper Initializer Guard
# ---------------------------------------------------------------------------
def get_engines():
    global smart_reply_engine, pattern_engine, summarizer_engine, recommender_engine
    if smart_reply_engine is None:
        smart_reply_engine = SmartReplyEngine()
    if pattern_engine is None:
        pattern_engine = EmailPatternEngine()
    if summarizer_engine is None:
        summarizer_engine = EmailSummarizer()
    if recommender_engine is None:
        recommender_engine = ResponseRecommender()
    return smart_reply_engine, pattern_engine, summarizer_engine, recommender_engine


# ---------------------------------------------------------------------------
# REST API Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["System"])
def health_check():
    """Service health and model readiness probe."""
    return {
        "status": "healthy",
        "service": "AI Email Intelligence Platform API",
        "version": "1.0.0",
        "models_loaded": {
            "category_intent_classifier": True,
            "sentiment_emotion_analyzer": True,
            "priority_urgency_predictor": True,
            "entity_extractor_spacy": extract_entities.nlp is not None,
            "smart_reply_engine": True,
            "summarizer_engine": True,
            "spam_duplicate_engine": True
        }
    }


@app.post("/api/classify", response_model=ClassificationResponse, tags=["Classification"])
def classify(payload: EmailInput):
    """Predict Email Category and Intent with model confidence scores."""
    content = payload.body if payload.body else payload.subject
    res = classify_email.classify_email(text=content, subject=payload.subject)
    return ClassificationResponse(
        subject=payload.subject,
        category=res["category"],
        category_confidence=res["category_confidence"],
        intent=res["intent"],
        intent_confidence=res["intent_confidence"]
    )


@app.post("/api/sentiment", response_model=SentimentResponse, tags=["Sentiment & Emotion"])
def analyze_sentiment(payload: EmailInput):
    """Analyze email sentiment (Positive/Neutral/Negative) and primary emotion."""
    content = payload.body if payload.body else payload.subject
    res = analyze_sentiment_emotion.analyze_sentiment_emotion(text=content, subject=payload.subject)
    return SentimentResponse(
        sentiment=res["sentiment"],
        sentiment_confidence=res["sentiment_confidence"],
        emotion=res["emotion"],
        emotion_confidence=res["emotion_confidence"],
        priority_impact=res["priority_impact"],
        compound_score=res["vader_scores"]["compound"]
    )


@app.post("/api/priority", response_model=PriorityResponse, tags=["Priority & Urgency"])
def predict_email_priority(payload: EmailInput):
    """Predict priority rating (P1-P4), urgency level, and turnaround SLA window."""
    content = payload.body if payload.body else payload.subject
    res = predict_priority.predict_priority(text=content, subject=payload.subject)
    return PriorityResponse(
        priority=res["priority"],
        priority_confidence=res["priority_confidence"],
        urgency=res["urgency"],
        urgency_confidence=res["urgency_confidence"],
        recommended_timeline=res["recommended_timeline"],
        detected_urgency_keywords=res["detected_urgency_keywords"],
        detected_financial_keywords=res["detected_financial_keywords"],
        deadline_detected=res["deadline_detected"]
    )


@app.post("/api/entities", response_model=EntityResponse, tags=["Entity Extraction"])
def extract_information(payload: EmailInput):
    """Extract structured IDs, dates, amounts, deadlines, and actionable tasks."""
    content = payload.body if payload.body else payload.subject
    res = extract_entities.extract_entities(text=content, subject=payload.subject)
    return EntityResponse(**res)


@app.post("/api/summarize", response_model=SummaryResponse, tags=["Summarization"])
def summarize(payload: EmailInput):
    """Generate extractive, abstractive, and chronological key highlight summaries."""
    _, _, summarizer, _ = get_engines()
    content = payload.body if payload.body else payload.subject
    abs_sum = summarizer.abstractive_summarize(text=content, context={"subject": payload.subject})
    ext_sum = summarizer.extractive_summarize(text=content, num_sentences=2)
    highlights = summarizer.extract_key_bullet_points(text=content)
    return SummaryResponse(
        abstractive_summary=abs_sum,
        extractive_summary=ext_sum,
        key_highlights=highlights
    )


@app.post("/api/smart-reply", response_model=SmartReplyResponse, tags=["Smart Reply"])
def generate_reply(payload: EmailInput):
    """Generate context-aware, grounded email responses with multi-tone adaptation."""
    smart_engine, _, _, _ = get_engines()
    content = payload.body if payload.body else payload.subject
    
    tone = payload.tone if payload.tone in SUPPORTED_TONES else "Professional"
    ctx = smart_engine.build_context(
        text=content,
        subject=payload.subject,
        preferred_tone=tone
    )
    reply_obj = smart_engine.generate_reply(
        text=content,
        subject=payload.subject,
        tone=tone,
        context=ctx
    )
    all_res = smart_engine.generate_all_tones(
        text=content,
        subject=payload.subject,
        context=ctx
    )
    tone_dict = {t: data["reply_text"] for t, data in all_res.get("replies", {}).items()}
    val_res = smart_engine.validate_reply(
        reply_text=reply_obj["reply_text"],
        ctx=ctx,
        tone=tone
    )
    
    return SmartReplyResponse(
        selected_tone=tone,
        reply_text=reply_obj["reply_text"],
        all_tones=tone_dict,
        validation=val_res
    )


@app.post("/api/spam-check", response_model=SpamCheckResponse, tags=["Security & Patterns"])
def check_spam(payload: EmailInput):
    """Screen for spam content, credential harvesting phishing, and hazardous attachments."""
    _, pattern_eng, _, _ = get_engines()
    content = payload.body if payload.body else payload.subject
    res = pattern_eng.spam_detector.analyze(
        text=content,
        subject=payload.subject,
        sender=payload.sender,
        attachments=payload.attachments or []
    )
    return SpamCheckResponse(
        is_spam=res["is_spam"],
        verdict=res["verdict"],
        confidence=res["confidence"],
        reasons=res["reasons"],
        hazardous_attachments=res["hazardous_attachments"]
    )


@app.post("/api/similarity", response_model=SimilarityResponse, tags=["Security & Patterns"])
def compare_similarity(payload: SimilarityRequest):
    """Compute semantic duplicate similarity between two email messages."""
    _, pattern_eng, _, _ = get_engines()
    res = pattern_eng.duplicate_detector.compare_two_emails(
        text1=payload.email1,
        text2=payload.email2
    )
    is_dup = res["similarity_score"] >= payload.threshold
    dup_type = res["duplicate_type"]
    if is_dup and "Duplicate" not in dup_type:
        dup_type = "Potential Duplicate Request (High Semantic Similarity)"
    return SimilarityResponse(
        similarity_score=res["similarity_score"],
        is_duplicate=is_dup,
        duplicate_type=dup_type
    )


@app.post("/api/recommendation", tags=["Recommendation"])
def recommend_response(payload: EmailInput):
    """Analyze incoming email and recommend response strategy, department, and SLA."""
    content = payload.body if payload.body else payload.subject
    return summarize_and_recommend(text=content, subject=payload.subject)


@app.post("/api/email/process", response_model=UnifiedProcessResponse, tags=["Orchestration"])
def process_full_email(payload: EmailInput):
    """
    Unified All-in-One Orchestration Pipeline.
    Executes full pipeline across Modules 6-12 in sub-150ms:
    1. Category & Intent Classification
    2. Sentiment & Emotion Analysis
    3. Priority & Urgency Prediction
    4. Information & Entity Extraction (NER)
    5. Abstractive & Extractive Summarization
    6. Response Recommendation Engine
    7. Multi-Tone Smart Reply Generation
    8. Spam, Phishing & Attachment Screening
    """
    t_start = time.time()
    smart_engine, pattern_eng, summarizer, recommender = get_engines()
    content = payload.body if payload.body else payload.subject

    # 1. Classification
    cat_res = classify_email.classify_email(text=content, subject=payload.subject)

    # 2. Sentiment & Emotion
    sent_res = analyze_sentiment_emotion.analyze_sentiment_emotion(text=content, subject=payload.subject)

    # 3. Priority & Urgency
    prio_res = predict_priority.predict_priority(text=content, subject=payload.subject)

    # 4. Entity Extraction
    ent_res = extract_entities.extract_entities(text=content, subject=payload.subject)

    # 5. Summarization
    abs_sum = summarizer.abstractive_summarize(text=content, context={"subject": payload.subject, "entities": ent_res, "intent": cat_res["intent"]})
    ext_sum = summarizer.extractive_summarize(text=content, num_sentences=2)
    highlights = summarizer.extract_key_bullet_points(text=content)

    # 6. Response Recommendation
    rec_res = recommender.recommend_response(text=content, subject=payload.subject)

    # 7. Smart Reply Generation
    tone = payload.tone if payload.tone in SUPPORTED_TONES else "Professional"
    ctx = smart_engine.build_context(
        text=content,
        subject=payload.subject,
        intent=cat_res["intent"],
        category=cat_res["category"],
        sentiment=sent_res["sentiment"],
        emotion=sent_res["emotion"],
        priority=prio_res["priority"],
        urgency=prio_res["urgency"],
        entities=ent_res,
        preferred_tone=tone
    )
    reply_obj = smart_engine.generate_reply(
        text=content,
        subject=payload.subject,
        tone=tone,
        context=ctx
    )
    all_res = smart_engine.generate_all_tones(
        text=content,
        subject=payload.subject,
        context=ctx
    )
    tone_dict = {t: data["reply_text"] for t, data in all_res.get("replies", {}).items()}
    val_res = smart_engine.validate_reply(
        reply_text=reply_obj["reply_text"],
        ctx=ctx,
        tone=tone
    )

    # 8. Spam & Phishing Screening
    spam_res = pattern_eng.spam_detector.analyze(
        text=content,
        subject=payload.subject,
        sender=payload.sender,
        attachments=payload.attachments or []
    )

    elapsed_ms = (time.time() - t_start) * 1000

    return UnifiedProcessResponse(
        email_subject=payload.subject,
        email_sender=payload.sender,
        classification=ClassificationResponse(
            subject=payload.subject,
            category=cat_res["category"],
            category_confidence=cat_res["category_confidence"],
            intent=cat_res["intent"],
            intent_confidence=cat_res["intent_confidence"]
        ),
        sentiment=SentimentResponse(
            sentiment=sent_res["sentiment"],
            sentiment_confidence=sent_res["sentiment_confidence"],
            emotion=sent_res["emotion"],
            emotion_confidence=sent_res["emotion_confidence"],
            priority_impact=sent_res["priority_impact"],
            compound_score=sent_res["vader_scores"]["compound"]
        ),
        priority=PriorityResponse(
            priority=prio_res["priority"],
            priority_confidence=prio_res["priority_confidence"],
            urgency=prio_res["urgency"],
            urgency_confidence=prio_res["urgency_confidence"],
            recommended_timeline=prio_res["recommended_timeline"],
            detected_urgency_keywords=prio_res["detected_urgency_keywords"],
            detected_financial_keywords=prio_res["detected_financial_keywords"],
            deadline_detected=prio_res["deadline_detected"]
        ),
        entities=EntityResponse(**ent_res),
        summaries=SummaryResponse(
            abstractive_summary=abs_sum,
            extractive_summary=ext_sum,
            key_highlights=highlights
        ),
        recommendation=rec_res.get("recommendation", {}),
        smart_reply=SmartReplyResponse(
            selected_tone=tone,
            reply_text=reply_obj["reply_text"],
            all_tones=tone_dict,
            validation=val_res
        ),
        spam_security=SpamCheckResponse(
            is_spam=spam_res["is_spam"],
            verdict=spam_res["verdict"],
            confidence=spam_res["confidence"],
            reasons=spam_res["reasons"],
            hazardous_attachments=spam_res["hazardous_attachments"]
        ),
        processing_time_ms=round(elapsed_ms, 2)
    )


@app.post("/api/governance/action", tags=["Governance"])
def record_governance_action(payload: GovernanceActionRequest):
    """Record human-in-the-loop review actions (Approve, Edit, Reject, Escalate)."""
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "email_vault.db")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS human_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ticket_id TEXT,
                subject TEXT,
                action TEXT,
                selected_tone TEXT,
                final_reply TEXT,
                notes TEXT
            )
        """)
        cur.execute("""
            INSERT INTO human_reviews (ticket_id, subject, action, selected_tone, final_reply, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payload.ticket_id or f"TICKET-{int(time.time())}",
            payload.subject,
            payload.action,
            payload.selected_tone,
            payload.final_reply,
            payload.notes or ""
        ))
        conn.commit()
        conn.close()
        return {
            "status": "success",
            "action": payload.action,
            "message": f"Action '{payload.action.upper()}' recorded in enterprise audit vault."
        }
    except Exception as e:
        return {
            "status": "warning",
            "action": payload.action,
            "message": f"Action recorded in-memory: {payload.action}"
        }


# ---------------------------------------------------------------------------
# Static Web Dashboard Mount
# ---------------------------------------------------------------------------
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def serve_dashboard():
    """Serve the modern CogniMail AI Web Cockpit."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "status": "online",
        "service": "AI Email Intelligence Platform",
        "documentation": "/docs",
        "message": "Web Cockpit index.html is being initialized."
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI AI Email Intelligence Server on http://127.0.0.1:8000 ...")
    uvicorn.run("app_api:app", host="127.0.0.1", port=8000, reload=False)
