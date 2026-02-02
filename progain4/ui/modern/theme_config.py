"""
Theme Configuration - Construction Manager Pro

Paleta de colores extraída del diseño React/Tailwind. 
Todos los colores en formato hexadecimal.
"""

# ========== PALETA DE COLORES ==========

COLORS = {
    # Slate (Grises)
    'slate_50': '#f8fafc',    # Fondo principal
    'slate_100': '#f1f5f9',   # Fondos secundarios, hover
    'slate_200': '#e2e8f0',   # Bordes
    'slate_300': '#cbd5e1',
    'slate_400': '#94a3b8',   # Texto deshabilitado, iconos inactivos
    'slate_500': '#64748b',   # Texto secundario
    'slate_600': '#475569',
    'slate_700':  '#334155',
    'slate_800': '#1e293b',   # Botón activo
    'slate_900':  '#0f172a',   # Sidebar background
    
    # Blue (Acento Principal)
    'blue_50': '#eff6ff',
    'blue_100': '#dbeafe',
    'blue_200': '#bfdbfe',
    'blue_500': '#3b82f6',    # Barra indicadora activo
    'blue_600': '#2563eb',    # Logo background
    'blue_700': '#1d4ed8',
    
    # Emerald (Éxito/Positivo)
    'emerald_50': '#ecfdf5',
    'emerald_100': '#d1fae5',
    'emerald_500': '#10b981',  # Progress bars, montos positivos
    'emerald_600': '#059669',
    'emerald_700': '#047857',
    
    # Rose (Error/Negativo)
    'rose_50': '#fff1f2',
    'rose_100':  '#ffe4e6',
    'rose_200': '#fecdd3',
    'rose_500': '#f43f5e',    # Montos negativos
    'rose_700':  '#be123c',
    
    # White
    'white':  '#ffffff',
}


# ========== TIPOGRAFÍA ==========

FONTS = {
    'family': 'Segoe UI, -apple-system, BlinkMacSystemFont, sans-serif',
    'size_xs':  10,     # Badges, labels pequeños
    'size_sm': 12,     # Texto normal, tabla
    'size_base': 14,   # Texto principal
    'size_lg': 16,     # Headers
    'size_xl': 18,     # Títulos
    'size_2xl': 24,    # Números grandes
}


# ========== ESPACIADO ==========

SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 20,
    '2xl': 24,
    '3xl': 32,
}


# ========== BORDES Y SOMBRAS ==========

BORDER = {
    'radius': 12,        # Border radius principal (rounded-xl)
    'radius_sm': 8,      # Para botones pequeños
    'radius_full': 9999, # Para círculos
}

SHADOW = {
    'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    'base': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
    'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
    'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
}


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
            font-size:  {FONTS['size_base']}px;
        }}
        
        QMainWindow {{
            background-color:  {COLORS['slate_50']};
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
        
        QScrollBar::handle: vertical {{
            background: {COLORS['slate_300']};
            border-radius:  5px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {COLORS['slate_400']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line: vertical {{
            border: none;
            background: none;
            height: 0px;
        }}
        
        QScrollBar:: up-arrow:vertical, QScrollBar::down-arrow: vertical {{
            background: none;
        }}
        
        QScrollBar: horizontal {{
            border: none;
            background: {COLORS['slate_100']};
            height:  10px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {COLORS['slate_300']};
            border-radius:  5px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {COLORS['slate_400']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 0px;
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
        QScrollBar: vertical {{
            border: none;
            background: {COLORS['slate_100']};
            width: 10px;
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
        QScrollBar::sub-line: vertical,
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
        QScrollBar::sub-line: horizontal,
        QScrollBar::left-arrow:horizontal,
        QScrollBar::right-arrow:horizontal {{
            width: 0px;
        }}
    """