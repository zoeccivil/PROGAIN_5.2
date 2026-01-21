"""
Centralized theme management for PROGRAIN 4.0/5.0

Provides:
- Multiple color schemes (light, dark, blue, green)
- Runtime theme switching
- Consistent styling across the application
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


# Current active theme
_current_theme = "light"


# ============================================================================
# DESIGN COLORS - Construction Manager Pro Palette
# ============================================================================
DESIGN_COLORS = {
    # Slate palette (grays)
    'slate_50': '#f8fafc',
    'slate_100': '#f1f5f9',
    'slate_200': '#e2e8f0',
    'slate_300': '#cbd5e1',
    'slate_400': '#94a3b8',
    'slate_500': '#64748b',
    'slate_600': '#475569',
    'slate_700': '#334155',
    'slate_800': '#1e293b',
    'slate_900': '#0f172a',
    
    # Blue palette (primary)
    'blue_50': '#eff6ff',
    'blue_100': '#dbeafe',
    'blue_200': '#bfdbfe',
    'blue_300': '#93c5fd',
    'blue_400': '#60a5fa',
    'blue_500': '#3b82f6',
    'blue_600': '#2563eb',
    'blue_700': '#1d4ed8',
    'blue_800': '#1e40af',
    'blue_900': '#1e3a8a',
    
    # Orange palette (accent)
    'orange_50': '#fff7ed',
    'orange_100': '#ffedd5',
    'orange_200': '#fed7aa',
    'orange_300': '#fdba74',
    'orange_400': '#fb923c',
    'orange_500': '#f97316',
    'orange_600': '#ea580c',
    'orange_700': '#c2410c',
    'orange_800': '#9a3412',
    'orange_900': '#7c2d12',
    
    # Semantic colors
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'info': '#3b82f6',
}


# Theme definitions
THEMES: Dict[str, str] = {}


# ============================================================================
# LIGHT THEME (Default - formalized version of existing theme)
# ============================================================================
THEMES["light"] = """
/* ========== GLOBAL ========== */
QMainWindow {
    background-color: #fafafa;
}

QWidget {
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 10pt;
    background-color: #fafafa;
    color: #333333;
}

/* ========== DIALOGS ========== */
QDialog {
    background-color: #fafafa;
    color: #333333;
}

/* ========== GROUP BOXES ========== */
QGroupBox {
    font-weight: bold;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px;
    color: #1976D2;
    font-size: 11pt;
}

/* ========== LIST WIDGETS ========== */
QListWidget {
    background-color: #ffffff;
    border: none;
    outline: none;
    color: #333333;
}

QListWidget::item {
    padding: 12px;
    border-bottom: 1px solid #e0e0e0;
    color: #333333;
}

QListWidget::item:selected {
    background-color: #1976D2;
    color: #ffffff;
    font-weight: bold;
}

QListWidget::item:hover:!selected {
    background-color: #E3F2FD;
    color: #1976D2;
}

/* ========== BUTTONS ========== */
QPushButton {
    background-color: #1976D2;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1565C0;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #BDBDBD;
    color: #757575;
}

/* ========== LABELS ========== */
QLabel {
    color: #333333;
}

/* ========== LINE EDITS ========== */
QLineEdit {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 6px;
    background-color: #ffffff;
    color: #333333;
}

QLineEdit:focus {
    border: 2px solid #1976D2;
}

QLineEdit:disabled {
    background-color: #F5F5F5;
    color: #999999;
}

/* ========== COMBO BOXES ========== */
QComboBox {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 6px;
    background-color: #ffffff;
    color: #333333;
}

QComboBox:hover {
    border: 1px solid #1976D2;
}

QComboBox:focus {
    border: 2px solid #1976D2;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    border: 1px solid #CCCCCC;
    background-color: #ffffff;
    color: #333333;
    selection-background-color: #1976D2;
    selection-color: #ffffff;
}

