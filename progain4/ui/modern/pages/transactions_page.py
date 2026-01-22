"""
Transactions Page - Página de transacciones optimizada con tabla y filtros

Integra el TransactionsWidget del sistema anterior con UI moderna. 
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..  theme_config import COLORS, FONTS, SPACING, get_button_style
from ..components.clean_card import CleanCard
from ..dialogs.transaction_dialog_modern import ModernTransactionDialog

# Import optimized TransactionsWidget from classic UI
from progain4.ui.widgets.transactions_widget import TransactionsWidget

import logging

logger = logging.getLogger(__name__)


class TransactionsPage(QWidget):
    """
    Página de transacciones optimizada. 
    
    Features:
    - Reutiliza TransactionsWidget del sistema anterior (optimizado)
    - Resumen visual moderno arriba
    - Diálogo moderno para agregar/editar
    - Integración completa con Firebase
    
    Señales:
        transaction_saved:  Emitida cuando se guarda una transacción
    """
    
    transaction_saved = pyqtSignal()
    
    def __init__(self, firebase_client, proyecto_id:  str, proyecto_nombre: str = None, account_service=None, parent=None):
        """
        Inicializar transactions page.
        
        Args:
            firebase_client:  Instancia de FirebaseClient
            proyecto_id: ID del proyecto activo
            proyecto_nombre:  Nombre del proyecto (opcional)
            account_service: Instancia de AccountService
            parent: Widget padre
        """
        super().__init__(parent)
        
        self.firebase_client = firebase_client
        self.proyecto_id = str(proyecto_id)
        self.proyecto_nombre = proyecto_nombre or f"Proyecto {proyecto_id}"  # ✅ AGREGADO
        self.account_service = account_service
        
        # Cache de datos
        self._cuentas_cache = None
        self._categorias_cache = None
        self._subcategorias_cache = None
        self._transacciones_cache = []
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Crear la UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(SPACING['xl'])
        main_layout.setContentsMargins(
            SPACING['3xl'], 
            SPACING['3xl'], 
            SPACING['3xl'], 
            SPACING['3xl']
        )
        
        # === HEADER ===
        header_layout = QHBoxLayout()
        
        title = QLabel("💰 Transacciones")
        title_font = QFont()
        title_font.setPointSize(FONTS['size_3xl'])
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón agregar
        self.btn_add = QPushButton("+ Nueva Transacción")
        self.btn_add.setMinimumHeight(44)
        self.btn_add.setMinimumWidth(180)
        self.btn_add.setStyleSheet(get_button_style('primary'))
        self.btn_add.clicked.connect(self._on_add_transaction)
        header_layout.addWidget(self. btn_add)
        
        main_layout.addLayout(header_layout)
        
        # === RESUMEN ===
        self.summary_card = self._create_summary_card()
        main_layout.addWidget(self.summary_card)
        
        # === TRANSACTIONS WIDGET (del sistema anterior) ===
        self.transactions_widget = TransactionsWidget()
        
        # Conectar señales
        self. transactions_widget.transaction_double_clicked.connect(self._on_edit_transaction)
        self.transactions_widget.transaction_deleted.connect(self._on_delete_transaction)
        
        main_layout.addWidget(self.transactions_widget)
    
    def _create_summary_card(self) -> QWidget:
        """Crear tarjeta de resumen"""
        card = CleanCard(padding=SPACING['xl'])
        
        layout = QHBoxLayout(card)
        layout.setSpacing(SPACING['3xl'])
        
        # Total transacciones
        self.lbl_total = self._create_metric_widget("0", "Transacciones")
        layout.addWidget(self.lbl_total)
        
        # Ingresos
        self.lbl_ingresos = self._create_metric_widget("RD$ 0.00", "Ingresos", COLORS['green_600'])
        layout.addWidget(self.lbl_ingresos)
        
        # Gastos
        self.lbl_gastos = self._create_metric_widget("RD$ 0.00", "Gastos", COLORS['red_600'])
        layout.addWidget(self. lbl_gastos)
        
        # Balance
        self.lbl_balance = self._create_metric_widget("RD$ 0.00", "Balance")
        layout.addWidget(self.lbl_balance)
        
        layout.addStretch()
        
        return card
    
    def _create_metric_widget(self, value: str, label: str, color: str = None) -> QWidget:
        """Crear widget de métrica"""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(4)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Valor
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(FONTS['size_2xl'])
        value_font. setWeight(QFont.Weight. Bold)
        value_label. setFont(value_font)
        value_label.setStyleSheet(f"color: {color or COLORS['slate_900']};")
        container_layout.addWidget(value_label)
        
        # Label
        text_label = QLabel(label)
        text_label.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: {FONTS['size_sm']}px;")
        container_layout. addWidget(text_label)
        
        # Guardar referencia para actualizar
        container.value_label = value_label
        
        return container
    
    def load_data(self):
        """Cargar datos desde Firebase (con caché)"""
        try:
            logger.info(f"Loading data for project {self.proyecto_id}")
            
            # === 1. CARGAR CUENTAS ===
            if self._cuentas_cache is None:
                self._cuentas_cache = self.firebase_client.get_cuentas_by_proyecto(self.proyecto_id)
                logger.info(f"✅ Loaded {len(self._cuentas_cache)} accounts")
            
            # === 2. CARGAR CATEGORÍAS Y SUBCATEGORÍAS ===
            if self._categorias_cache is None:
                try:
                    self._categorias_cache = self.firebase_client.get_categorias_por_proyecto(self.proyecto_id)
                    self._subcategorias_cache = self.firebase_client.get_subcategorias_por_proyecto(self.proyecto_id)
                    logger.info(f"✅ Loaded {len(self._categorias_cache)} categories, {len(self._subcategorias_cache)} subcategories")
                except: 
                    # Fallback to global
                    self._categorias_cache = self.firebase_client.get_categorias_maestras() or []
                    self._subcategorias_cache = self.firebase_client.get_subcategorias_maestras() or []
                    logger.warning("Using global catalog as fallback")
            
            # === 3. CARGAR TRANSACCIONES ===
            transacciones = self.firebase_client.get_transacciones_by_proyecto(
                self.proyecto_id,
                cuenta_id=None  # Todas las cuentas
            )
            self._transacciones_cache = transacciones
            logger.info(f"✅ Loaded {len(transacciones)} transactions")
            
            # === 4. PASAR DATOS AL WIDGET ===
            self. transactions_widget.set_cuentas_map(self._cuentas_cache)
            self.transactions_widget.set_categorias_map(self._categorias_cache)
            self.transactions_widget.set_subcategorias_map(self._subcategorias_cache)
            self.transactions_widget.load_transactions(transacciones)
            
            # === 5. ACTUALIZAR RESUMEN ===
            self._update_summary(transacciones)
            
        except Exception as e:
            logger.error(f"Error loading data: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar datos:\n{str(e)}"
            )
    
    def _update_summary(self, transacciones: list):
        """Actualizar tarjeta de resumen"""
        try:
            total = len(transacciones)
            
            ingresos = sum(
                float(t.get('monto', 0)) 
                for t in transacciones 
                if t.get('tipo', '').lower() == 'ingreso'
            )
            
            gastos = sum(
                float(t.get('monto', 0)) 
                for t in transacciones 
                if t.get('tipo', '').lower() == 'gasto'
            )
            
            balance = ingresos - gastos
            
            # Actualizar labels
            self.lbl_total.value_label.setText(str(total))
            self.lbl_ingresos.value_label.setText(f"RD$ {ingresos: ,.2f}")
            self.lbl_gastos.value_label.setText(f"RD$ {gastos:,.2f}")
            self.lbl_balance.value_label.setText(f"RD$ {balance: ,.2f}")
            
            # Color del balance
            if balance >= 0:
                self.lbl_balance.value_label.setStyleSheet(f"color: {COLORS['green_600']};")
            else:
                self.lbl_balance.value_label.setStyleSheet(f"color: {COLORS['red_600']};")
                
        except Exception as e: 
            logger.error(f"Error updating summary: {e}")
    
    def _on_add_transaction(self):
        """Abrir diálogo para agregar nueva transacción"""
        try:
            dialog = ModernTransactionDialog(
                firebase_client=self.firebase_client,
                proyecto_id=self. proyecto_id,
                proyecto_nombre=self.proyecto_nombre,  # ✅ AGREGADO
                cuentas=self._cuentas_cache,
                categorias=self._categorias_cache,
                subcategorias=self._subcategorias_cache,
                parent=self
            )
            
            if dialog.exec():
                logger.info("Transaction created successfully")
                QMessageBox.information(
                    self,
                    "Éxito",
                    "Transacción creada correctamente."
                )
                
                # Refrescar datos
                self.refresh()
                self.transaction_saved.emit()
                
        except Exception as e:
            logger.error(f"Error opening add dialog: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir el diálogo:\n{str(e)}"
            )
    
    def _on_edit_transaction(self, trans_id: str):
        """Abrir diálogo para editar transacción"""
        try:
            logger.info(f"Opening edit dialog for transaction {trans_id}")
            
            dialog = ModernTransactionDialog(
                firebase_client=self.firebase_client,
                proyecto_id=self.proyecto_id,
                proyecto_nombre=self.proyecto_nombre,  # ✅ AGREGADO
                cuentas=self._cuentas_cache,
                categorias=self._categorias_cache,
                subcategorias=self._subcategorias_cache,
                parent=self,
                transaction_id=trans_id
            )
            
            if dialog.exec():
                logger.info(f"Transaction {trans_id} updated successfully")
                QMessageBox. information(
                    self,
                    "Éxito",
                    "Transacción actualizada correctamente."
                )
                
                # Refrescar datos
                self.refresh()
                self.transaction_saved. emit()
                
        except Exception as e:
            logger.error(f"Error opening edit dialog:  {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir el diálogo:\n{str(e)}"
            )
    
    def _on_delete_transaction(self, trans_id: str):
        """Anular transacción"""
        try:
            logger.info(f"Anulando transacción {trans_id}")
            
            # Actualizar transacción marcándola como anulada
            success = self.firebase_client.update_transaccion(
                self.proyecto_id,
                trans_id,
                {'anulada': True}
            )
            
            if success:
                logger.info(f"Transaction {trans_id} anulada successfully")
                QMessageBox. information(
                    self,
                    "Éxito",
                    "Transacción anulada correctamente."
                )
                
                # Refrescar datos
                self.refresh()
                self.transaction_saved.emit()
            else:
                raise Exception("No se pudo anular la transacción")
                
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al anular la transacción:\n{str(e)}"
            )
    
    def refresh(self):
        """Refrescar datos (sin caché)"""
        # Limpiar caché
        self._transacciones_cache = []
        
        # Recargar
        self.load_data()
    
    def clear_cache(self):
        """Limpiar toda la caché"""
        self._cuentas_cache = None
        self._categorias_cache = None
        self._subcategorias_cache = None
        self._transacciones_cache = []
        logger.info("Cache cleared")