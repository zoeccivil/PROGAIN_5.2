"""
Header - Barra superior moderna completa

Componente de header con:
- Título dinámico
- Selector de proyecto/empresa (desde Firebase)
- Buscador global
- Notificaciones
- Usuario
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont

from ..components.icon_manager import icon_manager
from ..theme_config import COLORS, BORDER

import logging
logger = logging.getLogger(__name__)


class Header(QWidget):
    """
    Header moderno completo con selector de proyecto.
    
    Señales:
        project_changed(str, str): Emitida cuando cambia el proyecto (id, nombre)
        search_triggered(str): Emitida cuando se busca algo
        notifications_clicked(): Emitida cuando se hace click en notificaciones
        user_clicked(): Emitida cuando se hace click en usuario
    """
    
    project_changed = pyqtSignal(str, str)  # (proyecto_id, proyecto_nombre)
    search_triggered = pyqtSignal(str)
    notifications_clicked = pyqtSignal()
    user_clicked = pyqtSignal()
    
    def __init__(self, firebase_client=None, parent=None):
        super().__init__(parent)
        self.firebase_client = firebase_client
        self.current_title = "Control de Obra"
        self.projects = []
        self._loading_projects = False  # Flag para evitar señales durante carga
        
        self.setup_ui()
        
        # Cargar proyectos si tenemos firebase_client
        if self.firebase_client:
            self.load_projects()
    
    def setup_ui(self):
        """Crear la UI del header con diseño optimizado"""
        
        # ✅ Altura fija y compacta
        self.setFixedHeight(64)
        
        # Estilo del header
        self.setStyleSheet(f"""
            Header {{
                background-color: {COLORS['white']};
                border-bottom: 1px solid {COLORS['slate_200']};
            }}
        """)
        
        # Layout horizontal principal
        layout = QHBoxLayout(self)
        layout.setSpacing(20)  # ✅ Espaciado uniforme
        layout.setContentsMargins(24, 0, 24, 0)  # ✅ Márgenes balanceados
        
        # === SECCIÓN IZQUIERDA: Título ===
        self.title_label = QLabel(self.current_title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['slate_900']};
                background-color: transparent;
            }}
        """)
        self.title_label.setMinimumWidth(180)  # ✅ Ancho mínimo para estabilidad
        
        layout.addWidget(self.title_label)
        
        # === SECCIÓN CENTRO: Selector de Proyecto + Buscador ===
        center_container = QWidget()
        center_container.setStyleSheet("background-color: transparent;")
        center_layout = QHBoxLayout(center_container)
        center_layout.setSpacing(16)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Selector de Proyecto ---
        project_container = QWidget()
        project_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['slate_50']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
                padding: 0px;
            }}
            QWidget:hover {{
                background-color: {COLORS['slate_100']};
                border-color: {COLORS['slate_300']};
            }}
        """)
        
        project_layout = QHBoxLayout(project_container)
        project_layout.setContentsMargins(12, 6, 12, 6)
        project_layout.setSpacing(10)
        
        # Icono de proyecto
        self.project_icon = QLabel()
        icon_pixmap = icon_manager.get_pixmap('building-2', COLORS['slate_600'], 20)
        self.project_icon.setPixmap(icon_pixmap)
        self.project_icon.setStyleSheet("background-color: transparent;")
        project_layout.addWidget(self.project_icon)
        
        # ComboBox de proyectos
        self.project_selector = QComboBox()
        self.project_selector.setMinimumWidth(320)  # ✅ Ancho óptimo
        
        project_font = QFont()
        project_font.setPointSize(13)
        project_font.setWeight(QFont.Weight.DemiBold)
        self.project_selector.setFont(project_font)
        
        self.project_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: transparent;
                border: none;
                color: {COLORS['slate_800']};
                padding: 6px 10px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['slate_600']};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius: 8px;
                selection-background-color: {COLORS['blue_50']};
                selection-color: {COLORS['slate_900']};
                padding: 6px;
                outline: none;
                min-width: 340px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 12px 16px;
                min-height: 40px;
                border-radius: 6px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS['slate_100']};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {COLORS['blue_100']};
                color: {COLORS['slate_900']};
            }}
        """)
        
        self.project_selector.currentIndexChanged.connect(self._on_project_changed)
        project_layout.addWidget(self.project_selector)
        
        center_layout.addWidget(project_container)
        
        # --- Buscador ---
        search_container = QWidget()
        search_container.setFixedWidth(300)  # ✅ Ancho balanceado
        search_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['slate_50']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
                padding: 0px;
            }}
            QWidget:focus-within {{
                border-color: {COLORS['blue_500']};
                background-color: {COLORS['white']};
            }}
        """)
        
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 8, 12, 8)
        search_layout.setSpacing(10)
        
        # Icono de búsqueda
        search_icon = QLabel()
        search_icon_pixmap = icon_manager.get_pixmap('search', COLORS['slate_400'], 18)
        search_icon.setPixmap(search_icon_pixmap)
        search_icon.setStyleSheet("background-color: transparent;")
        search_layout.addWidget(search_icon)
        
        # Input de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar transacciones...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                border: none;
                color: {COLORS['slate_900']};
                font-size: 13px;
                padding: 0px;
            }}
            QLineEdit::placeholder {{
                color: {COLORS['slate_400']};
            }}
        """)
        self.search_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        
        center_layout.addWidget(search_container)
        
        layout.addWidget(center_container)
        
        # ✅ ESPACIADOR FLEXIBLE (empuja botones a la derecha)
        layout.addStretch()
        
        # === SECCIÓN DERECHA: Notificaciones + Usuario ===
        right_container = QWidget()
        right_container.setStyleSheet("background-color: transparent;")
        right_layout = QHBoxLayout(right_container)
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Notificaciones ---
        self.notif_button = QPushButton()
        self.notif_button.setFixedSize(40, 40)
        self.notif_button.setCursor(Qt.CursorShape.PointingHandCursor)
        notif_icon = icon_manager.get_icon('bell', COLORS['slate_600'], 20)
        self.notif_button.setIcon(notif_icon)
        self.notif_button.setIconSize(QSize(20, 20))
        self.notif_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['slate_100']};
                border-color: {COLORS['slate_300']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['slate_200']};
            }}
        """)
        self.notif_button.clicked.connect(self.notifications_clicked.emit)
        right_layout.addWidget(self.notif_button)
        
        # --- Usuario ---
        self.user_button = QPushButton()
        self.user_button.setFixedSize(40, 40)
        self.user_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.user_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['slate_200']};
                border: 2px solid {COLORS['slate_300']};
                border-radius: 20px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['slate_300']};
                border-color: {COLORS['slate_400']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['slate_400']};
            }}
        """)
        self.user_button.setText("👤")
        self.user_button.clicked.connect(self.user_clicked.emit)
        right_layout.addWidget(self.user_button)
        
        layout.addWidget(right_container)
    
    # ==================== PROJECT MANAGEMENT ====================
    
    def load_projects(self):
        """Cargar proyectos desde Firebase"""
        if not self.firebase_client:
            logger.warning("No firebase_client configured")
            return
        
        try:
            self._loading_projects = True
            
            logger.info("Loading projects from Firebase")
            proyectos_raw = self.firebase_client.get_proyectos()
            
            # Normalizar resultados
            self.projects = []
            for p in proyectos_raw:
                if hasattr(p, 'to_dict'):
                    data = p.to_dict() or {}
                    proj_id = p.id
                    proj_nombre = data.get('nombre', f'Proyecto {proj_id}')
                else:
                    proj_id = p.get('id', '')
                    proj_nombre = p.get('nombre', f'Proyecto {proj_id}')
                
                self.projects.append({
                    'id': str(proj_id),
                    'nombre': proj_nombre
                })
            
            # Poblar combo
            self.project_selector.clear()
            
            # Agregar "Vista Global"
            self.project_selector.addItem("🌎 Vista Global (Todas)", "all")
            
            # Agregar proyectos individuales
            for proyecto in self.projects:
                self.project_selector.addItem(proyecto['nombre'], proyecto['id'])
            
            logger.info(f"Loaded {len(self.projects)} projects")
            
        except Exception as e:
            logger.error(f"Error loading projects: {e}")
        finally:
            self._loading_projects = False
    
    def set_current_project(self, proyecto_id: str, proyecto_nombre: str = None):
        """
        Establecer el proyecto actual en el selector.
        
        Args:
            proyecto_id: ID del proyecto
            proyecto_nombre: Nombre del proyecto (opcional)
        """
        self._loading_projects = True
        
        try:
            # Buscar y seleccionar el proyecto
            for i in range(self.project_selector.count()):
                if str(self.project_selector.itemData(i)) == str(proyecto_id):
                    self.project_selector.setCurrentIndex(i)
                    break
            
            # Actualizar título si se proporciona nombre
            if proyecto_nombre:
                self.set_title(f"Control de Obra - {proyecto_nombre}")
        
        finally:
            self._loading_projects = False
    
    def _on_project_changed(self, index: int):
        """Handle project selection change"""
        if self._loading_projects:
            return
        
        if index < 0:
            return
        
        project_id = self.project_selector.itemData(index)
        project_name = self.project_selector.itemText(index)
        
        logger.info(f"Project changed: {project_name} ({project_id})")
        
        # Emitir señal
        self.project_changed.emit(str(project_id), project_name)
        
        # Actualizar título
        if project_id == "all":
            self.set_title("Control de Obra - Vista Global")
        else:
            self.set_title(f"Control de Obra - {project_name}")
    
    # ==================== OTHER METHODS ====================
    
    def set_title(self, title: str):
        """Cambiar el título del header"""
        self.current_title = title
        self.title_label.setText(title)
    
    def _on_search(self):
        """Handle search"""
        search_text = self.search_input.text().strip()
        if search_text:
            logger.info(f"Search triggered: {search_text}")
            self.search_triggered.emit(search_text)
    
    def clear_search(self):
        """Limpiar campo de búsqueda"""
        self.search_input.clear()