"""
Sidebar - Barra lateral de navegación moderna

Componente completo del sidebar con fondo oscuro garantizado mediante paintEvent
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QBrush

from .. components.nav_button import ModernNavButton
from ..components. icon_manager import icon_manager
from ..theme_config import COLORS, BORDER


class Sidebar(QWidget):
    """
    Sidebar de navegación moderno con fondo oscuro slate-900.
    
    Señales:
        navigation_changed(str): Emitida cuando cambia la navegación
    """
    
    navigation_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 'dashboard'
        self.nav_buttons = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Crear la UI del sidebar"""
        
        # Ancho fijo
        self.setFixedWidth(100)
        
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
        
        # === LOGO (ARRIBA) ===
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
        logo_icon = QLabel()
        logo_pixmap = icon_manager.get_pixmap('hard-hat', COLORS['white'], 32)
        logo_icon.setPixmap(logo_pixmap)
        logo_icon.setAlignment(Qt.AlignmentFlag. AlignCenter)
        logo_icon.setStyleSheet("background-color: transparent;")
        logo_layout.addWidget(logo_icon)
        
        layout.addWidget(logo_container, alignment=Qt.AlignmentFlag. AlignHCenter)
        layout.addSpacing(24)
        
        # === BOTONES DE NAVEGACIÓN ===
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(16)
        nav_layout.setAlignment(Qt.AlignmentFlag. AlignTop)
        
        # Crear los 5 botones
        self.btn_panel = ModernNavButton("dashboard", "Panel")
        self.btn_obras = ModernNavButton("building", "Obras")
        self.btn_trans = ModernNavButton("transactions", "Trans")
        self.btn_caja = ModernNavButton("wallet", "Caja")
        self.btn_reportes = ModernNavButton("chart", "Reportes")
        
        # Lista para gestionar estados
        self.nav_buttons = [
            ('dashboard', self.btn_panel),
            ('projects', self.btn_obras),
            ('transactions', self.btn_trans),
            ('cash', self.btn_caja),
            ('reports', self.btn_reportes),
        ]
        
        # Conectar señales
        for page_id, button in self.nav_buttons:
            button.clicked.connect(lambda p=page_id: self.navigate_to(p))
            nav_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        layout.addLayout(nav_layout)
        layout.addStretch()
        
        # === SETTINGS (ABAJO) ===
        settings_container = QWidget()
        settings_container.setFixedSize(40, 40)
        settings_container.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_container.setStyleSheet("background-color: transparent;")
        
        settings_layout = QVBoxLayout(settings_container)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout. setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.settings_icon = QLabel()
        self.settings_icon.setStyleSheet("background-color: transparent;")
        settings_pixmap = icon_manager.get_pixmap('settings', COLORS['slate_400'], 20)
        self.settings_icon.setPixmap(settings_pixmap)
        self.settings_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(self.settings_icon)
        
        # Hover effect
        settings_container.enterEvent = lambda e: self._on_settings_hover(True)
        settings_container.leaveEvent = lambda e: self._on_settings_hover(False)
        
        layout.addWidget(settings_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(12)
        
        # === AVATAR (ABAJO) ===
        avatar = QLabel("👤")
        avatar.setAlignment(Qt.AlignmentFlag. AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['slate_700']};
                border:  2px solid {COLORS['slate_600']};
                border-radius: 16px;
                font-size: 16px;
                color: {COLORS['slate_400']};
            }}
        """)
        avatar.setFixedSize(32, 32)
        avatar.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Activar primer botón
        self.btn_panel.set_active(True)
    
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
    
    def _on_settings_hover(self, hovered: bool):
        """Hover effect en settings"""
        color = COLORS['white'] if hovered else COLORS['slate_400']
        pixmap = icon_manager.get_pixmap('settings', color, 20)
        self.settings_icon.setPixmap(pixmap)
    
    def set_active_page(self, page_id: str):
        """Establecer página activa sin emitir señal"""
        for pid, button in self.nav_buttons:
            button.set_active(pid == page_id)
        self.current_page = page_id
    
    # ========== OVERRIDE PAINT EVENT (SOLUCIÓN NUCLEAR) ==========
    
    def paintEvent(self, event):
        """
        Override paintEvent para garantizar fondo oscuro SIEMPRE.
        Este método se llama cada vez que el widget necesita repintarse.
        """
        painter = QPainter(self)
        painter.fillRect(self.rect(), QBrush(QColor(COLORS['slate_900'])))
        painter.end()
        
        # Llamar al paintEvent original
        super().paintEvent(event)
    
    def showEvent(self, event):
        """
        Override showEvent para forzar estilos cuando se muestra el widget.
        """
        super().showEvent(event)
        
        # Forzar fondo oscuro DESPUÉS de que el widget sea visible
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['slate_900']))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # Forzar repintado
        self. update()