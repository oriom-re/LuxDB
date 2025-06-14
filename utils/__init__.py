"""
Utilities for LuxDB - Model Generator and helper classes
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union, Type
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import re

Base = declarative_base()

class FieldType(Enum):
    """Typy pól obsługiwane przez generator"""
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"

@dataclass
class FieldConfig:
    """Konfiguracja pola modelu"""
    field_type: FieldType
    nullable: bool = True
    unique: bool = False
    index: bool = False
    default: Any = None
    max_length: Optional[int] = None
    foreign_key: Optional[str] = None

@dataclass
class RelationshipConfig:
    """Konfiguracja relacji między modelami"""
    target_model: str
    relationship_type: str  # "one_to_many", "many_to_one", "many_to_many"
    back_populates: Optional[str] = None
    foreign_key: Optional[str] = None

class QueryBuilder:
    """Builder zapytań SQLAlchemy"""

    def __init__(self, model_class):
        self.model_class = model_class
        self.query = None
        self.session = None

    def set_session(self, session):
        """Ustaw sesję SQLAlchemy"""
        self.session = session
        return self

    def select(self, *columns):
        """Rozpocznij zapytanie SELECT"""
        if self.session is None:
            raise ValueError("Session must be set before querying")

        if columns:
            self.query = self.session.query(*columns)
        else:
            self.query = self.session.query(self.model_class)
        return self

    def filter(self, *conditions):
        """Dodaj warunki WHERE"""
        if self.query is None:
            raise ValueError("Must call select() first")
        self.query = self.query.filter(*conditions)
        return self

    def order_by(self, *columns):
        """Dodaj sortowanie"""
        if self.query is None:
            raise ValueError("Must call select() first")
        self.query = self.query.order_by(*columns)
        return self

    def join(self, *tables):
        """Dodaj JOIN"""
        if self.query is None:
            raise ValueError("Must call select() first")
        self.query = self.query.join(*tables)
        return self

    def limit(self, count):
        """Ogranicz liczbę wyników"""
        if self.query is None:
            raise ValueError("Must call select() first")
        self.query = self.query.limit(count)
        return self

    def all(self):
        """Pobierz wszystkie wyniki"""
        if self.query is None:
            raise ValueError("Must build query first")
        return self.query.all()

    def first(self):
        """Pobierz pierwszy wynik"""
        if self.query is None:
            raise ValueError("Must build query first")
        return self.query.first()

    def count(self):
        """Policz wyniki"""
        if self.query is None:
            raise ValueError("Must build query first")
        return self.query.count()

    def reset(self):
        """Zresetuj builder"""
        self.query = None
        return self

class ModelGenerator:
    """Generator modeli SQLAlchemy"""

    def __init__(self):
        self.base = Base

    def _get_sqlalchemy_type(self, field_config: Union[FieldConfig, str]):
        """Konwertuj typ pola na typ SQLAlchemy"""
        if isinstance(field_config, str):
            field_type = FieldType(field_config.lower())
            nullable = True
            max_length = None
        else:
            field_type = field_config.field_type
            nullable = field_config.nullable
            max_length = field_config.max_length

        type_mapping = {
            FieldType.STRING: String(max_length) if max_length else String(255),
            FieldType.TEXT: Text,
            FieldType.INTEGER: Integer,
            FieldType.FLOAT: Float,
            FieldType.BOOLEAN: Boolean,
            FieldType.DATETIME: DateTime
        }

        return type_mapping.get(field_type, String(255))

    def _create_column(self, field_name: str, field_config: Union[FieldConfig, str]):
        """Utwórz kolumnę SQLAlchemy"""
        if isinstance(field_config, str):
            field_config = FieldConfig(FieldType(field_config.lower()))

        column_args = []
        column_kwargs = {
            'nullable': field_config.nullable,
            'unique': field_config.unique,
            'index': field_config.index
        }

        # Dodaj typ kolumny
        sqlalchemy_type = self._get_sqlalchemy_type(field_config)
        column_args.append(sqlalchemy_type)

        # Dodaj foreign key jeśli jest
        if field_config.foreign_key:
            column_args.append(ForeignKey(field_config.foreign_key))

        # Dodaj domyślną wartość
        if field_config.default is not None:
            if field_config.default == "now" and field_config.field_type == FieldType.DATETIME:
                column_kwargs['default'] = func.current_timestamp()
            else:
                column_kwargs['default'] = field_config.default

        return Column(*column_args, **column_kwargs)

    def generate_basic_model(self, model_name: str, fields: Dict[str, str]) -> Type:
        """Generuj podstawowy model SQLAlchemy"""
        table_name = self._to_snake_case(model_name)

        # Atrybuty modelu
        attrs = {
            '__tablename__': table_name,
            'id': Column(Integer, primary_key=True, autoincrement=True)
        }

        # Dodaj pola
        for field_name, field_type in fields.items():
            attrs[field_name] = self._create_column(field_name, field_type)

        # Utwórz klasę modelu
        return type(model_name, (self.base,), attrs)

    def generate_advanced_model(self, model_name: str, fields: Dict[str, FieldConfig], 
                              relationships: Optional[Dict[str, RelationshipConfig]] = None) -> Type:
        """Generuj zaawansowany model SQLAlchemy"""
        table_name = self._to_snake_case(model_name)

        # Atrybuty modelu
        attrs = {
            '__tablename__': table_name,
            'id': Column(Integer, primary_key=True, autoincrement=True)
        }

        # Dodaj pola
        for field_name, field_config in fields.items():
            attrs[field_name] = self._create_column(field_name, field_config)

        # Dodaj relacje (tylko jeśli są podane)
        if relationships:
            for rel_name, rel_config in relationships.items():
                # Tymczasowo pomijamy relacje, które mogą powodować problemy
                pass

        # Utwórz klasę modelu
        return type(model_name, (self.base,), attrs)

    def generate_crud_model(self, model_name: str, fields: Dict[str, FieldConfig],
                           include_timestamps: bool = True, include_soft_delete: bool = False) -> Type:
        """Generuj model z metodami CRUD"""

        # Dodaj timestamps jeśli wymagane
        if include_timestamps:
            fields['created_at'] = FieldConfig(
                FieldType.DATETIME,
                nullable=False,
                default="now"
            )
            fields['updated_at'] = FieldConfig(
                FieldType.DATETIME,
                nullable=False,
                default="now"
            )

        # Dodaj soft delete jeśli wymagane
        if include_soft_delete:
            fields['is_deleted'] = FieldConfig(
                FieldType.BOOLEAN,
                nullable=False,
                default=False
            )

        # Wygeneruj podstawowy model
        ModelClass = self.generate_advanced_model(model_name, fields)

        # Dodaj metody CRUD
        def to_dict(self):
            """Konwertuj instancję na słownik"""
            result = {}
            for column in self.__table__.columns:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value
            return result

        def update_from_dict(self, data: Dict[str, Any]):
            """Aktualizuj instancję ze słownika"""
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)

        # Dodaj metody do klasy
        ModelClass.to_dict = to_dict
        ModelClass.update_from_dict = update_from_dict

        return ModelClass

    def generate_api_model(self, model_name: str, fields: Dict[str, FieldConfig],
                          validation_rules: Optional[Dict[str, List[str]]] = None) -> Type:
        """Generuj model API z walidacją"""

        # Wygeneruj podstawowy model
        ModelClass = self.generate_advanced_model(model_name, fields)

        # Dodaj walidację
        def validate(self) -> List[str]:
            """Waliduj instancję modelu"""
            errors = []

            if not validation_rules:
                return errors

            for field_name, rules in validation_rules.items():
                field_value = getattr(self, field_name, None)

                for rule in rules:
                    if rule == "required" and (field_value is None or field_value == ""):
                        errors.append(f"{field_name} is required")
                    elif rule.startswith("min_length:"):
                        min_len = int(rule.split(":")[1])
                        if field_value and len(str(field_value)) < min_len:
                            errors.append(f"{field_name} must be at least {min_len} characters")
                    elif rule.startswith("max_length:"):
                        max_len = int(rule.split(":")[1])
                        if field_value and len(str(field_value)) > max_len:
                            errors.append(f"{field_name} must be at most {max_len} characters")
                    elif rule == "email" and field_value:
                        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(field_value)):
                            errors.append(f"{field_name} must be a valid email")

            return errors

        # Dodaj metody do klasy
        ModelClass.validate = validate

        return ModelClass

    def create_migration_sql(self, model_class: Type) -> str:
        """Wygeneruj SQL dla migracji"""
        table_name = model_class.__tablename__

        sql_parts = [f"CREATE TABLE IF NOT EXISTS {table_name} ("]

        for column in model_class.__table__.columns:
            col_def = f"  {column.name}"

            # Typ kolumny
            if hasattr(column.type, 'length') and column.type.length:
                col_def += f" VARCHAR({column.type.length})"
            elif column.type.python_type == str:
                col_def += " TEXT"
            elif column.type.python_type == int:
                col_def += " INTEGER"
            elif column.type.python_type == float:
                col_def += " REAL"
            elif column.type.python_type == bool:
                col_def += " BOOLEAN"
            elif column.type.python_type == datetime:
                col_def += " TIMESTAMP"
            else:
                col_def += " TEXT"

            # Ograniczenia
            if column.primary_key:
                col_def += " PRIMARY KEY"
            if column.autoincrement:
                col_def += " AUTOINCREMENT"
            if not column.nullable:
                col_def += " NOT NULL"
            if column.unique:
                col_def += " UNIQUE"

            sql_parts.append(col_def + ",")

        # Usuń ostatni przecinek i zamknij
        if sql_parts[-1].endswith(","):
            sql_parts[-1] = sql_parts[-1][:-1]

        sql_parts.append(");")

        return "\n".join(sql_parts)

    def _to_snake_case(self, name: str) -> str:
        """Konwertuj CamelCase na snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

__all__ = [
    'ModelGenerator',
    'QueryBuilder', 
    'FieldConfig',
    'FieldType',
    'RelationshipConfig',
    'Base'
]