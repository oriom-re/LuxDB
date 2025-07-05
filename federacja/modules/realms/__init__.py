
"""
🌍 Realms Package - Wszystkie Moduły Wymiarów w Jednym Miejscu

Struktura:
- BaseRealmModule: Abstrakcyjna klasa bazowa
- MemoryRealmModule: Wymiar pamięci
- SQLiteRealmModule: Wymiar SQLite
- DynamicRealmLoader: Loader i manager cyklu życia
"""

from .base_realm import BaseRealmModule, TaskType, RealmTask, RealmTaskManager
from .memory_realm import MemoryRealmModule
from .sqlite_realm import SQLiteRealmModule
from .dynamic_loader import DynamicRealmLoader

# Registry typów realms
REALM_TYPES = {
    'memory': MemoryRealmModule,
    'sqlite': SQLiteRealmModule
}

__all__ = [
    'BaseRealmModule',
    'TaskType', 
    'RealmTask',
    'RealmTaskManager',
    'MemoryRealmModule',
    'SQLiteRealmModule',
    'DynamicRealmLoader',
    'REALM_TYPES'
]
