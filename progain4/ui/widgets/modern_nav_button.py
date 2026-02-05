"""
Modern navigation button widget for PROGAIN 5.2

Provides a vertical button layout with icon and label,
featuring visual indicators for active/hover states.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QCursor


class ModernNavButton(QWidget):
    """
    Botón de navegación moderno con indicador visual de estado activo.
    
    Diseño:
    - Layout vertical: Icono (arriba) + Label (abajo)
    - Estado inactivo: texto slate_400, sin fondo
    - Estado hover: fondo slate_800 (semi-transparente)
    - Estado activo: fondo slate_800, texto white, barra lateral izquierda azul
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, icon_path: str, label_text: str, parent=None):
        """
        Initialize modern navigation button.
        
        Args:
            icon_path: Path to icon image file (or empty string for emoji/text)
            label_text: Text label to display below icon
            parent: Parent widget
        """
        super().__init__(parent)
        self.is_active = False
        self.icon_path = icon_path
        self.label_text = label_text
        self.setup_ui(icon_path, label_text)
    
    def setup_ui(self, icon_path, label_text):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icono
        self.icon_label = QLabel()
        if icon_path:
            # Try to load image, fallback to text if fails
            try:
                pixmap = QPixmap(icon_path).scaled(
                    20, 20, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                if not pixmap.isNull():
                    self.icon_label.setPixmap(pixmap)
                else:
                    # Fallback to emoji if image doesn't load
                    self.icon_label.setText(self._get_fallback_icon(label_text))
                    self.icon_label.setStyleSheet("font-size: 20px;")
            except Exception:
                # Fallback to emoji
                self.icon_label.setText(self._get_fallback_icon(label_text))
                self.icon_label.setStyleSheet("font-size: 20px;")
        else:
            # Use emoji fallback
            self.icon_label.setText(self._get_fallback_icon(label_text))
            self.icon_label.setStyleSheet("font-size: 20px;")
            
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Texto
        self.text_label = QLabel(label_text)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet("font-size: 10px; font-weight: 500;")
        self.text_label.setWordWrap(True)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        
        self.setFixedHeight(70)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.update_style()
    
    def _get_fallback_icon(self, label: str) -> str:
        """Get fallback emoji icon based on label text"""
        label_lower = label.lower()
        if 'panel' in label_lower or 'dashboard' in label_lower:
            return "📊"
        elif 'obra' in label_lower or 'proyecto' in label_lower or 'building' in label_lower:
            return "🏗️"
        elif 'caja' in label_lower or 'wallet' in label_lower or 'transaction' in label_lower:
            return "💰"
        elif 'reporte' in label_lower or 'report' in label_lower or 'chart' in label_lower:
            return "📈"
        else:
            return "📋"
    
    def set_active(self, active: bool):
        """
        Set the active state of the button.
        
        Args:
            active: True to set as active, False for inactive
        """
        self.is_active = active
        self.update_style()
    
    def update_style(self):
        """Update the button style based on active state"""
        if self.is_active:
            self.setStyleSheet("""
                ModernNavButton {
                    background-color: #1e293b;
                    border-radius: 12px;
                    border-left: 4px solid #3b82f6;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                ModernNavButton {
                    background-color: transparent;
                    border-radius: 12px;
                }
                ModernNavButton:hover {
                    background-color: rgba(30, 41, 59, 0.5);
                }
                QLabel {
                    color: #94a3b8;
                }
            """)
    
    def mousePressEvent(self, event):
        """Handle mouse press event"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
