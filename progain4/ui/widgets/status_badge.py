"""
Status badge widget for PROGAIN 5.2

Provides status indicators for projects, works, and tasks.
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


class StatusBadge(QLabel):
    """
    Badge de estado para obras/proyectos.
    
    Estados disponibles: 
    - active: En Ejecución (verde)
    - delayed: Retrasado (rojo)
    - planning: Licitación (azul)
    - completed: Entregado (gris)
    - warning: Revisión (amarillo)
    """
    
    STYLES = {
        'active': {
            'bg': '#d1fae5',
            'text': '#047857',
            'border': '#a7f3d0',
            'label': 'En Ejecución'
        },
        'delayed': {
            'bg': '#ffe4e6',
            'text': '#be123c',
            'border': '#fecdd3',
            'label': 'Retrasado'
        },
        'planning': {
            'bg': '#dbeafe',
            'text': '#1d4ed8',
            'border': '#bfdbfe',
            'label': 'Licitación'
        },
        'completed': {
            'bg': '#f1f5f9',
            'text': '#475569',
            'border': '#e2e8f0',
            'label': 'Entregado'
        },
        'warning': {
            'bg': '#fef3c7',
            'text': '#b45309',
            'border': '#fde68a',
            'label': 'Revisión'
        }
    }
    
    def __init__(self, status='active', parent=None):
        """
        Initialize status badge.
        
        Args:
            status: Status type ('active', 'delayed', 'planning', 'completed', 'warning')
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_status = status
        self.set_status(status)
    
    def set_status(self, status):
        """
        Set the badge status and update styling.
        
        Args:
            status: Status type (one of STYLES keys)
        """
        self.current_status = status
        style = self.STYLES.get(status, self.STYLES['active'])
        
        self.setText(style['label'])
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {style['bg']};
                color: {style['text']};
                border: 1px solid {style['border']};
                border-radius: 12px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 700;
                text-transform: uppercase;
            }}
        """)
        
        self.adjustSize()
    
    def get_status(self) -> str:
        """
        Get the current status.
        
        Returns:
            Current status string
        """
        return self.current_status
