import streamlit as st


def show():
    st.title("ℹ️ About This Dashboard")

    st.markdown("""
    This interactive dashboard provides a comprehensive **geospatial analysis** of the **real estate market in Yerevan, Armenia**.

    It focuses on both **rental and sale apartment prices**, with additional insights into **new construction trends** and **urban object distributions** such as hotels, restaurants, cafes, banks, ATMs, and more.

    ### 🔍 Key Features:
    - **📊 Apartment Pricing Analysis**: Explore average rent and sale prices across Yerevan, with breakdowns by region and apartment type.
    - **🏗️ New Construction Monitoring**: Track the number and pricing trends of newly built apartments in key districts.
    - **📍 H3-Based Geospatial Visualization**: The city is divided into hexagonal regions using the [H3 spatial index](https://h3geo.org/), allowing for high-resolution spatial comparisons.
    - **🌆 District-Level Statistics**: Aggregated object counts (e.g., restaurants, banks, cafes, etc.) visualized for each of Yerevan's 12 administrative districts.
    - **🗺️ Interactive Maps & Charts**: Easily explore spatial and temporal trends with dynamic visualizations.

    ### 📚 Data Sources:
    - [List.am](https://www.list.am) — Apartment rent and sale listings in Armenia
    - [MyHome.am](https://myhome.am) — Verified listings and property market data
    - [Norakaruyc.am](https://norakaruyc.am/) — Verified listings and property market data
    - [OpenStreetMap](https://www.openstreetmap.org) — Location data for city infrastructure, POIs, and administrative boundaries
                

    ---
    Created for urban data insights and smarter real estate decisions in Yerevan.
    """)
