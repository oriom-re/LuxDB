
"""
Przykład użycia systemu obsługi błędów LuxDB
"""

from luxdb import get_db_manager
from luxdb.models import User
from luxdb.utils import LuxDBErrorCode, get_error_info

def test_error_handling():
    """Test nowego systemu obsługi błędów"""
    print("=== Test systemu obsługi błędów LuxDB ===")
    
    db = get_db_manager()
    
    # Utwórz bazę testową
    db.create_database("test_errors")
    
    # Test 1: Pomyślne wstawienie
    print("\n1. Test pomyślnego wstawienia:")
    user_data = {
        "username": "test_user_unique",
        "email": "unique@example.com",
        "password_hash": "hashed_password",
        "is_active": True
    }
    
    result = db.insert_data("test_errors", User, user_data)
    print(f"Wynik: {result}")
    
    if result["success"]:
        print(f"✅ Sukces! ID rekordu: {result['data']['record_id']}")
    
    # Test 2: Duplikat username (naruszenie unikalności)
    print("\n2. Test duplikatu username:")
    duplicate_data = {
        "username": "test_user_unique",  # Ten sam username
        "email": "different@example.com",
        "password_hash": "hashed_password",
        "is_active": True
    }
    
    result = db.insert_data("test_errors", User, duplicate_data)
    print(f"Wynik: {result}")
    
    if not result["success"]:
        error_info = result["error"]
        print(f"❌ Błąd wykryty:")
        print(f"   Kod: {error_info.get('code')} ({error_info.get('code_name')})")
        print(f"   Wiadomość: {error_info.get('message')}")
        print(f"   Opis: {error_info.get('description')}")
        print(f"   Wskazówka: {error_info.get('recovery_hint')}")
        print(f"   Tabela: {error_info.get('table_name', 'N/A')}")
        print(f"   Kolumna: {error_info.get('column_name', 'N/A')}")
    
    # Test 3: Batch insert z błędami
    print("\n3. Test batch insert z mieszanymi wynikami:")
    batch_data = [
        {
            "username": "user1",
            "email": "user1@example.com",
            "password_hash": "hash1",
            "is_active": True
        },
        {
            "username": "test_user_unique",  # Duplikat!
            "email": "duplicate@example.com",
            "password_hash": "hash2",
            "is_active": True
        },
        {
            "username": "user2",
            "email": "user2@example.com",
            "password_hash": "hash3",
            "is_active": True
        },
        {
            "username": "user1",  # Drugi duplikat!
            "email": "another@example.com",
            "password_hash": "hash4",
            "is_active": True
        }
    ]
    
    result = db.insert_batch("test_errors", User, batch_data)
    print(f"Wynik batch insert: {result}")
    
    if "data" in result:
        data = result["data"]
        print(f"📊 Podsumowanie batch insert:")
        print(f"   Łącznie rekordów: {data.get('total_count', 0)}")
        print(f"   Wstawione pomyślnie: {data.get('inserted_count', 0)}")
        print(f"   Niepowodzenia: {data.get('failed_count', 0)}")
        print(f"   Kody błędów: {data.get('error_codes', {})}")
    
    # Test 4: Informacje o kodach błędów
    print("\n4. Dostępne kody błędów:")
    common_errors = [
        LuxDBErrorCode.UNIQUE_CONSTRAINT_VIOLATION,
        LuxDBErrorCode.DUPLICATE_KEY,
        LuxDBErrorCode.NULL_CONSTRAINT_VIOLATION,
        LuxDBErrorCode.FOREIGN_KEY_VIOLATION
    ]
    
    for error_code in common_errors:
        info = get_error_info(error_code)
        print(f"   {error_code.name} ({error_code.value}): {info.message}")
        print(f"      💡 {info.recovery_hint}")
    
    print("\n✨ Test systemu obsługi błędów zakończony!")

if __name__ == "__main__":
    test_error_handling()
