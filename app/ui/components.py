# app/ui/components.py
import streamlit as st
from typing import List, Dict

def create_metric_card(
    title: str, 
    value: str, 
    delta: str = None,
    color: str = "primary"
) -> None:
    """Componente de tarjeta métrica moderna"""
    st.markdown(f"""
    <div class="metric-card-{color}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-delta">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def create_analysis_tabs() -> Dict:
    """Crea pestañas de análisis dinámicas"""
    tabs = st.tabs([
        "📊 Dashboard",
        "🗺️ Mapa Interactivo", 
        "🌱 Fertilidad",
        "🌦️ Clima",
        "📈 Reportes"
    ])
    return {tab: content for tab, content in zip(tabs, ["dashboard", "map", "fertility", "climate", "reports"])}
