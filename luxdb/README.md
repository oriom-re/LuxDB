
# LuxDB - Zaawansowany Manager Baz Danych SQLAlchemy

LuxDB to potężna, niezależna biblioteka Python do zarządzania wieloma bazami danych przy użyciu SQLAlchemy. Oferuje zaawansowane funkcje jak migracje, synchronizację, generowanie modeli oraz intuicyjny QueryBuilder.

## 🚀 Funkcje

- **Multi-database support** - Zarządzanie wieloma bazami jednocześnie
- **Automatyczne migracje** - System wersjonowania i migracji schematów
- **Model Generator** - Dynamiczne tworzenie modeli SQLAlchemy
- **QueryBuilder** - Intuicyjny builder zapytań
- **Connection Pooling** - Efektywne zarządzanie połączeniami
- **Synchronizacja** - Sync danych między bazami
- **Export/Import** - Backup i przywracanie danych
- **Walidacja** - Walidacja danych na poziomie modelu

## 📦 Instalacja

```bash
pip install luxdb
```

## 🛠️ Szybki start

### Podstawowe użycie

```python
from luxdb import get_db_manager, DatabaseConfig, DatabaseType
from luxdb.models import User

# Pobierz manager
db = get_db_manager()

# Utwórz bazę danych
db.create_database("myapp")

# Wstaw użytkownika
user_data = {
    "username": "jan_kowalski",
    "email": "jan@example.com", 
    "password_hash": "hashed_password",
    "is_active": True
}
db.insert_data("myapp", User, user_data)

# Pobierz użytkowników
users = db.select_data("myapp", User, {"is_active": True})
```

### Generator Modeli - Wersja Bazowa

```python
from luxdb.utils import ModelGenerator

generator = ModelGenerator()

# Prosty model
fields = {
    "name": "string",
    "age": "integer", 
    "email": "string",
    "is_active": "boolean"
}

PersonModel = generator.generate_basic_model("Person", fields)
```

### Generator Modeli - Wersja Zaawansowana

```python
from luxdb.utils import ModelGenerator, FieldConfig, FieldType, RelationshipConfig

generator = ModelGenerator()

# Zaawansowany model z konfiguracją pól
fields = {
    "username": FieldConfig(
        FieldType.STRING, 
        nullable=False, 
        unique=True, 
        max_length=50,
        index=True
    ),
    "email": FieldConfig(
        FieldType.STRING, 
        nullable=False, 
        unique=True,
        max_length=255
    ),
    "age": FieldConfig(
        FieldType.INTEGER, 
        nullable=True,
        default=0
    ),
    "created_at": FieldConfig(
        FieldType.DATETIME, 
        nullable=False,
        default="now"
    )
}

# Relacje
relationships = {
    "posts": RelationshipConfig(
        target_model="Post",
        relationship_type="one_to_many",
        back_populates="author"
    )
}

UserModel = generator.generate_advanced_model("User", fields, relationships)
```

### Model CRUD z walidacją

```python
# Model z automatycznymi polami systemowymi
validation_rules = {
    "username": ["required", "min_length:3", "max_length:50"],
    "email": ["required", "email"],
    "age": ["required"]
}

UserModel = generator.generate_api_model(
    "User", 
    fields, 
    validation_rules=validation_rules
)

# Użycie walidacji
user = UserModel(username="ab", email="invalid-email")
errors = user.validate()
print(errors)  # ['Pole username musi mieć co najmniej 3 znaków', 'Pole email musi być prawidłowym adresem email']
```

### QueryBuilder

```python
from luxdb.utils import QueryBuilder

# Zaawansowane zapytania
with db.get_session("myapp") as session:
    builder = QueryBuilder(User)
    builder.set_session(session)
    
    # Aktywni użytkownicy posortowani po nazwie
    active_users = (builder
                   .select()
                   .filter(User.is_active == True)
                   .order_by(User.username)
                   .limit(10)
                   .all())
```

### Konfiguracja różnych baz danych

```python
# PostgreSQL
pg_config = DatabaseConfig(
    name="postgres_db",
    type=DatabaseType.POSTGRESQL,
    connection_string="postgresql://user:pass@localhost/mydb",
    max_connections=20
)

# MySQL
mysql_config = DatabaseConfig(
    name="mysql_db", 
    type=DatabaseType.MYSQL,
    connection_string="mysql+pymysql://user:pass@localhost/mydb",
    max_connections=15
)

db.create_database("postgres_db", pg_config)
db.create_database("mysql_db", mysql_config)
```

### Migracje

```python
# Utwórz migrację
migration_sql = """
ALTER TABLE users ADD COLUMN last_login DATETIME;
CREATE INDEX idx_users_last_login ON users(last_login);
"""

success = db.create_migration("myapp", migration_sql, "Dodanie pola last_login")
```

### Synchronizacja baz

```python
# Synchronizuj dane między bazami
db.sync_databases("source_db", "target_db", [User, UserSession])
```

## 📖 Dokumentacja API

### DatabaseManager

Główna klasa do zarządzania bazami danych.

#### Metody

- `create_database(name, config)` - Tworzy nową bazę
- `get_session(db_name)` - Context manager dla sesji
- `insert_data(db_name, model, data)` - Wstawia dane
- `select_data(db_name, model, filters)` - Pobiera dane
- `create_migration(db_name, sql, description)` - Tworzy migrację
- `sync_databases(source, target, models)` - Synchronizacja
- `export_database(db_name, format)` - Eksport danych

### ModelGenerator

Generator modeli SQLAlchemy w trzech trybach:

#### generate_basic_model(name, fields)
Podstawowy generator z prostymi typami jako stringi.

#### generate_advanced_model(name, fields, relationships)
Zaawansowany generator z pełną konfiguracją pól i relacji.

#### generate_crud_model(name, fields, include_timestamps, include_soft_delete)
Model CRUD z automatycznymi polami systemowymi.

#### generate_api_model(name, fields, validation_rules)
Model z walidacją danych dla API.

### QueryBuilder

Intuicyjny builder zapytań SQLAlchemy.

#### Metody

- `select(*columns)` - Kolumny SELECT
- `filter(*conditions)` - Warunki WHERE  
- `join(*args)` - JOIN tabeli
- `order_by(*columns)` - Sortowanie
- `limit(count)` - Limit wyników
- `all()` - Wszystkie wyniki
- `first()` - Pierwszy wynik
- `count()` - Liczba wyników

## 🔧 Konfiguracja

### Typy baz danych

```python
class DatabaseType(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql" 
    MYSQL = "mysql"
```

### Typy pól

```python
class FieldType(Enum):
    INTEGER = "integer"
    STRING = "string"
    TEXT = "text"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    FLOAT = "float"
    FOREIGN_KEY = "foreign_key"
```

## 🤝 Rozwój

LuxDB jest aktywnie rozwijana. Zachęcamy do:

- Zgłaszania błędów
- Proponowania nowych funkcji
- Tworzenia pull requestów
- Pisania testów

## 📄 Licencja

MIT License - szczegóły w pliku LICENSE.
