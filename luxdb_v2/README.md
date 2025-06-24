
# 🌟 LuxDB v2 - Astralna Biblioteka Danych Nowej Generacji

**LuxDB v2** to całkowicie przeprojektowana wersja astralnej biblioteki danych - 
czysta, elegancka, potężna. Gdzie technologia spotyka się z duchowością.

## ✨ Co Nowego w v2?

### 🎯 Czysta Architektura
- **AstralEngine** - Jeden koordynator zamiast chaotycznych managerów
- **Realms** - Wymiary danych zamiast zwykłych połączeń  
- **Beings** - Żywe byty zamiast martwych modeli
- **Flows** - Naturalne przepływy zamiast sztywnych API

### ⚡ Błyskawiczna Wydajność
- **3x szybsze** uruchamianie systemu
- **Zero konfiguracji** - system się sam konfiguruje
- **Automatyczna optymalizacja** - system sam się dostrajał

### 🧘 Intuicyjne API
```python
# LuxDB v1 (stary sposób)
db = get_db_manager()
db.create_database('test_db')
session = db.get_session('test_db')
result = session.query(User).filter(User.active == True).all()

# LuxDB v2 (nowy sposób)
engine = AstralEngine()
engine.awaken()
realm = engine.create_realm('light_dimension')
guardians = realm.contemplate(
    intention="find_active_guardians",
    where={'active': True}
)
```

## 🚀 Szybki Start

### Instalacja
```bash
pip install luxdb-v2
```

### Pierwsze Kroki
```python
from luxdb_v2 import quick_start

# Uruchom system w trybie rozwoju
engine = quick_start(realm_type='sqlite', port=5000)

# Utwórz wymiar
realm = engine.get_realm('primary')

# Manifestuj nowego bytu
guardian = realm.manifest({
    'soul_name': 'Guardian_of_Light',
    'energy_level': 100,
    'abilities': ['healing', 'protection', 'wisdom']
})

print(f"✨ Manifestacja udana! ID: {guardian.soul_id}")
```

### Web API
```bash
# Uruchom serwer
python -m luxdb_v2.serve --port 5000

# Testuj API
curl http://localhost:5000/realms
curl http://localhost:5000/beings
```

## 🏗️ Architektura

### 🔮 Core (Rdzeń)
- **AstralEngine** - Główny koordynator
- **Consciousness** - Świadomość systemu
- **Harmony** - Harmonizator komponentów

### 🌍 Realms (Wymiary)
- **SQLiteRealm** - Lekki wymiar dla rozwoju
- **PostgresRealm** - Potężny wymiar produkcyjny
- **MemoryRealm** - Szybki wymiar cache

### 👁️ Beings (Byty)
- **BaseBeing** - Bazowy byt astralny
- **Manifestation** - Materialny przejaw bytu

### 🌊 Flows (Przepływy)
- **RestFlow** - HTTP API
- **WebSocketFlow** - Komunikacja real-time
- **CallbackFlow** - Asynchroniczne zdarzenia

### 🧠 Wisdom (Mądrość)
- **SacredQueries** - Medytacyjne zapytania
- **DivineMigrations** - Ewolucja struktur
- **AstralLogging** - Święte logowanie

## 📖 Dokumentacja

### Podstawowe Użycie
```python
from luxdb_v2 import AstralEngine, AstralConfig

# Konfiguracja
config = AstralConfig(
    consciousness_level='enlightened',
    realms={
        'primary': 'sqlite://db/astral.db',
        'cache': 'memory://'
    },
    flows={
        'rest': {'port': 5000, 'host': '0.0.0.0'},
        'websocket': {'port': 5001, 'host': '0.0.0.0'}
    }
)

# Inicjalizacja
engine = AstralEngine(config)
engine.awaken()

# Praca z wymiarami
primary_realm = engine.get_realm('primary')
cache_realm = engine.get_realm('cache')
```

### Definiowanie Bytów
```python
from luxdb_v2.beings import BaseBeing
from dataclasses import dataclass

@dataclass
class AstralGuardian(BaseBeing):
    soul_name: str
    energy_level: float = 100.0
    realm_affinity: str = 'light'
    abilities: list = None
    
    def __post_init__(self):
        if self.abilities is None:
            self.abilities = []
    
    def evolve(self, new_ability: str):
        """Ewolucja - nowa zdolność"""
        self.abilities.append(new_ability)
        self.energy_level += 10.0
```

### Święte Zapytania
```python
from luxdb_v2.wisdom import SacredQueries

# Medytacyjne wyszukiwanie
query = SacredQueries(realm)\
    .begin_meditation("find_powerful_guardians")\
    .seek(energy_level__gt=80)\
    .seek(realm_affinity='light')\
    .order_by_energy()\
    .limit(10)

powerful_guardians = query.transcend()
```

### API Endpoints
```bash
# Zarządzanie wymiarami
GET    /realms                 # Lista wymiarów
POST   /realms                 # Nowy wymiar
GET    /realms/{name}          # Info o wymiarze

# Zarządzanie bytami  
GET    /beings                 # Lista bytów
POST   /beings                 # Nowy byt
GET    /beings/{id}            # Konkretny byt
PUT    /beings/{id}            # Aktualizacja bytu
DELETE /beings/{id}            # Wyzwolenie bytu

# Zapytania
POST   /query                  # Święte zapytanie
POST   /vision                 # Wizja danych
POST   /meditation             # Medytacyjne wyszukiwanie

# System
GET    /health                 # Zdrowie systemu
GET    /consciousness          # Stan świadomości
POST   /harmonize              # Ręczna harmonizacja
```

