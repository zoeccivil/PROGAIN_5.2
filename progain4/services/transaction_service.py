"""
Transaction Service - Servicio para gestión de transacciones

Adapta los datos de FirebaseClient para la UI moderna.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal

logger = logging.getLogger(__name__)


class TransactionService:
    """
    Servicio para gestión de transacciones. 
    
    Proporciona una capa de abstracción entre FirebaseClient y la UI. 
    """
    
    def __init__(self, firebase_client, proyecto_id: str):
        """
        Inicializar servicio de transacciones.
        
        Args:
            firebase_client:   Instancia de FirebaseClient
            proyecto_id:  ID del proyecto activo
        """
        self. firebase = firebase_client
        self.proyecto_id = proyecto_id
        
        # ✅ CACHÉ para evitar recargas innecesarias
        self._cache_transacciones = None
        self._cache_timestamp = None
        self._cache_duration = 60  # segundos
    
    def clear_cache(self):
        """Limpiar caché de transacciones"""
        self._cache_transacciones = None
        self._cache_timestamp = None
        logger.info("Transaction cache cleared")
    
    def get_all_transactions(self, cuenta_id: Optional[str] = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Obtener todas las transacciones del proyecto.
        
        Args:
            cuenta_id: Filtrar por cuenta específica (opcional)
            use_cache:  Usar caché si está disponible
            
        Returns:  
            Lista de transacciones normalizadas
        """
        import time
        
        # ✅ Verificar caché
        if use_cache and self._cache_transacciones is not None:
            current_time = time.time()
            if self._cache_timestamp and (current_time - self._cache_timestamp) < self._cache_duration:
                logger.info(f"Using cached transactions ({len(self._cache_transacciones)} items)")
                
                # Filtrar por cuenta si se solicita
                if cuenta_id: 
                    return [t for t in self._cache_transacciones if str(t.get('cuenta_id')) == str(cuenta_id)]
                return self._cache_transacciones. copy()
        
        try: 
            logger.info(f"Loading transactions from Firebase for project {self.proyecto_id}")
            
            # Obtener transacciones desde Firebase
            transacciones_raw = self.firebase. get_transacciones_by_proyecto(
                self.proyecto_id,
                cuenta_id=None  # Siempre cargar todas para el caché
            )
            
            # Normalizar formato
            transacciones = []
            for trans in transacciones_raw: 
                try:
                    normalized = self._normalize_transaction(trans)
                    transacciones. append(normalized)
                except Exception as e:
                    logger. warning(f"Error normalizing transaction: {e}")
                    continue
            
            # Ordenar por fecha (más reciente primero)
            def get_sort_key(t):
                fecha = t.get('fecha', '')
                if fecha: 
                    try:
                        from datetime import datetime
                        return datetime.strptime(fecha, '%Y-%m-%d')
                    except:
                        from datetime import datetime
                        return datetime(1900, 1, 1)
                from datetime import datetime
                return datetime(1900, 1, 1)
            
            transacciones.sort(key=get_sort_key, reverse=True)
            
            # ✅ Guardar en caché
            self._cache_transacciones = transacciones
            self._cache_timestamp = time.time()
            
            logger.info(f"Loaded and cached {len(transacciones)} transactions")
            
            # Filtrar por cuenta si se solicita
            if cuenta_id:
                return [t for t in transacciones if str(t.get('cuenta_id')) == str(cuenta_id)]
            
            return transacciones
            
        except Exception as e: 
            logger.error(f"Error loading transactions: {e}", exc_info=True)
            return []
    
    def get_transaction_by_id(self, trans_id: str) -> Optional[Dict[str, Any]]: 
        """
        Obtener una transacción específica por ID.
        
        Args:
            trans_id: ID de la transacción
            
        Returns:
            Transacción normalizada o None si no existe
        """
        try: 
            transacciones = self.get_all_transactions()
            for trans in transacciones:
                if str(trans.get('id')) == str(trans_id):
                    return trans
            return None
        except Exception as e:
            logger.error(f"Error getting transaction {trans_id}: {e}")
            return None
    
    def get_transactions_summary(self, cuenta_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener resumen de transacciones. 
        
        Args:
            cuenta_id: Filtrar por cuenta específica (opcional)
            
        Returns: 
            Diccionario con estadísticas
        """
        try:
            transacciones = self.get_all_transactions(cuenta_id)
            
            total_ingresos = Decimal('0')
            total_gastos = Decimal('0')
            
            for trans in transacciones:
                tipo = trans.get('tipo', '')
                monto = Decimal(str(trans.get('monto', 0)))
                
                if tipo == 'ingreso':
                    total_ingresos += monto
                elif tipo == 'gasto':
                    total_gastos += monto
            
            balance = total_ingresos - total_gastos
            
            return {
                'total_transacciones': len(transacciones),
                'total_ingresos': float(total_ingresos),
                'total_gastos': float(total_gastos),
                'balance': float(balance),
            }
            
        except Exception as e:
            logger.error(f"Error getting transactions summary: {e}")
            return {
                'total_transacciones': 0,
                'total_ingresos': 0,
                'total_gastos': 0,
                'balance': 0,
            }
    
    def _normalize_transaction(self, trans_raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizar formato de transacción desde Firebase.
        
        Args:
            trans_raw:  Transacción en formato Firebase
            
        Returns:
            Transacción en formato normalizado
        """
        # Convertir fecha a string si es objeto datetime
        fecha = trans_raw.get('fecha', '')
        if fecha and not isinstance(fecha, str):
            try:
                # Si es DatetimeWithNanoseconds o datetime, convertir a string
                if hasattr(fecha, 'strftime'):
                    fecha = fecha.strftime('%Y-%m-%d')
                else:
                    fecha = str(fecha)
            except Exception as e:
                logger.warning(f"Error converting date:  {e}")
                fecha = ''
        
        return {
            'id': str(trans_raw. get('id', '')),
            'fecha': fecha,
            'tipo': trans_raw.get('tipo', 'gasto'),
            'cuenta_id': str(trans_raw.get('cuenta_id', '')),
            'categoria_id': str(trans_raw. get('categoria_id', '')),
            'subcategoria_id': str(trans_raw.get('subcategoria_id', '')),
            'monto': float(trans_raw.get('monto', 0)),
            'descripcion': trans_raw.get('descripcion', ''),
            'comentario': trans_raw.get('comentario', ''),
            'moneda': trans_raw.get('moneda', 'RD$'),
            'anulada': trans_raw.get('anulada', False),
            'es_transferencia': trans_raw.get('es_transferencia', False),
        }
    
    def filter_by_date_range(
        self, 
        transacciones: List[Dict[str, Any]], 
        fecha_inicio: date, 
        fecha_fin:  date
    ) -> List[Dict[str, Any]]:
        """
        Filtrar transacciones por rango de fechas.
        
        Args:
            transacciones: Lista de transacciones
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns: 
            Transacciones filtradas
        """
        try:
            filtradas = []
            for trans in transacciones:
                fecha_str = trans.get('fecha', '')
                if fecha_str:
                    try:
                        # Parsear fecha (formato:  YYYY-MM-DD)
                        fecha_trans = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                        if fecha_inicio <= fecha_trans <= fecha_fin:
                            filtradas.append(trans)
                    except ValueError:
                        continue
            
            return filtradas
        except Exception as e:
            logger.error(f"Error filtering by date range: {e}")
            return transacciones
    
    def filter_by_type(
        self, 
        transacciones: List[Dict[str, Any]], 
        tipo:  str
    ) -> List[Dict[str, Any]]:
        """
        Filtrar transacciones por tipo.
        
        Args:
            transacciones:  Lista de transacciones
            tipo: 'ingreso', 'gasto', o 'all'
            
        Returns:
            Transacciones filtradas
        """
        if tipo == 'all':
            return transacciones
        
        return [t for t in transacciones if t.get('tipo') == tipo]