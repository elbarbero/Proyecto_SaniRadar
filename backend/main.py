from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, SQLModel, create_engine, Session, select
from typing import List, Optional
import os
import threading
import time
from backend.sync_service import check_for_new_reports

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

class SpecialtyData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hospital_id: int = Field(foreign_key="hospital.id")
    specialty_id: str
    wait: int

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
app = FastAPI(title="SaniRadar API", version="0.2.2")

PROVINCES = [
    "Álava", "Albacete", "Alicante", "Almería", "Asturias", "Ávila", "Badajoz", "Barcelona", "Burgos", "Cáceres", 
    "Cádiz", "Cantabria", "Castellón", "Ciudad Real", "Córdoba", "A Coruña", "Cuenca", "Girona", "Granada", 
    "Guadalajara", "Guipúzcoa", "Huelva", "Huesca", "Islas Baleares", "Ibiza", "Menorca", "Formentera", "Jaén", "León", "Lleida", "Lugo", "Madrid", 
    "Málaga", "Murcia", "Navarra", "Ourense", "Palencia", "Las Palmas", "Lanzarote", "Fuerteventura", "Pontevedra", "La Rioja", "Salamanca", 
    "Segovia", "Sevilla", "Soria", "Tarragona", "Santa Cruz de Tenerife", "La Palma", "La Gomera", "El Hierro", "Teruel", "Toledo", "Valencia", 
    "Valladolid", "Vizcaya", "Zamora", "Zaragoza", "Ceuta", "Melilla"
]

SPECIALTIES = [
    {"id": "allergy", "key": "spec-allergy"},
    {"id": "pathology", "key": "spec-pathology"},
    {"id": "anesthesia", "key": "spec-anesthesia"},
    {"id": "angiology", "key": "spec-angiology"},
    {"id": "digestive", "key": "spec-digestive"},
    {"id": "cardio", "key": "spec-cardio"},
    {"id": "cardiovascular-surgery", "key": "spec-cardiovascular-surgery"},
    {"id": "general-surgery", "key": "spec-general-surgery"},
    {"id": "maxillofacial", "key": "spec-maxillofacial"},
    {"id": "trauma", "key": "spec-trauma"},
    {"id": "pediatric-surgery", "key": "spec-pediatric-surgery"},
    {"id": "plastic", "key": "spec-plastic"},
    {"id": "thoracic", "key": "spec-thoracic"},
    {"id": "dermo", "key": "spec-dermo"},
    {"id": "endocrinology", "key": "spec-endocrinology"},
    {"id": "pharmacology", "key": "spec-pharmacology"},
    {"id": "geriatrics", "key": "spec-geriatrics"},
    {"id": "hematology", "key": "spec-hematology"},
    {"id": "immunology", "key": "spec-immunology"},
    {"id": "occupational-medicine", "key": "spec-occupational-medicine"},
    {"id": "family-medicine", "key": "spec-family-medicine"},
    {"id": "rehab", "key": "spec-rehab"},
    {"id": "intensive-care", "key": "spec-intensive-care"},
    {"id": "internal-medicine", "key": "spec-internal-medicine"},
    {"id": "forensic", "key": "spec-forensic"},
    {"id": "nuclear-medicine", "key": "spec-nuclear-medicine"},
    {"id": "preventive", "key": "spec-preventive"},
    {"id": "nephrology", "key": "spec-nephrology"},
    {"id": "pneumology", "key": "spec-pneumology"},
    {"id": "neurosurgery", "key": "spec-neurosurgery"},
    {"id": "neurophysiology", "key": "spec-neurophysiology"},
    {"id": "neurology", "key": "spec-neurology"},
    {"id": "gyn", "key": "spec-gyn"},
    {"id": "ophthalmology", "key": "spec-ophthalmology"},
    {"id": "medical-oncology", "key": "spec-medical-oncology"},
    {"id": "radiation-oncology", "key": "spec-radiation-oncology"},
    {"id": "ent", "key": "spec-ent"},
    {"id": "pediatrics", "key": "spec-pediatrics"},
    {"id": "psychiatry", "key": "spec-psychiatry"},
    {"id": "radiology", "key": "spec-radiology"},
    {"id": "rheumatology", "key": "spec-rheumatology"},
    {"id": "urology", "key": "spec-urology"}
]