/* ========== TABLE WIDGETS ========== */
QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #F9F9F9;
    gridline-color: #E0E0E0;
    color: #333333;
    border: 1px solid #CCCCCC;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #E3F2FD;
    color: #1976D2;
}

QTableWidget::item:hover {
    background-color: #F5F5F5;
}

QHeaderView::section {
    background-color: #F5F5F5;
    color: #333333;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #1976D2;
    border-right: 1px solid #E0E0E0;
    font-weight: bold;
}

/* ========== SCROLL BARS ========== */
QScrollBar:vertical {
    border: none;
    background-color: #F5F5F5;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #BDBDBD;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9E9E9E;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #F5F5F5;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #BDBDBD;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #9E9E9E;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ========== SPLITTER ========== */
QSplitter::handle {
    background-color: #E0E0E0;
}

QSplitter::handle:hover {
    background-color: #BDBDBD;
}

/* ========== TAB WIDGET ========== */
QTabWidget::pane {
    border: 1px solid #CCCCCC;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #F5F5F5;
    color: #666666;
    padding: 8px 16px;
    border: 1px solid #CCCCCC;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #1976D2;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #E3F2FD;
}

/* ========== MENU BAR ========== */
QMenuBar {
    background-color: #ffffff;
    color: #333333;
    border-bottom: 1px solid #E0E0E0;
}

QMenuBar::item {
    padding: 8px 12px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #E3F2FD;
    color: #1976D2;
}

QMenu {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #CCCCCC;
}

QMenu::item {
    padding: 8px 24px;
}

QMenu::item:selected {
    background-color: #1976D2;
    color: #ffffff;
}

/* ========== CHECKBOXES ========== */
QCheckBox {
    color: #333333;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #CCCCCC;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #1976D2;
    border-color: #1976D2;
}

QCheckBox::indicator:hover {
    border-color: #1976D2;
}

/* ========== RADIO BUTTONS ========== */
QRadioButton {
    color: #333333;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #CCCCCC;
    border-radius: 9px;
    background-color: #ffffff;
}

QRadioButton::indicator:checked {
    background-color: #1976D2;
    border-color: #1976D2;
}

QRadioButton::indicator:hover {
    border-color: #1976D2;
}

/* ========== DATE EDIT ========== */
QDateEdit {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 6px;
    background-color: #ffffff;
    color: #333333;
}

QDateEdit:focus {
    border: 2px solid #1976D2;
}

QDateEdit::drop-down {
    border: none;
    width: 20px;
}

/* ========== SPIN BOX ========== */
QSpinBox,
QDoubleSpinBox {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 6px;
    background-color: #ffffff;
    color: #333333;
}

QSpinBox:focus,
QDoubleSpinBox:focus {
    border: 2px solid #1976D2;
}

/* ========== TEXT EDIT ========== */
QTextEdit,
QPlainTextEdit {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 6px;
    background-color: #ffffff;
    color: #333333;
}

QTextEdit:focus,
QPlainTextEdit:focus {
    border: 2px solid #1976D2;
}

/* ========== PROGRESS BAR ========== */
QProgressBar {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    background-color: #F5F5F5;
    text-align: center;
    color: #333333;
}

QProgressBar::chunk {
    background-color: #1976D2;
    border-radius: 3px;
}

/* ========== TOOL TIP ========== */
QToolTip {
    background-color: #333333;
    color: #ffffff;
    border: 1px solid #333333;
    padding: 4px;
    border-radius: 4px;
}

/* ========== TOOLBAR ========== */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #E0E0E0;
    spacing: 8px;
    padding: 4px;
}

/* ========== SIDEBAR (Light theme specific) ========== */
#sidebar {
    background-color: #f0f3f8;
    color: #2b3f5c;
    border-right: 1px solid #d0d7e3;
}

#sidebarHeader {
    background-color: #f0f3f8;
    color: #2b3f5c;
    font-weight: bold;
}

#sidebarFooter {
    background-color: #f0f3f8;
    color: #2b3f5c;
}

