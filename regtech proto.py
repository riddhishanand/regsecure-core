import feedparser
import pandas as pd
import spacy
from datetime import datetime

# Initialize English NLP model for legal text keyword analysis
import os
import subprocess
import sys
import spacy

# Automatically download the model if it's not already installed
try:
    nlp = spacy.load("en_core_web_sm")
    # or if that fails:
except OSError:
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
nlp = spacy.load("en_core_web_sm")

# Real live endpoint for RBI Notifications via RSS Feed
RBI_RSS_URL = "https://rbi.org.in"

# -------------------------------------------------------------------
# 1. LIVE COMPLIANCE ENGINE (FETCHING DATA FROM RBI CAP)
# -------------------------------------------------------------------
def fetch_latest_rbi_directives():
    """Fetches real-time regulatory announcements from the RBI."""
    print("[*] Contacting RBI Server...")
    feed = feedparser.parse(RBI_RSS_URL)
    directives = []
    
    for entry in feed.entries[:5]: # Analyze the 5 most recent announcements
        directives.append({
            "title": entry.title,
            "summary": entry.summary if 'summary' in entry else entry.title,
            "link": entry.link,
            "published": entry.get("published", datetime.now().strftime("%Y-%m-%d"))
        })
    return pd.DataFrame(directives)

# -------------------------------------------------------------------
# 2. AI TEXT PARSING LAYER (TRIGGER ALERTS BASED ON REGULATION BODY)
# -------------------------------------------------------------------
def scan_for_risk_triggers(df_directives, watch_keywords):
    """Scans regulatory text using NLP to detect if policies affect client operations."""
    print("[*] AI Engine analyzing circular text for compliance pivots...")
    flagged_alerts = []
    
    for _, row in df_directives.iterrows():
        text_to_analyze = (row['title'] + " " + row['summary']).lower()
        doc = nlp(text_to_analyze)
        
        # Token scanning for matches
        matched_terms = [token.text for token in doc if token.text in watch_keywords]
        
        if matched_terms:
            flagged_alerts.append({
                "Alert_Level": "CRITICAL UPDATE",
                "Source": "RBI Circular",
                "Context": row['title'],
                "Trigger_Keywords": list(set(matched_terms)),
                "Action_Required": "Review Transaction Parameters Immediately",
                "Link": row['link']
            })
            
    return pd.DataFrame(flagged_alerts)

# -------------------------------------------------------------------
# 3. CONCURRENT TRANSACTIONS AUDITING ENGINE
# -------------------------------------------------------------------
def audit_live_transactions(df_transactions, max_wallet_limit):
    """Continuous Forensic Auditor checking internal books for compliance violations."""
    print("[*] Continuous Auditor executing balance checks against transaction logs...")
    violations = []
    
    for _, tx in df_transactions.iterrows():
        # Concrete Compliance Rule: Flag any customer transaction crossing regulatory caps
        if tx['amount'] > max_wallet_limit:
            violations.append({
                "Transaction_ID": tx['tx_id'],
                "User_ID": tx['user_id'],
                "Amount": tx['amount'],
                "Regulatory_Cap": max_wallet_limit,
                "Status": "BLOCKED & REJECTED",
                "Reason": f"Transaction exceeds maximum limit of ₹{max_wallet_limit}"
            })
    return pd.DataFrame(violations)

# -------------------------------------------------------------------
# EXECUTIVE SYSTEM RUN
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Define compliance keywords we are tracking for our target client (e.g., a Fintech lender)
    compliance_watch_list = ["lending", "kyc", "wallet", "prepaid", "digital", "limit", "settlement"]
    
    # Define active RBI Dynamic Limits (e.g., Max non-KYC PPI transaction limit of ₹10,000)
    CURRENT_REGULATORY_CAP = 10000 
    
    # Mock Database representing a bank or fintech client's active stream of payments
    mock_bank_transactions = pd.DataFrame([
        {"tx_id": "TXN001", "user_id": "USR_890", "amount": 4500},
        {"tx_id": "TXN002", "user_id": "USR_112", "amount": 12500},  # Violates limit
        {"tx_id": "TXN003", "user_id": "USR_445", "amount": 9900},
        {"tx_id": "TXN004", "user_id": "USR_671", "amount": 22000}   # Violates limit
    ])

    print("=== STEP 1: PARSING OFFICIAL REGULATOR API ===")
    rbi_feed_data = fetch_latest_rbi_directives()
# Check what columns exist before printing to avoid errors
available_cols = [col for col in ['title', 'published'] if col in rbi_feed_data.columns]
if available_cols:
    print(rbi_feed_data[available_cols].to_string(), "\n")
else:
    print(rbi_feed_data.to_string(), "\n")
    print("=== STEP 2: AI SCANNING FOR LEGAL RISK TRIGGERS ===")
    detected_policy_shifts = scan_for_risk_triggers(rbi_feed_data, compliance_watch_list)
    if not detected_policy_shifts.empty:
        print(detected_policy_shifts.to_string(), "\n")
    else:
        print("[+] System Normal: No high-risk macro policy changes matching your criteria today.\n")

    print("=== STEP 3: RUNNING CONTINUOUS TRANSACTION AUDIT ===")
    compliance_violations = audit_live_transactions(mock_bank_transactions, CURRENT_REGULATORY_CAP)
    if not compliance_violations.empty:
        print("\n[🚨] ALERT: SYSTEM BLOCKED COMPLIANCE VIOLATIONS DETECTED:")
        print(compliance_violations.to_string())
    else:
        print("[+] System Clean: 100% of transactions conform to active legal restrictions.")
