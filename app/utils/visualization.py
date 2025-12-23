# app/utils/visualization.py
import folium
import matplotlib.pyplot as plt
import geopandas as gpd
from typing import Optional, Dict, Any
import io
from ..core.analysis import SoilAnalyzer

def crear_mapa_interactivo_esri(gdf: gpd.GeoDataFrame, titulo: str, columna_valor: Optional[str] = None, 
                                analisis_tipo: Optional[str] = None, nutriente: Optional[str] = None) -> Optional[folium.Map]:
    # Copiar función del original
    pass

def crear_mapa_visualizador_parcela(gdf: gpd.GeoDataFrame) -> Optional[folium.Map]:
    # Copiar función del original
    pass

def crear_mapa_estatico(gdf: gpd.GeoDataFrame, titulo: str, columna_valor: Optional[str] = None, 
                        analisis_tipo: Optional[str] = None, nutriente: Optional[str] = None) -> Optional[io.BytesIO]:
    # Copiar función del original
    pass

def crear_mapa_heatmap_climatico(gdf_centroid, datos_historicos, variable, titulo):
    # Copiar función del original
    pass