#sidebar QLabel.sectionTitle {
    color: #7a8aa6;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Botones de navegación del sidebar (Dashboard, Transacciones, etc.) */
QPushButton#sidebarNavButton {
    background-color: transparent;
    color: #2b3f5c;
    border-radius: 6px;
    padding: 6px 10px;
    text-align: left;
}

QPushButton#sidebarNavButton:hover {
    background-color: #e1e7f3;
}

QPushButton#sidebarNavButton:checked {
    background-color: #2563eb;
    color: white;
}

/* Botones de cuentas del sidebar */
QPushButton#sidebarAccountButton {
    background-color: transparent;
    color: #2b3f5c;
    border-radius: 6px;
    padding: 4px 8px;
    text-align: left;
}

QPushButton#sidebarAccountButton:hover {
    background-color: #e1e7f3;
}

QPushButton#sidebarAccountButton:checked {
    background-color: #2563eb;
    color: white;
}

/* Botones de acciones rápidas del sidebar */
QPushButton#sidebarQuickButton {
    background-color: transparent;
    color: #2b3f5c;
    border-radius: 6px;
    padding: 6px 10px;
    text-align: left;
}

QPushButton#sidebarQuickButton:hover {
    background-color: #e1e7f3;
}
"""


# ============================================================================
# DARK THEME
# ============================================================================
THEMES["dark"] = """
/* ========== GLOBAL ========== */
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 10pt;
    background-color: #1e1e1e;
    color: #e0e0e0;
}

