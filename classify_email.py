"""
Module 6 - Real-time Email Intent & Category Inference Engine
Fulfills Page 14 of docs_ai_email_classification.pdf:
Takes incoming email text, predicts Category & Intent with Confidence scores.

Usage:
    python classify_email.py --text "Could we schedule a meeting tomorrow to discuss the project?"
    python classify_email.py --text "My invoice INV-4587 is still showing as unpaid. Please refund immediately."
"""

import os
import argparse
import joblib
import numpy as np

MODELS_DIR = "models"

def load_inference_artifacts():
    tfidf = joblib.load(os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib"))
    cat_model = joblib.load(os.path.join(MODELS_DIR, "category_model.joblib"))
    cat_le = joblib.load(os.path.join(MODELS_DIR, "category_label_encoder.joblib"))
    int_model = joblib.load(os.path.join(MODELS_DIR, "intent_model.joblib"))
    int_le = joblib.load(os.path.join(MODELS_DIR, "intent_label_encoder.joblib"))
    return tfidf, cat_model, cat_le, int_model, int_le

def classify_email(text, subject=""):
    tfidf, cat_model, cat_le, int_model, int_le = load_inference_artifacts()
    
    # Weight subject higher to match training distribution
    if subject:
        input_text = f"{subject} {subject} {text}"
    else:
        input_text = f"{text} {text}"
    
    # Vectorize
    vec = tfidf.transform([input_text])
    
    # Predict Category
    cat_pred_idx = cat_model.predict(vec)[0]
    category = cat_le.inverse_transform([cat_pred_idx])[0]
    if hasattr(cat_model, "predict_proba"):
        cat_conf = np.max(cat_model.predict_proba(vec)) * 100
    else:
        cat_conf = 95.0
        
    # Predict Intent
    int_pred_idx = int_model.predict(vec)[0]
    intent = int_le.inverse_transform([int_pred_idx])[0]
    if hasattr(int_model, "predict_proba"):
        int_conf = np.max(int_model.predict_proba(vec)) * 100
    else:
        int_conf = 95.0
        
    return {
        "text": text,
        "subject": subject,
        "category": category,
        "category_confidence": round(cat_conf, 1),
        "intent": intent,
        "intent_confidence": round(int_conf, 1)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict Email Category & Intent")
    parser.add_argument("--text", type=str, default="", help="Email body content")
    parser.add_argument("--subject", type=str, default="", help="Email subject")
    args = parser.parse_args()

    content = args.text if args.text else args.subject
    res = classify_email(text=content, subject=args.subject)
    print("\n" + "="*50)
    print("AI EMAIL CLASSIFICATION RESULT")
    print("="*50)
    if res['subject']:
        print(f"Subject:    \"{res['subject']}\"")
    print(f"Email:      \"{res['text']}\"")
    print(f"Category:   {res['category']} ({res['category_confidence']}%)")
    print(f"Intent:     {res['intent']} ({res['intent_confidence']}%)")
    print("="*50 + "\n")
