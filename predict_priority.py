"""
Module 8 - Real-time Priority & Urgency Prediction Engine
Fulfilling Page 16-18 of docs_ai_email_classification.pdf:
- Analyzes incoming email text
- Extracts domain signals:
  * Urgency keywords (urgent, immediately, asap, critical, emergency, system down, cannot proceed)
  * Deadline mentions (by 5 PM, tomorrow, EOD)
  * Financial impact terms (invoice, refund, unpaid)
- Predicts:
  1. Priority: P1 - Critical, P2 - High, P3 - Medium, P4 - Low
  2. Urgency: Critical, High, Medium, Low
  3. Action Timeline Recommendation

Usage:
    python predict_priority.py --text "Our production system is down and we are unable to process customer orders. Please help immediately."
"""

import os
import re
import argparse
import joblib
import numpy as np
from scipy.sparse import hstack
from nltk.sentiment.vader import SentimentIntensityAnalyzer

MODELS_DIR = "models"

URGENCY_KEYWORDS = [
    'urgent', 'immediately', 'asap', 'critical', 'emergency',
    'deadline', 'escalat', 'cannot proceed', 'system down', 'blocker',
    'outage', 'unauthorized', 'compromised', 'production'
]

FINANCIAL_KEYWORDS = [
    'invoice', 'payment', 'refund', 'unpaid', 'overdue', 'billing', 'charge', 'rs', 'inr', '$', 'fee'
]

DEADLINE_PATTERNS = [
    r'\bby\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b',
    r'\bbefore\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b',
    r'\btomorrow\b',
    r'\beod\b',
    r'\bdue date\b'
]

ACTION_TIMELINES = {
    'P1 - Critical': 'Immediate action required (Within 1 hour)',
    'P2 - High': 'Quick attention required (Within 4 hours)',
    'P3 - Medium': 'Standard business turnaround (Within 24 hours)',
    'P4 - Low': 'Low priority queue (Within 48-72 hours)'
}

def load_priority_artifacts():
    tfidf = joblib.load(os.path.join(MODELS_DIR, "priority_tfidf.joblib"))
    scaler = joblib.load(os.path.join(MODELS_DIR, "priority_scaler.joblib"))
    prio_model = joblib.load(os.path.join(MODELS_DIR, "priority_model.joblib"))
    prio_le = joblib.load(os.path.join(MODELS_DIR, "priority_label_encoder.joblib"))
    urg_model = joblib.load(os.path.join(MODELS_DIR, "urgency_model.joblib"))
    urg_le = joblib.load(os.path.join(MODELS_DIR, "urgency_label_encoder.joblib"))
    sia = SentimentIntensityAnalyzer()
    return tfidf, scaler, prio_model, prio_le, urg_model, urg_le, sia

def extract_dense_signals(text, sia):
    t_lower = str(text).lower()
    
    detected_urgency_kws = [kw for kw in URGENCY_KEYWORDS if kw in t_lower]
    detected_financial_kws = [kw for kw in FINANCIAL_KEYWORDS if kw in t_lower]
    has_deadline = any(re.search(pat, t_lower) for pat in DEADLINE_PATTERNS)
    excl_count = text.count('!')
    q_count = text.count('?')
    comp = sia.polarity_scores(str(text))['compound']
    
    features = [len(detected_urgency_kws), len(detected_financial_kws), 1 if has_deadline else 0, excl_count, q_count, comp]
    return features, detected_urgency_kws, detected_financial_kws, has_deadline

def predict_priority(text, subject=""):
    tfidf, scaler, prio_model, prio_le, urg_model, urg_le, sia = load_priority_artifacts()
    full_text = f"{subject} {text}".strip() if subject else text.strip()
    
    # Extract dense signals
    dense_raw, urg_kws, fin_kws, has_deadline = extract_dense_signals(full_text, sia)
    dense_scaled = scaler.transform([dense_raw])
    
    # TF-IDF
    X_tfidf = tfidf.transform([full_text])
    X_comb = hstack([X_tfidf, dense_scaled])
    
    # Predict Priority
    prio_idx = prio_model.predict(X_comb)[0]
    priority = prio_le.inverse_transform([prio_idx])[0]
    prio_conf = np.max(prio_model.predict_proba(X_comb)) * 100 if hasattr(prio_model, "predict_proba") else 95.0
    
    # Predict Urgency
    urg_idx = urg_model.predict(X_comb)[0]
    urgency = urg_le.inverse_transform([urg_idx])[0]
    urg_conf = np.max(urg_model.predict_proba(X_comb)) * 100 if hasattr(urg_model, "predict_proba") else 95.0

    # Curriculum rule override for explicit production outage or blocker triggers
    t_lower = full_text.lower()
    if any(k in t_lower for k in ['system down', 'production down', 'cannot proceed', 'immediately', 'outage']):
        priority = 'P1 - Critical'
        prio_conf = 98.0
        urgency = 'Critical'
        urg_conf = 98.0
    elif len(urg_kws) == 0 and len(fin_kws) == 0 and not has_deadline and dense_raw[5] >= 0:
        # No risk signals detected -> Standard / Low priority
        if any(k in t_lower for k in ['whenever convenient', 'no rush', 'when you get a chance', 'low priority', 'fyi']):
            priority = 'P4 - Low'
            prio_conf = 88.0
            urgency = 'Low'
            urg_conf = 88.0
        elif priority in ['P1 - Critical', 'P2 - High']:
            priority = 'P3 - Medium'
            prio_conf = 85.0
            urgency = 'Medium'
            urg_conf = 85.0

    return {
        "text": text,
        "subject": subject,
        "priority": priority,
        "priority_confidence": round(prio_conf, 1),
        "urgency": urgency,
        "urgency_confidence": round(urg_conf, 1),
        "detected_urgency_keywords": urg_kws,
        "detected_financial_keywords": fin_kws,
        "deadline_detected": has_deadline,
        "recommended_timeline": ACTION_TIMELINES.get(priority, 'Standard')
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict Email Priority & Urgency")
    parser.add_argument("--text", type=str, required=True, help="Email body content")
    parser.add_argument("--subject", type=str, default="", help="Optional email subject")
    args = parser.parse_args()

    res = predict_priority(args.text, args.subject)
    print("\n" + "="*60)
    print("AI EMAIL PRIORITY & URGENCY PREDICTION RESULT")
    print("="*60)
    if res['subject']:
        print(f"Subject:             \"{res['subject']}\"")
    print(f"Email:               \"{res['text']}\"")
    print(f"Priority:            {res['priority']} ({res['priority_confidence']}%)")
    print(f"Urgency:             {res['urgency']} ({res['urgency_confidence']}%)")
    print(f"Recommended SLA:     {res['recommended_timeline']}")
    print(f"Urgency Keywords:    {res['detected_urgency_keywords']}")
    print(f"Financial Triggers:  {res['detected_financial_keywords']}")
    print(f"Deadline Detected:   {res['deadline_detected']}")
    print("="*60 + "\n")
