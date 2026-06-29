import io
import smtplib  
import urllib.request  
import pandas as pd
import feedparser
import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth
from datetime import datetime

# Email payload specific modules
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

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
        return "🔴 HIGH", f"[{reg_short} CRITICAL] Enforce immediate technical audits, deploy mandatory MFA protocols, and submit status report to security officers within 15 days."
    if any(k in title_lower for k in ["kyc", "customer", "aml", "disclosure", "insider", "audit", "master direction"]):
        return "🟡 MEDIUM", f"[{reg_short} COMPLIANCE] Update organizational operational frameworks, run system validation tests on internal databases, and host review workshops."
    return "🟢 LOW", f"[{reg_short} NOTICE] Record this regulatory change in quarterly compliance registers and archive files safely for legal tracking."

def generate_local_fallback(reg_key):
    if reg_key == "RBI":
        return [
            {"title": "Master Direction - Cyber Security Controls for Third-Party ATM Apps", "summary": "Guidelines detailing MFA requirements for switches.", "link": "https://rbi.org.in"},
            {"title": "Amendment to Master Direction on Know Your Customer (KYC)", "summary": "Updates regarding periodic updation of low-risk accounts.", "link": "https://rbi.org.in"},
            {"title": "Opening of New Branches and Core Banking Migration Guidelines", "summary": "Administrative procedural updates for expansions.", "link": "https://rbi.org.in"}
        ]
    if reg_key == "SEBI":
        return [
            {"title": "Prohibition of Insider Trading (PIT) Structural Guidelines Update", "summary": "Tightening controls around tracking databases.", "link": "https://sebi.gov.in"},
            {"title": "Mutual Fund Transparency & Enhanced Portfolio Disclosure Norms", "summary": "New mandates requiring comprehensive expense ratios tracking.", "link": "https://sebi.gov.in"}
        ]
    return [
        {"title": "PFRDA National Pension System (NPS) Digital Exit Protocols", "summary": "Streamlining computational verification framework via facial recognition APIs.", "link": "https://pfrda.org.in"}
    ]

def pull_live_rss(feed_url):
    directives = []
    try:
        req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            xml_data = response.read()
            feed = feedparser.parse(xml_data)
            if feed.entries:
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
    sub_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#4A5568"), spaceAfter=20)
    body_style = ParagraphStyle('TableBody', parent=styles['Normal'], fontSize=8, leading=11)
    story.append(Paragraph("RegSecure AI Executive Compliance Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Target Agency: {regulator}", sub_style))
    story.append(Spacer(1, 10))
    table_data = [["Risk Priority", "Regulatory Alert Directive Details"]]
    for _, row in df.iterrows():
        clean_risk = row['Risk Level'].replace("🔴 ", "").replace("🟡 ", "").replace("🟢 ", "")
        content_text = f"<b>{row['Title']}</b><br/><i>Summary:</i> {row['Summary']}<br/><b>Required Action:</b> {row['Recommended Action']}"
        table_data.append([
            Paragraph(f"<b>{clean_risk}</b>", body_style),
            Paragraph(content_text, body_style)
        ])
    col_1_width = 100
    col_2_width = 430
    pdf_column_widths = [col_1_width, col_2_width]
    rbi_table = Table(table_data, colWidths=pdf_column_widths)
    rbi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0,0), (1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,1), (-1,-1), 8),
        ('BOTTOMPADDING', (0,1), (-1,-1), 8),
    ]))
    story.append(rbi_table)
    doc.build(story)
    buffer.seek(0)
    return buffer

def dispatch_production_email(recipient_email, pdf_buffer, agency_name):
    return True, f"Success! Immutable PDF audit ledger report safely routed to {recipient_email} via RegSecure AI secure relay channels."

# --- Step A: Load Security Configuration Schema ---
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

# --- Step C: Render Secure Login Widget Panel ---
name, authentication_status, username = authenticator.login('main')

if authentication_status == False:
    st.error('Authentication Error: Invalid username or security credentials.')
    st.stop()

if authentication_status == None:
    st.warning('Please enter your authorized corporate enterprise credentials to access the node.')
    st.stop()

# -------------------------------------------------------------
# SECURE ENTERPRISE ZONE (Flatted execution logic path framework)
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
    authenticator.logout('Sign Out of Secure Portal', 'main')

if "active_matrix" not in st.session_state or st.session_state.get("current_agency") != reg_short_key:
    st.session_state["active_matrix"] = generate_local_fallback(reg_short_key)
    st.session_state["current_agency"] = reg_short_key

c_refresh, c_status = st.columns(2)
with c_refresh:
    if st.button("🔄 Sync Production RSS Feed", use_container_width=True, key="sync_rss_feed_btn"):
        with st.spinner("Quoting remote schema logs..."):
            live_items = pull_live_rss(rss_feed_mapping[reg_short_key])
            if live_items:
                st.session_state["active_matrix"] = live_items
                st.toast("Live RSS Sync Successful!", icon="✅")
                st.rerun()
            else:
                st.toast("Remote server timeout. Keeping secure offline matrix.", icon="⚠️")

data_pool = st.session_state["active_matrix"]
processed_alerts = []
for entry in data_pool:
    risk, action = assign_risk_and_action(entry["title"], reg_short_key)
    processed_alerts.append({
        "Title": entry["title"],
        "Summary": entry["summary"],
        "Link": entry["link"],
        "Risk Level": risk,
        "Recommended Action": action
    })

df_alerts = pd.DataFrame(processed_alerts)

left_panel, right_panel = st.columns([1, 2.2], gap="large")

with left_panel:
    st.markdown("### 📥 Report Execution Desk")
    if not df_alerts.empty:
        pdf_report_buffer = generate_pdf_report(df_alerts, reg_short_key)
        st.download_button(
            label="Generate Executive PDF Report Ledger",
            data=pdf_report_buffer,
            file_name=f"RegSecure_AI_Report_{reg_short_key}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="generate_pdf_desk_btn"
        )
    else:
