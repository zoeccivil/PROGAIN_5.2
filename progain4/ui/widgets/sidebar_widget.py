"""
Modern sidebar navigation widget for PROGRAIN 4.0/5.0 - Construction Manager Pro Design

Provides:
- Compact vertical navigation (80px width)
- Modern navigation buttons with active state indicators
- Settings and user profile in footer
- Maintains backward compatibility with all signals
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
from PyQt6.QtGui import QFont, QPainter, QColor
from typing import List, Dict, Any, Optional
import logging

# Import the new ModernNavButton
from progain4.ui.widgets.modern_nav_button import ModernNavButton

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
        """Initialize the sidebar UI - Construction Manager Pro Design"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Logo/Brand section at top
        logo_section = self._create_logo_section()
        main_layout.addWidget(logo_section)

        # Navigation buttons (center, with stretch)
        nav_section = self._create_navigation_section()
        main_layout.addWidget(nav_section, stretch=1)

        # Footer section (settings, avatar)
        footer = self._create_footer()
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

        # Width constraints for new compact design (80px fixed)
        self.setFixedWidth(80)

        # NO setStyleSheet aquí: el estilo viene del theme_manager

    def _create_logo_section(self) -> QWidget:
        """Create the logo/brand section at the top - Construction Manager Pro"""
        logo_frame = QFrame()
        logo_frame.setObjectName("sidebarHeader")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 24)
        layout.setSpacing(0)
        
        # Logo container - blue background with icon
        logo_container = QFrame()
        logo_container.setStyleSheet("""
            QFrame {
                background-color: #2563eb;
                border-radius: 8px;
            }
        """)
        logo_container.setFixedSize(48, 48)
        
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo icon (using emoji for now, can be replaced with image)
        logo_label = QLabel("🏗️")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 24px; background-color: transparent; color: white;")
        logo_layout.addWidget(logo_label)
        
        # Center the logo container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(logo_container)
        container_layout.addStretch()
        
        layout.addLayout(container_layout)
        logo_frame.setLayout(layout)
        
        return logo_frame

    def _create_navigation_section(self) -> QWidget:
        """Create the navigation section with Modern Nav Buttons"""
        section = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(16)
        
        # Navigation items - using ModernNavButton
        # Map old keys to new labels for backward compatibility
        nav_items = [
            ("dashboard", "Panel", ""),  # icon_path can be empty, will use emoji fallback
            ("transactions", "Caja", ""),  # Previously "transactions", now "Caja" (cash)
            ("cash_flow", "Obras", ""),  # Previously "cash_flow", now "Obras" (projects)
            ("budget", "Reportes", ""),  # Previously "budget", now "Reportes" (reports)
        ]
        
        for item_key, item_label, icon_path in nav_items:
            btn = ModernNavButton(icon_path, item_label)
            btn.clicked.connect(lambda checked=False, k=item_key: self._on_navigation_clicked(k))
            layout.addWidget(btn)
            self.navigation_buttons[item_key] = btn
        
        layout.addStretch()
        section.setLayout(layout)
        return section

    def _create_footer(self) -> QWidget:
        """Create the footer section with settings and avatar - Construction Manager Pro"""
        footer = QFrame()
        footer.setObjectName("sidebarFooter")

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 16)
        layout.setSpacing(16)

        # Settings button (icon only)
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(32, 32)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 20px;
                color: #94a3b8;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        # Connect to import (backward compatibility with quick actions)
        settings_btn.clicked.connect(self.import_requested.emit)
        
        # Avatar (circular label)
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            QLabel {
                background-color: #334155;
                color: #ffffff;
                border: 2px solid #475569;
                border-radius: 16px;
                font-weight: 700;
                font-size: 12px;
            }
        """)
        avatar.setText("U")  # Default user initial
        avatar.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Center align buttons
        settings_layout = QHBoxLayout()
        settings_layout.addStretch()
        settings_layout.addWidget(settings_btn)
        settings_layout.addStretch()
        
        avatar_layout = QHBoxLayout()
        avatar_layout.addStretch()
        avatar_layout.addWidget(avatar)
        avatar_layout.addStretch()
        
        layout.addLayout(settings_layout)
        layout.addLayout(avatar_layout)

        footer.setLayout(layout)
        return footer

    # --------------------------------------------------------------------- API
    # Keep backward compatibility methods

    def set_project_name(self, project_name: str):
        """Set the project name - kept for backward compatibility"""
        # In the new design, project name is shown in header widget instead
        # Store it but don't display in sidebar
        self._project_name = project_name
        logger.info("Sidebar: Project name set to %s (not displayed in compact mode)", project_name)

    def set_accounts(self, accounts: List[Dict[str, Any]]):
        """
        Set the list of accounts - kept for backward compatibility.
        
        In the new compact design (80px), accounts are not displayed in the sidebar.
        They should be accessed through the main content area instead.
        
        Args:
            accounts: List of account dictionaries with 'id', 'nombre', 'tipo' keys
        """
        # Store accounts but don't display them in compact sidebar
        self._accounts = accounts
        logger.info("Sidebar: Received %d accounts (not displayed in compact mode)", len(accounts))
        
        # Keep the account_buttons dict for potential future use
        self.account_buttons.clear()

    # --------------------------------------------------------------------- Internals

    def _on_navigation_clicked(self, item_key: str):
        """Handle navigation item click - updated for ModernNavButton"""
        # Update selection state for all navigation buttons
        for key, btn in self.navigation_buttons.items():
            if isinstance(btn, ModernNavButton):
                btn.set_active(key == item_key)
            else:
                # Fallback for any old-style buttons
                selected = key == item_key
                btn.setChecked(selected)
                btn.setProperty("selected", selected)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

        self.current_navigation_item = item_key
        self.navigation_changed.emit(item_key)
        logger.info("Sidebar: Navigation changed to %s", item_key)

    def _on_account_clicked(self, cuenta_id: Optional[str]):
        """Handle account selection - kept for backward compatibility"""
        # In compact mode, accounts are not displayed
        # But we keep the signal for backward compatibility
        self.current_account_id = cuenta_id
        self.account_selected.emit(cuenta_id)
        logger.info("Sidebar: Account selected: %s", cuenta_id or "All accounts")

    # --------------------------------------------------------------------- External selection helpers

    def select_navigation_item(self, item_key: str):
        """Programmatically select a navigation item"""
        if item_key in self.navigation_buttons:
            self._on_navigation_clicked(item_key)

    def select_account(self, cuenta_id: Optional[str]):
        """Programmatically select an account - kept for backward compatibility"""
        # In compact mode, this just emits the signal
        # Fixed: use 'and' instead of 'or' to properly check both conditions
        if cuenta_id is None or cuenta_id in self.account_buttons:
            self._on_account_clicked(cuenta_id)
    
    def refresh(self):
        """Refresh the sidebar - stub for backward compatibility"""
        # In compact mode, there's nothing to refresh
        # Accounts are not displayed
        logger.debug("Sidebar refresh called (no-op in compact mode)")