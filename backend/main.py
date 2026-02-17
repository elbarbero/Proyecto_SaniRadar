from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import json

app = FastAPI(title="SaniRadar API", version="0.1.0")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database - In a real app, this would be PostgreSQL
HOSPITALS_DB = [
    {"id": 1, "name_es": "Hosp. Universitario Burgos", "name_en": "Burgos University Hospital", "city": "Burgos", "lat": 42.3439, "lng": -3.6969, "wait": 12, "trend": -2},
    {"id": 2, "name_es": "Hosp. La Paz", "name_en": "La Paz Hospital", "city": "Madrid", "lat": 40.4819, "lng": -3.6872, "wait": 145, "trend": 15},
    {"id": 3, "name_es": "Clínic Barcelona", "name_en": "Clinic Hospital Barcelona", "city": "Barcelona", "lat": 41.3894, "lng": 2.1528, "wait": 68, "trend": 5},
    {"id": 4, "name_es": "Hosp. La Fe", "name_en": "La Fe Hospital", "city": "Valencia", "lat": 39.4449, "lng": -0.3754, "wait": 92, "trend": -1},
    {"id": 5, "name_es": "Hosp. Ramón y Cajal", "name_en": "Ramon y Cajal Hospital", "city": "Madrid", "lat": 40.4878, "lng": -3.6917, "wait": 110, "trend": 8},
    {"id": 6, "name_es": "Vall d'Hebron", "name_en": "Vall d'Hebron Hospital", "city": "Barcelona", "lat": 41.4276, "lng": 2.1432, "wait": 75, "trend": -3},
    {"id": 7, "name_es": "Hosp. Universitario de Álava", "name_en": "U. Hospital of Alava", "city": "Vitoria", "lat": 42.8467, "lng": -2.6717, "wait": 45, "trend": -5},
    {"id": 8, "name_es": "Hosp. Miguel Servet", "name_en": "Miguel Servet Hospital", "city": "Zaragoza", "lat": 41.6341, "lng": -0.8931, "wait": 88, "trend": 2},
    {"id": 9, "name_es": "Hosp. de Basurto", "name_en": "Basurto Hospital", "city": "Bilbao", "lat": 43.2618, "lng": -2.9494, "wait": 52, "trend": -1},
    {"id": 10, "name_es": "Hosp. Carlos Haya", "name_en": "Carlos Haya Hospital", "city": "Malaga", "lat": 36.7213, "lng": -4.4214, "wait": 120, "trend": 10},
    {"id": 11, "name_es": "Hosp. Virgen del Rocío", "name_en": "Virgen del Rocio Hospital", "city": "Sevilla", "lat": 37.3592, "lng": -5.9806, "wait": 105, "trend": 4}
]

class Hospital(BaseModel):
    id: int
    name_es: str
    name_en: str
    city: str
    lat: float
    lng: float
    wait: int
    trend: int

@app.get("/")
def read_root():
    return {"message": "Welcome to SaniRadar API"}

@app.get("/api/hospitals", response_model=List[Hospital])
def get_hospitals(specialty: str = None, province: str = None):
    results = HOSPITALS_DB
    
    # Simple filtering logic
    if specialty and specialty != "all":
        # In a real app, wait times vary by specialty. 
        # Here we simulate it by slightly adjusting the mock wait time based on specialty
        # Just to show it's dynamic
        modifier = len(specialty) % 5
        for h in results:
            h["wait"] = h["wait"] + modifier
            
    if province and province != "all":
        results = [h for h in results if h["city"].lower() == province.lower()]
        
    return results

@app.get("/api/stats")
def get_stats():
    waits = [h["wait"] for h in HOSPITALS_DB]
    return {
        "min": min(waits),
        "avg": sum(waits) / len(waits),
        "max": max(waits)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