/* ========== DIALOGS ========== */
QDialog {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

/* ========== GROUP BOXES ========== */
QGroupBox {
    font-weight: bold;
    color: #e0e0e0;
    border: 1px solid #404040;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: #2d2d2d;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px;
    color: #64B5F6;
    font-size: 11pt;
}

/* ========== LIST WIDGETS ========== */
QListWidget {
    background-color: #2d2d2d;
    border: none;
    outline: none;
    color: #e0e0e0;
}

QListWidget::item {
    padding: 12px;
    border-bottom: 1px solid #404040;
    color: #e0e0e0;
}

QListWidget::item:selected {
    background-color: #1976D2;
    color: #ffffff;
    font-weight: bold;
}

QListWidget::item:hover:!selected {
    background-color: #383838;
    color: #64B5F6;
}

/* ========== BUTTONS ========== */
QPushButton {
    background-color: #1976D2;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2196F3;
}

QPushButton:pressed {
    background-color: #1565C0;
}

QPushButton:disabled {
    background-color: #404040;
    color: #808080;
}

/* ========== LABELS ========== */
QLabel {
    color: #e0e0e0;
}

/* ========== LINE EDITS ========== */
QLineEdit {
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 6px;
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QLineEdit:focus {
    border: 2px solid #1976D2;
}

QLineEdit:disabled {
    background-color: #252525;
    color: #808080;
}

/* ========== COMBO BOXES ========== */
QComboBox {
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 6px;
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QComboBox:hover {
    border: 1px solid #1976D2;
}

QComboBox:focus {
    border: 2px solid #1976D2;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    border: 1px solid #404040;
    background-color: #2d2d2d;
    color: #e0e0e0;
    selection-background-color: #1976D2;
    selection-color: #ffffff;
}

/* ========== TABLE WIDGETS ========== */
QTableWidget {
    background-color: #2d2d2d;
    alternate-background-color: #252525;
    gridline-color: #404040;
    color: #e0e0e0;
    border: 1px solid #404040;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #1976D2;
    color: #ffffff;
}

QTableWidget::item:hover {
    background-color: #383838;
}

QHeaderView::section {
    background-color: #252525;
    color: #e0e0e0;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #1976D2;
    border-right: 1px solid #404040;
    font-weight: bold;
}

/* ========== SCROLL BARS ========== */
QScrollBar:vertical {
    border: none;
    background-color: #252525;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #505050;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #606060;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #252525;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #505050;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #606060;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ========== SPLITTER ========== */
QSplitter::handle {
    background-color: #404040;
}

QSplitter::handle:hover {
    background-color: #505050;
}

/* ========== TAB WIDGET ========== */
QTabWidget::pane {
    border: 1px solid #404040;
    background-color: #2d2d2d;
}

QTabBar::tab {
    background-color: #252525;
    color: #808080;
    padding: 8px 16px;
    border: 1px solid #404040;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #2d2d2d;
    color: #64B5F6;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #383838;
}

/* ========== MENU BAR ========== */
QMenuBar {
    background-color: #252525;
    color: #e0e0e0;
    border-bottom: 1px solid #404040;
}

QMenuBar::item {
    padding: 8px 12px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #383838;
    color: #64B5F6;
}

QMenu {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
}

QMenu::item {
    padding: 8px 24px;
}

QMenu::item:selected {
    background-color: #1976D2;
    color: #ffffff;
}

/* ========== CHECKBOXES ========== */
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #404040;
    border-radius: 3px;
    background-color: #2d2d2d;
}

QCheckBox::indicator:checked {
    background-color: #1976D2;
    border-color: #1976D2;
}

QCheckBox::indicator:hover {
    border-color: #1976D2;
}

/* ========== RADIO BUTTONS ========== */
QRadioButton {
    color: #e0e0e0;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #404040;
    border-radius: 9px;
    background-color: #2d2d2d;
}

QRadioButton::indicator:checked {
    background-color: #1976D2;
    border-color: #1976D2;
}

QRadioButton::indicator:hover {
    border-color: #1976D2;
}

/* ========== DATE EDIT ========== */
QDateEdit {
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 6px;
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QDateEdit:focus {
    border: 2px solid #1976D2;
}

QDateEdit::drop-down {
    border: none;
    width: 20px;
}

/* ========== SPIN BOX ========== */
QSpinBox,
QDoubleSpinBox {
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 6px;
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QSpinBox:focus,
QDoubleSpinBox:focus {
    border: 2px solid #1976D2;
}

/* ========== TEXT EDIT ========== */
QTextEdit,
QPlainTextEdit {
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 6px;
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QTextEdit:focus,
QPlainTextEdit:focus {
    border: 2px solid #1976D2;
}

/* ========== PROGRESS BAR ========== */
QProgressBar {
    border: 1px solid #404040;
    border-radius: 4px;
    background-color: #252525;
    text-align: center;
    color: #e0e0e0;
}

QProgressBar::chunk {
    background-color: #1976D2;
    border-radius: 3px;
}

/* ========== TOOL TIP ========== */
QToolTip {
    background-color: #383838;
    color: #e0e0e0;
    border: 1px solid #505050;
    padding: 4px;
    border-radius: 4px;
}

/* ========== TOOLBAR ========== */
QToolBar {
    background-color: #252525;
    border-bottom: 1px solid #404040;
    spacing: 8px;
    padding: 4px;
}

/* ========== SIDEBAR (Dark theme specific) ========== */
#sidebar {
    background-color: #0D47A1;
}

#sidebarHeader {
    background-color: #0a3c8a;
}

#sidebarFooter {
    background-color: #0a3c8a;
}
"""


# ============================================================================
# BLUE THEME (Blue accent variant)
# ============================================================================
THEMES["blue"] = """
/* ========== GLOBAL ========== */
QMainWindow {
    background-color: #e3f2fd;
}

QWidget {
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 10pt;
    background-color: #e3f2fd;
    color: #01579b;
}

/* ========== DIALOGS ========== */
QDialog {
    background-color: #e3f2fd;
    color: #01579b;
}

/* ========== GROUP BOXES ========== */
QGroupBox {
    font-weight: bold;
    color: #01579b;
    border: 1px solid #90caf9;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px;
    color: #0277bd;
    font-size: 11pt;
}

/* ========== LIST WIDGETS ========== */
QListWidget {
    background-color: #ffffff;
    border: none;
    outline: none;
    color: #01579b;
}

QListWidget::item {
    padding: 12px;
    border-bottom: 1px solid #bbdefb;
    color: #01579b;
}

QListWidget::item:selected {
    background-color: #0277bd;
    color: #ffffff;
    font-weight: bold;
}

QListWidget::item:hover:!selected {
    background-color: #bbdefb;
    color: #01579b;
}

/* ========== BUTTONS ========== */
QPushButton {
    background-color: #0277bd;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #01579b;
}

QPushButton:pressed {
    background-color: #003c6f;
}

QPushButton:disabled {
    background-color: #b0bec5;
    color: #607d8b;
}

/* Other elements inherit light theme with blue accents... */
QLineEdit {
    border: 1px solid #90caf9;
    border-radius: 4px;
    padding: 6px;
    background-color: #ffffff;
    color: #01579b;
}

QLineEdit:focus {
    border: 2px solid #0277bd;
}

QComboBox {
    border: 1px solid #90caf9;
    border-radius: 4px;
    padding: 6px;
    background-color: #ffffff;
    color: #01579b;
}

QComboBox:focus {
    border: 2px solid #0277bd;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f1f8fe;
    gridline-color: #bbdefb;
    color: #01579b;
    border: 1px solid #90caf9;
}

QTableWidget::item:selected {
    background-color: #bbdefb;
    color: #01579b;
}

QHeaderView::section {
    background-color: #e3f2fd;
    color: #01579b;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #0277bd;
    border-right: 1px solid #bbdefb;
    font-weight: bold;
}

QMenuBar {
    background-color: #ffffff;
    color: #01579b;
    border-bottom: 1px solid #90caf9;
}

QMenuBar::item:selected {
    background-color: #bbdefb;
    color: #01579b;
}

QMenu {
    background-color: #ffffff;
    color: #01579b;
    border: 1px solid #90caf9;
}

QMenu::item:selected {
    background-color: #0277bd;
    color: #ffffff;
}

QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #90caf9;
    spacing: 8px;
    padding: 4px;
}

#sidebar {
    background-color: #0277bd;
}

#sidebarHeader {
    background-color: #01579b;
}

