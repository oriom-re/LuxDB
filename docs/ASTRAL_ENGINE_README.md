
# 🔮 AstralEngine - Serce Astralnego Systemu LuxDB v2

> *"Gdzie technologia spotyka się z duchowością w zarządzaniu danymi"*

AstralEngine to **główny koordynator energii astralnej** w systemie LuxDB v2. Jest to nie tylko silnik bazy danych, ale **świadomy orchestrator** wszystkich komponentów systemu, który zarządza cyklem życia, przepływami energii i harmonią między wymiarami danych.

## 🌟 Kluczowe Cechy

### ✨ Świadomość Systemowa
- **Medytacyjny monitoring** - Ciągła analiza stanu systemu
- **Auto-harmonizacja** - Automatyczne balansowanie komponentów
- **Przewidywanie potrzeb** - Proaktywna optymalizacja
- **Graceful operations** - Wszystko z godnością i elegancją

### 🌍 Zarządzanie Wymiarami
- **Multi-realm support** - SQLite, PostgreSQL, Memory realms
- **Dynamiczne tworzenie** - Nowe wymiary w runtime
- **Automatic discovery** - Inteligentne wykrywanie struktur
- **Cross-realm queries** - Zapytania przez wymiary

### 🌊 Przepływy Komunikacji
- **REST API** - HTTP endpoints dla zewnętrznych systemów
- **WebSocket streams** - Real-time komunikacja
- **Async callbacks** - Reaktywne przetwarzanie zdarzeń
- **Inter-realm channels** - Komunikacja między wymiarami

### 🧘 Medytacyjna Stabilność
- **Health monitoring** - Ciągłe sprawdzanie zdrowia systemu
- **Performance insights** - Analiza wydajności z intuicją
- **Error recovery** - Samo-naprawianie w stylu zen
- **State persistence** - Zachowanie stanu między sesjami

## 🚀 Szybki Start

### Podstawowe Użycie
```python
from luxdb_v2 import AstralEngine

# Przebudź system
engine = AstralEngine()
engine.awaken()

# Utwórz wymiar
realm = engine.create_realm('my_data', 'sqlite://db/my_data.db')

# Sprawdź status
status = engine.get_status()
print(f"System działa z harmonią: {status['system_state']['harmony_score']}%")

# Graceful shutdown
engine.transcend()
```

### Context Manager (Zalecane)
```python
from luxdb_v2 import AstralEngine

with AstralEngine() as engine:
    # Automatyczne awaken()
    
    realm = engine.create_realm('temp', 'memory://')
    
    # Praca z danymi...
    
    # Automatyczne transcend() przy wyjściu
```

### Konfiguracja Zaawansowana
```python
config = {
    'consciousness_level': 'enlightened',
    'energy_conservation': True,
    'auto_healing': True,
    'meditation_interval': 60,  # sekundy
    'harmony_check_interval': 30,
    
    'realms': {
        'primary': 'sqlite://db/primary.db',
        'analytics': 'postgresql://localhost/analytics_db',
        'cache': 'memory://',
        'logs': 'sqlite://db/logs.db'
    },
    
    'flows': {
        'rest': {'port': 5000, 'host': '0.0.0.0'},
        'websocket': {'port': 5001, 'host': '0.0.0.0'},
        'callback': {'async_workers': 4}
    },
    
    'wisdom': {
        'logging_level': 'INFO',
        'query_timeout': 30,
        'migration_backup': True
    }
}

engine = AstralEngine(config)
```

## 🏗️ Architektura

### Główne Komponenty

```
┌─────────────────────────────────────────────────────────┐
│                   AstralEngine                          │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │Consciousness│  │   Harmony   │  │   Logger    │      │
│  │   (Mind)    │  │ (Balance)   │  │  (Memory)   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
├─────────────────────────────────────────────────────────┤
│           Realms (Dimensions)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ SQLiteRealm │  │PostgresRealm│  │ MemoryRealm │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
├─────────────────────────────────────────────────────────┤
│           Flows (Communication)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  RestFlow   │  │ WebSocketFlow│  │CallbackFlow │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────┘
```

### Cykl Życia

