# import streamlit as st
# import geopandas as gpd
# import pandas as pd
# import folium
# from streamlit_folium import st_folium
# from shapely.geometry import Polygon
# from branca.colormap import linear
# import h3
# from utils.data_prep import assign_h3

# def h3_to_polygon(h):
#     boundary = h3.h3_to_geo_boundary(h, geo_json=True)
#     return Polygon(boundary)

# def aggregate_and_build_gdf(df, h3_col, agg_funcs, resolution):
#     df['h3_res'] = df[h3_col].apply(lambda x: h3.h3_to_parent(x, resolution))
#     agg_df = df.groupby('h3_res').agg(agg_funcs).reset_index()
#     agg_df['geometry'] = agg_df['h3_res'].apply(h3_to_polygon)
#     gdf = gpd.GeoDataFrame(agg_df, geometry='geometry', crs='EPSG:4326')
#     gdf = gdf.set_geometry('geometry')
#     return gdf

# def show():
#     st.title("🏙️ Yerevan Real Estate & Business Dashboard (H3 Hexagons)")
#     st.subheader("🏙️ New features Coming Soon ...")

#     resolution = st.slider("Select H3 resolution (hex size):", min_value=6, max_value=9, value=8)
#     data_source = st.selectbox(
#         "Select data source for coloring hexagons:",
#         ['Sell', 'Rent', 'Ameria Primary Market', 'OSM Business Counts']
#     )
#     show_osm_points = st.checkbox("Show OSM business points on map", value=False)

#     osm_df = st.session_state.data['osm_points'].copy()
#     osm_df = assign_h3(osm_df, lat_col='lat', lon_col='lon', resolution=resolution)
#     osm_df['category'] = osm_df['category'].astype(str)
#     osm_df['district'] = osm_df['district'].astype(str)

#     sell_df = st.session_state.data['list_apartments_sell'].copy()
#     sell_df = assign_h3(sell_df, lat_col='latitude', lon_col='longitude', resolution=resolution)
#     rent_df = st.session_state.data['list_apartments_rent'].copy()
#     rent_df = assign_h3(rent_df, lat_col='latitude', lon_col='longitude', resolution=resolution)
#     ameria_df = st.session_state.data['ameria_primary_market'].copy()
#     ameria_df = assign_h3(ameria_df, lat_col='latitude', lon_col='longitude', resolution=resolution)

#     sell_metrics = {
#         'price_amd': ['mean', 'median', 'max', 'min', 'count'],
#         'price_amd_per_1ms_area': ['mean', 'median'],
#         'number_of_rooms': ['mean'],
#         'square_meters': ['mean'],
#     }
#     rent_metrics = {
#         'price_amd': ['mean', 'median', 'max', 'min', 'count'],
#         'price_amd_per_1ms_area': ['mean', 'median'],
#         'number_of_rooms': ['mean'],
#         'square_meters': ['mean'],
#     }
#     ameria_metrics = {
#         'apartmentPriceStartingAt': ['min', 'max', 'mean', 'median'],
#         'areaPriceStartingAt': ['mean'],
#         'id': ['count'],
#         'apartmentsCount': ['sum'],
#         'availableForSale': ['sum']
#     }

#     if data_source == 'Sell':
#         for c in ['price_amd', 'price_amd_per_1ms_area', 'number_of_rooms', 'square_meters']:
#             sell_df[c] = pd.to_numeric(sell_df[c], errors='coerce')
#         sell_df = sell_df.dropna(subset=['h3', 'price_amd', 'number_of_rooms', 'square_meters'])
#         agg_gdf = aggregate_and_build_gdf(sell_df, 'h3', sell_metrics, resolution)
#         agg_gdf.columns = ['h3_res'] + ['_'.join(col).strip() if isinstance(col, tuple) else col for col in agg_gdf.columns[1:-1]] + ['geometry']
#         agg_gdf = agg_gdf.set_geometry('geometry')
#         metric_choices = [c for c in agg_gdf.columns if c not in ['h3_res', 'geometry']]
#     elif data_source == 'Rent':
#         for c in ['price_amd', 'price_amd_per_1ms_area', 'number_of_rooms', 'square_meters']:
#             rent_df[c] = pd.to_numeric(rent_df[c], errors='coerce')
#         rent_df = rent_df.dropna(subset=['h3', 'price_amd', 'number_of_rooms', 'square_meters'])
#         agg_gdf = aggregate_and_build_gdf(rent_df, 'h3', rent_metrics, resolution)
#         agg_gdf.columns = ['h3_res'] + ['_'.join(col).strip() if isinstance(col, tuple) else col for col in agg_gdf.columns[1:-1]] + ['geometry']
#         agg_gdf = agg_gdf.set_geometry('geometry')

