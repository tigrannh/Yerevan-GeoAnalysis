import streamlit as st
from utils import about, districts_dashboard, map, data_prep, visualizations_3d, norakaruyc_yerevan_dashboard, manual_extract_info

st.set_page_config(page_title="Yereven Geospatial Analysis", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600;700&display=swap');

    /* ---------- App background: deep neon gradient ---------- */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0f0c29 0%, #302b63 55%, #24243e 100%);
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li { color: #F2F2F7; }

    /* ---------- Headings: neon gradient + Orbitron ---------- */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        background: linear-gradient(90deg, #00ff88, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        letter-spacing: 0.5px;
    }

    /* ---------- Glass card helper (use class="glass-card") ---------- */
    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.55);
        margin-bottom: 14px;
    }

    /* ---------- Metrics as glass tiles ---------- */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(0,212,255,0.25);
        border-radius: 16px;
        padding: 14px 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.45);
    }
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-family:'Orbitron',sans-serif; }

    /* ---------- Buttons: neon gradient pills ---------- */
    div.stButton > button {
        background: linear-gradient(45deg, #00ff88, #00d4ff) !important;
        color: #001018 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.5rem 1.4rem !important;
        transition: 0.3s !important;
    }
    div.stButton > button:hover { filter: brightness(1.08); transform: translateY(-1px); box-shadow: 0 6px 18px rgba(0,255,136,0.35); }
    div.stButton > button p, div.stButton > button div, div.stButton > button span {
        color: #001018 !important; font-weight: 900 !important;
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 10px 10px 0 0; color: #F2F2F7;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0,212,255,0.15) !important;
        border-bottom: 2px solid #00ff88 !important;
    }

    /* ---------- Selectbox / inputs (readable on dark) ---------- */
    div[data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.08) !important; color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.18) !important; border-radius: 10px !important;
    }
    div[data-baseweb="select"] input, .stTextInput input, .stNumberInput input { color: #FFFFFF !important; }
    div[data-baseweb="popover"] ul { background-color: #16213e !important; }
    div[data-baseweb="popover"] li, div[data-baseweb="popover"] li span, div[data-baseweb="popover"] li div { color: #FFFFFF !important; }
    div[data-baseweb="popover"] li:hover { background-color: rgba(0,212,255,0.30) !important; }

    /* ---------- Radio buttons (sidebar nav) ---------- */
    div[role="radiogroup"] > label {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 10px; padding: 8px 12px; margin-bottom: 6px;
        transition: 0.2s;
    }
    div[role="radiogroup"] > label:hover {
        background: rgba(0,212,255,0.12); border-color: rgba(0,212,255,0.45);
    }

    /* ---------- Sidebar: dark glass, always open ---------- */
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(22,33,62,0.96) 0%, rgba(15,12,41,0.96) 100%) !important;
        border-right: 1px solid rgba(0,255,136,0.25);
        visibility: visible !important; transform: none !important;
    }
    section[data-testid="stSidebar"] .block-container { padding-top: 14px; padding-bottom: 16px; }

    /* ---------- DataFrames ---------- */
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 12px; overflow: hidden;
    }

    /* ---------- Scrollbar ---------- */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.04); }
    ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.35); border-radius: 6px; }

    /* ---------- Hide Streamlit chrome ---------- */
    #MainMenu, footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none !important; }
    [class*="viewerBadge"], [data-testid="stAppViewerBadge"] { display: none !important; }
    a[href*="streamlit.io"] { display: none !important; }

    /* ---------- Sticky logo box (if re-enabled) ---------- */
    .sidebar-logo {
        position: sticky; top: 0; z-index: 1000;
        background: rgba(0,255,136,0.06);
        border-bottom: 1px solid rgba(0,255,136,0.25);
        padding: 10px 12px; text-align: center;
    }
    .sidebar-logo img { height: 36px; width: auto; }

    /* ---------- Responsive (phones) ---------- */
    @media (max-width: 640px) {
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.25rem !important; }
        .block-container { padding-left: 0.6rem !important; padding-right: 0.6rem !important; }
    }
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def show_login():
    st.title("🔐 Login Required")
    st.markdown("Please enter the password to access the dashboard.")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if password == "octogeo":
            st.session_state.authenticated = True
        else:
            st.error("❌ Incorrect password. Try again.")


# def show_sidebar():
#     with st.sidebar:
#        # --- Fixed "OctoBI" top-left bar ---
#         st.markdown("""
#             <style>
#             /* Push page content down so the fixed bar doesn't cover it */
#             [data-testid="stAppViewContainer"] .main {
#                 padding-top: 56px;
#             }

#             /* Simple fixed header bar with purple background */
#             .octobi-bar {
#                 position: fixed;
#                 top: 0; left: 0; right: 0;
#                 height: 48px;
#                 background: #6a0dad; /* Purple color */
#                 color: white;
#                 border-bottom: 1px solid #4b0b8a;
#                 display: flex;
#                 align-items: center;
#                 padding: 0 16px;
#                 font-weight: 700;
#                 font-size: 20px;
#                 z-index: 99999; /* stay on top of Streamlit chrome */
#             }

#             /* Sidebar design */
#             [data-testid="stSidebar"] {
#                 background-color: #f9f6ff; /* Light lavender */
#                 border-right: 1px solid #e0d7f3;
#                 padding-top: 20px;
#             }

#             [data-testid="stSidebar"] .block-container {
#                 padding: 1rem;
#             }

