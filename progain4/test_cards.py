"""
Test del componente CleanCard
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.modern.components.clean_card import CleanCard, CleanCardAccent, CleanCardDark
from ui.modern.theme_config import COLORS, get_global_stylesheet


class TestCardsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test - CleanCard Components")
        self.setGeometry(100, 100, 1000, 600)
        
        # Contenedor principal
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("🎴 Test - CleanCard Components")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Grid de tarjetas
        grid = QGridLayout()
        grid.setSpacing(16)
        
        # === TARJETA BÁSICA ===
        card1 = CleanCard(padding=20)
        card1_layout = QVBoxLayout(card1)
        
        card1_title = QLabel("CleanCard Básica")
        card1_title. setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['slate_900']};")
        
        card1_text = QLabel("Esta es una tarjeta básica con fondo blanco,\nborde gris claro y sombra suave.")
        card1_text.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 13px;")
        card1_text.setWordWrap(True)
        
        card1_layout.addWidget(card1_title)
        card1_layout.addWidget(card1_text)
        
        grid.addWidget(card1, 0, 0)
        
        # === TARJETA CON ACENTO AZUL ===
        card2 = CleanCardAccent(accent_color=COLORS['blue_500'], padding=20)
        card2_layout = QVBoxLayout(card2)
        
        card2_title = QLabel("CleanCard con Acento")
        card2_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['slate_900']};")
        
        card2_text = QLabel("Borde izquierdo azul de 4px.\nUsada para cuentas bancarias.")
        card2_text.setStyleSheet(f"color: {COLORS['slate_500']}; font-size: 13px;")
        card2_text.setWordWrap(True)
        
        card2_layout.addWidget(card2_title)
        card2_layout.addWidget(card2_text)
        
        grid.addWidget(card2, 0, 1)
        
        # === TARJETA OSCURA ===
        card3 = CleanCardDark(padding=20)
        card3_layout = QVBoxLayout(card3)
        
        card3_title = QLabel("CleanCard Oscura")
        card3_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['white']};")
        
        card3_text = QLabel("Fondo oscuro (slate-900).\nUsada para totales o resúmenes importantes.")
        card3_text.setStyleSheet(f"color: {COLORS['slate_400']}; font-size: 13px;")
        card3_text.setWordWrap(True)
        
        card3_layout.addWidget(card3_title)
        card3_layout.addWidget(card3_text)
        
        grid. addWidget(card3, 0, 2)
        
        # === EJEMPLO DE CUENTA BANCARIA ===
        account_card = CleanCardAccent(accent_color=COLORS['blue_500'], padding=16)
        account_layout = QVBoxLayout(account_card)
        
        # Header con icono
        header_layout = QHBoxLayout()
        icon = QLabel("🏦")
        icon.setStyleSheet("font-size: 20px;")
        
        bank_info = QVBoxLayout()
        bank_name = QLabel("BBVA BANCOMER")
        bank_name.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLORS['slate_400']};")
        
        account_name = QLabel("Cuenta Maestra")
        account_name. setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLORS['slate_800']};")
        
        bank_info.addWidget(bank_name)
        bank_info.addWidget(account_name)
        
        header_layout. addWidget(icon)
        header_layout.addLayout(bank_info)
        header_layout.addStretch()
        
        # Saldo
        balance = QLabel("$1,250,000")
        balance.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {COLORS['slate_900']};")
        
        # Tipo
        account_type = QLabel("Disponible • Corriente")
        account_type. setStyleSheet(f"font-size: 10px; color: {COLORS['slate_400']};")
        
        account_layout. addLayout(header_layout)
        account_layout.addWidget(balance)
        account_layout.addWidget(account_type)
        
        grid.addWidget(account_card, 1, 0)
        
        # === TARJETA DE TOTAL ===
        total_card = CleanCardDark(padding=16)
        total_layout = QVBoxLayout(total_card)
        
        total_label = QLabel("CAPITAL TOTAL")
        total_label.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLORS['slate_400']};")
        
        total_amount = QLabel("$4,795,000")
        total_amount.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['white']};")
        
        status = QHBoxLayout()
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {COLORS['emerald_500']}; font-size: 10px;")
        status_text = QLabel("Estado Saludable")
        status_text.setStyleSheet(f"font-size: 11px; color: {COLORS['slate_400']};")
        
        status. addWidget(status_dot)
        status.addWidget(status_text)
        status.addStretch()
        
        total_layout.addWidget(total_label)
        total_layout.addWidget(total_amount)
        total_layout.addLayout(status)
        
        grid.addWidget(total_card, 1, 1)
        
        main_layout.addLayout(grid)
        main_layout.addStretch()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(get_global_stylesheet())
    
    window = TestCardsWindow()
    window.show()
    
    print("✅ Test de CleanCard iniciado")
    print("📊 Mostrando 5 variaciones de tarjetas...")
    
    sys.exit(app.exec())