import datetime
import re
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="PDBBM TEV Executive Tracker",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# MODERN NEW LOOK CUSTOM CSS & GLOW EFFECTS
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp { 
        background: #0F172A; 
        color: #F8FAFC;
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .header-title { font-size: 28px; font-weight: 800; color: #38BDF8; margin-bottom: 5px; }
    .header-sub { font-size: 14px; color: #94A3B8; }

    /* Glowing Metric Cards */
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #38BDF8;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }
    .metric-value { font-size: 26px; font-weight: 800; color: #F8FAFC; margin: 8px 0; }
    .metric-label { font-size: 12px; font-weight: 600; color: #94A3B8; text-transform: uppercase; }

    /* Tracking Status Badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-approved { background: rgba(34, 197, 94, 0.2); color: #4ADE80; border: 1px solid #22C55E; }
    .badge-pending { background: rgba(234, 179, 8, 0.2); color: #FACC15; border: 1px solid #EAB308; }
    .badge-process { background: rgba(56, 189, 248, 0.2); color: #38BDF8; border: 1px solid #38BDF8; }

    /* Buttons Style */
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 22px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.6) !important;
    }

    /* Expander Card */
    .stExpander {
        background: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LIVE DATA LOAD
# ---------------------------------------------------------
PUBLISHED_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuXeMfsAR6xhb8rZXb_k-NJcERcbE7om2O7isdpHI_VpD6EdnJyT5kK6wFHjK0z7zMugyztwW4l-J-/pub?gid=656688492&single=true&output=csv"[cite: 5]

@st.cache_data(ttl=30)
def load_tev_data():
    try:
        df = pd.read_csv(PUBLISHED_CSV_URL)[cite: 5]
        df.columns = [str(col).strip() for col in df.columns][cite: 5]
        return df
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return pd.DataFrame()

# Helper function to convert Google Drive / AppSheet image links to direct image URLs
def format_drive_image_url(url_str):
    if pd.isna(url_str) or not isinstance(url_str, str):
        return None
    url_str = url_str.strip()
    match = re.search(r'(?:id=|\/d\/)([a-zA-Z0-9_-]+)', url_str)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w800"
    if url_str.startswith("http"):
        return url_str
    return None

df_tev = load_tev_data()

# ---------------------------------------------------------
# SIDEBAR NAVIGATION & FILTERS
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
    <div style="text-align: center; font-size: 0.8em; color: #94A3B8;">
        💻 <b>System Architect</b><br>
        Developed by <br><b style="color:#38BDF8;">LOUIE B. IDULSA - PDBBM ITO I</b><br>
        <i>DSWD FO X • 2026</i>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# HEADER SECTION
# ---------------------------------------------------------
st.markdown("""
    <div class="header-card">
        <div class="header-title">✈️ PDBBM TEV Interactive Tracking Portal</div>
        <div class="header-sub">Real-time status tracking across Budget, Accounting, Cashier & Finance Departments</div>
    </div>
""", unsafe_allow_html=True)

if not df_tev.empty:
    # Filter data by Program if selected
    if selected_program != "All Programs" and program_col:
        df_filtered = df_tev[df_tev[program_col].astype(str) == selected_program].copy()
    else:
        df_filtered = df_tev.copy()

    # Column mappings
    drn_col = next((c for c in df_tev.columns if 'drn' in c.lower() or 'voucher' in c.lower() or 'id' in c.lower()), df_tev.columns[0])
    name_col = next((c for c in df_tev.columns if 'name' in c.lower() or 'payee' in c.lower() or 'claimant' in c.lower() or 'personnel' in c.lower()), df_tev.columns[1] if len(df_tev.columns) > 1 else df_tev.columns[0])
    amt_col = next((c for c in df_tev.columns if 'amount' in c.lower() or 'tev' in c.lower() or 'total' in c.lower()), None)
    overall_status_col = next((c for c in df_tev.columns if 'status' in c.lower() or 'state' in c.lower()), None)
    img_col = next((c for c in df_tev.columns if 'image' in c.lower() or 'attach' in c.lower() or 'photo' in c.lower() or 'et.al' in c.lower() or 'file' in c.lower()), None)

    # Clean amount column
    if amt_col:
        df_filtered[amt_col] = pd.to_numeric(df_filtered[amt_col].astype(str).str.replace(',', '').str.replace('₱', ''), errors='coerce').fillna(0)

    # ---------------------------------------------------------
    # TOP METRIC CARDS
    # ---------------------------------------------------------
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
                <div class="metric-value" style="color:#FACC15;">{pend_cnt:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        app_cnt = len(df_filtered[df_filtered[overall_status_col].astype(str).str.contains('Approved|Completed|Paid|Released', case=False, na=False)]) if overall_status_col else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Completed / Paid</div>
                <div class="metric-value" style="color:#4ADE80;">{app_cnt:,}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SEARCH BAR (DRN #, Name, Station, etc.)
    # ---------------------------------------------------------
    search_query = st.text_input("🔍 Quick Search Voucher (Type DRN #, Claimant Name, Station, or Key terms):", "")

    if search_query:
        search_mask = df_filtered.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        df_searched = df_filtered[search_mask]
    else:
        df_searched = df_filtered

    st.markdown("---")

    # ---------------------------------------------------------
    # INTERACTIVE TEV CARDS WITH DEPARTMENT PIPELINE & ATTACHMENTS
    # ---------------------------------------------------------
    st.subheader(f"📋 TEV Claim Records ({len(df_searched)})")

    if df_searched.empty:
        st.info("No matching TEV voucher records found.")
    else:
        for idx, row in df_searched.iterrows():
            drn_val = str(row.get(drn_col, 'N/A'))
            name_val = str(row.get(name_col, 'N/A'))
            amt_val = f"₱{float(row.get(amt_col, 0)):,.2f}" if amt_col else "N/A"
            status_val = str(row.get(overall_status_col, 'In Process')) if overall_status_col else 'Logged'

            # Header label for expander
            expander_title = f"📄 DRN: {drn_val} | Claimant: {name_val} | Amount: {amt_val} | Status: {status_val}"

            with st.expander(expander_title, expanded=False):
                col_info, col_status, col_attach = st.columns([2, 2, 1.5])

                # Column 1: Voucher Basic Info
                with col_info:
                    st.markdown("##### 📌 Voucher Details")
                    for c in df_tev.columns[:6]:
                        st.write(f"**{c}:** {row[c]}")

                # Column 2: Department Status & Remarks (Budget, Accounting, Cash, Finance)
                with col_status:
                    st.markdown("##### 🏛️ Department Tracking & Remarks")
                    
                    # Auto-detect department specific columns if they exist in Google Sheet
                    budget_col = next((c for c in df_tev.columns if 'budget' in c.lower()), None)
                    acct_col = next((c for c in df_tev.columns if 'account' in c.lower()), None)
                    cash_col = next((c for c in df_tev.columns if 'cash' in c.lower() or 'treasury' in c.lower()), None)
                    fin_col = next((c for c in df_tev.columns if 'finance' in c.lower()), None)
                    rem_col = next((c for c in df_tev.columns if 'remark' in c.lower() or 'note' in c.lower()), None)

                    st.markdown(f"• **Budget Status:** `{row.get(budget_col, 'Updated / In Progress') if budget_col else 'Processed'}`")
                    st.markdown(f"• **Accounting Status:** `{row.get(acct_col, 'Pending Review') if acct_col else 'In Process'}`")
                    st.markdown(f"• **Cash / Treasury:** `{row.get(cash_col, 'Pending') if cash_col else 'For Disbursement'}`")
                    st.markdown(f"• **Finance Final:** `{row.get(fin_col, 'Ongoing') if fin_col else 'Pending Approval'}`")
                    
                    if rem_col and pd.notna(row.get(rem_col)):
                        st.info(f"💬 **Department Remarks:** {row.get(rem_col)}")

                # Column 3: AppSheet Image Attachment (Et. Al List / Documents)
                with col_attach:
                    st.markdown("##### 📎 Attached Document / Et. Al List")
                    if img_col and pd.notna(row.get(img_col)):
                        raw_img_link = str(row.get(img_col))
                        formatted_img = format_drive_image_url(raw_img_link)
                        
                        if formatted_img:
                            st.image(formatted_img, caption="Et. Al List / Attachment", use_container_width=True)
                            st.markdown(f"[🔗 Open Attachment Link]({raw_img_link})")
                        else:
                            st.caption("No valid image link found.")
                    else:
                        st.caption("No image/document attached in AppSheet entry.")

    st.markdown("---")

    # ---------------------------------------------------------
    # CHARTS & EXPORT MASTERLIST
    # ---------------------------------------------------------
    tab1, tab2 = st.tabs(["📊 Analytics & Charts", "📥 Full Table Data Export"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Status Breakdown")
            if overall_status_col:
                fig1 = px.pie(df_filtered, names=overall_status_col, hole=0.4, color_discrete_sequence=px.colors.qualitative.Dark24)
                fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("No Status column found for analytics.")

        with c2:
            st.subheader("💰 Top Claims Amount")
            if amt_col and name_col:
                top_10 = df_filtered.groupby(name_col)[amt_col].sum().reset_index().sort_values(by=amt_col, ascending=False).head(8)
                fig2 = px.bar(top_10, x=name_col, y=amt_col, text_auto=',.2f', color_discrete_sequence=['#38BDF8'])
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("📋 Raw Masterlist Table")
        st.dataframe(df_filtered, use_container_width=True)
        
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Filtered Report (.CSV)",
            data=csv_data,
            file_name=f"TEV_Executive_Report_{datetime.date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    st.warning("⚠️ Waiting for data from Google Sheets link...")

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; font-size: 0.85em; color: #64748B; padding-bottom: 20px;">
        ✈️ <b>PDBBM TEV Executive Tracker</b> | Real-time AppSheet & Google Sheets Dashboard<br>
        Developed by <b>LOUIE B. IDULSA - PDBBM ITO I</b> • DSWD Field Office X
    </div>
    """,
    unsafe_allow_html=True
)
