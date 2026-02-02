"""
MainWindow - Ventana principal moderna completa

Ensambla todos los componentes:  
- Sidebar (izquierda)
- Header (arriba)
- Contenido (páginas con QStackedWidget)
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QStackedWidget, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

# Imports absolutos (funcionan siempre)
from ui.modern.widgets.sidebar import Sidebar
from ui.modern.widgets.header import Header
from ui.modern. components.clean_card import CleanCard
from ui.modern.theme_config import COLORS


class MainWindow(QMainWindow):
    """
    Ventana principal moderna - Construction Manager Pro
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Estado
        self.current_page = 'dashboard'
        self.current_company = 'all'
        
        self.setup_window()
        self.setup_ui()
        self.setup_connections()
        
        print("✅ MainWindow inicializada correctamente")
    
    def setup_window(self):
        """Configurar ventana principal"""
        self.setWindowTitle("PROGAIN 5.2 - Construction Manager Pro")
        self.setMinimumSize(1280, 720)
        self.resize(1440, 900)
        
        # Fondo general
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['slate_50']};
            }}
        """)
    
    def setup_ui(self):
        """Crear la UI completa"""
        
        # Widget central
        central = QWidget()
        central.setStyleSheet(f"background-color: {COLORS['slate_50']};")
        self.setCentralWidget(central)
        
        # Layout horizontal principal
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # === SIDEBAR (Izquierda) ===
        self.sidebar = Sidebar()
        
        # FORZAR FONDO OSCURO DEL SIDEBAR
        sidebar_palette = self.sidebar.palette()
        sidebar_palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['slate_900']))
        self.sidebar.setPalette(sidebar_palette)
        self.sidebar.setAutoFillBackground(True)
        
        # Asegurar que el estilo se aplique
        self.sidebar. setStyleSheet(f"""
            Sidebar {{
                background-color:  {COLORS['slate_900']} !important;
                border-right: 1px solid {COLORS['slate_800']};
            }}
        """)
        
        main_layout.addWidget(self. sidebar)
        
        # === CONTENIDO DERECHO ===
        content_widget = QWidget()
        content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['slate_50']};
            }}
        """)
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- HEADER (Arriba) ---
        self.header = Header()
        content_layout.addWidget(self. header)
        
        # --- PÁGINAS (Abajo) ---
        self.pages_stack = QStackedWidget()
        self.pages_stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {COLORS['slate_50']};
            }}
        """)
        
        # Crear las páginas
        self.create_pages()
        
        content_layout.addWidget(self. pages_stack)
        
        # Agregar contenido al layout principal
        main_layout.addWidget(content_widget)
    
    def create_pages(self):
        """Crear las 5 páginas del stack"""
        
        # === PÁGINA 0: DASHBOARD ===
        self.page_dashboard = self.create_placeholder_page(
            "📊 Dashboard",
            "Panel de Control Principal",
            "Aquí se mostrarán las métricas clave, cuentas bancarias y resumen de proyectos"
        )
        self.pages_stack.addWidget(self.page_dashboard)
        
        # === PÁGINA 1: OBRAS ===
        self.page_projects = self.create_placeholder_page(
            "🏗️ Catálogo de Obras",
            "Gestión de Proyectos",
            "Listado de proyectos en ejecución con avances y presupuestos"
        )
        self.pages_stack. addWidget(self.page_projects)
        
        # === PÁGINA 2: TRANSACCIONES ===
        self.page_transactions = self.create_placeholder_page(
            "🔄 Transacciones",
            "Movimientos de Obra",
            "Registro de transacciones y movimientos por proyecto"
        )
        self.pages_stack.addWidget(self.page_transactions)
        
        # === PÁGINA 3: CAJA ===
        self.page_cash = self.create_placeholder_page(
            "💰 Flujo de Caja",
            "Gestión Financiera",
            "Movimientos de efectivo, bancos y cuentas por cobrar/pagar"
        )
        self.pages_stack.addWidget(self.page_cash)
        
        # === PÁGINA 4: REPORTES ===
        self.page_reports = self.create_placeholder_page(
            "📊 Reportes e Inteligencia",
            "Análisis y Reportes",
            "Dashboards, gráficos y reportes avanzados"
        )
        self.pages_stack.addWidget(self.page_reports)
        
        # Página inicial
        self.pages_stack.setCurrentIndex(0)
        
        print(f"✅ {self.pages_stack.count()} páginas creadas")
    
    def create_placeholder_page(self, icon_title: str, title: str, description: str) -> QWidget:
        """Crear una página placeholder moderna"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['slate_50']};")
        
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag. AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Tarjeta central
        card = CleanCard(padding=40)
        card.setMaximumWidth(600)
        
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(20)
        
        # Icono grande
        icon_label = QLabel(icon_title. split()[0])  # Solo el emoji
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size:  64px;
                background-color: transparent;
            }}
        """)
        icon_label.setAlignment(Qt. AlignmentFlag.AlignCenter)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_900']};
                background-color: transparent;
            }}
        """)
        title_label.setAlignment(Qt. AlignmentFlag.AlignCenter)
        
        # Descripción
        desc_label = QLabel(description)
        desc_font = QFont()
        desc_font.setPointSize(14)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_500']};
                background-color:  transparent;
                line-height: 1.6;
            }}
        """)
        desc_label.setAlignment(Qt.AlignmentFlag. AlignCenter)
        desc_label.setWordWrap(True)
        
        # Badge de estado
        status_label = QLabel("🚧 Próximamente")
        status_label. setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['blue_100']};
                color: {COLORS['blue_700']};
                padding: 8px 16px;
                border-radius:  6px;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        status_label.setAlignment(Qt. AlignmentFlag.AlignCenter)
        
        card_layout.addWidget(icon_label)
        card_layout. addWidget(title_label)
        card_layout.addWidget(desc_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(status_label, alignment=Qt.AlignmentFlag. AlignCenter)
        
        layout.addWidget(card)
        
        return page
    
    def setup_connections(self):
        """Conectar señales y slots"""
        
        # Sidebar → Navegación
        self.sidebar.navigation_changed.connect(self.on_navigation_changed)
        
        # Header → Cambio de empresa
        self.header. company_changed.connect(self. on_company_changed)
        
        # Header → Botón Registrar
        self.header. register_clicked.connect(self.on_register_clicked)
        
        print("✅ Señales conectadas")
    
    # ========== SLOTS (Callbacks) ==========
    
    def on_navigation_changed(self, page_id: str):
        """Callback cuando cambia la navegación desde el sidebar"""
        print(f"📍 Navegación:  {page_id}")
        
        # Mapeo de IDs a índices y títulos
        pages_map = {
            'dashboard': (0, 'Control de Obra'),
            'projects':  (1, 'Catálogo de Obras'),
            'transactions': (2, 'Transacciones'),
            'cash': (3, 'Flujo de Caja'),
            'reports': (4, 'Reportes e Inteligencia'),
        }
        
        if page_id in pages_map: 
            page_index, page_title = pages_map[page_id]
            
            # Cambiar página
            self.pages_stack.setCurrentIndex(page_index)
            
            # Actualizar título del header
            self.header.set_title(page_title)
            
            # Actualizar estado
            self.current_page = page_id
            
            print(f"✅ Página cambiada:  {page_title} (índice {page_index})")
    
    def on_company_changed(self, company_id: str):
        """Callback cuando cambia la empresa seleccionada"""
        print(f"🏢 Empresa:  {company_id}")
        
        self.current_company = company_id
        
        # TODO: Aquí irá la lógica de filtrado de datos por empresa
    
    def on_register_clicked(self):
        """Callback cuando se hace click en Registrar"""
        print("➕ Abriendo diálogo de registro...")
        
        # TODO: Aquí se abrirá el diálogo de nueva transacción
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Nueva Transacción",
            "Diálogo de registro por implementar.\n\n"
            f"Contexto:\n"
            f"• Página: {self.current_page}\n"
            f"• Empresa: {self.current_company}"
        )
    
    # ========== MÉTODOS PÚBLICOS ==========
    
    def navigate_to(self, page_id: str):
        """Navegar a una página programáticamente"""
        self.sidebar.navigate_to(page_id)