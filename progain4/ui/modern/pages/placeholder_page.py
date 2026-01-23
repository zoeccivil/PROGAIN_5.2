"""
Placeholder Page - Página genérica para secciones en desarrollo
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .. theme_config import COLORS, FONTS, SPACING
from ..components.clean_card import CleanCard


class PlaceholderPage(QWidget):
    """
    Página placeholder para secciones en desarrollo. 
    """
    
    def __init__(self, icon:  str, title: str, description: str, parent=None):
        """
        Inicializar página placeholder.
        
        Args:
            icon: Emoji/icono
            title: Título de la página
            description: Descripción
            parent: Widget padre
        """
        super().__init__(parent)
        
        self.icon = icon
        self.title = title
        self.description = description
        
        self.setup_ui()
    
    def setup_ui(self):
        """Crear la UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag. AlignCenter)
        layout.setContentsMargins(
            SPACING['3xl'],
            SPACING['3xl'],
            SPACING['3xl'],
            SPACING['3xl']
        )
        
        # Card central
        card = CleanCard(padding=SPACING['6xl'])
        card.setFixedSize(600, 400)
        
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(SPACING['xl'])
        
        # Icono grande
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 80px;
                background-color: transparent;
            }}
        """)
        icon_label.setAlignment(Qt. AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(FONTS['size_3xl'])
        title_font. setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_900']};
                background-color: transparent;
            }}
        """)
        title_label.setAlignment(Qt. AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_600']};
                font-size: {FONTS['size_lg']}px;
                background-color: transparent;
            }}
        """)
        desc_label. setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(desc_label)
        
        # Badge "Próximamente"
        badge = QLabel("🚧 Próximamente")
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['amber_100']};
                color: {COLORS['amber_700']};
                padding: 8px 16px;
                border-radius: 20px;
                font-size:  {FONTS['size_sm']}px;
                font-weight: bold;
            }}
        """)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(badge)
        
        layout. addWidget(card)