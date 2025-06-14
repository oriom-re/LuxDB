
"""
LuxDB Example 08: Rzeczywiste scenariusze biznesowe
- E-commerce: zarządzanie produktami i zamówieniami
- CRM: zarządzanie klientami i kontaktami
- System logowania: monitoring i alerting
- Data warehouse: ETL i raportowanie
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from manager import get_db_manager
from utils import (
    get_db_logger, handle_database_errors, ErrorCollector,
    DataFilter, DataTransformer, DataAggregator, DataValidator,
    DataExporter, SQLQueryBuilder,
    LuxDBError, ModelValidationError
)
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Definicje modeli dla rzeczywistych scenariuszy
from sqlalchemy import Column, Integer, String, Decimal as SQLDecimal, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Customer(Base):
    """Model klienta dla CRM"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    company = Column(String(100))
    status = Column(String(20), default='active')  # active, inactive, prospect
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    orders = relationship("Order", back_populates="customer")

class Product(Base):
    """Model produktu dla e-commerce"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    price = Column(SQLDecimal(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    category = Column(String(50))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Order(Base):
    """Model zamówienia"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    total_amount = Column(SQLDecimal(10, 2), nullable=False)
    order_date = Column(DateTime, default=datetime.now)
    shipping_date = Column(DateTime)
    delivery_date = Column(DateTime)
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    """Pozycja zamówienia"""
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(SQLDecimal(10, 2), nullable=False)
    total_price = Column(SQLDecimal(10, 2), nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

class SystemAlert(Base):
    """Alerty systemowe"""
    __tablename__ = 'system_alerts'
    
    id = Column(Integer, primary_key=True)
    alert_type = Column(String(50), nullable=False)  # performance, security, business
    severity = Column(String(20), nullable=False)    # low, medium, high, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    source_system = Column(String(50))
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    resolved_at = Column(DateTime)

@handle_database_errors("ecommerce_scenario")
def ecommerce_scenario():
    """Scenariusz e-commerce: zarządzanie produktami i zamówieniami"""
    print("\n=== 🛒 Scenariusz E-commerce ===")
    
    db = get_db_manager()
    logger = get_db_logger()
    
    # Utwórz bazę e-commerce
    if not db.create_database("ecommerce_db"):
        raise LuxDBError("Nie udało się utworzyć bazy e-commerce")
    
    # Utwórz tabele
    for model in [Customer, Product, Order, OrderItem]:
        db.create_table_from_model("ecommerce_db", model)
    
    logger.log_database_operation("ecommerce_setup", "ecommerce_db", True, "Created e-commerce tables")
    
    # 1. Zarządzanie produktami
    print("1. 📦 Zarządzanie katalogiem produktów")
    
    categories = ["Electronics", "Clothing", "Home & Garden", "Books", "Sports"]
    products_data = []
    
    for i in range(100):
        product = {
            "name": f"Product {i:03d}",
            "sku": f"SKU-{i:05d}",
            "price": round(random.uniform(10, 500), 2),
            "stock_quantity": random.randint(0, 100),
            "category": random.choice(categories),
            "description": f"Description for product {i:03d}",
            "is_active": random.random() > 0.1  # 90% aktywnych
        }
        products_data.append(product)
    
    # Wstaw produkty w batchu dla wydajności
    success = db.insert_batch("ecommerce_db", Product, products_data)
    if success:
        print(f"  ✅ Dodano {len(products_data)} produktów")
    else:
        print("  ❌ Błąd dodawania produktów")
    
    # 2. Zarządzanie klientami
    print("\n2. 👥 Zarządzanie bazą klientów")
    
    first_names = ["Jan", "Anna", "Piotr", "Maria", "Tomasz", "Agnieszka", "Michał", "Katarzyna"]
    last_names = ["Kowalski", "Nowak", "Wiśniewski", "Dąbrowski", "Lewandowski", "Wójcik"]
    companies = ["TechCorp", "InnoSoft", "DataSystems", "CloudTech", None]
    
    customers_data = []
    for i in range(50):
        customer = {
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "email": f"customer{i:03d}@example.com",
            "phone": f"+48-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(100, 999)}",
            "company": random.choice(companies),
            "status": random.choice(["active", "active", "active", "prospect", "inactive"])  # Więcej aktywnych
        }
        customers_data.append(customer)
    
    db.insert_batch("ecommerce_db", Customer, customers_data)
    print(f"  ✅ Dodano {len(customers_data)} klientów")
    
    # 3. Generowanie zamówień
    print("\n3. 🧾 Generowanie zamówień")
    
    # Pobierz klientów i produkty
    customers = db.select_data("ecommerce_db", Customer, {"status": "active"})
    products = db.select_data("ecommerce_db", Product, {"is_active": True})
    
    orders_data = []
    order_items_data = []
    
    for i in range(200):
        customer = random.choice(customers)
        order_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        order = {
            "customer_id": customer.id,
            "order_number": f"ORD-{i:06d}",
            "status": random.choice(["pending", "confirmed", "shipped", "delivered"]),
            "order_date": order_date,
            "total_amount": 0  # Będzie obliczone później
        }
        
        # Symuluj shipping i delivery dates
        if order["status"] in ["shipped", "delivered"]:
            order["shipping_date"] = order_date + timedelta(days=random.randint(1, 3))
        if order["status"] == "delivered":
            order["delivery_date"] = order["shipping_date"] + timedelta(days=random.randint(1, 7))
        
        orders_data.append(order)
        
        # Generuj pozycje zamówienia
        num_items = random.randint(1, 5)
        order_total = Decimal('0.00')
        
        for j in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 3)
            unit_price = product.price
            total_price = unit_price * quantity
            order_total += total_price
            
            order_item = {
                "order_id": i + 1,  # Zakładając auto-increment ID
                "product_id": product.id,
                "quantity": quantity,
                "unit_price": float(unit_price),
                "total_price": float(total_price)
            }
            order_items_data.append(order_item)
        
        orders_data[i]["total_amount"] = float(order_total)
    
    # Wstaw zamówienia
    db.insert_batch("ecommerce_db", Order, orders_data)
    print(f"  ✅ Wygenerowano {len(orders_data)} zamówień")
    
    # 4. Analiza sprzedaży
    print("\n4. 📊 Analiza wyników sprzedaży")
    
    builder = SQLQueryBuilder()
    
    # Sprzedaż według kategorii
    sales_query = (builder
                  .select("p.category",
                         "COUNT(DISTINCT o.id) as order_count",
                         "SUM(oi.total_price) as total_revenue",
                         "AVG(oi.total_price) as avg_item_value")
                  .from_table("orders o")
                  .join("order_items oi", "o.id = oi.order_id")
                  .join("products p", "oi.product_id = p.id")
                  .where("o.status IN ('confirmed', 'shipped', 'delivered')")
                  .group_by("p.category")
                  .order_by("total_revenue", "DESC")
                  .build())
    
    try:
        sales_results = db.execute_raw_sql("ecommerce_db", sales_query)
        if sales_results:
            print(f"  {'Kategoria':<15} {'Zamówienia':<10} {'Przychód':<12} {'Śr. wartość'}")
            print(f"  {'-'*15} {'-'*10} {'-'*12} {'-'*10}")
            
            for row in sales_results:
                print(f"  {row['category']:<15} {row['order_count']:<10} {row['total_revenue']:<12.2f} {row['avg_item_value']:<10.2f}")
    except Exception as e:
        print(f"  ❌ Błąd analizy sprzedaży: {e}")
    
    # 5. Alert o niskich stanach magazynowych
    print("\n5. ⚠️ Monitoring stanu magazynu")
    
    low_stock_query = (SQLQueryBuilder()
                      .select("name", "sku", "stock_quantity", "category")
                      .from_table("products")
                      .where("stock_quantity < 10")
                      .where("is_active = 1")
                      .order_by("stock_quantity", "ASC")
                      .build())
    
    try:
        low_stock = db.execute_raw_sql("ecommerce_db", low_stock_query)
        if low_stock:
            print(f"  🔴 Produkty o niskim stanie ({len(low_stock)}):")
            for product in low_stock[:5]:  # Pokaż top 5
                print(f"    {product['sku']}: {product['name']} - {product['stock_quantity']} szt.")
        else:
            print("  ✅ Wszystkie produkty mają wystarczający stan magazynowy")
    except Exception as e:
        print(f"  ❌ Błąd sprawdzania stanu magazynu: {e}")

