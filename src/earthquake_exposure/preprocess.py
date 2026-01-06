import geopandas as gpd

def cleanup_gdf(gdf):
    """
    Simple function to drop rows with no geometry and extract depth.
    The USGS puts depth in the 3rd coordinate (z-axis).
    """
    if gdf.empty:
        return gdf
    
    # Drop rows where geometry is missing
    gdf = gdf.dropna(subset=['geometry']).copy()
    
    # Extract depth from 3D points if available
    # The depth is the Z coordinate in Point(x, y, z)
    # I use apply because it's easier to read than a loop
    gdf['depth_km'] = gdf.geometry.apply(lambda p: p.z if p.has_z else 0)
    
    return gdf

def fix_crs_to_metric(gdf):
    """
    This changes the CRS to a metric one (EPSG:4087).
    We need meters to calculate distances, not degrees!
    """
    # EPSG:4087 is World Equidistant Cylindrical - good for distance
    if gdf.crs != "EPSG:4087":
        return gdf.to_crs(epsg=4087)
    return gdf
