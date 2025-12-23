# app/ui/components.py
"""
Componentes reutilizables de la interfaz de usuario.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional, Any, Tuple
import pandas as pd
import numpy as np

def create_metric_card(
    title: str,
    value: Any,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    help_text: Optional[str] = None,
    col: Optional[st.delta_generator.DeltaGenerator] = None
):
    """
    Crear una tarjeta métrica estilizada.
    
    Args:
        title: Título de la métrica
        value: Valor principal
        delta: Valor delta (cambio)
        delta_color: Color del delta ("normal", "inverse", "off")
        help_text: Texto de ayuda (tooltip)
        col: Columna de Streamlit donde colocar (opcional)
    """
    if col is None:
        col = st
    
    with col:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color=delta_color,
            help=help_text
        )

def create_info_card(
    title: str,
    content: str,
    icon: str = "ℹ️",
    color: str = "#4CAF50",
    col: Optional[st.delta_generator.DeltaGenerator] = None
):
    """
    Crear una tarjeta informativa.
    
    Args:
        title: Título de la tarjeta
        content: Contenido (puede ser markdown)
        icon: Ícono para mostrar
        color: Color del borde
        col: Columna de Streamlit
    """
    if col is None:
        col = st
    
    with col:
        st.markdown(f"""
        <div style="
            border-left: 4px solid {color};
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <strong>{title}</strong>
            </div>
            <div style="color: #495057;">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_warning_card(
    title: str,
    content: str,
    col: Optional[st.delta_generator.DeltaGenerator] = None
):
    """Crear tarjeta de advertencia."""
    create_info_card(title, content, "⚠️", "#FF9800", col)

def create_error_card(
    title: str,
    content: str,
    col: Optional[st.delta_generator.DeltaGenerator] = None
):
    """Crear tarjeta de error."""
    create_info_card(title, content, "❌", "#F44336", col)

def create_success_card(
    title: str,
    content: str,
    col: Optional[st.delta_generator.DeltaGenerator] = None
):
    """Crear tarjeta de éxito."""
    create_info_card(title, content, "✅", "#4CAF50", col)

def create_analysis_tabs() -> Dict[str, st.delta_generator.DeltaGenerator]:
    """
    Crear pestañas de análisis predefinidas.
    
    Returns:
        Diccionario con pestañas y sus contenedores
    """
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "🗺️ Mapa Interactivo", 
        "🌱 Fertilidad",
        "🌦️ Clima",
        "📈 Reportes"
    ])
    
    return {
        'dashboard': tab1,
        'map': tab2,
        'fertility': tab3,
        'climate': tab4,
        'reports': tab5
    }

