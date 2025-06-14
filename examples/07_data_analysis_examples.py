
"""
LuxDB Example 07: Analiza danych i raportowanie
- Zaawansowane filtrowanie i agregacje
- Generowanie raportów
- Analiza trendów
- Wizualizacja danych (tekstowa)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from manager import get_db_manager
from models import User, Log
from utils import (
    DataFilter, DataAggregator, DataTransformer,
    SQLQueryBuilder, SQLTemplateEngine,
    get_db_logger, handle_database_errors
)
from datetime import datetime, timedelta
from collections import defaultdict

@handle_database_errors("setup_analysis_data")
def setup_analysis_data():
    """Przygotuj rozbudowane dane do analizy"""
    db = get_db_manager()
    logger = get_db_logger()
    
    # Utwórz bazę analityczną
    if not db.create_database("analytics_demo"):
        print("❌ Nie udało się utworzyć bazy analitycznej")
        return False
    
    db.create_table_from_model("analytics_demo", User)
    db.create_table_from_model("analytics_demo", Log)
    
    # Wygeneruj realistyczne dane użytkowników
    departments = ["IT", "Sales", "Marketing", "HR", "Finance"]
    domains = ["company.com", "partner.com", "external.com"]
    
    test_users = []
    for i in range(50):
        dept = departments[i % len(departments)]
        domain = domains[i % len(domains)]
        
        user = {
            "username": f"user_{i:03d}",
            "email": f"user_{i:03d}@{domain}",
            "password_hash": f"hash_{i}",
            "is_active": i % 7 != 0,  # ~85% aktywnych
            "phone": f"+48-{500 + i:03d}-{100 + i:03d}-{200 + i:03d}" if i % 3 != 0 else None
        }
        test_users.append(user)
    
    # Wstaw użytkowników
    for user_data in test_users:
        db.insert_data("analytics_demo", User, user_data)
    
    # Wygeneruj logi dla różnych scenariuszy
    log_types = [
        ("INFO", "auth", "User login successful"),
        ("INFO", "auth", "User logout"),
        ("WARNING", "auth", "Invalid login attempt"),
        ("ERROR", "auth", "Account locked"),
        ("INFO", "system", "System backup completed"),
        ("WARNING", "system", "High memory usage"),
        ("ERROR", "system", "Service unavailable"),
        ("INFO", "api", "API request processed"),
        ("WARNING", "api", "Rate limit exceeded"),
        ("ERROR", "api", "Authentication failed"),
        ("DEBUG", "cache", "Cache miss"),
        ("INFO", "export", "Data export completed"),
        ("ERROR", "database", "Connection timeout")
    ]
    
    import random
    base_date = datetime.now() - timedelta(days=30)
    
    test_logs = []
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        
        # Więcej logów w dni robocze
        daily_logs = 50 if current_date.weekday() < 5 else 20
        
        for _ in range(daily_logs):
            level, module, message = random.choice(log_types)
            user_id = random.randint(1, 50) if random.random() > 0.3 else None
            
            # Symuluj wzór czasowy (więcej błędów w nocy)
            hour_offset = random.randint(0, 23)
            if hour_offset > 22 or hour_offset < 6:
                # Więcej błędów w nocy
                if random.random() < 0.4:
                    level = "ERROR"
            
            log_time = current_date + timedelta(hours=hour_offset, 
                                              minutes=random.randint(0, 59))
            
            log = {
                "level": level,
                "message": message,
                "module": module,
                "user_id": user_id,
                "created_at": log_time
            }
            test_logs.append(log)
    
    # Wstaw logi
    db.insert_batch("analytics_demo", Log, test_logs)
    
    logger.log_database_operation("setup_analysis_data", "analytics_demo", True, 
                                f"Created {len(test_users)} users and {len(test_logs)} logs")
    print(f"✅ Utworzono {len(test_users)} użytkowników i {len(test_logs)} logów")
    return True

def analyze_user_activity():
    """Analiza aktywności użytkowników"""
    print("\n=== 👥 Analiza aktywności użytkowników ===")
    
    db = get_db_manager()
    
    # Pobierz dane użytkowników
    users = db.select_data("analytics_demo", User)
    user_data = []
    for user in users:
        user_dict = {}
        for column in User.__table__.columns:
            user_dict[column.name] = getattr(user, column.name)
        user_data.append(user_dict)
    
    # 1. Analiza według domeny email
    print("1. Rozkład użytkowników według domeny:")
    domain_groups = {}
    for user in user_data:
        domain = user['email'].split('@')[1]
        if domain not in domain_groups:
            domain_groups[domain] = []
        domain_groups[domain].append(user)
    
    for domain, users_in_domain in domain_groups.items():
        active_count = len(DataFilter.filter_active_records(users_in_domain))
        total_count = len(users_in_domain)
        percentage = (active_count / total_count * 100) if total_count > 0 else 0
        print(f"  📧 {domain}: {total_count} użytkowników ({active_count} aktywnych, {percentage:.1f}%)")
    
    # 2. Analiza kontaktów
    print("\n2. Analiza danych kontaktowych:")
    users_with_phone = DataFilter.filter_by_field(user_data, "phone", None, "is_not_null")
    users_without_phone = DataFilter.filter_by_field(user_data, "phone", None, "is_null")
    
    print(f"  📱 Z telefonem: {len(users_with_phone)} ({len(users_with_phone)/len(user_data)*100:.1f}%)")
    print(f"  📵 Bez telefonu: {len(users_without_phone)} ({len(users_without_phone)/len(user_data)*100:.1f}%)")
    
    # 3. Segmentacja użytkowników
    print("\n3. Segmentacja użytkowników:")
    
    def classify_user(user):
        domain = user['email'].split('@')[1]
        has_phone = user['phone'] is not None
        is_active = user['is_active']
        
        if domain == "company.com":
            if is_active and has_phone:
                return "VIP Internal"
            elif is_active:
                return "Active Internal"
            else:
                return "Inactive Internal"
        elif domain == "partner.com":
            return "Partner" if is_active else "Inactive Partner"
        else:
            return "External" if is_active else "Inactive External"
    
    # Dodaj segmentację
    segmented_users = DataTransformer.add_computed_field(user_data, "segment", classify_user)
    
    # Policz segmenty
    segment_counts = DataAggregator.count_by_field(segmented_users, "segment")
    
    for segment, count in sorted(segment_counts.items()):
        percentage = count / len(user_data) * 100
        print(f"  🏷️  {segment}: {count} ({percentage:.1f}%)")

def analyze_log_patterns():
    """Analiza wzorców w logach"""
    print("\n=== 📊 Analiza wzorców w logach ===")
    
    db = get_db_manager()
    
    # Pobierz logi
    logs = db.select_data("analytics_demo", Log)
    log_data = []
    for log in logs:
        log_dict = {}
        for column in Log.__table__.columns:
            value = getattr(log, column.name)
            log_dict[column.name] = value
        log_data.append(log_dict)
    
    print(f"📥 Analizując {len(log_data)} wpisów w logach")
    
    # 1. Rozkład poziomów logów
    print("\n1. Rozkład poziomów logów:")
    level_counts = DataAggregator.count_by_field(log_data, "level")
    total_logs = len(log_data)
    
    for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        count = level_counts.get(level, 0)
        percentage = count / total_logs * 100
        bar = "█" * int(percentage / 2)  # Prosta wizualizacja
        print(f"  {level:8}: {count:4} ({percentage:5.1f}%) {bar}")
    
    # 2. Aktywność według modułów
    print("\n2. Aktywność według modułów:")
    module_stats = {}
    
    modules = set(log['module'] for log in log_data)
    for module in modules:
        module_logs = DataFilter.filter_by_field(log_data, "module", module)
        error_logs = DataFilter.filter_by_field(module_logs, "level", "ERROR")
        
        module_stats[module] = {
            "total": len(module_logs),
            "errors": len(error_logs),
            "error_rate": len(error_logs) / len(module_logs) * 100 if module_logs else 0
        }
    
    for module, stats in sorted(module_stats.items()):
        print(f"  🔧 {module:10}: {stats['total']:3} logów, {stats['errors']:2} błędów ({stats['error_rate']:4.1f}%)")
    
    # 3. Analiza czasowa
    print("\n3. Wzorce czasowe:")
    
    # Grupuj według dnia
    daily_stats = defaultdict(lambda: {"total": 0, "errors": 0})
    
    for log in log_data:
        if log['created_at']:
            # Konwertuj string na datetime jeśli potrzeba
            if isinstance(log['created_at'], str):
                try:
                    created_at = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
                except:
                    continue
            else:
                created_at = log['created_at']
            
            date_key = created_at.strftime('%Y-%m-%d')
            daily_stats[date_key]["total"] += 1
            if log['level'] == "ERROR":
                daily_stats[date_key]["errors"] += 1
    
    # Pokaż ostatnie 7 dni
    print("  📅 Ostatnie 7 dni:")
    sorted_dates = sorted(daily_stats.keys())[-7:]
    
    for date in sorted_dates:
        stats = daily_stats[date]
        error_rate = stats["errors"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"    {date}: {stats['total']:3} logów, {stats['errors']:2} błędów ({error_rate:4.1f}%)")

def generate_executive_report():
    """Generuj raport wykonawczy"""
    print("\n=== 📋 Raport wykonawczy ===")
    
    db = get_db_manager()
    
    # Użyj SQL Builder do złożonych zapytań
    builder = SQLQueryBuilder()
    
    # 1. Podsumowanie użytkowników
    print("1. Podsumowanie użytkowników:")
    
    user_summary_query = (builder
                         .select("COUNT(*) as total_users",
                                "SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_users",
                                "SUM(CASE WHEN phone IS NOT NULL THEN 1 ELSE 0 END) as users_with_phone")
                         .from_table("users")
                         .build())
    
    try:
        result = db.execute_raw_sql("analytics_demo", user_summary_query)
        if result:
            stats = result[0]
            print(f"  👥 Łączna liczba użytkowników: {stats['total_users']}")
            print(f"  ✅ Aktywnych: {stats['active_users']} ({stats['active_users']/stats['total_users']*100:.1f}%)")
            print(f"  📱 Z danymi kontaktowymi: {stats['users_with_phone']} ({stats['users_with_phone']/stats['total_users']*100:.1f}%)")
    except Exception as e:
        print(f"  ❌ Błąd pozyskiwania statystyk użytkowników: {e}")
    
    # 2. Statystyki systemowe
    print("\n2. Statystyki systemowe (ostatnie 7 dni):")
    
    builder.reset()
    system_query = (builder
                   .select("DATE(created_at) as log_date",
                          "COUNT(*) as total_logs",
                          "SUM(CASE WHEN level = 'ERROR' THEN 1 ELSE 0 END) as error_count",
                          "SUM(CASE WHEN level = 'WARNING' THEN 1 ELSE 0 END) as warning_count")
                   .from_table("logs")
                   .where("created_at >= datetime('now', '-7 days')")
                   .group_by("DATE(created_at)")
                   .order_by("log_date", "DESC")
                   .build())
    
    try:
        results = db.execute_raw_sql("analytics_demo", system_query)
        if results:
            print(f"  {'Data':<12} {'Łącznie':<8} {'Błędy':<6} {'Ostrzeżenia':<11} {'Wskaźnik'}")
            print(f"  {'-'*12} {'-'*8} {'-'*6} {'-'*11} {'-'*8}")
            
            for row in results:
                error_rate = (row['error_count'] / row['total_logs'] * 100) if row['total_logs'] > 0 else 0
                print(f"  {row['log_date']:<12} {row['total_logs']:<8} {row['error_count']:<6} {row['warning_count']:<11} {error_rate:6.1f}%")
    except Exception as e:
        print(f"  ❌ Błąd pozyskiwania statystyk systemowych: {e}")
    
    # 3. Top problemy
    print("\n3. Najczęstsze problemy:")
    
    builder.reset()
    problems_query = (builder
                     .select("message", "COUNT(*) as occurrence_count", "module")
                     .from_table("logs")
                     .where("level IN ('ERROR', 'WARNING')")
                     .where("created_at >= datetime('now', '-7 days')")
                     .group_by("message", "module")
                     .order_by("occurrence_count", "DESC")
                     .limit(5)
                     .build())
    
    try:
        problems = db.execute_raw_sql("analytics_demo", problems_query)
        if problems:
            for i, problem in enumerate(problems, 1):
                print(f"  {i}. [{problem['module']}] {problem['message']} ({problem['occurrence_count']} razy)")
        else:
            print("  ✅ Brak znaczących problemów w ostatnich 7 dniach")
    except Exception as e:
        print(f"  ❌ Błąd analizy problemów: {e}")
    
    # 4. Rekomendacje
    print("\n4. Rekomendacje:")
    
    # Analiza na podstawie zebranych danych
    try:
        # Sprawdź wskaźnik błędów
        builder.reset()
        error_rate_query = (builder
                           .select("COUNT(*) as total_logs",
                                  "SUM(CASE WHEN level = 'ERROR' THEN 1 ELSE 0 END) as error_count")
                           .from_table("logs")
                           .where("created_at >= datetime('now', '-7 days')")
                           .build())
        
        error_stats = db.execute_raw_sql("analytics_demo", error_rate_query)
        if error_stats and error_stats[0]['total_logs'] > 0:
            error_rate = error_stats[0]['error_count'] / error_stats[0]['total_logs'] * 100
            
            if error_rate > 10:
                print("  🔴 KRYTYCZNE: Wysoki wskaźnik błędów (>10%) - wymaga natychmiastowej uwagi")
            elif error_rate > 5:
                print("  🟡 UWAGA: Podwyższony wskaźnik błędów (>5%) - zaleca się monitoring")
            else:
                print("  🟢 DOBRY: Normalny wskaźnik błędów (<5%)")
        
        # Sprawdź kompletność danych użytkowników
        incomplete_users_query = (builder.reset()
                                 .select("COUNT(*) as users_without_phone")
                                 .from_table("users")
                                 .where("phone IS NULL")
                                 .where("is_active = 1")
                                 .build())
        
        incomplete_data = db.execute_raw_sql("analytics_demo", incomplete_users_query)
        if incomplete_data and incomplete_data[0]['users_without_phone'] > 0:
            count = incomplete_data[0]['users_without_phone']
            print(f"  📞 Zaleca się uzupełnienie danych kontaktowych dla {count} aktywnych użytkowników")
        
        print("  💡 Zaimplementowano monitoring automatyczny z wykorzystaniem LuxDB")
        print("  📊 Raporty są generowane automatycznie z wykorzystaniem zaawansowanych narzędzi SQL")
        
    except Exception as e:
        print(f"  ❌ Błąd generowania rekomendacji: {e}")

def trend_analysis():
    """Analiza trendów"""
    print("\n=== 📈 Analiza trendów ===")
    
    db = get_db_manager()
    
    # Pobierz dane logów z ostatnich 14 dni
    builder = SQLQueryBuilder()
    trend_query = (builder
                  .select("DATE(created_at) as day",
                         "strftime('%H', created_at) as hour",
                         "COUNT(*) as log_count",
                         "level")
                  .from_table("logs")
                  .where("created_at >= datetime('now', '-14 days')")
                  .group_by("DATE(created_at)", "strftime('%H', created_at)", "level")
                  .order_by("day", "ASC")
                  .order_by("hour", "ASC")
                  .build())
    
    try:
        trend_data = db.execute_raw_sql("analytics_demo", trend_query)
        
        if trend_data:
            # Grupuj dane według dnia
            daily_trends = defaultdict(lambda: {"total": 0, "errors": 0, "hours": defaultdict(int)})
            
            for row in trend_data:
                day = row['day']
                hour = int(row['hour'])
                count = row['log_count']
                level = row['level']
                
                daily_trends[day]["total"] += count
                daily_trends[day]["hours"][hour] += count
                
                if level == "ERROR":
                    daily_trends[day]["errors"] += count
            
            # Analiza trendu aktywności
            print("1. Trend aktywności systemowej (ostatnie 7 dni):")
            
            sorted_days = sorted(daily_trends.keys())[-7:]
            prev_total = None
            
            for day in sorted_days:
                stats = daily_trends[day]
                total = stats["total"]
                errors = stats["errors"]
                error_rate = (errors / total * 100) if total > 0 else 0
                
                trend_indicator = ""
                if prev_total is not None:
                    if total > prev_total * 1.1:
                        trend_indicator = "📈"
                    elif total < prev_total * 0.9:
                        trend_indicator = "📉"
                    else:
                        trend_indicator = "➡️"
                
                print(f"  {day}: {total:4} logów, {errors:2} błędów ({error_rate:4.1f}%) {trend_indicator}")
                prev_total = total
            
            # Analiza wzorców godzinowych
            print("\n2. Wzorce aktywności w ciągu dnia:")
            
            hourly_totals = defaultdict(int)
            for day_stats in daily_trends.values():
                for hour, count in day_stats["hours"].items():
                    hourly_totals[hour] += count
            
            max_hourly = max(hourly_totals.values()) if hourly_totals else 1
            
            for hour in range(0, 24, 3):  # Co 3 godziny
                count = hourly_totals.get(hour, 0)
                percentage = count / max_hourly * 100 if max_hourly > 0 else 0
                bar = "█" * int(percentage / 10)
                print(f"  {hour:02d}:00-{hour+2:02d}:59: {count:4} ({percentage:5.1f}%) {bar}")
        
        else:
            print("  📊 Brak danych do analizy trendów")
    
    except Exception as e:
        print(f"❌ Błąd analizy trendów: {e}")

def performance_insights():
    """Wglądy w wydajność"""
    print("\n=== ⚡ Analiza wydajności ===")
    
    db = get_db_manager()
    
    # Sprawdź wydajność różnych operacji
    operations = [
        ("Prosty SELECT", "SELECT COUNT(*) FROM users"),
        ("SELECT z WHERE", "SELECT COUNT(*) FROM users WHERE is_active = 1"),
        ("JOIN", "SELECT COUNT(*) FROM users u LEFT JOIN logs l ON u.id = l.user_id"),
        ("Agregacja", "SELECT level, COUNT(*) FROM logs GROUP BY level"),
        ("Sortowanie", "SELECT * FROM logs ORDER BY created_at DESC LIMIT 10")
    ]
    
    print("Testowanie wydajności zapytań:")
    
    for name, query in operations:
        start_time = datetime.now()
        try:
            result = db.execute_raw_sql("analytics_demo", query)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result_count = len(result) if result else 0
            print(f"  🔍 {name:15}: {execution_time:6.1f}ms (wyników: {result_count})")
            
        except Exception as e:
            print(f"  ❌ {name:15}: Błąd - {e}")
    
    # Analiza rozmiarów tabel
    print("\n📊 Statystyki tabel:")
    
    table_queries = [
        ("users", "SELECT COUNT(*) as count FROM users"),
        ("logs", "SELECT COUNT(*) as count FROM logs")
    ]
    
    for table_name, query in table_queries:
        try:
            result = db.execute_raw_sql("analytics_demo", query)
            if result:
                count = result[0]['count']
                print(f"  📋 {table_name:10}: {count:6} rekordów")
        except Exception as e:
            print(f"  ❌ {table_name:10}: Błąd - {e}")

def main():
    """Główna funkcja analityczna"""
    print("🚀 LuxDB - Zaawansowana analiza danych")
    print("=" * 60)
    
    logger = get_db_logger()
    
    try:
        # Przygotuj dane analityczne
        logger.log_database_operation("analysis_start", "analytics_demo", True, "Starting data analysis")
        
        if not setup_analysis_data():
            return
        
        # Uruchom analizy
        analyze_user_activity()
        analyze_log_patterns()
        generate_executive_report()
        trend_analysis()
        performance_insights()
        
        logger.log_database_operation("analysis_complete", "analytics_demo", True, "Data analysis completed successfully")
        print("\n✅ Analiza danych zakończona pomyślnie!")
        
    except Exception as e:
        logger.log_error("data_analysis", e)
        print(f"\n❌ Błąd podczas analizy: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Zamknij połączenia
        db = get_db_manager()
        db.close_all_connections()
        print("\n🔒 Zamknięto wszystkie połączenia")

if __name__ == "__main__":
    main()
