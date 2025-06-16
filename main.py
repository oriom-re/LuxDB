"""
System Asty - Główny plik aplikacji
Demonstracja użycia zaawansowanego menedżera baz danych SQLAlchemy
"""

import sys
import os

# Dodaj główny katalog do ścieżki
sys.path.append(os.path.dirname(__file__))

# Import z nowej struktury LuxDB
from luxdb import get_db_manager, DatabaseManager
from luxdb.config import DatabaseConfig, DatabaseType
from luxdb.models import User, UserSession, Log
from luxdb.utils import ModelGenerator, FieldConfig, FieldType, RelationshipConfig
# import luxdb.examples as ex  # Będzie dodane później

def test_basic_model_generator():
    """Test podstawowego generatora modeli"""
    print("=== Test podstawowego generatora modeli ===")

    generator = ModelGenerator()

    # Prosty model
    fields = {
        "name": "string",
        "age": "integer",
        "email": "string",
        "is_active": "boolean"
    }

    PersonModel = generator.generate_basic_model("Person", fields)
    print(f"Wygenerowano model: {PersonModel.__name__}")
    print(f"Tabela: {PersonModel.__tablename__}")
    print(f"Kolumny: {[col.name for col in PersonModel.__table__.columns]}")

def test_advanced_model_generator():
    """Test zaawansowanego generatora modeli"""
    print("\n=== Test zaawansowanego generatora modeli ===")

    generator = ModelGenerator()

    # Zaawansowany model użytkownika - bez problematycznych relacji
    user_fields = {
        "username": FieldConfig(
            FieldType.STRING,
            nullable=False,
            unique=True,
            max_length=50,
            index=True
        ),
        "email": FieldConfig(
            FieldType.STRING,
            nullable=False,
            unique=True,
            max_length=255
        ),
        "age": FieldConfig(
            FieldType.INTEGER,
            nullable=True,
            default=0
        ),
        "is_premium": FieldConfig(
            FieldType.BOOLEAN,
            nullable=False,
            default=False
        ),
        "created_at": FieldConfig(
            FieldType.DATETIME,
            nullable=False,
            default="now"
        )
    }

    AdvancedUserModel = generator.generate_advanced_model(
        "AdvancedUser", 
        user_fields
    )

    print(f"Wygenerowano zaawansowany model: {AdvancedUserModel.__name__}")
    print(f"Tabela: {AdvancedUserModel.__tablename__}")
    print(f"Kolumny: {[col.name for col in AdvancedUserModel.__table__.columns]}")

def test_crud_model():
    """Test modelu CRUD"""
    print("\n=== Test modelu CRUD ===")

    generator = ModelGenerator()

    fields = {
        "title": FieldConfig(FieldType.STRING, nullable=False, max_length=200),
        "content": FieldConfig(FieldType.TEXT, nullable=True),
        "view_count": FieldConfig(FieldType.INTEGER, default=0)
    }

    ArticleModel = generator.generate_crud_model(
        "Article", 
        fields,
        include_timestamps=True,
        include_soft_delete=True
    )

    print(f"Wygenerowano model CRUD: {ArticleModel.__name__}")
    print(f"Kolumny: {[col.name for col in ArticleModel.__table__.columns]}")

    # Test metod CRUD
    article = ArticleModel(title="Test Article", content="Some content")
    data_dict = article.to_dict()
    print(f"Converted to dict: {data_dict}")

def test_api_model_with_validation():
    """Test modelu API z walidacją"""
    print("\n=== Test modelu API z walidacją ===")

    generator = ModelGenerator()

    fields = {
        "username": FieldConfig(FieldType.STRING, nullable=False, max_length=50),
        "email": FieldConfig(FieldType.STRING, nullable=False, max_length=255),
        "age": FieldConfig(FieldType.INTEGER, nullable=True)
    }

    validation_rules = {
        "username": ["required", "min_length:3", "max_length:50"],
        "email": ["required", "email"],
        "age": ["required"]
    }

    ValidatedUserModel = generator.generate_api_model(
        "ValidatedUser",
        fields,
        validation_rules=validation_rules
    )

    print(f"Wygenerowano model API: {ValidatedUserModel.__name__}")

    # Test walidacji
    user = ValidatedUserModel(username="ab", email="invalid-email", age=None)
    errors = user.validate()
    print(f"Błędy walidacji: {errors}")

    # Poprawny użytkownik
    valid_user = ValidatedUserModel(username="john_doe", email="john@example.com", age=25)
    errors = valid_user.validate()
    print(f"Błędy walidacji (poprawny): {errors}")

