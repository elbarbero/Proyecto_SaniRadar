from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, SQLModel, create_engine, Session, select
from typing import List, Optional
import os

# --- Models ---
class Hospital(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name_es: str
    name_en: str
    city: str
    lat: float
    lng: float
    wait: int
    trend: int

# --- Database ---
sqlite_file_name = "data/saniradar.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- App ---
app = FastAPI(title="SaniRadar API", version="0.2.0")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Seed data if empty
    with Session(engine) as session:
        statement = select(Hospital)
        results = session.exec(statement).first()
        if not results:
            seed_data = [
                Hospital(name_es="Hosp. Universitario Burgos", name_en="Burgos University Hospital", city="Burgos", lat=42.3439, lng=-3.6969, wait=12, trend=-2),
                Hospital(name_es="Hosp. La Paz", name_en="La Paz Hospital", city="Madrid", lat=40.4819, lng=-3.6872, wait=145, trend=15),
                Hospital(name_es="Clínic Barcelona", name_en="Clinic Hospital Barcelona", city="Barcelona", lat=41.3894, lng=2.1528, wait=68, trend=5),
                Hospital(name_es="Hosp. La Fe", name_en="La Fe Hospital", city="Valencia", lat=39.4449, lng=-0.3754, wait=92, trend=-1),
                Hospital(name_es="Hosp. Ramón y Cajal", name_en="Ramon y Cajal Hospital", city="Madrid", lat=40.4878, lng=-3.6917, wait=110, trend=8),
                Hospital(name_es="Vall d'Hebron", name_en="Vall d'Hebron Hospital", city="Barcelona", lat=41.4276, lng=2.1432, wait=75, trend=-3)
            ]
            session.add_all(seed_data)
            session.commit()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to SaniRadar API (v0.2.0 with persistence)"}

@app.get("/api/hospitals", response_model=List[Hospital])
def get_hospitals(
    specialty: Optional[str] = None, 
    province: Optional[str] = None,
    session: Session = Depends(get_session)
):
    statement = select(Hospital)
    if province and province != "all":
        statement = statement.where(Hospital.city == province.capitalize())
    
    results = session.exec(statement).all()
    
    # Deterministic simulation for specialty (not stored in DB yet)
    if specialty and specialty != "all":
        modifier = len(specialty) % 7
        for h in results:
            h.wait = h.wait + modifier
            
    return results

@app.get("/api/stats")
def get_stats(session: Session = Depends(get_session)):
    statement = select(Hospital)
    hospitals = session.exec(statement).all()
    if not hospitals:
        return {"min": 0, "avg": 0, "max": 0}
        
    waits = [h.wait for h in hospitals]
    return {
        "min": min(waits),
        "avg": sum(waits) / len(waits),
        "max": max(waits)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
