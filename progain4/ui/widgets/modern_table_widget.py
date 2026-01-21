"""
Modern table widget for PROGAIN 5.2

Provides styled table with clean, modern appearance.
"""

from PyQt6.QtWidgets import QTableWidget, QHeaderView
from PyQt6.QtCore import Qt


class ModernTableWidget(QTableWidget):
    """
    QTableWidget con estilo moderno y limpio.
    
    Características:
    - Sin líneas de grid verticales
    - Headers con fondo gris claro
    - Filas con separador sutil
    - Hover state
    - Padding generoso
    - Selection de filas completas
    """
    
    def __init__(self, parent=None):
        """
        Initialize modern table widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_style()
    
    def setup_style(self):
        """Setup the table styling and behavior"""
        # Table behavior
        self.setShowGrid(False)
        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.verticalHeader().setVisible(False)
        
        # Header horizontal
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Styling
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                font-size: 12px;
                color: #475569;
            }
            QTableWidget::item {
                border-bottom: 1px solid #f1f5f9;
                padding: 12px 8px;
            }
            QTableWidget::item:hover {
                background-color: rgba(248, 250, 252, 0.8);
            }
            QTableWidget::item:selected {
                background-color: #f1f5f9;
                color: #0f172a;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #64748b;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
    
    def set_header_labels(self, labels: list):
        """
        Set column headers with proper count.
        
        Args:
            labels: List of header label strings
        """
        self.setColumnCount(len(labels))
        self.setHorizontalHeaderLabels(labels)
