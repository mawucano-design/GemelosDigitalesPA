import time
import requests
import os
from sqlalchemy import create_engine, text

# --- CONFIGURACIÓN DE CONEXIÓN DB (Docker) ---
DB_HOST = os.getenv('DB_HOST', 'db')
DB_NAME = os.getenv('DB_NAME', 'agro_db')
DB_USER = os.getenv('DB_USER', 'jaidi')
DB_PASS = os.getenv('DB_PASS', 'password_segura_123')
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

# --- CONFIGURACIÓN UBICACIÓN (Dos Hermanas, Sevilla) ---
LAT = 37.28
LON = -5.92
# API Gratuita de Open-Meteo (No requiere Key)
API_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,relative_humidity_2m&timezone=auto"

# --- TU LÓGICA BIOLÓGICA (El valor añadido) ---
def diagnostico_agronomo(temp, hum):
    """
    Analiza las condiciones reales y emite un juicio técnico.
    """
    msg = "OPTIMO"
    
    # Lógica de Hongos (Botrytis/Mildeu)
    if hum > 85 and temp > 20:
        return "PELIGRO CRÍTICO: Riesgo fúngico alto"
    elif hum > 70:
        return "ALERTA: Humedad excesiva"
    
    # Lógica de Estrés Hídrico/Térmico
    if temp > 35:
        return "ALERTA: Estrés térmico (Calor)"
    if temp < 5:
        return "PELIGRO: Riesgo de Helada"
        
    return msg

# --- MOTOR PRINCIPAL ---
if __name__ == "__main__":
    print(f"🌍 Iniciando Monitor Real para Coordenadas: {LAT}, {LON}")
    
    # 1. Conexión Resiliente a la DB
    engine = None
    while not engine:
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ DB Conectada.")
        except Exception as e:
            print(f"⏳ Esperando DB... {e}")
            time.sleep(5)

    # 2. Bucle de Monitoreo Real
    while True:
        try:
            # A) PETICIÓN A LA API (El mundo real)
            print("☁️ Consultando satélite (Open-Meteo)...")
            response = requests.get(API_URL)
            data = response.json()
            
            # Extraer datos exactos de AHORA
            current = data['current']
            temp_real = current['temperature_2m']
            hum_real = current['relative_humidity_2m']
            
            # B) TU DIAGNÓSTICO
            estado = diagnostico_agronomo(temp_real, hum_real)
            
            # C) GUARDAR EN TIMESCALE
            with engine.begin() as conn:
                query = text("""
                    INSERT INTO mediciones_clima (time, sensor_id, temperatura, humedad, riesgo_hongo)
                    VALUES (NOW(), :s, :t, :h, :r)
                """)
                
                # Guardamos con etiqueta "EXTERIOR_REAL" para diferenciarlo
                conn.execute(query, {
                    "s": "Dos_Hermanas_Exterior", 
                    "t": temp_real, 
                    "h": hum_real, 
                    "r": estado
                })
                
            print(f"📍 Dos Hermanas: {temp_real}ºC | {hum_real}% | 📝 {estado}")
            
            # Esperamos 60 segundos (para no saturar la API ni tu log)
            time.sleep(60)

        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            time.sleep(10)