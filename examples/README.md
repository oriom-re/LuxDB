
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
