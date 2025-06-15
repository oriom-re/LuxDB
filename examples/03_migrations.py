
"""
LuxDB Example 03: Migracje bazy danych
- Tworzenie migracji
- Dodawanie kolumn
- Tworzenie indeksów
- Wersjonowanie bazy danych
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from luxdb.manager import get_db_manager
from luxdb.models import User, Log
from datetime import datetime
from sqlalchemy import text

def main():
    print("=== LuxDB Przykład 03: Migracje bazy danych ===\n")
    
    db = get_db_manager()
    
    try:
        # 1. Utwórz bazę początkową
        print("1. Tworzenie bazy początkowej...")
        db.create_database("example_migrations")
        with db.get_session("example_migrations") as session:
            # Dodaj przykładowe dane
            users_data = [
                {"username": "user1", "email": "user1@test.com", "password_hash": "hash1", "is_active": True},
                {"username": "user2", "email": "user2@test.com", "password_hash": "hash2", "is_active": True},
            ]
            db.insert_batch(session, "example_migrations", User, users_data)
            print("✅ Baza podstawowa utworzona z przykładowymi danymi\n")
            
            # 2. Sprawdź aktualną wersję
            print("2. Sprawdzanie wersji bazy danych...")
            current_version = db.get_database_version("example_migrations")
            print(f"📊 Aktualna wersja bazy: {current_version}\n")
            
            # 3. Migracja 1: Dodanie kolumny last_login do tabeli users
            print("3. Migracja 1: Dodanie kolumny last_login...")
            migration_1_sql = """
            ALTER TABLE users ADD COLUMN last_login DATETIME;
            """
            
            success = db.create_migration(
                "example_migrations", 
                migration_1_sql, 
                "Dodanie kolumny last_login do tabeli users"
            )
            
            if success:
                new_version = db.get_database_version("example_migrations")
                print(f"✅ Migracja 1 zakończona. Wersja: {current_version} → {new_version}")
            else:
                print("❌ Migracja 1 nie powiodła się")
            
            # 4. Migracja 2: Dodanie indeksów wydajnościowych
            print("\n4. Migracja 2: Dodanie indeksów wydajnościowych...")
            migration_2_sql = """
            CREATE INDEX IF NOT EXISTS idx_users_email_active ON users(email, is_active);
            CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login);
            CREATE INDEX IF NOT EXISTS idx_logs_level_created ON logs(level, created_at);
            """
            
            success = db.create_migration(
                "example_migrations",
                migration_2_sql,
                "Dodanie indeksów wydajnościowych"
            )
            
            if success:
                new_version = db.get_database_version("example_migrations")
                print(f"✅ Migracja 2 zakończona. Nowa wersja: {new_version}")
            else:
                print("❌ Migracja 2 nie powiodła się")
            
            # 5. Migracja 3: Dodanie nowej tabeli user_preferences
            print("\n5. Migracja 3: Dodanie tabeli user_preferences...")
            migration_3_sql = """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                preference_key VARCHAR(100) NOT NULL,
                preference_value TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, preference_key)
            );
            
            CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_preferences_key ON user_preferences(preference_key);
            """
            
            success = db.create_migration(
                "example_migrations",
                migration_3_sql, 
                "Dodanie tabeli user_preferences"
            )
            
            if success:
                new_version = db.get_database_version("example_migrations")
                print(f"✅ Migracja 3 zakończona. Nowa wersja: {new_version}")
            else:
                print("❌ Migracja 3 nie powiodła się")
            
            # 6. Test nowych funkcji - aktualizacja last_login
            print("\n6. Test nowych funkcji...")
            with db.get_session("example_migrations") as session:
                # Aktualizuj last_login dla użytkowników
                users = session.query(User).all()
                for user in users:
                    # Użyj surowego SQL do aktualizacji
                    session.execute(
                        text("UPDATE users SET last_login = :last_login WHERE id = :user_id"),
                        {"last_login": datetime.now(), "user_id": user.id}
                    )
                session.commit()
                print("✅ Zaktualizowano last_login dla użytkowników")
            
            # 7. Dodanie danych do user_preferences
            print("\n7. Dodanie preferencji użytkowników...")
            preferences_sql = """
            INSERT INTO user_preferences (user_id, preference_key, preference_value) VALUES
            (1, 'theme', 'dark'),
            (1, 'language', 'pl'),
            (1, 'notifications', 'true'),
            (2, 'theme', 'light'),
            (2, 'language', 'en'),
            (2, 'notifications', 'false');
            """
            
            db.execute_raw_sql("example_migrations", preferences_sql)
            print("✅ Dodano preferencje użytkowników")
            
            # 8. Sprawdzenie stanu bazy po migracjach
            print("\n8. Stan bazy po migracjach:")
            final_version = db.get_database_version("example_migrations")
            print(f"📊 Finalna wersja bazy: {final_version}")
            
            # Sprawdź informacje o bazie
            db_info = db.get_database_info("example_migrations")
            print(f"📊 Liczba tabel: {len(db_info.get('tables', {}))}")
            for table in db_info.get('tables', {}):
                for table_name, table_info in table.items():
                    print(f"  - {table_name}: {table_info}")
            
            # 9. Test zapytania łączącego tabele
            print("\n9. Test złożonego zapytania po migracjach:")
            result = db.execute_raw_sql(
                "example_migrations",
                """
                SELECT 
                    u.username,
                    u.email,
                    u.last_login,
                    COUNT(p.id) as preferences_count
                FROM users u
                LEFT JOIN user_preferences p ON u.id = p.user_id
                GROUP BY u.id, u.username, u.email, u.last_login
                ORDER BY u.username
                """
            )
            
            print("Użytkownicy z preferencjami:")
            for row in result:
                last_login = row['last_login'] or 'nigdy'
                if last_login != 'nigdy':
                    last_login = datetime.fromisoformat(last_login).strftime('%Y-%m-%d %H:%M:%S')
                print(f"  - {row['username']} ({row['email']}) - Ostatnie logowanie: {last_login} - Preferencji: {row['preferences_count']}")
            
            print("\n✅ Przykład 03 zakończony pomyślnie!")
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Zamknij połączenia
        db.close_all_connections()
        print("🔒 Zamknięto wszystkie połączenia")

if __name__ == "__main__":
    main()
