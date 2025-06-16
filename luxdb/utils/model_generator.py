
"""
Generator modeli SQLAlchemy dla LuxDB
"""

from typing import Dict, Any, List, Optional, Type, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ..config import Base
from .error_handlers import ModelGenerationError, handle_database_errors

class FieldType(Enum):
    """Typy pól dla generatora modeli"""
    INTEGER = "integer"
    STRING = "string"
    TEXT = "text"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    FOREIGN_KEY = "foreign_key"

@dataclass
class FieldConfig:
    """Konfiguracja pola modelu"""
    field_type: FieldType
    nullable: bool = True
    unique: bool = False
    index: bool = False
    default: Any = None
    max_length: Optional[int] = None
    foreign_table: Optional[str] = None
    foreign_key: Optional[str] = None

@dataclass
class RelationshipConfig:
    """Konfiguracja relacji między modelami"""
    target_model: str
    relationship_type: str = "one_to_many"  # one_to_many, many_to_one, many_to_many
    back_populates: Optional[str] = None
    cascade: Optional[str] = None

class ModelGenerator:
    """Generator modeli SQLAlchemy"""
    
    def __init__(self, base_class: Type = None):
        self.base_class = base_class or Base
        self._generated_models = {}
    
    @handle_database_errors("model_generation")
    def generate_basic_model(self, model_name: str, fields: Dict[str, str]) -> Type:
        """Generuj podstawowy model z prostymi typami pól"""
        if model_name in self._generated_models:
            return self._generated_models[model_name]
        
        # Konwertuj proste typy na FieldConfig
        field_configs = {}
        for field_name, field_type in fields.items():
            field_configs[field_name] = self._string_to_field_config(field_type)
        
        return self.generate_advanced_model(model_name, field_configs)
    
    @handle_database_errors("model_generation")
    def generate_advanced_model(self, model_name: str, fields: Dict[str, FieldConfig], 
                               relationships: Dict[str, RelationshipConfig] = None) -> Type:
        """Generuj zaawansowany model z pełną konfiguracją"""
        if model_name in self._generated_models:
            return self._generated_models[model_name]
        
        # Przygotuj atrybuty modelu
        model_attrs = {
            '__tablename__': model_name.lower() + 's',
            'id': Column(Integer, primary_key=True, autoincrement=True)
        }
        
        # Dodaj pola
        for field_name, field_config in fields.items():
            column = self._create_column_from_config(field_config)
            model_attrs[field_name] = column
        
        # Dodaj relacje
        if relationships:
            for rel_name, rel_config in relationships.items():
                rel = relationship(
                    rel_config.target_model,
                    back_populates=rel_config.back_populates,
                    cascade=rel_config.cascade
                )
                model_attrs[rel_name] = rel
        
        # Utwórz klasę modelu
        model_class = type(model_name, (self.base_class,), model_attrs)
        self._generated_models[model_name] = model_class
        
        return model_class
    
    @handle_database_errors("model_generation")
    def generate_crud_model(self, model_name: str, fields: Dict[str, FieldConfig],
                           include_timestamps: bool = True, include_soft_delete: bool = False) -> Type:
        """Generuj model z metodami CRUD"""
        
        # Dodaj standardowe pola timestamp
        if include_timestamps:
            fields['created_at'] = FieldConfig(FieldType.DATETIME, nullable=False, default='now')
            fields['updated_at'] = FieldConfig(FieldType.DATETIME, nullable=False, default='now')
        
        # Dodaj soft delete
        if include_soft_delete:
            fields['deleted_at'] = FieldConfig(FieldType.DATETIME, nullable=True)
            fields['is_deleted'] = FieldConfig(FieldType.BOOLEAN, nullable=False, default=False)
        
        # Generuj podstawowy model
        model_class = self.generate_advanced_model(model_name, fields)
        
        # Dodaj metody CRUD
        def to_dict(self):
            """Konwertuj instancję na słownik"""
            result = {}
            for column in self.__table__.columns:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                else:
                    result[column.name] = value
            return result
        
        def from_dict(cls, data: Dict[str, Any]):
            """Utwórz instancję ze słownika"""
            filtered_data = {}
            for column in cls.__table__.columns:
                if column.name in data:
                    filtered_data[column.name] = data[column.name]
            return cls(**filtered_data)
        
        def update_from_dict(self, data: Dict[str, Any]):
            """Zaktualizuj instancję ze słownika"""
            for column in self.__table__.columns:
                if column.name in data and column.name != 'id':
                    setattr(self, column.name, data[column.name])
        
        # Dodaj metody do klasy
        model_class.to_dict = to_dict
        model_class.from_dict = classmethod(from_dict)
        model_class.update_from_dict = update_from_dict
        
        return model_class
    
    @handle_database_errors("model_generation")
    def generate_api_model(self, model_name: str, fields: Dict[str, FieldConfig],
                          validation_rules: Dict[str, List[str]] = None) -> Type:
        """Generuj model z walidacją dla API"""
        
        # Generuj model CRUD
        model_class = self.generate_crud_model(model_name, fields, include_timestamps=True)
        
        # Dodaj walidację
        def validate(self) -> List[str]:
            """Waliduj instancję modelu"""
            errors = []
            
            if validation_rules:
                for field_name, rules in validation_rules.items():
                    field_value = getattr(self, field_name, None)
                    
                    for rule in rules:
                        error = self._validate_field(field_name, field_value, rule)
                        if error:
                            errors.append(error)
            
            return errors
        
        def _validate_field(self, field_name: str, value: Any, rule: str) -> Optional[str]:
            """Waliduj pojedyncze pole"""
            if rule == "required" and (value is None or value == ""):
                return f"{field_name} is required"
            
            if rule == "email" and value:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, str(value)):
                    return f"{field_name} must be a valid email"
            
            if rule.startswith("min_length:") and value:
                min_len = int(rule.split(":")[1])
                if len(str(value)) < min_len:
                    return f"{field_name} must be at least {min_len} characters"
            
            if rule.startswith("max_length:") and value:
                max_len = int(rule.split(":")[1])
                if len(str(value)) > max_len:
                    return f"{field_name} must be at most {max_len} characters"
            
            return None
        
        # Dodaj metody walidacji
        model_class.validate = validate
        model_class._validate_field = _validate_field
        
        return model_class
    
    def _string_to_field_config(self, field_type: str) -> FieldConfig:
        """Konwertuj string typu na FieldConfig"""
        type_mapping = {
            'string': FieldType.STRING,
            'text': FieldType.TEXT,
            'integer': FieldType.INTEGER,
            'float': FieldType.FLOAT,
            'boolean': FieldType.BOOLEAN,
            'datetime': FieldType.DATETIME
        }
        
        if field_type not in type_mapping:
            raise ModelGenerationError(f"Nieznany typ pola: {field_type}")
        
        return FieldConfig(type_mapping[field_type])
    
    def _create_column_from_config(self, field_config: FieldConfig) -> Column:
        """Utwórz kolumnę SQLAlchemy z konfiguracji"""
        column_type = self._get_sqlalchemy_type(field_config)
        
        kwargs = {
            'nullable': field_config.nullable,
            'unique': field_config.unique,
            'index': field_config.index
        }
        
        if field_config.default is not None:
            if field_config.default == 'now' and field_config.field_type == FieldType.DATETIME:
                from sqlalchemy import func
                kwargs['default'] = func.current_timestamp()
            else:
                kwargs['default'] = field_config.default
        
        return Column(column_type, **kwargs)
    
    def _get_sqlalchemy_type(self, field_config: FieldConfig):
        """Pobierz typ SQLAlchemy dla konfiguracji pola"""
        if field_config.field_type == FieldType.INTEGER:
            return Integer
        elif field_config.field_type == FieldType.STRING:
            if field_config.max_length:
                return String(field_config.max_length)
            return String(255)
        elif field_config.field_type == FieldType.TEXT:
            return Text
        elif field_config.field_type == FieldType.FLOAT:
            return Float
        elif field_config.field_type == FieldType.BOOLEAN:
            return Boolean
        elif field_config.field_type == FieldType.DATETIME:
            return DateTime
        elif field_config.field_type == FieldType.FOREIGN_KEY:
            if not field_config.foreign_table:
                raise ModelGenerationError("Foreign key requires foreign_table")
            return Integer  # Will be handled separately with ForeignKey
        else:
            raise ModelGenerationError(f"Nieobsługiwany typ pola: {field_config.field_type}")
    
    def create_migration_sql(self, model_class: Type) -> str:
        """Generuj SQL migracji dla modelu"""
        table_name = model_class.__tablename__
        columns = []
        
        for column in model_class.__table__.columns:
            col_def = f"{column.name} {self._get_sql_type(column.type)}"
            
            if column.primary_key:
                col_def += " PRIMARY KEY"
            if column.autoincrement:
                col_def += " AUTOINCREMENT"
            if not column.nullable:
                col_def += " NOT NULL"
            if column.unique:
                col_def += " UNIQUE"
            if column.default is not None:
                col_def += f" DEFAULT {column.default}"
            
            columns.append(col_def)
        
        sql = f"CREATE TABLE {table_name} (\n"
        sql += ",\n".join(f"  {col}" for col in columns)
        sql += "\n);"
        
        return sql
    
    def _get_sql_type(self, sqlalchemy_type) -> str:
        """Konwertuj typ SQLAlchemy na SQL"""
        type_name = str(sqlalchemy_type)
        
        if 'INTEGER' in type_name:
            return 'INTEGER'
        elif 'VARCHAR' in type_name or 'STRING' in type_name:
            return 'VARCHAR(255)'
        elif 'TEXT' in type_name:
            return 'TEXT'
        elif 'FLOAT' in type_name or 'REAL' in type_name:
            return 'REAL'
        elif 'BOOLEAN' in type_name:
            return 'BOOLEAN'
        elif 'DATETIME' in type_name:
            return 'DATETIME'
        else:
            return 'TEXT'
    
    def list_generated_models(self) -> List[str]:
        """Lista wygenerowanych modeli"""
        return list(self._generated_models.keys())
    
    def get_model(self, model_name: str) -> Optional[Type]:
        """Pobierz wygenerowany model"""
        return self._generated_models.get(model_name)
