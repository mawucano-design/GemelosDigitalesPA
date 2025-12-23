# Dockerfile
# Usar imagen base de Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para GeoPandas y librerías geoespaciales
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libspatialindex-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgeos-dev \
    libproj-dev \
    libsqlite3-mod-spatialite \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para mejor caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY app/ ./app/
COPY .env.example .env

# Variables de entorno
ENV PYTHONPATH=/app
ENV SHAPE_RESTORE_SHX=YES
ENV GDAL_DATA=/usr/share/gdal
ENV PROJ_DATA=/usr/share/proj

# Puerto para Streamlit
EXPOSE 8501

# Configurar healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')"

# Comando para ejecutar la aplicación
ENTRYPOINT ["streamlit", "run", "app/main.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.enableCORS=false", \
    "--server.enableXsrfProtection=false", \
    "--browser.serverAddress=0.0.0.0"]
