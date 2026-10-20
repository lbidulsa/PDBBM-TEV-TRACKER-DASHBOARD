import os
import datetime
import re
import io
import requests
from PIL import Image
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="PDBBM TEV Executive Tracker",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. GOOGLE SHEETS LIVE SYNC CONFIGURATION
# ---------------------------------------------------------
PUBLISHED_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuXeMfsAR6xhb8rZXb_k-NJcERcbE7om2O7isdpHI_VpD6EdnJyT5kK6wFHjK0z7zMugyztwW4l-J-/pub?gid=656688492&single=true&output=csv"
APPSHEET_APP_NAME = "PDBBM-RPMODocumentTracker-270708318"
APPSHEET_TABLE_NAME = "TEV"

@st.cache_data(ttl=20)
def load_tev_data():
    try:
        df = pd.read_csv(PUBLISHED_CSV_URL)
        df.columns = [str(col).strip() for col in df.columns]
        
        # Alisin ang mga empty rows
        df = df.dropna(how='all')
        
        # Detect DRN Column
        drn_c = df.columns[0]
        df = df[df[drn_c].notna() & (df[drn_c].astype(str).str.strip() != '') & (df[drn_c].astype(str).str.strip().str.upper() != 'NAN')]
        
        # Smart Date Sorting (Latest October first)
        date_c = None
        for c in df.columns:
            if any(k in c.lower() for k in ['date', 'time', 'received', 'created']):
                date_c = c
                break
        if not date_c and len(df.columns) > 1:
            date_c = df.columns[1]
            
        if date_c:
            df['parsed_date'] = pd.to_datetime(df[date_c], errors='coerce')
            df = df.sort_values(by='parsed_date', ascending=False, na_position='last').drop(columns=['parsed_date'])
        else:
            df = df.iloc[::-1]
            
        return df.reset_index(drop=True)
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return pd.DataFrame()

# Smart URL Parser para sa AppSheet File URL
def format_appsheet_file_url(val):
    if pd.isna(val) or not str(val).strip() or str(val).lower() == 'nan':
        return None
    val_str = str(val).strip()
    
    if val_str.startswith("http://") or val_str.startswith("https://"):
        return val_str

    drive_match = re.search(r'(?:id=|\/d\/)([a-zA-Z0-9_-]+)', val_str)
    if drive_match:
        file_id = drive_match.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"

    encoded_table = APPSHEET_TABLE_NAME.replace(" ", "%20")
    encoded_path = val_str.replace(" ", "%20").replace("/", "%2F")
    return f"https://www.appsheet.com/template/gettablefileurl?appName={APPSHEET_APP_NAME}&tableName={encoded_table}&fileName={encoded_path}"

