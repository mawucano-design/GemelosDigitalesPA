# app/core/climate.py
import requests
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class ClimateData:
    """Estructura para datos climáticos."""
    solar_radiation: float  # MJ/m²/día
    precipitation: float    # mm/día
    temperature: float      # °C
    wind_speed: float       # m/s
    humidity: float         # %
    eto: float             # mm/día (evapotranspiración)
    
class ClimateAnalyzer:
    """Analizador de datos climáticos de NASA POWER."""
    
    NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializar analizador climático.
        
        Args:
            api_key: Clave API de NASA POWER (opcional)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.timeout = 30
        
    def get_current_climate(
        self,
        lat: float,
        lon: float,
        month: str
    ) -> ClimateData:
        """
        Obtener datos climáticos actuales para un mes específico.
        
        Args:
            lat: Latitud
            lon: Longitud
            month: Mes (ENERO, FEBRERO, etc.)
            
        Returns:
            Datos climáticos promediados para el mes
        """
        try:
            # Convertir mes a número
            month_num = self._month_to_number(month)
            current_year = datetime.now().year
            
            # Crear rango de fechas para el mes
            start_date = f"{current_year}{month_num:02d}01"
            if month_num == 12:
                end_date = f"{current_year + 1}0101"
            else:
                end_date = f"{current_year}{month_num + 1:02d}01"
            
            # Parámetros de la API
            params = {
                "parameters": "ALLSKY_SFC_SW_DWN,PRECTOTCORR,T2M,WS10M,RH2M,ETO",
                "community": "ag",
                "longitude": lon,
                "latitude": lat,
                "start": start_date,
                "end": end_date,
                "format": "json"
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
            
            # Hacer petición
            response = self.session.get(self.NASA_POWER_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Procesar datos
            parameters = data['properties']['parameter']
            
            # Calcular promedios
            solar_rad = np.mean(list(parameters['ALLSKY_SFC_SW_DWN'].values()))
            precip = np.mean(list(parameters['PRECTOTCORR'].values()))
            temp = np.mean(list(parameters['T2M'].values()))
            wind = np.mean(list(parameters['WS10M'].values()))
            humidity = np.mean(list(parameters['RH2M'].values()))
            eto = np.mean(list(parameters['ETO'].values()))
            
            return ClimateData(
                solar_radiation=float(solar_rad),
                precipitation=float(precip),
                temperature=float(temp),
                wind_speed=float(wind),
                humidity=float(humidity),
                eto=float(eto)
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo datos climáticos: {e}")
            # Retornar valores por defecto
            return self._get_default_climate_data()
    
    def get_historical_climate(
        self,
        lat: float,
        lon: float,
        years: int = 10
    ) -> Dict[str, List[float]]:
        """
        Obtener datos climáticos históricos.
        
        Args:
            lat: Latitud
            lon: Longitud
            years: Número de años hacia atrás
            
        Returns:
            Diccionario con datos mensuales promediados
        """
        try:
            current_year = datetime.now().year
            historical_data = {
                'solar_radiation': [[] for _ in range(12)],
                'precipitation': [[] for _ in range(12)],
                'temperature': [[] for _ in range(12)],
                'wind_speed': [[] for _ in range(12)],
                'humidity': [[] for _ in range(12)],
                'eto': [[] for _ in range(12)]
            }
            
            # Recorrer años
            for year in range(current_year - years, current_year):
                for month in range(1, 13):
                    try:
                        month_data = self._get_monthly_data(lat, lon, year, month)
                        
                        # Agregar a listas por mes
                        idx = month - 1
                        historical_data['solar_radiation'][idx].append(month_data.solar_radiation)
                        historical_data['precipitation'][idx].append(month_data.precipitation)
                        historical_data['temperature'][idx].append(month_data.temperature)
                        historical_data['wind_speed'][idx].append(month_data.wind_speed)
                        historical_data['humidity'][idx].append(month_data.humidity)
                        historical_data['eto'][idx].append(month_data.eto)
                        
                    except Exception as e:
                        logger.warning(f"Error mes {month}/{year}: {e}")
                        continue
            
            # Calcular promedios por mes
            result = {}
            for key in historical_data:
                monthly_averages = []
                for month_data in historical_data[key]:
                    if month_data:
                        monthly_averages.append(float(np.mean(month_data)))
                    else:
                        monthly_averages.append(0.0)
                result[key] = monthly_averages
            
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos: {e}")
            return self._get_default_historical_data()
    
    async def get_climate_async(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str
    ) -> Optional[ClimateData]:
        """
        Obtener datos climáticos de forma asíncrona.
        
        Args:
            lat: Latitud
            lon: Longitud
            start_date: Fecha inicio (YYYYMMDD)
            end_date: Fecha fin (YYYYMMDD)
            
        Returns:
            Datos climáticos o None
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "parameters": "ALLSKY_SFC_SW_DWN,PRECTOTCORR,T2M,WS10M,RH2M,ETO",
                    "community": "ag",
                    "longitude": lon,
                    "latitude": lat,
                    "start": start_date,
                    "end": end_date,
                    "format": "json"
                }
                
                async with session.get(self.NASA_POWER_BASE_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_climate_data(data)
        
        except Exception as e:
            logger.error(f"Error async obteniendo clima: {e}")
            return None
    
    def calculate_climate_indicators(
        self,
        climate_data: ClimateData,
        crop_type: str
    ) -> Dict[str, str]:
        """
        Calcular indicadores climáticos para cultivo específico.
        
        Returns:
            Indicadores y recomendaciones
        """
        indicators = {}
        
        # Indicador de radiación solar
        if climate_data.solar_radiation < 12:
            indicators['solar_radiation'] = {
                'status': 'BAJA',
                'description': 'Radiación insuficiente para crecimiento óptimo',
                'recommendation': 'Considerar cultivos de sombra o adaptados'
            }
        elif climate_data.solar_radiation > 22:
            indicators['solar_radiation'] = {
                'status': 'ALTA',
                'description': 'Radiación excesiva puede causar estrés',
                'recommendation': 'Implementar sombreado o riego adicional'
            }
        else:
            indicators['solar_radiation'] = {
                'status': 'ÓPTIMA',
                'description': 'Radiación adecuada para el cultivo',
                'recommendation': 'Mantener prácticas actuales'
            }
        
        # Indicador de precipitación
        monthly_precip = climate_data.precipitation * 30
        
        if crop_type == 'PALMA_ACEITERA':
            if monthly_precip < 100:
                precip_status = 'BAJA'
            elif monthly_precip > 300:
                precip_status = 'ALTA'
            else:
                precip_status = 'ÓPTIMA'
        else:
            if monthly_precip < 80:
                precip_status = 'BAJA'
            elif monthly_precip > 250:
                precip_status = 'ALTA'
            else:
                precip_status = 'ÓPTIMA'
        
        indicators['precipitation'] = {
            'status': precip_status,
            'value': f"{monthly_precip:.0f} mm/mes",
            'recommendation': self._get_precipitation_recommendation(precip_status, crop_type)
        }
        
        # Indicador de temperatura
        if climate_data.temperature < 18:
            temp_status = 'BAJA'
        elif climate_data.temperature > 32:
            temp_status = 'ALTA'
        else:
            temp_status = 'ÓPTIMA'
        
        indicators['temperature'] = {
            'status': temp_status,
            'value': f"{climate_data.temperature:.1f}°C",
            'recommendation': self._get_temperature_recommendation(temp_status)
        }
        
        # Balance hídrico (Precipitación - ETO)
        water_balance = climate_data.precipitation - climate_data.eto
        if water_balance < -2:
            water_status = 'DÉFICIT'
        elif water_balance > 2:
            water_status = 'EXCESO'
        else:
            water_status = 'BALANCEADO'
        
        indicators['water_balance'] = {
            'status': water_status,
            'value': f"{water_balance:.1f} mm/día",
            'recommendation': self._get_water_recommendation(water_status)
        }
        
        return indicators
    
    def _get_monthly_data(
        self,
        lat: float,
        lon: float,
        year: int,
        month: int
    ) -> ClimateData:
        """Obtener datos para un mes específico."""
        start_date = f"{year}{month:02d}01"
        if month == 12:
            end_date = f"{year + 1}0101"
        else:
            end_date = f"{year}{month + 1:02d}01"
        
        return self.get_current_climate(lat, lon, self._number_to_month(month))
    
    def _parse_climate_data(self, data: Dict) -> ClimateData:
        """Parsear respuesta de la API."""
        params = data['properties']['parameter']
        
        return ClimateData(
            solar_radiation=float(np.mean(list(params['ALLSKY_SFC_SW_DWN'].values()))),
            precipitation=float(np.mean(list(params['PRECTOTCORR'].values()))),
            temperature=float(np.mean(list(params['T2M'].values()))),
            wind_speed=float(np.mean(list(params['WS10M'].values()))),
            humidity=float(np.mean(list(params['RH2M'].values()))),
            eto=float(np.mean(list(params['ETO'].values())))
        )
    
    def _month_to_number(self, month: str) -> int:
        """Convertir nombre de mes a número."""
        months = {
            "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4,
            "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8,
            "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
        }
        return months.get(month.upper(), 1)
    
    def _number_to_month(self, number: int) -> str:
        """Convertir número a nombre de mes."""
        months = [
            "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
            "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
        ]
        return months[number - 1] if 1 <= number <= 12 else "ENERO"
    
    def _get_default_climate_data(self) -> ClimateData:
        """Obtener datos climáticos por defecto."""
        return ClimateData(
            solar_radiation=16.0,
            precipitation=6.0,
            temperature=25.0,
            wind_speed=2.5,
            humidity=70.0,
            eto=4.0
        )
    
    def _get_default_historical_data(self) -> Dict[str, List[float]]:
        """Obtener datos históricos por defecto."""
        default_monthly = [16.0] * 12  # Valores constantes por mes
        return {
            'solar_radiation': default_monthly.copy(),
            'precipitation': default_monthly.copy(),
            'temperature': default_monthly.copy(),
            'wind_speed': default_monthly.copy(),
            'humidity': default_monthly.copy(),
            'eto': default_monthly.copy()
        }
    
    def _get_precipitation_recommendation(self, status: str, crop_type: str) -> str:
        """Obtener recomendación basada en precipitación."""
        recommendations = {
            'BAJA': {
                'PALMA_ACEITERA': 'Implementar riego suplementario, uso de mulch',
                'CACAO': 'Riego por goteo, sombreado para reducir evaporación',
                'BANANO': 'Riego frecuente, cubiertas vegetales'
            },
            'ALTA': {
                'PALMA_ACEITERA': 'Mejorar drenaje, control de enfermedades fúngicas',
                'CACAO': 'Drenaje adecuado, poda para mejorar circulación de aire',
                'BANANO': 'Canales de drenaje, manejo integrado de plagas'
            },
            'ÓPTIMA': 'Mantener prácticas actuales, monitorear regularmente'
        }
        
        if status == 'ÓPTIMA':
            return recommendations[status]
        
        return recommendations[status].get(crop_type, 'Ajustar prácticas de manejo')
    
    def _get_temperature_recommendation(self, status: str) -> str:
        """Obtener recomendación basada en temperatura."""
        return {
            'BAJA': 'Usar cubiertas, seleccionar variedades tolerantes al frío',
            'ALTA': 'Implementar sombreado, riego en horas frescas',
            'ÓPTIMA': 'Condiciones ideales para crecimiento'
        }.get(status, 'Monitorear condiciones')
    
    def _get_water_recommendation(self, status: str) -> str:
        """Obtener recomendación basada en balance hídrico."""
        return {
            'DÉFICIT': 'Aumentar riego, reducir densidad de siembra',
            'EXCESO': 'Mejorar drenaje, evitar laboreo en suelo húmedo',
            'BALANCEADO': 'Condiciones óptimas de humedad'
        }.get(status, 'Ajustar manejo hídrico según necesidad')