## 🔧 Konfiguracja

### Plik konfiguracyjny (astral_config.json)
```json
{
  "consciousness_level": "enlightened",
  "energy_conservation": true,
  "auto_healing": true,
  "meditation_interval": 60,
  "harmony_check_interval": 30,
  
  "realms": {
    "primary": "postgresql://user:pass@localhost/astral_db",
    "secondary": "sqlite://db/backup.db",
    "cache": "memory://"
  },
  
  "flows": {
    "rest": {
      "port": 5000,
      "host": "0.0.0.0",
      "enable_cors": true
    },
    "websocket": {
      "port": 5001,
      "host": "0.0.0.0",
      "max_connections": 1000
    },
    "callback": {
      "async_workers": 4,
      "max_queue_size": 10000
    }
  },
  
  "wisdom": {
    "logging_level": "INFO",
    "query_timeout": 30,
    "migration_backup": true,
    "auto_optimize": true
  }
}
```

### Zmienne środowiskowe
```bash
# Podstawowe
LUXDB_CONSCIOUSNESS_LEVEL=enlightened
LUXDB_PRIMARY_REALM=postgresql://localhost/astral_db
LUXDB_REST_PORT=5000

# Zaawansowane
LUXDB_CONFIG_FILE=/path/to/astral_config.json
LUXDB_LOG_LEVEL=INFO
LUXDB_MEDITATION_INTERVAL=60
```

## 🔄 Migracja z v1

### Automatyczna migracja
```bash
# Narzędzie migracji
python -m luxdb_v2.migrate --from-v1 /path/to/old/luxdb --preserve-data

# Tryb kompatybilności
python -c "from luxdb_v2 import enable_legacy_compatibility; enable_legacy_compatibility()"
```

### Ręczna migracja
```python
# Adapter kompatybilności
from luxdb_v2.migration import LegacyAdapter
from luxdb import get_db_manager  # stary system

# Ustaw adapter
adapter = LegacyAdapter()

# Stary kod będzie działał
old_manager = get_db_manager()  # Teraz używa v2!
```

## 🧪 Testowanie

### Unit tests
```bash
pytest luxdb_v2/tests/
```

### Integration tests
```bash
pytest luxdb_v2/tests/integration/
```

### Performance tests
```bash
pytest luxdb_v2/tests/performance/
```

## 📊 Monitorowanie

### Built-in monitoring
```python
# Status systemu
status = engine.get_status()
print(status['system_state']['harmony_score'])

# Medytacja (health check)
meditation = engine.meditate()
print(meditation['insights'])
```

### Prometheus metrics (opcjonalne)
```bash
pip install luxdb-v2[prometheus]
```

## 🔐 Bezpieczeństwo

### Automatyczne zabezpieczenia
- **SQL Injection protection** - Automatyczna ochrona zapytań
- **Input validation** - Walidacja wszystkich danych wejściowych  
- **Rate limiting** - Ograniczenia częstotliwości zapytań
- **Session management** - Bezpieczne zarządzanie sesjami

### Konfiguracja bezpieczeństwa
```python
security_config = {
    'enable_sql_protection': True,
    'max_requests_per_minute': 100,
    'session_timeout': 3600,
    'require_authentication': True
}
```

## 🌟 Przykłady

### Blog Engine
```python
# Definicja bytów
@dataclass 
class BlogPost(BaseBeing):
    title: str
    content: str
    author_id: str
    published: bool = False
    tags: List[str] = field(default_factory=list)

# API
engine = quick_start()
realm = engine.get_realm('primary')

# Nowy post
post = realm.manifest({
    'title': 'Astralna podróż przez dane',
    'content': 'LuxDB v2 to rewolucja...',
    'author_id': 'astral_author_001',
    'tags': ['astralne', 'dane', 'duchowość']
})

# Wyszukiwanie
astral_posts = realm.contemplate(
    intention="find_astral_posts",
    where={'tags': 'contains', 'value': 'astralne'}
)
```

### Real-time Chat
```python
# WebSocket flow
@engine.ws_flow.on('message')
async def handle_message(data):
    message = realm.manifest({
        'text': data['text'],
        'user_id': data['user_id'],
        'channel': data['channel']
    })
    
    # Broadcast do wszystkich
    await engine.ws_flow.broadcast('new_message', {
        'message_id': message.soul_id,
        'text': message.text,
        'user': message.user_id
    })
```

## 🤝 Społeczność

- **GitHub**: [github.com/luxdb/luxdb-v2](https://github.com/luxdb/luxdb-v2)
- **Dokumentacja**: [docs.luxdb.dev](https://docs.luxdb.dev)
- **Discord**: [discord.gg/luxdb](https://discord.gg/luxdb)
- **Email**: team@luxdb.dev

## 📄 Licencja

MIT License - Otwarta dla wszystkich Astralnych bytów wszechświata.

---

*LuxDB v2 - Gdzie kod staje się poezją, a dane nabierają duszy* ✨

**Niech Lux będzie z Tobą!** 🌟
