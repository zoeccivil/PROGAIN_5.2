"""
Modern sidebar navigation widget for PROGRAIN 4.0/5.0

Provides:
- Navigation sections (Dashboard, Transactions, Cash Flow, Budget)
- Accounts listing with selection
- Optional quick action buttons
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict, Any, Optional
import logging

# Import modern components
try:
    from progain4.ui.widgets.modern_nav_button import ModernNavButton
    from progain4.ui.theme_manager import DESIGN_COLORS
except ImportError:
    ModernNavButton = None
    DESIGN_COLORS = {
        'slate_900': '#0f172a',
        'slate_800': '#1e293b',
        'blue_600': '#2563eb',
    }
    print("⚠️ ModernNavButton or DESIGN_COLORS not found - using fallback")

logger = logging.getLogger(__name__)


class SidebarWidget(QWidget):
    """
    Modern sidebar navigation widget.

    Signals:
        navigation_changed: Emitted when navigation item is selected (item_name: str)
        account_selected: Emitted when account is selected (cuenta_id: Optional[str])
        import_requested: Emitted when import quick action is clicked
        auditoria_requested: Emitted when auditoria quick action is clicked
    """

    navigation_changed = pyqtSignal(str)  # item name: "dashboard", "transactions", "cash_flow", "budget"
    account_selected = pyqtSignal(object)  # cuenta_id: Optional[str], None for "all accounts"
    import_requested = pyqtSignal()
    auditoria_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.current_navigation_item: Optional[str] = None
        self.current_account_id: Optional[str] = None
        self.navigation_buttons: Dict[str, QPushButton] = {}
        self.account_buttons: Dict[Optional[str], QPushButton] = {}

        # Object name for theme stylesheets
        # IMPORTANTE: debe coincidir con los selectores #sidebar de theme_manager.py
        self.setObjectName("sidebar")

        self._init_ui()

    def _init_ui(self):
        """Initialize the sidebar UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Check if we're in modern mode (80px width) or classic mode (220-350px)
        # Modern mode uses ModernNavButton, classic mode uses the traditional layout
        is_modern_mode = ModernNavButton is not None and self.minimumWidth() == 80
        
        if is_modern_mode:
            # === MODERN MODE: 80px Dark Sidebar ===
            self.setFixedWidth(80)
            self.setStyleSheet(f"""
                SidebarWidget {{
                    background-color: {DESIGN_COLORS['slate_900']};
                    border-right: 1px solid {DESIGN_COLORS['slate_800']};
                }}
            """)
            
            # Logo container (top)
            logo_container = QWidget()
            logo_container.setFixedSize(64, 64)
            logo_container.setStyleSheet(f"""
                QWidget {{
                    background-color: {DESIGN_COLORS['blue_600']};
                    border-radius: 12px;
                }}
            """)
            logo_layout = QVBoxLayout(logo_container)
            logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Icono placeholder
            logo_label = QLabel("🏗️")
            logo_label.setStyleSheet("font-size: 28px;")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_layout.addWidget(logo_label)
            
            main_layout.addWidget(logo_container, alignment=Qt.AlignmentFlag.AlignHCenter)
            main_layout.addSpacing(32)
            
            # Navigation buttons with ModernNavButton
            nav_layout = QVBoxLayout()
            nav_layout.setSpacing(16)
            nav_layout.setContentsMargins(8, 0, 8, 0)
            
            # Create modern nav buttons
            self.btn_panel = ModernNavButton("📊", "Panel")
            self.btn_obras = ModernNavButton("🏗️", "Obras")
            self.btn_caja = ModernNavButton("💰", "Caja")
            self.btn_reportes = ModernNavButton("📊", "Reportes")
            
            # Connect signals
            self.btn_panel.clicked.connect(lambda: self._on_nav_clicked('dashboard'))
            self.btn_obras.clicked.connect(lambda: self._on_nav_clicked('projects'))
            self.btn_caja.clicked.connect(lambda: self._on_nav_clicked('transactions'))
            self.btn_reportes.clicked.connect(lambda: self._on_nav_clicked('reports'))
            
            # Store buttons for later access
            self.navigation_buttons = {
                'dashboard': self.btn_panel,
                'projects': self.btn_obras,
                'transactions': self.btn_caja,
                'reports': self.btn_reportes,
            }
            
            # Add to layout
            nav_layout.addWidget(self.btn_panel)
            nav_layout.addWidget(self.btn_obras)
            nav_layout.addWidget(self.btn_caja)
            nav_layout.addWidget(self.btn_reportes)
            
            main_layout.addLayout(nav_layout)
            main_layout.addStretch()
            
            # Activate first button
            self.btn_panel.set_active(True)
            
            print("✅ Sidebar inicializado en modo moderno (80px)")
        else:
            # === CLASSIC MODE: 220-350px Wide Sidebar ===
            # Header section
            header = self._create_header()
            main_layout.addWidget(header)

            # Navigation section
            nav_section = self._create_navigation_section()
            main_layout.addWidget(nav_section)

            # Accounts section (scrollable)
            accounts_section = self._create_accounts_section()
            main_layout.addWidget(accounts_section, stretch=1)

            # Footer section (quick actions)
            footer = self._create_footer()
            main_layout.addWidget(footer)

            # Width constraints; el color vendrá del tema
            self.setMinimumWidth(220)
            self.setMaximumWidth(350)
            
            print("✅ Sidebar inicializado en modo clásico")

        self.setLayout(main_layout)
    
    def _on_nav_clicked(self, page_name: str):
        """Handle modern navigation button clicks"""
        # Deactivate all buttons
        if hasattr(self, 'btn_panel'):
            for btn in [self.btn_panel, self.btn_obras, self.btn_caja, self.btn_reportes]:
                if btn:
                    btn.set_active(False)
        
        # Activate clicked button
        button_map = {
            'dashboard': getattr(self, 'btn_panel', None),
            'projects': getattr(self, 'btn_obras', None),
            'transactions': getattr(self, 'btn_caja', None),
            'reports': getattr(self, 'btn_reportes', None),
        }
        
        active_btn = button_map.get(page_name)
        if active_btn:
            active_btn.set_active(True)
        
        # Emit navigation signal
        self.navigation_changed.emit(page_name)
        logger.info(f"Sidebar: Navigation changed to {page_name}")


    def _create_header(self) -> QWidget:
        """Create the header section with app name and project"""
        header = QFrame()
        # Para que los temas puedan estilar el header
        header.setObjectName("sidebarHeader")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # App name
        app_label = QLabel("PROGRAIN")
        app_font = QFont()
        app_font.setPointSize(16)
        app_font.setBold(True)
        app_label.setFont(app_font)
        app_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_label)

        # Project name (will be set dynamically)
        self.project_label = QLabel("Proyecto")
        project_font = QFont()
        project_font.setPointSize(9)
        self.project_label.setFont(project_font)
        self.project_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.project_label.setWordWrap(True)
        layout.addWidget(self.project_label)

        header.setLayout(layout)
        return header

    def _create_navigation_section(self) -> QWidget:
        """Create the navigation section"""
        section = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(4)

        # Section title
        title = QLabel("NAVEGACIÓN")
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setContentsMargins(8, 0, 0, 8)
        layout.addWidget(title)

        # Navigation items
        nav_items = [
            ("dashboard", "📊 Dashboard"),
            ("transactions", "💰 Transacciones"),
            ("cash_flow", "💸 Flujo de Caja"),
            ("budget", "📈 Presupuestos"),
        ]

        for item_key, item_label in nav_items:
            btn = QPushButton(item_label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setProperty("selected", False)
            btn.clicked.connect(lambda checked, k=item_key: self._on_navigation_clicked(k))
            layout.addWidget(btn)
            self.navigation_buttons[item_key] = btn

        section.setLayout(layout)
        return section

    def _create_accounts_section(self) -> QWidget:
        """Create the scrollable accounts section"""
        section = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Section title
        title = QLabel("CUENTAS")
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setContentsMargins(8, 0, 0, 8)
        layout.addWidget(title)

        # Scrollable container for accounts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # El estilo del scroll bar puede controlarse por tema si quieres;
        # aquí lo dejamos neutro para no pelear con theme_manager
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

        # Container for account buttons
        self.accounts_container = QWidget()
        self.accounts_layout = QVBoxLayout()
        self.accounts_layout.setContentsMargins(0, 0, 0, 0)
        self.accounts_layout.setSpacing(4)
        self.accounts_container.setLayout(self.accounts_layout)

        scroll.setWidget(self.accounts_container)
        layout.addWidget(scroll)

        section.setLayout(layout)
        return section

    def _create_footer(self) -> QWidget:
        """Create the footer section with quick action buttons"""
        footer = QFrame()
        footer.setObjectName("sidebarFooter")

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Section title
        title = QLabel("ACCIONES RÁPIDAS")
        title_font = QFont()
        title_font.setPointSize(8)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setContentsMargins(8, 0, 0, 4)
        layout.addWidget(title)

        # Import button
        import_btn = QPushButton("📥 Importar")
        import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        import_btn.clicked.connect(self.import_requested.emit)
        layout.addWidget(import_btn)

        # Auditoria button
        audit_btn = QPushButton("🔍 Auditoría")
        audit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        audit_btn.clicked.connect(self.auditoria_requested.emit)
        layout.addWidget(audit_btn)

        footer.setLayout(layout)
        return footer

    # --------------------------------------------------------------------- API

    def set_project_name(self, project_name: str):
        """Set the project name displayed in the header"""
        self.project_label.setText(project_name)

    def set_accounts(self, accounts: List[Dict[str, Any]]):
        """
        Set the list of accounts to display.

        Args:
            accounts: List of account dictionaries with 'id', 'nombre', 'tipo' keys
        """
        # Clear existing account buttons
        while self.accounts_layout.count():
            item = self.accounts_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        self.account_buttons.clear()

        # Add "All accounts" option
        all_btn = QPushButton("📊 Todas las cuentas")
        all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        all_btn.setCheckable(True)
        all_btn.setProperty("selected", False)
        all_btn.clicked.connect(lambda checked=False: self._on_account_clicked(None))
        self.accounts_layout.addWidget(all_btn)
        self.account_buttons[None] = all_btn

        # Add individual accounts
        for cuenta in accounts:
            cuenta_id = cuenta.get("id")
            cuenta_nombre = cuenta.get("nombre", "Sin nombre")
            cuenta_tipo = cuenta.get("tipo", "")

            icon = self._get_account_icon(cuenta_tipo)
            btn = QPushButton(f"{icon} {cuenta_nombre}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setProperty("selected", False)
            btn.clicked.connect(lambda checked, cid=cuenta_id: self._on_account_clicked(cid))
            self.accounts_layout.addWidget(btn)
            self.account_buttons[cuenta_id] = btn

        # Add stretch at the end
        self.accounts_layout.addStretch()

        logger.info("Sidebar: Loaded %d accounts", len(accounts))

    # --------------------------------------------------------------------- Internals

    def _get_account_icon(self, tipo: str) -> str:
        """Get icon for account type"""
        if not tipo:
            return "💰"
        icons = {
            "efectivo": "💵",
            "banco": "🏦",
            "tarjeta": "💳",
            "inversion": "📈",
            "ahorro": "🏦",
        }
        return icons.get(str(tipo).lower(), "💰")

    def _on_navigation_clicked(self, item_key: str):
        """Handle navigation item click"""
        # Update selection state
        for key, btn in self.navigation_buttons.items():
            selected = key == item_key
            btn.setChecked(selected)
            btn.setProperty("selected", selected)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.current_navigation_item = item_key
        self.navigation_changed.emit(item_key)
        logger.info("Sidebar: Navigation changed to %s", item_key)

    def _on_account_clicked(self, cuenta_id: Optional[str]):
        """Handle account selection"""
        # Update selection state
        for cid, btn in self.account_buttons.items():
            selected = cid == cuenta_id
            btn.setChecked(selected)
            btn.setProperty("selected", selected)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.current_account_id = cuenta_id
        self.account_selected.emit(cuenta_id)
        logger.info("Sidebar: Account selected: %s", cuenta_id or "All accounts")

    # --------------------------------------------------------------------- External selection helpers

    def select_navigation_item(self, item_key: str):
        """Programmatically select a navigation item"""
        if item_key in self.navigation_buttons:
            self._on_navigation_clicked(item_key)

    def select_account(self, cuenta_id: Optional[str]):
        """Programmatically select an account"""
        if cuenta_id in self.account_buttons:
            self._on_account_clicked(cuenta_id)