"""
ObrasPage - Gestión de proyectos de construcción

Vista híbrida (Cards + Lista) con avance físico y financiero.  
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QLineEdit, QComboBox, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QAction

from .. components.clean_card import CleanCard
from ..components.icon_manager import icon_manager
from ..theme_config import COLORS, BORDER

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ObrasPage(QWidget):
    """
    Página de gestión de obras/proyectos. 
    
    Funcionalidades:
    - Vista Cards y Lista (toggle)
    - Filtros por estado
    - Búsqueda
    - Avance físico (manual) + financiero (automático)
    - Estados:  Activo, Pausado, Completado
    - Fecha de inicio real (primera transacción)
    - Botones:  Dashboard y + Transacción
    """
    
    project_selected = pyqtSignal(str, str)  # (proyecto_id, proyecto_nombre)
    
    def __init__(self, firebase_client=None, parent=None):
        super().__init__(parent)
        
        self.firebase_client = firebase_client
        
        # Estado de la vista
        self.view_mode = "cards"  # "cards" | "list"
        self.filter_estado = "todos"  # "todos" | "activo" | "pausado" | "completado"
        self.search_text = ""
        
        # Cache de datos
        self._proyectos = []
        self._gastos_por_proyecto = {}  # {proyecto_id: gastado_total}
        self._fechas_inicio_real = {}  # {proyecto_id: fecha_primera_transaccion}
        
        self.setup_ui()
        
        # Cargar datos iniciales
        if self.firebase_client:
            self.refresh()
    
    def setup_ui(self):
        """Crear interfaz de la página"""
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(32, 32, 32, 32)
        
        # === HEADER CON CONTROLES ===
        header = self._create_header()
        main_layout.addWidget(header)
        
        # === RESUMEN GLOBAL ===
        self. summary_section = self._create_summary()
        main_layout.addWidget(self.summary_section)
        
        # === CONTENEDOR DE VISTAS (Cards o Lista) ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape. NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS['slate_50']};
                border:  none;
            }}
        """)
        
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self. content_container)
        self.content_layout.setSpacing(16)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.content_container)
        main_layout.addWidget(scroll)
    
    def _create_header(self) -> QWidget:
        """Crear header con controles"""
        
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setSpacing(16)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title = QLabel("🏗️ Gestión de Obras")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Toggle Vista
        self.btn_view_cards = QPushButton("🔲 Cards")
        self.btn_view_cards.setCheckable(True)
        self.btn_view_cards.setChecked(True)
        self.btn_view_cards.clicked.connect(lambda: self._change_view("cards"))
        
        self.btn_view_list = QPushButton("☰ Lista")
        self.btn_view_list.setCheckable(True)
        self.btn_view_list.clicked.connect(lambda: self._change_view("list"))
        
        for btn in [self.btn_view_cards, self.btn_view_list]:
            btn.setCursor(Qt.CursorShape. PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['slate_100']};
                    border: 1px solid {COLORS['slate_200']};
                    border-radius: {BORDER['radius_sm']}px;
                    padding: 8px 16px;
                    color: {COLORS['slate_700']};
                    font-weight: 600;
                }}
                QPushButton:checked {{
                    background-color:  {COLORS['blue_600']};
                    color: {COLORS['white']};
                    border-color: {COLORS['blue_600']};
                }}
                QPushButton:hover {{
                    background-color: {COLORS['slate_200']};
                }}
                QPushButton:checked:hover {{
                    background-color: {COLORS['blue_700']};
                }}
            """)
        
        header_layout.addWidget(self.btn_view_cards)
        header_layout.addWidget(self.btn_view_list)
        header_layout.addSpacing(16)
        
        # Filtro por estado
        self.combo_filter = QComboBox()
        self.combo_filter.addItems(["Todos", "Activos", "Pausados", "Completados"])
        self.combo_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
                padding: 8px 12px;
                min-width: 120px;
                color: {COLORS['slate_800']};
            }}
        """)
        self.combo_filter.currentTextChanged.connect(self._on_filter_changed)
        header_layout.addWidget(self. combo_filter)
        
        # Búsqueda
        search_container = QWidget()
        search_container. setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
            }}
        """)
        
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 6, 12, 6)
        search_layout.setSpacing(8)
        
        search_icon = QLabel()
        search_icon.setPixmap(icon_manager.get_pixmap('search', COLORS['slate_400'], 16))
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar obras...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                border: none;
                color: {COLORS['slate_900']};
                font-size: 13px;
            }}
            QLineEdit:: placeholder {{
                color: {COLORS['slate_400']};
            }}
        """)
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)
        
        search_container.setFixedWidth(250)
        header_layout.addWidget(search_container)
        header_layout.addSpacing(16)
        
        # Botón Nueva Obra
        btn_new = QPushButton("+ Nueva Obra")
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.setStyleSheet(f"""
            QPushButton {{
                background-color:  {COLORS['blue_600']};
                color:  {COLORS['white']};
                border: none;
                border-radius: {BORDER['radius_sm']}px;
                padding: 10px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['blue_700']};
            }}
        """)
        btn_new.clicked.connect(self._open_new_obra_dialog)
        header_layout.addWidget(btn_new)
        
        return header
    
    def _create_summary(self) -> QWidget:
        """Crear sección de resumen global"""
        
        card = CleanCard(padding=20)
        layout = QHBoxLayout(card)
        layout.setSpacing(32)
        
        # Total proyectos
        self.label_total = self._create_summary_item("📊 Total Proyectos", "0", COLORS['slate_700'])
        layout.addWidget(self.label_total)
        
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet(f"background-color: {COLORS['slate_200']};")
        sep1.setFixedWidth(1)
        layout.addWidget(sep1)
        
        # Activos
        self.label_activos = self._create_summary_item("🟢 Activos", "0", COLORS['green_600'])
        layout.addWidget(self.label_activos)
        
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape. VLine)
        sep2.setStyleSheet(f"background-color: {COLORS['slate_200']};")
        sep2.setFixedWidth(1)
        layout.addWidget(sep2)
        
        # Pausados
        self.label_pausados = self._create_summary_item("🟡 Pausados", "0", COLORS['yellow_600'])
        layout.addWidget(self.label_pausados)
        
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.VLine)
        sep3.setStyleSheet(f"background-color: {COLORS['slate_200']};")
        sep3.setFixedWidth(1)
        layout.addWidget(sep3)
        
        # Completados
        self.label_completados = self._create_summary_item("✅ Completados", "0", COLORS['blue_600'])
        layout.addWidget(self.label_completados)
        
        layout.addStretch()
        
        return card
    
    def _create_summary_item(self, label: str, value: str, color: str) -> QWidget:
        """Crear item de resumen"""
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 12px; font-weight: 500;")
        layout.addWidget(label_widget)
        
        value_widget = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setWeight(QFont.Weight.Bold)
        value_widget.setFont(value_font)
        value_widget.setStyleSheet(f"color: {color};")
        
        container.value_label = value_widget
        layout. addWidget(value_widget)
        
        return container
    
    # ==================== CAMBIO DE VISTA ====================
    
    def _change_view(self, mode: str):
        """Cambiar entre vista de cards y lista"""
        self.view_mode = mode
        self.btn_view_cards.setChecked(mode == "cards")
        self.btn_view_list.setChecked(mode == "list")
        self._update_content_display()
    
    # ==================== FILTROS ====================
    
    def _on_filter_changed(self, text: str):
        """Callback cuando cambia el filtro de estado"""
        filter_map = {
            "Todos":  "todos",
            "Activos": "activo",
            "Pausados":  "pausado",
            "Completados": "completado"
        }
        self.filter_estado = filter_map.get(text, "todos")
        self._update_content_display()
    
    def _on_search_changed(self, text: str):
        """Callback cuando cambia el texto de búsqueda"""
        self.search_text = text. lower()
        self._update_content_display()
    
    # ==================== DATOS ====================
    
    def refresh(self):
        """Recargar datos desde Firebase"""
        if not self.firebase_client:
            logger.warning("No firebase_client configured")
            return
        
        logger.info("Refreshing obras page")
        
        try:
            self._load_proyectos()
            self._calculate_gastos()
            self._update_summary()
            self._update_content_display()
            logger.info("✅ Obras page refreshed successfully")
        except Exception as e:
            logger. error(f"Error refreshing obras page: {e}", exc_info=True)
    
    def _load_proyectos(self):
        """Cargar proyectos desde Firebase"""
        try:
            # ✅ Leer DIRECTAMENTE desde Firestore (sin usar get_proyectos)
            from firebase_admin import firestore
            db = firestore.client()
            
            proyectos_raw = db.collection('proyectos').stream()
            self._proyectos = []
            
            for p in proyectos_raw: 
                data = p.to_dict() or {}
                proyecto_id = p.id
                
                # ✅ AHORA SÍ debería leer el presupuesto_total
                presupuesto_raw = data.get('presupuesto_total')
                logger.info(f"Proyecto {proyecto_id}: presupuesto_raw = {presupuesto_raw} (type: {type(presupuesto_raw)})")
                
                try:
                    presupuesto_total = float(presupuesto_raw) if presupuesto_raw else 0.0
                except (ValueError, TypeError):
                    logger.warning(f"Proyecto {proyecto_id}: No se pudo convertir presupuesto '{presupuesto_raw}' a float")
                    presupuesto_total = 0.0
                
                proyecto = {
                    'id': str(proyecto_id),
                    'nombre': data.get('nombre', f'Proyecto {proyecto_id}'),
                    'descripcion': data.get('descripcion', ''),
                    'estado': data.get('estado', 'activo'),
                    'presupuesto_total': presupuesto_total,
                    'avance_fisico': int(data.get('avance_fisico', 0)),
                    'duracion_meses': int(data.get('duracion_meses', 6)),
                    'fecha_inicio': data.get('fecha_inicio', ''),
                    'fecha_fin_estimada': data.get('fecha_fin_estimada', ''),
                    'cliente': data.get('cliente', ''),
                    'ubicacion': data.get('ubicacion', ''),
                    'responsable': data.get('responsable', ''),
                    'imagen_url': data.get('imagen_url', ''),
                    'color': data.get('color', COLORS['blue_600']),
                    'notas': data.get('notas', ''),
                    'creado_en': data.get('creado_en'),
                    'actualizado_en': data.get('actualizado_en'),
                }
                self._proyectos.append(proyecto)
            
            logger.info(f"Loaded {len(self._proyectos)} proyectos")
        except Exception as e:
            logger.error(f"Error loading proyectos: {e}", exc_info=True)
            self._proyectos = []
    
    def _calculate_gastos(self):
        """Calcular gastado total y fecha de inicio real por proyecto"""
        self._gastos_por_proyecto = {}
        self._fechas_inicio_real = {}
        
        for proyecto in self._proyectos:
            proyecto_id = proyecto['id']
            
            try:
                transacciones = self.firebase_client. get_transacciones_by_proyecto(
                    proyecto_id, cuenta_id=None
                )
                
                total_gastado = 0.0
                fecha_primera_trans = None
                
                for trans in transacciones:
                    if hasattr(trans, 'to_dict'):
                        data = trans.to_dict() or {}
                    else:
                        data = trans
                    
                    tipo = data.get('tipo', '')
                    estado = data.get('estado', 'activa')
                    es_transferencia = data.get('es_transferencia', False)
                    
                    # Sumar gastos
                    if tipo == 'gasto' and estado != 'anulada' and not es_transferencia:
                        monto = float(data.get('monto', 0))
                        total_gastado += monto
                    
                    # Buscar fecha más antigua
                    if estado != 'anulada': 
                        fecha = data.get('fecha')
                        if fecha:
                            if isinstance(fecha, str):
                                try:
                                    from datetime import datetime
                                    fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
                                except: 
                                    try:
                                        fecha = datetime.fromisoformat(fecha).date()
                                    except:
                                        continue
                            elif hasattr(fecha, 'date'):
                                fecha = fecha.date()
                            
                            if fecha_primera_trans is None or fecha < fecha_primera_trans:
                                fecha_primera_trans = fecha
                
                self._gastos_por_proyecto[proyecto_id] = total_gastado
                self._fechas_inicio_real[proyecto_id] = fecha_primera_trans
            except Exception as e:
                logger. error(f"Error calculating gastos for proyecto {proyecto_id}: {e}")
                self._gastos_por_proyecto[proyecto_id] = 0.0
                self._fechas_inicio_real[proyecto_id] = None
        
        logger.info(f"Calculated gastos for {len(self._gastos_por_proyecto)} proyectos")
    
    # ==================== ACTUALIZACIÓN UI ====================
    
    def _update_summary(self):
        """Actualizar resumen global"""
        total = len(self._proyectos)
        activos = sum(1 for p in self._proyectos if p['estado'] == 'activo')
        pausados = sum(1 for p in self._proyectos if p['estado'] == 'pausado')
        completados = sum(1 for p in self._proyectos if p['estado'] == 'completado')
        
        self.label_total.value_label.setText(str(total))
        self.label_activos.value_label. setText(str(activos))
        self.label_pausados.value_label.setText(str(pausados))
        self.label_completados.value_label.setText(str(completados))
    
    def _update_content_display(self):
        """Actualizar contenido según vista y filtros"""
        self._clear_layout(self.content_layout)
        proyectos_filtrados = self._filter_proyectos()
        
        if not proyectos_filtrados: 
            empty_label = QLabel("No hay proyectos que coincidan con los filtros")
            empty_label.setStyleSheet(f"color: {COLORS['slate_400']}; font-size: 14px;")
            empty_label.setAlignment(Qt. AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(empty_label)
            self.content_layout.addStretch()
            return
        
        if self.view_mode == "cards":
            self._show_cards_view(proyectos_filtrados)
        else:
            self._show_list_view(proyectos_filtrados)
    
    def _filter_proyectos(self) -> List[Dict[str, Any]]:
        """Filtrar proyectos según estado y búsqueda"""
        filtered = []
        
        for proyecto in self._proyectos:
            if self.filter_estado != "todos": 
                if proyecto['estado'] != self.filter_estado:
                    continue
            
            if self.search_text:
                nombre = proyecto['nombre'].lower()
                descripcion = proyecto['descripcion'].lower()
                cliente = proyecto['cliente'].lower()
                
                if not (self.search_text in nombre or 
                       self.search_text in descripcion or 
                       self.search_text in cliente):
                    continue
            
            filtered.append(proyecto)
        
        return filtered
    
    def _show_cards_view(self, proyectos: List[Dict[str, Any]]):
        """Mostrar vista de cards"""
        grid = QGridLayout()
        grid.setSpacing(20)
        
        row = 0
        col = 0
        max_cols = 3
        
        for proyecto in proyectos:
            card = self._create_project_card(proyecto)
            grid.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        grid_widget = QWidget()
        grid_widget.setLayout(grid)
        self.content_layout. addWidget(grid_widget)
        self.content_layout.addStretch()
    
    def _show_list_view(self, proyectos:  List[Dict[str, Any]]):
        """Mostrar vista de lista/tabla"""
        table = QTableWidget()
        table.setColumnCount(7)  # ✅ 7 columnas (sin Acciones)
        table.setRowCount(len(proyectos))
        
        headers = ["Nombre", "Estado", "Fecha Inicio", "Avance Físico", "Avance Financiero",
                "Presupuesto", "Gastado"]  # ✅ Sin "Acciones"
        table. setHorizontalHeaderLabels(headers)
        
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_200']};
                border-radius:  {BORDER['radius']}px;
                gridline-color: {COLORS['slate_100']};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item: selected {{
                background-color: {COLORS['blue_100']};
                color: {COLORS['slate_900']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['slate_50']};
                color: {COLORS['slate_700']};
                padding: 10px;
                border:  none;
                border-bottom: 1px solid {COLORS['slate_200']};
                font-weight: 600;
            }}
        """)
        
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # ✅ HABILITAR SELECCIÓN DE FILAS COMPLETAS
        table.setSelectionBehavior(QTableWidget.SelectionBehavior. SelectRows)
        table.setSelectionMode(QTableWidget. SelectionMode.SingleSelection)
        
        # ✅ HABILITAR MENÚ CONTEXTUAL
        table.setContextMenuPolicy(Qt.ContextMenuPolicy. CustomContextMenu)
        table.customContextMenuRequested.connect(lambda pos: self._show_table_context_menu(table, pos))
        
        # ✅ HABILITAR DOBLE CLICK
        table.itemDoubleClicked.connect(lambda item: self._on_table_double_click(table, item))
        
        # ✅ HABILITAR ATAJOS DE TECLADO
        table.keyPressEvent = lambda event: self._on_table_key_press(table, event)
        
        for i, proyecto in enumerate(proyectos):
            col = 0
            
            # Nombre (con proyecto_id guardado)
            nombre_item = QTableWidgetItem(proyecto['nombre'])
            nombre_item. setData(Qt.ItemDataRole.UserRole, proyecto['id'])  # ✅ Guardar ID
            table.setItem(i, col, nombre_item)
            col += 1
            
            # Estado
            estado_text = self._get_estado_display(proyecto['estado'])
            table.setItem(i, col, QTableWidgetItem(estado_text))
            col += 1
            
            # Fecha Inicio
            fecha_inicio_real = self._fechas_inicio_real.get(proyecto['id'])
            if fecha_inicio_real:
                fecha_text = fecha_inicio_real.strftime('%d/%m/%Y')
            elif proyecto['fecha_inicio']: 
                fecha_text = proyecto['fecha_inicio']
            else: 
                fecha_text = "-"
            table.setItem(i, col, QTableWidgetItem(fecha_text))
            col += 1
            
            # Avance físico
            avance_fisico = proyecto['avance_fisico']
            table.setItem(i, col, QTableWidgetItem(f"{avance_fisico}%"))
            col += 1
            
            # ✅ Avance financiero (CON VALIDACIÓN)
            gastado = self._gastos_por_proyecto.get(proyecto['id'], 0)
            presupuesto = proyecto['presupuesto_total']
            
            if presupuesto > 0:
                avance_financiero = int((gastado / presupuesto * 100))
                table.setItem(i, col, QTableWidgetItem(f"{avance_financiero}%"))
            else:
                # ⚠️ Sin presupuesto
                item = QTableWidgetItem("N/A")
                item.setForeground(QColor(COLORS['orange_600']))
                table.setItem(i, col, item)
            col += 1
            
            # Presupuesto
            if presupuesto > 0:
                table.setItem(i, col, QTableWidgetItem(self._format_currency(presupuesto)))
            else:
                item = QTableWidgetItem("No definido")
                item.setForeground(QColor(COLORS['orange_600']))
                table.setItem(i, col, item)
            col += 1
            
            # Gastado
            gastado_item = QTableWidgetItem(self._format_currency(gastado))
            # ✅ Colorear según si excede o no el presupuesto
            if presupuesto > 0:
                if gastado > presupuesto: 
                    gastado_item.setForeground(QColor(COLORS['red_600']))
                else:
                    gastado_item.setForeground(QColor(COLORS['green_600']))
            table.setItem(i, col, gastado_item)
            col += 1
            
            # ✅ YA NO HAY columna "Acciones"
        
        self.content_layout. addWidget(table)
    
    def _create_project_card(self, proyecto: Dict[str, Any]) -> CleanCard:
        """Crear card de proyecto"""
        card = CleanCard(padding=20)
        card.setMinimumHeight(300)
        card.setMinimumWidth(320)
        card.setCursor(Qt.CursorShape. PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        
        # Header con icono y estado
        header_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_pixmap = icon_manager.get_pixmap('building-2', proyecto['color'], 32)
        icon_label.setPixmap(icon_pixmap)
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        
        estado_badge = self._create_estado_badge(proyecto['estado'])
        header_layout.addWidget(estado_badge)
        layout.addLayout(header_layout)
        
        # Nombre
        nombre_label = QLabel(proyecto['nombre'])
        nombre_font = QFont()
        nombre_font.setPointSize(14)
        nombre_font.setWeight(QFont.Weight.Bold)
        nombre_label.setFont(nombre_font)
        nombre_label.setStyleSheet(f"color: {COLORS['slate_900']};")
        nombre_label.setWordWrap(True)
        layout.addWidget(nombre_label)
        
        # Cliente
        if proyecto['cliente']: 
            cliente_label = QLabel(f"👤 {proyecto['cliente']}")
            cliente_label.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 11px;")
            layout.addWidget(cliente_label)
        
        # Fecha de inicio (primera transacción)
        fecha_inicio_real = self._fechas_inicio_real. get(proyecto['id'])
        if fecha_inicio_real:
            fecha_label = QLabel(f"📅 Inicio: {fecha_inicio_real.strftime('%d/%m/%Y')}")
            fecha_label.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 11px;")
            layout.addWidget(fecha_label)
        elif proyecto['fecha_inicio']:
            fecha_label = QLabel(f"📅 Inicio: {proyecto['fecha_inicio']}")
            fecha_label.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 11px;")
            layout.addWidget(fecha_label)
        
        # ✅ Duración estimada y tiempo transcurrido
        duracion_meses = proyecto. get('duracion_meses', 0)
        if duracion_meses > 0:
            if fecha_inicio_real:
                # Calcular tiempo transcurrido
                from datetime import date as date_class
                dias_transcurridos = (date_class. today() - fecha_inicio_real).days
                meses_transcurridos = dias_transcurridos / 30.44
                meses_transcurridos_int = round(meses_transcurridos)
                
                # ✅ NUEVO: Calcular diferencia con el avance físico esperado
                avance_fisico = proyecto['avance_fisico']
                
                # Meses que DEBERÍAN haber transcurrido según el avance físico
                meses_esperados_segun_avance = (avance_fisico / 100) * duracion_meses
                
                # Diferencia:  positivo = atrasado, negativo = adelantado
                diferencia_meses = meses_transcurridos - meses_esperados_segun_avance
                diferencia_int = round(diferencia_meses)
                
                # Determinar color y símbolo
                if diferencia_int > 0:
                    # ATRASADO (transcurrió más tiempo del que debería según el avance)
                    diferencia_text = f"-{diferencia_int} meses"
                    diferencia_color = COLORS['red_600']
                    diferencia_emoji = "🔴"
                elif diferencia_int < 0:
                    # ADELANTADO (transcurrió menos tiempo del esperado)
                    diferencia_text = f"+{abs(diferencia_int)} meses"
                    diferencia_color = COLORS['green_600']
                    diferencia_emoji = "🟢"
                else: 
                    # EN TIEMPO
                    diferencia_text = "en tiempo"
                    diferencia_color = COLORS['blue_600']
                    diferencia_emoji = "🔵"
                
                # Crear label con formato
                duracion_container = QWidget()
                duracion_layout = QHBoxLayout(duracion_container)
                duracion_layout.setContentsMargins(0, 0, 0, 0)
                duracion_layout.setSpacing(4)
                
                # Parte 1: "⏱️ Duración:  6 meses | Transcurrido: 3 meses"
                duracion_base = QLabel(
                    f"⏱️ Duración: {duracion_meses} meses | Transcurrido: {meses_transcurridos_int} meses"
                )
                duracion_base.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 11px;")
                duracion_layout.addWidget(duracion_base)
                
                # Parte 2: Diferencia con color
                diferencia_label = QLabel(f"({diferencia_emoji} {diferencia_text})")
                diferencia_label.setStyleSheet(f"color: {diferencia_color}; font-size: 11px; font-weight: 600;")
                duracion_layout.addWidget(diferencia_label)
                
                duracion_layout.addStretch()
                
                layout.addWidget(duracion_container)
            else:
                # Solo mostrar duración estimada
                duracion_label = QLabel(f"⏱️ Duración estimada: {duracion_meses} meses")
                duracion_label.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 11px;")
                layout.addWidget(duracion_label)
        
        layout.addSpacing(8)
        
        # ✅ Avance Físico
        avance_fisico = proyecto['avance_fisico']
        fisico_label = QLabel(f"Avance Físico:  {avance_fisico}%")
        fisico_label.setStyleSheet(f"color:  {COLORS['slate_700']}; font-size: 11px; font-weight: 500;")
        layout.addWidget(fisico_label)
        
        fisico_bar = self._create_progress_bar(avance_fisico, COLORS['green_500'])
        layout.addWidget(fisico_bar)
        
        # ✅ Avance Financiero (CON VALIDACIÓN DE PRESUPUESTO)
        gastado = self._gastos_por_proyecto.get(proyecto['id'], 0)
        presupuesto = proyecto['presupuesto_total']
        
        if presupuesto > 0:
            avance_financiero = int((gastado / presupuesto * 100))
            financiero_label = QLabel(f"Avance Financiero: {avance_financiero}%")
            financiero_label.setStyleSheet(f"color: {COLORS['slate_700']}; font-size: 11px; font-weight: 500;")
            layout.addWidget(financiero_label)
            
            financiero_bar = self._create_progress_bar(avance_financiero, COLORS['blue_500'])
            layout.addWidget(financiero_bar)
        else:
            # ⚠️ Sin presupuesto definido
            financiero_label = QLabel("⚠️ Avance Financiero: Sin presupuesto definido")
            financiero_label.setStyleSheet(f"color: {COLORS['orange_600']}; font-size: 11px; font-weight: 600;")
            layout.addWidget(financiero_label)
            
            # Barra vacía con color de advertencia
            empty_bar = self._create_progress_bar(0, COLORS['orange_300'])
            layout.addWidget(empty_bar)
        
        layout.addSpacing(8)
        
        # Presupuesto y Gastado
        if presupuesto > 0:
            presupuesto_label = QLabel(f"Presupuesto: {self._format_currency(presupuesto)}")
            presupuesto_label. setStyleSheet(f"color:  {COLORS['slate_600']}; font-size: 12px;")
            layout.addWidget(presupuesto_label)
        else:
            presupuesto_label = QLabel("Presupuesto: No definido")
            presupuesto_label.setStyleSheet(f"color: {COLORS['orange_600']}; font-size: 12px; font-weight: 600;")
            layout.addWidget(presupuesto_label)
        
        gastado_label = QLabel(f"Gastado: {self._format_currency(gastado)}")
        if presupuesto > 0:
            gastado_color = COLORS['red_600'] if gastado > presupuesto else COLORS['green_600']
        else: 
            gastado_color = COLORS['slate_700']
        gastado_label.setStyleSheet(f"color: {gastado_color}; font-size: 12px; font-weight: 600;")
        layout.addWidget(gastado_label)
        
        layout.addStretch()
        
        # ✅ DOS BOTONES: Dashboard + Transacción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        # Botón Ver Dashboard
        btn_dashboard = QPushButton("📊 Dashboard")
        btn_dashboard.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_dashboard.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['blue_600']};
                color: {COLORS['white']};
                border: none;
                border-radius: {BORDER['radius_sm']}px;
                padding: 8px 12px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['blue_700']};
            }}
        """)
        btn_dashboard.clicked.connect(lambda: self._view_proyecto_dashboard(proyecto['id'], proyecto['nombre']))
        buttons_layout.addWidget(btn_dashboard)
        
        # Botón + Transacción
        btn_add_trans = QPushButton("+ Trans")
        btn_add_trans. setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_trans.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['green_600']};
                color:  {COLORS['white']};
                border: none;
                border-radius: {BORDER['radius_sm']}px;
                padding: 8px 12px;
                font-weight: 600;
                font-size:  12px;
            }}
            QPushButton:hover {{
                background-color: #16A34A;
            }}
        """)
        btn_add_trans.clicked.connect(lambda: self._add_transaccion_proyecto(proyecto['id'], proyecto['nombre']))
        buttons_layout.addWidget(btn_add_trans)
        
        layout.addLayout(buttons_layout)
        
        # Context menu
        card. setContextMenuPolicy(Qt. ContextMenuPolicy.CustomContextMenu)
        card.customContextMenuRequested.connect(
            lambda pos, pid=proyecto['id']: self._show_card_context_menu(pid, card. mapToGlobal(pos))
        )
        
        return card
    
    def _create_estado_badge(self, estado:  str) -> QLabel:
        """Crear badge de estado"""
        estados = {
            'activo': ('🟢 Activo', COLORS['green_100'], COLORS['green_700']),
            'pausado':  ('🟡 Pausado', COLORS['yellow_100'], COLORS['yellow_700']),
            'completado': ('✅ Completado', COLORS['blue_100'], COLORS['blue_700'])
        }
        
        text, bg_color, text_color = estados.get(estado, ('⚪ Desconocido', COLORS['slate_100'], COLORS['slate_700']))
        
        badge = QLabel(text)
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                padding: 4px 12px;
                border-radius:  12px;
                font-size:  11px;
                font-weight:  600;
            }}
        """)
        return badge
    
    def _create_progress_bar(self, value: int, color: str) -> QFrame:
        """Crear barra de progreso personalizada"""
        from PyQt6.QtWidgets import QProgressBar
        
        bar = QProgressBar()
        bar.setFixedHeight(8)
        bar.setTextVisible(False)
        bar.setValue(value)
        bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {COLORS['slate_200']};
            }}
            QProgressBar::chunk {{
                border-radius: 4px;
                background-color: {color};
            }}
        """)
        return bar
    
    # ==================== ACCIONES ====================
    
    def _view_proyecto_dashboard(self, proyecto_id: str, proyecto_nombre: str):
        """Ver dashboard del proyecto (cambiar proyecto activo)"""
        logger.info(f"Viewing dashboard for proyecto: {proyecto_nombre}")
        self.project_selected. emit(proyecto_id, proyecto_nombre)
    
    def _add_transaccion_proyecto(self, proyecto_id: str, proyecto_nombre:  str):
        """
        Ir a la página de transacciones y abrir el diálogo de nueva transacción.  
        """
        logger.info(f"Adding transaction for proyecto: {proyecto_nombre}")
        
        # Cambiar proyecto activo
        self. project_selected.emit(proyecto_id, proyecto_nombre)
        
        # Navegar a transacciones y abrir diálogo
        QTimer.singleShot(100, self._navigate_to_transactions_and_register)
    
    def _navigate_to_transactions_and_register(self):
        """Helper para navegar a transacciones y abrir diálogo de registro"""
        parent = self.parent()
        while parent and not hasattr(parent, 'navigate_to_page'):
            parent = parent.parent()
        
        if parent: 
            if hasattr(parent, 'navigate_to_page'):
                parent.navigate_to_page('transactions')
            
            QTimer.singleShot(200, lambda: self._trigger_register_button(parent))
    
    def _trigger_register_button(self, main_window):
        """Simular click en botón + Registrar del header"""
        if hasattr(main_window, 'header') and hasattr(main_window. header, 'register_button'):
            main_window.header. register_button.click()
        else:
            logger.warning("Could not find register button")
    
    def _show_actions_menu(self, proyecto_id: str):
        """Mostrar menú de acciones para un proyecto"""
        logger.info(f"Actions menu for proyecto: {proyecto_id}")
    
    def _show_card_context_menu(self, proyecto_id: str, pos):
        """Mostrar menú contextual en card"""
        menu = QMenu(self)
        
        action_edit = QAction("✏️ Editar", self)
        action_edit. triggered.connect(lambda: self._edit_proyecto(proyecto_id))
        menu.addAction(action_edit)
        
        action_estado = QAction("🔄 Cambiar Estado", self)
        menu.addAction(action_estado)
        
        menu.addSeparator()
        
        action_dashboard = QAction("📊 Ver Dashboard", self)
        proyecto = next((p for p in self._proyectos if p['id'] == proyecto_id), None)
        if proyecto:
            action_dashboard.triggered.connect(
                lambda: self._view_proyecto_dashboard(proyecto_id, proyecto['nombre'])
            )
        menu.addAction(action_dashboard)
        
        menu.exec(pos)
    
    def _open_new_obra_dialog(self):
        """Abrir diálogo para crear nueva obra"""
        from . obra_dialog import ObraDialog
        
        dialog = ObraDialog(
            firebase_client=self.firebase_client,
            parent=self
        )
        
        # ✅ Aunque es nuevo proyecto, conectar por si se implementa crear+editar en un solo flujo
        dialog.proyecto_updated.connect(self._on_proyecto_updated)
        
        if dialog.exec():
            self.refresh()
    
    def _edit_proyecto(self, proyecto_id: str):
        """Editar proyecto existente"""
        from . obra_dialog import ObraDialog
        
        # ✅ BUSCAR EL PROYECTO EN EL CACHE
        proyecto = next((p for p in self._proyectos if p['id'] == proyecto_id), None)
        if not proyecto: 
            logger.warning(f"Proyecto {proyecto_id} not found")
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo cargar el proyecto {proyecto_id}"
            )
            return
        
        # ✅ CREAR DIÁLOGO EN MODO EDITAR CON LOS DATOS DEL PROYECTO
        dialog = ObraDialog(
            firebase_client=self.firebase_client,
            modo='editar',              # ✅ MODO EXPLÍCITO
            proyecto_id=proyecto_id,    # ✅ ID DEL PROYECTO
            proyecto=proyecto,          # ✅ DATOS DEL PROYECTO
            parent=self
        )
        
        # ✅ CONECTAR la señal de actualización
        dialog.proyecto_updated.connect(self._on_proyecto_updated)
        
        if dialog.exec():
            # Refrescar esta página
            self.refresh()
    
    # ==================== UTILIDADES ====================
    
    def _format_currency(self, amount: float) -> str:
        """Formatear monto como moneda"""
        return f"RD$ {amount: ,.2f}"
    
    def _get_estado_display(self, estado: str) -> str:
        """Obtener texto display del estado"""
        estados = {
            'activo':  '🟢 Activo',
            'pausado': '🟡 Pausado',
            'completado': '✅ Completado'
        }
        return estados.get(estado, '⚪ Desconocido')
    
    def _clear_layout(self, layout):
        """Limpiar todos los widgets de un layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())



    # ==================== EVENTOS DE TABLA ====================

    def _on_table_double_click(self, table:  QTableWidget, item: QTableWidgetItem):
        """Callback cuando se hace doble clic en una fila"""
        row = item.row()
        proyecto_id = table.item(row, 0).data(Qt.ItemDataRole. UserRole)
        
        if proyecto_id:
            logger.info(f"Double click on proyecto:  {proyecto_id}")
            self._edit_proyecto(proyecto_id)

    def _on_table_key_press(self, table: QTableWidget, event):
        """Callback para atajos de teclado en la tabla"""
        from PyQt6.QtGui import QKeyEvent
        from PyQt6.QtCore import Qt
        
        # Obtener fila seleccionada
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows:
            # Si no hay selección, llamar al keyPressEvent por defecto
            QTableWidget.keyPressEvent(table, event)
            return
        
        row = selected_rows[0].row()
        proyecto_id = table.item(row, 0).data(Qt.ItemDataRole. UserRole)
        
        if not proyecto_id:
            QTableWidget.keyPressEvent(table, event)
            return
        
        # ENTER o F2:  Editar proyecto
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_F2):
            logger.info(f"Keyboard shortcut: Edit proyecto {proyecto_id}")
            self._edit_proyecto(proyecto_id)
            event.accept()
        
        # DELETE: Eliminar proyecto (con confirmación)
        elif event.key() == Qt.Key.Key_Delete:
            logger.info(f"Keyboard shortcut:  Delete proyecto {proyecto_id}")
            self._confirm_delete_proyecto(proyecto_id)
            event.accept()
        
        # D: Ver Dashboard
        elif event.key() == Qt.Key.Key_D: 
            proyecto = next((p for p in self._proyectos if p['id'] == proyecto_id), None)
            if proyecto:
                logger.info(f"Keyboard shortcut: View dashboard {proyecto_id}")
                self._view_proyecto_dashboard(proyecto_id, proyecto['nombre'])
            event.accept()
        
        # T: Agregar transacción
        elif event.key() == Qt.Key.Key_T:
            proyecto = next((p for p in self._proyectos if p['id'] == proyecto_id), None)
            if proyecto:
                logger.info(f"Keyboard shortcut: Add transaction {proyecto_id}")
                self._add_transaccion_proyecto(proyecto_id, proyecto['nombre'])
            event.accept()
        
        # ESPACIO: Cambiar estado (ciclo:  activo → pausado → completado → activo)
        elif event.key() == Qt.Key.Key_Space:
            logger.info(f"Keyboard shortcut: Toggle estado {proyecto_id}")
            self._toggle_proyecto_estado(proyecto_id)
            event.accept()
        
        else:
            # Para otras teclas, comportamiento por defecto
            QTableWidget.keyPressEvent(table, event)

    def _show_table_context_menu(self, table: QTableWidget, pos):
        """Mostrar menú contextual en la tabla"""
        # Obtener fila donde se hizo click
        item = table.itemAt(pos)
        if not item:
            return
        
        row = item.row()
        proyecto_id = table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        if not proyecto_id: 
            return
        
        proyecto = next((p for p in self._proyectos if p['id'] == proyecto_id), None)
        if not proyecto:
            return
        
        # Crear menú
        menu = QMenu(self)
        
        # Editar
        action_edit = QAction("✏️ Editar (Enter/F2)", self)
        action_edit.triggered.connect(lambda: self._edit_proyecto(proyecto_id))
        menu.addAction(action_edit)
        
        # Cambiar estado
        estado_menu = menu.addMenu("🔄 Cambiar Estado (Space)")
        
        action_activo = QAction("🟢 Activo", self)
        action_activo.triggered.connect(lambda: self._change_proyecto_estado(proyecto_id, 'activo'))
        estado_menu.addAction(action_activo)
        
        action_pausado = QAction("🟡 Pausado", self)
        action_pausado.triggered.connect(lambda: self._change_proyecto_estado(proyecto_id, 'pausado'))
        estado_menu.addAction(action_pausado)
        
        action_completado = QAction("✅ Completado", self)
        action_completado.triggered.connect(lambda: self._change_proyecto_estado(proyecto_id, 'completado'))
        estado_menu.addAction(action_completado)
        
        menu.addSeparator()
        
        # Ver dashboard
        action_dashboard = QAction("📊 Ver Dashboard (D)", self)
        action_dashboard.triggered.connect(lambda: self._view_proyecto_dashboard(proyecto_id, proyecto['nombre']))
        menu.addAction(action_dashboard)
        
        # Agregar transacción
        action_trans = QAction("💰 Agregar Transacción (T)", self)
        action_trans.triggered.connect(lambda: self._add_transaccion_proyecto(proyecto_id, proyecto['nombre']))
        menu.addAction(action_trans)
        
        menu.addSeparator()
        
        # Eliminar
        action_delete = QAction("🗑️ Eliminar (Delete)", self)
        action_delete.triggered.connect(lambda: self._confirm_delete_proyecto(proyecto_id))
        menu.addAction(action_delete)
        
        # Mostrar menú en la posición del cursor
        menu.exec(table. viewport().mapToGlobal(pos))

    def _show_actions_menu_for_row(self, proyecto_id: str, table: QTableWidget):
        """Mostrar menú de acciones desde el botón ⚙️"""
        # Buscar la fila del proyecto
        for row in range(table.rowCount()):
            if table.item(row, 0).data(Qt.ItemDataRole.UserRole) == proyecto_id:
                # Simular click derecho en esa fila
                item = table.item(row, 0)
                pos = table.visualItemRect(item).center()
                self._show_table_context_menu(table, pos)
                break

    def _toggle_proyecto_estado(self, proyecto_id: str):
        """Cambiar estado del proyecto (ciclo)"""
        proyecto = next((p for p in self._proyectos if p['id'] == proyecto_id), None)
        if not proyecto:
            return
        
        # Ciclo: activo → pausado → completado → activo
        estado_actual = proyecto['estado']
        if estado_actual == 'activo':
            nuevo_estado = 'pausado'
        elif estado_actual == 'pausado':
            nuevo_estado = 'completado'
        else: 
            nuevo_estado = 'activo'
        
        self._change_proyecto_estado(proyecto_id, nuevo_estado)

    def _change_proyecto_estado(self, proyecto_id: str, nuevo_estado: str):
        """Cambiar el estado de un proyecto en Firestore"""
        if not self. firebase_client: 
            return
        
        try:
            from firebase_admin import firestore
            db = firestore.client()
            
            doc_ref = db.collection('proyectos').document(str(proyecto_id))
            doc_ref.update({
                'estado': nuevo_estado,
                'actualizado_en': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Estado del proyecto {proyecto_id} cambiado a:  {nuevo_estado}")
            
            # Refrescar vista
            self. refresh()
            
        except Exception as e: 
            logger.error(f"Error changing proyecto estado: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cambiar el estado del proyecto:\n{e}"
            )

    def _confirm_delete_proyecto(self, proyecto_id: str):
        """Confirmar eliminación de proyecto"""
        proyecto = next((p for p in self._proyectos if p['id'] == proyecto_id), None)
        if not proyecto:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar el proyecto:\n\n'{proyecto['nombre']}'?\n\n"
            f"⚠️ ADVERTENCIA: Esta acción NO se puede deshacer.\n"
            f"Se eliminarán todas las transacciones y datos asociados.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox. StandardButton.Yes:
            self._delete_proyecto(proyecto_id)

    def _delete_proyecto(self, proyecto_id: str):
        """Eliminar proyecto de Firestore (PENDIENTE:  implementar lógica completa)"""
        # TODO: Implementar eliminación completa (proyecto + transacciones + cuentas)
        QMessageBox.information(
            self,
            "Función no implementada",
            "La eliminación de proyectos aún no está implementada.\n\n"
            "Se requiere eliminar:\n"
            "- El proyecto\n"
            "- Todas sus transacciones\n"
            "- Todas sus cuentas\n\n"
            "Por seguridad, esta función se implementará después."
        )
        logger.warning(f"Delete proyecto {proyecto_id} - NOT IMPLEMENTED YET")





    def _on_proyecto_updated(self, proyecto_id: str, proyecto_nombre: str):
        """
        Callback cuando se actualiza un proyecto desde el diálogo. 
        Notifica al MainWindow para que actualice el Dashboard.
        """
        logger.info(f"Proyecto actualizado desde diálogo: {proyecto_nombre} ({proyecto_id})")
        
        # Refrescar esta página
        self.refresh()
        
        # Notificar al MainWindow para que actualice el Dashboard
        main_window = self.parent()
        while main_window and not hasattr(main_window, 'on_project_changed'):
            main_window = main_window.parent()
        
        if main_window and hasattr(main_window, 'on_project_changed'):
            logger.info(f"Notifying MainWindow of project update: {proyecto_id}")
            main_window.on_project_changed(proyecto_id, proyecto_nombre)
        else:
            logger.warning("MainWindow not found - cannot update dashboard")