
### 8. **Código Principal Modernizado** (app/main.py)

```python
# app/main.py - Versión modernizada
import streamlit as st
from ui.components import (
    create_metric_card,
    create_analysis_tabs,
    create_sidebar,
    create_footer
)
from core.analysis import SoilAnalyzer
from core.climate import ClimateAnalyzer
from utils.file_processing import FileProcessor
from utils.visualization import MapVisualizer
import warnings

# Configuración inicial
st.set_page_config(
    page_title="🌴 Analizador Cultivos Digital Twin",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS moderno
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main-header { 
        background: rgba(255, 255, 255, 0.95); 
        padding: 1.5rem; 
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Título moderno
st.markdown("""
<div class="main-header">
    <h1 style="color: #2E7D32; margin: 0;">🌱 ANALIZADOR CULTIVOS</h1>
    <p style="color: #666; margin-top: 0.5rem;">
        Digital Twin con NASA POWER + PlanetScope
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar con componentes modernos
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    
    uploaded_file = st.file_uploader(
        "📤 Subir parcela",
        type=["zip", "kml", "geojson"],
        help="Formato: Shapefile ZIP, KML o GeoJSON"
    )
    
    cultivo = st.selectbox(
        "🌱 Cultivo",
        ["PALMA_ACEITERA", "CACAO", "BANANO"],
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    # Selector de fecha moderna
    fecha_analisis = st.date_input(
        "📅 Fecha de análisis",
        value=datetime.now(),
        max_value=datetime.now()
    )
    
    # Slider moderno
    n_zonas = st.slider(
        "🔢 Número de zonas",
        min_value=4,
        max_value=50,
        value=16,
        help="Divide la parcela en zonas homogéneas"
    )
    
    # Botón con ícono
    if st.button("🚀 Iniciar análisis", type="primary", use_container_width=True):
        with st.spinner("Analizando..."):
            # Lógica de análisis aquí
            pass

# Contenido principal con pestañas
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "🗺️ Mapa Interactivo", 
    "🌱 Fertilidad",
    "🌦️ Clima",
    "📈 Reportes"
])

with tab1:
    # Dashboard con métricas modernas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        create_metric_card("Área Total", "125.5 ha", "+2.3%", "success")
    with col2:
        create_metric_card("Fertilidad Media", "0.78", "-0.5%", "warning")
    with col3:
        create_metric_card("Precipitación", "156 mm", "+12%", "info")
    with col4:
        create_metric_card("Potencial Cosecha", "28 t/ha", "Óptimo", "primary")

with tab2:
    # Mapa interactivo
    st.markdown("### 🗺️ Mapa Interactivo")
    # Aquí iría tu mapa Folium/Plotly

with tab3:
    # Análisis de fertilidad
    st.markdown("### 🌱 Análisis de Fertilidad")
    # Gráficos de fertilidad

with tab4:
    # Análisis climático
    st.markdown("### 🌦️ Datos Climáticos")
    # Gráficos climáticos

with tab5:
    # Generación de reportes
    st.markdown("### 📈 Reportes Personalizados")
    if st.button("📥 Generar Reporte PDF", icon="📄"):
        with st.spinner("Generando reporte..."):
            # Lógica de generación de PDF
            pass

# Footer moderno
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🌿 <b>Analizador de Cultivos v2.0</b> | Powered by NASA POWER API</p>
    <p style="font-size: 0.9rem;">
        © 2024 AgTech Solutions | 
        <a href="#" style="color: #4CAF50;">Documentación</a> | 
        <a href="#" style="color: #4CAF50;">API</a> | 
        <a href="#" style="color: #4CAF50;">GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)
