"""
CacheManager - Sistema de caché global para optimizar lecturas de Firebase

Cachea: 
- Proyectos
- Categorías/Subcategorías
- Transacciones por proyecto
- Cuentas por proyecto
"""

from functools import lru_cache
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Gestor de caché global para datos de Firebase"""
    
    def __init__(self):
        # Cache de datos
        self._proyectos_cache = None
        self._proyectos_cache_time = None
        self._proyectos_ttl = timedelta(minutes=5)
        
        self._categorias_cache = None
        self._categorias_cache_time = None
        self._categorias_ttl = timedelta(hours=1)  # Categorías casi no cambian
        
        self._subcategorias_cache = None
        self._subcategorias_cache_time = None
        self._subcategorias_ttl = timedelta(hours=1)
        
        # Cache por proyecto (dict de {proyecto_id: {data, timestamp}})
        self._transacciones_cache = {}
        self._transacciones_ttl = timedelta(minutes=2)
        
        self._cuentas_cache = {}
        self._cuentas_ttl = timedelta(minutes=5)
        
        logger.info("✅ CacheManager initialized")
    
    # ==================== PROYECTOS ====================
    
    def get_proyectos(self, fetch_func) -> List[Any]:
        """
        Obtener proyectos (desde caché o Firebase)
        
        Args: 
            fetch_func: Función para obtener datos de Firebase si no están en caché
        """
        now = datetime.now()
        
        # Verificar si el caché es válido
        if (self._proyectos_cache is not None and 
            self._proyectos_cache_time is not None and 
            (now - self._proyectos_cache_time) < self._proyectos_ttl):
            logger.info(f"📦 Using cached proyectos ({len(self._proyectos_cache)} items)")
            return self._proyectos_cache
        
        # Cache inválido o vacío, obtener de Firebase
        logger.info("🔄 Fetching proyectos from Firebase...")
        self._proyectos_cache = fetch_func()
        self._proyectos_cache_time = now
        logger.info(f"✅ Cached {len(self._proyectos_cache)} proyectos")
        
        return self._proyectos_cache
    
    def invalidate_proyectos(self):
        """Invalidar caché de proyectos"""
        logger.info("🗑️ Invalidating proyectos cache")
        self._proyectos_cache = None
        self._proyectos_cache_time = None
    
    # ==================== CATEGORÍAS ====================
    
    def get_categorias(self, fetch_func) -> List[Any]:
        """Obtener categorías (desde caché o Firebase)"""
        now = datetime.now()
        
        if (self._categorias_cache is not None and 
            self._categorias_cache_time is not None and 
            (now - self._categorias_cache_time) < self._categorias_ttl):
            logger.info(f"📦 Using cached categorías ({len(self._categorias_cache)} items)")
            return self._categorias_cache
        
        logger.info("🔄 Fetching categorías from Firebase...")
        self._categorias_cache = fetch_func()
        self._categorias_cache_time = now
        logger.info(f"✅ Cached {len(self._categorias_cache)} categorías")
        
        return self._categorias_cache
    
    def invalidate_categorias(self):
        """Invalidar caché de categorías"""
        logger.info("🗑️ Invalidating categorías cache")
        self._categorias_cache = None
        self._categorias_cache_time = None
    
    # ==================== SUBCATEGORÍAS ====================
    
    def get_subcategorias(self, fetch_func) -> List[Any]:
        """Obtener subcategorías (desde caché o Firebase)"""
        now = datetime.now()
        
        if (self._subcategorias_cache is not None and 
            self._subcategorias_cache_time is not None and 
            (now - self._subcategorias_cache_time) < self._subcategorias_ttl):
            logger.info(f"📦 Using cached subcategorías ({len(self._subcategorias_cache)} items)")
            return self._subcategorias_cache
        
        logger.info("🔄 Fetching subcategorías from Firebase...")
        self._subcategorias_cache = fetch_func()
        self._subcategorias_cache_time = now
        logger.info(f"✅ Cached {len(self._subcategorias_cache)} subcategorías")
        
        return self._subcategorias_cache
    
    def invalidate_subcategorias(self):
        """Invalidar caché de subcategorías"""
        logger.info("🗑️ Invalidating subcategorías cache")
        self._subcategorias_cache = None
        self._subcategorias_cache_time = None
    
    # ==================== TRANSACCIONES ====================
    
    def get_transacciones(self, proyecto_id: str, fetch_func) -> List[Any]:
        """Obtener transacciones de un proyecto (desde caché o Firebase)"""
        now = datetime.now()
        
        # ✅ DEBUG: Ver estado del caché
        logger.debug(f"🔍 Buscando transacciones en caché para proyecto {proyecto_id}")
        logger.debug(f"   Caché actual tiene {len(self._transacciones_cache)} proyectos")
        
        # Verificar si existe en caché y es válido
        if proyecto_id in self._transacciones_cache:
            cached_data = self._transacciones_cache[proyecto_id]
            time_elapsed = (now - cached_data['timestamp'])
            logger.debug(f"   Encontrado en caché, edad: {time_elapsed.total_seconds()}s (TTL: {self._transacciones_ttl. total_seconds()}s)")
            
            if time_elapsed < self._transacciones_ttl:
                logger.info(f"📦 Using cached transacciones for project {proyecto_id} ({len(cached_data['data'])} items)")
                return cached_data['data']
            else:
                logger.debug(f"   ⏰ Caché expirado para proyecto {proyecto_id}")
        else:
            logger.debug(f"   ❌ NO encontrado en caché para proyecto {proyecto_id}")
        
        # Obtener de Firebase
        logger.info(f"🔄 Fetching transacciones for project {proyecto_id}...")
        data = fetch_func()
        self._transacciones_cache[proyecto_id] = {
            'data': data,
            'timestamp':  now
        }
        logger.info(f"✅ Cached {len(data)} transacciones for project {proyecto_id}")
        
        return data
    
    def invalidate_transacciones(self, proyecto_id: Optional[str] = None):
        """
        Invalidar caché de transacciones
        
        Args: 
            proyecto_id: Si se especifica, solo invalida ese proyecto.  Si es None, invalida todo.
        """
        if proyecto_id:
            if proyecto_id in self._transacciones_cache:
                logger.info(f"🗑️ Invalidating transacciones cache for project {proyecto_id}")
                del self._transacciones_cache[proyecto_id]
        else:
            logger.info("🗑️ Invalidating ALL transacciones cache")
            self._transacciones_cache = {}
    
    # ==================== CUENTAS ====================
    
    def get_cuentas(self, proyecto_id: str, fetch_func) -> List[Any]:
        """Obtener cuentas de un proyecto (desde caché o Firebase)"""
        now = datetime. now()
        
        if proyecto_id in self._cuentas_cache:
            cached_data = self._cuentas_cache[proyecto_id]
            if (now - cached_data['timestamp']) < self._cuentas_ttl:
                logger. info(f"📦 Using cached cuentas for project {proyecto_id} ({len(cached_data['data'])} items)")
                return cached_data['data']
        
        logger.info(f"🔄 Fetching cuentas for project {proyecto_id}...")
        data = fetch_func()
        self._cuentas_cache[proyecto_id] = {
            'data': data,
            'timestamp': now
        }
        logger.info(f"✅ Cached {len(data)} cuentas for project {proyecto_id}")
        
        return data
    
    def invalidate_cuentas(self, proyecto_id: Optional[str] = None):
        """Invalidar caché de cuentas"""
        if proyecto_id: 
            if proyecto_id in self._cuentas_cache:
                logger.info(f"🗑️ Invalidating cuentas cache for project {proyecto_id}")
                del self._cuentas_cache[proyecto_id]
        else:
            logger.info("🗑️ Invalidating ALL cuentas cache")
            self._cuentas_cache = {}



# ==================== SUBCATEGORÍAS POR PROYECTO ====================

    def get_subcategorias_proyecto(self, proyecto_id: str, fetch_func) -> List[Any]:
        """Obtener subcategorías de un proyecto (desde caché o Firebase)"""
        now = datetime.now()
        
        # Usar clave específica
        cache_key = f"{proyecto_id}_subcats"
        
        if cache_key in self._cuentas_cache:  # Reutilizar el mismo dict de caché
            cached_data = self._cuentas_cache[cache_key]
            if (now - cached_data['timestamp']) < self._cuentas_ttl: 
                logger.info(f"📦 Using cached subcategorías for project {proyecto_id} ({len(cached_data['data'])} items)")
                return cached_data['data']
        
        logger.info(f"🔄 Fetching subcategorías for project {proyecto_id}...")
        data = fetch_func()
        self._cuentas_cache[cache_key] = {
            'data': data,
            'timestamp': now
        }
        logger.info(f"✅ Cached {len(data)} subcategorías for project {proyecto_id}")
        
        return data

    def invalidate_subcategorias_proyecto(self, proyecto_id: Optional[str] = None):
        """Invalidar caché de subcategorías por proyecto"""
        if proyecto_id:
            cache_key = f"{proyecto_id}_subcats"
            if cache_key in self._cuentas_cache:
                logger.info(f"🗑️ Invalidating subcategorías cache for project {proyecto_id}")
                del self._cuentas_cache[cache_key]
        else:
            # Invalidar todas las subcategorías (filtrar por sufijo _subcats)
            keys_to_delete = [k for k in self._cuentas_cache.keys() if k.endswith('_subcats')]
            for key in keys_to_delete:
                del self._cuentas_cache[key]
            logger.info(f"🗑️ Invalidated {len(keys_to_delete)} subcategorías caches")



    # ==================== LIMPIEZA GLOBAL ====================
    
    def clear_all(self):
        """Limpiar TODO el caché"""
        logger. info("🗑️ Clearing ALL cache")
        self._proyectos_cache = None
        self._proyectos_cache_time = None
        self._categorias_cache = None
        self._categorias_cache_time = None
        self._subcategorias_cache = None
        self._subcategorias_cache_time = None
        self._transacciones_cache = {}
        self._cuentas_cache = {}


# ✅ Instancia global del caché
cache_manager = CacheManager()