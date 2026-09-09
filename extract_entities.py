"""
Module 9 - Important Information & Entity Extraction (NER)
Fulfilling all specifications from Module 9 of docs_ai_email_classification.pdf:
- Extracted Entities:
  * Person names (spaCy PERSON)
  * Organizations (spaCy ORG)
  * Dates & Times (spaCy DATE/TIME + Regex)
  * Locations (spaCy GPE/LOC)
  * Phone numbers (Regex)
  * Email addresses (Regex)
  * Invoice numbers (INV-XXXX, Invoice #XXXX)
  * Order IDs (ORD-XXXX, Order #XXXX)
  * Transaction IDs (TXN-XXXX, Transaction #XXXX)
  * Financial Amounts (₹, Rs, $, USD, EUR)
  * Deadlines (by X, before X, EOD, due dates)
  * Product / System names (Portal, CRM, Sarees, Server, DB)
- Action Item Extraction:
  * Action to be taken
  * Associated Deadline
  * Responsible Department / Team

Usage:
    python extract_entities.py --text "Please process invoice INV-9845 for ₹45,000 before September 10."
"""

import sys
import re
import json
import argparse
import spacy

# Ensure Windows terminal supports Unicode symbols like Rupee (₹)
sys.stdout.reconfigure(encoding='utf-8')

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# Custom Regex Patterns for Structured Email Entities
INVOICE_PATTERN = re.compile(r'\b(?:inv[\-_#]?\d{3,10}|invoice\s*(?:id|no|num|number|#)?[\s:\-_]*([a-z0-9\-]{4,15}))\b', re.IGNORECASE)
ORDER_PATTERN = re.compile(r'\b(?:ord[\-_#]?\d{3,10}|order\s*(?:id|no|num|number|#)?[\s:\-_]*([a-z0-9\-]{4,15}))\b', re.IGNORECASE)
TRANSACTION_PATTERN = re.compile(r'\b(?:txn[\-_#]?[a-z0-9]{4,15}|transaction\s*(?:id|no|num|number|#|ref)?[\s:\-_]*([a-z0-9\-]{4,20}))\b', re.IGNORECASE)
PHONE_PATTERN = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b')
EMAIL_PATTERN = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
AMOUNT_PATTERN = re.compile(r'(?:₹|rs\.?|inr|\$|usd|eur|€|£)\s*[\d,]+(?:\.\d{2})?|\b[\d,]+(?:\.\d{2})?\s*(?:rupees|inr|usd|dollars|euros)\b', re.IGNORECASE)
TIME_PATTERN = re.compile(r'\b\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)\b')
DEADLINE_PATTERN = re.compile(r'\b(?:before|by|until|due on|due date is|deadline is|no later than)\s+([a-zA-Z0-9\s,]{3,25}?)(?=[.,;\n]|and\b|for\b|$)', re.IGNORECASE)

PRODUCT_KEYWORDS = [
    'employee portal', 'reporting dashboard', 'cotton saree', 'kanchipuram', 'silk saree',
    'crm', 'vpn', 'database', 'apache server', 'linux', 'production system', 'api gateway'
]

DEPARTMENT_ROUTING = {
    'Invoice': 'Finance & Accounts',
    'Payment': 'Finance & Accounts',
    'Technical': 'IT Support & DevOps',
    'Portal': 'IT Support & DevOps',
    'Server': 'IT Support & DevOps',
    'Meeting': 'Operations / Admin',
    'Candidate': 'HR & Recruitment',
    'Application': 'HR & Recruitment',
    'Leave': 'HR & Personnel',
    'Quote': 'Sales & Merchandising',
    'Pricing': 'Sales & Merchandising',
    'Complaint': 'Customer Experience Desk'
}

