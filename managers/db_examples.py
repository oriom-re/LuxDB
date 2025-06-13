
"""
Przykłady użycia menedżera baz danych
"""

from db_manager import get_db_manager, DatabaseManager
from db_config import SYSTEM_TABLES, QueryBuilder, DatabaseConfig, Migration, MigrationType
import json

def example_basic_usage():
    """Podstawowe przykłady użycia"""
    print("=== Podstawowe użycie menedżera baz danych ===")
    
    # Pobierz instancję menedżera
    db_manager = get_db_manager()
    
    # Utwórz nową bazę danych
    print("Tworzenie bazy danych 'example'...")
    db_manager.create_database("example")
    
    # Utwórz tabelę użytkowników
    print("Tworzenie tabeli users...")
    user_schema = SYSTEM_TABLES["users"]
    db_manager.create_table(
        "example", 
        user_schema.name, 
        user_schema.columns,
        user_schema.constraints
    )
    
    # Dodaj indeksy
    for index_sql in user_schema.indexes:
        db_manager.execute_custom_query("example", index_sql)
    
    # Wstaw przykładowych użytkowników
    print("Wstawianie przykładowych użytkowników...")
    users_data = [
        {
            "username": "admin",
            "email": "admin@example.com", 
            "password_hash": "hashed_password_1",
            "is_active": 1,
            "phone": "+48123456789"
        },
        {
            "username": "user1",
            "email": "user1@example.com",
            "password_hash": "hashed_password_2", 
            "is_active": 1,
            "phone": "+48123456789"
        },
        {
            "username": "user2",
            "email": "user2@example.com",
            "password_hash": "hashed_password_3",
            "is_active": 0,
            "phone": None
        }
    ]
    
    db_manager.insert_batch("example", "users", users_data)
    
    # Pobierz wszystkich aktywnych użytkowników
    print("Pobieranie aktywnych użytkowników...")
    active_users = db_manager.select_data(
        "example", 
        "users", 
        where_clause="is_active = ?",
        where_params=[1]
    )
    
    print(f"Znaleziono {len(active_users)} aktywnych użytkowników:")
    for user in active_users:
        print(f"  - {user['username']} ({user['email']})")
    
    # Aktualizuj dane użytkownika
    print("Aktualizacja danych użytkownika...")
    updated_rows = db_manager.update_data(
        "example",
        "users",
        {"email": "new_admin@example.com"},
        "username = ?",
        ["admin"]
    )
    users = db_manager.select_data("example", "users")
    for user in users:
        print(f"  - {user['username']} ({user['email']}) ({user['phone']})")

    print(f"Zaktualizowano {updated_rows} rekordów")
    
    # Pobierz informacje o bazie
    print("\nInformacje o bazie danych:")
    db_info = db_manager.get_database_info("example")
    print(json.dumps(db_info, indent=2, default=str))

def example_query_builder():
    """Przykład użycia QueryBuilder"""
    print("\n=== Przykład QueryBuilder ===")
    
    db_manager = get_db_manager()
    
    # Utwórz builder zapytań
    builder = QueryBuilder("users")
    
    # Złożone zapytanie z joinami
    sql, params = builder.select("u.username", "u.email", "s.id as session_id") \
                         .join("sessions s", "s.user_id = u.id") \
                         .where("u.is_active = ?", 1) \
                         .where("s.expires_at > datetime('now')") \
                         .order_by("u.username") \
                         .limit(10) \
                         .build_select()
    
    print(f"Wygenerowane zapytanie SQL: {sql}")
    print(f"Parametry: {params}")
    
    # Zapytanie UPDATE
    builder.reset()
    update_sql, update_params = builder.where("username = ?", "admin") \
                                     .build_update({"email": "updated@example.com"})
    
    print(f"UPDATE SQL: {update_sql}")
    print(f"Parametry: {update_params}")

def example_migrations():
    """Przykład systemu migracji"""
    print("\n=== Przykład migracji ===")
    
    db_manager = get_db_manager()
    
    # Sprawdź aktualną wersję
    current_version = db_manager.get_database_version("example")
    print(f"Aktualna wersja bazy: {current_version}")
    
    # Przygotuj migrację - dodanie kolumny 'phone'
    migration_sql = """
    ALTER TABLE users ADD COLUMN phone TEXT;
    CREATE INDEX idx_users_phone ON users(phone);
    """
    
    print("Wykonywanie migracji...")
    success = db_manager.create_migration("example", migration_sql, "Dodanie pola telefonu")
    
    if success:
        new_version = db_manager.get_database_version("example")
        print(f"Migracja zakończona. Nowa wersja: {new_version}")
        
        # Dodaj numer telefonu do istniejącego użytkownika
        db_manager.update_data(
            "example",
            "users", 
            {"phone": "+48123456789"},
            "username = ?",
            ["admin"]
        )
        print("Dodano numer telefonu dla admina")
    else:
        print("Migracja nie powiodła się")

def example_distributed_sync():
    """Przykład synchronizacji między bazami"""
    print("\n=== Przykład synchronizacji baz ===")
    
    db_manager = get_db_manager()
    
    # Utwórz bazę backup
    print("Tworzenie bazy backup...")
    db_manager.create_database("example_backup")
    
    # Synchronizuj dane
    print("Synchronizacja danych...")
    success = db_manager.sync_databases("example", "example_backup", ["users"])
    
    if success:
        print("Synchronizacja zakończona")
        
        # Sprawdź dane w backup
        backup_users = db_manager.select_data("example_backup", "users")
        print(f"Baza backup zawiera {len(backup_users)} użytkowników")
    else:
        print("Synchronizacja nie powiodła się")

def example_export_import():
    """Przykład eksportu i importu danych"""
    print("\n=== Przykład eksportu/importu ===")
    
    db_manager = get_db_manager()
    
    # Eksport do SQL
    print("Eksport bazy do SQL...")
    sql_export_path = db_manager.export_database("example", "sql")
    if sql_export_path:
        print(f"Eksport SQL zapisany w: {sql_export_path}")
    
    # Eksport do JSON
    print("Eksport bazy do JSON...")
    json_export_path = db_manager.export_database("example", "json")
    if json_export_path:
        print(f"Eksport JSON zapisany w: {json_export_path}")

def example_optimization():
    """Przykład optymalizacji bazy"""
    print("\n=== Przykład optymalizacji ===")
    
    db_manager = get_db_manager()
    
    # Optymalizuj bazę
    print("Optymalizacja bazy danych...")
    success = db_manager.optimize_database("example")
    
    if success:
        print("Optymalizacja zakończona")
    else:
        print("Optymalizacja nie powiodła się")

def run_all_examples():
    """Uruchamia wszystkie przykłady"""
    try:
        example_basic_usage()
        example_query_builder()
        # example_migrations()
        # example_distributed_sync()
        # example_export_import()
        # example_optimization()
        
        print("\n=== Lista wszystkich baz danych ===")
        db_manager = get_db_manager()
        databases = db_manager.list_databases()
        print("Dostępne bazy danych:")
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
        print("\nZamknięte wszystkie połączenia")

if __name__ == "__main__":
    run_all_examples()