@handle_database_errors("crm_scenario")
def crm_scenario():
    """Scenariusz CRM: zarządzanie relacjami z klientami"""
    print("\n=== 👔 Scenariusz CRM ===")
    
    db = get_db_manager()
    logger = get_db_logger()
    
    # Użyj istniejącej bazy ecommerce_db z danymi klientów
    if "ecommerce_db" not in db.list_databases():
        print("  ❌ Baza e-commerce nie istnieje, uruchom najpierw ecommerce_scenario()")
        return
    
    # 1. Segmentacja klientów
    print("1. 🎯 Segmentacja klientów")
    
    # Pobierz dane klientów z ich zamówieniami
    customer_analysis_query = """
    SELECT 
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.company,
        c.status,
        COUNT(o.id) as order_count,
        COALESCE(SUM(o.total_amount), 0) as total_spent,
        MAX(o.order_date) as last_order_date,
        CASE 
            WHEN COUNT(o.id) = 0 THEN 'No Orders'
            WHEN COUNT(o.id) >= 5 AND SUM(o.total_amount) >= 1000 THEN 'VIP'
            WHEN COUNT(o.id) >= 2 AND SUM(o.total_amount) >= 500 THEN 'Regular'
            WHEN COUNT(o.id) >= 1 THEN 'Occasional'
            ELSE 'Prospect'
        END as customer_segment
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.first_name, c.last_name, c.email, c.company, c.status
    """
    
    try:
        customer_segments = db.execute_raw_sql("ecommerce_db", customer_analysis_query)
        if customer_segments:
            # Agreguj według segmentów
            segments_data = []
            for customer in customer_segments:
                segments_data.append({
                    "customer_id": customer["id"],
                    "name": f"{customer['first_name']} {customer['last_name']}",
                    "email": customer["email"],
                    "segment": customer["customer_segment"],
                    "total_spent": float(customer["total_spent"]),
                    "order_count": customer["order_count"]
                })
            
            # Analizuj segmenty
            segment_stats = DataAggregator.count_by_field(segments_data, "segment")
            
            print(f"  {'Segment':<12} {'Klienci':<8} {'Procent'}")
            print(f"  {'-'*12} {'-'*8} {'-'*7}")
            
            total_customers = len(segments_data)
            for segment, count in sorted(segment_stats.items()):
                percentage = count / total_customers * 100
                print(f"  {segment:<12} {count:<8} {percentage:6.1f}%")
            
            # Top klienci VIP
            vip_customers = DataFilter.filter_by_field(segments_data, "segment", "VIP")
            if vip_customers:
                print(f"\n  🌟 Top klienci VIP:")
                sorted_vip = sorted(vip_customers, key=lambda x: x["total_spent"], reverse=True)
                for customer in sorted_vip[:3]:
                    print(f"    {customer['name']}: {customer['total_spent']:.2f} PLN ({customer['order_count']} zamówień)")
    
    except Exception as e:
        print(f"  ❌ Błąd segmentacji klientów: {e}")
    
    # 2. Analiza retencji klientów
    print("\n2. 🔄 Analiza retencji klientów")
    
    retention_query = """
    SELECT 
        DATE(o.order_date, 'start of month') as order_month,
        COUNT(DISTINCT o.customer_id) as unique_customers,
        COUNT(o.id) as total_orders,
        AVG(o.total_amount) as avg_order_value
    FROM orders o
    WHERE o.order_date >= datetime('now', '-6 months')
    GROUP BY DATE(o.order_date, 'start of month')
    ORDER BY order_month DESC
    """
    
    try:
        retention_data = db.execute_raw_sql("ecommerce_db", retention_query)
        if retention_data:
            print(f"  {'Miesiąc':<12} {'Klienci':<8} {'Zamówienia':<10} {'Śr. wartość'}")
            print(f"  {'-'*12} {'-'*8} {'-'*10} {'-'*11}")
            
            for row in retention_data:
                month = row['order_month'][:7]  # YYYY-MM
                print(f"  {month:<12} {row['unique_customers']:<8} {row['total_orders']:<10} {row['avg_order_value']:<11.2f}")
    
    except Exception as e:
        print(f"  ❌ Błąd analizy retencji: {e}")
    
    # 3. Identyfikacja klientów wymagających uwagi
    print("\n3. 🚨 Klienci wymagający uwagi")
    
    # Klienci, którzy nie złożyli zamówienia przez długi czas
    inactive_customers_query = """
    SELECT 
        c.first_name,
        c.last_name,
        c.email,
        MAX(o.order_date) as last_order_date,
        julianday('now') - julianday(MAX(o.order_date)) as days_since_last_order,
        COUNT(o.id) as total_orders,
        SUM(o.total_amount) as total_spent
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    WHERE c.status = 'active'
    GROUP BY c.id
    HAVING days_since_last_order > 60 AND total_orders >= 2
    ORDER BY total_spent DESC
    LIMIT 5
    """
    
    try:
        inactive_customers = db.execute_raw_sql("ecommerce_db", inactive_customers_query)
        if inactive_customers:
            print("  📧 Klienci do kampanii reaktywacyjnej:")
            for customer in inactive_customers:
                days = int(customer['days_since_last_order'])
                print(f"    {customer['first_name']} {customer['last_name']}: {days} dni temu ({customer['total_spent']:.2f} PLN)")
        else:
            print("  ✅ Brak klientów wymagających kampanii reaktywacyjnej")
    
    except Exception as e:
        print(f"  ❌ Błąd identyfikacji nieaktywnych klientów: {e}")

