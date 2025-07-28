import streamlit as st
from utils import about, districts_dashboard, map, data_prep

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


def show_sidebar():
    with st.sidebar:
        st.title("📂 Yerevan GeoAnalysis")
        return st.radio("Go to page:", [
            "🏠 Overview",
            "📈 Yerevan Districts Analysis",
            "🗺️ Yerevan hexagonal analysis"
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
    elif page == "🗺️ Yerevan hexagonal analysis":
        map.show()
