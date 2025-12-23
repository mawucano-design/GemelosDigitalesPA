# app/core/analysis.py
import numpy as np
import pandas as pd
import geopandas as gpd
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class CropParameters:
    """Parámetros específicos por cultivo."""
    nitrogeno_min: float
    nitrogeno_max: float
    nitrogeno_optimo: float
    fosforo_min: float
    fosforo_max: float
    fosforo_optimo: float
    potasio_min: float
    potasio_max: float
    potasio_optimo: float
    materia_organica_optima: float
    humedad_optima: float
    ph_optimo: float
    conductividad_optima: float

class SoilAnalyzer:
    """Analizador principal de suelo y fertilidad."""
    
    # Parámetros por cultivo
    CROP_PARAMETERS = {
        'PALMA_ACEITERA': CropParameters(
            nitrogeno_min=120, nitrogeno_max=200, nitrogeno_optimo=160,
            fosforo_min=40, fosforo_max=80, fosforo_optimo=60,
            potasio_min=160, potasio_max=240, potasio_optimo=200,
            materia_organica_optima=3.5,
            humedad_optima=0.35,
            ph_optimo=5.5,
            conductividad_optima=1.2
        ),
        'CACAO': CropParameters(
            nitrogeno_min=100, nitrogeno_max=180, nitrogeno_optimo=140,
            fosforo_min=30, fosforo_max=60, fosforo_optimo=45,
            potasio_min=120, potasio_max=200, potasio_optimo=160,
            materia_organica_optima=4.0,
            humedad_optima=0.4,
            ph_optimo=6.0,
            conductividad_optima=1.0
        ),
        'BANANO': CropParameters(
            nitrogeno_min=180, nitrogeno_max=280, nitrogeno_optimo=230,
            fosforo_min=50, fosforo_max=90, fosforo_optimo=70,
            potasio_min=250, potasio_max=350, potasio_optimo=300,
            materia_organica_optima=4.5,
            humedad_optima=0.45,
            ph_optimo=6.2,
            conductividad_optima=1.5
        )
    }
    
    # Factores estacionales
    MONTH_FACTORS = {
        "ENERO": 0.9, "FEBRERO": 0.95, "MARZO": 1.0, "ABRIL": 1.05,
        "MAYO": 1.1, "JUNIO": 1.0, "JULIO": 0.95, "AGOSTO": 0.9,
        "SEPTIEMBRE": 0.95, "OCTUBRE": 1.0, "NOVIEMBRE": 1.05, "DICIEMBRE": 1.0
    }
    
    def __init__(self, crop_type: str, analysis_month: str):
        """
        Inicializar analizador.
        
        Args:
            crop_type: Tipo de cultivo (PALMA_ACEITERA, CACAO, BANANO)
            analysis_month: Mes de análisis
        """
        self.crop_type = crop_type
        self.analysis_month = analysis_month
        self.params = self.CROP_PARAMETERS.get(crop_type)
        
        if not self.params:
            raise ValueError(f"Cultivo no soportado: {crop_type}")
    
    def calculate_fertility_index(
        self,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        organic_matter: float,
        ph: float,
        ndvi: float = 0.6
    ) -> Dict[str, Any]:
        """
        Calcular índice de fertilidad compuesto.
        
        Returns:
            Diccionario con índice y categoría
        """
        try:
            # Normalizar valores
            n_norm = self._normalize_value(nitrogen, self.params.nitrogeno_optimo)
            p_norm = self._normalize_value(phosphorus, self.params.fosforo_optimo)
            k_norm = self._normalize_value(potassium, self.params.potasio_optimo)
            om_norm = self._normalize_value(organic_matter, self.params.materia_organica_optima)
            ph_norm = 1 - abs(ph - self.params.ph_optimo) / 4.0
            
            # Aplicar factor estacional
            month_factor = self.MONTH_FACTORS.get(self.analysis_month, 1.0)
            
            # Calcular índice compuesto (pesos ajustables)
            fertility_index = (
                n_norm * 0.25 +
                p_norm * 0.20 +
                k_norm * 0.20 +
                om_norm * 0.15 +
                ph_norm * 0.10 +
                ndvi * 0.10
            ) * month_factor
            
            fertility_index = np.clip(fertility_index, 0, 1)
            
            # Determinar categoría
            category, priority = self._classify_fertility(fertility_index)
            
            return {
                'index': float(fertility_index),
                'category': category,
                'priority': priority,
                'components': {
                    'nitrogen': float(n_norm),
                    'phosphorus': float(p_norm),
                    'potassium': float(k_norm),
                    'organic_matter': float(om_norm),
                    'ph': float(ph_norm)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculando índice de fertilidad: {e}")
            return {
                'index': 0.5,
                'category': 'MEDIA',
                'priority': 'MEDIA',
                'components': {}
            }
    
    def calculate_npk_recommendations(
        self,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        ndvi: float,
        organic_matter: float,
        ph: float
    ) -> Dict[str, Dict[str, float]]:
        """
        Calcular recomendaciones de fertilización NPK.
        
        Returns:
            Recomendaciones para cada nutriente
        """
        recommendations = {}
        
        # Nitrógeno
        n_deficit = max(0, self.params.nitrogeno_optimo - nitrogen)
        n_efficiency = 1.4
        n_growth = 1.2
        n_om_factor = max(0.7, 1.0 - (organic_matter / 15.0))
        n_ndvi_factor = 1.0 + (0.5 - ndvi) * 0.4
        n_recommendation = n_deficit * n_efficiency * n_growth * n_om_factor * n_ndvi_factor
        n_recommendation = np.clip(n_recommendation, 20, 250)
        
        # Fósforo
        p_deficit = max(0, self.params.fosforo_optimo - phosphorus)
        p_efficiency = 1.6
        p_ph_factor = 1.3 if ph < 5.5 or ph > 7.5 else 1.0
        p_recommendation = p_deficit * p_efficiency * p_ph_factor
        p_recommendation = np.clip(p_recommendation, 10, 120)
        
        # Potasio
        k_deficit = max(0, self.params.potasio_optimo - potassium)
        k_efficiency = 1.3
        k_texture_factor = 1.2 if organic_matter < 2.0 else 1.0
        k_yield_factor = 1.0 + (0.5 - ndvi) * 0.3
        k_recommendation = k_deficit * k_efficiency * k_texture_factor * k_yield_factor
        k_recommendation = np.clip(k_recommendation, 15, 200)
        
        recommendations['nitrogen'] = {
            'deficit': float(n_deficit),
            'recommendation': float(n_recommendation),
            'unit': 'kg/ha N'
        }
        recommendations['phosphorus'] = {
            'deficit': float(p_deficit),
            'recommendation': float(p_recommendation),
            'unit': 'kg/ha P₂O₅'
        }
        recommendations['potassium'] = {
            'deficit': float(k_deficit),
            'recommendation': float(k_recommendation),
            'unit': 'kg/ha K₂O'
        }
        
        return recommendations
    
    def calculate_yield_potential(
        self,
        fertility_index: float,
        solar_radiation: float,
        precipitation: float,
        wind_speed: float,
        ndvi: float,
        temperature: float = 25.0
    ) -> float:
        """
        Calcular potencial de cosecha.
        
        Returns:
            Potencial en toneladas por hectárea
        """
        try:
            # Factores de ajuste
            rad_factor = np.clip(solar_radiation / 20.0, 0.5, 1.2)
            water_factor = np.clip(precipitation / 6.0, 0.3, 1.5)
            wind_factor = np.clip(1.0 - (wind_speed - 2.0) / 10.0, 0.7, 1.0)
            temp_factor = 1.0 - abs(temperature - 25.0) / 20.0
            ndvi_factor = np.clip(ndvi / 0.8, 0.5, 1.2)
            
            # Potencial base según cultivo
            base_yield = {
                'PALMA_ACEITERA': 25.0,
                'CACAO': 1.5,
                'BANANO': 40.0
            }.get(self.crop_type, 20.0)
            
            # Calcular potencial
            yield_potential = (
                base_yield *
                fertility_index *
                rad_factor *
                water_factor *
                wind_factor *
                temp_factor *
                ndvi_factor
            )
            
            return float(np.clip(yield_potential, 0, base_yield * 2))
            
        except Exception as e:
            logger.error(f"Error calculando potencial de cosecha: {e}")
            return 0.0
    
    def _normalize_value(self, value: float, optimal: float) -> float:
        """Normalizar valor respecto al óptimo."""
        return np.clip(value / (optimal * 1.5), 0, 1)
    
    def _classify_fertility(self, index: float) -> Tuple[str, str]:
        """Clasificar índice de fertilidad."""
        if index >= 0.85:
            return "EXCELENTE", "BAJA"
        elif index >= 0.70:
            return "MUY ALTA", "MEDIA-BAJA"
        elif index >= 0.55:
            return "ALTA", "MEDIA"
        elif index >= 0.40:
            return "MEDIA", "MEDIA-ALTA"
        elif index >= 0.25:
            return "BAJA", "ALTA"
        else:
            return "MUY BAJA", "URGENTE"
    
    def analyze_zones(
        self,
        gdf: gpd.GeoDataFrame,
        n_zones: int = 16,
        seed: int = 42
    ) -> gpd.GeoDataFrame:
        """
        Analizar parcelas divididas en zonas.
        
        Returns:
            GeoDataFrame con análisis por zona
        """
        try:
            # Copiar GeoDataFrame
            result_gdf = gdf.copy()
            
            # Generar datos sintéticos (en producción usar datos reales)
            np.random.seed(seed)
            n_rows = len(result_gdf)
            
            # Generar valores aleatorios pero consistentes
            for idx in range(n_rows):
                # Coordenadas para semilla única
                if hasattr(result_gdf.iloc[idx].geometry, 'centroid'):
                    centroid = result_gdf.iloc[idx].geometry.centroid
                    zone_seed = int(abs(hash(f"{centroid.x}_{centroid.y}"))) % 10000
                    np.random.seed(zone_seed)
                
                # Generar datos de suelo
                result_gdf.loc[idx, 'nitrogeno'] = np.random.normal(
                    self.params.nitrogeno_optimo * 0.9,
                    self.params.nitrogeno_optimo * 0.15
                )
                result_gdf.loc[idx, 'fosforo'] = np.random.normal(
                    self.params.fosforo_optimo * 0.9,
                    self.params.fosforo_optimo * 0.2
                )
                result_gdf.loc[idx, 'potasio'] = np.random.normal(
                    self.params.potasio_optimo * 0.9,
                    self.params.potasio_optimo * 0.18
                )
                result_gdf.loc[idx, 'materia_organica'] = np.random.normal(
                    self.params.materia_organica_optima,
                    1.0
                )
                result_gdf.loc[idx, 'ph'] = np.random.normal(
                    self.params.ph_optimo,
                    0.5
                )
                result_gdf.loc[idx, 'ndvi'] = np.random.uniform(0.4, 0.8)
            
            # Calcular índices para cada zona
            for idx in range(n_rows):
                fertility_result = self.calculate_fertility_index(
                    nitrogen=result_gdf.loc[idx, 'nitrogeno'],
                    phosphorus=result_gdf.loc[idx, 'fosforo'],
                    potassium=result_gdf.loc[idx, 'potasio'],
                    organic_matter=result_gdf.loc[idx, 'materia_organica'],
                    ph=result_gdf.loc[idx, 'ph'],
                    ndvi=result_gdf.loc[idx, 'ndvi']
                )
                
                result_gdf.loc[idx, 'indice_fertilidad'] = fertility_result['index']
                result_gdf.loc[idx, 'categoria'] = fertility_result['category']
                result_gdf.loc[idx, 'prioridad'] = fertility_result['priority']
                
                # Calcular recomendaciones
                recommendations = self.calculate_npk_recommendations(
                    nitrogen=result_gdf.loc[idx, 'nitrogeno'],
                    phosphorus=result_gdf.loc[idx, 'fosforo'],
                    potassium=result_gdf.loc[idx, 'potasio'],
                    ndvi=result_gdf.loc[idx, 'ndvi'],
                    organic_matter=result_gdf.loc[idx, 'materia_organica'],
                    ph=result_gdf.loc[idx, 'ph']
                )
                
                result_gdf.loc[idx, 'recomendacion_n'] = recommendations['nitrogen']['recommendation']
                result_gdf.loc[idx, 'recomendacion_p'] = recommendations['phosphorus']['recommendation']
                result_gdf.loc[idx, 'recomendacion_k'] = recommendations['potassium']['recommendation']
            
            return result_gdf
            
        except Exception as e:
            logger.error(f"Error en análisis de zonas: {e}")
            raise