# 🎯 Clean Physical Crop Function (I-crop ra ang gi-red box nga bahin: Header + Names + Inclusive Dates)
@st.cache_data(ttl=3600)
def get_clean_boxed_crop(img_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(img_url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return None
        
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        width, height = img.size
        
        # Precise Bounding Box para makuha ra ang Red Box Area (Walang Amount & Slashes)
        # Left: 0, Top: 0, Right: 67% width, Bottom: 88% height
        crop_area = (0, 0, int(width * 0.67), int(height * 0.88))
        cropped_img = img.crop(crop_area)
        
        return cropped_img
    except Exception:
        return None

def clean_val(val, default="---"):
    if pd.isna(val) or str(val).strip().lower() == 'nan' or not str(val).strip():
        return default
    return str(val).strip()

df_tev = load_tev_data()

# ---------------------------------------------------------
# 3. HIGH-CONTRAST NEON CYBERPUNK THEME
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp { 
        background-color: #080C14 !important; 
        color: #FFFFFF !important;
    }
    
    .header-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E1035 100%);
        border: 2px solid #00F5FF;
        border-radius: 14px;
        padding: 22px 28px;
        margin-bottom: 22px;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
    }
    .header-title { font-size: 30px; font-weight: 900; color: #00F5FF; text-shadow: 0 0 10px rgba(0, 245, 255, 0.6); }
    .header-sub { font-size: 15px; color: #E2E8F0; font-weight: 500; }

    .metric-card {
        background: #0F172A;
        border: 2px solid #1E293B;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .metric-value { font-size: 28px; font-weight: 900; color: #00F5FF; margin-top: 5px; }
    .metric-label { font-size: 13px; font-weight: 700; color: #94A3B8; text-transform: uppercase; }

    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(135deg, #FF007F 0%, #7928CA 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: 1px solid #FF007F !important;
    }

    .stExpander {
        background-color: #0F172A !important;
        border: 1px solid #1E293B !important;
        border-radius: 12px !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #080C14 !important;
        border-right: 1px solid #1E293B;
    }
    
    label, p, span, h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. SIDEBAR NAVIGATION WITH LOGO
# ---------------------------------------------------------
logo_path = "logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
elif os.path.exists("Peace and Dev LOGO.jpg"):
    st.sidebar.image("Peace and Dev LOGO.jpg", use_container_width=True)

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
    prog_list = ["All Programs"] + sorted([str(p) for p in df_tev[program_col].dropna().unique() if str(p).strip() != "" and str(p).lower() != 'nan'])
    selected_program = st.sidebar.selectbox("Select Program / Office:", prog_list)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align: center; font-size: 0.85em; color: #E0E6ED;">
        💻 <b>System Architect</b><br>
        Developed by <br><b style="color:#00F5FF;">LOUIE B. IDULSA - PDBBM ITO I</b><br>
        <i>DSWD FO X • 2026</i>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 5. MAIN HEADER & DASHBOARD
# ---------------------------------------------------------
st.markdown("""
    <div class="header-card">
        <div class="header-title">✈️ PDBBM TEV Executive Tracker</div>
        <div class="header-sub">Live Executive Dashboard • Latest Dates Priority</div>
    </div>
""", unsafe_allow_html=True)

if not df_tev.empty:
    if selected_program != "All Programs" and program_col:
        df_filtered = df_tev[df_tev[program_col].astype(str) == selected_program].copy()
    else:
        df_filtered = df_tev.copy()

    drn_col = df_tev.columns[0]
    name_col = df_tev.columns[3] if len(df_tev.columns) > 3 else df_tev.columns[1]

    overall_status_col = next((c for c in df_tev.columns if 'status' in c.lower() or 'state' in c.lower()), None)

    attach_count = sum(1 for _, r in df_filtered.iterrows() if any(ext in str(v).lower() for v in r.values for ext in ['.jpg', '.png', '.pdf', 'tev_images', 'documents_files']))
    acct_count = sum(1 for _, r in df_filtered.iterrows() if 'acct' in str(r.values).lower() or 'accounting' in str(r.values).lower())
    fin_count = sum(1 for _, r in df_filtered.iterrows() if 'finance' in str(r.values).lower())

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Valid TEV Vouchers</div>
                <div class="metric-value">{len(df_filtered):,}</div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">With Attachments</div>
                <div class="metric-value" style="color:#00F5FF;">{attach_count:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">For Accounting</div>
                <div class="metric-value" style="color:#FFE600;">{acct_count:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Finance Tracked</div>
                <div class="metric-value" style="color:#39FF14;">{fin_count:,}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    search_query = st.text_input("🔍 Quick Search (DRN #, Claimant / Et. Al, Station, Status, etc.):", "")

    if search_query:
        search_mask = df_filtered.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        df_searched = df_filtered[search_mask]
    else:
        df_searched = df_filtered

    st.markdown("---")

    st.subheader(f"📋 TEV Claim Records ({len(df_searched)}) — Latest Dates First")

    if df_searched.empty:
        st.info("Walang nahanap na TEV record batay sa iyong hinahanap.")
    else:
        for idx, row in df_searched.iterrows():
            drn_val = clean_val(row.get(drn_col), "N/A")
            name_val = clean_val(row.get(name_col), "N/A")

            expander_title = f"📄 DRN: {drn_val}  |  Claimant/Et.Al: {name_val}"

            with st.expander(expander_title, expanded=False):
                col_info, col_status, col_attach = st.columns([2, 2, 1.5])

                with col_info:
                    st.markdown("##### 📌 Basic Information")
                    for c in df_tev.columns[:6]:
                        col_label = c if not c.startswith('Unnamed:') else f"Field {c.split(':')[1] if ':' in c else c.split(' ')[1]}"
                        val_cleaned = clean_val(row[c])
                        st.write(f"**{col_label}:** {val_cleaned}")

                with col_status:
                    st.markdown("##### 🏛️ Department Tracking & Remarks")
                    budget_col = next((c for c in df_tev.columns if 'budget' in c.lower()), None)
                    acct_col = next((c for c in df_tev.columns if 'account' in c.lower()), None)
                    cash_col = next((c for c in df_tev.columns if 'cash' in c.lower() or 'treasury' in c.lower()), None)
                    fin_col = next((c for c in df_tev.columns if 'finance' in c.lower()), None)
                    rem_col = next((c for c in df_tev.columns if 'remark' in c.lower() or 'note' in c.lower()), None)

                    b_val = clean_val(row.get(budget_col), "Pending / Process")
                    a_val = clean_val(row.get(acct_col), "Pending / Process")
                    c_val = clean_val(row.get(cash_col), "Pending / Process")
                    f_val = clean_val(row.get(fin_col), "Pending / Process")

                    st.markdown(f"• **Budget:** `{b_val}`")
                    st.markdown(f"• **Accounting:** `{a_val}`")
                    st.markdown(f"• **Cashier:** `{c_val}`")
                    st.markdown(f"• **Finance:** `{f_val}`")
                    
                    if rem_col and pd.notna(row.get(rem_col)) and str(row.get(rem_col)).lower() != 'nan':
                        st.info(f"💬 **Remarks:** {row.get(rem_col)}")

                with col_attach:
                    st.markdown("##### 📎 Et. Al Attachment Verification")
                    
                    found_file = None
                    for cell in row.values:
                        cell_str = str(cell).strip()
                        if cell_str.lower() != 'nan' and any(ext in cell_str.lower() for ext in ['.jpg', '.jpeg', '.png', '.pdf', 'tev_images', 'documents_files', 'tev_files', 'drive.google']):
                            found_file = cell_str
                            break
                    
                    img_url = format_appsheet_file_url(found_file)

                    if img_url and any(ext in str(found_file).lower() for ext in ['.jpg', '.jpeg', '.png']):
                        clean_crop = get_clean_boxed_crop(img_url)
                        if clean_crop:
                            st.image(clean_crop, caption="Et. Al List Verification (Names & Details Only)", use_container_width=True)
                        else:
                            st.image(img_url, caption="Et. Al List Verification", use_container_width=True)
                    else:
                        st.caption("ℹ️ Walang naka-attach na image preview sa entry na ito.")

    st.markdown("---")

    tab1, tab2 = st.tabs(["📊 Analytics & Charts", "📥 Raw Masterlist Data"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Status Breakdown")
            if overall_status_col:
                fig1 = px.pie(df_filtered, names=overall_status_col, hole=0.4, color_discrete_sequence=px.colors.qualitative.Dark24)
                fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
                st.plotly_chart(fig1, use_container_width=True)

        with c2:
            st.subheader("📋 Top Claims Summary")
            top_records = df_filtered.head(8)
            if name_col:
                fig2 = px.bar(top_records, x=drn_col, y=df_filtered.index[:len(top_records)], color_discrete_sequence=['#00F5FF'])
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF", yaxis_title="Record Index")
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
