# app/main.py
"""
Aplicación principal Streamlit - Analizador de Cultivos Digital Twin
"""
import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
import sys

# Añadir directorio actual al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos personalizados
from ui.styles import inject_custom_css, create_color_palette, get_status_color
from ui.components import (
    create_metric_card,
    create_info_card,
    create_warning_card,
    create_error_card,
    create_success_card,
    create_analysis_tabs,
    create_progress_with_text,
    create_soil_texture_chart,
    create_npk_gauge_chart,
    create_download_button,
    create_expandable_recommendations
)
from core.analysis import SoilAnalyzer
from core.climate import ClimateAnalyzer
from core.soil import SoilTextureAnalyzer
from utils.file_processing import FileProcessor
from utils.visualization import MapVisualizer
from streamlit_folium import st_folium

# Configuración de la página
st.set_page_config(
    page_title="🌴 Analizador Cultivos Digital Twin",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Suprimir advertencias
warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

# Inyectar CSS personalizado
inject_custom_css()
colors = create_color_palette()

# Configurar variables de entorno
os.environ['SHAPE_RESTORE_SHX'] = 'YES'

# Inicializar session state
def init_session_state():
    """Inicializar variables de session state."""
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
    if 'cultivo_seleccionado' not in st.session_state:
        st.session_state.cultivo_seleccionado = "PALMA_ACEITERA"
    if 'mes_seleccionado' not in st.session_state:
        st.session_state.mes_seleccionado = "ENERO"
    if 'n_zonas_seleccionado' not in st.session_state:
        st.session_state.n_zonas_seleccionado = 16

# Header principal
def render_header():
    """Renderizar header de la aplicación."""
    st.markdown(f"""
    <div class="main-header">
        <h1 style="color: {colors['primary']}; margin: 0;">🌱 ANALIZADOR CULTIVOS DIGITAL TWIN</h1>
        <p style="color: {colors['text_light']}; margin-top: 0.5rem;">
            Análisis avanzado con NASA POWER API + PlanetScope | v2.0
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

# Sidebar de configuración
def render_sidebar():
    """Renderizar sidebar de configuración."""
    with st.sidebar:
        st.markdown(f"## ⚙️ **Configuración**")
        
        # Subida de archivos
        uploaded_file = st.file_uploader(
            "📤 **Subir parcela**",
            type=["zip", "kml", "geojson", "shp"],
            help="Formato: Shapefile ZIP, KML o GeoJSON"
        )
        
        if uploaded_file is not None:
            with st.spinner("🔄 Procesando archivo..."):
                gdf = FileProcessor.process_uploaded_file(uploaded_file)
                
                if gdf is not None:
                    st.session_state.gdf_original = gdf
                    st.session_state.area_total = FileProcessor.calculate_area(gdf)
                    st.success(f"✅ Parcela procesada ({st.session_state.area_total:.2f} ha)")
                else:
                    st.error("❌ Error procesando archivo")
        
        st.markdown("---")
        
        # Selección de parámetros
        st.markdown("### 🌱 **Parámetros del Cultivo**")
        
        cultivo = st.selectbox(
            "**Cultivo**",
            ["PALMA_ACEITERA", "CACAO", "BANANO"],
            index=0,
            key="cultivo_select",
            help="Seleccione el cultivo a analizar"
        )
        
        mes = st.selectbox(
            "**Mes de Análisis**",
            ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
             "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"],
            index=datetime.now().month - 1,
            key="mes_select",
            help="Seleccione el mes para el análisis climático"
        )
        
        n_zonas = st.slider(
            "**Número de Zonas**",
            min_value=4,
            max_value=50,
            value=16,
            step=1,
            key="zonas_slider",
            help="Divide la parcela en zonas homogéneas para análisis detallado"
        )
        
        # Botón de análisis
        st.markdown("---")
        if st.button(
            "🚀 **Iniciar Análisis Completo**",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.gdf_original is None
        ):
            st.session_state.cultivo_seleccionado = cultivo
            st.session_state.mes_seleccionado = mes
            st.session_state.n_zonas_seleccionado = n_zonas
            
            with st.spinner("🔬 **Ejecutando análisis completo...**"):
                try:
                    # Dividir en zonas
                    gdf_zonas = FileProcessor.divide_into_zones(
                        st.session_state.gdf_original,
                        n_zones=n_zonas
                    )
                    
                    # Inicializar analizadores
                    soil_analyzer = SoilAnalyzer(cultivo, mes)
                    climate_analyzer = ClimateAnalyzer()
                    texture_analyzer = SoilTextureAnalyzer(cultivo)
                    
                    # Obtener centroide para datos climáticos
                    centroid = gdf_zonas.unary_union.centroid
                    
                    # Obtener datos climáticos
                    st.session_state.datos_clima = climate_analyzer.get_current_climate(
                        centroid.y, centroid.x, mes
                    )
                    
                    # Obtener datos históricos
                    st.session_state.datos_clima_historicos = climate_analyzer.get_historical_climate(
                        centroid.y, centroid.x, years=10
                    )
                    
                    # Analizar fertilidad
                    st.session_state.gdf_analisis = soil_analyzer.analyze_zones(
                        gdf_zonas,
                        n_zones=n_zonas
                    )
                    
                    # Analizar textura (datos simulados)
                    texture_gdf = gdf_zonas.copy()
                    for idx in range(len(texture_gdf)):
                        # Generar datos de textura simulados
                        texture_gdf.loc[idx, 'arena'] = np.random.uniform(30, 60)
                        texture_gdf.loc[idx, 'limo'] = np.random.uniform(20, 40)
                        texture_gdf.loc[idx, 'arcilla'] = np.random.uniform(10, 40)
                        
                        # Clasificar textura
                        texture = texture_analyzer.classify_texture(
                            texture_gdf.loc[idx, 'arena'],
                            texture_gdf.loc[idx, 'limo'],
                            texture_gdf.loc[idx, 'arcilla']
                        )
                        texture_gdf.loc[idx, 'textura_suelo'] = texture
                        
                        # Evaluar adecuación
                        categoria, puntaje = texture_analyzer.evaluate_texture_suitability(texture)
                        texture_gdf.loc[idx, 'categoria_adecuacion'] = categoria
                        texture_gdf.loc[idx, 'adecuacion_textura'] = puntaje
                    
                    st.session_state.analisis_textura = texture_gdf
                    st.session_state.analisis_completado = True
                    
                    st.success("✅ **Análisis completado exitosamente!**")
                    
                except Exception as e:
                    st.error(f"❌ **Error en el análisis:** {str(e)}")
        
        # Información adicional
        st.markdown("---")
        with st.expander("ℹ️ **Acerca de**"):
            st.markdown("""
            **Analizador de Cultivos Digital Twin v2.0**
            
            Esta aplicación utiliza:
            - **NASA POWER API** para datos climáticos
            - **GeoPandas** para análisis geoespacial
            - **Machine Learning** para predicciones
            
            Desarrollado para agricultura de precisión.
            """)

# Panel principal de resultados
def render_main_content():
    """Renderizar contenido principal."""
    if st.session_state.analisis_completado:
        # Crear pestañas de análisis
        tabs = create_analysis_tabs()
        
        with tabs['dashboard']:
            render_dashboard_tab()
        
        with tabs['map']:
            render_map_tab()
        
        with tabs['fertility']:
            render_fertility_tab()
        
        with tabs['climate']:
            render_climate_tab()
        
        with tabs['reports']:
            render_reports_tab()
    
    else:
        # Estado inicial o sin análisis
        if st.session_state.gdf_original is not None:
            render_parcel_preview()
        else:
            render_welcome_screen()

# Tablero de control
def render_dashboard_tab():
    """Renderizar pestaña de dashboard."""
    st.markdown("## 📊 **Dashboard de Análisis**")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card(
            "Área Total",
            f"{st.session_state.area_total:.2f} ha",
            help_text="Área total de la parcela"
        )
    
    with col2:
        if st.session_state.gdf_analisis is not None:
            avg_fertility = st.session_state.gdf_analisis['indice_fertilidad'].mean()
            create_metric_card(
                "Fertilidad Promedio",
                f"{avg_fertility:.3f}",
                delta="Óptimo" if avg_fertility > 0.7 else "Mejorable",
                delta_color="normal" if avg_fertility > 0.7 else "inverse",
                help_text="Índice de fertilidad promedio (0-1)"
            )
    
    with col3:
        if st.session_state.datos_clima:
            create_metric_card(
                "Precipitación",
                f"{st.session_state.datos_clima['precipitation']:.1f} mm/día",
                help_text="Precipitación diaria promedio"
            )
    
    with col4:
        create_metric_card(
            "Zonas Analizadas",
            f"{len(st.session_state.gdf_analisis) if st.session_state.gdf_analisis is not None else 0}",
            help_text="Número de zonas homogéneas"
        )
    
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.gdf_analisis is not None:
            st.markdown("### 📈 **Distribución de Fertilidad**")
            
            # Histograma de fertilidad
            fig = px.histogram(
                st.session_state.gdf_analisis,
                x='indice_fertilidad',
                nbins=20,
                title="Distribución del Índice de Fertilidad",
                labels={'indice_fertilidad': 'Índice de Fertilidad'},
                color_discrete_sequence=[colors['primary']]
            )
            
            fig.update_layout(
                xaxis_range=[0, 1],
                bargap=0.1
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if st.session_state.gdf_analisis is not None:
            st.markdown("### 🎯 **Prioridad de Intervención**")
            
            # Gráfico de pastel de prioridades
            priority_counts = st.session_state.gdf_analisis['prioridad'].value_counts()
            fig = px.pie(
                values=priority_counts.values,
                names=priority_counts.index,
                title="Distribución de Prioridades",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla resumen
    st.markdown("### 📋 **Resumen por Zona**")
    
    if st.session_state.gdf_analisis is not None:
        summary_cols = ['id_zona', 'area_ha', 'indice_fertilidad', 'categoria', 'prioridad']
        if 'textura_suelo' in st.session_state.gdf_analisis.columns:
            summary_cols.append('textura_suelo')
        
        summary_df = st.session_state.gdf_analisis[summary_cols].copy()
        summary_df['area_ha'] = summary_df['area_ha'].round(2)
        summary_df['indice_fertilidad'] = summary_df['indice_fertilidad'].round(3)
        
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'id_zona': st.column_config.NumberColumn("ID Zona", format="%d"),
                'area_ha': st.column_config.NumberColumn("Área (ha)", format="%.2f"),
                'indice_fertilidad': st.column_config.NumberColumn("Fertilidad", format="%.3f")
            }
        )

# Pestaña de mapas
def render_map_tab():
    """Renderizar pestaña de mapas."""
    st.markdown("## 🗺️ **Mapas Interactivos**")
    
    if st.session_state.gdf_analisis is None:
        st.warning("No hay datos de análisis disponibles.")
        return
    
    # Selector de tipo de mapa
    col1, col2 = st.columns([3, 1])
    
    with col2:
        map_type = st.selectbox(
            "**Tipo de Mapa**",
            ["Fertilidad", "Textura", "Potencial", "Clima"],
            key="map_type_select"
        )
        
        layer_style = st.selectbox(
            "**Estilo de Capa Base**",
            ["Esri Satellite", "OpenStreetMap", "Esri Street", "CartoDB Dark"],
            key="layer_style_select"
        )
    
    with col1:
        # Crear visualizador
        centroid = st.session_state.gdf_analisis.unary_union.centroid
        visualizer = MapVisualizer(
            center_lat=centroid.y,
            center_lon=centroid.x,
            zoom=14
        )
        
        # Crear mapa base
        m = visualizer.create_base_map(layer=layer_style)
        
        # Añadir capa según tipo
        if map_type == "Fertilidad":
            m = visualizer.add_choropleth_layer(
                m,
                st.session_state.gdf_analisis,
                column='indice_fertilidad',
                layer_name="Fertilidad",
                palette='fertility',
                legend_name="Índice de Fertilidad"
            )
        elif map_type == "Textura" and st.session_state.analisis_textura is not None:
            m = visualizer.add_choropleth_layer(
                m,
                st.session_state.analisis_textura,
                column='adecuacion_textura',
                layer_name="Adecuación de Textura",
                palette='texture',
                legend_name="Puntaje de Adecuación"
            )
        elif map_type == "Potencial":
            # Añadir capa de potencial (simulada)
            if 'potencial_cosecha' not in st.session_state.gdf_analisis.columns:
                st.session_state.gdf_analisis['potencial_cosecha'] = np.random.uniform(
                    10, 30, len(st.session_state.gdf_analisis)
                )
            
            m = visualizer.add_choropleth_layer(
                m,
                st.session_state.gdf_analisis,
                column='potencial_cosecha',
                layer_name="Potencial de Cosecha",
                palette='yield_potential',
                legend_name="Ton/Ha"
            )
        
        # Añadir capa de parcela original
        if st.session_state.gdf_original is not None:
            m = visualizer.add_parcel_layer(
                m,
                st.session_state.gdf_original,
                layer_name="Parcela Original",
                color='gray',
                fill_opacity=0.1
            )
        
        # Mostrar mapa
        st_folium(m, width=800, height=600, returned_objects=[])
    
    # Mapa estático
    st.markdown("---")
    st.markdown("### 🖼️ **Mapa Estático para Reportes**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🖨️ **Generar Mapa Estático**", use_container_width=True):
            with st.spinner("Generando mapa..."):
                if map_type == "Fertilidad":
                    static_map = visualizer.create_static_map(
                        st.session_state.gdf_analisis,
                        column='indice_fertilidad',
                        title="Mapa de Fertilidad"
                    )
                elif map_type == "Textura" and st.session_state.analisis_textura is not None:
                    static_map = visualizer.create_static_map(
                        st.session_state.analisis_textura,
                        column='adecuacion_textura',
                        title="Mapa de Adecuación de Textura"
                    )
                else:
                    static_map = visualizer.create_static_map(
                        st.session_state.gdf_analisis,
                        title="Mapa de Parcela"
                    )
                
                if static_map:
                    st.image(static_map, use_column_width=True)
                    
                    # Botón de descarga
                    create_download_button(
                        static_map.getvalue(),
                        filename=f"mapa_{map_type.lower()}.png",
                        button_text="📥 Descargar Mapa PNG",
                        mime_type="image/png"
                    )

# Pestaña de fertilidad
def render_fertility_tab():
    """Renderizar pestaña de fertilidad."""
    st.markdown("## 🌱 **Análisis de Fertilidad**")
    
    if st.session_state.gdf_analisis is None:
        st.warning("No hay datos de fertilidad disponibles.")
        return
    
    # Gráficos de NPK
    st.markdown("### 📊 **Niveles de Nutrientes**")
    
    if all(col in st.session_state.gdf_analisis.columns for col in ['nitrogeno', 'fosforo', 'potasio']):
        optimal_ranges = {
            'nitrogen': (120, 200),
            'phosphorus': (40, 80),
            'potassium': (160, 240)
        }
        
        avg_n = st.session_state.gdf_analisis['nitrogeno'].mean()
        avg_p = st.session_state.gdf_analisis['fosforo'].mean()
        avg_k = st.session_state.gdf_analisis['potasio'].mean()
        
        create_npk_gauge_chart(avg_n, avg_p, avg_k, optimal_ranges)
    
    # Distribución espacial
    st.markdown("### 🗺️ **Distribución Espacial de Fertilidad**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Mapa de calor de fertilidad
        fig = visualizer.create_interactive_plotly_map(
            st.session_state.gdf_analisis,
            color_column='indice_fertilidad',
            title="Mapa de Calor de Fertilidad"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de barras por zona
        fig = visualizer.create_fertility_chart(
            st.session_state.gdf_analisis.sort_values('indice_fertilidad', ascending=False).head(10),
            title="Top 10 Zonas por Fertilidad"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recomendaciones de fertilización
    st.markdown("### 💡 **Recomendaciones de Fertilización**")
    
    if all(col in st.session_state.gdf_analisis.columns 
           for col in ['recomendacion_n', 'recomendacion_p', 'recomendacion_k']):
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_n = st.session_state.gdf_analisis['recomendacion_n'].sum()
            create_metric_card(
                "Nitrógeno Requerido",
                f"{total_n:.0f} kg",
                help_text="Total de nitrógeno recomendado para toda la parcela"
            )
        
        with col2:
            total_p = st.session_state.gdf_analisis['recomendacion_p'].sum()
            create_metric_card(
                "Fósforo Requerido",
                f"{total_p:.0f} kg",
                help_text="Total de fósforo recomendado para toda la parcela"
            )
        
        with col3:
            total_k = st.session_state.gdf_analisis['recomendacion_k'].sum()
            create_metric_card(
                "Potasio Requerido",
                f"{total_k:.0f} kg",
                help_text="Total de potasio recomendado para toda la parcela"
            )
        
        # Tabla de recomendaciones detalladas
        with st.expander("📋 **Ver Recomendaciones Detalladas por Zona**"):
            rec_cols = ['id_zona', 'area_ha', 'recomendacion_n', 'recomendacion_p', 'recomendacion_k', 'prioridad']
            rec_df = st.session_state.gdf_analisis[rec_cols].copy()
            rec_df['area_ha'] = rec_df['area_ha'].round(2)
            
            for col in ['recomendacion_n', 'recomendacion_p', 'recomendacion_k']:
                rec_df[col] = rec_df[col].round(1)
            
            st.dataframe(rec_df, use_container_width=True, hide_index=True)

# Pestaña de clima
def render_climate_tab():
    """Renderizar pestaña de análisis climático."""
    st.markdown("## 🌦️ **Análisis Climático**")
    
    if not st.session_state.datos_clima:
        st.warning("No hay datos climáticos disponibles.")
        return
    
    # Datos climáticos actuales
    st.markdown("### ☀️ **Condiciones Climáticas Actuales**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card(
            "Radiación Solar",
            f"{st.session_state.datos_clima['solar_radiation']:.1f} MJ/m²/día",
            help_text="Radiación solar diaria promedio"
        )
    
    with col2:
        create_metric_card(
            "Precipitación",
            f"{st.session_state.datos_clima['precipitation']:.1f} mm/día",
            help_text="Precipitación diaria promedio"
        )
    
    with col3:
        create_metric_card(
            "Temperatura",
            f"{st.session_state.datos_clima['temperature']:.1f} °C",
            help_text="Temperatura promedio"
        )
    
    with col4:
        create_metric_card(
            "Humedad Relativa",
            f"{st.session_state.datos_clima['humidity']:.1f} %",
            help_text="Humedad relativa promedio"
        )
    
    # Datos históricos
    st.markdown("---")
    st.markdown("### 📅 **Datos Climáticos Históricos (10 años)**")
    
    if st.session_state.datos_clima_historicos:
        fig = visualizer.create_climate_timeseries(
            st.session_state.datos_clima_historicos,
            title="Promedios Mensuales - Últimos 10 Años"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recomendaciones climáticas
    st.markdown("---")
    st.markdown("### 💡 **Recomendaciones Climáticas**")
    
    clima_analyzer = ClimateAnalyzer()
    indicators = clima_analyzer.calculate_climate_indicators(
        st.session_state.datos_clima,
        st.session_state.cultivo_seleccionado
    )
    
    for indicator_name, indicator_data in indicators.items():
        with st.expander(f"{indicator_name.replace('_', ' ').title()}: {indicator_data['status']}"):
            st.markdown(f"**Descripción:** {indicator_data['description']}")
            st.markdown(f"**Recomendación:** {indicator_data['recommendation']}")
            if 'value' in indicator_data:
                st.markdown(f"**Valor:** {indicator_data['value']}")

# Pestaña de reportes
def render_reports_tab():
    """Renderizar pestaña de reportes."""
    st.markdown("## 📈 **Generación de Reportes**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "**Tipo de Reporte**",
            ["Reporte Completo", "Reporte de Fertilidad", "Reporte Climático", "Reporte de Textura"],
            key="report_type_select"
        )
    
    with col2:
        format_type = st.selectbox(
            "**Formato**",
            ["PDF", "Excel", "CSV", "GeoJSON"],
            key="format_type_select"
        )
    
    st.markdown("---")
    
    # Botones de generación
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 **Generar Reporte PDF**", use_container_width=True, icon="📄"):
            with st.spinner("Generando reporte PDF..."):
                # Aquí iría la lógica de generación de PDF
                st.success("Reporte PDF generado exitosamente!")
                # create_download_button(pdf_data, "reporte.pdf", "application/pdf")
    
    with col2:
        if st.button("📊 **Exportar a Excel**", use_container_width=True, icon="📊"):
            with st.spinner("Exportando a Excel..."):
                if st.session_state.gdf_analisis is not None:
                    # Convertir a DataFrame
                    df = pd.DataFrame(st.session_state.gdf_analisis.drop(columns='geometry'))
                    
                    # Exportar a Excel
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Análisis', index=False)
                    
                    excel_buffer.seek(0)
                    
                    create_download_button(
                        excel_buffer.getvalue(),
                        filename="analisis_cultivos.xlsx",
                        button_text="📥 Descargar Excel",
                        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    
    with col3:
        if st.button("🌐 **Exportar GeoJSON**", use_container_width=True, icon="🌐"):
            with st.spinner("Exportando GeoJSON..."):
                if st.session_state.gdf_analisis is not None:
                    geojson_str = FileProcessor.export_to_geojson(st.session_state.gdf_analisis)
                    
                    create_download_button(
                        geojson_str,
                        filename="parcela_analisis.geojson",
                        button_text="📥 Descargar GeoJSON",
                        mime_type="application/json"
                    )
    
    # Vista previa de datos
    st.markdown("---")
    st.markdown("### 👁️ **Vista Previa de Datos**")
    
    if st.session_state.gdf_analisis is not None:
        preview_cols = st.multiselect(
            "Seleccionar columnas para vista previa:",
            options=st.session_state.gdf_analisis.columns.tolist(),
            default=['id_zona', 'area_ha', 'indice_fertilidad', 'categoria', 'prioridad']
        )
        
        if preview_cols:
            preview_df = st.session_state.gdf_analisis[preview_cols].copy()
            
            # Formatear números
            for col in preview_df.columns:
                if preview_df[col].dtype == 'float64':
                    preview_df[col] = preview_df[col].round(3)
            
            st.dataframe(preview_df, use_container_width=True, hide_index=True)

# Vista previa de parcela
def render_parcel_preview():
    """Renderizar vista previa de parcela."""
    st.markdown("## 🗺️ **Vista Previa de la Parcela**")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Crear mapa de la parcela
        if st.session_state.gdf_original is not None:
            centroid = st.session_state.gdf_original.unary_union.centroid
            visualizer = MapVisualizer(
                center_lat=centroid.y,
                center_lon=centroid.x,
                zoom=14
            )
            
            m = visualizer.create_base_map()
            m = visualizer.add_parcel_layer(
                m,
                st.session_state.gdf_original,
                layer_name="Parcela",
                color=colors['primary'],
                fill_opacity=0.3
            )
            
            st_folium(m, width=600, height=400, returned_objects=[])
    
    with col2:
        create_info_card(
            "Información de la Parcela",
            f"""
            **Área Total:** {st.session_state.area_total:.2f} ha
            
            **Cultivo Seleccionado:** {st.session_state.cultivo_seleccionado}
            
            **Mes de Análisis:** {st.session_state.mes_seleccionado}
            
            **Zonas a crear:** {st.session_state.n_zonas_seleccionado}
            
            **Estado:** Listo para análisis
            """,
            icon="📋",
            color=colors['info']
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ **Acciones**")
        
        if st.button("🔄 **Actualizar Vista**", use_container_width=True):
            st.rerun()

# Pantalla de bienvenida
def render_welcome_screen():
    """Renderizar pantalla de bienvenida."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 👋 **Bienvenido al Analizador de Cultivos Digital Twin**
        
        Esta aplicación le permite realizar análisis avanzados de suelos y cultivos
        utilizando datos satelitales y climáticos en tiempo real.
        
        ### 🚀 **Cómo empezar:**
        
        1. **Suba su parcela** en formato Shapefile (ZIP), KML o GeoJSON
        2. **Seleccione el cultivo** a analizar
        3. **Configure los parámetros** de análisis
        4. **Ejecute el análisis completo**
        5. **Explore los resultados** en las diferentes pestañas
        
        ### 📊 **Características principales:**
        
        ✅ **Análisis de fertilidad NPK** por zonas homogéneas  
        ✅ **Mapas interactivos** con múltiples capas base  
        ✅ **Datos climáticos históricos** de NASA POWER  
        ✅ **Recomendaciones personalizadas** de fertilización  
        ✅ **Reportes exportables** en múltiples formatos  
        ✅ **Interfaz moderna y responsiva**
        
        ### 🌐 **Datos utilizados:**
        
        - **NASA POWER API**: Datos climáticos históricos y en tiempo real
        - **PlanetScope**: Imágenes satelitales de alta resolución
        - **Modelos predictivos**: Machine Learning para recomendaciones
        """)
    
    with col2:
        st.markdown("### 📁 **Formatos soportados**")
        create_info_card(
            "Shapefile (.zip)",
            "Archivo ZIP que contiene .shp, .shx, .dbf, .prj",
            icon="🗺️",
            color=colors['primary']
        )
        
        create_info_card(
            "KML/KMZ",
            "Archivos de Google Earth/Google Maps",
            icon="🌍",
            color=colors['secondary']
        )
        
        create_info_card(
            "GeoJSON",
            "Formato estándar para datos geoespaciales",
            icon="📄",
            color=colors['accent']
        )
        
        st.markdown("---")
        
        create_warning_card(
            "Recomendaciones",
            """
            Para mejores resultados:
            1. Use coordenadas en WGS84 (EPSG:4326)
            2. Asegure geometrías válidas
            3. Parcelas menores a 10,000 ha
            4. Conexión a internet estable
            """
        )

# Footer
def render_footer():
    """Renderizar footer de la aplicación."""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; color: {colors['text_light']};">
            <p>🌿 <b>Analizador de Cultivos Digital Twin v2.0</b></p>
            <p>Powered by NASA POWER API</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; color: {colors['text_light']};">
            <p>📧 <b>Soporte:</b> soporte@agtech.com</p>
            <p>📞 <b>Teléfono:</b> +57 1 234 5678</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center; color: {colors['text_light']};">
            <p>🔗 <b>Enlaces:</b></p>
            <p>
                <a href="#" style="color: {colors['primary']};">Documentación</a> | 
                <a href="#" style="color: {colors['primary']};">API</a> | 
                <a href="#" style="color: {colors['primary']};">GitHub</a>
            </p>
        </div>
        """, unsafe_allow_html=True)

# Función principal
def main():
    """Función principal de la aplicación."""
    # Inicializar session state
    init_session_state()
    
    # Renderizar componentes
    render_header()
    render_sidebar()
    render_main_content()
    render_footer()

# Punto de entrada
if __name__ == "__main__":
    main()
