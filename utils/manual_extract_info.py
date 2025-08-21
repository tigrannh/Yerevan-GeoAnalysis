import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
from shapely.geometry import Polygon

def show():
    st.title("🖌️ Custom Area Analysis Dashboard")
    st.markdown("""
    **How to use this page:**
    1.  Select the dataset you want to analyze from the sidebar (e.g., Apartments Sell, Businesses).
    2.  Use the drawing tools on the left side of the map to draw a **Polygon** or **Rectangle** around your area of interest.
    3.  Once you complete the shape, the dashboard will automatically find all the data points inside it and display a summary below the map.
    
    This allows for highly flexible, on-the-fly analysis of any custom-defined area in Yerevan.
    """)

    # --- Sidebar for Data Selection ---
    st.sidebar.header("⚙️ Configuration")
    data_source = st.sidebar.selectbox(
        "Select Dataset to Analyze:",
        ['Apartments Sell', 'Apartments Rent', 'Apartments Primary Market', 'Community Services & Businesses']
    )

    # --- Caching and Data Loading ---
    @st.cache_data(ttl=3600)
    def load_data():
        # Load all dataframes and convert to GeoDataFrames immediately
        def to_geodf(df, lat_col, lon_col):
            df_copy = df.copy()
            # Ensure numeric types and drop invalid rows
            df_copy[lat_col] = pd.to_numeric(df_copy[lat_col], errors='coerce')
            df_copy[lon_col] = pd.to_numeric(df_copy[lon_col], errors='coerce')
            df_copy.dropna(subset=[lat_col, lon_col], inplace=True)
            
            return gpd.GeoDataFrame(
                df_copy,
                geometry=gpd.points_from_xy(df_copy[lon_col], df_copy[lat_col]),
                crs="EPSG:4326"
            )

        sell_gdf = to_geodf(st.session_state.data['list_apartments_sell'], 'latitude', 'longitude')
        rent_gdf = to_geodf(st.session_state.data['list_apartments_rent'], 'latitude', 'longitude')
        ameria_gdf = to_geodf(st.session_state.data['ameria_primary_market'], 'latitude', 'longitude')
        osm_gdf = to_geodf(st.session_state.data['osm_points'], 'lat', 'lon')
        districts_gdf = st.session_state.data['yerevan_distrincts'].copy().to_crs(epsg=4326)

        return sell_gdf, rent_gdf, ameria_gdf, osm_gdf, districts_gdf

    sell_gdf, rent_gdf, ameria_gdf, osm_gdf, districts_gdf = load_data()

    # --- Map Initialization with Drawing Tools ---
    m = folium.Map(location=[40.18, 44.51], zoom_start=12, tiles='cartodbpositron')

    # Add district boundaries for context
    folium.GeoJson(
        districts_gdf,
        style_function=lambda x: {'color': 'black', 'weight': 1, 'fillOpacity': 0.05, 'dashArray': '5, 5'},
        name='District Boundaries'
    ).add_to(m)

    # Add the drawing plugin to the map
    Draw(
        export=False,
        draw_options={
            'polygon': {'allowIntersection': False},
            'rectangle': True,
            'circle': False,
            'marker': False,
            'polyline': False,
            'circlemarker': False
        }
    ).add_to(m)

    # --- Render Map and Capture Drawn Shape ---
    st.subheader("Draw on the Map to Define Your Analysis Area")
    map_data = st_folium(m, width=1100, height=600)

    # This variable will hold our final analysis results
    points_inside = gpd.GeoDataFrame()
    drawn_polygon = None

    # Check if a shape has been drawn
    if map_data.get("all_drawings") is not None:
        if len(map_data["all_drawings"]) > 0:
            # Get the coordinates of the last drawn shape
            last_drawing = map_data["all_drawings"][-1]
            coords = last_drawing['geometry']['coordinates'][0]
            drawn_polygon = Polygon(coords)

            # --- Perform Spatial Query Based on Selected Data Source ---
            st.sidebar.success("Area Selected! See analysis below.")
            
            if data_source == 'Apartments Sell':
                points_inside = sell_gdf[sell_gdf.within(drawn_polygon)]
            elif data_source == 'Apartments Rent':
                points_inside = rent_gdf[rent_gdf.within(drawn_polygon)]
            elif data_source == 'Apartments Primary Market':
                points_inside = ameria_gdf[ameria_gdf.within(drawn_polygon)]
            elif data_source == 'Community Services & Businesses':
                points_inside = osm_gdf[osm_gdf.within(drawn_polygon)]

    st.markdown("---")

    # --- Display Aggregated Analysis if an area was selected ---
    if drawn_polygon:
        st.header("📈 Analysis for Your Selected Area")

        if points_inside.empty:
            st.warning("No data points found in the selected area for the chosen dataset.")
        else:
            # Display metrics and aggregated tables based on the dataset
            if data_source == 'Apartments Sell' or data_source == 'Apartments Rent':
                st.metric(f"Total Listings Found", len(points_inside))
                
                # Ensure columns are numeric for aggregation
                for col in ['price_amd', 'price_amd_per_1ms_area', 'square_meters', 'number_of_rooms']:
                    points_inside[col] = pd.to_numeric(points_inside[col], errors='coerce')

              
                summary = points_inside.agg({
                    'price_amd': ['min', 'max', 'mean', 'median'],
                    'price_amd_per_1ms_area': ['min', 'max', 'mean', 'median'],
                    'square_meters': ['min', 'max', 'mean', 'median'],
                    'number_of_rooms': ['min', 'max', 'mean', 'median'],
                }).rename(columns={
                    'price_amd': 'Price (AMD)',
                    'price_amd_per_1ms_area': 'Price/m² (AMD)',
                    'square_meters': 'Area (m²)',
                    'number_of_rooms': 'Rooms'
                })
                st.dataframe(summary.style.format("{:,.2f}"))

            elif data_source == 'Apartments Primary Market':
                st.metric("Total New Buildings Found", len(points_inside))
                
                summary = points_inside.agg({
                    'apartmentPriceStartingAt': ['min', 'max', 'mean', 'median'],
                    'apartmentsCount': ['sum'],
                    'availableForSale': ['sum']
                }).rename(columns={
                    'apartmentPriceStartingAt': 'Starting Price (AMD)',
                    'apartmentsCount': 'Total Apartments',
                    'availableForSale': 'Free Apartments'
                })
                st.dataframe(summary.style.format("{:,.0f}"))

            elif data_source == 'Community Services & Businesses':
                st.metric("Total Businesses/Services Found", len(points_inside))
                
                category_counts = points_inside['main_category'].value_counts().reset_index()
                category_counts.columns = ['Business Category', 'Count']
                st.dataframe(category_counts)

            # Show raw data in an expander
            with st.expander("View Raw Data for the Selected Area"):
                st.dataframe(points_inside.drop(columns='geometry'))

    else:
        st.info("ℹ️ Use the drawing tools on the map to select an area. The analysis will appear here.")


if __name__ == "__main__":
    show()