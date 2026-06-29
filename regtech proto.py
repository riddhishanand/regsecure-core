import io
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# =====================================================================
# 1. DATABASE LAYER (SQLite Initialization & Persistence Engine)
# =====================================================================
DB_FILE = "regsecure.db"

def init_db():
    """Initializes local secure storage tables for tasks."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_states (
            task_key TEXT PRIMARY KEY,
            is_checked INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def get_task_state(key, default=False):
    """Loads a checklist state from the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT is_checked FROM task_states WHERE task_key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        if row is not None:
            return bool(row[0])
    except Exception:
        pass
    return default

def save_task_state(key, val):
    """Saves a checklist state permanently into the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO task_states (task_key, is_checked)
            VALUES (?, ?)
            ON CONFLICT(task_key) DO UPDATE SET is_checked = excluded.is_checked
        ''', (key, int(val)))
        conn.commit()
        conn.close()
    except Exception:
        pass

init_db()

def assign_risk_and_action(title, regulator):
    """Rule-based engine to tag risk levels and generate tailored action items."""
    title_lower = title.lower()
    reg_short = "RBI" if "RBI" in regulator else ("SEBI" if "SEBI" in regulator else "PFRDA")
    
    if any(k in title_lower for k in ["cyber", "security", "atm", "fraud", "vulnerability"]):
        return "🔴 HIGH", f"[{reg_short} CRITICAL] Enforce immediate technical audits, deploy mandatory MFA protocols, and submit status report to security officers within 15 days."
    elif any(k in title_lower for k in ["kyc", "customer", "aml", "disclosure", "insider", "audit"]):
        return "🟡 MEDIUM", f"[{reg_short} COMPLIANCE] Update organizational operational frameworks, run system validation tests on internal databases, and host review workshops."
    else:
        return "🟢 LOW", f"[{reg_short} NOTICE] Record this regulatory change in quarterly compliance registers and archive files safely for legal tracking."

def fetch_regulatory_directives(regulator):
    """Generates instant, localized compliance matrix profiles without network delay flags."""
    directives = []
    
    if "RBI" in regulator:
        raw_data = [
            {"title": "Master Direction - Cyber Security Controls for Third-Party ATM Apps", "summary": "Compliance guidelines detailing multifactor authentication requirements for financial switches.", "link": "https://rbi.org.in"},
            {"title": "Amendment to Master Direction on Know Your Customer (KYC)", "summary": "Updates regarding periodic updation of KYC for low-risk accounts via digital channels.", "link": "https://rbi.org.in"},
            {"title": "Opening of New Branches and Core Banking Migration Guidelines", "summary": "Administrative procedural updates for banking expansions into tier-3 semi-urban localities.", "link": "https://rbi.org.in"}
        ]
    elif "SEBI" in regulator:
        raw_data = [
            {"title": "Prohibition of Insider Trading (PIT) Structural Guidelines Update", "summary": "Tightening controls around digital tracking databases for specified connected corporate individuals.", "link": "https://sebi.gov.in"},
            {"title": "Mutual Fund Transparency & Enhanced Portfolio Disclosure Norms", "summary": "New mandates requiring comprehensive asset and expense ratios tracking updates weekly.", "link": "https://sebi.gov.in"}
        ]
    else:
        raw_data = [
            {"title": "PFRDA National Pension System (NPS) Digital Exit Protocols", "summary": "Streamlining computational verification framework via facial recognition APIs on point-of-presence desks.", "link": "https://pfrda.org.in"}
        ]
        
    for item in raw_data:
        risk, action = assign_risk_and_action(item["title"], regulator)
        directives.append({
            "Source": regulator,
            "Title": item["title"],
            "Summary": item["summary"],
            "Risk Level": risk,
            "Recommended Action": action,
            "Link": item["link"],
            "Published": datetime.now().strftime("%Y-%m-%d")
        })
        
    return pd.DataFrame(directives)

def generate_pdf_report(df, regulator):
    """Generates a professional executive-ready PDF report buffer."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor("#1A365D"), spaceAfter=10)
    sub_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#4A5568"), spaceAfter=20)
    body_style = ParagraphStyle('TableBody', parent=styles['Normal'], fontSize=8, leading=10)
    
    story.append(Paragraph("🛡️ RegSecure AI Executive Compliance Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Target Agency: {regulator}", sub_style))
    story.append(Spacer(1, 10))
    
    table_data = [["Risk Priority", "Regulatory Alert Directive Details"]]
    for _, row in df.iterrows():
        content_text = f"<b>{row['Title']}</b><br/><i>Summary:</i> {row['Summary']}<br/><b>Required Action:</b> {row['Recommended Action']}"
        table_data.append([
            Paragraph(f"<b>{row['Risk Level']}</b>", body_style),
            Paragraph(content_text, body_style)
        ])
    
    rbi_table = Table(table_data, colWidths=[100, 430])
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

# =====================================================================
# 2. LOGIN SECURITY LAYER
# =====================================================================
st.set_page_config(page_title="RegSecure AI Dashboard", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<div style='padding-top:50px;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col2:
        st.info("### 🔐 RegSecure AI Portal Sign-In")
        username = st.text_input("Username:", value="admin")
        password = st.text_input("Password:", type="password", value="admin123")
        if st.button("Access Dashboard", use_container_width=True):
            if username == "admin" and password == "admin123":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Invalid operational credentials. Please try again.")
    st.stop()

# =====================================================================
# 3. MAIN DASHBOARD UI DISPLAY LAYER (Authenticated User)
# =====================================================================
st.title("🛡️ RegSecure AI Enterprise Platform")
st.subheader("Multi-Regulatory Compliance Matrix & Autonomous Response Center")

selected_regulator = st.selectbox(
    "🌐 Switch Active Regulatory Intelligence Feed:",
    ["Reserve Bank of India (RBI)", "Securities and Exchange Board of India (SEBI)", "Pension Fund Regulatory and Development Authority (PFRDA)"]
)

df_directives = fetch_regulatory_directives(selected_regulator)

# =====================================================================
# 4. DATA VISUALIZATION ENGINE (Analytical Distribution Charts)
# =====================================================================
st.write("### 📊 Risk Profile Analytics")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    risk_counts = df_directives["Risk Level"].value_counts()
    chart_data = pd.DataFrame({
        "Risk Priority": risk_counts.index,
        "Alert Count": risk_counts.values
    }).set_index("Risk Priority")
    st.bar_chart(chart_data, color="#1A365D")

with chart_col2:
    st.markdown("<div style='padding-top:10px;'></div>", unsafe_allow_html=True)
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(label="Total Logged Items", value=len(df_directives))
    col_m2.metric(label="High Risk Priority", value=len(df_directives[df_directives['Risk Level'].str.contains("🔴")]))
    col_m3.metric(label="Medium Risk Priority", value=len(df_directives[df_directives['Risk Level'].str.contains("🟡")]))
    st.success("🤖 AI Threat Assessment Level: STABLE")

st.write("---")

col_a, col_b = st.columns(2)
with col_a:
    search_query = st.text_input("🔍 Search active monitoring datagrid by keyword instantly:", "")
with col_b:
    st.write("<div style='padding-top:25px;'></div>", unsafe_allow_html=True)
