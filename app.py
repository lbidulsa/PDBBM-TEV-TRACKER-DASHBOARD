import datetime
import re
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION (DAPAT UNANG-UNA!)
# ---------------------------------------------------------
st.set_page_config(
    page_title="PDBBM TEV Executive Tracker",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. GOOGLE SHEETS LIVE CSV LINK & APPSHEET CONFIG
# ---------------------------------------------------------
PUBLISHED_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuXeMfsAR6xhb8rZXb_k-NJcERcbE7om2O7isdpHI_VpD6EdnJyT5kK6wFHjK0z7zMugyztwW4l-J-/pub?gid=656688492&single=true&output=csv"[cite: 5]
APPSHEET_APP_NAME = "PDBBM-RPMODocumentTracker-270708318"

@st.cache_data(ttl=30)
def load_tev_data():
    try:
        df = pd.read_csv(PUBLISHED_CSV_URL)[cite: 5]
        df.columns = [str(col).strip() for col in df.columns][cite: 5]
        return df
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return pd.DataFrame()

# Smart Image / Document URL Parser para sa AppSheet & Google Drive Files
def format_appsheet_file_url(val):
    if pd.isna(val) or not str(val).strip():
        return None, None
    val_str = str(val).strip()
    
    # 1. Google Drive direct file ID match
    drive_match = re.search(r'(?:id=|\/d\/)([a-zA-Z0-9_-]+)', val_str)
    if drive_match:
        file_id = drive_match.group(1)
        embed_url = f"https://drive.google.com/uc?export=view&id={file_id}"
        view_url = f"https://drive.google.com/file/d/{file_id}/view"
        return embed_url, view_url
    
    # 2. Direct Web URL (http/https)
    if val_str.startswith("http://") or val_str.startswith("https://"):
        return val_str, val_str
        
    # 3. AppSheet Template GetTableFileUrl relative path conversion
    encoded_path = val_str.replace(" ", "%20").replace("/", "%2F")
    appsheet_url = f"https://www.appsheet.com/template/gettablefileurl?appName={APPSHEET_APP_NAME}&fileName={encoded_path}"
    return appsheet_url, appsheet_url

# Load Data
df_tev = load_tev_data()

# ---------------------------------------------------------
# 3. HIGH-CONTRAST DARK THEME CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp { 
        background-color: #0B132B !important; 
        color: #FFFFFF !important;
    }
    
    /* Header Card */
    .header-card {
        background: #1C2541;
        border: 2px solid #3A506B;
        border-radius: 12px;
        padding: 20px 25px;
        margin-bottom: 20px;
    }
    .header-title { font-size: 28px; font-weight: 900; color: #6FFFE9; }
    .header-sub { font-size: 15px; color: #E0E6ED; font-weight: 500; }

    /* High Contrast Metric Cards */
    .metric-card {
        background: #1C2541;
        border: 2px solid #3A506B;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .metric-value { font-size: 26px; font-weight: 900; color: #6FFFE9; margin-top: 5px; }
    .metric-label { font-size: 13px; font-weight: 700; color: #FFFFFF; text-transform: uppercase; }

    /* Buttons */
    div.stButton > button, div.stDownloadButton > button {
        background-color: #5BC0BE !important;
        color: #0B132B !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 20px !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background-color: #6FFFE9 !important;
        color: #000000 !important;
        box-shadow: 0 0 15px rgba(111, 255, 233, 0.6) !important;
    }

    /* Expander Text Styling */
    .stExpander {
        background-color: #1C2541 !important;
        border: 1px solid #3A506B !important;
        border-radius: 10px !important;
    }
    
    /* Text Visibility Fix */
    label, p, span, h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.markdown("### ✈️ PDBBM TEV Portal")
st.sidebar.caption("AppSheet Live Synchronization")
st.sidebar.markdown("---")

if st.sidebar.button("🔄 Sync / Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.toast("⚡ Refreshed latest TEV records!", icon="🔄")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("#### 🎯 Quick Program Filter")

program_col = next((c for c in df_tev.columns if 'program' in c.lower() or 'office' in c.lower() or 'unit' in c.lower()), None)
selected_program = "All Programs"

if not df_tev.empty and program_col:
    prog_list = ["All Programs"] + sorted([str(p) for p in df_tev[program_col].dropna().unique() if str(p).strip() != ""])
    selected_program = st.sidebar.selectbox("Select Program / Office:", prog_list)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align: center; font-size: 0.85em; color: #E0E6ED;">
        💻 <b>System Architect</b><br>
        Developed by <br><b style="color:#6FFFE9;">LOUIE B. IDULSA - PDBBM ITO I</b><br>
        <i>DSWD FO X • 2026</i>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 5. MAIN HEADER
# ---------------------------------------------------------
st.markdown("""
    <div class="header-card">
        <div class="header-title">✈️ PDBBM TEV Executive Tracker</div>
        <div class="header-sub">Live Executive Dashboard • AppSheet Connected</div>
    </div>
""", unsafe_allow_html=True)

if not df_tev.empty:
    if selected_program != "All Programs" and program_col:
        df_filtered = df_tev[df_tev[program_col].astype(str) == selected_program].copy()
    else:
        df_filtered = df_tev.copy()

    # Column Auto-Detect
    drn_col = next((c for c in df_tev.columns if 'drn' in c.lower() or 'voucher' in c.lower() or 'id' in c.lower()), df_tev.columns[0])
    name_col = next((c for c in df_tev.columns if 'et.al' in c.lower() or 'etal' in c.lower() or 'name' in c.lower() or 'payee' in c.lower() or 'claimant' in c.lower()), df_tev.columns[1] if len(df_tev.columns) > 1 else df_tev.columns[0])
    amt_col = next((c for c in df_tev.columns if 'amount' in c.lower() or 'tev' in c.lower() or 'total' in c.lower()), None)
    overall_status_col = next((c for c in df_tev.columns if 'status' in c.lower() or 'state' in c.lower()), None)
    img_col = next((c for c in df_tev.columns if 'image' in c.lower() or 'attach' in c.lower() or 'photo' in c.lower() or 'file' in c.lower() or 'picture' in c.lower()), None)

    if amt_col:
        df_filtered[amt_col] = pd.to_numeric(df_filtered[amt_col].astype(str).str.replace(',', '').str.replace('₱', ''), errors='coerce').fillna(0)

    # Top Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Vouchers</div>
                <div class="metric-value">{len(df_filtered):,}</div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        tot_val = df_filtered[amt_col].sum() if amt_col else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Amount</div>
                <div class="metric-value">₱{tot_val:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        pend_cnt = len(df_filtered[df_filtered[overall_status_col].astype(str).str.contains('Pending|Ongoing|Process', case=False, na=False)]) if overall_status_col else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">In Progress</div>
                <div class="metric-value" style="color:#FFD166;">{pend_cnt:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        app_cnt = len(df_filtered[df_filtered[overall_status_col].astype(str).str.contains('Approved|Completed|Paid|Released', case=False, na=False)]) if overall_status_col else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Completed / Paid</div>
                <div class="metric-value" style="color:#06D6A0;">{app_cnt:,}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Instant Search Bar
    search_query = st.text_input("🔍 Quick Search (DRN #, Claimant / Et. Al, Station, Status, etc.):", "")

    if search_query:
        search_mask = df_filtered.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        df_searched = df_filtered[search_mask]
    else:
        df_searched = df_filtered

    st.markdown("---")

    # Interactive Records Card
    st.subheader(f"📋 TEV Claim Records ({len(df_searched)})")

    if df_searched.empty:
        st.info("Walay nakita nga TEV record base sa imong gi-search.")
    else:
        for idx, row in df_searched.iterrows():
            drn_val = str(row.get(drn_col, 'N/A'))
            name_val = str(row.get(name_col, 'N/A'))
            amt_val = f"₱{float(row.get(amt_col, 0)):,.2f}" if amt_col else "N/A"
            status_val = str(row.get(overall_status_col, 'In Process')) if overall_status_col else 'Logged'

            # Header format: DRN | Name (Et. Al) | Amount | Status
            expander_title = f"📄 DRN: {drn_val}  |  Claimant/Et.Al: {name_val}  |  Amount: {amt_val}  |  Status: {status_val}"

            with st.expander(expander_title, expanded=False):
                col_info, col_status, col_attach = st.columns([2, 2, 1.5])

                with col_info:
                    st.markdown("##### 📌 Basic Information")
                    for c in df_tev.columns[:6]:
                        st.write(f"**{c}:** {row[c]}")

                with col_status:
                    st.markdown("##### 🏛️ Department Tracking & Remarks")
                    budget_col = next((c for c in df_tev.columns if 'budget' in c.lower()), None)
                    acct_col = next((c for c in df_tev.columns if 'account' in c.lower()), None)
                    cash_col = next((c for c in df_tev.columns if 'cash' in c.lower() or 'treasury' in c.lower()), None)
                    fin_col = next((c for c in df_tev.columns if 'finance' in c.lower()), None)
                    rem_col = next((c for c in df_tev.columns if 'remark' in c.lower() or 'note' in c.lower()), None)

                    st.markdown(f"• **Budget:** `{row.get(budget_col, 'Processed') if budget_col else 'In Process'}`")
                    st.markdown(f"• **Accounting:** `{row.get(acct_col, 'Pending Review') if acct_col else 'In Process'}`")
                    st.markdown(f"• **Cashier:** `{row.get(cash_col, 'Pending') if cash_col else 'For Disbursement'}`")
                    st.markdown(f"• **Finance:** `{row.get(fin_col, 'Ongoing') if fin_col else 'Pending Approval'}`")
                    
                    if rem_col and pd.notna(row.get(rem_col)):
                        st.info(f"💬 **Remarks:** {row.get(rem_col)}")

                with col_attach:
                    st.markdown("##### 📎 Attached Document / Et. Al List")
                    img_val = row.get(img_col) if img_col else None
                    embed_link, view_link = format_appsheet_file_url(img_val)

                    if embed_link or view_link:
                        st.markdown(f"📄 [**Open / View Attached File**]({view_link})")
                        if embed_link and any(ext in str(img_val).lower() for ext in ['.jpg', '.jpeg', '.png']):
                            st.image(embed_link, caption="Et. Al Attachment Preview", use_container_width=True)
                    else:
                        st.caption("ℹ️ Walay naka-attach nga document o image sa kining nga entry.")

    st.markdown("---")

    # Analytics & Masterlist Tabs
    tab1, tab2 = st.tabs(["📊 Analytics & Charts", "📥 Raw Masterlist Data"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Status Breakdown")
            if overall_status_col:
                fig1 = px.pie(df_filtered, names=overall_status_col, hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
                fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
                st.plotly_chart(fig1, use_container_width=True)

        with c2:
            st.subheader("💰 Top Claims Amount")
            if amt_col and name_col:
                top_10 = df_filtered.groupby(name_col)[amt_col].sum().reset_index().sort_values(by=amt_col, ascending=False).head(8)
                fig2 = px.bar(top_10, x=name_col, y=amt_col, text_auto=',.2f', color_discrete_sequence=['#6FFFE9'])
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("📋 Complete Table Data")
        st.dataframe(df_filtered, use_container_width=True)
        
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Export CSV Report",
            data=csv_data,
            file_name=f"TEV_Report_{datetime.date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    st.warning("⚠️ Waiting for data from Google Sheets link...")

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; font-size: 0.85em; color: #E0E6ED; padding-bottom: 20px;">
        ✈️ <b>PDBBM TEV Executive Tracker</b> | Real-time AppSheet Integration<br>
        Developed by <b>LOUIE B. IDULSA - PDBBM ITO I</b> • DSWD Field Office X
    </div>
    """,
    unsafe_allow_html=True
)
