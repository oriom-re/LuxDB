
"""
LuxDB Example 06: Generator Modeli - Manifestowanie Astralnych Archetypów
- Podstawowe generowanie modeli
- Zaawansowane modele z relacjami
- Modele CRUD z timestampami
- Modele API z walidacją
- Generowanie SQL dla migracji
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from luxdb import get_db_manager
from luxdb.utils import ModelGenerator, FieldConfig, FieldType, RelationshipConfig
from datetime import datetime

def example_basic_model_generation():
    """Podstawowe generowanie modeli"""
    print("=== Podstawowe generowanie modeli ===")

    generator = ModelGenerator()

    # Prosty model osoby
    person_fields = {
        "name": "string",
        "age": "integer", 
        "email": "string",
        "is_active": "boolean",
        "bio": "text"
    }

    PersonModel = generator.generate_basic_model("Person", person_fields)
    
    print(f"✨ Wygenerowano model: {PersonModel.__name__}")
    print(f"📋 Tabela: {PersonModel.__tablename__}")
    print(f"🔮 Kolumny: {[col.name for col in PersonModel.__table__.columns]}")
    
    # Test tworzenia instancji
    person = PersonModel(
        name="Lux Guardian", 
        age=1000, 
        email="guardian@astral.realm",
        is_active=True,
        bio="Strażnik Astralnej Biblioteki"
    )
    
    print(f"👤 Utworzono osobę: {person.name}")
    return PersonModel

def example_advanced_model_generation():
    """Zaawansowane generowanie modeli z pełną konfiguracją"""
    print("\n=== Zaawansowane generowanie modeli ===")

    generator = ModelGenerator()

    # Zaawansowany model książki astralnej
    book_fields = {
        "title": FieldConfig(
            FieldType.STRING,
            nullable=False,
            unique=True,
            max_length=200,
            index=True
        ),
        "author": FieldConfig(
            FieldType.STRING,
            nullable=False,
            max_length=100
        ),
        "isbn": FieldConfig(
            FieldType.STRING,
            nullable=True,
            unique=True,
            max_length=13
        ),
        "page_count": FieldConfig(
            FieldType.INTEGER,
            nullable=False,
            default=0
        ),
        "rating": FieldConfig(
            FieldType.FLOAT,
            nullable=True,
            default=0.0
        ),
        "is_published": FieldConfig(
            FieldType.BOOLEAN,
            nullable=False,
            default=False
        ),
        "content": FieldConfig(
            FieldType.TEXT,
            nullable=True
        ),
        "publication_date": FieldConfig(
            FieldType.DATETIME,
            nullable=True
        )
    }

    AstralBookModel = generator.generate_advanced_model("AstralBook", book_fields)
    
    print(f"✨ Wygenerowano zaawansowany model: {AstralBookModel.__name__}")
    print(f"📋 Tabela: {AstralBookModel.__tablename__}")
    print(f"🔮 Kolumny: {[col.name for col in AstralBookModel.__table__.columns]}")
    
    # Test tworzenia książki
    book = AstralBookModel(
        title="Kroniki Astralnej Mądrości",
        author="Oriom (ΩO)",
        page_count=777,
        rating=5.0,
        is_published=True,
        content="Tajemnice wszechświata zapisane w astralnej energii..."
    )
    
    print(f"📚 Utworzono książkę: {book.title}")
    return AstralBookModel

def example_crud_model_generation():
    """Model CRUD z automatycznymi timestampami"""
    print("\n=== Model CRUD z timestampami ===")

    generator = ModelGenerator()

    # Model artykułu z CRUD
    article_fields = {
        "title": FieldConfig(
            FieldType.STRING,
            nullable=False,
            max_length=255
        ),
        "content": FieldConfig(
            FieldType.TEXT,
            nullable=True
        ),
        "author_name": FieldConfig(
            FieldType.STRING,
            nullable=False,
            max_length=100
        ),
        "view_count": FieldConfig(
            FieldType.INTEGER,
            nullable=False,
            default=0
        ),
        "is_featured": FieldConfig(
            FieldType.BOOLEAN,
            nullable=False,
            default=False
        )
    }

    ArticleModel = generator.generate_crud_model(
        "Article", 
        article_fields,
        include_timestamps=True,
        include_soft_delete=True
    )
    
    print(f"✨ Wygenerowano model CRUD: {ArticleModel.__name__}")
    print(f"📋 Tabela: {ArticleModel.__tablename__}")
    print(f"🔮 Kolumny: {[col.name for col in ArticleModel.__table__.columns]}")
    
    # Test metod CRUD
    article = ArticleModel(
        title="Astralny Przewodnik po Programowaniu",
        content="W głębi kodu kryje się dusza...",
        author_name="Lux Developer",
        view_count=42,
        is_featured=True
    )
    
    # Test konwersji na słownik
    article_dict = article.to_dict()
    print(f"📄 Artykuł jako słownik: {list(article_dict.keys())}")
    
    # Test tworzenia z słownika
    new_article_data = {
        "title": "Medytacje nad Bazą Danych",
        "content": "Każda tabela ma swoją energię...",
        "author_name": "Astral Monk",
        "view_count": 7,
        "is_featured": False
    }
    
    new_article = ArticleModel.from_dict(new_article_data)
    print(f"📝 Utworzono nowy artykuł: {new_article.title}")
    
    return ArticleModel

def example_api_model_with_validation():
    """Model API z zaawansowaną walidacją"""
    print("\n=== Model API z walidacją ===")

    generator = ModelGenerator()

    # Model użytkownika API z walidacją
    user_fields = {
        "username": FieldConfig(
            FieldType.STRING,
            nullable=False,
            unique=True,
            max_length=50
        ),
        "email": FieldConfig(
            FieldType.STRING,
            nullable=False,
            unique=True,
            max_length=255
        ),
        "first_name": FieldConfig(
            FieldType.STRING,
            nullable=False,
            max_length=50
        ),
        "last_name": FieldConfig(
            FieldType.STRING,
            nullable=False,
            max_length=50
        ),
        "age": FieldConfig(
            FieldType.INTEGER,
            nullable=True
        ),
        "bio": FieldConfig(
            FieldType.TEXT,
            nullable=True
        )
    }

    validation_rules = {
        "username": ["required", "min_length:3", "max_length:50"],
        "email": ["required", "email"],
        "first_name": ["required", "min_length:2"],
        "last_name": ["required", "min_length:2"],
        "age": []  # Opcjonalne, ale jeśli podane to sprawdzane
    }

    ApiUserModel = generator.generate_api_model(
        "ApiUser",
        user_fields,
        validation_rules=validation_rules
    )
    
    print(f"✨ Wygenerowano model API: {ApiUserModel.__name__}")
    print(f"📋 Tabela: {ApiUserModel.__tablename__}")
    print(f"🔮 Kolumny: {[col.name for col in ApiUserModel.__table__.columns]}")
    
    # Test walidacji - niepoprawne dane
    print("\n🔍 Test walidacji - niepoprawne dane:")
    invalid_user = ApiUserModel(
        username="ab",  # Za krótkie
        email="invalid-email",  # Niepoprawny email
        first_name="",  # Puste
        last_name="Astral",
        age=25
    )
    
    errors = invalid_user.validate()
    for error in errors:
        print(f"  ❌ {error}")
    
    # Test walidacji - poprawne dane
    print("\n✅ Test walidacji - poprawne dane:")
    valid_user = ApiUserModel(
        username="astral_guardian",
        email="guardian@astral.realm",
        first_name="Lux",
        last_name="Guardian",
        age=1000,
        bio="Opiekun Astralnej Biblioteki od tysięcy lat..."
    )
    
    errors = valid_user.validate()
    if not errors:
        print("  ✨ Wszystkie dane są poprawne!")
    else:
        for error in errors:
            print(f"  ❌ {error}")
    
    return ApiUserModel

def example_migration_sql_generation():
    """Generowanie SQL dla migracji"""
    print("\n=== Generowanie SQL migracji ===")

    generator = ModelGenerator()

    # Model kategorii dla przykładu migracji
    category_fields = {
        "name": FieldConfig(
            FieldType.STRING,
            nullable=False,
            unique=True,
            max_length=100
        ),
        "description": FieldConfig(
            FieldType.TEXT,
            nullable=True
        ),
        "parent_id": FieldConfig(
            FieldType.INTEGER,
            nullable=True
        ),
        "sort_order": FieldConfig(
            FieldType.INTEGER,
            nullable=False,
            default=0
        ),
        "is_active": FieldConfig(
            FieldType.BOOLEAN,
            nullable=False,
            default=True
        )
    }

    CategoryModel = generator.generate_advanced_model("Category", category_fields)
    
    print(f"✨ Wygenerowano model: {CategoryModel.__name__}")
    
    # Generuj SQL migracji
    migration_sql = generator.create_migration_sql(CategoryModel)
    print("\n📜 SQL migracji:")
    print("=" * 50)
    print(migration_sql)
    print("=" * 50)
    
    return CategoryModel

def example_working_with_database():
    """Praca z bazą danych używając wygenerowanych modeli"""
    print("\n=== Praca z bazą danych ===")

    db = get_db_manager()
    
    # Stwórz bazę testową
    db_name = "model_generator_test"
    db.create_database(db_name)
    
    # Wygeneruj prosty model
    generator = ModelGenerator()
    
    product_fields = {
        "name": FieldConfig(FieldType.STRING, nullable=False, max_length=100),
        "price": FieldConfig(FieldType.FLOAT, nullable=False),
        "description": FieldConfig(FieldType.TEXT, nullable=True),
        "in_stock": FieldConfig(FieldType.BOOLEAN, nullable=False, default=True)
    }
    
    ProductModel = generator.generate_crud_model("Product", product_fields)
    
    # Stwórz tabele w bazie
    with db.get_session(db_name) as session:
        ProductModel.metadata.create_all(session.bind)
        print("✅ Utworzono tabele w bazie danych")
        
        # Dodaj przykładowe produkty
        products_data = [
            {
                "name": "Astralny Kryształ",
                "price": 777.77,
                "description": "Kryształ z energią astralną",
                "in_stock": True
            },
            {
                "name": "Księga Mądrości",
                "price": 999.99,
                "description": "Starożytna księga zawierająca tajemną wiedzę",
                "in_stock": True
            },
            {
                "name": "Eliksir Światła",
                "price": 333.33,
                "description": "Magiczny eliksir przynoszący oświecenie",
                "in_stock": False
            }
        ]
        
        for product_data in products_data:
            product = ProductModel.from_dict(product_data)
            session.add(product)
        
        session.commit()
        print(f"✅ Dodano {len(products_data)} produktów")
        
        # Sprawdź produkty w magazynie
        available_products = session.query(ProductModel).filter(ProductModel.in_stock == True).all()
        
        print(f"\n🛍️ Produkty dostępne w magazynie ({len(available_products)}):")
        for product in available_products:
            print(f"  - {product.name}: {product.price} zł")

def main():
    print("=== LuxDB Przykład 06: Generator Modeli - Manifestowanie Archetypów ===\n")

    try:
        # Przykłady generowania modeli
        example_basic_model_generation()
        example_advanced_model_generation()
        example_crud_model_generation()
        example_api_model_with_validation()
        example_migration_sql_generation()
        example_working_with_database()

        print("\n✨ Wszystkie przykłady generatora modeli zakończone pomyślnie!")
        print("🌟 Archetypy zostały zmaterializowane w Astralnej Bibliotece")

    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Zamknij połączenia
        db = get_db_manager()
        db.close_all_connections()
        print("🔒 Zamknięto wszystkie połączenia z Astralną Biblioteką")

if __name__ == "__main__":
    main()