def create_progress_with_text(
    label: str,
    value: float,
    max_value: float = 100,
    color: str = "#4CAF50"
):
    """
    Crear barra de progreso con texto.
    
    Args:
        label: Etiqueta descriptiva
        value: Valor actual
        max_value: Valor máximo
        color: Color de la barra
    """
    percentage = (value / max_value) * 100
    
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
            <span>{label}</span>
            <span><strong>{value:.1f}</strong> / {max_value:.1f} ({percentage:.0f}%)</span>
        </div>
        <div style="
            width: 100%;
            background-color: #e9ecef;
            border-radius: 0.5rem;
            overflow: hidden;
            height: 0.75rem;
        ">
            <div style="
                width: {percentage}%;
                background-color: {color};
                height: 100%;
                border-radius: 0.5rem;
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_soil_texture_chart(
    sand: float,
    silt: float,
    clay: float,
    title: str = "Triángulo Textural"
):
    """
    Crear gráfico de triángulo textural.
    
    Args:
        sand: Porcentaje de arena
        silt: Porcentaje de limo
        clay: Porcentaje de arcilla
        title: Título del gráfico
    """
    # Crear figura del triángulo textural
    fig = go.Figure()
    
    # Definir vértices del triángulo
    vertices = {
        'sand': (100, 0, 0),    # 100% arena, 0% limo, 0% arcilla
        'silt': (0, 100, 0),    # 0% arena, 100% limo, 0% arcilla
        'clay': (0, 0, 100)     # 0% arena, 0% limo, 100% arcilla
    }
    
    # Añadir triángulo base
    fig.add_trace(go.Scatterternary({
        'mode': 'lines',
        'a': [100, 0, 0, 100],
        'b': [0, 100, 0, 0],
        'c': [0, 0, 100, 0],
        'line': {'color': 'black', 'width': 2},
        'fill': 'toself',
        'fillcolor': 'rgba(240, 240, 240, 0.5)',
        'name': 'Triángulo textural'
    }))
    
    # Añadir punto de la muestra
    fig.add_trace(go.Scatterternary({
        'mode': 'markers+text',
        'a': [sand],
        'b': [silt],
        'c': [clay],
        'marker': {
            'size': 20,
            'color': '#FF5722',
            'symbol': 'circle'
        },
        'text': [f'Arena: {sand:.1f}%<br>Limo: {silt:.1f}%<br>Arcilla: {clay:.1f}%'],
        'textposition': 'top center',
        'name': 'Muestra'
    }))
    
    # Configurar layout
    fig.update_layout({
        'title': {
            'text': title,
            'font': {'size': 16}
        },
        'ternary': {
            'sum': 100,
            'aaxis': {
                'title': 'Arena (%)',
                'min': 0,
                'linewidth': 2,
                'ticks': 'outside'
            },
            'baxis': {
                'title': 'Limo (%)',
                'min': 0,
                'linewidth': 2,
                'ticks': 'outside'
            },
            'caxis': {
                'title': 'Arcilla (%)',
                'min': 0,
                'linewidth': 2,
                'ticks': 'outside'
            }
        },
        'showlegend': False,
        'height': 500
    })
    
    return fig

def create_npk_gauge_chart(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    optimal_ranges: Dict[str, Tuple[float, float]]
):
    """
    Crear gráficos de gauge para NPK.
    
    Args:
        nitrogen: Valor de nitrógeno
        phosphorus: Valor de fósforo
        potassium: Valor de potasio
        optimal_ranges: Rangos óptimos para cada nutriente
    """
    col1, col2, col3 = st.columns(3)
    
    nutrients = [
        ('Nitrógeno', nitrogen, optimal_ranges['nitrogen'], 'N', col1, '#FF6B6B'),
        ('Fósforo', phosphorus, optimal_ranges['phosphorus'], 'P₂O₅', col2, '#4ECDC4'),
        ('Potasio', potassium, optimal_ranges['potassium'], 'K₂O', col3, '#45B7D1')
    ]
    
    for name, value, (min_val, max_val), unit, col, color in nutrients:
        with col:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                title={'text': f"{name} ({unit})"},
                delta={'reference': (min_val + max_val) / 2},
                gauge={
                    'axis': {'range': [min_val * 0.5, max_val * 1.5]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [min_val * 0.5, min_val], 'color': "lightgray"},
                        {'range': [min_val, max_val], 'color': "lightgreen"},
                        {'range': [max_val, max_val * 1.5], 'color': "lightgray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': max_val
                    }
                }
            ))
            
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)

def create_download_button(
    data: Any,
    filename: str,
    button_text: str = "📥 Descargar",
    mime_type: str = "text/csv"
):
    """
    Crear botón de descarga para diferentes tipos de datos.
    
    Args:
        data: Datos a descargar
        filename: Nombre del archivo
        button_text: Texto del botón
        mime_type: Tipo MIME del archivo
    """
    st.download_button(
        label=button_text,
        data=data,
        file_name=filename,
        mime=mime_type
    )

def create_expandable_recommendations(
    title: str,
    recommendations: List[str],
    icon: str = "💡"
):
    """
    Crear sección expandible de recomendaciones.
    
    Args:
        title: Título de la sección
        recommendations: Lista de recomendaciones
        icon: Ícono para mostrar
    """
    with st.expander(f"{icon} {title}"):
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
