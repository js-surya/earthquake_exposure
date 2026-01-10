from fastapi import FastAPI
import uvicorn
from earthquake_exposure.acquire import get_earthquake_data

app = FastAPI()

@app.get("/")
def home():
    """Welcome message"""
    return {"message": "Welcome to the Earthquake Exposure API!"}

@app.get("/latest_quakes")
def get_latest(min_mag: float = 5.0):
    """Get latest earthquakes"""
    gdf = get_earthquake_data(days_back=7, min_mag=min_mag)
    
    if gdf.empty:
        return {"count": 0, "quakes": []}
        
    results = []
    for _, row in gdf.iterrows():
        results.append({
            "place": row['place'],
            "magnitude": row['mag'],
            "depth_km": row.get('depth_km', 0),
            "lat": row.geometry.y,
            "lon": row.geometry.x
        })
        
    return {"count": len(results), "quakes": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

