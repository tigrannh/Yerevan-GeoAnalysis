import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
from branca.colormap import linear
from branca.element import MacroElement, Template


def show():
    st.title("🏙️ Yerevan Real Estate & Business Dashboard")

    # --- Sidebar options ---
    data_source = st.selectbox(
        "Select data source for coloring districts:",
        ['Sell', 'Rent', 'Ameria Primary Market', 'OSM Business Counts']
    )

    # Checkbox to show/hide OSM points on map
    show_osm_points = st.checkbox("Show OSM business points on map", value=False)

    # Load OSM dataframe early to get categories
    osm_df = st.session_state.data['osm_points'].copy()
    osm_df['category'] = osm_df['category'].astype(str)
    osm_df['district'] = osm_df['district'].astype(str)
    osm_categories = osm_df['category'].dropna().unique().tolist()
    osm_categories_sorted = sorted(osm_categories)

    # If OSM points toggled, multiselect to filter categories shown
    selected_osm_categories = []
    if show_osm_points:
        selected_osm_categories = st.multiselect(
            "Select OSM business categories to show on map:",
            osm_categories_sorted,
            default=[],
            help="Select which OSM business points to show on map"
        )

    # Define metrics per source
    sell_metrics = ['mean_price_amd', 'median_price_amd', 'max_price_amd', 'min_price_amd',
                    'mean_price_amd_per_1ms_area', 'median_price_amd_per_1ms_area',
                    'rooms_mean', 'square_meters_mean']
    rent_metrics = [m + '_rent' for m in sell_metrics]
    ameria_metrics = ['new_price_min', 'new_price_max', 'new_price_mean', 'new_price_median',
                     'new_area_mean', 'buildings_count', 'apartments_total', 'apartments_free', 'apartments_sold', 'sold_pct']

    # Select metric to color districts by
    if data_source == 'Sell':
        metric_choice = st.selectbox("Select metric to color districts by:", sell_metrics)
    elif data_source == 'Rent':
        metric_choice = st.selectbox("Select metric to color districts by:", rent_metrics)
    elif data_source == 'Ameria Primary Market':
        metric_choice = st.selectbox("Select metric to color districts by:", ameria_metrics)
    else:
        metric_choice = st.selectbox("Select OSM business category to color districts by:", osm_categories_sorted)

    # Load districts
    districts_gdf = st.session_state.data['yerevan_distrincts'].copy()
    districts_gdf = districts_gdf.to_crs(epsg=4326)
    districts_gdf['geometry'] = districts_gdf['geometry'].buffer(0)
    districts_gdf = districts_gdf.rename(columns={'district': 'district_name'})

    # --- Aggregate Sell ---
    sell_df = st.session_state.data['list_apartments_sell'].copy()
    sell_df['price_amd'] = pd.to_numeric(sell_df['price_amd'], errors='coerce')
    sell_df['square_meters'] = pd.to_numeric(sell_df['square_meters'], errors='coerce')
    sell_df['number_of_rooms'] = pd.to_numeric(sell_df['number_of_rooms'], errors='coerce')
    sell_df = sell_df.dropna(subset=['price_amd', 'square_meters', 'distrinct', 'number_of_rooms'])
    sell_agg = sell_df.groupby('distrinct').agg(
        mean_price_amd=('price_amd', 'mean'),
        median_price_amd=('price_amd', 'median'),
        max_price_amd=('price_amd', 'max'),
        min_price_amd=('price_amd', 'min'),
        mean_price_amd_per_1ms_area=('price_amd_per_1ms_area', 'mean'),
        median_price_amd_per_1ms_area=('price_amd_per_1ms_area', 'median'),
        rooms_mean=('number_of_rooms', 'mean'),
        square_meters_mean=('square_meters', 'mean'),
        count_listings=('price_amd', 'count')
    ).reset_index()

    # --- Aggregate Rent ---
    rent_df = st.session_state.data['list_apartments_rent'].copy()
    rent_df['price_amd'] = pd.to_numeric(rent_df['price_amd'], errors='coerce')
    rent_df['square_meters'] = pd.to_numeric(rent_df['square_meters'], errors='coerce')
    rent_df['number_of_rooms'] = pd.to_numeric(rent_df['number_of_rooms'], errors='coerce')
    rent_df = rent_df.dropna(subset=['price_amd', 'square_meters', 'distrinct', 'number_of_rooms'])
    rent_agg = rent_df.groupby('distrinct').agg(
        mean_price_amd=('price_amd', 'mean'),
        median_price_amd=('price_amd', 'median'),
        max_price_amd=('price_amd', 'max'),
        min_price_amd=('price_amd', 'min'),
        mean_price_amd_per_1ms_area=('price_amd_per_1ms_area', 'mean'),
        median_price_amd_per_1ms_area=('price_amd_per_1ms_area', 'median'),
        rooms_mean=('number_of_rooms', 'mean'),
        square_meters_mean=('square_meters', 'mean'),
        count_listings=('price_amd', 'count')
    ).reset_index()

    # --- Aggregate Ameria ---
    ameria_df = st.session_state.data['ameria_primary_market'].copy()
    ameria_df['apartmentPriceStartingAt'] = pd.to_numeric(ameria_df['apartmentPriceStartingAt'], errors='coerce')
    ameria_df['areaPriceStartingAt'] = pd.to_numeric(ameria_df['areaPriceStartingAt'], errors='coerce')
    ameria_df['apartmentsCount'] = pd.to_numeric(ameria_df['apartmentsCount'], errors='coerce')
    ameria_df['availableForSale'] = pd.to_numeric(ameria_df['availableForSale'], errors='coerce')
    ameria_agg = ameria_df.groupby('distrinct').agg(
        new_price_min=('apartmentPriceStartingAt', 'min'),
        new_price_max=('apartmentPriceStartingAt', 'max'),
        new_price_mean=('apartmentPriceStartingAt', 'mean'),
        new_price_median=('apartmentPriceStartingAt', 'median'),
        new_area_mean=('areaPriceStartingAt', 'mean'),
        buildings_count=('id', 'count'),
        apartments_total=('apartmentsCount', 'sum'),
        apartments_free=('availableForSale', 'sum')
    ).reset_index()
    ameria_agg['apartments_sold'] = ameria_agg['apartments_total'] - ameria_agg['apartments_free']
    ameria_agg['sold_pct'] = 100 * ameria_agg['apartments_sold'] / ameria_agg['apartments_total'].replace(0, 1)

    # --- Aggregate OSM business counts ---
    osm_counts = osm_df.groupby('district')['category'].value_counts().unstack(fill_value=0).reset_index()

    # --- Merge all data ---
    districts_gdf = districts_gdf.merge(sell_agg, left_on='district_name', right_on='distrinct', how='left')
    districts_gdf = districts_gdf.merge(rent_agg.add_suffix('_rent'), left_on='district_name', right_on='distrinct_rent', how='left')
    districts_gdf = districts_gdf.merge(ameria_agg, left_on='district_name', right_on='distrinct', how='left')
    districts_gdf = districts_gdf.merge(osm_counts, left_on='district_name', right_on='district', how='left').fillna(0)

    # Fill missing numeric values to zero to avoid errors
    districts_gdf.fillna(0, inplace=True)

    # Choose metric column
    metric_column = metric_choice if metric_choice in districts_gdf.columns else 'mean_price_amd'

    # --- Create Folium map ---
    m = folium.Map(location=[40.18, 44.51], zoom_start=11, tiles='cartodbpositron')

    # Add CSS to make popup font smaller
    popup_css = """
    <style>
    .leaflet-popup-content {
        font-size: 12px !important;
        line-height: 1.2em !important;
        max-width: 250px !important;
    }
    </style>
    """
    m.get_root().header.add_child(folium.Element(popup_css))

    min_val = districts_gdf[metric_column].min()
    max_val = districts_gdf[metric_column].max()
    colormap = linear.YlOrRd_09.scale(min_val, max_val)
    colormap.caption = f"{data_source} - {metric_choice.replace('_', ' ').capitalize()}"
    colormap.add_to(m)

    # Hide colormap ticks CSS
    hide_ticks_css = """
    <style>
    .legend .tick text { 
        display: none !important;
    }
    </style>
    """

    class HideTicks(MacroElement):
        def __init__(self):
            super().__init__()
            self._template = Template(f"""
            {{% macro html(this, kwargs) %}}
            {hide_ticks_css}
            {{% endmacro %}}
            """)

    m.get_root().add_child(HideTicks())

    # Style districts polygons
    def style_function(feature):
        val = feature['properties'].get(metric_column, 0)
        if val == 0:
            return {'fillColor': '#cccccc', 'color': 'black', 'weight': 1, 'fillOpacity': 0.2}
        else:
            return {'fillColor': colormap(val), 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}

    # Tooltip fields (minimal info)
    tooltip_fields = ['district_name', metric_column]
    tooltip_aliases = ['District:', f'{metric_choice.replace("_", " ").capitalize()}:']

    # Popup fields: detailed + all OSM categories dynamically added
    popup_fields = [
        'district_name',
        'mean_price_amd', 'median_price_amd', 'max_price_amd', 'min_price_amd',
        'mean_price_amd_per_1ms_area', 'median_price_amd_per_1ms_area',
        'rooms_mean', 'square_meters_mean', 'count_listings',
        'mean_price_amd_rent', 'median_price_amd_rent', 'max_price_amd_rent', 'min_price_amd_rent',
        'mean_price_amd_per_1ms_area_rent', 'median_price_amd_per_1ms_area_rent',
        'rooms_mean_rent', 'square_meters_mean_rent', 'count_listings_rent',
        'new_price_min', 'new_price_max', 'new_price_mean', 'new_price_median', 'new_area_mean',
        'buildings_count', 'apartments_total', 'apartments_free', 'apartments_sold', 'sold_pct'
    ]
    extra_osm_cats = [c for c in districts_gdf.columns if c not in popup_fields + ['geometry', 'distrinct', 'distrinct_rent', 'district', 'district_name']]
    popup_fields.extend(extra_osm_cats)

    popup_aliases = [
        'District',
        'Sell Mean Price (AMD)', 'Sell Median Price (AMD)', 'Sell Max Price (AMD)', 'Sell Min Price (AMD)',
        'Sell Mean Price/m²', 'Sell Median Price/m²',
        'Sell Avg Rooms', 'Sell Avg Sqm', 'Sell Listings Count',
        'Rent Mean Price (AMD)', 'Rent Median Price (AMD)', 'Rent Max Price (AMD)', 'Rent Min Price (AMD)',
        'Rent Mean Price/m²', 'Rent Median Price/m²',
        'Rent Avg Rooms', 'Rent Avg Sqm', 'Rent Listings Count',
        'Ameria New Price Min', 'Ameria New Price Max', 'Ameria New Price Mean', 'Ameria New Price Median', 'Ameria New Area Mean',
        'Ameria Buildings Count', 'Ameria Total Apartments', 'Ameria Free Apartments', 'Ameria Sold Apartments', 'Ameria Sold %'
    ]
    popup_aliases.extend([f"OSM {c.capitalize()}" for c in extra_osm_cats])

    # Add district polygons with popup and tooltip
    folium.GeoJson(
        data=districts_gdf.to_json(),
        name='Districts',
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, aliases=tooltip_aliases, localize=True, labels=True),
        popup=folium.GeoJsonPopup(fields=popup_fields, aliases=popup_aliases, localize=True, labels=True, max_width=350),
        highlight_function=lambda x: {'weight': 3, 'color': 'blue'}
    ).add_to(m)

    # Add filtered OSM points only if checkbox enabled and categories selected
    if show_osm_points and selected_osm_categories:
        filtered_osm = osm_df[osm_df['category'].isin(selected_osm_categories)]
        for idx, row in filtered_osm.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=4,
                popup=f"Category: {row['category']}<br>District: {row['district']}",
                color='blue',
                fill=True,
                fill_opacity=0.6,
            ).add_to(m)

    st.subheader(f"Map: {data_source} by District colored by {metric_choice.replace('_', ' ').capitalize()}")
    st.markdown(
        "🛈 **Hint:** Hover on districts for metric preview, click for full details."
        + (" OSM points shown as blue dots." if show_osm_points and selected_osm_categories else "")
    )
    st_folium(m, width=1100, height=800)

    # --- Summary tables ---
    st.subheader("Summary: Apartments for Sale")
    st.dataframe(
        sell_agg.rename(columns={'distrinct': 'district'})
        .style.format({
            'mean_price_amd': "{:,.0f}", 'median_price_amd': "{:,.0f}",
            'max_price_amd': "{:,.0f}", 'min_price_amd': "{:,.0f}",
            'mean_price_amd_per_1ms_area': "{:,.0f}", 'median_price_amd_per_1ms_area': "{:,.0f}",
            'rooms_mean': "{:.2f}", 'square_meters_mean': "{:.2f}",
            'count_listings': "{:,.0f}"
        })
    )

    st.subheader("Summary: Apartments for Rent")
    st.dataframe(
        rent_agg.rename(columns={'distrinct': 'district'})
        .style.format({
            'mean_price_amd': "{:,.0f}", 'median_price_amd': "{:,.0f}",
            'max_price_amd': "{:,.0f}", 'min_price_amd': "{:,.0f}",
            'mean_price_amd_per_1ms_area': "{:,.0f}", 'median_price_amd_per_1ms_area': "{:,.0f}",
            'rooms_mean': "{:.2f}", 'square_meters_mean': "{:.2f}",
            'count_listings': "{:,.0f}"
        })
    )

    st.subheader("Summary: Ameria Primary Market (New Buildings)")
    st.dataframe(
        ameria_agg.rename(columns={'distrinct': 'district'})
        .style.format({
            'new_price_min': "{:,.0f}", 'new_price_max': "{:,.0f}",
            'new_price_mean': "{:,.0f}", 'new_price_median': "{:,.0f}",
            'new_area_mean': "{:,.0f}", 'buildings_count': "{:,.0f}",
            'apartments_total': "{:,.0f}", 'apartments_free': "{:,.0f}",
            'apartments_sold': "{:,.0f}", 'sold_pct': "{:.2f}%"
        })
    )

    st.subheader("Summary: OSM Business Categories Count by District")
    if not osm_counts.empty:
        osm_counts_fixed = osm_counts.rename(columns={'district': 'district_name'}).copy()
        for col in osm_counts_fixed.columns:
            if col != 'district_name':
                osm_counts_fixed[col] = pd.to_numeric(osm_counts_fixed[col], errors='coerce').fillna(0)
        st.dataframe(osm_counts_fixed)
    else:
        st.info("No OSM business category data available.")
