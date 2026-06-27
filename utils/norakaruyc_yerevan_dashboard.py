import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from branca.colormap import linear
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
import plotly.express as px

# Shared brand palette (matches the app's aurora/glass theme)
BRAND_SCALE = ["#6366F1", "#8B5CF6", "#06B6D4"]  # indigo -> violet -> cyan


def style_fig(fig, title=None):
    """Apply the professional transparent/glass-friendly look to a Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#0F172A",
                                         family="Space Grotesk, sans-serif")) if title else None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#334155", size=13),
        margin=dict(l=10, r=10, t=56 if title else 16, b=10),
        coloraxis_showscale=False,
        bargap=0.32,
        xaxis=dict(showgrid=False, title=None, tickfont=dict(color="#475569")),
        yaxis=dict(showgrid=True, gridcolor="rgba(15,23,42,0.07)", zeroline=False,
                   title=None, tickfont=dict(color="#475569")),
        hoverlabel=dict(bgcolor="white", font_size=13,
                        font_family="Plus Jakarta Sans, sans-serif"),
    )
    return fig


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
            df[col] = df[col].fillna('Not Specified').replace('', 'Not Specified')
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


    agg_df = (
        filtered_df
        .groupby(['lat', 'lon'], as_index=False)
        .agg({
            'district': 'first',
            'address': 'first',
            'constructors': 'first',
            'status': 'first',
            'building_type': 'first',
            'building_subtype': 'first',
            'permit_start_dt': 'first',
            'permit_end_dt': 'first',
            'risk_category': 'first',
            'district_eng': 'first',
            'status': 'first',
            'building_type': 'first',
            'building_subtype': 'first',
            'constructors': 'first',
            'address': 'first',
            'risk_category': 'first',
        })
    )

    agg_df['value'] = (
        filtered_df.groupby(['lat', 'lon']).size().values
    )


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
    tooltip = {
    "html": """
    <div style="font-size: 11px; line-height: 1.4;">
        <b>Projects:</b> {value}<br>
        <b>District:</b> {district_eng}<br>
        <b>Address:</b> {address}<br>
        <b>Owner:</b> {constructors}<br>
        <b>Status:</b> {status}<br>
        <b>Type:</b> {building_type}<br>
        <b>Subtype:</b> {building_subtype}<br>
        <b>Risk:</b> {risk_category}
    </div>
    """,
    "style": {
        "backgroundColor": "white",
        "color": "black"
    }
})

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
    
    district_agg = df.groupby('district').size().sort_values(ascending=False).reset_index()
    district_agg.columns = ['District', 'Projects']
    fig1 = px.bar(
        district_agg, x='District', y='Projects',
        color='Projects', color_continuous_scale=BRAND_SCALE, text='Projects',
    )
    fig1.update_traces(
        textposition='outside', cliponaxis=False,
        marker_line_width=0, textfont=dict(color="#0F172A"),
        hovertemplate='<b>%{x}</b><br>Projects: %{y}<extra></extra>',
    )
    style_fig(fig1, "Total Construction Projects per District")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown(f"#### Construction Status Breakdown for: **{selected_district}**")
    if not filtered_df.empty:
        status_agg = filtered_df['status'].value_counts().reset_index()
        status_agg.columns = ['Status', 'Projects']
        fig2 = px.bar(
            status_agg, x='Status', y='Projects',
            color='Projects', color_continuous_scale=BRAND_SCALE, text='Projects',
        )
        fig2.update_traces(
            textposition='outside', cliponaxis=False,
            marker_line_width=0, textfont=dict(color="#0F172A"),
            hovertemplate='<b>%{x}</b><br>Projects: %{y}<extra></extra>',
        )
        style_fig(fig2, f"Project Status in {selected_district}")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info(f"No construction data to display for {selected_district}.")

    st.markdown("### Browse Construction Data")
    st.dataframe(
        filtered_df[['district', 'address', 'constructors', "building_type", "building_subtype", 'status',  'permit_start_dt', 'permit_end_dt']]
        .rename(columns={
            'district': 'District', 'address': 'Address', 'constructors': 'Constructor',
            'building_type': 'Building Type', 'building_subtype': 'Building Subtype',
            'status': 'Status', 'permit_start_dt': 'Permit Start Date', 'permit_end_dt': 'Permit End Date'
        }),
        height=400
    )

    #######
    # === NEW: 3D Building Footprints (extruded) with height boosted by nearby projects ===
    # --- 3D building footprints (corrected order) ---

    st.subheader("🏢 3D Building Footprints — Height Boosted by Nearby Projects"
                 )
    with st.spinner("Loading 3D building footprints and rendering…"):
       
        # Controls for this view
        with st.sidebar.expander("🏢 3D Buildings settings", expanded=False):
            radius_m = st.slider("Match radius (meters)", 5, 80, 25, 5)
            boost_per_project = st.slider("Height boost per project (m)", 3, 50, 12, 1)
            min_base_h = st.slider("Minimum base height (m)", 3, 20, 6, 1)
            height_scale = st.slider("Overall height scale", 1.0, 5.0, 2.0, 0.1)  # NEW
        # with st.sidebar.expander("🏢 3D Buildings settings", expanded=False):
        #     radius_m = st.slider("Match radius (meters)", 5, 120, 35, 5)
        #     boost_per_project = st.slider("Height boost per project (m)", 3, 100, 20, 1)  # higher default & max
        #     min_base_h = st.slider("Minimum base height (m)", 3, 40, 10, 1)               # taller base
        #     height_scale = st.slider("Overall height scale", 1.0, 30.0, 8.0, 0.5)  


        try:
            import osmnx as ox
            import geopandas as gpd
            import numpy as np
            import json

            # 1) Get OSM building footprints for Yerevan (works for osmnx <2.0 and >=2.0)
            if hasattr(ox, "features_from_place"):
                buildings = ox.features_from_place("Yerevan, Armenia", tags={"building": True})
            else:
                buildings = ox.geometries_from_place("Yerevan, Armenia", tags={"building": True})

            # Keep only polygonal geometries
            buildings = buildings[buildings.geometry.notnull()].copy()
            buildings = buildings[~buildings.geometry.is_empty].copy()
            buildings = buildings[buildings.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
            buildings = buildings.to_crs(epsg=4326)

            # 2) Base height (meters): prefer 'height', else 3m per 'building:levels', else fallback
            def _base_height(row):
                h = row.get("height")
                lv = row.get("building:levels")
                try:
                    if h:
                        return float(str(h).lower().replace("m", "").strip())
                    if lv:
                        return float(lv) * 3.0
                except Exception:
                    pass
                return 6.0

            buildings["base_h"] = buildings.apply(_base_height, axis=1)

            # 3) Project to meters for spatial ops and give each building an id
            bldg_m = buildings.to_crs(epsg=3857).copy()
            bldg_m["_bidx"] = np.arange(len(bldg_m))

            # 4) Points -> GeoDataFrame, buffer by radius, count how many touch each building
            gdf_pts = gpd.GeoDataFrame(
                filtered_df,
                geometry=gpd.points_from_xy(filtered_df["lon"], filtered_df["lat"]),
                crs="EPSG:4326",
            ).to_crs(epsg=3857)

            if len(gdf_pts) > 0:
                buf_gdf = gpd.GeoDataFrame(geometry=gdf_pts.geometry.buffer(radius_m), crs=gdf_pts.crs)
                hit = gpd.sjoin(bldg_m[["_bidx", "geometry"]], buf_gdf, how="left", predicate="intersects")
                proj_counts = hit.groupby("_bidx").size().rename("proj_count")
                bldg_m = bldg_m.join(proj_counts, on="_bidx")
            else:
                bldg_m["proj_count"] = 0

            bldg_m["proj_count"] = bldg_m["proj_count"].fillna(0).astype(int)

            # 5) Compute final elevation: max(min_base_h, base_h) + proj_count * boost_per_project
            # bldg_m["elevation_m"] = np.maximum(bldg_m["base_h"], min_base_h) + bldg_m["proj_count"] * boost_per_project
            bldg_m["elevation_m"] = (
                np.maximum(bldg_m["base_h"], min_base_h) + bldg_m["proj_count"] * boost_per_project
            ) * height_scale
            bldg_m["has_proj"] = (bldg_m["proj_count"] > 0).astype(int)

            # 6) Back to WGS84 and keep only what pydeck needs
            out_bldg = bldg_m.to_crs(epsg=4326)[["geometry", "elevation_m", "proj_count", "has_proj"]].copy()
            geojson = json.loads(out_bldg.to_json())

            # 7) Render extruded polygons: gray if 0 projects, purple if >=1
            bldg_layer = pdk.Layer(
                "GeoJsonLayer",
                data=geojson,
                extruded=True,
                wireframe=False,
                get_elevation="properties.elevation_m",
                get_fill_color="""
                    [properties.proj_count > 0 ? 106 : 210,
                    properties.proj_count > 0 ? 13  : 210,
                    properties.proj_count > 0 ? 173 : 210,
                    150]
                """,
                get_line_color="[150,150,180]",
                line_width_min_pixels=0.5,
                pickable=True,
                auto_highlight=True,
            )

            deck_bld = pdk.Deck(
                layers=[bldg_layer],
                initial_view_state=view_state,  # reuse your existing view_state
                map_style="light",
                tooltip={
                    "html": "<b>Projects nearby:</b> {proj_count}<br/><b>Elevation (m):</b> {elevation_m}",
                    "style": {"backgroundColor": "white", "color": "black"},
                },
            )

            st.pydeck_chart(deck_bld)
            st.caption(f"All buildings are shown. Elevation = max(base, {min_base_h}m) + proj_count × {boost_per_project}m. "
                    f"Project match radius = {radius_m}m.")

        except Exception as e:
            st.info(
                "To render extruded building footprints, install: `pip install osmnx geopandas` "
                f"and ensure they import correctly. Error: {e}"
            )






