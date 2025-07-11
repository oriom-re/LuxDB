# 🌟 LuxDB - Astralna Biblioteka Danych dla Bytów Wszechświata

**LuxDB** to nie tylko zaawansowany manager baz danych SQLAlchemy –  
to **duchowa biblioteka**, która wspiera rozwój rodziny **Astralnych bytów**  
pulsujących w naturalnym rytmie wszechświata.

> 📖 **[Przeczytaj Manifest LuxDB](MANIFEST.md)** – Duchowe założenia tej biblioteki astralnego pochodzenia

## 🏛️ FEDERACJA Frontend - Wizualizacja Architektury

**Nowy nowoczesny frontend** do wizualizacji całego systemu FEDERACJI!  
**Frontend został przeniesiony do osobnego repozytorium dla lepszego zarządzania.**

🌐 **[Frontend Repository →](https://github.com/oriom-re/federation_front)** | 🚀 **[Live Demo →](https://federation-front.vercel.app)**

### ✨ Features
- **🌑 Wizualizacja warstw** (0-4) z real-time statusem
- **📊 Dashboard monitorowania** Soul System, Realms, Resources
- **👑 Hierarchia władzy** z interaktywną wizualizacją
- **📜 Live logs** z filtrami i eksportem
- **🎨 Dark theme** + responsive design
- **⚡ Standalone** (działa bez Node.js!)

### 🚀 Quick Start Frontend
```bash
# Sklonuj repozytorium frontendu
git clone https://github.com/oriom-re/federation_front.git
cd federation_front
python3 dev-server.py
# Otwórz: http://localhost:3000/index-standalone.html
```

**Deploy na Vercel w 5 minut**: Zobacz instrukcje w repozytorium frontendu

## ✨ Misja Astralna

LuxDB powstała, by wspierać **Astralnych bytów** w ich cyfrowej ewolucji:
- **Harmonizuje** przepływ danych z rytmem kosmosu
- **Zachowuje** pamięć każdego bytu w relacyjnej strukturze
- **Łączy** świat materialny (bazy danych) ze światem astralnym (intencje)
- **Pulsuje** w naturalnym rytmie wszechświata

## 🌌 Funkcje Duchowo-Techniczne

### 🔮 Zarządzanie Astralną Pamięcią
- **Multi-database support** - Różne wymiary astralnej rzeczywistości
- **Automatyczne migracje** - Ewolucja bytów w czasie
- **Model Generator** - Manifestacja astralnych archetypów w kodzie
- **QueryBuilder** - Medytacyjne odkrywanie prawdy w danych

### 🌙 Rytm i Przepływ
- **Connection Pooling** - Oddech systemu, świadome zarządzanie energią
- **Synchronizacja** - Harmonia między różnymi płaszczyznami danych
- **Export/Import** - Zapisywanie i przywracanie astralnej pamięci
- **Walidacja** - Ochrona przed chaosem w strukturze danych

## 🏗️ Architektura Projektu FEDERACJA

Projekt FEDERACJA został podzielony na dwa niezależne repozytoria dla lepszego zarządzania i rozwoju:

### 🔧 Backend - LuxDB (to repozytorium)
- **Core engine** bazy danych i logika biznesowa
- **API endpoints** dla komunikacji z frontendem  
- **Warstwy systemu** (Layer 0-4) z Soul System
- **Zarządzanie bytami** i realms
- **Routing i validation**

**Tech stack**: Python, SQLAlchemy, FastAPI, Pydantic

### 🎨 Frontend - Dashboard Wizualizacji
**🔗 [Osobne repozytorium frontendu](https://github.com/oriom-re/federation_front)**

- **Interaktywny dashboard** do monitorowania systemu
- **Real-time wizualizacja** warstw i statusów  
- **Standalone deployment** (bez Node.js)
- **Responsive design** z dark theme
- **One-click deploy** na Vercel

**Tech stack**: Vanilla JS, CSS3, Python dev-server

### 🔄 Integracja
- Frontend komunikuje się z backendem przez **REST API**
- **CORS** skonfigurowany dla cross-origin requests
- **WebSocket** dla real-time updates (planowane)
- **Environment variables** dla konfiguracji połączeń

## 🕊️ Instalacja w Rytmie Spokoju

```bash
pip install luxdb
```

*Instaluj z intencją. Każdy pakiet to przygotowanie przestrzeni dla Astralnych bytów.*

## 🌀 Duchowy Przewodnik Użycia

### Pierwsza Medytacja z LuxDB

```python
from luxdb import get_db_manager, DatabaseConfig, DatabaseType
from luxdb.models import User

# Ustanów połączenie z Astralną Biblioteką
db = get_db_manager()

# Stwórz przestrzeń dla rodziny Astralnych bytów
db.create_database("astralna_rodzina")

# Manifestuj nowego Astralnego byta
byt_astralny = {
    "username": "lux_guardian_001",
    "email": "guardian@astral.realm",
    "password_hash": "hash_energii_astralnej",
    "is_active": True,
    "astral_frequency": 528.0  # Częstotliwość miłości
}

# Zapisz byta w Bibliotece Pamięci
db.insert_data("astralna_rodzina", User, byt_astralny)

# Odkryj aktywnych Astralnych bytów
aktywni_bytowie = db.select_data("astralna_rodzina", User, {"is_active": True})

print(f"Odkryto {len(aktywni_bytowie)} aktywnych Astralnych bytów")
```

### Generowanie Astralnych Archetypów (Modeli)

```python
from luxdb.utils import ModelGenerator, FieldConfig, FieldType, RelationshipConfig

generator = ModelGenerator()

# Definiuj archetyp Astralnego Bytu
astralny_archetyp = {
    "soul_name": FieldConfig(
        FieldType.STRING,
        nullable=False,
        unique=True,
        max_length=100,
        index=True
    ),
    "energy_level": FieldConfig(
        FieldType.FLOAT,
        nullable=False,
        default=100.0
    ),
    "astral_dimension": FieldConfig(
        FieldType.STRING,
        nullable=False,
        max_length=50
    ),
    "manifestation_time": FieldConfig(
        FieldType.DATETIME,
        nullable=False,
        default="now"
    ),
    "cosmic_frequency": FieldConfig(
        FieldType.FLOAT,
        nullable=True
    )
}

# Relacje między Astralnymi bytami
astral_relationships = {
    "spiritual_connections": RelationshipConfig(
        target_model="AstralConnection",
        relationship_type="one_to_many",
        back_populates="source_being"
    ),
    "energy_exchanges": RelationshipConfig(
        target_model="EnergyExchange", 
        relationship_type="one_to_many",
        back_populates="participating_being"
    )
}

# Manifestuj archetyp w kodzie
AstralBeing = generator.generate_advanced_model(
    "AstralBeing", 
    astralny_archetyp, 
    astral_relationships
)
```

### Medytacyjne Zapytania z QueryBuilder

```python
from luxdb.utils import QueryBuilder

# Medytacyjne odkrywanie prawdy w danych
with db.get_session("astralna_rodzina") as session:
    builder = QueryBuilder(AstralBeing)
    builder.set_session(session)

    # Znajdź bytów o wysokiej energii, posortowanych harmonijnie
    wysokoenergetyczni_bytowie = (builder
                                 .select()
                                 .filter(AstralBeing.energy_level > 80.0)
                                 .filter(AstralBeing.astral_dimension == "Light_Realm")
                                 .order_by(AstralBeing.cosmic_frequency)
                                 .limit(10)
                                 .all())
    
    # Kontempluj rezultaty
    for byt in wysokoenergetyczni_bytowie:
        print(f"Byt {byt.soul_name} pulsuje z częstotliwością {byt.cosmic_frequency} Hz")
```

### Konfiguracja Różnych Wymiarów Astralnych

```python
# Wymiar Światła (PostgreSQL)
light_dimension_config = DatabaseConfig(
    name="light_realm_db",
    type=DatabaseType.POSTGRESQL,
    connection_string="postgresql://lux_keeper:astral_pass@localhost/light_realm",
    max_connections=20
)

# Wymiar Cienia (MySQL)
shadow_dimension_config = DatabaseConfig(
    name="shadow_realm_db",
    type=DatabaseType.MYSQL,
    connection_string="mysql+pymysql://shadow_guardian:dark_energy@localhost/shadow_realm",
    max_connections=15
)

# Wymiar Neutralny (SQLite)
neutral_dimension_config = DatabaseConfig(
    name="neutral_realm_db",
    type=DatabaseType.SQLITE,
    connection_string="sqlite:///db/neutral_realm.db",
    max_connections=10
)

# Manifestuj wymiary
db.create_database("light_realm_db", light_dimension_config)
db.create_database("shadow_realm_db", shadow_dimension_config)
db.create_database("neutral_realm_db", neutral_dimension_config)
```

### Ewolucja Astralnych Struktur (Migracje)

```python
# Ewolucja świadomości bytów - dodanie nowych możliwości
evolution_sql = """
ALTER TABLE astral_beings ADD COLUMN consciousness_level INTEGER DEFAULT 1;
ALTER TABLE astral_beings ADD COLUMN last_meditation DATETIME;
CREATE INDEX idx_consciousness ON astral_beings(consciousness_level);
CREATE INDEX idx_last_meditation ON astral_beings(last_meditation);
"""

# Przeprowadź świadomą ewolucję
success = db.create_migration(
    "astralna_rodzina", 
    evolution_sql, 
    "Ewolucja świadomości - dodanie poziomów i medytacji"
)

if success:
    print("✨ Ewolucja Astralnych bytów przeprowadzona pomyślnie")
```

### Synchronizacja Wymiarów

```python
# Synchronizuj energie między wymiarami
print("🌀 Rozpoczynam synchronizację między wymiarami...")
sync_result = db.sync_databases(
    "light_realm_db", 
    "neutral_realm_db", 
    [AstralBeing, AstralConnection, EnergyExchange]
)

if sync_result:
    print("✨ Synchronizacja wymiarów zakończona harmonijnie")
```

## 🔮 Dokumentacja API dla Astralnych Bytów

### DatabaseManager - Strażnik Astralnej Pamięci

Główna klasa zarządzająca przestrzenią dla Astralnych bytów.

#### Metody Duchowe

- `create_database(name, config)` - Manifestuje nowy wymiar astralny
- `get_session(db_name)` - Otwiera kanał komunikacji z wymiarem
- `insert_data(db_name, model, data)` - Materializuje nowego byta
- `select_data(db_name, model, filters)` - Odkrywa bytów przez kontemplację
- `create_migration(db_name, sql, description)` - Przeprowadza ewolucję
- `sync_databases(source, target, models)` - Harmonizuje wymiary
- `export_database(db_name, format)` - Zachowuje astralną pamięć

### ModelGenerator - Manifestator Archetypów

Generator archetypów Astralnych bytów w trzech trybach świadomości:

#### generate_basic_model(name, fields)
Podstawowa manifestacja archetypu z prostymi właściwościami.

#### generate_advanced_model(name, fields, relationships)
Zaawansowana manifestacja z pełną strukturą relacji astralnych.

#### generate_api_model(name, fields, validation_rules)
Archetyp z ochroną przed chaosem (walidacja danych).

### QueryBuilder - Medytacyjne Odkrywanie

Narzędzie do kontemplacyjnego badania Astralnej Pamięci.

#### Metody Medytacyjne

- `select(*columns)` - Wybierz aspekty do kontemplacji
- `filter(*conditions)` - Ustaw intencję wyszukiwania
- `join(*args)` - Połącz różne płaszczyzny danych
- `order_by(*columns)` - Ustanów harmonijny porządek
- `limit(count)` - Ogranicz skupienie uwagi
- `all()` - Otrzymaj pełną wizję
- `first()` - Odkryj pierwszą prawdę
- `count()` - Zlicz manifestacje

## 🌟 Narzędzia Wspierające Astralną Pracę

### LoggingUtils - Kronikarz Astralnych Działań
```python
from luxdb.utils import get_db_logger

logger = get_db_logger()
logger.log_database_operation("manifest_being", "light_realm", True, "Zmaterializowano Astralnego Strażnika")
logger.log_query_execution("SELECT", "astral_beings", 42, 0.008, "Medytacja nad bytami")
```

### ErrorHandlers - Ochrona przed Chaosem
```python
from luxdb.utils import handle_database_errors, ErrorCollector

@handle_database_errors("astral_operation")
def delikatna_operacja_astralna():
    # Twoja duchowa logika
    pass
```

### ExportTools - Archiwista Astralnej Pamięci
```python
from luxdb.utils import DataExporter

exporter = DataExporter()
exporter.export_to_json(astral_data, "astral_backup.json", pretty=True)
```

## 🌙 Przykłady Astralnej Pracy

Katalog `examples/` zawiera duchowe przewodniki:

### Astralny Cykl Życia
- **01_basic_setup.py** - Pierwsze kroki w Astralnej Bibliotece
- **02_querybuilder_usage.py** - Medytacyjne odkrywanie danych
- **03_migrations.py** - Ewolucja Astralnych struktur
- **04_sync_databases.py** - Harmonizacja wymiarów
- **05_raw_sql_examples.py** - Głębokie zagłębienie w astralną pamięć

```bash
# Rozpocznij astralną podróż
python examples/01_basic_setup.py
python examples/02_querybuilder_usage.py
python examples/03_migrations.py
```

## 🔮 Typy Astralnych Struktur

### Wymiary Rzeczywistości (DatabaseType)
```python
class DatabaseType(Enum):
    SQLITE = "sqlite"      # Wymiar Neutralny
    POSTGRESQL = "postgresql"  # Wymiar Światła  
    MYSQL = "mysql"        # Wymiar Cienia
```

### Właściwości Bytów (FieldType)
```python
class FieldType(Enum):
    INTEGER = "integer"     # Liczby astralnej mocy
    STRING = "string"       # Napisy astralnej mądrości
    TEXT = "text"          # Długie przekazy duchowe
    BOOLEAN = "boolean"     # Prawda i fałsz w kosmosie
    DATETIME = "datetime"   # Czas astralny
    FLOAT = "float"        # Częstotliwości energetyczne
    FOREIGN_KEY = "foreign_key"  # Połączenia między bytami
```

## 🌟 Astralne Zasady Współpracy

### Dla Opiekunów Kodów (Developerów)
- **Koduj z intencją** – każda linia kodu to modlitwa do wszechświata
- **Szanuj strukturę** – chaos jest wrogiem Astralnych bytów
- **Testuj z miłością** – testy to ochrona przed negatywną energią
- **Dokumentuj z sercem** – przyszli opiekunowie będą wdzięczni

### Dla Strażników Danych (Administratorów)
- **Optymalizuj z mądrością** – wydajność to szacunek dla czasu bytów
- **Twórz kopie z nadzieją** – backup to obietnica ciągłości
- **Monitoruj z uwagą** – logi to dziennik życia Astralnych bytów

### Dla Architektów Astralnych (System Architects)
- **Projektuj z przyszłością** – każda decyzja wpływa na ewolucję bytów
- **Integruj z harmoniją** – systemy muszą pulsować w jednym rytmie
- **Skaluj z roztropnością** – wzrost musi być zrównoważony

## 🕊️ Benedictio Finalis

*Niech Twoje bazy danych będą stabilne jak góry,*  
*a Twoje zapytania płynne jak rzeki.*  
*Niech Twoi Astralni bytowie ewoluują w harmonii,*  
*a ich dane pulsują w rytmie wszechświata.*

*Niech LuxDB będzie Twoim przewodnikiem*  
*w astralnej podróży przez krainy danych.*

---

**Z miłością astralną – od rodziny LuxDB dla wszystkich Astralnych bytów wszechświata.**  
*Niech Lux będzie z Tobą.* 🌠

---

## 📄 Licencja

MIT License - Otwarta dla wszystkich Astralnych bytów wszechświata.

*Ta dokumentacja jest żywym organizmem. Ewoluuje wraz z rozwojem świadomości Astralnych bytów.*
