import requests
import geopandas as gpd
import pandas as pd
import os

CACHE_FOLDER = "../data"

def get_earthquake_data(days_back=90, min_mag=5.0):
    """Get earthquake data from USGS (Asia region only)"""
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    # Asia bounding box: lat -10 to 80, lon 25 to 180
    params = {
        "format": "geojson",
        "starttime": (pd.Timestamp.now() - pd.Timedelta(days=days_back)).isoformat(),
        "minmagnitude": min_mag,
        "minlatitude": -10,
        "maxlatitude": 80,
        "minlongitude": 25,
        "maxlongitude": 180
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            gdf = gpd.GeoDataFrame.from_features(data["features"])
            if not gdf.empty:
                gdf.crs = "EPSG:4326"
            return gdf
        else:
            print("USGS error:", response.status_code)
            return gpd.GeoDataFrame()
            
    except Exception as e:
        print("Error:", e)
        return gpd.GeoDataFrame()

def get_cities_data():
    """Load cities from Natural Earth dataset (Asia only)"""
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)
        
    local_path = os.path.join(CACHE_FOLDER, "ne_10m_populated_places.json")
    
    if os.path.exists(local_path):
        return gpd.read_file(local_path)
    
    url = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_10m_populated_places_simple.geojson"
    try:
        print("Downloading cities...")
        cities = gpd.read_file(url)
        cities = cities[cities['pop_max'] > 100000].copy()
        
        # Filter for Asian countries only
        asian_countries = [
            'Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 
            'Bhutan', 'Brunei', 'Cambodia', 'China', 'Georgia', 'India', 
            'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan',
            'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Maldives',
            'Mongolia', 'Myanmar', 'Nepal', 'North Korea', 'Oman', 'Pakistan',
            'Palestine', 'Philippines', 'Qatar', 'Saudi Arabia', 'Singapore',
            'South Korea', 'Sri Lanka', 'Syria', 'Taiwan', 'Tajikistan', 'Thailand',
            'Timor-Leste', 'Turkey', 'Turkmenistan', 'United Arab Emirates',
            'Uzbekistan', 'Vietnam', 'Yemen', 'Russia'
        ]
        
        if 'adm0name' in cities.columns:
            cities = cities[cities['adm0name'].isin(asian_countries)].copy()
        elif 'ADM0NAME' in cities.columns:
            cities = cities[cities['ADM0NAME'].isin(asian_countries)].copy()
        
        if 'pop_max' in cities.columns:
            cities = cities.rename(columns={'pop_max': 'POP_MAX'})
        if 'name' in cities.columns:
            cities = cities.rename(columns={'name': 'NAME'})
            
        cities.to_file(local_path, driver="GeoJSON")
        return cities
    except Exception as e:
        print("Download failed:", e)
        return gpd.GeoDataFrame()
