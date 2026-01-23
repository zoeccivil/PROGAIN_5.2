"""
Header Widget Component

Top header bar with title, company selector, and action buttons.
Part of the Construction Manager Pro design system.

Author: GitHub Copilot Agent
Date: 2026-01-21
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, List


class HeaderWidget(QWidget):
    """
    Modern header bar for the main window.
    
    Features:
    - Page title display
    - Company/filter selector
    - Primary action button (+ Registrar)
    - Clean white background
    
    Signals:
        company_changed: Emitted when company selector changes (company_name: str)
        register_clicked: Emitted when register button is clicked
    """
    
    company_changed = pyqtSignal(str)
    register_clicked = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.companies = ["all", "Empresa 1", "Empresa 2", "Empresa 3"]
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the header UI"""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(16)
        
        # === LEFT: Title ===
        self.title_label = QLabel("Control de Obra")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #0f172a;")  # slate-900
        layout.addWidget(self.title_label)
        
        # Spacer
        layout.addStretch()
        
        # === CENTER/RIGHT: Company Selector ===
        company_label = QLabel("Empresa:")
        company_label.setStyleSheet("color: #64748b; font-size: 11pt;")  # slate-500
        layout.addWidget(company_label)
        
        self.company_combo = QComboBox()
        self.company_combo.addItems(self.companies)
        self.company_combo.setMinimumWidth(180)
        self.company_combo.setStyleSheet("""
            QComboBox {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11pt;
                color: #1e293b;
            }
            QComboBox:hover {
                border-color: #cbd5e1;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #64748b;
                margin-right: 4px;
            }
        """)
        self.company_combo.currentTextChanged.connect(self._on_company_changed)
        layout.addWidget(self.company_combo)
        
        # === RIGHT: Register Button ===
        self.register_button = QPushButton("+ Registrar")
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        self.register_button.clicked.connect(self.register_clicked.emit)
        layout.addWidget(self.register_button)
        
        # Widget styling
        self.setStyleSheet("""
            HeaderWidget {
                background-color: #ffffff;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        self.setObjectName("HeaderWidget")
    
    def set_title(self, title: str):
        """
        Set the header title.
        
        Args:
            title: Title text to display
        """
        self.title_label.setText(title)
    
    def set_companies(self, companies: List[str]):
        """
        Set the list of companies in the selector.
        
        Args:
            companies: List of company names
        """
        self.companies = companies
        current = self.company_combo.currentText()
        self.company_combo.clear()
        self.company_combo.addItems(companies)
        
        # Restore selection if possible
        if current in companies:
            self.company_combo.setCurrentText(current)
    
    def get_selected_company(self) -> str:
        """Get the currently selected company"""
        return self.company_combo.currentText()
    
    def _on_company_changed(self, company_name: str):
        """Handle company selector change"""
        self.company_changed.emit(company_name)
