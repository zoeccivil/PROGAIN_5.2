"""
Transactions Page - Página de transacciones optimizada con tabla y filtros

Integra el TransactionsWidget del sistema anterior con UI moderna.    
Incluye botones de Transferencia, Undo/Redo y toolbar completo con iconos SVG.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QToolBar, QMenu, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QAction, QShortcut, QKeySequence, QIcon

# ✅ Imports absolutos (Modern UI)
from progain4.ui.modern.theme_config import COLORS, FONTS, SPACING, get_button_style
from progain4.ui.modern. components.clean_card import CleanCard
from progain4.ui.modern.dialogs.transaction_dialog_modern import ModernTransactionDialog

# ✅ Import dialogs from classic UI
from progain4.ui.dialogs.transfer_dialog import TransferDialog

# ✅ Import optimized TransactionsWidget from classic UI
from progain4.ui.widgets.transactions_widget import TransactionsWidget

# ✅ Import Undo/Redo Manager
from progain4.services.undo_manager import UndoRedoManager

# ✅ Import IconManager para iconos SVG
from progain4.ui.modern.components.icon_manager import icon_manager

import logging

logger = logging.getLogger(__name__)


class TransactionsPage(QWidget):
    """
    Página de transacciones optimizada.   
    
    Features:
    - Reutiliza TransactionsWidget del sistema anterior (optimizado)
    - Resumen visual moderno arriba
    - Diálogo moderno para agregar/editar
    - Botón de Transferencia
    - Sistema Undo/Redo completo
    - Toolbar con iconos SVG monocromáticos
    - Integración completa con Firebase
    
    Señales:
        transaction_saved: Emitida cuando se guarda una transacción
    """
    
    transaction_saved = pyqtSignal()
    
    def __init__(
        self, 
        firebase_client, 
        proyecto_id:   str, 
        proyecto_nombre: str = None, 
        config_manager=None,
        account_service=None, 
        parent=None
    ):
        """
        Inicializar transactions page.  
        
        Args:
            firebase_client:   Instancia de FirebaseClient
            proyecto_id:   ID del proyecto activo
            proyecto_nombre:  Nombre del proyecto (opcional)
            config_manager:   Instancia de ConfigManager (opcional, se crea si es None)
            account_service:   Instancia de AccountService
            parent:  Widget padre
        """
        super().__init__(parent)
        
        self.firebase_client = firebase_client
        self.proyecto_id = str(proyecto_id)
        self.proyecto_nombre = proyecto_nombre or f"Proyecto {proyecto_id}"
        
        # ✅ VALIDACIÓN:   Crear ConfigManager si no se proporciona
        if config_manager is None:
            from progain4.services.config import ConfigManager
            config_manager = ConfigManager()
            logger.warning("⚠️ ConfigManager not provided, creating new instance")
        
        self.config_manager = config_manager
        self.account_service = account_service
        
        # Cache de datos
        self._cuentas_cache = None
        self._categorias_cache = None
        self._subcategorias_cache = None
        self._transacciones_cache = []
        
        # ✅ Undo/Redo Manager
        try:
            self.undo_manager = UndoRedoManager(
                self.firebase_client,
                self.config_manager
            )
            logger.info("✅ UndoRedoManager initialized successfully")
        except Exception as e: 
            logger.error(f"❌ Error initializing UndoRedoManager: {e}")
            self.undo_manager = None
        
        # Referencias a acciones
        self.action_undo = None
        self.action_redo = None
        self.btn_undo = None
        self.btn_redo = None
        
        self.setup_ui()
        self._setup_shortcuts()
        self. load_data()
    
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
        title_font. setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['slate_900']};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # ✅ NUEVO: Toolbar de acciones (más compacto)
        self.toolbar = self._create_toolbar()
        header_layout.addWidget(self. toolbar)
        
        main_layout.addLayout(header_layout)
        
        # === RESUMEN ===
        self.summary_card = self._create_summary_card()
        main_layout.addWidget(self.summary_card)
        
        # === TRANSACTIONS WIDGET (del sistema anterior) ===
        self.transactions_widget = TransactionsWidget()
        
        # Conectar señales
        self.transactions_widget.transaction_double_clicked.connect(self._on_edit_transaction)
        self.transactions_widget.transaction_deleted.connect(self._on_delete_transaction)
        
        main_layout.addWidget(self. transactions_widget)
    
    def _create_toolbar(self) -> QToolBar:
        """
        Crear toolbar con todas las acciones e iconos SVG.
        
        ✅ Botones más pequeños (36px) con iconos SVG monocromáticos
        """
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: transparent;
                border: none;
                spacing: {SPACING['sm']}px;
            }}
            QToolBar QToolButton {{
                min-height: 36px;
                min-width: 36px;
                border-radius: 6px;
                padding: 6px;
                background-color: {COLORS['slate_100']};
                border: 1px solid {COLORS['slate_200']};
                font-weight: 600;
            }}
            QToolBar QToolButton:hover {{
                background-color: {COLORS['slate_200']};
                border-color: {COLORS['slate_300']};
            }}
            QToolBar QToolButton:pressed {{
                background-color: {COLORS['slate_300']};
            }}
            QToolBar QToolButton:disabled {{
                background-color: {COLORS['slate_50']};
                border-color: {COLORS['slate_100']};
                opacity: 0.5;
            }}
        """)
        
        # ✅ Botón:  Nueva Transacción
        action_add = QAction("+ Nueva", self)
        action_add.setIcon(icon_manager.get_icon("plus", COLORS['blue_600'], 20))
        action_add.setToolTip("Agregar nueva transacción (Ctrl+N)")
        action_add.triggered.connect(self._on_add_transaction)  # ✅ CONECTAR
        toolbar.addAction(action_add)  # ✅ AGREGAR AL TOOLBAR
        
        # ✅ Botón:  Transferencia
        action_transfer = QAction("🔄 Transferencia", self)
        action_transfer.setIcon(icon_manager.get_icon("arrow-left-right", COLORS['purple_600'], 20))
        action_transfer.setToolTip("Crear transferencia entre cuentas")
        action_transfer.triggered. connect(self._on_add_transfer)  # ✅ CONECTAR
        toolbar.addAction(action_transfer)  # ✅ AGREGAR AL TOOLBAR
        
        toolbar.addSeparator()  # ✅ Separador visual
        
        # ✅ Botón: Undo
        self.action_undo = QAction("⏪", self)
        self.action_undo.setIcon(icon_manager.get_icon("undo-2", COLORS['slate_600'], 20))
        self.action_undo.setToolTip("Deshacer (Ctrl+Z)")
        self.action_undo.setEnabled(False)
        self.action_undo. triggered.connect(self._perform_undo)  # ✅ CONECTAR
        toolbar.addAction(self.action_undo)  # ✅ AGREGAR AL TOOLBAR
        
        # ✅ Botón: Redo
        self.action_redo = QAction("⏩", self)
        self.action_redo.setIcon(icon_manager.get_icon("redo-2", COLORS['slate_600'], 20))
        self.action_redo.setToolTip("Rehacer (Ctrl+Y)")
        self.action_redo.setEnabled(False)
        self.action_redo.triggered.connect(self._perform_redo)  # ✅ CONECTAR
        toolbar.addAction(self.action_redo)  # ✅ AGREGAR AL TOOLBAR
        
        toolbar.addSeparator()  # ✅ Separador visual
        
        # ✅ Botón: Refrescar
        action_refresh = QAction("🔄", self)
        action_refresh. setIcon(icon_manager.get_icon("refresh-cw", COLORS['slate_600'], 20))
        action_refresh.setToolTip("Refrescar transacciones (F5)")
        action_refresh. triggered.connect(self. refresh)  # ✅ CONECTAR
        toolbar.addAction(action_refresh)  # ✅ AGREGAR AL TOOLBAR
        
        # ✅ Botón:  Historial
        action_history = QAction("📋", self)
        action_history.setIcon(icon_manager. get_icon("history", COLORS['slate_600'], 20))
        action_history. setToolTip("Ver historial de cambios")
        action_history.triggered. connect(self._show_undo_history)  # ✅ CONECTAR
        toolbar. addAction(action_history)  # ✅ AGREGAR AL TOOLBAR
        
        return toolbar
    
    def _setup_shortcuts(self):
        """
        Configurar atajos de teclado. 
        
        ✅ Atajos para Undo/Redo
        """
        # Undo:  Ctrl+Z
        undo_shortcut = QShortcut(QKeySequence.StandardKey. Undo, self)
        undo_shortcut.activated.connect(self._perform_undo)
        
        # Redo:  Ctrl+Y o Ctrl+Shift+Z
        redo_shortcut1 = QShortcut(QKeySequence.StandardKey. Redo, self)
        redo_shortcut1.activated. connect(self._perform_redo)
        
        redo_shortcut2 = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        redo_shortcut2.activated.connect(self._perform_redo)
        
        # Nueva transacción: Ctrl+N
        new_shortcut = QShortcut(QKeySequence.StandardKey.New, self)
        new_shortcut.activated.connect(self._on_add_transaction)
        
        # Refrescar: F5
        refresh_shortcut = QShortcut(QKeySequence. StandardKey.Refresh, self)
        refresh_shortcut.activated.connect(self.refresh)
        
        logger.info("✅ Keyboard shortcuts configured")
    
    def _create_summary_card(self) -> QWidget:
        """Crear tarjeta de resumen"""
        card = CleanCard(padding=SPACING['xl'])
        
        layout = QHBoxLayout(card)
        layout.setSpacing(SPACING['3xl'])
        
        # Total transacciones
        self. lbl_total = self._create_metric_widget("0", "Transacciones")
        layout.addWidget(self. lbl_total)
        
        # Ingresos
        self.lbl_ingresos = self._create_metric_widget("RD$ 0.00", "Ingresos", COLORS['green_600'])
        layout.addWidget(self.lbl_ingresos)
        
        # Gastos
        self.lbl_gastos = self._create_metric_widget("RD$ 0.00", "Gastos", COLORS['red_600'])
        layout.addWidget(self.lbl_gastos)
        
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
        value_font. setWeight(QFont.Weight.Bold)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color or COLORS['slate_900']};")
        container_layout.addWidget(value_label)
        
        # Label
        text_label = QLabel(label)
        text_label.setStyleSheet(f"color: {COLORS['slate_600']}; font-size: {FONTS['size_sm']}px;")
        container_layout.addWidget(text_label)
        
        # Guardar referencia para actualizar
        container.value_label = value_label
        
        return container
    
    def load_data(self):
        """Cargar datos desde Firebase (con caché)"""
        try:
            logger.info(f"Loading data for project {self.proyecto_id}")
            
            # === 1. CARGAR CUENTAS ===
            if self._cuentas_cache is None:
                self._cuentas_cache = self. firebase_client.get_cuentas_by_proyecto(self.proyecto_id)
                logger.info(f"✅ Loaded {len(self._cuentas_cache)} accounts")
            
            # === 2. CARGAR CATEGORÍAS Y SUBCATEGORÍAS ===
            if self._categorias_cache is None:
                try:
                    self._categorias_cache = self.firebase_client.get_categorias_por_proyecto(self.proyecto_id)
                    self._subcategorias_cache = self.firebase_client.get_subcategorias_activas_por_proyecto(self.proyecto_id)
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
            self.transactions_widget.set_cuentas_map(self._cuentas_cache)
            self.transactions_widget.set_categorias_map(self._categorias_cache)
            self.transactions_widget.set_subcategorias_map(self._subcategorias_cache)
            self.transactions_widget.load_transactions(transacciones)
            
            # === 5. ACTUALIZAR RESUMEN ===
            self._update_summary(transacciones)
            
            # ✅ Actualizar estado de Undo/Redo
            self._update_undo_redo_state()
            
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
                if t.get('tipo', '').lower() == 'ingreso' and not t.get('es_transferencia', False)
            )
            
            gastos = sum(
                float(t.get('monto', 0)) 
                for t in transacciones 
                if t.get('tipo', '').lower() == 'gasto' and not t.get('es_transferencia', False)
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
                proyecto_id=self.proyecto_id,
                proyecto_nombre=self.proyecto_nombre,
                cuentas=self._cuentas_cache,
                categorias=self._categorias_cache,
                subcategorias=self._subcategorias_cache,
                parent=self
            )
            
            # ✅ Ejecutar diálogo y verificar resultado
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                logger.info("Transaction created successfully")
                
                # ✅ NUEVO: Refrescar INMEDIATAMENTE sin mensaje
                self.refresh()
                
                # ✅ Emitir señal para otros componentes
                self.transaction_saved.emit()
                
                # ✅ Mensaje de éxito OPCIONAL (puedes quitarlo si prefieres silencioso)
                # QMessageBox.information(
                #     self,
                #     "Éxito",
                #     "Transacción creada correctamente."
                # )
                
                logger.info("✅ Transactions page refreshed after save")
            else:
                logger.info("Transaction creation cancelled by user")
                
        except Exception as e:
            logger.error(f"Error opening add dialog: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir el diálogo:\n{str(e)}"
            )
    
    def _on_add_transfer(self):
        """Abrir diálogo para crear transferencia."""
        try:  
            # Validar que hay al menos 2 cuentas
            if len(self._cuentas_cache) < 2:
                QMessageBox.warning(
                    self,
                    "Transferencias",
                    "Necesita al menos 2 cuentas en el proyecto para crear transferencias."
                )
                return
            
            dialog = TransferDialog(
                firebase_client=self.firebase_client,
                proyecto_id=self.proyecto_id,
                cuentas=self._cuentas_cache,
                parent=self
            )
            
            if dialog.exec():
                logger. info("Transfer created successfully")
                QMessageBox.information(
                    self,
                    "Éxito",
                    "Transferencia creada correctamente."
                )
                
                # Refrescar datos
                self.refresh()
                self.transaction_saved.emit()
                
        except Exception as e:
            logger.error(f"Error opening transfer dialog: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir el diálogo de transferencia:\n{str(e)}"
            )
    
    def _on_edit_transaction(self, trans_id: str):
        """Abrir diálogo para editar transacción"""
        try:
            logger.info(f"Opening edit dialog for transaction {trans_id}")
            
            dialog = ModernTransactionDialog(
                firebase_client=self.firebase_client,
                proyecto_id=self.proyecto_id,
                proyecto_nombre=self.proyecto_nombre,
                cuentas=self._cuentas_cache,
                categorias=self._categorias_cache,
                subcategorias=self._subcategorias_cache,
                parent=self,
                transaction_id=trans_id  # ✅ Pasar ID para edición
            )
            
            # ✅ Ejecutar diálogo y verificar resultado
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                logger.info(f"Transaction {trans_id} updated successfully")
                
                # ✅ NUEVO: Refrescar INMEDIATAMENTE sin mensaje
                self.refresh()
                
                # ✅ Emitir señal para otros componentes
                self.transaction_saved.emit()
                
                # ✅ Mensaje de éxito OPCIONAL
                # QMessageBox.information(
                #     self,
                #     "Éxito",
                #     "Transacción actualizada correctamente."
                # )
                
                logger.info("✅ Transactions page refreshed after update")
            else:
                logger.info("Transaction edit cancelled by user")
                
        except Exception as e:
            logger.error(f"Error opening edit dialog: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir el diálogo:\n{str(e)}"
            )
    
    def _on_delete_transaction(self, trans_id: str):
        """Anular transacción"""
        try:
            logger.info(f"Anulando transacción {trans_id}")
            
            # ✅ Confirmar antes de anular
            reply = QMessageBox.question(
                self,
                "Confirmar Anulación",
                "¿Está seguro que desea anular esta transacción?\n\n"
                "Esta acción marcará la transacción como anulada.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                logger.info("Transaction deletion cancelled by user")
                return
            
            # Usar soft delete (marcar como anulada)
            success = self.firebase_client.delete_transaccion(
                self.proyecto_id,
                trans_id,
                soft_delete=True
            )
            
            if success:
                logger.info(f"Transaction {trans_id} anulada successfully")
                
                # ✅ NUEVO: Refrescar INMEDIATAMENTE sin mensaje
                self.refresh()
                
                # ✅ Emitir señal para otros componentes
                self.transaction_saved.emit()
                
                # ✅ Mensaje de éxito OPCIONAL
                # QMessageBox.information(
                #     self,
                #     "Éxito",
                #     "Transacción anulada correctamente."
                # )
                
                logger.info("✅ Transactions page refreshed after delete")
            else:
                raise Exception("No se pudo anular la transacción")
                
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al anular la transacción:\n{str(e)}"
            )
    
    # ==================== UNDO/REDO METHODS ====================
    
    def _perform_undo(self):
        """Deshacer última acción."""
        if not self. undo_manager:
            return
            
        if self.undo_manager. undo(parent_widget=self):
            self.refresh()
            self._update_undo_redo_state()
            
            # Mostrar mensaje
            desc = self.undo_manager. get_redo_description()
            self.statusBar().showMessage(f"✅ Deshecho: {desc}", 3000) if hasattr(self, 'statusBar') else None
        else:
            if not self.undo_manager.can_undo():
                QMessageBox.information(
                    self,
                    "Deshacer",
                    "No hay acciones para deshacer."
                )
    
    def _perform_redo(self):
        """Rehacer última acción deshecha."""
        if not self.undo_manager:
            return
            
        if self. undo_manager.redo(parent_widget=self):
            self.refresh()
            self._update_undo_redo_state()
            
            # Mostrar mensaje
            desc = self.undo_manager.get_undo_description()
            self.statusBar().showMessage(f"✅ Rehecho: {desc}", 3000) if hasattr(self, 'statusBar') else None
        else:
            if not self. undo_manager.can_redo():
                QMessageBox. information(
                    self,
                    "Rehacer",
                    "No hay acciones para rehacer."
                )
    
    def _update_undo_redo_state(self):
        """Actualizar estado de botones Undo/Redo."""
        if not self.undo_manager:
            return
            
        can_undo = self.undo_manager.can_undo()
        can_redo = self.undo_manager.can_redo()
        
        # Actualizar acciones
        if self.action_undo:
            self.action_undo.setEnabled(can_undo)
            if can_undo:
                desc = self.undo_manager. get_undo_description()
                if len(desc) > 50: 
                    desc = desc[:50] + "..."
                self.action_undo.setToolTip(f"Deshacer: {desc}\n(Ctrl+Z)")
            else:
                self.action_undo.setToolTip("Deshacer (Ctrl+Z)")
        
        if self.action_redo:
            self.action_redo.setEnabled(can_redo)
            if can_redo:
                desc = self. undo_manager.get_redo_description()
                if len(desc) > 50:
                    desc = desc[:50] + "..."
                self.action_redo.setToolTip(f"Rehacer:  {desc}\n(Ctrl+Y)")
            else:
                self.action_redo.setToolTip("Rehacer (Ctrl+Y)")
    
    def _show_undo_history(self):
        """Mostrar diálogo con historial de cambios."""
        if not self.undo_manager:
            QMessageBox.information(self, "Historial", "Undo/Redo no disponible.")
            return
            
        try:
            from progain4. ui.dialogs.undo_history_dialog import UndoHistoryDialog
            dialog = UndoHistoryDialog(self. undo_manager, self)
            dialog.exec()
        except ImportError:
            QMessageBox.information(
                self,
                "Historial",
                f"Acciones disponibles para deshacer:  {len(self.undo_manager._undo_stack)}\n"
                f"Acciones disponibles para rehacer:  {len(self.undo_manager._redo_stack)}"
            )
        except Exception as e:
            logger.error(f"Error showing history: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar historial:\n{str(e)}")
    
    # ==================== PUBLIC METHODS ====================
    
    def refresh(self):
        """Refrescar datos forzando recarga desde Firebase"""
        logger.info("🔄 Refreshing transactions (clearing cache)...")
        
        # Limpiar caché local
        self._transacciones_cache = []
        
        # Invalidar caché del cache_manager
        try:
            from progain4.services.cache_manager import cache_manager
            cache_manager.invalidate_transacciones(self.proyecto_id)
            logger.info(f"✅ Cache invalidated for project {self.proyecto_id}")
        except Exception as e:
            logger.error(f"❌ Error invalidating cache: {e}", exc_info=True)
        
        # Recargar datos desde Firebase
        self.load_data()
        
        logger.info("✅ Refresh complete")

    def clear_cache(self):
        """Limpiar toda la caché local y global"""
        logger.info("🗑️ Clearing all cache...")
        
        # Limpiar caché local
        self._cuentas_cache = None
        self._categorias_cache = None
        self._subcategorias_cache = None
        self._transacciones_cache = []
        
        # Invalidar caché global
        try:
            from progain4.services.cache_manager import cache_manager
            
            cache_manager.invalidate_transacciones(self.proyecto_id)
            cache_manager.invalidate_cuentas(self.proyecto_id)
            cache_manager.invalidate_subcategorias_proyecto(self.proyecto_id)
            
            logger.info(f"✅ All cache cleared for project {self.proyecto_id}")
        except Exception as e:
            logger.error(f"❌ Error clearing cache: {e}", exc_info=True)
    
    def on_project_changed(self, proyecto_id: str, proyecto_nombre: str):
        """Callback cuando cambia el proyecto."""
        logger.info(f"Project changed to: {proyecto_nombre} ({proyecto_id})")
        
        # Actualizar referencias
        self.proyecto_id = str(proyecto_id)
        self.proyecto_nombre = proyecto_nombre
        
        # Limpiar caché
        self. clear_cache()
        
        # Limpiar historial de Undo/Redo
        if self.undo_manager:
            self.undo_manager. clear()
            self._update_undo_redo_state()
            logger.info("Cleared undo/redo history on project change")
        
        # Recargar datos
        self.load_data()