"""
CleanCard - Componente de tarjeta moderna

Réplica exacta del componente CleanCard de React: 
- Fondo blanco
- Borde gris claro (slate-200)
- Border radius 12px (rounded-xl)
- Sombra suave
- Padding configurable

Uso:
    card = CleanCard(padding=16)
    layout = QVBoxLayout(card)
    layout.addWidget(QLabel("Contenido"))
"""

from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from .. theme_config import COLORS, BORDER


class CleanCard(QFrame):
    """
    Tarjeta blanca moderna con sombra y bordes redondeados. 
    
    Equivalente a: 
    ```jsx
    <div className="bg-white border border-slate-200 shadow-sm rounded-xl">
        {children}
    </div>
    ```
    """
    
    def __init__(self, padding:  int = 16, parent=None):
        """
        Args:
            padding: Padding interno en pixels (default: 16)
            parent:  Widget padre
        """
        super().__init__(parent)
        self.padding = padding
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar estilos y efectos de la tarjeta"""
        
        # Aplicar estilo QSS
        self.setStyleSheet(f"""
            CleanCard {{
                background-color: {COLORS['white']};
                border:  1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius']}px;
                padding: {self.padding}px;
            }}
        """)
        
        # Agregar sombra suave (shadow-sm)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(4)        # Radio de difuminado
        shadow.setXOffset(0)           # Sin offset horizontal
        shadow.setYOffset(1)           # 1px hacia abajo
        shadow.setColor(QColor(0, 0, 0, 13))  # Negro con ~5% opacidad (13/255)
        
        self.setGraphicsEffect(shadow)
        
        # Permitir que el contenido se ajuste automáticamente
        self. setFrameShape(QFrame.Shape. NoFrame)


class CleanCardAccent(QFrame):
    """
    Tarjeta con borde izquierdo de color (acento).
    
    Usada para las tarjetas de cuentas bancarias.
    
    Equivalente a:
    ```jsx
    <div className="bg-white border border-slate-200 shadow-sm rounded-xl border-l-4 border-l-blue-500">
        {children}
    </div>
    ```
    """
    
    def __init__(self, accent_color: str = None, padding: int = 16, parent=None):
        """
        Args:
            accent_color: Color del borde izquierdo (hex). Default: blue_500
            padding: Padding interno en pixels
            parent: Widget padre
        """
        super().__init__(parent)
        self.accent_color = accent_color or COLORS['blue_500']
        self.padding = padding
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar estilos y efectos"""
        
        # Estilo con borde izquierdo de color
        self.setStyleSheet(f"""
            CleanCardAccent {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_200']};
                border-left: 4px solid {self.accent_color};
                border-radius: {BORDER['radius']}px;
                padding:  {self.padding}px;
            }}
        """)
        
        # Agregar sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(4)
        shadow.setXOffset(0)
        shadow.setYOffset(1)
        shadow.setColor(QColor(0, 0, 0, 13))
        
        self.setGraphicsEffect(shadow)
        
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Cursor pointer para indicar que es clickeable
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class CleanCardDark(QFrame):
    """
    Tarjeta con fondo oscuro (para totales o datos destacados).
    
    Equivalente a:
    ```jsx
    <div className="bg-slate-900 text-white border-none rounded-xl shadow-sm">
        {children}
    </div>
    ```
    """
    
    def __init__(self, padding: int = 16, parent=None):
        """
        Args:
            padding: Padding interno en pixels
            parent: Widget padre
        """
        super().__init__(parent)
        self.padding = padding
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar estilos oscuros"""
        
        self.setStyleSheet(f"""
            CleanCardDark {{
                background-color: {COLORS['slate_900']};
                border: none;
                border-radius: {BORDER['radius']}px;
                padding: {self.padding}px;
            }}
            CleanCardDark QLabel {{
                color: {COLORS['white']};
            }}
        """)
        
        # Sombra más pronunciada para tarjeta oscura
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 26))  # ~10% opacidad
        
        self.setGraphicsEffect(shadow)
        
        self.setFrameShape(QFrame.Shape.NoFrame)