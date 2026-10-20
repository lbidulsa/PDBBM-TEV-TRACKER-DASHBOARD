import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# PAGE CONFIGURATION & CUSTOM STYLING (GLOWING EFFECTS INJECTED)
# ---------------------------------------------------------
st.set_page_config(
    page_title="PDBBM TEV Tracker Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #F4F6F9; }
    .main-title { font-size: 26px; font-weight: 800; color: #1F4E78; margin-bottom: 5px; }
    .sub-title { font-size: 14px; color: #5A6A85; margin-bottom: 20px; }
    
    /* 🌟 METRIC CARDS WITH RED GLOW / SIGA-SIGA EFFECT */
    .stMetric { 
        background-color: #FFFFFF !important; 
        padding: 16px !important; 
        border-radius: 12px !important; 
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    .stMetric:hover {
        transform: translateY(-4px) scale(1.02) !important;
        border-color: #E53E3E !important;
        box-shadow: 0 0 15px rgba(229, 62, 62, 0.6), 0 0 25px rgba(229, 62, 62, 0.3) !important;
    }
    
    /* 🌟 BUTTONS WITH HOVER GLOW / SIGA EFFECT */
    div.stButton > button, 
    div.stFormSubmitButton > button,
    div.stDownloadButton > button {
        background-color: #E2E8F0 !important;
        color: #0F2A4A !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        padding: 8px 20px !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    
    div.stButton > button:hover, 
    div.stFormSubmitButton > button:hover,
    div.stDownloadButton > button:hover {
        background-color: #FFFFFF !important;
        color: #C53030 !important;
        border-color: #E53E3E !important;
        box-shadow: 0 0 15px rgba(229, 62, 62, 0.6), 0 0 25px rgba(229, 62, 62, 0.3) !important;
        transform: translateY(-2px) scale(1.01) !important;
    }
    
    div.stButton > button:active, 
    div.stFormSubmitButton > button:active,
    div.stDownloadButton > button:active {
        transform: translateY(1px) scale(0.99) !important;
        box-shadow: 0 0 5px rgba(229, 62, 62, 0.4) !important;
    }

    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] {
        background-color: #0F2A4A !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label {
        color: #E2E8F0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GOOGLE SHEETS LIVE CSV LINK
# ---------------------------------------------------------
PUBLISHED_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuXeMfsAR6xhb8rZXb_k-NJcERcbE7om2O7isdpHI_VpD6EdnJyT5kK6wFHjK0z7zMugyztwW4l-J-/pub?gid=656688492&single=true&output=csv"

@st.cache_data(ttl=60)  # Auto refresh data every 60 seconds
def load_tev_data():
    try:
        df = pd.read_csv(PUBLISHED_CSV_URL)
        # Clean column headers (remove leading/trailing spaces)
        df.columns = [str(col).strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Error fetching live Google Sheet data: {e}")
        return pd.DataFrame()

# ---------------------------------------------------------
# SIDEBAR CREDITS
# ---------------------------------------------------------
st.sidebar.title("✈️ PDBBM TEV Portal")
st.sidebar.markdown("Live AppSheet & Google Sheets Synchronization")
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align: center; font-size: 0.8em; color: #CBD5E1;">
        💻 <b>System Developer & Architect</b><br>
        Developed with ❤️ by <br><b style="color:#00E6FF;">LOUIE B. IDULSA - PDBBM ITO I</b><br>
        <i>DSWD FO X • 2026</i>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# HEADER & SYNC BUTTON
# ---------------------------------------------------------
c_hdr1, c_hdr2 = st.columns([3, 1])
with c_hdr1:
    st.markdown('<div class="main-title">✈️ PDBBM TEV Tracker Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Live Executive Tracking for Traveling Expenses Vouchers (AppSheet Connected)</div>', unsafe_allow_html=True)

with c_hdr2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Sync / Refresh AppSheet Data", use_container_width=True):
        st.cache_data.clear()
        st.toast("⚡ Refreshed latest TEV records!", icon="🔄")
        st.rerun()

st.markdown("---")

df_tev = load_tev_data()

# ---------------------------------------------------------
# DASHBOARD METRICS & CHARTS DISPLAY
# ---------------------------------------------------------
if not df_tev.empty:
    # Auto-detect numeric and status columns if available
    amt_col = next((c for c in df_tev.columns if 'amount' in c.lower() or 'tev' in c.lower() or 'cost' in c.lower()), None)
    status_col = next((c for c in df_tev.columns if 'status' in c.lower() or 'state' in c.lower()), None)
    name_col = next((c for c in df_tev.columns if 'name' in c.lower() or 'payee' in c.lower() or 'personnel' in c.lower() or 'employee' in c.lower()), None)

    # 1. Summary Metrics with Siga-siga Effect
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total TEV Records", f"{len(df_tev):,}")
        
    with m2:
        if amt_col:
            # Convert to numeric safely
            df_tev[amt_col] = pd.to_numeric(df_tev[amt_col].astype(str).str.replace(',', '').str.replace('₱', ''), errors='coerce').fillna(0)
            tot_amt = df_tev[amt_col].sum()
            st.metric("Total Amount Claimed", f"₱{tot_amt:,.2f}")
        else:
            st.metric("Total Columns Detected", len(df_tev.columns))
            
    with m3:
        if status_col:
            pending_cnt = len(df_tev[df_tev[status_col].astype(str).str.contains('Pending|Process|Ongoing', case=False, na=False)])
            st.metric("Pending Vouchers", f"{pending_cnt:,}")
        else:
            st.metric("Total Entries", f"{len(df_tev):,}")

    with m4:
        if status_col:
            app_cnt = len(df_tev[df_tev[status_col].astype(str).str.contains('Approved|Completed|Paid|Released', case=False, na=False)])
            st.metric("Approved / Paid", f"{app_cnt:,}")
        else:
            st.metric("Last Updated", datetime.date.today().strftime("%b %d, %Y"))

    st.markdown("---")

    # 2. Interactive Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 Vouchers Status Breakdown")
        if status_col:
            fig_status = px.pie(df_tev, names=status_col, hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("ℹ️ Status column not detected for Pie Chart.")

    with col_chart2:
        st.subheader("💰 TEV Amount Distribution")
        if name_col and amt_col:
            top_df = df_tev.groupby(name_col)[amt_col].sum().reset_index().sort_values(by=amt_col, ascending=False).head(10)
            fig_bar = px.bar(top_df, x=name_col, y=amt_col, text_auto=',.2f', color=amt_col, color_continuous_scale="Blues")
            st.plotly_chart(fig_bar, use_container_width=True)
        elif amt_col:
            fig_hist = px.histogram(df_tev, x=amt_col, nbins=15, color_discrete_sequence=['#1F4E78'])
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("ℹ️ Amount column not detected for Bar Chart.")

    st.markdown("---")

    # 3. Searchable Live Data Masterlist
    st.subheader("📋 Live TEV Records Masterlist (AppSheet Connected)")
    
    search_term = st.text_input("🔍 Quick Keyword Search across all fields:", "")
    df_display = df_tev.copy()
    
    if search_term:
        mask = df_display.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)
        df_display = df_display[mask]

    st.dataframe(df_display, use_container_width=True)

    # 4. Export Options
    st.markdown("##### 📥 Export Live Records")
    csv_data = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Download Extracted CSV Report",
        data=csv_data,
        file_name=f"TEV_Tracker_Report_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=False
    )

else:
    st.warning("⚠️ Waiting for data... Unable to load records from the published link.")

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; font-size: 0.85em; color: #6c757d; padding-bottom: 20px;">
        ✈️ <b>PDBBM TEV Tracker Dashboard</b> | AppSheet Live Google Sheet Integration<br>
        Developed by <b>LOUIE B. IDULSA - PDBBM ITO I</b> • DSWD Field Office X
    </div>
    """,
    unsafe_allow_html=True
)