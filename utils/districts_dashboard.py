import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
from branca.colormap import linear
from branca.element import MacroElement, Template
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def show():
    st.title("🏙️ Yerevan Real Estate & Business Dashboard")

    data_source = st.selectbox(
        "Select data source for coloring districts:",
        ['Apartments Sell', 'Apartments Rent', 'Apartments Primary Market', 'Community Services & Businesses']
    )

    show_osm_points = st.checkbox("Show Community Services & Businesses as points on map", value=False)

    osm_df = st.session_state.data['osm_points'].copy()
    osm_df['category'] = osm_df['category'].astype(str)
    osm_df['main_category'] = osm_df['main_category'].astype(str)
    osm_df['district'] = osm_df['district'].astype(str)
    osm_categories = osm_df['main_category'].dropna().unique().tolist()
    osm_categories_sorted = sorted(osm_categories)

    selected_osm_categories = []
    selected_subcategories = {}
    selected_bank_names = []

    if show_osm_points:
        selected_osm_categories = st.multiselect(
            "Select Community Services & Businesses to show on map:",
            osm_categories_sorted,
            default=[],
            help="Select which Community Services & Businesses to show on map"
        )
        
        for category in selected_osm_categories:
            subcategories = osm_df[osm_df['main_category'] == category]['category'].unique().tolist()
            subcategories_sorted = sorted(subcategories)
            
            if category == "Financial Services":
                unique_bank_names = osm_df[osm_df['main_category'] == category]['name'].unique().tolist()
                with st.expander(f"Select Subcategories for {category}"):
                    selected_subcategories[category] = st.multiselect(
                        f"Select subcategories under {category}:",
                        subcategories_sorted,
                        default=subcategories_sorted,  
                        help=f"Select which subcategories of {category} to show on the map"
                    )
                    selected_bank_names = st.multiselect(
                        f"Select Bank name under {category}:",
                        unique_bank_names,
                        default=unique_bank_names,  
                        help=f"Select which Bank of {category} to show on the map"
                    )
            else:
                with st.expander(f"Select Subcategories for {category}"):
                    selected_subcategories[category] = st.multiselect(
                        f"Select subcategories under {category}:",
                        subcategories_sorted,
                        default=subcategories_sorted,  
                        help=f"Select which subcategories of {category} to show on the map"
                    )


    sell_metrics = ['mean_price_amd', 'median_price_amd', 'max_price_amd', 'min_price_amd',
                    'mean_price_amd_per_1ms_area', 'median_price_amd_per_1ms_area',
                    'rooms_mean', 'square_meters_mean']
    rent_metrics = [m + '_rent' for m in sell_metrics]
    ameria_metrics = ['new_price_min', 'new_price_max', 'new_price_mean', 'new_price_median',
                     'new_area_mean', 'buildings_count', 'apartments_total', 'apartments_free', 'apartments_sold', 'sold_pct']


    if data_source == 'Apartments Sell':
        metric_choice = st.selectbox("Select metric to color districts by:", sell_metrics)
    elif data_source == 'Apartments Rent':
        metric_choice = st.selectbox("Select metric to color districts by:", rent_metrics)
    elif data_source == 'Apartments Primary Market':
        metric_choice = st.selectbox("Select metric to color districts by:", ameria_metrics)
    else:
        metric_choice = st.selectbox("Select Community Services & Businesses category to color districts by:", osm_categories_sorted)

    districts_gdf = st.session_state.data['yerevan_distrincts'].copy()
    districts_gdf = districts_gdf.to_crs(epsg=4326)
    districts_gdf['geometry'] = districts_gdf['geometry'].buffer(0)
    districts_gdf = districts_gdf.rename(columns={'district': 'district_name'})

    sell_df = st.session_state.data['list_apartments_sell'].copy()
    sell_df['price_amd'] = sell_df['price_amd'].astype('float64')
    sell_df['square_meters'] = sell_df['square_meters'].astype('float64')
    sell_df['number_of_rooms'] = sell_df['number_of_rooms'].astype('int')
    sell_df = sell_df.dropna(subset=['price_amd', 'square_meters', 'distrinct', 'number_of_rooms']).copy()
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


    rent_df = st.session_state.data['list_apartments_rent'].copy()
    rent_df['price_amd'] = rent_df['price_amd'].astype('float64')
    rent_df['square_meters'] = rent_df['square_meters'].astype('float64')
    rent_df['number_of_rooms'] = rent_df['number_of_rooms'].astype('int')
    rent_df = rent_df.dropna(subset=['price_amd', 'square_meters', 'distrinct', 'number_of_rooms']).copy()
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


    ameria_df = st.session_state.data['ameria_primary_market'].copy()
    ameria_df['apartmentPriceStartingAt'] = ameria_df['apartmentPriceStartingAt'].astype('float64')
    ameria_df['areaPriceStartingAt'] = ameria_df['areaPriceStartingAt'].astype('float64')
    ameria_df['apartmentsCount'] = ameria_df['apartmentsCount'].astype('int')
    ameria_df['availableForSale'] = ameria_df['availableForSale'].astype('int')
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
    ameria_agg['sold_pct'] = 100 * ameria_agg['apartments_sold'] / ameria_agg['apartments_total']

    osm_counts = osm_df.groupby('district')['main_category'].value_counts().unstack(fill_value=0).reset_index()
    #osm_counts = pd.pivot_table(osm_df, index='district', columns=['main_category', 'category'], values='id', aggfunc='count', fill_value=0).reset_index()

    districts_gdf = districts_gdf.merge(sell_agg, left_on='district_name', right_on='distrinct', how='left')
    districts_gdf = districts_gdf.merge(rent_agg.add_suffix('_rent'), left_on='district_name', right_on='distrinct_rent', how='left')
    districts_gdf = districts_gdf.merge(ameria_agg, left_on='district_name', right_on='distrinct', how='left')
    #osm_counts.columns = ['district'] + [f"{main_cat}_{cat}" for main_cat, cat in osm_counts.columns[1:].to_list()]
    districts_gdf = districts_gdf.merge(osm_counts, left_on='district_name', right_on='district', how='left')


    districts_gdf.fillna(0, inplace=True)

    metric_column = metric_choice if metric_choice in districts_gdf.columns else 'mean_price_amd'

    m = folium.Map(location=[40.18, 44.51], zoom_start=11, tiles='cartodbpositron')

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

    def style_function(feature):
        val = feature['properties'].get(metric_column, 0)
        if val == 0:
            return {'fillColor': '#cccccc', 'color': 'black', 'weight': 1, 'fillOpacity': 0.2}
        else:
            return {'fillColor': colormap(val), 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}

    tooltip_fields = ['district_name', metric_column]
    tooltip_aliases = ['District:', f'{metric_choice.replace("_", " ").capitalize()}:']

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
    popup_aliases.extend([f"Retail {c.capitalize()}" for c in extra_osm_cats])

    folium.GeoJson(
        data=districts_gdf.to_json(),
        name='Districts',
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, aliases=tooltip_aliases, localize=True, labels=True),
        popup=folium.GeoJsonPopup(fields=popup_fields, aliases=popup_aliases, localize=True, labels=True, max_width=350),
        highlight_function=lambda x: {'weight': 3, 'color': 'blue'}
    ).add_to(m)

    # if show_osm_points and selected_osm_categories:
    #     filtered_osm = osm_df[osm_df['main_category'].isin(selected_osm_categories)]
    #     for idx, row in filtered_osm.iterrows():
    #         folium.CircleMarker(
    #             location=[row['lat'], row['lon']],
    #             radius=4,
    #             popup=f"Category: {row['main_category']}<br><br>SubCategory: {row['category']}<br><br>Name: {row['name']}<br><br>District: {row['district']}",
    #             color='blue',
    #             fill=True,
    #             fill_opacity=0.6,
    #         ).add_to(m)

    if show_osm_points and selected_osm_categories:
        filtered_osm = osm_df[osm_df['main_category'].isin(selected_osm_categories)] 
        chosen_subcategories = []     
        for k, v in selected_subcategories.items():
            chosen_subcategories.extend(v)

        filtered_osm = filtered_osm[filtered_osm['category'].isin(chosen_subcategories)].copy()
        if "Financial Services" in filtered_osm['main_category'].values:
            filtered_osm = filtered_osm[(filtered_osm['main_category']!="Financial Services") | 
                                        ((filtered_osm['main_category']=="Financial Services") & (filtered_osm['name'].isin(selected_bank_names)))].copy()

        category_colors = {category: mcolors.rgb2hex(plt.cm.get_cmap('Set3')(i)) 
                           for i, category in enumerate(filtered_osm['category'].unique())}

        legend_html = '''
            <div style="position: fixed; bottom: 50px; left: 50px; width: 200px; height: auto; background-color: white; 
            border:2px solid grey; z-index:9999; font-size:14px; padding: 10px; border-radius: 5px;">
            <b>Categories Legend</b><br>'''

        for category, color in category_colors.items():
            legend_html += f'<i style="background-color:{color}; width: 20px; height: 20px; display: inline-block;"></i> {category}<br>'
        
        legend_html += '</div>'
        
        st.markdown(legend_html, unsafe_allow_html=True)

        for idx, row in filtered_osm.iterrows():
            color = category_colors.get(row['category'], '#0000FF')  

            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=4,
                popup=f"Category: {row['main_category']}<br><br>SubCategory: {row['category']}<br><br>Name: {row['name']}<br><br>District: {row['district']}",
                color=color,  
                fill=True,
                fill_opacity=0.6,
            ).add_to(m)



    st.subheader(f"Map: {data_source} by District colored by {metric_choice.replace('_', ' ').capitalize()}")
    st.markdown(
        "🛈 **Hint:** Hover on districts for metric preview, click for full details.<br>"
        + (f"  Community Services & Businesses shown as dots. Click on them to see more information.<br>" if show_osm_points and selected_osm_categories else "")
        + ("  You can select multiple categories and subcategories to filter the data.<br>" if show_osm_points else "")
        + "  Use the dropdown to choose different metrics and see the map update accordingly.",
        unsafe_allow_html=True
    )
    st_folium(m, width=1100, height=800)

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

    st.subheader("Summary: Apartments Primary Market (New Buildings)")
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

    st.subheader("Summary: Community Services & Businesses Categories Count by District")
    if not osm_counts.empty:
        osm_counts_fixed = osm_counts.rename(columns={'district': 'district_name'}).copy()
        for col in osm_counts_fixed.columns:
            if col != 'district_name':
                osm_counts_fixed[col] = pd.to_numeric(osm_counts_fixed[col], errors='coerce').fillna(0)
        st.dataframe(osm_counts_fixed)
    else:
        st.info("No Community Services & Businesses category data available.")






