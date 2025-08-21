import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
from branca.colormap import linear
import h3
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

# --- H3 v3→v4 compatibility shims (safe no-ops if already present) ---
# v3 name -> v4 function
if not hasattr(h3, "geo_to_h3"):
    h3.geo_to_h3 = h3.latlng_to_cell

if not hasattr(h3, "h3_to_geo_boundary"):
    def _h3_to_geo_boundary_compat(h, geo_json: bool = False):
        # v4 returns [(lat, lng), ...]
        coords_latlng = h3.cell_to_boundary(h)
        # v3 geo_json=True expected (lon, lat) for GeoJSON/Shapely
        return [(lng, lat) for (lat, lng) in coords_latlng] if geo_json else coords_latlng
    h3.h3_to_geo_boundary = _h3_to_geo_boundary_compat

if not hasattr(h3, "h3_to_parent"):
    h3.h3_to_parent = h3.cell_to_parent

if not hasattr(h3, "h3_to_children"):
    def _h3_to_children_compat(h, res):
        return list(h3.cell_to_children(h, res))
    h3.h3_to_children = _h3_to_children_compat


# Utility function to convert an H3 index to a Shapely Polygon
def h3_to_polygon(h):
    """Converts an H3 index to a Shapely Polygon (expects lon,lat order)."""
    # v4: returns [(lat, lng), ...] – convert to (lon, lat) for Shapely/GeoJSON
    boundary_latlng = h3.cell_to_boundary(h)
    boundary_lonlat = [(lng, lat) for (lat, lng) in boundary_latlng]
    return Polygon(boundary_lonlat)


