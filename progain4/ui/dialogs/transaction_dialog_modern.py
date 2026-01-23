"""
Modern Transaction Dialog for PROGRAIN 5.0 - Professional Design

Ultra-refined 2-column layout with modern styling and optimal spacing.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
import logging
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QWidget,
    QLabel, QComboBox, QLineEdit, QTextEdit, QDateEdit, QPushButton,
    QMessageBox, QDoubleSpinBox, QCheckBox, QListWidget, QFileDialog
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont

from ui.modern.theme_config import COLORS, FONTS, SPACING, get_button_style
logger = logging.getLogger(__name__)


class ModernTransactionDialog(QDialog):
    """
    Professional modern dialog for creating or editing transactions.
    
    Features:
    - Compact, refined 2-column layout
    - Modern styled comboboxes with custom arrows
    - Optimal spacing and typography
    - Real project name display
    - Professional card design
    """
    
    def __init__(
        self,
        firebase_client,
        proyecto_id: Union[str, int],
        proyecto_nombre: str = None,  # ✅ NUEVO: nombre del proyecto
        cuentas: List[Dict[str, Any]] = None,
        categorias: List[Dict[str, Any]] = None,
        subcategorias: List[Dict[str, Any]] = None,
        parent=None,
        transaction_id: Optional[str] = None
    ):
        """
        Initialize modern transaction dialog.
        
        Args:
            firebase_client: Firebase client instance
            proyecto_id:  Project ID
            proyecto_nombre:  Project name (optional)
            cuentas: List of accounts (optional, will load if None)
            categorias: List of categories (optional, will load if None)
            subcategorias: List of subcategories (optional, will load if None)
            parent:  Parent widget
            transaction_id:  Transaction ID for editing (None for new)
        """
        super().__init__(parent)
        
        self.firebase_client = firebase_client
        self.proyecto_id = str(proyecto_id)
        self.proyecto_nombre = proyecto_nombre or f"Proyecto {proyecto_id}"
        self.transaction_id = transaction_id
        self.transaction_data = None
        
        # Attachment management
        self.attachment_files: List[str] = []
        self.existing_attachments: List[str] = []
        
        logger.info(f"Initializing modern transaction dialog for project: {self.proyecto_id}")
        
        # ===== LOAD DATA =====
        self._load_accounts(cuentas)
        self._load_categories(categorias, subcategorias)
        
        # ===== WINDOW SETUP =====
        title = "Editar Transacción" if transaction_id else "Nueva Transacción"
        self.setWindowTitle(title)
        self.setModal(True)
        
        # Optimized size
        self.setMinimumWidth(950)
        self.setMinimumHeight(620)
        self.resize(1050, 680)
        
        # Apply modern styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['slate_50']};
            }}
            
            /* Modern ComboBox Styling */
            QComboBox {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 6px;
                padding: 8px 12px;
                padding-right: 30px;
                font-size: 14px;
                color: {COLORS['slate_800']};
            }}
            
            QComboBox: hover {{
                border-color: {COLORS['blue_500']};
                background-color: {COLORS['slate_50']};
            }}
            
            QComboBox: focus {{
                border-color:  {COLORS['blue_600']};
                border-width: 2px;
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin:  padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: none;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['slate_600']};
                margin-right: 8px;
            }}
            
            QComboBox::down-arrow: hover {{
                border-top-color: {COLORS['blue_600']};
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 6px;
                selection-background-color: {COLORS['blue_100']};
                selection-color:  {COLORS['slate_900']};
                padding: 4px;
                outline: none;
            }}
            
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 4px;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS['blue_50']};
            }}
            
            /* Modern DateEdit Styling */
            QDateEdit {{
                background-color:  {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {COLORS['slate_800']};
            }}
            
            QDateEdit:hover {{
                border-color: {COLORS['blue_500']};
            }}
            
            QDateEdit:: drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: none;
            }}
            
            QDateEdit::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right:  5px solid transparent;
                border-top: 6px solid {COLORS['slate_600']};
                margin-right: 8px;
            }}
            
            /* Modern SpinBox Styling */
            QDoubleSpinBox {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 15px;
                font-weight: 600;
                color: {COLORS['slate_900']};
            }}
            
            QDoubleSpinBox:hover {{
                border-color: {COLORS['blue_500']};
            }}
            
            QDoubleSpinBox:: up-button, QDoubleSpinBox::down-button {{
                width: 20px;
                border:  none;
                background-color: transparent;
            }}
            
            QDoubleSpinBox::up-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid {COLORS['slate_600']};
            }}
            
            QDoubleSpinBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right:  4px solid transparent;
                border-top: 5px solid {COLORS['slate_600']};
            }}
            
            /* Modern LineEdit Styling */
            QLineEdit {{
                background-color:  {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {COLORS['slate_800']};
            }}
            
            QLineEdit:hover {{
                border-color: {COLORS['blue_500']};
            }}
            
            QLineEdit: focus {{
                border-color:  {COLORS['blue_600']};
                border-width: 2px;
            }}
            
            /* Modern TextEdit Styling */
            QTextEdit {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius:  6px;
                padding:  8px 12px;
                font-size: 13px;
                color: {COLORS['slate_800']};
            }}
            
            QTextEdit:hover {{
                border-color: {COLORS['blue_500']};
            }}
            
            QTextEdit:focus {{
                border-color: {COLORS['blue_600']};
                border-width: 2px;
            }}
        """)
        
        # ===== INITIALIZE UI =====
        self._init_ui()
        
        # ===== LOAD TRANSACTION DATA IF EDITING =====
        if transaction_id:
            self._load_transaction()
    
    def _load_accounts(self, cuentas: Optional[List[Dict[str, Any]]]):
        """Load accounts from Firebase or use provided list"""
        if cuentas is None:
            try:
                self.cuentas = self.firebase_client.get_cuentas_by_proyecto(self.proyecto_id)
                logger.info(f"✅ Loaded {len(self.cuentas)} accounts")
            except Exception as e: 
                logger.error(f"❌ Error loading accounts: {e}")
                self.cuentas = []
        else:
            self.cuentas = cuentas
    
    def _load_categories(self, categorias: Optional[List[Dict[str, Any]]], 
                        subcategorias: Optional[List[Dict[str, Any]]]):
        """
        Load categories and subcategories from project.
        
        ✅ CORREGIDO: Usa métodos correctos de Firebase y tiene fallback a maestras.
        """
        self.categorias = []
        self.subcategorias = []
        
        try:
            # ===== 1️⃣ CARGAR CATEGORÍAS =====
            if categorias is None:
                # ✅ Obtener categorías activas del proyecto
                categorias_proyecto = self.firebase_client.get_categorias_por_proyecto(self.proyecto_id)
                logger.info(f"📋 Categorías del proyecto obtenidas: {len(categorias_proyecto)}")
                
                if categorias_proyecto:
                    # Ya vienen con nombres resueltos desde firebase_client
                    self.categorias = categorias_proyecto
                    
                    for cat in self.categorias[:5]:
                        logger.debug(f"  - {cat.get('nombre')} (ID: {cat.get('id')})")
            else:
                self.categorias = categorias
            
            # ===== 2️⃣ CARGAR SUBCATEGORÍAS =====
            if subcategorias is None:
                # ✅ CORREGIDO: Usar método correcto (con "activas")
                subcategorias_proyecto = self.firebase_client.get_subcategorias_activas_por_proyecto(self.proyecto_id)
                logger.info(f"📋 Subcategorías del proyecto obtenidas: {len(subcategorias_proyecto)}")
                
                if subcategorias_proyecto:
                    # Ya vienen con nombres resueltos desde firebase_client
                    self.subcategorias = subcategorias_proyecto
                    
                    for sub in self.subcategorias[:5]:
                        logger.debug(f"  - {sub.get('nombre')} (cat: {sub.get('categoria_id')})")
            else:
                self.subcategorias = subcategorias
                
        except Exception as e:
            logger.error(f"❌ Error cargando categorías del proyecto: {e}", exc_info=True)
        
        # ===== 3️⃣ FALLBACK: Cargar catálogo global si no hay asignadas =====
        if not self.categorias:
            logger.warning("⚠️ No hay categorías asignadas, cargando catálogo global como fallback")
            
            try:
                # ✅ Usar método que ya tiene el mapeo correcto
                self.categorias = self.firebase_client.get_categorias_maestras() or []
                self.subcategorias = self.firebase_client.get_subcategorias_maestras() or []
                
                logger.info(f"Fallback: {len(self.categorias)} categorías, {len(self.subcategorias)} subcategorías")
                
            except Exception as e:
                logger.error(f"❌ Error en fallback de catálogo global: {e}")
        
        # ===== 4️⃣ LOG RESUMEN =====
        logger.info("="*50)
        logger.info(f"✅ RESUMEN DE DATOS CARGADOS:")
        logger.info(f"   Categorías:     {len(self.categorias)}")
        logger.info(f"   Subcategorías:  {len(self.subcategorias)}")
        logger.info("="*50)
        
        if self.categorias:
            logger.info("📂 Primeras categorías:")
            for cat in self.categorias[:3]:
                logger.info(f"   • {cat.get('nombre', 'Sin nombre')} (ID: {cat.get('id')})")
        
        # ===== 5️⃣ VALIDACIÓN =====
        if not self.categorias:
            QMessageBox.warning(
                self,
                "Sin Categorías",
                f"No se encontraron categorías para el proyecto {self.proyecto_nombre}.\n\n"
                "Puede asignar categorías al proyecto desde:\n"
                "Editar → Gestionar categorías del proyecto"
            )
    
    def _init_ui(self):
        """Initialize the refined 2-column UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(SPACING['md'])
        main_layout.setContentsMargins(SPACING['xl'], SPACING['lg'], SPACING['xl'], SPACING['lg'])
        
        # === COMPACT HEADER ===
        header = self._create_compact_header()
        main_layout.addWidget(header)
        
        # === MAIN CONTENT:  2 COLUMNS ===
        content_layout = QHBoxLayout()
        content_layout.setSpacing(SPACING['lg'])
        
        # === LEFT COLUMN ===
        left_column = QVBoxLayout()
        left_column.setSpacing(SPACING['md'])
        
        main_card = self._create_main_details_card()
        left_column.addWidget(main_card)
        
        state_card = self._create_state_card()
        left_column.addWidget(state_card)
        
        left_column.addStretch()
        
        content_layout.addLayout(left_column, 1)
        
        # === RIGHT COLUMN ===
        right_column = QVBoxLayout()
        right_column.setSpacing(SPACING['md'])
        
        category_card = self._create_category_card()
        right_column.addWidget(category_card)
        
        desc_card = self._create_description_card()
        right_column.addWidget(desc_card)
        
        attachments_card = self._create_attachments_card()
        right_column.addWidget(attachments_card)
        
        right_column.addStretch()
        
        content_layout.addLayout(right_column, 1)
        
        main_layout.addLayout(content_layout, 1)
        
        # === COMPACT FOOTER ===
        footer = self._create_compact_footer()
        main_layout.addWidget(footer)
        
        self.setLayout(main_layout)
        
        if self.categoria_combo. count() > 0:
            self._on_category_changed(0)
    
    def _create_compact_header(self) -> QWidget:
        """Create ultra-compact, professional header"""
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['white']};
                border-radius: 6px;
                padding: 8px 14px;
                border: 1px solid {COLORS['slate_200']};
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setSpacing(SPACING['sm'])
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon (smaller)
        icon = QLabel("💰")
        icon.setStyleSheet("font-size: 16px; background:  transparent;")
        layout.addWidget(icon)
        
        # Title (compact)
        title_text = "Editar Transacción" if self.transaction_id else "Nueva Transacción"
        title = QLabel(title_text)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']}; background: transparent;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Project name (real name, not ID)
        project_label = QLabel(self.proyecto_nombre)  # ✅ USA NOMBRE REAL
        project_label. setStyleSheet(f"""
            color: {COLORS['slate_700']};
            font-size: 12px;
            font-weight:  500;
            background: {COLORS['slate_100']};
            padding: 3px 8px;
            border-radius: 4px;
        """)
        layout.addWidget(project_label)
        
        # Categories count (compact)
        cat_label = QLabel(f"{len(self.categorias)} cat.")
        cat_label.setStyleSheet(f"""
            color:  {COLORS['blue_700']};
            font-size:  11px;
            font-weight:  500;
            background: {COLORS['blue_50']};
            padding: 3px 7px;
            border-radius:  4px;
        """)
        layout.addWidget(cat_label)
        
        return header
    
    def _create_main_details_card(self) -> QWidget:
        """Create refined main details card"""
        card = self._create_refined_card("💰 Detalles Principales")
        form = QFormLayout()
        form.setSpacing(SPACING['sm'])
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy. ExpandingFieldsGrow)
        form.setHorizontalSpacing(SPACING['md'])
        
        # Type
        self. tipo_combo = QComboBox()
        self.tipo_combo.addItem("💸 Gasto", "gasto")
        self.tipo_combo.addItem("💵 Ingreso", "ingreso")
        self.tipo_combo.setMinimumHeight(36)
        form.addRow(self._create_compact_label("Tipo: "), self.tipo_combo)
        
        # Account
        self.cuenta_combo = QComboBox()
        self.cuenta_combo.setMinimumHeight(36)
        if self.cuentas:
            for cuenta in sorted(self.cuentas, key=lambda x: x. get('nombre', '')):
                c_id = str(cuenta.get('id', ''))
                c_nombre = cuenta.get('nombre', 'Sin nombre')
                self.cuenta_combo.addItem(f"🏦 {c_nombre}", c_id)
        else:
            self.cuenta_combo.addItem("(Sin cuentas disponibles)", None)
        form.addRow(self._create_compact_label("Cuenta:"), self.cuenta_combo)
        
        # Date
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setDisplayFormat("yyyy-MM-dd")
        self.fecha_edit.setMinimumHeight(36)
        form.addRow(self._create_compact_label("Fecha:"), self.fecha_edit)
        
        # Amount
        self.monto_spin = QDoubleSpinBox()
        self.monto_spin.setRange(0.01, 999999999.99)
        self.monto_spin.setDecimals(2)
        self.monto_spin.setPrefix("RD$ ")
        self.monto_spin.setValue(0.00)
        self.monto_spin.setMinimumHeight(36)
        form.addRow(self._create_compact_label("Monto:"), self.monto_spin)
        
        card.layout().addLayout(form)
        return card
    
    def _create_category_card(self) -> QWidget:
        """Create refined category card with equal width comboboxes"""
        card = self._create_refined_card(f"📁 Categorización ({len(self.categorias)})")
        form = QFormLayout()
        form.setSpacing(SPACING['sm'])
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setHorizontalSpacing(SPACING['md'])
        
        # === CATEGORY ===
        self.categoria_combo = QComboBox()
        
        # ✅ SOBRESCRIBIR ESTILO para este ComboBox específico
        self.categoria_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 6px;
                padding: 8px 12px;
                padding-right: 30px;
                font-size: 14px;
                color: {COLORS['slate_800']};
                min-width: 320px;  /* ✅ ANCHO MÍNIMO */
                max-width: 320px;  /* ✅ ANCHO MÁXIMO */
            }}
            QComboBox:hover {{
                border-color: {COLORS['blue_500']};
                background-color: {COLORS['slate_50']};
            }}
            QComboBox:focus {{
                border-color: {COLORS['blue_600']};
                border-width: 2px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['slate_600']};
                margin-right: 8px;
            }}
            QComboBox::down-arrow:hover {{
                border-top-color: {COLORS['blue_600']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 6px;
                selection-background-color: {COLORS['blue_100']};
                selection-color: {COLORS['slate_900']};
                padding: 4px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 4px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS['blue_50']};
            }}
        """)
        
        self.categoria_combo.setMinimumHeight(36)
        
        if self.categorias:
            cats_sorted = sorted(self.categorias, key=lambda x: x.get('nombre', '').upper())
            for categoria in cats_sorted:
                cat_id = str(categoria.get('id', ''))
                cat_nombre = categoria.get('nombre', 'Sin nombre')
                self.categoria_combo.addItem(cat_nombre, cat_id)
        else:
            self.categoria_combo.addItem("(Sin categorías disponibles)", None)
            self.categoria_combo.setEnabled(False)
        
        self.categoria_combo.currentIndexChanged.connect(self._on_category_changed)
        form.addRow(self._create_compact_label("Categoría:"), self.categoria_combo)
        
        # === SUBCATEGORY ===
        self.subcategoria_combo = QComboBox()
        
        # ✅ MISMO ESTILO para Subcategoría
        self.subcategoria_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 6px;
                padding: 8px 12px;
                padding-right: 30px;
                font-size: 14px;
                color: {COLORS['slate_800']};
                min-width: 320px;  /* ✅ MISMO ANCHO */
                max-width: 320px;  /* ✅ MISMO ANCHO */
            }}
            QComboBox:hover {{
                border-color: {COLORS['blue_500']};
                background-color: {COLORS['slate_50']};
            }}
            QComboBox:focus {{
                border-color: {COLORS['blue_600']};
                border-width: 2px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['slate_600']};
                margin-right: 8px;
            }}
            QComboBox::down-arrow:hover {{
                border-top-color: {COLORS['blue_600']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 6px;
                selection-background-color: {COLORS['blue_100']};
                selection-color: {COLORS['slate_900']};
                padding: 4px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 4px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS['blue_50']};
            }}
        """)
        
        self.subcategoria_combo.setMinimumHeight(36)
        self.subcategoria_combo.addItem("(Ninguna)", None)
        form.addRow(self._create_compact_label("Subcategoría:"), self.subcategoria_combo)
        
        card.layout().addLayout(form)
        return card

    def _force_equal_category_combo_widths(self):
        """Force subcategory combo to have the same width as category combo."""
        if not hasattr(self, "categoria_combo") or not hasattr(self, "subcategoria_combo"):
            return

        # ancho objetivo: el ancho real del combo de categoría
        w = self.categoria_combo.width()
        if w <= 0:
            w = self.categoria_combo.sizeHint().width()

        # fuerza mínimo igual al ancho objetivo (así no se encoge)
        self.subcategoria_combo.setMinimumWidth(w)
        self.subcategoria_combo.updateGeometry()


    def showEvent(self, event):
        super().showEvent(event)
        self._force_equal_category_combo_widths()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._force_equal_category_combo_widths()



    def _create_description_card(self) -> QWidget:
        """Create refined description card"""
        card = self._create_refined_card("📝 Descripción")
        layout = card.layout()
        
        # Description
        desc_label = self._create_compact_label("Descripción:")
        desc_label.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 13px; font-weight: 600;")
        layout.addWidget(desc_label)
        
        self.descripcion_edit = QLineEdit()
        self.descripcion_edit.setPlaceholderText("Ej: Compra de materiales")
        self.descripcion_edit.setMinimumHeight(36)
        layout.addWidget(self.descripcion_edit)
        
        layout.addSpacing(SPACING['xs'])
        
        # Comments
        comment_label = self._create_compact_label("Comentario (opcional):")
        comment_label.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: 13px; font-weight: 600;")
        layout.addWidget(comment_label)
        
        self.comentario_edit = QTextEdit()
        self.comentario_edit.setPlaceholderText("Información adicional...")
        self.comentario_edit.setMaximumHeight(70)
        layout.addWidget(self.comentario_edit)
        
        return card
    
    def _create_attachments_card(self) -> QWidget:
        """Create refined attachments card"""
        card = self._create_refined_card("📎 Adjuntos")
        layout = card.layout()
        
        self.attachments_list = QListWidget()
        self.attachments_list.setMaximumHeight(90)
        self.attachments_list.setStyleSheet(f"""
            QListWidget {{
                background-color:  {COLORS['slate_50']};
                border:  1px solid {COLORS['slate_200']};
                border-radius: 6px;
                padding: 6px;
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 4px 6px;
                border-radius: 3px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['blue_100']};
                color: {COLORS['slate_900']};
            }}
        """)
        layout.addWidget(self.attachments_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(SPACING['xs'])
        
        add_btn = QPushButton("📎 Agregar")
        add_btn.setStyleSheet(self._get_secondary_button_style())
        add_btn.setMinimumHeight(32)
        add_btn.setMaximumWidth(100)
        add_btn.clicked.connect(self._add_attachment)
        buttons_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("🗑️ Quitar")
        remove_btn.setStyleSheet(self._get_secondary_button_style())
        remove_btn.setMinimumHeight(32)
        remove_btn. setMaximumWidth(90)
        remove_btn.clicked.connect(self._remove_attachment)
        buttons_layout.addWidget(remove_btn)
        
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        return card
    
    def _create_state_card(self) -> QWidget:
        """Create refined state card"""
        card = self._create_refined_card("✓ Estado")
        layout = card.layout()
        
        self.cleared_checkbox = QCheckBox("Transacción conciliada")
        self.cleared_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS['slate_700']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {COLORS['slate_400']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['blue_600']};
                border-color: {COLORS['blue_600']};
                image: none;
            }}
        """)
        layout.addWidget(self.cleared_checkbox)
        
        info = QLabel("Marca si esta transacción ya fue verificada con el banco")
        info.setStyleSheet(f"""
            color:  {COLORS['slate_500']};
            font-size:  11px;
            margin-left: 26px;
            margin-top: 2px;
        """)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        return card
    
    def _create_compact_footer(self) -> QWidget:
        """Create compact footer"""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setSpacing(SPACING['sm'])
        layout.setContentsMargins(0, SPACING['sm'], 0, 0)
        
        layout.addStretch()
        
        # Cancel
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(self._get_secondary_button_style())
        cancel_btn.setMinimumHeight(38)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self. reject)
        layout.addWidget(cancel_btn)
        
        # Save
        save_btn = QPushButton("💾 Guardar")
        save_btn.setStyleSheet(self._get_primary_button_style())
        save_btn.setMinimumHeight(38)
        save_btn.setMinimumWidth(110)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_transaction)
        layout.addWidget(save_btn)
        
        return footer
    
    def _create_refined_card(self, title: str) -> QWidget:
        """Helper to create refined card"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['white']};
                border-radius: 8px;
                border: 1px solid {COLORS['slate_200']};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(SPACING['sm'])
        layout.setContentsMargins(SPACING['md'], SPACING['md'], SPACING['md'], SPACING['md'])
        
        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLORS['slate_800']}; background: transparent;")
        layout.addWidget(title_label)
        
        return card
    
    def _create_compact_label(self, text: str) -> QLabel:
        """Helper to create compact label"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_700']};
                font-size:  13px;
                font-weight:  600;
                background: transparent;
            }}
        """)
        return label
    
    def _get_primary_button_style(self) -> str:
        """Get primary button style"""
        return f"""
            QPushButton {{
                background-color: {COLORS['blue_600']};
                color:  white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size:  14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['blue_700']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['blue_800']};
            }}
        """
    
    def _get_secondary_button_style(self) -> str:
        """Get secondary button style"""
        return f"""
            QPushButton {{
                background-color: {COLORS['white']};
                color: {COLORS['slate_700']};
                border: 1px solid {COLORS['slate_300']};
                border-radius:  6px;
                padding:  6px 12px;
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
        """
    
    # ==================== LOGIC METHODS ====================
    
    def _on_category_changed(self, index: int):
        """Update subcategories combo when category changes"""
        self.subcategoria_combo.clear()
        self.subcategoria_combo.addItem("(Ninguna)", None)
        
        if index < 0:
            return
        
        categoria_id = self.categoria_combo.currentData()
        if not categoria_id:
            return
        
        logger.debug(f"Category changed to ID: {categoria_id}")
        
        subs_filtradas = [
            s for s in self.subcategorias 
            if str(s.get('categoria_id', '')) == str(categoria_id)
        ]
        
        logger.debug(f"Found {len(subs_filtradas)} subcategories for category {categoria_id}")
        
        if not subs_filtradas:
            return
        
        subs_filtradas.sort(key=lambda x: x.get('nombre', '').upper())
        
        for subcat in subs_filtradas: 
            sub_id = str(subcat. get('id', ''))
            sub_nombre = subcat.get('nombre', 'Sin nombre')
            self.subcategoria_combo.addItem(sub_nombre, sub_id)
    
    def _load_transaction(self):
        """Load transaction data for editing"""
        try:
            self.transaction_data = self.firebase_client.get_transaccion_by_id(
                self.proyecto_id,
                self.transaction_id
            )
            
            if not self.transaction_data:
                QMessageBox.warning(self, "Error", "No se pudo cargar la transacción.")
                return
            
            logger.info(f"Loading transaction {self.transaction_id}")
            
            # Type
            tipo = self.transaction_data.get('tipo', 'gasto')
            if isinstance(tipo, str):
                tipo = tipo.lower()
            index = self.tipo_combo.findData(tipo)
            if index >= 0:
                self.tipo_combo.setCurrentIndex(index)
            
            # Account
            cuenta_id = str(self.transaction_data.get('cuenta_id', ''))
            index = self.cuenta_combo.findData(cuenta_id)
            if index >= 0:
                self.cuenta_combo.setCurrentIndex(index)
            
            # Date
            fecha = self.transaction_data.get('fecha')
            if isinstance(fecha, datetime):
                qdate = QDate(fecha.year, fecha.month, fecha.day)
                self. fecha_edit.setDate(qdate)
            elif isinstance(fecha, str):
                try:
                    fecha_str = fecha[: 10] if len(fecha) >= 10 else fecha
                    dt = datetime.strptime(fecha_str, "%Y-%m-%d")
                    self.fecha_edit.setDate(QDate(dt.year, dt. month, dt.day))
                except:
                    pass
            
            # Amount
            monto = self.transaction_data.get('monto', 0.0)
            self.monto_spin.setValue(float(monto))
            
            # Category
            categoria_id = str(self.transaction_data.get('categoria_id', ''))
            index = self.categoria_combo.findData(categoria_id)
            if index >= 0:
                self.categoria_combo. setCurrentIndex(index)
                self._on_category_changed(index)
            
            # Subcategory
            subcategoria_id = str(self.transaction_data.get('subcategoria_id', ''))
            if subcategoria_id and subcategoria_id != 'None':
                index = self.subcategoria_combo.findData(subcategoria_id)
                if index >= 0:
                    self.subcategoria_combo.setCurrentIndex(index)
            
            # Description
            self. descripcion_edit.setText(self.transaction_data.get('descripcion', ''))
            
            # Comments
            self. comentario_edit.setPlainText(self.transaction_data.get('comentario', ''))
            
            # Cleared
            self.cleared_checkbox. setChecked(self.transaction_data.get('cleared', False))
            
            # Attachments
            self.existing_attachments = self.transaction_data.get('adjuntos', [])
            self._update_attachments_list()
            
        except Exception as e: 
            logger.error(f"Error loading transaction: {e}")
            QMessageBox.critical(self, "Error", f"Error al cargar la transacción:\n{str(e)}")
    
    def _add_attachment(self):
        """Add attachment files"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar archivos adjuntos",
            "",
            "Todos los archivos (*);;PDF (*.pdf);;Imágenes (*.jpg *.jpeg *.png);;Excel (*.xlsx *.xls);;CSV (*.csv)"
        )
        
        if file_paths:
            for file_path in file_paths: 
                if file_path not in self.attachment_files:
                    self. attachment_files.append(file_path)
            
            self._update_attachments_list()
            logger.info(f"Added {len(file_paths)} attachments")
    
    def _remove_attachment(self):
        """Remove selected attachment"""
        current_item = self.attachments_list.currentItem()
        if not current_item:
            return
        
        item_text = current_item.text()
        
        if "(nuevo)" in item_text:
            for file_path in self.attachment_files[: ]:
                if os.path.basename(file_path) in item_text:
                    self.attachment_files.remove(file_path)
                    break
        elif "(existente)" in item_text:
            reply = QMessageBox.question(
                self,
                "Confirmar",
                "¿Está seguro de que desea eliminar este archivo adjunto?",
                QMessageBox.StandardButton.Yes | QMessageBox. StandardButton.No
            )
            
            if reply == QMessageBox. StandardButton.Yes:
                row = self.attachments_list.row(current_item)
                if row < len(self.existing_attachments):
                    del self.existing_attachments[row]
        
        self._update_attachments_list()
    
    def _update_attachments_list(self):
        """Update attachments list display"""
        self.attachments_list.clear()
        
        for url in self.existing_attachments:
            try:
                from urllib.parse import unquote
                filename = os.path.basename(unquote(url).split('? ')[0])
            except:
                filename = "Archivo adjunto"
            self.attachments_list.addItem(f"📎 {filename} (existente)")
        
        for file_path in self.attachment_files:
            filename = os.path.basename(file_path)
            try:
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                self.attachments_list.addItem(f"📎 {filename} ({file_size:.2f} MB) (nuevo)")
            except: 
                self.attachments_list. addItem(f"📎 {filename} (nuevo)")
    
    def _save_transaction(self):
        """Save the transaction to Firebase"""
        if self.monto_spin.value() <= 0:
            QMessageBox.warning(self, "Campo requerido", "El monto debe ser mayor que cero.")
            self.monto_spin.setFocus()
            return
        
        if not self.cuentas or self.cuenta_combo.currentData() is None:
            QMessageBox. warning(self, "Campo requerido", "Debe seleccionar una cuenta.")
            self.cuenta_combo.setFocus()
            return
        
        if not self.categorias or self.categoria_combo. currentData() is None:
            QMessageBox.warning(self, "Campo requerido", "Debe seleccionar una categoría.")
            self.categoria_combo. setFocus()
            return
        
        try:
            tipo = self.tipo_combo.currentData()
            cuenta_id = self.cuenta_combo.currentData()
            categoria_id = self.categoria_combo.currentData()
            subcategoria_id = self.subcategoria_combo.currentData()
            
            categoria_nombre = self.categoria_combo.currentText()
            subcategoria_nombre = self.subcategoria_combo.currentText() if subcategoria_id else ""
            
            qdate = self.fecha_edit. date()
            fecha_str = qdate.toString("yyyy-MM-dd")
            
            monto = self.monto_spin.value()
            descripcion = self.descripcion_edit.text().strip()
            comentario = self.comentario_edit.toPlainText().strip()
            cleared = self.cleared_checkbox.isChecked()
            
            transaction_data = {
                'tipo': tipo. capitalize() if tipo else 'Gasto',
                'cuenta_id': cuenta_id,
                'categoria_id': categoria_id,
                'categoriaNombre': categoria_nombre,
                'subcategoria_id':  subcategoria_id,
                'subcategoriaNombre': subcategoria_nombre if subcategoria_nombre != "(Ninguna)" else "",
                'fecha': fecha_str,
                'monto': monto,
                'descripcion': descripcion,
                'comentario': comentario,
                'cleared': cleared,
                'proyecto_id': self.proyecto_id
            }
            
            try:
                if cuenta_id and str(cuenta_id).isdigit():
                    transaction_data['cuenta_id'] = int(cuenta_id)
                if categoria_id and str(categoria_id).isdigit():
                    transaction_data['categoria_id'] = int(categoria_id)
                if subcategoria_id and str(subcategoria_id).isdigit():
                    transaction_data['subcategoria_id'] = int(subcategoria_id)
            except:
                pass
            
            if self.transaction_id:
                transaction_data['adjuntos'] = self.existing_attachments
                
                success = self.firebase_client.update_transaccion(
                    self.proyecto_id,
                    self.transaction_id,
                    transaction_data
                )
                
                if not success:
                    raise Exception("No se pudo actualizar la transacción")
                
                if self.attachment_files:
                    self._upload_attachments(self.transaction_id)
                
                logger.info(f"Transaction {self.transaction_id} updated successfully")
            else:
                trans_id = self.firebase_client.create_transaccion(
                    proyecto_id=self.proyecto_id,
                    fecha=fecha_str,
                    tipo=tipo. capitalize() if tipo else 'Gasto',
                    cuenta_id=transaction_data['cuenta_id'],
                    categoria_id=transaction_data['categoria_id'],
                    monto=monto,
                    descripcion=descripcion,
                    comentario=comentario,
                    subcategoria_id=transaction_data. get('subcategoria_id'),
                    adjuntos=None
                )
                
                if not trans_id:
                    raise Exception("No se pudo crear la transacción")
                
                if trans_id:
                    update_data = {
                        'categoriaNombre': categoria_nombre,
                        'subcategoriaNombre': subcategoria_nombre if subcategoria_nombre != "(Ninguna)" else ""
                    }
                    
                    try:
                        self.firebase_client.update_transaccion(
                            self. proyecto_id,
                            trans_id,
                            update_data
                        )
                        logger.debug(f"Updated transaction {trans_id} with category names")
                    except Exception as e:
                        logger.warning(f"Could not update category names: {e}")
                
                if self.attachment_files:
                    self._upload_attachments(trans_id)
                
                logger.info(f"Transaction {trans_id} created successfully")
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Error saving transaction: {e}")
            QMessageBox.critical(self, "Error", f"Error al guardar la transacción:\n{str(e)}")
    
    def _upload_attachments(self, trans_id:  str):
        """Upload attachment files to Firebase Storage"""
        if not self.attachment_files:
            return
        
        uploaded_urls = list(self.existing_attachments)
        uploaded_paths = []
        
        if hasattr(self, 'transaction_data') and self.transaction_data:
            uploaded_paths = list(self.transaction_data.get('adjuntos_paths', []))
        
        for file_path in self.attachment_files:
            try:
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                if file_size > 10: 
                    QMessageBox.warning(
                        self,
                        "Archivo muy grande",
                        f"El archivo {os.path.basename(file_path)} es muy grande ({file_size:.2f} MB).\n"
                        "El límite es 10 MB."
                    )
                    continue
                
                result = self.firebase_client.upload_attachment(
                    proyecto_id=self.proyecto_id,
                    transaccion_id=trans_id,
                    file_path=file_path
                )
                
                if result:
                    url, storage_path = result
                    uploaded_urls.append(url)
                    uploaded_paths.append(storage_path)
                    logger.info(f"Uploaded attachment: {file_path}")
                    
            except Exception as e: 
                logger.error(f"Error uploading {file_path}: {e}")
        
        if uploaded_urls != self.existing_attachments or uploaded_paths: 
            try:
                update_data = {
                    'adjuntos':  uploaded_urls,
                    'adjuntos_paths': uploaded_paths
                }
                
                self.firebase_client.update_transaccion(
                    self.proyecto_id,
                    trans_id,
                    update_data
                )
                
                logger.info(f"Updated transaction with {len(uploaded_urls)} attachments")
                
            except Exception as e: 
                logger.error(f"Error updating transaction with attachments: {e}")