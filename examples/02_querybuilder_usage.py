"""
LuxDB Example 02: Zaawansowane zapytania z QueryBuilder
- Używanie QueryBuilder
- Filtrowanie i sortowanie
- JOIN-y między tabelami
- Agregacje i grupowanie
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from luxdb import get_db_manager
from luxdb.models import User, UserSession, Log
from luxdb.utils import QueryBuilder
from datetime import datetime, timedelta
import json

def setup_test_data():
    """Przygotowanie danych testowych"""
    db = get_db_manager()

    # Utwórz bazę testową
    db.create_database("example_querybuilder")

    # Dodaj użytkowników
    users_data = [
        {"username": "admin", "email": "admin@test.com", "password_hash": "hash1", "is_active": True, "phone": "+48111111111"},
        {"username": "moderator", "email": "mod@test.com", "password_hash": "hash2", "is_active": True, "phone": "+48222222222"},
        {"username": "user1", "email": "user1@test.com", "password_hash": "hash3", "is_active": True, "phone": "+48333333333"},
        {"username": "user2", "email": "user2@test.com", "password_hash": "hash4", "is_active": False, "phone": None},
        {"username": "testuser", "email": "test@test.com", "password_hash": "hash5", "is_active": True, "phone": "+48555555555"},
    ]
    db.insert_batch("example_querybuilder", User, users_data)

    # Dodaj sesje
    sessions_data = [
        {"id": "qb_session_1", "user_id": 1, "expires_at": datetime.now() + timedelta(hours=24), "data": "{}"},
        {"id": "qb_session_2", "user_id": 2, "expires_at": datetime.now() + timedelta(hours=12), "data": "{}"},
        {"id": "qb_session_3", "user_id": 3, "expires_at": datetime.now() - timedelta(hours=1), "data": "{}"},
        {"id": "qb_session_4", "user_id": 5, "expires_at": datetime.now() + timedelta(hours=6), "data": "{}"},
    ]
    db.insert_batch("example_querybuilder", UserSession, sessions_data)

    # Dodaj logi
    logs_data = [
        {"level": "INFO", "message": "Login successful", "module": "auth", "user_id": 1, "ip_address": "192.168.1.1"},
        {"level": "INFO", "message": "Login successful", "module": "auth", "user_id": 2, "ip_address": "192.168.1.2"},
        {"level": "WARNING", "message": "Failed login attempt", "module": "auth", "user_id": None, "ip_address": "192.168.1.100"},
        {"level": "ERROR", "message": "Database connection failed", "module": "db", "user_id": None, "ip_address": None},
        {"level": "INFO", "message": "User profile updated", "module": "profile", "user_id": 3, "ip_address": "192.168.1.3"},
    ]
    db.insert_batch("example_querybuilder", Log, logs_data)

def example_basic_queries():
    """Podstawowe zapytania z QueryBuilder"""
    print("=== Podstawowe zapytania QueryBuilder ===")

    db = get_db_manager()

    with db.get_session("example_querybuilder") as session:
        builder = QueryBuilder(User)
        builder.set_session(session)

        # 1. Wszystkich aktywnych użytkowników
        print("1. Aktywni użytkownicy:")
        active_users = (builder
                       .select()
                       .filter(User.is_active == True)
                       .order_by(User.username)
                       .all())

        for user in active_users:
            print(f"  - {user.username} ({user.email})")

        # 2. Pierwszy użytkownik o nazwie zawierającej "user"
        print("\n2. Pierwszy użytkownik z 'user' w nazwie:")
        builder.reset()
        user_with_user = (builder
                         .select()
                         .filter(User.username.like('%user%'))
                         .first())

        if user_with_user:
            print(f"  - {user_with_user.username}")

        # 3. Liczba wszystkich użytkowników
        print("\n3. Statystyki użytkowników:")
        builder.reset()
        total_users = builder.select().count()

        builder.reset() 
        active_count = (builder
                       .select()
                       .filter(User.is_active == True)
                       .count())

        print(f"  - Łączna liczba: {total_users}")
        print(f"  - Aktywnych: {active_count}")
        print(f"  - Nieaktywnych: {total_users - active_count}")

def example_joins():
    """Przykłady JOIN-ów"""
    print("\n=== Zapytania z JOIN-ami ===")

    db = get_db_manager()

    with db.get_session("example_querybuilder") as session:
        builder = QueryBuilder(User)
        builder.set_session(session)

        # 1. Użytkownicy z aktywnymi sesjami
        print("1. Użytkownicy z aktywnymi sesjami:")
        users_with_sessions = (builder
                              .select()
                              .join(UserSession)
                              .filter(UserSession.expires_at > datetime.now())
                              .order_by(User.username)
                              .all())

        for user in users_with_sessions:
            print(f"  - {user.username}")

        # 2. Szczegółowe informacje o sesjach
        print("\n2. Szczegóły aktywnych sesji:")
        builder.reset()
        sessions_info = (builder
                        .select(User.username, UserSession.id, UserSession.expires_at)
                        .join(UserSession)
                        .filter(UserSession.expires_at > datetime.now())
                        .order_by(UserSession.expires_at)
                        .all())

        for username, session_id, expires_at in sessions_info:
            print(f"  - {username}: {session_id} (wygasa: {expires_at.strftime('%H:%M:%S')})")

def example_complex_filters():
    """Złożone filtry i warunki"""
    print("\n=== Złożone filtry ===")

    db = get_db_manager()

    with db.get_session("example_querybuilder") as session:
        # 1. Logi błędów i ostrzeżeń
        print("1. Logi błędów i ostrzeżeń:")
        builder = QueryBuilder(Log)
        builder.set_session(session)

        error_logs = (builder
                     .select()
                     .filter((Log.level == "ERROR") | (Log.level == "WARNING"))
                     .order_by(Log.created_at.desc())
                     .all())

        for log in error_logs:
            print(f"  - [{log.level}] {log.message} (moduł: {log.module})")

        # 2. Użytkownicy z numerem telefonu
        print("\n2. Użytkownicy z numerem telefonu:")
        builder = QueryBuilder(User)
        builder.set_session(session)

        users_with_phone = (builder
                           .select()
                           .filter(User.phone != None)
                           .filter(User.is_active == True)
                           .order_by(User.username)
                           .all())

        for user in users_with_phone:
            print(f"  - {user.username}: {user.phone}")

def example_aggregations():
    """Przykłady agregacji"""
    print("\n=== Agregacje i grupowanie ===")

    db = get_db_manager()

    # Surowe zapytania SQL dla agregacji
    print("1. Statystyki logów według poziomu:")
    log_stats = db.execute_raw_sql(
        "example_querybuilder",
        """
        SELECT level, COUNT(*) as count
        FROM logs 
        GROUP BY level 
        ORDER BY count DESC
        """
    )

    for row in log_stats:
        print(f"  - {row['level']}: {row['count']} wpisów")

    print("\n2. Statystyki użytkowników:")
    user_stats = db.execute_raw_sql(
        "example_querybuilder", 
        """
        SELECT 
            COUNT(*) as total_users,
            SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_users,
            SUM(CASE WHEN phone IS NOT NULL THEN 1 ELSE 0 END) as users_with_phone
        FROM users
        """
    )

    for row in user_stats:
        print(f"  - Łączna liczba użytkowników: {row['total_users']}")
        print(f"  - Aktywnych: {row['active_users']}")
        print(f"  - Z numerem telefonu: {row['users_with_phone']}")

def main():
    print("=== LuxDB Przykład 02: QueryBuilder ===\n")

    try:
        # Przygotuj dane testowe
        print("Przygotowywanie danych testowych...")
        setup_test_data()
        print("✅ Dane testowe przygotowane\n")

        # Uruchom przykłady
        example_basic_queries()
        example_joins()
        example_complex_filters()
        example_aggregations()

        print("\n✅ Przykład 02 zakończony pomyślnie!")

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