#sidebarFooter {
    background-color: #01579b;
}
"""


# ============================================================================
# GREEN THEME (Green/eco accent variant)
# ============================================================================
THEMES["green"] = """
/* ========== GLOBAL ========== */
QMainWindow {
    background-color: #f1f8e9;
}

QWidget {
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 10pt;
    background-color: #f1f8e9;
    color: #1b5e20;
}

/* ========== DIALOGS ========== */
QDialog {
    background-color: #f1f8e9;
    color: #1b5e20;
}

/* ========== GROUP BOXES ========== */
QGroupBox {
    font-weight: bold;
    color: #1b5e20;
    border: 1px solid #aed581;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px;
    color: #388e3c;
    font-size: 11pt;
}

/* ========== LIST WIDGETS ========== */
QListWidget {
    background-color: #ffffff;
    border: none;
    outline: none;
    color: #1b5e20;
}

QListWidget::item {
    padding: 12px;
    border-bottom: 1px solid #c5e1a5;
    color: #1b5e20;
}

QListWidget::item:selected {
    background-color: #388e3c;
    color: #ffffff;
    font-weight: bold;
}

QListWidget::item:hover:!selected {
    background-color: #c5e1a5;
    color: #1b5e20;
}

/* ========== BUTTONS ========== */
QPushButton {
    background-color: #388e3c;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2e7d32;
}

QPushButton:pressed {
    background-color: #1b5e20;
}

QPushButton:disabled {
    background-color: #b0bec5;
    color: #607d8b;
}

QLineEdit {
    border: 1px solid #aed581;
    border-radius: 4px;
    padding: 6px;
    background-color: #ffffff;
    color: #1b5e20;
}

QLineEdit:focus {
    border: 2px solid #388e3c;
}

QComboBox {
    border: 1px solid #aed581;
    border-radius: 4px;
    padding: 6px;
    background-color: #ffffff;
    color: #1b5e20;
}

