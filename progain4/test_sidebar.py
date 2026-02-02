"""
Test del componente Sidebar completo
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, 
    QVBoxLayout, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.modern.widgets.sidebar import Sidebar
from ui.modern.theme_config import get_minimal_stylesheet, COLORS


class TestSidebarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test - Sidebar Component")
        self.setGeometry(100, 100, 900, 600)
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout horizontal
        main_layout = QHBoxLayout(central)
        main_layout. setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # === SIDEBAR ===
        self.sidebar = Sidebar()
        self.sidebar.navigation_changed.connect(self.on_navigation_changed)
        main_layout.addWidget(self. sidebar)
        
        # === ÁREA DE CONTENIDO ===
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['slate_50']};")
        
        content_layout = QVBoxLayout(content)
        content_layout. setSpacing(20)
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        # Título
        title = QLabel("✅ Test - Sidebar Completo")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']};")
        content_layout.addWidget(title)
        
        # Status
        self.status_label = QLabel("📍 Página activa: Panel (dashboard)")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['blue_50']};
                color: {COLORS['blue_700']};
                padding: 20px;
                border-radius:  12px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid {COLORS['blue_200']};
            }}
        """)
        content_layout.addWidget(self.status_label)
        
        # Instrucciones
        instructions = QLabel(
            "<b>🧭 Componente Sidebar Completo</b><br><br>"
            "Este es el sidebar final que se usará en la aplicación. <br><br>"
            "<b>Características:</b><br>"
            "• Logo con icono hard-hat SVG<br>"
            "• 5 botones de navegación con iconos Lucide<br>"
            "• Botón settings con hover effect<br>"
            "• Avatar circular<br>"
            "• Señal navigation_changed(str) emitida al cambiar<br>"
            "• Ancho fijo de 100px<br>"
            "• Fondo slate-900 oscuro<br><br>"
            "<b>Prueba haciendo click en los botones! </b>"
        )
        instructions.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['white']};
                color: {COLORS['slate_700']};
                padding: 24px;
                border-radius:  12px;
                font-size: 14px;
                line-height: 1.8;
                border: 1px solid {COLORS['slate_200']};
            }}
        """)
        instructions.setWordWrap(True)
        content_layout.addWidget(instructions)
        
        # Contador
        self.click_counter = 0
        self.counter_label = QLabel(f"Total de navegaciones: {self.click_counter}")
        self.counter_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['slate_100']};
                color: {COLORS['slate_700']};
                padding: 16px;
                border-radius:  8px;
                font-size: 14px;
                font-weight: 600;
            }}
        """)
        content_layout.addWidget(self. counter_label)
        
        content_layout.addStretch()
        
        main_layout.addWidget(content)
    
    def on_navigation_changed(self, page_id: str):
        """Callback cuando cambia la navegación"""
        self.click_counter += 1
        
        page_names = {
            'dashboard': 'Panel',
            'projects':  'Obras',
            'transactions': 'Transacciones',
            'cash': 'Caja',
            'reports': 'Reportes',
        }
        
        page_name = page_names.get(page_id, page_id)
        
        print(f"🔄 Navegación #{self.click_counter}: {page_id} → {page_name}")
        
        self.status_label.setText(f"📍 Página activa: {page_name} ({page_id})")
        self.counter_label.setText(f"Total de navegaciones: {self.click_counter}")


if __name__ == "__main__": 
    app = QApplication(sys.argv)
    app.setStyleSheet(get_minimal_stylesheet())  # ← Usar el minimalista
    
    window = TestSidebarWindow()
    window.show()
    
    print("=" * 70)
    print("✅ Test del Sidebar Completo iniciado")
    print("=" * 70)
    print("🧭 Haz click en los botones para navegar")
    print("📊 Observa la señal navigation_changed en la consola")
    print("=" * 70)
    
    sys.exit(app.exec())