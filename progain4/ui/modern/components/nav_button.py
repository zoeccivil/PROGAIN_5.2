"""
ModernNavButton - Versión con iconos SVG de Lucide
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QPixmap

from .. theme_config import COLORS, BORDER
from . icon_manager import icon_manager


# Mapeo de nombres a archivos SVG
ICON_MAP = {
    'dashboard': 'layout-dashboard',
    'panel': 'layout-dashboard',
    'building': 'building-2',
    'obras': 'building-2',
    'wallet': 'wallet',
    'caja': 'wallet',
    'chart': 'bar-chart-3',
    'reportes': 'bar-chart-3',
    'settings': 'settings',
    'hard-hat': 'hard-hat',
    'list': 'list',                    # ← AGREGAR ESTO
    'transacciones': 'list',           # ← AGREGAR ESTO
    'transactions': 'list',            # ← AGREGAR ESTO
}

class ModernNavButton(QWidget):
    """
    Botón de navegación moderno con iconos SVG profesionales
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, icon_name: str, label_text: str, parent=None):
        """
        Args:  
            icon_name: Nombre del icono ('dashboard', 'building', 'wallet', 'chart')
            label_text: Texto del botón
        """
        super().__init__(parent)
        self.icon_name = icon_name. lower()
        self.label_text = label_text
        self.is_active = False
        self. is_hovered = False
        
        # Obtener nombre del archivo SVG
        self.svg_name = ICON_MAP.get(self.icon_name, 'layout-dashboard')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Crear la UI del botón"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icono SVG
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(20, 20)
        
        # Texto
        self.text_label = QLabel(self. label_text)
        text_font = QFont()
        text_font.setPointSize(10)
        text_font.setWeight(QFont.Weight.Medium)
        self.text_label.setFont(text_font)
        self.text_label. setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        
        self.setFixedHeight(70)
        self.setFixedWidth(84)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.update_style()
        self.update_icon()
    
    def set_active(self, active: bool):
        """Cambiar estado activo/inactivo"""
        self. is_active = active
        self.update_style()
        self.update_icon()
        self.update()
    
    def update_style(self):
        """Actualizar estilos según estado"""
        
        if self.is_active:
            self.setStyleSheet(f"""
                ModernNavButton {{
                    background-color: {COLORS['slate_800']};
                    border-radius: {BORDER['radius']}px;
                }}
                QLabel {{
                    color: {COLORS['white']};
                    background-color: transparent;
                }}
            """)
        else:
            if self.is_hovered:
                self.setStyleSheet(f"""
                    ModernNavButton {{
                        background-color:  {COLORS['slate_100']};
                        border-radius: {BORDER['radius']}px;
                    }}
                    QLabel {{
                        color: {COLORS['slate_600']};
                        background-color: transparent;
                    }}
                """)
            else:
                self.setStyleSheet(f"""
                    ModernNavButton {{
                        background-color:  transparent;
                        border-radius: {BORDER['radius']}px;
                    }}
                    QLabel {{
                        color: {COLORS['slate_400']};
                        background-color: transparent;
                    }}
                """)
    
    def update_icon(self):
        """Actualizar el icono según el estado"""
        # Determinar color del icono
        if self.is_active:
            color = COLORS['white']
        elif self.is_hovered:
            color = COLORS['slate_600']
        else:
            color = COLORS['slate_400']
        
        # Cargar pixmap del icono
        pixmap = icon_manager.get_pixmap(self.svg_name, color, 20)
        self.icon_label.setPixmap(pixmap)
    
    def paintEvent(self, event):
        """Dibujar barra azul lateral cuando está activo"""
        super().paintEvent(event)
        
        if self.is_active:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(COLORS['blue_500']))
            
            bar_width = 4
            bar_height = 32
            x = 0
            y = (self.height() - bar_height) // 2
            
            painter.drawRoundedRect(x, y, bar_width, bar_height, 2, 2)
            painter.end()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        self.is_hovered = True
        if not self.is_active:
            self.update_style()
            self.update_icon()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.is_hovered = False
        if not self.is_active:
            self.update_style()
            self.update_icon()
        super().leaveEvent(event)