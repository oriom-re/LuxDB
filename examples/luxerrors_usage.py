
#!/usr/bin/env python3
"""
Przykład użycia biblioteki LuxErrors w projekcie zewnętrznym
"""

from luxerrors import (
    LuxError, ValidationError, ConnectionError, DataNotFoundError,
    handle_errors, safe_execute, ErrorCollector,
    get_error_logger, log_error_event,
    LuxErrorCode, ErrorSeverity
)

class APIService:
    """Przykładowa klasa serwisu API używająca LuxErrors"""
    
    def __init__(self):
        self.logger = get_error_logger()
        self.users = {}  # Prosta baza danych w pamięci
    
    @handle_errors("create_user", return_result=True)
    def create_user(self, user_data: dict):
        """Tworzy użytkownika z obsługą błędów"""
        # Walidacja danych
        required_fields = ["username", "email", "password"]
        missing = [f for f in required_fields if f not in user_data]
        if missing:
            raise ValidationError(
                f"Missing required fields: {missing}",
                field_errors={f: "Field is required" for f in missing},
                context={"operation": "user_creation"}
            )
        
        # Sprawdź duplikaty
        username = user_data["username"]
        if username in self.users:
            raise ValidationError(
                f"User {username} already exists",
                field_errors={"username": "Username must be unique"},
                context={"existing_user": username}
            )
        
        # Symulacja błędu połączenia (losowo)
        import random
        if random.random() < 0.2:  # 20% szans na błąd
            raise ConnectionError(
                "Database connection failed",
                service_name="user_database",
                context={"retry_count": 0}
            )
        
        # Utwórz użytkownika
        user_id = len(self.users) + 1
        self.users[username] = {
            "id": user_id,
            "username": username,
            "email": user_data["email"],
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        return self.users[username]
    
    @handle_errors("get_user")
    def get_user(self, username: str):
        """Pobiera użytkownika"""
        if username not in self.users:
            raise DataNotFoundError(
                f"User not found: {username}",
                resource_type="user",
                resource_id=username
            )
        
        return self.users[username]
    
    def batch_create_users(self, users_data: list):
        """Tworzy użytkowników w trybie batch z kolekcją błędów"""
        collector = ErrorCollector("batch_user_creation")
        results = []
        
        for user_data in users_data:
            collector.increment_total()
            
            success, result = self.create_user(user_data)
            
            if success:
                collector.add_success()
                results.append(result)
                self.logger.log_operation_success(
                    "create_user",
                    context={"username": user_data.get("username")}
                )
            else:
                collector.add_error(
                    Exception(f"Failed to create user: {result}"),
                    context={"user_data": user_data}
                )
        
        return {
            "results": results,
            "summary": collector.get_summary(),
            "error_codes": collector.get_error_codes_summary()
        }

def demonstrate_basic_error_handling():
    """Demonstracja podstawowej obsługi błędów"""
    print("=== Podstawowa obsługa błędów ===")
    
    service = APIService()
    
    # Test sukcesu
    print("Tworzenie użytkownika - sukces:")
    success, result = service.create_user({
        "username": "john_doe",
        "email": "john@example.com",
        "password": "secret123"
    })
    print(f"Success: {success}")
    if success:
        print(f"Created user: {result['username']}")
    
    # Test błędu walidacji
    print("\nTworzenie użytkownika - błąd walidacji:")
    success, error_info = service.create_user({
        "username": "jane_doe"
        # Brak email i password
    })
    print(f"Success: {success}")
    if not success:
        print(f"Error: {error_info['error']['code_name']}")
        print(f"Message: {error_info['error']['message']}")

def demonstrate_batch_operations():
    """Demonstracja operacji batch z kolekcją błędów"""
    print("\n=== Operacje batch ===")
    
    service = APIService()
    
    users_data = [
        {"username": "user1", "email": "user1@example.com", "password": "pass1"},
        {"username": "user2", "email": "user2@example.com"},  # Brak password
        {"username": "user3", "email": "user3@example.com", "password": "pass3"},
        {"email": "user4@example.com", "password": "pass4"},  # Brak username
        {"username": "user5", "email": "user5@example.com", "password": "pass5"},
    ]
    
    batch_result = service.batch_create_users(users_data)
    
    print(f"Utworzono {len(batch_result['results'])} użytkowników")
    
    summary = batch_result['summary']
    print(f"Statystyki:")
    print(f"  Total: {summary['total_operations']}")
    print(f"  Success: {summary['successful_operations']}")
    print(f"  Failed: {summary['failed_operations']}")
    print(f"  Success rate: {summary['success_rate']:.1f}%")
    
    print(f"Najczęstsze błędy: {batch_result['error_codes']}")

def demonstrate_custom_errors():
    """Demonstracja niestandardowych błędów"""
    print("\n=== Niestandardowe błędy ===")
    
    class PaymentError(LuxError):
        """Niestandardowy błąd płatności"""
        def __init__(self, message: str, amount: float, currency: str = "PLN"):
            context = {"amount": amount, "currency": currency}
            super().__init__(message, LuxErrorCode.EXTERNAL_SERVICE_ERROR, context)
    
    class PaymentService:
        @handle_errors("process_payment", return_result=True)
        def process_payment(self, amount: float, card_number: str):
            if amount <= 0:
                raise ValidationError("Amount must be positive")
            
            if len(card_number) != 16:
                raise ValidationError("Invalid card number format")
            
            # Symulacja błędu płatności
            if card_number.startswith("4000"):
                raise PaymentError(f"Payment declined for amount {amount}", amount)
            
            return {"transaction_id": "TXN123", "status": "completed", "amount": amount}
    
    payment_service = PaymentService()
    
    # Test sukcesu
    success, result = payment_service.process_payment(99.99, "4111111111111111")
    print(f"Payment success: {success}")
    
    # Test błędu
    success, error_info = payment_service.process_payment(99.99, "4000000000000000")
    print(f"Payment failed: {not success}")
    if not success:
        print(f"Error context: {error_info['error'].get('context', {})}")

def demonstrate_safe_operations():
    """Demonstracja bezpiecznych operacji"""
    print("\n=== Bezpieczne operacje ===")
    
    def risky_file_operation():
        # Symulacja operacji mogącej się nie powieść
        import random
        if random.random() < 0.5:
            raise FileNotFoundError("File not found")
        return "File content loaded successfully"
    
    # Bezpieczne wykonanie z wartością domyślną
    result = safe_execute(
        risky_file_operation,
        default_return="Default content",
        log_errors=True
    )
    print(f"Safe operation result: {result}")
    
    # Bezpieczne wykonanie z lambda
    result = safe_execute(
        lambda: 10 / 0,  # Błąd dzielenia przez zero
        default_return=0
    )
    print(f"Safe division result: {result}")

if __name__ == "__main__":
    print("🔧 LuxErrors - Demonstracja użycia w projekcie zewnętrznym")
    print("=" * 60)
    
    demonstrate_basic_error_handling()
    demonstrate_batch_operations()
    demonstrate_custom_errors()
    demonstrate_safe_operations()
    
    print("\n✅ Demonstracja zakończona!")
    print("\nLuxErrors zapewnia:")
    print("- Ustandaryzowane kody błędów")
    print("- Kontekstowe informacje o błędach")
    print("- Automatyczną detekcję typów błędów")
    print("- Integrację z systemem logowania")
    print("- Narzędzia do operacji batch")
    print("- Łatwą obsługę przez dekoratory")
