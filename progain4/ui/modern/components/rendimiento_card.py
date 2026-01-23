"""
RendimientoCard - Card de métricas de rendimiento del proyecto

Muestra:  
- Rendimiento global
- Rendimiento financiero
- Rendimiento temporal
- Proyecciones
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .clean_card import CleanCard
from .. theme_config import COLORS, BORDER

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class RendimientoCard(QWidget):  # ← Cambiar de CleanCard a QWidget
    """
    Card que muestra las métricas de rendimiento del proyecto. 
    """
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)  # ← Llamar a QWidget
        
        # ✅ Aplicar estilo de card manualmente
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                border: 1px solid {COLORS['slate_200']};
                padding: 0px;
            }}
        """)
        
        self. metricas = None
        self._has_data = False
        self.setup_ui()
    
    def setup_ui(self):
        """Crear interfaz del card"""
        
        # ✅ Obtener el layout existente en lugar de crear uno nuevo
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
        
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # ...  resto del código ... 
        
        # === HEADER ===
        header_layout = QHBoxLayout()
        
        title = QLabel("⚡ Rendimiento del Proyecto")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Badge de estado global (se actualiza dinámicamente)
        self.global_badge = QLabel("--")
        self.global_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['slate_100']};
                color: {COLORS['slate_700']};
                padding: 6px 16px;
                border-radius:  16px;
                font-size:  12px;
                font-weight: 600;
            }}
        """)
        header_layout.addWidget(self. global_badge)
        
        layout.addLayout(header_layout)
        
        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {COLORS['slate_200']};")
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        
        # === RENDIMIENTO GLOBAL ===
        self.global_section = self._create_global_section()
        layout.addWidget(self. global_section)
        
        # === RENDIMIENTOS INDIVIDUALES ===
        rendimientos_layout = QHBoxLayout()
        rendimientos_layout.setSpacing(16)
        
        # Financiero
        self.financiero_section = self._create_rendimiento_section("financiero")
        rendimientos_layout.addWidget(self.financiero_section)
        
        # Temporal
        self.temporal_section = self._create_rendimiento_section("temporal")
        rendimientos_layout.addWidget(self.temporal_section)
        
        layout.addLayout(rendimientos_layout)
        
        # === INDICADORES CLAVE ===
        self.indicadores_section = self._create_indicadores_section()
        layout.addWidget(self.indicadores_section)
        
        # === PROYECCIONES ===
        self. proyecciones_section = self._create_proyecciones_section()
        layout.addWidget(self.proyecciones_section)
        
        layout.addStretch()
        
        # ✅ NO llamar _show_no_data() aquí
        # Solo se mostrará cuando realmente no haya datos (en update_metricas)
    
    def _create_global_section(self) -> QWidget:
        """Crear sección de rendimiento global"""
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label de rendimiento
        label_layout = QHBoxLayout()
        
        label = QLabel("🎯 Rendimiento Global:")
        label.setStyleSheet(f"color: {COLORS['slate_700']}; font-size: 13px; font-weight: 500;")
        label_layout. addWidget(label)
        
        label_layout.addStretch()
        
        self.global_value = QLabel("--")
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setWeight(QFont.Weight.Bold)
        self.global_value.setFont(value_font)
        self.global_value.setStyleSheet(f"color: {COLORS['slate_900']};")
        label_layout.addWidget(self.global_value)
        
        layout.addLayout(label_layout)
        
        # Barra de progreso
        self.global_bar = QProgressBar()
        self.global_bar.setFixedHeight(12)
        self.global_bar.setTextVisible(False)
        self.global_bar.setMinimum(0)
        self.global_bar.setMaximum(150)  # Hasta 150% para mostrar excelencia
        self.global_bar. setValue(0)
        self.global_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 6px;
                background-color:  {COLORS['slate_200']};
            }}
            QProgressBar::chunk {{
                border-radius: 6px;
                background-color: {COLORS['blue_500']};
            }}
        """)
        layout.addWidget(self.global_bar)
        
        # Mensaje descriptivo
        self.global_message = QLabel("--")
        self.global_message.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 12px; font-style: italic;")
        self.global_message.setWordWrap(True)
        layout.addWidget(self.global_message)
        
        return container
    
    def _create_rendimiento_section(self, tipo: str) -> QWidget:
        """Crear sección de rendimiento individual (financiero o temporal)"""
        
        container = CleanCard(padding=16)
        container.setMinimumWidth(200)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(8)
        
        # Título
        if tipo == "financiero":
            icon = "💰"
            title_text = "Financiero"
        else:
            icon = "⏱️"
            title_text = "Temporal"
        
        title = QLabel(f"{icon} {title_text}")
        title.setStyleSheet(f"color: {COLORS['slate_700']}; font-size: 12px; font-weight: 600;")
        layout.addWidget(title)
        
        # Valor
        value_label = QLabel("--")
        value_font = QFont()
        value_font. setPointSize(20)
        value_font.setWeight(QFont.Weight.Bold)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {COLORS['slate_900']};")
        layout.addWidget(value_label)
        
        # Emoji de estado
        estado_label = QLabel("--")
        estado_label.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 11px;")
        layout.addWidget(estado_label)
        
        # Mensaje
        mensaje_label = QLabel("--")
        mensaje_label.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 10px;")
        mensaje_label.setWordWrap(True)
        layout.addWidget(mensaje_label)
        
        # Guardar referencias
        if tipo == "financiero":
            self.financiero_value = value_label
            self. financiero_estado = estado_label
            self. financiero_mensaje = mensaje_label
        else:
            self. temporal_value = value_label
            self.temporal_estado = estado_label
            self.temporal_mensaje = mensaje_label
        
        return container
    
    def _create_indicadores_section(self) -> QWidget:
        """Crear sección de indicadores clave"""
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title = QLabel("📈 Indicadores Clave")
        title.setStyleSheet(f"color: {COLORS['slate_700']}; font-size: 13px; font-weight: 600;")
        layout.addWidget(title)
        
        # Grid de indicadores
        grid = QHBoxLayout()
        grid.setSpacing(12)
        
        # Avance Físico
        self.ind_fisico = self._create_indicador_item("Avance Físico", "--", COLORS['green_600'])
        grid.addWidget(self.ind_fisico)
        
        # Avance Financiero
        self.ind_financiero = self._create_indicador_item("Avance Financiero", "--", COLORS['blue_600'])
        grid.addWidget(self.ind_financiero)
        
        # Tiempo Transcurrido
        self.ind_tiempo = self._create_indicador_item("Tiempo Transcurrido", "--", COLORS['slate_600'])
        grid.addWidget(self.ind_tiempo)
        
        # Presupuesto Ejecutado
        self.ind_presupuesto = self._create_indicador_item("Presup. Ejecutado", "--", COLORS['slate_600'])
        grid.addWidget(self.ind_presupuesto)
        
        layout.addLayout(grid)
        
        return container
    
    def _create_indicador_item(self, label: str, value: str, color: str) -> QWidget:
        """Crear item individual de indicador"""
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 10px;")
        label_widget.setWordWrap(True)
        layout.addWidget(label_widget)
        
        value_widget = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(16)
        value_font.setWeight(QFont.Weight.Bold)
        value_widget.setFont(value_font)
        value_widget.setStyleSheet(f"color: {color};")
        
        # Guardar referencia al value_widget en el container
        container.value_label = value_widget
        
        layout.addWidget(value_widget)
        
        return container
    
    def _create_proyecciones_section(self) -> QWidget:
        """Crear sección de proyecciones"""
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title = QLabel("🔮 Proyecciones")
        title.setStyleSheet(f"color: {COLORS['slate_700']}; font-size: 13px; font-weight: 600;")
        layout.addWidget(title)
        
        # Proyección de gasto
        self.proy_gasto = QLabel("--")
        self.proy_gasto.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 12px;")
        self.proy_gasto.setWordWrap(True)
        layout.addWidget(self.proy_gasto)
        
        # Proyección de tiempo
        self.proy_tiempo = QLabel("--")
        self.proy_tiempo.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 12px;")
        self.proy_tiempo.setWordWrap(True)
        layout.addWidget(self.proy_tiempo)
        
        return container
    
    def _show_no_data(self):
        """Mostrar estado cuando no hay datos"""
        
        # ✅ Si ya hay datos válidos, NO sobrescribir
        if getattr(self, '_has_data', False):
            logger.info("   ⚠️ Ya hay datos válidos, no sobrescribir con '--'")
            return
        
        logger.info("   📋 Mostrando estado 'Sin datos'")
        
        self.global_badge.setText("Sin datos")
        self.global_value.setText("--")
        self.global_message. setText("No hay suficiente información para calcular el rendimiento")
        
        self. financiero_value.setText("--")
        self.financiero_estado.setText("--")
        self.financiero_mensaje.setText("--")
        
        self.temporal_value.setText("--")
        self.temporal_estado.setText("--")
        self.temporal_mensaje.setText("--")
        
        self.ind_fisico.value_label. setText("--")
        self.ind_financiero.value_label.setText("--")
        self.ind_tiempo.value_label.setText("--")
        self.ind_presupuesto. value_label.setText("--")
        
        self.proy_gasto.setText("--")
        self.proy_tiempo.setText("--")
    
    def update_metricas(self, metricas: Optional[Dict[str, Any]]):
        """
        Actualizar el card con nuevas métricas.
        
        Args:
            metricas:  Dict retornado por RendimientoCalculator. calcular_rendimiento_completo()
        """
        # ✅ DEBUG LOG - INICIO
        logger.info("=" * 80)
        logger.info("🔔 RendimientoCard. update_metricas() LLAMADO")
        logger.info(f"   Métricas recibidas: {metricas is not None}")
        
        # ✅ CORRECCIÓN CRÍTICA:  Verificar None explícitamente
        if metricas is None:
            logger. warning("   ⚠️ Métricas es None - mostrando estado vacío")
            self._has_data = False  # ✅ Marcar que NO hay datos
            self._show_no_data()
            return
        
        # ✅ SEGUNDA VALIDACIÓN: Verificar que tenga los campos requeridos
        required_fields = ['rendimiento_global', 'rendimiento_financiero', 'rendimiento_temporal',
                          'estado_global', 'estado_financiero', 'estado_temporal']
        
        if not all(field in metricas for field in required_fields):
            logger.warning(f"   ⚠️ Métricas incompletas - campos faltantes")
            logger.warning(f"   Campos recibidos: {list(metricas.keys())}")
            self._has_data = False  # ✅ Marcar que NO hay datos válidos
            self._show_no_data()
            return
        
        # ✅ LOG:  Datos recibidos (DESPUÉS de validar)
        logger.info(f"   ✅ Rendimiento Global: {metricas. get('rendimiento_global')}")
        logger.info(f"   ✅ Rendimiento Financiero: {metricas.get('rendimiento_financiero')}")
        logger.info(f"   ✅ Rendimiento Temporal: {metricas.get('rendimiento_temporal')}")
        logger.info(f"   ✅ Estado Global: {metricas.get('estado_global')}")
        
        try:
            self. metricas = metricas
            
            # === RENDIMIENTO GLOBAL ===
            logger.info("   📊 Actualizando Rendimiento Global...")
            rendimiento_global = metricas['rendimiento_global']
            estado_global = metricas['estado_global']
            
            self.global_value.setText(f"{rendimiento_global:.0f}%")
            self.global_bar.setValue(min(int(rendimiento_global), 150))
            logger.info(f"      - Valor: {rendimiento_global:.0f}%")
            logger.info(f"      - Estado: {estado_global['descripcion']}")
            
            # Actualizar color de la barra según rendimiento
            if rendimiento_global >= 100:
                bar_color = COLORS['green_600']
            elif rendimiento_global >= 90:
                bar_color = COLORS['yellow_600']
            else:
                bar_color = COLORS['red_600']
            
            self.global_bar. setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    border-radius: 6px;
                    background-color: {COLORS['slate_200']};
                }}
                QProgressBar:: chunk {{
                    border-radius: 6px;
                    background-color: {bar_color};
                }}
            """)
            
            # Badge global
            self.global_badge. setText(f"{estado_global['emoji']} {estado_global['descripcion']}")
            self.global_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {estado_global['color']}20;
                    color: {estado_global['color']};
                    padding: 6px 16px;
                    border-radius: 16px;
                    font-size: 12px;
                    font-weight: 600;
                }}
            """)
            
            # Mensaje global
            if rendimiento_global >= 100:
                self.global_message.setText("El proyecto tiene un rendimiento superior al esperado")
            elif rendimiento_global >= 90:
                self.global_message. setText("El proyecto tiene un rendimiento dentro de lo aceptable")
            else:
                self.global_message.setText("El proyecto requiere atención - Rendimiento por debajo del esperado")
            
            # === RENDIMIENTO FINANCIERO ===
            logger.info("   💰 Actualizando Rendimiento Financiero...")
            rendimiento_fin = metricas['rendimiento_financiero']
            estado_fin = metricas['estado_financiero']
            
            self. financiero_value.setText(f"{rendimiento_fin:.0f}%")
            self.financiero_estado.setText(f"{estado_fin['emoji']} {estado_fin['descripcion']}")
            logger.info(f"      - Valor: {rendimiento_fin:.0f}%")
            logger.info(f"      - Estado: {estado_fin['descripcion']}")
            
            # ✅ USAR MENSAJE PRE-CALCULADO (sin importar RendimientoCalculator)
            mensaje_fin = metricas.get('mensaje_financiero', 'Calculando...')
            self.financiero_mensaje.setText(mensaje_fin)
            
            # === RENDIMIENTO TEMPORAL ===
            logger.info("   ⏱️ Actualizando Rendimiento Temporal...")
            rendimiento_temp = metricas['rendimiento_temporal']
            estado_temp = metricas['estado_temporal']
            
            self.temporal_value.setText(f"{rendimiento_temp:.0f}%")
            self.temporal_estado.setText(f"{estado_temp['emoji']} {estado_temp['descripcion']}")
            logger.info(f"      - Valor: {rendimiento_temp:.0f}%")
            logger.info(f"      - Estado: {estado_temp['descripcion']}")
            
            # ✅ USAR MENSAJE PRE-CALCULADO (sin importar RendimientoCalculator)
            mensaje_temp = metricas.get('mensaje_temporal', 'Calculando...')
            self.temporal_mensaje.setText(mensaje_temp)
            
            # === INDICADORES ===
            logger.info("   📈 Actualizando Indicadores Clave...")
            self.ind_fisico.value_label.setText(f"{metricas['avance_fisico']:.0f}%")
            self.ind_financiero.value_label. setText(f"{metricas['avance_financiero']:.0f}%")
            self.ind_tiempo.value_label. setText(f"{metricas['porcentaje_tiempo']:.0f}%")
            
            porcentaje_ejecutado = (metricas['gastado_total'] / metricas['presupuesto_total'] * 100) if metricas['presupuesto_total'] > 0 else 0
            self.ind_presupuesto.value_label.setText(f"{porcentaje_ejecutado:.0f}%")
            logger.info(f"      - Avance Físico: {metricas['avance_fisico']:.0f}%")
            logger.info(f"      - Avance Financiero: {metricas['avance_financiero']:.0f}%")
            logger.info(f"      - Tiempo Transcurrido: {metricas['porcentaje_tiempo']:.0f}%")
            logger.info(f"      - Presupuesto Ejecutado:  {porcentaje_ejecutado:.0f}%")
            
            # === PROYECCIONES ===
            logger.info("   🔮 Actualizando Proyecciones...")
            
            # Proyección de gasto
            if metricas['sobrecosto_estimado'] > 0:
                self.proy_gasto. setText(
                    f"💰 Gasto final proyectado: RD$ {metricas['proyeccion_gasto_final']:,.2f} "
                    f"(Sobrecosto: +{metricas['porcentaje_sobrecosto']:.1f}%)"
                )
                self.proy_gasto.setStyleSheet(f"color: {COLORS['red_600']}; font-size: 12px; font-weight: 600;")
                logger.info(f"      - Sobrecosto proyectado: +{metricas['porcentaje_sobrecosto']:.1f}%")
            elif metricas['sobrecosto_estimado'] < 0:
                self.proy_gasto.setText(
                    f"💰 Gasto final proyectado: RD$ {metricas['proyeccion_gasto_final']:,.2f} "
                    f"(Ahorro: -{abs(metricas['porcentaje_sobrecosto']):.1f}%)"
                )
                self.proy_gasto. setStyleSheet(f"color:  {COLORS['green_600']}; font-size: 12px; font-weight: 600;")
                logger.info(f"      - Ahorro proyectado: -{abs(metricas['porcentaje_sobrecosto']):.1f}%")
            else:
                self.proy_gasto. setText(
                    f"💰 Gasto final proyectado: RD$ {metricas['proyeccion_gasto_final']:,.2f} (En presupuesto)"
                )
                self.proy_gasto.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 12px;")
                logger.info("      - En presupuesto")
            
            # Proyección de tiempo
            if metricas['retraso_estimado_meses'] > 0:
                self.proy_tiempo.setText(
                    f"📅 Duración proyectada: {metricas['meses_proyectados_totales']:.1f} meses "
                    f"(Retraso: +{metricas['retraso_estimado_meses']:.1f} meses)"
                )
                self.proy_tiempo.setStyleSheet(f"color: {COLORS['red_600']}; font-size: 12px; font-weight: 600;")
                logger.info(f"      - Retraso proyectado: +{metricas['retraso_estimado_meses']:.1f} meses")
            elif metricas['retraso_estimado_meses'] < 0:
                adelanto = abs(metricas['retraso_estimado_meses'])
                self.proy_tiempo.setText(
                    f"📅 Duración proyectada: {metricas['meses_proyectados_totales']:.1f} meses "
                    f"(Adelanto: -{adelanto:.1f} meses)"
                )
                self.proy_tiempo.setStyleSheet(f"color: {COLORS['green_600']}; font-size:  12px; font-weight:  600;")
                logger. info(f"      - Adelanto proyectado: -{adelanto:.1f} meses")
            else:
                self.proy_tiempo.setText(
                    f"📅 Duración proyectada: {metricas['meses_proyectados_totales']:.1f} meses (En tiempo)"
                )
                self.proy_tiempo.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 12px;")
                logger.info("      - En tiempo")
            
            # ✅ MARCAR QUE HAY DATOS VÁLIDOS
            self._has_data = True
            
            # ✅ FORZAR REPINTADO
            self.update()
            self.repaint()
            
            # ✅ LOG FINAL
            logger.info("   ✅ RendimientoCard actualizado exitosamente")
            logger.info("=" * 80)
            
        except KeyError as e:
            logger. error(f"   ❌ Campo faltante en métricas: {e}")
            logger.error(f"   Métricas recibidas: {list(metricas.keys()) if metricas else 'None'}")
            self._has_data = False
            self._show_no_data()
        except ImportError as e:
            logger. error(f"   ❌ Error de importación: {e}", exc_info=True)
            logger.error(f"   Verifica la estructura de carpetas del proyecto")
            self._has_data = False
            self._show_no_data()
        except Exception as e:
            logger. error(f"   ❌ Error actualizando card: {e}", exc_info=True)
            logger.error(f"   Tipo de error: {type(e).__name__}")
            self._has_data = False
            self._show_no_data()