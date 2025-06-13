
# System Asty - Zaawansowany Menedżer Baz Danych SQLite

Kompleksowy system zarządzania bazami danych SQLite z obsługą wersjonowania, migracji, synchronizacji i replikacji dla rozproszonego systemu Asty.

## 🚀 Funkcje

### Podstawowe zarządzanie bazami
- ✅ Tworzenie i usuwanie baz danych
- ✅ Zarządzanie tabelami (tworzenie, usuwanie, modyfikacja)
- ✅ Operacje CRUD (Create, Read, Update, Delete)
- ✅ Wsadowe operacje na danych
- ✅ Bezpieczne połączenia z Connection pooling

### Wersjonowanie i migracje
- ✅ Automatyczne wersjonowanie schematów
- ✅ System migracji z możliwością rollback
- ✅ Kompatybilność wsteczna
- ✅ Śledzenie zmian w schematach
- ✅ Backup przed migracjami

### Synchronizacja i replikacja
- ✅ Synchronizacja między bazami
- ✅ Obsługa wielu instancji baz
- ✅ Replikacja danych
- ✅ Rozproszony system współpracujących baz

### Narzędzia i optymalizacja
- ✅ Query Builder do złożonych zapytań
- ✅ Eksport/import (SQL, JSON)
- ✅ Optymalizacja baz (VACUUM, ANALYZE)
- ✅ Monitoring i statystyki
- ✅ Logowanie operacji

## 📁 Struktura projektu

```
/
├── managers/
│   ├── db_manager.py      # Główny menedżer baz danych
│   ├── db_config.py       # Konfiguracja i klasy pomocnicze
│   └── db_examples.py     # Przykłady użycia
├── db/                    # Katalog z plikami baz danych
│   ├── _metadata.db       # Baza metadanych systemu
│   └── *.db              # Pliki baz danych użytkownika
├── main.py               # Główny plik aplikacji
└── README.md            # Dokumentacja
```

## 🛠️ Instalacja i uruchomienie

1. Sklonuj projekt do Replit
2. Uruchom główny plik:

```bash
python main.py
```

System automatycznie utworzy potrzebne katalogi i bazę metadanych.

## 📖 Przykłady użycia

### Podstawowe operacje

```python
from managers.db_manager import get_db_manager

# Pobierz instancję menedżera
db_manager = get_db_manager()

# Utwórz nową bazę
db_manager.create_database("my_app")

# Utwórz tabelę
columns = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "name": "TEXT NOT NULL",
    "email": "TEXT UNIQUE NOT NULL",
    "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
}
db_manager.create_table("my_app", "users", columns)

# Wstaw dane
user_data = {
    "name": "Jan Kowalski",
    "email": "jan@example.com"
}
db_manager.insert_data("my_app", "users", user_data)

# Pobierz dane
users = db_manager.select_data("my_app", "users", 
                              where_clause="name LIKE ?",
                              where_params=["%Jan%"])
```

### Query Builder

```python
from managers.db_config import QueryBuilder

# Utwórz builder
builder = QueryBuilder("users")

# Złożone zapytanie
sql, params = builder.select("name", "email") \
                    .where("created_at > ?", "2024-01-01") \
                    .order_by("name") \
                    .limit(10) \
                    .build_select()

# Wykonaj zapytanie
results = db_manager.execute_custom_query("my_app", sql, params)
```

### Migracje

```python
# Sprawdź wersję bazy
version = db_manager.get_database_version("my_app")
print(f"Aktualna wersja: {version}")

# Wykonaj migrację
migration_sql = """
ALTER TABLE users ADD COLUMN phone TEXT;
CREATE INDEX idx_users_phone ON users(phone);
"""

success = db_manager.create_migration("my_app", migration_sql, 
                                    "Dodanie pola telefonu")
```

### Synchronizacja

```python
# Synchronizuj dane między bazami
db_manager.sync_databases("source_db", "target_db", ["users", "orders"])

# Utwórz backup
db_manager._create_database_backup("my_app", "my_app_backup_20241201")
```

## 🔧 Konfiguracja

System używa predefiniowanych konfiguracji w `db_config.py`:

```python
from managers.db_config import DatabaseConfig, DatabaseType

# Konfiguracja bazy głównej
main_config = DatabaseConfig(
    name="main",
    type=DatabaseType.SQLITE,
    max_connections=20,
    backup_enabled=True,
    auto_optimize=True,
    replication_enabled=True,
    replica_targets=["backup_db", "analytics_db"]
)
```

## 📊 Monitoring

```python
# Informacje o bazie
info = db_manager.get_database_info("my_app")
print(f"Baza: {info['name']}")
print(f"Wersja: {info['version']}")
print(f"Rozmiar: {info['size']} bajtów")
print(f"Tabele: {len(info['tables'])}")

# Lista wszystkich baz
databases = db_manager.list_databases()
for db_name in databases:
    print(f"- {db_name}")
```

## 🔄 Eksport/Import

```python
# Eksport do SQL
sql_file = db_manager.export_database("my_app", "sql")
print(f"Eksport SQL: {sql_file}")

# Eksport do JSON
json_file = db_manager.export_database("my_app", "json")
print(f"Eksport JSON: {json_file}")
```

## 🛡️ Bezpieczeństwo

- **Connection pooling** - zarządzanie połączeniami
- **Thread-safe** - bezpieczne operacje wielowątkowe
- **Transakcje** - atomowość operacji
- **Parametryzowane zapytania** - ochrona przed SQL injection
- **Backup** - automatyczne kopie przed zmianami

## 🚀 Funkcje zaawansowane

### Distributed System Support
- Obsługa wielu współpracujących baz
- Automatyczna replikacja
- Konflikt resolution
- Load balancing

### Version Management
- Semantic versioning
- Dependency tracking
- Rollback capabilities
- Schema evolution

### Performance Optimization
- Connection pooling
- Query optimization
- Index management
- VACUUM scheduling

## 📝 Logowanie

System automatycznie loguje wszystkie operacje:

```
INFO - Utworzono bazę danych: my_app
INFO - Utworzono tabelę users w bazie my_app
INFO - Migracja bazy my_app z wersji 1 do 2 zakończona
INFO - Synchronizacja z source_db do target_db zakończona
```

## 🤝 Rozwój

Aby rozszerzyć system:

1. Dodaj nowe metody do `DatabaseManager`
2. Rozszerz `QueryBuilder` o dodatkowe funkcje
3. Utwórz nowe typy migracji w `MigrationType`
4. Dodaj własne schematy tabel do `SYSTEM_TABLES`

## 📞 Wsparcie

System został zaprojektowany jako self-contained i nie wymaga zewnętrznych zależności poza standardową biblioteką Pythona.

---

**System Asty Database Manager** - Profesjonalne zarządzanie bazami danych SQLite dla nowoczesnych aplikacji.
