import plotly.express as px
import plotly.graph_objects as go
import folium

def generate_interactive_map(cities_gdf, eq_gdf, exposure_df):
    """
    Generates a Folium map with earthquake depth info.
    (Legacy function kept for compatibility if needed)
    """
    # Create base map. Center it based on the cities
    center_lat = cities_gdf.geometry.y.mean()
    center_lon = cities_gdf.geometry.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=2,  tiles='CartoDB positron') # Light Theme
    
    # Add Earthquakes
    for _, row in eq_gdf.iterrows():
        depth_str = f"Depth: {row['depth_km']} km<br>" if 'depth_km' in row else ""
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=row['mag'],
            color='#FF4B4B',
            fill=True,
            fill_color='#FF4B4B',
            popup=folium.Popup(f"<b>Mag:</b> {row['mag']}<br>{depth_str}{row['place']}", max_width=200)
        ).add_to(m)

    # Add Cities with Exposure
    for _, row in cities_gdf.iterrows():
        # Match with exposure score
        score_row = exposure_df[exposure_df['city_name'] == row['NAME']]
        if not score_row.empty:
            score = score_row.iloc[0]['exposure_score']
            color = 'blue' if score < 0.3 else 'orange' if score < 0.7 else 'red'
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=5 + (score * 10),
                color=color,
                fill=True,
                popup=f"{row['NAME']}: {score:.2f} Risk"
            ).add_to(m)
            
    return m

def generate_interactive_dashboard(eq_gdf, exposure_df):
    """
    Generates Plotly dashboard charts using LIGHT THEME.
    """
    # 1. Depth vs Magnitude
    fig1 = px.scatter(
        eq_gdf,
        x='mag',
        y='depth_km' if 'depth_km' in eq_gdf.columns else 'mag',
        color='mag',
        title="Earthquake Depth vs Magnitude",
        color_continuous_scale='Viridis',
        labels={'mag': 'Magnitude', 'depth_km': 'Depth (km)'}
    )
    if 'depth_km' in eq_gdf.columns:
        fig1.update_yaxes(autorange="reversed")
    fig1.update_layout(template="plotly_white") # Light Theme

    # 2. Risk vs Distance
    fig2 = px.scatter(
        exposure_df,
        x='d_near',
        y='exposure_score',
        size='population',
        color='m_max',
        hover_name='city_name',
        title="City Risk Analysis: Score vs Distance",
        labels={'d_near': 'Dist to Quake (km)', 'exposure_score': 'Risk Score'},
        size_max=40
    )
    fig2.update_layout(template="plotly_white") # Light Theme
    
    return fig1, fig2

def generate_plotly_map(cities_gdf, eq_gdf, exposure_df):
    """
    Generates a Plotly Mapbox map in LIGHT MODE ('carto-positron').
    """
    # Prepare Cities
    cities_df = cities_gdf.copy()
    
    # Merge cities with their scores to ensure alignment
    cities_df = cities_df.merge(
        exposure_df[['city_name', 'exposure_score']], 
        left_on='NAME', 
        right_on='city_name', 
        how='inner'
    )
    
    cities_df['lat'] = cities_df.geometry.y
    cities_df['lon'] = cities_df.geometry.x
    
    cities_df['hover'] = (
        "<b>" + cities_df['NAME'] + "</b><br>" +
        "Risk: " + cities_df['exposure_score'].round(2).astype(str)
    )

    # Prepare Quakes
    eq_df = eq_gdf.copy()
    eq_df['lat'] = eq_df.geometry.y
    eq_df['lon'] = eq_df.geometry.x
    eq_df['hover'] = (
        "Mag " + eq_df['mag'].astype(str) + "<br>" +
        eq_df['place']
    )

    fig = go.Figure()

    # Earthquakes Layer (Orange dots for visibility on light map)
    fig.add_trace(go.Scattermapbox(
        lat=eq_df['lat'], lon=eq_df['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=7, color='#FF8C00', opacity=0.7 # Darker orange for contrast
        ),
        text=eq_df['hover'], hoverinfo='text', name='Earthquakes'
    ))

    # Cities Layer (Colored by Risk)
    fig.add_trace(go.Scattermapbox(
        lat=cities_df['lat'], lon=cities_df['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10, 
            color=cities_df['exposure_score'],
            colorscale='Bluered',
            showscale=True,
            colorbar=dict(title="Risk", x=0.98, bgcolor='rgba(255,255,255,0.8)'), # White BG for legend
        ),
        text=cities_df['hover'], hoverinfo='text', name='Cities'
    ))

    fig.update_layout(
        title="Global Seismic Exposure (Light Mode)",
        mapbox_style="carto-positron", # LIGHT THEME
        mapbox=dict(center=dict(lat=20, lon=0), zoom=1.1),
        margin={"r":0,"t":40,"l":0,"b":0},
        height=700,
        paper_bgcolor='white',
        font=dict(color='black')
    )
    return fig
