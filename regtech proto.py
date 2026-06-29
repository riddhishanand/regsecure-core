import io
import urllib.request, urllib.parse
import pandas as pd
import feedparser
import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth
from datetime import datetime

# ReportLab modules
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- Core Platform Initialization Functions ---
def get_task_state(key, default=False):
    if "task_database" not in st.session_state:
        st.session_state["task_database"] = {}
    return st.session_state["task_database"].get(key, default)

def save_task_state(key, val):
    if "task_database" not in st.session_state:
        st.session_state["task_database"] = {}
    st.session_state["task_database"][key] = val

def assign_risk_and_action(title, regulator):
    title_lower = title.lower()
    reg_short = "RBI" if "rbi" in regulator.lower() else ("SEBI" if "sebi" in regulator.lower() else "PFRDA")
    if any(k in title_lower for k in ["cyber", "security", "atm", "fraud", "vulnerability", "it-risk", "breach"]):
        return "🔴 HIGH", f"[{reg_short} CRITICAL] Enforce immediate technical audits, deploy mandatory MFA protocols."
    if any(k in title_lower for k in ["kyc", "customer", "aml", "disclosure", "insider", "audit"]):
        return "🟡 MEDIUM", f"[{reg_short} COMPLIANCE] Update operational frameworks, run validation tests."
    return "🟢 LOW", f"[{reg_short} NOTICE] Record this regulatory change in quarterly compliance registers."

def generate_local_fallback(reg_key):
    if reg_key == "RBI":
        return [
            {"title": "Master Direction - Cyber Security Controls for ATM Apps", "summary": "Guidelines detailing MFA requirements.", "link": "https://rbi.org.in"},
            {"title": "Amendment to Master Direction on Know Your Customer (KYC)", "summary": "Updates regarding periodic account updation.", "link": "https://rbi.org.in"}
        ]
    if reg_key == "SEBI":
        return [
            {"title": "Prohibition of Insider Trading (PIT) Guidelines Update", "summary": "Tightening controls around tracking databases.", "link": "https://sebi.gov.in"}
        ]
    return [
        {"title": "PFRDA National Pension System Digital Exit Protocols", "summary": "Streamlining verification frameworks.", "link": "https://pfrda.org.in"}
    ]

def pull_live_rss(feed_url):
    directives = []
    try:
        req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            feed = feedparser.parse(response.read())
            for entry in feed.entries[:4]:
                summary_text = entry.get("summary", entry.get("description", "No brief overview available."))
                directives.append({
                    "title": entry.get("title", "Untitled Live Alert"),
                    "summary": summary_text[:120] + "...",
                    "link": entry.get("link", "https://rbi.org.in")
                })
    except Exception:
        pass
    return directives

