# Earthquake Exposure Analysis - Asia

**Authors:** Surya Jamuna Rani Subramanian & Govindharajulu Ramachandran  
**Course:** Scientific Programming for Geospatial Sciences (Assignment 1)

This project analyzes seismic risk for cities in the Asian region over the last 90 days. It downloads live earthquake data from USGS, combines it with populated places from Natural Earth, and calculates a risk exposure score for each city.

## Structure
- `src/`: Python source code
- `data/`: Where datasets go
- `notebooks/`: Jupyter notebooks for testing

## Installation

This project uses Poetry for dependency management.

1. Clone the repository:
   ```bash
   git clone https://github.com/js-surya/earthquake_exposure.git
   cd earthquake_exposure
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

## How to Run

### 1. Interactive Analysis (Jupyter Notebook)

The main analysis and visualizations are in the notebook.

```bash
poetry run jupyter notebook notebooks/exploration.ipynb
```
Open the link in your browser and run all cells to see the interactive dashboard and map.

### 2. REST API (Optional)
We also created a simple REST API to query the earthquake data. You can start it with:
```bash
poetry run uvicorn src.earthquake_exposure.api:app --reload
```

Then visit these URLs:
- `http://127.0.0.1:8000/` - Just shows a welcome message
- `http://127.0.0.1:8000/latest_quakes?min_mag=6.0` - Gets earthquakes from the last week

The `min_mag` parameter filters by magnitude (default is 5.0).

**Tip:** FastAPI automatically creates documentation at `http://127.0.0.1:8000/docs` where you can test the endpoints in your browser.

### 3. Run Tests
To verify the logic (data cleaning, projection, metrics):
```bash
poetry run pytest tests/ -v
```
