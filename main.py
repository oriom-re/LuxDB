
"""
System Asty - Główny plik aplikacji
Demonstracja użycia zaawansowanego menedżera baz danych SQLAlchemy
"""

import sys
import os

# Dodaj folder managers do ścieżki
sys.path.append(os.path.join(os.path.dirname(__file__), 'managers'))

from db_manager import get_db_manager
from db_config import DEFAULT_CONFIGS, SYSTEM_MODELS
from db_examples import run_all_examples

def main():
    """Główna funkcja aplikacji"""
    print("🚀 System Asty - Zaawansowany menedżer baz danych SQLAlchemy")
    print("=" * 60)
    
    try:
        # Inicjalizuj menedżer baz danych
        db_manager = get_db_manager()
        
        print("✅ Menedżer baz danych SQLAlchemy zainicjalizowany")
        print(f"📁 Katalog baz danych: {db_manager.db_directory}")
        
        # Lista dostępnych baz
        databases = db_manager.list_databases()
        print(f"📊 Dostępne bazy danych: {len(databases)}")
        for db_name in databases:
            version = db_manager.get_database_version(db_name)
            print(f"   - {db_name} (wersja {version})")
        
        print("\n" + "=" * 60)
        print("🧪 Uruchamianie przykładów użycia SQLAlchemy...")
        print("=" * 60)
        
        # Uruchom przykłady
        run_all_examples()
        
        print("\n" + "=" * 60)
        print("✅ Wszystkie przykłady SQLAlchemy wykonane pomyślnie!")
        print("📋 Funkcje dostępne w systemie:")
        print("   • Modele ORM SQLAlchemy z relacjami")
        print("   • Automatyczne tworzenie tabel z modeli")
        print("   • Connection pooling SQLAlchemy")
        print("   • QueryBuilder oparty na SQLAlchemy")
        print("   • Wersjonowanie i migracje schematów")
        print("   • Synchronizacja między bazami")
        print("   • Eksport/import danych (JSON)")
        print("   • Optymalizacja i transakcje")
        print("   • Wsparcie dla PostgreSQL/MySQL")
        print("   • Type hints i bezpieczeństwo typów")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Przygotuj system do zamknięcia
        try:
            db_manager = get_db_manager()
            db_manager.close_all_connections()
            print("🔒 Połączenia SQLAlchemy zamknięte")
        except:
            pass

if __name__ == "__main__":
    main()
