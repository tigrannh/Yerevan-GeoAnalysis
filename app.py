import streamlit as st
from utils import about, districts_dashboard, map, data_prep, visualizations_3d, norakaruyc_yerevan_dashboard, manual_extract_info

st.set_page_config(page_title="Yereven Geospatial Analysis", layout="wide")

st.markdown("""
<style>
/* Hide menu/footer + toolbar items you don't want */
#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"] a[href*="github.com"],
[data-testid="stToolbar"] button[title="Share"],
[data-testid="stToolbar"] button[title="Edit source"] { display: none !important; }

/* Keep sidebar always open and visible */
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { visibility: visible !important; transform: none !important; }

/* 💜 Very light purple sidebar theme */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #F8F3FF 0%, #FBF9FF 100%);
  border-right: 1px solid #E6DFFF;
}
section[data-testid="stSidebar"] .block-container {
  padding-top: 14px; padding-bottom: 16px;
}

/* Sticky logo box at top of sidebar */
.sidebar-logo {
  position: sticky; top: 0; z-index: 1000;
  background: #F2EAFE;                      /* light lilac box */
  border-bottom: 1px solid #E2D6FF;
  padding: 10px 12px; text-align: center;
}
.sidebar-logo img { height: 36px; width: auto; }

/* Sidebar headings */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {
  color: #5C2E91;          /* deep purple */
  margin-top: 0.6rem; margin-bottom: 0.4rem;
}

/* Sidebar widgets look */
section[data-testid="stSidebar"] [data-baseweb="select"]>div,
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
  border: 1px solid #E6DFFF !important;
  background: #FFFFFF !important;
  border-radius: 8px !important;
}
section[data-testid="stSidebar"] button[kind="primary"] {
  background: #6A0DAD !important; border-color: #6A0DAD !important;
}
section[data-testid="stSidebar"] button[kind="primary"]:hover { filter: brightness(1.05); }

/* DataFrame card look in sidebar */
section[data-testid="stSidebar"] div[data-testid="stDataFrame"] {
  background: #FFFFFF;
  border: 1px solid #E6DFFF;
  border-radius: 10px;
  padding: 6px;
  box-shadow: 0 1px 4px rgba(90,60,150,0.06);
}

/* Subtle purple scrollbar in sidebar */
section[data-testid="stSidebar"] ::-webkit-scrollbar { width: 10px; }
section[data-testid="stSidebar"] ::-webkit-scrollbar-track { background: #F6F0FF; }
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb { background: #D8C9FF; border-radius: 6px; }
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
        st.markdown(
        """
            <style>
            /* Sticky logo container pinned to the top of the sidebar */
            .sidebar-logo {
                position: sticky;
                top: 0;
                z-index: 1000;
                background: #f9f6ff;                  /* match your sidebar color */
                padding: 10px 12px;
                border-bottom: 1px solid #e0d7f3;
                text-align: center;
            }
            .sidebar-logo img {
                height: 34px;                         /* tweak to taste */
                width: auto;
                display: inline-block;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div class="sidebar-logo">
                <img src="data:image/svg+xml;base64,{logo_b64}" alt="Logo">
            </div>
            """,
            unsafe_allow_html=True
        )

        st.title("📂 Yerevan GeoAnalysis")
        return st.radio("Go to page:", [
            "🏠 Overview",
            "📈 Yerevan Districts Analysis",
            "🏗️ New Buildings Map",
            "🗺️ Yerevan hexagonal analysis",
            "🌐 Advanced 3D Real Estate Dashboard",
            "✍️ Custom Area Analysis",
        ])





if not st.session_state.authenticated:
    show_login()
else:
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
