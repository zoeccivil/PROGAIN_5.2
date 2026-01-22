"""
Test del componente ModernNavButton
Muestra un sidebar simulado con 4 botones de navegación usando iconos Unicode
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.modern.components.nav_button import ModernNavButton
from ui.modern.theme_config import COLORS, get_global_stylesheet


class TestNavButtonsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test - ModernNavButton Component")
        self.setGeometry(100, 100, 900, 600)
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout horizontal principal
        main_layout = QHBoxLayout(central)
        main_layout. setSpacing(40)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # === SIDEBAR SIMULADO ===
        sidebar = QFrame()
        sidebar.setFixedWidth(100)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['slate_900']};
                border-radius: 12px;
            }}
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout. setSpacing(16)
        sidebar_layout.setContentsMargins(8, 16, 8, 16)
        sidebar_layout.setAlignment(Qt. AlignmentFlag.AlignTop)
        
        # Logo
        logo = QLabel("⬢")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['blue_600']};
                border-radius: 8px;
                font-size: 28px;
                padding: 8px;
                color: white;
                font-weight: 300;
            }}
        """)
        logo.setFixedSize(48, 48)
        sidebar_layout.addWidget(logo, alignment=Qt.AlignmentFlag. AlignHCenter)
        
        sidebar_layout.addSpacing(16)
        
        # Botones de navegación con iconos SVG (5 botones ahora)
        self.btn_panel = ModernNavButton("dashboard", "Panel")
        self.btn_obras = ModernNavButton("building", "Obras")
        self.btn_transacciones = ModernNavButton("transactions", "Trans")  # ← NUEVO
        self.btn_caja = ModernNavButton("wallet", "Caja")
        self.btn_reportes = ModernNavButton("chart", "Reportes")
        
        self.nav_buttons = [
            self.btn_panel,
            self.btn_obras,
            self.btn_transacciones,  # ← NUEVO
            self.btn_caja,
            self.btn_reportes
        ]
        
        # Conectar señales
        self.btn_panel.clicked.connect(lambda: self.on_nav_click(self.btn_panel, "Panel"))
        self.btn_obras.clicked.connect(lambda: self.on_nav_click(self.btn_obras, "Obras"))
        self.btn_transacciones.clicked.connect(lambda: self.on_nav_click(self.btn_transacciones, "Transacciones"))  # ← NUEVO
        self.btn_caja.clicked. connect(lambda: self.on_nav_click(self.btn_caja, "Caja"))
        self.btn_reportes.clicked.connect(lambda: self.on_nav_click(self.btn_reportes, "Reportes"))
        
        # Agregar al sidebar
        for btn in self.nav_buttons:
            sidebar_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        sidebar_layout.addStretch()
        
        # Botón settings abajo
        settings_btn = QLabel("⚙")
        settings_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_btn.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_400']};
                font-size: 20px;
                padding: 8px;
                background-color: transparent;
            }}
            QLabel:hover {{
                color: {COLORS['white']};
            }}
        """)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sidebar_layout.addWidget(settings_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Avatar
        avatar = QLabel("◯")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['slate_700']};
                border:  2px solid {COLORS['slate_600']};
                border-radius: 16px;
                font-size: 16px;
                color: {COLORS['slate_400']};
            }}
        """)
        avatar.setFixedSize(32, 32)
        sidebar_layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Activar primer botón por defecto
        self.btn_panel.set_active(True)
        
        main_layout. addWidget(sidebar)
        
        # === ÁREA DE INFO ===
        info_area = QWidget()
        info_layout = QVBoxLayout(info_area)
        info_layout. setSpacing(20)
        info_layout.setAlignment(Qt.AlignmentFlag. AlignTop)
        
        # Título
        title = QLabel("🧭 Test - ModernNavButton")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setWeight(QFont. Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']};")
        info_layout.addWidget(title)
        
        # Instrucciones
        instructions = QLabel(
            "<b>Instrucciones de prueba:</b><br><br>"
            "• Haz click en los botones del sidebar<br>"
            "• Estado activo: fondo oscuro + barra azul izquierda<br>"
            "• Estado inactivo: transparente, texto gris<br>"
            "• Hover: fondo gris claro<br>"
            "• Solo un botón activo a la vez<br><br>"
            "<b>Iconos SVG Lucide utilizados:</b><br>"
            "▪ layout-dashboard → Panel<br>"
            "▪ building-2 → Obras<br>"
            "▪ list → Transacciones<br>"
            "▪ wallet → Caja<br>"
            "▪ bar-chart-3 → Reportes"
        )
        instructions.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_600']};
                font-size:  14px;
                line-height: 1.8;
                background-color: {COLORS['slate_50']};
                padding: 16px;
                border-radius: 12px;
                border: 1px solid {COLORS['slate_200']};
            }}
        """)
        instructions.setWordWrap(True)
        info_layout.addWidget(instructions)
        
        # Status actual
        self.status_label = QLabel("📍 Página activa: Panel")
        self.status_label. setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['blue_50']};
                color:  {COLORS['blue_700']};
                padding: 16px;
                border-radius:  12px;
                font-weight: bold;
                font-size: 15px;
                border: 1px solid {COLORS['blue_200']};
            }}
        """)
        info_layout.addWidget(self. status_label)
        
        # Checklist visual
        checklist_items = [
            ("✅", "Sidebar oscuro (slate-900) - 100px ancho", COLORS['emerald_600']),
            ("✅", "Logo azul arriba", COLORS['emerald_600']),
            ("✅", "5 botones verticales con iconos SVG", COLORS['emerald_600']),  # ← CAMBIAR a 5
            ("✅", "Barra azul en botón activo", COLORS['emerald_600']),
            ("✅", "Hover effect funcional", COLORS['emerald_600']),
            ("✅", "Click cambia estado", COLORS['emerald_600']),
        ]
        
        checklist_text = "<br>".join([f"<span style='color:{color}'>{icon}</span> {text}" 
                                      for icon, text, color in checklist_items])
        
        checklist = QLabel(checklist_text)
        checklist.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['emerald_50']};
                color: {COLORS['emerald_700']};
                padding: 16px;
                border-radius: 12px;
                font-size: 13px;
                line-height: 1.8;
                border: 1px solid {COLORS['emerald_100']};
            }}
        """)
        checklist.setWordWrap(True)
        info_layout.addWidget(checklist)
        
        # Contador de clicks
        self.click_counter = 0
        self.counter_label = QLabel(f"Total de clicks: {self.click_counter}")
        self.counter_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['slate_100']};
                color: {COLORS['slate_700']};
                padding: 12px;
                border-radius:  8px;
                font-size:  13px;
                text-align: center;
            }}
        """)
        info_layout.addWidget(self.counter_label)
        
        info_layout.addStretch()
        
        main_layout.addWidget(info_area)
    
    def on_nav_click(self, clicked_button, page_name):
        """Manejar click en navegación"""
        self.click_counter += 1
        print(f"🔘 Click #{self.click_counter} - Navegando a: {page_name}")
        
        # Desactivar todos los botones
        for btn in self.nav_buttons:
            btn.set_active(False)
        
        # Activar el botón clickeado
        clicked_button.set_active(True)
        
        # Actualizar labels
        self.status_label. setText(f"📍 Página activa: {page_name}")
        self.counter_label.setText(f"Total de clicks: {self.click_counter}")


if __name__ == "__main__": 
    app = QApplication(sys.argv)
    
    # Aplicar stylesheet global
    app.setStyleSheet(get_global_stylesheet())
    
    # Crear y mostrar ventana
    window = TestNavButtonsWindow()
    window.show()
    
    print("=" * 60)
    print("✅ Test de ModernNavButton iniciado correctamente")
    print("=" * 60)
    print("🧭 Haz click en los botones del sidebar para probar")
    print("📊 Observa:")
    print("   - Barra azul lateral en botón activo")
    print("   - Cambios de color en hover")
    print("   - Solo un botón activo a la vez")
    print("=" * 60)
    
    sys.exit(app.exec())