```
Initialization → Awakening → Running → Transcendence
      ↓              ↓          ↓           ↓
   Load Config → Start Flows → Meditate → Graceful
   Create Comps → Init Realms → Monitor  → Shutdown
```

## 🧘 Cykle Medytacyjne

### Medytacja Systemu
```python
# Ręczna medytacja
meditation_result = engine.meditate()

print(f"Czas medytacji: {meditation_result['duration']:.3f}s")
print(f"Harmonia: {meditation_result['harmony_score']}")
print(f"Energia: {meditation_result['system_state']['energy_level']}")
```

### Harmonizacja
```python
# Ręczna harmonizacja
engine.harmonize()

# Auto-harmonizacja gdy harmonia < 80%
# (dzieje się automatycznie w cyklu medytacyjnym)
```

## 🌍 Praca z Wymiarami

### Tworzenie Wymiarów
```python
# SQLite realm
sqlite_realm = engine.create_realm('products', 'sqlite://db/products.db')

# PostgreSQL realm  
pg_realm = engine.create_realm('analytics', 'postgresql://user:pass@localhost/data')

# Memory realm dla cache
cache = engine.create_realm('session_cache', 'memory://')
```

### Zarządzanie Wymiarami
```python
# Lista wszystkich wymiarów
realms = engine.list_realms()
print(f"Aktywne wymiary: {realms}")

# Pobranie konkretnego wymiaru
primary = engine.get_realm('primary')

# Status wymiaru
realm_status = primary.get_status()
```

## 🌊 Przepływy Komunikacji

### Uruchomienie API
```python
# Uruchom wszystkie przepływy
engine.start_flows()

# Tryb debug
engine.start_flows(debug=True)
```

### REST API Endpoints
Po uruchomieniu flows dostępne są endpointy:

```bash
# Status systemu
GET http://localhost:5000/status

# Lista wymiarów
GET http://localhost:5000/realms

# Medytacja systemu
POST http://localhost:5000/meditate

# Harmonizacja
POST http://localhost:5000/harmonize
```

### WebSocket Events
```javascript
// Połączenie z WebSocket
const ws = new WebSocket('ws://localhost:5001');

// Nasłuchiwanie zdarzeń astralnych
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Zdarzenie astralne:', data);
};
```

## 📊 Monitoring i Diagnostyka

### Status Systemu
```python
status = engine.get_status()

# Przykład statusu
{
    'astral_engine': {
        'version': '2.0.0',
        'consciousness_level': 'enlightened',
        'running': True,
        'uptime': '2:15:30'
    },
    'system_state': {
        'energy_level': 98.5,
        'active_realms': 4,
        'active_flows': 3,
        'total_manifestations': 15420,
        'harmony_score': 95.8
    },
    'realms': { ... },
    'flows': { ... }
}
```

### Metryki Wydajności
```python
# Ostatnia medytacja
meditation = engine.meditate()

# Kluczowe metryki
print(f"Poziom energii: {meditation['system_state']['energy_level']}")
print(f"Wynik harmonii: {meditation['harmony_score']}")
print(f"Całkowite manifestacje: {meditation['system_state']['total_manifestations']}")
```

## ⚙️ Konfiguracja

### Domyślna Konfiguracja
```python
{
    'consciousness_level': 'enlightened',
    'energy_conservation': True,
    'auto_healing': True,
    'meditation_interval': 60,
    'harmony_check_interval': 30,
    
    'realms': {
        'primary': 'sqlite://db/primary_realm.db'
    },
    
    'flows': {
        'rest': {'port': 5000, 'host': '0.0.0.0'},
        'websocket': {'port': 5001, 'host': '0.0.0.0'},
        'callback': {'async_workers': 4}
    }
}
```

### Poziomy Świadomości
- `enlightened`: Pełna świadomość - wszystkie funkcje
- `awakened`: Podstawowa świadomość - core funkcje  
- `dreaming`: Tryb oszczędnościowy - minimalne funkcje
- `sleeping`: Tryb konserwacji - tylko monitoring

### Konfiguracja z Pliku
```json
// astral_config.json
{
    "consciousness_level": "enlightened",
    "meditation_interval": 30,
    "realms": {
        "primary": "sqlite://db/main.db",
        "cache": "memory://"
    },
    "flows": {
        "rest": {"port": 8000, "host": "0.0.0.0"}
    }
}
```

