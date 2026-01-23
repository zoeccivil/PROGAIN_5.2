"""
Test del Account Service y Account Card
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.modern.components.account_card import AccountCard
from ui.modern.components.clean_card import CleanCard
from ui.modern.theme_config import COLORS, get_minimal_stylesheet
from services.account_service import AccountService
from services.firebase_client import FirebaseClient
from services.config import ConfigManager


class TestAccountServiceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test - Account Service")
        self.setGeometry(100, 100, 1200, 800)
        
        # Inicializar Firebase
        config = ConfigManager()
        cred_path, bucket = config.get_firebase_config()
        
        self.firebase = FirebaseClient()
        if not self.firebase.initialize(cred_path, bucket):
            print("Error:  No se pudo conectar a Firebase")
            sys.exit(1)
        
        # Obtener primer proyecto
        proyectos = self.firebase.get_proyectos()
        if not proyectos:
            print("Error: No hay proyectos")
            sys.exit(1)
        
        if hasattr(proyectos[0], 'id'):
            proyecto_id = str(proyectos[0].id)
        else:
            proyecto_id = str(proyectos[0].get('id'))
        
        # Inicializar servicio
        self.account_service = AccountService(self. firebase, proyecto_id)
        
        self.setup_ui()
        self.load_accounts()
    
    def setup_ui(self):
        """Crear UI"""
        central = QWidget()
        central. setStyleSheet(f"background-color: {COLORS['slate_50']};")
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Título
        title = QLabel("🏦 Test - Account Service")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setWeight(QFont. Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']};")
        layout.addWidget(title)
        
        # Resumen
        self.summary_card = CleanCard(padding=20)
        self.summary_layout = QVBoxLayout(self. summary_card)
        layout.addWidget(self.summary_card)
        
        # Scroll area para cuentas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        scroll_content = QWidget()
        self.accounts_layout = QVBoxLayout(scroll_content)
        self.accounts_layout.setSpacing(16)
        self.accounts_layout.setAlignment(Qt.AlignmentFlag. AlignTop)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
    
    def load_accounts(self):
        """Cargar cuentas desde el servicio"""
        # Obtener resumen
        summary = self.account_service.get_accounts_summary()
        
        # Mostrar resumen
        summary_title = QLabel(f"📊 Resumen de Cuentas")
        summary_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['slate_900']};")
        self.summary_layout.addWidget(summary_title)
        
        summary_text = QLabel(
            f"Total de cuentas: {summary['total_cuentas']}\n"
            f"Saldo total: RD$ {summary['saldo_total']: ,.2f}\n"
            f"Cuentas activas: {summary['cuentas_activas']}"
        )
        summary_text.setStyleSheet(f"color: {COLORS['slate_700']}; font-size: 13px;")
        self.summary_layout.addWidget(summary_text)
        
        # Obtener cuentas
        cuentas = self.account_service.get_all_accounts()
        
        print(f"\n✅ Cargadas {len(cuentas)} cuentas")
        
        # Crear tarjetas
        for cuenta in cuentas: 
            card = AccountCard(cuenta)
            card.clicked.connect(self.on_account_clicked)
            self.accounts_layout.addWidget(card)
        
        print("✅ Tarjetas creadas")
    
    def on_account_clicked(self, cuenta_id:  str):
        """Callback cuando se hace click en una cuenta"""
        print(f"🖱️ Click en cuenta: {cuenta_id}")
        
        cuenta = self.account_service.get_account_by_id(cuenta_id)
        if cuenta:
            print(f"   Nombre: {cuenta['nombre']}")
            print(f"   Saldo: RD$ {cuenta['saldo']:,.2f}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(get_minimal_stylesheet())
    
    window = TestAccountServiceWindow()
    window.show()
    
    print("=" * 70)
    print("✅ Test Account Service iniciado")
    print("=" * 70)
    
    sys.exit(app.exec())