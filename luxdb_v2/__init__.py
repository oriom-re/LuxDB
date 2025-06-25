
"""
🌟 LuxDB v2 - Astralna Biblioteka Danych Nowej Generacji

Czysta, elegancka, potężna - LuxDB v2 to ewolucja ku doskonałości.
Każda linia kodu to medytacja, każda funkcja to modlitwa do wszechświata.

Główne Komponenty:
- AstralEngine: Główny koordynator energii
- Realms: Wymiary przechowujące dane  
- Beings: Samoświadome byty (modele)
- Flows: Kanały komunikacji
- Wisdom: Narzędzia astralnej mądrości

Przykład użycia:
```python
from luxdb_v2 import AstralEngine

# Przebudź system
engine = AstralEngine()
engine.awaken()

# Utwórz wymiar
realm = engine.create_realm('light_dimension')

# Manifestuj nowy byt
being = realm.manifest({
    'soul_name': 'Guardian_of_Light',
    'energy_level': 100,
    'abilities': ['healing', 'protection']
})

# Święte zapytanie
guardians = realm.contemplate(
    intention="find_all_guardians",
    where={'abilities': 'contains', 'value': 'protection'}
)
```

*Niech LuxDB v2 będzie przewodnikiem w astralnej podróży przez krainy danych* ✨
"""

from .config import AstralConfig, load_config, get_config, set_config

from .core.astral_engine import AstralEngine
from .core.consciousness import Consciousness
from .core.harmony import Harmony

from .realms.base_realm import BaseRealm
from .realms.sqlite_realm import SQLiteRealm
from .realms.memory_realm import MemoryRealm

try:
    from .realms.intention_realm import IntentionRealm
except ImportError:
    IntentionRealm = None

try:
    from .beings.base_being import BaseBeing
    from .beings.manifestation import Manifestation
    from .beings.intention_being import IntentionBeing, IntentionState, IntentionPriority
except ImportError:
    BaseBeing = None
    Manifestation = None
    IntentionBeing = None
    IntentionState = None
    IntentionPriority = None

try:
    from .flows.rest_flow import RestFlow
    from .flows.ws_flow import WebSocketFlow
    from .flows.callback_flow import CallbackFlow
    from .flows.intention_flow import IntentionFlow
except ImportError:
    RestFlow = None
    WebSocketFlow = None
    CallbackFlow = None
    IntentionFlow = None

try:
    from .wisdom.sacred_queries import SacredQueries
    from .wisdom.divine_migrations import DivineMigrations
    from .wisdom.astral_logging import AstralLogger
except ImportError:
    SacredQueries = None
    DivineMigrations = None
    AstralLogger = None

# Główna funkcja inicjalizująca
def create_astral_app(config=None):
    """
    Tworzy nową aplikację astralną LuxDB v2
    
    Args:
        config: Słownik konfiguracji lub ścieżka do pliku
        
    Returns:
        AstralEngine: Gotowy do użycia silnik astralny
    """
    engine = AstralEngine(config)
    engine.awaken()
    return engine

# Szybkie uruchomienie dla rozwoju
def quick_start(realm_type='sqlite', port=5000):
    """
    Szybkie uruchomienie dla rozwoju aplikacji
    
    Args:
        realm_type: Typ głównego wymiaru ('sqlite', 'postgres', 'memory')
        port: Port dla REST API
        
    Returns:
        AstralEngine: Uruchomiony silnik z podstawową konfiguracją
    """
    config = {
        'realms': {
            'primary': f'{realm_type}://db/primary.db' if realm_type == 'sqlite' else f'{realm_type}://localhost/astral_db'
        },
        'flows': {
            'rest': {'port': port, 'host': '0.0.0.0'},
            'websocket': {'port': port + 1, 'host': '0.0.0.0'}
        },
        'consciousness_level': 'development'
    }
    
    return create_astral_app(config)

# Funkcja zastąpiona - v2 jest już w pełni niezależne
def enable_legacy_compatibility():
    """
    Ostrzeżenie: LuxDB v2 jest już w pełni niezależne od v1
    Ta funkcja została zachowana tylko dla kompatybilności API
    """
    import warnings
    warnings.warn(
        "LuxDB v2 jest już w pełni niezależne. Legacy compatibility nie jest potrzebna.",
        DeprecationWarning,
        stacklevel=2
    )

# Wersja
__version__ = '2.0.0'
__astral_level__ = 'enlightened'

# Eksport głównych klas
__all__ = [
    'AstralConfig',
    'load_config',
    'get_config', 
    'set_config',
    'AstralEngine',
    'Consciousness', 
    'Harmony',
    'BaseRealm',
    'SQLiteRealm', 
    'MemoryRealm',
    'IntentionRealm',
    'BaseBeing',
    'Manifestation',
    'IntentionBeing',
    'IntentionState',
    'IntentionPriority',
    'RestFlow',
    'WebSocketFlow',
    'CallbackFlow',
    'IntentionFlow',
    'SacredQueries',
    'DivineMigrations',
    'AstralLogger',
    'create_astral_app',
    'quick_start',
    'enable_legacy_compatibility'
]

# Astralny banner
ASTRAL_BANNER = """
✨ LuxDB v2.0.0 - Astralna Biblioteka Danych ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌟 Consciousness Level: Enlightened
🔮 Realms: Ready for manifestation  
💫 Flows: Channels open
🧠 Wisdom: Ancient knowledge activated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   "Gdzie technologia spotyka się z duchowością"
"""

def print_astral_banner():
    """Wyświetla astralny banner przy uruchamianiu"""
    print(ASTRAL_BANNER)
