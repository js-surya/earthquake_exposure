from fastapi import FastAPI
import uvicorn
from earthquake_exposure.acquire import get_earthquake_data

app = FastAPI()

@app.get("/")
def home():
    """
    Just a simple welcome message.
    """
    return {"message": "Welcome to the Earthquake Exposure API!"}

@app.get("/latest_quakes")
def get_latest(min_mag: float = 5.0):
    """
    Fetches the latest quakes and returns a simplified list.
    """
    gdf = get_earthquake_data(days_back=7, min_mag=min_mag)
    
    if gdf.empty:
        return {"count": 0, "quakes": []}
        
    # Convert to a simple dictionary for JSON
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
    # This runs the server if I execute this file directly
    uvicorn.run(app, host="0.0.0.0", port=8000)
