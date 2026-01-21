"""
Header widget for PROGAIN 5.2

Provides top navigation bar with company selector and action buttons.
"""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal


class HeaderWidget(QFrame):
    """
    Barra superior con selector de empresa y acciones globales.
    
    Características:
    - Altura fija: 64px
    - Fondo: white
    - Borde inferior: 1px solid slate_200
    
    Signals:
        company_changed: Emitted when company selection changes (str: company name)
        register_clicked: Emitted when register button is clicked
    """
    
    company_changed = pyqtSignal(str)  # Emite cuando cambia la empresa seleccionada
    register_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialize header widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        self.setFixedHeight(64)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)
        
        # SECCIÓN IZQUIERDA
        left_layout = QHBoxLayout()
        left_layout.setSpacing(16)
        
        # Título dinámico
        self.title_label = QLabel("Control de Obra")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a;")
        left_layout.addWidget(self.title_label)
        
        # Selector de Empresa
        company_container = QFrame()
        company_container.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
            }
        """)
        
        company_layout = QHBoxLayout(company_container)
        company_layout.setContentsMargins(8, 0, 8, 0)
        company_layout.setSpacing(8)
        
        # Company selector dropdown
        self.company_selector = QComboBox()
        self.company_selector.setObjectName("companySwitcher")
        self.company_selector.addItems([
            "Vista Global (Todas)",
            "Constructora Roca S.A.",
            "Inmobiliaria Horizonte"
        ])
        self.company_selector.setStyleSheet("""
            QComboBox#companySwitcher {
                background-color: transparent;
                border: none;
                font-size: 13px;
                font-weight: 600;
                color: #334155;
                min-width: 180px;
                padding: 4px;
            }
            QComboBox#companySwitcher::drop-down {
                border: none;
            }
            QComboBox#companySwitcher QAbstractItemView {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                selection-background-color: #f1f5f9;
                padding: 4px;
            }
        """)
        self.company_selector.currentTextChanged.connect(self.company_changed.emit)
        
        company_layout.addWidget(self.company_selector)
        left_layout.addWidget(company_container)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        # SECCIÓN DERECHA
        right_layout = QHBoxLayout()
        right_layout.setSpacing(12)
        
        # Botón Registrar
        self.register_button = QPushButton("+ Registrar")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #0f172a;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1e293b;
            }
            QPushButton:pressed {
                background-color: #334155;
            }
        """)
        self.register_button.clicked.connect(self.register_clicked.emit)
        
        right_layout.addWidget(self.register_button)
        layout.addLayout(right_layout)
    
    def set_title(self, title: str):
        """
        Update the header title.
        
        Args:
            title: New title text
        """
        self.title_label.setText(title)
    
    def set_companies(self, companies: list):
        """
        Update the company selector with new list of companies.
        
        Args:
            companies: List of company names
        """
        current = self.company_selector.currentText()
        self.company_selector.clear()
        self.company_selector.addItems(companies)
        
        # Try to restore previous selection
        index = self.company_selector.findText(current)
        if index >= 0:
            self.company_selector.setCurrentIndex(index)
    
    def get_selected_company(self) -> str:
        """
        Get the currently selected company.
        
        Returns:
            Selected company name
        """
        return self.company_selector.currentText()
