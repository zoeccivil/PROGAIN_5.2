"""
DashboardPage - Dashboard moderno con filtros de fecha

Permite navegar por diferentes períodos para ver datos históricos.  
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QPushButton, QComboBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from .. components.clean_card import CleanCard
from ..components.icon_manager import icon_manager
from ..components.rendimiento_card import RendimientoCard
from ..theme_config import COLORS, BORDER

from ....services.rendimiento_calculator import RendimientoCalculator

import logging
from datetime import datetime, date
from calendar import monthrange
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class DashboardPage(QWidget):
    """
    Dashboard moderno con resumen financiero y filtros de fecha.  
    """
    
    account_clicked = pyqtSignal(str)
    
    def __init__(self, firebase_client=None, proyecto_id=None, proyecto_nombre=None, parent=None):
        """
        Initialize DashboardPage with Firebase integration. 
        
        Args:
            firebase_client: FirebaseClient instance
            proyecto_id: Current project ID
            proyecto_nombre:  Current project name
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.firebase_client = firebase_client
        self.proyecto_id = proyecto_id
        self.proyecto_nombre = proyecto_nombre or "Proyecto"
        
        # Estado de filtros
        self.current_year = datetime. now().year
        self.current_month = datetime.now().month
        self.current_project_data = None  # ✅ Guardar datos completos del proyecto
        
        # Cache de datos
        self._cuentas = []
        self._resumen_financiero = {}
        self._gastos_categoria = []
        self._ingresos_gastos_mes = {}
        
        self.setup_ui()
        
        # Cargar datos iniciales
        if self.firebase_client and self.proyecto_id:
            self._detect_last_month_with_data()
            self.refresh()
            
            # ✅ NUEVO: Cargar datos del proyecto DESPUÉS del refresh inicial
            # Usar QTimer para asegurar que Firebase tenga datos actualizados
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(200, self._load_project_data_and_update)
    
    def _load_project_data(self):
        """Cargar datos completos del proyecto actual DIRECTAMENTE desde Firestore"""
        
        if not self. firebase_client or not self.proyecto_id:
            self.current_project_data = None
            return
        
        try:
            # ✅ NUEVO: Leer DIRECTAMENTE desde Firestore (sin caché)
            from firebase_admin import firestore
            db = firestore.client()
            
            # Obtener documento directo
            doc_ref = db.collection('proyectos').document(str(self.proyecto_id))
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"Project {self.proyecto_id} not found in Firestore")
                self.current_project_data = None
                return
            
            # Extraer datos
            data = doc.to_dict() or {}
            
            # ✅ LOG DEBUG: Ver si existe el campo rendimiento
            if 'rendimiento' in data: 
                logger.info(f"✅ Campo 'rendimiento' ENCONTRADO en Firestore")
                logger.info(f"   Rendimiento Global: {data['rendimiento']. get('rendimiento_global')}%")
            else:
                logger.warning(f"❌ Campo 'rendimiento' NO EXISTE en el documento")
            
            # Normalizar datos del proyecto
            self.current_project_data = {
                'id': str(self.proyecto_id),
                'nombre': data.get('nombre', ''),
                'avance_fisico': int(data.get('avance_fisico', 0)),
                'presupuesto_total': float(data.get('presupuesto_total', 0)),
                'duracion_meses': int(data.get('duracion_meses', 6)),
                'fecha_inicio': data.get('fecha_inicio', ''),
                'rendimiento':  data.get('rendimiento'),  # ✅ INCLUIR RENDIMIENTO
            }
            
            # ✅ LOG DEBUG:  Verificar que se guardó en current_project_data
            if self.current_project_data. get('rendimiento'):
                logger.info(f"✅ Rendimiento guardado en current_project_data")
            else:
                logger.warning(f"❌ Rendimiento NO se guardó en current_project_data")
            
            # ✅ LOG DETALLADO para debugging
            logger.info(f"✅ Loaded project data DIRECT from Firestore:")
            logger.info(f"   Nombre: {self.current_project_data['nombre']}")
            logger.info(f"   Presupuesto: RD$ {self.current_project_data['presupuesto_total']: ,.2f}")
            logger. info(f"   Avance Físico: {self. current_project_data['avance_fisico']}%")
            logger.info(f"   Duración:  {self.current_project_data['duracion_meses']} meses")
            logger.info(f"   Fecha Inicio: {self.current_project_data['fecha_inicio']}")
            
        except Exception as e:
            logger.error(f"Error loading project data: {e}", exc_info=True)
            self.current_project_data = None
    


    def _get_rendimiento_from_cache(self) -> Optional[Dict[str, Any]]:
        """
        Intentar leer rendimiento guardado en el documento del proyecto. 
        Retorna None si no existe o está desactualizado.
        """
        logger.info("🔍 Intentando leer rendimiento desde cache...")
        
        if not self. current_project_data:
            logger.warning("❌ current_project_data es None")
            return None
        
        logger.info(f"✅ current_project_data existe: {list(self.current_project_data.keys())}")
        
        rendimiento_guardado = self.current_project_data.get('rendimiento')
        
        if not rendimiento_guardado:
            logger.warning("❌ No hay campo 'rendimiento' en current_project_data")
            return None
        
        logger.info(f"✅ Campo rendimiento encontrado: {list(rendimiento_guardado.keys())}")
        
        # Verificar que tenga los campos necesarios
        campos_requeridos = [
            'rendimiento_global', 'rendimiento_financiero', 'rendimiento_temporal',
            'fecha_calculo'
        ]
        
        faltantes = [c for c in campos_requeridos if c not in rendimiento_guardado]
        if faltantes:
            logger. warning(f"❌ Rendimiento incompleto.  Faltan:  {faltantes}")
            return None
        
        logger.info("✅ Todos los campos requeridos presentes")
        
        # Opcional: Verificar si está desactualizado (más de 1 día)
        try:
            from datetime import datetime, timedelta
            fecha_calculo_str = rendimiento_guardado.get('fecha_calculo')
            if fecha_calculo_str: 
                fecha_calculo = datetime.fromisoformat(fecha_calculo_str)
                dias_antiguedad = (datetime.now() - fecha_calculo).days
                logger.info(f"📅 Rendimiento calculado hace {dias_antiguedad} días")
                
                if dias_antiguedad > 1:
                    logger.warning(f"⚠️ Rendimiento desactualizado (>{dias_antiguedad} días)")
                    return None
        except Exception as e:
            logger.warning(f"Error verificando fecha:  {e}")
        
        logger.info("✅ ✅ ✅ Usando rendimiento guardado del documento")
        return rendimiento_guardado

    def _get_emoji_for_estado(self, estado: str) -> str:
        """Obtener emoji según estado de rendimiento"""
        emojis = {
            'Excelente': '🟢',
            'Bueno': '🔵',
            'Aceptable': '🟡',
            'Deficiente': '🟠',
            'Crítico': '🔴'
        }
        return emojis.get(estado, '⚪')
    
    def _get_color_for_estado(self, estado: str) -> str:
        """Obtener color según estado de rendimiento"""
        from ui.modern. theme_config import COLORS
        colores = {
            'Excelente': COLORS['green_600'],
            'Bueno': COLORS['blue_600'],
            'Aceptable': COLORS['yellow_600'],
            'Deficiente': COLORS['orange_600'],
            'Crítico': COLORS['red_600']
        }
        return colores.get(estado, COLORS['slate_600'])

    def set_project(self, proyecto_id:  str, proyecto_nombre: str):
        """
        Actualizar el proyecto activo del dashboard. 
        
        Args:
            proyecto_id:  Nuevo ID del proyecto
            proyecto_nombre: Nuevo nombre del proyecto
        """
        logger.info(f"Setting dashboard project to: {proyecto_nombre} ({proyecto_id})")
        
        self.proyecto_id = proyecto_id
        self.proyecto_nombre = proyecto_nombre
        
        # ✅ IMPORTANTE: Limpiar datos anteriores
        self. current_project_data = None
        
        # Detectar último mes con datos del nuevo proyecto
        self._detect_last_month_with_data()
        
        # ✅ NUEVO: Refrescar Y recargar datos en secuencia
        self.refresh()
        
        # ✅ NUEVO:  Forzar recarga de datos del proyecto DESPUÉS del refresh
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._load_project_data_delayed)
    

    def _load_project_data_and_update(self):
        """Cargar datos del proyecto y forzar actualización de rendimiento (inicial)"""
        logger.info("Initial project data load...")
        self._load_project_data()
        
        # Forzar actualización del rendimiento después de cargar datos
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._update_rendimiento_card)


    def _load_project_data_delayed(self):
        """Cargar datos del proyecto con delay para asegurar que Firebase esté actualizado"""
        logger.info("Loading project data (delayed)...")
        self._load_project_data()
        
        # ✅ Actualizar rendimiento DESPUÉS de cargar datos
        self._update_rendimiento_card()
    
    def setup_ui(self):
        """Crear la interfaz del dashboard"""
        
        # Scroll area principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape. NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS['slate_50']};
                border: none;
            }}
        """)
        
        # Container principal
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(32, 32, 32, 32)
        
        # === FILTROS DE FECHA (ARRIBA) ===
        filters_section = self._create_filters_section()
        main_layout.addWidget(filters_section)
        
        # === FILA 1: RESUMEN FINANCIERO + RENDIMIENTO ===
        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(24)
        
        # Resumen Financiero
        self.financial_section = self._create_financial_summary()
        top_row_layout.addWidget(self.financial_section, stretch=2)
        
        # ✅ Card de Rendimiento (con parent explícito)
        self.rendimiento_card = RendimientoCard(parent=self)  # ← AGREGAR parent=self
        self.rendimiento_card.setMinimumWidth(400)
        top_row_layout.addWidget(self.rendimiento_card, stretch=1)
        
        main_layout.addLayout(top_row_layout)
        
        # === CUENTAS BANCARIAS ===
        self.accounts_section = self._create_accounts_section()
        main_layout.addWidget(self. accounts_section)
        
        # === GASTOS POR CATEGORÍA + INGRESOS VS GASTOS ===
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(24)
        
        self.categories_section = self._create_categories_section()
        bottom_layout.addWidget(self.categories_section, stretch=1)
        
        self.income_expenses_section = self._create_income_expenses_section()
        bottom_layout.addWidget(self.income_expenses_section, stretch=1)
        
        main_layout.addLayout(bottom_layout)
        main_layout.addStretch()
        
        scroll.setWidget(container)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
    
    # ==================== FILTROS ====================
    
    def _create_filters_section(self) -> QWidget:
        """Crear sección de filtros de fecha"""
        
        section = QWidget()
        section_layout = QHBoxLayout(section)
        section_layout.setSpacing(16)
        section_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title = QLabel("📅 Período:")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_700']};")
        section_layout.addWidget(title)
        
        # Botón mes anterior
        self.btn_prev_month = QPushButton("◀")
        self.btn_prev_month.setFixedSize(36, 36)
        self.btn_prev_month.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev_month.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['slate_100']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
                color: {COLORS['slate_700']};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['slate_200']};
            }}
        """)
        self.btn_prev_month.clicked.connect(self._go_prev_month)
        section_layout.addWidget(self.btn_prev_month)
        
        # Selector de mes
        self.combo_month = QComboBox()
        self.combo_month. addItems([
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ])
        self.combo_month.setCurrentIndex(self.current_month - 1)
        self.combo_month. setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
                padding: 8px 12px;
                min-width: 120px;
                font-size: 13px;
                color: {COLORS['slate_800']};
            }}
            QComboBox: hover {{
                border-color: {COLORS['slate_300']};
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
        """)
        self.combo_month.currentIndexChanged.connect(self._on_filter_changed)
        section_layout.addWidget(self.combo_month)
        
        # Selector de año
        self.combo_year = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 2):
            self.combo_year.addItem(str(year), year)
        
        # Seleccionar año actual
        index = self.combo_year.findData(self.current_year)
        if index >= 0:
            self.combo_year.setCurrentIndex(index)
        
        self.combo_year.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_200']};
                border-radius:  {BORDER['radius_sm']}px;
                padding: 8px 12px;
                min-width: 100px;
                font-size: 13px;
                color: {COLORS['slate_800']};
            }}
            QComboBox:hover {{
                border-color: {COLORS['slate_300']};
            }}
        """)
        self.combo_year.currentIndexChanged.connect(self._on_filter_changed)
        section_layout.addWidget(self.combo_year)
        
        # Botón mes siguiente
        self.btn_next_month = QPushButton("▶")
        self.btn_next_month.setFixedSize(36, 36)
        self.btn_next_month. setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next_month.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['slate_100']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
                color: {COLORS['slate_700']};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['slate_200']};
            }}
        """)
        self.btn_next_month. clicked.connect(self._go_next_month)
        section_layout.addWidget(self.btn_next_month)
        
        section_layout.addSpacing(20)
        
        # Botón "Mes Actual"
        btn_current = QPushButton("Hoy")
        btn_current. setCursor(Qt.CursorShape.PointingHandCursor)
        btn_current.setStyleSheet(f"""
            QPushButton {{
                background-color:  {COLORS['blue_600']};
                color: {COLORS['white']};
                border: none;
                border-radius: {BORDER['radius_sm']}px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['blue_700']};
            }}
        """)
        btn_current.clicked.connect(self._go_current_month)
        section_layout.addWidget(btn_current)
        
        section_layout. addStretch()
        
        # Indicador de datos
        self.data_indicator = QLabel("● Con datos")
        self.data_indicator. setStyleSheet(f"color:  {COLORS['green_600']}; font-size: 12px; font-weight: 500;")
        section_layout.addWidget(self.data_indicator)
        
        return section
    
    def _go_prev_month(self):
        """Ir al mes anterior"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        
        self._update_filter_ui()
        self.refresh()
    
    def _go_next_month(self):
        """Ir al mes siguiente"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        
        self._update_filter_ui()
        self.refresh()
    
    def _go_current_month(self):
        """Ir al mes actual"""
        self.current_year = datetime.now().year
        self.current_month = datetime. now().month
        
        self._update_filter_ui()
        self.refresh()
    
    def _on_filter_changed(self):
        """Callback cuando cambian los filtros"""
        self. current_month = self.combo_month.currentIndex() + 1
        self.current_year = self.combo_year.currentData()
        
        logger.info(f"Filter changed to: {self.current_year}-{self.current_month:02d}")
        self.refresh()
    
    def _update_filter_ui(self):
        """Actualizar UI de filtros sin triggear eventos"""
        self.combo_month.blockSignals(True)
        self.combo_year.blockSignals(True)
        
        self.combo_month.setCurrentIndex(self.current_month - 1)
        
        index = self.combo_year.findData(self.current_year)
        if index >= 0:
            self.combo_year. setCurrentIndex(index)
        
        self.combo_month. blockSignals(False)
        self.combo_year.blockSignals(False)
    
    def _detect_last_month_with_data(self):
        """Detectar el último mes con datos y usarlo como default"""
        try:
            # Obtener rango de fechas de transacciones
            fecha_min, fecha_max = self. firebase_client.get_rango_fechas_transacciones_gasto(
                self.proyecto_id
            )
            
            if fecha_max: 
                self.current_year = fecha_max.year
                self.current_month = fecha_max.month
                logger.info(f"Last month with data: {self.current_year}-{self.current_month:02d}")
                self._update_filter_ui()
            
        except Exception as e:
            logger.warning(f"Could not detect last month with data: {e}")
    
    def _get_selected_period(self) -> tuple[date, date]:
        """Obtener período seleccionado (primer y último día del mes)"""
        year = self.current_year
        month = self.current_month
        
        primer_dia = date(year, month, 1)
        ultimo_dia = date(year, month, monthrange(year, month)[1])
        
        return primer_dia, ultimo_dia
    
    # ==================== SECCIONES UI ====================
    
    def _create_financial_summary(self) -> QWidget:
        """Crear sección de resumen financiero"""
        
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(16)
        section_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title = QLabel("💰 Resumen Financiero")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color:  {COLORS['slate_900']};")
        section_layout.addWidget(title)
        
        # Cards layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        # Card 1: Capital Total
        self.card_capital = self._create_metric_card(
            icon="wallet",
            label="Capital Total",
            value="RD$ 0.00",
            subtitle="Todas las cuentas",
            color=COLORS['blue_600']
        )
        cards_layout.addWidget(self.card_capital)
        
        # Card 2: Ingresos del Mes
        self.card_ingresos = self._create_metric_card(
            icon="trending-up",
            label="Ingresos del Mes",
            value="RD$ 0.00",
            subtitle=self._get_current_month_name(),
            color=COLORS['green_600']
        )
        cards_layout.addWidget(self.card_ingresos)
        
        # Card 3: Gastos del Mes
        self.card_gastos = self._create_metric_card(
            icon="trending-down",
            label="Gastos del Mes",
            value="RD$ 0.00",
            subtitle=self._get_current_month_name(),
            color=COLORS['red_600']
        )
        cards_layout.addWidget(self.card_gastos)
        
        # Card 4: Balance
        self.card_balance = self._create_metric_card(
            icon="bar-chart-3",
            label="Balance",
            value="RD$ 0.00",
            subtitle="Ingresos - Gastos",
            color=COLORS['slate_700']
        )
        cards_layout.addWidget(self.card_balance)
        
        section_layout.addLayout(cards_layout)
        
        return section
    
    def _create_accounts_section(self) -> QWidget:
        """Crear sección de cuentas bancarias"""
        
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(16)
        section_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🏦 Cuentas Bancarias")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        section_layout.addLayout(header_layout)
        
        # Container de cuentas
        self.accounts_container = QHBoxLayout()
        self.accounts_container.setSpacing(16)
        section_layout.addLayout(self. accounts_container)
        
        return section
    
    def _create_categories_section(self) -> QWidget:
        """Crear sección de gastos por categoría"""
        
        card = CleanCard(padding=24)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        
        # Header
        title = QLabel("📊 Gastos por Categoría")
        title_font = QFont()
        title_font. setPointSize(14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color:  {COLORS['slate_900']};")
        card_layout.addWidget(title)
        
        # Subtitle con mes actual
        self.categories_subtitle = QLabel(self._get_current_month_name())
        self.categories_subtitle.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 12px;")
        card_layout.addWidget(self.categories_subtitle)
        
        # Container de categorías
        self.categories_container = QVBoxLayout()
        self.categories_container.setSpacing(12)
        card_layout.addLayout(self.categories_container)
        
        card_layout.addStretch()
        
        return card
    
    def _create_income_expenses_section(self) -> QWidget:
        """Crear sección de ingresos vs gastos"""
        
        card = CleanCard(padding=24)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        
        # Header
        title = QLabel("💹 Ingresos vs Gastos")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']};")
        card_layout.addWidget(title)
        
        # Subtitle
        self.income_subtitle = QLabel(self._get_current_month_name())
        self.income_subtitle.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 12px;")
        card_layout.addWidget(self.income_subtitle)
        
        # Ingresos
        ing_layout = QVBoxLayout()
        ing_layout.setSpacing(4)
        
        ing_label = QLabel("Ingresos")
        ing_label.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 11px; font-weight: 500;")
        ing_layout. addWidget(ing_label)
        
        self.ing_amount = QLabel("RD$ 0.00")
        self.ing_amount.setStyleSheet(f"color: {COLORS['green_600']}; font-size: 18px; font-weight: bold;")
        ing_layout. addWidget(self.ing_amount)
        
        card_layout.addLayout(ing_layout)
        
        # Gastos
        gas_layout = QVBoxLayout()
        gas_layout.setSpacing(4)
        
        gas_label = QLabel("Gastos")
        gas_label.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 11px; font-weight: 500;")
        gas_layout.addWidget(gas_label)
        
        self. gas_amount = QLabel("RD$ 0.00")
        self.gas_amount.setStyleSheet(f"color: {COLORS['red_600']}; font-size: 18px; font-weight: bold;")
        gas_layout.addWidget(self.gas_amount)
        
        card_layout.addLayout(gas_layout)
        
        # Balance
        bal_layout = QVBoxLayout()
        bal_layout.setSpacing(4)
        
        bal_label = QLabel("Balance Neto")
        bal_label.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 11px; font-weight: 500;")
        bal_layout.addWidget(bal_label)
        
        self.bal_amount = QLabel("RD$ 0.00")
        self.bal_amount.setStyleSheet(f"color: {COLORS['slate_900']}; font-size: 18px; font-weight: bold;")
        bal_layout. addWidget(self.bal_amount)
        
        card_layout.addLayout(bal_layout)
        
        card_layout. addStretch()
        
        return card
    
    def _create_metric_card(self, icon: str, label: str, value: str, 
                           subtitle: str, color: str) -> CleanCard:
        """Crear card de métrica financiera"""
        
        card = CleanCard(padding=20)
        card.setMinimumHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Header con icono
        header_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_pixmap = icon_manager.get_pixmap(icon, color, 24)
        icon_label.setPixmap(icon_pixmap)
        header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            color: {COLORS['slate_600']};
            font-size: 12px;
            font-weight:  500;
        """)
        layout.addWidget(label_widget)
        
        # Value
        value_widget = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setWeight(QFont.Weight.Bold)
        value_widget.setFont(value_font)
        value_widget.setStyleSheet(f"color: {COLORS['slate_900']};")
        layout.addWidget(value_widget)
        
        # Subtitle
        subtitle_widget = QLabel(subtitle)
        subtitle_widget.setStyleSheet(f"""
            color: {COLORS['slate_500']};
            font-size: 11px;
        """)
        layout.addWidget(subtitle_widget)
        
        layout.addStretch()
        
        # Guardar referencias
        card.value_label = value_widget
        card. subtitle_label = subtitle_widget
        
        return card
    
    # ==================== MÉTODOS DE DATOS ====================
    
    def refresh(self):
        """Recargar todos los datos del dashboard"""
        if not self. firebase_client or not self.proyecto_id:
            logger.warning("Cannot refresh: missing firebase_client or proyecto_id")
            return
        
        logger.info(f"Refreshing dashboard for {self.current_year}-{self.current_month:02d}")
        
        try:
            # ✅ CRÍTICO: Cargar datos del proyecto PRIMERO
            self._load_project_data()
            
            # 1. Cargar cuentas
            self._load_accounts()
            
            # 2. Calcular resumen financiero
            self._calculate_financial_summary()
            
            # 3. Cargar gastos por categoría
            self._load_category_expenses()
            
            # 4. Cargar ingresos vs gastos
            self._load_income_vs_expenses()
            
            # 5. Actualizar UI
            self._update_ui()
            
            # 6. Actualizar indicador de datos
            self._update_data_indicator()
            
            # 7. ✅ AHORA SÍ:  Calcular y actualizar rendimiento (con datos cargados)
            self._update_rendimiento_card()
            
            logger.info("✅ Dashboard refreshed successfully")
            
        except Exception as e: 
            logger.error(f"Error refreshing dashboard: {e}", exc_info=True)
    
    def _load_accounts(self):
        """Cargar cuentas del proyecto"""
        try:
            self._cuentas = self.firebase_client.get_cuentas_por_proyecto(self.proyecto_id) or []
            logger.info(f"Loaded {len(self._cuentas)} accounts")
        except Exception as e: 
            logger.error(f"Error loading accounts: {e}")
            self._cuentas = []
    
    def _calculate_financial_summary(self):
        """Calcular resumen financiero del período seleccionado"""
        try:
            primer_dia, ultimo_dia = self._get_selected_period()
            
            # Obtener ingresos
            ingresos_data = self.firebase_client.get_agrupado_ingresos_por_mes(
                self. proyecto_id, primer_dia, ultimo_dia, None
            ) or []
            
            total_ingresos = sum(float(item. get('monto', 0)) for item in ingresos_data 
                               if not item.get('es_transferencia'))
            
            # Obtener gastos
            gastos_data = self.firebase_client.get_agrupado_gastos_por_mes(
                self. proyecto_id, primer_dia, ultimo_dia, None
            ) or []
            
            total_gastos = sum(float(item.get('monto', 0)) for item in gastos_data 
                             if not item.get('es_transferencia'))
            
            # Capital total
            capital_total = sum(float(cuenta.get('saldo', 0)) for cuenta in self._cuentas)
            
            self._resumen_financiero = {
                'capital_total': capital_total,
                'ingresos_mes': total_ingresos,
                'gastos_mes': total_gastos,
                'balance':  total_ingresos - total_gastos
            }
            
            logger. info(f"Financial summary:  {self._resumen_financiero}")
            
        except Exception as e:
            logger.error(f"Error calculating financial summary: {e}")
            self._resumen_financiero = {
                'capital_total': 0,
                'ingresos_mes':  0,
                'gastos_mes': 0,
                'balance': 0
            }
    
    def _load_category_expenses(self):
        """Cargar gastos por categoría del período seleccionado"""
        try:
            primer_dia, ultimo_dia = self._get_selected_period()
            
            self._gastos_categoria = self.firebase_client.get_gastos_agrupados_por_categoria(
                self.proyecto_id, primer_dia, ultimo_dia, None
            ) or []
            
            # Filtrar transferencias
            self._gastos_categoria = [
                cat for cat in self._gastos_categoria 
                if cat.get('categoria') not in ['0', 0, None]
            ]
            
            # Ordenar por monto descendente y tomar top 5
            self._gastos_categoria = sorted(
                self._gastos_categoria,
                key=lambda x: float(x.get('total_gastado', 0)),
                reverse=True
            )[:5]
            
            logger.info(f"Loaded {len(self._gastos_categoria)} category expenses")
            
        except Exception as e:
            logger.error(f"Error loading category expenses:  {e}")
            self._gastos_categoria = []
    
    def _load_income_vs_expenses(self):
        """Cargar datos de ingresos vs gastos"""
        self._ingresos_gastos_mes = {
            'ingresos': self._resumen_financiero. get('ingresos_mes', 0),
            'gastos': self._resumen_financiero.get('gastos_mes', 0),
            'balance':  self._resumen_financiero. get('balance', 0)
        }
    
    def _update_ui(self):
        """Actualizar todos los elementos visuales"""
        
        # Actualizar mes mostrado en cards
        month_name = self._get_current_month_name()
        self.card_ingresos.subtitle_label.setText(month_name)
        self.card_gastos.subtitle_label. setText(month_name)
        self.categories_subtitle.setText(month_name)
        self.income_subtitle.setText(month_name)
        
        # Actualizar datos
        self._update_financial_cards()
        self._update_accounts_display()
        self._update_categories_display()
        self._update_income_expenses_display()
    
    def _update_data_indicator(self):
        """Actualizar indicador de datos"""
        has_data = (
            self._resumen_financiero.get('ingresos_mes', 0) > 0 or 
            self._resumen_financiero.get('gastos_mes', 0) > 0
        )
        
        if has_data:
            self.data_indicator.setText("● Con datos")
            self.data_indicator.setStyleSheet(f"color: {COLORS['green_600']}; font-size: 12px; font-weight: 500;")
        else:
            self. data_indicator.setText("● Sin datos")
            self.data_indicator.setStyleSheet(f"color: {COLORS['slate_400']}; font-size: 12px; font-weight: 500;")
    
    def _update_financial_cards(self):
        """Actualizar los 4 cards de resumen financiero"""
        
        capital = self._resumen_financiero. get('capital_total', 0)
        ingresos = self._resumen_financiero.get('ingresos_mes', 0)
        gastos = self._resumen_financiero.get('gastos_mes', 0)
        balance = self._resumen_financiero.get('balance', 0)
        
        self.card_capital.value_label.setText(self._format_currency(capital))
        self.card_ingresos.value_label.setText(self._format_currency(ingresos))
        self.card_gastos.value_label.setText(self._format_currency(gastos))
        self.card_balance.value_label.setText(self._format_currency(balance))
        
        # Cambiar color del balance
        if balance >= 0:
            self.card_balance.value_label.setStyleSheet(f"color: {COLORS['green_600']}; font-size: 18px; font-weight: bold;")
        else:
            self.card_balance. value_label.setStyleSheet(f"color: {COLORS['red_600']}; font-size: 18px; font-weight: bold;")
    
    def _update_accounts_display(self):
        """Actualizar visualización de cuentas"""
        
        # Limpiar container
        self._clear_layout(self.accounts_container)
        
        if not self._cuentas:
            empty_label = QLabel("No hay cuentas registradas")
            empty_label. setStyleSheet(f"color: {COLORS['slate_400']};")
            self.accounts_container.addWidget(empty_label)
            return
        
        # Agregar cards de cuentas (máximo 4)
        for cuenta in self._cuentas[:4]:
            account_card = self._create_account_card(cuenta)
            self.accounts_container.addWidget(account_card)
        
        self. accounts_container.addStretch()
    
    def _update_categories_display(self):
        """Actualizar visualización de categorías"""
        
        # Limpiar container
        self._clear_layout(self.categories_container)
        
        if not self._gastos_categoria:
            empty_label = QLabel("No hay gastos registrados")
            empty_label. setStyleSheet(f"color:  {COLORS['slate_400']};")
            self.categories_container.addWidget(empty_label)
            return
        
        # Calcular total para porcentajes
        total_gastos = sum(float(cat.get('total_gastado', 0)) for cat in self._gastos_categoria)
        
        # Agregar barras de categorías
        for cat in self._gastos_categoria:
            category_widget = self._create_category_bar(cat, total_gastos)
            self.categories_container.addWidget(category_widget)
    
    def _update_income_expenses_display(self):
        """Actualizar visualización de ingresos vs gastos"""
        
        ingresos = self._ingresos_gastos_mes. get('ingresos', 0)
        gastos = self._ingresos_gastos_mes.get('gastos', 0)
        balance = self._ingresos_gastos_mes. get('balance', 0)
        
        self.ing_amount.setText(self._format_currency(ingresos))
        self.gas_amount.setText(self._format_currency(gastos))
        self.bal_amount.setText(self._format_currency(balance))
        
        # Color del balance
        if balance >= 0:
            self.bal_amount.setStyleSheet(f"color: {COLORS['green_600']}; font-size: 18px; font-weight: bold;")
        else:
            self.bal_amount.setStyleSheet(f"color: {COLORS['red_600']}; font-size: 18px; font-weight: bold;")
    
    def _update_rendimiento_card(self):
        """Actualizar card de rendimiento del proyecto"""
        
        if not self.current_project_data:
            logger.warning("No project data available for rendimiento calculation")
            self.rendimiento_card.update_metricas(None)
            return
        
        try: 
            # ✅ Intentar usar rendimiento guardado primero
            rendimiento_guardado = self._get_rendimiento_from_cache()
            
            if rendimiento_guardado: 
                # Importar aquí para calcular mensajes
                from services.rendimiento_calculator import RendimientoCalculator
                
                # Reconstruir métricas desde cache
                metricas = {
                    # Valores principales
                    'rendimiento_global': rendimiento_guardado['rendimiento_global'],
                    'rendimiento_financiero': rendimiento_guardado['rendimiento_financiero'],
                    'rendimiento_temporal': rendimiento_guardado['rendimiento_temporal'],
                    
                    # Estados (reconstruir dict completo)
                    'estado_global': {
                        'emoji': self._get_emoji_for_estado(rendimiento_guardado. get('estado_global', '')),
                        'descripcion':  rendimiento_guardado.get('estado_global', 'Desconocido'),
                        'color': self._get_color_for_estado(rendimiento_guardado.get('estado_global', ''))
                    },
                    'estado_financiero': {
                        'emoji': self._get_emoji_for_estado(rendimiento_guardado.get('estado_financiero', '')),
                        'descripcion': rendimiento_guardado.get('estado_financiero', 'Desconocido'),
                        'color': self._get_color_for_estado(rendimiento_guardado.get('estado_financiero', ''))
                    },
                    'estado_temporal': {
                        'emoji': self._get_emoji_for_estado(rendimiento_guardado.get('estado_temporal', '')),
                        'descripcion': rendimiento_guardado. get('estado_temporal', 'Desconocido'),
                        'color': self._get_color_for_estado(rendimiento_guardado.get('estado_temporal', ''))
                    },
                    
                    # Datos base
                    'avance_fisico': self. current_project_data.get('avance_fisico', 0),
                    'avance_financiero': rendimiento_guardado.get('avance_financiero', 0),
                    'porcentaje_tiempo': rendimiento_guardado.get('porcentaje_tiempo', 0),
                    'presupuesto_total': self.current_project_data.get('presupuesto_total', 0),
                    'gastado_total': rendimiento_guardado.get('gastado_total', 0),
                    
                    # Proyecciones
                    'proyeccion_gasto_final': rendimiento_guardado.get('proyeccion_gasto_final', 0),
                    'sobrecosto_estimado': rendimiento_guardado.get('sobrecosto_estimado', 0),
                    'porcentaje_sobrecosto': rendimiento_guardado.get('porcentaje_sobrecosto', 0),
                    'meses_proyectados_totales': rendimiento_guardado.get('meses_proyectados_totales', 0),
                    'retraso_estimado_meses': rendimiento_guardado.get('retraso_estimado_meses', 0),
                }
                
                # ✅ CALCULAR MENSAJES AQUÍ (no en el card)
                metricas['mensaje_financiero'] = RendimientoCalculator.get_mensaje_rendimiento_financiero(
                    metricas['rendimiento_financiero'],
                    metricas['avance_fisico'],
                    metricas['avance_financiero']
                )
                
                metricas['mensaje_temporal'] = RendimientoCalculator. get_mensaje_rendimiento_temporal(
                    metricas['rendimiento_temporal'],
                    metricas['avance_fisico'],
                    metricas['porcentaje_tiempo']
                )
                
                logger.info(f"📊 Rendimiento desde cache: Global={metricas['rendimiento_global']:.1f}%, "
                          f"Financiero={metricas['rendimiento_financiero']:.1f}%, "
                          f"Temporal={metricas['rendimiento_temporal']:.1f}%")
            else:
                # ✅ FALLBACK:  Calcular en tiempo real
                logger.info("Calculando rendimiento en tiempo real...")
                
                from services.rendimiento_calculator import RendimientoCalculator
                
                # PASO 1: Calcular gastado_total
                gastado_total = self._calcular_gastado_total()
                
                # PASO 2: Parsear fecha_inicio
                fecha_inicio_str = self. current_project_data.get('fecha_inicio', '')
                try:
                    if fecha_inicio_str:
                        fecha_inicio_date = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                    else: 
                        fecha_inicio_date = date.today()
                except Exception as e:
                    logger. warning(f"Error parseando fecha_inicio: {e}")
                    fecha_inicio_date = date.today()
                
                # PASO 3: Llamar al calculador
                metricas = RendimientoCalculator. calcular_rendimiento_completo(
                    avance_fisico=self.current_project_data.get('avance_fisico', 0),
                    presupuesto_total=self. current_project_data.get('presupuesto_total', 0),
                    gastado_total=gastado_total,
                    fecha_inicio=fecha_inicio_date,
                    duracion_meses=self.current_project_data.get('duracion_meses', 6)
                )
                
                if not metricas:
                    logger.info("No sufficient data for rendimiento (avance=0, presupuesto=0)")
                    self.rendimiento_card.update_metricas(None)
                    return
                
                # ✅ CALCULAR MENSAJES AQUÍ (no en el card)
                metricas['mensaje_financiero'] = RendimientoCalculator.get_mensaje_rendimiento_financiero(
                    metricas['rendimiento_financiero'],
                    metricas['avance_fisico'],
                    metricas['avance_financiero']
                )
                
                metricas['mensaje_temporal'] = RendimientoCalculator.get_mensaje_rendimiento_temporal(
                    metricas['rendimiento_temporal'],
                    metricas['avance_fisico'],
                    metricas['porcentaje_tiempo']
                )
                
                logger.info(f"Rendimiento calculado: Global={metricas['rendimiento_global']:.1f}%, "
                        f"Financiero={metricas['rendimiento_financiero']:.1f}%, "  # ✅ SIN ESPACIO
                        f"Temporal={metricas['rendimiento_temporal']:.1f}%")
            
            # ✅ ENVIAR AL CARD CON MENSAJES YA CALCULADOS
            logger.info(f"🎯 ENVIANDO métricas al card:")
            logger.info(f"   - rendimiento_global: {metricas['rendimiento_global']}")
            logger.info(f"   - rendimiento_financiero:  {metricas['rendimiento_financiero']}")
            logger. info(f"   - rendimiento_temporal: {metricas['rendimiento_temporal']}")
            logger.info(f"   - mensaje_financiero: {metricas['mensaje_financiero']}")
            logger.info(f"   - mensaje_temporal: {metricas['mensaje_temporal']}")
            
            # Actualizar card
            self.rendimiento_card.update_metricas(metricas)
            
        except ImportError as e:
            logger. error(f"Error importando RendimientoCalculator: {e}", exc_info=True)
            self. rendimiento_card.update_metricas(None)
        except Exception as e:
            logger. error(f"Error calculating rendimiento: {e}", exc_info=True)
            self.rendimiento_card.update_metricas(None)
            
                
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
            
            return total
            
        except Exception as e:
            logger. error(f"Error calculating gastado_total: {e}")
            return 0.0
    
    def _get_fecha_primera_transaccion(self):
        """Obtener la fecha de la primera transacción del proyecto"""
        
        if not self.firebase_client or not self.proyecto_id:
            return None
        
        try: 
            transacciones = self.firebase_client.get_transacciones_by_proyecto(
                self.proyecto_id,
                cuenta_id=None
            )
            
            fecha_primera = None
            
            for trans in transacciones: 
                if hasattr(trans, 'to_dict'):
                    data = trans.to_dict() or {}
                else: 
                    data = trans
                
                estado = data.get('estado', 'activa')
                if estado == 'anulada': 
                    continue
                
                fecha = data.get('fecha')
                if fecha:
                    # Convertir a date
                    if isinstance(fecha, str):
                        try:
                            fecha = datetime. strptime(fecha, '%Y-%m-%d').date()
                        except:
                            try:
                                fecha = datetime. fromisoformat(fecha).date()
                            except:
                                continue
                    elif hasattr(fecha, 'date'):
                        fecha = fecha.date()
                    
                    if fecha_primera is None or fecha < fecha_primera:
                        fecha_primera = fecha
            
            return fecha_primera
            
        except Exception as e:
            logger.error(f"Error getting fecha_primera_transaccion: {e}")
            return None
    
    def _create_account_card(self, account:  Dict[str, Any]) -> CleanCard:
        """Crear card de cuenta bancaria"""
        
        card = CleanCard(padding=16)
        card.setMinimumHeight(140)
        card.setMinimumWidth(200)
        card.setCursor(Qt.CursorShape. PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Icono banco
        icon_layout = QHBoxLayout()
        bank_icon = QLabel()
        bank_pixmap = icon_manager.get_pixmap('building-2', COLORS['blue_600'], 32)
        bank_icon.setPixmap(bank_pixmap)
        icon_layout.addWidget(bank_icon)
        icon_layout.addStretch()
        layout.addLayout(icon_layout)
        
        # Nombre cuenta
        nombre = account.get('nombre', 'Sin nombre')
        nombre_label = QLabel(nombre)
        nombre_font = QFont()
        nombre_font.setPointSize(12)
        nombre_font.setWeight(QFont.Weight.Bold)
        nombre_label.setFont(nombre_font)
        nombre_label.setStyleSheet(f"color: {COLORS['slate_900']};")
        nombre_label.setWordWrap(True)
        layout.addWidget(nombre_label)
        
        # Saldo
        saldo = float(account.get('saldo', 0))
        saldo_label = QLabel(self._format_currency(saldo))
        saldo_font = QFont()
        saldo_font.setPointSize(16)
        saldo_font. setWeight(QFont.Weight. Bold)
        saldo_label.setFont(saldo_font)
        
        # Color según saldo
        if saldo >= 0:
            saldo_label.setStyleSheet(f"color: {COLORS['green_600']};")
        else:
            saldo_label.setStyleSheet(f"color: {COLORS['red_600']};")
        
        layout.addWidget(saldo_label)
        
        # Estado
        estado = account.get('estado', 'activa')
        estado_label = QLabel(f"● {estado. capitalize()}")
        estado_label.setStyleSheet(f"color: {COLORS['green_600']}; font-size: 11px;")
        layout.addWidget(estado_label)
        
        layout.addStretch()
        
        # Click handler
        cuenta_id = str(account.get('id', ''))
        card.mousePressEvent = lambda e: self. account_clicked. emit(cuenta_id)
        
        return card
    
    def _create_category_bar(self, category: Dict[str, Any], total: float) -> QWidget:
        """Crear barra de categoría con progreso"""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Nombre y monto
        top_layout = QHBoxLayout()
        
        nombre = category.get('nombre') or category.get('categoria', 'Sin categoría')
        nombre_label = QLabel(str(nombre))
        nombre_label.setStyleSheet(f"color: {COLORS['slate_700']}; font-size: 12px; font-weight: 500;")
        top_layout.addWidget(nombre_label)
        
        top_layout.addStretch()
        
        monto = float(category.get('total_gastado', 0))
        monto_label = QLabel(self._format_currency(monto))
        monto_label.setStyleSheet(f"color: {COLORS['slate_900']}; font-size: 12px; font-weight: 600;")
        top_layout. addWidget(monto_label)
        
        layout.addLayout(top_layout)
        
        # Barra de progreso
        progress = QProgressBar()
        progress.setFixedHeight(8)
        progress.setTextVisible(False)
        
        percentage = int((monto / total * 100)) if total > 0 else 0
        progress.setValue(percentage)
        
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {COLORS['slate_200']};
            }}
            QProgressBar::chunk {{
                border-radius: 4px;
                background-color: {COLORS['blue_500']};
            }}
        """)
        
        layout.addWidget(progress)
        
        # Porcentaje
        pct_label = QLabel(f"{percentage}%")
        pct_label.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 10px;")
        layout.addWidget(pct_label)
        
        return widget
    
    # ==================== UTILIDADES ====================
    
    def _format_currency(self, amount: float) -> str:
        """Formatear monto como moneda"""
        return f"RD$ {amount: ,.2f}"
    
    def _get_current_month_name(self) -> str:
        """Obtener nombre del mes seleccionado"""
        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        return months[self.current_month - 1]
    
    def _clear_layout(self, layout):
        """Limpiar todos los widgets de un layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child. widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

