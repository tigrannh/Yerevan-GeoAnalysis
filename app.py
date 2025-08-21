import streamlit as st
from utils import about, districts_dashboard, map, data_prep, visualizations_3d, norakaruyc_yerevan_dashboard, manual_extract_info

st.set_page_config(page_title="Yereven Geospatial Analysis", layout="wide")



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

        st.markdown(f"""
            <style>
            /* Push page content down so the logo doesn't cover content */
            [data-testid="stAppViewContainer"] .main {{
                padding-top: 56px;
            }}

            /* Logo container (transparent, no background) */
            .octobi-bar {{
                position: fixed;
                top: 0; left: 0; right: 0;
                height: 56px;
                background: transparent;
                border: none;
                display: flex;
                align-items: center;
                justify-content: flex-start;
                padding: 0 16px;
                z-index: 99999;
            }}

            .octobi-bar img {{
                height: 40px;
                width: auto;
                display: block;
            }}

            /* Sidebar design */
            [data-testid="stSidebar"] {{
                background-color: #f9f6ff;
                border-right: 1px solid #e0d7f3;
                padding-top: 20px;
            }}

            [data-testid="stSidebar"] .block-container {{
                padding: 1rem;
            }}

            [data-testid="stSidebar"] h1, 
            [data-testid="stSidebar"] h2, 
            [data-testid="stSidebar"] h3 {{
                color: #6a0dad;
            }}

            /* Radio buttons beautified */
            div[role="radiogroup"] > label {{
                background: white;
                border: 1px solid #e0d7f3;
                border-radius: 6px;
                padding: 6px 10px;
                margin-bottom: 4px;
                cursor: pointer;
                transition: all 0.2s ease-in-out;
            }}
            div[role="radiogroup"] > label:hover {{
                background: #f0e6ff;
                border-color: #cbb3f7;
            }}
            </style>

            <div class="octobi-bar">
                <img src="data:image/svg+xml;base64,{logo_b64}" alt="Logo">
            </div>
        """, unsafe_allow_html=True)

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
