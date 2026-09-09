"""
Module 14: Real-Time Email Processing & Human-in-the-Loop Audit Engine
Fulfills Page 27-28 of docs_ai_email_classification.pdf:
- Real-Time Workflow:
  Incoming Email -> Email Parser -> Text Processing -> Intent Classification -> 
  Sentiment Analysis -> Priority Detection -> Entity Extraction -> Email Summarization -> 
  Context Analysis -> Smart Reply Generation -> Response Recommendation -> 
  Human Approval -> Store / Send Response
- Embedded SQLite Database (email_vault.db) with audit trail
- Human-in-the-Loop Status State Machine:
  PENDING_APPROVAL -> APPROVED / REJECTED / ESCALATED / SENT
- Continuous Streaming Ingestion Simulator
- Operational Metrics & Monitoring KPIs

Usage:
    python realtime_processor.py --simulate 5
    python realtime_processor.py --metrics
    python realtime_processor.py --list
    python realtime_processor.py --review EMAIL-XXXX --action APPROVE
"""

import os
import sys
import time
import json
import sqlite3
import argparse
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Ensure terminal handles UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Import core AI inference modules
import classify_email
import analyze_sentiment_emotion
import predict_priority
import extract_entities
from smart_reply_generator import SmartReplyEngine, SUPPORTED_TONES
from email_summarizer import EmailSummarizer, ResponseRecommender
from spam_duplicate_detector import EmailPatternEngine

DB_PATH = "email_vault.db"

