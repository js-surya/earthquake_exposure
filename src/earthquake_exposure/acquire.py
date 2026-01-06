import requests
import geopandas as gpd
import pandas as pd
import os

# Where I will save the cache locally
CACHE_FOLDER = "../data"

def get_earthquake_data(days_back=30, min_mag=5.0):
    """
    Get live earthquake data from USGS.
    I fetch only quakes > min_mag because listing everything is too much.
    """
    
    # This is the url provided in the assignment for live feeds
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    # Parameters for the API
    params = {
        "format": "geojson",
        "starttime": (pd.Timestamp.now() - pd.Timedelta(days=days_back)).isoformat(),
        "minmagnitude": min_mag
    }
    
    try:
        # Requesting data...
        response = requests.get(url, params=params)
        
        # Checking if it works (200 means OK)
        if response.status_code == 200:
            data = response.json()
            # Convert the 'features' part to a GeoDataFrame
            gdf = gpd.GeoDataFrame.from_features(data["features"])
            if not gdf.empty:
                # Set the crs to WGS84 just to be sure
                gdf.crs = "EPSG:4326"
            return gdf
        else:
            print("Something went wrong with USGS:", response.status_code)
            return gpd.GeoDataFrame() # Empty result
            
    except Exception as e:
        print("Error connecting to USGS:", e)
        return gpd.GeoDataFrame()

def get_cities_data():
    """
    Get populated places from Natural Earth.
    I downloaded the file and put it in the data folder to be safe.
    """
    # I check if the cache folder exists, if not i make one
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)
        
    local_path = os.path.join(CACHE_FOLDER, "ne_10m_populated_places.json")
    
    # If I already have the file, just load it
    if os.path.exists(local_path):
        return gpd.read_file(local_path)
    
    # Otherwise, download it (this is a backup link)
    url = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_10m_populated_places_simple.geojson"
    try:
        print("Downloading cities data...")
        cities = gpd.read_file(url)
        # Filter for bigger cities so my computer doesn't crash
        cities = cities[cities['pop_max'] > 100000].copy()
        
        # Rename columns to standardized names for my code
        if 'pop_max' in cities.columns:
            cities = cities.rename(columns={'pop_max': 'POP_MAX'})
        if 'name' in cities.columns:
            cities = cities.rename(columns={'name': 'NAME'})
            
        # Save it for next time
        cities.to_file(local_path, driver="GeoJSON")
        return cities
    except Exception as e:
        print("Could not download cities:", e)
        return gpd.GeoDataFrame()
