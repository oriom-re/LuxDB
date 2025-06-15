
#!/usr/bin/env python3
"""
Test wyświetlania lokalizacji błędów w ErrorInfo
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from luxerrors import LuxError, ValidationError, UnifiedErrorHandler
from luxerrors.error_codes import LuxErrorCode, ErrorInfo
import json

def test_function_with_error():
    """Funkcja testowa która generuje błąd"""
    # Ta linia powinna być pokazana w informacjach o błędzie
    raise ValidationError("Test błędu walidacji", {"field": "username"})

def test_direct_error_info():
    """Test bezpośredniego tworzenia ErrorInfo"""
    print("=== Test bezpośredniego ErrorInfo ===")
    
    # Ta linia zostanie przechwycona jako miejsce błędu
    error_info = ErrorInfo(
        LuxErrorCode.VALIDATION_ERROR,
        "Test message",
        "Test description"
    )
    
    print("Informacje o błędzie:")
    print(f"Lokalizacja: {error_info.get_error_location_info()}")
    print(f"Link: {error_info.get_error_location_link()}")
    print(f"Pełne dane: {json.dumps(error_info.to_dict(), indent=2)}")

def test_lux_error_location():
    """Test wyświetlania lokalizacji w LuxError"""
    print("\n=== Test LuxError z lokalizacją ===")
    
    try:
        # Ta linia zostanie przechwycona
        test_function_with_error()
    except LuxError as e:
        print(f"Błąd: {e}")
        print(f"Lokalizacja: {e.error_info.get_error_location_info()}")
        print(f"Link: {e.error_info.get_error_location_link()}")
        
        detailed = e.get_detailed_info()
        if 'location' in detailed:
            print("Szczegóły lokalizacji:")
            location = detailed['location']
            print(f"  Plik: {location['file']}")
            print(f"  Linia: {location['line']}")
            print(f"  Funkcja: {location['function']}")
            print(f"  Kod: {location['code']}")
            print(f"  Link: {location['link']}")

def test_unified_handler_location():
    """Test UnifiedErrorHandler z lokalizacją"""
    print("\n=== Test UnifiedErrorHandler z lokalizacją ===")
    
    # Ta linia zostanie przechwycona jako miejsce błędu
    error = UnifiedErrorHandler.validation_error(
        "Nieprawidłowe dane użytkownika",
        {"username": "Za krótka nazwa", "email": "Nieprawidłowy format"}
    )
    
    print(f"Błąd: {error}")
    print(f"Lokalizacja: {error.error_info.get_error_location_info()}")
    
    detailed = error.get_detailed_info()
    if 'location' in detailed:
        print(f"Link do kodu: {detailed['location']['link']}")

def test_nested_function_calls():
    """Test z zagnieżdżonymi wywołaniami funkcji"""
    print("\n=== Test zagnieżdżonych wywołań ===")
    
    def level_3():
        # Ta linia powinna być wskazana jako źródło błędu
        raise UnifiedErrorHandler.data_not_found_error(
            "Użytkownik nie znaleziony", 
            resource_type="User", 
            resource_id="123"
        )
    
    def level_2():
        level_3()
    
    def level_1():
        level_2()
    
    try:
        level_1()
    except LuxError as e:
        print(f"Błąd: {e}")
        location_info = e.error_info.get_error_location_info()
        print(f"Prawdziwa lokalizacja błędu: {location_info}")

if __name__ == "__main__":
    print("🔍 Test wyświetlania lokalizacji błędów LuxErrors")
    print("=" * 60)
    
    test_direct_error_info()
    test_lux_error_location()
    test_unified_handler_location()
    test_nested_function_calls()
    
    print("\n✅ Testy zakończone!")
