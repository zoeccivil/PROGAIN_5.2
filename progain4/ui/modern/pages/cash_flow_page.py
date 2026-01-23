"""
Modern Cash Flow Page for PROGRAIN 5.0

Professional cash flow analysis with:
- Summary cards (Income, Expenses, Balance)
- Account-based summary table
- Monthly summary table  
- Date range filters
- Export to CSV/PDF
- Modern UI with icons and cards
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional
from collections import defaultdict
import csv
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QLabel, 
    QDateEdit, QMessageBox, QFileDialog, QAbstractItemView,
    QGroupBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QAction

from progain4.services.firebase_client import FirebaseClient
from progain4.ui.modern.theme_config import COLORS, FONTS, SPACING
from progain4.ui.modern.components.icon_manager import icon_manager

# Importar el generador de reportes
try:
    from progain4.services.report_generator import ReportGenerator
    REPORT_GENERATOR_AVAILABLE = True
except ImportError:
    REPORT_GENERATOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class CashFlowPage(QWidget):
    """
    Modern cash flow page for displaying income/expense summaries.
    
    Features:
    - Summary cards with totals
    - Account-based breakdown
    - Monthly trends
    - Date range filtering
    - CSV/PDF export
    """
    
    # Signals
    period_changed = pyqtSignal(date, date)
    
    def __init__(
        self,
        firebase_client: FirebaseClient,
        proyecto_id: str,
        proyecto_nombre: str,
        parent=None
    ):
        super().__init__(parent)
        
        self.firebase_client = firebase_client
        self.proyecto_id = proyecto_id
        self.proyecto_nombre = proyecto_nombre
        
        # ✅ CAMBIO: Inicializar con None, se calculará después
        self.fecha_inicio = None
        self.fecha_fin = None
        
        # Data storage
        self.transacciones: List[Dict[str, Any]] = []
        self.cuentas_map: Dict[str, str] = {}
        
        # Summary totals
        self.total_ingresos = 0.0
        self.total_gastos = 0.0
        self.total_balance = 0.0
        
        logger.info(f"Initializing CashFlowPage for project {proyecto_id}")
        
        # Initialize UI
        self._init_ui()
        
        # Load initial data
        self._load_accounts()
        
        # ✅ NUEVO: Calcular rango automático y cargar
        self._set_smart_date_range()
        self.refresh()


    def _set_smart_date_range(self):
        """
        Calcular rango de fechas inteligente:
        - Fecha inicio: Primera transacción del proyecto
        - Fecha fin: Hoy
        """
        try:
            logger.info(f"🔍 Calculating smart date range for project {self.proyecto_id}")
            
            # Obtener TODAS las transacciones del proyecto (sin filtro de fecha)
            all_trans = self.firebase_client.get_transacciones_by_proyecto(
                self.proyecto_id,
                cuenta_id=None,
                include_deleted=False
            )
            
            if not all_trans:
                # Si no hay transacciones, usar año actual
                logger.warning("⚠️ No transactions found, using current year as default")
                today = date.today()
                self.fecha_inicio = date(today.year, 1, 1)
                self.fecha_fin = today
            else:
                # Encontrar la fecha más antigua
                fechas = []
                for trans in all_trans:
                    trans_date = self._parse_date(trans.get('fecha'))
                    if trans_date:
                        fechas.append(trans_date)
                
                if fechas:
                    self.fecha_inicio = min(fechas)  # ✅ Primera transacción
                    self.fecha_fin = date.today()     # ✅ Hoy
                    logger.info(f"✅ Smart date range: {self.fecha_inicio} to {self.fecha_fin}")
                else:
                    # Fallback si no se pudieron parsear fechas
                    today = date.today()
                    self.fecha_inicio = date(today.year, 1, 1)
                    self.fecha_fin = today
            
            # ✅ Actualizar controles UI (sin disparar eventos)
            self.fecha_inicio_edit.blockSignals(True)
            self.fecha_fin_edit.blockSignals(True)
            
            self.fecha_inicio_edit.setDate(QDate(self.fecha_inicio.year, self.fecha_inicio.month, self.fecha_inicio.day))
            self.fecha_fin_edit.setDate(QDate(self.fecha_fin.year, self.fecha_fin.month, self.fecha_fin.day))
            
            self.fecha_inicio_edit.blockSignals(False)
            self.fecha_fin_edit.blockSignals(False)
            
        except Exception as e:
            logger.error(f"❌ Error calculating smart date range: {e}", exc_info=True)
            # Fallback a año actual
            today = date.today()
            self.fecha_inicio = date(today.year, 1, 1)
            self.fecha_fin = today

    def _init_ui(self):
        """Initialize the modern user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING['lg'])
        layout.setContentsMargins(SPACING['xl'], SPACING['lg'], SPACING['xl'], SPACING['lg'])
        
        # === HEADER ===
        header = self._create_header()
        layout.addWidget(header)
        
        # === TOOLBAR (Date filters + Export) ===
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)
        
        # === SUMMARY CARDS ===
        summary_cards = self._create_summary_cards()
        layout.addLayout(summary_cards)
        
        # === ACCOUNT SUMMARY TABLE ===
        account_group = self._create_account_summary_table()
        layout.addWidget(account_group)
        
        # === MONTHLY SUMMARY TABLE ===
        month_group = self._create_month_summary_table()
        layout.addWidget(month_group)
        
        self.setLayout(layout)
    
    def _create_header(self) -> QWidget:
        """Create page header"""
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['white']};
                border-radius: 8px;
                padding: 16px 20px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon + Title
        icon_label = QLabel("💰")
        icon_label.setStyleSheet("font-size: 24px; background: transparent;")
        layout.addWidget(icon_label)
        
        title = QLabel(f"Flujo de Caja - {self.proyecto_nombre}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']}; background: transparent;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        return header
    
    def _create_toolbar(self) -> QWidget:
        """Create toolbar with date filters and export buttons"""
        toolbar = QWidget()
        toolbar.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['white']};
                border-radius: 8px;
                padding: 12px 16px;
            }}
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(SPACING['md'])
        layout.setContentsMargins(0, 0, 0, 0)
        
        # === DATE FILTERS ===
        date_label = QLabel("📅 Período:")
        date_label.setStyleSheet(f"color: {COLORS['slate_700']}; font-weight: 600; background: transparent;")
        layout.addWidget(date_label)
        
        # Start date
        layout.addWidget(QLabel("Desde:"))
        self.fecha_inicio_edit = QDateEdit()
        self.fecha_inicio_edit.setCalendarPopup(True)
        self.fecha_inicio_edit.setDisplayFormat("yyyy-MM-dd")
        self.fecha_inicio_edit.setStyleSheet(self._get_date_edit_style())
        # ✅ NUEVO: Auto-refresh al cambiar fecha
        self.fecha_inicio_edit.dateChanged.connect(self._on_date_changed)
        layout.addWidget(self.fecha_inicio_edit)

        # End date
        layout.addWidget(QLabel("Hasta:"))
        self.fecha_fin_edit = QDateEdit()
        self.fecha_fin_edit.setCalendarPopup(True)
        self.fecha_fin_edit.setDisplayFormat("yyyy-MM-dd")
        self.fecha_fin_edit.setStyleSheet(self._get_date_edit_style())
        # ✅ NUEVO: Auto-refresh al cambiar fecha
        self.fecha_fin_edit.dateChanged.connect(self._on_date_changed)
        layout.addWidget(self.fecha_fin_edit)

        # Refresh button (ahora opcional, pero lo dejamos)
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.setStyleSheet(self._get_button_style('primary'))
        refresh_btn.clicked.connect(self._on_refresh_clicked)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        
        # === EXPORT BUTTONS ===
        csv_btn = QPushButton("📄 Exportar CSV")
        csv_btn.setStyleSheet(self._get_button_style('secondary'))
        csv_btn.clicked.connect(self._export_csv)
        layout.addWidget(csv_btn)
        
        pdf_btn = QPushButton("📑 Exportar PDF")
        pdf_btn.setStyleSheet(self._get_button_style('secondary'))
        pdf_btn.clicked.connect(self._export_pdf)
        if not REPORT_GENERATOR_AVAILABLE:
            pdf_btn.setEnabled(False)
            pdf_btn.setToolTip("ReportGenerator no disponible")
        layout.addWidget(pdf_btn)
        
        return toolbar
    
    def _on_date_changed(self):
        """Handle date change from date pickers (auto-refresh)"""
        logger.info("📅 Date range changed, auto-refreshing...")
        self.refresh()

    def _create_summary_cards(self) -> QHBoxLayout:
        """Create summary cards for Income, Expenses, Balance"""
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(SPACING['md'])
        
        # === INCOME CARD ===
        self.income_card = self._create_summary_card(
            "💵 Total Ingresos",
            "RD$ 0.00",
            COLORS['green_100'],
            COLORS['green_700']
        )
        cards_layout.addWidget(self.income_card)
        
        # === EXPENSES CARD ===
        self.expenses_card = self._create_summary_card(
            "💸 Total Gastos",
            "RD$ 0.00",
            COLORS['red_100'],
            COLORS['red_700']
        )
        cards_layout.addWidget(self.expenses_card)
        
        # === BALANCE CARD ===
        self.balance_card = self._create_summary_card(
            "💰 Balance",
            "RD$ 0.00",
            COLORS['blue_100'],
            COLORS['blue_700']
        )
        cards_layout.addWidget(self.balance_card)
        
        return cards_layout
    
    def _create_summary_card(self, title: str, value: str, bg_color: str, text_color: str) -> QWidget:
        """Helper to create a summary card"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(SPACING['xs'])
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {text_color}; font-size: 13px; font-weight: 600; background: transparent;")
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("card_value")  # For updating later
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setWeight(QFont.Weight.Bold)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {text_color}; background: transparent;")
        layout.addWidget(value_label)
        
        return card
    
    def _create_account_summary_table(self) -> QGroupBox:
        """Create account summary table"""
        group = QGroupBox("📊 Resumen por Cuenta")
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS['white']};
                border-radius: 8px;
                border: 1px solid {COLORS['slate_200']};
                padding: 16px;
                font-size: 14px;
                font-weight: 600;
                color: {COLORS['slate_800']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        self.account_table = QTableWidget()
        self.account_table.setColumnCount(4)
        self.account_table.setHorizontalHeaderLabels([
            "Cuenta", "Total Ingresos", "Total Gastos", "Balance"
        ])
        
        # Table settings
        self.account_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.account_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.account_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.account_table.setAlternatingRowColors(True)
        self.account_table.setStyleSheet(self._get_table_style())
        
        # Header settings
        header = self.account_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.account_table)
        group.setLayout(layout)
        return group
    
    def _create_month_summary_table(self) -> QGroupBox:
        """Create monthly summary table"""
        group = QGroupBox("📅 Resumen Mensual")
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS['white']};
                border-radius: 8px;
                border: 1px solid {COLORS['slate_200']};
                padding: 16px;
                font-size: 14px;
                font-weight: 600;
                color: {COLORS['slate_800']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        self.month_table = QTableWidget()
        self.month_table.setColumnCount(4)
        self.month_table.setHorizontalHeaderLabels([
            "Mes/Año", "Ingresos", "Gastos", "Balance"
        ])
        
        # Table settings
        self.month_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.month_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.month_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.month_table.setAlternatingRowColors(True)
        self.month_table.setStyleSheet(self._get_table_style())
        
        # Header settings
        header = self.month_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.month_table)
        group.setLayout(layout)
        return group
    
    # ==================== STYLES ====================
    
    def _get_button_style(self, variant='primary') -> str:
        """Get button stylesheet"""
        if variant == 'primary':
            return f"""
                QPushButton {{
                    background-color: {COLORS['blue_600']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['blue_700']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['blue_800']};
                }}
            """
        else:  # secondary
            return f"""
                QPushButton {{
                    background-color: {COLORS['white']};
                    color: {COLORS['slate_700']};
                    border: 1px solid {COLORS['slate_300']};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['slate_50']};
                    border-color: {COLORS['slate_400']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['slate_100']};
                }}
                QPushButton:disabled {{
                    background-color: {COLORS['slate_100']};
                    color: {COLORS['slate_400']};
                }}
            """
    
    def _get_date_edit_style(self) -> str:
        """Get DateEdit stylesheet"""
        return f"""
            QDateEdit {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                color: {COLORS['slate_800']};
            }}
            QDateEdit:hover {{
                border-color: {COLORS['blue_500']};
            }}
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: none;
            }}
        """
    
    def _get_table_style(self) -> str:
        """Get table stylesheet"""
        return f"""
            QTableWidget {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: 6px;
                gridline-color: {COLORS['slate_200']};
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['blue_100']};
                color: {COLORS['slate_900']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['slate_100']};
                color: {COLORS['slate_700']};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {COLORS['slate_300']};
                font-weight: 600;
                font-size: 13px;
            }}
        """
    
    # ==================== DATA LOADING ====================
    
    def _load_accounts(self):
        """Load accounts for the current project"""
        try:
            cuentas = self.firebase_client.get_cuentas_by_proyecto(self.proyecto_id)
            self.cuentas_map = {str(c['id']): c['nombre'] for c in cuentas}
            logger.info(f"Loaded {len(self.cuentas_map)} accounts")
        except Exception as e:
            logger.error(f"Error loading accounts: {e}")
            self.cuentas_map = {}
    
    def _load_transactions(self):
        """Load transactions for the current project and period"""
        try:
            logger.info(f"Loading transactions for project {self.proyecto_id}, period: {self.fecha_inicio} to {self.fecha_fin}")
            
            # Get ALL transactions for the project
            all_trans = self.firebase_client.get_transacciones_by_proyecto(
                self.proyecto_id,
                cuenta_id=None,
                include_deleted=False
            )
            
            logger.info(f"Retrieved {len(all_trans)} total transactions from project")
            
            # Filter by date range in Python
            self.transacciones = []
            for trans in all_trans:
                trans_date = self._parse_date(trans.get('fecha'))
                if trans_date and self.fecha_inicio <= trans_date <= self.fecha_fin:
                    self.transacciones.append(trans)
            
            logger.info(f"Filtered to {len(self.transacciones)} transactions in period {self.fecha_inicio} to {self.fecha_fin}")
            
        except Exception as e:
            logger.error(f"Error loading transactions: {e}", exc_info=True)
            self.transacciones = []
    
    def _parse_date(self, date_val: Any) -> Optional[date]:
        """Helper to parse dates from Firebase"""
        if not date_val:
            return None
        try:
            if isinstance(date_val, datetime):
                return date_val.date()
            if isinstance(date_val, date):
                return date_val
            if isinstance(date_val, str):
                return datetime.strptime(date_val[:10], "%Y-%m-%d").date()
        except ValueError:
            return None
        return None
    
    # ==================== UI UPDATES ====================
    
    def _update_summary_cards(self):
        """Update summary cards with totals"""
        # Update income card
        income_label = self.income_card.findChild(QLabel, "card_value")
        if income_label:
            income_label.setText(f"RD$ {self.total_ingresos:,.2f}")
        
        # Update expenses card
        expenses_label = self.expenses_card.findChild(QLabel, "card_value")
        if expenses_label:
            expenses_label.setText(f"RD$ {self.total_gastos:,.2f}")
        
        # Update balance card
        balance_label = self.balance_card.findChild(QLabel, "card_value")
        if balance_label:
            balance_label.setText(f"RD$ {self.total_balance:,.2f}")
            # Change color based on positive/negative
            color = COLORS['green_700'] if self.total_balance >= 0 else COLORS['red_700']
            balance_label.setStyleSheet(f"color: {color}; background: transparent;")
    
    def _update_account_summary(self):
        """Update account summary table (includes transfers per account, excludes from total)"""
        account_summary = defaultdict(lambda: {'ingresos': 0.0, 'gastos': 0.0})
        
        # For total general (without transfers)
        total_real = {'ingresos': 0.0, 'gastos': 0.0}
        
        for trans in self.transacciones:
            cuenta_id = str(trans.get('cuenta_id', ''))
            try:
                monto = float(trans.get('monto', 0.0))
            except:
                monto = 0.0
            tipo = str(trans.get('tipo', '')).lower()
            es_transferencia = trans.get('es_transferencia') == True
            
            # Count in individual account (includes transfers)
            if 'ingreso' in tipo:
                account_summary[cuenta_id]['ingresos'] += monto
                # Only count in total if NOT a transfer
                if not es_transferencia:
                    total_real['ingresos'] += monto
            elif 'gasto' in tipo:
                account_summary[cuenta_id]['gastos'] += monto
                # Only count in total if NOT a transfer
                if not es_transferencia:
                    total_real['gastos'] += monto
        
        # Store totals for summary cards
        self.total_ingresos = total_real['ingresos']
        self.total_gastos = total_real['gastos']
        self.total_balance = self.total_ingresos - self.total_gastos
        
        # Update summary cards
        self._update_summary_cards()
        
        # Number of rows: accounts + separator + total
        num_cuentas = len(account_summary)
        self.account_table.setRowCount(num_cuentas + 2)  # +1 separator, +1 total
        
        row = 0
        font_bold = QFont()
        font_bold.setBold(True)
        
        # Account rows
        for cuenta_id, data in sorted(account_summary.items(), key=lambda x: self.cuentas_map.get(x[0], x[0])):
            cuenta_nombre = self.cuentas_map.get(cuenta_id, f'ID:{cuenta_id}')
            ing = data['ingresos']
            gas = data['gastos']
            bal = ing - gas
            
            self.account_table.setItem(row, 0, QTableWidgetItem(cuenta_nombre))
            
            item_ing = QTableWidgetItem(f"RD$ {ing:,.2f}")
            item_ing.setForeground(QColor(COLORS['green_700']))
            item_ing.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.account_table.setItem(row, 1, item_ing)
            
            item_gas = QTableWidgetItem(f"RD$ {gas:,.2f}")
            item_gas.setForeground(QColor(COLORS['red_700']))
            item_gas.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.account_table.setItem(row, 2, item_gas)
            
            item_bal = QTableWidgetItem(f"RD$ {bal:,.2f}")
            color = QColor(COLORS['green_700']) if bal >= 0 else QColor(COLORS['red_700'])
            item_bal.setForeground(color)
            item_bal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_bal.setFont(font_bold)
            self.account_table.setItem(row, 3, item_bal)
            row += 1
        
        # Separator row
        for col in range(4):
            sep_item = QTableWidgetItem("")
            sep_item.setBackground(QColor(COLORS['slate_100']))
            self.account_table.setItem(row, col, sep_item)
        row += 1
        
        # TOTAL GENERAL row (without transfers)
        total_label = QTableWidgetItem("TOTAL GENERAL (sin transferencias internas)")
        total_label.setFont(font_bold)
        total_label.setForeground(QColor(COLORS['blue_700']))
        self.account_table.setItem(row, 0, total_label)
        
        t_ing = QTableWidgetItem(f"RD$ {total_real['ingresos']:,.2f}")
        t_ing.setForeground(QColor(COLORS['green_700']))
        t_ing.setFont(font_bold)
        t_ing.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.account_table.setItem(row, 1, t_ing)
        
        t_gas = QTableWidgetItem(f"RD$ {total_real['gastos']:,.2f}")
        t_gas.setForeground(QColor(COLORS['red_700']))
        t_gas.setFont(font_bold)
        t_gas.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.account_table.setItem(row, 2, t_gas)
        
        tot_bal = total_real['ingresos'] - total_real['gastos']
        t_bal = QTableWidgetItem(f"RD$ {tot_bal:,.2f}")
        t_bal.setForeground(QColor(COLORS['green_700']) if tot_bal >= 0 else QColor(COLORS['red_700']))
        t_bal.setFont(font_bold)
        t_bal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.account_table.setItem(row, 3, t_bal)
        
        logger.info(f"Account summary: {num_cuentas} accounts, Total: RD$ {tot_bal:,.2f}")
    
    def _update_month_summary(self):
        """Update monthly summary table (excludes internal transfers)"""
        month_summary = defaultdict(lambda: {'ingresos': 0.0, 'gastos': 0.0})
        
        for trans in self.transacciones:
            # EXCLUDE TRANSFERS from monthly summary (internal movements)
            if trans.get('es_transferencia') == True:
                continue
            
            d = self._parse_date(trans.get('fecha'))
            if not d:
                continue
            month_key = f"{d.year}-{d.month:02d}"
            
            try:
                monto = float(trans.get('monto', 0.0))
            except:
                monto = 0.0
            tipo = str(trans.get('tipo', '')).lower()
            
            if 'ingreso' in tipo:
                month_summary[month_key]['ingresos'] += monto
            elif 'gasto' in tipo:
                month_summary[month_key]['gastos'] += monto
        
        num_months = len(month_summary)
        self.month_table.setRowCount(num_months + 2)  # +1 separator, +1 total
        
        row = 0
        font_bold = QFont()
        font_bold.setBold(True)
        
        total_ing_acum = 0.0
        total_gas_acum = 0.0
        
        # Months sorted (most recent first)
        for month_key in sorted(month_summary.keys(), reverse=True):
            data = month_summary[month_key]
            ing = data['ingresos']
            gas = data['gastos']
            bal = ing - gas
            
            total_ing_acum += ing
            total_gas_acum += gas
            
            # Format label
            y, m = month_key.split('-')
            m_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            lbl = f"{m_names[int(m)-1]} {y}"
            
            self.month_table.setItem(row, 0, QTableWidgetItem(lbl))
            
            item_ing = QTableWidgetItem(f"RD$ {ing:,.2f}")
            item_ing.setForeground(QColor(COLORS['green_700']))
            item_ing.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.month_table.setItem(row, 1, item_ing)
            
            item_gas = QTableWidgetItem(f"RD$ {gas:,.2f}")
            item_gas.setForeground(QColor(COLORS['red_700']))
            item_gas.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.month_table.setItem(row, 2, item_gas)
            
            item_bal = QTableWidgetItem(f"RD$ {bal:,.2f}")
            item_bal.setForeground(QColor(COLORS['green_700']) if bal >= 0 else QColor(COLORS['red_700']))
            item_bal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_bal.setFont(font_bold)
            self.month_table.setItem(row, 3, item_bal)
            
            row += 1
        
        # Separator row
        for col in range(4):
            sep_item = QTableWidgetItem("")
            sep_item.setBackground(QColor(COLORS['slate_100']))
            self.month_table.setItem(row, col, sep_item)
        row += 1
        
        # TOTAL row
        total_label = QTableWidgetItem("TOTAL ACUMULADO")
        total_label.setFont(font_bold)
        total_label.setForeground(QColor(COLORS['blue_700']))
        self.month_table.setItem(row, 0, total_label)
        
        t_ing = QTableWidgetItem(f"RD$ {total_ing_acum:,.2f}")
        t_ing.setForeground(QColor(COLORS['green_700']))
        t_ing.setFont(font_bold)
        t_ing.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.month_table.setItem(row, 1, t_ing)
        
        t_gas = QTableWidgetItem(f"RD$ {total_gas_acum:,.2f}")
        t_gas.setForeground(QColor(COLORS['red_700']))
        t_gas.setFont(font_bold)
        t_gas.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.month_table.setItem(row, 2, t_gas)
        
        tot_bal = total_ing_acum - total_gas_acum
        t_bal = QTableWidgetItem(f"RD$ {tot_bal:,.2f}")
        t_bal.setForeground(QColor(COLORS['green_700']) if tot_bal >= 0 else QColor(COLORS['red_700']))
        t_bal.setFont(font_bold)
        t_bal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.month_table.setItem(row, 3, t_bal)
        
        logger.info(f"Month summary: {num_months} months, Total balance: RD$ {tot_bal:,.2f}")
    
    # ==================== ACTIONS ====================
    
    def refresh(self):
        """Refresh data and update tables"""
        logger.info(f"Refreshing cashflow for project {self.proyecto_id}")
        
        # Read dates from UI
        q_inicio = self.fecha_inicio_edit.date()
        q_fin = self.fecha_fin_edit.date()
        
        self.fecha_inicio = date(q_inicio.year(), q_inicio.month(), q_inicio.day())
        self.fecha_fin = date(q_fin.year(), q_fin.month(), q_fin.day())
        
        # Load transactions
        self._load_transactions()
        
        # Update tables
        self._update_account_summary()
        self._update_month_summary()
        
        # Emit signal
        self.period_changed.emit(self.fecha_inicio, self.fecha_fin)
    
    def _on_refresh_clicked(self):
        """Handle refresh button click"""
        self.refresh()
    
    def set_period(self, start: date, end: date):
        """Set date range and refresh (called from external)"""
        self.fecha_inicio = start
        self.fecha_fin = end
        
        # Update UI controls (blocking signals to avoid double load)
        self.fecha_inicio_edit.blockSignals(True)
        self.fecha_fin_edit.blockSignals(True)
        
        self.fecha_inicio_edit.setDate(QDate(start.year, start.month, start.day))
        self.fecha_fin_edit.setDate(QDate(end.year, end.month, end.day))
        
        self.fecha_inicio_edit.blockSignals(False)
        self.fecha_fin_edit.blockSignals(False)
        
        # Refresh data with new dates
        self.refresh()

    # ✅ NUEVO MÉTODO
    def on_project_change(self, proyecto_id: str, proyecto_nombre: str):
        """
        Handle project change event from MainWindow.
        
        Args:
            proyecto_id: New project ID
            proyecto_nombre: New project name
        """
        logger.info(f"🔄 CashFlowPage: Project changed to {proyecto_id} ({proyecto_nombre})")
        
        # Update project info
        self.proyecto_id = proyecto_id
        self.proyecto_nombre = proyecto_nombre
        
        # Update header title
        title_label = self.findChild(QLabel)
        if title_label and "Flujo de Caja" in title_label.text():
            title_label.setText(f"Flujo de Caja - {proyecto_nombre}")
        
        # Clear current data
        self.transacciones = []
        self.cuentas_map = {}
        self.total_ingresos = 0.0
        self.total_gastos = 0.0
        self.total_balance = 0.0
        
        # Reload accounts for new project
        self._load_accounts()
        
        # ✅ NUEVO: Recalcular rango de fechas inteligente
        self._set_smart_date_range()
        
        # Refresh data
        self.refresh()
        
        logger.info(f"✅ CashFlowPage updated for project {proyecto_nombre}")
    
    # ==================== EXPORT ====================
    
    def _export_csv(self):
        """Export to CSV"""
        if not self.proyecto_id:
            QMessageBox.warning(self, "Exportar", "No hay datos para exportar")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar CSV", f"flujo_caja_{self.proyecto_nombre}.csv", "CSV Files (*.csv)"
        )
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([f"Flujo de Caja - {self.proyecto_nombre}"])
                writer.writerow([f"Período: {self.fecha_inicio} - {self.fecha_fin}"])
                writer.writerow([])
                
                writer.writerow(["RESUMEN POR CUENTA"])
                writer.writerow(["Cuenta", "Total Ingresos", "Total Gastos", "Balance"])
                for r in range(self.account_table.rowCount()):
                    cols = [self.account_table.item(r, c).text() if self.account_table.item(r, c) else "" for c in range(4)]
                    writer.writerow(cols)
                
                writer.writerow([])
                writer.writerow(["RESUMEN MENSUAL"])
                writer.writerow(["Mes/Año", "Ingresos", "Gastos", "Balance"])
                for r in range(self.month_table.rowCount()):
                    cols = [self.month_table.item(r, c).text() if self.month_table.item(r, c) else "" for c in range(4)]
                    writer.writerow(cols)
            
            QMessageBox.information(self, "Exportar", "CSV exportado exitosamente.")
            logger.info(f"Exported CSV: {filename}")
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            QMessageBox.critical(self, "Error", f"Error al exportar CSV:\n{str(e)}")
    
    def _export_pdf(self):
        """Export to PDF using ReportGenerator"""
        if not REPORT_GENERATOR_AVAILABLE:
            QMessageBox.warning(self, "Error", "El módulo ReportGenerator no está disponible.")
            return
        
        if not self.proyecto_id:
            QMessageBox.warning(self, "Exportar", "No hay datos para exportar")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", f"flujo_caja_{self.proyecto_nombre}.pdf", "PDF Files (*.pdf)"
        )
        if not filename:
            return
        
        try:
            # Prepare data for report
            data_export = []
            
            # Collect data from monthly table
            for r in range(self.month_table.rowCount()):
                item = self.month_table.item(r, 0)
                if not item:
                    continue
                mes_lbl = item.text()
                
                def parse_monto(txt):
                    try:
                        return float(txt.replace("RD$", "").replace(",", "").strip())
                    except:
                        return 0.0
                
                ing_item = self.month_table.item(r, 1)
                gas_item = self.month_table.item(r, 2)
                bal_item = self.month_table.item(r, 3)
                
                ing = parse_monto(ing_item.text() if ing_item else "0")
                gas = parse_monto(gas_item.text() if gas_item else "0")
                bal = parse_monto(bal_item.text() if bal_item else "0")
                
                data_export.append({
                    "Mes": mes_lbl,
                    "Ingresos": ing,
                    "Gastos": gas,
                    "Balance": bal,
                    "Tipo": "Ingreso" if bal >= 0 else "Gasto"
                })
            
            date_range_str = f"{self.fecha_inicio} - {self.fecha_fin}"
            
            rg = ReportGenerator(
                data=data_export,
                title="Reporte de Flujo de Caja",
                project_name=self.proyecto_nombre,
                date_range=date_range_str,
                currency_symbol="RD$",
                column_map={"Mes": "Mes", "Ingresos": "Total Ingresos", "Gastos": "Total Gastos", "Balance": "Balance"}
            )
            
            ok, msg = rg.to_pdf(filename)
            
            if ok:
                QMessageBox.information(self, "Exportar", "PDF exportado exitosamente.")
                logger.info(f"Exported PDF: {filename}")
            else:
                QMessageBox.critical(self, "Error", f"Error al exportar PDF: {msg}")
        
        except Exception as e:
            logger.error(f"Error exporting PDF: {e}")
            QMessageBox.critical(self, "Error", f"Error al exportar PDF:\n{str(e)}")