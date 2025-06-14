
"""
Narzędzia do eksportu i importu danych w LuxDB
"""

import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Type
from pathlib import Path
from .logging_utils import get_db_logger
from .error_handlers import LuxDBError, handle_database_errors

class ExportFormat:
    """Formaty eksportu"""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    SQL = "sql"

class DataExporter:
    """Eksporter danych do różnych formatów"""
    
    def __init__(self):
        self.logger = get_db_logger()
    
    @handle_database_errors("export_to_json")
    def export_to_json(self, data: List[Dict[str, Any]], output_path: str, 
                      pretty: bool = True) -> str:
        """Eksportuj dane do JSON"""
        processed_data = self._process_data_for_export(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(processed_data, f, indent=2, default=self._json_serializer, ensure_ascii=False)
            else:
                json.dump(processed_data, f, default=self._json_serializer, ensure_ascii=False)
        
        self.logger.log_database_operation("export_json", output_path, True, f"Records: {len(data)}")
        return output_path
    
    @handle_database_errors("export_to_csv")
    def export_to_csv(self, data: List[Dict[str, Any]], output_path: str,
                     delimiter: str = ",") -> str:
        """Eksportuj dane do CSV"""
        if not data:
            raise LuxDBError("No data to export")
        
        processed_data = self._process_data_for_export(data)
        fieldnames = processed_data[0].keys() if processed_data else []
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(processed_data)
        
        self.logger.log_database_operation("export_csv", output_path, True, f"Records: {len(data)}")
        return output_path
    
    @handle_database_errors("export_to_xml")
    def export_to_xml(self, data: List[Dict[str, Any]], output_path: str,
                     root_name: str = "data", record_name: str = "record") -> str:
        """Eksportuj dane do XML"""
        processed_data = self._process_data_for_export(data)
        
        root = ET.Element(root_name)
        
        for record in processed_data:
            record_elem = ET.SubElement(root, record_name)
            for key, value in record.items():
                field_elem = ET.SubElement(record_elem, str(key))
                field_elem.text = str(value) if value is not None else ""
        
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        self.logger.log_database_operation("export_xml", output_path, True, f"Records: {len(data)}")
        return output_path
    
    @handle_database_errors("export_to_sql")
    def export_to_sql(self, data: List[Dict[str, Any]], table_name: str,
                     output_path: str, include_create: bool = True) -> str:
        """Eksportuj dane do pliku SQL"""
        if not data:
            raise LuxDBError("No data to export")
        
        processed_data = self._process_data_for_export(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if include_create:
                f.write(self._generate_create_table_sql(processed_data[0], table_name))
                f.write("\n\n")
            
            for record in processed_data:
                f.write(self._generate_insert_sql(record, table_name))
                f.write("\n")
        
        self.logger.log_database_operation("export_sql", output_path, True, f"Records: {len(data)}")
        return output_path
    
    def _process_data_for_export(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Przetwórz dane przed eksportem"""
        processed = []
        
        for record in data:
            processed_record = {}
            for key, value in record.items():
                if isinstance(value, datetime):
                    processed_record[key] = value.isoformat()
                elif value is None:
                    processed_record[key] = None
                else:
                    processed_record[key] = value
            processed.append(processed_record)
        
        return processed
    
    def _json_serializer(self, obj):
        """Serializer JSON dla specjalnych typów"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)
    
    def _generate_create_table_sql(self, sample_record: Dict[str, Any], table_name: str) -> str:
        """Generuj SQL CREATE TABLE"""
        columns = []
        
        for key, value in sample_record.items():
            if isinstance(value, int):
                col_type = "INTEGER"
            elif isinstance(value, float):
                col_type = "REAL"
            elif isinstance(value, bool):
                col_type = "BOOLEAN"
            elif isinstance(value, datetime) or (isinstance(value, str) and 'T' in value):
                col_type = "TIMESTAMP"
            else:
                col_type = "TEXT"
            
            columns.append(f"  {key} {col_type}")
        
        return f"CREATE TABLE IF NOT EXISTS {table_name} (\n" + ",\n".join(columns) + "\n);"
    
    def _generate_insert_sql(self, record: Dict[str, Any], table_name: str) -> str:
        """Generuj SQL INSERT"""
        columns = ", ".join(record.keys())
        values = []
        
        for value in record.values():
            if value is None:
                values.append("NULL")
            elif isinstance(value, str):
                # Escape single quotes
                escaped_value = value.replace("'", "''")
                values.append(f"'{escaped_value}'")
            elif isinstance(value, bool):
                values.append("1" if value else "0")
            else:
                values.append(str(value))
        
        values_str = ", ".join(values)
        return f"INSERT INTO {table_name} ({columns}) VALUES ({values_str});"

class DataImporter:
    """Importer danych z różnych formatów"""
    
    def __init__(self):
        self.logger = get_db_logger()
    
    @handle_database_errors("import_from_json")
    def import_from_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Importuj dane z JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Konwertuj z powrotem datetime strings
        processed_data = self._process_data_for_import(data)
        
        self.logger.log_database_operation("import_json", file_path, True, f"Records: {len(processed_data)}")
        return processed_data
    
    @handle_database_errors("import_from_csv")
    def import_from_csv(self, file_path: str, delimiter: str = ",") -> List[Dict[str, Any]]:
        """Importuj dane z CSV"""
        data = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                data.append(dict(row))
        
        processed_data = self._process_data_for_import(data)
        
        self.logger.log_database_operation("import_csv", file_path, True, f"Records: {len(processed_data)}")
        return processed_data
    
    def _process_data_for_import(self, data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Przetwórz dane po imporcie"""
        if isinstance(data, dict):
            # Jeśli to słownik z tabelami
            all_records = []
            for table_data in data.values():
                if isinstance(table_data, list):
                    all_records.extend(table_data)
            data = all_records
        
        processed = []
        
        for record in data:
            processed_record = {}
            for key, value in record.items():
                # Próbuj konwertować datetime strings
                if isinstance(value, str) and self._is_datetime_string(value):
                    try:
                        processed_record[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except:
                        processed_record[key] = value
                elif value == "NULL" or value == "":
                    processed_record[key] = None
                else:
                    processed_record[key] = value
            processed.append(processed_record)
        
        return processed
    
    def _is_datetime_string(self, value: str) -> bool:
        """Sprawdź czy string to datetime"""
        return 'T' in value and (':' in value or '.' in value)

# Funkcje pomocnicze
def export_model_data(model_instances: List[Any], format: str, output_path: str,
                     table_name: Optional[str] = None) -> str:
    """Eksportuj dane modelu do pliku"""
    exporter = DataExporter()
    
    # Konwertuj instancje modeli na słowniki
    data = []
    for instance in model_instances:
        if hasattr(instance, 'to_dict'):
            data.append(instance.to_dict())
        else:
            # Fallback - użyj kolumn tabeli
            record = {}
            for column in instance.__table__.columns:
                record[column.name] = getattr(instance, column.name)
            data.append(record)
    
    # Eksportuj w odpowiednim formacie
    if format.lower() == ExportFormat.JSON:
        return exporter.export_to_json(data, output_path)
    elif format.lower() == ExportFormat.CSV:
        return exporter.export_to_csv(data, output_path)
    elif format.lower() == ExportFormat.XML:
        return exporter.export_to_xml(data, output_path)
    elif format.lower() == ExportFormat.SQL:
        if not table_name:
            table_name = model_instances[0].__tablename__ if model_instances else "exported_data"
        return exporter.export_to_sql(data, table_name, output_path)
    else:
        raise LuxDBError(f"Unsupported export format: {format}")

def create_backup_filename(db_name: str, format: str, timestamp: Optional[datetime] = None) -> str:
    """Utwórz nazwę pliku backup"""
    if timestamp is None:
        timestamp = datetime.now()
    
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    return f"{db_name}_backup_{timestamp_str}.{format}"
