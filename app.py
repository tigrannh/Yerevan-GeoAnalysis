import streamlit as st
from utils import about, districts_dashboard, map, data_prep, visualizations_3d, norakaruyc_yerevan_dashboard, manual_extract_info

st.set_page_config(page_title="Yereven Geospatial Analysis", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --bg:        #0E1117;   /* deep slate */
        --panel:     #161B22;   /* cards / sidebar */
        --line:      rgba(255,255,255,0.08);
        --text:      #E6EDF3;   /* primary text */
        --muted:     #9AA7B4;   /* secondary text */
        --accent:    #10B981;   /* emerald */
        --accent-soft: rgba(16,185,129,0.12);
    }

    /* ---------- Base ---------- */
    .stApp {
        background: var(--bg);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li { color: var(--text); }

    /* ---------- Headings: clean, solid, professional ---------- */
    h1, h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #F1F5F9 !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }
    h1 { font-weight: 800 !important; }
    /* subtle emerald accent rule under the main title area */
    h1::after {
        content: ""; display: block; width: 56px; height: 3px;
        background: var(--accent); border-radius: 3px; margin-top: 10px;
    }

    /* ---------- Card helper (use class="glass-card") ---------- */
    .glass-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.35);
        margin-bottom: 14px;
    }

    /* ---------- Metric tiles ---------- */
    [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-left: 3px solid var(--accent);
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.25);
    }
    [data-testid="stMetricLabel"] { color: var(--muted) !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #F1F5F9 !important; font-weight: 800; }

    /* ---------- Buttons: solid emerald, restrained ---------- */
    div.stButton > button {
        background: var(--accent) !important;
        color: #04130D !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.3rem !important;
        transition: 0.2s !important;
    }
    div.stButton > button:hover { filter: brightness(1.07); box-shadow: 0 4px 14px rgba(16,185,129,0.30); }
    div.stButton > button p, div.stButton > button div, div.stButton > button span {
        color: #04130D !important; font-weight: 700 !important;
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line); }
    .stTabs [data-baseweb="tab"] { background: transparent; color: var(--muted); border-radius: 8px 8px 0 0; }
    .stTabs [aria-selected="true"] { color: #F1F5F9 !important; border-bottom: 2px solid var(--accent) !important; }

    /* ---------- Selectbox / inputs ---------- */
    div[data-baseweb="select"] > div {
        background-color: var(--panel) !important; color: var(--text) !important;
        border: 1px solid var(--line) !important; border-radius: 10px !important;
    }
    div[data-baseweb="select"] input, .stTextInput input, .stNumberInput input { color: var(--text) !important; }
    div[data-baseweb="popover"] ul { background-color: var(--panel) !important; }
    div[data-baseweb="popover"] li, div[data-baseweb="popover"] li span, div[data-baseweb="popover"] li div { color: var(--text) !important; }
    div[data-baseweb="popover"] li:hover { background-color: var(--accent-soft) !important; }

    /* ---------- Sliders ---------- */
    div[data-baseweb="slider"] [role="slider"] { background: var(--accent) !important; }

    /* ---------- Sidebar nav (radio) ---------- */
    div[role="radiogroup"] > label {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px; padding: 9px 12px; margin-bottom: 6px;
        transition: 0.18s;
    }
    div[role="radiogroup"] > label:hover { border-color: var(--accent); background: var(--accent-soft); }

    /* ---------- Sidebar: solid panel, always open ---------- */
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] {
        background: #0B0E14 !important;
        border-right: 1px solid var(--line);
        visibility: visible !important; transform: none !important;
    }
    section[data-testid="stSidebar"] .block-container { padding-top: 14px; padding-bottom: 16px; }

    /* ---------- DataFrames ---------- */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 12px; overflow: hidden;
    }

    /* ---------- Links ---------- */
    .stApp a { color: var(--accent) !important; }

    /* ---------- Scrollbar ---------- */
    ::-webkit-scrollbar { width: 9px; height: 9px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.14); border-radius: 6px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.24); }

    /* ---------- Hide Streamlit chrome ---------- */
    #MainMenu, footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none !important; }
    [class*="viewerBadge"], [data-testid="stAppViewerBadge"] { display: none !important; }
    a[href*="streamlit.io"] { display: none !important; }

    /* ---------- Sticky logo box (if re-enabled) ---------- */
    .sidebar-logo {
        position: sticky; top: 0; z-index: 1000;
        background: var(--panel);
        border-bottom: 1px solid var(--line);
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
