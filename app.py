import streamlit as st
from utils import about, districts_dashboard, map, data_prep, visualizations_3d, norakaruyc_yerevan_dashboard, manual_extract_info

st.set_page_config(page_title="Yereven Geospatial Analysis", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --bg:        #F6F7FB;
        --panel:     rgba(255,255,255,0.72);
        --panel-solid:#FFFFFF;
        --line:      rgba(15,23,42,0.08);
        --text:      #0F172A;
        --muted:     #5B6677;
        --c1:        #6366F1;   /* indigo  */
        --c2:        #8B5CF6;   /* violet  */
        --c3:        #06B6D4;   /* cyan    */
        --grad:      linear-gradient(135deg, #6366F1 0%, #8B5CF6 45%, #06B6D4 100%);
        --grad-soft: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(6,182,212,0.12));
    }

    /* ---------- Aurora background ---------- */
    .stApp {
        background:
            radial-gradient(40rem 40rem at 8% -5%, rgba(99,102,241,0.22), transparent 60%),
            radial-gradient(38rem 38rem at 100% 0%, rgba(6,182,212,0.20), transparent 55%),
            radial-gradient(45rem 45rem at 50% 120%, rgba(139,92,246,0.18), transparent 55%),
            var(--bg);
        background-attachment: fixed;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li { color: var(--text); }
    .block-container { padding-top: 2.2rem; }

    /* ---------- Headings: gradient, modern ---------- */
    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: #0F172A !important;
    }
    h1 {
        font-weight: 700 !important; font-size: 2.3rem !important;
        background: var(--grad);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    h1::after {
        content: ""; display: block; width: 64px; height: 4px;
        background: var(--grad); border-radius: 4px; margin-top: 12px;
    }

    /* ---------- Glass cards ---------- */
    .glass-card {
        background: var(--panel);
        backdrop-filter: blur(18px) saturate(160%);
        -webkit-backdrop-filter: blur(18px) saturate(160%);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 10px 30px rgba(31,38,135,0.10), inset 0 1px 0 rgba(255,255,255,0.6);
        margin-bottom: 16px;
        transition: transform .25s ease, box-shadow .25s ease;
    }
    .glass-card:hover { transform: translateY(-3px); box-shadow: 0 18px 40px rgba(31,38,135,0.16); }

    /* ---------- Metric tiles: glassy with gradient edge ---------- */
    [data-testid="stMetric"] {
        position: relative; overflow: hidden;
        background: var(--panel);
        backdrop-filter: blur(14px) saturate(160%);
        -webkit-backdrop-filter: blur(14px) saturate(160%);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 8px 24px rgba(31,38,135,0.10);
        transition: transform .2s ease, box-shadow .2s ease;
    }
    [data-testid="stMetric"]::before {
        content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--grad);
    }
    [data-testid="stMetric"]:hover { transform: translateY(-2px); box-shadow: 0 14px 32px rgba(31,38,135,0.16); }
    [data-testid="stMetricLabel"] { color: var(--muted) !important; font-weight: 600; }
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important; font-weight: 700;
        background: var(--grad); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    }

    /* ---------- Buttons: gradient, animated ---------- */
    div.stButton > button {
        background: var(--grad) !important;
        background-size: 180% 180% !important;
        color: #FFFFFF !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.55rem 1.4rem !important;
        box-shadow: 0 6px 18px rgba(99,102,241,0.35) !important;
        transition: transform .2s ease, box-shadow .2s ease, background-position .6s ease !important;
    }
    div.stButton > button:hover { transform: translateY(-2px); background-position: 100% 0 !important; box-shadow: 0 10px 26px rgba(99,102,241,0.45) !important; }
    div.stButton > button p, div.stButton > button div, div.stButton > button span { color: #FFFFFF !important; font-weight: 700 !important; }

    /* ---------- Tabs: pill style ---------- */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: none; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.55); border: 1px solid var(--line);
        border-radius: 999px; padding: 4px 16px; color: var(--muted);
    }
    .stTabs [aria-selected="true"] { background: var(--grad) !important; border: none !important; }
    .stTabs [aria-selected="true"] * { color: #FFFFFF !important; }

    /* ---------- Inputs / selects ---------- */
    div[data-baseweb="select"] > div {
        background-color: var(--panel-solid) !important; color: var(--text) !important;
        border: 1px solid var(--line) !important; border-radius: 12px !important;
    }
    div[data-baseweb="select"] input, .stTextInput input, .stNumberInput input { color: var(--text) !important; }
    div[data-baseweb="popover"] ul { background-color: #FFFFFF !important; border-radius: 12px; }
    div[data-baseweb="popover"] li, div[data-baseweb="popover"] li span, div[data-baseweb="popover"] li div { color: var(--text) !important; }
    div[data-baseweb="popover"] li:hover { background: var(--grad-soft) !important; }
    div[data-baseweb="slider"] [role="slider"] { background: var(--c1) !important; }

    /* ---------- Sidebar nav (radio) ---------- */
    div[role="radiogroup"] > label {
        background: rgba(255,255,255,0.55);
        border: 1px solid var(--line);
        border-radius: 12px; padding: 10px 14px; margin-bottom: 7px;
        transition: .2s; backdrop-filter: blur(8px);
    }
    div[role="radiogroup"] > label:hover { border-color: transparent; background: var(--grad-soft); transform: translateX(2px); }

    /* ---------- Sidebar: frosted glass ---------- */
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] {
        background: rgba(255,255,255,0.55) !important;
        backdrop-filter: blur(20px) saturate(160%);
        -webkit-backdrop-filter: blur(20px) saturate(160%);
        border-right: 1px solid rgba(255,255,255,0.6);
        visibility: visible !important; transform: none !important;
    }
    section[data-testid="stSidebar"] .block-container { padding-top: 14px; padding-bottom: 16px; }

    /* ---------- DataFrames ---------- */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line); border-radius: 14px; overflow: hidden;
        box-shadow: 0 8px 24px rgba(31,38,135,0.08);
    }

    /* ---------- Links ---------- */
    .stApp a { color: var(--c1) !important; font-weight: 600; }

    /* ---------- Scrollbar ---------- */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--c1), var(--c3)); border-radius: 8px; }

    /* ---------- Hide Streamlit chrome ---------- */
    #MainMenu, footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none !important; }
    [class*="viewerBadge"], [data-testid="stAppViewerBadge"] { display: none !important; }
    a[href*="streamlit.io"] { display: none !important; }

    /* ---------- Sticky logo box (if re-enabled) ---------- */
    .sidebar-logo {
        position: sticky; top: 0; z-index: 1000;
        background: rgba(255,255,255,0.6); backdrop-filter: blur(10px);
        border-bottom: 1px solid var(--line); padding: 10px 12px; text-align: center;
    }
    .sidebar-logo img { height: 36px; width: auto; }

    /* ---------- Responsive ---------- */
    @media (max-width: 640px) {
        h1 { font-size: 1.6rem !important; }
        h2 { font-size: 1.3rem !important; }
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