def show():
    st.title("🛰️ Yerevan Real Estate & Business Dashboard (H3 Hexagons)")

    st.sidebar.header("⚙️ Map Configuration")
    resolution = st.sidebar.slider(
        "Select H3 Resolution (smaller number = larger hex)",
        min_value=5, max_value=10, value=8,
        help="Resolution 8 is optimal for city-level analysis."
    )

    data_source = st.sidebar.selectbox(
        "Select Data Source for Coloring Hexagons:",
        ['Apartments Sell', 'Apartments Rent', 'Apartments Primary Market', 'Community Services & Businesses']
    )

    show_osm_points = st.sidebar.checkbox("Show Community Services & Businesses on Map", value=False)

    @st.cache_data(ttl=3600)
    def load_and_prep_data(resolution):
        districts_gdf = st.session_state.data['yerevan_distrincts'].copy().to_crs(epsg=4326)
        districts_gdf['geometry'] = districts_gdf['geometry'].buffer(0)
        districts_gdf = districts_gdf.rename(columns={'district': 'district_name'})

        sell_df = st.session_state.data['list_apartments_sell'].copy()
        sell_cols_to_numeric = ['price_amd', 'price_amd_per_1ms_area', 'square_meters', 'number_of_rooms', 'latitude', 'longitude']
        for col in sell_cols_to_numeric:
            sell_df[col] = pd.to_numeric(sell_df[col], errors='coerce')
        sell_df.dropna(subset=['price_amd', 'square_meters', 'latitude', 'longitude'], inplace=True)

        rent_df = st.session_state.data['list_apartments_rent'].copy()
        rent_cols_to_numeric = ['price_amd', 'price_amd_per_1ms_area', 'square_meters', 'number_of_rooms', 'latitude', 'longitude']
        for col in rent_cols_to_numeric:
            rent_df[col] = pd.to_numeric(rent_df[col], errors='coerce')
        rent_df.dropna(subset=['price_amd', 'square_meters', 'latitude', 'longitude'], inplace=True)

        ameria_df = st.session_state.data['ameria_primary_market'].copy()
        ameria_cols_to_numeric = ['apartmentPriceStartingAt', 'areaPriceStartingAt', 'apartmentsCount', 'availableForSale', 'latitude', 'longitude']
        for col in ameria_cols_to_numeric:
            ameria_df[col] = pd.to_numeric(ameria_df[col], errors='coerce')
        ameria_df.dropna(subset=['apartmentPriceStartingAt', 'latitude', 'longitude'], inplace=True)

        osm_df = st.session_state.data['osm_points'].copy()
        osm_df['lat'] = pd.to_numeric(osm_df['lat'], errors='coerce')
        osm_df['lon'] = pd.to_numeric(osm_df['lon'], errors='coerce')
        osm_df.dropna(subset=['lat', 'lon'], inplace=True)

        # v4 encoder: lat,lng -> H3 index
        def assign_h3_index(df, lat_col, lon_col, res):
            df['h3'] = df.apply(
                lambda row: h3.latlng_to_cell(float(row[lat_col]), float(row[lon_col]), int(res))
                if pd.notna(row[lat_col]) and pd.notna(row[lon_col]) else None,
                axis=1
            )
            return df

        sell_df = assign_h3_index(sell_df, 'latitude', 'longitude', resolution)
        rent_df = assign_h3_index(rent_df, 'latitude', 'longitude', resolution)
        ameria_df = assign_h3_index(ameria_df, 'latitude', 'longitude', resolution)
        osm_df = assign_h3_index(osm_df, 'lat', 'lon', resolution)

        return districts_gdf, sell_df, rent_df, ameria_df, osm_df

    districts_gdf, sell_df, rent_df, ameria_df, osm_df = load_and_prep_data(resolution)

    selected_osm_categories = []
    selected_subcategories = {}
    selected_bank_names = []

    if show_osm_points:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📍 Filter Businesses to Display")
        osm_categories_sorted = sorted(osm_df['main_category'].dropna().unique().tolist())
        selected_osm_categories = st.sidebar.multiselect(
            "Select Main Categories:",
            osm_categories_sorted,
            default=[],
        )

        for category in selected_osm_categories:
            subcategories = sorted(osm_df[osm_df['main_category'] == category]['category'].unique().tolist())
            with st.sidebar.expander(f"Filter Subcategories for {category}", expanded=False):
                selected_subcategories[category] = st.multiselect(
                    f"Select subcategories for {category}:",
                    subcategories,
                    default=subcategories
                )
                if category == "Financial Services":
                    unique_bank_names = sorted(osm_df[osm_df['main_category'] == category]['name'].unique().tolist())
                    selected_bank_names = st.multiselect(
                        f"Select Bank Name:",
                        unique_bank_names,
                        default=unique_bank_names
                    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Metric Selection")

    if data_source in ['Apartments Sell', 'Apartments Rent']:
        metric_type = st.sidebar.radio("Metric Type:", ["Price (AMD)", "Price/m² (AMD)", "Area (m²)", "Rooms"], horizontal=True)
        metric_agg = st.sidebar.radio("Statistic:", ["Mean", "Median", "Min", "Max", "Count"], horizontal=True)
    elif data_source == 'Apartments Primary Market':
        metric_type = st.sidebar.radio("Metric Type:", ["Price (AMD)", "Price/m² (AMD)", "Building Count", "Apartment Count", "Sold %"], horizontal=True)
        metric_agg = st.sidebar.radio("Statistic:", ["Mean", "Median", "Min", "Max", "Sum"], horizontal=True)
    else:  # Community Services
        osm_main_cats = sorted(osm_df['main_category'].dropna().unique())
        metric_type = st.sidebar.selectbox("Business Category:", osm_main_cats)
        metric_agg = "Count"

    def get_aggregated_gdf(df, metrics, h3_res_col='h3'):
        agg_df = df.groupby(h3_res_col).agg(metrics).reset_index()
        agg_df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in agg_df.columns.values]
        agg_df = agg_df.rename(columns={f'{h3_res_col}_': h3_res_col})
        agg_df['geometry'] = agg_df[h3_res_col].apply(h3_to_polygon)
        return gpd.GeoDataFrame(agg_df, geometry='geometry', crs='EPSG:4326').dropna(subset=['geometry'])

    sell_agg_metrics = {
        'price_amd': ['mean', 'median', 'min', 'max', 'count'],
        'price_amd_per_1ms_area': ['mean', 'median'],
        'square_meters': ['mean', 'median'],
        'number_of_rooms': ['mean', 'median']
    }
    rent_agg_metrics = {k: v for k, v in sell_agg_metrics.items()}
    ameria_agg_metrics = {
        'apartmentPriceStartingAt': ['mean', 'median', 'min', 'max'],
        'areaPriceStartingAt': ['mean', 'median'],
        'id': [('building_count', 'count')],
        'apartmentsCount': ['sum'],
        'availableForSale': ['sum']
    }

    if data_source == 'Apartments Sell':
        agg_gdf = get_aggregated_gdf(sell_df, sell_agg_metrics)
        cols = ['price_amd_mean', 'price_amd_median', 'price_amd_min', 'price_amd_max',
                'price_amd_per_1ms_area_mean', 'price_amd_per_1ms_area_median']
        agg_gdf[cols] = agg_gdf[cols].round().round(-3)
        cols = ['square_meters_mean', 'square_meters_median', 'number_of_rooms_mean', 'number_of_rooms_median']
        agg_gdf[cols] = agg_gdf[cols].round(1)
    elif data_source == 'Apartments Rent':
        agg_gdf = get_aggregated_gdf(rent_df, rent_agg_metrics)
        cols = ['price_amd_mean', 'price_amd_median', 'price_amd_min', 'price_amd_max',
                'price_amd_per_1ms_area_mean', 'price_amd_per_1ms_area_median']
        agg_gdf[cols] = agg_gdf[cols].round().round(-3)
        cols = ['square_meters_mean', 'square_meters_median', 'number_of_rooms_mean', 'number_of_rooms_median']
        agg_gdf[cols] = agg_gdf[cols].round(1)
    elif data_source == 'Apartments Primary Market':
        agg_gdf = get_aggregated_gdf(ameria_df, ameria_agg_metrics)
        agg_gdf['apartments_sold_sum'] = agg_gdf['apartmentsCount_sum'] - agg_gdf['availableForSale_sum']
        agg_gdf['sold_pct_mean'] = (100 * agg_gdf['apartments_sold_sum'] / agg_gdf['apartmentsCount_sum'].replace(0, 1)).round(1)
    else:  # OSM
        osm_counts = osm_df.groupby(['h3', 'main_category']).size().unstack(fill_value=0).reset_index()
        osm_counts['geometry'] = osm_counts['h3'].apply(h3_to_polygon)
        agg_gdf = gpd.GeoDataFrame(osm_counts, geometry='geometry', crs='EPSG:4326').dropna(subset=['geometry'])

    col_map = {
        'Apartments Sell': {'Price (AMD)': 'price_amd', 'Price/m² (AMD)': 'price_amd_per_1ms_area', 'Area (m²)': 'square_meters', 'Rooms': 'number_of_rooms'},
        'Apartments Rent': {'Price (AMD)': 'price_amd', 'Price/m² (AMD)': 'price_amd_per_1ms_area', 'Area (m²)': 'square_meters', 'Rooms': 'number_of_rooms'},
        'Apartments Primary Market': {'Price (AMD)': 'apartmentPriceStartingAt', 'Price/m² (AMD)': 'areaPriceStartingAt', 'Building Count': 'id_building_count', 'Apartment Count': 'apartmentsCount_sum', 'Sold %': 'sold_pct'},
    }

    metric_column = None
    if data_source != 'Community Services & Businesses':
        base_col = col_map[data_source][metric_type]
        agg_suffix = metric_agg.lower() if metric_agg != "Count" else 'count'

        if base_col == 'id_building_count':
            metric_column = 'id_building_count'
        elif base_col == 'apartmentsCount_sum':
            metric_column = 'apartmentsCount_sum'
        elif base_col == 'sold_pct':
            metric_column = 'sold_pct_mean'
        else:
            metric_column = f"{base_col}_{agg_suffix}"
    else:
        metric_column = metric_type

    if metric_column not in agg_gdf.columns:
        st.error(f"Selected metric '{metric_column}' is not available. This might happen if there's no data for the chosen category. Please select a different metric.")
        st.stop()

    m = folium.Map(location=[40.18, 44.51], zoom_start=12, tiles='cartodbpositron')

    folium.GeoJson(
        districts_gdf,
        style_function=lambda x: {'color': 'black', 'weight': 2.5, 'fillOpacity': 0.0, 'dashArray': '5, 5'},
        tooltip=folium.GeoJsonTooltip(fields=['district_name'], aliases=['District:']),
        name='District Boundaries'
    ).add_to(m)

    min_val, max_val = agg_gdf[metric_column].min(), agg_gdf[metric_column].max()
    colormap = linear.YlOrRd_09.scale(min_val, max_val)
    colormap.caption = f"{metric_type} ({metric_agg})"

    popup_fields = [c for c in agg_gdf.columns if c not in ['h3', 'geometry']]

    folium.GeoJson(
        agg_gdf,
        name='H3 Hexagons',
        style_function=lambda feature: {
            'fillColor': colormap(feature['properties'][metric_column]) if pd.notna(feature['properties'][metric_column]) and feature['properties'][metric_column] > 0 else '#cccccc',
            'color': 'black', 'weight': 0.5,
            'fillOpacity': 0.75 if pd.notna(feature['properties'][metric_column]) and feature['properties'][metric_column] > 0 else 0.3,
        },
        tooltip=folium.GeoJsonTooltip(fields=['h3', metric_column], aliases=['H3 Index:', f'{metric_type} ({metric_agg}):'], localize=True, sticky=True),
        popup=folium.GeoJsonPopup(fields=popup_fields, aliases=[f.replace("_", " ").title() for f in popup_fields], localize=True, max_width=400),
        highlight_function=lambda x: {'weight': 3, 'color': '#1E90FF', 'fillOpacity': 0.9}
    ).add_to(m)

    if max_val > 0:
        colormap.add_to(m)

    if show_osm_points and selected_osm_categories:
        filtered_osm = osm_df[osm_df['main_category'].isin(selected_osm_categories)].copy()

        chosen_subcategories = []
        for cat in selected_osm_categories:
            if cat in selected_subcategories:
                chosen_subcategories.extend(selected_subcategories[cat])
        if chosen_subcategories:
            filtered_osm = filtered_osm[filtered_osm['category'].isin(chosen_subcategories)]

        if "Financial Services" in selected_osm_categories and selected_bank_names:
            filtered_osm = filtered_osm[(filtered_osm['main_category'] != "Financial Services") | (filtered_osm['name'].isin(selected_bank_names))]

        unique_cats = filtered_osm['category'].unique()
        category_colors = {cat: mcolors.rgb2hex(plt.cm.get_cmap('tab10')(i % 10)) for i, cat in enumerate(unique_cats)}

        legend_html = '<div style="position: fixed; bottom: 50px; left: 10px; width: auto; background-color: white; border:2px solid grey; z-index:9999; font-size:12px; padding: 5px; border-radius: 5px;"><b>Business Legend</b><br>'
        for category, color in category_colors.items():
            legend_html += f'<i style="background:{color}; width:15px; height:15px; border-radius:50%; display:inline-block; margin-right:5px;"></i>{category}<br>'
        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))

        for _, row in filtered_osm.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=4,
                popup=f"<b>{row['name']}</b><br>Category: {row['category']}<br>District: {row['district']}",
                color=category_colors.get(row['category'], 'gray'),
                fill=True, fill_opacity=0.8
            ).add_to(m)

    folium.LayerControl().add_to(m)

    st.subheader(f"Map: {data_source} by H3 Hexagons (Resolution {resolution})")
    st.markdown(f"Colored by: **{metric_type} ({metric_agg})**")
    st.markdown("🛈 **Hint:** Hover on a hexagon for a quick metric view, or click for all details. District boundaries are shown with dashed lines.")
    st_folium(m, width=1100, height=700)

    st.markdown("---")
    view_choice = st.radio("📋 What would you like to view below?", ["📈 Visual Dashboard", "📊 Aggregated Tables"])

    if view_choice == "📊 Aggregated Tables":
        st.subheader(f"Aggregated Data Table: {data_source} at H3 Resolution {resolution}")
        display_df = agg_gdf.drop(columns='geometry').rename(columns={'h3_': 'h3'})
        st.dataframe(display_df.style.format(precision=2))

    elif view_choice == "📈 Visual Dashboard":
        st.markdown("## 📈 Visual Analytics Dashboard")

        plot_df = agg_gdf.nlargest(20, metric_column)

        st.markdown(f"### Top 20 Hexagons by: **{metric_type} ({metric_agg})**")

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=plot_df.sort_values(metric_column, ascending=False), x="h3", y=metric_column, palette="viridis", ax=ax)
        ax.set_ylabel(f"{metric_type} ({metric_agg})")
        ax.set_xlabel(f"H3 Hexagon Index (Resolution {resolution})")
        ax.set_title(f"Top 20 Hexagons by {metric_type.replace('_', ' ').capitalize()}")
        ax.tick_params(axis='x', rotation=90)
        st.pyplot(fig)


if __name__ == "__main__":
    show()
