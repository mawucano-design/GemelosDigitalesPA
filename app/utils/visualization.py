# app/utils/visualization.py
"""
Utilidades para visualización de datos geoespaciales.
"""
import folium
from folium import plugins
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import io
import base64
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
import logging

logger = logging.getLogger(__name__)

class MapVisualizer:
    """Visualizador de mapas interactivos."""
    
    # Paletas de colores
    COLOR_PALETTES = {
        'fertility': ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850', '#006837'],
        'nitrogen': ['#8c510a', '#bf812d', '#dfc27d', '#f6e8c3', '#c7eae5', '#80cdc1', '#35978f', '#01665e'],
        'phosphorus': ['#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#d1e5f0', '#92c5de', '#4393c3', '#2166ac', '#053061'],
        'potassium': ['#4d004b', '#810f7c', '#8c6bb1', '#8c96c6', '#9ebcda', '#bfd3e6', '#e0ecf4', '#edf8fb'],
        'texture': ['#8c510a', '#d8b365', '#f6e8c3', '#c7eae5', '#5ab4ac', '#01665e'],
        'yield_potential': ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b'],
        'climate': ['#ffffcc', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494']
    }
    
    # Capas de mapas base
    BASE_LAYERS = {
        'Esri Satellite': {
            'tiles': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            'attr': 'Esri',
            'name': 'Esri Satellite'
        },
        'OpenStreetMap': {
            'tiles': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'attr': 'OpenStreetMap',
            'name': 'OpenStreetMap'
        },
        'Esri Street': {
            'tiles': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
            'attr': 'Esri',
            'name': 'Esri Streets'
        },
        'CartoDB Dark': {
            'tiles': 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
            'attr': 'CartoDB',
            'name': 'CartoDB Dark'
        }
    }
    
    def __init__(self, center_lat: float = 4.0, center_lon: float = -74.0, zoom: int = 6):
        """
        Inicializar visualizador.
        
        Args:
            center_lat: Latitud central
            center_lon: Longitud central
            zoom: Nivel de zoom inicial
        """
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.zoom = zoom
    
    def create_base_map(self, layer: str = 'Esri Satellite') -> folium.Map:
        """
        Crear mapa base con capa seleccionada.
        
        Args:
            layer: Nombre de la capa base
            
        Returns:
            Mapa Folium
        """
        layer_config = self.BASE_LAYERS.get(layer, self.BASE_LAYERS['Esri Satellite'])
        
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=self.zoom,
            tiles=layer_config['tiles'],
            attr=layer_config['attr'],
            name=layer_config['name'],
            control_scale=True
        )
        
        # Añadir otras capas base
        for name, config in self.BASE_LAYERS.items():
            if name != layer:
                folium.TileLayer(
                    tiles=config['tiles'],
                    attr=config['attr'],
                    name=config['name'],
                    overlay=False
                ).add_to(m)
        
        # Añadir control de capas
        folium.LayerControl().add_to(m)
        
        # Añadir minimapa
        minimap = plugins.MiniMap()
        m.add_child(minimap)
        
        # Añadir botón de pantalla completa
        plugins.Fullscreen().add_to(m)
        
        # Añadir medición
        plugins.MeasureControl(
            position='topleft',
            primary_length_unit='meters',
            secondary_length_unit='kilometers',
            primary_area_unit='sqmeters',
            secondary_area_unit='hectares'
        ).add_to(m)
        
        return m
    
    def add_parcel_layer(
        self,
        m: folium.Map,
        gdf: gpd.GeoDataFrame,
        layer_name: str = "Parcela",
        color: str = '#1f77b4',
        fill_opacity: float = 0.5
    ) -> folium.Map:
        """
        Añadir capa de parcela al mapa.
        
        Args:
            m: Mapa Folium
            gdf: GeoDataFrame con geometrías
            layer_name: Nombre de la capa
            color: Color de relleno
            fill_opacity: Opacidad del relleno
            
        Returns:
            Mapa actualizado
        """
        if gdf.empty:
            return m
        
        # Crear grupo de capa
        feature_group = folium.FeatureGroup(name=layer_name)
        
        for idx, row in gdf.iterrows():
            # Crear popup informativo
            popup_html = f"""
            <div style="font-family: Arial; font-size: 12px;">
                <b>{layer_name} {idx + 1}</b><br>
                <b>Área:</b> {row.get('area_ha', 0):.2f} ha<br>
                <b>ID Zona:</b> {row.get('id_zona', 'N/A')}<br>
            """
            
            # Añadir información adicional si existe
            if 'indice_fertilidad' in row:
                popup_html += f"<b>Fertilidad:</b> {row['indice_fertilidad']:.3f}<br>"
            if 'categoria' in row:
                popup_html += f"<b>Categoría:</b> {row['categoria']}<br>"
            
            popup_html += "</div>"
            
            # Añadir geometría
            folium.GeoJson(
                row.geometry.__geo_interface__,
                style_function=lambda x, color=color, fill_opacity=fill_opacity: {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 2,
                    'fillOpacity': fill_opacity,
                    'opacity': 0.8
                },
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{layer_name} {idx + 1}"
            ).add_to(feature_group)
        
        feature_group.add_to(m)
        return m
    
    def add_choropleth_layer(
        self,
        m: folium.Map,
        gdf: gpd.GeoDataFrame,
        column: str,
        layer_name: str,
        palette: str = 'fertility',
        legend_name: str = "Valor",
        bins: int = 7
    ) -> folium.Map:
        """
        Añadir capa coroplética al mapa.
        
        Args:
            m: Mapa Folium
            gdf: GeoDataFrame con datos
            column: Columna para colorear
            layer_name: Nombre de la capa
            palette: Nombre de la paleta de colores
            legend_name: Nombre para la leyenda
            bins: Número de intervalos
            
        Returns:
            Mapa actualizado
        """
        if gdf.empty or column not in gdf.columns:
            return m
        
        # Obtener paleta de colores
        colors = self.COLOR_PALETTES.get(palette, self.COLOR_PALETTES['fertility'])
        
        # Calcular rangos
        values = gdf[column].dropna()
        if len(values) == 0:
            return m
        
        vmin = values.min()
        vmax = values.max()
        
        # Crear capa coroplética
        choropleth = folium.Choropleth(
            geo_data=gdf.__geo_interface__,
            data=gdf,
            columns=['id_zona', column],
            key_on='feature.properties.id_zona',
            fill_color='YlOrRd' if palette == 'fertility' else 'Blues',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=legend_name,
            bins=bins,
            nan_fill_color='gray',
            name=layer_name,
            highlight=True
        ).add_to(m)
        
        # Añadir tooltips
        style_function = lambda x: {
            'fillColor': '#ffffff',
            'color': '#000000',
            'fillOpacity': 0.0,
            'weight': 0.0
        }
        
        highlight_function = lambda x: {
            'fillColor': '#000000',
            'color': '#000000',
            'fillOpacity': 0.50,
            'weight': 0.1
        }
        
        # Añadir información en hover
        for idx, row in gdf.iterrows():
            html = f"""
            <div style="font-family: Arial; font-size: 12px;">
                <b>Zona {row.get('id_zona', idx+1)}</b><br>
                <b>{legend_name}:</b> {row[column]:.3f}<br>
                <b>Área:</b> {row.get('area_ha', 0):.2f} ha<br>
            """
            
            if 'categoria' in row:
                html += f"<b>Categoría:</b> {row['categoria']}<br>"
            
            html += "</div>"
            
            iframe = folium.IFrame(html=html, width=200, height=100)
            popup = folium.Popup(iframe, max_width=300)
            
            folium.GeoJson(
                row.geometry.__geo_interface__,
                style_function=style_function,
                highlight_function=highlight_function,
                tooltip=folium.Tooltip(f"Zona {row.get('id_zona', idx+1)}: {row[column]:.3f}"),
                popup=popup
            ).add_to(choropleth.geojson)
        
        return m
    
    def add_heatmap_layer(
        self,
        m: folium.Map,
        points: List[Tuple[float, float, float]],
        layer_name: str = "Heatmap",
        radius: int = 15,
        blur: int = 10,
        max_zoom: int = 18
    ) -> folium.Map:
        """
        Añadir capa de heatmap al mapa.
        
        Args:
            m: Mapa Folium
            points: Lista de puntos (lat, lon, weight)
            layer_name: Nombre de la capa
            radius: Radio de los puntos
            blur: Nivel de desenfoque
            max_zoom: Zoom máximo
            
        Returns:
            Mapa actualizado
        """
        if not points:
            return m
        
        # Crear heatmap
        heat_data = [[point[0], point[1], point[2]] for point in points]
        
        plugins.HeatMap(
            heat_data,
            name=layer_name,
            min_opacity=0.3,
            max_zoom=max_zoom,
            radius=radius,
            blur=blur,
            gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red'}
        ).add_to(m)
        
        return m
    
    def add_marker_cluster(
        self,
        m: folium.Map,
        points: List[Dict[str, Any]],
        layer_name: str = "Puntos de Muestra"
    ) -> folium.Map:
        """
        Añadir cluster de marcadores al mapa.
        
        Args:
            m: Mapa Folium
            points: Lista de puntos con información
            layer_name: Nombre de la capa
            
        Returns:
            Mapa actualizado
        """
        if not points:
            return m
        
        # Crear cluster
        marker_cluster = plugins.MarkerCluster(name=layer_name)
        
        for point in points:
            lat = point.get('lat')
            lon = point.get('lon')
            
            if lat is None or lon is None:
                continue
            
            # Crear popup
            popup_html = "<div style='font-family: Arial; font-size: 12px;'>"
            popup_html += f"<b>Punto de Muestra</b><br>"
            
            for key, value in point.items():
                if key not in ['lat', 'lon']:
                    if isinstance(value, float):
                        popup_html += f"<b>{key}:</b> {value:.3f}<br>"
                    else:
                        popup_html += f"<b>{key}:</b> {value}<br>"
            
            popup_html += "</div>"
            
            # Crear marcador
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)
        
        marker_cluster.add_to(m)
        return m
    
    def create_static_map(
        self,
        gdf: gpd.GeoDataFrame,
        column: Optional[str] = None,
        title: str = "Mapa de Análisis",
        figsize: Tuple[int, int] = (12, 8),
        dpi: int = 100
    ) -> Optional[io.BytesIO]:
        """
        Crear mapa estático en formato imagen.
        
        Args:
            gdf: GeoDataFrame con datos
            column: Columna para colorear (opcional)
            title: Título del mapa
            figsize: Tamaño de la figura
            dpi: Resolución
            
        Returns:
            BytesIO con imagen PNG
        """
        try:
            fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
            
            if column and column in gdf.columns:
                # Mapa coroplético
                gdf.plot(
                    column=column,
                    ax=ax,
                    legend=True,
                    legend_kwds={
                        'label': column,
                        'orientation': "horizontal",
                        'shrink': 0.6
                    },
                    cmap='viridis',
                    edgecolor='black',
                    linewidth=0.5
                )
                
                # Añadir etiquetas de zona
                for idx, row in gdf.iterrows():
                    try:
                        centroid = row.geometry.centroid
                        zone_id = row.get('id_zona', idx + 1)
                        ax.annotate(
                            f"Z{zone_id}",
                            (centroid.x, centroid.y),
                            xytext=(3, 3),
                            textcoords="offset points",
                            fontsize=8,
                            weight='bold',
                            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8)
                        )
                    except:
                        pass
            else:
                # Mapa simple
                gdf.plot(
                    ax=ax,
                    color='lightblue',
                    edgecolor='black',
                    linewidth=1,
                    alpha=0.7
                )
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
            ax.set_xlabel("Longitud")
            ax.set_ylabel("Latitud")
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Guardar en buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            
            return buf
            
        except Exception as e:
            logger.error(f"Error creando mapa estático: {e}")
            return None
    
    def create_interactive_plotly_map(
        self,
        gdf: gpd.GeoDataFrame,
        color_column: str,
        title: str = "Mapa Interactivo"
    ) -> go.Figure:
        """
        Crear mapa interactivo con Plotly.
        
        Args:
            gdf: GeoDataFrame con datos
            color_column: Columna para colorear
            title: Título del mapa
            
        Returns:
            Figura de Plotly
        """
        try:
            # Convertir a GeoJSON
            geojson = gdf.__geo_interface__
            
            # Crear figura
            fig = px.choropleth_mapbox(
                gdf,
                geojson=geojson,
                locations='id_zona',
                color=color_column,
                hover_name='id_zona',
                hover_data={
                    'area_ha': ':.2f',
                    color_column: ':.3f',
                    'categoria': True
                } if 'categoria' in gdf.columns else {
                    'area_ha': ':.2f',
                    color_column: ':.3f'
                },
                mapbox_style="carto-positron",
                zoom=10,
                center={
                    "lat": gdf.geometry.centroid.y.mean(),
                    "lon": gdf.geometry.centroid.x.mean()
                },
                opacity=0.7,
                title=title,
                color_continuous_scale="Viridis"
            )
            
            fig.update_layout(
                margin={"r": 0, "t": 30, "l": 0, "b": 0},
                height=600
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creando mapa Plotly: {e}")
            # Retornar figura vacía
            fig = go.Figure()
            fig.update_layout(
                title="Error creando mapa",
                annotations=[dict(text=str(e), showarrow=False)]
            )
            return fig
    
    @staticmethod
    def create_fertility_chart(
        data: pd.DataFrame,
        x_column: str = 'id_zona',
        y_column: str = 'indice_fertilidad',
        title: str = "Índice de Fertilidad por Zona"
    ) -> go.Figure:
        """
        Crear gráfico de barras de fertilidad.
        
        Args:
            data: DataFrame con datos
            x_column: Columna para eje X
            y_column: Columna para eje Y
            title: Título del gráfico
            
        Returns:
            Figura de Plotly
        """
        fig = px.bar(
            data,
            x=x_column,
            y=y_column,
            title=title,
            color=y_column,
            color_continuous_scale="Viridis",
            hover_data=['categoria', 'area_ha'] if 'categoria' in data.columns else ['area_ha']
        )
        
        fig.update_layout(
            xaxis_title="Zona",
            yaxis_title="Índice de Fertilidad",
            yaxis_range=[0, 1],
            coloraxis_showscale=False
        )
        
        # Añadir línea de referencia en 0.5
        fig.add_hline(
            y=0.5,
            line_dash="dash",
            line_color="red",
            annotation_text="Límite Mínimo",
            annotation_position="bottom right"
        )
        
        return fig
    
    @staticmethod
    def create_climate_timeseries(
        historical_data: Dict[str, List[float]],
        title: str = "Datos Climáticos Históricos"
    ) -> go.Figure:
        """
        Crear gráfico de series temporales climáticas.
        
        Args:
            historical_data: Diccionario con datos históricos
            title: Título del gráfico
            
        Returns:
            Figura de Plotly
        """
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        fig = go.Figure()
        
        # Añadir cada variable climática
        colors = {'solar_radiation': 'orange', 'precipitation': 'blue', 
                 'temperature': 'red', 'humidity': 'green'}
        
        for var, color in colors.items():
            if var in historical_data:
                fig.add_trace(go.Scatter(
                    x=meses,
                    y=historical_data[var],
                    mode='lines+markers',
                    name=var.replace('_', ' ').title(),
                    line=dict(color=color, width=2),
                    marker=dict(size=8)
                ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Mes",
            yaxis_title="Valor",
            hovermode="x unified",
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def create_soil_texture_triangle(
        sand: float,
        silt: float,
        clay: float,
        title: str = "Triángulo Textural"
    ) -> go.Figure:
        """
        Crear triángulo textural interactivo.
        
        Args:
            sand: Porcentaje de arena
            silt: Porcentaje de limo
            clay: Porcentaje de arcilla
            title: Título del gráfico
            
        Returns:
            Figura de Plotly
        """
        # Crear figura de triángulo ternario
        fig = go.Figure(go.Scatterternary({
            'mode': 'markers',
            'a': [sand],
            'b': [silt],
            'c': [clay],
            'marker': {
                'size': 20,
                'color': '#FF5722',
                'symbol': 'circle'
            },
            'text': [f'Arena: {sand:.1f}%<br>Limo: {silt:.1f}%<br>Arcilla: {clay:.1f}%'],
            'hoverinfo': 'text',
            'name': 'Muestra'
        }))
        
        fig.update_layout({
            'title': title,
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
    
    @staticmethod
    def image_to_base64(image_buffer: io.BytesIO) -> str:
        """
        Convertir imagen a base64 para incrustar en HTML.
        
        Args:
            image_buffer: Buffer con imagen
            
        Returns:
            String base64
        """
        try:
            return base64.b64encode(image_buffer.getvalue()).decode()
        except:
            return ""
