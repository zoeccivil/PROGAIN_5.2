"""
Account Card - Tarjeta de cuenta bancaria moderna
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .. theme_config import COLORS


class AccountCard(QFrame):
    """
    Tarjeta moderna para mostrar información de cuenta bancaria. 
    
    Señales: 
        clicked: Emitida cuando se hace click en la tarjeta
    """
    
    clicked = pyqtSignal(str)  # cuenta_id
    
    def __init__(self, account_data:  dict, parent=None):
        """
        Inicializar tarjeta de cuenta.
        
        Args:
            account_data:  Datos de la cuenta
            parent: Widget padre
        """
        super().__init__(parent)
        
        # Guardar datos
        self.account_data = account_data
        self.cuenta_id = str(account_data. get('id', ''))
        
        # Estilos de la tarjeta
        self. setStyleSheet(f"""
            AccountCard {{
                background-color:  white;
                border-radius:  12px;
                border:  1px solid {COLORS['slate_200']};
                padding: 20px;
            }}
            AccountCard:hover {{
                border-color: {COLORS['blue_300']};
            }}
        """)
        
        # Crear UI
        self.setup_ui()
        
        # Cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def setup_ui(self):
        """Crear la UI de la tarjeta"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # === HEADER:   Banco/Tipo ===
        header_layout = QHBoxLayout()
        
        # Icono del banco
        banco = self.account_data.get('banco', self.account_data.get('tipo', 'Banco'))
        banco_label = QLabel(self._get_bank_icon(banco))
        banco_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                background-color:  transparent;
            }}
        """)
        header_layout.addWidget(banco_label)
        
        # Nombre del banco
        banco_name = QLabel(banco)
        banco_font = QFont()
        banco_font.setPointSize(11)
        banco_font.setWeight(QFont.Weight.DemiBold)
        banco_name.setFont(banco_font)
        banco_name.setStyleSheet(f"color: {COLORS['slate_600']}; background-color: transparent;")
        header_layout.addWidget(banco_name)
        
        header_layout.addStretch()
        
        # Tipo de cuenta (badge)
        tipo_cuenta = self.account_data.get('tipo_cuenta', 'Disponible')
        tipo_badge = QLabel(tipo_cuenta)
        tipo_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['blue_100']};
                color: {COLORS['blue_700']};
                padding: 4px 10px;
                border-radius:   4px;
                font-size:   10px;
                font-weight: bold;
            }}
        """)
        header_layout.addWidget(tipo_badge)
        
        layout.addLayout(header_layout)
        
        # === NOMBRE DE LA CUENTA ===
        nombre = self.account_data.get('nombre', 'Sin nombre')
        nombre_label = QLabel(nombre)
        nombre_font = QFont()
        nombre_font.setPointSize(14)
        nombre_font.setWeight(QFont.Weight.Bold)
        nombre_label.setFont(nombre_font)
        nombre_label.setStyleSheet(f"color: {COLORS['slate_900']}; background-color: transparent;")
        layout.addWidget(nombre_label)
        
        # === NÚMERO DE CUENTA (si existe) ===
        numero = self.account_data.get('numero', '')
        if numero:
            numero_label = QLabel(f"****{numero[-4:]}" if len(numero) > 4 else numero)
            numero_label.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['slate_500']};
                    font-size: 12px;
                    font-family: 'Courier New', monospace;
                    background-color: transparent;
                }}
            """)
            layout.addWidget(numero_label)
        
        layout.addSpacing(8)
        
        # === SALDO ===
        saldo = self.account_data.get('saldo', 0)
        moneda = self.account_data. get('moneda', 'RD$')
        
        saldo_label = QLabel(self._format_currency(saldo, moneda))
        saldo_font = QFont()
        saldo_font.setPointSize(22)
        saldo_font. setWeight(QFont.Weight. Bold)
        saldo_label.setFont(saldo_font)
        
        # Color según saldo
        if saldo >= 0:
            color = COLORS['slate_900']
        else:
            color = COLORS['red_600']
        
        saldo_label.setStyleSheet(f"color: {color}; background-color: transparent;")
        layout.addWidget(saldo_label)
        
        # === FOOTER:   Estado ===
        activa = self.account_data.get('activa', True)
        estado_label = QLabel("● Activa" if activa else "○ Inactiva")
        estado_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['green_600'] if activa else COLORS['slate_400']};
                font-size:   11px;
                background-color: transparent;
            }}
        """)
        layout.addWidget(estado_label)
    
    def _get_bank_icon(self, banco: str) -> str:
        """Obtener emoji según banco"""
        banco_lower = banco.lower()
        
        icons = {
            'bbva': '🏦',
            'santander': '🏧',
            'banorte': '🏛️',
            'scotiabank': '🏦',
            'hsbc': '🏦',
            'citibanamex': '🏦',
            'banco': '🏦',
            'efectivo': '💵',
            'caja': '💰',
            'inversion': '📈',
        }
        
        for key, icon in icons.items():
            if key in banco_lower:
                return icon
        
        return '🏦'
    
    def _format_currency(self, amount:   float, currency: str = 'RD$') -> str:
        """Formatear monto como moneda"""
        try:
            if amount >= 0:
                return f"{currency} {amount: ,.2f}"
            else:
                return f"-{currency} {abs(amount):,.2f}"
        except:
            return f"{currency} 0.00"
    
    def mousePressEvent(self, event):
        """Handle click en la tarjeta"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self. cuenta_id)
        super().mousePressEvent(event)