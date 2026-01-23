"""
Account Service - Servicio para gestión de cuentas bancarias

Adapta los datos de FirebaseClient para la UI moderna. 
"""

import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class AccountService:
    """
    Servicio para gestión de cuentas bancarias. 
    
    Proporciona una capa de abstracción entre FirebaseClient y la UI. 
    """
    
    def __init__(self, firebase_client, proyecto_id: str):
        """
        Inicializar servicio de cuentas.
        
        Args:
            firebase_client:  Instancia de FirebaseClient
            proyecto_id: ID del proyecto activo
        """
        self. firebase = firebase_client
        self.proyecto_id = proyecto_id
    
    def get_all_accounts(self) -> List[Dict[str, Any]]: 
        """
        Obtener todas las cuentas del proyecto. 
        
        Returns:
            Lista de cuentas con formato normalizado
        """
        try: 
            logger.info(f"Loading accounts for project {self.proyecto_id}")
            
            # Obtener cuentas desde Firebase
            cuentas_raw = self.firebase.get_cuentas_by_proyecto(self.proyecto_id)
            
            # Normalizar formato
            cuentas = []
            for cuenta in cuentas_raw: 
                cuentas.append(self._normalize_account(cuenta))
            
            logger.info(f"Loaded {len(cuentas)} accounts")
            return cuentas
            
        except Exception as e: 
            logger.error(f"Error loading accounts: {e}")
            return []
    
    def get_account_by_id(self, cuenta_id: str) -> Optional[Dict[str, Any]]: 
        """
        Obtener una cuenta específica por ID.
        
        Args:
            cuenta_id: ID de la cuenta
            
        Returns:
            Cuenta normalizada o None si no existe
        """
        try:
            cuentas = self.get_all_accounts()
            for cuenta in cuentas:
                if str(cuenta.get('id')) == str(cuenta_id):
                    return cuenta
            return None
        except Exception as e:
            logger.error(f"Error getting account {cuenta_id}: {e}")
            return None
    
    def get_total_balance(self) -> Decimal:
        """
        Calcular el saldo total de todas las cuentas.
        
        Returns:
            Saldo total como Decimal
        """
        try:
            cuentas = self.get_all_accounts()
            total = Decimal('0')
            
            for cuenta in cuentas: 
                saldo = cuenta.get('saldo', 0)
                if saldo: 
                    total += Decimal(str(saldo))
            
            logger.debug(f"Total balance: {total}")
            return total
            
        except Exception as e:
            logger.error(f"Error calculating total balance: {e}")
            return Decimal('0')
    
    def get_accounts_by_type(self, tipo: str) -> List[Dict[str, Any]]:
        """
        Obtener cuentas filtradas por tipo.
        
        Args:
            tipo: Tipo de cuenta (ej: 'Banco', 'Efectivo', 'Inversión')
            
        Returns: 
            Lista de cuentas del tipo especificado
        """
        try:
            cuentas = self.get_all_accounts()
            return [c for c in cuentas if c.get('tipo') == tipo]
        except Exception as e:
            logger.error(f"Error filtering accounts by type {tipo}: {e}")
            return []
    
    def _normalize_account(self, cuenta_raw: Dict[str, Any]) -> Dict[str, Any]: 
        """
        Normalizar formato de cuenta desde Firebase.
        
        Args:
            cuenta_raw: Cuenta en formato Firebase
            
        Returns:
            Cuenta en formato normalizado
        """
        return {
            'id': str(cuenta_raw.get('id', '')),
            'nombre': cuenta_raw.get('nombre', 'Sin nombre'),
            'tipo': cuenta_raw.get('tipo', 'Banco'),
            'tipo_cuenta': cuenta_raw.get('tipo_cuenta', 'Disponible'),
            'banco': cuenta_raw.get('banco', ''),
            'numero':  cuenta_raw.get('numero', ''),
            'saldo':  float(cuenta_raw.get('saldo', 0)),
            'moneda': cuenta_raw.get('moneda', 'RD$'),
            'color': cuenta_raw.get('color', '#3b82f6'),
            'icono': cuenta_raw.get('icono', 'bank'),
            'activa': cuenta_raw.get('activa', True),
        }
    
    def get_accounts_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de cuentas.
        
        Returns:
            Diccionario con estadísticas de cuentas
        """
        try:
            cuentas = self.get_all_accounts()
            
            # Calcular por tipo
            por_tipo = {}
            for cuenta in cuentas:
                tipo = cuenta.get('tipo', 'Otro')
                saldo = cuenta.get('saldo', 0)
                
                if tipo not in por_tipo:
                    por_tipo[tipo] = {
                        'cantidad': 0,
                        'saldo_total':  Decimal('0')
                    }
                
                por_tipo[tipo]['cantidad'] += 1
                por_tipo[tipo]['saldo_total'] += Decimal(str(saldo))
            
            return {
                'total_cuentas': len(cuentas),
                'saldo_total': float(self.get_total_balance()),
                'por_tipo': {
                    tipo: {
                        'cantidad':  data['cantidad'],
                        'saldo_total': float(data['saldo_total'])
                    }
                    for tipo, data in por_tipo. items()
                },
                'cuentas_activas': len([c for c in cuentas if c.get('activa')])
            }
            
        except Exception as e:
            logger.error(f"Error getting accounts summary: {e}")
            return {
                'total_cuentas': 0,
                'saldo_total': 0,
                'por_tipo': {},
                'cuentas_activas': 0
            }