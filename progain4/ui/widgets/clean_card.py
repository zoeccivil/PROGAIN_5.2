"""
Clean card widgets for PROGAIN 5.2

Provides modern card containers with consistent styling.
"""

from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt


class CleanCard(QFrame):
    """
    Contenedor base para tarjetas modernas.
    
    Características:
    - Fondo: white
    - Borde: 1px solid slate_200
    - Border-radius: 12px
    - Sombra suave (elevación baja)
    - Padding: configurable (default 16px)
    """
    
    def __init__(self, padding=16, parent=None):
        """
        Initialize clean card widget.
        
        Args:
            padding: Internal padding in pixels
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui(padding)
    
    def setup_ui(self, padding):
        """Setup the card styling"""
        self.setObjectName("CleanCard")
        self.setStyleSheet(f"""
            QFrame#CleanCard {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: {padding}px;
            }}
        """)


class CleanCardAccent(QFrame):
    """
    CleanCard con borde lateral izquierdo de color.
    
    Usado para tarjetas de cuentas bancarias o elementos destacados.
    El borde izquierdo más ancho actúa como acento visual.
    """
    
    def __init__(self, accent_color='#3b82f6', padding=16, parent=None):
        """
        Initialize clean card with accent border.
        
        Args:
            accent_color: Hex color for left accent border (default: blue_500)
            padding: Internal padding in pixels
            parent: Parent widget
        """
        super().__init__(parent)
        self.accent_color = accent_color
        self.setup_ui(accent_color, padding)
    
    def setup_ui(self, accent_color, padding):
        """Setup the card styling with accent"""
        self.setObjectName("CleanCardAccent")
        self.setStyleSheet(f"""
            QFrame#CleanCardAccent {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-left: 4px solid {accent_color};
                border-radius: 12px;
                padding: {padding}px;
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def set_accent_color(self, color: str):
        """
        Change the accent border color.
        
        Args:
            color: Hex color string (e.g., '#3b82f6')
        """
        self.accent_color = color
        padding = 16  # Use default padding
        self.setStyleSheet(f"""
            QFrame#CleanCardAccent {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-left: 4px solid {color};
                border-radius: 12px;
                padding: {padding}px;
            }}
        """)
