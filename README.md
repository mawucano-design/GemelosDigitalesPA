cat <<EOF > README.md
# 🌾 AgroSentinel: De "Chatarra" a Agricultura de Precisión

![AgroSentinel Dashboard](dashboard.png)

> **Estado:** 🟢 Producción (v1.2)
> **Stack:** Python + Docker + TimescaleDB + Grafana
> **Desarrollador:** El Mostapha | Ingeniero Agro-Tech

---

## 💡 ¿Qué es AgroSentinel?
**AgroSentinel** es un sistema de **inteligencia artificial y monitoreo climático** capaz de ejecutarse en hardware reciclado (viejas torres, portátiles en desuso).

Su misión es democratizar la tecnología agrícola:
1.  🤖 **Diagnostica** enfermedades fúngicas y estrés térmico en tiempo real.
2.  📡 **Conecta** con satélites meteorológicos para obtener datos hiper-locales.
3.  📊 **Visualiza** KPIs críticos para la toma de decisiones en campo.

## 🚀 Arquitectura "Rock-Solid"
Diseñado para ser **inmortal**. Si se va la luz, arranca solo. Si falla la red, se recupera.

* **🧠 AgroBot (Python):** El cerebro optimizado (consume <100MB RAM).
* **⏱️ TimescaleDB:** Base de datos de alto rendimiento para series temporales.
* **📈 Grafana:** Panel de control visual (ver captura arriba).
* **🐳 Docker:** Despliegue idéntico en cualquier máquina del mundo.

## 🛠️ Instalación en 3 Pasos
Convierte cualquier ordenador en un servidor agrícola en 5 minutos:

1.  **Clonar el repositorio:**
    \`\`\`bash
    git clone https://github.com/TU_USUARIO/AgroSentinel.git
    cd AgroSentinel
    \`\`\`

2.  **Configurar tu finca:**
    \`\`\`bash
    cp .env.example .env
    # Edita las coordenadas (LAT/LON) de tus cultivos
    \`\`\`

3.  **Desplegar:**
    \`\`\`bash
    docker compose up -d --build
    \`\`\`

## 🌿 Lógica de Protección
El sistema vigila tus cultivos 24/7 con algoritmos agronómicos:
* ✅ **ÓPTIMO:** Condiciones ideales para crecimiento.
* ⚠️ **ALERTA:** Riesgo de estrés hídrico o calórico.
* 🚨 **PELIGRO:** Condiciones favorables para **Hongos** o **Heladas**.

---
*Hecho con código, pasión y hardware reciclado.* ♻️
EOF