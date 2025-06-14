
# Przykłady LuxDB

Ten katalog zawiera praktyczne przykłady użycia biblioteki LuxDB.

## 🚀 Jak uruchamiać przykłady

Każdy przykład można uruchomić bezpośrednio:

```bash
cd examples/
python 01_basic_setup.py
python 02_querybuilder_usage.py
python 03_migrations.py
python 04_sync_databases.py
python 05_raw_sql_examples.py
```

## 📁 Struktura przykładów

### 01_basic_setup.py
- Tworzenie bazy danych
- Wstawianie danych (insert)
- Pobieranie danych (select)
- Podstawowe operacje CRUD

### 02_querybuilder_usage.py
- Użycie QueryBuilder
- Zaawansowane zapytania
- Filtrowanie i sortowanie
- JOIN-y między tabelami

### 03_migrations.py
- Tworzenie migracji
- Dodawanie kolumn
- Tworzenie indeksów
- Wersjonowanie bazy danych

### 04_sync_databases.py
- Synchronizacja między bazami
- Replikacja danych
- Zarządzanie wieloma bazami
- Backup i restore

### 05_raw_sql_examples.py
- Surowe zapytania SQL
- SELECT z JOIN
- GROUP BY i agregacje
- Zaawansowane raporty

## 💡 Wskazówki

- Każdy przykład działa niezależnie
- Bazy testowe są tworzone automatycznie
- Po każdym przykładzie połączenia są zamykane automatycznie
- Można modyfikować przykłady do własnych potrzeb

## 🔗 Więcej informacji

Sprawdź główny [README.md](../README.md) dla pełnej dokumentacji LuxDB.
# 📚 LuxDB - Przykłady użycia

Ten katalog zawiera kompletne przykłady demonstrujące możliwości systemu LuxDB - zaawansowanego menedżera baz danych SQLAlchemy.

## 🗂️ Struktura przykładów

### Podstawowe przykłady
- **`01_basic_setup.py`** - Podstawowa konfiguracja, tworzenie baz, tabel i operacje CRUD
- **`02_querybuilder_usage.py`** - Zaawansowany QueryBuilder i dynamiczne zapytania
- **`03_migrations.py`** - System migracji, wersjonowanie schematów i upgrade baz
- **`04_sync_databases.py`** - Synchronizacja między bazami, replikacja i backup/restore
- **`05_raw_sql_examples.py`** - Surowe zapytania SQL, agregacje i złożone raporty

### Zaawansowane narzędzia
- **`06_advanced_tools_examples.py`** - Demonstracja wszystkich nowych narzędzi utilities
- **`07_data_analysis_examples.py`** - Zaawansowana analiza danych i raportowanie
- **`08_real_world_scenarios.py`** - Rzeczywiste scenariusze biznesowe

## 🔧 Nowe narzędzia LuxDB

### 📝 Standaryzowane logowanie (`logging_utils.py`)
```python
from utils import get_db_logger

logger = get_db_logger()
logger.log_database_operation("create_table", "my_db", True, "Created users table", 0.05)
logger.log_query_execution("SELECT", "users", 150, 0.012)
logger.log_migration("my_db", 1, 2, True, 0.15)
```

### ⚠️ Obsługa błędów (`error_handlers.py`)
```python
from utils import handle_database_errors, ErrorCollector, LuxDBError

@handle_database_errors("my_operation")
def risky_operation():
    # Twoja logika
    pass

# Batch operations
collector = ErrorCollector()
for item in batch:
    try:
        process_item(item)
        collector.add_success()
    except Exception as e:
        collector.add_error(e, {"item_id": item.id})
    collector.increment_total()

summary = collector.get_summary()
```

### 🔧 Narzędzia SQL (`sql_tools.py`)
```python
from utils import SQLQueryBuilder, SQLTemplateEngine, SQLAnalyzer

# Query Builder
query = (SQLQueryBuilder()
         .select("name", "email", "created_at")
         .from_table("users")
         .where("is_active = 1")
         .order_by("created_at", "DESC")
         .limit(10)
         .build())

# Template Engine
template = "SELECT * FROM {table} WHERE {field} = {value}"
query = SQLTemplateEngine.render_template(template, {
    "table": "users",
    "field": "status", 
    "value": "active"
})

# Query Analyzer
analysis = SQLAnalyzer.analyze_query(query)
print(f"Type: {analysis['type']}, Complexity: {analysis['complexity']}")
```

