"""
Clean Card Component

A simple, clean card container widget with rounded corners and subtle shadow.
Part of the Construction Manager Pro design system.

Author: GitHub Copilot Agent
Date: 2026-01-21
"""

from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from typing import Optional


class CleanCard(QWidget):
    """
    A clean card container widget.
    
    Features:
    - White background with rounded corners
    - Subtle drop shadow
    - Configurable padding
    - Minimal design
    """
    
    def __init__(
        self, 
        padding: int = 20,
        radius: int = 8,
        shadow: bool = True,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize clean card.
        
        Args:
            padding: Internal padding in pixels
            radius: Border radius in pixels
            shadow: Whether to show drop shadow
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.padding = padding
        self.radius = radius
        
        # Setup styling
        self._apply_style()
        
        # Add shadow effect if requested
        if shadow:
            self._add_shadow()
    
    def _apply_style(self):
        """Apply card styling"""
        self.setStyleSheet(f"""
            CleanCard {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: {self.radius}px;
                padding: {self.padding}px;
            }}
        """)
        self.setObjectName("CleanCard")
    
    def _add_shadow(self):
        """Add subtle drop shadow effect"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 15))  # Very subtle
        self.setGraphicsEffect(shadow)
    
    def set_padding(self, padding: int):
        """
        Update card padding.
        
        Args:
            padding: New padding in pixels
        """
        self.padding = padding
        self._apply_style()
    
    def set_radius(self, radius: int):
        """
        Update border radius.
        
        Args:
            radius: New radius in pixels
        """
        self.radius = radius
        self._apply_style()