@handle_database_errors("monitoring_scenario")
def monitoring_scenario():
    """Scenariusz monitoringu systemowego"""
    print("\n=== 🔍 Scenariusz Monitoring Systemowy ===")
    
    db = get_db_manager()
    logger = get_db_logger()
    
    # Utwórz bazę monitoringu
    if not db.create_database("monitoring_db"):
        raise LuxDBError("Nie udało się utworzyć bazy monitoringu")
    
    db.create_table_from_model("monitoring_db", SystemAlert)
    
    # 1. Generowanie alertów systemowych
    print("1. 🚨 Generowanie alertów systemowych")
    
    alert_types = [
        ("performance", "high", "High CPU Usage", "CPU usage exceeded 90% for 5 minutes"),
        ("performance", "medium", "Memory Warning", "Memory usage is at 75%"),
        ("security", "critical", "Failed Login Attempts", "Multiple failed login attempts detected"),
        ("security", "high", "Suspicious Activity", "Unusual access pattern detected"),
        ("business", "medium", "Low Stock Alert", "Multiple products below minimum stock level"),
        ("business", "low", "Order Processing Delay", "Order processing time increased"),
        ("performance", "critical", "Database Connection Timeout", "Database response time exceeded threshold"),
        ("security", "medium", "Unauthorized API Access", "API access from unrecognized IP"),
        ("business", "high", "Payment Processing Error", "Payment gateway returned errors"),
        ("performance", "low", "Slow Query Detected", "Database query execution time warning")
    ]
    
    systems = ["web-server", "api-gateway", "database", "payment-service", "notification-service"]
    
    alerts_data = []
    error_collector = ErrorCollector()
    
    # Generuj alerty z ostatnich 7 dni
    for day in range(7):
        base_date = datetime.now() - timedelta(days=day)
        
        # Więcej alertów w dzień roboczy
        daily_alerts = 15 if base_date.weekday() < 5 else 8
        
        for _ in range(daily_alerts):
            alert_type, severity, title, message = random.choice(alert_types)
            
            # Symuluj różne wzorce
            alert_time = base_date + timedelta(
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            alert = {
                "alert_type": alert_type,
                "severity": severity,
                "title": title,
                "message": message,
                "source_system": random.choice(systems),
                "is_resolved": random.random() > 0.3,  # 70% rozwiązanych
                "created_at": alert_time
            }
            
            # Dodaj resolved_at dla rozwiązanych alertów
            if alert["is_resolved"]:
                alert["resolved_at"] = alert_time + timedelta(
                    hours=random.randint(1, 24)
                )
            
            error_collector.increment_total()
            try:
                alerts_data.append(alert)
                error_collector.add_success()
            except Exception as e:
                error_collector.add_error(e, {"alert": alert})
    
    # Wstaw alerty
    success = db.insert_batch("monitoring_db", SystemAlert, alerts_data)
    
    if success:
        print(f"  ✅ Wygenerowano {len(alerts_data)} alertów")
        
        # Pokaż statystyki generowania
        summary = error_collector.get_summary()
        if summary['failed_operations'] > 0:
            print(f"  ⚠️  {summary['failed_operations']} błędów podczas generowania")
    else:
        print("  ❌ Błąd generowania alertów")
        return
    
    # 2. Analiza alertów według priorytetów
    print("\n2. 📊 Analiza alertów według priorytetów")
    
    priority_analysis_query = (SQLQueryBuilder()
                              .select("severity",
                                     "COUNT(*) as alert_count",
                                     "SUM(CASE WHEN is_resolved = 1 THEN 1 ELSE 0 END) as resolved_count",
                                     "AVG(CASE WHEN is_resolved = 1 THEN julianday(resolved_at) - julianday(created_at) ELSE NULL END) as avg_resolution_time")
                              .from_table("system_alerts")
                              .where("created_at >= datetime('now', '-7 days')")
                              .group_by("severity")
                              .order_by("CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END")
                              .build())
    
    try:
        priority_results = db.execute_raw_sql("monitoring_db", priority_analysis_query)
        if priority_results:
            print(f"  {'Priorytet':<10} {'Łącznie':<8} {'Rozwiązane':<10} {'Śr. czas':<10}")
            print(f"  {'-'*10} {'-'*8} {'-'*10} {'-'*10}")
            
            for row in priority_results:
                resolution_rate = (row['resolved_count'] / row['alert_count'] * 100) if row['alert_count'] > 0 else 0
                avg_time = row['avg_resolution_time'] or 0
                avg_hours = avg_time * 24  # Konwersja dni na godziny
                
                print(f"  {row['severity']:<10} {row['alert_count']:<8} {resolution_rate:<9.1f}% {avg_hours:<9.1f}h")
    
    except Exception as e:
        print(f"  ❌ Błąd analizy priorytetów: {e}")
    
    # 3. Trendy alertów w czasie
    print("\n3. 📈 Trendy alertów w czasie")
    
    trends_query = """
    SELECT 
        DATE(created_at) as alert_date,
        COUNT(*) as total_alerts,
        SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_alerts,
        SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high_alerts,
        COUNT(DISTINCT source_system) as affected_systems
    FROM system_alerts
    WHERE created_at >= datetime('now', '-7 days')
    GROUP BY DATE(created_at)
    ORDER BY alert_date DESC
    """
    
    try:
        trends_data = db.execute_raw_sql("monitoring_db", trends_query)
        if trends_data:
            print(f"  {'Data':<12} {'Łącznie':<8} {'Krytyczne':<10} {'Wysokie':<8} {'Systemy'}")
            print(f"  {'-'*12} {'-'*8} {'-'*10} {'-'*8} {'-'*7}")
            
            for row in trends_data:
                print(f"  {row['alert_date']:<12} {row['total_alerts']:<8} {row['critical_alerts']:<10} {row['high_alerts']:<8} {row['affected_systems']}")
    
    except Exception as e:
        print(f"  ❌ Błąd analizy trendów: {e}")
    
    # 4. System rekomendacji
    print("\n4. 💡 Rekomendacje systemowe")
    
    # Znajdź systemy z najwyższą liczbą nierozwiązanych alertów
    problem_systems_query = """
    SELECT 
        source_system,
        COUNT(*) as unresolved_alerts,
        COUNT(CASE WHEN severity IN ('critical', 'high') THEN 1 END) as critical_high_alerts,
        MIN(created_at) as oldest_alert
    FROM system_alerts
    WHERE is_resolved = 0
    GROUP BY source_system
    HAVING unresolved_alerts >= 2
    ORDER BY critical_high_alerts DESC, unresolved_alerts DESC
    """
    
    try:
        problem_systems = db.execute_raw_sql("monitoring_db", problem_systems_query)
        if problem_systems:
            print("  🚨 Systemy wymagające uwagi:")
            for system in problem_systems:
                print(f"    {system['source_system']}: {system['unresolved_alerts']} nierozwiązanych ({system['critical_high_alerts']} krytycznych/wysokich)")
        else:
            print("  ✅ Wszystkie systemy działają prawidłowo")
        
        # Ogólne rekomendacje
        total_unresolved_query = "SELECT COUNT(*) as count FROM system_alerts WHERE is_resolved = 0"
        unresolved_result = db.execute_raw_sql("monitoring_db", total_unresolved_query)
        
        if unresolved_result:
            unresolved_count = unresolved_result[0]['count']
            if unresolved_count > 10:
                print("  📋 Zalecenie: Rozważ zwiększenie zespołu wsparcia technicznego")
            elif unresolved_count > 5:
                print("  📋 Zalecenie: Przeanalizuj najczęstsze przyczyny alertów")
            else:
                print("  📋 Status: Poziom alertów w normie")
    
    except Exception as e:
        print(f"  ❌ Błąd generowania rekomendacji: {e}")

@handle_database_errors("data_warehouse_scenario")
def data_warehouse_scenario():
    """Scenariusz hurtowni danych - ETL i raportowanie"""
    print("\n=== 🏢 Scenariusz Data Warehouse ===")
    
    db = get_db_manager()
    logger = get_db_logger()
    
    # Sprawdź czy mamy dane źródłowe
    source_databases = ["ecommerce_db", "monitoring_db"]
    available_dbs = db.list_databases()
    
    missing_dbs = [db_name for db_name in source_databases if db_name not in available_dbs]
    if missing_dbs:
        print(f"  ❌ Brakuje baz źródłowych: {missing_dbs}")
        print("  Uruchom najpierw ecommerce_scenario() i monitoring_scenario()")
        return
    
    # Utwórz bazę hurtowni danych
    if not db.create_database("datawarehouse_db"):
        raise LuxDBError("Nie udało się utworzyć bazy hurtowni danych")
    
    # 1. Proces ETL - Extract, Transform, Load
    print("1. 🔄 Proces ETL")
    
    # Extract - wyciągnij dane z różnych źródeł
    print("  📤 Extract - pobieranie danych źródłowych")
    
    # Dane sprzedażowe z e-commerce
    sales_extract_query = """
    SELECT 
        o.order_date,
        o.total_amount,
        o.status as order_status,
        c.company,
        CASE 
            WHEN c.company IS NOT NULL THEN 'B2B'
            ELSE 'B2C'
        END as customer_type,
        p.category as product_category
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    WHERE o.status IN ('confirmed', 'shipped', 'delivered')
    """
    
    try:
        sales_data = db.execute_raw_sql("ecommerce_db", sales_extract_query)
        print(f"    ✅ Wyodrębniono {len(sales_data)} rekordów sprzedażowych")
    except Exception as e:
        print(f"    ❌ Błąd ekstrakcji sprzedaży: {e}")
        sales_data = []
    
    # Dane systemowe z monitoringu
    monitoring_extract_query = """
    SELECT 
        DATE(created_at) as alert_date,
        alert_type,
        severity,
        source_system,
        CASE WHEN is_resolved = 1 THEN 'resolved' ELSE 'open' END as status
    FROM system_alerts
    WHERE created_at >= datetime('now', '-30 days')
    """
    
    try:
        monitoring_data = db.execute_raw_sql("monitoring_db", monitoring_extract_query)
        print(f"    ✅ Wyodrębniono {len(monitoring_data)} rekordów monitoringu")
    except Exception as e:
        print(f"    ❌ Błąd ekstrakcji monitoringu: {e}")
        monitoring_data = []
    
    # Transform - przetwórz dane
    print("  🔧 Transform - przetwarzanie danych")
    
    if sales_data:
        # Dodaj pola obliczone
        sales_transformed = DataTransformer.add_computed_field(
            sales_data, 
            "revenue_bucket",
            lambda r: "High" if r.get("total_amount", 0) > 500 else "Medium" if r.get("total_amount", 0) > 100 else "Low"
        )
        
        # Normalizuj kategorie
        sales_transformed = DataTransformer.normalize_strings(
            sales_transformed, 
            ["product_category"], 
            lowercase=True
        )
        
        print(f"    ✅ Przetworzono dane sprzedażowe")
    else:
        sales_transformed = []
    
    if monitoring_data:
        # Agreguj alerty według dnia i systemu
        monitoring_aggregated = []
        daily_system_stats = defaultdict(lambda: {"total_alerts": 0, "critical_alerts": 0, "resolved_alerts": 0})
        
        for record in monitoring_data:
            key = (record["alert_date"], record["source_system"])
            daily_system_stats[key]["total_alerts"] += 1
            
            if record["severity"] == "critical":
                daily_system_stats[key]["critical_alerts"] += 1
            
            if record["status"] == "resolved":
                daily_system_stats[key]["resolved_alerts"] += 1
        
        for (date, system), stats in daily_system_stats.items():
            monitoring_aggregated.append({
                "alert_date": date,
                "source_system": system,
                "total_alerts": stats["total_alerts"],
                "critical_alerts": stats["critical_alerts"],
                "resolved_alerts": stats["resolved_alerts"],
                "resolution_rate": (stats["resolved_alerts"] / stats["total_alerts"] * 100) if stats["total_alerts"] > 0 else 0
            })
        
        print(f"    ✅ Zagregowano dane monitoringu do {len(monitoring_aggregated)} rekordów")
    else:
        monitoring_aggregated = []
    
    # Load - załaduj do hurtowni (symulacja poprzez eksport)
    print("  📥 Load - ładowanie do hurtowni danych")
    
    exporter = DataExporter()
    
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Zapisz przetworzone dane
            if sales_transformed:
                sales_file = os.path.join(temp_dir, "sales_mart.json")
                exporter.export_to_json(sales_transformed, sales_file)
                print(f"    ✅ Załadowano dane sprzedażowe")
            
            if monitoring_aggregated:
                monitoring_file = os.path.join(temp_dir, "monitoring_mart.json")
                exporter.export_to_json(monitoring_aggregated, monitoring_file)
                print(f"    ✅ Załadowano dane monitoringu")
    
    except Exception as e:
        print(f"    ❌ Błąd ładowania danych: {e}")
    
    # 2. Analiza wielowymiarowa
    print("\n2. 📊 Analiza wielowymiarowa")
    
    if sales_transformed:
        # Analiza sprzedaży według wymiarów
        print("  Analiza sprzedaży:")
        
        # Według typu klienta
        customer_type_analysis = DataAggregator.summarize_by_group(
            sales_transformed, 
            "customer_type", 
            "total_amount",
            ["count", "sum", "avg"]
        )
        
        print(f"    {'Typ klienta':<10} {'Zamówienia':<10} {'Przychód':<12} {'Śr. wartość'}")
        print(f"    {'-'*10} {'-'*10} {'-'*12} {'-'*11}")
        
        for customer_type, stats in customer_type_analysis.items():
            print(f"    {customer_type:<10} {stats['count']:<10} {stats['sum']:<12.2f} {stats['avg']:<11.2f}")
        
        # Według kategorii produktów
        category_revenue = DataAggregator.count_by_field(sales_transformed, "product_category")
        print(f"\n    Top kategorie produktów:")
        for category, count in sorted(category_revenue.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"      {category}: {count} zamówień")
    
    # 3. Raport wykonawczy
    print("\n3. 📋 Raport wykonawczy - Dashboard")
    
    print("  KPI - Kluczowe wskaźniki wydajności:")
    
    # Oblicz KPI sprzedażowe
    if sales_transformed:
        total_revenue = sum(float(record.get("total_amount", 0)) for record in sales_transformed)
        total_orders = len(sales_transformed)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        print(f"    💰 Łączny przychód: {total_revenue:,.2f} PLN")
        print(f"    🛒 Liczba zamówień: {total_orders:,}")
        print(f"    📊 Średnia wartość zamówienia: {avg_order_value:.2f} PLN")
        
        # Analiza rentowności
        high_value_orders = len(DataFilter.filter_by_field(sales_transformed, "revenue_bucket", "High"))
        high_value_percentage = (high_value_orders / total_orders * 100) if total_orders > 0 else 0
        print(f"    🎯 Zamówienia wysokiej wartości: {high_value_percentage:.1f}%")
    
    # Oblicz KPI systemowe
    if monitoring_aggregated:
        total_alerts = sum(record.get("total_alerts", 0) for record in monitoring_aggregated)
        total_critical = sum(record.get("critical_alerts", 0) for record in monitoring_aggregated)
        
        if total_alerts > 0:
            critical_percentage = (total_critical / total_alerts * 100)
            avg_resolution_rate = sum(record.get("resolution_rate", 0) for record in monitoring_aggregated) / len(monitoring_aggregated)
            
            print(f"    🚨 Łączna liczba alertów: {total_alerts:,}")
            print(f"    🔴 Alerty krytyczne: {critical_percentage:.1f}%")
            print(f"    ✅ Średni wskaźnik rozwiązań: {avg_resolution_rate:.1f}%")
    
    # 4. Automatyzacja raportowania
    print("\n4. 🤖 Automatyzacja raportowania")
    
    # Symulacja automatycznego harmonogramu
    automation_schedule = [
        ("Raport sprzedażowy", "codziennie 08:00", "kierownictwo sprzedaży"),
        ("Analiza systemowa", "codziennie 06:00", "zespół IT"),
        ("Dashboard wykonawczy", "poniedziałek 09:00", "zarząd"),
        ("Raport klientów", "pierwszy dzień miesiąca", "zespół CRM"),
        ("Analiza rentowności", "co tydzień", "kontroling")
    ]
    
    print("  📅 Harmonogram automatycznych raportów:")
    for report_name, schedule, recipients in automation_schedule:
        print(f"    {report_name}: {schedule} → {recipients}")
    
    logger.log_database_operation("data_warehouse_etl", "datawarehouse_db", True, 
                                f"Processed {len(sales_data)} sales + {len(monitoring_data)} monitoring records")

def main():
    """Główna funkcja demonstracyjna"""
    print("🚀 LuxDB - Rzeczywiste scenariusze biznesowe")
    print("=" * 60)
    
    try:
        # Uruchom wszystkie scenariusze
        ecommerce_scenario()
        crm_scenario()
        monitoring_scenario()
        data_warehouse_scenario()
        
        print("\n✅ Wszystkie scenariusze biznesowe zakończone pomyślnie!")
        print("\n📊 Podsumowanie:")
        print("  🛒 E-commerce: Zarządzanie produktami, zamówieniami i analizą sprzedaży")
        print("  👔 CRM: Segmentacja klientów i analiza retencji")
        print("  🔍 Monitoring: Alerty systemowe i analiza trendów")
        print("  🏢 Data Warehouse: Proces ETL i raportowanie wielowymiarowe")
        
    except Exception as e:
        print(f"\n❌ Błąd w scenariuszach: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Zamknij połączenia
        db = get_db_manager()
        db.close_all_connections()
        print("\n🔒 Zamknięto wszystkie połączenia")

if __name__ == "__main__":
    main()
