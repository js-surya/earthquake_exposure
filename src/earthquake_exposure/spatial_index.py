from scipy.spatial import cKDTree
import numpy as np
import pandas as pd

class EarthquakeIndex:
    """KDTree index for fast spatial queries of earthquakes"""
    
    def __init__(self, eq_gdf):
        self.coords = np.array(list(zip(eq_gdf.geometry.x, eq_gdf.geometry.y)))
        self.magnitudes = eq_gdf['mag'].values
        self.depths = eq_gdf['depth_km'].values if 'depth_km' in eq_gdf.columns else np.zeros(len(eq_gdf))
        self.tree = cKDTree(self.coords)
        
    def query_radius(self, x, y, radius_m):
        """Find all earthquakes within radius_m meters of (x, y)"""
        indices = self.tree.query_ball_point([x, y], r=radius_m)
        return indices
        
    def get_nearest_dist(self, x, y):
        """Get distance to nearest earthquake"""
        dist, idx = self.tree.query([x, y], k=1)
        return dist

