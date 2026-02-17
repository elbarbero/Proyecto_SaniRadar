import pandas as pd
import os

def collect_sns_data():
    """
    Simula la recolección de datos del SNS/EpData.
    En la versión final, esto descargará archivos reales y los procesará.
    """
    print("Starting data collection...")
    
    # Datos simulados basados en el informe de 2025
    data = [
        {"hospital": "Hosp. Universitario Burgos", "city": "Burgos", "specialty": "Traumatology", "wait_days": 12, "last_month_wait": 14},
        {"hospital": "Hosp. La Paz", "city": "Madrid", "specialty": "Traumatology", "wait_days": 145, "last_month_wait": 130},
        {"hospital": "Clínic Barcelona", "city": "Barcelona", "specialty": "Traumatology", "wait_days": 68, "last_month_wait": 65},
        {"hospital": "Hosp. La Fe", "city": "Valencia", "specialty": "Traumatology", "wait_days": 92, "last_month_wait": 93}
    ]
    
    df = pd.DataFrame(data)
    
    # Asegurar que el directorio de datos existe
    os.makedirs("data", exist_ok=True)
    
    output_path = os.path.join("data", "waiting_times_latest.csv")
    df.to_csv(output_path, index=False)
    
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    collect_sns_data()