#         metric_choices = [c for c in agg_gdf.columns if c not in ['h3_res', 'geometry']]
#     elif data_source == 'Ameria Primary Market':
#         for c in ['apartmentPriceStartingAt', 'areaPriceStartingAt', 'id', 'apartmentsCount', 'availableForSale']:
#             ameria_df[c] = pd.to_numeric(ameria_df[c], errors='coerce')
#         ameria_df = ameria_df.dropna(subset=['h3', 'apartmentPriceStartingAt'])
#         agg_gdf = aggregate_and_build_gdf(ameria_df, 'h3', ameria_metrics, resolution)
#         agg_gdf.columns = ['h3_res'] + ['_'.join(col).strip() if isinstance(col, tuple) else col for col in agg_gdf.columns[1:-1]] + ['geometry']
#         agg_gdf = agg_gdf.set_geometry('geometry')
#         agg_gdf['apartments_sold_sum'] = agg_gdf['apartmentsCount_sum'] - agg_gdf['availableForSale_sum']
#         agg_gdf['sold_pct'] = 100 * agg_gdf['apartments_sold_sum'] / agg_gdf['apartmentsCount_sum'].replace(0, 1)
#         agg_gdf = agg_gdf.set_geometry('geometry')
#         metric_choices = [c for c in agg_gdf.columns if c not in ['h3_res', 'geometry']] + ['apartments_sold_sum', 'sold_pct']
#     else:
#         osm_df['count'] = 1
#         osm_counts = osm_df.groupby(['h3', 'category']).size().unstack(fill_value=0).reset_index()
#         osm_counts['geometry'] = osm_counts['h3'].apply(h3_to_polygon)
#         agg_gdf = gpd.GeoDataFrame(osm_counts, geometry='geometry', crs='EPSG:4326')
#         agg_gdf = agg_gdf.set_geometry('geometry')
#         metric_choices = [c for c in agg_gdf.columns if c not in ['h3', 'geometry']]

#     metric_choice = st.selectbox("Select metric to color hexagons by:", metric_choices)

#     m = folium.Map(location=[40.18, 44.51], zoom_start=11, tiles='cartodbpositron')

#     min_val = agg_gdf[metric_choice].min()
#     max_val = agg_gdf[metric_choice].max()
#     colormap = linear.YlOrRd_09.scale(min_val, max_val)
#     colormap.caption = f"{data_source} - {metric_choice.replace('_', ' ').capitalize()}"
#     colormap.add_to(m)

#     def style_function(feature):
#         val = feature['properties'].get(metric_choice, 0)
#         if pd.isna(val) or val == 0:
#             return {'fillColor': '#cccccc', 'color': 'gray', 'weight': 0.5, 'fillOpacity': 0.2}
#         else:
#             return {'fillColor': colormap(val), 'color': 'black', 'weight': 0.7, 'fillOpacity': 0.7}

#     tooltip_fields = ['h3_res', metric_choice]
#     tooltip_aliases = ['H3 Hex', metric_choice.replace('_', ' ').capitalize()]

#     popup_fields = [metric_choice]
#     popup_aliases = [metric_choice.replace('_', ' ').capitalize()]

#     folium.GeoJson(
#         agg_gdf.to_json(),
#         name='H3 Hexagons',
#         style_function=style_function,
#         tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, aliases=tooltip_aliases, localize=True, labels=True),
#         popup=folium.GeoJsonPopup(fields=popup_fields, aliases=popup_aliases, localize=True, labels=True),
#         highlight_function=lambda x: {'weight': 3, 'color': 'blue'}
#     ).add_to(m)

