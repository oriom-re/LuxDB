
"""
LuxDB Example 01: Podstawowe operacje
- Tworzenie bazy danych
- Insert, select, update, delete
- Praca z modelami
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from luxdb.manager import get_db_manager
from luxdb.models import User, UserSession, Log
from datetime import datetime, timedelta
import json

def main():
    print("=== LuxDB Przykład 01: Podstawowe operacje ===\n")
    
    # Pobierz manager bazy danych
    db = get_db_manager()
    
    try:
        # 1. Tworzenie bazy danych
        print("1. Tworzenie bazy danych 'example_basic'...")
        db.create_database("example_basic")
        print("✅ Baza danych utworzona\n")
        
        # 2. Wstawianie użytkowników
        print("2. Wstawianie przykładowych użytkowników...")
        users_data = [
            {
                "username": "jan_kowalski",
                "email": "jan@example.com",
                "password_hash": "hashed_password_1",
                "is_active": True,
                "phone": "+48123456789"
            },
            {
                "username": "anna_nowak",
                "email": "anna@example.com", 
                "password_hash": "hashed_password_2",
                "is_active": True,
                "phone": "+48987654321"
            },
            {
                "username": "test_user",
                "email": "test@example.com",
                "password_hash": "hashed_password_3",
                "is_active": False,
                "phone": None
            }
        ]
        
        # Wstaw użytkowników wsadowo
        db.insert_batch("example_basic", User, users_data)
        print(f"✅ Wstawiono {len(users_data)} użytkowników\n")
        
        # 3. Pobieranie danych
        print("3. Pobieranie użytkowników...")
        
        # Wszyscy użytkownicy
        with db.get_session("example_basic") as session:
            all_users = db.select_data(session, "example_basic", User)
            print(f"📊 Wszystkich użytkowników: {len(all_users)}")
            
            # Tylko aktywni użytkownicy
            active_users = db.select_data(session, "example_basic", User, {"is_active": True})
            print(f"📊 Aktywnych użytkowników: {len(active_users)}")
            
            print("\nLista aktywnych użytkowników:")
            for user in active_users:
                print(f"  - {user.username} ({user.email}) - Tel: {user.phone}")
        
        # 4. Aktualizacja danych
        print("\n4. Aktualizacja danych użytkownika...")
        with db.get_session("example_basic") as session:
            # Znajdź użytkownika i zaktualizuj email
            user_to_update = session.query(User).filter(User.username == "jan_kowalski").first()
            if user_to_update:
                old_email = user_to_update.email
                user_to_update.email = "jan.kowalski.nowy@example.com"
                session.commit()
                print(f"✅ Zaktualizowano email: {old_email} → {user_to_update.email}")
        
        # 5. Dodawanie sesji użytkowników
        print("\n5. Dodawanie sesji użytkowników...")
        sessions_data = [
            {
                "id": "session_basic_1",
                "user_id": 1,
                "expires_at": datetime.now() + timedelta(hours=24),
                "data": json.dumps({"theme": "dark", "language": "pl"})
            },
            {
                "id": "session_basic_2",
                "user_id": 2, 
                "expires_at": datetime.now() + timedelta(hours=12),
                "data": json.dumps({"theme": "light", "language": "en"})
            }
        ]
        
        db.insert_batch("example_basic", UserSession, sessions_data)
        print(f"✅ Dodano {len(sessions_data)} sesji użytkowników\n dsd{sessions_data[0]['expires_at']}")
        
        # 6. Pobieranie z filtrowaniem
        print("6. Pobieranie aktywnych sesji...")
        with db.get_session("example_basic") as session:
            # Używamy bezpośredniego zapytania SQLAlchemy dla operatorów porównania
            current_time = datetime.now()
            active_sessions = session.query(UserSession).filter(UserSession.expires_at >= current_time).all()
            print(f"📊 Aktywnych sesji: {len(active_sessions)}")
        
        # 7. Dodawanie logów
        print("\n7. Dodawanie logów systemowych...")
        logs_data = [
            {
                "level": "INFO",
                "message": "Użytkownik zalogowany",
                "module": "auth",
                "user_id": 1,
                "ip_address": "192.168.1.100"
            },
            {
                "level": "WARNING",
                "message": "Próba logowania z nieprawidłowym hasłem", 
                "module": "auth",
                "user_id": None,
                "ip_address": "192.168.1.200"
            },
            {
                "level": "ERROR",
                "message": "Błąd połączenia z zewnętrznym API",
                "module": "api_client",
                "user_id": None,
                "ip_address": None
            }
        ]
        
        db.insert_batch("example_basic", Log, logs_data)
        print(f"✅ Dodano {len(logs_data)} wpisów do logów\n")
        
        # 8. Podsumowanie bazy danych
        print("8. Podsumowanie bazy danych:")
        db_info = db.get_database_info("example_basic")
        print(f"📊 Tabele w bazie: {len(db_info.get('tables', []))}")
        for table_name, table_info in db_info.get('tables', {}).items():
            print(f"  - {table_name}: {table_info.get('row_count', 0)} rekordów")
        
        print("\n✅ Przykład 01 zakończony pomyślnie!")
        
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
