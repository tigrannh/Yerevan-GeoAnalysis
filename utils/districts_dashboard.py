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
import matplotlib.pyplot as plt
import seaborn as sns


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
    ameria_metrics = ['primary_market_price_min', 'primary_market_price_max', 'primary_market_price_mean', 'primary_market_price_median',
                     'primary_market_price_amd_per_1ms_mean', 'buildings_count', 'apartments_total', 'apartments_free', 'apartments_sold', 'sold_pct']


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

    cols = ['mean_price_amd', 'median_price_amd', 'mean_price_amd_per_1ms_area', 'median_price_amd_per_1ms_area',
            'max_price_amd', 'min_price_amd']
    sell_agg.loc[:, cols] = sell_agg.loc[:, cols].round(-3)
    sell_agg.loc[:, ['rooms_mean','square_meters_mean']] = sell_agg.loc[:, ['rooms_mean','square_meters_mean']].round(1)
    sell_agg['count_listings'] = sell_agg['count_listings'].astype('int')


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

    cols = ['mean_price_amd', 'median_price_amd', 'max_price_amd', 'min_price_amd',
            'mean_price_amd_per_1ms_area', 'median_price_amd_per_1ms_area']
    rent_agg.loc[:, cols] = rent_agg.loc[:, cols].round(-3)
    rent_agg.loc[:, ['rooms_mean','square_meters_mean']] = rent_agg.loc[:, ['rooms_mean','square_meters_mean']].round(1)
    rent_agg['count_listings'] = rent_agg['count_listings'].astype('int')




    ameria_df = st.session_state.data['ameria_primary_market'].copy()
    ameria_df['apartmentPriceStartingAt'] = ameria_df['apartmentPriceStartingAt'].astype('float64')
    ameria_df['areaPriceStartingAt'] = ameria_df['areaPriceStartingAt'].astype('float64')
    ameria_df['apartmentsCount'] = ameria_df['apartmentsCount'].astype('int')
    ameria_df['availableForSale'] = ameria_df['availableForSale'].astype('int')
    
    ameria_agg = ameria_df.groupby('distrinct').agg(
        primary_market_price_min=('apartmentPriceStartingAt', 'min'),
        primary_market_price_max=('apartmentPriceStartingAt', 'max'),
        primary_market_price_mean=('apartmentPriceStartingAt', 'mean'),
        primary_market_price_median=('apartmentPriceStartingAt', 'median'),
        primary_market_price_amd_per_1ms_mean=('areaPriceStartingAt', 'mean'),
        buildings_count=('id', 'count'),
        apartments_total=('apartmentsCount', 'sum'),
        apartments_free=('availableForSale', 'sum')
    ).reset_index()
    
    ameria_agg['apartments_sold'] = ameria_agg['apartments_total'] - ameria_agg['apartments_free']
    ameria_agg['sold_pct'] = (100 * ameria_agg['apartments_sold'] / ameria_agg['apartments_total']).round(1)
    cols = ['primary_market_price_min', 'primary_market_price_max', 'primary_market_price_mean', 'primary_market_price_median', 'primary_market_price_amd_per_1ms_mean']
    ameria_agg.loc[:, cols] = ameria_agg.loc[:, cols].round(-3)
    ameria_agg['primary_market_price_amd_per_1ms_mean'] = ameria_agg['primary_market_price_amd_per_1ms_mean'].round(1)
    cols = ['buildings_count', 'apartments_total', 'apartments_free']
    ameria_agg.loc[:, cols] = ameria_agg.loc[:, cols].astype('int')

    osm_counts = osm_df.groupby('district')['main_category'].value_counts().unstack(fill_value=0).reset_index()

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
        'primary_market_price_min', 'primary_market_price_max', 'primary_market_price_mean', 'primary_market_price_median', 'primary_market_price_amd_per_1ms_mean',
        'buildings_count', 'apartments_total', 'apartments_free', 'apartments_sold', 'sold_pct'
    ]

    extra_osm_cats = [c for c in districts_gdf.columns if c not in (popup_fields + ['geometry', 'distrinct', 'distrinct_rent', 'district', 'district_name', 'distrinct_x', 'distrinct_y'])]
    popup_fields.extend(extra_osm_cats)

    popup_aliases = [
        'District',
        'Sell Mean Price (AMD)', 'Sell Median Price (AMD)', 'Sell Max Price (AMD)', 'Sell Min Price (AMD)',
        'Sell Mean Price/m²', 'Sell Median Price/m²',
        'Sell Avg Rooms', 'Sell Avg Sqm', 'Sell Listings Count',
        'Rent Mean Price (AMD)', 'Rent Median Price (AMD)', 'Rent Max Price (AMD)', 'Rent Min Price (AMD)',
        'Rent Mean Price/m²', 'Rent Median Price/m²',
        'Rent Avg Rooms', 'Rent Avg Sqm', 'Rent Listings Count',
        'Primary Market Price Min', 'Primary Market Price Max', 'Primary Market Price Mean', 'Primary Market Price Median', 'Primary Market Price/m² Mean',
        'Primary Market Buildings Count', 'Primary Market Total Apartments', 'Primary Market Free Apartments', 'Primary Market Sold Apartments', 'Primary Market Sold %'
    ]
    popup_aliases.extend([f"Retail {c.capitalize()}" for c in extra_osm_cats if (c!=' Distrinct') and (c!='distrinct_x') and (c!='distrinct_y')])   
    
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
            fin_category_colors = {}
            unique_keys = []
            for i, name in enumerate(filtered_osm['name'].unique()):
                key = f"Bank: {name}"
                fin_category_colors[key] = mcolors.rgb2hex(plt.cm.tab10(i % 10))
                unique_keys.append(key)

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
            if row['main_category'] == "Financial Services":
                color = fin_category_colors[f"Bank: {row['name']}"]

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

    osm_counts_detailed = pd.pivot_table(
        osm_df,
        index='district',
        columns=['main_category', 'category'],
        values='id',
        aggfunc='count',
        fill_value=0
    ).reset_index()


    view_choice = st.radio("📋 What would you like to view?", ["📊 Aggregated Tables", "📈 Visual Dashboard"])

    if view_choice == "📊 Aggregated Tables":
        st.subheader("Summary: Apartments for Sale")
        popup_fields = [
            'district_name',
            'mean_price_amd', 'median_price_amd', 'max_price_amd', 'min_price_amd',
            'mean_price_amd_per_1ms_area', 'median_price_amd_per_1ms_area',
            'rooms_mean', 'square_meters_mean', 'count_listings',
            'mean_price_amd_rent', 'median_price_amd_rent', 'max_price_amd_rent', 'min_price_amd_rent',
            'mean_price_amd_per_1ms_area_rent', 'median_price_amd_per_1ms_area_rent',
            'rooms_mean_rent', 'square_meters_mean_rent', 'count_listings_rent',
            'primary_market_price_min', 'primary_market_price_max', 'primary_market_price_mean', 'primary_market_price_median', 'primary_market_price_amd_per_1ms_mean',
            'buildings_count', 'apartments_total', 'apartments_free', 'apartments_sold', 'sold_pct'
        ]
        popup_aliases = [
            'District',
            'Sell Mean Price (AMD)', 'Sell Median Price (AMD)', 'Sell Max Price (AMD)', 'Sell Min Price (AMD)',
            'Sell Mean Price/m²', 'Sell Median Price/m²',
            'Sell Avg Rooms', 'Sell Avg Sqm', 'Sell Listings Count',
            'Rent Mean Price (AMD)', 'Rent Median Price (AMD)', 'Rent Max Price (AMD)', 'Rent Min Price (AMD)',
            'Rent Mean Price/m²', 'Rent Median Price/m²',
            'Rent Avg Rooms', 'Rent Avg Sqm', 'Rent Listings Count',
            'Primary Market Price Min', 'Primary Market Price Max', 'Primary Market Price Mean', 'Primary Market Price Median', 'Primary Market Price/m² Mean',
            'Primary Market Buildings Count', 'Primary Market Total Apartments', 'Primary Market Free Apartments', 'Primary Market Sold Apartments', 'Primary Market Sold %'
        ]
        col_map = dict(zip(popup_fields, popup_aliases))

        st.dataframe(
            sell_agg.rename(columns={'distrinct': 'district'}).rename(columns=col_map)
            .style.format({
                'Sell Mean Price (AMD)': "{:,.0f}", 'Sell Median Price (AMD)': "{:,.0f}",
                'Sell Max Price (AMD)': "{:,.0f}", 'Sell Min Price (AMD)': "{:,.0f}",
                'Sell Mean Price/m²': "{:,.0f}", 'Sell Median Price/m²': "{:,.0f}",
                'Sell Avg Rooms': "{:.2f}", 'Sell Avg Sqm': "{:.2f}",
                'Sell Listings Count': "{:,.0f}"
            })
        )

        st.subheader("Summary: Apartments for Rent")
        st.dataframe(
            rent_agg.add_suffix('_rent').rename(columns={'distrinct_rent': 'district'}).rename(columns=col_map)
            .style.format({
                'Rent Mean Price (AMD)': "{:,.0f}", 'Rent Median Price (AMD)': "{:,.0f}",
                'Rent Max Price (AMD)': "{:,.0f}", 'Rent Min Price (AMD)': "{:,.0f}",
                'Rent Mean Price/m²': "{:,.0f}", 'Rent Median Price/m²': "{:,.0f}",
                'Rent Avg Rooms': "{:.2f}", 'Rent Avg Sqm': "{:.2f}",
                'Rent Listings Count': "{:,.0f}"
            })
        )

        st.subheader("Summary: Apartments Primary Market (New Buildings)")
        st.dataframe(
            ameria_agg.rename(columns={'distrinct': 'district'}).rename(columns=col_map)
            .style.format({
                'Primary Market Price Min': "{:,.0f}", 'Primary Market Price Max': "{:,.0f}",
                'Primary Market Price Mean': "{:,.0f}", 'Primary Market Price Median': "{:,.0f}",
                'Primary Market Price/m² Mean': "{:,.0f}", 'Primary Market Buildings Count': "{:,.0f}",
                'Primary Market Total Apartments': "{:,.0f}", 'Primary Market Free Apartments': "{:,.0f}",
                'Primary Market Sold Apartments': "{:,.0f}", 'Primary Market Sold %': "{:.2f}%"
            })
        )

    # osm_counts_detailed = pd.pivot_table(osm_df, index='district', columns=['main_category', 'category'], values='id', aggfunc='count', fill_value=0).reset_index()
    # st.subheader("Summary: Community Services & Businesses Categories Count by District")
    # if not osm_counts.empty:
    #     osm_counts_fixed = osm_counts.rename(columns={'district': 'district_name'}).copy()
    #     for col in osm_counts_fixed.columns:
    #         if col != 'district_name':
    #             osm_counts_fixed[col] = pd.to_numeric(osm_counts_fixed[col], errors='coerce').fillna(0)
    #     st.dataframe(osm_counts_fixed)
    #     st.dataframe(osm_counts_detailed)
    # else:
    #     st.info("No Community Services & Businesses category data available.")

    # COMMUNITY SERVICES SUMMARY
    
        st.subheader("Summary: Community Services & Businesses Categories Count by District")

        if not osm_counts.empty:
            osm_counts_fixed = osm_counts.copy()
            for col in osm_counts_fixed.columns:
                if col != 'district':
                    osm_counts_fixed[col] = pd.to_numeric(osm_counts_fixed[col], errors='coerce').fillna(0)

            st.dataframe(osm_counts_fixed)
            st.dataframe(osm_counts_detailed)

    elif view_choice == "📈 Visual Dashboard":
        st.markdown("## 📈 Visual Dashboard")

        st.markdown("### 🏠 Apartment Sale Prices")
        sell_options = [col for col in sell_agg.columns if col not in ['distrinct']]
        selected_sell_metric = st.selectbox("Choose metric for sale price plot:", sell_options, index=sell_options.index('mean_price_amd'))

        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.barplot(
            data=sell_agg.sort_values(selected_sell_metric, ascending=False),
            x="distrinct", y=selected_sell_metric,
            palette="YlGnBu", ax=ax1
        )
        ax1.set_ylabel(selected_sell_metric.replace('_', ' ').capitalize())
        ax1.set_xlabel("District")
        ax1.set_title(f"Sale Metric: {selected_sell_metric.replace('_', ' ').capitalize()} by District")
        ax1.tick_params(axis='x', rotation=45)
        st.pyplot(fig1)

        st.markdown("### 🏡 Apartment Rent Prices")
        rent_options = [col for col in rent_agg.columns if col not in ['distrinct']]
        selected_rent_metric = st.selectbox("Choose metric for rent price plot:", rent_options, index=rent_options.index('mean_price_amd'))

        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.barplot(
            data=rent_agg.sort_values(selected_rent_metric, ascending=False),
            x="distrinct", y=selected_rent_metric,
            palette="OrRd", ax=ax2
        )
        ax2.set_ylabel(selected_rent_metric.replace('_', ' ').capitalize())
        ax2.set_xlabel("District")
        ax2.set_title(f"Rent Metric: {selected_rent_metric.replace('_', ' ').capitalize()} by District")
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig2)

        st.markdown("### 🏗️ Primary Market, New Apartments")
        ameria_options = [col for col in ameria_agg.columns if col not in ['distrinct']]
        selected_ameria_metric = st.selectbox("Choose metric for primary market price plot:", ameria_options, index=ameria_options.index('sold_pct'))

        fig3, ax3 = plt.subplots(figsize=(10, 5))
        sns.barplot(
            data=ameria_agg.sort_values(selected_ameria_metric, ascending=False),
            x="distrinct", y=selected_ameria_metric,
            palette="BuPu", ax=ax3
        )
        ax3.set_ylabel(selected_ameria_metric.replace('_', ' ').capitalize())
        ax3.set_xlabel("District")
        ax3.set_title(f"New Building Metric: {selected_ameria_metric.replace('_', ' ').capitalize()} by District")
        ax3.tick_params(axis='x', rotation=45)
        st.pyplot(fig3)

        st.markdown("### 🏢 Community Services & Businesses per District")
        osm_counts_cleaned = osm_counts.copy()
        osm_counts_cleaned['district'] = osm_counts_cleaned['district'].astype(str)
        for col in osm_counts_cleaned.columns:
            if col != 'district':
                osm_counts_cleaned[col] = pd.to_numeric(osm_counts_cleaned[col], errors='coerce').fillna(0)

        poi_options = [col for col in osm_counts_cleaned.columns if col != "district"]
        selected_poi_category = st.selectbox("Choose POI category to plot:", sorted(poi_options))

        if selected_poi_category:
            sorted_df = osm_counts_cleaned[["district", selected_poi_category]].sort_values(selected_poi_category, ascending=False)

            fig4, ax4 = plt.subplots(figsize=(10, 5))
            sns.barplot(
                data=sorted_df,
                x="district", y=selected_poi_category,
                palette="viridis", ax=ax4
            )
            ax4.set_ylabel("POI Count")
            ax4.set_xlabel("District")
            ax4.set_title(f"{selected_poi_category} Count by District")
            ax4.tick_params(axis='x', rotation=45)
            st.pyplot(fig4)
        st.markdown("---")

        st.markdown("---")
        st.header("📊 Multi-Metric Grouped Dashboard")

        grouped_df = sell_agg.rename(columns={'distrinct': 'district'}).copy()
        grouped_df = grouped_df.merge(rent_agg.rename(columns={'distrinct': 'district'}), on='district', suffixes=('_sell', '_rent'))
        grouped_df = grouped_df.merge(ameria_agg.rename(columns={'distrinct': 'district'}), on='district', suffixes=('', '_ameria'))
        grouped_df = grouped_df.merge(osm_counts.rename(columns={'district': 'district'}), on='district', how='left')

        available_metrics = [col for col in grouped_df.columns if col != "district"]
        selected_metrics = st.multiselect("📌 Choose metrics to compare by district:", available_metrics, default=available_metrics[:4])

        if selected_metrics:
            melted = grouped_df.melt(id_vars='district', value_vars=selected_metrics, var_name='Metric', value_name='Value')

            st.markdown("### 📊 Grouped Bar Chart of Metrics by District")
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.barplot(data=melted, x='district', y='Value', hue='Metric', palette='Set2', ax=ax)
            ax.set_title("Selected Metrics by District")
            ax.tick_params(axis='x', rotation=45)
            ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
            st.pyplot(fig)

            if st.checkbox("🔁 Normalize metrics (0-1 scale) for comparison"):
                norm_df = grouped_df[['district'] + selected_metrics].copy()
                for col in selected_metrics:
                    min_val = norm_df[col].min()
                    max_val = norm_df[col].max()
                    if max_val - min_val != 0:
                        norm_df[col] = (norm_df[col] - min_val) / (max_val - min_val)
                melted_norm = norm_df.melt(id_vars='district', value_vars=selected_metrics, var_name='Metric', value_name='Normalized Value')

                st.markdown("### ⚖️ Normalized Comparison")
                fig_norm, ax_norm = plt.subplots(figsize=(12, 6))
                sns.barplot(data=melted_norm, x='district', y='Normalized Value', hue='Metric', palette='Dark2', ax=ax_norm)
                ax_norm.set_title("Normalized Metrics by District (0-1 scale)")
                ax_norm.tick_params(axis='x', rotation=45)
                ax_norm.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
                st.pyplot(fig_norm)
        else:
            st.info("Select at least two metrics to build grouped visual comparisons.")



    # elif view_choice == "📈 Visual Dashboard":

    #     st.markdown("## 📈 Visual Dashboard")

    #     st.markdown("### 🏠 Mean Apartment Sale Price by District")
    #     fig1, ax1 = plt.subplots(figsize=(10, 5))
    #     sns.barplot(
    #         data=sell_agg.sort_values("mean_price_amd", ascending=False),
    #         x="distrinct", y="mean_price_amd",
    #         palette="YlGnBu", ax=ax1
    #     )
    #     ax1.set_ylabel("Mean Price (AMD)")
    #     ax1.set_xlabel("District")
    #     ax1.set_title("Average Apartment Sell Price by District")
    #     ax1.tick_params(axis='x', rotation=45)
    #     st.pyplot(fig1)

    #     st.markdown("### 🏡 Mean Apartment Rent Price by District")
    #     fig2, ax2 = plt.subplots(figsize=(10, 5))
    #     sns.barplot(
    #         data=rent_agg.sort_values("mean_price_amd", ascending=False),
    #         x="distrinct", y="mean_price_amd",
    #         palette="OrRd", ax=ax2
    #     )
    #     ax2.set_ylabel("Mean Rent (AMD)")
    #     ax2.set_xlabel("District")
    #     ax2.set_title("Average Apartment Rent Price by District")
    #     ax2.tick_params(axis='x', rotation=45)
    #     st.pyplot(fig2)

    #     st.markdown("### 🏗️ New Building Apartments: % Sold by District")
    #     fig3, ax3 = plt.subplots(figsize=(10, 5))
    #     sorted_ameria = ameria_agg.sort_values("sold_pct", ascending=False)
    #     sns.barplot(
    #         data=sorted_ameria,
    #         x="distrinct", y="sold_pct",
    #         palette="BuPu", ax=ax3
    #     )
    #     ax3.set_ylabel("Sold %")
    #     ax3.set_xlabel("District")
    #     ax3.set_title("Share of Sold Apartments (New Buildings)")
    #     ax3.tick_params(axis='x', rotation=45)
    #     st.pyplot(fig3)

    #     st.markdown("### 🏢 Total Community Services & Businesses per District")

    #     osm_counts_cleaned = osm_counts.copy()
    #     osm_counts_cleaned['district'] = osm_counts_cleaned['district'].astype(str)
    #     for col in osm_counts_cleaned.columns:
    #         if col != 'district':
    #             osm_counts_cleaned[col] = pd.to_numeric(osm_counts_cleaned[col], errors='coerce').fillna(0)

    #     category_options = [col for col in osm_counts_cleaned.columns if col != "district"]
    #     selected_category = st.selectbox("🔍 Choose a main category to analyze", sorted(category_options))

    #     if selected_category:
    #         sorted_df = osm_counts_cleaned[["district", selected_category]].sort_values(selected_category, ascending=False)

    #         fig4, ax4 = plt.subplots(figsize=(10, 5))
    #         sns.barplot(
    #             data=sorted_df,
    #             x="district", y=selected_category,
    #             palette="viridis", ax=ax4
    #         )
    #         ax4.set_ylabel("POI Count")
    #         ax4.set_xlabel("District")
    #         ax4.set_title(f"{selected_category} Count by District")
    #         ax4.tick_params(axis='x', rotation=45)
    #         st.pyplot(fig4)





