from scipy.spatial import cKDTree
import numpy as np
import pandas as pd

class EarthquakeIndex:
    """
    I created a class to query earthquakes faster.
    Doing a loop over all quakes for every city is too slow (O(N*M)),
    so I use a KDTree which is way faster.
    """
    
    def __init__(self, eq_gdf):
        # We need the x and y coordinates as a numpy array for the tree
        self.coords = np.array(list(zip(eq_gdf.geometry.x, eq_gdf.geometry.y)))
        self.magnitudes = eq_gdf['mag'].values
        self.depths = eq_gdf['depth_km'].values if 'depth_km' in eq_gdf.columns else np.zeros(len(eq_gdf))
        
        # This builds the tree
        self.tree = cKDTree(self.coords)
        
    def query_radius(self, x, y, radius_m):
        """
        Finds all earthquakes within 'radius_m' meters of point (x, y).
        Returns the indices of the neighbors.
        """
        # query_ball_point finds everything in range
        indices = self.tree.query_ball_point([x, y], r=radius_m)
        return indices
        
    def get_nearest_dist(self, x, y):
        """
        Calculates distance to only the single closest earthquake.
        """
        # k=1 means 'Get me the 1 closest neighbor'
        dist, idx = self.tree.query([x, y], k=1)
        return dist
