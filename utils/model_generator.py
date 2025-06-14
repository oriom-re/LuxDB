from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict

Base = declarative_base()

SQLALCHEMY_TYPE_MAP = {
    "int": Integer,
    "str": String,
    "text": Text,
    "bool": Boolean,
    "datetime": DateTime,
    "float": Float
}

def generate_model_class(name: str, fields: Dict[str, str]):
    """
    Dynamicznie generuje klasę modelu SQLAlchemy
    :param name: Nazwa klasy
    :param fields: Słownik {nazwa_pola: typ (str)}
    :return: Klasa modelu dziedzicząca po Base
    """
    attrs = {
        '__tablename__': name.lower(),
        'id': Column(Integer, primary_key=True, autoincrement=True)
    }

    for field_name, field_type in fields.items():
        field_type = field_type.lower()
        if field_type not in SQLALCHEMY_TYPE_MAP:
            raise ValueError(f"Nieobsługiwany typ pola: {field_type}")
        column_type = SQLALCHEMY_TYPE_MAP[field_type]
        attrs[field_name] = Column(column_type)

    return type(name, (Base,), attrs)
