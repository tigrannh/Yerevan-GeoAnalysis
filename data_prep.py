import geopandas as gpd
import pandas as pd
import h3
import streamlit as st
from shapely.geometry import LineString, Polygon


import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString


def assign_h3(df, lat_col='latitude', lon_col='longitude', resolution=8):
    df['h3'] = df.apply(lambda r: h3.geo_to_h3(r[lat_col], r[lon_col], resolution), axis=1)
    return df


def assign_points_to_districts(df, districts_gdf,
                              lat_col='latitude', lon_col='longitude',
                              district_col='district'):
    # Convert LineStrings to Polygons if necessary
    def to_polygon(geom):
        if isinstance(geom, LineString):
            return Polygon(geom.coords)
        return geom
    districts_gdf = districts_gdf.copy()
    districts_gdf['geometry'] = districts_gdf['geometry'].apply(to_polygon)

    # Create GeoDataFrame for points
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
        crs="EPSG:4326"
    )

    # Ensure CRS matches
    districts_gdf = districts_gdf.to_crs("EPSG:4326")
    gdf_points = gdf_points.to_crs(districts_gdf.crs)

    # Spatial join to assign points inside polygons
    joined = gpd.sjoin(gdf_points, districts_gdf[[district_col, 'geometry']],
                       how='left', predicate='within')

    gdf_points[district_col] = joined[district_col].values

    # Handle points not inside any district
    no_district_mask = gdf_points[district_col].isna()
    if no_district_mask.any():
        points_no_district = gdf_points[no_district_mask]

        # Build spatial index on districts
        districts_sindex = districts_gdf.sindex

        assigned_districts = []
        for pt in points_no_district.geometry:
            nearest_indices = districts_sindex.nearest(pt)
            nearest_idx = nearest_indices[0]  # fixed here

            nearest_poly = districts_gdf.iloc[nearest_idx]

            assigned_districts.append(nearest_poly[district_col])

        # Assign back
        gdf_points.loc[no_district_mask, district_col] = assigned_districts

    # Return original df with new district column
    df_result = df.copy()
    df_result[district_col] = gdf_points[district_col].values
    return df_result




def line_to_closed_polygon(geom):
    if geom.is_empty:
        return geom
    if isinstance(geom, Polygon):
        return geom
    if isinstance(geom, LineString):
        coords = list(geom.coords)
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        return Polygon(coords)
    return geom

