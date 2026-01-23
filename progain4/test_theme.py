"""
Test básico del tema - Verificar que los colores funcionan
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea
from ui.modern.theme_config import COLORS, get_global_stylesheet

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test - Construction Manager Pro Colors")
        self.setGeometry(100, 100, 500, 700)
        
        # Widget central con scroll
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout. setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Contenedor de colores
        colors_widget = QWidget()
        layout = QVBoxLayout(colors_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("🎨 Paleta de Colores - Construction Manager Pro")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight:  bold;
                color: {COLORS['slate_900']};
                padding: 10px;
                background-color: {COLORS['white']};
                border-radius:  8px;
            }}
        """)
        layout.addWidget(title)
        
        # Mostrar todos los colores
        for name, hex_color in COLORS.items():
            # Determinar color de texto (blanco para fondos oscuros)
            text_color = 'white' if any(dark in name for dark in ['900', '800', '700', '600']) else COLORS['slate_900']
            
            label = QLabel(f"<b>{name}</b>:  {hex_color}")
            label.setStyleSheet(f"""
                QLabel {{
                    background-color: {hex_color};
                    padding: 15px;
                    border-radius: 8px;
                    color: {text_color};
                    font-size: 13px;
                    border: 1px solid {COLORS['slate_200']};
                }}
            """)
            layout.addWidget(label)
        
        scroll.setWidget(colors_widget)
        main_layout.addWidget(scroll)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Aplicar stylesheet global
    app.setStyleSheet(get_global_stylesheet())
    
    window = TestWindow()
    window.show()
    
    print("✅ Test iniciado correctamente")
    print("📊 Mostrando paleta de colores...")
    
    sys.exit(app.exec())