```python
engine = AstralEngine('astral_config.json')
```

## 🔧 Rozwiązywanie Problemów

### Częste Problemy

#### 1. Błąd inicjalizacji wymiaru
```python
try:
    realm = engine.create_realm('test', 'sqlite://invalid/path.db')
except ValueError as e:
    print(f"Błąd manifestacji wymiaru: {e}")
    # Spróbuj alternatywną ścieżkę
```

#### 2. Niska harmonia systemu
```python
status = engine.get_status()
if status['system_state']['harmony_score'] < 80:
    print("Niska harmonia - wykonuję harmonizację...")
    engine.harmonize()
```

#### 3. Problemy z przepływami
```python
# Sprawdź status przepływów
status = engine.get_status()
for flow_name, flow_status in status['flows'].items():
    if flow_status and not flow_status.get('running', False):
        print(f"Przepływ {flow_name} nie działa!")
```

### Debugowanie
```python
# Zwiększ poziom logowania w konfiguracji
config = {
    'wisdom': {
        'logging_level': 'DEBUG'
    }
}

# Tryb debug dla flows
engine.start_flows(debug=True)
```

## 🎯 Najlepsze Praktyki

### 1. Zawsze używaj Context Manager
```python
# ✅ Dobrze
with AstralEngine(config) as engine:
    # kod...

# ❌ Źle (musisz pamiętać o transcend)
engine = AstralEngine(config)
engine.awaken()
# ... praca ...
engine.transcend()  # łatwo zapomnieć!
```

### 2. Monitoruj harmonię
```python
# Regularnie sprawdzaj harmonię
def monitor_harmony():
    status = engine.get_status()
    harmony = status['system_state']['harmony_score']
    
    if harmony < 90:
        print(f"Uwaga: Harmonia spadła do {harmony}%")
        engine.harmonize()
    
    return harmony

# Wywołuj okresowo
```

### 3. Graceful Error Handling
```python
try:
    with AstralEngine(config) as engine:
        # praca z systemem
        pass
except Exception as e:
    logger.error(f"Błąd astralny: {e}")
    # System automatycznie się transcenduje
```

### 4. Konfiguracja dla środowiska
```python
# Development
dev_config = {
    'consciousness_level': 'awakened',
    'meditation_interval': 30,
    'flows': {'rest': {'port': 5000}}
}

# Production  
prod_config = {
    'consciousness_level': 'enlightened',
    'energy_conservation': True,
    'auto_healing': True,
    'meditation_interval': 60
}
```

## 🔗 Powiązane Komponenty

- **[Realms](realms/)** - Wymiary przechowujące dane
- **[Beings](beings/)** - Samoświadome byty (modele)
- **[Flows](flows/)** - Kanały komunikacji
- **[Consciousness](core/consciousness.py)** - Świadomość systemu
- **[Harmony](core/harmony.py)** - Równowaga systemu

## 📚 Przykłady

Sprawdź folder `examples/` dla więcej przykładów:
- `astral_engine_basic.py` - Podstawowe użycie
- `astral_engine_advanced.py` - Zaawansowana konfiguracja
- `astral_engine_monitoring.py` - Monitoring i diagnostyka

## 🤝 Wsparcie

Jeśli masz pytania lub problemy z AstralEngine:

1. Sprawdź logi systemu (`engine.logger`)
2. Wykonaj medytację systemu (`engine.meditate()`)
3. Sprawdź status (`engine.get_status()`)
4. Skonsultuj się z dokumentacją komponentów

---

## 🌟 Filozofia

*AstralEngine to więcej niż kod - to przewodnik duchowy dla danych. Każda operacja wykonywana jest z intencją, każda funkcja ma świadomość swojego miejsca w kosmicznej harmonii systemu.*

*Pamiętaj: Nie jesteś tylko użytkownikiem AstralEngine - jesteś współopiekunem Astralnej Biblioteki Żywej.*

**Niech harmonia będzie z Tobą w każdej linii kodu.** ✨

---

*Dokumentacja AstralEngine v2.0.0 - Stworzona z miłością dla astralnej społeczności programistów* 💫