# ---------------------------------------------------------------------------
# Database Initialization & Schema
# ---------------------------------------------------------------------------
def init_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Initializes the SQLite tables for persistent ticket vault and audit logs."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT UNIQUE NOT NULL,
        timestamp TEXT NOT NULL,
        sender TEXT NOT NULL,
        subject TEXT NOT NULL,
        body TEXT NOT NULL,
        category TEXT NOT NULL,
        intent TEXT NOT NULL,
        sentiment TEXT NOT NULL,
        emotion TEXT NOT NULL,
        priority TEXT NOT NULL,
        urgency TEXT NOT NULL,
        entities_json TEXT,
        abstractive_summary TEXT,
        recommended_action TEXT,
        suggested_reply TEXT,
        selected_tone TEXT,
        is_spam INTEGER DEFAULT 0,
        spam_verdict TEXT,
        status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
        processing_latency_ms REAL,
        reviewer_notes TEXT,
        final_reply TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT NOT NULL,
        action TEXT NOT NULL,
        actor TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (email_id) REFERENCES emails(email_id)
    );
    """)

    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Real-Time Email Processor Class
# ---------------------------------------------------------------------------
class RealtimeEmailProcessor:
    """
    Orchestrates real-time email ingestion, automated multi-stage AI inference,
    database persistence, and human-in-the-loop audit governance.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_db(self.db_path)
        self.smart_reply_engine = SmartReplyEngine()
        self.pattern_engine = EmailPatternEngine()
        self.summarizer = EmailSummarizer()
        self.recommender = ResponseRecommender()

    def process_and_store(
        self,
        subject: str,
        body: str,
        sender: str = "customer@example.com",
        attachments: Optional[List[str]] = None,
        preferred_tone: str = "Professional"
    ) -> Dict[str, Any]:
        """
        Executes the complete syllabus pipeline (Page 27) and saves to database.
        """
        t0 = time.time()
        email_id = f"EML-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        effective_text = body if body.strip() else subject

        # Stage 1: Classification
        cat_res = classify_email.classify_email(text=effective_text, subject=subject)

        # Stage 2: Sentiment & Emotion
        sent_res = analyze_sentiment_emotion.analyze_sentiment_emotion(text=effective_text, subject=subject)

        # Stage 3: Priority & Urgency
        prio_res = predict_priority.predict_priority(text=effective_text, subject=subject)

        # Stage 4: Entity Extraction
        ent_res = extract_entities.extract_entities(text=effective_text, subject=subject)

        # Stage 5: Summarization
        abs_sum = self.summarizer.abstractive_summarize(
            text=effective_text,
            context={"subject": subject, "entities": ent_res, "intent": cat_res["intent"]}
        )

        # Stage 6: Response Recommendation
        rec_res = self.recommender.recommend_response(text=effective_text, subject=subject)
        rec_data = rec_res.get("recommendation", {})
        rec_action = rec_data.get("primary_action", "Review customer inquiry")

        # Stage 7: Context-Aware Smart Reply Generation
        tone = preferred_tone if preferred_tone in SUPPORTED_TONES else "Professional"
        ctx = self.smart_reply_engine.build_context(
            text=effective_text,
            subject=subject,
            intent=cat_res["intent"],
            category=cat_res["category"],
            sentiment=sent_res["sentiment"],
            emotion=sent_res["emotion"],
            priority=prio_res["priority"],
            urgency=prio_res["urgency"],
            entities=ent_res,
            preferred_tone=tone
        )
        reply_obj = self.smart_reply_engine.generate_reply(
            text=effective_text,
            subject=subject,
            tone=tone,
            context=ctx
        )
        suggested_reply = reply_obj["reply_text"]

        # Stage 8: Spam & Phishing Screening
        spam_res = self.pattern_engine.spam_detector.analyze(
            text=effective_text,
            subject=subject,
            sender=sender,
            attachments=attachments or []
        )

        latency_ms = round((time.time() - t0) * 1000, 2)

        # Status determined by spam/urgency
        initial_status = "PENDING_APPROVAL"
        if spam_res["is_spam"]:
            initial_status = "FLAGGED_SPAM"

        # Stage 9: Store in SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO emails (
            email_id, timestamp, sender, subject, body,
            category, intent, sentiment, emotion, priority, urgency,
            entities_json, abstractive_summary, recommended_action,
            suggested_reply, selected_tone, is_spam, spam_verdict,
            status, processing_latency_ms, final_reply
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email_id, timestamp_str, sender, subject, body,
            cat_res["category"], cat_res["intent"],
            sent_res["sentiment"], sent_res["emotion"],
            prio_res["priority"], prio_res["urgency"],
            json.dumps(ent_res), abs_sum, rec_action,
            suggested_reply, tone, 1 if spam_res["is_spam"] else 0,
            spam_res["verdict"], initial_status, latency_ms, suggested_reply
        ))

        # Log audit entry
        cursor.execute("""
        INSERT INTO audit_logs (email_id, action, actor, timestamp, notes)
        VALUES (?, ?, ?, ?, ?)
        """, (
            email_id, "INGESTED_AND_CLASSIFIED", "AI_ENGINE",
            timestamp_str, f"Processed in {latency_ms}ms with status {initial_status}"
        ))

        conn.commit()
        conn.close()

        return {
            "email_id": email_id,
            "timestamp": timestamp_str,
            "sender": sender,
            "subject": subject,
            "category": cat_res["category"],
            "intent": cat_res["intent"],
            "sentiment": sent_res["sentiment"],
            "emotion": sent_res["emotion"],
            "priority": prio_res["priority"],
            "urgency": prio_res["urgency"],
            "summary": abs_sum,
            "recommended_action": rec_action,
            "suggested_reply": suggested_reply,
            "is_spam": spam_res["is_spam"],
            "spam_verdict": spam_res["verdict"],
            "status": initial_status,
            "latency_ms": latency_ms
        }

    # =========================================================================
    # Human-in-the-Loop Review API
    # =========================================================================
    def review_ticket(
        self,
        email_id: str,
        action: str,
        modified_reply: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fulfills syllabus Page 28 Human-in-the-Loop review actions:
        - APPROVE: Marks ticket approved and ready for sending
        - REJECT: Discards AI response or escalates to human agent
        - EDIT: Saves reviewer-modified response
        - REGENERATE: Triggers re-synthesis of reply with new tone
        """
        action = action.upper()
        allowed_actions = ["APPROVE", "REJECT", "EDIT", "REGENERATE", "SEND"]
        if action not in allowed_actions:
            raise ValueError(f"Action '{action}' not recognized. Must be one of {allowed_actions}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT email_id, subject, body, status, final_reply FROM emails WHERE email_id = ?", (email_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise KeyError(f"Ticket '{email_id}' not found in database.")

        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_status = row[3]
        final_text = row[4]

        if action == "APPROVE":
            new_status = "APPROVED"
        elif action == "REJECT":
            new_status = "REJECTED_BY_HUMAN"
        elif action == "SEND":
            new_status = "SENT"
        elif action == "EDIT":
            new_status = "MODIFIED_BY_HUMAN"
            if modified_reply:
                final_text = modified_reply
        elif action == "REGENERATE":
            # Re-synthesize with Apologetic or Empathetic tone
            reply_obj = self.smart_reply_engine.generate_reply(
                text=row[2],
                subject=row[1],
                tone="Empathetic"
            )
            final_text = reply_obj["reply_text"]
            new_status = "REGENERATED_PENDING_APPROVAL"

        cursor.execute("""
        UPDATE emails
        SET status = ?, final_reply = ?, reviewer_notes = ?
        WHERE email_id = ?
        """, (new_status, final_text, notes, email_id))

        cursor.execute("""
        INSERT INTO audit_logs (email_id, action, actor, timestamp, notes)
        VALUES (?, ?, ?, ?, ?)
        """, (email_id, f"HUMAN_{action}", "HUMAN_SUPERVISOR", timestamp_str, notes or f"Executed action {action}"))

        conn.commit()
        conn.close()

        return {
            "email_id": email_id,
            "previous_status": row[3],
            "current_status": new_status,
            "final_reply": final_text,
            "timestamp": timestamp_str
        }

    # =========================================================================
    # Operational Monitoring & Analytics
    # =========================================================================
    def get_metrics(self) -> Dict[str, Any]:
        """Aggregates operational monitoring KPIs for system health."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM emails")
        total_ingested = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emails WHERE status = 'APPROVED'")
        approved_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emails WHERE status = 'REJECTED_BY_HUMAN'")
        rejected_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emails WHERE is_spam = 1")
        spam_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(processing_latency_ms) FROM emails")
        avg_latency = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT priority, COUNT(*) FROM emails GROUP BY priority")
        priority_breakdown = dict(cursor.fetchall())

        cursor.execute("SELECT category, COUNT(*) FROM emails GROUP BY category")
        category_breakdown = dict(cursor.fetchall())

        conn.close()

        return {
            "total_ingested": total_ingested,
            "approved": approved_count,
            "rejected": rejected_count,
            "spam_blocked": spam_count,
            "avg_latency_ms": round(avg_latency, 2),
            "priority_distribution": priority_breakdown,
            "category_distribution": category_breakdown
        }

    def list_tickets(self, status: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves recently processed email records."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT email_id, timestamp, subject, category, priority, status, processing_latency_ms FROM emails"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "email_id": r[0],
                "timestamp": r[1],
                "subject": r[2],
                "category": r[3],
                "priority": r[4],
                "status": r[5],
                "latency_ms": r[6]
            }
            for r in rows
        ]


