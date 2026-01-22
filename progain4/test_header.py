"""
Test del componente Header
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.modern.widgets.header import Header
from ui.modern.components.clean_card import CleanCard
from ui.modern.theme_config import COLORS, get_minimal_stylesheet


class TestHeaderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test - Header Component")
        self.setGeometry(100, 100, 1200, 600)
        
        # Widget central
        central = QWidget()
        central.setStyleSheet(f"background-color: {COLORS['slate_50']};")
        self.setCentralWidget(central)
        
        # Layout vertical
        main_layout = QVBoxLayout(central)
        main_layout. setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # === HEADER ===
        self.header = Header()
        self.header.company_changed.connect(self.on_company_changed)
        self.header.register_clicked.connect(self.on_register_clicked)
        main_layout.addWidget(self. header)
        
        # === CONTENIDO ===
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        # Título
        title = QLabel("✅ Test - Header Component")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']};")
        content_layout.addWidget(title)
        
        # Status card
        self.status_card = CleanCard(padding=20)
        status_layout = QVBoxLayout(self. status_card)
        
        self.status_label = QLabel("🏢 Empresa: Vista Global (Todas)")
        status_font = QFont()
        status_font.setPointSize(14)
        status_font.setWeight(QFont.Weight.Bold)
        self.status_label. setFont(status_font)
        self.status_label.setStyleSheet(f"color: {COLORS['blue_700']};")
        
        self.clicks_label = QLabel("Clicks en Registrar: 0")
        self.clicks_label.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 13px;")
        
        self.changes_label = QLabel("Cambios de empresa: 0")
        self.changes_label.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 13px;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.clicks_label)
        status_layout.addWidget(self.changes_label)
        
        content_layout.addWidget(self.status_card)
        
        # Instrucciones
        instructions = CleanCard(padding=24)
        instructions_layout = QVBoxLayout(instructions)
        
        instructions_title = QLabel("🧭 Componente Header Completo")
        instructions_title. setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['slate_900']};")
        
        instructions_text = QLabel(
            "<b>Características: </b><br>"
            "• Altura fija de 64px<br>"
            "• Título dinámico (izquierda)<br>"
            "• Selector de empresa con icono (centro)<br>"
            "• Botón '+ Registrar' (derecha)<br>"
            "• Fondo blanco con borde inferior<br>"
            "• Señales: company_changed, register_clicked<br><br>"
            "<b>Prueba:</b><br>"
            "• Cambia la empresa en el selector<br>"
            "• Haz click en el botón '+ Registrar'"
        )
        instructions_text.setStyleSheet(f"color: {COLORS['slate_700']}; font-size: 13px; line-height: 1.8;")
        instructions_text.setWordWrap(True)
        
        instructions_layout.addWidget(instructions_title)
        instructions_layout.addWidget(instructions_text)
        
        content_layout.addWidget(instructions)
        content_layout.addStretch()
        
        main_layout.addWidget(content)
        
        # Contadores
        self.click_counter = 0
        self.change_counter = 0
    
    def on_company_changed(self, company_id: str):
        """Callback cuando cambia la empresa"""
        self. change_counter += 1
        
        company_names = {
            'vista_global_(todas)': 'Vista Global (Todas)',
            'constructora_roca_s. a.': 'Constructora Roca S.A.',
            'inmobiliaria_horizonte': 'Inmobiliaria Horizonte',
        }
        
        company_name = company_names.get(company_id, company_id)
        
        print(f"🏢 Cambio #{self.change_counter}: {company_name}")
        
        self.status_label.setText(f"🏢 Empresa: {company_name}")
        self.changes_label.setText(f"Cambios de empresa: {self. change_counter}")
    
    def on_register_clicked(self):
        """Callback cuando se hace click en Registrar"""
        self.click_counter += 1
        print(f"➕ Click en Registrar #{self.click_counter}")
        self.clicks_label.setText(f"Clicks en Registrar: {self.click_counter}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(get_minimal_stylesheet())
    
    window = TestHeaderWindow()
    window.show()
    
    print("=" * 70)
    print("✅ Test del Header iniciado")
    print("=" * 70)
    
    sys.exit(app.exec())