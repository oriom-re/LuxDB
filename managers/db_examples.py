
"""
Przykłady użycia menedżera baz danych SQLAlchemy
"""

import logging
import json
from datetime import datetime, timedelta
import sys
import os

# Dodaj główny katalog do ścieżki
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from manager import get_db_manager, DatabaseManager
from config import DatabaseConfig, DatabaseType
from models import User, Log, UserSession
from utils import QueryBuilder

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def example_basic_usage():
    """Podstawowe przykłady użycia SQLAlchemy"""
    print("=== Podstawowe użycie menedżera baz danych SQLAlchemy ===")

    # Pobierz instancję menedżera
    db_manager = get_db_manager()

    # Utwórz nową bazę danych
    print("Tworzenie bazy danych 'example'...")
    db_manager.create_database("example")

    print("Tabele zostały utworzone automatycznie z modeli SQLAlchemy")

    # Wstaw przykładowych użytkowników
    print("Wstawianie przykładowych użytkowników...")
    users_data = [
        {
            "username": "admin",
            "email": "admin@example.com", 
            "password_hash": "hashed_password_1",
            "is_active": True,
            "phone": "+48123456789"
        },
        {
            "username": "user1",
            "email": "user1@example.com",
            "password_hash": "hashed_password_2", 
            "is_active": True,
            "phone": "+48123456789"
        },
        {
            "username": "user2",
            "email": "user2@example.com",
            "password_hash": "hashed_password_3",
            "is_active": False,
            "phone": None
        }
    ]

    db_manager.insert_batch("example", User, users_data)

    # Pobierz wszystkich aktywnych użytkowników
    print("Pobieranie aktywnych użytkowników...")
    with db_manager.get_session("example") as db_session:
        active_users = db_session.query(User).filter(User.is_active == True).all()
        print(f"Znaleziono {len(active_users)} aktywnych użytkowników:")
        for user in active_users:
            print(f"  - {user.username} ({user.email})")

        # Aktualizuj dane użytkownika
        print("Aktualizacja danych użytkownika...")
        updated_rows = db_session.query(User).filter(User.username == "admin").update(
            {"email": "new_admin@example.com"}
        )

        # Sprawdź zaktualizowane dane
        print("Sprawdzenie zaktualizowanych danych...")
        all_users = db_session.query(User).all()

        for user in all_users:
            print(f"  - {user.username} ({user.email}) ({user.phone})")

        print(f"Zaktualizowano {updated_rows} rekordów")

        # Dodaj sesje użytkowników
        print("Dodawanie sesji użytkowników...")
        sessions_data = [
            {
                "id": "session_1",
                "user_id": 1,
                "expires_at": datetime.now() + timedelta(hours=24),
                "data": json.dumps({"theme": "dark", "language": "pl"})
            },
            {
                "id": "session_2", 
                "user_id": 2,
                "expires_at": datetime.now() + timedelta(hours=12),
                "data": json.dumps({"theme": "light", "language": "en"})
            }
        ]
        db_session.add_all([UserSession(**session) for session in sessions_data])
        db_session.commit()

        # Pobierz informacje o bazie
        print("\nInformacje o bazie danych:")
        db_info = db_manager.get_database_info("example")
        print(json.dumps(db_info, indent=2, default=str))

def example_query_builder():
    """Przykład użycia QueryBuilder SQLAlchemy"""
    print("\n=== Przykład QueryBuilder SQLAlchemy ===")

    db_manager = get_db_manager()

    try:
        with db_manager.get_session("example") as session:
            builder = QueryBuilder(User)
            builder.set_session(session)

            # Pobierz aktywnych użytkowników
            active_users = builder.select().filter(User.is_active == True).order_by(User.username).all()

            print(f"QueryBuilder - aktywni użytkownicy: {len(active_users)}")
            for user in active_users:
                print(f"  - {user.username} ({user.email})")

            # Złożone zapytanie z joinami
            builder.reset()
            users_with_sessions = (builder
                                 .select()
                                 .join(UserSession)
                                 .filter(UserSession.expires_at > datetime.now())
                                 .all())

            print(f"Użytkownicy z aktywnymi sesjami: {len(users_with_sessions)}")
            for user in users_with_sessions:
                print(f"  - {user.username}")

    except Exception as e:
        print(f"Błąd QueryBuilder: {e}")

