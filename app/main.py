# app/main.py
import streamlit as st
from ui.styles import inject_custom_css
from ui.components import create_metric_card, create_sidebar
from utils.file_processing import procesar_archivo, dividir_parcela_en_zonas
from core.analysis import SoilAnalyzer
from core.climate import ClimateAnalyzer
from utils.visualization import (
    crear_mapa_interactivo_esri, 
    crear_mapa_visualizador_parcela,
    crear_mapa_estatico,
    crear_mapa_heatmap_climatico
)
import warnings
warnings.filterwarnings("ignore")

# Configuración de página
st.set_page_config(
    page_title="🌴 Analizador Cultivos Digital Twin",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyectar CSS
inject_custom_css()

# Título
st.markdown("""
<div class="main-header">
    <h1 style="color: #2E7D32; margin: 0;">🌱 ANALIZADOR CULTIVOS</h1>
    <p style="color: #666; margin-top: 0.5rem;">
        Digital Twin con NASA POWER + PlanetScope
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
params = create_sidebar()

# Inicializar session_state
if 'gdf_original' not in st.session_state:
    st.session_state.gdf_original = None
if 'gdf_analisis' not in st.session_state:
    st.session_state.gdf_analisis = None
if 'analisis_textura' not in st.session_state:
    st.session_state.analisis_textura = None
if 'area_total' not in st.session_state:
    st.session_state.area_total = 0.0
if 'analisis_completado' not in st.session_state:
    st.session_state.analisis_completado = False
if 'datos_clima' not in st.session_state:
    st.session_state.datos_clima = {}
if 'datos_satelitales' not in st.session_state:
    st.session_state.datos_satelitales = {}
if 'datos_clima_historicos' not in st.session_state:
    st.session_state.datos_clima_historicos = {}

# Procesar archivo subido
if params['uploaded_file'] is not None:
    with st.spinner("🔄 Procesando archivo geoespacial..."):
        gdf = procesar_archivo(params['uploaded_file'])
        if gdf is not None:
            st.session_state.gdf_original = gdf
            st.success("✅ Archivo procesado exitosamente")

# Mostrar vista previa de la parcela
if st.session_state.gdf_original is not None:
    st.markdown("### 🗺️ Vista previa de la parcela")
    area_total = SoilAnalyzer.calcular_superficie(st.session_state.gdf_original)
    st.session_state.area_total = area_total
    st.metric("📐 Área Total", f"{area_total:.2f} ha")
    
    mapa_parcela = crear_mapa_visualizador_parcela(st.session_state.gdf_original)
    if mapa_parcela:
        st_folium(mapa_parcela, width=800, height=500)
    
    # Botón para iniciar análisis
    if st.button("🚀 Iniciar Análisis Completo", type="primary", use_container_width=True):
        with st.spinner("🔬 Analizando parcela con datos históricos de NASA POWER..."):
            # Dividir en zonas
            gdf_zonas = dividir_parcela_en_zonas(st.session_state.gdf_original, params['n_zonas'])
            gdf_zonas = gdf_zonas.reset_index(drop=True)
            gdf_zonas['id_zona'] = range(1, len(gdf_zonas) + 1)
            
            centroid_total = gdf_zonas.unary_union.centroid
            
            # Datos históricos
            climate_analyzer = ClimateAnalyzer()
            datos_historicos = climate_analyzer.obtener_datos_nasa_power_historicos(
                centroid_total.y, centroid_total.x, years=10
            )
            st.session_state.datos_clima_historicos = datos_historicos
            
            # Análisis de textura
            soil_analyzer = SoilAnalyzer(params['cultivo'], params['mes_analisis'])
            gdf_textura = soil_analyzer.analizar_textura_suelo(gdf_zonas)
            st.session_state.analisis_textura = gdf_textura
            
            # Datos climáticos actuales
            datos_clima = climate_analyzer.obtener_datos_nasa_power(
                centroid_total.y, centroid_total.x, params['mes_analisis']
            )
            st.session_state.datos_clima = datos_clima
            
            # Datos satelitales
            from datetime import datetime
            fecha_analisis = datetime(datetime.now().year, 
                                      list(soil_analyzer.factores_mes.keys()).index(params['mes_analisis']) + 1, 15)
            datos_satelitales = climate_analyzer.obtener_datos_satelitales(
                centroid_total.y, centroid_total.x, fecha_analisis, params['cultivo']
            )
            st.session_state.datos_satelitales = datos_satelitales
            
            # Análisis de fertilidad
            gdf_fertilidad = soil_analyzer.calcular_indices_gee(
                gdf_zonas, params['analisis_tipo'], params['nutriente'],
                ndvi_base=datos_satelitales['ndvi'],
                evi_base=datos_satelitales['evi']
            )
            
            # Potencial de cosecha (solo para palma)
            if params['cultivo'] == "PALMA_ACEITERA":
                gdf_fertilidad = soil_analyzer.calcular_potencial_cosecha(
                    gdf_fertilidad, datos_clima, datos_satelitales, params['cultivo']
                )
            
            st.session_state.gdf_analisis = gdf_fertilidad
            st.session_state.analisis_completado = True
            
            st.success("✅ Análisis completado con éxito")

# Mostrar resultados si el análisis está completado
if st.session_state.analisis_completado:
    st.markdown("### 📊 Seleccione el tipo de análisis a visualizar")
    opcion = st.selectbox(
        "🔍 Tipo de análisis",
        ["ANÁLISIS PRINCIPAL (Fertilidad)",
         "ANÁLISIS DE TEXTURA",
         "POTENCIAL DE COSECHA (Palma)",
         "ANÁLISIS CLIMÁTICO (NASA POWER)",
         "MAPAS CLIMÁTICOS HISTÓRICOS"],
        key="tipo_analisis"
    )
    
    # Aquí irían las funciones para mostrar cada tipo de análisis
    # (Deben ser adaptadas del código original)
    # Por ejemplo:
    if opcion == "ANÁLISIS PRINCIPAL (Fertilidad)":
        # Llamar a función que muestra resultados principales
        pass
    elif opcion == "ANÁLISIS DE TEXTURA":
        # Llamar a función que muestra textura
        pass
    # ... etc.

# Nota: Las funciones de visualización de resultados (mostrar_resultados_principales, etc.) 
# deben ser adaptadas y posiblemente movidas a un módulo de presentación o mantenidas aquí.
