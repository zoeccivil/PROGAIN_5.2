"""
Theme Configuration - Construction Manager Pro

Paleta de colores extraída del diseño React/Tailwind. 
Todos los colores en formato hexadecimal. 
"""

# ========== PALETA DE COLORES ==========

COLORS = {
    # Slate (Grises)
    'slate_50': '#f8fafc',    # Fondo principal
    'slate_100':  '#f1f5f9',   # Fondos secundarios, hover
    'slate_200':  '#e2e8f0',   # Bordes
    'slate_300': '#cbd5e1',   # Bordes hover
    'slate_400': '#94a3b8',   # Texto deshabilitado, iconos inactivos
    'slate_500': '#64748b',   # Texto secundario
    'slate_600': '#475569',   # Texto terciario
    'slate_700':  '#334155',   # Texto oscuro
    'slate_800':  '#1e293b',   # Botón activo
    'slate_900': '#0f172a',   # Sidebar background
    
    # Blue (Acento Principal)
    'blue_50': '#eff6ff',     # Fondo muy claro
    'blue_100': '#dbeafe',    # Badges, fondos claros
    'blue_200':  '#bfdbfe',    # Bordes claros
    'blue_300': '#93c5fd',    # ← AGREGADO - Hover borders
    'blue_400': '#60a5fa',    # ← AGREGADO - Hover states
    'blue_500': '#3b82f6',    # Barra indicadora activo
    'blue_600': '#2563eb',    # Logo background
    'blue_700': '#1d4ed8',    # Texto azul oscuro
    'blue_800': '#1e40af',    # ← AGREGADO - Estados pressed
    'blue_900': '#1e3a8a',    # ← AGREGADO - Muy oscuro
    
    # Emerald (Éxito/Positivo)
    'emerald_50': '#ecfdf5',
    'emerald_100': '#d1fae5',
    'emerald_200': '#a7f3d0',  # ← AGREGADO
    'emerald_300': '#6ee7b7',  # ← AGREGADO
    'emerald_400': '#34d399',  # ← AGREGADO
    'emerald_500': '#10b981',  # Progress bars, montos positivos
    'emerald_600': '#059669',  # Estados hover
    'emerald_700':  '#047857',  # Estados pressed
    'emerald_800': '#065f46',  # ← AGREGADO
    'emerald_900': '#064e3b',  # ← AGREGADO
    
    # Green (Verdes adicionales - alias de emerald para compatibilidad)
    'green_50': '#f0fdf4',
    'green_100': '#dcfce7',
    'green_200': '#bbf7d0',
    'green_300': '#86efac',
    'green_400':  '#4ade80',
    'green_500': '#22c55e',
    'green_600': '#16a34a',   # ← Usado en AccountCard
    'green_700': '#15803d',
    'green_800': '#166534',
    'green_900': '#14532d',
    
    # Rose (Error/Negativo)
    'rose_50': '#fff1f2',
    'rose_100': '#ffe4e6',
    'rose_200': '#fecdd3',
    'rose_300': '#fda4af',    # ← AGREGADO
    'rose_400': '#fb7185',    # ← AGREGADO
    'rose_500': '#f43f5e',    # Montos negativos
    'rose_600': '#e11d48',    # ← AGREGADO
    'rose_700': '#be123c',    # Estados pressed
    'rose_800': '#9f1239',    # ← AGREGADO
    'rose_900': '#881337',    # ← AGREGADO
    
    # Red (Rojos adicionales - alias de rose para compatibilidad)
    'red_50': '#fef2f2',
    'red_100': '#fee2e2',
    'red_200':  '#fecaca',
    'red_300': '#fca5a5',
    'red_400': '#f87171',
    'red_500': '#ef4444',
    'red_600': '#dc2626',     # ← Usado en AccountCard
    'red_700': '#b91c1c',
    'red_800': '#991b1b',
    'red_900': '#7f1d1d',
    

    # ✅ AGREGAR ESTOS COLORES AMARILLOS: 
    'yellow_100': '#FEF3C7',
    'yellow_600': '#CA8A04',
    'yellow_700': '#A16207',


    # Amber (Advertencias)
    'amber_50': '#fffbeb',
    'amber_100': '#fef3c7',
    'amber_200': '#fde68a',
    'amber_300': '#fcd34d',
    'amber_400': '#fbbf24',
    'amber_500': '#f59e0b',
    'amber_600': '#d97706',
    'amber_700': '#b45309',
    'amber_800': '#92400e',
    'amber_900': '#78350f',
    
    # Orange (Naranjas)
    'orange_50': '#fff7ed',
    'orange_100': '#ffedd5',
    'orange_200': '#fed7aa',
    'orange_300': '#fdba74',
    'orange_400': '#fb923c',
    'orange_500': '#f97316',
    'orange_600': '#ea580c',
    'orange_700': '#c2410c',
    'orange_800': '#9a3412',
    'orange_900':  '#7c2d12',
    
    # Purple (Púrpuras)
    'purple_50': '#faf5ff',
    'purple_100': '#f3e8ff',
    'purple_200': '#e9d5ff',
    'purple_300': '#d8b4fe',
    'purple_400': '#c084fc',
    'purple_500': '#a855f7',
    'purple_600': '#9333ea',
    'purple_700': '#7e22ce',
    'purple_800': '#6b21a8',
    'purple_900': '#581c87',
    
    # Básicos
    'white': '#ffffff',
    'black': '#000000',
    'transparent': 'transparent',
}


