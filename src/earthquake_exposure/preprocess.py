import geopandas as gpd

def cleanup_gdf(gdf):
    """Drop rows with missing geometry and extract depth from z-coordinate"""
    if gdf.empty:
        return gdf
    
    gdf = gdf.dropna(subset=['geometry']).copy()
    gdf['depth_km'] = gdf.geometry.apply(lambda p: p.z if p.has_z else 0)
    
    return gdf

def fix_crs_to_metric(gdf):
    """Convert to EPSG:4087 for metric distance calculations"""
    if gdf.crs != "EPSG:4087":
        return gdf.to_crs(epsg=4087)
    return gdf