@app.get("/api/specialties")
def get_specialties():
    return SPECIALTIES

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Seed data if empty or incomplete
    with Session(engine) as session:
        statement = select(Hospital)
        results = session.exec(statement).all()
        # Si hay pocos hospitales (menos de 70), limpiamos y re-poblamos para asegurar cobertura total
        if len(results) < 70:
            # Eliminar antiguos para evitar duplicados en el re-seed
            for h in results:
                session.delete(h)
            # También limpiar especialidades viejas
            old_specialties = session.exec(select(SpecialtyData)).all()
            for s in old_specialties:
                session.delete(s)
            session.commit()
            
            seed_data = [
                # Andalucía
                Hospital(name_es="Hosp. Virgen del Rocío", name_en="Virgen del Rocio Hospital", city="Sevilla", lat=37.3592, lng=-5.9806, wait=105, trend=4),
                Hospital(name_es="Hosp. Carlos Haya", name_en="Carlos Haya Hospital", city="Málaga", lat=36.7213, lng=-4.4214, wait=120, trend=10),
                Hospital(name_es="Hosp. Virgen de las Nieves", name_en="Virgen de las Nieves Hospital", city="Granada", lat=37.1895, lng=-3.6095, wait=110, trend=2),
                Hospital(name_es="Hosp. Puerta del Mar", name_en="Puerta del Mar Hospital", city="Cádiz", lat=36.5111, lng=-6.2736, wait=95, trend=-1),
                Hospital(name_es="Hosp. Reina Sofía", name_en="Reina Sofia Hospital", city="Córdoba", lat=37.8687, lng=-4.7936, wait=85, trend=3),
                Hospital(name_es="Hosp. Juan Ramón Jiménez", name_en="Juan Ramon Jimenez Hospital", city="Huelva", lat=37.2825, lng=-6.9536, wait=102, trend=5),
                Hospital(name_es="Hosp. Torrecárdenas", name_en="Torrecardenas Hospital", city="Almería", lat=36.8587, lng=-2.4392, wait=115, trend=6),
                Hospital(name_es="Hosp. Ciudad de Jaén", name_en="Jaen Hospital", city="Jaén", lat=37.7656, lng=-3.7744, wait=98, trend=4),

                # Aragón
                Hospital(name_es="Hosp. Miguel Servet", name_en="Miguel Servet Hospital", city="Zaragoza", lat=41.6341, lng=-0.8931, wait=88, trend=2),
                Hospital(name_es="Hosp. San Jorge", name_en="San Jorge Hospital", city="Huesca", lat=42.1317, lng=-0.4181, wait=75, trend=-2),
                Hospital(name_es="Hosp. Obispo Polanco", name_en="Obispo Polanco Hospital", city="Teruel", lat=40.3425, lng=-1.1067, wait=70, trend=-1),

                # Asturias
                Hospital(name_es="Hosp. Universitario Central de Asturias", name_en="Asturias Central Hospital", city="Asturias", lat=43.3761, lng=-5.8428, wait=85, trend=-3),

                # Baleares
                Hospital(name_es="Hosp. Son Espases", name_en="Son Espases Hospital", city="Islas Baleares", lat=39.6083, lng=2.6394, wait=92, trend=4),
                Hospital(name_es="Hosp. Can Misses", name_en="Can Misses Hospital", city="Ibiza", lat=38.9189, lng=1.4239, wait=110, trend=5), # Ibiza
                Hospital(name_es="Hosp. Mateu Orfila", name_en="Mateu Orfila Hospital", city="Menorca", lat=39.8864, lng=4.2514, wait=85, trend=2), # Menorca
                Hospital(name_es="Hosp. de Formentera", name_en="Formentera Hospital", city="Formentera", lat=38.7064, lng=1.4425, wait=70, trend=-1),

                # Canarias
                Hospital(name_es="Hosp. Dr. Negrín", name_en="Dr. Negrin Hospital", city="Las Palmas", lat=28.1256, lng=-15.4475, wait=140, trend=8),
                Hospital(name_es="Hosp. Univ. de Canarias", name_en="Canary Islands Univ. Hospital", city="Santa Cruz de Tenerife", lat=28.4552, lng=-16.2847, wait=135, trend=10),
                Hospital(name_es="Hosp. Dr. José Molina Orosa", name_en="Dr. Jose Molina Orosa Hospital", city="Lanzarote", lat=28.9722, lng=-13.5656, wait=120, trend=4), # Lanzarote
                Hospital(name_es="Hosp. de Fuerteventura", name_en="Fuerteventura Hospital", city="Fuerteventura", lat=28.5039, lng=-13.8686, wait=115, trend=3),
                Hospital(name_es="Hosp. General de La Palma", name_en="La Palma General Hospital", city="La Palma", lat=28.6608, lng=-17.7781, wait=105, trend=2),
                Hospital(name_es="Hosp. Nuestra Señora de los Reyes", name_en="Our Lady of the Kings Hospital", city="El Hierro", lat=27.8103, lng=-17.9158, wait=65, trend=-2), # El Hierro
                Hospital(name_es="Hosp. Nuestra Señora de Guadalupe", name_en="Our Lady of Guadalupe Hospital", city="La Gomera", lat=28.0933, lng=-17.1194, wait=75, trend=1), # La Gomera

                # Cantabria
                Hospital(name_es="Hosp. Marqués de Valdecilla", name_en="Valdecilla Hospital", city="Cantabria", lat=43.4561, lng=-3.8292, wait=80, trend=-2),

                # Castilla - La Mancha
                Hospital(name_es="Hosp. Universitario de Toledo", name_en="Toledo University Hospital", city="Toledo", lat=39.8722, lng=-3.9961, wait=130, trend=12),
                Hospital(name_es="Hosp. Universitario de Albacete", name_en="Albacete University Hospital", city="Albacete", lat=38.9839, lng=-1.8544, wait=90, trend=3),
                Hospital(name_es="Hosp. General de Ciudad Real", name_en="Ciudad Real General Hospital", city="Ciudad Real", lat=38.9814, lng=-3.9239, wait=105, trend=5),
                Hospital(name_es="Hosp. Univ. de Guadalajara", name_en="Guadalajara Univ. Hospital", city="Guadalajara", lat=40.6303, lng=-3.1592, wait=112, trend=7),
                Hospital(name_es="Hosp. Virgen de la Luz", name_en="Virgen de la Luz Hospital", city="Cuenca", lat=40.0767, lng=-2.1408, wait=88, trend=2),

                # Castilla y León
                Hospital(name_es="Hosp. Universitario Burgos", name_en="Burgos University Hospital", city="Burgos", lat=42.3439, lng=-3.6969, wait=12, trend=-2),
                Hospital(name_es="Hosp. Clínico de Valladolid", name_en="Valladolid Clinical Hospital", city="Valladolid", lat=41.6606, lng=-4.7194, wait=115, trend=9),
                Hospital(name_es="Hosp. Univ. de Salamanca", name_en="Salamanca Univ. Hospital", city="Salamanca", lat=40.9639, lng=-5.6739, wait=95, trend=4),
                Hospital(name_es="Hosp. Univ. de León", name_en="Leon Univ. Hospital", city="León", lat=42.6131, lng=-5.5714, wait=108, trend=6),
                Hospital(name_es="Hosp. de Segovia", name_en="Segovia Hospital", city="Segovia", lat=40.9392, lng=-4.1136, wait=75, trend=-1),
                Hospital(name_es="Hosp. Univ. de Palencia", name_en="Palencia Univ. Hospital", city="Palencia", lat=42.0125, lng=-4.5264, wait=82, trend=2),
                Hospital(name_es="Hosp. de Soria", name_en="Soria Hospital", city="Soria", lat=41.7661, lng=-2.4789, wait=65, trend=-2),
                Hospital(name_es="Hosp. de Zamora", name_en="Zamora Hospital", city="Zamora", lat=41.5036, lng=-5.7486, wait=78, trend=1),
                Hospital(name_es="Hosp. Univ. de Ávila", name_en="Avila Univ. Hospital", city="Ávila", lat=40.6552, lng=-4.6864, wait=85, trend=3),

                # Cataluña
                Hospital(name_es="Clínic Barcelona", name_en="Clinic Hospital Barcelona", city="Barcelona", lat=41.3894, lng=2.1528, wait=68, trend=5),
                Hospital(name_es="Vall d'Hebron", name_en="Vall d'Hebron Hospital", city="Barcelona", lat=41.4276, lng=2.1432, wait=75, trend=-3),
                Hospital(name_es="Hosp. Josep Trueta", name_en="Josep Trueta Hospital", city="Girona", lat=41.9961, lng=2.8252, wait=110, trend=6),
                Hospital(name_es="Hosp. Arnau de Vilanova", name_en="Arnau de Vilanova Hospital", city="Lleida", lat=41.6264, lng=0.6083, wait=105, trend=4),
                Hospital(name_es="Hosp. Joan XXIII", name_en="Joan XXIII Hospital", city="Tarragona", lat=41.1219, lng=1.2389, wait=98, trend=3),

                # Extremadura
                Hospital(name_es="Hosp. de Badajoz", name_en="Badajoz Hospital", city="Badajoz", lat=38.8789, lng=-6.9786, wait=120, trend=9),
                Hospital(name_es="Hosp. San Pedro de Alcántara", name_en="San Pedro de Alcantara Hospital", city="Cáceres", lat=39.4792, lng=-6.3769, wait=115, trend=7),

                # Galicia
                Hospital(name_es="Hosp. Clínico de Santiago", name_en="Santiago Clinical Hospital", city="A Coruña", lat=42.8711, lng=-8.5636, wait=85, trend=-2),
                Hospital(name_es="Hosp. Álvaro Cunqueiro", name_en="Alvaro Cunqueiro Hospital", city="Pontevedra", lat=42.1969, lng=-8.7417, wait=112, trend=5),
                Hospital(name_es="Hosp. Lucus Augusti", name_en="Lucus Augusti Hospital", city="Lugo", lat=43.0131, lng=-7.5347, wait=78, trend=-3),
                Hospital(name_es="Hosp. Univ. de Ourense", name_en="Ourense Univ. Hospital", city="Ourense", lat=42.3422, lng=-7.8547, wait=92, trend=2),

                # Madrid
                Hospital(name_es="Hosp. La Paz", name_en="La Paz Hospital", city="Madrid", lat=40.4819, lng=-3.6872, wait=145, trend=15),
                Hospital(name_es="Hosp. Ramón y Cajal", name_en="Ramon y Cajal Hospital", city="Madrid", lat=40.4878, lng=-3.6917, wait=110, trend=8),
                Hospital(name_es="Hosp. 12 de Octubre", name_en="12 de Octubre Hospital", city="Madrid", lat=40.3775, lng=-3.6975, wait=125, trend=10),
                Hospital(name_es="Hosp. Clínico San Carlos", name_en="San Carlos Clinical Hospital", city="Madrid", lat=40.4406, lng=-3.7225, wait=105, trend=4),

                # Murcia
                Hospital(name_es="Hosp. Virgen de la Arrixaca", name_en="Virgen de la Arrixaca Hospital", city="Murcia", lat=37.9431, lng=-1.1347, wait=118, trend=7),

                # Navarra
                Hospital(name_es="Hosp. Univ. de Navarra", name_en="Navarra Univ. Hospital", city="Navarra", lat=42.8083, lng=-1.6631, wait=72, trend=-4),

                # País Vasco
                Hospital(name_es="Hosp. Universitario de Álavo", name_en="U. Hospital of Alava", city="Álava", lat=42.8467, lng=-2.6717, wait=45, trend=-5),
                Hospital(name_es="Hosp. de Basurto", name_en="Basurto Hospital", city="Vizcaya", lat=43.2618, lng=-2.9494, wait=52, trend=-1),
                Hospital(name_es="Hosp. Donostia", name_en="Donostia Hospital", city="Guipúzcoa", lat=43.3083, lng=-1.9744, wait=68, trend=2),

                # La Rioja
                Hospital(name_es="Hosp. San Pedro", name_en="San Pedro Hospital", city="La Rioja", lat=42.4592, lng=-2.4286, wait=60, trend=-3),

                # Comunidad Valenciana
                Hospital(name_es="Hosp. La Fe", name_en="La Fe Hospital", city="Valencia", lat=39.4449, lng=-0.3754, wait=92, trend=-1),
                Hospital(name_es="Hosp. General de Alicante", name_en="Alicante General Hospital", city="Alicante", lat=38.3562, lng=-0.4908, wait=125, trend=11),
                Hospital(name_es="Hosp. General de Castellón", name_en="Castellón General Hospital", city="Castellón", lat=39.9961, lng=-0.0436, wait=110, trend=6),

                # Ceuta y Melilla
                Hospital(name_es="Hosp. Univ. de Ceuta", name_en="Ceuta Univ. Hospital", city="Ceuta", lat=35.8883, lng=-5.3164, wait=55, trend=-2),
                Hospital(name_es="Hospital Comarcal de Melilla", name_en="Melilla Regional Hospital", city="Melilla", lat=35.2919, lng=-2.9411, wait=65, trend=1)
            ]
            session.add_all(seed_data)
            session.commit()
            
            # Seed specific specialty data (Real data from research)
            hospitals = {h.name_es: h.id for h in session.exec(select(Hospital)).all()}
            
            specialty_seed = [
                # Ibiza - Can Misses
                SpecialtyData(hospital_id=hospitals["Hosp. Can Misses"], specialty_id="trauma", wait=145),
                SpecialtyData(hospital_id=hospitals["Hosp. Can Misses"], specialty_id="digestive", wait=40),
                SpecialtyData(hospital_id=hospitals["Hosp. Can Misses"], specialty_id="dermo", wait=30),
                SpecialtyData(hospital_id=hospitals["Hosp. Can Misses"], specialty_id="urology", wait=15),
                
                # Lanzarote - Molina Orosa
                SpecialtyData(hospital_id=hospitals["Hosp. Dr. José Molina Orosa"], specialty_id="trauma", wait=74),
                SpecialtyData(hospital_id=hospitals["Hosp. Dr. José Molina Orosa"], specialty_id="urology", wait=25),
                SpecialtyData(hospital_id=hospitals["Hosp. Dr. José Molina Orosa"], specialty_id="ophthalmology", wait=90),
                SpecialtyData(hospital_id=hospitals["Hosp. Dr. José Molina Orosa"], specialty_id="gyn", wait=20),
            ]
            session.add_all(specialty_seed)
            session.commit()

    # Iniciar programador de actualizaciones automáticas (Cada 30 días)
    def run_periodic_sync():
        while True:
            check_for_new_reports()
            # Dormir 30 días (30 * 24 * 60 * 60 segundos)
            time.sleep(2592000)

    thread = threading.Thread(target=run_periodic_sync, daemon=True)
    thread.start()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to SaniRadar API (v0.2.2 - Real Specialty Data)"}