# ========== TIPOGRAFÍA ==========

FONTS = {
    'family': 'Segoe UI, -apple-system, BlinkMacSystemFont, "Roboto", "Helvetica Neue", Arial, sans-serif',
    'family_mono': '"Courier New", "Consolas", "Monaco", monospace',
    'size_xs': 10,     # Badges, labels pequeños
    'size_sm': 12,     # Texto normal, tabla
    'size_base': 14,   # Texto principal
    'size_lg': 16,     # Headers
    'size_xl': 18,     # Títulos
    'size_2xl': 24,    # Números grandes
    'size_3xl': 30,    # Títulos principales
    'size_4xl': 36,    # Hero text
}


# ========== ESPACIADO ==========

SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 20,
    '2xl':  24,
    '3xl': 32,
    '4xl': 40,
    '5xl': 48,
    '6xl':  64,
}


# ========== BORDES Y SOMBRAS ==========

BORDER = {
    'radius': 12,        # Border radius principal (rounded-xl)
    'radius_sm': 6,      # Para elementos pequeños
    'radius_md': 8,      # Para botones
    'radius_lg':  16,     # Para cards grandes
    'radius_full': 9999, # Para círculos
    'width': 1,          # Ancho de borde estándar
    'width_thick': 2,    # Borde grueso
}

SHADOW = {
    'none': 'none',
    'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    'base': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
    'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
    'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
}


# ========== TAMAÑOS COMUNES ==========

SIZES = {
    'sidebar_width': 100,
    'header_height': 80,
    'button_height': 40,
    'button_height_sm': 32,
    'button_height_lg': 48,
    'input_height': 40,
    'card_padding': 24,
    'card_padding_sm': 16,
    'card_padding_lg': 32,
}


# ========== HELPERS DE COLOR ==========

def get_color(color_key: str, default: str = '#000000') -> str:
    """
    Obtener un color de forma segura.
    
    Args:
        color_key: Clave del color (ej: 'blue_500')
        default: Color por defecto si no existe
        
    Returns:
        Color hexadecimal
    """
    return COLORS.get(color_key, default)


def get_gradient(color1_key: str, color2_key: str) -> str:
    """
    Crear un gradiente CSS entre dos colores.
    
    Args:
        color1_key: Primera clave de color
        color2_key:  Segunda clave de color
        
    Returns:
        Código CSS de gradiente lineal
    """
    color1 = get_color(color1_key)
    color2 = get_color(color2_key)
    return f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:1 {color2})"


# ========== QSS GLOBAL ==========