@st.cache_data(show_spinner=True)
def load_data():
    ameria_secondary_market = pd.read_parquet("data/ameria_secondary_market_long_lat.parquet")
    list_apartments_sell = pd.read_parquet("data/list_apartments_sell_long_lat.parquet")
    list_apartments_rent = pd.read_parquet("data/list_apartments_rent_long_lat.parquet")
    ameria_primary_market_all_info = pd.read_excel("data/ameria_primary_market_all_info.xlsx")
    norakaruyc_am = pd.read_excel("data/norakaruyc_am.xlsx")
    osm_df = pd.read_pickle("data/osm_objects_by_categories.pkl")  
    osm_new_buildings = pd.read_pickle("data/osm_new_buildings.pkl")
    districts = gpd.read_file("data/yerevan_12_districts.geojson")

    currency_to_amd = {
    '$': 390,
    '֏': 1,
    '€': 425,
    '₽': 4.5
    }
    list_apartments_sell['price_amd'] = list_apartments_sell.apply(
        lambda row: row['price_value'] * currency_to_amd.get(row['currency'], 1),
        axis=1
    )
    list_apartments_sell = list_apartments_sell[list_apartments_sell['score']>80].copy()
    list_apartments_sell = list_apartments_sell[list_apartments_sell["price_amd"].notna()].copy()
    list_apartments_sell = list_apartments_sell[list_apartments_sell["square_meters"].notna()].copy()
    list_apartments_sell['price_amd_per_1ms_area'] = list_apartments_sell.apply(lambda row: float(row["price_amd"])/float(row["square_meters"]), axis=1)
    #list_apartments_sell = list_apartments_sell[['latitude', 'longitude', 'number_of_rooms', 'square_meters', 'price_amd', 'price_amd_per_1ms_area']].copy()


    currency_to_amd = {
    '$': 390,
    '֏': 1,
    '€': 425,
    '₽': 4.5
    }
    list_apartments_rent['price_amd'] = list_apartments_rent.apply(
        lambda row: row['price_value'] * currency_to_amd.get(row['currency'], 1),
        axis=1
    )
    list_apartments_rent = list_apartments_rent[list_apartments_rent["price_amd"].notna()].copy()
    list_apartments_rent = list_apartments_rent[list_apartments_rent["square_meters"].notna()].copy()
    list_apartments_rent['price_amd_per_1ms_area'] = list_apartments_rent.apply(lambda row: float(row["price_amd"])/float(row["square_meters"]), axis=1)
    #list_apartments_rent = list_apartments_rent[['latitude', 'longitude', 'number_of_rooms', 'square_meters', 'price_amd', 'price_amd_per_1ms_area']].copy()


    cols =  [ "id", "exploitationDate", "apartmentsCount", "availableForSale", "apartmentPriceStartingAt",
         "areaPriceStartingAt", "floorsCount", "isTownHouse", "isWithIncomeTax", "longitude", "latitude",
         "minAreaOfApartments", "maxAreaOfApartments", "address_city_arm", "address_city_eng",
         "address_district_arm", "address_district_eng", "address_street_arm", "address_street_eng",
         "address_buildingNumber", 
        ]
    ameria_primary_market_all_info = ameria_primary_market_all_info[cols].copy()
    ameria_primary_market_all_info = ameria_primary_market_all_info[ameria_primary_market_all_info["address_city_eng"] == "Yerevan"].copy()
    # ameria_primary_market_all_info = ameria_primary_market_all_info[['longitude', 'latitude', 'apartmentsCount', 'availableForSale', 
    #                                                              'apartmentPriceStartingAt', 'areaPriceStartingAt', 'floorsCount',
    #                                                              'minAreaOfApartments',	'maxAreaOfApartments']].copy()
    
    ameria_secondary_market = ameria_secondary_market[ameria_secondary_market['score']>80].copy()
    #ameria_secondary_market = ameria_secondary_market[['latitude', 'longitude', 'salePriceAMD', 'floor', 'area', 'roomsCount']].copy()
    ameria_secondary_market['price_amd_per_1ms_area'] = ameria_secondary_market.apply(lambda row: float(row["salePriceAMD"])/float(row["area"]), axis=1)


    cols = ["Id", "Latitude", "Longitude", "Address", "Area", "BuildingsNumber",
        "StartDate", "EndDate", "MinPrice", "MaxPrice", "FlatMinArea", "FlatMaxArea",
        "FlatRoomMinCount", "FlatRoomMaxCount", "HaveSecurityPoint", "HaveCommercialPlaces",
        "HaveMetro", "HasGas", "IsApartment", "FlatsCount", "FreeFlatsCount"]
    #norakaruyc_am = norakaruyc_am[cols].copy()
    norakaruyc_am = norakaruyc_am[norakaruyc_am['Address'].str.lower().str.contains('երևան')].copy()
    # norakaruyc_am = norakaruyc_am[['Latitude', 'Longitude', 'StartDate', 'EndDate', 'MinPrice',	'MaxPrice',	'FlatMinArea',	
    #                            'FlatMaxArea',	'FlatRoomMinCount',	'FlatRoomMaxCount',
    #                            'FlatsCount',	'FreeFlatsCount']].copy()
    

    osm_df = osm_df[osm_df['lat'].notna() & osm_df['lon'].notna()].copy()

    distrinct_arm_eng_map = {"Աջափնյակ": "Ajapnyak",
        "Դավթաշեն": "Davtashen",
        "Արաբկիր": "Arabkir",
        "Մալաթիա-Սեբաստիա": "Malatia-Sebastia",
        "Նոր Նորք": "Nor Nork",
        "Կենտրոն": "Kentron (Center)",
        "Շենգավիթ": "Shengavit",
        "Քանաքեռ-Զեյթուն": "Kanaker-Zeitun",
        "Նորք-Մարաշ": "Nork-Marash",
        "Ավան": "Avan",
        "Էրեբունի": "Erebuni",
        "Նուբարաշեն": "Nubarashen"
        }
    
    list_apartments_sell['distrinct'] = list_apartments_sell['region'].map(distrinct_arm_eng_map)
    list_apartments_rent['distrinct'] = list_apartments_rent['region'].map(distrinct_arm_eng_map)
    ameria_primary_market_all_info['distrinct'] = ameria_primary_market_all_info['address_district_arm'].map(distrinct_arm_eng_map)

    districts['geometry'] = districts['geometry'].apply(line_to_closed_polygon)
    osm_df = assign_points_to_districts(osm_df.drop('district', axis=1), districts, lat_col='lat', lon_col='lon', district_col='district')
    

    return {
        "list_apartments_sell": list_apartments_sell,
        "list_apartments_rent": list_apartments_rent,
        "ameria_primary_market": ameria_primary_market_all_info,
        "ameria_secondary_market": ameria_secondary_market,
        "norakaruyc_am_apartments": norakaruyc_am,
        "osm_points": osm_df,
        "osm_new_buildings": osm_new_buildings,
        "yerevan_distrincts": districts
    }