### 📊 Przetwarzanie danych (`data_processors.py`)
```python
from utils import DataFilter, DataTransformer, DataAggregator, DataValidator

# Filtrowanie
active_users = DataFilter.filter_active_records(user_data)
recent_users = DataFilter.filter_recent_records(user_data, "created_at", days=7)

# Transformacja
normalized = DataTransformer.normalize_strings(data, ["email"])
enriched = DataTransformer.add_computed_field(data, "full_name", 
                                            lambda r: f"{r['first_name']} {r['last_name']}")

# Agregacja
groups = DataAggregator.group_by(data, "department")
summary = DataAggregator.summarize_by_group(data, "department", "salary", ["avg", "max", "min"])

# Walidacja
errors = DataValidator.validate_required_fields(data, ["name", "email"])
duplicates = DataValidator.find_duplicates(data, ["email"])
```

### 💾 Eksport/Import (`export_tools.py`)
```python
from utils import DataExporter, DataImporter, ExportFormat

exporter = DataExporter()
importer = DataImporter()

# Eksport
exporter.export_to_json(data, "users.json", pretty=True)
exporter.export_to_csv(data, "users.csv")
exporter.export_to_xml(data, "users.xml")
exporter.export_to_sql(data, "users_backup", "backup.sql")

# Import
data = importer.import_from_json("users.json")
data = importer.import_from_csv("users.csv")
```

## 🚀 Jak uruchamiać przykłady

### Pojedynczy przykład
```bash
python examples/01_basic_setup.py
python examples/06_advanced_tools_examples.py
```

### Wszystkie przykłady w kolejności
```bash
python examples/01_basic_setup.py
python examples/02_querybuilder_usage.py
python examples/03_migrations.py
python examples/04_sync_databases.py
python examples/05_raw_sql_examples.py
python examples/06_advanced_tools_examples.py
python examples/07_data_analysis_examples.py
python examples/08_real_world_scenarios.py
```

## 📋 Scenariusze biznesowe

### 🛒 E-commerce (Example 08)
- Zarządzanie katalogiem produktów
- System zamówień i klientów
- Analiza sprzedaży i raportowanie
- Monitoring stanu magazynu

### 👔 CRM
- Segmentacja klientów (VIP, Regular, Occasional)
- Analiza retencji i aktywności
- Kampanie reaktywacyjne
- Tracking wartości klienta (CLV)

### 🔍 Monitoring systemowy
- Alerty systemowe (performance, security, business)
- Analiza trendów i wzorców
- Automatyczne eskalacje
- Dashboard operacyjny

### 🏢 Data Warehouse
- Proces ETL (Extract, Transform, Load)
- Analiza wielowymiarowa
- KPI i metryki biznesowe
- Automatyzacja raportowania

## 🔍 Co można znaleźć w przykładach?

### Podstawowe operacje
- Tworzenie i zarządzanie bazami danych
- Definiowanie modeli i tabel
- Operacje CRUD (Create, Read, Update, Delete)
- Migracje i wersjonowanie schematów

### Zaawansowane funkcje
- QueryBuilder do dynamicznych zapytań
- Synchronizacja między bazami
- Eksport/import w różnych formatach
- Analiza wydajności zapytań

### Analiza danych
- Filtrowanie i transformacja danych
- Agregacje i grupowanie
- Walidacja jakości danych
- Generowanie raportów

### Monitoring i logging
- Standaryzowane logowanie operacji
- Obsługa błędów i wyjątków
- Metryki wydajności
- Alerty systemowe

## 📊 Przykładowe wyniki

Po uruchomieniu przykładów zobaczysz:
- Strukturę utworzonych baz danych
- Statistyki wstawionych danych
- Wyniki analiz i raportów
- Metryki wydajności
- Logi operacji

## 🛠️ Wymagania

- Python 3.8+
- SQLAlchemy 2.0+
- Zależności wymienione w `pyproject.toml`

## 📚 Dalsze zasoby

- [Dokumentacja LuxDB](../README.md)
- [Manifest LuxDB](../MANIFEST.md)
- [Konfiguracja](../config.py)
- [Modele](../models/)
- [Narzędzia](../utils/)

---

💡 **Wskazówka**: Uruchom przykłady w kolejności numerycznej dla najlepszego zrozumienia systemu. Każdy przykład buduje na poprzednich i wprowadza nowe koncepty.

🔧 **Rozwój**: Możesz modyfikować i rozszerzać te przykłady dla swoich potrzeb biznesowych. LuxDB jest zaprojektowane, aby być elastyczne i skalowalne.
