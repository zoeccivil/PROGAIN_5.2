"""
MainWindow - Ventana principal moderna completa

Ensambla todos los componentes:    
- Sidebar (izquierda) - Colapsable y resizable con QSplitter
- Header (arriba)
- Contenido (páginas con QStackedWidget)
- Settings menu handlers
"""

import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QStackedWidget, QLabel, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

# Imports absolutos (funcionan siempre)
from ui.modern.widgets.sidebar import Sidebar
from ui.modern.widgets.header import Header
from ui. modern.components.clean_card import CleanCard
from ui. modern.theme_config import COLORS

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Ventana principal moderna - Construction Manager Pro
    
    Features:
    - Sidebar colapsable y resizable
    - Header con búsqueda y acciones
    - Sistema de páginas con QStackedWidget
    - Integración completa con Firebase
    - Menú de settings
    """
    
    def __init__(self, firebase_client=None, proyecto_id=None, proyecto_nombre=None, config_manager=None, parent=None):
        """
        Initialize MainWindow with Firebase integration.  
        
        Args: 
            firebase_client: FirebaseClient instance
            proyecto_id: Current project ID
            proyecto_nombre:   Current project name
            config_manager: ConfigManager instance
            parent:   Parent widget
        """
        super().__init__(parent)
        
        # Store Firebase integration
        self.firebase_client = firebase_client
        self.proyecto_id = proyecto_id
        self.proyecto_nombre = proyecto_nombre or f"Proyecto {proyecto_id}"
        self.config_manager = config_manager
        
        # Estado
        self.current_page = 'dashboard'
        self.current_company = proyecto_id  # Map proyecto to company
        
        self.setup_window()
        self.setup_ui()
        self.setup_connections()
        
        # Update with real project name
        if proyecto_nombre:
            self.  header. set_title(f"Control de Obra - {proyecto_nombre}")
        
        print("✅ Modern MainWindow inicializada con Firebase")
    
    def setup_window(self):
        """Configurar ventana principal"""
        self.setWindowTitle("PROGAIN 5.0 - Construction Manager Pro")
        self.setMinimumSize(1280, 720)
        self.resize(1440, 900)
        
        # Fondo general
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['slate_50']};
            }}
        """)
    
    def setup_ui(self):
        """Crear la UI completa con QSplitter"""
        
        # Widget central
        central = QWidget()
        central.setStyleSheet(f"background-color: {COLORS['slate_50']};")
        self.setCentralWidget(central)
        
        # ✅ USAR QSPLITTER para sidebar resizable
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter. setHandleWidth(1)  # Línea delgada para arrastrar
        main_splitter.setStyleSheet(f"""
            QSplitter::  handle {{
                background-color:   {COLORS['slate_800']};
            }}
            QSplitter::  handle:hover {{
                background-color:  {COLORS['blue_600']};
            }}
        """)
        
        # === SIDEBAR (Izquierda - Resizable) ===
        self.sidebar = Sidebar()
        
        # FORZAR FONDO OSCURO DEL SIDEBAR
        sidebar_palette = self.sidebar.palette()
        sidebar_palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['slate_900']))
        self.sidebar.setPalette(sidebar_palette)
        self.sidebar.setAutoFillBackground(True)
        
        main_splitter.addWidget(self.sidebar)
        
        # === CONTENIDO DERECHO ===
        content_widget = QWidget()
        content_widget.  setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['slate_50']};
            }}
        """)
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- HEADER (Arriba) ---
        self.header = Header(firebase_client=self.firebase_client)
        
        # Cargar proyectos en el header
        self.header.load_projects()
        
        # Establecer proyecto actual
        self.header.set_current_project(self.proyecto_id, self.proyecto_nombre)
        
        content_layout.addWidget(self.  header)
        
        # --- PÁGINAS (Abajo) ---
        self.pages_stack = QStackedWidget()
        self.pages_stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color:   {COLORS['slate_50']};
            }}
        """)
        
        # Crear las páginas
        self.create_pages()
        
        content_layout.addWidget(self.  pages_stack)
        
        main_splitter.addWidget(content_widget)
        
        # ✅ CONFIGURAR TAMAÑOS Y COMPORTAMIENTO DEL SPLITTER
        main_splitter.setSizes([135, 1000])  # [sidebar inicial, content]
        main_splitter.setStretchFactor(0, 0)  # Sidebar no stretch
        main_splitter.setStretchFactor(1, 1)  # Content stretch
        
        # Layout principal
        main_layout = QHBoxLayout(central)
        main_layout.  setSpacing(0)
        main_layout. setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_splitter)
    
    def create_pages(self):
        """Crear las páginas del contenido principal"""
        from .pages.dashboard_page import DashboardPage
        from .pages.obras_page import ObrasPage
        from .pages.transactions_page import TransactionsPage
        from .pages.cash_flow_page import CashFlowPage  # ✅ NUEVO
        from .pages.placeholder_page import PlaceholderPage
        from services.account_service import AccountService
        
        # Crear servicio de cuentas
        self.account_service = AccountService(self.firebase_client, self.proyecto_id)
        
        # === PÁGINA 0: DASHBOARD ===
        self.page_dashboard = DashboardPage(
            firebase_client=self.firebase_client,
            proyecto_id=self.proyecto_id,
            proyecto_nombre=self.proyecto_nombre,
            parent=self
        )
        self.page_dashboard.account_clicked.connect(self._on_account_clicked_from_dashboard)
        self.pages_stack.addWidget(self.page_dashboard)
        
        # === PÁGINA 1: OBRAS ===
        self.page_obras = ObrasPage(
            firebase_client=self.firebase_client,
            parent=self
        )
        self.page_obras.project_selected.connect(self._on_project_selected_from_obras)
        self.pages_stack.addWidget(self.page_obras)
        
        # === PÁGINA 2: TRANSACCIONES ===
        self.page_trans = TransactionsPage(
            firebase_client=self.firebase_client,
            proyecto_id=self.proyecto_id,
            proyecto_nombre=self.proyecto_nombre,
            parent=self
        )
        self.pages_stack.addWidget(self.page_trans)
        
        # === PÁGINA 3: FLUJO DE CAJA ✅ NUEVO ===
        self.page_caja = CashFlowPage(
            firebase_client=self.firebase_client,
            proyecto_id=self.proyecto_id,
            proyecto_nombre=self.proyecto_nombre,
            parent=self
        )
        self.pages_stack.addWidget(self.page_caja)
        
        # === PÁGINA 4: REPORTES ✅ NUEVO ===
        from .pages.reports_page import ReportsPage

        self.page_reportes = ReportsPage(
            firebase_client=self.firebase_client,
            proyecto_id=self.proyecto_id,
            proyecto_nombre=self.proyecto_nombre,
            parent=self
        )
        self.pages_stack.addWidget(self.page_reportes)
        
        self.page_importar = PlaceholderPage(
            icon="📥",
            title="Importar Datos",
            description="Próximamente: Importación masiva desde Excel, CSV y otros formatos"
        )
        self.pages_stack.addWidget(self.page_importar)
        
        print("✅ 6 páginas creadas (Dashboard, Obras, Transacciones, Caja, Reportes, Importar)")

    def setup_connections(self):
        """Conectar signals y slots"""
        
        # === SIDEBAR SIGNALS ===
        if hasattr(self.sidebar, 'navigation_changed'):
            self.sidebar.navigation_changed.connect(self.on_navigation_changed)
        
        # === HEADER SIGNALS ===
        
        # Cambio de proyecto
        if hasattr(self.header, 'project_changed'):
            self.header.project_changed.connect(self.on_project_changed)
        
        # Búsqueda
        if hasattr(self.header, 'search_triggered'):
            self.header.search_triggered.connect(self.on_search_triggered)
        
        # Notificaciones
        if hasattr(self.header, 'notifications_clicked'):
            self.header.notifications_clicked.connect(self.on_notifications_clicked)
        
        # Usuario
        if hasattr(self.header, 'user_clicked'):
            self.header.user_clicked.connect(self.on_user_clicked)
        
        print("✅ Señales y slots conectados")

    # ✅ AGREGAR ESTE MÉTODO AQUÍ:
    def on_navigation_changed(self, page_key: str):
        """
        Callback cuando cambia la navegación desde el sidebar.
        
        Args:
            page_key: Clave de la página ('dashboard', 'obras', 'trans', etc.)
        """
        logger.info(f"📍 Navigation changed from sidebar: {page_key}")
        self.navigate_to_page(page_key)


    
    # ========== NAVEGACIÓN ==========
    
    def navigate_to_page(self, page_key:  str):
        """
        Navegar a una página según la clave. 
        
        Args:
            page_key: Clave de la página o acción
        """
        print(f"📍 Navegando a:  {page_key}")
        
        # ===== MANEJO DE SETTINGS =====
        if page_key.  startswith('settings_'):
            self._handle_settings_action(page_key)
            return
        
        # ===== MAPEO DE PÁGINAS =====
        page_map = {
            'dashboard': 0,
            'obras': 1,
            'trans': 2,
            'caja': 3,
            'reportes':  4,
            'import': 5,
            
            # Compatibilidad con nombres antiguos
            'projects': 1,
            'transactions': 2,
            'cash':  3,
            'reports': 4,
        }
        
        page_index = page_map.  get(page_key)
        
        if page_index is not None:
            self.pages_stack.setCurrentIndex(page_index)
            self.current_page = page_key
            print(f"✅ Navegado a:   {page_key} (página {page_index})")
            
            # Actualizar botón activo del sidebar
            if hasattr(self. sidebar, 'set_active_page'):
                self. sidebar.set_active_page(page_key)
            
            # Actualizar título del header
            titles = {
                'dashboard': f"Control de Obra - {self.proyecto_nombre}",
                'obras': "Gestión de Obras",
                'trans': "Transacciones",
                'caja': "Flujo de Caja",
                'reportes': "Reportes",
                'import': "Importar Datos",
                'projects': "Gestión de Obras",
                'transactions':   "Transacciones",
                'cash': "Flujo de Caja",
                'reports': "Reportes",
            }
            
            self.header.set_title(titles.get(page_key, self.proyecto_nombre))
        else:
            print(f"⚠️ Página no encontrada:   {page_key}")
    
    # ========== SETTINGS HANDLERS ==========
    
    def _handle_settings_action(self, action_key: str):
        """
        Handle settings menu actions. 
        
        Args:
            action_key: Settings action key (e.g., 'settings_database_config')
        """
        # Remove 'settings_' prefix
        action = action_key.  replace('settings_', '')
        
        logger.info(f"⚙️ Settings action triggered: {action}")
        
        # ===== MAPEO DE ACCIONES =====
        actions_map = {
            'database_config': self._open_database_config,
            'categorias_maestras': self._open_categorias_maestras,
            'categorias_proyecto': self._open_categorias_proyecto,
            'cuentas_maestras': self._open_cuentas_maestras,
            'cuentas_proyecto': self._open_cuentas_proyecto,
            'presupuestos': self._open_presupuestos,
            'auditorias': self._open_auditorias,
            'preferencias': self._open_preferencias,
        }
        
        # Execute action
        handler = actions_map.get(action)
        if handler:
            handler()
        else:
            QMessageBox.information(
                self,
                "Próximamente",
                f"La funcionalidad '{action}' está en desarrollo.\n\n"
                "Será implementada en la siguiente fase."
            )
    
    # ===== SETTINGS HANDLERS (PLACEHOLDERS) =====
    
    def _open_database_config(self):
        """Open database configuration dialog"""
        logger.info("Opening database configuration...")
        QMessageBox.information(
            self,
            "Configuración de Base de Datos",
            "Próximamente:  Configuración de conexión a Firebase\n\n"
            "Aquí podrás:\n"
            "• Cambiar credenciales de Firebase\n"
            "• Configurar bucket de almacenamiento\n"
            "• Verificar conexión"
        )
    
    def _open_categorias_maestras(self):
        """Open master categories editor"""
        logger.info("Opening master categories...")
        QMessageBox.information(
            self,
            "Categorías Maestras",
            "Próximamente:  Editor de categorías globales\n\n"
            "Aquí podrás:\n"
            "• Crear nuevas categorías\n"
            "• Editar categorías existentes\n"
            "• Eliminar categorías no utilizadas"
        )
    
    def _open_categorias_proyecto(self):
        """Open project categories editor"""
        logger.info("Opening project categories...")
        QMessageBox.information(
            self,
            "Categorías del Proyecto",
            f"Próximamente:  Asignar categorías al proyecto {self.proyecto_nombre}\n\n"
            "Aquí podrás:\n"
            "• Asignar categorías maestras al proyecto\n"
            "• Ver categorías activas\n"
            "• Desactivar categorías no utilizadas"
        )
    
    def _open_cuentas_maestras(self):
        """Open master accounts editor"""
        logger.  info("Opening master accounts...")
        QMessageBox.information(
            self,
            "Cuentas Maestras",
            "Próximamente: Editor de cuentas globales\n\n"
            "Aquí podrás:\n"
            "• Crear nuevas cuentas bancarias\n"
            "• Editar cuentas existentes\n"
            "• Administrar tipos de cuenta"
        )
    
    def _open_cuentas_proyecto(self):
        """Open project accounts editor"""
        logger.info("Opening project accounts...")
        QMessageBox.information(
            self,
            "Cuentas del Proyecto",
            f"Próximamente:  Vincular cuentas al proyecto {self.proyecto_nombre}\n\n"
            "Aquí podrás:\n"
            "• Vincular cuentas maestras al proyecto\n"
            "• Configurar saldos iniciales\n"
            "• Ver historial de cuentas"
        )
    
    def _open_presupuestos(self):
        """Open budget management"""
        logger.info("Opening budget management...")
        QMessageBox.  information(
            self,
            "Gestión de Presupuestos",
            "Próximamente:   Sistema de presupuestos\n\n"
            "Aquí podrás:\n"
            "• Crear presupuestos por categoría\n"
            "• Monitorear gastos vs presupuesto\n"
            "• Recibir alertas de sobregasto"
        )
    
    def _open_auditorias(self):
        """Open audit logs"""
        logger.info("Opening audit logs...")
        QMessageBox.information(
            self,
            "Auditorías",
            "Próximamente:  Sistema de auditorías\n\n"
            "Aquí podrás:\n"
            "• Ver historial de cambios\n"
            "• Rastrear modificaciones\n"
            "• Exportar logs de auditoría"
        )
    
    def _open_preferencias(self):
        """Open preferences dialog"""
        logger.info("Opening preferences...")
        QMessageBox.  information(
            self,
            "Preferencias",
            "Próximamente:  Configuración de preferencias\n\n"
            "Aquí podrás:\n"
            "• Cambiar tema (claro/oscuro)\n"
            "• Configurar moneda predeterminada\n"
            "• Personalizar formato de fechas\n"
            "• Ajustar notificaciones"
        )
    
    # ========== CALLBACKS ==========
    
    
    def on_project_changed(self, proyecto_id: str, proyecto_nombre: str):
        """
        Callback cuando cambia el proyecto desde el header O desde obras_page.
        
        Args:
            proyecto_id: ID del proyecto seleccionado
            proyecto_nombre: Nombre del proyecto
        """
        logger.info(f"🏢 Project changed: {proyecto_nombre} ({proyecto_id})")
        
        # Si es "Vista Global", manejar diferente
        if proyecto_id == "all":
            logger.info("Switched to global view")
            QMessageBox.information(
                self,
                "Vista Global",
                "La vista global mostrará datos de todos los proyectos.\n\n"
                "Esta funcionalidad se implementará próximamente."
            )
            return
        
        # ✅ Actualizar proyecto actual
        self.proyecto_id = proyecto_id
        self.proyecto_nombre = proyecto_nombre
        
        # Actualizar título
        self.header.set_title(f"Control de Obra - {proyecto_nombre}")
        
        # Actualizar selector de proyecto en el header
        if hasattr(self.header, 'set_current_project'):
            self.header.set_current_project(proyecto_id, proyecto_nombre)
        
        # Guardar en config
        if hasattr(self, 'config_manager') and self.config_manager:
            self.config_manager.set_last_project(proyecto_id, proyecto_nombre)
        
        # ✅ NUEVO: Actualizar TODAS las páginas con el nuevo proyecto
        logger.info(f"Updating all pages with new project: {proyecto_nombre}")
        
        # Update Dashboard
        if hasattr(self, 'page_dashboard'):
            try:
                self.page_dashboard.on_project_change(proyecto_id, proyecto_nombre)
                logger.info("✅ Dashboard updated")
            except Exception as e:
                logger.error(f"Error updating dashboard: {e}")
        
        # Update Transactions
        if hasattr(self, 'page_trans'):
            try:
                self.page_trans.on_project_change(proyecto_id, proyecto_nombre)
                logger.info("✅ Transactions updated")
            except Exception as e:
                logger.error(f"Error updating transactions: {e}")
        
        # ✅ Update CashFlowPage
        if hasattr(self, 'page_caja'):
            try:
                self.page_caja.on_project_change(proyecto_id, proyecto_nombre)
                logger.info("✅ CashFlow updated")
            except Exception as e:
                logger.error(f"Error updating cashflow: {e}")
        
        # Update Obras (refresh list)
        if hasattr(self, 'page_obras'):
            try:
                self.page_obras.refresh()
                logger.info("✅ Obras refreshed")
            except Exception as e:
                logger.error(f"Error refreshing obras: {e}")
        
        logger.info("✅ All pages updated for new project")

        # Update Reports
        if hasattr(self, 'page_reportes'):
            try:
                self.page_reportes.on_project_change(proyecto_id, proyecto_nombre)
                logger.info("✅ Reports updated")
            except Exception as e:
                logger.error(f"Error updating reports: {e}")
    
    def _reload_project_data(self):
        """Recargar todos los datos del proyecto actual"""
        logger.info(f"Reloading data for project {self.proyecto_id}")
        
        # Recargar servicios
        if hasattr(self, 'account_service'):
            self.account_service.proyecto_id = self.proyecto_id
        
        # Recargar Dashboard
        if hasattr(self, 'page_dashboard'):
            try:
                self.page_dashboard.set_project(self.proyecto_id, self.  proyecto_nombre)
                logger.info("✅ Dashboard project updated")
            except Exception as e:  
                logger.error(f"Error refreshing dashboard: {e}")
        
        # Recargar Obras
        if hasattr(self, 'page_obras'):
            try:
                self.page_obras.refresh()
                logger.info("✅ Obras page refreshed")
            except Exception as e:  
                logger.error(f"Error refreshing obras: {e}")
        
        # Recargar TransactionsPage
        if hasattr(self, 'page_trans'):
            try:
                self.  page_trans.proyecto_id = self.proyecto_id
                self.page_trans.  proyecto_nombre = self.proyecto_nombre
                self.page_trans.load_data()
                logger.info("✅ Transactions page updated")
            except Exception as e:  
                logger.error(f"Error refreshing transactions: {e}")
        
        logger.info("✅ Project data reloaded")
    
    def on_search_triggered(self, search_text: str):
        """Handle global search"""
        logger.info(f"🔍 Search triggered: {search_text}")
        
        QMessageBox.information(
            self,
            "Búsqueda",
            f"Buscando:   {search_text}\n\n"
            "La búsqueda global se implementará próximamente."
        )
    
    def on_notifications_clicked(self):
        """Handle notifications button click"""
        logger.info("🔔 Notifications clicked")
        
        QMessageBox.information(
            self,
            "Notificaciones",
            "Panel de notificaciones próximamente:\n\n"
            "• Alertas de presupuesto\n"
            "• Transacciones pendientes\n"
            "• Recordatorios de pagos\n"
            "• Actualizaciones del sistema"
        )
    
    def on_user_clicked(self):
        """Handle user button click"""
        logger.info("👤 User menu clicked")
        
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        # Crear menú de usuario
        menu = QMenu(self)
        
        # Perfil
        action_profile = QAction("👤 Mi Perfil", self)
        action_profile.triggered.connect(lambda: QMessageBox.information(
            self, "Perfil", "Configuración de perfil próximamente"
        ))
        menu.addAction(action_profile)
        
        menu.addSeparator()
        
        # Configuración
        action_settings = QAction("⚙️ Configuración", self)
        action_settings.  triggered.connect(lambda: self. navigate_to_page('settings_preferencias'))
        menu.addAction(action_settings)
        
        menu.addSeparator()
        
        # Cerrar sesión
        action_logout = QAction("🚪 Cerrar Sesión", self)
        action_logout.triggered.connect(self.close)
        menu.addAction(action_logout)
        
        # Mostrar menú
        menu.exec(self.header.user_button. mapToGlobal(
            self.header.user_button.rect().bottomRight()
        ))
    
    def _on_account_clicked_from_dashboard(self, cuenta_id: str):
        """Handle cuando se hace click en una cuenta del dashboard"""
        logger.info(f"✅ MainWindow:   Cuenta seleccionada: {cuenta_id}")
        
        # Navegar a transacciones
        self.navigate_to_page('transactions')
    
    def _on_project_selected_from_obras(self, proyecto_id: str, proyecto_nombre: str):
        """Handle project selection from ObrasPage"""
        logger.info(f"Project selected from Obras: {proyecto_id} - {proyecto_nombre}")
        
        # Update current project
        self.proyecto_id = proyecto_id
        self.proyecto_nombre = proyecto_nombre
        
        # Update all pages
        if hasattr(self, 'page_dashboard'):
            self.page_dashboard.on_project_change(proyecto_id, proyecto_nombre)
        
        if hasattr(self, 'page_trans'):
            self.page_trans.on_project_change(proyecto_id, proyecto_nombre)
        
        # ✅ NUEVO: Update CashFlowPage
        if hasattr(self, 'page_caja'):
            self.page_caja.on_project_change(proyecto_id, proyecto_nombre)
        
        # Navigate to dashboard
        self.navigate_to_page('dashboard')
    
    # ========== MÉTODOS PÚBLICOS ==========
    
    def navigate_to(self, page_id: str):
        """Navegar a una página programáticamente"""
        self.navigate_to_page(page_id)