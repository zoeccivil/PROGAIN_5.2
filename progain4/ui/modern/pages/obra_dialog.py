"""
ObraDialog - Diálogo para crear/editar proyectos de obra

Campos completos:
- Información básica (nombre, descripción)
- Estado y avance
- Datos financieros (presupuesto)
- Fechas y duración
- Datos del cliente
- Responsable y ubicación
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QDateEdit, QSlider,
    QFormLayout, QWidget, QMessageBox, QScrollArea, QFrame, QSpinBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont

from .. components.clean_card import CleanCard
from ..theme_config import COLORS, BORDER

import logging
from datetime import datetime, date
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ObraDialog(QDialog):
    """
    Diálogo para crear o editar una obra/proyecto.    
    
    Modos:  
    - Crear: proyecto=None
    - Editar: proyecto=dict con datos existentes
    """
    
    # ✅ Signal para notificar cuando se actualiza un proyecto
    proyecto_updated = pyqtSignal(str, str)  # (proyecto_id, proyecto_nombre)
    
    def __init__(self, firebase_client, modo='crear', proyecto_id=None, proyecto=None, parent=None):
        """
        Initialize ObraDialog.  
        
        Args: 
            firebase_client: FirebaseClient instance
            modo: 'crear' o 'editar'
            proyecto_id: ID del proyecto (solo para editar)
            proyecto: Dict con datos del proyecto (alternativa a proyecto_id)
            parent:  Parent widget
        """
        super().__init__(parent)
        
        self.firebase_client = firebase_client
        self.modo = modo
        self.proyecto_id = proyecto_id
        
        # Si se pasa proyecto dict directamente (compatibilidad)
        if proyecto and not proyecto_id:
            self. proyecto_id = proyecto.get('id')
            self.proyecto_data = proyecto
        elif proyecto_id:
            # Cargar datos del proyecto desde Firebase
            self.proyecto_data = self._load_proyecto_from_firebase(proyecto_id)
        else:
            self.proyecto_data = None
        
        self.setup_ui()
        
        # Si es modo editar, cargar datos en los campos
        if self.modo == 'editar' and self.proyecto_data:
            self._load_proyecto_data()

    def _load_proyecto_from_firebase(self, proyecto_id: str) -> Optional[Dict[str, Any]]: 
        """Cargar datos del proyecto desde Firebase"""
        try:
            from firebase_admin import firestore
            db = firestore.client()
            
            doc_ref = db.collection('proyectos').document(proyecto_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = proyecto_id
                return data
            else:
                logger.warning(f"Proyecto {proyecto_id} no encontrado")
                return None
        except Exception as e:
            logger.error(f"Error loading proyecto {proyecto_id}: {e}")
            return None

    def setup_ui(self):
        """Crear interfaz del diálogo"""
        
        # Configuración de ventana
        title = "Editar Obra" if self.modo == 'editar' else "Nueva Obra"
        self.setWindowTitle(title)
        self.resize(700, 850)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        # Título
        title_label = QLabel(f"🏗️ {title}")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLORS['slate_900']};")
        main_layout.addWidget(title_label)
        
        # Scroll area para el formulario
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape. NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # Container del formulario
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(24)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # === SECCIÓN 1: INFORMACIÓN BÁSICA ===
        basic_section = self._create_basic_section()
        form_layout.addWidget(basic_section)
        
        # === SECCIÓN 2: ESTADO Y AVANCE ===
        status_section = self._create_status_section()
        form_layout.addWidget(status_section)
        
        # === SECCIÓN 3: DATOS FINANCIEROS ===
        financial_section = self._create_financial_section()
        form_layout.addWidget(financial_section)
        
        # === SECCIÓN 4: FECHAS Y DURACIÓN ===
        dates_section = self._create_dates_section()
        form_layout.addWidget(dates_section)
        
        # === SECCIÓN 5: DATOS DEL CLIENTE ===
        client_section = self._create_client_section()
        form_layout.addWidget(client_section)
        
        # === SECCIÓN 6: NOTAS ===
        notes_section = self._create_notes_section()
        form_layout.addWidget(notes_section)
        
        scroll.setWidget(form_container)
        main_layout.addWidget(scroll)
        
        # === BOTONES ===
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['slate_100']};
                color: {COLORS['slate_700']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
                padding: 10px 24px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['slate_200']};
            }}
        """)
        btn_cancel. clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("Guardar" if self.modo == 'editar' else "Crear Obra")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['blue_600']};
                color:  {COLORS['white']};
                border: none;
                border-radius: {BORDER['radius_sm']}px;
                padding: 10px 24px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['blue_700']};
            }}
        """)
        btn_save.clicked.connect(self._save_proyecto)
        buttons_layout.addWidget(btn_save)
        
        main_layout.addLayout(buttons_layout)
    
    def _create_basic_section(self) -> QWidget:
        """Crear sección de información básica"""
        
        card = CleanCard(padding=20)
        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        
        # Título de sección
        section_title = QLabel("📋 Información Básica")
        section_title.setStyleSheet(f"color: {COLORS['slate_900']}; font-size: 14px; font-weight: 600;")
        layout.addWidget(section_title)
        
        # Formulario
        form = QFormLayout()
        form.setSpacing(12)
        
        # Nombre del proyecto (REQUERIDO)
        self. input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Ej:  PISCINA ADUANAS DGAP-0022")
        self.input_nombre.setStyleSheet(self._get_input_style())
        form.addRow("Nombre:  *", self.input_nombre)
        
        # Descripción
        self.input_descripcion = QTextEdit()
        self.input_descripcion.setPlaceholderText("Descripción breve del proyecto...")
        self.input_descripcion.setMaximumHeight(80)
        self.input_descripcion.setStyleSheet(self._get_input_style())
        form.addRow("Descripción:", self.input_descripcion)
        
        layout.addLayout(form)
        
        return card
    
    def _create_status_section(self) -> QWidget:
        """Crear sección de estado y avance"""
        
        card = CleanCard(padding=20)
        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        
        # Título de sección
        section_title = QLabel("🔄 Estado y Avance")
        section_title.setStyleSheet(f"color: {COLORS['slate_900']}; font-size: 14px; font-weight: 600;")
        layout.addWidget(section_title)
        
        # Formulario
        form = QFormLayout()
        form.setSpacing(12)
        
        # Estado
        self.combo_estado = QComboBox()
        self.combo_estado. addItems(["Activo", "Pausado", "Completado"])
        self.combo_estado. setStyleSheet(self._get_input_style())
        form.addRow("Estado:", self.combo_estado)
        
        layout.addLayout(form)
        
        # Avance Físico (Slider)
        avance_container = QWidget()
        avance_layout = QVBoxLayout(avance_container)
        avance_layout.setSpacing(8)
        avance_layout.setContentsMargins(0, 0, 0, 0)
        
        avance_label_container = QHBoxLayout()
        avance_label = QLabel("Avance Físico:")
        avance_label.setStyleSheet(f"color: {COLORS['slate_700']}; font-weight: 500;")
        avance_label_container.addWidget(avance_label)
        avance_label_container.addStretch()
        
        self.avance_value_label = QLabel("0%")
        self.avance_value_label.setStyleSheet(f"color: {COLORS['blue_600']}; font-weight: 600; font-size: 16px;")
        avance_label_container.addWidget(self. avance_value_label)
        
        avance_layout.addLayout(avance_label_container)
        
        # Slider de avance
        self.slider_avance = QSlider(Qt.Orientation.Horizontal)
        self.slider_avance. setMinimum(0)
        self.slider_avance.setMaximum(100)
        self.slider_avance.setValue(0)
        self.slider_avance.setTickPosition(QSlider.TickPosition. TicksBelow)
        self.slider_avance.setTickInterval(10)
        self.slider_avance.setStyleSheet(f"""
            QSlider:: groove: horizontal {{
                border: none;
                height: 8px;
                background-color: {COLORS['slate_200']};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background-color: {COLORS['blue_600']};
                border:  none;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background-color: {COLORS['blue_700']};
            }}
            QSlider::sub-page: horizontal {{
                background-color:  {COLORS['blue_500']};
                border-radius: 4px;
            }}
        """)
        self.slider_avance.valueChanged.connect(self._on_avance_changed)
        avance_layout.addWidget(self.slider_avance)
        
        layout.addWidget(avance_container)
        
        return card
    
    def _create_financial_section(self) -> QWidget:
        """Crear sección de datos financieros"""
        
        card = CleanCard(padding=20)
        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        
        # Título de sección
        section_title = QLabel("💰 Datos Financieros")
        section_title.setStyleSheet(f"color: {COLORS['slate_900']}; font-size: 14px; font-weight: 600;")
        layout.addWidget(section_title)
        
        # Formulario
        form = QFormLayout()
        form.setSpacing(12)
        
        # Presupuesto Total (REQUERIDO)
        self.input_presupuesto = QLineEdit()
        self.input_presupuesto.setPlaceholderText("0.00")
        self.input_presupuesto.setStyleSheet(self._get_input_style())
        form.addRow("Presupuesto Total (RD$): *", self.input_presupuesto)
        
        layout.addLayout(form)
        
        # Nota informativa
        note = QLabel("ℹ️ El monto gastado se calcula automáticamente desde las transacciones")
        note.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 11px; font-style: italic;")
        note.setWordWrap(True)
        layout.addWidget(note)
        
        return card
    
    def _create_dates_section(self) -> QWidget:
        """Crear sección de fechas y duración"""
        
        card = CleanCard(padding=20)
        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        
        # Título de sección
        section_title = QLabel("📅 Fechas y Duración del Proyecto")
        section_title.setStyleSheet(f"color: {COLORS['slate_900']}; font-size: 14px; font-weight: 600;")
        layout.addWidget(section_title)
        
        # Formulario
        form = QFormLayout()
        form.setSpacing(12)
        
        # Fecha de inicio
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDate(QDate.currentDate())
        self.date_inicio.setDisplayFormat("dd/MM/yyyy")
        self.date_inicio. setStyleSheet(self._get_input_style())
        form.addRow("Fecha de Inicio:", self.date_inicio)
        
        # Fecha fin estimada
        self.date_fin_estimada = QDateEdit()
        self.date_fin_estimada.setCalendarPopup(True)
        self.date_fin_estimada.setDate(QDate.currentDate().addMonths(6))
        self.date_fin_estimada.setDisplayFormat("dd/MM/yyyy")
        self.date_fin_estimada.setStyleSheet(self._get_input_style())
        self.date_fin_estimada. dateChanged.connect(self._on_date_changed)
        form.addRow("Fecha Fin Estimada:", self.date_fin_estimada)
        
        # Duración estimada (en meses)
        self.spin_duracion = QSpinBox()
        self.spin_duracion.setMinimum(1)
        self.spin_duracion.setMaximum(120)
        self.spin_duracion.setValue(6)
        self.spin_duracion.setSuffix(" meses")
        self.spin_duracion.setStyleSheet(self._get_input_style())
        self.spin_duracion.valueChanged.connect(self._on_duracion_changed)
        form.addRow("Duración Estimada:", self.spin_duracion)
        
        layout.addLayout(form)
        
        # Nota informativa
        note = QLabel("💡 La duración se calcula automáticamente según las fechas, pero puedes ajustarla manualmente")
        note.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 11px; font-style: italic;")
        note.setWordWrap(True)
        layout.addWidget(note)
        
        return card
    
    def _create_client_section(self) -> QWidget:
        """Crear sección de datos del cliente"""
        
        card = CleanCard(padding=20)
        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        
        # Título de sección
        section_title = QLabel("👥 Datos del Cliente y Equipo")
        section_title. setStyleSheet(f"color:  {COLORS['slate_900']}; font-size: 14px; font-weight: 600;")
        layout.addWidget(section_title)
        
        # Formulario
        form = QFormLayout()
        form.setSpacing(12)
        
        # Cliente
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Ej: DGAP - Dirección General de Aduanas")
        self.input_cliente.setStyleSheet(self._get_input_style())
        form.addRow("Cliente:", self.input_cliente)
        
        # Ubicación
        self.input_ubicacion = QLineEdit()
        self.input_ubicacion.setPlaceholderText("Ej:  Santo Domingo, República Dominicana")
        self.input_ubicacion.setStyleSheet(self._get_input_style())
        form.addRow("Ubicación:", self.input_ubicacion)
        
        # Responsable
        self.input_responsable = QLineEdit()
        self.input_responsable.setPlaceholderText("Ej: Ing. Juan Pérez")
        self.input_responsable.setStyleSheet(self._get_input_style())
        form.addRow("Responsable:", self. input_responsable)
        
        layout.addLayout(form)
        
        return card
    
    def _create_notes_section(self) -> QWidget:
        """Crear sección de notas"""
        
        card = CleanCard(padding=20)
        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        
        # Título de sección
        section_title = QLabel("📝 Notas y Observaciones")
        section_title.setStyleSheet(f"color: {COLORS['slate_900']}; font-size:  14px; font-weight:  600;")
        layout.addWidget(section_title)
        
        # Notas
        self.input_notas = QTextEdit()
        self.input_notas.setPlaceholderText("Observaciones generales del proyecto...")
        self.input_notas.setMaximumHeight(100)
        self.input_notas.setStyleSheet(self._get_input_style())
        layout.addWidget(self.input_notas)
        
        return card
    
    # ==================== CALLBACKS ====================
    
    def _on_avance_changed(self, value:  int):
        """Callback cuando cambia el slider de avance"""
        self. avance_value_label.setText(f"{value}%")
    
    def _on_date_changed(self):
        """Callback cuando cambian las fechas - auto-calcular duración"""
        try:
            fecha_inicio = self.date_inicio.date()
            fecha_fin = self.date_fin_estimada.date()
            
            # Calcular diferencia en días
            dias = fecha_inicio. daysTo(fecha_fin)
            
            # Convertir a meses (30. 44 días promedio por mes)
            meses = round(dias / 30.44)
            
            if meses > 0:
                # Bloquear señal para evitar loop infinito
                self.spin_duracion.blockSignals(True)
                self.spin_duracion.setValue(meses)
                self.spin_duracion.blockSignals(False)
        except Exception as e:
            logger.error(f"Error calculating duration: {e}")
    
    def _on_duracion_changed(self, meses: int):
        """Callback cuando cambia la duración - auto-calcular fecha fin"""
        try:
            fecha_inicio = self.date_inicio.date()
            
            # Calcular fecha fin basada en duración
            fecha_fin = fecha_inicio.addMonths(meses)
            
            # Bloquear señal para evitar loop infinito
            self.date_fin_estimada.blockSignals(True)
            self.date_fin_estimada.setDate(fecha_fin)
            self.date_fin_estimada.blockSignals(False)
        except Exception as e:
            logger.error(f"Error calculating end date: {e}")
    
    # ==================== DATOS ====================
    
    def _load_proyecto_data(self):
        """Cargar datos del proyecto en modo edición"""
        
        if not self.proyecto_data:
            logger.warning("No project data to load")
            return
        
        # Información básica
        self.input_nombre.setText(self.proyecto_data.get('nombre', ''))
        self.input_descripcion.setPlainText(self.proyecto_data. get('descripcion', ''))
        
        # Estado y avance
        estado_map = {'activo': 0, 'pausado': 1, 'completado': 2}
        estado_index = estado_map.get(self.proyecto_data.get('estado', 'activo'), 0)
        self.combo_estado.setCurrentIndex(estado_index)
        
        avance_fisico = int(self.proyecto_data.get('avance_fisico', 0))
        self.slider_avance.setValue(avance_fisico)
        
        # Financiero
        presupuesto = self.proyecto_data.get('presupuesto_total', 0)
        self.input_presupuesto. setText(str(presupuesto))
        
        # Fechas
        fecha_inicio_str = self.proyecto_data. get('fecha_inicio', '')
        if fecha_inicio_str:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
                self.date_inicio.setDate(QDate(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day))
            except Exception as e:
                logger.error(f"Error parsing fecha_inicio: {e}")
        
        fecha_fin_str = self. proyecto_data.get('fecha_fin_estimada', '')
        if fecha_fin_str:
            try:
                fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
                self. date_fin_estimada.setDate(QDate(fecha_fin.year, fecha_fin.month, fecha_fin.day))
            except Exception as e:
                logger.error(f"Error parsing fecha_fin: {e}")
        
        # Duración
        duracion_meses = int(self.proyecto_data.get('duracion_meses', 6))
        self.spin_duracion.setValue(duracion_meses)
        
        # Cliente
        self.input_cliente.setText(self.proyecto_data.get('cliente', ''))
        self.input_ubicacion.setText(self.proyecto_data.get('ubicacion', ''))
        self.input_responsable.setText(self.proyecto_data.get('responsable', ''))
        
        # Notas
        self.input_notas.setPlainText(self.proyecto_data.get('notas', ''))
    
    def _save_proyecto(self):
        """Guardar proyecto en Firebase"""
        
        # Validaciones
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Validación", "El nombre del proyecto es obligatorio.")
            self.input_nombre.setFocus()
            return
        
        presupuesto_str = self.input_presupuesto.text().strip()
        if not presupuesto_str:
            QMessageBox. warning(self, "Validación", "El presupuesto es obligatorio.")
            self.input_presupuesto.setFocus()
            return
        
        try:
            presupuesto = float(presupuesto_str)
            if presupuesto < 0:
                raise ValueError()
        except: 
            QMessageBox.warning(self, "Validación", "El presupuesto debe ser un número válido.")
            self.input_presupuesto.setFocus()
            return
        
        # Recopilar datos
        estado_map = {0: 'activo', 1: 'pausado', 2: 'completado'}
        estado = estado_map.get(self. combo_estado.currentIndex(), 'activo')
        
        # Convertir fechas
        qdate_inicio = self.date_inicio.date()
        fecha_inicio = f"{qdate_inicio.year()}-{qdate_inicio.month():02d}-{qdate_inicio.day():02d}"
        
        qdate_fin = self.date_fin_estimada. date()
        fecha_fin_estimada = f"{qdate_fin.year()}-{qdate_fin.month():02d}-{qdate_fin.day():02d}"
        
        # Construir diccionario de datos
        proyecto_data = {
            'nombre': nombre,
            'descripcion': self.input_descripcion.toPlainText().strip(),
            'estado': estado,
            'presupuesto_total': presupuesto,
            'avance_fisico': self.slider_avance.value(),
            'fecha_inicio': fecha_inicio,
            'fecha_fin_estimada': fecha_fin_estimada,
            'duracion_meses': self.spin_duracion.value(),
            'cliente': self.input_cliente.text().strip(),
            'ubicacion': self.input_ubicacion. text().strip(),
            'responsable': self.input_responsable.text().strip(),
            'notas': self.input_notas.toPlainText().strip(),
            'color':  COLORS['blue_600'],
            'actualizado_en': datetime.now()
        }
        
        # ==================== CALCULAR Y GUARDAR RENDIMIENTO ====================
        # ✅ Calcular rendimiento si es modo editar
        if self.modo == 'editar' and self.proyecto_id:
            try:
                from services.rendimiento_calculator import RendimientoCalculator
                
                logger.info("Calculando rendimiento para guardar en el documento...")
                
                # ✅ PASO 1: Calcular gastado_total desde transacciones
                gastado_total = self._calcular_gastado_total()
                
                # ✅ PASO 2: Parsear fecha_inicio a objeto date
                try:
                    if isinstance(fecha_inicio, str):
                        fecha_inicio_date = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                    else: 
                        fecha_inicio_date = fecha_inicio
                except Exception as e:
                    logger. warning(f"Error parseando fecha_inicio: {e}")
                    fecha_inicio_date = date.today()
                
                # ✅ PASO 3: Llamar al calculador con los parámetros correctos
                metricas = RendimientoCalculator.calcular_rendimiento_completo(
                    avance_fisico=self.slider_avance. value(),
                    presupuesto_total=presupuesto,
                    gastado_total=gastado_total,
                    fecha_inicio=fecha_inicio_date,
                    duracion_meses=self.spin_duracion.value()
                )
                
                # Agregar rendimiento al proyecto_data
                if metricas: 
                    proyecto_data['rendimiento'] = {
                        # Valores principales
                        'rendimiento_global': round(metricas['rendimiento_global'], 2),
                        'rendimiento_financiero': round(metricas['rendimiento_financiero'], 2),
                        'rendimiento_temporal': round(metricas['rendimiento_temporal'], 2),
                        
                        # Estados
                        'estado_global': metricas['estado_global']['descripcion'],
                        'estado_financiero': metricas['estado_financiero']['descripcion'],
                        'estado_temporal': metricas['estado_temporal']['descripcion'],
                        
                        # Proyecciones
                        'proyeccion_gasto_final': round(metricas['proyeccion_gasto_final'], 2),
                        'sobrecosto_estimado': round(metricas['sobrecosto_estimado'], 2),
                        'porcentaje_sobrecosto': round(metricas['porcentaje_sobrecosto'], 2),
                        'meses_proyectados_totales': round(metricas['meses_proyectados_totales'], 2),
                        'retraso_estimado_meses': round(metricas['retraso_estimado_meses'], 2),
                        
                        # Datos del momento
                        'gastado_total': round(metricas['gastado_total'], 2),
                        'avance_financiero': round(metricas['avance_financiero'], 2),
                        'porcentaje_tiempo': round(metricas['porcentaje_tiempo'], 2),
                        
                        # Metadata
                        'fecha_calculo': datetime.now().isoformat(),
                        'version':  '1.0'
                    }
                    logger.info(f"✅ Rendimiento calculado:  Global={metricas['rendimiento_global']:.1f}%, "
                              f"Financiero={metricas['rendimiento_financiero']:.1f}%, "
                              f"Temporal={metricas['rendimiento_temporal']:.1f}%")
                else: 
                    logger.warning("No se pudo calcular rendimiento (datos insuficientes)")
                    
            except Exception as e:
                logger.error(f"Error calculando rendimiento: {e}", exc_info=True)
                # No fallar el guardado por esto
        # ==================== FIN CÁLCULO RENDIMIENTO ====================
        
        try:
            if self.modo == 'editar':
                # Actualizar proyecto existente
                self.firebase_client.update_proyecto(self.proyecto_id, proyecto_data)
                logger.info(f"Proyecto {self.proyecto_id} actualizado")
                
                # ✅ Emitir señal de actualización
                self.proyecto_updated.emit(self.proyecto_id, nombre)
                
                QMessageBox.information(self, "Éxito", "Proyecto actualizado correctamente.")
            else:
                # Crear nuevo proyecto
                proyecto_data['creado_en'] = datetime.now()
                proyecto_id = self.firebase_client.create_proyecto(
                    nombre=nombre,
                    descripcion=proyecto_data['descripcion']
                )
                
                # Actualizar con el resto de campos
                self.firebase_client. update_proyecto(proyecto_id, proyecto_data)
                logger.info(f"Nuevo proyecto creado: {proyecto_id}")
                QMessageBox.information(self, "Éxito", "Proyecto creado correctamente.")
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Error saving proyecto: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al guardar el proyecto:\n{str(e)}")
    
    # ==================== ESTILOS ====================
    
    def _get_input_style(self) -> str:
        """Obtener estilo común para inputs"""
        return f"""
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
                padding:  8px 12px;
                color: {COLORS['slate_900']};
                font-size:  13px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox: focus {{
                border-color:  {COLORS['blue_500']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox:: down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {COLORS['slate_600']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 16px;
                border: none;
            }}
        """
    

    def _calcular_gastado_total(self) -> float:
        """Calcular el total gastado en el proyecto (todas las transacciones)"""
        
        if not self.firebase_client or not self.proyecto_id:
            return 0.0
        
        try:
            transacciones = self.firebase_client.get_transacciones_by_proyecto(
                self.proyecto_id,
                cuenta_id=None
            )
            
            total = 0.0
            for trans in transacciones:
                if hasattr(trans, 'to_dict'):
                    data = trans.to_dict() or {}
                else:
                    data = trans
                
                tipo = data.get('tipo', '')
                estado = data.get('estado', 'activa')
                es_transferencia = data.get('es_transferencia', False)
                
                if tipo == 'gasto' and estado != 'anulada' and not es_transferencia:
                    monto = float(data.get('monto', 0))
                    total += monto
            
            logger.info(f"Gastado total calculado: RD$ {total: ,.2f}")
            return total
            
        except Exception as e: 
            logger.error(f"Error calculating gastado_total: {e}")
            return 0.0