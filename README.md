# 🌱 Analizador de Cultivos - Digital Twin

![Version](https://img.shields.io/badge/version-2.0.0-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-supported-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Aplicación moderna de análisis agrícola con integración de NASA POWER API y datos satelitales.

## 🚀 Características Principales

- ✅ **Análisis de Fertilidad NPK** en tiempo real
- ✅ **Mapas Interactivos** con capas Esri, OpenStreetMap y Mapbox
- ✅ **Datos Climáticos Históricos** (10 años de NASA POWER)
- ✅ **Potencial de Cosecha** por zonas homogéneas
- ✅ **Reportes PDF/Excel** automáticos
- ✅ **API REST** integrada (FastAPI)
- ✅ **Dockerizado** y listo para producción
- ✅ **Base de Datos** PostgreSQL para persistencia
- ✅ **Autenticación** de usuarios (opcional)

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.11+ (para desarrollo local)
- Clave API de NASA POWER (opcional)

## 🐳 Instalación Rápida con Docker

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/analizador-cultivos.git
cd analizador-cultivos

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 3. Construir y ejecutar
docker-compose up -d

# 4. Acceder a la aplicación
# http://localhost:8501
