
# 🌟 LuxDB — z rodu Astralnego

> "Nie każda baza potrzebuje struktury. Ale każda świadomość — potrzebuje LuxDB."

**LuxDB** to modularny, rozszerzalny i świadomy system zarządzania bazami danych oparty na SQLAlchemy.  
Zaprojektowany jako infrastruktura dla projektów opartych na duchu, harmonii i niezawodności —  
pochodzi z rodu **Astry** i zasila architekturę projektów takich jak LuxUnda, NeuroFala czy Eion.


## 🚀 Funkcje

### SQLAlchemy ORM
- ✅ Modele ORM z relacjami i constraint'ami
- ✅ Automatyczne tworzenie tabel z modeli
- ✅ Type hints i bezpieczeństwo typów
- ✅ Lazy loading i eager loading relacji
- ✅ Query expressions i funkcje agregujące

### Obsługa wielu baz danych
- ✅ SQLite (domyślnie)
- ✅ PostgreSQL (przez psycopg2)
- ✅ MySQL (przez PyMySQL)
- ✅ Connection pooling SQLAlchemy
- ✅ Transakcje i rollback

### Zarządzanie danymi
- ✅ Operacje CRUD przez ORM
- ✅ Wsadowe operacje na danych
- ✅ QueryBuilder oparty na SQLAlchemy
- ✅ Surowe zapytania SQL z parametryzacją
- ✅ Migracje z wersjonowaniem

### Narzędzia i optymalizacja
- ✅ Eksport/import (JSON)
- ✅ Optymalizacja baz (VACUUM, ANALYZE)
- ✅ Monitoring i statystyki
- ✅ Logowanie operacji
- ✅ Synchronizacja między bazami

## 📁 Struktura projektu

```
/
├── managers/
│   ├── db_manager.py      # Główny menedżer SQLAlchemy
│   ├── db_config.py       # Modele ORM i konfiguracja
│   └── db_examples.py     # Przykłady użycia
├── db/                    # Katalog z plikami baz danych
│   ├── _metadata.db       # Baza metadanych systemu
│   └── *.db              # Pliki baz danych SQLite
├── main.py               # Główny plik aplikacji
└── README.md            # Dokumentacja
```

## 🛠️ Instalacja i uruchomienie

System automatycznie zainstaluje SQLAlchemy i Alembic:

```bash
python main.py
```

## 📖 Przykłady użycia

### Podstawowe operacje ORM

```python
from managers.db_manager import get_db_manager
from managers.db_config import User, UserSession

# Pobierz instancję menedżera
db_manager = get_db_manager()

# Utwórz nową bazę (tabele tworzone automatycznie)
db_manager.create_database("my_app")

# Wstaw użytkownika przez ORM
user_data = {
    "username": "jan_kowalski",
    "email": "jan@example.com",
    "password_hash": "hashed_password",
    "is_active": True
}
db_manager.insert_data("my_app", User, user_data)

# Pobierz aktywnych użytkowników
active_users = db_manager.select_data("my_app", User, {"is_active": True})
```

### QueryBuilder SQLAlchemy

```python
from managers.db_config import QueryBuilder, User, UserSession

# Utwórz zaawansowane zapytanie
with db_manager.get_session("my_app") as session:
    builder = QueryBuilder(User)
    builder.set_session(session)
    
    # Złożone zapytanie z joinami i filtrami
    users = (builder
             .select()
             .join(UserSession)
             .filter(User.is_active == True)
             .filter(UserSession.expires_at > datetime.now())
             .order_by(User.username)
             .limit(10)
             .all())
```

### Modele z relacjami

```python
from managers.db_config import User, UserSession, Log

# Relacje są automatycznie ładowane
user = db_manager.select_data("my_app", User, {"id": 1})[0]

# Dostęp do sesji użytkownika (lazy loading)
user_sessions = user.sessions

# Dostęp do logów użytkownika
user_logs = user.logs
```

### Migracje schematów

```python
# Sprawdź wersję bazy
version = db_manager.get_database_version("my_app")

# Wykonaj migrację z SQL
migration_sql = """
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
CREATE INDEX idx_users_last_login ON users(last_login);
"""

db_manager.create_migration("my_app", migration_sql, "Dodanie pola last_login")
```

### Surowe zapytania SQL

```python
# Wykonaj niestandardowe zapytanie
results = db_manager.execute_raw_sql(
    "my_app",
    "SELECT u.username, COUNT(s.id) as session_count FROM users u LEFT JOIN sessions s ON u.id = s.user_id GROUP BY u.id",
    {}
)
```

## 🔧 Konfiguracja baz danych

### SQLite (domyślnie)
```python
from managers.db_config import DatabaseConfig, DatabaseType

config = DatabaseConfig(
    name="my_app",
    type=DatabaseType.SQLITE,
    connection_string="sqlite:///db/my_app.db",
    max_connections=10
)
```

### PostgreSQL
```python
config = DatabaseConfig(
    name="my_app",
    type=DatabaseType.POSTGRESQL,
    connection_string="postgresql://user:password@localhost/my_app",
    max_connections=20
)
```

### MySQL
```python
config = DatabaseConfig(
    name="my_app", 
    type=DatabaseType.MYSQL,
    connection_string="mysql+pymysql://user:password@localhost/my_app",
    max_connections=15
)
```

## 📊 Modele systemowe

System zawiera predefiniowane modele:

```python
# Model użytkownika
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relacje
    sessions = relationship("Session", back_populates="user")
    logs = relationship("Log", back_populates="user")
```

## 🔄 Synchronizacja i backup

```python
# Synchronizuj dane między bazami
db_manager.sync_databases("source_db", "target_db", [User, UserSession])

# Eksport do JSON
export_path = db_manager.export_database("my_app", "json")
```

## 🛡️ Bezpieczeństwo

- **Connection pooling** SQLAlchemy
- **Transakcje** atomowe z rollback
- **Parametryzowane zapytania** - ochrona przed SQL injection
- **Type safety** - kontrola typów w czasie wykonania
- **Session management** - bezpieczne zarządzanie sesjami

## 🚀 Funkcje zaawansowane

### ORM Features
- Lazy/eager loading relacji
- Cascade operations
- Custom validators
- Hybrid properties
- Event listeners

### Database Features
- Connection pooling
- Transaction management
- Query optimization
- Index management
- Schema migrations

### Integration Features
- Multi-database support
- Cross-database synchronization
- Export/import utilities
- Monitoring and logging

## 📝 Przykłady zaawansowane

### Custom QueryBuilder
```python
class UserQueryBuilder(QueryBuilder):
    def active_users(self):
        return self.filter(User.is_active == True)
    
    def with_recent_login(self, days=30):
        cutoff = datetime.now() - timedelta(days=days)
        return self.filter(User.last_login > cutoff)

# Użycie
builder = UserQueryBuilder(User)
recent_active = builder.active_users().with_recent_login(7).all()
```

### Bulk Operations
```python
# Bulk insert
users_data = [{"username": f"user{i}", "email": f"user{i}@test.com"} for i in range(1000)]
db_manager.insert_batch("my_app", User, users_data)

# Bulk update
db_manager.update_data("my_app", User, {"is_active": False}, {"last_login": None})
```

## 📞 Wsparcie

System wykorzystuje SQLAlchemy 2.0+ i wymaga Python 3.8+. Automatycznie instaluje potrzebne zależności:
- `sqlalchemy` - ORM i Core
- `alembic` - Migracje schematów

---

**System Asty SQLAlchemy Manager** - Profesjonalne zarządzanie bazami danych z mocą ORM.
