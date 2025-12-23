# 🌱 Analizador de Cultivos - Digital Twin

Aplicación moderna de análisis agrícola con NASA POWER + PlanetScope

## 🚀 Características

- ✅ Análisis de fertilidad NPK en tiempo real
- ✅ Mapas interactivos con Esri Satellite
- ✅ Datos climáticos históricos (10 años)
- ✅ Potencial de cosecha por zona
- ✅ Reportes PDF automáticos
- ✅ Dockerizado y escalable

## 🐳 Ejecución con Docker

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/analizador-cultivos.git
cd analizador-cultivos

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Ejecutar con Docker Compose
docker-compose up -d

# Acceder a la aplicación
# http://localhost:8501