#     if show_osm_points:
#         osm_categories = osm_df['category'].dropna().unique().tolist()
#         selected_osm_categories = st.multiselect(
#             "Select OSM business categories to show on map:",
#             sorted(osm_categories),
#             default=[]
#         )
#         if selected_osm_categories:
#             filtered_osm = osm_df[osm_df['category'].isin(selected_osm_categories)]
#             for _, row in filtered_osm.iterrows():
#                 folium.CircleMarker(
#                     location=[row['lat'], row['lon']],
#                     radius=3,
#                     popup=f"Category: {row['category']}<br>District: {row['district']}",
#                     color='blue',
#                     fill=True,
#                     fill_opacity=0.6,
#                 ).add_to(m)

#     folium.LayerControl().add_to(m)

#     st.subheader(f"Map: {data_source} by H3 hexagons at resolution {resolution}, colored by {metric_choice.replace('_', ' ').capitalize()}")
#     st.markdown(
#         "🛈 **Hint:** Hover on hexagons for metric preview, click for full details."
#         + (" OSM points shown as blue dots." if show_osm_points else "")
#     )
#     st_folium(m, width=1100, height=800)

#     if data_source == 'Sell':
#         st.subheader("Summary: Apartments for Sale")
#         st.dataframe(
#             sell_df.groupby('h3').agg(
#                 mean_price_amd=('price_amd', 'mean'),
#                 median_price_amd=('price_amd', 'median'),
#                 max_price_amd=('price_amd', 'max'),
#                 min_price_amd=('price_amd', 'min'),
#                 mean_price_amd_per_1ms_area=('price_amd_per_1ms_area', 'mean'),
#                 median_price_amd_per_1ms_area=('price_amd_per_1ms_area', 'median'),
#                 rooms_mean=('number_of_rooms', 'mean'),
#                 square_meters_mean=('square_meters', 'mean'),
#                 count_listings=('price_amd', 'count')
#             ).reset_index()
#         )
#     elif data_source == 'Rent':
#         st.subheader("Summary: Apartments for Rent")
#         st.dataframe(
#             rent_df.groupby('h3').agg(
#                 mean_price_amd=('price_amd', 'mean'),
#                 median_price_amd=('price_amd', 'median'),
#                 max_price_amd=('price_amd', 'max'),
#                 min_price_amd=('price_amd', 'min'),
#                 mean_price_amd_per_1ms_area=('price_amd_per_1ms_area', 'mean'),
#                 median_price_amd_per_1ms_area=('price_amd_per_1ms_area', 'median'),
#                 rooms_mean=('number_of_rooms', 'mean'),
#                 square_meters_mean=('square_meters', 'mean'),
#                 count_listings=('price_amd', 'count')
#             ).reset_index()
#         )
#     elif data_source == 'Ameria Primary Market':
#         st.subheader("Summary: Ameria Primary Market (New Buildings)")
#         st.dataframe(
#             ameria_df.groupby('h3').agg(
#                 apartmentPriceStartingAt_min=('apartmentPriceStartingAt', 'min'),
#                 apartmentPriceStartingAt_max=('apartmentPriceStartingAt', 'max'),
#                 apartmentPriceStartingAt_mean=('apartmentPriceStartingAt', 'mean'),
#                 apartmentPriceStartingAt_median=('apartmentPriceStartingAt', 'median'),
#                 areaPriceStartingAt_mean=('areaPriceStartingAt', 'mean'),
#                 id_count=('id', 'count'),
#                 apartmentsCount_sum=('apartmentsCount', 'sum'),
#                 availableForSale_sum=('availableForSale', 'sum')
#             ).reset_index()
#         )
#     else:
#         st.subheader("Summary: OSM Business Categories Count by Hex")
#         if not osm_counts.empty:
#             st.dataframe(osm_counts)
#         else:
#             st.info("No OSM business category data available.")

# if __name__ == "__main__":
#     show()

import streamlit as st
def show():
    st.title("Coming soon.")