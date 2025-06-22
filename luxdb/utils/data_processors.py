
"""
Narzędzia do przetwarzania i transformacji danych w LuxDB
"""

from typing import Dict, List, Any, Optional, Callable, Union, Type
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
from .logging_utils import get_db_logger
from .error_handlers import LuxDBError, handle_database_errors

class DataFilter:
    """Filtrowanie danych"""
    
    @staticmethod
    def filter_by_field(data: List[Dict[str, Any]], field: str, value: Any,
                       operator: str = "eq") -> List[Dict[str, Any]]:
        """Filtruj dane według pola"""
        filtered = []
        
        for record in data:
            field_value = record.get(field)
            
            if operator == "eq" and field_value == value:
                filtered.append(record)
            elif operator == "ne" and field_value != value:
                filtered.append(record)
            elif operator == "gt" and field_value is not None and field_value > value:
                filtered.append(record)
            elif operator == "lt" and field_value is not None and field_value < value:
                filtered.append(record)
            elif operator == "gte" and field_value is not None and field_value >= value:
                filtered.append(record)
            elif operator == "lte" and field_value is not None and field_value <= value:
                filtered.append(record)
            elif operator == "contains" and isinstance(field_value, str) and value in field_value:
                filtered.append(record)
            elif operator == "startswith" and isinstance(field_value, str) and field_value.startswith(value):
                filtered.append(record)
            elif operator == "endswith" and isinstance(field_value, str) and field_value.endswith(value):
                filtered.append(record)
            elif operator == "regex" and isinstance(field_value, str) and re.search(value, field_value):
                filtered.append(record)
            elif operator == "in" and isinstance(value, (list, tuple)) and field_value in value:
                filtered.append(record)
            elif operator == "not_in" and isinstance(value, (list, tuple)) and field_value not in value:
                filtered.append(record)
            elif operator == "is_null" and field_value is None:
                filtered.append(record)
            elif operator == "is_not_null" and field_value is not None:
                filtered.append(record)
        
        return filtered
    
    @staticmethod
    def filter_by_date_range(data: List[Dict[str, Any]], date_field: str,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Filtruj dane według zakresu dat"""
        filtered = []
        
        for record in data:
            field_value = record.get(date_field)
            
            if not isinstance(field_value, datetime):
                continue
            
            if start_date and field_value < start_date:
                continue
            
            if end_date and field_value > end_date:
                continue
            
            filtered.append(record)
        
        return filtered
    
    @staticmethod
    def filter_active_records(data: List[Dict[str, Any]], 
                            status_field: str = "is_active") -> List[Dict[str, Any]]:
        """Filtruj aktywne rekordy"""
        return DataFilter.filter_by_field(data, status_field, True)
    
    @staticmethod
    def filter_recent_records(data: List[Dict[str, Any]], date_field: str,
                            days: int = 7) -> List[Dict[str, Any]]:
        """Filtruj ostatnie rekordy"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return DataFilter.filter_by_date_range(data, date_field, start_date=cutoff_date)

class DataTransformer:
    """Transformacja danych"""
    
    @staticmethod
    def transform_field(data: List[Dict[str, Any]], field: str,
                       transformer: Callable[[Any], Any]) -> List[Dict[str, Any]]:
        """Transformuj pole w danych"""
        transformed = []
        
        for record in data.copy():
            new_record = record.copy()
            if field in new_record:
                try:
                    new_record[field] = transformer(new_record[field])
                except Exception:
                    # Jeśli transformacja się nie powiodła, zachowaj oryginalną wartość
                    pass
            transformed.append(new_record)
        
        return transformed
    
    @staticmethod
    def normalize_strings(data: List[Dict[str, Any]], fields: List[str],
                         lowercase: bool = True, strip: bool = True) -> List[Dict[str, Any]]:
        """Normalizuj pola tekstowe"""
        def normalize_string(value):
            if not isinstance(value, str):
                return value
            
            if strip:
                value = value.strip()
            if lowercase:
                value = value.lower()
            
            return value
        
        transformed = data.copy()
        for field in fields:
            transformed = DataTransformer.transform_field(transformed, field, normalize_string)
        
        return transformed
    
    @staticmethod
    def add_computed_field(data: List[Dict[str, Any]], new_field: str,
                          computer: Callable[[Dict[str, Any]], Any]) -> List[Dict[str, Any]]:
        """Dodaj obliczone pole"""
        transformed = []
        
        for record in data:
            new_record = record.copy()
            try:
                new_record[new_field] = computer(record)
            except Exception:
                new_record[new_field] = None
            transformed.append(new_record)
        
        return transformed
    
    @staticmethod
    def rename_fields(data: List[Dict[str, Any]], 
                     field_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """Zmień nazwy pól"""
        transformed = []
        
        for record in data:
            new_record = {}
            for old_field, value in record.items():
                new_field = field_mapping.get(old_field, old_field)
                new_record[new_field] = value
            transformed.append(new_record)
        
        return transformed
    
    @staticmethod
    def select_fields(data: List[Dict[str, Any]], 
                     fields: List[str]) -> List[Dict[str, Any]]:
        """Wybierz tylko określone pola"""
        transformed = []
        
        for record in data:
            new_record = {field: record.get(field) for field in fields}
            transformed.append(new_record)
        
        return transformed

class DataAggregator:
    """Agregacja danych"""
    
    @staticmethod
    def group_by(data: List[Dict[str, Any]], group_field: str) -> Dict[Any, List[Dict[str, Any]]]:
        """Grupuj dane według pola"""
        groups = defaultdict(list)
        
        for record in data:
            group_value = record.get(group_field)
            groups[group_value].append(record)
        
        return dict(groups)
    
    @staticmethod
    def count_by_field(data: List[Dict[str, Any]], field: str) -> Dict[Any, int]:
        """Policz wystąpienia według pola"""
        counter = Counter()
        
        for record in data:
            value = record.get(field)
            counter[value] += 1
        
        return dict(counter)
    
    @staticmethod
    def aggregate_numeric_field(data: List[Dict[str, Any]], field: str,
                              operation: str = "sum") -> Optional[float]:
        """Agreguj pole numeryczne"""
        values = []
        
        for record in data:
            value = record.get(field)
            if isinstance(value, (int, float)):
                values.append(value)
        
        if not values:
            return None
        
        if operation == "sum":
            return sum(values)
        elif operation == "avg":
            return sum(values) / len(values)
        elif operation == "min":
            return min(values)
        elif operation == "max":
            return max(values)
        elif operation == "count":
            return len(values)
        else:
            raise LuxDBError(f"Unsupported aggregation operation: {operation}")
    
    @staticmethod
    def summarize_by_group(data: List[Dict[str, Any]], group_field: str,
                          numeric_field: str, operations: List[str] = None) -> Dict[Any, Dict[str, float]]:
        """Podsumuj dane według grup"""
        if operations is None:
            operations = ["count", "sum", "avg", "min", "max"]
        
        groups = DataAggregator.group_by(data, group_field)
        summary = {}
        
        for group_value, group_data in groups.items():
            group_summary = {}
            for operation in operations:
                try:
                    result = DataAggregator.aggregate_numeric_field(group_data, numeric_field, operation)
                    group_summary[operation] = result
                except:
                    group_summary[operation] = None
            summary[group_value] = group_summary
        
        return summary

class DataValidator:
    """Walidacja danych"""
    
    @staticmethod
    def validate_required_fields(data: List[Dict[str, Any]], 
                               required_fields: List[str]) -> List[Dict[str, Any]]:
        """Znajdź rekordy z brakującymi wymaganymi polami"""
        invalid_records = []
        
        for i, record in enumerate(data):
            missing_fields = []
            for field in required_fields:
                if field not in record or record[field] is None or record[field] == "":
                    missing_fields.append(field)
            
            if missing_fields:
                invalid_records.append({
                    "record_index": i,
                    "record": record,
                    "missing_fields": missing_fields
                })
        
        return invalid_records
    
    @staticmethod
    def validate_data_types(data: List[Dict[str, Any]], 
                          field_types: Dict[str, type]) -> List[Dict[str, Any]]:
        """Sprawdź typy danych"""
        invalid_records = []
        
        for i, record in enumerate(data):
            type_errors = []
            for field, expected_type in field_types.items():
                if field in record and record[field] is not None:
                    if not isinstance(record[field], expected_type):
                        type_errors.append({
                            "field": field,
                            "expected_type": expected_type.__name__,
                            "actual_type": type(record[field]).__name__,
                            "value": record[field]
                        })
            
            if type_errors:
                invalid_records.append({
                    "record_index": i,
                    "record": record,
                    "type_errors": type_errors
                })
        
        return invalid_records
    
    @staticmethod
    def find_duplicates(data: List[Dict[str, Any]], 
                       unique_fields: List[str]) -> List[Dict[str, Any]]:
        """Znajdź duplikaty według pól"""
        seen = set()
        duplicates = []
        
        for i, record in enumerate(data):
            # Utwórz klucz z wartości unique_fields
            key_values = tuple(record.get(field) for field in unique_fields)
            
            if key_values in seen:
                duplicates.append({
                    "record_index": i,
                    "record": record,
                    "duplicate_key": dict(zip(unique_fields, key_values))
                })
            else:
                seen.add(key_values)
        
        return duplicates

class DataCleaner:
    """Czyszczenie danych"""
    
    @staticmethod
    def remove_nulls(data: List[Dict[str, Any]], 
                    fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Usuń rekordy z wartościami null"""
        cleaned = []
        
        for record in data:
            has_null = False
            
            fields_to_check = fields if fields else record.keys()
            
            for field in fields_to_check:
                if record.get(field) is None:
                    has_null = True
                    break
            
            if not has_null:
                cleaned.append(record)
        
        return cleaned
    
    @staticmethod
    def remove_duplicates(data: List[Dict[str, Any]], 
                         unique_fields: List[str]) -> List[Dict[str, Any]]:
        """Usuń duplikaty"""
        seen = set()
        cleaned = []
        
        for record in data:
            key_values = tuple(record.get(field) for field in unique_fields)
            
            if key_values not in seen:
                seen.add(key_values)
                cleaned.append(record)
        
        return cleaned
    
    @staticmethod
    def standardize_phone_numbers(data: List[Dict[str, Any]], 
                                phone_field: str = "phone") -> List[Dict[str, Any]]:
        """Standaryzuj numery telefonów"""
        def clean_phone(phone):
            if not isinstance(phone, str):
                return phone
            
            # Usuń wszystkie znaki oprócz cyfr i znaku +
            cleaned = re.sub(r'[^\d+]', '', phone)
            
            # Dodaj prefix +48 jeśli zaczyna się od 0
            if cleaned.startswith('0'):
                cleaned = '+48' + cleaned[1:]
            
            return cleaned
        
        return DataTransformer.transform_field(data, phone_field, clean_phone)

# Funkcje pomocnicze
@handle_database_errors("data_processing")
def process_model_data(model_instances: List[Any], 
                      processors: List[Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]]]) -> List[Dict[str, Any]]:
    """Przetwórz dane modelu przez pipeline procesorów"""
    # Konwertuj na słowniki
    data = []
    for instance in model_instances:
        if hasattr(instance, 'to_dict'):
            data.append(instance.to_dict())
        else:
            record = {}
            for column in instance.__table__.columns:
                record[column.name] = getattr(instance, column.name)
            data.append(record)
    
    # Zastosuj procesory
    for processor in processors:
        data = processor(data)
    
    return data

def create_data_summary(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Utwórz podsumowanie danych"""
    if not data:
        return {"total_records": 0}
    
    summary = {
        "total_records": len(data),
        "fields": list(data[0].keys()) if data else [],
        "field_stats": {}
    }
    
    # Statystyki dla każdego pola
    for field in summary["fields"]:
        field_values = [record.get(field) for record in data]
        
        summary["field_stats"][field] = {
            "null_count": sum(1 for v in field_values if v is None),
            "unique_count": len(set(v for v in field_values if v is not None)),
            "data_types": list(set(type(v).__name__ for v in field_values if v is not None))
        }
    
    return summary
