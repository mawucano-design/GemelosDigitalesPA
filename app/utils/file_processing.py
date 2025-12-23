# app/utils/file_processing.py
"""
Utilidades para procesamiento de archivos geoespaciales.
"""
import geopandas as gpd
import pandas as pd
import numpy as np
import tempfile
import os
import zipfile
import shutil
from typing import Optional, Tuple, List
import logging
from shapely.geometry import Polygon, MultiPolygon
import fiona

logger = logging.getLogger(__name__)

class FileProcessor:
    """Procesador de archivos geoespaciales."""
    
    SUPPORTED_EXTENSIONS = ['.zip', '.kml', '.geojson', '.shp', '.gpkg']
    
    @staticmethod
    def process_uploaded_file(uploaded_file) -> Optional[gpd.GeoDataFrame]:
        """
        Procesar archivo subido por el usuario.
        
        Args:
            uploaded_file: Archivo subido a Streamlit
            
        Returns:
            GeoDataFrame procesado o None
        """
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                file_path = os.path.join(tmp_dir, uploaded_file.name)
                
                # Guardar archivo subido
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Procesar según extensión
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                
                if file_ext == '.kml':
                    gdf = gpd.read_file(file_path, driver='KML')
                elif file_ext == '.geojson':
                    gdf = gpd.read_file(file_path)
                elif file_ext == '.zip':
                    gdf = FileProcessor._process_zip_file(file_path, tmp_dir)
                elif file_ext == '.shp':
                    gdf = gpd.read_file(file_path)
                else:
                    logger.error(f"Formato no soportado: {file_ext}")
                    return None
                
                # Validar y limpiar geometrías
                if not gdf.empty:
                    gdf = FileProcessor._clean_geometries(gdf)
                    gdf = FileProcessor._ensure_crs(gdf)
                
                return gdf
                
        except Exception as e:
            logger.error(f"Error procesando archivo: {e}")
            return None
    
    @staticmethod
    def _process_zip_file(zip_path: str, tmp_dir: str) -> Optional[gpd.GeoDataFrame]:
        """Procesar archivo ZIP que contiene shapefile."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_dir)
            
            # Buscar archivos shapefile
            shp_files = [f for f in os.listdir(tmp_dir) if f.endswith('.shp')]
            if not shp_files:
                # Buscar KML
                kml_files = [f for f in os.listdir(tmp_dir) if f.endswith('.kml')]
                if kml_files:
                    return gpd.read_file(os.path.join(tmp_dir, kml_files[0]), driver='KML')
                return None
            
            # Leer el primer shapefile encontrado
            shp_path = os.path.join(tmp_dir, shp_files[0])
            return gpd.read_file(shp_path)
            
        except Exception as e:
            logger.error(f"Error procesando ZIP: {e}")
            return None
    
    @staticmethod
    def _clean_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Limpiar y validar geometrías."""
        if gdf.empty:
            return gdf
        
        # Hacer geometrías válidas
        gdf['geometry'] = gdf['geometry'].make_valid()
        
        # Remover geometrías nulas o vacías
        gdf = gdf[~gdf['geometry'].isna()]
        gdf = gdf[~gdf['geometry'].is_empty]
        
        # Simplificar si hay muchas geometrías
        if len(gdf) > 100:
            gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.0001)
        
        return gdf
    
    @staticmethod
    def _ensure_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Asegurar que el GeoDataFrame tenga CRS definido."""
        if gdf.crs is None:
            # Asumir WGS84 (EPSG:4326) si no hay CRS
            gdf.set_crs(epsg=4326, inplace=True)
        return gdf
    
    @staticmethod
    def calculate_area(gdf: gpd.GeoDataFrame) -> float:
        """
        Calcular área en hectáreas.
        
        Args:
            gdf: GeoDataFrame con geometrías
            
        Returns:
            Área total en hectáreas
        """
        try:
            if gdf.empty:
                return 0.0
            
            # Proyectar a CRS métrico para cálculo de área
            crs_options = ['EPSG:3857', 'EPSG:5367', 'EPSG:3116', 'EPSG:32718', 'EPSG:32719']
            
            for crs_code in crs_options:
                try:
                    gdf_proj = gdf.to_crs(crs_code)
                    area_m2 = gdf_proj.geometry.area.sum()
                    area_ha = area_m2 / 10000
                    return float(area_ha)
                except:
                    continue
            
            # Fallback: cálculo aproximado
            bounds = gdf.total_bounds
            if len(bounds) == 4:
                import math
                lat_rad = math.radians((bounds[1] + bounds[3]) / 2)
                m_per_degree_lat = 111319.9
                m_per_degree_lon = 111319.9 * math.cos(lat_rad)
                width_deg = bounds[2] - bounds[0]
                height_deg = bounds[3] - bounds[1]
                area_m2 = abs(width_deg * m_per_degree_lon * height_deg * m_per_degree_lat)
                return area_m2 / 10000
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculando área: {e}")
            return 0.0
    
    @staticmethod
    def divide_into_zones(
        gdf: gpd.GeoDataFrame,
        n_zones: int,
        min_area: float = 0.1
    ) -> gpd.GeoDataFrame:
        """
        Dividir parcela en zonas homogéneas.
        
        Args:
            gdf: GeoDataFrame de parcela
            n_zones: Número de zonas deseadas
            min_area: Área mínima por zona (hectáreas)
            
        Returns:
            GeoDataFrame con zonas divididas
        """
        try:
            if gdf.empty:
                return gdf
            
            # Unir todas las geometrías en una
            union_geom = gdf.unary_union
            
            if not union_geom.is_valid:
                union_geom = union_geom.buffer(0)
            
            # Obtener bounding box
            bounds = union_geom.bounds
            if len(bounds) != 4:
                return gdf
            
            minx, miny, maxx, maxy = bounds
            
            # Calcular número de filas y columnas
            n_cols = int(np.ceil(np.sqrt(n_zones)))
            n_rows = int(np.ceil(n_zones / n_cols))
            
            width = (maxx - minx) / n_cols
            height = (maxy - miny) / n_rows
            
            # Asegurar tamaño mínimo
            if width < 0.00001 or height < 0.00001:
                return gdf
            
            # Crear cuadrícula
            zones = []
            zone_id = 1
            
            for i in range(n_rows):
                for j in range(n_cols):
                    if zone_id > n_zones:
                        break
                    
                    cell_minx = minx + (j * width)
                    cell_maxx = minx + ((j + 1) * width)
                    cell_miny = miny + (i * height)
                    cell_maxy = miny + ((i + 1) * height)
                    
                    cell_poly = Polygon([
                        (cell_minx, cell_miny),
                        (cell_maxx, cell_miny),
                        (cell_maxx, cell_maxy),
                        (cell_minx, cell_maxy)
                    ])
                    
                    if cell_poly.is_valid:
                        intersection = union_geom.intersection(cell_poly)
                        
                        if not intersection.is_empty and intersection.area > 0:
                            # Manejar MultiPolygon
                            if intersection.geom_type == 'MultiPolygon':
                                for poly in intersection.geoms:
                                    if poly.area > 0:
                                        zones.append({
                                            'id_zona': zone_id,
                                            'geometry': poly
                                        })
                                        zone_id += 1
                            else:
                                zones.append({
                                    'id_zona': zone_id,
                                    'geometry': intersection
                                })
                                zone_id += 1
            
            if zones:
                zones_gdf = gpd.GeoDataFrame(zones, crs=gdf.crs)
                # Calcular área de cada zona
                zones_gdf['area_ha'] = zones_gdf.geometry.apply(
                    lambda g: FileProcessor.calculate_area(gpd.GeoDataFrame([g], columns=['geometry'], crs=zones_gdf.crs))
                )
                # Filtrar zonas muy pequeñas
                zones_gdf = zones_gdf[zones_gdf['area_ha'] >= min_area]
                return zones_gdf.reset_index(drop=True)
            
            return gdf
            
        except Exception as e:
            logger.error(f"Error dividiendo en zonas: {e}")
            return gdf
    
    @staticmethod
    def export_to_shapefile(gdf: gpd.GeoDataFrame, output_path: str) -> bool:
        """
        Exportar GeoDataFrame a shapefile.
        
        Args:
            gdf: GeoDataFrame a exportar
            output_path: Ruta de salida
            
        Returns:
            True si éxito, False si error
        """
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Exportar a shapefile
            gdf.to_file(output_path, driver='ESRI Shapefile')
            return True
            
        except Exception as e:
            logger.error(f"Error exportando shapefile: {e}")
            return False
    
    @staticmethod
    def export_to_geojson(gdf: gpd.GeoDataFrame) -> str:
        """
        Exportar GeoDataFrame a GeoJSON string.
        
        Args:
            gdf: GeoDataFrame a exportar
            
        Returns:
            String GeoJSON
        """
        try:
            return gdf.to_json()
        except Exception as e:
            logger.error(f"Error exportando GeoJSON: {e}")
            return '{"type": "FeatureCollection", "features": []}'
    
    @staticmethod
    def create_sample_data(geometry: Polygon, n_points: int = 10) -> gpd.GeoDataFrame:
        """
        Crear datos de muestra para análisis.
        
        Args:
            geometry: Polígono de referencia
            n_points: Número de puntos de muestra
            
        Returns:
            GeoDataFrame con puntos de muestra
        """
        try:
            bounds = geometry.bounds
            points = []
            
            for _ in range(n_points):
                # Generar punto aleatorio dentro del polígono
                point = None
                attempts = 0
                
                while point is None and attempts < 100:
                    x = np.random.uniform(bounds[0], bounds[2])
                    y = np.random.uniform(bounds[1], bounds[3])
                    candidate = Point(x, y)
                    
                    if geometry.contains(candidate):
                        point = candidate
                    
                    attempts += 1
                
                if point:
                    points.append({
                        'geometry': point,
                        'nitrogeno': np.random.normal(150, 30),
                        'fosforo': np.random.normal(60, 15),
                        'potasio': np.random.normal(200, 40),
                        'ndvi': np.random.uniform(0.4, 0.8)
                    })
            
            if points:
                return gpd.GeoDataFrame(points, crs='EPSG:4326')
            
            return gpd.GeoDataFrame(columns=['geometry'], crs='EPSG:4326')
            
        except Exception as e:
            logger.error(f"Error creando datos de muestra: {e}")
            return gpd.GeoDataFrame(columns=['geometry'], crs='EPSG:4326')
