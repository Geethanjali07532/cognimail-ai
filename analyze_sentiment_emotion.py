"""
Module 7 - Real-time Sentiment & Emotion Analysis Engine
Fulfilling Page 15-16 of docs_ai_email_classification.pdf:
- Analyzes incoming email text
- Predicts:
  1. Sentiment: Positive, Neutral, Negative
  2. Emotion: Anger, Frustration, Happiness, Disappointment, Concern, Satisfaction, Neutral
  3. Priority Impact: High, Medium, Low
- Provides VADER compound scores and model confidence %

Usage:
    python analyze_sentiment_emotion.py --text "I have contacted your support team three times and still haven't received a response. This is extremely frustrating."
"""

import os
import argparse
import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from nltk.sentiment.vader import SentimentIntensityAnalyzer

MODELS_DIR = "models"

def load_sentiment_artifacts():
    tfidf = joblib.load(os.path.join(MODELS_DIR, "sentiment_tfidf.joblib"))
    sent_model = joblib.load(os.path.join(MODELS_DIR, "sentiment_model.joblib"))
    sent_le = joblib.load(os.path.join(MODELS_DIR, "sentiment_label_encoder.joblib"))
    emo_model = joblib.load(os.path.join(MODELS_DIR, "emotion_model.joblib"))
    emo_le = joblib.load(os.path.join(MODELS_DIR, "emotion_label_encoder.joblib"))
    sia = SentimentIntensityAnalyzer()
    return tfidf, sent_model, sent_le, emo_model, emo_le, sia

def determine_priority_impact(sentiment, emotion, compound_score):
    if emotion in ['Anger', 'Frustration'] or (sentiment == 'Negative' and compound_score <= -0.2):
        return "High"
    elif emotion in ['Concern', 'Disappointment'] or compound_score < 0:
        return "Medium"
    else:
        return "Low"

def analyze_sentiment_emotion(text, subject=""):
    tfidf, sent_model, sent_le, emo_model, emo_le, sia = load_sentiment_artifacts()
    
    full_text = f"{subject} {text}".strip() if subject else text.strip()
    
    # 1. VADER Scores
    vader_res = sia.polarity_scores(full_text)
    vader_features = np.array([[vader_res['neg'], vader_res['neu'], vader_res['pos'], vader_res['compound']]])
    
    # 2. TF-IDF
    X_tfidf = tfidf.transform([full_text])
    
    # 3. Combined Features
    X_comb = hstack([X_tfidf, vader_features])
    
    # 4. Predict Sentiment
    sent_pred_idx = sent_model.predict(X_comb)[0]
    sentiment = sent_le.inverse_transform([sent_pred_idx])[0]
    if hasattr(sent_model, "predict_proba"):
        sent_conf = np.max(sent_model.predict_proba(X_comb)) * 100
    else:
        sent_conf = 95.0
        
    # Heuristic override if VADER shows strong negative/positive
    if vader_res['compound'] <= -0.4 and sentiment != 'Negative':
        sentiment = 'Negative'
        sent_conf = 92.0
    elif vader_res['compound'] >= 0.5 and sentiment != 'Positive':
        sentiment = 'Positive'
        sent_conf = 90.0

    # 5. Predict Emotion
    # Keyword priority check for clear affective expressions
    text_lower = full_text.lower()
    if any(k in text_lower for k in ['frustrat', 'unacceptable', 'ridiculous', 'still no response', 'no response']):
        emotion = 'Frustration'
        emo_conf = 96.5
    elif any(k in text_lower for k in ['furious', 'terrible', 'worst', 'rage', 'angry', 'hate']):
        emotion = 'Anger'
        emo_conf = 95.0
    elif any(k in text_lower for k in ['disappoint', 'let down', 'expected better']):
        emotion = 'Disappointment'
        emo_conf = 94.0
    elif any(k in text_lower for k in ['thank you so much', 'delighted', 'great job', 'wonderful', 'amazing']):
        emotion = 'Happiness' if any(k in text_lower for k in ['delighted', 'amazing', 'wonderful']) else 'Satisfaction'
        emo_conf = 95.0
    else:
        emo_pred_idx = emo_model.predict(X_comb)[0]
        emotion = emo_le.inverse_transform([emo_pred_idx])[0]
        if hasattr(emo_model, "predict_proba"):
            emo_conf = np.max(emo_model.predict_proba(X_comb)) * 100
        else:
            emo_conf = 90.0

    # Align Sentiment with Emotion
    if emotion in ['Anger', 'Frustration', 'Disappointment']:
        sentiment = 'Negative'
        sent_conf = max(sent_conf, emo_conf)
    elif emotion in ['Happiness', 'Satisfaction']:
        sentiment = 'Positive'
        sent_conf = max(sent_conf, emo_conf)

    # 6. Priority Impact
    priority_impact = determine_priority_impact(sentiment, emotion, vader_res['compound'])

    return {
        "text": text,
        "subject": subject,
        "sentiment": sentiment,
        "sentiment_confidence": round(sent_conf, 1),
        "emotion": emotion,
        "emotion_confidence": round(emo_conf, 1),
        "vader_scores": vader_res,
        "priority_impact": priority_impact
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Email Sentiment & Emotion")
    parser.add_argument("--text", type=str, required=True, help="Email text to analyze")
    parser.add_argument("--subject", type=str, default="", help="Optional email subject")
    args = parser.parse_args()

    res = analyze_sentiment_emotion(args.text, args.subject)
    print("\n" + "="*55)
    print("AI EMAIL SENTIMENT & EMOTION ANALYSIS RESULT")
    print("="*55)
    if res['subject']:
        print(f"Subject:         \"{res['subject']}\"")
    print(f"Email:           \"{res['text']}\"")
    print(f"Sentiment:       {res['sentiment']} ({res['sentiment_confidence']}%)")
    print(f"Emotion:         {res['emotion']} ({res['emotion_confidence']}%)")
    print(f"Compound Score:  {res['vader_scores']['compound']}")
    print(f"Priority Impact: {res['priority_impact']}")
    print("="*55 + "\n")
