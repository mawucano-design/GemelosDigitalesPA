import time
import requests
import os
import logging
from sqlalchemy import create_engine, text

# --- 1. CONFIGURACIÓN DE LOGS (Nivel Ingeniería) ---
# En producción, no usamos print(). Usamos logs con fecha y nivel de severidad.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- 2. CONFIGURACIÓN DEL ENTORNO ---
# Leemos secretos del entorno. Si no existen, usa valores por defecto (seguridad)
DB_HOST = os.getenv('DB_HOST', 'db')
DB_NAME = os.getenv('DB_NAME', 'agro_db')
DB_USER = os.getenv('DB_USER', 'jaidi')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password_segura_123')

# Coordenadas dinámicas (para poder cambiar de finca sin tocar código)
# Por defecto: Dos Hermanas
LAT = float(os.getenv('SENSOR_LAT', '37.28'))
LON = float(os.getenv('SENSOR_LON', '-5.92'))

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
API_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,relative_humidity_2m&timezone=auto"

# --- 3. LÓGICA DE NEGOCIO ---
def diagnostico_agronomo(temp, hum):
    if hum > 85 and temp > 20:
        return "PELIGRO CRÍTICO: Riesgo fúngico alto"
    elif hum > 70:
        return "ALERTA: Humedad excesiva"
    if temp > 35:
        return "ALERTA: Estrés térmico (Calor)"
    if temp < 5:
        return "PELIGRO: Riesgo de Helada"
    return "OPTIMO: Crecimiento Activo"

def init_db(engine):
    """Inicialización idempotente de la base de datos."""
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS mediciones_clima (
                    time TIMESTAMPTZ NOT NULL,
                    sensor_id TEXT NOT NULL,
                    temperatura FLOAT,
                    humedad FLOAT,
                    riesgo_hongo TEXT
                );
            """))
            # Intento de activar hiperpociones de TimescaleDB
            try:
                conn.execute(text("SELECT create_hypertable('mediciones_clima', 'time', if_not_exists => TRUE);"))
                logger.info("⚡ Tabla convertida a Hypertable (TimescaleDB).")
            except Exception:
                logger.warning("⚠️ No se pudo convertir a Hypertable. Continuando en modo PostgreSQL estándar.")
    except Exception as e:
        logger.error(f"❌ Error inicializando DB: {e}")

# --- 4. MOTOR PRINCIPAL ---
if __name__ == "__main__":
    logger.info(f"🌍 Iniciando AgroBot System | Ubicación: {LAT}, {LON}")
    
    # Bucle de espera de Base de Datos (Resiliencia)
    engine = None
    while not engine:
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Conexión a Base de Datos establecida.")
            init_db(engine)
        except Exception as e:
            logger.warning(f"⏳ Base de datos no lista... reintentando en 5s. ({e})")
            time.sleep(5)

    # Ciclo de vida infinito
    while True:
        try:
            logger.info("☁️  Solicitando datos satelitales...")
            response = requests.get(API_URL, timeout=10) # Importante: timeout para no congelar el proceso
            response.raise_for_status()
            
            data = response.json()
            current = data['current']
            temp = current['temperature_2m']
            hum = current['relative_humidity_2m']
            
            estado = diagnostico_agronomo(temp, hum)
            
            with engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO mediciones_clima (time, sensor_id, temperatura, humedad, riesgo_hongo) VALUES (NOW(), :s, :t, :h, :r)"),
                    {"s": "Dos_Hermanas_V1", "t": temp, "h": hum, "r": estado}
                )
                
            logger.info(f"💾 Guardado: {temp}ºC | {hum}% | {estado}")
            
            # Pausa operativa
            time.sleep(60)

        except Exception as e:
            logger.error(f"🔥 Error crítico en el ciclo: {e}")
            time.sleep(10) # Espera de seguridad antes de reintentar