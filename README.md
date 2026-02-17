# 🩺 SaniRadar - Waiting List Monitor

Este es el primer prototipo funcional con arquitectura completa (Backend + Scraper + Frontend).

## 📋 Requisitos Previos

- **Python 3.10 o superior** (Detectado en tu sistema).

## 🚀 Cómo probarlo (Paso a paso)

### 1. Instalación de dependencias
Abre una terminal en la carpeta del proyecto y ejecuta:
```powershell
pip install -r requirements.txt
```

### 2. Ejecutar el Backend (El Cerebro)
Inicia el servidor de datos para que el mapa pueda consultar la información:
```powershell
python backend/main.py
```
*El servidor se iniciará en `http://localhost:8000`. Mantén esta ventana abierta.*

### 3. Ejecutar el Scraper (Opcional - Captura de datos)
Si quieres regenerar los datos de las listas de espera:
```powershell
python scraper/collect_data.py
```
*Esto actualizará el archivo `data/waiting_times_latest.csv`.*

### 4. Abrir la Web (Frontend)
Simplemente abre el archivo en tu navegador:
- Navega a la carpeta `web/`
- Abre `index.html` con Chrome, Edge o Firefox.

---

## 🛠️ Qué verificar
- **Cambio de Idioma**: Prueba los botones ES/EN en la parte superior derecha.
- **Conexión API**: Si el backend está corriendo, el frontend obtendrá los nombres de los hospitales directamente de la API.
- **Mapa Interactivo**: Haz clic en los puntos del mapa para ver los días de espera en cada hospital.