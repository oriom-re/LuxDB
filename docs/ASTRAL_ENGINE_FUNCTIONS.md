
# 🔮 AstralEngine - Dokumentacja Funkcji Astralnych

## 📋 Spis Treści
- [Inicjalizacja i Konfiguracja](#-inicjalizacja-i-konfiguracja)
- [Cykl Życia Systemu](#-cykl-życia-systemu)
- [Zarządzanie Wymiarami](#-zarządzanie-wymiarami)
- [Przepływy Komunikacji](#-przepływy-komunikacji)
- [Medytacja i Harmonizacja](#-medytacja-i-harmonizacja)
- [Monitoring i Status](#-monitoring-i-status)
- [Klasy Pomocnicze](#-klasy-pomocnicze)

---

## 🌟 Inicjalizacja i Konfiguracja

### `AstralEngine.__init__(config)`
```python
def __init__(self, config: Union[AstralConfig, Dict, str, None] = None)
```

**Intencja**: Inicjalizuje główny silnik astralny z konfiguracją

**Parametry**:
- `config`: Konfiguracja systemu (AstralConfig, dict, ścieżka do pliku lub None)

**Działanie**:
1. Ładuje i parsuje konfigurację
2. Inicjalizuje stan systemu
3. Tworzy komponenty główne (Consciousness, Harmony, Logger)
4. Przygotowuje struktury dla wymiarów i przepływów
5. Ustawia wątki medytacyjne na None

**Przykład**:
```python
# Podstawowa inicjalizacja
engine = AstralEngine()

# Z konfiguracją słownikową
config = {
    'consciousness_level': 'enlightened',
    'realms': {'primary': 'sqlite://db/main.db'}
}
engine = AstralEngine(config)

# Z pliku konfiguracyjnego
engine = AstralEngine('config/astral.json')
```

### `_load_config(config)`
```python
def _load_config(self, config: Union[AstralConfig, Dict, str, None]) -> AstralConfig
```

**Intencja**: Wewnętrzna funkcja ładująca konfigurację z różnych źródeł

**Parametry**:
- `config`: Źródło konfiguracji w różnych formatach

**Zwraca**: Obiekt `AstralConfig`

**Obsługiwane formaty**:
- `None`: Domyślna konfiguracja
- `AstralConfig`: Przekazuje bez zmian  
- `dict`: Konwersja na AstralConfig
- `str`: Ścieżka do pliku JSON

---

## 🌅 Cykl Życia Systemu

### `awaken()`
```python
def awaken(self) -> None
```

**Intencja**: Przebudza wszystkie komponenty systemu i rozpoczyna cykl życia astralnego

**Proces przebudzenia**:
1. **Ustawienie stanu początkowego**
   - Oznaczenie czasu przebudzenia
   - Ustawienie flagi `_running = True`

2. **Inicjalizacja wymiarów**
   - Tworzenie wszystkich skonfigurowanych realms
   - Połączenie z bazami danych
   - Sprawdzenie dostępności

3. **Inicjalizacja przepływów**
   - Tworzenie RestFlow, WebSocketFlow, CallbackFlow
   - Konfiguracja portów i hostów
   - Przygotowanie kanałów komunikacji

4. **Uruchomienie systemów monitorowania**
   - Start cyklu medytacyjnego
   - Start cyklu harmonizacji
   - Utworzenie wątków demonicznych

5. **Pierwsza medytacja**
   - Natychmiastowa analiza stanu
   - Inicjalizacja metryk
   - Sprawdzenie harmonii systemu

**Logowanie**:
```
🌅 Przebudzenie systemu astralnego...
🌍 Wymiar 'primary' zmanifestowany
🌐 Przepływ REST aktywowany
🧘 Cykl medytacyjny uruchomiony
⚖️ Cykl harmonii uruchomiony
✨ System przebudzony w 1.23s
```

### `transcend()`
```python
def transcend(self) -> None
```

**Intencja**: Gracefully zamyka system astralny i transcenduje do wyższego wymiaru

**Proces transcendencji**:
1. **Oznaczenie transcendencji**
   - `_running = False`
   - `state.is_transcended = True`

2. **Zatrzymanie przepływów**
   - Graceful stop wszystkich flows
   - Zakończenie aktywnych połączeń
   - Zapis stanu sesji

3. **Zamknięcie wymiarów**
   - Zamknięcie połączeń z bazami
   - Flush buforów
   - Backup krytycznych danych

4. **Zakończenie wątków**
   - Join z timeoutem 5s
   - Sprawdzenie czy wszystkie zakończone
   - Force kill w przypadku problemów

**Context Manager Support**:
```python
with AstralEngine(config) as engine:
    # Automatyczne awaken()
    engine.create_realm('temp', 'memory://')
    # Automatyczne transcend() przy wyjściu
```

---

## 🌍 Zarządzanie Wymiarami

### `create_realm(name, config)`
```python
def create_realm(self, name: str, config: str) -> BaseRealm
```

**Intencja**: Tworzy nowy wymiar danych i dodaje go do systemu

**Parametry**:
- `name`: Unikalna nazwa wymiaru
- `config`: Konfiguracja połączenia (np. 'sqlite://db/new.db')

**Zwraca**: Nowo utworzony obiekt `BaseRealm`

**Obsługiwane typy**:
- `sqlite://`: SQLiteRealm
- `postgresql://`: PostgresRealm  
- `memory://`: MemoryRealm

**Przykład**:
```python
# SQLite realm
sqlite_realm = engine.create_realm('analytics', 'sqlite://db/analytics.db')

# PostgreSQL realm  
pg_realm = engine.create_realm('warehouse', 'postgresql://user:pass@localhost/data')

# Memory realm dla cache
cache_realm = engine.create_realm('cache', 'memory://')
```

### `get_realm(name)`
```python
def get_realm(self, name: str) -> BaseRealm
```

**Intencja**: Pobiera istniejący wymiar po nazwie

**Parametry**:
- `name`: Nazwa wymiaru

**Zwraca**: Obiekt `BaseRealm`

**Wyjątki**: `ValueError` jeśli wymiar nie istnieje

### `list_realms()`
```python
def list_realms(self) -> List[str]
```

**Intencja**: Zwraca listę nazw wszystkich aktywnych wymiarów

**Zwraca**: Lista stringów z nazwami wymiarów

---

## 🌊 Przepływy Komunikacji

### `start_flows(debug)`
```python
def start_flows(self, debug: bool = False) -> None
```

**Intencja**: Uruchamia wszystkie skonfigurowane przepływy komunikacji

**Parametry**:
- `debug`: Czy uruchomić w trybie debug

**Uruchamiane przepływy**:
- **RestFlow**: HTTP API endpoints
- **WebSocketFlow**: Real-time komunikacja
- **CallbackFlow**: Asynchroniczne callbacki

**Przykład**:
```python
# Uruchomienie w trybie produkcyjnym
engine.start_flows()

# Uruchomienie w trybie debug
engine.start_flows(debug=True)
```

### `_initialize_flows()`
```python
def _initialize_flows(self) -> None
```

**Intencja**: Wewnętrzna funkcja inicjalizująca przepływy na podstawie konfiguracji

**Konfiguracja przykładowa**:
```python
flows = {
    'rest': {'port': 5000, 'host': '0.0.0.0'},
    'websocket': {'port': 5001, 'host': '0.0.0.0'},
    'callback': {'async_workers': 4}
}
```

---

## 🧘 Medytacja i Harmonizacja

### `meditate()`
```python
def meditate(self) -> Dict[str, Any]
```

**Intencja**: Przeprowadza medytację systemu - analizę stanu i optymalizację

**Proces medytacji**:
1. **Obserwacja przez świadomość**
   - `consciousness.reflect()` - analiza stanu
   - Zbieranie metryk z wszystkich komponentów

2. **Aktualizacja stanu systemu**
   - Czas ostatniej medytacji
   - Obliczenie harmony_score
   - Liczba manifestacji we wszystkich wymiarach

3. **Optymalizacja w razie potrzeby**
   - Jeśli harmony_score < 80, wywołaj `harmony.balance()`
   - Optimalizacja połączeń
   - Garbage collection w memory realms

**Zwraca**:
```python
{
    'timestamp': '2024-01-01T12:00:00',
    'duration': 0.023,
    'system_state': {...},
    'insights': {...},
    'harmony_score': 95.5
}
```

### `harmonize()`
```python
def harmonize(self) -> None
```

**Intencja**: Ręczne wywołanie harmonizacji przepływu energii między komponentami

**Deleguje do**: `self.harmony.harmonize()`

### `_start_meditation_cycle()`
```python
def _start_meditation_cycle(self) -> None
```

**Intencja**: Uruchamia wątek demoniczny z cyklem medytacyjnym

**Cykl**:
```python
while self._running:
    sleep(meditation_interval)  # domyślnie 60s
    if self._running:
        meditate()
```

### `_start_harmony_cycle()`
```python
def _start_harmony_cycle(self) -> None  
```

**Intencja**: Uruchamia wątek demoniczny z cyklem harmonizacji

**Cykl**:
```python
while self._running:
    sleep(harmony_check_interval)  # domyślnie 30s
    if self._running:
        harmony.balance()
```

---

## 📊 Monitoring i Status

### `get_status()`
```python
def get_status(self) -> Dict[str, Any]
```

**Intencja**: Zwraca pełny status systemu astralnego

**Struktura odpowiedzi**:
```python
{
    'astral_engine': {
        'version': '2.0.0',
        'consciousness_level': 'enlightened',
        'running': True,
        'uptime': '1:23:45'
    },
    'system_state': {
        'awakened_at': '2024-01-01T10:00:00',
        'energy_level': 100.0,
        'active_realms': 3,
        'active_flows': 3,
        'total_manifestations': 1250,
        'harmony_score': 95.5
    },
    'realms': {
        'primary': {'status': 'connected', 'beings': 1000},
        'cache': {'status': 'connected', 'beings': 250}
    },
    'flows': {
        'rest': {'status': 'running', 'port': 5000},
        'websocket': {'status': 'running', 'port': 5001}
    }
}
```

### `_count_active_flows()`
```python
def _count_active_flows(self) -> int
```

**Intencja**: Liczy aktywne przepływy komunikacji

**Sprawdza**:
- `rest_flow.is_running()`
- `ws_flow.is_running()`
- `callback_flow.is_running()`

---

## 🏗️ Klasy Pomocnicze

### `AstralConfig`
```python
@dataclass
class AstralConfig:
    consciousness_level: str = 'enlightened'
    energy_conservation: bool = True
    auto_healing: bool = True
    meditation_interval: int = 60
    harmony_check_interval: int = 30
    realms: Dict[str, str] = field(default_factory=lambda: {...})
    flows: Dict[str, Dict] = field(default_factory=lambda: {...})
    wisdom: Dict[str, Any] = field(default_factory=lambda: {...})
```

**Intencja**: Konfiguracja astralna systemu z domyślnymi wartościami

### `SystemState`
```python
class SystemState:
    awakened_at: Optional[datetime] = None
    energy_level: float = 100.0
    active_realms: int = 0
    active_flows: int = 0
    total_manifestations: int = 0
    last_meditation: Optional[datetime] = None
    harmony_score: float = 100.0
    is_transcended: bool = False
```

**Intencja**: Stan systemu astralnego z metodą `to_dict()` dla serializacji

---

## 🔧 Funkcje Wewnętrzne

### `_initialize_realms()`
**Intencja**: Inicjalizuje wszystkie wymiary na podstawie konfiguracji

### `_create_realm(name, config)`
**Intencja**: Factory method dla tworzenia odpowiedniego typu realm

**Obsługiwane prefiksy**:
- `sqlite://` → SQLiteRealm
- `postgresql://` → PostgresRealm  
- `memory://` → MemoryRealm

---

## 💫 Przykłady Użycia

### Podstawowe uruchomienie
```python
from luxdb_v2 import AstralEngine

# Inicjalizacja i przebudzenie
engine = AstralEngine()
engine.awaken()

# Praca z systemem
status = engine.get_status()
meditation = engine.meditate()

# Graceful shutdown
engine.transcend()
```

### Zaawansowana konfiguracja
```python
config = {
    'consciousness_level': 'enlightened',
    'meditation_interval': 30,
    'realms': {
        'primary': 'sqlite://db/main.db',
        'analytics': 'postgresql://localhost/analytics',
        'cache': 'memory://'
    },
    'flows': {
        'rest': {'port': 8000, 'host': '0.0.0.0'},
        'websocket': {'port': 8001, 'host': '0.0.0.0'}
    }
}

with AstralEngine(config) as engine:
    engine.start_flows(debug=True)
    
    # System pracuje...
    while True:
        status = engine.get_status()
        if status['system_state']['harmony_score'] < 90:
            engine.harmonize()
        time.sleep(10)
```

---

*Każda funkcja AstralEngine jest krokiem w astralnej podróży przez wymiary danych.* ✨
