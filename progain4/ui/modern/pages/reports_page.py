"""
Modern Reports Page for PROGRAIN 5.0 - WITH TABS & DASHBOARDS

Professional reporting system with:
- TAB 1: Reports (4 report types with SVG icons)
- TAB 2: Dashboards (3 interactive dashboards)
- Modern UI design
- Proper card sizing
- Firebase integration
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QLabel,
    QDateEdit, QMessageBox, QFileDialog, QGroupBox,
    QFrame, QTabWidget, QGridLayout, QComboBox, QTreeWidget,
    QTreeWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView

from progain4.services.firebase_client import FirebaseClient
from progain4.ui.modern.theme_config import COLORS, FONTS, SPACING

# Importar ReportGenerator
try:
    from progain4.services.report_generator import ReportGenerator
    REPORT_GENERATOR_AVAILABLE = True
except ImportError:
    REPORT_GENERATOR_AVAILABLE = False
    logging.warning("ReportGenerator no disponible")

# Importar librerías para dashboards
try:
    import pandas as pd
    import plotly.express as px
    DASHBOARD_LIBS_AVAILABLE = True
except ImportError:
    DASHBOARD_LIBS_AVAILABLE = False
    logging.warning("Pandas o Plotly no disponibles - Dashboards deshabilitados")

logger = logging.getLogger(__name__)


class ReportsPage(QWidget):
    """
    Modern reports page with tabs for Reports and Dashboards.
    
    TAB 1: Reports
    - Detailed by Date
    - By Category
    - Account Summary
    - Global Accounts
    
    TAB 2: Dashboards
    - Advanced Expenses Dashboard
    - Global Accounts Dashboard
    - Income vs Expenses Dashboard
    """
    
    def __init__(
        self,
        firebase_client: FirebaseClient,
        proyecto_id: str,
        proyecto_nombre: str,
        parent=None
    ):
        super().__init__(parent)
        
        self.firebase_client = firebase_client
        self.proyecto_id = proyecto_id
        self.proyecto_nombre = proyecto_nombre
        self.moneda = "RD$"
        
        # Current active report/dashboard
        self.current_report = None
        self.current_dashboard = None
        
        # Data cache
        self._all_transacciones: Optional[List[Dict[str, Any]]] = None
        self.transacciones_filtradas: List[Dict[str, Any]] = []
        
        # Maps for lookups
        self.cuentas_map: Dict[str, str] = {}
        self.categorias_map: Dict[str, str] = {}
        
        # Date range
        self.fecha_inicio = None
        self.fecha_fin = None
        
        logger.info(f"Initializing ReportsPage for project {proyecto_id}")
        
        self._init_ui()
        self._load_maps()
        self._set_smart_date_range()
    
    def _init_ui(self):
        """Initialize the modern user interface with TABS"""
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING['lg'])
        layout.setContentsMargins(SPACING['xl'], SPACING['lg'], SPACING['xl'], SPACING['lg'])
        
        # === HEADER ===
        header = self._create_header()
        layout.addWidget(header)
        
        # === TAB WIDGET ===
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(self._get_tab_style())
        
        # TAB 1: Reportes
        self.tab_reportes = self._create_reports_tab()
        self.tabs.addTab(self.tab_reportes, "📋 Reportes")
        
        # TAB 2: Dashboards
        self.tab_dashboards = self._create_dashboards_tab()
        self.tabs.addTab(self.tab_dashboards, "📊 Dashboards")
        
        layout.addWidget(self.tabs)
        
        self.setLayout(layout)
        
        # Set default to reports tab and select first report
        self.tabs.setCurrentIndex(0)
        self._select_report('detailed')
    
    def _create_header(self) -> QWidget:
        """Create page header"""
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['white']};
                border-radius: 8px;
                padding: 16px 20px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon + Title
        icon_label = QLabel("📊")
        icon_label.setStyleSheet("font-size: 24px; background: transparent;")
        layout.addWidget(icon_label)
        
        title = QLabel(f"Reportes y Dashboards - {self.proyecto_nombre}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']}; background: transparent;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        return header
    
    # ==================== TAB 1: REPORTS ====================
    
    def _create_reports_tab(self) -> QWidget:
        """Create the Reports tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(SPACING['lg'])
        layout.setContentsMargins(SPACING['md'], SPACING['md'], SPACING['md'], SPACING['md'])
        
        # Report type selector (cards)
        selector = self._create_report_selector()
        layout.addWidget(selector)
        
        # Filters toolbar
        self.filters_widget = self._create_filters_toolbar()
        layout.addWidget(self.filters_widget)
        
        # Preview area
        preview_group = self._create_preview_area()
        layout.addWidget(preview_group, stretch=1)
        
        # Export buttons
        export_buttons = self._create_export_buttons()
        layout.addWidget(export_buttons)
        
        return tab
    
    def _create_report_selector(self) -> QWidget:
        """Create report type selector with horizontal buttons"""
        container = QWidget()
        container.setStyleSheet(f"background-color: transparent;")
        
        layout = QVBoxLayout(container)
        layout.setSpacing(SPACING['sm'])
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel("Selecciona el tipo de reporte:")
        label.setStyleSheet(f"color: {COLORS['slate_700']}; font-weight: 600; font-size: 13px;")
        layout.addWidget(label)
        
        # Buttons layout - HORIZONTAL
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(SPACING['sm'])
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # === BUTTON 1: Detailed Report ===
        self.btn_detailed = self._create_report_button(
            self._get_document_icon_svg(),
            "Reporte Detallado",
            "detailed"
        )
        buttons_layout.addWidget(self.btn_detailed)
        
        # === BUTTON 2: By Category ===
        self.btn_category = self._create_report_button(
            self._get_folder_icon_svg(),
            "Por Categoría",
            "category"
        )
        buttons_layout.addWidget(self.btn_category)
        
        # === BUTTON 3: Account Summary ===
        self.btn_cashflow = self._create_report_button(
            self._get_bank_icon_svg(),
            "Resumen por Cuenta",
            "cashflow"
        )
        buttons_layout.addWidget(self.btn_cashflow)
        
        # === BUTTON 4: Global Accounts ===
        self.btn_summary = self._create_report_button(
            self._get_globe_icon_svg(),
            "Explorador Global",
            "summary"
        )
        buttons_layout.addWidget(self.btn_summary)
        
        layout.addLayout(buttons_layout)
        
        return container

    def _create_report_button(self, svg_content: str, title: str, report_id: str) -> QPushButton:
        """Create a horizontal button with SVG icon + text"""
        btn = QPushButton()
        btn.setObjectName(f"report_btn_{report_id}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Fixed height, flexible width
        btn.setMinimumHeight(50)
        btn.setMaximumHeight(50)
        
        # Create layout for button content
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(12, 8, 12, 8)
        
        # SVG Icon (left side)
        svg_widget = QSvgWidget()
        svg_widget.load(svg_content.encode())
        svg_widget.setFixedSize(QSize(24, 24))
        btn_layout.addWidget(svg_widget)
        
        # Text (right side)
        text_label = QLabel(title)
        text_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_700']};
                font-weight: 600;
                font-size: 13px;
                background: transparent;
                border: none;
            }}
        """)
        text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        btn_layout.addWidget(text_label, stretch=1)
        
        # Set layout to button
        btn.setLayout(btn_layout)
        
        # Style
        btn.setStyleSheet(f"""
            QPushButton#report_btn_{report_id} {{
                background-color: {COLORS['white']};
                border: 2px solid {COLORS['slate_200']};
                border-radius: 6px;
                text-align: left;
            }}
            QPushButton#report_btn_{report_id}:hover {{
                border-color: {COLORS['blue_500']};
                background-color: {COLORS['blue_50']};
            }}
            QPushButton#report_btn_{report_id}:pressed {{
                background-color: {COLORS['blue_100']};
            }}
        """)
        
        # Click handler
        btn.clicked.connect(lambda: self._select_report(report_id))
        
        # Store reference to inner widgets for styling updates
        btn._svg_widget = svg_widget
        btn._text_label = text_label
        
        return btn
    
    # ==================== TAB 2: DASHBOARDS ====================
    
    def _create_dashboards_tab(self) -> QWidget:
        """Create the Dashboards tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(SPACING['lg'])
        layout.setContentsMargins(SPACING['md'], SPACING['md'], SPACING['md'], SPACING['md'])
        
        # Dashboard selector (cards)
        selector = self._create_dashboard_selector()
        layout.addWidget(selector)
        
        # Dashboard content area (stacked widget for different dashboards)
        self.dashboard_container = QWidget()
        self.dashboard_layout = QVBoxLayout(self.dashboard_container)
        self.dashboard_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.dashboard_container, stretch=1)
        
        # Placeholder
        placeholder = QLabel("Selecciona un dashboard arriba para visualizarlo")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(f"color: {COLORS['slate_400']}; font-size: 14px; padding: 40px;")
        self.dashboard_layout.addWidget(placeholder)
        
        return tab
    
    def _create_dashboard_selector(self) -> QWidget:
        """Create dashboard type selector with horizontal buttons"""
        container = QWidget()
        container.setStyleSheet(f"background-color: transparent;")
        
        layout = QVBoxLayout(container)
        layout.setSpacing(SPACING['sm'])
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel("Selecciona el dashboard:")
        label.setStyleSheet(f"color: {COLORS['slate_700']}; font-weight: 600; font-size: 13px;")
        layout.addWidget(label)
        
        # Buttons layout - HORIZONTAL
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(SPACING['sm'])
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Check if dashboard libraries are available
        enabled = DASHBOARD_LIBS_AVAILABLE
        
        # === DASHBOARD 1: Advanced Expenses ===
        self.btn_dashboard1 = self._create_dashboard_button(
            self._get_chart_icon_svg(),
            "Gastos Avanzados",
            "dashboard1",
            enabled
        )
        buttons_layout.addWidget(self.btn_dashboard1)
        
        # === DASHBOARD 2: Global Accounts ===
        self.btn_dashboard2 = self._create_dashboard_button(
            self._get_pie_chart_icon_svg(),
            "Cuentas Globales",
            "dashboard2",
            enabled
        )
        buttons_layout.addWidget(self.btn_dashboard2)
        
        # === DASHBOARD 3: Income vs Expenses ===
        self.btn_dashboard3 = self._create_dashboard_button(
            self._get_trending_icon_svg(),
            "Ingresos vs Gastos",
            "dashboard3",
            enabled
        )
        buttons_layout.addWidget(self.btn_dashboard3)
        
        layout.addLayout(buttons_layout)
        
        # Info message if libs not available
        if not enabled:
            info = QLabel("⚠️ Instala pandas y plotly para habilitar dashboards: pip install pandas plotly kaleido")
            info.setStyleSheet(f"color: {COLORS['amber_600']}; font-size: 11px; font-style: italic; padding: 8px;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)
        
        return container

    def _create_dashboard_button(self, svg_content: str, title: str, dashboard_id: str, enabled: bool = True) -> QPushButton:
        """Create a horizontal button for dashboard selection"""
        btn = QPushButton()
        btn.setObjectName(f"dashboard_btn_{dashboard_id}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor if enabled else Qt.CursorShape.ForbiddenCursor)
        btn.setEnabled(enabled)
        
        # Fixed height, flexible width
        btn.setMinimumHeight(50)
        btn.setMaximumHeight(50)
        
        # Create layout for button content
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(12, 8, 12, 8)
        
        # SVG Icon (left side)
        svg_widget = QSvgWidget()
        svg_widget.load(svg_content.encode())
        svg_widget.setFixedSize(QSize(24, 24))
        btn_layout.addWidget(svg_widget)
        
        # Text (right side)
        text_label = QLabel(title)
        text_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_700'] if enabled else COLORS['slate_400']};
                font-weight: 600;
                font-size: 13px;
                background: transparent;
                border: none;
            }}
        """)
        text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        btn_layout.addWidget(text_label, stretch=1)
        
        # Set layout to button
        btn.setLayout(btn_layout)
        
        # Style
        if enabled:
            btn.setStyleSheet(f"""
                QPushButton#dashboard_btn_{dashboard_id} {{
                    background-color: {COLORS['white']};
                    border: 2px solid {COLORS['slate_200']};
                    border-radius: 6px;
                    text-align: left;
                }}
                QPushButton#dashboard_btn_{dashboard_id}:hover {{
                    border-color: {COLORS['blue_500']};
                    background-color: {COLORS['blue_50']};
                }}
                QPushButton#dashboard_btn_{dashboard_id}:pressed {{
                    background-color: {COLORS['blue_100']};
                }}
            """)
            # Click handler
            btn.clicked.connect(lambda: self._select_dashboard(dashboard_id))
        else:
            btn.setStyleSheet(f"""
                QPushButton#dashboard_btn_{dashboard_id} {{
                    background-color: {COLORS['slate_100']};
                    border: 2px solid {COLORS['slate_200']};
                    border-radius: 6px;
                    text-align: left;
                    opacity: 0.6;
                }}
            """)
        
        # Store reference to inner widgets
        btn._svg_widget = svg_widget
        btn._text_label = text_label
        
        return btn
    
    def _select_dashboard(self, dashboard_id: str):
        """Load selected dashboard"""
        if not DASHBOARD_LIBS_AVAILABLE:
            QMessageBox.warning(
                self,
                "Librerías no disponibles",
                "Instala pandas y plotly:\npip install pandas plotly kaleido"
            )
            return
        
        logger.info(f"📊 Selected dashboard: {dashboard_id}")
        self.current_dashboard = dashboard_id
        
        # Clear previous dashboard
        while self.dashboard_layout.count():
            child = self.dashboard_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Load new dashboard
        if dashboard_id == 'dashboard1':
            widget = self._create_advanced_expenses_dashboard()
        elif dashboard_id == 'dashboard2':
            widget = self._create_global_accounts_dashboard()
        elif dashboard_id == 'dashboard3':
            widget = self._create_income_vs_expenses_dashboard()
        else:
            widget = QLabel("Dashboard no implementado")
        
        self.dashboard_layout.addWidget(widget)
        
        # Update card selection
        self._update_dashboard_card_selection(dashboard_id)
    
    def _update_dashboard_card_selection(self, selected_id: str):
        """Update visual state of dashboard buttons"""
        buttons = {
            'dashboard1': self.btn_dashboard1,
            'dashboard2': self.btn_dashboard2,
            'dashboard3': self.btn_dashboard3
        }
        
        for btn_id, btn in buttons.items():
            if not btn.isEnabled():
                continue
                
            if btn_id == selected_id:
                # Selected state
                btn.setStyleSheet(f"""
                    QPushButton#dashboard_btn_{btn_id} {{
                        background-color: {COLORS['blue_600']};
                        border: 2px solid {COLORS['blue_600']};
                        border-radius: 6px;
                        text-align: left;
                    }}
                    QPushButton#dashboard_btn_{btn_id}:hover {{
                        background-color: {COLORS['blue_700']};
                        border-color: {COLORS['blue_700']};
                    }}
                """)
                # Change text color to white
                if hasattr(btn, '_text_label'):
                    btn._text_label.setStyleSheet(f"""
                        QLabel {{
                            color: white;
                            font-weight: 600;
                            font-size: 13px;
                            background: transparent;
                            border: none;
                        }}
                    """)
            else:
                # Default state
                btn.setStyleSheet(f"""
                    QPushButton#dashboard_btn_{btn_id} {{
                        background-color: {COLORS['white']};
                        border: 2px solid {COLORS['slate_200']};
                        border-radius: 6px;
                        text-align: left;
                    }}
                    QPushButton#dashboard_btn_{btn_id}:hover {{
                        border-color: {COLORS['blue_500']};
                        background-color: {COLORS['blue_50']};
                    }}
                    QPushButton#dashboard_btn_{btn_id}:pressed {{
                        background-color: {COLORS['blue_100']};
                    }}
                """)
                # Reset text color
                if hasattr(btn, '_text_label'):
                    btn._text_label.setStyleSheet(f"""
                        QLabel {{
                            color: {COLORS['slate_700']};
                            font-weight: 600;
                            font-size: 13px;
                            background: transparent;
                            border: none;
                        }}
                    """)
    
    # ==================== DASHBOARD IMPLEMENTATIONS ====================
    
    def _create_advanced_expenses_dashboard(self) -> QWidget:
        """Create Advanced Expenses Dashboard (embedded version)"""
        if not DASHBOARD_LIBS_AVAILABLE:
            return QLabel("⚠️ Instala pandas y plotly para usar dashboards")
        
        # Main container
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter (left panel + right panel)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # === LEFT PANEL ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)
        
        # Account filter
        left_layout.addWidget(QLabel("Cuenta:"))
        dash1_combo_cuentas = QComboBox()
        dash1_combo_cuentas.addItem("Todas", None)
        try:
            cuentas = self.firebase_client.get_cuentas_por_proyecto(self.proyecto_id) or []
            for c in cuentas:
                dash1_combo_cuentas.addItem(c.get("nombre", str(c["id"])), c["id"])
        except Exception as e:
            logger.error(f"Error loading accounts for dashboard: {e}")
        left_layout.addWidget(dash1_combo_cuentas)
        
        # Filter type
        left_layout.addWidget(QLabel("Filtrar por:"))
        dash1_combo_filtro = QComboBox()
        dash1_combo_filtro.addItems(["Categoría", "Subcategoría"])
        left_layout.addWidget(dash1_combo_filtro)
        
        # Category tree
        left_layout.addWidget(QLabel("Categorías/Subcategorías:"))
        dash1_tree = QTreeWidget()
        dash1_tree.setHeaderLabels(["Nombre", "Total"])
        left_layout.addWidget(dash1_tree, stretch=1)
        
        # Select all / Clear buttons
        btn_select_all = QPushButton("Seleccionar todo")
        btn_clear = QPushButton("Limpiar selección")
        left_layout.addWidget(btn_select_all)
        left_layout.addWidget(btn_clear)
        
        splitter.addWidget(left_panel)
        
        # === RIGHT PANEL ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        
        # Filters
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Desde:"))
        dash1_date_desde = QDateEdit()
        dash1_date_desde.setCalendarPopup(True)
        dash1_date_desde.setDisplayFormat("yyyy-MM-dd")
        dash1_date_desde.setDate(self.fecha_inicio_edit.date())
        filters_layout.addWidget(dash1_date_desde)
        
        filters_layout.addWidget(QLabel("Hasta:"))
        dash1_date_hasta = QDateEdit()
        dash1_date_hasta.setCalendarPopup(True)
        dash1_date_hasta.setDisplayFormat("yyyy-MM-dd")
        dash1_date_hasta.setDate(self.fecha_fin_edit.date())
        filters_layout.addWidget(dash1_date_hasta)
        
        filters_layout.addWidget(QLabel("Tipo:"))
        dash1_tipo_grafico = QComboBox()
        dash1_tipo_grafico.addItems(["Donut", "Pastel", "Barra"])
        filters_layout.addWidget(dash1_tipo_grafico)
        
        right_layout.addLayout(filters_layout)
        
        # Summary label
        dash1_summary = QLabel(f"Total gastado: RD$ 0.00")
        dash1_summary.setStyleSheet("font-size:16px;font-weight:bold;")
        right_layout.addWidget(dash1_summary)
        
        # Web view for chart
        dash1_webview = QWebEngineView()
        right_layout.addWidget(dash1_webview, stretch=1)
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        btn_export_img = QPushButton("📷 Exportar Imagen")
        btn_export_pdf = QPushButton("📑 Exportar PDF")
        btn_export_img.setStyleSheet(self._get_button_style('secondary'))
        btn_export_pdf.setStyleSheet(self._get_button_style('primary'))
        export_layout.addWidget(btn_export_img)
        export_layout.addWidget(btn_export_pdf)
        right_layout.addLayout(export_layout)
        
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter)
        
        # Store references for update logic
        container._dash1_combo_cuentas = dash1_combo_cuentas
        container._dash1_combo_filtro = dash1_combo_filtro
        container._dash1_tree = dash1_tree
        container._dash1_date_desde = dash1_date_desde
        container._dash1_date_hasta = dash1_date_hasta
        container._dash1_tipo_grafico = dash1_tipo_grafico
        container._dash1_summary = dash1_summary
        container._dash1_webview = dash1_webview
        container._dash1_figura_actual = None
        container._dash1_datos_full = None
        
        # Connect signals
        def update_dashboard1():
            self._update_dashboard1(container)
        
        dash1_combo_cuentas.currentIndexChanged.connect(update_dashboard1)
        dash1_combo_filtro.currentIndexChanged.connect(update_dashboard1)
        dash1_date_desde.dateChanged.connect(update_dashboard1)
        dash1_date_hasta.dateChanged.connect(update_dashboard1)
        dash1_tipo_grafico.currentIndexChanged.connect(update_dashboard1)
        dash1_tree.itemChanged.connect(update_dashboard1)
        
        btn_select_all.clicked.connect(lambda: self._dash1_select_all(container))
        btn_clear.clicked.connect(lambda: self._dash1_clear_selection(container))
        btn_export_img.clicked.connect(lambda: self._dash1_export_image(container))
        btn_export_pdf.clicked.connect(lambda: self._dash1_export_pdf(container))
        
        # Initial load
        self._update_dashboard1(container)
        
        return container
    
    def _update_dashboard1(self, container):
        """Update dashboard 1 with data"""
        if not DASHBOARD_LIBS_AVAILABLE:
            return
        
        try:
            cuenta_id = container._dash1_combo_cuentas.currentData()
            filtro_tipo = container._dash1_combo_filtro.currentText()
            
            qd_ini = container._dash1_date_desde.date()
            qd_fin = container._dash1_date_hasta.date()
            fecha_ini = date(qd_ini.year(), qd_ini.month(), qd_ini.day())
            fecha_fin = date(qd_fin.year(), qd_fin.month(), qd_fin.day())
            
            # Get data from Firebase
            try:
                if filtro_tipo == "Categoría":
                    raw = self.firebase_client.get_gastos_agrupados_por_categoria(
                        self.proyecto_id, fecha_ini, fecha_fin, cuenta_id
                    ) or []
                else:
                    raw = self.firebase_client.get_gastos_agrupados_por_categoria_y_subcategoria(
                        self.proyecto_id, fecha_ini, fecha_fin, cuenta_id
                    ) or []
            except Exception as e:
                logger.error(f"Error loading dashboard data: {e}")
                raw = []
            
            df = pd.DataFrame(raw)
            container._dash1_datos_full = df
            
            if df.empty:
                container._dash1_webview.setHtml("<h3>No hay datos para mostrar</h3>")
                container._dash1_summary.setText("Total gastado: RD$ 0.00")
                container._dash1_tree.clear()
                return
            
            # Update tree
            container._dash1_tree.blockSignals(True)
            container._dash1_tree.clear()
            
            font_bold = QFont()
            font_bold.setBold(True)
            
            if filtro_tipo == "Categoría":
                col_nombre = "nombre" if "nombre" in df.columns else "categoria"
                for _, row in df.iterrows():
                    nombre = row.get(col_nombre, "Sin nombre")
                    total = float(row.get("total_gastado", 0.0))
                    item = QTreeWidgetItem([str(nombre), f"RD$ {total:,.2f}"])
                    item.setFont(0, font_bold)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.CheckState.Checked)
                    container._dash1_tree.addTopLevelItem(item)
            else:
                categorias = df.groupby(["categoria"])
                for cat, cat_group in categorias:
                    nombre_cat = cat if isinstance(cat, str) else str(cat)
                    total_cat = float(cat_group["total_gastado"].sum())
                    cat_item = QTreeWidgetItem([nombre_cat, f"RD$ {total_cat:,.2f}"])
                    cat_item.setFont(0, font_bold)
                    cat_item.setFlags(cat_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    cat_item.setCheckState(0, Qt.CheckState.Checked)
                    
                    subcats = cat_group[cat_group["subcategoria"].notnull()]
                    for _, sub_row in subcats.iterrows():
                        subcat = sub_row["subcategoria"]
                        total_sub = float(sub_row["total_gastado"])
                        sub_item = QTreeWidgetItem([str(subcat), f"RD$ {total_sub:,.2f}"])
                        sub_item.setFlags(sub_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        sub_item.setCheckState(0, Qt.CheckState.Checked)
                        cat_item.addChild(sub_item)
                    
                    container._dash1_tree.addTopLevelItem(cat_item)
                    cat_item.setExpanded(True)
            
            container._dash1_tree.blockSignals(False)
            
            # Update chart
            self._render_dashboard1_chart(container)
            
        except Exception as e:
            logger.error(f"Error updating dashboard1: {e}")
    
    def _render_dashboard1_chart(self, container):
        """Render chart for dashboard 1"""
        if not DASHBOARD_LIBS_AVAILABLE:
            return
        
        df = container._dash1_datos_full
        if df is None or df.empty:
            return
        
        filtro_tipo = container._dash1_combo_filtro.currentText()
        tipo_grafico = container._dash1_tipo_grafico.currentText()
        
        # Get selected items from tree
        seleccionadas = []
        for i in range(container._dash1_tree.topLevelItemCount()):
            item = container._dash1_tree.topLevelItem(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                seleccionadas.append(item.text(0))
                # Also check children if subcategory mode
                if filtro_tipo == "Subcategoría":
                    for j in range(item.childCount()):
                        child = item.child(j)
                        if child.checkState(0) == Qt.CheckState.Checked:
                            seleccionadas.append(child.text(0))
        
        if not seleccionadas:
            container._dash1_webview.setHtml("<h3>Selecciona al menos una categoría</h3>")
            return
        
        # Filter data
        if filtro_tipo == "Categoría":
            col_nombre = "nombre" if "nombre" in df.columns else "categoria"
            df_filtrado = df[df[col_nombre].isin(seleccionadas)]
        else:
            df_filtrado = df[df["subcategoria"].isin(seleccionadas)]
        
        if df_filtrado.empty:
            container._dash1_webview.setHtml("<h3>No hay datos para mostrar</h3>")
            return
        
        total = float(df_filtrado["total_gastado"].sum())
        container._dash1_summary.setText(f"Total gastado: RD$ {total:,.2f}")
        
        # Create chart
        col_nombre = "nombre" if "nombre" in df_filtrado.columns else ("subcategoria" if filtro_tipo == "Subcategoría" else "categoria")
        
        if tipo_grafico == "Donut":
            fig = px.pie(df_filtrado, names=col_nombre, values="total_gastado", hole=0.55,
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        title="Gastos por Categoría")
        elif tipo_grafico == "Pastel":
            fig = px.pie(df_filtrado, names=col_nombre, values="total_gastado",
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        title="Gastos por Categoría")
        else:  # Barra
            fig = px.bar(df_filtrado, x="total_gastado", y=col_nombre, orientation="h",
                        color=col_nombre, color_discrete_sequence=px.colors.qualitative.Pastel,
                        title="Gastos por Categoría")
        
        fig.update_layout(margin=dict(l=30, r=30, t=60, b=30))
        container._dash1_figura_actual = fig
        
        html = fig.to_html(include_plotlyjs="cdn", full_html=False)
        container._dash1_webview.setHtml(html)
    
    def _dash1_select_all(self, container):
        """Select all items in dashboard 1 tree"""
        for i in range(container._dash1_tree.topLevelItemCount()):
            item = container._dash1_tree.topLevelItem(i)
            item.setCheckState(0, Qt.CheckState.Checked)
            for j in range(item.childCount()):
                item.child(j).setCheckState(0, Qt.CheckState.Checked)
    
    def _dash1_clear_selection(self, container):
        """Clear all selections in dashboard 1 tree"""
        for i in range(container._dash1_tree.topLevelItemCount()):
            item = container._dash1_tree.topLevelItem(i)
            item.setCheckState(0, Qt.CheckState.Unchecked)
            for j in range(item.childCount()):
                item.child(j).setCheckState(0, Qt.CheckState.Unchecked)
    
    def _dash1_export_image(self, container):
        """Export dashboard 1 chart as image"""
        if container._dash1_figura_actual is None:
            QMessageBox.warning(self, "Sin gráfico", "No hay gráfico para exportar.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar imagen", "dashboard_gastos.png", "PNG (*.png)")
        if filepath:
            try:
                container._dash1_figura_actual.write_image(filepath, width=1200, height=700)
                QMessageBox.information(self, "Éxito", "Imagen exportada correctamente.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo exportar: {e}")
    
    def _dash1_export_pdf(self, container):
        """Export dashboard 1 to PDF"""
        if container._dash1_figura_actual is None or container._dash1_datos_full is None:
            QMessageBox.warning(self, "Sin datos", "No hay datos para exportar.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "dashboard_gastos.pdf", "PDF (*.pdf)")
        if not filepath:
            return
        
        try:
            df = container._dash1_datos_full.copy()
            datos_exportar = []
            
            col_cat = "nombre" if "nombre" in df.columns else "categoria"
            col_sub = "subcategoria" if "subcategoria" in df.columns else None
            
            if col_sub:
                for _, row in df.iterrows():
                    datos_exportar.append({
                        "Categoría": str(row.get(col_cat, "")),
                        "Subcategoría": str(row.get(col_sub, "")),
                        "Monto": float(row.get("total_gastado", 0)),
                        "Tipo": "Gasto"
                    })
            else:
                for _, row in df.iterrows():
                    datos_exportar.append({
                        "Categoría": str(row.get(col_cat, "")),
                        "Monto": float(row.get("total_gastado", 0)),
                        "Tipo": "Gasto"
                    })
            
            rango = f"{container._dash1_date_desde.text()} - {container._dash1_date_hasta.text()}"
            
            rg = ReportGenerator(
                data=datos_exportar,
                title="Dashboard de Gastos Avanzado",
                project_name=self.proyecto_nombre,
                date_range=rango,
                currency_symbol="RD$"
            )
            
            figures = {'grafico_principal': container._dash1_figura_actual}
            ok, msg = rg.dashboard_to_pdf(filepath, figures)
            
            if ok:
                QMessageBox.information(self, "Éxito", "PDF exportado correctamente.")
            else:
                QMessageBox.warning(self, "Error", f"Error al exportar: {msg}")
        
        except Exception as e:
            logger.error(f"Error exporting dashboard PDF: {e}")
            QMessageBox.critical(self, "Error", str(e))
    
    def _create_global_accounts_dashboard(self) -> QWidget:
        """Create Global Accounts Dashboard (embedded version)"""
        if not DASHBOARD_LIBS_AVAILABLE:
            return QLabel("⚠️ Instala pandas y plotly para usar dashboards")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # === LEFT PANEL: Table ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)
        
        left_layout.addWidget(QLabel("<b>Resumen de Cuentas:</b>"))
        dash2_table = QTableWidget()
        dash2_table.setAlternatingRowColors(True)
        left_layout.addWidget(dash2_table)
        
        splitter.addWidget(left_panel)
        
        # === RIGHT PANEL: Chart ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        
        # Filters
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Tipo:"))
        dash2_tipo = QComboBox()
        dash2_tipo.addItems(["Balance neto por cuenta", "Ingresos vs Gastos por cuenta", "Gastos por proyecto"])
        filters_layout.addWidget(dash2_tipo)
        
        filters_layout.addWidget(QLabel("Cuenta:"))
        dash2_cuenta = QComboBox()
        filters_layout.addWidget(dash2_cuenta)
        
        filters_layout.addWidget(QLabel("Paleta:"))
        dash2_paleta = QComboBox()
        dash2_paleta.addItems(["Pastel", "Set3", "Dark2", "Viridis"])
        filters_layout.addWidget(dash2_paleta)
        
        right_layout.addLayout(filters_layout)
        
        # Web view
        dash2_webview = QWebEngineView()
        right_layout.addWidget(dash2_webview, stretch=1)
        
        # Export button
        btn_export = QPushButton("📑 Exportar PDF")
        btn_export.setStyleSheet(self._get_button_style('primary'))
        right_layout.addWidget(btn_export)
        
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter)
        
        # Store references
        container._dash2_table = dash2_table
        container._dash2_tipo = dash2_tipo
        container._dash2_cuenta = dash2_cuenta
        container._dash2_paleta = dash2_paleta
        container._dash2_webview = dash2_webview
        container._dash2_figura_actual = None
        container._dash2_df_cuentas = None
        container._dash2_df_trans = None
        
        # Connect signals
        def update_dashboard2():
            self._update_dashboard2(container)
        
        dash2_tipo.currentIndexChanged.connect(update_dashboard2)
        dash2_cuenta.currentIndexChanged.connect(update_dashboard2)
        dash2_paleta.currentIndexChanged.connect(update_dashboard2)
        btn_export.clicked.connect(lambda: self._dash2_export_pdf(container))
        
        # Initial load
        self._load_dashboard2_data(container)
        update_dashboard2()
        
        return container
    
    def _load_dashboard2_data(self, container):
        """Load data for dashboard 2"""
        try:
            if hasattr(self.firebase_client, 'get_balances_globales_todas_cuentas'):
                resumen = self.firebase_client.get_balances_globales_todas_cuentas() or []
            else:
                resumen = []
            
            df = pd.DataFrame(resumen)
            if not df.empty:
                if "cuenta_nombre" in df.columns:
                    df.rename(columns={"cuenta_nombre": "cuenta"}, inplace=True)
                if "cuenta" not in df.columns and "nombre" in df.columns:
                    df.rename(columns={"nombre": "cuenta"}, inplace=True)
                if "total_ingresos" not in df.columns:
                    df["total_ingresos"] = 0.0
                if "total_gastos" not in df.columns:
                    df["total_gastos"] = 0.0
                if "balance" not in df.columns:
                    df["balance"] = df["total_ingresos"] - df["total_gastos"]
            
            container._dash2_df_cuentas = df
            
            # Load transactions
            if hasattr(self.firebase_client, 'get_todas_las_transacciones_globales'):
                trans = self.firebase_client.get_todas_las_transacciones_globales() or []
            else:
                trans = []
            container._dash2_df_trans = pd.DataFrame(trans)
            
            # Update table
            if not df.empty:
                container._dash2_table.setRowCount(len(df))
                container._dash2_table.setColumnCount(4)
                container._dash2_table.setHorizontalHeaderLabels(["Cuenta", "Ingresos", "Gastos", "Balance"])
                
                for i, row in df.iterrows():
                    container._dash2_table.setItem(i, 0, QTableWidgetItem(str(row.get("cuenta", ""))))
                    container._dash2_table.setItem(i, 1, QTableWidgetItem(f"RD$ {float(row['total_ingresos']):,.2f}"))
                    container._dash2_table.setItem(i, 2, QTableWidgetItem(f"RD$ {float(row['total_gastos']):,.2f}"))
                    container._dash2_table.setItem(i, 3, QTableWidgetItem(f"RD$ {float(row['balance']):,.2f}"))
            
            # Update cuenta combo
            container._dash2_cuenta.clear()
            container._dash2_cuenta.addItem("Todas", None)
            if not df.empty:
                for nombre in df["cuenta"].dropna().unique():
                    container._dash2_cuenta.addItem(str(nombre), str(nombre))
        
        except Exception as e:
            logger.error(f"Error loading dashboard 2 data: {e}")
    
    def _update_dashboard2(self, container):
        """Update dashboard 2 chart"""
        if not DASHBOARD_LIBS_AVAILABLE:
            return
        
        df = container._dash2_df_cuentas
        if df is None or df.empty:
            container._dash2_webview.setHtml("<h3>No hay datos</h3>")
            return
        
        tipo = container._dash2_tipo.currentText()
        paleta = container._dash2_paleta.currentText()
        
        palettes = {
            "Pastel": px.colors.qualitative.Pastel,
            "Set3": px.colors.qualitative.Set3,
            "Dark2": px.colors.qualitative.Dark2,
            "Viridis": px.colors.sequential.Viridis
        }
        palette_colors = palettes.get(paleta, px.colors.qualitative.Pastel)
        
        if tipo == "Balance neto por cuenta":
            fig = px.bar(df, x="balance", y="cuenta", orientation="h",
                        labels={"cuenta": "Cuenta", "balance": "Balance"},
                        color_discrete_sequence=palette_colors,
                        title="Balance neto por cuenta")
        elif tipo == "Ingresos vs Gastos por cuenta":
            df_melt = df.melt(id_vars="cuenta", value_vars=["total_ingresos", "total_gastos"],
                            var_name="Tipo", value_name="Monto")
            df_melt["Tipo"] = df_melt["Tipo"].map({"total_ingresos": "Ingresos", "total_gastos": "Gastos"})
            fig = px.bar(df_melt, x="Monto", y="cuenta", color="Tipo", orientation="h",
                        barmode="group", color_discrete_sequence=palette_colors,
                        title="Ingresos vs Gastos")
        else:  # Gastos por proyecto
            cuenta_sel = container._dash2_cuenta.currentData()
            df_trx = container._dash2_df_trans
            if df_trx is not None and not df_trx.empty:
                df_trx = df_trx[df_trx["tipo"] == "Gasto"]
                if cuenta_sel and "cuenta_nombre" in df_trx.columns:
                    df_trx = df_trx[df_trx["cuenta_nombre"] == cuenta_sel]
                
                if not df_trx.empty:
                    nombre_col = "proyecto_nombre" if "proyecto_nombre" in df_trx.columns else "proyecto_id"
                    gastos_proj = df_trx.groupby(nombre_col)["monto"].sum().reset_index(name="monto")
                    fig = px.pie(gastos_proj, names=nombre_col, values="monto",
                                title="Gastos por Proyecto", color_discrete_sequence=palette_colors)
                else:
                    fig = px.bar(x=["Sin datos"], y=[0])
            else:
                fig = px.bar(x=["Sin datos"], y=[0])
        
        container._dash2_figura_actual = fig
        html = fig.to_html(include_plotlyjs="cdn", full_html=False)
        container._dash2_webview.setHtml(html)
    
    def _dash2_export_pdf(self, container):
        """Export dashboard 2 to PDF"""
        QMessageBox.information(self, "Exportar", "Exportación de Dashboard Global en desarrollo")
    
    def _create_income_vs_expenses_dashboard(self) -> QWidget:
        """Create Income vs Expenses Dashboard (embedded version)"""
        if not DASHBOARD_LIBS_AVAILABLE:
            return QLabel("⚠️ Instala pandas y plotly para usar dashboards")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Simple message for now
        label = QLabel("🚧 Dashboard Ingresos vs Gastos\n\nEn desarrollo - Implementación completa próximamente")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 14px; padding: 60px;")
        layout.addWidget(label)
        
        return container
    
    # ==================== SVG ICONS ====================
    
    def _get_document_icon_svg(self) -> str:
        """SVG icon for document/report"""
        return f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{COLORS['blue_600']}" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
        '''
    
    def _get_folder_icon_svg(self) -> str:
        """SVG icon for folder/category"""
        return f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{COLORS['amber_600']}" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
        </svg>
        '''
    
    def _get_bank_icon_svg(self) -> str:
        """SVG icon for bank/account"""
        return f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{COLORS['green_600']}" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
        '''
    
    def _get_globe_icon_svg(self) -> str:
        """SVG icon for globe/global"""
        return f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{COLORS['blue_600']}" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="2" y1="12" x2="22" y2="12"></line>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
        </svg>
        '''
    
    def _get_chart_icon_svg(self) -> str:
        """SVG icon for chart"""
        return f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{COLORS['purple_600']}" stroke-width="2">
            <line x1="12" y1="20" x2="12" y2="10"></line>
            <line x1="18" y1="20" x2="18" y2="4"></line>
            <line x1="6" y1="20" x2="6" y2="16"></line>
        </svg>
        '''
    
    def _get_pie_chart_icon_svg(self) -> str:
        """SVG icon for pie chart"""
        return f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{COLORS['pink_600']}" stroke-width="2">
            <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
            <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
        </svg>
        '''
    
    def _get_trending_icon_svg(self) -> str:
        """SVG icon for trending"""
        return f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{COLORS['emerald_600']}" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
        </svg>
        '''
    
    # ==================== FILTERS & PREVIEW ====================
    
    def _create_filters_toolbar(self) -> QWidget:
        """Create filters toolbar (dates, etc.) - VERSIÓN COMPACTA"""
        toolbar = QWidget()
        toolbar.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['white']};
                border-radius: 6px;
                padding: 8px 12px;
            }}
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(10)  # Antes: SPACING['md']
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Date filters - LABELS MÁS PEQUEÑOS
        date_label = QLabel("📅 Período:")
        date_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_700']};
                font-weight: 600;
                font-size: 12px;
                background: transparent;
            }}
        """)
        layout.addWidget(date_label)
        
        # Start date
        desde_label = QLabel("Desde:")
        desde_label.setStyleSheet(f"color: {COLORS['slate_700']}; font-size: 11px; background: transparent;")
        layout.addWidget(desde_label)
        
        self.fecha_inicio_edit = QDateEdit()
        self.fecha_inicio_edit.setCalendarPopup(True)
        self.fecha_inicio_edit.setDisplayFormat("yyyy-MM-dd")
        self.fecha_inicio_edit.setStyleSheet(self._get_date_edit_style())
        self.fecha_inicio_edit.setFixedHeight(28)  # MÁS PEQUEÑO
        self.fecha_inicio_edit.dateChanged.connect(self._on_date_changed)
        layout.addWidget(self.fecha_inicio_edit)
        
        # End date
        hasta_label = QLabel("Hasta:")
        hasta_label.setStyleSheet(f"color: {COLORS['slate_700']}; font-size: 11px; background: transparent;")
        layout.addWidget(hasta_label)
        
        self.fecha_fin_edit = QDateEdit()
        self.fecha_fin_edit.setCalendarPopup(True)
        self.fecha_fin_edit.setDisplayFormat("yyyy-MM-dd")
        self.fecha_fin_edit.setStyleSheet(self._get_date_edit_style())
        self.fecha_fin_edit.setFixedHeight(28)  # MÁS PEQUEÑO
        self.fecha_fin_edit.dateChanged.connect(self._on_date_changed)
        layout.addWidget(self.fecha_fin_edit)
        
        # Refresh button - MÁS PEQUEÑO
        refresh_btn = QPushButton("🔄 Recargar")
        refresh_btn.setStyleSheet(self._get_button_style('secondary'))
        refresh_btn.setFixedHeight(28)  # MÁS PEQUEÑO
        refresh_btn.clicked.connect(self._reload_from_firebase)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        
        return toolbar
    
    def _create_preview_area(self) -> QGroupBox:
        """Create preview area for report data"""
        group = QGroupBox("Vista Previa del Reporte")
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS['white']};
                border-radius: 8px;
                border: 1px solid {COLORS['slate_200']};
                padding: 12px;
                font-size: 13px;
                font-weight: 600;
                color: {COLORS['slate_800']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Cuenta", "Categoría", "Descripción", "Monto", "Adjuntos"
        ])
        
        # Table settings
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(self._get_table_style())
        
        # ✅ NUEVO: Altura de filas más compacta
        self.table.verticalHeader().setDefaultSectionSize(32)  # Antes: 40+
        self.table.verticalHeader().setVisible(False)  # Ocultar números de fila
        
        # Header settings
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)
        
        # Column widths - MÁS COMPACTOS
        self.table.setColumnWidth(0, 90)   # Antes: 100
        self.table.setColumnWidth(1, 70)   # Antes: 80
        self.table.setColumnWidth(2, 130)  # Antes: 150
        self.table.setColumnWidth(3, 130)  # Antes: 150
        self.table.setColumnWidth(5, 110)  # Antes: 120
        self.table.setColumnWidth(6, 70)   # Antes: 80
        
        layout.addWidget(self.table)
        
        # Totals label - LETRA MÁS PEQUEÑA
        self.totals_label = QLabel()
        self.totals_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.totals_label.setStyleSheet(f"color: {COLORS['slate_700']}; font-size: 12px; font-weight: 600; padding: 6px; background: transparent;")
        layout.addWidget(self.totals_label)
        
        group.setLayout(layout)
        return group
    
    def _create_export_buttons(self) -> QWidget:
        """Create export buttons bar"""
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        
        layout = QHBoxLayout(container)
        layout.setSpacing(SPACING['md'])
        
        layout.addStretch()
        
        # PDF button
        self.btn_pdf = QPushButton("📑 Exportar PDF")
        self.btn_pdf.setStyleSheet(self._get_button_style('primary'))
        self.btn_pdf.clicked.connect(self._exportar_pdf)
        if not REPORT_GENERATOR_AVAILABLE:
            self.btn_pdf.setEnabled(False)
            self.btn_pdf.setToolTip("ReportGenerator no disponible")
        layout.addWidget(self.btn_pdf)
        
        # Excel button
        self.btn_excel = QPushButton("📊 Exportar Excel")
        self.btn_excel.setStyleSheet(self._get_button_style('primary'))
        self.btn_excel.clicked.connect(self._exportar_excel)
        if not REPORT_GENERATOR_AVAILABLE:
            self.btn_excel.setEnabled(False)
        layout.addWidget(self.btn_excel)
        
        return container
    
    # ==================== STYLES ====================
    
    def _get_tab_style(self) -> str:
        """Get tab widget stylesheet"""
        return f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['slate_200']};
                border-radius: 8px;
                background-color: {COLORS['slate_50']};
                padding: 10px;
            }}
            QTabBar::tab {{
                background-color: {COLORS['slate_100']};
                color: {COLORS['slate_700']};
                padding: 10px 20px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 600;
                font-size: 14px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['white']};
                color: {COLORS['blue_600']};
                border-bottom: 2px solid {COLORS['blue_600']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLORS['slate_200']};
            }}
        """
    
    def _get_button_style(self, variant='primary') -> str:
        """Get button stylesheet - VERSIÓN COMPACTA"""
        if variant == 'primary':
            return f"""
                QPushButton {{
                    background-color: {COLORS['blue_600']};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 7px 16px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['blue_700']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['blue_800']};
                }}
                QPushButton:disabled {{
                    background-color: {COLORS['slate_300']};
                    color: {COLORS['slate_500']};
                }}
            """
        else:  # secondary
            return f"""
                QPushButton {{
                    background-color: {COLORS['white']};
                    color: {COLORS['slate_700']};
                    border: 1px solid {COLORS['slate_300']};
                    border-radius: 5px;
                    padding: 6px 14px;
                    font-size: 11px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['slate_50']};
                    border-color: {COLORS['slate_400']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['slate_100']};
                }}
            """
    
    def _get_date_edit_style(self) -> str:
        """Get DateEdit stylesheet - VERSIÓN COMPACTA"""
        return f"""
            QDateEdit {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 11px;
                color: {COLORS['slate_800']};
            }}
            QDateEdit:hover {{
                border-color: {COLORS['blue_500']};
            }}
            QDateEdit::drop-down {{
                border: none;
                width: 20px;
            }}
        """
    
    def _get_table_style(self) -> str:
        """Get table stylesheet - VERSIÓN COMPACTA"""
        return f"""
            QTableWidget {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: 6px;
                gridline-color: {COLORS['slate_200']};
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 4px 6px;
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['blue_100']};
                color: {COLORS['slate_900']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['slate_100']};
                color: {COLORS['slate_700']};
                padding: 6px 8px;
                border: none;
                border-bottom: 2px solid {COLORS['slate_300']};
                font-weight: 600;
                font-size: 11px;
            }}
        """
    
    # ==================== DATA LOADING ====================
    
    def _load_maps(self):
        """Load lookup maps for accounts and categories"""
        try:
            cuentas_list = self.firebase_client.get_cuentas_by_proyecto(self.proyecto_id)
            categorias_list = self.firebase_client.get_categorias_by_proyecto(self.proyecto_id)
            
            self.cuentas_map = {str(c["id"]): c.get("nombre", "Sin nombre") for c in cuentas_list}
            self.categorias_map = {str(c["id"]): c.get("nombre", "Sin nombre") for c in categorias_list}
            
            logger.info(f"Loaded {len(self.cuentas_map)} accounts, {len(self.categorias_map)} categories")
        except Exception as e:
            logger.error(f"Error loading maps: {e}")
            self.cuentas_map = {}
            self.categorias_map = {}
    
    def _set_smart_date_range(self):
        """Calculate smart date range from first transaction to today"""
        try:
            logger.info(f"🔍 Calculating smart date range for project {self.proyecto_id}")
            
            all_trans = self.firebase_client.get_transacciones_by_proyecto(
                self.proyecto_id,
                cuenta_id=None,
                include_deleted=False
            )
            
            if not all_trans:
                logger.warning("⚠️ No transactions found, using current month as default")
                today = date.today()
                self.fecha_inicio = date(today.year, today.month, 1)
                self.fecha_fin = today
            else:
                fechas = []
                for trans in all_trans:
                    trans_date = self._parse_date(trans.get('fecha'))
                    if trans_date:
                        fechas.append(trans_date)
                
                if fechas:
                    self.fecha_inicio = min(fechas)
                    self.fecha_fin = date.today()
                    logger.info(f"✅ Smart date range: {self.fecha_inicio} to {self.fecha_fin}")
                else:
                    today = date.today()
                    self.fecha_inicio = date(today.year, today.month, 1)
                    self.fecha_fin = today
            
            # Update UI
            self.fecha_inicio_edit.blockSignals(True)
            self.fecha_fin_edit.blockSignals(True)
            
            self.fecha_inicio_edit.setDate(QDate(self.fecha_inicio.year, self.fecha_inicio.month, self.fecha_inicio.day))
            self.fecha_fin_edit.setDate(QDate(self.fecha_fin.year, self.fecha_fin.month, self.fecha_fin.day))
            
            self.fecha_inicio_edit.blockSignals(False)
            self.fecha_fin_edit.blockSignals(False)
            
        except Exception as e:
            logger.error(f"❌ Error calculating smart date range: {e}", exc_info=True)
            today = date.today()
            self.fecha_inicio = date(today.year, today.month, 1)
            self.fecha_fin = today
    
    def _parse_date(self, date_val: Any) -> Optional[date]:
        """Parse date from various formats"""
        if not date_val:
            return None
        try:
            if type(date_val) is date:
                return date_val
            if isinstance(date_val, datetime):
                return date_val.date()
            if isinstance(date_val, str):
                return datetime.strptime(date_val[:10], "%Y-%m-%d").date()
        except Exception:
            return None
        return None
    
    # ==================== REPORT SELECTION ====================
    
    def _select_report(self, report_id: str):
        """Handle report selection"""
        logger.info(f"📊 Selected report: {report_id}")
        self.current_report = report_id
        
        # Update card styles (highlight selected)
        self._update_card_selection(report_id)
        
        # Load report data
        if report_id == 'detailed':
            # Reset table to detailed view
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                "Fecha", "Tipo", "Cuenta", "Categoría", "Descripción", "Monto", "Adjuntos"
            ])
            self._load_detailed_report()
        elif report_id == 'category':
            self._load_category_report()
        elif report_id == 'cashflow':
            self._load_account_summary_report()
        elif report_id == 'summary':
            self._load_global_accounts_report()
    
    def _update_card_selection(self, selected_id: str):
        """Update visual state of report buttons"""
        buttons = {
            'detailed': self.btn_detailed,
            'category': self.btn_category,
            'cashflow': self.btn_cashflow,
            'summary': self.btn_summary
        }
        
        for btn_id, btn in buttons.items():
            if btn_id == selected_id:
                # Selected state
                btn.setStyleSheet(f"""
                    QPushButton#report_btn_{btn_id} {{
                        background-color: {COLORS['blue_600']};
                        border: 2px solid {COLORS['blue_600']};
                        border-radius: 6px;
                        text-align: left;
                    }}
                    QPushButton#report_btn_{btn_id}:hover {{
                        background-color: {COLORS['blue_700']};
                        border-color: {COLORS['blue_700']};
                    }}
                """)
                # Change text color to white
                if hasattr(btn, '_text_label'):
                    btn._text_label.setStyleSheet(f"""
                        QLabel {{
                            color: white;
                            font-weight: 600;
                            font-size: 13px;
                            background: transparent;
                            border: none;
                        }}
                    """)
            else:
                # Default state
                btn.setStyleSheet(f"""
                    QPushButton#report_btn_{btn_id} {{
                        background-color: {COLORS['white']};
                        border: 2px solid {COLORS['slate_200']};
                        border-radius: 6px;
                        text-align: left;
                    }}
                    QPushButton#report_btn_{btn_id}:hover {{
                        border-color: {COLORS['blue_500']};
                        background-color: {COLORS['blue_50']};
                    }}
                    QPushButton#report_btn_{btn_id}:pressed {{
                        background-color: {COLORS['blue_100']};
                    }}
                """)
                # Reset text color
                if hasattr(btn, '_text_label'):
                    btn._text_label.setStyleSheet(f"""
                        QLabel {{
                            color: {COLORS['slate_700']};
                            font-weight: 600;
                            font-size: 13px;
                            background: transparent;
                            border: none;
                        }}
                    """)

    # ==================== DETAILED REPORT ====================
    
    def _load_detailed_report(self):
        """Load detailed transactions report"""
        try:
            qdesde = self.fecha_inicio_edit.date()
            qhasta = self.fecha_fin_edit.date()
            
            desde_date = qdesde.toPyDate()
            hasta_date = qhasta.toPyDate()
            
            if hasta_date < desde_date:
                self.totals_label.setText("<font color='red'>Fecha 'Hasta' menor que 'Desde'</font>")
                self.table.setRowCount(0)
                return
            
            # Get all transactions (cached if possible)
            if self._all_transacciones is None:
                self._all_transacciones = self.firebase_client.get_transacciones_by_proyecto(
                    self.proyecto_id
                )
            
            transacciones = self._all_transacciones or []
            
            # Filter by date range
            filtradas: List[Dict[str, Any]] = []
            total_ingresos = 0.0
            total_gastos = 0.0
            
            for t in transacciones:
                fecha_date = self._parse_date(t.get("fecha"))
                
                if not fecha_date:
                    continue
                
                if not (desde_date <= fecha_date <= hasta_date):
                    continue
                
                # Prepare data
                fecha_str = fecha_date.strftime("%Y-%m-%d")
                tipo = str(t.get("tipo", "")).lower()
                cuenta_nombre = self.cuentas_map.get(str(t.get("cuenta_id", "")), str(t.get("cuenta_id", "Sin cuenta")))
                categoria_nombre = self.categorias_map.get(str(t.get("categoria_id", "")), str(t.get("categoria_id", "Sin categoría")))
                descripcion = t.get("descripcion", "")
                
                # Parse monto
                try:
                    monto_val = t.get("monto", 0.0)
                    if monto_val is None or monto_val == '':
                        monto = 0.0
                    else:
                        monto = float(monto_val)
                except (ValueError, TypeError):
                    monto = 0.0
                
                if "ingreso" in tipo:
                    total_ingresos += monto
                elif "gasto" in tipo:
                    total_gastos += monto
                
                # Adjuntos
                adjuntos_paths = t.get("adjuntos_paths", [])
                adjuntos_count = len(adjuntos_paths) if adjuntos_paths else 0
                adjuntos_display = f"📎 {adjuntos_count}" if adjuntos_count > 0 else ""
                
                # Store for export
                filtradas.append({
                    "Fecha": fecha_str,
                    "Cuenta": cuenta_nombre,
                    "Categoría": categoria_nombre,
                    "Descripción": descripcion,
                    "Monto": monto,
                    "Tipo": t.get("tipo", "").capitalize(),
                    "Adjuntos": adjuntos_display,
                    "_raw_tipo": tipo,
                    "_transaction_id": t.get("id", ""),
                    "_adjuntos_paths": adjuntos_paths
                })
            
            self.transacciones_filtradas = filtradas
            
            # Populate table
            self.table.setRowCount(len(filtradas))
            for row, t in enumerate(filtradas):
                # Fecha
                self.table.setItem(row, 0, QTableWidgetItem(t["Fecha"]))
                
                # Tipo
                tipo_item = QTableWidgetItem(t["Tipo"])
                raw_tipo = t["_raw_tipo"]
                if "ingreso" in raw_tipo:
                    tipo_item.setForeground(QColor(COLORS['green_700']))
                elif "gasto" in raw_tipo:
                    tipo_item.setForeground(QColor(COLORS['red_700']))
                self.table.setItem(row, 1, tipo_item)
                
                # Cuenta
                self.table.setItem(row, 2, QTableWidgetItem(t["Cuenta"]))
                
                # Categoría
                self.table.setItem(row, 3, QTableWidgetItem(t["Categoría"]))
                
                # Descripción
                self.table.setItem(row, 4, QTableWidgetItem(t["Descripción"]))
                
                # Monto
                try:
                    monto_valor = t.get('Monto', 0.0)
                    if not isinstance(monto_valor, (int, float)):
                        monto_valor = float(monto_valor)
                    monto_display = f"RD$ {monto_valor:,.2f}"
                except Exception:
                    monto_display = "RD$ 0.00"
                
                monto_item = QTableWidgetItem(monto_display)
                monto_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if "ingreso" in raw_tipo:
                    monto_item.setForeground(QColor(COLORS['green_700']))
                elif "gasto" in raw_tipo:
                    monto_item.setForeground(QColor(COLORS['red_700']))
                self.table.setItem(row, 5, monto_item)
                
                # Adjuntos
                adjuntos_item = QTableWidgetItem(t["Adjuntos"])
                adjuntos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                if t["Adjuntos"]:
                    adjuntos_item.setForeground(QColor(COLORS['blue_600']))
                self.table.setItem(row, 6, adjuntos_item)
            
            # Update totals
            total_trans = len(filtradas)
            if total_trans == 0:
                self.totals_label.setText("No hay transacciones en el rango seleccionado.")
            else:
                balance = total_ingresos - total_gastos
                self.totals_label.setText(
                    f"<b>Items:</b> {total_trans} | "
                    f"<b>Ingresos:</b> <font color='{COLORS['green_700']}'>RD$ {total_ingresos:,.2f}</font> | "
                    f"<b>Gastos:</b> <font color='{COLORS['red_700']}'>RD$ {total_gastos:,.2f}</font> | "
                    f"<b>Balance:</b> <font color='{COLORS['blue_700']}'>RD$ {balance:,.2f}</font>"
                )
            
            logger.info(f"�� Loaded {total_trans} transactions for detailed report")
            
        except Exception as e:
            logger.error(f"Error loading detailed report: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar el reporte:\n{str(e)}")
    
    # ==================== CATEGORY REPORT ====================
    
    def _load_category_report(self):
        """Load expenses by category report (tree structure)"""
        try:
            qdesde = self.fecha_inicio_edit.date()
            qhasta = self.fecha_fin_edit.date()
            
            desde_date = qdesde.toPyDate()
            hasta_date = qhasta.toPyDate()
            
            if hasta_date < desde_date:
                self.totals_label.setText("<font color='red'>Fecha 'Hasta' menor que 'Desde'</font>")
                self.table.setRowCount(0)
                return
            
            # Get category/subcategory grouping
            agrupacion = self._obtener_agrupacion_gastos(desde_date, hasta_date)
            
            if not agrupacion:
                self.table.setRowCount(0)
                self.totals_label.setText("No hay gastos en el rango seleccionado.")
                return
            
            # Prepare data for table display
            self.transacciones_filtradas = []
            total_general = 0.0
            
            for cat_nombre in sorted(agrupacion.keys()):
                sub_list = agrupacion[cat_nombre]
                total_cat = sum(s["total_gasto"] for s in sub_list)
                total_general += total_cat
                
                # Add category row
                self.transacciones_filtradas.append({
                    "Categoría": cat_nombre,
                    "Subcategoría": "",
                    "Monto": total_cat,
                    "_is_category": True
                })
                
                # Add subcategory rows
                for s in sorted(sub_list, key=lambda x: (x["subcategoria"] == "", x["subcategoria"] or "")):
                    sub_nombre = s["subcategoria"] or "Sin subcategoría"
                    total_sub = s["total_gasto"]
                    
                    self.transacciones_filtradas.append({
                        "Categoría": cat_nombre,
                        "Subcategoría": sub_nombre,
                        "Monto": total_sub,
                        "_is_category": False
                    })
            
            # Add total row
            self.transacciones_filtradas.append({
                "Categoría": "TOTAL GENERAL",
                "Subcategoría": "",
                "Monto": total_general,
                "_is_category": True,
                "_is_total": True
            })
            
            # Update table structure
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["Categoría", "Subcategoría", "Monto"])
            
            # Adjust column resize modes
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
            self.table.setColumnWidth(2, 150)
            
            # Populate table
            self.table.setRowCount(len(self.transacciones_filtradas))
            
            for row, item in enumerate(self.transacciones_filtradas):
                is_category = item.get("_is_category", False)
                is_total = item.get("_is_total", False)
                
                # Categoría
                cat_item = QTableWidgetItem(item["Categoría"])
                if is_category or is_total:
                    font_bold = QFont()
                    font_bold.setBold(True)
                    cat_item.setFont(font_bold)
                    if is_total:
                        cat_item.setForeground(QColor(COLORS['blue_700']))
                self.table.setItem(row, 0, cat_item)
                
                # Subcategoría
                sub_text = item["Subcategoría"]
                if sub_text and not is_category:
                    sub_text = f"   → {sub_text}"  # Indent subcategories
                sub_item = QTableWidgetItem(sub_text)
                self.table.setItem(row, 1, sub_item)
                
                # Monto
                monto = item["Monto"]
                monto_item = QTableWidgetItem(f"RD$ {monto:,.2f}")
                monto_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                monto_item.setForeground(QColor(COLORS['red_700']))
                if is_category or is_total:
                    font_bold = QFont()
                    font_bold.setBold(True)
                    monto_item.setFont(font_bold)
                    if is_total:
                        monto_item.setForeground(QColor(COLORS['blue_700']))
                self.table.setItem(row, 2, monto_item)
            
            # Update totals
            self.totals_label.setText(
                f"<b>Total de Gastos:</b> <font color='{COLORS['red_700']}'>RD$ {total_general:,.2f}</font>"
            )
            
            logger.info(f"✅ Loaded category report with {len(agrupacion)} categories, total: RD$ {total_general:,.2f}")
            
        except Exception as e:
            logger.error(f"Error loading category report: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar el reporte:\n{str(e)}")
    
    def _obtener_agrupacion_gastos(self, desde_date: date, hasta_date: date) -> Dict[str, List[Dict[str, Any]]]:
        """Group expenses by category and subcategory"""
        from collections import defaultdict
        
        # Get catalogs
        categorias = self.firebase_client.get_categorias_by_proyecto(self.proyecto_id)
        subcategorias = self.firebase_client.get_subcategorias_by_proyecto(self.proyecto_id)
        
        cat_by_id = {str(c["id"]): c for c in categorias}
        subcat_by_id = {str(s["id"]): s for s in subcategorias}
        
        cat_name_by_id = {cid: c.get("nombre", "") for cid, c in cat_by_id.items()}
        subcat_info_by_id = {
            sid: (s.get("nombre", ""), str(s.get("categoria_id", "")))
            for sid, s in subcat_by_id.items()
        }
        
        # Get transactions
        if self._all_transacciones is None:
            self._all_transacciones = self.firebase_client.get_transacciones_by_proyecto(
                self.proyecto_id
            )
        transacciones = self._all_transacciones or []
        
        cat_map: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        for t in transacciones:
            tipo = str(t.get("tipo", "")).lower()
            if tipo != "gasto":
                continue
            
            fecha_date = self._parse_date(t.get("fecha"))
            if not fecha_date:
                continue
            
            if not (desde_date <= fecha_date <= hasta_date):
                continue
            
            categoria_id = str(t.get("categoria_id", ""))
            subcategoria_id = (
                str(t.get("subcategoria_id", ""))
                if t.get("subcategoria_id") is not None
                else None
            )
            
            try:
                monto = float(t.get("monto", 0.0))
            except (ValueError, TypeError):
                monto = 0.0
            
            cat_nombre = cat_name_by_id.get(categoria_id, "Sin categoría")
            sub_nombre: Optional[str] = None
            if subcategoria_id and subcategoria_id in subcat_info_by_id:
                sub_nombre = subcat_info_by_id[subcategoria_id][0]
            
            cat_map[cat_nombre][sub_nombre] += monto
        
        result: Dict[str, List[Dict[str, Any]]] = {}
        for cat_nombre, sub_dict in cat_map.items():
            lista_subs: List[Dict[str, Any]] = []
            for sub_nombre, total_val in sub_dict.items():
                lista_subs.append({
                    "subcategoria": sub_nombre or "",
                    "total_gasto": total_val,
                })
            result[cat_nombre] = lista_subs
        
        return result
    
    # ==================== ACCOUNT SUMMARY REPORT ====================
    
    def _load_account_summary_report(self):
        """Load account summary report (Income/Expenses/Balance per account)"""
        try:
            qdesde = self.fecha_inicio_edit.date()
            qhasta = self.fecha_fin_edit.date()
            
            desde_date = qdesde.toPyDate()
            hasta_date = qhasta.toPyDate()
            
            if hasta_date < desde_date:
                self.totals_label.setText("<font color='red'>Fecha 'Hasta' menor que 'Desde'</font>")
                self.table.setRowCount(0)
                return
            
            # Get accounts
            cuentas = self.firebase_client.get_cuentas_by_proyecto(self.proyecto_id)
            cuentas_by_id = {str(c["id"]): c for c in cuentas}
            
            # Get transactions
            if self._all_transacciones is None:
                self._all_transacciones = self.firebase_client.get_transacciones_by_proyecto(
                    self.proyecto_id
                )
            transacciones = self._all_transacciones or []
            
            # Aggregate by account
            resumen: Dict[str, Dict[str, float]] = {}
            total_ingresos_general = 0.0
            total_gastos_general = 0.0
            
            for t in transacciones:
                fecha_date = self._parse_date(t.get("fecha"))
                if not fecha_date:
                    continue
                
                if not (desde_date <= fecha_date <= hasta_date):
                    continue
                
                cuenta_id = str(t.get("cuenta_id", ""))
                cuenta_data = cuentas_by_id.get(cuenta_id)
                if not cuenta_data:
                    continue
                
                cuenta_nombre = cuenta_data.get("nombre", f"Cuenta {cuenta_id}")
                
                tipo = str(t.get("tipo", "")).lower()
                es_transferencia = t.get("es_transferencia") == True
                
                try:
                    monto = float(t.get("monto", 0.0))
                except:
                    monto = 0.0
                
                if cuenta_nombre not in resumen:
                    resumen[cuenta_nombre] = {"Ingresos": 0.0, "Gastos": 0.0}
                
                if "ingreso" in tipo:
                    resumen[cuenta_nombre]["Ingresos"] += monto
                    if not es_transferencia:
                        total_ingresos_general += monto
                elif "gasto" in tipo:
                    resumen[cuenta_nombre]["Gastos"] += monto
                    if not es_transferencia:
                        total_gastos_general += monto
            
            # Build rows
            rows: List[Dict[str, Any]] = []
            for cuenta_nombre in sorted(resumen.keys()):
                ing = resumen[cuenta_nombre]["Ingresos"]
                gas = resumen[cuenta_nombre]["Gastos"]
                bal = ing - gas
                rows.append({
                    "Cuenta": cuenta_nombre,
                    "Ingresos": ing,
                    "Gastos": gas,
                    "Balance": bal,
                })
            
            balance_total = total_ingresos_general - total_gastos_general
            rows.append({
                "Cuenta": "TOTAL GENERAL",
                "Ingresos": total_ingresos_general,
                "Gastos": total_gastos_general,
                "Balance": balance_total,
                "_is_total": True
            })
            
            self.transacciones_filtradas = rows
            
            # Update table structure
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Cuenta", "Ingresos", "Gastos", "Balance"])
            
            # Adjust column resize modes
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
            self.table.setColumnWidth(1, 150)
            self.table.setColumnWidth(2, 150)
            self.table.setColumnWidth(3, 150)
            
            # Populate table
            self.table.setRowCount(len(rows))
            
            for i, row in enumerate(rows):
                is_total = row.get("_is_total", False)
                
                # Cuenta
                item_cuenta = QTableWidgetItem(str(row["Cuenta"]))
                item_cuenta.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if is_total:
                    font_bold = QFont()
                    font_bold.setBold(True)
                    item_cuenta.setFont(font_bold)
                    item_cuenta.setForeground(QColor(COLORS['blue_700']))
                self.table.setItem(i, 0, item_cuenta)
                
                # Ingresos
                item_ing = QTableWidgetItem(f"RD$ {row['Ingresos']:,.2f}")
                item_ing.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                item_ing.setForeground(QColor(COLORS['green_700']))
                if is_total:
                    font_bold = QFont()
                    font_bold.setBold(True)
                    item_ing.setFont(font_bold)
                self.table.setItem(i, 1, item_ing)
                
                # Gastos
                item_gas = QTableWidgetItem(f"RD$ {row['Gastos']:,.2f}")
                item_gas.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                item_gas.setForeground(QColor(COLORS['red_700']))
                if is_total:
                    font_bold = QFont()
                    font_bold.setBold(True)
                    item_gas.setFont(font_bold)
                self.table.setItem(i, 2, item_gas)
                
                # Balance
                bal = row['Balance']
                item_bal = QTableWidgetItem(f"RD$ {bal:,.2f}")
                item_bal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                color = QColor(COLORS['green_700']) if bal >= 0 else QColor(COLORS['red_700'])
                item_bal.setForeground(color)
                if is_total:
                    font_bold = QFont()
                    font_bold.setBold(True)
                    item_bal.setFont(font_bold)
                    item_bal.setForeground(QColor(COLORS['blue_700']))
                self.table.setItem(i, 3, item_bal)
            
            # Update totals
            self.totals_label.setText(
                f"<b>Totales:</b> "
                f"Ingresos: <font color='{COLORS['green_700']}'>RD$ {total_ingresos_general:,.2f}</font> | "
                f"Gastos: <font color='{COLORS['red_700']}'>RD$ {total_gastos_general:,.2f}</font> | "
                f"Balance: <font color='{COLORS['blue_700']}'>RD$ {balance_total:,.2f}</font>"
            )
            
            logger.info(f"✅ Loaded account summary report with {len(resumen)} accounts")
            
        except Exception as e:
            logger.error(f"Error loading account summary report: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar el reporte:\n{str(e)}")


    # ==================== GLOBAL ACCOUNTS REPORT ====================
    
    def _load_global_accounts_report(self):
        """
        Load GLOBAL accounts report.
        Shows summary per account (ALL accounts from ALL projects).
        Columns: Cuenta | Ingresos | Gastos | Balance
        """
        try:
            qdesde = self.fecha_inicio_edit.date()
            qhasta = self.fecha_fin_edit.date()
            
            desde_date = qdesde.toPyDate()
            hasta_date = qhasta.toPyDate()
            
            if hasta_date < desde_date:
                self.totals_label.setText("<font color='red'>Fecha 'Hasta' menor que 'Desde'</font>")
                self.table.setRowCount(0)
                return
            
            # Get ALL accounts from system (global)
            try:
                if hasattr(self.firebase_client, 'get_cuentas_maestras'):
                    todas_cuentas = self.firebase_client.get_cuentas_maestras()
                else:
                    todas_cuentas = []
                
                logger.info(f"🌐 Cuentas globales obtenidas: {len(todas_cuentas)}")
            except Exception as e:
                logger.error(f"Error obteniendo cuentas globales: {e}")
                todas_cuentas = []
            
            # Get ALL global transactions
            try:
                if hasattr(self.firebase_client, 'get_transacciones_globales'):
                    todas_transacciones = self.firebase_client.get_transacciones_globales(limit=50000)
                else:
                    todas_transacciones = []
                
                logger.info(f"🌐 Transacciones globales obtenidas: {len(todas_transacciones)}")
            except Exception as e:
                logger.error(f"Error obteniendo transacciones globales: {e}")
                todas_transacciones = []
            
            # Create accounts map (ID → Name)
            cuentas_map_global = {}
            for c in todas_cuentas:
                doc_id = str(c.get('id', ''))
                nombre = c.get('nombre', 'Sin nombre')
                cuentas_map_global[doc_id] = nombre
                
                # Also map numeric cuenta_id if exists
                if 'cuenta_id' in c:
                    cuenta_id_num = str(c['cuenta_id'])
                    cuentas_map_global[cuenta_id_num] = nombre
            
            logger.info(f"🗺️ Mapa de cuentas creado: {len(cuentas_map_global)} IDs")
            
            # Aggregate by account
            resumen_cuentas: Dict[str, Dict[str, float]] = {}
            total_ingresos_global = 0.0
            total_gastos_global = 0.0
            
            for t in todas_transacciones:
                # Filter by date
                fecha_date = self._parse_date(t.get("fecha"))
                if not fecha_date:
                    continue
                
                if not (desde_date <= fecha_date <= hasta_date):
                    continue
                
                # Get account
                cuenta_id = str(t.get("cuenta_id", ""))
                if not cuenta_id:
                    continue
                
                # Get account name
                cuenta_nombre = cuentas_map_global.get(cuenta_id, f"Cuenta {cuenta_id}")
                
                # Get type and amount
                tipo = str(t.get("tipo", "")).lower()
                es_transferencia = t.get("es_transferencia") == True
                
                try:
                    monto = float(t.get("monto", 0.0))
                except:
                    monto = 0.0
                
                # Initialize account if not exists
                if cuenta_nombre not in resumen_cuentas:
                    resumen_cuentas[cuenta_nombre] = {"Ingresos": 0.0, "Gastos": 0.0}
                
                # Add to account (includes transfers for individual balance)
                if "ingreso" in tipo:
                    resumen_cuentas[cuenta_nombre]["Ingresos"] += monto
                    # Only count in total if NOT a transfer
                    if not es_transferencia:
                        total_ingresos_global += monto
                elif "gasto" in tipo:
                    resumen_cuentas[cuenta_nombre]["Gastos"] += monto
                    # Only count in total if NOT a transfer
                    if not es_transferencia:
                        total_gastos_global += monto
            
            logger.info(f"📊 Resumen calculado para {len(resumen_cuentas)} cuentas")
            
            # Build rows for table
            rows: List[Dict[str, Any]] = []
            for cuenta_nombre in sorted(resumen_cuentas.keys()):
                ing = resumen_cuentas[cuenta_nombre]["Ingresos"]
                gas = resumen_cuentas[cuenta_nombre]["Gastos"]
                bal = ing - gas
                rows.append({
                    "Cuenta": cuenta_nombre,
                    "Ingresos": ing,
                    "Gastos": gas,
                    "Balance": bal,
                })
            
            # Add total row
            balance_total = total_ingresos_global - total_gastos_global
            rows.append({
                "Cuenta": "TOTAL GENERAL",
                "Ingresos": total_ingresos_global,
                "Gastos": total_gastos_global,
                "Balance": balance_total,
                "_is_total": True
            })
            
            self.transacciones_filtradas = rows
            
            # Update table structure
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Cuenta", "Ingresos", "Gastos", "Balance"])
            
            # Adjust resize modes
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
            self.table.setColumnWidth(1, 150)
            self.table.setColumnWidth(2, 150)
            self.table.setColumnWidth(3, 150)
            
            # Populate table
            self.table.setRowCount(len(rows))
            
            for i, row in enumerate(rows):
                is_total = row.get("_is_total", False)
                
                # Cuenta
                item_cuenta = QTableWidgetItem(str(row["Cuenta"]))
                item_cuenta.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if is_total:
                    font_bold = QFont()
                    font_bold.setBold(True)
                    item_cuenta.setFont(font_bold)
                    item_cuenta.setForeground(QColor(COLORS['blue_700']))
                self.table.setItem(i, 0, item_cuenta)
                
                # Ingresos
                item_ing = QTableWidgetItem(f"RD$ {row['Ingresos']:,.2f}")
                item_ing.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                item_ing.setForeground(QColor(COLORS['green_700']))
                if is_total:
                    font_bold = QFont()
                    font_bold.setBold(True)
                    item_ing.setFont(font_bold)
                self.table.setItem(i, 1, item_ing)
                
                # Gastos
                item_gas = QTableWidgetItem(f"RD$ {row['Gastos']:,.2f}")
                item_gas.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                item_gas.setForeground(QColor(COLORS['red_700']))
                if is_total:
                    font_bold = QFont()
                    font_bold.setBold(True)
                    item_gas.setFont(font_bold)
                self.table.setItem(i, 2, item_gas)
                
                # Balance
                bal = row['Balance']
                item_bal = QTableWidgetItem(f"RD$ {bal:,.2f}")
                item_bal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                color = QColor(COLORS['green_700']) if bal >= 0 else QColor(COLORS['red_700'])
                item_bal.setForeground(color)
                if is_total:
                    font_bold = QFont()
                    font_bold.setBold(True)
                    item_bal.setFont(font_bold)
                    item_bal.setForeground(QColor(COLORS['blue_700']))
                self.table.setItem(i, 3, item_bal)
            
            # Update totals
            self.totals_label.setText(
                f"<b>Cuentas:</b> {len(resumen_cuentas)} | "
                f"<b>Ingresos:</b> <font color='{COLORS['green_700']}'>RD$ {total_ingresos_global:,.2f}</font> | "
                f"<b>Gastos:</b> <font color='{COLORS['red_700']}'>RD$ {total_gastos_global:,.2f}</font> | "
                f"<b>Balance:</b> <font color='{COLORS['blue_700']}'>RD$ {balance_total:,.2f}</font>"
            )
            
            logger.info(f"✅ Loaded global accounts report: {len(resumen_cuentas)} cuentas")
            
        except Exception as e:
            logger.error(f"Error loading global accounts report: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar el reporte:\n{str(e)}")
    
    # ==================== ACTIONS ====================
    
    def _on_date_changed(self):
        """Handle date change (auto-refresh)"""
        if self.current_report:
            logger.info("📅 Date changed, refreshing report...")
            self._select_report(self.current_report)
    
    def _reload_from_firebase(self):
        """Force reload from Firebase"""
        logger.info("🔄 Forcing reload from Firebase...")
        self._all_transacciones = None
        self._load_maps()
        if self.current_report:
            self._select_report(self.current_report)
    
    def on_project_change(self, proyecto_id: str, proyecto_nombre: str):
        """Handle project change"""
        logger.info(f"🔄 ReportsPage: Project changed to {proyecto_id} ({proyecto_nombre})")
        
        self.proyecto_id = proyecto_id
        self.proyecto_nombre = proyecto_nombre
        
        # Clear cache
        self._all_transacciones = None
        self.transacciones_filtradas = []
        
        # Reload data
        self._load_maps()
        self._set_smart_date_range()
        
        if self.current_report:
            self._select_report(self.current_report)
        
        logger.info(f"✅ ReportsPage updated for project {proyecto_nombre}")
    
    # ==================== EXPORT ====================
    
    def _exportar_pdf(self):
        """Export to PDF (adapts to current report type)"""
        if not self.transacciones_filtradas:
            QMessageBox.information(self, "Sin datos", "No hay datos para exportar.")
            return
        
        if self.current_report == 'category':
            self._exportar_pdf_categoria()
        elif self.current_report == 'cashflow':
            self._exportar_pdf_account_summary()
        elif self.current_report == 'summary':
            self._exportar_pdf_global_accounts()
        else:
            self._exportar_pdf_detailed()
    
    def _exportar_pdf_detailed(self):
        """Export detailed report to PDF"""
        fecha_ini = self.fecha_inicio_edit.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin_edit.date().toString("yyyy-MM-dd")
        nombre_defecto = f"Reporte_Detallado_{fecha_ini}_{fecha_fin}.pdf"
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", nombre_defecto, "PDF Files (*.pdf)")
        if not filepath:
            return
        
        try:
            data_export = []
            for t in self.transacciones_filtradas:
                row = t.copy()
                if "_raw_tipo" in row:
                    del row["_raw_tipo"]
                data_export.append(row)
            
            rango = f"{self.fecha_inicio_edit.text()} - {self.fecha_fin_edit.text()}"
            
            col_map = {
                "Fecha": "Fecha",
                "Tipo": "Tipo",
                "Cuenta": "Cuenta",
                "Categoría": "Categoría",
                "Descripción": "Descripción",
                "Monto": "Monto",
                "Adjuntos": "Adjuntos",
                "_transaction_id": "_transaction_id",
                "_adjuntos_paths": "_adjuntos_paths"
            }
            
            rg = ReportGenerator(
                data=data_export,
                title="Reporte Detallado de Transacciones",
                project_name=self.proyecto_nombre,
                date_range=rango,
                currency_symbol="RD$",
                column_map=col_map,
                firebase_client=self.firebase_client,
                proyecto_id=self.proyecto_id
            )
            
            success, msg = rg.to_pdf(filepath)
            
            if success:
                QMessageBox.information(self, "Éxito", f"PDF exportado correctamente:\n{filepath}")
                logger.info(f"✅ PDF exported: {filepath}")
            else:
                QMessageBox.warning(self, "Error PDF", f"No se pudo generar el PDF:\n{msg}")
        
        except Exception as e:
            logger.error(f"Error exporting PDF: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado al exportar:\n{e}")
    
    def _exportar_pdf_categoria(self):
        """Export category report to PDF with attachments"""
        ruta_archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar PDF",
            f"{self.proyecto_nombre}_gastos_categoria.pdf",
            "Archivos PDF (*.pdf)",
        )
        if not ruta_archivo:
            return
        
        try:
            # Get transactions with attachments
            transacciones_con_adjuntos = self._get_transacciones_con_adjuntos()
            
            # Calculate total steps
            num_anexos = len(transacciones_con_adjuntos)
            total_steps = 3 + num_anexos + 1
            
            # Import progress dialog
            try:
                from progain4.ui.widgets.progress_dialog import ProgressDialog
                progress_dialog = ProgressDialog(self, total_steps=total_steps)
                progress_dialog.show()
                
                def update_progress(step, status, detail=""):
                    progress_dialog.update_progress(step, status, detail)
            except ImportError:
                logger.warning("ProgressDialog not available, using None")
                progress_dialog = None
                update_progress = None
            
            date_range = (
                f"{self.fecha_inicio_edit.date().toString('dd/MM/yyyy')} - "
                f"{self.fecha_fin_edit.date().toString('dd/MM/yyyy')}"
            )
            
            # Prepare data (remove internal flags)
            data_export = []
            for item in self.transacciones_filtradas:
                row = {
                    "Categoría": item["Categoría"],
                    "Subcategoría": item["Subcategoría"],
                    "Monto": item["Monto"]
                }
                data_export.append(row)
            
            rg = ReportGenerator(
                data=data_export,
                title="Gastos por Categoría",
                project_name=self.proyecto_nombre,
                date_range=date_range,
                currency_symbol="RD$",
                column_map={
                    "Categoría": "Categoría",
                    "Subcategoría": "Subcategoría",
                    "Monto": "Monto",
                },
                firebase_client=self.firebase_client,
                proyecto_id=self.proyecto_id,
            )
            
            ok, msg = rg.to_pdf_gastos_por_categoria(
                ruta_archivo,
                transacciones_anexos=transacciones_con_adjuntos,
                progress_callback=update_progress
            )
            
            if progress_dialog:
                progress_dialog.finish()
            
            if ok:
                mensaje = "Datos exportados a PDF correctamente."
                if transacciones_con_adjuntos:
                    mensaje += f"\n\n✅ Se incluyeron {len(transacciones_con_adjuntos)} anexos con adjuntos."
                QMessageBox.information(self, "Exportación", mensaje)
            else:
                QMessageBox.warning(self, "Error PDF", f"No se pudo exportar PDF: {msg}")
        
        except Exception as e:
            logger.error(f"Error exportando PDF: {e}", exc_info=True)
            QMessageBox.warning(self, "Error PDF", f"No se pudo exportar PDF: {e}")
    
    def _get_transacciones_con_adjuntos(self) -> List[Dict[str, Any]]:
        """Get all transactions with attachments in date range"""
        try:
            qdesde = self.fecha_inicio_edit.date()
            qhasta = self.fecha_fin_edit.date()
            desde_date = qdesde.toPyDate()
            hasta_date = qhasta.toPyDate()
            
            # Get catalogs
            categorias = self.firebase_client.get_categorias_by_proyecto(self.proyecto_id)
            subcategorias = self.firebase_client.get_subcategorias_by_proyecto(self.proyecto_id)
            
            cat_by_id = {str(c["id"]): c.get("nombre", "Sin categoría") for c in categorias}
            subcat_by_id = {str(s["id"]): s.get("nombre", "Sin subcategoría") for s in subcategorias}
            
            if self._all_transacciones is None:
                self._all_transacciones = self.firebase_client.get_transacciones_by_proyecto(
                    self.proyecto_id
                )
            transacciones = self._all_transacciones or []
            
            resultado = []
            numero = 1
            
            for t in transacciones:
                tipo = str(t.get("tipo", "")).lower()
                if tipo != "gasto":
                    continue
                
                fecha_date = self._parse_date(t.get("fecha"))
                if not fecha_date or not (desde_date <= fecha_date <= hasta_date):
                    continue
                
                adjuntos_urls = t.get("adjuntos", [])
                if not isinstance(adjuntos_urls, list) or len(adjuntos_urls) == 0:
                    continue
                
                adjuntos_urls = [url for url in adjuntos_urls if url and str(url).strip()]
                if not adjuntos_urls:
                    continue
                
                categoria_id = str(t.get("categoria_id", ""))
                subcategoria_id = str(t.get("subcategoria_id", "")) if t.get("subcategoria_id") else None
                
                categoria_nombre = cat_by_id.get(categoria_id, "Sin categoría")
                subcategoria_nombre = subcat_by_id.get(subcategoria_id, "Sin subcategoría") if subcategoria_id else "Sin subcategoría"
                
                resultado.append({
                    "numero": numero,
                    "id": str(t.get("id", "")),
                    "fecha": fecha_date.strftime("%Y-%m-%d"),
                    "descripcion": str(t.get("descripcion", "Sin descripción"))[:100],
                    "categoria": categoria_nombre,
                    "subcategoria": subcategoria_nombre,
                    "monto": float(t.get("monto", 0.0)),
                    "adjunto_url": adjuntos_urls[0],
                    "adjuntos_urls": adjuntos_urls,
                })
                
                numero += 1
            
            logger.info(f"✅ Found {len(resultado)} transactions with attachments")
            return resultado
            
        except Exception as e:
            logger.error(f"Error getting transactions with attachments: {e}")
            return []
    
    def _exportar_pdf_account_summary(self):
        """Export account summary report to PDF"""
        if not self.transacciones_filtradas:
            QMessageBox.information(self, "Sin datos", "No hay datos para exportar.")
            return
        
        fecha_ini = self.fecha_inicio_edit.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin_edit.date().toString("yyyy-MM-dd")
        nombre_archivo = f"{self.proyecto_nombre}_Resumen_Cuenta_{fecha_ini}_{fecha_fin}.pdf"
        
        ruta_archivo, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", nombre_archivo, "Archivos PDF (*.pdf)"
        )
        if not ruta_archivo:
            return
        
        try:
            # Remove internal flags
            data_export = []
            for item in self.transacciones_filtradas:
                row = {
                    "Cuenta": item["Cuenta"],
                    "Ingresos": item["Ingresos"],
                    "Gastos": item["Gastos"],
                    "Balance": item["Balance"]
                }
                data_export.append(row)
            
            rg = ReportGenerator(
                data=data_export,
                title="Resumen por Cuenta",
                project_name=self.proyecto_nombre,
                date_range=f"{fecha_ini} - {fecha_fin}",
                currency_symbol="RD$",
                column_map={
                    "Cuenta": "Cuenta",
                    "Ingresos": "Ingresos",
                    "Gastos": "Gastos",
                    "Balance": "Balance",
                },
            )
            
            ok, msg = rg.to_pdf_resumen_por_cuenta(ruta_archivo)
            if ok:
                QMessageBox.information(self, "Exportación", "Resumen exportado a PDF correctamente.")
                logger.info(f"✅ PDF exported: {ruta_archivo}")
            else:
                QMessageBox.warning(self, "Error PDF", f"No se pudo exportar PDF: {msg}")
        
        except Exception as e:
            logger.error(f"Error PDF export: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado: {e}")
    
    def _exportar_pdf_global_accounts(self):
        """Export global accounts report to PDF"""
        if not self.transacciones_filtradas:
            QMessageBox.information(self, "Sin datos", "No hay datos para exportar.")
            return
        
        fecha_ini = self.fecha_inicio_edit.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin_edit.date().toString("yyyy-MM-dd")
        nombre_archivo = f"Reporte_Global_Cuentas_{fecha_ini}_{fecha_fin}.pdf"
        
        ruta_archivo, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", nombre_archivo, "Archivos PDF (*.pdf)"
        )
        if not ruta_archivo:
            return
        
        try:
            # Remove internal flags
            data_export = []
            for item in self.transacciones_filtradas:
                row = {
                    "Cuenta": item["Cuenta"],
                    "Ingresos": item["Ingresos"],
                    "Gastos": item["Gastos"],
                    "Balance": item["Balance"]
                }
                data_export.append(row)
            
            rg = ReportGenerator(
                data=data_export,
                title="Reporte Global de Cuentas",
                project_name="Todas las Cuentas",
                date_range=f"{fecha_ini} - {fecha_fin}",
                currency_symbol="RD$",
                column_map={
                    "Cuenta": "Cuenta",
                    "Ingresos": "Ingresos",
                    "Gastos": "Gastos",
                    "Balance": "Balance",
                },
            )
            
            ok, msg = rg.to_pdf_resumen_por_cuenta(ruta_archivo)
            if ok:
                QMessageBox.information(self, "Exportación", "Reporte global exportado a PDF correctamente.")
                logger.info(f"✅ PDF exported: {ruta_archivo}")
            else:
                QMessageBox.warning(self, "Error PDF", f"No se pudo exportar PDF: {msg}")
        
        except Exception as e:
            logger.error(f"Error PDF export: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado: {e}")
    
    def _exportar_excel(self):
        """Export to Excel (adapts to current report type)"""
        if not self.transacciones_filtradas:
            QMessageBox.information(self, "Sin datos", "No hay datos para exportar.")
            return
        
        if self.current_report == 'category':
            self._exportar_excel_categoria()
        elif self.current_report == 'cashflow':
            self._exportar_excel_account_summary()
        elif self.current_report == 'summary':
            self._exportar_excel_global_accounts()
        else:
            self._exportar_excel_detailed()
    
    def _exportar_excel_detailed(self):
        """Export detailed report to Excel"""
        fecha_ini = self.fecha_inicio_edit.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin_edit.date().toString("yyyy-MM-dd")
        nombre_defecto = f"Reporte_Detallado_{fecha_ini}_{fecha_fin}.xlsx"
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar Excel", nombre_defecto, "Excel Files (*.xlsx)")
        if not filepath:
            return
        
        try:
            data_export = []
            for t in self.transacciones_filtradas:
                row = t.copy()
                if "_raw_tipo" in row:
                    del row["_raw_tipo"]
                if "_transaction_id" in row:
                    del row["_transaction_id"]
                if "_adjuntos_paths" in row:
                    del row["_adjuntos_paths"]
                data_export.append(row)
            
            rango = f"{self.fecha_inicio_edit.text()} - {self.fecha_fin_edit.text()}"
            
            rg = ReportGenerator(
                data=data_export,
                title="Reporte Detallado de Transacciones",
                project_name=self.proyecto_nombre,
                date_range=rango,
                currency_symbol="RD$"
            )
            
            success, msg = rg.to_excel(filepath)
            
            if success:
                QMessageBox.information(self, "Éxito", "Excel exportado correctamente.")
                logger.info(f"✅ Excel exported: {filepath}")
            else:
                QMessageBox.warning(self, "Error Excel", f"No se pudo generar el Excel:\n{msg}")
        
        except Exception as e:
            logger.error(f"Error exporting Excel: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado al exportar:\n{e}")
    
    def _exportar_excel_categoria(self):
        """Export category report to Excel"""
        ruta_archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Excel",
            f"{self.proyecto_nombre}_gastos_categoria.xlsx",
            "Archivos Excel (*.xlsx)",
        )
        if not ruta_archivo:
            return
        
        try:
            date_range = (
                f"{self.fecha_inicio_edit.date().toString('dd/MM/yyyy')} - "
                f"{self.fecha_fin_edit.date().toString('dd/MM/yyyy')}"
            )
            
            # Prepare data (remove internal flags)
            data_export = []
            for item in self.transacciones_filtradas:
                row = {
                    "Categoría": item["Categoría"],
                    "Subcategoría": item["Subcategoría"],
                    "Monto": item["Monto"]
                }
                data_export.append(row)
            
            rg = ReportGenerator(
                data=data_export,
                title="Gastos por Categoría",
                project_name=self.proyecto_nombre,
                date_range=date_range,
                currency_symbol="RD$",
                column_map={
                    "Categoría": "Categoría",
                    "Subcategoría": "Subcategoría",
                    "Monto": "Monto",
                },
            )
            
            ok, msg = rg.to_excel_categoria(ruta_archivo)
            
            if ok:
                QMessageBox.information(self, "Exportación", "Datos exportados a Excel correctamente.")
            else:
                QMessageBox.warning(self, "Error Excel", f"No se pudo exportar Excel: {msg}")
        
        except Exception as e:
            logger.error(f"Error exporting Excel: {e}", exc_info=True)
            QMessageBox.warning(self, "Error Excel", f"No se pudo exportar Excel: {e}")
    
    def _exportar_excel_account_summary(self):
        """Export account summary report to Excel"""
        if not self.transacciones_filtradas:
            QMessageBox.information(self, "Sin datos", "No hay datos para exportar.")
            return
        
        fecha_ini = self.fecha_inicio_edit.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin_edit.date().toString("yyyy-MM-dd")
        nombre_archivo = f"{self.proyecto_nombre}_Resumen_Cuenta_{fecha_ini}_{fecha_fin}.xlsx"
        
        ruta_archivo, _ = QFileDialog.getSaveFileName(
            self, "Guardar Excel", nombre_archivo, "Archivos Excel (*.xlsx)"
        )
        if not ruta_archivo:
            return
        
        try:
            # Remove internal flags
            data_export = []
            for item in self.transacciones_filtradas:
                row = {
                    "Cuenta": item["Cuenta"],
                    "Ingresos": item["Ingresos"],
                    "Gastos": item["Gastos"],
                    "Balance": item["Balance"]
                }
                data_export.append(row)
            
            rg = ReportGenerator(
                data=data_export,
                title="Resumen por Cuenta",
                project_name=self.proyecto_nombre,
                date_range=f"{fecha_ini} - {fecha_fin}",
                currency_symbol="RD$",
                column_map={
                    "Cuenta": "Cuenta",
                    "Ingresos": "Ingresos",
                    "Gastos": "Gastos",
                    "Balance": "Balance",
                },
            )
            
            ok, msg = rg.to_excel_resumen_por_cuenta(ruta_archivo)
            if ok:
                QMessageBox.information(self, "Exportación", "Resumen exportado a Excel correctamente.")
                logger.info(f"✅ Excel exported: {ruta_archivo}")
            else:
                QMessageBox.warning(self, "Error Excel", f"No se pudo exportar Excel: {msg}")
        
        except Exception as e:
            logger.error(f"Error Excel export: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado: {e}")
    
    def _exportar_excel_global_accounts(self):
        """Export global accounts report to Excel"""
        if not self.transacciones_filtradas:
            QMessageBox.information(self, "Sin datos", "No hay datos para exportar.")
            return
        
        fecha_ini = self.fecha_inicio_edit.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin_edit.date().toString("yyyy-MM-dd")
        nombre_archivo = f"Reporte_Global_Cuentas_{fecha_ini}_{fecha_fin}.xlsx"
        
        ruta_archivo, _ = QFileDialog.getSaveFileName(
            self, "Guardar Excel", nombre_archivo, "Archivos Excel (*.xlsx)"
        )
        if not ruta_archivo:
            return
        
        try:
            # Remove internal flags
            data_export = []
            for item in self.transacciones_filtradas:
                row = {
                    "Cuenta": item["Cuenta"],
                    "Ingresos": item["Ingresos"],
                    "Gastos": item["Gastos"],
                    "Balance": item["Balance"]
                }
                data_export.append(row)
            
            rg = ReportGenerator(
                data=data_export,
                title="Reporte Global de Cuentas",
                project_name="Todas las Cuentas",
                date_range=f"{fecha_ini} - {fecha_fin}",
                currency_symbol="RD$",
                column_map={
                    "Cuenta": "Cuenta",
                    "Ingresos": "Ingresos",
                    "Gastos": "Gastos",
                    "Balance": "Balance",
                },
            )
            
            ok, msg = rg.to_excel_resumen_por_cuenta(ruta_archivo)
            if ok:
                QMessageBox.information(self, "Exportación", "Reporte global exportado a Excel correctamente.")
                logger.info(f"✅ Excel exported: {ruta_archivo}")
            else:
                QMessageBox.warning(self, "Error Excel", f"No se pudo exportar Excel: {msg}")
        
        except Exception as e:
            logger.error(f"Error Excel export: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado: {e}")