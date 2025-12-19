from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Delivery Intelligence Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# PREMIUM STYLING
# =========================
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main .block-container { padding: 2rem; background: rgba(255,255,255,0.98); border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
    [data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    div[data-testid="metric-container"] { background: linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%); padding:20px; border-radius:15px; border:2px solid rgba(102,126,234,0.15); box-shadow:0 4px 15px rgba(0,0,0,0.1); transition: all 0.3s ease; }
    div[data-testid="metric-container"]:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(102,126,234,0.4); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%); }
    [data-testid="stSidebar"] * { color: white !important; }
    h1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; text-align:center; font-size:3rem !important; }
    .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; border:none; border-radius:12px; padding:0.6rem 2.5rem; font-weight:700; box-shadow:0 4px 15px rgba(102,126,234,0.4); transition:all 0.3s ease; font-size:1rem; }
    .stButton > button:hover { transform: translateY(-3px); box-shadow:0 6px 25px rgba(102,126,234,0.6); }
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.title("📦 DELIVERY INTELLIGENCE HUB")
st.markdown(
    "<p style='text-align: center; color: #718096; font-size: 1.3rem;'>Advanced Package Tracking & Analytics Platform</p>",
    unsafe_allow_html=True)
st.markdown("---")

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("### ⚙️ CONTROL PANEL")
    st.markdown("---")

    company_name = st.text_input("🏢 Company Name", "FastTrack Logistics")

    st.markdown("---")
    st.markdown("### 📁 DATA UPLOAD")
    st.info("💡 You can drop multiple files. Supported formats: CSV, Excel (.xlsx), JSON")

    uploaded_csvs = st.file_uploader("Drop CSV files", type=["csv"], accept_multiple_files=True)
    uploaded_excels = st.file_uploader("Drop Excel files", type=["xlsx"], accept_multiple_files=True)
    uploaded_jsons = st.file_uploader("Drop JSON files", type=["json"], accept_multiple_files=True)

    df_list = []

    for file in uploaded_csvs:
        try:
            df_list.append(pd.read_csv(file))
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")

    for file in uploaded_excels:
        try:
            df_list.append(pd.read_excel(file))
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")

    for file in uploaded_jsons:
        try:
            df_list.append(pd.read_json(file))
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")

    df = pd.concat(df_list, ignore_index=True) if df_list else None

    st.markdown("---")
    st.markdown("### 🕒 TIME FILTER")
    time_filter = st.selectbox(
        "Select period:",
        ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
    )

# =========================
# CHECK DATA
# =========================
if df is None or df.empty:
    st.info("👈 **Upload data to start**")
    st.stop()

# =========================
# DATA PREPROCESSING
# =========================
df.columns = df.columns.str.strip().str.replace(" ", "_")
date_col = next((col for col in df.columns if "date" in col.lower()), None)
status_col = next((col for col in df.columns if any(k in col.lower() for k in ["status", "delivery", "state"])), None)

if date_col:
    df[date_col] = pd.to_datetime(df[date_col])
    if time_filter != "All Time":
        days = int(time_filter.split()[1])
        df = df[df[date_col] >= df[date_col].max() - timedelta(days=days)]

if status_col:
    df["_status_clean"] = df[status_col].astype(str).str.lower().str.strip()

num_cols = df.select_dtypes("number").columns.tolist()
cat_cols = df.select_dtypes(["object", "category"]).columns.tolist()

# =========================
# METRICS
# =========================
st.markdown(f"<h2 style='text-align:center;'>🚚 {company_name} Performance Dashboard</h2>", unsafe_allow_html=True)
st.markdown("---")

total = len(df)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📦 Total Orders", f"{total:,}")

if status_col:
    delivered = (df["_status_clean"] == "delivered").sum()
    undelivered = df["_status_clean"].isin(["undelivered", "returned", "failed"]).sum()
    in_transit = df["_status_clean"].isin(["in transit", "pending"]).sum()

    col2.metric("✅ Delivered", f"{delivered:,}", f"{delivered / total * 100:.1f}%")
    col3.metric("❌ Undelivered", f"{undelivered:,}", f"{undelivered / total * 100:.1f}%")
    col4.metric("🚛 In Transit", f"{in_transit:,}", f"{in_transit / total * 100:.1f}%")
    col5.metric("📈 Success Rate", f"{delivered / total * 100:.1f}%")

# =========================
# SIMPLE TAB EXAMPLE
# =========================
tab1, tab2 = st.tabs(["📊 Overview", "📋 Data Explorer"])

with tab1:
    st.markdown("### Delivery Status Distribution")
    if status_col:
        counts = df[status_col].value_counts()
        fig = px.pie(values=counts.values, names=counts.index, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Filter & Export Data")
    rows = st.slider("Show Rows", 10, min(500, len(df)), 100)
    st.dataframe(df.head(rows), use_container_width=True, height=400)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", csv, f"delivery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                       "text/csv")

    json_str = df.to_json(orient='records', indent=2)
    st.download_button("⬇️ Download JSON", json_str, f"delivery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                       "application/json")
