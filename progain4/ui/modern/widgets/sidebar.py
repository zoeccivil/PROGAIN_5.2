"""
Sidebar - Barra lateral de navegación moderna

Componente completo del sidebar con fondo oscuro garantizado mediante paintEvent
Incluye: Dashboard, Obras, Trans, Caja, Reportes, Importar, Config (con menú)
Soporta: Colapsar/Expandir y Resize con Splitter
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QMenu, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QBrush, QAction, QCursor

from .. components.nav_button import ModernNavButton
from ..components.icon_manager import icon_manager
from ..theme_config import COLORS, BORDER


class Sidebar(QWidget):
    """
    Sidebar de navegación moderno con fondo oscuro slate-900.
    
    Features: 
    - Colapsable con botón toggle
    - Resizable con QSplitter
    - Límites min/max configurables
    
    Señales:  
        navigation_changed(str): Emitida cuando cambia la navegación o acción de settings
        width_changed(int): Emitida cuando cambia el ancho
    """
    
    navigation_changed = pyqtSignal(str)
    width_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 'dashboard'
        self.nav_buttons = []
        
        # ✅ ESTADO DE COLAPSO
        self.is_collapsed = False
        self. expanded_width = 135   # Ancho expandido (tu actual)
        self.collapsed_width = 70   # Ancho colapsado (solo iconos)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Crear la UI del sidebar"""
        
        # ✅ ANCHO FLEXIBLE CON LÍMITES
        self.setMinimumWidth(70)   # Mínimo (colapsado)
        self.setMaximumWidth(200)  # Máximo (muy expandido)
        self.setFixedWidth(self.expanded_width)  # Inicial
        
        # FORZAR FONDO OSCURO CON PALETTE
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['slate_900']))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # Estilo adicional del sidebar
        self.setStyleSheet(f"""
            Sidebar {{
                background-color:  {COLORS['slate_900']};
                border-right: 1px solid {COLORS['slate_800']};
            }}
        """)
        
        # Layout principal vertical
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setAlignment(Qt.AlignmentFlag. AlignTop)
        
        # === HEADER CON LOGO Y BOTÓN TOGGLE ===
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        # Logo container
        logo_container = QFrame()
        logo_container.setFixedSize(64, 64)
        logo_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['blue_600']};
                border-radius: 12px;
            }}
        """)
        
        logo_layout = QVBoxLayout(logo_container)
        logo_layout. setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icono del logo
        self.logo_icon = QLabel()
        logo_pixmap = icon_manager. get_pixmap('hard-hat', COLORS['white'], 32)
        self.logo_icon.setPixmap(logo_pixmap)
        self.logo_icon.setAlignment(Qt. AlignmentFlag.AlignCenter)
        self.logo_icon.setStyleSheet("background-color:  transparent;")
        logo_layout.addWidget(self. logo_icon)
        
        header_layout.addWidget(logo_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # ✅ BOTÓN TOGGLE (Colapsar/Expandir)
        self.btn_toggle = QPushButton()
        self.btn_toggle. setFixedSize(32, 32)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle. setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['slate_800']};
                border: none;
                border-radius: 6px;
            }}
            QPushButton: hover {{
                background-color:  {COLORS['slate_700']};
            }}
        """)
        self._update_toggle_icon()
        self.btn_toggle.clicked.connect(self. toggle_collapse)
        header_layout.addWidget(self. btn_toggle, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        layout.addLayout(header_layout)
        layout.addSpacing(24)
        
        # === BOTONES DE NAVEGACIÓN ===
        self.nav_layout = QVBoxLayout()
        self.nav_layout.setSpacing(16)
        self.nav_layout.setAlignment(Qt.AlignmentFlag. AlignTop)
        
        # Crear los 6 botones
        self.btn_dashboard = ModernNavButton("layout-dashboard", "Dashboard")
        self.btn_obras = ModernNavButton("building-2", "Obras")
        self.btn_trans = ModernNavButton("repeat", "Trans")
        self.btn_caja = ModernNavButton("wallet", "Caja")
        self.btn_reportes = ModernNavButton("bar-chart-3", "Reportes")
        self.btn_import = ModernNavButton("download", "Importar")
        
        # Lista para gestionar estados
        self.nav_buttons = [
            ('dashboard', self.btn_dashboard),
            ('projects', self.btn_obras),
            ('transactions', self.btn_trans),
            ('cash', self.btn_caja),
            ('reports', self.btn_reportes),
            ('import', self.btn_import),
        ]
        
        # Conectar señales
        for page_id, button in self.nav_buttons:
            button.clicked.connect(lambda p=page_id: self.navigate_to(p))
            self.nav_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        layout.addLayout(self.nav_layout)
        layout.addStretch()
        
        # === SETTINGS BUTTON (CON MENÚ) ===
        self.settings_container = QWidget()
        self.settings_container.setFixedSize(64, 64)
        self.settings_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_container. setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border-radius: 12px;
            }}
            QWidget: hover {{
                background-color:  {COLORS['slate_800']};
            }}
        """)
        
        settings_layout = QVBoxLayout(self.settings_container)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.setSpacing(2)
        
        # Icono de settings
        self.settings_icon = QLabel()
        self.settings_icon.setStyleSheet("background-color: transparent;")
        settings_pixmap = icon_manager.get_pixmap('settings', COLORS['slate_400'], 24)
        self.settings_icon.setPixmap(settings_pixmap)
        self.settings_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(self. settings_icon)
        
        # Label "Config"
        self.settings_label = QLabel("Config")
        self.settings_label.setAlignment(Qt.AlignmentFlag. AlignCenter)
        self.settings_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {COLORS['slate_400']};
                font-size:  10px;
                font-weight:  500;
            }}
        """)
        settings_layout.addWidget(self. settings_label)
        
        # Click event para abrir menú
        self.settings_container.mousePressEvent = lambda e: self._show_settings_menu()
        
        # Hover effect
        self.settings_container.enterEvent = lambda e: self._on_settings_hover(True)
        self.settings_container.leaveEvent = lambda e: self._on_settings_hover(False)
        
        layout.addWidget(self.settings_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(12)
        
        # === AVATAR (ABAJO) ===
        self.avatar = QLabel("👤")
        self.avatar. setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['slate_700']};
                border:  2px solid {COLORS['slate_600']};
                border-radius: 16px;
                font-size: 16px;
                color: {COLORS['slate_400']};
            }}
        """)
        self.avatar.setFixedSize(32, 32)
        self.avatar.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(self. avatar, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Activar primer botón (Dashboard)
        self.btn_dashboard.set_active(True)
    
    # ==================== NAVEGACIÓN ====================
    
    def navigate_to(self, page_id:  str):
        """Navegar a una página"""
        print(f"📍 Navegando a: {page_id}")
        
        # Desactivar todos
        for pid, button in self.nav_buttons:
            button.set_active(False)
        
        # Activar el correspondiente
        for pid, button in self.nav_buttons:
            if pid == page_id: 
                button.set_active(True)
                break
        
        self.current_page = page_id
        self.navigation_changed. emit(page_id)
    
    def set_active_page(self, page_id: str):
        """Establecer página activa sin emitir señal"""
        for pid, button in self.nav_buttons:
            button.set_active(pid == page_id)
        self.current_page = page_id
    
    # ==================== COLAPSAR/EXPANDIR ====================
    
    def toggle_collapse(self):
        """Alternar entre colapsado y expandido"""
        if self.is_collapsed:
            self.expand()
        else:
            self. collapse()
    
    def collapse(self):
        """Colapsar el sidebar (solo iconos)"""
        if self.is_collapsed:
            return
        
        self.is_collapsed = True
        
        # Cambiar ancho del sidebar
        self.setFixedWidth(self.collapsed_width)
        
        # ✅ OCULTAR TEXTOS DE BOTONES (usando text_label)
        for _, button in self.nav_buttons: 
            if hasattr(button, 'hide_text'):
                button.hide_text()
        
        # Ocultar label de settings
        if hasattr(self, 'settings_label'):
            self.settings_label.hide()
        
        # Actualizar icono del botón toggle
        self._update_toggle_icon()
        
        # Emitir señal
        self.width_changed.emit(self.collapsed_width)
        
        print("📐 Sidebar colapsado")
    
    def expand(self):
        """Expandir el sidebar (iconos + texto)"""
        if not self.is_collapsed:
            return
        
        self.is_collapsed = False
        
        # Cambiar ancho del sidebar
        self.setFixedWidth(self.expanded_width)
        
        # ✅ MOSTRAR TEXTOS DE BOTONES (usando text_label)
        for _, button in self.nav_buttons:
            if hasattr(button, 'show_text'):
                button.show_text()
        
        # Mostrar label de settings
        if hasattr(self, 'settings_label'):
            self.settings_label.show()
        
        # Actualizar icono del botón toggle
        self._update_toggle_icon()
        
        # Emitir señal
        self.width_changed.emit(self.expanded_width)
        
        print("📐 Sidebar expandido")
    
    def _update_toggle_icon(self):
        """Actualizar icono del botón toggle"""
        if self.is_collapsed:
            # Icono para expandir (→)
            icon_name = 'chevron-right'
        else: 
            # Icono para colapsar (←)
            icon_name = 'chevron-left'
        
        pixmap = icon_manager.get_pixmap(icon_name, COLORS['slate_400'], 20)
        self.btn_toggle.setIcon(icon_manager.get_icon(icon_name, COLORS['slate_400'], 20))
    
    # ==================== SETTINGS MENU ====================
    
    def _on_settings_hover(self, hovered: bool):
        """Hover effect en settings"""
        color = COLORS['white'] if hovered else COLORS['slate_400']
        pixmap = icon_manager.get_pixmap('settings', color, 24)
        self.settings_icon.setPixmap(pixmap)
    
    def _show_settings_menu(self):
        """Mostrar menú contextual de configuración"""
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['slate_800']};
                border: 1px solid {COLORS['slate_700']};
                border-radius: 8px;
                padding: 6px;
            }}
            QMenu::item {{
                padding:  10px 20px 10px 40px;
                border-radius: 6px;
                font-size: 13px;
                color: {COLORS['slate_200']};
                background-color: transparent;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['slate_700']};
                color:  {COLORS['white']};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {COLORS['slate_700']};
                margin: 6px 10px;
            }}
            QMenu::item:disabled {{
                color: {COLORS['slate_500']};
                font-weight: 600;
                padding-left: 20px;
            }}
        """)
        
        # Base de Datos
        db_action = QAction("🗄️ Base de Datos", self)
        db_action.triggered.connect(lambda: self._emit_settings_action('database_config'))
        menu.addAction(db_action)
        
        menu.addSeparator()
        
        # EDITAR
        edit_header = QAction("EDITAR", self)
        edit_header.setEnabled(False)
        menu.addAction(edit_header)
        
        cat_maestras_action = QAction("   📁 Categorías Maestras", self)
        cat_maestras_action. triggered.connect(lambda: self._emit_settings_action('categorias_maestras'))
        menu.addAction(cat_maestras_action)
        
        cat_proyecto_action = QAction("   📂 Cat.  del Proyecto", self)
        cat_proyecto_action.triggered.connect(lambda: self._emit_settings_action('categorias_proyecto'))
        menu.addAction(cat_proyecto_action)
        
        acc_maestras_action = QAction("   💳 Cuentas Maestras", self)
        acc_maestras_action.triggered.connect(lambda: self._emit_settings_action('cuentas_maestras'))
        menu.addAction(acc_maestras_action)
        
        acc_proyecto_action = QAction("   🏦 Cuentas del Proyecto", self)
        acc_proyecto_action.triggered.connect(lambda: self._emit_settings_action('cuentas_proyecto'))
        menu.addAction(acc_proyecto_action)
        
        budget_action = QAction("   💰 Presupuestos", self)
        budget_action.triggered.connect(lambda: self._emit_settings_action('presupuestos'))
        menu.addAction(budget_action)
        
        menu.addSeparator()
        
        audit_action = QAction("✅ Auditorías", self)
        audit_action.triggered.connect(lambda: self._emit_settings_action('auditorias'))
        menu.addAction(audit_action)
        
        prefs_action = QAction("⚙️ Preferencias", self)
        prefs_action.triggered.connect(lambda: self._emit_settings_action('preferencias'))
        menu.addAction(prefs_action)
        
        # Mostrar menú a la derecha del botón settings
        button_rect = self.settings_container.geometry()
        menu_pos = self.mapToGlobal(button_rect.topRight())
        menu.exec(menu_pos)
    
    def _emit_settings_action(self, action_name: str):
        """Emitir señal de acción de settings"""
        print(f"⚙️ Settings action: {action_name}")
        self.navigation_changed.emit(f'settings_{action_name}')
    
    # ==================== PAINT EVENT ====================
    
    def paintEvent(self, event):
        """Override paintEvent para garantizar fondo oscuro SIEMPRE"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QBrush(QColor(COLORS['slate_900'])))
        painter.end()
        super().paintEvent(event)
    
    def showEvent(self, event):
        """Override showEvent para forzar estilos cuando se muestra el widget"""
        super().showEvent(event)
        palette = self.palette()
        palette.setColor(QPalette. ColorRole.Window, QColor(COLORS['slate_900']))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.update()