"""
Custom progress bar widget for PROGAIN 5.2

Provides modern, slim progress indicators.
"""

from PyQt6.QtWidgets import QProgressBar


class CustomProgressBar(QProgressBar):
    """
    Barra de progreso moderna y delgada.
    
    Características:
    - Altura configurable (default: 6px)
    - Border-radius completo
    - Sin bordes
    - Colores configurables
    - Sin texto visible
    """
    
    def __init__(self, bg_color='#f1f5f9', fill_color='#10b981', height=6, parent=None):
        """
        Initialize custom progress bar.
        
        Args:
            bg_color: Background color (default: slate_100)
            fill_color: Fill/progress color (default: emerald_500)
            height: Bar height in pixels
            parent: Parent widget
        """
        super().__init__(parent)
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.bar_height = height
        
        self.setTextVisible(False)
        self.setFixedHeight(height)
        
        radius = height // 2
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: {radius}px;
                background-color: {bg_color};
            }}
            QProgressBar::chunk {{
                border-radius: {radius}px;
                background-color: {fill_color};
            }}
        """)
    
    def set_colors(self, bg_color: str, fill_color: str):
        """
        Update the progress bar colors.
        
        Args:
            bg_color: New background color
            fill_color: New fill color
        """
        self.bg_color = bg_color
        self.fill_color = fill_color
        
        radius = self.bar_height // 2
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: {radius}px;
                background-color: {bg_color};
            }}
            QProgressBar::chunk {{
                border-radius: {radius}px;
                background-color: {fill_color};
            }}
        """)
