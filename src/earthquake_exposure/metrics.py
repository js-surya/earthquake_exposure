import pandas as pd
import numpy as np

def calculate_exposure(cities_m, eq_m, index, radius_km=50):
    """Calculate risk metrics for cities near earthquakes"""
    results = []
    radius_m = radius_km * 1000
    
    for idx, city in cities_m.iterrows():
        cx, cy = city.geometry.x, city.geometry.y
        
        d_near = index.get_nearest_dist(cx, cy)
        neighbor_indices = index.query_radius(cx, cy, radius_m)
        
        if neighbor_indices:
            nearby_mags = index.magnitudes[neighbor_indices]
            n_quakes = len(neighbor_indices)
            m_avg = np.mean(nearby_mags)
            m_max = np.max(nearby_mags)
            impact_score = np.sum(nearby_mags) / (d_near / 1000 + 1)
        else:
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
            'd_near': d_near / 1000,
            'impact_score': impact_score
        })
        
    return pd.DataFrame(results)

def apply_normalization(df):
    """Normalize metrics to 0-1 range"""
    df_norm = df.copy()
    
    cols_to_norm = ['n_quakes', 'm_max', 'impact_score']
    
    for col in cols_to_norm:
        min_v = df[col].min()
        max_v = df[col].max()
        
        if max_v - min_v > 0:
            df_norm[col] = (df[col] - min_v) / (max_v - min_v)
        else:
            df_norm[col] = 0
            
    # Invert distance (closer = higher risk)
    df_norm['d_score'] = 1 / (df['d_near'] + 0.1)
    df_norm['d_score'] = (df_norm['d_score'] - df_norm['d_score'].min()) / (df_norm['d_score'].max() - df_norm['d_score'].min())
    
    return df_norm

def get_final_score(norm_df):
    """Calculate weighted risk score"""
    score = (0.3 * norm_df['n_quakes']) + \
            (0.4 * norm_df['m_max']) + \
            (0.3 * norm_df['d_score'])
            
    return score

