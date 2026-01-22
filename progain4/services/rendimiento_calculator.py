"""
RendimientoCalculator - Cálculo de métricas de rendimiento de obra

Calcula: 
- Rendimiento financiero (físico vs gastado)
- Rendimiento temporal (físico vs tiempo)
- Rendimiento global
- Proyecciones
"""

from datetime import date, datetime
from typing import Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class RendimientoCalculator:
    """Calculador de métricas de rendimiento de proyectos de construcción"""
    
    @staticmethod
    def calcular_rendimiento_completo(
        avance_fisico: float,
        presupuesto_total: float,
        gastado_total: float,
        fecha_inicio: date,
        duracion_meses: int,
        fecha_actual: Optional[date] = None
    ) -> Dict[str, Any]: 
        """
        Calcular todas las métricas de rendimiento. 
        
        Args:
            avance_fisico:  Avance físico en % (0-100)
            presupuesto_total: Presupuesto total del proyecto
            gastado_total:  Monto gastado hasta ahora
            fecha_inicio:  Fecha de inicio real de la obra
            duracion_meses: Duración estimada en meses
            fecha_actual: Fecha actual (default: hoy)
        
        Returns:
            Dict con todas las métricas calculadas
        """
        if fecha_actual is None:
            fecha_actual = date.today()
        
        # === CÁLCULOS BÁSICOS ===
        
        # Avance financiero (% del presupuesto gastado)
        avance_financiero = (gastado_total / presupuesto_total * 100) if presupuesto_total > 0 else 0
        
        # Tiempo transcurrido
        dias_transcurridos = (fecha_actual - fecha_inicio).days
        meses_transcurridos = dias_transcurridos / 30.44
        porcentaje_tiempo = (meses_transcurridos / duracion_meses * 100) if duracion_meses > 0 else 0
        
        # === RENDIMIENTOS ===
        
        # 1. Rendimiento Financiero
        # Compara avance físico vs avance financiero
        # > 100% = Eficiente (más avance que gasto)
        # < 100% = Ineficiente (más gasto que avance)
        rendimiento_financiero = (avance_fisico / avance_financiero * 100) if avance_financiero > 0 else 0
        
        # 2. Rendimiento Temporal
        # Compara avance físico vs tiempo transcurrido
        # > 100% = Adelantado
        # < 100% = Atrasado
        rendimiento_temporal = (avance_fisico / porcentaje_tiempo * 100) if porcentaje_tiempo > 0 else 0
        
        # 3. Rendimiento Global
        # Promedio ponderado:  60% financiero, 40% temporal
        if rendimiento_financiero > 0 and rendimiento_temporal > 0:
            rendimiento_global = (rendimiento_financiero * 0.6 + rendimiento_temporal * 0.4)
        elif rendimiento_financiero > 0:
            rendimiento_global = rendimiento_financiero * 0.6
        elif rendimiento_temporal > 0:
            rendimiento_global = rendimiento_temporal * 0.4
        else:
            rendimiento_global = 0
        
        # === DIFERENCIAS TEMPORALES ===
        
        # Meses esperados según el avance físico
        meses_esperados = (avance_fisico / 100) * duracion_meses
        diferencia_meses = meses_transcurridos - meses_esperados
        
        # === PROYECCIONES ===
        
        # Proyección de gasto final
        if avance_fisico > 0:
            proyeccion_gasto_final = (gastado_total / avance_fisico) * 100
            sobrecosto_estimado = proyeccion_gasto_final - presupuesto_total
            porcentaje_sobrecosto = (sobrecosto_estimado / presupuesto_total * 100) if presupuesto_total > 0 else 0
        else:
            proyeccion_gasto_final = presupuesto_total
            sobrecosto_estimado = 0
            porcentaje_sobrecosto = 0
        
        # Proyección de fecha de finalización
        if avance_fisico > 0:
            meses_proyectados_totales = (meses_transcurridos / avance_fisico) * 100
            retraso_estimado_meses = meses_proyectados_totales - duracion_meses
        else:
            meses_proyectados_totales = duracion_meses
            retraso_estimado_meses = 0
        
        # === ESTADOS ===
        
        estado_financiero = RendimientoCalculator._get_estado_rendimiento(rendimiento_financiero)
        estado_temporal = RendimientoCalculator._get_estado_rendimiento(rendimiento_temporal)
        estado_global = RendimientoCalculator._get_estado_rendimiento(rendimiento_global)
        
        # === RETORNAR RESULTADOS ===
        
        return {
            # Avances
            'avance_fisico': round(avance_fisico, 2),
            'avance_financiero': round(avance_financiero, 2),
            'porcentaje_tiempo': round(porcentaje_tiempo, 2),
            
            # Rendimientos
            'rendimiento_financiero': round(rendimiento_financiero, 2),
            'rendimiento_temporal': round(rendimiento_temporal, 2),
            'rendimiento_global': round(rendimiento_global, 2),
            
            # Estados
            'estado_financiero':  estado_financiero,
            'estado_temporal': estado_temporal,
            'estado_global': estado_global,
            
            # Datos temporales
            'dias_transcurridos': dias_transcurridos,
            'meses_transcurridos': round(meses_transcurridos, 1),
            'meses_transcurridos_int': round(meses_transcurridos),
            'duracion_total_meses': duracion_meses,
            'meses_esperados': round(meses_esperados, 1),
            'diferencia_meses': round(diferencia_meses, 1),
            'diferencia_meses_int': round(diferencia_meses),
            
            # Proyecciones
            'presupuesto_total': presupuesto_total,
            'gastado_total': gastado_total,
            'saldo_disponible': presupuesto_total - gastado_total,
            'proyeccion_gasto_final': proyeccion_gasto_final,
            'sobrecosto_estimado': sobrecosto_estimado,
            'porcentaje_sobrecosto': round(porcentaje_sobrecosto, 2),
            'meses_proyectados_totales': round(meses_proyectados_totales, 1),
            'retraso_estimado_meses': round(retraso_estimado_meses, 1),
        }
    
    @staticmethod
    def _get_estado_rendimiento(rendimiento: float) -> Dict[str, Any]:
        """
        Determinar estado según valor de rendimiento. 
        
        Returns:
            Dict con:  nivel, emoji, color, descripcion
        """
        if rendimiento >= 110:
            return {
                'nivel': 'excelente',
                'emoji':  '🟢',
                'color': '#16A34A',  # green_600
                'descripcion': 'Excelente'
            }
        elif rendimiento >= 100:
            return {
                'nivel': 'bueno',
                'emoji': '🟢',
                'color': '#16A34A',
                'descripcion': 'Bueno'
            }
        elif rendimiento >= 90:
            return {
                'nivel':  'aceptable',
                'emoji': '🟡',
                'color': '#CA8A04',  # yellow_600
                'descripcion':  'Aceptable'
            }
        elif rendimiento >= 75:
            return {
                'nivel': 'regular',
                'emoji': '🟡',
                'color': '#CA8A04',
                'descripcion': 'Regular'
            }
        else:
            return {
                'nivel': 'critico',
                'emoji': '🔴',
                'color': '#DC2626',  # red_600
                'descripcion': 'Crítico'
            }
    
    @staticmethod
    def get_mensaje_rendimiento_financiero(rendimiento: float, avance_fisico: float, avance_financiero: float) -> str:
        """Generar mensaje descriptivo del rendimiento financiero"""
        if avance_financiero == 0:
            return "Sin gastos registrados"
        
        if rendimiento > 100:
            diferencia = avance_fisico - avance_financiero
            return f"Eficiente: {diferencia:.1f}% más de avance que de gasto"
        elif rendimiento == 100:
            return "Normal: Avance proporcional al gasto"
        else:
            diferencia = avance_financiero - avance_fisico
            return f"Ineficiente: {diferencia:.1f}% más de gasto que de avance"
    
    @staticmethod
    def get_mensaje_rendimiento_temporal(rendimiento: float, avance_fisico: float, porcentaje_tiempo: float) -> str:
        """Generar mensaje descriptivo del rendimiento temporal"""
        if porcentaje_tiempo == 0:
            return "Obra recién iniciada"
        
        if rendimiento > 100:
            diferencia = avance_fisico - porcentaje_tiempo
            return f"Adelantado:  {diferencia:.1f}% más de avance que de tiempo"
        elif rendimiento == 100:
            return "En tiempo:  Avance según cronograma"
        else: 
            diferencia = porcentaje_tiempo - avance_fisico
            return f"Atrasado: {diferencia:.1f}% menos de avance que de tiempo"