def get_global_stylesheet() -> str:
    """
    Retorna el stylesheet global de la aplicación.
    Debe aplicarse al QApplication.
    
    IMPORTANTE: No sobrescribe widgets con autoFillBackground=True
    """
    return f"""
        * {{
            font-family: {FONTS['family']};
            font-size: {FONTS['size_base']}px;
        }}
        
        QMainWindow {{
            background-color: {COLORS['slate_50']};
        }}
        
        /* NO aplicar fondo a widgets con autoFillBackground */
        QWidget {{
            color: {COLORS['slate_900']};
        }}
        
        QWidget: ! window {{
            background-color: transparent;
        }}
        
        /* Scrollbars personalizados */
        QScrollBar: vertical {{
            border: none;
            background: {COLORS['slate_100']};
            width: 10px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {COLORS['slate_300']};
            border-radius: 5px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {COLORS['slate_400']};
        }}
        
        QScrollBar:: add-line:vertical, QScrollBar::sub-line: vertical {{
            border: none;
            background: none;
            height: 0px;
        }}
        
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow: vertical {{
            background: none;
        }}
        
        QScrollBar: horizontal {{
            border: none;
            background: {COLORS['slate_100']};
            height: 10px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {COLORS['slate_300']};
            border-radius: 5px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {COLORS['slate_400']};
        }}
        
        QScrollBar:: add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width:  0px;
        }}
        
        QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {{
            background: none;
        }}
        
        /* Labels por defecto */
        QLabel {{
            background-color: transparent;
        }}
    """


def get_minimal_stylesheet() -> str:
    """
    Stylesheet minimalista que NO interfiere con widgets personalizados.
    Solo afecta:  tipografía y scrollbars. 
    """
    return f"""
        /* Tipografía global */
        * {{
            font-family: {FONTS['family']};
        }}
        
        /* Scrollbars personalizados */
        QScrollBar:vertical {{
            border: none;
            background: {COLORS['slate_100']};
            width:  10px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {COLORS['slate_300']};
            border-radius:  5px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {COLORS['slate_400']};
        }}
        
        QScrollBar::add-line:vertical, 
        QScrollBar::sub-line:vertical,
        QScrollBar::up-arrow:vertical,
        QScrollBar::down-arrow:vertical {{
            height: 0px;
        }}
        
        QScrollBar: horizontal {{
            border: none;
            background: {COLORS['slate_100']};
            height: 10px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {COLORS['slate_300']};
            border-radius: 5px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {COLORS['slate_400']};
        }}
        
        QScrollBar:: add-line:horizontal,
        QScrollBar::sub-line:horizontal,
        QScrollBar::left-arrow:horizontal,
        QScrollBar::right-arrow:horizontal {{
            width: 0px;
        }}
    """


# ========== ESTILOS DE COMPONENTES COMUNES ==========

def get_button_style(variant: str = 'primary') -> str:
    """
    Obtener estilo para botones según variante.
    
    Args:
        variant: 'primary', 'secondary', 'danger', 'success'
        
    Returns:
        Código QSS para el botón
    """
    styles = {
        'primary': f"""
            QPushButton {{
                background-color: {COLORS['blue_600']};
                color: {COLORS['white']};
                border: none;
                border-radius: {BORDER['radius_md']}px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['blue_700']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['blue_800']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['slate_300']};
                color:  {COLORS['slate_500']};
            }}
        """,
        'secondary': f"""
            QPushButton {{
                background-color: {COLORS['slate_200']};
                color: {COLORS['slate_900']};
                border: none;
                border-radius: {BORDER['radius_md']}px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['slate_300']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['slate_400']};
            }}
        """,
        'danger': f"""
            QPushButton {{
                background-color: {COLORS['red_600']};
                color: {COLORS['white']};
                border: none;
                border-radius: {BORDER['radius_md']}px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['red_700']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['red_800']};
            }}
        """,
        'success': f"""
            QPushButton {{
                background-color: {COLORS['green_600']};
                color: {COLORS['white']};
                border: none;
                border-radius: {BORDER['radius_md']}px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['green_700']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['green_800']};
            }}
        """,
    }
    
    return styles. get(variant, styles['primary'])