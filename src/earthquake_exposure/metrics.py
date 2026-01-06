import pandas as pd
import numpy as np

def calculate_exposure(cities_m, eq_m, index, radius_km=50):
    """
    This is the main loop. For each city, we look up nearby earthquakes
    and calculate some risk statistics.
    """
    results = []
    
    # Radius must be in meters for our projection
    radius_m = radius_km * 1000 
    
    # Iterate over every city
    for idx, city in cities_m.iterrows():
        cx, cy = city.geometry.x, city.geometry.y
        
        # 1. Get distance to the absolutely nearest quake
        d_near = index.get_nearest_dist(cx, cy)
        
        # 2. Get all quakes within the danger zones
        neighbor_indices = index.query_radius(cx, cy, radius_m)
        
        # If there are quakes nearby...
        if neighbor_indices:
            # We fetch the magnitudes of those specific quakes
            nearby_mags = index.magnitudes[neighbor_indices]
            
            # Here are my simple metrics:
            n_quakes = len(neighbor_indices) # How many?
            m_avg = np.mean(nearby_mags)     # Average strength
            m_max = np.max(nearby_mags)      # Max strength
            
            # Custom 'Impact Score': (Sum of Mags / Distance) roughly
            # I added 1000 to distance so we don't divide by zero
            impact_score = np.sum(nearby_mags) / (d_near / 1000 + 1)
        else:
            # No danger nearby
            n_quakes = 0
            m_avg = 0
            m_max = 0
            impact_score = 0
            
        results.append({
            'city_name': city['NAME'],
            'population': city.get('POP_MAX', 0),
            'country': city.get('ADM0NAME', 'Unknown'),
            'n_quakes': n_quakes,
            'm_avg': m_avg,
            'm_max': m_max,
            'd_near': d_near / 1000, # convert back to km for reading
            'impact_score': impact_score
        })
        
    return pd.DataFrame(results)

def apply_normalization(df):
    """
    Normalization makes all metrics between 0 and 1.
    This helps to make a final score where no single metric dominates.
    """
    df_norm = df.copy()
    
    cols_to_norm = ['n_quakes', 'm_max', 'impact_score']
    
    for col in cols_to_norm:
        min_v = df[col].min()
        max_v = df[col].max()
        
        # Avoid division by zero if all values are same
        if max_v - min_v > 0:
            df_norm[col] = (df[col] - min_v) / (max_v - min_v)
        else:
            df_norm[col] = 0
            
    # For distance, closer is BAD (high risk), so we invert it.
    # We take 1 / distance
    # I add epsilon so we don't crash
    df_norm['d_score'] = 1 / (df['d_near'] + 0.1)
    # Normalize that new d_score too
    df_norm['d_score'] = (df_norm['d_score'] - df_norm['d_score'].min()) / (df_norm['d_score'].max() - df_norm['d_score'].min())
    
    return df_norm

def get_final_score(norm_df):
    """
    Weighted sum of the normalized metrics.
    I decided Max Magnitude is most important (40%).
    """
    # 30% frequency, 40% max magnitude, 30% proximity
    score = (0.3 * norm_df['n_quakes']) + \
            (0.4 * norm_df['m_max']) + \
            (0.3 * norm_df['d_score'])
            
    return score
