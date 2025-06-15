
"""
Przykłady użycia biblioteki LuxErrors
"""

from luxerrors import (
    LuxError, ValidationError, ConnectionError, DataNotFoundError,
    handle_errors, safe_execute, ErrorCollector,
    get_error_logger, log_error_event
)

def example_basic_usage():
    """Podstawowe użycie LuxErrors"""
    print("=== Podstawowe użycie LuxErrors ===")
    
    try:
        # Symulacja błędu walidacji
        raise ValidationError(
            "Invalid user data", 
            field_errors={"email": "Invalid email format", "age": "Must be positive"},
            context={"user_id": 123}
        )
    except LuxError as e:
        print(f"Caught LuxError: {e}")
        print("Detailed info:", e.get_detailed_info())

def example_error_decorator():
    """Przykład użycia dekoratora handle_errors"""
    print("\n=== Dekorator handle_errors ===")
    
    @handle_errors("user_creation", return_result=True)
    def create_user(username: str, email: str):
        if not username:
            raise ValidationError("Username is required")
        if "@" not in email:
            raise ValidationError("Invalid email format")
        return {"id": 1, "username": username, "email": email}
    
    # Test sukcesu
    success, result = create_user("john", "john@example.com")
    print(f"Success: {success}, Result: {result}")
    
    # Test błędu
    success, error_info = create_user("", "invalid-email")
    print(f"Success: {success}, Error: {error_info['code_name']}")

def example_error_collector():
    """Przykład użycia ErrorCollector dla operacji batch"""
    print("\n=== ErrorCollector dla operacji batch ===")
    
    collector = ErrorCollector("batch_user_import")
    
    users_data = [
        {"username": "john", "email": "john@example.com"},
        {"username": "", "email": "jane@example.com"},  # Błąd
        {"username": "bob", "email": "invalid-email"},  # Błąd
        {"username": "alice", "email": "alice@example.com"}
    ]
    
    for user_data in users_data:
        collector.increment_total()
        try:
            # Symulacja walidacji
            if not user_data["username"]:
                raise ValidationError("Username is required")
            if "@" not in user_data["email"]:
                raise ValidationError("Invalid email format")
            
            # Symulacja sukcesu
            collector.add_success()
            print(f"✓ User {user_data['username']} created successfully")
            
        except Exception as e:
            collector.add_error(e, {"user_data": user_data})
            print(f"✗ Failed to create user: {e}")
    
    # Podsumowanie
    summary = collector.get_summary()
    print(f"\nBatch summary:")
    print(f"Total: {summary['total_operations']}")
    print(f"Success: {summary['successful_operations']}")
    print(f"Failed: {summary['failed_operations']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    print(f"Most common errors: {collector.get_most_common_errors()}")

def example_logging_integration():
    """Przykład integracji z systemem logowania"""
    print("\n=== Integracja z logowaniem ===")
    
    logger = get_error_logger()
    
    try:
        # Symulacja operacji z błędem
        raise ConnectionError("Failed to connect to database", service_name="postgres")
    except LuxError as e:
        logger.log_error(e, {"operation": "database_connect", "retry_count": 3})
    
    # Logowanie sukcesu operacji
    logger.log_operation_success("user_export", duration=1.234, 
                                context={"exported_users": 150})

def example_safe_execute():
    """Przykład bezpiecznego wykonywania funkcji"""
    print("\n=== Bezpieczne wykonywanie funkcji ===")
    
    def risky_operation():
        import random
        if random.choice([True, False]):
            raise ValueError("Random error occurred")
        return "Success!"
    
    # Bezpieczne wykonanie z wartością domyślną
    result = safe_execute(risky_operation, default_return="Operation failed")
    print(f"Safe execute result: {result}")

def example_custom_errors():
    """Przykład tworzenia niestandardowych błędów"""
    print("\n=== Niestandardowe błędy ===")
    
    class PaymentError(LuxError):
        """Błąd płatności"""
        def __init__(self, message: str, amount: float, payment_method: str):
            from luxerrors.error_codes import LuxErrorCode
            context = {
                "amount": amount,
                "payment_method": payment_method,
                "currency": "PLN"
            }
            super().__init__(message, LuxErrorCode.EXTERNAL_SERVICE_ERROR, context)
    
    try:
        raise PaymentError("Payment processing failed", 99.99, "credit_card")
    except PaymentError as e:
        print(f"Payment error: {e}")
        print("Context:", e.context)

if __name__ == "__main__":
    example_basic_usage()
    example_error_decorator()
    example_error_collector()
    example_logging_integration()
    example_safe_execute()
    example_custom_errors()
