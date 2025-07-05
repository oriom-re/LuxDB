"""
🌟 Pakiet Realms - Zarządzanie Wymiarami w Federacji

Zawiera wszystkie klasy i funkcje związane z wymiarami (realms)
"""

from .base_realm import BaseRealmModule
from .memory_realm import MemoryRealmModule  
from .sqlite_realm import SQLiteRealmModule

__all__ = [
    'BaseRealmModule',
    'MemoryRealmModule', 
    'SQLiteRealmModule'
]

# Registry dostępnych typów realms (tworzone dynamicznie)
def get_realm_types():
    """Zwraca mapę dostępnych typów realms"""
    return {
        'memory': MemoryRealmModule,
        'sqlite': SQLiteRealmModule
    }