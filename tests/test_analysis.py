# tests/test_analysis.py
import pytest
import numpy as np
from app.core.analysis import SoilAnalyzer

def test_soil_analyzer_initialization():
    """Test de inicialización del analizador de suelo."""
    analyzer = SoilAnalyzer("PALMA_ACEITERA", "ENERO")
    assert analyzer.crop_type == "PALMA_ACEITERA"
    assert analyzer.analysis_month == "ENERO"
    assert analyzer.params is not None

def test_fertility_index_calculation():
    """Test de cálculo de índice de fertilidad."""
    analyzer = SoilAnalyzer("PALMA_ACEITERA", "ENERO")
    
    result = analyzer.calculate_fertility_index(
        nitrogen=160,  # óptimo para palma
        phosphorus=60,  # óptimo para palma
        potassium=200,  # óptimo para palma
        organic_matter=3.5,
        ph=5.5,
        ndvi=0.7
    )
    
    assert 'index' in result
    assert 'category' in result
    assert 'priority' in result
    assert 0 <= result['index'] <= 1

def test_npk_recommendations():
    """Test de recomendaciones NPK."""
    analyzer = SoilAnalyzer("PALMA_ACEITERA", "ENERO")
    
    recommendations = analyzer.calculate_npk_recommendations(
        nitrogen=100,  # bajo
        phosphorus=60,  # óptimo
        potassium=180,  # cercano a óptimo
        ndvi=0.6,
        organic_matter=3.0,
        ph=5.5
    )
    
    assert 'nitrogen' in recommendations
    assert 'phosphorus' in recommendations
    assert 'potassium' in recommendations
    assert recommendations['nitrogen']['deficit'] > 0