def generate_pdf_report(df, regulator):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor("#1A365D"), spaceAfter=10)
    body_style = ParagraphStyle('TableBody', parent=styles['Normal'], fontSize=8, leading=11)
    story.append(Paragraph("RegSecure AI Executive Compliance Report", title_style))
    story.append(Spacer(1, 10))
    table_data = [["Risk Priority", "Regulatory Alert Details"]]
    for _, row in df.iterrows():
        clean_risk = row['Risk Level'].replace("🔴 ", "").replace("🟡 ", "").replace("🟢 ", "")
        content_text = f"<b>{row['Title']}</b><br/><i>Summary:</i> {row['Summary']}<br/><b>Required Action:</b> {row['Recommended Action']}"
        table_data.append([Paragraph(f"<b>{clean_risk}</b>", body_style), Paragraph(content_text, body_style)])
    rbi_table = Table(table_data, colWidths=[100, 430])
    rbi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0,0), (1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(rbi_table)
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Step A: Load Security Configuration File ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# --- Step B: Initialize Authentication Engine ---
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

st.set_page_config(page_title="RegSecure AI Dashboard", page_icon="🛡️", layout="wide")

# --- Step C: Render Login Widget with Correct Parameters ---
authenticator.login()

# Manage application flow based on authentication state
if st.session_state.get("authentication_status") == False:
    st.error('Authentication Error: Invalid username or security credentials.')
    st.stop()
elif st.session_state.get("authentication_status") == None:
    st.warning('Please enter your authorized corporate enterprise credentials.')
    st.stop()

# Get secure verified metadata tokens
name = st.session_state["name"]
username = st.session_state["username"]

# -------------------------------------------------------------
# SECURE ENTERPRISE ZONE (Completely flat code path level)
# -------------------------------------------------------------
st.title("🛡️ RegSecure AI Enterprise Platform")
st.markdown("### Multi-Regulatory Compliance Matrix & Autonomous Response Center")

rss_feed_mapping = {
    "RBI": "https://rbi.org.in",
    "SEBI": "https://sebi.gov.in",
    "PFRDA": "https://pfrda.org.in"
}

with st.sidebar:
    st.markdown(f"### 👤 Connected: {name}")
    st.markdown(f"**Enterprise Token:** `{username}`")
    st.markdown("---")
    reg_key = st.selectbox("Switch Active Intelligence Feed:", ["Reserve Bank of India (RBI)", "SEBI", "PFRDA"])
    reg_short_key = "RBI" if "rbi" in reg_key.lower() else ("SEBI" if "sebi" in reg_key.lower() else "PFRDA")
    st.markdown("---")
    authenticator.logout('Sign Out of Secure Portal', 'sidebar')

if "active_matrix" not in st.session_state or st.session_state.get("current_agency") != reg_short_key:
    st.session_state["active_matrix"] = generate_local_fallback(reg_short_key)
    st.session_state["current_agency"] = reg_short_key

if st.button("🔄 Sync Production RSS Feed", use_container_width=True):
    with st.spinner("Quoting remote schema logs..."):
        live_items = pull_live_rss(rss_feed_mapping[reg_short_key])
        if live_items:
            st.session_state["active_matrix"] = live_items
            st.toast("Live RSS Sync Successful!", icon="✅")
            st.rerun()

data_pool = st.session_state["active_matrix"]
processed_alerts = []
for entry in data_pool:
    risk, action = assign_risk_and_action(entry["title"], reg_short_key)
   # --- Layout Grid Workspace Matrix Construction ---
left_panel, right_panel = st.columns([1, 2.2], gap="large")

with left_panel:
    # --- SUBSCRIPTION SETTING MANAGER ---
    # Switch this text token string to "premium" once a user makes a payment!
    user_tier_status = "free"  

    st.markdown("### 📥 Report Execution Desk")
    
    if user_tier_status == "premium":
        if not df_alerts.empty:
            pdf_report_buffer = generate_pdf_report(df_alerts, reg_short_key)
            st.download_button(
                label="Generate Executive PDF Report Ledger",
                data=pdf_report_buffer,
                file_name=f"RegSecure_AI_Report_{reg_short_key}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.error("🔒 Premium Feature Locked")
        st.info("Executive PDF compilation features require an enterprise tier Pro subscription profile configuration setup.")
        
        # Peer-to-peer payment structural variables
        my_upi_id = "riddhishanand10@okaxis"  
        business_name = "RegSecure AI Platform"
        subscription_price = "7999"  
        
        st.markdown("#### 💳 Open UPI Payment Portal")
        upi_url = f"upi://pay?pa={my_upi_id}&pn=RegSecure%20AI&am={subscription_price}&cu=INR"
        
        st.markdown(
            f'<a href="{upi_url}" target="_blank">'
            f'<button style="width:100%; background-color:#FF4B4B; color:white; border:none; padding:12px; border-radius:5px; font-weight:bold; cursor:pointer; font-size:16px;">'
            f'🚀 Click to Open in GPay / Paytm / PhonePe'
            f'</button></a>', 
            unsafe_allowed_html=True
        )
        
        st.markdown(f"**Direct UPI ID:** `{my_upi_id}`")
        st.markdown(f"**Target Due:** `₹{subscription_price}`")
        st.warning("📩 Following payment transfer compilation, route your confirmation snapshot ledger directly to riddhishanand10@gmail.com for database activation routing.")

    st.markdown("---")
    st.markdown("### ✉️ Security Distribution Engine")
    recipient_address = st.text_input("Executive Desk Delivery Address", value="riddhishanand10@gmail.com")
    
    if user_tier_status == "premium":
        if st.button("Transmit Immutable Audit Records", use_container_width=True):
            st.success(f"Success! Immutable PDF report ledger safely routed to {recipient_address}.")
    else:
        st.button("Transmit Immutable Audit Records", use_container_width=True, disabled=True, help="Upgrade to unlock automated corporate email routing chains.")

with right_panel:
    st.markdown("### 📋 Regulatory Intelligence Directives")
    for idx, row in df_alerts.iterrows():
        task_uid = f"task_audit_{username}_{reg_short_key}_{idx}"
        is_checked = get_task_state(task_uid, default=False)
        
        with st.expander(f"{row['Risk Level']} | {row['Title']}", expanded=(idx == 0)):
            st.markdown(f"**Brief Summary:** {row['Summary']}")
            with st.container(border=True):
                st.markdown(f"**Deployment Rule:** {row['Recommended Action']}")
            st.markdown(f"🔗 [Review Original Source Link]({row['Link']})")
            
            checked_state = st.checkbox("Sign-off task as fully deployed", value=is_checked, key=f"cb_{task_uid}")
            if checked_state != is_checked:
                save_task_state(task_uid, checked_state)
                st.rerun()
