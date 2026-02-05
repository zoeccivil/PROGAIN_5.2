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
    # Grises (Slate scale)
    'slate_900': '#0f172a',   # Sidebar background principal
    'slate_800': '#1e293b',   # Botón activo, hover states
    'slate_700': '#334155',   # Bordes avatar, elementos secundarios
    'slate_600': '#475569',
    'slate_500': '#64748b',   # Texto secundario
    'slate_400': '#94a3b8',   # Iconos inactivos, labels
    'slate_300': '#cbd5e1',
    'slate_200': '#e2e8f0',   # Bordes de cards, divisores
    'slate_100': '#f1f5f9',   # Fondos secundarios, hover backgrounds
    'slate_50': '#f8fafc',    # Fondo principal de la aplicación
    
    # Blancos
    'white': '#ffffff',       # Tarjetas, cards, header
    
    # Azules (Primary)
    'blue_600': '#2563eb',    # Acento principal, botones CTA
    'blue_500': '#3b82f6',    # Borde izquierdo de nav activo, badges
    'blue_100': '#dbeafe',    # Fondo badge "Licitación"
    'blue_700': '#1d4ed8',    # Texto badge "Licitación"
    
    # Verdes (Success/Progress)
    'emerald_600': '#059669',
    'emerald_500': '#10b981', # Barras de progreso, montos positivos
    'emerald_100': '#d1fae5', # Fondo badge "En Ejecución"
    'emerald_700': '#047857', # Texto badge "En Ejecución"
    
    # Rojos (Error/Alert)
    'rose_600': '#e11d48',
    'rose_500': '#f43f5e',    # Montos negativos, alertas
    'rose_100': '#ffe4e6',    # Fondo badge "Retrasado"
    'rose_700': '#be123c',    # Texto badge "Retrasado"
    
    # Amarillos (Warning)
    'amber_100': '#fef3c7',   # Fondo badge "Revisión"
    'amber_700': '#b45309',   # Texto badge "Revisión"
    
    # Índigo (Multi-empresa)
    'indigo_600': '#4f46e5',  # Empresa 1
    'indigo_50': '#eef2ff',   # Fondo badge empresa 1
    'indigo_100': '#e0e7ff',  # Borde badge empresa 1
    'indigo_700': '#4338ca',  # Texto badge empresa 1
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
# CONSTRUCTION PRO THEME (Modern Construction Manager Design)
# ============================================================================
THEMES["construction_pro"] = """
/* ========== GLOBAL ========== */
QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    font-family: "Segoe UI", "Arial", "Helvetica", sans-serif;
    font-size: 10pt;
    background-color: #f8fafc;
    color: #0f172a;
}

/* ========== DIALOGS ========== */
QDialog {
    background-color: #f8fafc;
    color: #0f172a;
}

/* ========== GROUP BOXES ========== */
QGroupBox {
    font-weight: 600;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 16px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: #2563eb;
    font-size: 11pt;
    font-weight: 700;
}

/* ========== LIST WIDGETS ========== */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    outline: none;
    color: #475569;
}

QListWidget::item {
    padding: 12px;
    border-bottom: 1px solid #f1f5f9;
    color: #475569;
}

QListWidget::item:selected {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 600;
}

QListWidget::item:hover:!selected {
    background-color: #f8fafc;
    color: #2563eb;
}

/* ========== BUTTONS ========== */
QPushButton {
    background-color: #0f172a;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #1e293b;
}

QPushButton:pressed {
    background-color: #334155;
}

QPushButton:disabled {
    background-color: #cbd5e1;
    color: #94a3b8;
}

/* ========== LABELS ========== */
QLabel {
    color: #0f172a;
}

/* ========== LINE EDITS ========== */
QLineEdit {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #ffffff;
    color: #0f172a;
    font-size: 13px;
}

QLineEdit:focus {
    border: 2px solid #2563eb;
}

QLineEdit:disabled {
    background-color: #f1f5f9;
    color: #94a3b8;
}

/* ========== COMBO BOXES ========== */
QComboBox {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #ffffff;
    color: #334155;
    font-size: 13px;
}

QComboBox:hover {
    border: 1px solid #cbd5e1;
}

QComboBox:focus {
    border: 2px solid #2563eb;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background-color: #ffffff;
    color: #334155;
    selection-background-color: #f1f5f9;
    selection-color: #0f172a;
    padding: 4px;
}

/* ========== TABLE WIDGETS ========== */
QTableWidget {
    background-color: #ffffff;
    gridline-color: #f1f5f9;
    color: #475569;
    border: none;
}

QTableWidget::item {
    padding: 12px 8px;
    border-bottom: 1px solid #f1f5f9;
}

QTableWidget::item:selected {
    background-color: #f1f5f9;
    color: #0f172a;
}

QTableWidget::item:hover {
    background-color: rgba(248, 250, 252, 0.8);
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #64748b;
    padding: 12px 8px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
}

/* ========== SCROLL BARS ========== */
QScrollBar:vertical {
    border: none;
    background-color: #f8fafc;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f8fafc;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    border-radius: 4px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ========== SPLITTER ========== */
QSplitter::handle {
    background-color: #e2e8f0;
}

QSplitter::handle:hover {
    background-color: #cbd5e1;
}

/* ========== TAB WIDGET ========== */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    border-radius: 12px;
}

QTabBar::tab {
    background-color: #f8fafc;
    color: #64748b;
    padding: 10px 20px;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #2563eb;
    font-weight: 700;
}

QTabBar::tab:hover:!selected {
    background-color: #f1f5f9;
}

/* ========== MENU BAR ========== */
QMenuBar {
    background-color: #ffffff;
    color: #0f172a;
    border-bottom: 1px solid #e2e8f0;
}

QMenuBar::item {
    padding: 8px 16px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #f1f5f9;
    color: #2563eb;
}

QMenu {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

QMenu::item {
    padding: 8px 24px;
}

QMenu::item:selected {
    background-color: #f1f5f9;
    color: #2563eb;
}

/* ========== CHECKBOXES ========== */
QCheckBox {
    color: #0f172a;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #cbd5e1;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}

QCheckBox::indicator:hover {
    border-color: #2563eb;
}

/* ========== RADIO BUTTONS ========== */
QRadioButton {
    color: #0f172a;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #cbd5e1;
    border-radius: 9px;
    background-color: #ffffff;
}

QRadioButton::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}

QRadioButton::indicator:hover {
    border-color: #2563eb;
}

/* ========== DATE EDIT ========== */
QDateEdit {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #ffffff;
    color: #0f172a;
}

QDateEdit:focus {
    border: 2px solid #2563eb;
}

QDateEdit::drop-down {
    border: none;
    width: 20px;
}

/* ========== SPIN BOX ========== */
QSpinBox,
QDoubleSpinBox {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #ffffff;
    color: #0f172a;
}

QSpinBox:focus,
QDoubleSpinBox:focus {
    border: 2px solid #2563eb;
}

/* ========== TEXT EDIT ========== */
QTextEdit,
QPlainTextEdit {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
    background-color: #ffffff;
    color: #0f172a;
}

QTextEdit:focus,
QPlainTextEdit:focus {
    border: 2px solid #2563eb;
}

/* ========== PROGRESS BAR ========== */
QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #f1f5f9;
    text-align: center;
    color: #475569;
    height: 8px;
}

QProgressBar::chunk {
    background-color: #10b981;
    border-radius: 4px;
}

/* ========== TOOL TIP ========== */
QToolTip {
    background-color: #0f172a;
    color: #ffffff;
    border: 1px solid #1e293b;
    padding: 6px 10px;
    border-radius: 6px;
}

/* ========== TOOLBAR ========== */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    spacing: 8px;
    padding: 8px;
}

/* ========== SIDEBAR (Construction Pro specific) ========== */
#sidebar {
    background-color: #0f172a;
    color: #94a3b8;
    border-right: 1px solid #1e293b;
    min-width: 80px;
    max-width: 80px;
}

#sidebarHeader {
    background-color: #0f172a;
    color: #ffffff;
    font-weight: 700;
}

#sidebarFooter {
    background-color: #0f172a;
    color: #94a3b8;
}

#sidebar QLabel.sectionTitle {
    color: #64748b;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 9px;
}

/* Botones de navegación del sidebar (Dashboard, Transacciones, etc.) */
QPushButton#sidebarNavButton {
    background-color: transparent;
    color: #94a3b8;
    border-radius: 12px;
    padding: 12px;
    text-align: center;
}

QPushButton#sidebarNavButton:hover {
    background-color: rgba(30, 41, 59, 0.5);
}

QPushButton#sidebarNavButton:checked {
    background-color: #1e293b;
    color: #ffffff;
    border-left: 4px solid #3b82f6;
}

/* Botones de cuentas del sidebar */
QPushButton#sidebarAccountButton {
    background-color: transparent;
    color: #94a3b8;
    border-radius: 8px;
    padding: 6px 10px;
    text-align: left;
}

QPushButton#sidebarAccountButton:hover {
    background-color: rgba(30, 41, 59, 0.3);
}

QPushButton#sidebarAccountButton:checked {
    background-color: #1e293b;
    color: #ffffff;
}

/* Botones de acciones rápidas del sidebar */
QPushButton#sidebarQuickButton {
    background-color: transparent;
    color: #94a3b8;
    border-radius: 8px;
    padding: 8px 12px;
    text-align: left;
}

QPushButton#sidebarQuickButton:hover {
    background-color: rgba(30, 41, 59, 0.3);
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