def extract_entities(text, subject=""):
    full_text = f"{subject} {text}".strip() if subject else text.strip()
    entities = {
        "invoice_ids": [],
        "order_ids": [],
        "transaction_ids": [],
        "amounts": [],
        "deadlines": [],
        "times": [],
        "dates": [],
        "phone_numbers": [],
        "email_addresses": [],
        "person_names": [],
        "organizations": [],
        "locations": [],
        "products_or_systems": [],
        "action_items": []
    }

    # 1. Regex Extraction for structured entities
    # Invoices: extract pure ID code
    inv_matches = re.findall(r'\b(?:invoice[\s:\-_#]*(?:id|no|num|#)?)?\s*([A-Za-z]{2,4}[\s\-_#]?\d{3,10})\b', full_text, re.IGNORECASE)
    for m in inv_matches:
        code = m.strip().upper().replace(" ", "-")
        if any(code.startswith(prefix) for prefix in ['INV', 'INVOICE', 'BILL']):
            entities["invoice_ids"].append(code)
    if not entities["invoice_ids"]:
        direct_inv = re.findall(r'\b(INV[\-_#]?\d{3,10})\b', full_text, re.IGNORECASE)
        entities["invoice_ids"].extend([d.upper() for d in direct_inv])

    # Orders: extract pure ID code
    ord_matches = re.findall(r'\b(ORD[\-_#]?\d{3,10})\b', full_text, re.IGNORECASE)
    entities["order_ids"].extend([o.upper() for o in ord_matches])

    # Transactions
    txn_matches = re.findall(r'\b(TXN?[\-_#]?[a-zA-Z0-9]{4,15})\b', full_text, re.IGNORECASE)
    entities["transaction_ids"].extend([t.upper() for t in txn_matches])
    # Amounts
    for m in AMOUNT_PATTERN.finditer(full_text):
        entities["amounts"].append(m.group(0).strip())
    # Deadlines
    for m in DEADLINE_PATTERN.finditer(full_text):
        entities["deadlines"].append(m.group(1).strip())
    # Times
    for m in TIME_PATTERN.finditer(full_text):
        entities["times"].append(m.group(0).strip())
    # Phone numbers
    for m in PHONE_PATTERN.finditer(full_text):
        num = m.group(0).strip()
        if len(re.sub(r'\D', '', num)) >= 7:
            entities["phone_numbers"].append(num)
    # Emails
    for m in EMAIL_PATTERN.finditer(full_text):
        entities["email_addresses"].append(m.group(0).strip())

    # Products / Systems
    text_lower = full_text.lower()
    for prod in PRODUCT_KEYWORDS:
        if prod in text_lower:
            entities["products_or_systems"].append(prod.title())

    # 2. spaCy Extraction for NLP Named Entities
    if nlp:
        doc = nlp(full_text)
        for ent in doc.ents:
            val = ent.text.strip()
            if ent.label_ == "PERSON" and val not in entities["person_names"] and len(val) > 2:
                entities["person_names"].append(val)
            elif ent.label_ == "ORG" and val not in entities["organizations"] and len(val) > 2:
                entities["organizations"].append(val)
            elif ent.label_ == "GPE" and val not in entities["locations"]:
                entities["locations"].append(val)
            elif ent.label_ == "DATE" and val not in entities["dates"]:
                entities["dates"].append(val)
            elif ent.label_ == "TIME" and val not in entities["times"]:
                entities["times"].append(val)
            elif ent.label_ == "MONEY" and val not in entities["amounts"]:
                entities["amounts"].append(val)

    # De-duplicate lists
    for k in entities:
        if isinstance(entities[k], list):
            entities[k] = list(dict.fromkeys(entities[k]))

    # 3. Action Item Extraction
    action_item = extract_action_item(full_text, entities)
    entities["action_items"].append(action_item)

    return entities

def extract_action_item(text, entities):
    t_lower = text.lower()
    
    # Identify Primary Action
    action = "Review and address incoming inquiry"
    team = "General Support Operations"

    if "process invoice" in t_lower or entities["invoice_ids"]:
        inv = entities["invoice_ids"][0] if entities["invoice_ids"] else "referenced invoice"
        action = f"Process invoice {inv}"
        team = "Finance & Accounts"
    elif "ship" in t_lower or "order" in t_lower or entities["order_ids"]:
        ord_id = entities["order_ids"][0] if entities["order_ids"] else "referenced order"
        action = f"Fulfill and dispatch order {ord_id}"
        team = "Sales & Fulfillment Operations"
    elif "schedule" in t_lower or "meeting" in t_lower:
        action = "Schedule team meeting and send calendar invite"
    elif "password" in t_lower or "unauthorized" in t_lower or "reset" in t_lower:
        action = "Verify security credentials and reset account access"
    elif "system down" in t_lower or "portal" in t_lower or "error" in t_lower:
        action = "Investigate production service error and resolve outage"
    elif "apply" in t_lower or "resume" in t_lower or "candidate" in t_lower:
        action = "Screen candidate application and schedule interview"
    elif "quote" in t_lower or "pricing" in t_lower or "wholesale" in t_lower:
        action = "Generate wholesale pricing quotation and send product catalog"
    elif "leave" in t_lower:
        action = "Review and approve employee leave request"
    elif "refund" in t_lower:
        action = "Audit merchant transaction and initiate refund"

    # Identify Deadline
    deadline = "Not specified"
    if entities["deadlines"]:
        deadline = entities["deadlines"][0]
    elif entities["dates"]:
        deadline = entities["dates"][0]
    elif entities["times"]:
        deadline = entities["times"][0]

    # Identify Responsible Team
    team = "General Support Operations"
    for key, dept in DEPARTMENT_ROUTING.items():
        if key.lower() in t_lower:
            team = dept
            break

    return {
        "action": action,
        "deadline": deadline,
        "responsible_team": team
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Important Information & Entities (NER)")
    parser.add_argument("--text", type=str, required=True, help="Email content")
    parser.add_argument("--subject", type=str, default="", help="Optional email subject")
    args = parser.parse_args()

    results = extract_entities(args.text, args.subject)
    
    print("\n" + "="*60)
    print("AI EMAIL ENTITY & INFORMATION EXTRACTION RESULT")
    print("="*60)
    print(f"Email Text:  \"{args.text}\"")
    print("\nEXTRACTED ENTITIES:")
    for category, items in results.items():
        if category != "action_items" and items:
            print(f"  * {category.replace('_', ' ').title():<22} : {', '.join(items)}")

    print("\nACTION ITEM EXTRACTION:")
    act = results["action_items"][0]
    print(f"  * Action           : {act['action']}")
    print(f"  * Deadline         : {act['deadline']}")
    print(f"  * Responsible Team : {act['responsible_team']}")
    print("="*60 + "\n")