#             [data-testid="stSidebar"] h1, 
#             [data-testid="stSidebar"] h2, 
#             [data-testid="stSidebar"] h3 {
#                 color: #6a0dad;
#             }

#             /* Radio buttons beautified */
#             div[role="radiogroup"] > label {
#                 background: white;
#                 border: 1px solid #e0d7f3;
#                 border-radius: 6px;
#                 padding: 6px 10px;
#                 margin-bottom: 4px;
#                 cursor: pointer;
#                 transition: all 0.2s ease-in-out;
#             }
#             div[role="radiogroup"] > label:hover {
#                 background: #f0e6ff;
#                 border-color: #cbb3f7;
#             }
#             </style>
#             <div class="octobi-bar">OctoBI</div>
#         """, unsafe_allow_html=True)

#         st.title("📂 Yerevan GeoAnalysis")
#         return st.radio("Go to page:", [
#             "🏠 Overview",
#             "📈 Yerevan Districts Analysis",
#             "🏗️ New Buildings Map",
#             "🗺️ Yerevan hexagonal analysis",
#             "🌐 Advanced 3D Real Estate Dashboard",
#             "✍️ Custom Area Analysis",
#         ])

import base64
from pathlib import Path

import base64
from pathlib import Path

def show_sidebar():
    with st.sidebar:
        # Encode the logo file so it always loads
        logo_path = Path(__file__).parent / "logo_v1.svg"
        logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()

        # st.markdown(f"""
        #     <style>
        #     /* Push page content down so the logo doesn't cover content */
        #     [data-testid="stAppViewContainer"] .main {{
        #         padding-top: 56px;
        #     }}

        #     /* Logo container (transparent, no background) */
        #     .octobi-bar {{
        #         position: fixed;
        #         top: 0; left: 0; right: 0;
        #         height: 56px;
        #         background: transparent;
        #         border: none;
        #         display: flex;
        #         align-items: center;
        #         justify-content: flex-start;
        #         padding: 0 16px;
        #         z-index: 99999;
        #     }}

        #     .octobi-bar img {{
        #         height: 40px;
        #         width: auto;
        #         display: block;
        #     }}

        #     /* Sidebar design */
        #     [data-testid="stSidebar"] {{
        #         background-color: #f9f6ff;
        #         border-right: 1px solid #e0d7f3;
        #         padding-top: 20px;
        #     }}

        #     [data-testid="stSidebar"] .block-container {{
        #         padding: 1rem;
        #     }}

        #     [data-testid="stSidebar"] h1, 
        #     [data-testid="stSidebar"] h2, 
        #     [data-testid="stSidebar"] h3 {{
        #         color: #6a0dad;
        #     }}

        #     /* Radio buttons beautified */
        #     div[role="radiogroup"] > label {{
        #         background: white;
        #         border: 1px solid #e0d7f3;
        #         border-radius: 6px;
        #         padding: 6px 10px;
        #         margin-bottom: 4px;
        #         cursor: pointer;
        #         transition: all 0.2s ease-in-out;
        #     }}
        #     div[role="radiogroup"] > label:hover {{
        #         background: #f0e6ff;
        #         border-color: #cbb3f7;
        #     }}
        #     </style>

        #     <div class="octobi-bar">
        #         <img src="data:image/svg+xml;base64,{logo_b64}" alt="Logo">
        #     </div>
        # """, unsafe_allow_html=True)
        # --- OctoBi logo hidden for now ---
        # st.markdown(
        # """
        #     <style>
        #     /* Sticky logo container pinned to the top of the sidebar */
        #     .sidebar-logo {
        #         position: sticky;
        #         top: 0;
        #         z-index: 1000;
        #         background: #f9f6ff;                  /* match your sidebar color */
        #         padding: 10px 12px;
        #         border-bottom: 1px solid #e0d7f3;
        #         text-align: center;
        #     }
        #     .sidebar-logo img {
        #         height: 34px;                         /* tweak to taste */
        #         width: auto;
        #         display: inline-block;
        #     }
        #     </style>
        #     """,
        #     unsafe_allow_html=True
        # )
        # st.markdown(
        #     f"""
        #     <div class="sidebar-logo">
        #         <img src="data:image/svg+xml;base64,{logo_b64}" alt="Logo">
        #     </div>
        #     """,
        #     unsafe_allow_html=True
        # )

        st.title("📂 Yerevan GeoAnalysis")
        return st.radio("Go to page:", [
            "🏠 Overview",
            "📈 Yerevan Districts Analysis",
            "🏗️ New Buildings Map",
            "🗺️ Yerevan hexagonal analysis",
            "🌐 Advanced 3D Real Estate Dashboard",
            "✍️ Custom Area Analysis",
        ])





# --- Login disabled for now (open access) ---
# if not st.session_state.authenticated:
#     show_login()
# else:
if True:
    if "data" not in st.session_state:
        with st.spinner("Loading data..."):
            st.session_state.data = data_prep.load_data()

    page = show_sidebar()

    if page == "🏠 Overview":
        about.show()
    elif page == "📈 Yerevan Districts Analysis":
        districts_dashboard.show()
    elif page == "🏗️ New Buildings Map":
        norakaruyc_yerevan_dashboard.show()
    elif page == "🗺️ Yerevan hexagonal analysis":
        map.show()
    elif page=="🌐 Advanced 3D Real Estate Dashboard":
        visualizations_3d.show()
    elif page == "✍️ Custom Area Analysis": 
        manual_extract_info.show()
