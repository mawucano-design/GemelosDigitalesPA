# app/ui/styles.py
"""
Estilos CSS personalizados para la aplicación.
"""
import streamlit as st

def inject_custom_css():
    """Inyectar CSS personalizado en la aplicación."""
    st.markdown("""
    <style>
    /* Estilos generales */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header principal */
    .main-header {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
    }
    
    /* Tarjetas métricas */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .metric-title {
        color: #2C3E50;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: #2E7D32;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
    }
    
    .metric-delta {
        color: #4CAF50;
        font-size: 14px;
        margin-top: 4px;
    }
    
    /* Botones */
    .stButton > button {
        background-color: #2E7D32;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1B5E20;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        background-color: rgba(255, 255, 255, 0.8);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        border-bottom: 3px solid #2E7D32;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 1px solid #E0E0E0;
    }
    
    /* Dataframes */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Tooltips */
    .stTooltip {
        border-radius: 8px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid #E0E0E0;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
        }
        
        .metric-value {
            font-size: 24px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_color_palette():
    """Definir paleta de colores de la aplicación."""
    return {
        'primary': '#2E7D32',
        'primary_light': '#4CAF50',
        'primary_dark': '#1B5E20',
        'secondary': '#2196F3',
        'accent': '#FF9800',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#F44336',
        'info': '#2196F3',
        'text': '#2C3E50',
        'text_light': '#666666',
        'background': '#F5F5F5',
        'card_bg': '#FFFFFF',
        'border': '#E0E0E0'
    }

def get_status_color(status: str) -> str:
    """Obtener color basado en estado."""
    colors = {
        'EXCELENTE': '#4CAF50',
        'MUY ALTA': '#8BC34A',
        'ALTA': '#CDDC39',
        'MEDIA': '#FFC107',
        'BAJA': '#FF9800',
        'MUY BAJA': '#F44336',
        'URGENTE': '#D32F2F',
        'ÓPTIMA': '#4CAF50',
        'ADECUADA': '#8BC34A',
        'MODERADA': '#FFC107',
        'LIMITANTE': '#FF9800',
        'MUY LIMITANTE': '#F44336'
    }
    return colors.get(status.upper(), '#666666')
