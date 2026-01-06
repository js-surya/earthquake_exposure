# Earthquake Exposure Analysis

**Authors:** Surya Jamuna Rani Subramanian & Govindharajulu Ramachandran  
**Course:** Scientific Programming for Geospatial Sciences (Assignment 1)

## Project Overview
This project performs a spatial analysis to identify major cities at risk from recent seismic activity. 
We fetch real-time data from the USGS API, process it using a KD-Tree for efficient spatial queries, and calculate a custom "Exposure Score" for populated places.

## Installation

This project uses Poetry for dependency management.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/js-surya/earthquake_exposure.git
   cd earthquake_exposure
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

## How to Run

### 1. Interactive Analysis (Jupyter Notebook)
The main analysis and visualizations map are in the notebook.
```bash
poetry run jupyter notebook notebooks/exploration.ipynb
```
Open the link in your browser and run all cells to see the interactive dashboard and map.

### 2. REST API Service
We provide a simple API to query the latest earthquake data.
```bash
poetry run uvicorn src.earthquake_exposure.api:app --reload
```
* API Endpoint: `http://127.0.0.1:8000/latest_quakes`
* Interactive Docs: `http://127.0.0.1:8000/docs`

### 3. Run Automated Tests
To verify the logic (data cleaning, projection, metrics):
```bash
poetry run pytest tests/ -v
```

## Project Structure
* `src/earthquake_exposure/`: Core Python modules
  * `acquire.py`: Fetches data from APIs
  * `spatial_index.py`: KD-Tree implementation for fast search
  * `viz.py`: Plotly and Folium visualization logic
* `notebooks/`: Jupyter notebooks for exploration
* `tests/`: Unit tests for integrity checks
