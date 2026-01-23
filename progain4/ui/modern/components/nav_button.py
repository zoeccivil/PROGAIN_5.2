"""
ModernNavButton - Versión con iconos SVG de Lucide
Soporta colapso (ocultar texto)
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor

from ..  theme_config import COLORS, BORDER
from . icon_manager import icon_manager


class ModernNavButton(QWidget):
    """
    Botón de navegación moderno con iconos SVG profesionales
    Soporta texto colapsable
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, icon_name: str, label_text: str, parent=None):
        """
        Args:  
            icon_name: Nombre del archivo SVG (ej: 'layout-dashboard')
            label_text: Texto del botón
        """
        super().__init__(parent)
        self.icon_name = icon_name
        self.label_text = label_text
        self.is_active = False
        self.is_hovered = False
        self.text_visible = True  # ✅ NUEVO: controlar visibilidad del texto
        
        self.setup_ui()
    
    def setup_ui(self):
        """Crear la UI del botón"""
        
        self.layout = QVBoxLayout(self)
        self.layout. setContentsMargins(8, 10, 8, 10)  # ✅ Reducido padding
        self.layout.setSpacing(4)
        self.layout.setAlignment(Qt. AlignmentFlag.AlignCenter)
        
        # Icono SVG
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(24, 24)  # ✅ Aumentado de 20 a 24
        self.icon_label.setStyleSheet("background-color: transparent;")
        
        # Texto
        self. text_label = QLabel(self. label_text)
        text_font = QFont()
        text_font.setPointSize(9)  # ✅ Reducido de 10 a 9
        text_font.setWeight(QFont.Weight.Medium)
        self.text_label.setFont(text_font)
        self.text_label. setAlignment(Qt.AlignmentFlag. AlignCenter)
        self.text_label.setWordWrap(True)  # ✅ NUEVO: permite wrap
        self.text_label.setStyleSheet("background-color: transparent;")
        
        self.layout.addWidget(self. icon_label)
        self.layout.addWidget(self.text_label)
        
        # ✅ Tamaño dinámico según estado
        self.setFixedHeight(70)
        self.setMinimumWidth(60)  # ✅ Mínimo para colapsado
        self.setMaximumWidth(120)  # ✅ Máximo para expandido
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
            bg_color = COLORS['slate_800']
            text_color = COLORS['white']
        elif self.is_hovered:
            bg_color = COLORS['slate_800']
            text_color = COLORS['slate_300']
        else:
            bg_color = 'transparent'
            text_color = COLORS['slate_400']
        
        self.setStyleSheet(f"""
            ModernNavButton {{
                background-color: {bg_color};
                border-radius: {BORDER['radius']}px;
            }}
        """)
        
        self.text_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                background-color: transparent;
            }}
        """)
    
    def update_icon(self):
        """Actualizar el icono según el estado"""
        # Determinar color del icono
        if self.is_active:
            color = COLORS['white']
        elif self.is_hovered:
            color = COLORS['slate_300']
        else: 
            color = COLORS['slate_400']
        
        # Cargar pixmap del icono
        pixmap = icon_manager.get_pixmap(self.icon_name, color, 24)
        self.icon_label.setPixmap(pixmap)
    
    def paintEvent(self, event):
        """Dibujar barra azul lateral cuando está activo"""
        super().paintEvent(event)
        
        if self.is_active:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(COLORS['blue_500']))
            
            bar_width = 3
            bar_height = 28
            x = 0
            y = (self.height() - bar_height) // 2
            
            painter.drawRoundedRect(x, y, bar_width, bar_height, 2, 2)
            painter.end()
    
    # ✅ NUEVO: Métodos para colapsar/expandir
    def hide_text(self):
        """Ocultar el texto del botón"""
        self.text_label.hide()
        self.text_visible = False
        self.setFixedWidth(60)  # Ancho colapsado
    
    def show_text(self):
        """Mostrar el texto del botón"""
        self.text_label.show()
        self.text_visible = True
        self.setFixedWidth(100)  # Ancho expandido
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        self.is_hovered = True
        self.update_style()
        self.update_icon()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.is_hovered = False
        self.update_style()
        self.update_icon()
        super().leaveEvent(event)