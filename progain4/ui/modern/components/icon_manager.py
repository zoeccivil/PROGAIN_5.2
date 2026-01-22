"""
IconManager - Sistema de gestión de iconos SVG

Carga y proporciona iconos SVG como QIcon con colores personalizables. 
Optimizado para iconos de Lucide. dev
"""

import os
from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QByteArray
import re


class IconManager:
    """
    Gestor centralizado de iconos SVG.   
    
    Permite cargar iconos SVG y cambiarles el color dinámicamente.  
    Compatible con iconos de Lucide que usan 'currentColor'. 
    """
    
    _instance = None
    _icons_cache = {}
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializar el gestor de iconos"""
        if self._initialized:
            return
        
        # Ruta a la carpeta de iconos
        self. icons_dir = Path(__file__).parent.parent / "assets" / "icons"
        
        # Verificar que la carpeta existe
        if not self.icons_dir.exists():
            print(f"⚠️ Advertencia: Carpeta de iconos no encontrada: {self.icons_dir}")
            self.icons_dir.mkdir(parents=True, exist_ok=True)
        
        self._initialized = True
        
        print(f"✅ IconManager inicializado - Ruta: {self.icons_dir}")
    
    def get_icon(self, icon_name: str, color: str = "#000000", size: int = 24) -> QIcon:
        """
        Obtener un icono SVG con color personalizado.
        
        Args:
            icon_name:   Nombre del archivo SVG sin extensión (ej: "layout-dashboard")
            color: Color en formato hex (ej: "#ffffff", "#94a3b8")
            size: Tamaño del icono en pixels
            
        Returns:
            QIcon con el icono cargado
        """
        # Clave de caché
        cache_key = f"{icon_name}_{color}_{size}"
        
        # Verificar si ya está en caché
        if cache_key in self._icons_cache:
            return self._icons_cache[cache_key]
        
        # Ruta del archivo SVG
        svg_path = self.icons_dir / f"{icon_name}.svg"
        
        if not svg_path.exists():
            print(f"⚠️ Icono no encontrado: {svg_path}")
            # Retornar icono vacío
            return QIcon()
        
        # Leer el SVG
        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
        except Exception as e: 
            print(f"❌ Error leyendo icono {icon_name}: {e}")
            return QIcon()
        
        # ✅ MEJORADO: Reemplazar colores de forma más robusta
        svg_content = self._apply_color_to_svg(svg_content, color)
        
        # Crear renderer SVG
        svg_bytes = QByteArray(svg_content.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)
        
        if not renderer.isValid():
            print(f"❌ SVG inválido:  {icon_name}")
            return QIcon()
        
        # Crear pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt. GlobalColor.transparent)
        
        # Renderizar SVG en el pixmap
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        # Crear icono
        icon = QIcon(pixmap)
        
        # Guardar en caché
        self._icons_cache[cache_key] = icon
        
        return icon
    
    def _apply_color_to_svg(self, svg_content: str, color: str) -> str:
        """
        Aplicar color al contenido SVG de forma robusta.
        
        Maneja múltiples formatos: 
        - currentColor
        - stroke="currentColor"
        - fill="currentColor"
        - stroke="#000000" y variantes
        - fill="#000000" y variantes
        
        Args:
            svg_content:   Contenido del SVG
            color:  Color en formato hex
            
        Returns: 
            SVG con color aplicado
        """
        # Reemplazar currentColor (con o sin comillas)
        svg_content = svg_content.replace('currentColor', color)
        svg_content = svg_content.replace('"currentColor"', f'"{color}"')
        svg_content = svg_content.replace("'currentColor'", f"'{color}'")
        
        # Reemplazar stroke="#000000" y variantes
        svg_content = re.sub(r'stroke="[#]? 000000?"', f'stroke="{color}"', svg_content)
        svg_content = re.sub(r'stroke="[#]?000?"', f'stroke="{color}"', svg_content)
        svg_content = re.sub(r"stroke='[#]?000000? '", f"stroke='{color}'", svg_content)
        svg_content = re.sub(r"stroke='[#]?000? '", f"stroke='{color}'", svg_content)
        
        # Reemplazar fill="#000000" y variantes (para iconos que usan fill)
        svg_content = re.sub(r'fill="[#]?000000?"', f'fill="{color}"', svg_content)
        svg_content = re.sub(r'fill="[#]?000?"', f'fill="{color}"', svg_content)
        svg_content = re.sub(r"fill='[#]?000000?'", f"fill='{color}'", svg_content)
        svg_content = re.sub(r"fill='[#]?000?'", f"fill='{color}'", svg_content)
        
        # Reemplazar stroke="black" y fill="black"
        svg_content = svg_content.replace('stroke="black"', f'stroke="{color}"')
        svg_content = svg_content.replace("stroke='black'", f"stroke='{color}'")
        svg_content = svg_content.replace('fill="black"', f'fill="{color}"')
        svg_content = svg_content.replace("fill='black'", f"fill='{color}'")
        
        return svg_content
    
    def get_pixmap(self, icon_name: str, color: str = "#000000", size: int = 24) -> QPixmap:
        """
        Obtener un pixmap del icono (para usar en QLabel).
        
        Args:
            icon_name:  Nombre del archivo SVG
            color:  Color hex
            size:   Tamaño en pixels
            
        Returns:  
            QPixmap del icono
        """
        icon = self.get_icon(icon_name, color, size)
        return icon.pixmap(size, size)
    
    def clear_cache(self):
        """Limpiar caché de iconos (útil para desarrollo)"""
        self._icons_cache.clear()
        print("🗑️ Caché de iconos limpiada")
    
    def list_available_icons(self):
        """Listar todos los iconos disponibles en la carpeta"""
        if not self.icons_dir.exists():
            print("❌ Carpeta de iconos no existe")
            return []
        
        icons = [f.stem for f in self.icons_dir.glob("*. svg")]
        print(f"📁 {len(icons)} iconos disponibles:")
        for icon in sorted(icons):
            print(f"   • {icon}")
        return icons


# Instancia global del gestor
icon_manager = IconManager()