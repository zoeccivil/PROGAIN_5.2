"""
Modern Navigation Button Component

A clean, minimal navigation button for sidebar menus with modern aesthetics.
Part of the Construction Manager Pro design system.

Author: GitHub Copilot Agent
Date: 2026-01-21
"""

from PyQt6.QtWidgets import QPushButton, QWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from typing import Optional


class ModernNavButton(QPushButton):
    """
    Modern navigation button with clean aesthetics.
    
    Features:
    - Minimal design with hover and active states
    - Icon + text or text only
    - Smooth transitions
    - Dark theme optimized
    """
    
    def __init__(self, icon: str = "", text: str = "", parent: Optional[QWidget] = None):
        """
        Initialize modern navigation button.
        
        Args:
            icon: Icon text or emoji (e.g., "🏗️" or "")
            text: Button text label
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.icon_text = icon
        self.label_text = text
        self._is_active = False
        
        # Setup button
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(64, 64)
        
        # Set text
        display_text = f"{icon}\n{text}" if icon and text else (text or icon)
        self.setText(display_text)
        
        # Font
        font = QFont()
        font.setPointSize(9)
        self.setFont(font)
        
        # Apply default styling
        self._apply_style()
    
    def set_active(self, active: bool):
        """Set the active state of the button"""
        self._is_active = active
        self.setChecked(active)
        self._apply_style()
    
    def _apply_style(self):
        """Apply styling based on current state"""
        # Colors for dark sidebar
        bg_default = "transparent"
        bg_hover = "rgba(255, 255, 255, 0.05)"
        bg_active = "rgba(59, 130, 246, 0.15)"  # blue-500 with opacity
        
        text_default = "#94a3b8"  # slate-400
        text_hover = "#e2e8f0"    # slate-200
        text_active = "#3b82f6"   # blue-500
        
        border_active = "#3b82f6" # blue-500
        
        if self._is_active:
            bg = bg_active
            text = text_active
            border = f"border-left: 3px solid {border_active};"
        else:
            bg = bg_default
            text = text_default
            border = "border-left: 3px solid transparent;"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                border: none;
                {border}
                border-radius: 8px;
                padding: 8px;
                text-align: center;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
                color: {text_hover};
            }}
            QPushButton:pressed {{
                background-color: {bg_active};
                color: {text_active};
            }}
        """)
    
    def sizeHint(self) -> QSize:
        """Return the recommended size"""
        return QSize(64, 64)
    
    def minimumSizeHint(self) -> QSize:
        """Return the minimum size"""
        return QSize(64, 64)
