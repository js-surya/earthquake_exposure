import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import pytest
from earthquake_exposure.preprocess import cleanup_gdf, fix_crs_to_metric
from earthquake_exposure.spatial_index import EarthquakeIndex
from earthquake_exposure.metrics import apply_normalization, get_final_score

def test_cleanup_gdf():
    df = pd.DataFrame({
        'mag': [5.0, 6.0],
        'geometry': [Point(0, 0), None]
    })
    gdf = gpd.GeoDataFrame(df)
    
    cleaned = cleanup_gdf(gdf)
    
    assert len(cleaned) == 1
    assert 'depth_km' in cleaned.columns

def test_fix_crs_to_metric():
    df = pd.DataFrame({'geometry': [Point(0, 0)]})
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326")
    
    projected = fix_crs_to_metric(gdf)
    
    assert projected.crs == "EPSG:4087"

def test_spatial_index():
    df = pd.DataFrame({
        'mag': [5.0, 5.0],
        'geometry': [Point(0, 0), Point(10, 10)]
    })
    gdf = gpd.GeoDataFrame(df)
    index = EarthquakeIndex(gdf)
    
    dist = index.get_nearest_dist(1, 1)
    
    assert dist < 2.0

def test_normalization():
    df = pd.DataFrame({
        'n_quakes': [1, 10],
        'm_max': [5, 8],
        'impact_score': [10, 100],
        'd_near': [100, 10]
    })
    
    norm = apply_normalization(df)
    
    assert norm['n_quakes'].max() <= 1.0
    assert norm['m_max'].max() <= 1.0
    
def test_final_score():
    df_norm = pd.DataFrame({
        'n_quakes': [0.5],
        'm_max': [0.5],
        'd_score': [0.5]
    })
    
    score = get_final_score(df_norm)
    
    assert score.iloc[0] >= 0
    assert score.iloc[0] <= 1

