import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from branca.colormap import linear
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk


def show():
    """
    Renders a Streamlit page to visualize and analyze new construction projects in Yerevan.
    This includes an interactive choropleth map and a dashboard with aggregated data and charts.
    """
    st.title("🏗️ Yerevan New Constructions Dashboard")


    @st.cache_data
    def load_data():
        df = st.session_state.data['yerevan_all_norakaruyc'].copy()
        df.rename(columns={'x': 'lon', 'y': 'lat'}, inplace=True)
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df.dropna(subset=['lat', 'lon', 'district'], inplace=True)
        for col in ['status', 'building_type', 'building_subtype', 'constructors', 'address',
                    'permit_start_dt', 'permit_end_dt', 'risk_category']:
            df[col] = df[col].fillna('Not Specified')
        df['permit_start_dt'] = pd.to_datetime(df['permit_start_dt'], errors='coerce')
        df['permit_end_dt'] = pd.to_datetime(df['permit_end_dt'], errors='coerce')
        return df

    @st.cache_data
    def load_geo_data():
        districts_gdf = st.session_state.data['yerevan_distrincts'].copy()
        districts_gdf = districts_gdf.to_crs(epsg=4326)
        districts_gdf = districts_gdf.rename(columns={'district': 'district_name'})
        return districts_gdf

    df = load_data()
    districts_gdf = load_geo_data()

    st.sidebar.header("Map & Data Filters")

    district_list = ["All Yerevan"] + sorted(df['district_eng'].unique().tolist())
    selected_district = st.sidebar.selectbox(
        "Focus on a specific district:",
        district_list
    )

    building_type_list = ["Բոլորը"] + ['Բնակելի շինություններ', 'Հասարակական շինություններ', 'Արտադրական շինություններ']
    selected_building_type = st.sidebar.selectbox(
        "Focus on a specific building type:",
        building_type_list
    )

    
    selected_subbuilding_type = st.sidebar.multiselect(
                        "Focus on a specific subbuilding type:",
                        ["Բոլորը"] + list(df['building_subtype'].value_counts().index),
                        default="Բոլորը",  
                        help="Focus on a specific subbuilding type:"
                    )
    
    selected_status_type = st.sidebar.multiselect(
                        "Focus on a building status type:",
                        ["Բոլորը"] + list(df['status'].value_counts().index),
                        default="Բոլորը",  
                        help="Focus on a building status type:"
                    )
    
    selected_risk_category_type = st.sidebar.multiselect(
                        "Focus on a building risk category type:",
                        ["All"] + list(df['risk_category'].value_counts().index),
                        default="All",  
                        help="Focus on a building risk category type:"
                    )
    


    min_start, max_start = df['permit_start_dt'].min(), df['permit_start_dt'].max()
    min_end, max_end = df['permit_end_dt'].min(), df['permit_end_dt'].max()

    start_date_range = st.sidebar.date_input(
        "📆 Filter by Permit Start Date:",
        value=(min_start.date(), max_start.date()),
        min_value=min_start.date(),
        max_value=max_start.date()
        )

    end_date_range = st.sidebar.date_input(
        "📅 Filter by Permit End Date:",
        value=(min_end.date(), max_end.date()),
        min_value=min_end.date(),
        max_value=max_end.date()
    )
   
    
    show_points = st.sidebar.checkbox("Show Individual Construction Projects", value=False)

    if selected_district == 'All Yerevan':
        filtered_df = df.copy()
        map_center = [40.18, 44.51]
        map_zoom = 11.5
    else:
        filtered_df = df[df['district_eng'] == selected_district].copy()
        try:
            district_centroid = districts_gdf[districts_gdf['district_name'] == selected_district].geometry.centroid.iloc[0]
            map_center = [district_centroid.y, district_centroid.x]
            map_zoom = 13.5
        except (IndexError, AttributeError):
            map_center = [40.18, 44.51]
            map_zoom = 11.5

    if selected_building_type != "Բոլորը":
        filtered_df = filtered_df[filtered_df['building_type'] == selected_building_type]


    if "Բոլորը" not in selected_subbuilding_type:
        filtered_df = filtered_df[filtered_df['building_subtype'].isin(selected_subbuilding_type)]

    if "Բոլորը" not in selected_status_type:
        filtered_df = filtered_df[filtered_df['status'].isin(selected_status_type)]

    if "All" not in selected_risk_category_type:
        filtered_df = filtered_df[filtered_df['risk_category'].isin(selected_risk_category_type)]

    if len(start_date_range)==2 and len(end_date_range)==2:
        filtered_df = filtered_df[
            (filtered_df['permit_start_dt'].dt.date >= start_date_range[0]) &
            (filtered_df['permit_start_dt'].dt.date <= start_date_range[1]) &
            (filtered_df['permit_end_dt'].dt.date >= end_date_range[0]) &
            (filtered_df['permit_end_dt'].dt.date <= end_date_range[1])
        ]
    else:
        st.sidebar.write("Invalid date range(need to specify both start and end), so no filtration is done!")


    st.subheader("Interactive Map of New Constructions")
    
    district_counts = filtered_df.groupby('district_eng').size().reset_index(name='construction_count')
    districts_with_counts = districts_gdf.merge(
        district_counts, left_on='district_name', right_on='district_eng', how='left'
    )
    districts_with_counts['construction_count'] = districts_with_counts['construction_count'].fillna(0).astype(int)

    m = folium.Map(location=map_center, zoom_start=map_zoom, tiles='cartodbpositron')
    
    min_val = districts_with_counts['construction_count'].min()
    max_val = districts_with_counts['construction_count'].max()
    colormap = linear.YlOrRd_09.scale(min_val, max_val)
    colormap.caption = "Number of Construction Projects"
    colormap.add_to(m)

    folium.GeoJson(
        data=districts_with_counts.to_json(),
        name='Districts',
        style_function=lambda feature: {
            'fillColor': colormap(feature['properties']['construction_count']),
            'color': 'black', 'weight': 1.5,
            'fillOpacity': 0.7 if feature['properties']['construction_count'] > 0 else 0.2,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['district_name', 'construction_count'],
            aliases=['District:', 'Construction Projects:'],
            localize=True, sticky=True
        ),
        highlight_function=lambda x: {'weight': 3, 'color': 'blue'}
    ).add_to(m)

    if show_points:
        for _, row in filtered_df.iterrows():
            popup_html = f"""
            <div style="font-size: 11px;">
                <b>Constructor:</b> {row['constructors']}<br>
                <b>Address:</b> {row['address']}<br>
                <b>Status:</b> {row['status']}<br>
                <b>Building Type:</b> {row['building_type']}<br>
                <b>Building SubType:</b> {row['building_subtype']}<br>
                <b>Permission Start:</b> {row['permit_start_dt']}<br>
                <b>Permission End:</b> {row['permit_end_dt']}<br>
                <b>Risk Category:</b> {row['risk_category']}
            </div>      
            """
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=5,
                popup=folium.Popup(popup_html, max_width=300),
                color='blue', fill=True, fill_color='#3186cc', fill_opacity=0.7
            ).add_to(m)

    st.markdown("🛈 **Hint:** Hover over a district for total counts. Use the sidebar checkbox to show/hide individual project locations.")
    st_folium(m, width=1100, height=700)


    grouped = filtered_df.groupby(['lat', 'lon'])
    agg_df = grouped.size().reset_index(name='value')

    height_multiplier = st.sidebar.slider("Height Multiplier", 1, 100, 20)
    agg_df['elevation'] = agg_df['value'] * height_multiplier

    vmin, vmax = agg_df['value'].min(), agg_df['value'].max()
    agg_df['color_r'] = ((agg_df['value'] - vmin) / (vmax - vmin + 1e-6) * 255).astype(int)
    agg_df['color_g'] = 100
    agg_df['color_b'] = (255 - agg_df['color_r']).astype(int)
    agg_df['color'] = agg_df[['color_r', 'color_g', 'color_b']].values.tolist()

    st.subheader("📍 3D Map of New Construction Volume")

    view_state = pdk.ViewState(
        latitude=agg_df['lat'].mean(),
        longitude=agg_df['lon'].mean(),
        zoom=12,
        pitch=90,
    )

    layer = pdk.Layer(
        "ColumnLayer",
        data=agg_df,
        get_position='[lon, lat]',
        get_elevation='elevation',
        radius=30,
        get_fill_color='color',
        pickable=True,
        auto_highlight=True,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Projects: {value}"}
    )

    st.pydeck_chart(deck)

    st.markdown(f"📊 Showing **{filtered_df.shape[0]}** filtered construction records.")

    
    st.markdown("---")

    st.header("📊 Construction Project Analysis")

    col1, col2, col3 = st.columns(3)
    total_projects = df.shape[0]
    col1.metric("Total Projects in Yerevan", f"{total_projects:,}")
    projects_in_view = filtered_df.shape[0]
    col2.metric("Projects in Current Filter", f"{projects_in_view:,}")
    active_statuses = ['Ընթացքում գտնվող']
    active_projects = filtered_df[filtered_df['status'].isin(active_statuses)].shape[0]
    col3.metric("Active Projects", f"{active_projects:,}")

    st.markdown("### Projects by District and Status")
    
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    district_agg = df.groupby('district').size().sort_values(ascending=False)
    sns.barplot(x=district_agg.index, y=district_agg.values, palette="crest", ax=ax1)
    ax1.set_title("Total Construction Projects per District", fontsize=16)
    ax1.set_xlabel("District")
    ax1.set_ylabel("Number of Projects")
    ax1.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig1)

    st.markdown(f"#### Construction Status Breakdown for: **{selected_district}**")
    if not filtered_df.empty:
        fig2, ax2 = plt.subplots(figsize=(12, 7))
        status_agg = filtered_df['status'].value_counts()
        sns.barplot(x=status_agg.index, y=status_agg.values, palette="magma", ax=ax2)
        ax2.set_title(f"Project Status in {selected_district}", fontsize=16)
        ax2.set_xlabel("Status")
        ax2.set_ylabel("Number of Projects")
        ax2.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)
    else:
        st.info(f"No construction data to display for {selected_district}.")

    st.markdown("### Browse Construction Data")
    st.dataframe(
        filtered_df[['district', 'address', 'constructors', 'status', 'building_type', 'permit_end_dt']]
        .rename(columns={
            'district': 'District', 'address': 'Address', 'constructors': 'Constructor',
            'status': 'Status', 'building_type': 'Building Type', 'permit_end_dt': 'Permit End Date'
        }),
        height=400
    )