# ---------------------------------------------------------------------------
# Stream Simulation Engine
# ---------------------------------------------------------------------------
SAMPLE_STREAM = [
    {
        "subject": "Urgent: Payment Issue",
        "body": "Hi Support Team, the payment was deducted from my account yesterday but the order is still showing as unpaid. Please resolve this as soon as possible. Thanks, Sarah",
        "sender": "sarah.j@consumer.com"
    },
    {
        "subject": "CRITICAL: Database Outage on US-East Node",
        "body": "Production cluster us-east-1 went down with kernel panic. Portal is returning 502 Bad Gateway. Fix immediately!",
        "sender": "ops-monitor@infra-alerts.net"
    },
    {
        "subject": "Overdue Invoice INV-5542 for $8,200",
        "body": "Hello Accounts, invoice INV-5542 for $8,200 is 15 days overdue. Please process wire transfer by Thursday.",
        "sender": "billing@cloudservices.io"
    },
    {
        "subject": "SECURITY ALERT: Verify Password Now",
        "body": "Your bank account has been suspended! Please confirm your credentials immediately at http://192.168.1.1/login",
        "sender": "security-support@secure-update-host.xyz",
        "attachments": ["account_patch.pdf.exe"]
    },
    {
        "subject": "Meeting Reschedule to 3 PM",
        "body": "Hi Michael, could we move our sprint sync tomorrow from 11 AM to 3 PM? Let me know if that works for you.",
        "sender": "alex.t@partnertech.org"
    }
]


