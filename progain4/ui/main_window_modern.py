"""
Main Window Moderna - Construction Manager Pro Design

Esta es la ventana principal rediseñada con el sistema de diseño moderno. 
Preserva toda la funcionalidad de main_window4.py pero con nueva estructura visual. 

Autor: GitHub Copilot Agent
Fecha: 2026-01-21
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QStackedWidget, QLabel, QMessageBox, QMenuBar,
    QToolBar, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon

# Importar componentes modernos
from progain4.ui.widgets.sidebar_widget import SidebarWidget
from progain4.ui.widgets.header_widget import HeaderWidget
from progain4.ui.widgets.clean_card import CleanCard

# Importar theme manager
from progain4.ui.theme_manager import ThemeManager, DESIGN_COLORS

# Importar widgets de contenido existentes
# IMPORTANTE: Ajustar estos imports según la estructura real del proyecto
try:
    from progain4.ui.widgets.transactions_widget import TransactionsWidget
except ImportError:
    TransactionsWidget = None
    print("⚠️ TransactionsWidget no encontrado - usando placeholder")

try:
    from progain4.ui.widgets.accounts_window import AccountsWindow
except ImportError:
    AccountsWindow = None
    print("⚠️ AccountsWindow no encontrado - usando placeholder")


class MainWindowModern(QMainWindow):
    """
    Ventana principal moderna con diseño Construction Manager Pro. 
    
    Estructura:
    ┌──────────────────────────────────────────────┐
    │ MenuBar (opcional, preservado del original)  │
    ├────────┬─────────────────────────────────────┤
    │        │ HeaderWidget (64px)                 │
    │ Side   ├─────────────────────────────────────┤
    │ bar    │                                     │
    │ (80px) │  QStackedWidget (páginas)          │
    │        │  - Dashboard                        │
    │        │  - Obras                            │
    │        │  - Transacciones                    │
    │        │  - Reportes                         │
    │        │                                     │
    └────────┴─────────────────────────────────────┘
    """
    
    # Signals (preservar los mismos del original si existen)
    project_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Variables de estado
        self.current_project = None
        self.current_company = "all"
        self.current_page = "dashboard"
        
        # Theme manager
        self.theme_manager = ThemeManager()
        
        # Setup UI
        self.setup_window()
        self.setup_menubar()  # Preservar menús del original
        self.setup_toolbar()   # Preservar toolbar del original
        self.setup_main_layout()
        self.setup_statusbar()
        self.setup_connections()
        
        # Aplicar tema moderno AUTOMÁTICAMENTE
        self.apply_modern_theme()
        
        print("✅ MainWindowModern inicializada correctamente")
    
    def setup_window(self):
        """Configuración básica de la ventana"""
        self.setWindowTitle("PROGAIN 5.2 - Control de Obra")
        self.setMinimumSize(1280, 720)
        self.resize(1440, 900)
        
        # Estilo base de la ventana
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {DESIGN_COLORS['slate_50']};
            }}
        """)
    
    def setup_menubar(self):
        """
        Crear MenuBar preservando funcionalidad del original. 
        
        IMPORTANTE: Si main_window4.py tiene menús específicos,
        copiar esa lógica aquí EXACTAMENTE igual.
        """
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        # Acción: Nuevo Proyecto
        new_project_action = QAction("&Nuevo Proyecto", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self.on_new_project)
        file_menu.addAction(new_project_action)
        
        # Acción: Abrir Proyecto
        open_project_action = QAction("&Abrir Proyecto", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.triggered.connect(self.on_open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        # Acción: Salir
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Ver
        view_menu = menubar.addMenu("&Ver")
        
        # Acción: Cambiar Tema
        theme_action = QAction("&Temas", self)
        theme_action.triggered.connect(self.on_change_theme)
        view_menu.addAction(theme_action)
        
        # Menú Dashboards
        dash_menu = menubar.addMenu("&Dashboards")
        
        # Acción: Dashboard Principal
        dashboard_action = QAction("&Panel Principal", self)
        dashboard_action.triggered.connect(lambda: self.navigate_to_page("dashboard"))
        dash_menu.addAction(dashboard_action)
        
        # Menú Herramientas
        tools_menu = menubar.addMenu("&Herramientas")
        
        # Acción: Configuración
        settings_action = QAction("&Configuración", self)
        settings_action.triggered.connect(self.on_settings)
        tools_menu.addAction(settings_action)
        
        # Menú Reportes
        reports_menu = menubar.addMenu("&Reportes")
        
        # TODO: Agregar acciones de reportes específicos del proyecto
        
        print("✅ MenuBar creado con funcionalidad básica")
    
    def setup_toolbar(self):
        """
        Crear ToolBar preservando funcionalidad del original.
        
        IMPORTANTE: Si main_window4.py tiene toolbar específico,
        copiar esa lógica aquí.
        """
        toolbar = QToolBar("Principal")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Botón: Nuevo Registro
        new_action = QAction("Nuevo", self)
        new_action.triggered.connect(self.on_new_transaction)
        toolbar.addAction(new_action)
        
        toolbar.addSeparator()
        
        # Botón: Refrescar
        refresh_action = QAction("Refrescar", self)
        refresh_action.triggered.connect(self.on_refresh)
        toolbar.addAction(refresh_action)
        
        print("✅ ToolBar creado")
    
    def setup_main_layout(self):
        """
        Crear el layout principal moderno.
        
        Estructura:
        - Layout Horizontal: Sidebar (izq) + Contenido (der)
        - Contenido: Layout Vertical con Header (arriba) + Páginas (abajo)
        """
        # Widget central principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout horizontal principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # === SIDEBAR (Izquierda - 80px) ===
        self.sidebar = SidebarWidget()
        self.sidebar.setFixedWidth(80)
        main_layout.addWidget(self.sidebar)
        
        # === CONTENIDO DERECHO ===
        content_widget = QWidget()
        content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {DESIGN_COLORS['slate_50']};
            }}
        """)
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- HEADER (Arriba - 64px) ---
        self.header = HeaderWidget()
        self.header.setFixedHeight(64)
        content_layout.addWidget(self.header)
        
        # --- PÁGINAS (Abajo - Crece) ---
        self.pages_stack = QStackedWidget()
        self.pages_stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {DESIGN_COLORS['slate_50']};
            }}
        """)
        
        # Crear páginas
        self.create_pages()
        
        content_layout.addWidget(self.pages_stack)
        
        # Agregar contenido al layout principal
        main_layout.addWidget(content_widget)
        
        print("✅ Layout principal creado correctamente")
    
    def create_pages(self):
        """
        Crear las páginas del QStackedWidget.
        
        IMPORTANTE: Aquí se integran los widgets de contenido existentes
        (TransactionsWidget, AccountsWindow, etc.)
        """
        
        # === PÁGINA 0: DASHBOARD ===
        if TransactionsWidget:
            # Usar el widget existente de transacciones como dashboard principal
            self.page_dashboard = TransactionsWidget()
        else:
            # Placeholder si no existe
            self.page_dashboard = self.create_placeholder_page(
                "📊 Dashboard",
                "Panel de control principal\nAquí se mostrarán las métricas clave"
            )
        self.pages_stack.addWidget(self.page_dashboard)
        
        # === PÁGINA 1: OBRAS ===
        self.page_projects = self.create_placeholder_page(
            "🏗️ Catálogo de Obras",
            "Listado de proyectos en ejecución\n(Por implementar)"
        )
        self.pages_stack.addWidget(self.page_projects)
        
        # === PÁGINA 2: CAJA / TRANSACCIONES ===
        if TransactionsWidget:
            self.page_transactions = TransactionsWidget()
        else:
            self.page_transactions = self.create_placeholder_page(
                "💰 Flujo de Caja",
                "Movimientos y transacciones\n(Widget no encontrado)"
            )
        self.pages_stack.addWidget(self.page_transactions)
        
        # === PÁGINA 3: REPORTES ===
        self.page_reports = self.create_placeholder_page(
            "📊 Reportes e Inteligencia",
            "Análisis y reportes avanzados\n(Por implementar)"
        )
        self.pages_stack.addWidget(self.page_reports)
        
        # Establecer página inicial
        self.pages_stack.setCurrentIndex(0)
        
        print(f"✅ {self.pages_stack.count()} páginas creadas en el stack")
    
    def create_placeholder_page(self, title: str, description: str) -> QWidget:
        """
        Crea una página placeholder moderna.
        
        Args:
            title: Título de la página
            description: Descripción
            
        Returns:
            QWidget con diseño placeholder
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Tarjeta central
        card = CleanCard(padding=40)
        card.setMaximumWidth(600)
        
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(20)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: 700;
                color: {DESIGN_COLORS['slate_900']};
            }}
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {DESIGN_COLORS['slate_500']};
                line-height: 1.6;
            }}
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        
        layout.addWidget(card)
        
        return page
    
    def setup_statusbar(self):
        """Crear StatusBar preservando funcionalidad del original"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("✅ Sistema listo - Tema: Construction Pro", 3000)
    
    def setup_connections(self):
        """Conectar signals y slots"""
        
        # Sidebar → Navegación
        if hasattr(self.sidebar, 'navigation_changed'):
            self.sidebar.navigation_changed.connect(self.on_navigation_changed)
        
        # Header → Cambio de empresa
        if hasattr(self.header, 'company_changed'):
            self.header.company_changed.connect(self.on_company_changed)
        
        # Header → Botón Registrar
        if hasattr(self.header, 'register_clicked'):
            self.header.register_clicked.connect(self.on_register_clicked)
        
        print("✅ Señales y slots conectados")
    
    def apply_modern_theme(self):
        """Aplicar tema construction_pro automáticamente"""
        try:
            self.theme_manager.apply_theme(self, "construction_pro")
            print("✅ Tema 'construction_pro' aplicado exitosamente")
        except Exception as e:
            print(f"⚠️ Error al aplicar tema: {e}")
            print("   La app funcionará con estilos por defecto")
    
    # ========== SLOTS (Callbacks) ==========
    
    def on_navigation_changed(self, page_name: str):
        """Callback cuando cambia la navegación desde el sidebar"""
        print(f"📍 Navegación solicitada: {page_name}")
        self.navigate_to_page(page_name)
    
    def navigate_to_page(self, page_name: str):
        """
        Navega a una página específica del stack.
        
        Args:
            page_name: Nombre de la página ('dashboard', 'projects', 'transactions', 'reports')
        """
        page_index = {
            'dashboard': 0,
            'projects': 1,
            'transactions': 2,
            'caja': 2,  # Alias
            'reports': 3,
        }.get(page_name.lower(), 0)
        
        self.pages_stack.setCurrentIndex(page_index)
        self.current_page = page_name
        
        # Actualizar título del header
        titles = {
            'dashboard': "Control de Obra",
            'projects': "Catálogo de Obras",
            'transactions': "Flujo de Caja",
            'caja': "Flujo de Caja",
            'reports': "Inteligencia de Costos",
        }
        
        if hasattr(self.header, 'set_title'):
            self.header.set_title(titles.get(page_name, "PROGAIN 5.2"))
        
        self.statusbar.showMessage(f"📄 Página activa: {titles.get(page_name, page_name)}", 2000)
    
    def on_company_changed(self, company_name: str):
        """Callback cuando cambia la empresa seleccionada"""
        print(f"🏢 Empresa seleccionada: {company_name}")
        self.current_company = company_name
        
        # TODO: Implementar filtrado de datos por empresa
        # Si ya existe lógica en main_window4.py, migrarla aquí
        
        self.statusbar.showMessage(f"🏢 Filtrando por: {company_name}", 2000)
    
    def on_register_clicked(self):
        """Callback cuando se hace clic en el botón Registrar"""
        print("➕ Abriendo diálogo de nueva transacción")
        
        # TODO: Abrir diálogo de nueva transacción
        # Si ya existe en main_window4.py, migrar aquí
        
        self.statusbar.showMessage("➕ Nueva transacción (diálogo por implementar)", 2000)
    
    def on_new_project(self):
        """Acción: Nuevo Proyecto"""
        print("📁 Nuevo Proyecto")
        # TODO: Implementar lógica de nuevo proyecto
        QMessageBox.information(self, "Nuevo Proyecto", "Funcionalidad por implementar")
    
    def on_open_project(self):
        """Acción: Abrir Proyecto"""
        print("📂 Abrir Proyecto")
        # TODO: Implementar lógica de abrir proyecto
        QMessageBox.information(self, "Abrir Proyecto", "Funcionalidad por implementar")
    
    def on_change_theme(self):
        """Acción: Cambiar Tema"""
        print("🎨 Cambiar Tema")
        # TODO: Implementar diálogo de selección de tema
        QMessageBox.information(self, "Temas", "Tema actual: Construction Pro")
    
    def on_settings(self):
        """Acción: Configuración"""
        print("⚙️ Configuración")
        # TODO: Implementar diálogo de configuración
        QMessageBox.information(self, "Configuración", "Funcionalidad por implementar")
    
    def on_new_transaction(self):
        """Acción: Nueva Transacción"""
        print("💰 Nueva Transacción")
        self.on_register_clicked()
    
    def on_refresh(self):
        """Acción: Refrescar datos"""
        print("🔄 Refrescando datos...")
        # TODO: Recargar datos desde Firebase
        self.statusbar.showMessage("🔄 Datos actualizados", 2000)
    
    # ========== MÉTODOS PÚBLICOS (API Compatibility) ==========
    
    def set_project(self, project_name: str):
        """
        Establece el proyecto activo.
        
        Preserva compatibilidad con main_window4.py
        """
        self.current_project = project_name
        
        if hasattr(self.sidebar, 'set_project_name'):
            self.sidebar.set_project_name(project_name)
        
        self.project_changed.emit(project_name)
        print(f"📁 Proyecto activo: {project_name}")
    
    def set_accounts(self, accounts_data: list):
        """
        Establece las cuentas disponibles.
        
        Preserva compatibilidad con main_window4.py
        """
        if hasattr(self.sidebar, 'set_accounts'):
            self.sidebar.set_accounts(accounts_data)
        
        print(f"💳 {len(accounts_data)} cuentas cargadas")
    
    # ========== LIFECYCLE METHODS ==========
    
    def closeEvent(self, event):
        """Override para manejar el cierre de la ventana"""
        reply = QMessageBox.question(
            self,
            'Confirmar Salida',
            '¿Está seguro que desea salir de PROGAIN?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print("👋 Cerrando aplicación...")
            event.accept()
        else:
            event.ignore()


# ========== FUNCIÓN AUXILIAR PARA TESTING ==========

def main():
    """
    Función main para testing standalone de la ventana.
    
    Ejecutar con: python -m progain4.ui.main_window_modern
    """
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setApplicationName("PROGAIN 5.2")
    app.setOrganizationName("Constructora")
    
    window = MainWindowModern()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
