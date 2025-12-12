# 🌱 AgroSentinel: Sistema de Monitoreo IoT & Cálculo de VPD

![Dashboard Preview](dashboard-preview.jpg)

![Status](https://img.shields.io/badge/Status-Active-success)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Python](https://img.shields.io/badge/Python-ETL-yellow)
![TimescaleDB](https://img.shields.io/badge/DB-TimeSeries-green)

**AgroSentinel** es una solución de arquitectura de microservicios diseñada para la agricultura de precisión. El sistema ingiere datos meteorológicos en tiempo real, calcula indicadores de estrés vegetal (VPD) y alerta sobre riesgos fúngicos (Botrytis/Mildeu).

## 🚀 Arquitectura Técnica

El proyecto despliega 5 microservicios orquestados mediante **Docker Compose**:

* **🐍 AgroBot (Python Worker):** Motor ETL que conecta con la API de Open-Meteo (Datos reales de Dos Hermanas, Sevilla) y procesa la lógica agronómica.
* **🗄️ TimescaleDB (PostgreSQL):** Base de datos optimizada para series temporales (Time-Series) y alta frecuencia de ingestión.
* **📊 Grafana:** Visualización avanzada con cálculo matemático de VPD (Déficit de Presión de Vapor) en tiempo real.
* **⚙️ n8n:** Orquestador de flujos de trabajo y alertas (Backend low-code).
* **🛠️ Adminer:** Gestión de base de datos vía web.

## 🧠 Lógica Agronómica (Bio-Algorithm)

El sistema no solo monitorea, **diagnostica**. Implementa la fórmula de *Tetens* para calcular el VPD en tiempo real y clasifica el estado del cultivo:

* 🔵 **< 0.4 kPa:** Riesgo Fúngico (Humedad excesiva).
* 🟢 **0.4 - 1.5 kPa:** Zona de Confort (Transpiración óptima).
* 🔴 **> 1.5 kPa:** Estrés Hídrico (Cierre estomático).

## 🛠️ Instalación y Uso

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/jaaidi0/AgroSentinel.git](https://github.com/jaaidi0/AgroSentinel.git)