"""
Header - Barra superior moderna

Componente de header con:
- Título dinámico
- Selector de empresa (multi-empresa)
- Botón "+ Registrar"
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .. components.icon_manager import icon_manager
from ..theme_config import COLORS, BORDER


class Header(QWidget):
    """
    Header moderno con título, selector de empresa y acciones. 
    
    Señales:
        company_changed(str): Emitida cuando cambia la empresa seleccionada
        register_clicked(): Emitida cuando se hace click en "+ Registrar"
    """
    
    company_changed = pyqtSignal(str)  # ID de la empresa
    register_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_title = "Control de Obra"
        self.companies = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Crear la UI del header"""
        
        # Altura fija
        self.setFixedHeight(64)
        
        # Estilo del header
        self.setStyleSheet(f"""
            Header {{
                background-color: {COLORS['white']};
                border-bottom: 1px solid {COLORS['slate_200']};
            }}
        """)
        
        # Layout horizontal
        layout = QHBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 0, 24, 0)
        
        # === TÍTULO (IZQUIERDA) ===
        self.title_label = QLabel(self.current_title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_900']};
                background-color: transparent;
            }}
        """)
        
        layout.addWidget(self.title_label)
        
        # === SELECTOR DE EMPRESA (CENTRO-IZQUIERDA) ===
        company_container = QWidget()
        company_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['slate_100']};
                border: 1px solid {COLORS['slate_200']};
                border-radius:  {BORDER['radius_sm']}px;
                padding: 4px 8px;
            }}
        """)
        
        company_layout = QHBoxLayout(company_container)
        company_layout.setContentsMargins(8, 4, 8, 4)
        company_layout.setSpacing(8)
        
        # Icono de empresa
        company_icon = QLabel()
        icon_pixmap = icon_manager.get_pixmap('building', COLORS['slate_600'], 16)
        company_icon.setPixmap(icon_pixmap)
        company_icon.setStyleSheet("background-color: transparent;")
        company_layout.addWidget(company_icon)
        
        # ComboBox de empresas
        self.company_selector = QComboBox()
        self.company_selector.addItems([
            "Vista Global (Todas)",
            "Constructora Roca S.A.",
            "Inmobiliaria Horizonte"
        ])
        
        company_font = QFont()
        company_font.setPointSize(12)
        company_font.setWeight(QFont.Weight.DemiBold)
        self.company_selector.setFont(company_font)
        
        self.company_selector.setStyleSheet(f"""
            QComboBox {{
                background-color:  transparent;
                border: none;
                color: {COLORS['slate_700']};
                min-width: 200px;
                padding: 4px 8px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {COLORS['slate_600']};
                width: 0px;
                height: 0px;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
                selection-background-color: {COLORS['slate_100']};
                padding: 4px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                min-height: 32px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS['slate_100']};
            }}
        """)
        
        self.company_selector.currentTextChanged.connect(self._on_company_changed)
        
        company_layout.addWidget(self.company_selector)
        
        layout.addWidget(company_container)
        layout.addStretch()  # Empujar botón a la derecha
        
        # === BOTÓN REGISTRAR (DERECHA) ===
        self.register_button = QPushButton("+ Registrar")
        
        button_font = QFont()
        button_font.setPointSize(13)
        button_font.setWeight(QFont.Weight.DemiBold)
        self.register_button.setFont(button_font)
        
        self.register_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['slate_900']};
                color: {COLORS['white']};
                border: none;
                border-radius: {BORDER['radius_sm']}px;
                padding: 10px 20px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['slate_800']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['slate_700']};
            }}
        """)
        
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button. clicked.connect(self.register_clicked. emit)
        
        layout. addWidget(self.register_button)
    
    def set_title(self, title:  str):
        """
        Cambiar el título del header.
        
        Args:
            title: Nuevo título
        """
        self. current_title = title
        self.title_label.setText(title)
    
    def set_companies(self, companies: list):
        """
        Establecer lista de empresas disponibles.
        
        Args:
            companies: Lista de tuplas (id, nombre)
                      Ej: [('all', 'Vista Global'), ('c1', 'Constructora Roca')]
        """
        self.companies = companies
        self.company_selector.clear()
        
        for company_id, company_name in companies:
            self.company_selector.addItem(company_name, company_id)
    
    def _on_company_changed(self, company_name: str):
        """Callback interno cuando cambia la empresa"""
        # Obtener el ID de la empresa (userData)
        index = self.company_selector.currentIndex()
        company_id = self.company_selector.itemData(index)
        
        if company_id is None:
            company_id = company_name. lower().replace(' ', '_')
        
        print(f"🏢 Empresa cambiada: {company_name} (ID: {company_id})")
        self.company_changed. emit(company_id)