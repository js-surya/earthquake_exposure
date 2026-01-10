import plotly.express as px
import plotly.graph_objects as go
import folium
import pandas as pd

def generate_interactive_map(cities_gdf, eq_gdf, exposure_df):
    """Generate Folium map with cities and earthquakes"""
    center_lat = cities_gdf.geometry.y.mean()
    center_lon = cities_gdf.geometry.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=2, tiles='CartoDB positron')
    
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

    for _, row in cities_gdf.iterrows():
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
    """Generate Plotly charts for dashboard"""
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
    fig1.update_layout(template="plotly_white")

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
    fig2.update_layout(template="plotly_white")
    
    return fig1, fig2

def generate_plotly_map(cities_gdf, eq_gdf, exposure_df):
    """Generate professional interactive map with rich tooltips and layers"""
    # Prepare Cities Data
    cities_df = cities_gdf.copy()
    cities_df = cities_df.merge(
        exposure_df[['city_name', 'exposure_score', 'n_quakes', 'm_max', 'd_near']], 
        left_on='NAME', 
        right_on='city_name', 
        how='inner'
    )
    
    cities_df['lat'] = cities_df.geometry.y
    cities_df['lon'] = cities_df.geometry.x
    
    # Create rich hover text for cities
    # Handle potentially different column names for country
    country_col = 'ADM0NAME' if 'ADM0NAME' in cities_df.columns else 'adm0name'
    country_name = cities_df[country_col] if country_col in cities_df.columns else "Unknown"
    
    cities_df['hover_text'] = (
        "<b>" + cities_df['NAME'] + "</b> (" + country_name + ")<br>" +
        "Population: " + cities_df['POP_MAX'].apply(lambda x: f"{x:,.0f}") + "<br>" +
        "<b>Risk Score: " + cities_df['exposure_score'].round(2).astype(str) + "</b><br>" +
        "Nearby Quakes: " + cities_df['n_quakes'].astype(str) + "<br>" +
        "Max Mag Nearby: " + cities_df['m_max'].round(1).astype(str) + "<br>" +
        "Nearest Quake: " + cities_df['d_near'].round(1).astype(str) + " km"
    )

    # Prepare Earthquake Data
    eq_df = eq_gdf.copy()
    eq_df['lat'] = eq_df.geometry.y
    eq_df['lon'] = eq_df.geometry.x
    eq_df['date'] = pd.to_datetime(eq_df['time'], unit='ms').dt.strftime('%Y-%m-%d')
    
    # Create rich hover text for earthquakes
    eq_df['hover_text'] = (
        "<b>Magnitude " + eq_df['mag'].astype(str) + "</b><br>" +
        eq_df['place'] + "<br>" +
        "Date: " + eq_df['date'] + "<br>" +
        "Depth: " + eq_df['depth_km'].astype(str) + " km"
    )

    fig = go.Figure()

    # Layer 1: Earthquakes (sized by magnitude)
    fig.add_trace(go.Scattermapbox(
        lat=eq_df['lat'],
        lon=eq_df['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=eq_df['mag'] ** 2.5 / 2,  # Exponential sizing for dramatic effect
            color=eq_df['mag'],
            colorscale='YlOrRd',
            cmin=5.0,
            cmax=8.0,
            opacity=0.7,
            showscale=True,
            colorbar=dict(
                title="Magnitude",
                x=0.02,
                y=0.5,
                len=0.5,
                bgcolor='rgba(255,255,255,0.8)'
            )
        ),
        text=eq_df['hover_text'],
        hoverinfo='text',
        name='Earthquakes'
    ))

    # Layer 2: Cities (colored by risk score)
    fig.add_trace(go.Scattermapbox(
        lat=cities_df['lat'],
        lon=cities_df['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10, 
            color=cities_df['exposure_score'],
            colorscale='Viridis_r',  # Reversed Viridis means darker = safer, brighter = risky
            showscale=True,
            cmin=0,
            cmax=1,
            colorbar=dict(
                title="Risk Score",
                x=0.98,
                len=0.5,
                bgcolor='rgba(255,255,255,0.8)'
            )
        ),
        text=cities_df['hover_text'],
        hoverinfo='text',
        name='Cities at Risk'
    ))

    # Update layout for maximum interactivity and aesthetics
    fig.update_layout(
        title={
            'text': "<b>Asian Cities Seismic Risk Analysis</b><br><sup>Exposure to Earthquakes > Mag 5.0 (Last 90 Days)</sup>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        mapbox_style="carto-positron",
        mapbox=dict(
            center=dict(lat=30, lon=100),
            zoom=2.5
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
        height=800,
        paper_bgcolor='white',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="Black",
            borderwidth=1
        ),
        font=dict(family="Arial", size=12, color="black")
    )
    
    return fig