def normalize_str(s: str) -> str:
    """Simple normalization for accents and case."""
    import unicodedata
    return "".join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')

@app.get("/api/provinces")
def get_provinces():
    return PROVINCES

@app.get("/api/hospitals", response_model=List[Hospital])
def get_hospitals(
    specialty: Optional[str] = None, 
    province: Optional[str] = None,
    session: Session = Depends(get_session)
):
    statement = select(Hospital)
    results = session.exec(statement).all()
    
    # Filtering in Python for maximum flexibility with accents/normalization
    if province and province != "all":
        norm_prov = normalize_str(province)
        results = [h for h in results if normalize_str(h.city) == norm_prov]
    
    # Use real specialty data if available
    if specialty and specialty != "all":
        for h in results:
            spec_data_stmt = select(SpecialtyData).where(
                SpecialtyData.hospital_id == h.id,
                SpecialtyData.specialty_id == specialty
            )
            spec_data = session.exec(spec_data_stmt).first()
            
            if spec_data:
                h.wait = spec_data.wait
            else:
                # Deterministic simulation fallback
                modifier = len(specialty) % 7
                h.wait = h.wait + modifier
            
    return results
            
    return results

@app.get("/api/stats")
def get_stats(session: Session = Depends(get_session)):
    statement = select(Hospital)
    hospitals = session.exec(statement).all()
    if not hospitals:
        return {"min_hosp": None, "avg": 0, "max_hosp": None}
        
    min_hosp = min(hospitals, key=lambda h: h.wait)
    max_hosp = max(hospitals, key=lambda h: h.wait)
    avg_wait = sum(h.wait for h in hospitals) / len(hospitals)
    
    return {
        "min_hosp": min_hosp,
        "avg": round(avg_wait, 1),
        "max_hosp": max_hosp
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
