# app/__init__.py
"""
Analizador de Cultivos - Digital Twin con NASA POWER + PlanetScope
"""

__version__ = "2.0.0"
__author__ = "AgTech Solutions"
__email__ = "soporte@agtech.com"

# Exportar módulos principales
from .core.analysis import SoilAnalyzer
from .core.climate import ClimateAnalyzer
from .core.soil import SoilTextureAnalyzer
from .ui.components import *
from .ui.styles import *
from .utils.file_processing import FileProcessor
from .utils.visualization import MapVisualizer
