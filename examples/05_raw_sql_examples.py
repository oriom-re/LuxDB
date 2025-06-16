
"""
LuxDB Example 05: Surowe zapytania SQL
- SELECT z JOIN
- GROUP BY i agregacje
- Zaawansowane raporty
- Analiza danych
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from luxdb.manager import get_db_manager
from luxdb.models import User, UserSession, Log
from datetime import datetime, timedelta
import json

def setup_reporting_data():
    """Przygotowanie danych dla raportów"""
    db = get_db_manager()
    
    print("Przygotowywanie danych do raportowania...")
    db.create_database("reporting_db")

    with db.get_session("reporting_db") as session:
        # Dodaj użytkowników z różnymi rolami
        users_data = [
            {"username": "admin", "email": "admin@company.com", "password_hash": "hash1", "is_active": True, "phone": "+48111111111"},
            {"username": "manager1", "email": "manager1@company.com", "password_hash": "hash2", "is_active": True, "phone": "+48222222222"},
            {"username": "manager2", "email": "manager2@company.com", "password_hash": "hash3", "is_active": True, "phone": "+48333333333"},
            {"username": "employee1", "email": "emp1@company.com", "password_hash": "hash4", "is_active": True, "phone": "+48444444444"},
            {"username": "employee2", "email": "emp2@company.com", "password_hash": "hash5", "is_active": True, "phone": "+48555555555"},
            {"username": "employee3", "email": "emp3@company.com", "password_hash": "hash6", "is_active": False, "phone": None},
            {"username": "contractor1", "email": "cont1@external.com", "password_hash": "hash7", "is_active": True, "phone": "+48666666666"},
            {"username": "contractor2", "email": "cont2@external.com", "password_hash": "hash8", "is_active": False, "phone": None},
            {"username": "intern1", "email": "intern1@company.com", "password_hash": "hash9", "is_active": True, "phone": "+48777777777"},
            {"username": "intern2", "email": "intern2@company.com", "password_hash": "hash10", "is_active": True, "phone": "+48888888888"},
        ]
        db.insert_batch(session, "reporting_db", User, users_data)
        
        # Dodaj sesje o różnych czasach wygaśnięcia
        base_time = datetime.now()
        sessions_data = [
            {"id": "report_session_1", "user_id": 1, "expires_at": base_time + timedelta(hours=24), "data": json.dumps({"role": "admin", "department": "IT"})},
            {"id": "report_session_2", "user_id": 2, "expires_at": base_time + timedelta(hours=12), "data": json.dumps({"role": "manager", "department": "Sales"})},
            {"id": "report_session_3", "user_id": 3, "expires_at": base_time + timedelta(hours=8), "data": json.dumps({"role": "manager", "department": "Marketing"})},
            {"id": "report_session_4", "user_id": 4, "expires_at": base_time + timedelta(hours=6), "data": json.dumps({"role": "employee", "department": "Sales"})},
            {"id": "report_session_5", "user_id": 5, "expires_at": base_time + timedelta(hours=4), "data": json.dumps({"role": "employee", "department": "Marketing"})},
            {"id": "report_session_6", "user_id": 7, "expires_at": base_time - timedelta(hours=1), "data": json.dumps({"role": "contractor", "department": "External"})},
            {"id": "report_session_7", "user_id": 9, "expires_at": base_time + timedelta(hours=2), "data": json.dumps({"role": "intern", "department": "IT"})},
            {"id": "report_session_8", "user_id": 10, "expires_at": base_time + timedelta(hours=3), "data": json.dumps({"role": "intern", "department": "HR"})},
        ]
        db.insert_batch(session, "reporting_db", UserSession, sessions_data)
        
        # Dodaj różnorodne logi z różnych okresów
        logs_data = []
        
        # Logi z ostatnich 7 dni
        for day in range(7):
            log_time = base_time - timedelta(days=day)
            
            # Logi systemowe
            logs_data.extend([
                {"level": "INFO", "message": "System backup completed", "module": "backup", "user_id": None, "ip_address": None, "created_at": log_time.replace(hour=2)},
                {"level": "INFO", "message": "Database maintenance started", "module": "maintenance", "user_id": None, "ip_address": None, "created_at": log_time.replace(hour=3)},
            ])
            
            # Logi logowań
            for user_id in [1, 2, 3, 4, 5, 7, 9, 10]:
                if day < 3:  # Ostatnie 3 dni - więcej aktywności
                    logs_data.append({
                        "level": "INFO", 
                        "message": "User login successful", 
                        "module": "auth", 
                        "user_id": user_id, 
                        "ip_address": f"192.168.1.{user_id + 100}",
                        "created_at": log_time.replace(hour=8 + user_id % 8)
                    })
            
            # Błędy - rzadziej
            if day % 2 == 0:
                logs_data.extend([
                    {"level": "ERROR", "message": "Database connection timeout", "module": "database", "user_id": None, "ip_address": None, "created_at": log_time.replace(hour=14)},
                    {"level": "WARNING", "message": "High memory usage detected", "module": "monitoring", "user_id": None, "ip_address": None, "created_at": log_time.replace(hour=15)},
                ])
            
            # Nieudane logowania
            logs_data.extend([
                {"level": "WARNING", "message": "Failed login attempt", "module": "auth", "user_id": None, "ip_address": "192.168.1.200", "created_at": log_time.replace(hour=10)},
                {"level": "WARNING", "message": "Failed login attempt", "module": "auth", "user_id": None, "ip_address": "192.168.1.201", "created_at": log_time.replace(hour=16)},
            ])
    
            db.insert_batch(session, "reporting_db", Log, logs_data)
            print(f"✅ Przygotowano {len(logs_data)} wpisów logów")

def example_basic_joins():
    """Podstawowe JOIN-y"""
    print("\n=== Podstawowe JOIN-y ===")
    
    db = get_db_manager()
    
    # 1. Użytkownicy z aktywnymi sesjami
    print("1. Użytkownicy z aktywnymi sesjami:")
    query = """
    SELECT 
        u.username,
        u.email,
        s.id as session_id,
        s.expires_at,
        s.data
    FROM users u
    INNER JOIN sessions s ON u.id = s.user_id
    WHERE s.expires_at > datetime('now')
    ORDER BY s.expires_at DESC
    """
    
    result = db.execute_raw_sql("reporting_db", query)
    for row in result:
        print(f"  - {row['username']}: {row['session_id']} (wygasa: {row['expires_at']})")
    
    # 2. Użytkownicy bez aktywnych sesji
    print("\n2. Użytkownicy bez aktywnych sesji:")
    query = """
    SELECT 
        u.username,
        u.email,
        u.is_active
    FROM users u
    LEFT JOIN sessions s ON u.id = s.user_id AND s.expires_at > datetime('now')
    WHERE s.id IS NULL AND u.is_active = 1
    ORDER BY u.username
    """
    
    result = db.execute_raw_sql("reporting_db", query)
    for row in result:
        print(f"  - {row['username']} ({row['email']})")

def example_aggregations():
    """Agregacje i grupowanie"""
    print("\n=== Agregacje i grupowanie ===")
    
    db = get_db_manager()
    
    # 1. Statystyki użytkowników
    print("1. Statystyki użytkowników:")
    query = """
    SELECT 
        COUNT(*) as total_users,
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_users,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) as inactive_users,
        SUM(CASE WHEN phone IS NOT NULL THEN 1 ELSE 0 END) as users_with_phone,
        SUM(CASE WHEN email LIKE '%@company.com' THEN 1 ELSE 0 END) as company_emails,
        SUM(CASE WHEN email LIKE '%@external.com' THEN 1 ELSE 0 END) as external_emails
    FROM users
    """
    
    result = db.execute_raw_sql("reporting_db", query)
    for row in result:
        print(f"  - Łączna liczba: {row['total_users']}")
        print(f"  - Aktywnych: {row['active_users']}")
        print(f"  - Nieaktywnych: {row['inactive_users']}")
        print(f"  - Z telefonem: {row['users_with_phone']}")
        print(f"  - Email firmowy: {row['company_emails']}")
        print(f"  - Email zewnętrzny: {row['external_emails']}")
    
    # 2. Statystyki logów według poziomów
    print("\n2. Statystyki logów według poziomów:")
    query = """
    SELECT 
        level,
        COUNT(*) as count,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(DISTINCT module) as unique_modules,
        MIN(created_at) as first_occurrence,
        MAX(created_at) as last_occurrence
    FROM logs
    GROUP BY level
    ORDER BY count DESC
    """
    
    result = db.execute_raw_sql("reporting_db", query)
    for row in result:
        print(f"  - {row['level']}: {row['count']} wpisów, {row['unique_users']} użytkowników, {row['unique_modules']} modułów")
        print(f"    Pierwszy: {row['first_occurrence']}, Ostatni: {row['last_occurrence']}")

def example_time_based_analysis():
    """Analiza czasowa"""
    print("\n=== Analiza czasowa ===")
    
    db = get_db_manager()
    
    # 1. Aktywność użytkowników w ostatnich dniach
    print("1. Aktywność logowania w ostatnich 7 dniach:")
    query = """
    SELECT 
        DATE(l.created_at) as login_date,
        COUNT(*) as login_count,
        COUNT(DISTINCT l.user_id) as unique_users
    FROM logs l
    WHERE l.level = 'INFO' 
        AND l.message = 'User login successful'
        AND l.created_at >= datetime('now', '-7 days')
    GROUP BY DATE(l.created_at)
    ORDER BY login_date DESC
    """
    
    result = db.execute_raw_sql("reporting_db", query)
    for row in result:
        print(f"  - {row['login_date']}: {row['login_count']} logowań, {row['unique_users']} unikalnych użytkowników")
    
    # 2. Błędy według godzin
    print("\n2. Rozkład błędów według godzin:")
    query = """
    SELECT 
        strftime('%H', created_at) as hour,
        COUNT(*) as error_count
    FROM logs
    WHERE level IN ('ERROR', 'WARNING')
        AND created_at >= datetime('now', '-7 days')
    GROUP BY strftime('%H', created_at)
    ORDER BY hour
    """
    
    result = db.execute_raw_sql("reporting_db", query)
    for row in result:
        print(f"  - Godzina {row['hour']}:00: {row['error_count']} błędów/ostrzeżeń")

def example_complex_reports():
    """Złożone raporty"""
    print("\n=== Złożone raporty ===")
    
    db = get_db_manager()
    
    # 1. Raport aktywności użytkowników
    print("1. Raport aktywności użytkowników:")
    query = """
    SELECT 
        u.username,
        u.email,
        u.is_active,
        COUNT(DISTINCT s.id) as total_sessions,
        SUM(CASE WHEN s.expires_at > datetime('now') THEN 1 ELSE 0 END) as active_sessions,
        COUNT(DISTINCT l.id) as total_logs,
        MAX(l.created_at) as last_activity,
        CASE 
            WHEN u.email LIKE '%@company.com' THEN 'Internal'
            WHEN u.email LIKE '%@external.com' THEN 'External'
            ELSE 'Other'
        END as user_type
    FROM users u
    LEFT JOIN sessions s ON u.id = s.user_id
    LEFT JOIN logs l ON u.id = l.user_id
    GROUP BY u.id, u.username, u.email, u.is_active
    ORDER BY total_logs DESC, last_activity DESC
    """
    
    result = db.execute_raw_sql("reporting_db", query)
    print(f"{'Username':<15} {'Type':<10} {'Sessions':<8} {'Active':<6} {'Logs':<5} {'Last Activity'}")
    print("-" * 80)
    for row in result:
        last_activity = row['last_activity'] or 'Nigdy'
        if last_activity != 'Nigdy':
            last_activity = datetime.fromisoformat(last_activity).strftime('%m-%d %H:%M')
        
        print(f"{row['username']:<15} {row['user_type']:<10} {row['total_sessions'] or 0:<8} {row['active_sessions'] or 0:<6} {row['total_logs'] or 0:<5} {last_activity}")
    
    # 2. Raport bezpieczeństwa
    print("\n2. Raport bezpieczeństwa - nieudane logowania:")
    query = """
    SELECT 
        ip_address,
        COUNT(*) as failed_attempts,
        MIN(created_at) as first_attempt,
        MAX(created_at) as last_attempt,
        COUNT(DISTINCT DATE(created_at)) as days_active
    FROM logs
    WHERE level = 'WARNING' 
        AND message = 'Failed login attempt'
        AND ip_address IS NOT NULL
    GROUP BY ip_address
    HAVING failed_attempts >= 2
    ORDER BY failed_attempts DESC, last_attempt DESC
    """
    
    result = db.execute_raw_sql("reporting_db", query)
    print(f"{'IP Address':<15} {'Attempts':<8} {'Days Active':<11} {'Last Attempt'}")
    print("-" * 60)
    for row in result:
        last_attempt = datetime.fromisoformat(row['last_attempt']).strftime('%m-%d %H:%M')
        print(f"{row['ip_address']:<15} {row['failed_attempts']:<8} {row['days_active']:<11} {last_attempt}")

def example_advanced_analytics():
    """Zaawansowana analiza danych"""
    print("\n=== Zaawansowana analiza danych ===")
    
    db = get_db_manager()
    
    # 1. Korelacja między typem użytkownika a aktywnością
    print("1. Analiza aktywności według typu użytkownika:")
    query = """
    WITH user_stats AS (
        SELECT 
            u.id,
            u.username,
            CASE 
                WHEN u.email LIKE '%@company.com' THEN 'Internal'
                WHEN u.email LIKE '%@external.com' THEN 'External' 
                ELSE 'Other'
            END as user_type,
            COUNT(DISTINCT s.id) as session_count,
            COUNT(DISTINCT l.id) as log_count,
            CASE WHEN u.is_active = 1 THEN 'Active' ELSE 'Inactive' END as status
        FROM users u
        LEFT JOIN sessions s ON u.id = s.user_id
        LEFT JOIN logs l ON u.id = l.user_id
        GROUP BY u.id, u.username, u.email, u.is_active
    )
    SELECT 
        user_type,
        status,
        COUNT(*) as user_count,
        AVG(session_count) as avg_sessions,
        AVG(log_count) as avg_logs,
        SUM(session_count) as total_sessions,
        SUM(log_count) as total_logs
    FROM user_stats
    GROUP BY user_type, status
    ORDER BY user_type, status
    """
    
    result = db.execute_raw_sql("reporting_db", query)
    print(f"{'Type':<10} {'Status':<8} {'Users':<6} {'Avg Sessions':<12} {'Avg Logs':<9} {'Total Sessions':<14} {'Total Logs'}")
    print("-" * 85)
    for row in result:
        print(f"{row.get('user_type', 0):<10} {row.get('status', 0):<8} {row.get('user_count', 0):<6} {row.get('avg_sessions', 0):<12.1f} {row.get('avg_logs', 0):<9.1f} {row.get('total_sessions', 0):<14} {row.get('total_logs', 0)}")
    
    # 2. Trending - aktywność w czasie
    print("\n2. Trend aktywności w ostatnich dniach:")
    query = """
    SELECT 
        DATE(created_at) as activity_date,
        COUNT(CASE WHEN level = 'INFO' THEN 1 END) as info_logs,
        COUNT(CASE WHEN level = 'WARNING' THEN 1 END) as warning_logs,
        COUNT(CASE WHEN level = 'ERROR' THEN 1 END) as error_logs,
        COUNT(*) as total_logs,
        COUNT(DISTINCT user_id) as active_users
    FROM logs
    WHERE created_at >= datetime('now', '-7 days')
    GROUP BY DATE(created_at)
    ORDER BY activity_date DESC
    """
    
    result = db.execute_raw_sql("reporting_db", query)
    print(f"{'Date':<12} {'Total':<6} {'INFO':<5} {'WARN':<5} {'ERROR':<6} {'Users':<6}")
    print("-" * 50)
    for row in result:
        print(f"{row['activity_date']:<12} {row['total_logs']:<6} {row['info_logs']:<5} {row['warning_logs']:<5} {row['error_logs']:<6} {row['active_users'] or 0:<6}")

def main():
    print("=== LuxDB Przykład 05: Surowe zapytania SQL ===\n")
    
    try:
        # Przygotuj dane testowe
        setup_reporting_data()
        
        # Uruchom przykłady
        example_basic_joins()
        example_aggregations()
        example_time_based_analysis()
        example_complex_reports()
        example_advanced_analytics()
        
        print("\n✅ Przykład 05 zakończony pomyślnie!")
        
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