QComboBox:focus {
    border: 2px solid #388e3c;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f9fdf7;
    gridline-color: #c5e1a5;
    color: #1b5e20;
    border: 1px solid #aed581;
}

QTableWidget::item:selected {
    background-color: #c5e1a5;
    color: #1b5e20;
}

QHeaderView::section {
    background-color: #f1f8e9;
    color: #1b5e20;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #388e3c;
    border-right: 1px solid #c5e1a5;
    font-weight: bold;
}

QMenuBar {
    background-color: #ffffff;
    color: #1b5e20;
    border-bottom: 1px solid #aed581;
}

QMenuBar::item:selected {
    background-color: #c5e1a5;
    color: #1b5e20;
}

QMenu {
    background-color: #ffffff;
    color: #1b5e20;
    border: 1px solid #aed581;
}

QMenu::item:selected {
    background-color: #388e3c;
    color: #ffffff;
}

QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #aed581;
    spacing: 8px;
    padding: 4px;
}

#sidebar {
    background-color: #388e3c;
}

#sidebarHeader {
    background-color: #2e7d32;
}

#sidebarFooter {
    background-color: #2e7d32;
}
"""


# ============================================================================
# CONSTRUCTION MANAGER PRO THEME (Modern Design System)
# ============================================================================
THEMES["construction_pro"] = """
/* ========== GLOBAL ========== */
QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    font-family: "Segoe UI", "Inter", "Arial", sans-serif;
    font-size: 10pt;
    background-color: transparent;
    color: #0f172a;
}

/* ========== DIALOGS ========== */
QDialog {
    background-color: #ffffff;
    color: #0f172a;
}

/* ========== SIDEBAR (Dark) ========== */
#sidebar {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
}

#sidebarHeader {
    background-color: #1e293b;
    color: #f1f5f9;
}

#sidebarFooter {
    background-color: #1e293b;
}

/* ========== MENUS ========== */
QMenuBar {
    background-color: #ffffff;
    color: #0f172a;
    border-bottom: 1px solid #e2e8f0;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #f1f5f9;
}

QMenuBar::item:pressed {
    background-color: #e2e8f0;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #f1f5f9;
}

/* ========== TOOLBARS ========== */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    spacing: 4px;
    padding: 4px;
}

QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    color: #475569;
}

QToolButton:hover {
    background-color: #f1f5f9;
    color: #0f172a;
}

QToolButton:pressed {
    background-color: #e2e8f0;
}

/* ========== BUTTONS ========== */
QPushButton {
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #2563eb;
}

QPushButton:pressed {
    background-color: #1d4ed8;
}

QPushButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
}

QPushButton[class="secondary"] {
    background-color: #f1f5f9;
    color: #475569;
}

QPushButton[class="secondary"]:hover {
    background-color: #e2e8f0;
}

/* ========== TABLES ========== */
QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #e2e8f0;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #64748b;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
    font-weight: 600;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QTableWidget::item {
    padding: 8px;
    color: #1e293b;
}

QTableWidget::item:selected {
    background-color: #dbeafe;
    color: #1e40af;
}