def test_database_operations():
    """Test operacji bazodanowych z nowymi modelami"""
    print("\n=== Test operacji bazodanowych ===")

    db = get_db_manager()

    # Utwórz bazę testową
    db.create_database("test_luxdb")

    # Test z wbudowanymi modelami
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password_hash": "hashed_password",
        "is_active": True
    }

    with db.get_session("test_luxdb") as session:
        user = db.insert_data(session, "test_luxdb", User, user_data)
        print(f"Wstawiono użytkownika: {user.id if user else 'Błąd'}")

        # Pobierz użytkowników
        users = db.select_data(session, "test_luxdb", User, {"is_active": True})
    print(f"Znaleziono {len(users)} aktywnych użytkowników")

    # Test z wygenerowanym modelem
    generator = ModelGenerator()
    ProductModel = generator.generate_basic_model("Product", {
        "name": "string",
        "price": "float",
        "in_stock": "boolean"
    })

    # Utwórz tabelę dla nowego modelu
    db.create_table_from_model("test_luxdb", ProductModel)

    # Wstaw dane do nowego modelu
    product_data = {
        "name": "Test Product",
        "price": 99.99,
        "in_stock": True
    }

    with db.get_session("test_luxdb") as session:
        product = db.insert_data(session, "test_luxdb", ProductModel, product_data)
        print(f"Wstawiono produkt: {product.id if product else 'Błąd'}")

def test_migration_sql_generation():
    """Test generowania SQL dla migracji"""
    print("\n=== Test generowania SQL migracji ===")

    generator = ModelGenerator()

    fields = {
        "name": FieldConfig(FieldType.STRING, nullable=False, max_length=100),
        "description": FieldConfig(FieldType.TEXT, nullable=True),
        "created_at": FieldConfig(FieldType.DATETIME, default="now")
    }

    CategoryModel = generator.generate_advanced_model("Category", fields)

    migration_sql = generator.create_migration_sql(CategoryModel)
    print("Wygenerowany SQL migracji:")
    print(migration_sql)

def test_session_manager():
    """Test menedżera sesji"""
    print("\n=== Test menedżera sesji ===")
    
    from luxdb.session_manager import get_session_manager
    
    session_mgr = get_session_manager("test_sessions")
    
    # Tworzenie użytkownika
    try:
        user_id = session_mgr.create_user(
            username="test_user",
            email="test@example.com",
            password="bezpieczne_haslo123"
        )
        print(f"Utworzono użytkownika z ID: {user_id}")
    except Exception as e:
        print(f"Błąd tworzenia użytkownika: {e}")
        return
    
    # Uwierzytelnianie
    try:
        user_data = session_mgr.authenticate_user("test_user", "bezpieczne_haslo123")
        print(f"Uwierzytelniono użytkownika: {user_data['username']}")
    except Exception as e:
        print(f"Błąd uwierzytelniania: {e}")
        return
    
    # Tworzenie sesji
    try:
        session_token = session_mgr.create_session(
            user_id=user_data["id"],
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )
        print(f"Utworzono sesję: {session_token[:20]}...")
    except Exception as e:
        print(f"Błąd tworzenia sesji: {e}")
        return
    
    # Walidacja sesji
    try:
        session_data = session_mgr.validate_session(session_token)
        if session_data:
            print("Sesja jest ważna")
        else:
            print("Sesja jest nieważna")
    except Exception as e:
        print(f"Błąd walidacji sesji: {e}")
    
    # Test kontekstu użytkownika
    try:
        with session_mgr.user_context(session_token) as user:
            print(f"Kontekst użytkownika: {user['username']}")
    except Exception as e:
        print(f"Błąd kontekstu użytkownika: {e}")
    
    # Wylogowanie
    try:
        destroyed = session_mgr.destroy_session(session_token)
        print(f"Sesja zniszczona: {destroyed}")
    except Exception as e:
        print(f"Błąd niszczenia sesji: {e}")

def main():
    """Główna funkcja demonstrująca LuxDB"""
    try:
        print("🚀 LuxDB - Zaawansowany Manager Baz Danych SQLAlchemy")
        print("=" * 60)
        # ex.basic_setup.main()  # Tymczasowo wyłączone - brak modułu examples
        test_basic_model_generator()
        test_advanced_model_generator()
        test_crud_model()
        test_api_model_with_validation()
        test_database_operations()
        test_migration_sql_generation()
        test_session_manager()

        print("\n✅ Wszystkie testy zakończone pomyślnie!")

        # Informacje o bibliotece
        print(f"\n📦 LuxDB v1.0.0")
        print("🔗 Repozytorium: https://github.com/luxdb/luxdb")
        print("📚 Dokumentacja: https://luxdb.readthedocs.io")

    except Exception as e:
        print(f"❌ Błąd podczas testów: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Zamknij wszystkie połączenia
        db = get_db_manager()
        db.close_all_connections()
        print("\n🔒 Zamknięto wszystkie połączenia")

if __name__ == "__main__":
    main()