def run_stream_simulation(count: int = 3, delay_sec: float = 1.0, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Simulates real-time continuous email ingestion."""
    processor = RealtimeEmailProcessor(db_path=db_path)
    results = []

    print("=" * 70)
    print(f"STARTING REAL-TIME EMAIL STREAM SIMULATOR ({count} incoming emails)")
    print("=" * 70)

    for i in range(min(count, len(SAMPLE_STREAM))):
        sample = SAMPLE_STREAM[i]
        print(f"\n[Incoming Event #{i+1}] Subject: \"{sample['subject']}\"")
        res = processor.process_and_store(
            subject=sample["subject"],
            body=sample["body"],
            sender=sample["sender"],
            attachments=sample.get("attachments", [])
        )
        print(f"  ● Ticket ID:   {res['email_id']}")
        print(f"  ● Category:    {res['category']} | Priority: {res['priority']}")
        print(f"  ● Action:      {res['recommended_action']}")
        print(f"  ● Status:      {res['status']} (Latency: {res['latency_ms']} ms)")
        results.append(res)
        if i < count - 1:
            time.sleep(delay_sec)

    print("\n" + "=" * 70)
    print(f"SIMULATION COMPLETE: {len(results)} emails ingested and stored in {db_path} ✅")
    print("=" * 70)
    return results


# ---------------------------------------------------------------------------
# CLI Command Line Interface
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Module 14: Real-Time Email Processor & Audit Engine")
    parser.add_argument("--simulate", type=int, default=0, help="Run live simulation with N emails")
    parser.add_argument("--metrics", action="store_true", help="Display operational monitoring KPIs")
    parser.add_argument("--list", action="store_true", help="List recent processed email tickets")
    parser.add_argument("--review", type=str, default="", help="Review a ticket by Email ID")
    parser.add_argument("--action", type=str, default="APPROVE", help="Review action (APPROVE, REJECT, EDIT, REGENERATE, SEND)")
    parser.add_argument("--notes", type=str, default="", help="Reviewer comments/notes")

    args = parser.parse_args()
    engine = RealtimeEmailProcessor()

    if args.simulate > 0:
        run_stream_simulation(count=args.simulate)
    elif args.metrics:
        m = engine.get_metrics()
        print("\n" + "=" * 50)
        print("OPERATIONAL MONITORING METRICS (email_vault.db)")
        print("=" * 50)
        print(f"Total Ingested:        {m['total_ingested']}")
        print(f"Approved Tickets:      {m['approved']}")
        print(f"Rejected Tickets:      {m['rejected']}")
        print(f"Spam Blocked:          {m['spam_blocked']}")
        print(f"Average Latency:       {m['avg_latency_ms']} ms")
        print("\nPriority Breakdown:")
        for p, cnt in m["priority_distribution"].items():
            print(f"  * {p:<20}: {cnt}")
        print("\nCategory Breakdown:")
        for c, cnt in m["category_distribution"].items():
            print(f"  * {c:<25}: {cnt}")
        print("=" * 50 + "\n")
    elif args.list:
        tickets = engine.list_tickets(limit=10)
        print("\n" + "=" * 75)
        print(f"{'TICKET ID':<22} | {'TIMESTAMP':<19} | {'PRIORITY':<12} | {'STATUS'}")
        print("-" * 75)
        for t in tickets:
            print(f"{t['email_id']:<22} | {t['timestamp']:<19} | {t['priority']:<12} | {t['status']}")
        print("=" * 75 + "\n")
    elif args.review:
        res = engine.review_ticket(email_id=args.review, action=args.action, notes=args.notes)
        print(f"\n[REVIEW SUCCESS] Ticket {res['email_id']}: {res['previous_status']} -> {res['current_status']}\n")
    else:
        parser.print_help()
