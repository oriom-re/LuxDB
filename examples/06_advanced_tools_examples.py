
"""
LuxDB Example 06: Zaawansowane narzędzia
- Standaryzowane logowanie z DatabaseLogger
- Obsługa błędów i walidacja
- SQL Builder i szablony
- Przetwarzanie i filtrowanie danych
- Eksport/import w różnych formatach
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from manager import get_db_manager
from models import User, Log
from utils import (
    DatabaseLogger, get_db_logger, LuxDBError, handle_database_errors,
    SQLQueryBuilder, SQLTemplateEngine, SQLAnalyzer, execute_sql_safely,
    DataFilter, DataTransformer, DataAggregator, DataValidator, DataCleaner,
    DataExporter, DataImporter, ExportFormat, create_data_summary
)
from datetime import datetime, timedelta
import json
import tempfile

def setup_test_data():
    """Przygotuj dane testowe"""
    db = get_db_manager()
    
    # Utwórz bazę testową
    if not db.create_database("tools_demo"):
        print("❌ Nie udało się utworzyć bazy testowej")
        return False
    
    # Utwórz tabele
    db.create_table_from_model("tools_demo", User)
    db.create_table_from_model("tools_demo", Log)
    
    # Dodaj testowych użytkowników
    test_users = [
        {"username": "alice", "email": "alice@company.com", "password_hash": "hash1", "is_active": True, "phone": "123-456-789"},
        {"username": "bob", "email": "bob@external.com", "password_hash": "hash2", "is_active": True, "phone": "987-654-321"},
        {"username": "charlie", "email": "charlie@company.com", "password_hash": "hash3", "is_active": False, "phone": None},
        {"username": "diana", "email": "diana@external.com", "password_hash": "hash4", "is_active": True, "phone": "555-123-456"},
        {"username": "eve", "email": "eve@company.com", "password_hash": "hash5", "is_active": True, "phone": "111-222-333"}
    ]
    
    for user_data in test_users:
        db.insert_data("tools_demo", User, user_data)
    
    # Dodaj testowe logi
    test_logs = [
        {"level": "INFO", "message": "User login successful", "module": "auth", "user_id": 1},
        {"level": "WARNING", "message": "Invalid login attempt", "module": "auth", "user_id": None},
        {"level": "ERROR", "message": "Database connection failed", "module": "database", "user_id": None},
        {"level": "INFO", "message": "Data export completed", "module": "export", "user_id": 2},
        {"level": "DEBUG", "message": "Cache cleared", "module": "cache", "user_id": 3}
    ]
    
    for log_data in test_logs:
        db.insert_data("tools_demo", Log, log_data)
    
    print("✅ Dane testowe przygotowane")
    return True

def example_logging_utils():
    """Przykład użycia DatabaseLogger"""
    print("\n=== 📝 Standaryzowane logowanie ===")
    
    # Pobierz logger
    logger = get_db_logger()
    
    # Logowanie operacji bazodanowych
    logger.log_database_operation("create_table", "tools_demo", True, "Created users table", 0.05)
    logger.log_database_operation("insert_data", "tools_demo", False, "Validation failed")
    
    # Logowanie wykonania zapytań
    logger.log_query_execution("SELECT", "users", 5, 0.012)
    logger.log_query_execution("UPDATE", "users", 2, 0.008)
    
    # Logowanie migracji
    logger.log_migration("tools_demo", 1, 2, True, 0.15)
    
    # Logowanie synchronizacji
    from models import User
    logger.log_sync("source_db", "target_db", [User], True, 25)
    
    # Logowanie błędów z kontekstem
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.log_error("test_operation", e, {"user_id": 123, "action": "test"})
    
    print("✅ Przykłady logowania wykonane")

def example_error_handling():
    """Przykład obsługi błędów"""
    print("\n=== ⚠️ Obsługa błędów i walidacja ===")
    
    # Użycie dekoratora obsługi błędów
    @handle_database_errors("demo_operation")
    def risky_operation(will_fail=False):
        if will_fail:
            raise LuxDBError("Symulowany błąd", {"context": "demo"})
        return "Operacja zakończona pomyślnie"
    
    # Test udanej operacji
    try:
        result = risky_operation(False)
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ Błąd: {e}")
    
    # Test nieudanej operacji
    try:
        result = risky_operation(True)
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ Przechwycony błąd: {type(e).__name__}: {e}")
    
    # ErrorCollector dla operacji batch
    from utils.error_handlers import ErrorCollector
    
    collector = ErrorCollector()
    
    # Symulacja operacji batch
    for i in range(10):
        collector.increment_total()
        if i % 3 == 0:  # Symuluj błędy co trzecią operację
            collector.add_error(ValueError(f"Błąd w operacji {i}"), {"operation_id": i})
        else:
            collector.add_success()
    
    summary = collector.get_summary()
    print(f"📊 Podsumowanie batch:")
    print(f"  - Łącznie operacji: {summary['total_operations']}")
    print(f"  - Udanych: {summary['successful_operations']}")
    print(f"  - Nieudanych: {summary['failed_operations']}")
    print(f"  - Wskaźnik sukcesu: {summary['success_rate']:.1f}%")

def example_sql_tools():
    """Przykład narzędzi SQL"""
    print("\n=== 🔧 Narzędzia SQL ===")
    
    db = get_db_manager()
    
    # 1. SQLQueryBuilder
    print("1. SQL Query Builder:")
    builder = SQLQueryBuilder()
    
    # Proste zapytanie
    query1 = (builder
              .select("username", "email", "is_active")
              .from_table("users")
              .where("is_active = 1")
              .order_by("username", "ASC")
              .limit(10)
              .build())
    
    print(f"Query 1: {query1}")
    
    # Złożone zapytanie z JOIN
    builder.reset()
    query2 = (builder
              .select("u.username", "COUNT(l.id) as log_count")
              .from_table("users u")
              .join("logs l", "u.id = l.user_id", "LEFT")
              .where("u.is_active = 1")
              .group_by("u.id", "u.username")
              .having("COUNT(l.id) > 0")
              .order_by("log_count", "DESC")
              .build())
    
    print(f"Query 2: {query2}")
    
    # 2. SQLTemplateEngine
    print("\n2. SQL Template Engine:")
    template_engine = SQLTemplateEngine()
    
    # Użyj gotowych szablonów
    templates = template_engine.get_common_queries()
    count_query = template_engine.render_template(
        templates["count_records"], 
        {"table": "users"}
    )
    print(f"Count query: {count_query}")
    
    # Własny szablon
    custom_template = "SELECT * FROM {table} WHERE {field} = {value} AND created_at >= {date}"
    rendered = template_engine.render_template(custom_template, {
        "table": "users",
        "field": "is_active", 
        "value": 1,
        "date": datetime.now() - timedelta(days=7)
    })
    print(f"Custom query: {rendered}")
    
    # 3. SQLAnalyzer
    print("\n3. SQL Analyzer:")
    analyzer = SQLAnalyzer()
    
    test_queries = [
        "SELECT * FROM users WHERE is_active = 1",
        "SELECT u.*, COUNT(l.id) FROM users u LEFT JOIN logs l ON u.id = l.user_id GROUP BY u.id",
        "INSERT INTO users (username, email) VALUES ('test', 'test@example.com')",
        "UPDATE users SET is_active = 0 WHERE last_login < '2024-01-01'"
    ]
    
    for query in test_queries:
        analysis = analyzer.analyze_query(query)
        print(f"  Query: {query[:50]}...")
        print(f"    Type: {analysis['type']}, Read-only: {analysis['is_read_only']}")
        print(f"    Tables: {analysis['tables']}, Complexity: {analysis['complexity']}")
    
    # 4. Bezpieczne wykonywanie SQL
    print("\n4. Bezpieczne wykonywanie SQL:")
    try:
        if "tools_demo" in db.connection_pools:
            engine = db.connection_pools["tools_demo"].engine
            result = execute_sql_safely(engine, "SELECT COUNT(*) as user_count FROM users")
            print(f"  Liczba użytkowników: {result[0]['user_count']}")
        else:
            print("  Baza tools_demo nie istnieje")
    except Exception as e:
        print(f"  Błąd wykonania SQL: {e}")

def example_data_processing():
    """Przykład przetwarzania danych"""
    print("\n=== 📊 Przetwarzanie danych ===")
    
    db = get_db_manager()
    
    # Pobierz dane testowe
    users = db.select_data("tools_demo", User)
    user_data = []
    for user in users:
        user_dict = {}
        for column in User.__table__.columns:
            user_dict[column.name] = getattr(user, column.name)
        user_data.append(user_dict)
    
    print(f"📥 Załadowano {len(user_data)} użytkowników")
    
    # 1. DataFilter - filtrowanie
    print("\n1. Filtrowanie danych:")
    
    # Filtruj aktywnych użytkowników
    active_users = DataFilter.filter_active_records(user_data)
    print(f"  Aktywni użytkownicy: {len(active_users)}")
    
    # Filtruj użytkowników firmowych
    company_users = DataFilter.filter_by_field(user_data, "email", "@company.com", "contains")
    print(f"  Użytkownicy firmowi: {len(company_users)}")
    
    # Filtruj użytkowników z telefonem
    users_with_phone = DataFilter.filter_by_field(user_data, "phone", None, "is_not_null")
    print(f"  Użytkownicy z telefonem: {len(users_with_phone)}")
    
    # 2. DataTransformer - transformacja
    print("\n2. Transformacja danych:")
    
    # Normalizuj emaile (małe litery)
    normalized_data = DataTransformer.normalize_strings(user_data, ["email"])
    print("  ✅ Znormalizowano emaile")
    
    # Dodaj pole obliczone
    def compute_user_type(record):
        if "@company.com" in record.get("email", ""):
            return "Internal"
        elif "@external.com" in record.get("email", ""):
            return "External"
        return "Other"
    
    enriched_data = DataTransformer.add_computed_field(user_data, "user_type", compute_user_type)
    print("  ✅ Dodano pole user_type")
    
    # Zmień nazwy pól
    renamed_data = DataTransformer.rename_fields(enriched_data, {
        "username": "login", 
        "is_active": "active_status"
    })
    print("  ✅ Zmieniono nazwy pól")
    
    # Wybierz tylko określone pola
    selected_data = DataTransformer.select_fields(enriched_data, ["username", "email", "user_type", "is_active"])
    print("  ✅ Wybrano pola: username, email, user_type, is_active")
    
    # 3. DataAggregator - agregacje
    print("\n3. Agregacje:")
    
    # Grupuj według typu użytkownika
    groups = DataAggregator.group_by(enriched_data, "user_type")
    for user_type, group in groups.items():
        print(f"  {user_type}: {len(group)} użytkowników")
    
    # Policz według statusu aktywności
    active_counts = DataAggregator.count_by_field(enriched_data, "is_active")
    print(f"  Aktywni/nieaktywni: {dict(active_counts)}")
    
    # 4. DataValidator - walidacja
    print("\n4. Walidacja danych:")
    
    # Sprawdź wymagane pola
    missing_fields = DataValidator.validate_required_fields(user_data, ["username", "email"])
    if missing_fields:
        print(f"  ❌ Rekordy z brakującymi polami: {len(missing_fields)}")
    else:
        print("  ✅ Wszystkie wymagane pola obecne")
    
    # Sprawdź typy danych
    type_errors = DataValidator.validate_data_types(user_data, {
        "username": str,
        "email": str,
        "is_active": bool
    })
    if type_errors:
        print(f"  ❌ Błędy typów: {len(type_errors)}")
    else:
        print("  ✅ Wszystkie typy poprawne")
    
    # Znajdź duplikaty
    duplicates = DataValidator.find_duplicates(user_data, ["email"])
    if duplicates:
        print(f"  ❌ Duplikaty: {len(duplicates)}")
    else:
        print("  ✅ Brak duplikatów")
    
    # 5. DataCleaner - czyszczenie
    print("\n5. Czyszczenie danych:")
    
    # Usuń rekordy z null w telefonie
    cleaned_data = DataCleaner.remove_nulls(user_data, ["phone"])
    print(f"  Rekordy bez null w telefonie: {len(cleaned_data)}")
    
    # Standaryzuj numery telefonów
    standardized_data = DataCleaner.standardize_phone_numbers(user_data)
    print("  ✅ Znormalizowano numery telefonów")
    
    # 6. Podsumowanie danych
    print("\n6. Podsumowanie danych:")
    summary = create_data_summary(user_data)
    print(f"  📊 Łączna liczba rekordów: {summary['total_records']}")
    print(f"  📋 Pola: {summary['fields']}")
    for field, stats in summary['field_stats'].items():
        print(f"    {field}: {stats['unique_count']} unikalnych, {stats['null_count']} null")

def example_export_import():
    """Przykład eksportu i importu"""
    print("\n=== 💾 Eksport i import danych ===")
    
    db = get_db_manager()
    
    # Pobierz dane do eksportu
    users = db.select_data("tools_demo", User)
    user_data = []
    for user in users:
        user_dict = {}
        for column in User.__table__.columns:
            user_dict[column.name] = getattr(user, column.name)
        user_data.append(user_dict)
    
    # Utwórz eksporter
    exporter = DataExporter()
    importer = DataImporter()
    
    # Eksport do różnych formatów
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # 1. Eksport do JSON
        json_path = os.path.join(temp_dir, "users.json")
        exporter.export_to_json(user_data, json_path, pretty=True)
        print(f"✅ Eksport do JSON: {json_path}")
        
        # Sprawdź rozmiar pliku
        file_size = os.path.getsize(json_path)
        print(f"  📏 Rozmiar: {file_size} bajtów")
        
        # 2. Eksport do CSV
        csv_path = os.path.join(temp_dir, "users.csv")
        exporter.export_to_csv(user_data, csv_path)
        print(f"✅ Eksport do CSV: {csv_path}")
        
        # 3. Eksport do XML
        xml_path = os.path.join(temp_dir, "users.xml")
        exporter.export_to_xml(user_data, xml_path, root_name="users", record_name="user")
        print(f"✅ Eksport do XML: {xml_path}")
        
        # 4. Eksport do SQL
        sql_path = os.path.join(temp_dir, "users.sql")
        exporter.export_to_sql(user_data, "users_backup", sql_path, include_create=True)
        print(f"✅ Eksport do SQL: {sql_path}")
        
        # 5. Import z JSON
        imported_data = importer.import_from_json(json_path)
        print(f"📥 Zaimportowano z JSON: {len(imported_data)} rekordów")
        
        # 6. Import z CSV
        imported_csv = importer.import_from_csv(csv_path)
        print(f"📥 Zaimportowano z CSV: {len(imported_csv)} rekordów")
        
        # 7. Porównaj dane przed i po eksport/import
        original_usernames = {u['username'] for u in user_data}
        imported_usernames = {u['username'] for u in imported_data}
        
        if original_usernames == imported_usernames:
            print("✅ Dane zgodne przed i po eksport/import")
        else:
            print("❌ Różnice w danych po eksport/import")
        
        # 8. Przykład tworzenia nazwy backup
        from utils.export_tools import create_backup_filename
        backup_name = create_backup_filename("tools_demo", "json")
        print(f"📦 Przykładowa nazwa backup: {backup_name}")

def comprehensive_workflow():
    """Kompleksowy przepływ pracy z wszystkimi narzędziami"""
    print("\n=== 🔄 Kompleksowy przepływ pracy ===")
    
    logger = get_db_logger()
    db = get_db_manager()
    
    try:
        # 1. Pobierz dane
        logger.log_database_operation("data_fetch", "tools_demo", True, "Fetching user data")
        users = db.select_data("tools_demo", User)
        
        # Konwertuj na słowniki
        user_data = []
        for user in users:
            user_dict = {}
            for column in User.__table__.columns:
                user_dict[column.name] = getattr(user, column.name)
            user_data.append(user_dict)
        
        # 2. Waliduj dane
        validator = DataValidator()
        errors = validator.validate_required_fields(user_data, ["username", "email"])
        if errors:
            logger.logger.warning(f"Found {len(errors)} validation errors")
        
        # 3. Przetwórz dane
        # Filtruj tylko aktywnych użytkowników firmowych
        active_company_users = DataFilter.filter_by_field(
            DataFilter.filter_active_records(user_data),
            "email", "@company.com", "contains"
        )
        
        # Dodaj obliczone pola
        enriched_users = DataTransformer.add_computed_field(
            active_company_users, 
            "has_phone", 
            lambda r: r.get("phone") is not None
        )
        
        # 4. Agreguj statystyki
        aggregator = DataAggregator()
        phone_stats = aggregator.count_by_field(enriched_users, "has_phone")
        
        print(f"📊 Aktywni użytkownicy firmowi: {len(enriched_users)}")
        print(f"📱 Z telefonem: {phone_stats.get(True, 0)}")
        print(f"📵 Bez telefonu: {phone_stats.get(False, 0)}")
        
        # 5. Wyeksportuj wyniki
        if enriched_users:
            exporter = DataExporter()
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                result_path = exporter.export_to_json(enriched_users, f.name)
                print(f"💾 Wyeksportowano wyniki do: {result_path}")
        
        # 6. Wygeneruj raport SQL
        builder = SQLQueryBuilder()
        report_query = (builder
                       .select("email", "username", "phone", "created_at")
                       .from_table("users")
                       .where("is_active = 1")
                       .where("email LIKE '%@company.com'")
                       .order_by("created_at", "DESC")
                       .build())
        
        print(f"🔍 Wygenerowane zapytanie raportu:")
        print(f"   {report_query}")
        
        logger.log_database_operation("workflow_complete", "tools_demo", True, 
                                    f"Processed {len(enriched_users)} records")
        
    except Exception as e:
        logger.log_error("comprehensive_workflow", e, {"step": "unknown"})
        raise

def main():
    """Główna funkcja demonstracyjna"""
    print("🚀 LuxDB - Przykłady zaawansowanych narzędzi")
    print("=" * 60)
    
    try:
        # Przygotuj dane testowe
        if not setup_test_data():
            return
        
        # Uruchom wszystkie przykłady
        example_logging_utils()
        example_error_handling()
        example_sql_tools()
        example_data_processing()
        example_export_import()
        comprehensive_workflow()
        
        print("\n✅ Wszystkie przykłady zaawansowanych narzędzi zakończone pomyślnie!")
        
    except Exception as e:
        print(f"\n❌ Błąd w przykładach: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Zamknij połączenia
        db = get_db_manager()
        db.close_all_connections()
        print("\n🔒 Zamknięto wszystkie połączenia")

if __name__ == "__main__":
    main()
