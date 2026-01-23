"""
Test de la MainWindow completa
"""
import sys
from PyQt6.QtWidgets import QApplication

from ui.modern.main_window import MainWindow
from ui.modern.theme_config import get_minimal_stylesheet


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Aplicar stylesheet minimalista
    app.setStyleSheet(get_minimal_stylesheet())
    
    # Crear ventana principal
    window = MainWindow()
    window.show()
    
    print("=" * 70)
    print("🚀 PROGAIN 5.2 - Construction Manager Pro")
    print("=" * 70)
    print("✅ Ventana principal cargada")
    print("🧭 Haz click en los botones del sidebar para navegar")
    print("🏢 Cambia la empresa en el header")
    print("➕ Haz click en '+ Registrar' para probar el diálogo")
    print("=" * 70)
    
    sys.exit(app.exec())