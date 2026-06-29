import io
import sqlite3
import pandas as pd
import feedparser
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# =====================================================================
# DATABASE STORAGE LAYER
# =====================================================================
DB_FILE = "regsecure.db"

def init_db():
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

# =====================================================================
# INTELLIGENCE PARSING LOGIC ENGINE
# =====================================================================
def assign_risk_and_action(title, regulator):
    title_lower = title.lower()
    reg_short = "RBI" if "rbi" in regulator.lower() else ("SEBI" if "sebi" in regulator.lower() else "PFRDA")
    
    if any(k in title_lower for k in ["cyber", "security", "atm", "fraud", "vulnerability", "it-risk", "breach"]):
        return "🔴 HIGH", f"[{reg_short} CRITICAL] Enforce immediate technical audits, deploy mandatory MFA protocols, and submit status report to security officers within 15 days."
    elif any(k in title_lower for k in ["kyc", "customer", "aml", "disclosure", "insider", "audit", "master direction"]):
        return "🟡 MEDIUM", f"[{reg_short} COMPLIANCE] Update organizational operational frameworks, run system validation tests on internal databases, and host review workshops."
    else:
        return "🟢 LOW", f"[{reg_short} NOTICE] Record this regulatory change in quarterly compliance registers and archive files safely for legal tracking."

def fetch_regulatory_directives(regulator):
    directives = []
    rss_feed_mapping = {
        "RBI": "https://rbi.org.in", 
        "SEBI": "https://sebi.gov.in",
        "PFRDA": "https://pfrda.org.in"
    }
    
    reg_key = "RBI" if "RBI" in regulator else ("SEBI" if "SEBI" in regulator else "PFRDA")
    feed_url = rss_feed_mapping[reg_key]
    
    try:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            for entry in feed.entries[:4]:
                summary_text = entry.get("summary", entry.get("description", "No brief overview available."))
                directives.append({
                    "title": entry.get("title", "Untitled Alert"),
                    "summary": summary_text[:120] + "...",
                    "link": entry.get("link", "https://rbi.org.in")
                })
    except Exception:
        pass

    if not directives:
        if reg_key == "RBI":
            directives = [
                {"title": "Master Direction - Cyber Security Controls for Third-Party ATM Apps", "summary": "Guidelines detailing MFA requirements for switches.", "link": "https://rbi.org.in"},
                {"title": "Amendment to Master Direction on Know Your Customer (KYC)", "summary": "Updates regarding periodic updation of low-risk accounts.", "link": "https://rbi.org.in"},
                {"title": "Opening of New Branches and Core Banking Migration Guidelines", "summary": "Administrative procedural updates for expansions.", "link": "https://rbi.org.in"}
            ]
        elif reg_key == "SEBI":
            directives = [
                {"title": "Prohibition of Insider Trading (PIT) Structural Guidelines Update", "summary": "Tightening controls around tracking databases.", "link": "https://sebi.gov.in"},
                {"title": "Mutual Fund Transparency & Enhanced Portfolio Disclosure Norms", "summary": "New mandates requiring comprehensive expense ratios tracking.", "link": "https://sebi.gov.in"}
            ]
        else:
            directives = [
                {"title": "PFRDA National Pension System (NPS) Digital Exit Protocols", "summary": "Streamlining computational verification framework via facial recognition APIs.", "link": "https://pfrda.org.in"}
            ]
            
    processed_records = []
    for item in directives:
        risk, action = assign_risk_and_action(item["title"], regulator)
        processed_records.append({
            "Source": reg_key,
            "Title": item["title"],
            "Summary": item["summary"],
            "Risk Level": risk,
            "Recommended Action": action,
            "Link": item["link"],
            "Published": datetime.now().strftime("%Y-%m-%d")
        })
        
    return pd.DataFrame(processed_records)

# =====================================================================
# MAIN USER INTERFACE HOOK
# =====================================================================
st.set_page_config(page_title="RegSecure AI Dashboard", layout="wide")

st.title("🛡️ RegSecure AI Enterprise Platform")
st.markdown("### Multi-Regulatory Compliance Matrix & Autonomous Response Center")

# Filter Navigation control unit
selected_agency = st.selectbox(
    "Switch Active Regulatory Intelligence Feed:", 
    ["Reserve Bank of India (RBI)", "Securities & Exchange Board (SEBI)", "Pension Fund Authority (PFRDA)"]
)

# Pull data tables securely
combined_df = fetch_regulatory_directives(selected_agency)

# 🛠️ INSTANT FIX: Text keyword search data processing filter implementation
search_query = st.text_input("🔍 Search active monitoring datagrid by keyword instantly:", key="global_search_input")
if search_query:
    combined_df = combined_df[
        combined_df['Title'].str.contains(search_query, case=False, na=False) |
        combined_df['Summary'].str.contains(search_query, case=False, na=False)
    ]

st.markdown("---")
st.subheader("📊 Risk Profile Analytics")

# Structural logic processing block calculations
total_directives = len(combined_df)
high_risk_count = len(combined_df[combined_df["Risk Level"].str.contains("HIGH")]) if total_directives > 0 else 0
med_risk_count = len(combined_df[combined_df["Risk Level"].str.contains("MEDIUM")]) if total_directives > 0 else 0
low_risk_count = len(combined_df[combined_df["Risk Level"].str.contains("LOW")]) if total_directives > 0 else 0

# Split grid window layout explicitly to ensure spacing stability
col_chart, col_metrics = st.columns([3, 2])

with col_chart:
    # 🛠️ INSTANT FIX: Static Text mapping to prevent text trimming or canvas bounds collisions
    chart_df = pd.DataFrame({
        'Count': [high_risk_count, med_risk_count, low_risk_count],
        'Priority Level': ['High Risk', 'Medium Risk', 'Low Notice']
    }).set_index('Priority Level')
    st.bar_chart(chart_df, color="#1A365D", use_container_width=True)

with col_metrics:
    # 🛠️ INSTANT FIX: Encapsulated cleanly in dedicated metrics metrics block row layers
    st.metric(label="Total Logged Items", value=str(total_directives))
    st.metric(label="High Risk Priority", value=str(high_risk_count))
    st.metric(label="Medium Risk Priority", value=str(med_risk_count))
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Adaptive status alert engine
    if high_risk_count >= 2:
        st.error("🚨 **AI Threat Assessment Level: ELEVATED CRISIS**")
    elif high_risk_count == 1:
        st.warning("⚡ **AI Threat Assessment Level: GUARDED / MONITORING**")
    else:
        st.success("🌐 **AI Threat Assessment Level: STABLE**")

st.markdown("---")
st.subheader("📋 Auditable Compliance Work-hub")

# 🛠️ INSTANT FIX: Absolute defense boundary layout safeguard loop block
if combined_df.empty:
    st.warning("⚠️ No regulatory matches found matching your active keyword query criteria matrix.")
else:
    for index, row in combined_df.iterrows():
        task_unique_key = f"task_{row['Source']}_{index}_{row['Title'][:10].replace(' ', '_').lower()}"
        current_saved_db_state = get_task_state(task_unique_key, default=False)
        
        with st.expander(f"{row['Risk Level']} - {row['Title']}", expanded=True):
            c_text, c_box = st.columns([5, 1])
            with c_text:
                st.write(f"**Summary:** {row['Summary']}")
                st.info(f"⚡ **Action:** {row['Recommended Action']}")
            with c_box:
                checked_status = st.checkbox("Attested", value=current_saved_db_state, key=f"w_{task_unique_key}")
                if checked_status != current_saved_db_state:
                    save_task_state(task_unique_key, checked_status)
                    st.rerun()
