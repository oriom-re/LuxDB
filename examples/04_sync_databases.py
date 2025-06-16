
"""
LuxDB Example 04: Synchronizacja baz danych
- Synchronizacja między bazami
- Replikacja danych
- Zarządzanie wieloma bazami
- Backup i restore
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from luxdb.manager import get_db_manager
from luxdb.models import User, UserSession, Log
from luxdb.config import DatabaseConfig, DatabaseType
from datetime import datetime, timedelta
import json

def setup_source_database():
    """Przygotowanie źródłowej bazy danych z danymi"""
    db = get_db_manager()
    
    print("Przygotowywanie źródłowej bazy danych...")
    db.create_database("source_db")
    with db.get_session("source_db") as session:
        # Dodaj użytkowników
        users_data = [
            {"username": "admin", "email": "admin@company.com", "password_hash": "hash1", "is_active": True, "phone": "+48111111111"},
            {"username": "manager", "email": "manager@company.com", "password_hash": "hash2", "is_active": True, "phone": "+48222222222"},
            {"username": "employee1", "email": "emp1@company.com", "password_hash": "hash3", "is_active": True, "phone": "+48333333333"},
            {"username": "employee2", "email": "emp2@company.com", "password_hash": "hash4", "is_active": False, "phone": None},
            {"username": "contractor", "email": "contractor@external.com", "password_hash": "hash5", "is_active": True, "phone": "+48555555555"},
        ]
        db.insert_batch(session, "source_db", User, users_data)
        
        # Dodaj sesje
        sessions_data = [
            {"id": "sync_session_1", "user_id": 1, "expires_at": datetime.now() + timedelta(hours=24), "data": json.dumps({"role": "admin"})},
            {"id": "sync_session_2", "user_id": 2, "expires_at": datetime.now() + timedelta(hours=12), "data": json.dumps({"role": "manager"})},
            {"id": "sync_session_3", "user_id": 3, "expires_at": datetime.now() + timedelta(hours=8), "data": json.dumps({"role": "employee"})},
        ]
        db.insert_batch(session, "source_db", UserSession, sessions_data)
        
        # Dodaj logi
        logs_data = [
            {"level": "INFO", "message": "System started", "module": "system", "user_id": None, "ip_address": None},
            {"level": "INFO", "message": "Admin login", "module": "auth", "user_id": 1, "ip_address": "192.168.1.10"},
            {"level": "INFO", "message": "Manager login", "module": "auth", "user_id": 2, "ip_address": "192.168.1.20"},
            {"level": "WARNING", "message": "Failed login attempt", "module": "auth", "user_id": None, "ip_address": "192.168.1.100"},
            {"level": "ERROR", "message": "Database connection timeout", "module": "database", "user_id": None, "ip_address": None},
        ]
        db.insert_batch(session, "source_db", Log, logs_data)
        
        print("✅ Źródłowa baza danych przygotowana")
    
def create_target_databases():
    """Tworzenie docelowych baz danych"""
    db = get_db_manager()
    
    print("Tworzenie docelowych baz danych...")
    
    # Baza docelowa 1: backup_db
    db.create_database("backup_db")
    
    # Baza docelowa 2: analytics_db (tylko do analiz)
    db.create_database("analytics_db")
    
    print("✅ Docelowe bazy danych utworzone")

def example_full_sync():
    """Pełna synchronizacja baz danych"""
    print("\n=== Pełna synchronizacja baz danych ===")
    
    db = get_db_manager()
    
    try:
        # Synchronizuj wszystkie modele do backup_db
        print("1. Synchronizacja source_db → backup_db...")
        success = db.sync_databases("source_db", "backup_db", [User, UserSession, Log])
        
        if success:
            print("✅ Synchronizacja zakończona pomyślnie")
            
            # Sprawdź dane w backup_db
            with db.get_session("backup_db") as backup_session:
                backup_users = backup_session.query(User).all()
                backup_sessions = backup_session.query(UserSession).all()
                backup_logs = backup_session.query(Log).all()
            
            print(f"📊 Zsynchronizowano:")
            print(f"  - Użytkowników: {len(backup_users)}")
            print(f"  - Sesji: {len(backup_sessions)}")
            print(f"  - Logów: {len(backup_logs)}")
        else:
            print("❌ Synchronizacja nie powiodła się")
            
    except Exception as e:
        print(f"❌ Błąd podczas synchronizacji: {e}")

def example_selective_sync():
    """Selektywna synchronizacja - tylko określone dane"""
    print("\n=== Selektywna synchronizacja ===")
    
    db = get_db_manager()
    
    try:
        # Synchronizuj tylko aktywnych użytkowników
        print("1. Synchronizacja aktywnych użytkowników...")
        
        # Pobierz aktywnych użytkowników ze źródła
        with db.get_session("source_db") as source_session:
            active_users = source_session.query(User).filter(User.is_active == True).all()
            
            # Wstaw do analytics_db
            with db.get_session("analytics_db") as target_session:
                for user in active_users:
                    user_data = User(
                        username=user.username,
                        email=user.email,
                        password_hash=user.password_hash,
                        is_active=user.is_active,
                        phone=user.phone
                    )
                    target_session.add(user_data)
                target_session.commit()
            
            print(f"✅ Zsynchronizowano {len(active_users)} aktywnych użytkowników")
        
        # Synchronizuj tylko logi błędów i ostrzeżeń
        print("\n2. Synchronizacja logów błędów i ostrzeżeń...")
        
        with db.get_session("source_db") as source_session:
            error_logs = source_session.query(Log).filter(
                (Log.level == "ERROR") | (Log.level == "WARNING")
            ).all()
            
            with db.get_session("analytics_db") as target_session:
                for log in error_logs:
                    log_data = Log(
                        level=log.level,
                        message=log.message,
                        module=log.module,
                        user_id=log.user_id,
                        ip_address=log.ip_address,
                        created_at=log.created_at
                    )
                    target_session.add(log_data)
                target_session.commit()
        
        print(f"✅ Zsynchronizowano {len(error_logs)} logów błędów/ostrzeżeń")
        
    except Exception as e:
        print(f"❌ Błąd podczas selektywnej synchronizacji: {e}")

def example_incremental_sync():
    """Synchronizacja przyrostowa - tylko nowe dane"""
    print("\n=== Synchronizacja przyrostowa ===")
    
    db = get_db_manager()
    
    try:
        with db.get_session("source_db") as source_session:
            # Dodaj nowe dane do źródłowej bazy
            print("1. Dodawanie nowych danych do źródłowej bazy...")
            
            new_users = [
                {"username": "new_user1", "email": "new1@company.com", "password_hash": "newhash1", "is_active": True, "phone": "+48666666666"},
                {"username": "new_user2", "email": "new2@company.com", "password_hash": "newhash2", "is_active": True, "phone": "+48777777777"},
            ]
            db.insert_batch(source_session, "source_db", User, new_users)
            
            new_logs = [
                {"level": "INFO", "message": "New user registered", "module": "registration", "user_id": 6, "ip_address": "192.168.1.30"},
                {"level": "INFO", "message": "New user registered", "module": "registration", "user_id": 7, "ip_address": "192.168.1.31"},
            ]
            db.insert_batch(source_session, "source_db", Log, new_logs)
            
            print("✅ Dodano nowe dane do źródłowej bazy")
        
        # Znajdź najnowszy rekord w backup_db
        print("\n2. Synchronizacja tylko nowych danych...")
        
        with db.get_session("backup_db") as backup_session:
            last_user = backup_session.query(User).order_by(User.id.desc()).first()
            last_user_id = last_user.id if last_user else 0
            
            last_log = backup_session.query(Log).order_by(Log.id.desc()).first()
            last_log_id = last_log.id if last_log else 0
        
        # Synchronizuj tylko nowe rekordy
        new_users_to_sync = source_session.query(User).filter(User.id > last_user_id).all()
        new_logs_to_sync = source_session.query(Log).filter(Log.id > last_log_id).all()
        
        # Wstaw nowe rekordy
        with db.get_session("backup_db") as backup_session:
            for user in new_users_to_sync:
                user_data = User(
                    username=user.username,
                    email=user.email,
                    password_hash=user.password_hash,
                    is_active=user.is_active,
                    phone=user.phone
                )
                backup_session.add(user_data)
            
            for log in new_logs_to_sync:
                log_data = Log(
                    level=log.level,
                    message=log.message,
                    module=log.module,
                    user_id=log.user_id,
                    ip_address=log.ip_address,
                    created_at=log.created_at
                )
                backup_session.add(log_data)
            
            backup_session.commit()
        
        print(f"✅ Synchronizacja przyrostowa zakończona:")
        print(f"  - Nowych użytkowników: {len(new_users_to_sync)}")
        print(f"  - Nowych logów: {len(new_logs_to_sync)}")
        
    except Exception as e:
        print(f"❌ Błąd podczas synchronizacji przyrostowej: {e}")

def example_export_import():
    """Eksport i import bazy danych"""
    print("\n=== Eksport i import bazy danych ===")
    
    db = get_db_manager()
    
    try:
        # Eksport bazy do JSON
        print("1. Eksport bazy danych do JSON...")
        export_path = db.export_database("source_db", "json")
        
        if export_path:
            print(f"✅ Baza wyeksportowana do: {export_path}")
            
            # Sprawdź rozmiar pliku
            import os
            file_size = os.path.getsize(export_path) if os.path.exists(export_path) else 0
            print(f"📊 Rozmiar pliku: {file_size} bajtów")
        else:
            print("❌ Eksport nie powiódł się")
            
    except Exception as e:
        print(f"❌ Błąd podczas eksportu: {e}")

def compare_databases():
    """Porównanie zawartości baz danych"""
    print("\n=== Porównanie baz danych ===")
    
    db = get_db_manager()
    
    try:
        # Porównaj dane w różnych bazach
        databases = ["source_db", "backup_db", "analytics_db"]
        
        print("Statystyki baz danych:")
        for db_name in databases:
            try:
                with db.get_session(db_name) as session:
                    users = db.select_data(session, db_name, User)
                    sessions = db.select_data(session, db_name, UserSession)
                    logs = db.select_data(session, db_name, Log)
                
                print(f"\n📊 {db_name}:")
                print(f"  - Użytkowników: {len(users)}")
                print(f"  - Sesji: {len(sessions)}")
                print(f"  - Logów: {len(logs)}")
                
            except Exception as e:
                print(f"  ❌ Błąd odczytu {db_name}: {e}")
                
    except Exception as e:
        print(f"❌ Błąd podczas porównywania: {e}")

def main():
    print("=== LuxDB Przykład 04: Synchronizacja baz danych ===\n")
    
    try:
        # Przygotuj dane testowe
        setup_source_database()
        create_target_databases()
        
        # Uruchom przykłady synchronizacji
        example_full_sync()
        example_selective_sync() 
        example_incremental_sync()
        example_export_import()
        compare_databases()
        
        print("\n✅ Przykład 04 zakończony pomyślnie!")
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Zamknij połączenia
        db = get_db_manager()
        db.close_all_connections()
        print("🔒 Zamknięto wszystkie połączenia")

if __name__ == "__main__":
    main()
