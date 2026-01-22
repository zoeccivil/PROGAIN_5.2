"""
Header - Barra superior moderna completa

Componente de header con:
- Título dinámico
- Selector de proyecto/empresa (desde Firebase)
- Buscador global
- Notificaciones
- Usuario
- Botón "+ Registrar"
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont

from .. components.icon_manager import icon_manager
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
        register_clicked(): Emitida cuando se hace click en "+ Registrar"
    """
    
    project_changed = pyqtSignal(str, str)  # (proyecto_id, proyecto_nombre)
    search_triggered = pyqtSignal(str)
    notifications_clicked = pyqtSignal()
    user_clicked = pyqtSignal()
    register_clicked = pyqtSignal()
    
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
        """Crear la UI del header con proporciones optimizadas"""
        
        # ✅ Altura reducida y más compacta
        self.setFixedHeight(64)
        
        # Estilo del header
        self.setStyleSheet(f"""
            Header {{
                background-color: {COLORS['white']};
                border-bottom: 1px solid {COLORS['slate_200']};
            }}
        """)
        
        # Layout horizontal
        layout = QHBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # === TÍTULO (IZQUIERDA) ===
        self.title_label = QLabel(self. current_title)
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
        
        layout.addWidget(self.title_label)
        layout.addSpacing(8)
        
        # === SELECTOR DE PROYECTO (MÁS ANCHO) ===
        project_container = QWidget()
        project_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['slate_50']};
                border:  1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
                padding: 0px;
            }}
            QWidget: hover {{
                background-color:  {COLORS['slate_100']};
                border-color: {COLORS['slate_300']};
            }}
        """)
        
        project_layout = QHBoxLayout(project_container)
        project_layout.setContentsMargins(10, 4, 10, 4)
        project_layout.setSpacing(8)
        
        # Icono de proyecto (más pequeño)
        self.project_icon = QLabel()
        icon_pixmap = icon_manager.get_pixmap('building-2', COLORS['slate_600'], 18)
        self.project_icon. setPixmap(icon_pixmap)
        self.project_icon.setStyleSheet("background-color: transparent;")
        project_layout.addWidget(self. project_icon)
        
        # ComboBox de proyectos (más ancho)
        self.project_selector = QComboBox()
        self.project_selector.setMinimumWidth(300)  # ✅ Aumentado de 250 a 300
        
        project_font = QFont()
        project_font.setPointSize(12)  # ✅ Reducido de 13 a 12
        project_font.setWeight(QFont.Weight.DemiBold)
        self.project_selector.setFont(project_font)
        
        self.project_selector.setStyleSheet(f"""
            QComboBox {{
                background-color:  transparent;
                border: none;
                color: {COLORS['slate_800']};
                padding: 6px 8px;
            }}
            QComboBox:: drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox:: down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {COLORS['slate_600']};
                margin-right: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['slate_300']};
                border-radius:  8px;
                selection-background-color: {COLORS['blue_50']};
                selection-color: {COLORS['slate_900']};
                padding: 4px;
                outline: none;
                min-width: 320px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 10px 14px;
                min-height: 36px;
                border-radius: 4px;
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
        project_layout.addWidget(self. project_selector)
        
        layout.addWidget(project_container)
        
        # === BUSCADOR (MÁS COMPACTO) ===
        search_container = QWidget()
        search_container.setFixedWidth(280)  # ✅ Reducido de 350 a 280
        search_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['slate_50']};
                border: 1px solid {COLORS['slate_200']};
                border-radius: {BORDER['radius_sm']}px;
                padding: 0px;
            }}
            QWidget:focus-within {{
                border-color:  {COLORS['blue_500']};
                background-color: {COLORS['white']};
            }}
        """)
        
        search_layout = QHBoxLayout(search_container)
        search_layout. setContentsMargins(10, 6, 10, 6)
        search_layout.setSpacing(8)
        
        # Icono de búsqueda (más pequeño)
        search_icon = QLabel()
        search_icon_pixmap = icon_manager.get_pixmap('search', COLORS['slate_400'], 16)
        search_icon.setPixmap(search_icon_pixmap)
        search_icon. setStyleSheet("background-color:  transparent;")
        search_layout.addWidget(search_icon)
        
        # Input de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar...")
        self.search_input. setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                border:  none;
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
        
        layout.addWidget(search_container)
        layout.addStretch()
        
        # === NOTIFICACIONES (MÁS PEQUEÑO) ===
        self.notif_button = QPushButton()
        self.notif_button.setFixedSize(38, 38)  # ✅ Reducido de 44 a 38
        self. notif_button.setCursor(Qt.CursorShape.PointingHandCursor)
        notif_icon = icon_manager. get_icon('bell', COLORS['slate_600'], 18)  # ✅ Icono 18px
        self.notif_button.setIcon(notif_icon)
        self.notif_button.setIconSize(QSize(18, 18))
        self.notif_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['slate_200']};
                border-radius:  {BORDER['radius_sm']}px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['slate_100']};
                border-color: {COLORS['slate_300']};
            }}
        """)
        self.notif_button.clicked. connect(self. notifications_clicked. emit)
        layout.addWidget(self.notif_button)
        
        # === USUARIO (MÁS PEQUEÑO) ===
        self.user_button = QPushButton()
        self.user_button. setFixedSize(38, 38)  # ✅ Reducido de 44 a 38
        self.user_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.user_button.setStyleSheet(f"""
            QPushButton {{
                background-color:  {COLORS['slate_200']};
                border: 2px solid {COLORS['slate_300']};
                border-radius:  19px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['slate_300']};
                border-color: {COLORS['slate_400']};
            }}
        """)
        self.user_button.setText("👤")
        self.user_button.clicked.connect(self.user_clicked.emit)
        layout.addWidget(self.user_button)
        
        layout.addSpacing(12)
        
        # === BOTÓN REGISTRAR (AJUSTADO) ===
        self.register_button = QPushButton("+ Registrar")
        
        button_font = QFont()
        button_font.setPointSize(13)  # ✅ Reducido de 14 a 13
        button_font.setWeight(QFont. Weight.DemiBold)
        self.register_button.setFont(button_font)
        
        self.register_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['blue_600']};
                color: {COLORS['white']};
                border: none;
                border-radius: {BORDER['radius_sm']}px;
                padding: 10px 20px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['blue_700']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['blue_800']};
            }}
        """)
        
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button. clicked.connect(self.register_clicked.emit)
        
        layout.addWidget(self. register_button)
        
            
    # ==================== PROJECT MANAGEMENT ====================
    
    def load_projects(self):
        """Cargar proyectos desde Firebase"""
        if not self. firebase_client:
            logger.warning("No firebase_client configured")
            return
        
        try:
            self._loading_projects = True  # Activar flag
            
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
                    proj_id = p. get('id', '')
                    proj_nombre = p.get('nombre', f'Proyecto {proj_id}')
                
                self.projects.append({
                    'id': str(proj_id),
                    'nombre': proj_nombre
                })
            
            # Poblar combo
            self.project_selector.clear()
            
            # Agregar "Vista Global"
            self.project_selector. addItem("🌎 Vista Global (Todas)", "all")
            
            # Agregar proyectos individuales
            for proyecto in self. projects:
                self.project_selector.addItem(proyecto['nombre'], proyecto['id'])
            
            logger.info(f"Loaded {len(self.projects)} projects")
            
        except Exception as e:
            logger.error(f"Error loading projects: {e}")
        finally:
            self._loading_projects = False  # Desactivar flag
    
    def set_current_project(self, proyecto_id:  str, proyecto_nombre: str = None):
        """
        Establecer el proyecto actual en el selector. 
        
        Args:
            proyecto_id: ID del proyecto
            proyecto_nombre: Nombre del proyecto (opcional)
        """
        self._loading_projects = True  # Evitar señal durante set
        
        try:
            # Buscar y seleccionar el proyecto
            for i in range(self.project_selector. count()):
                if str(self.project_selector.itemData(i)) == str(proyecto_id):
                    self.project_selector.setCurrentIndex(i)
                    break
            
            # Actualizar título si se proporciona nombre
            if proyecto_nombre: 
                self.set_title(f"Control de Obra - {proyecto_nombre}")
        
        finally:
            self._loading_projects = False
    
    def _on_project_changed(self, index:  int):
        """Handle project selection change"""
        if self._loading_projects:  # Ignorar si estamos cargando
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
    
    def set_title(self, title:   str):
        """Cambiar el título del header"""
        self. current_title = title
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