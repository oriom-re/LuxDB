
"""
Narzędzia pomocnicze dla LuxDB
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func
from typing import Dict, List, Any, Optional, Type, Union
from datetime import datetime
from enum import Enum
import re

from ..config import Base

class QueryBuilder:
    """Builder do tworzenia zapytań SQLAlchemy"""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.session = None
        self.reset()
    
    def reset(self):
        """Resetuje builder"""
        self._query = None
        self._filters = []
        self._joins = []
        self._order_by_clauses = []
        self._group_by_clauses = []
        self._having_clauses = []
        self._limit_value = None
        self._offset_value = None
        return self
    
    def set_session(self, session: Session):
        """Ustawia sesję SQLAlchemy"""
        self.session = session
        return self
    
    def select(self, *columns):
        """Dodaje kolumny do SELECT"""
        if not self.session:
            raise ValueError("Sesja nie została ustawiona")
        
        if columns:
            self._query = self.session.query(*[getattr(self.model_class, col) for col in columns])
        else:
            self._query = self.session.query(self.model_class)
        return self
    
    def filter(self, *conditions):
        """Dodaje warunki WHERE"""
        if not self._query:
            self.select()
        
        for condition in conditions:
            self._query = self._query.filter(condition)
        return self
    
    def join(self, *args, **kwargs):
        """Dodaje JOIN"""
        if not self._query:
            self.select()
        
        self._query = self._query.join(*args, **kwargs)
        return self
    
    def order_by(self, *columns):
        """Dodaje ORDER BY"""
        if not self._query:
            self.select()
        
        self._query = self._query.order_by(*columns)
        return self
    
    def group_by(self, *columns):
        """Dodaje GROUP BY"""
        if not self._query:
            self.select()
        
        self._query = self._query.group_by(*columns)
        return self
    
    def having(self, condition):
        """Dodaje HAVING"""
        if not self._query:
            self.select()
        
        self._query = self._query.having(condition)
        return self
    
    def limit(self, count: int):
        """Dodaje LIMIT"""
        if not self._query:
            self.select()
        
        self._query = self._query.limit(count)
        return self
    
    def offset(self, count: int):
        """Dodaje OFFSET"""
        if not self._query:
            self.select()
        
        self._query = self._query.offset(count)
        return self
    
    def all(self):
        """Zwraca wszystkie wyniki"""
        if not self._query:
            self.select()
        return self._query.all()
    
    def first(self):
        """Zwraca pierwszy wynik"""
        if not self._query:
            self.select()
        return self._query.first()
    
    def count(self):
        """Zwraca liczbę wyników"""
        if not self._query:
            self.select()
        return self._query.count()

class FieldType(Enum):
    """Typy pól dla generatora modeli"""
    INTEGER = "integer"
    STRING = "string"
    TEXT = "text"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    FLOAT = "float"
    FOREIGN_KEY = "foreign_key"

class FieldConfig:
    """Konfiguracja pola modelu"""
    def __init__(self, field_type: FieldType, nullable: bool = True, unique: bool = False, 
                 default: Any = None, max_length: int = None, foreign_key: str = None,
                 index: bool = False, primary_key: bool = False):
        self.field_type = field_type
        self.nullable = nullable
        self.unique = unique
        self.default = default
        self.max_length = max_length
        self.foreign_key = foreign_key
        self.index = index
        self.primary_key = primary_key

class RelationshipConfig:
    """Konfiguracja relacji między modelami"""
    def __init__(self, target_model: str, relationship_type: str = "one_to_many",
                 back_populates: str = None, cascade: str = None):
        self.target_model = target_model
        self.relationship_type = relationship_type  # one_to_many, many_to_one, many_to_many
        self.back_populates = back_populates
        self.cascade = cascade

class ModelGenerator:
    """Generator modeli SQLAlchemy - wersja bazowa i zaawansowana"""
    
    # Mapowanie typów na kolumny SQLAlchemy
    TYPE_MAP = {
        FieldType.INTEGER: Integer,
        FieldType.STRING: String,
        FieldType.TEXT: Text,
        FieldType.BOOLEAN: Boolean,
        FieldType.DATETIME: DateTime,
        FieldType.FLOAT: Float
    }
    
    def __init__(self):
        self.generated_models = {}
        self.relationships = {}
    
    def generate_basic_model(self, name: str, fields: Dict[str, str]) -> Type[Base]:
        """
        Generuje podstawowy model SQLAlchemy (wersja bazowa)
        :param name: Nazwa modelu
        :param fields: Słownik {nazwa_pola: typ_jako_string}
        :return: Klasa modelu
        """
        table_name = self._to_snake_case(name)
        
        attrs = {
            '__tablename__': table_name,
            'id': Column(Integer, primary_key=True, autoincrement=True)
        }
        
        for field_name, field_type_str in fields.items():
            field_type_str = field_type_str.lower()
            
            # Mapowanie prostych typów
            if field_type_str in ['int', 'integer']:
                column_type = Integer
            elif field_type_str in ['str', 'string']:
                column_type = String(255)
            elif field_type_str in ['text']:
                column_type = Text
            elif field_type_str in ['bool', 'boolean']:
                column_type = Boolean
            elif field_type_str in ['datetime', 'timestamp']:
                column_type = DateTime
            elif field_type_str in ['float', 'decimal']:
                column_type = Float
            else:
                raise ValueError(f"Nieobsługiwany typ pola: {field_type_str}")
            
            attrs[field_name] = Column(column_type)
        
        model_class = type(name, (Base,), attrs)
        self.generated_models[name] = model_class
        return model_class
    
    def generate_advanced_model(self, name: str, fields: Dict[str, FieldConfig],
                              relationships: Dict[str, RelationshipConfig] = None) -> Type[Base]:
        """
        Generuje zaawansowany model SQLAlchemy (wersja rozbudowana)
        :param name: Nazwa modelu
        :param fields: Słownik {nazwa_pola: FieldConfig}
        :param relationships: Słownik {nazwa_relacji: RelationshipConfig}
        :return: Klasa modelu
        """
        table_name = self._to_snake_case(name)
        
        attrs = {
            '__tablename__': table_name,
            'id': Column(Integer, primary_key=True, autoincrement=True)
        }
        
        indexes = []
        
        # Generuj kolumny
        for field_name, field_config in fields.items():
            column_args = []
            column_kwargs = {
                'nullable': field_config.nullable,
                'unique': field_config.unique
            }
            
            # Typ kolumny
            if field_config.field_type == FieldType.FOREIGN_KEY:
                column_type = Integer
                column_kwargs['foreign_key'] = ForeignKey(field_config.foreign_key)
            else:
                column_type = self.TYPE_MAP[field_config.field_type]
                
                # Długość dla stringów
                if field_config.field_type == FieldType.STRING and field_config.max_length:
                    column_type = String(field_config.max_length)
            
            # Wartość domyślna
            if field_config.default is not None:
                if field_config.field_type == FieldType.DATETIME and field_config.default == 'now':
                    column_kwargs['default'] = func.current_timestamp()
                else:
                    column_kwargs['default'] = field_config.default
            
            # Klucz główny
            if field_config.primary_key:
                column_kwargs['primary_key'] = True
            
            attrs[field_name] = Column(column_type, **column_kwargs)
            
            # Indeksy
            if field_config.index:
                indexes.append(Index(f'idx_{table_name}_{field_name}', field_name))
        
        # Dodaj indeksy do atrybutów
        if indexes:
            attrs['__table_args__'] = tuple(indexes)
        
        # Generuj relacje
        if relationships:
            for rel_name, rel_config in relationships.items():
                rel_kwargs = {}
                
                if rel_config.back_populates:
                    rel_kwargs['back_populates'] = rel_config.back_populates
                
                if rel_config.cascade:
                    rel_kwargs['cascade'] = rel_config.cascade
                
                attrs[rel_name] = relationship(rel_config.target_model, **rel_kwargs)
        
        model_class = type(name, (Base,), attrs)
        self.generated_models[name] = model_class
        
        # Zapisz relacje do późniejszego przetworzenia
        if relationships:
            self.relationships[name] = relationships
        
        return model_class
    
    def generate_crud_model(self, name: str, fields: Dict[str, FieldConfig], 
                           include_timestamps: bool = True, include_soft_delete: bool = False) -> Type[Base]:
        """
        Generuje model CRUD z automatycznymi polami systemowymi
        :param name: Nazwa modelu
        :param fields: Pola modelu
        :param include_timestamps: Czy dodać created_at/updated_at
        :param include_soft_delete: Czy dodać soft delete (is_deleted)
        :return: Klasa modelu z metodami CRUD
        """
        # Dodaj systemowe pola
        if include_timestamps:
            fields['created_at'] = FieldConfig(
                FieldType.DATETIME, 
                nullable=False, 
                default='now'
            )
            fields['updated_at'] = FieldConfig(
                FieldType.DATETIME, 
                nullable=False, 
                default='now'
            )
        
        if include_soft_delete:
            fields['is_deleted'] = FieldConfig(
                FieldType.BOOLEAN, 
                nullable=False, 
                default=False
            )
        
        model_class = self.generate_advanced_model(name, fields)
        
        # Dodaj metody CRUD jako metody klasowe
        def to_dict(self):
            """Konwertuje instancję na słownik"""
            result = {}
            for column in self.__table__.columns:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value
            return result
        
        def update_from_dict(self, data: Dict[str, Any]):
            """Aktualizuje instancję ze słownika"""
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            if include_timestamps and hasattr(self, 'updated_at'):
                setattr(self, 'updated_at', datetime.now())
        
        # Dodaj metody do klasy
        model_class.to_dict = to_dict
        model_class.update_from_dict = update_from_dict
        
        return model_class
    
    def generate_api_model(self, name: str, fields: Dict[str, FieldConfig],
                          validation_rules: Dict[str, List[str]] = None) -> Type[Base]:
        """
        Generuje model z walidacją API
        :param name: Nazwa modelu
        :param fields: Pola modelu
        :param validation_rules: Reguły walidacji {pole: [reguły]}
        :return: Model z walidacją
        """
        model_class = self.generate_crud_model(name, fields)
        
        def validate(self, field_name: str = None) -> List[str]:
            """Waliduje model lub konkretne pole"""
            errors = []
            
            if not validation_rules:
                return errors
            
            fields_to_validate = [field_name] if field_name else validation_rules.keys()
            
            for field in fields_to_validate:
                if field not in validation_rules:
                    continue
                
                value = getattr(self, field, None)
                
                for rule in validation_rules[field]:
                    if rule == 'required' and (value is None or value == ''):
                        errors.append(f"Pole {field} jest wymagane")
                    elif rule.startswith('min_length:'):
                        min_len = int(rule.split(':')[1])
                        if value and len(str(value)) < min_len:
                            errors.append(f"Pole {field} musi mieć co najmniej {min_len} znaków")
                    elif rule.startswith('max_length:'):
                        max_len = int(rule.split(':')[1])
                        if value and len(str(value)) > max_len:
                            errors.append(f"Pole {field} może mieć maksymalnie {max_len} znaków")
                    elif rule == 'email' and value:
                        if '@' not in str(value):
                            errors.append(f"Pole {field} musi być prawidłowym adresem email")
            
            return errors
        
        model_class.validate = validate
        return model_class
    
    def _to_snake_case(self, name: str) -> str:
        """Konwertuje CamelCase na snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def get_model(self, name: str) -> Optional[Type[Base]]:
        """Zwraca wygenerowany model po nazwie"""
        return self.generated_models.get(name)
    
    def list_models(self) -> List[str]:
        """Zwraca listę nazw wygenerowanych modeli"""
        return list(self.generated_models.keys())
    
    def create_migration_sql(self, model_class: Type[Base]) -> str:
        """Generuje SQL do utworzenia tabeli dla modelu"""
        from sqlalchemy.schema import CreateTable
        return str(CreateTable(model_class.__table__).compile(compile_kwargs={"literal_binds": True}))

__all__ = [
    "QueryBuilder", 
    "ModelGenerator", 
    "FieldType", 
    "FieldConfig", 
    "RelationshipConfig"
]