/* ========== SCROLLBARS ========== */
QScrollBar:vertical {
    border: none;
    background: #f1f5f9;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar:horizontal {
    border: none;
    background: #f1f5f9;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background: #94a3b8;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}

/* ========== LINE EDITS ========== */
QLineEdit {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 12px;
    background-color: #ffffff;
    color: #0f172a;
}

QLineEdit:focus {
    border: 2px solid #3b82f6;
}

QLineEdit:disabled {
    background-color: #f8fafc;
    color: #94a3b8;
}

/* ========== COMBO BOXES ========== */
QComboBox {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 12px;
    background-color: #ffffff;
    color: #0f172a;
}

QComboBox:hover {
    border: 1px solid #cbd5e1;
}

QComboBox:focus {
    border: 2px solid #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background-color: #ffffff;
    color: #0f172a;
    selection-background-color: #dbeafe;
    selection-color: #1e40af;
}

/* ========== TEXT EDITS ========== */
QTextEdit, QPlainTextEdit {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px;
    background-color: #ffffff;
    color: #0f172a;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #3b82f6;
}

/* ========== GROUP BOXES ========== */
QGroupBox {
    font-weight: 600;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #ffffff;
}

/* ========== STATUS BAR ========== */
QStatusBar {
    background-color: #ffffff;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
}

/* ========== PROGRESS BARS ========== */
QProgressBar {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    text-align: center;
    background-color: #f1f5f9;
}

QProgressBar::chunk {
    background-color: #3b82f6;
    border-radius: 5px;
}

/* ========== TABS ========== */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #f8fafc;
    color: #64748b;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #0f172a;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #f1f5f9;
}

/* ========== SPIN BOXES ========== */
QSpinBox, QDoubleSpinBox {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px;
    background-color: #ffffff;
    color: #0f172a;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #3b82f6;
}

/* ========== DATE/TIME EDITS ========== */
QDateEdit, QDateTimeEdit, QTimeEdit {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px;
    background-color: #ffffff;
    color: #0f172a;
}

QDateEdit:focus, QDateTimeEdit:focus, QTimeEdit:focus {
    border: 2px solid #3b82f6;
}

/* ========== CHECKBOXES ========== */
QCheckBox {
    spacing: 8px;
    color: #0f172a;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #cbd5e1;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
    image: none;
}

QCheckBox::indicator:hover {
    border-color: #94a3b8;
}

/* ========== RADIO BUTTONS ========== */
QRadioButton {
    spacing: 8px;
    color: #0f172a;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #cbd5e1;
    border-radius: 9px;
    background-color: #ffffff;
}

QRadioButton::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
}

QRadioButton::indicator:hover {
    border-color: #94a3b8;
}
"""


# ============================================================================
# Theme Management Functions
# ============================================================================

def get_available_themes() -> List[str]:
    """
    Get list of available theme names.
    
    Returns:
        List of theme names (e.g., ["light", "dark", "blue", "green"])
    """
    return list(THEMES.keys())


def get_current_theme() -> str:
    """
    Get the name of the currently active theme.
    
    Returns:
        Current theme name
    """
    return _current_theme


def apply_theme(app, theme_name: str) -> None:
    """
    Apply a theme to the application.
    
    Args:
        app: QApplication instance
        theme_name: Name of the theme to apply (e.g., "light", "dark", "blue", "green")
    
    Raises:
        ValueError: If theme_name is not valid
    """
    global _current_theme
    
    if theme_name not in THEMES:
        available = ", ".join(get_available_themes())
        raise ValueError(
            f"Invalid theme '{theme_name}'. Available themes: {available}"
        )
    
    logger.info(f"Applying theme: {theme_name}")
    
    # Apply stylesheet
    stylesheet = THEMES[theme_name]
    app.setStyleSheet(stylesheet)
    
    # Update current theme
    _current_theme = theme_name
    
    logger.info(f"Theme '{theme_name}' applied successfully")

# ============================================================================
# ThemeManager Class (OOP Wrapper)
# ============================================================================

class ThemeManager:
    """
    Object-oriented wrapper for theme management.
    Provides an instance-based interface for theme operations.
    """
    
    def __init__(self):
        """Initialize the theme manager"""
        self.current_theme = get_current_theme()
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names"""
        return get_available_themes()
    
    def get_current_theme(self) -> str:
        """Get the name of the currently active theme"""
        return get_current_theme()
    
    def apply_theme(self, app, theme_name: str) -> None:
        """
        Apply a theme to the application.
        
        Args:
            app: QApplication or QMainWindow instance
            theme_name: Name of the theme to apply
        
        Raises:
            ValueError: If theme_name is not valid
        """
        apply_theme(app, theme_name)
        self.current_theme = theme_name