def example_advanced_queries():
    """Przykład zaawansowanych zapytań SQLAlchemy"""
    print("\n=== Przykład zaawansowanych zapytań ===")

    db_manager = get_db_manager()

    # Surowe zapytanie SQL
    print("Wykonywanie surowego zapytania SQL...")
    sql_result = db_manager.execute_raw_sql(
        "example",
        "SELECT u.username, u.email, COUNT(s.id) as session_count FROM users u LEFT JOIN sessions s ON u.id = s.user_id GROUP BY u.id, u.username, u.email"
    )

    print("Wyniki surowego zapytania:")
    for row in sql_result:
        print(f"  - {row['username']}: {row['session_count']} sesji")

def example_models_and_relationships():
    """Przykład pracy z modelami i relacjami"""
    print("\n=== Przykład modeli i relacji SQLAlchemy ===")

    db_manager = get_db_manager()

    try:
        # Pobierz użytkowników wraz z sesjami (lazy loading)
        users = db_manager.select_data("example", User)

        print("Użytkownicy i ich sesje:")
        for user in users:
            print(f"  - {user.username}")

        # Dodaj logi
        logs_data = [
            {
                "level": "INFO",
                "message": "Użytkownik zalogowany",
                "module": "auth",
                "user_id": 1,
                "ip_address": "192.168.1.1"
            },
            {
                "level": "WARNING", 
                "message": "Nieudana próba logowania",
                "module": "auth",
                "user_id": None,
                "ip_address": "192.168.1.100"
            }
        ]

        db_manager.insert_batch("example", Log, logs_data)
        print("Dodano logi systemowe")

    except Exception as e:
        print(f"Błąd podczas pracy z modelami: {e}")

def example_migrations():
    """Przykład systemu migracji SQLAlchemy"""
    print("\n=== Przykład migracji SQLAlchemy ===")

    db_manager = get_db_manager()

    # Sprawdź aktualną wersję
    current_version = db_manager.get_database_version("example")
    print(f"Aktualna wersja bazy: {current_version}")

    # Przygotuj migrację - dodanie indeksu
    migration_sql = """
    CREATE INDEX IF NOT EXISTS idx_users_email_active ON users(email, is_active);
    CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
    """

    print("Wykonywanie migracji...")
    success = db_manager.create_migration("example", migration_sql, "Dodanie indeksów wydajnościowych")

    if success:
        new_version = db_manager.get_database_version("example")
        print(f"Migracja zakończona. Nowa wersja: {new_version}")
    else:
        print("Migracja nie powiodła się")

def example_export_import():
    """Przykład eksportu i importu danych"""
    print("\n=== Przykład eksportu/importu ===")

    db_manager = get_db_manager()

    # Eksport do JSON
    print("Eksport bazy do JSON...")
    json_export_path = db_manager.export_database("example", "json")
    if json_export_path:
        print(f"Eksport JSON zapisany w: {json_export_path}")

def run_all_examples():
    """Uruchamia wszystkie przykłady SQLAlchemy"""
    try:
        example_basic_usage()
        example_query_builder()
        example_advanced_queries()
        example_models_and_relationships()
        example_migrations()
        example_export_import()

        print("\n=== Lista wszystkich baz danych ===")
        db_manager = get_db_manager()
        databases = db_manager.list_databases()
        print("Dostępne bazy danych SQLAlchemy:")
        for db_name in databases:
            print(f"  - {db_name}")

    except Exception as e:
        print(f"Błąd podczas wykonywania przykładów: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Zamknij wszystkie połączenia
        db_manager = get_db_manager()
        db_manager.close_all_connections()
        print("\nZamknięte wszystkie połączenia SQLAlchemy")

if __name__ == "__main__":
    run_all_examples()
