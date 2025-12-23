# app/core/soil.py
"""
Módulo para análisis de textura y propiedades físicas del suelo.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SoilTexture:
    """Estructura para propiedades de textura del suelo."""
    sand: float  # Arena %
    silt: float  # Limo %
    clay: float  # Arcilla %
    texture_class: str  # Clase textural
    bulk_density: float  # Densidad aparente g/cm³
    porosity: float  # Porosidad %
    field_capacity: float  # Capacidad de campo %
    wilting_point: float  # Punto de marchitez %
    available_water: float  # Agua disponible %
    hydraulic_conductivity: float  # Conductividad hidráulica cm/día

class SoilTextureAnalyzer:
    """Analizador de textura y propiedades físicas del suelo."""
    
    # Parámetros óptimos por cultivo
    OPTIMAL_TEXTURE = {
        'PALMA_ACEITERA': {
            'sand': 40,
            'silt': 30,
            'clay': 30,
            'texture_class': 'Franco Arcilloso',
            'bulk_density': 1.3,
            'porosity': 0.5
        },
        'CACAO': {
            'sand': 45,
            'silt': 35,
            'clay': 20,
            'texture_class': 'Franco',
            'bulk_density': 1.2,
            'porosity': 0.55
        },
        'BANANO': {
            'sand': 50,
            'silt': 30,
            'clay': 20,
            'texture_class': 'Franco Arcilloso-Arenoso',
            'bulk_density': 1.25,
            'porosity': 0.52
        }
    }
    
    # Textura base para propiedades físicas
    TEXTURE_PROPERTIES = {
        'Arcilloso': {
            'field_capacity': 350,
            'wilting_point': 200,
            'bulk_density': 1.3,
            'porosity': 0.5,
            'hydraulic_conductivity': 0.1
        },
        'Franco Arcilloso': {
            'field_capacity': 300,
            'wilting_point': 150,
            'bulk_density': 1.25,
            'porosity': 0.53,
            'hydraulic_conductivity': 0.5
        },
        'Franco': {
            'field_capacity': 250,
            'wilting_point': 100,
            'bulk_density': 1.2,
            'porosity': 0.55,
            'hydraulic_conductivity': 1.5
        },
        'Franco Arcilloso-Arenoso': {
            'field_capacity': 180,
            'wilting_point': 80,
            'bulk_density': 1.35,
            'porosity': 0.49,
            'hydraulic_conductivity': 5.0
        },
        'Arenoso': {
            'field_capacity': 120,
            'wilting_point': 50,
            'bulk_density': 1.5,
            'porosity': 0.43,
            'hydraulic_conductivity': 15.0
        }
    }
    
    # Recomendaciones por textura
    TEXTURE_RECOMMENDATIONS = {
        'Arcilloso': [
            "Añadir materia orgánica para mejorar estructura",
            "Evitar laboreo en condiciones húmedas",
            "Implementar drenajes superficiales",
            "Usar cultivos de cobertura para romper compactación"
        ],
        'Franco Arcilloso': [
            "Mantener niveles adecuados de materia orgánica",
            "Rotación de cultivos para mantener estructura",
            "Laboreo mínimo conservacionista",
            "Aplicación moderada de enmiendas"
        ],
        'Franco': [
            "Textura ideal - mantener prácticas conservacionistas",
            "Rotación balanceada de cultivos",
            "Manejo integrado de nutrientes",
            "Conservar estructura con coberturas"
        ],
        'Franco Arcilloso-Arenoso': [
            "Aplicación frecuente de materia orgánica",
            "Riego por goteo para eficiencia hídrica",
            "Fertilización fraccionada para reducir pérdidas",
            "Cultivos de cobertura para retener humedad"
        ],
        'Arenoso': [
            "Altas dosis de materia orgánica y compost",
            "Sistema de riego por goteo con alta frecuencia",
            "Fertilización en múltiples aplicaciones",
            "Barreras vivas para reducir erosión"
        ]
    }
    
    def __init__(self, crop_type: str):
        """
        Inicializar analizador de textura.
        
        Args:
            crop_type: Tipo de cultivo
        """
        self.crop_type = crop_type
        self.optimal_params = self.OPTIMAL_TEXTURE.get(crop_type, self.OPTIMAL_TEXTURE['PALMA_ACEITERA'])
    
    def classify_texture(self, sand: float, silt: float, clay: float) -> str:
        """
        Clasificar textura del suelo usando triángulo textural.
        
        Args:
            sand: Porcentaje de arena
            silt: Porcentaje de limo
            clay: Porcentaje de arcilla
            
        Returns:
            Clase textural
        """
        try:
            # Normalizar a 100%
            total = sand + silt + clay
            if total == 0:
                return "NO_DETERMINADA"
            
            sand_norm = (sand / total) * 100
            silt_norm = (silt / total) * 100
            clay_norm = (clay / total) * 100
            
            # Clasificación basada en USDA
            if clay_norm >= 40:
                return "Arcilloso"
            elif clay_norm >= 27 and silt_norm >= 15 and silt_norm <= 53 and sand_norm >= 20 and sand_norm <= 45:
                return "Franco Arcilloso"
            elif clay_norm >= 7 and clay_norm <= 27 and silt_norm >= 28 and silt_norm <= 50 and sand_norm >= 43 and sand_norm <= 52:
                return "Franco"
            elif sand_norm >= 70 and sand_norm <= 85 and clay_norm <= 20:
                return "Franco Arcilloso-Arenoso"
            elif sand_norm >= 85:
                return "Arenoso"
            else:
                return "Franco"
                
        except Exception as e:
            logger.error(f"Error clasificando textura: {e}")
            return "NO_DETERMINADA"
    
    def calculate_physical_properties(
        self,
        texture_class: str,
        organic_matter: float = 3.0
    ) -> Dict[str, float]:
        """
        Calcular propiedades físicas del suelo basado en textura.
        
        Args:
            texture_class: Clase textural
            organic_matter: Contenido de materia orgánica (%)
            
        Returns:
            Propiedades físicas calculadas
        """
        if texture_class not in self.TEXTURE_PROPERTIES:
            texture_class = "Franco"
        
        base_props = self.TEXTURE_PROPERTIES[texture_class]
        
        # Ajustar con materia orgánica
        om_factor = 1.0 + (organic_matter * 0.05)
        
        field_capacity = base_props['field_capacity'] * om_factor
        wilting_point = base_props['wilting_point'] * om_factor
        available_water = field_capacity - wilting_point
        bulk_density = base_props['bulk_density'] / om_factor
        porosity = min(0.65, base_props['porosity'] * om_factor)
        hydraulic_conductivity = base_props['hydraulic_conductivity'] * om_factor
        
        return {
            'field_capacity': float(field_capacity),
            'wilting_point': float(wilting_point),
            'available_water': float(available_water),
            'bulk_density': float(bulk_density),
            'porosity': float(porosity),
            'hydraulic_conductivity': float(hydraulic_conductivity)
        }
    
    def evaluate_texture_suitability(
        self,
        current_texture: str
    ) -> Tuple[str, float]:
        """
        Evaluar adecuación de textura para el cultivo.
        
        Args:
            current_texture: Textura actual del suelo
            
        Returns:
            (categoría_adecuación, puntaje_adecuación)
        """
        optimal_texture = self.optimal_params['texture_class']
        
        # Jerarquía de texturas (de más arenoso a más arcilloso)
        texture_hierarchy = {
            'Arenoso': 1,
            'Franco Arcilloso-Arenoso': 2,
            'Franco': 3,
            'Franco Arcilloso': 4,
            'Arcilloso': 5
        }
        
        if current_texture not in texture_hierarchy:
            return "NO_DETERMINADA", 0
        
        current_idx = texture_hierarchy[current_texture]
        optimal_idx = texture_hierarchy.get(optimal_texture, 3)
        
        difference = abs(current_idx - optimal_idx)
        
        if difference == 0:
            return "ÓPTIMA", 1.0
        elif difference == 1:
            return "ADECUADA", 0.8
        elif difference == 2:
            return "MODERADA", 0.6
        elif difference == 3:
            return "LIMITANTE", 0.4
        else:
            return "MUY LIMITANTE", 0.2
    
    def generate_texture_recommendations(
        self,
        current_texture: str,
        suitability_score: float
    ) -> List[str]:
        """
        Generar recomendaciones basadas en textura y adecuación.
        
        Args:
            current_texture: Textura actual
            suitability_score: Puntaje de adecuación
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        # Recomendaciones específicas por textura
        if current_texture in self.TEXTURE_RECOMMENDATIONS:
            recommendations.extend(self.TEXTURE_RECOMMENDATIONS[current_texture])
        
        # Recomendaciones basadas en adecuación
        if suitability_score < 0.4:
            recommendations.append("⚠️ CONSIDERAR CAMBIO DE CULTIVO: La textura es muy limitante")
        elif suitability_score < 0.6:
            recommendations.append("📋 REALIZAR ENMIENDAS: Mejorar propiedades físicas del suelo")
        elif suitability_score < 0.8:
            recommendations.append("🔍 MONITOREAR: La textura es aceptable pero requiere atención")
        else:
            recommendations.append("✅ ÓPTIMO: Mantener prácticas actuales de manejo")
        
        return recommendations
    
    def analyze_soil_sample(
        self,
        sand: float,
        silt: float,
        clay: float,
        organic_matter: float = 3.0
    ) -> SoilTexture:
        """
        Análisis completo de muestra de suelo.
        
        Returns:
            Objeto SoilTexture con todas las propiedades
        """
        # Clasificar textura
        texture_class = self.classify_texture(sand, silt, clay)
        
        # Calcular propiedades físicas
        physical_props = self.calculate_physical_properties(texture_class, organic_matter)
        
        # Evaluar adecuación
        suitability_category, suitability_score = self.evaluate_texture_suitability(texture_class)
        
        # Generar recomendaciones
        recommendations = self.generate_texture_recommendations(texture_class, suitability_score)
        
        return SoilTexture(
            sand=float(sand),
            silt=float(silt),
            clay=float(clay),
            texture_class=texture_class,
            bulk_density=physical_props['bulk_density'],
            porosity=physical_props['porosity'],
            field_capacity=physical_props['field_capacity'],
            wilting_point=physical_props['wilting_point'],
            available_water=physical_props['available_water'],
            hydraulic_conductivity=physical_props['hydraulic_conductivity'],
            # Campos adicionales
            suitability_category=suitability_category,
            suitability_score=float(suitability_score),
            recommendations=recommendations
        )
