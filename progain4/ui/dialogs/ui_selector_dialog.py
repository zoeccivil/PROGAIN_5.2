"""
UI Selector Dialog - Choose between Classic and Modern UI
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class UISelectorDialog(QDialog):
    """Dialog to select UI version"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.selected_ui = "classic"  # Default
        self.remember_choice = False
        
        # Load saved preference
        saved_ui = self.config_manager.get_ui_preference()
        if saved_ui: 
            self.selected_ui = saved_ui
        
        self. setup_ui()
    
    def setup_ui(self):
        """Create the UI"""
        self.setWindowTitle("PROGAIN 5.2 - Seleccionar Interfaz")
        self.setFixedSize(600, 450)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # === HEADER ===
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background:  qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #1e40af);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title = QLabel("🎨 Seleccione su Interfaz")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title. setStyleSheet("color: white; background: transparent;")
        header_layout. addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Elija la experiencia que prefiera")
        subtitle.setAlignment(Qt.AlignmentFlag. AlignCenter)
        subtitle.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px; background: transparent;")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)
        layout.addSpacing(10)
        
        # === BUTTONS CONTAINER ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # --- CLASSIC UI CARD ---
        classic_card = QFrame()
        classic_card. setStyleSheet("""
            QFrame {
                background-color: white;
                border:  2px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
            }
            QFrame: hover {
                border-color: #3b82f6;
                background-color: #f8fafc;
            }
        """)
        
        classic_layout = QVBoxLayout(classic_card)
        classic_layout.setSpacing(15)
        classic_layout.setAlignment(Qt.AlignmentFlag. AlignTop)
        
        classic_icon = QLabel("🎨")
        classic_icon.setStyleSheet("font-size: 48px; background: transparent;")
        classic_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        classic_layout.addWidget(classic_icon)
        
        classic_title = QLabel("Interfaz Clásica")
        classic_title_font = QFont()
        classic_title_font.setPointSize(14)
        classic_title_font.setWeight(QFont.Weight.Bold)
        classic_title.setFont(classic_title_font)
        classic_title. setAlignment(Qt.AlignmentFlag.AlignCenter)
        classic_title.setStyleSheet("color: #1e293b; background: transparent;")
        classic_layout.addWidget(classic_title)
        
        classic_desc = QLabel(
            "• Interfaz actual\n"
            "• Todas las funciones\n"
            "• Estable y probada\n"
            "• Múltiples temas"
        )
        classic_desc.setStyleSheet("color: #64748b; font-size:  12px; background: transparent; line-height: 1.6;")
        classic_desc. setAlignment(Qt.AlignmentFlag.AlignCenter)
        classic_layout.addWidget(classic_desc)
        
        classic_btn = QPushButton("Usar Clásica")
        classic_btn.setMinimumHeight(45)
        classic_btn.setStyleSheet("""
            QPushButton {
                background-color:  #3b82f6;
                color: white;
                font-size: 13px;
                font-weight:  bold;
                border-radius:  8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        classic_btn. clicked.connect(lambda: self._select_ui("classic"))
        classic_layout.addWidget(classic_btn)
        
        buttons_layout.addWidget(classic_card)
        
        # --- MODERN UI CARD ---
        modern_card = QFrame()
        modern_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
            }
            QFrame:hover {
                border-color: #0f172a;
                background-color: #f8fafc;
            }
        """)
        
        modern_layout = QVBoxLayout(modern_card)
        modern_layout.setSpacing(15)
        modern_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        modern_icon = QLabel("✨")
        modern_icon.setStyleSheet("font-size: 48px; background: transparent;")
        modern_icon.setAlignment(Qt. AlignmentFlag.AlignCenter)
        modern_layout.addWidget(modern_icon)
        
        modern_title = QLabel("Interfaz Moderna")
        modern_title_font = QFont()
        modern_title_font.setPointSize(14)
        modern_title_font. setWeight(QFont.Weight. Bold)
        modern_title. setFont(modern_title_font)
        modern_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        modern_title.setStyleSheet("color: #1e293b; background: transparent;")
        modern_layout.addWidget(modern_title)
        
        modern_desc = QLabel(
            "• Diseño renovado\n"
            "• Navegación fluida\n"
            "• Iconos SVG\n"
            "• En desarrollo"
        )
        modern_desc.setStyleSheet("color: #64748b; font-size: 12px; background: transparent; line-height: 1.6;")
        modern_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        modern_layout.addWidget(modern_desc)
        
        modern_btn = QPushButton("Usar Moderna")
        modern_btn.setMinimumHeight(45)
        modern_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f172a;
                color:  white;
                font-size:  13px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1e293b;
            }
            QPushButton:pressed {
                background-color: #334155;
            }
        """)
        modern_btn.clicked.connect(lambda: self._select_ui("modern"))
        modern_layout.addWidget(modern_btn)
        
        buttons_layout.addWidget(modern_card)
        
        layout.addLayout(buttons_layout)
        layout.addSpacing(10)
        
        # === REMEMBER CHECKBOX ===
        self.remember_checkbox = QCheckBox("Recordar mi elección")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #475569;
                font-size:  12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        self.remember_checkbox.setChecked(False)
        layout.addWidget(self.remember_checkbox, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # === INFO FOOTER ===
        info = QLabel("💡 Puede cambiar entre interfaces desde el menú Archivo → Cambiar Interfaz")
        info.setWordWrap(True)
        info.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 11px;
                background-color: #f1f5f9;
                padding: 12px;
                border-radius:  6px;
            }
        """)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
    
    def _select_ui(self, ui_type:  str):
        """Handle UI selection"""
        self.selected_ui = ui_type
        self.remember_choice = self.remember_checkbox.isChecked()
        
        # Save preference if remember is checked
        if self.remember_choice:
            self.config_manager.set_ui_preference(ui_type)
        
        self.accept()
    
    def get_selected_ui(self) -> str:
        """Get the selected UI type"""
        return self.selected_ui