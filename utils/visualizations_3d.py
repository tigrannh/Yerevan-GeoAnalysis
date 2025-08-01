# import streamlit as st
# import pandas as pd
# import pydeck as pdk
# import numpy as np


# def show():
#     st.title("📈 Advanced 3D Real Estate Dashboard")

#     st.sidebar.header("🔧 Controls")
#     metric_group = st.sidebar.selectbox("Select Metric Group", ["Sell Price", "Rent Price"])
#     agg_stat = st.sidebar.selectbox("Select Statistic", ["mean", "median", "min", "max"])
#     height_multiplier = st.sidebar.slider("Height Scaling Multiplier", 1, 100, 60)
    

#     if metric_group == "Sell Price":
#         df = st.session_state.data['list_apartments_sell'].copy()
#     elif metric_group == "Rent Price":
#         df = st.session_state.data['list_apartments_rent'].copy()

#     df['lat_rounded'] = df['latitude'].round(4)
#     df['lon_rounded'] = df['longitude'].round(4)
#     grouped = df.groupby(['lat_rounded', 'lon_rounded'])

#     metric_column = 'price_amd'
    
#     if agg_stat == "mean":
#         agg_df = grouped[metric_column].mean().reset_index(name='value')
#     elif agg_stat == "median":
#         agg_df = grouped[metric_column].median().reset_index(name='value')
#     elif agg_stat == "min":
#         agg_df = grouped[metric_column].min().reset_index(name='value')
#     elif agg_stat == "max":
#         agg_df = grouped[metric_column].max().reset_index(name='value')

#     agg_df['elevation'] = agg_df['value'] / height_multiplier

#     st.subheader(f"3D Map: {agg_stat.title()} of {metric_group}")

#     layer = pdk.Layer(
#         "ColumnLayer",
#         data=agg_df,
#         get_position='[lon_rounded, lat_rounded]',
#         get_elevation="elevation",
#         elevation_scale=1,
#         radius=50,
#         get_fill_color="[255 - value / 1000, 100, value / 50]",
#         pickable=True,
#         auto_highlight=True,
#     )

#     view_state = pdk.ViewState(
#         latitude=agg_df['lat_rounded'].mean(),
#         longitude=agg_df['lon_rounded'].mean(),
#         zoom=12,
#         pitch=50,
#     )

#     deck = pdk.Deck(
#         layers=[layer],
#         initial_view_state=view_state,
#         tooltip={"text": f"{agg_stat.title()} {metric_group}: {{value:.2f}}"}
#     )

#     st.pydeck_chart(deck)




import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np


def show():
    st.title("📈 Advanced 3D Real Estate Dashboard")

    st.sidebar.header("🔧 Controls")
    metric_group = st.sidebar.selectbox("Select Metric Group", ["Rent Price", "Sell Price", "Primary Market Price"])
    agg_stat = st.sidebar.selectbox("Select Statistic", ["mean", "median", "min", "max"])
    height_multiplier = st.sidebar.slider("Height Scaling Multiplier", 1, 100, 60)

    if metric_group == "Rent Price":
        df = st.session_state.data['list_apartments_rent'].copy()
    elif metric_group == "Sell Price":
        df = st.session_state.data['list_apartments_sell'].copy()
    elif metric_group == "Primary Market Price":
        df = st.session_state.data['ameria_primary_market'].copy()
        df = df.rename(columns={'areaPriceStartingAt': 'price_amd'})

    # Ensure numeric

    df['price_amd'] = pd.to_numeric(df['price_amd'], errors='coerce')
    df = df.dropna(subset=['price_amd', 'latitude', 'longitude'])

    # Round lat/lon to group by small areas
    df['lat_rounded'] = df['latitude'].round(4)
    df['lon_rounded'] = df['longitude'].round(4)
    grouped = df.groupby(['lat_rounded', 'lon_rounded'])

    # Aggregate based on user-selected statistic
    if agg_stat == "mean":
        agg_df = grouped['price_amd'].mean().reset_index(name='value')
    elif agg_stat == "median":
        agg_df = grouped['price_amd'].median().reset_index(name='value')
    elif agg_stat == "min":
        agg_df = grouped['price_amd'].min().reset_index(name='value')
    elif agg_stat == "max":
        agg_df = grouped['price_amd'].max().reset_index(name='value')

    # Compute elevation (height)
    if metric_group == "Rent Price":
        agg_df['elevation'] = agg_df['value'] /( height_multiplier*10)
    elif metric_group == "Sell Price":
        agg_df['elevation'] = agg_df['value'] /( height_multiplier*1000)
    elif metric_group == "Primary Market Price":
        agg_df['elevation'] = agg_df['value'] /( height_multiplier*10)

    # Normalize for color between 0-255
    vmin = agg_df['value'].min()
    vmax = agg_df['value'].max()
    agg_df['color_r'] = ((agg_df['value'] - vmin) / (vmax - vmin + 1e-6) * 255).astype(int)
    agg_df['color_g'] = 100
    agg_df['color_b'] = (255 - agg_df['color_r']).astype(int)
    agg_df['color'] = agg_df[['color_r', 'color_g', 'color_b']].values.tolist()

    st.subheader(f"3D Map: {agg_stat.title()} of {metric_group}")

    layer = pdk.Layer(
        "ColumnLayer",
        data=agg_df,
        get_position='[lon_rounded, lat_rounded]',
        get_elevation="elevation",
        radius=60,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=agg_df['lat_rounded'].mean(),
        longitude=agg_df['lon_rounded'].mean(),
        zoom=12,
        pitch=50,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": f"{agg_stat.title()} {metric_group}: {{value}} AMD"}
    )

    st.pydeck_chart(deck)
