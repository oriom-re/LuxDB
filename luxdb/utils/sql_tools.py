
"""
Narzędzia do pracy z surowym SQL w LuxDB
"""

import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from .logging_utils import get_db_logger
from .error_handlers import QueryExecutionError, handle_database_errors

class SQLQueryBuilder:
    """Builder do tworzenia zapytań SQL"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Resetuj builder"""
        self._select_fields = []
        self._from_table = ""
        self._joins = []
        self._where_conditions = []
        self._group_by = []
        self._having_conditions = []
        self._order_by = []
        self._limit_count = None
        self._offset_count = None
        return self
    
    def select(self, *fields):
        """Dodaj pola SELECT"""
        self._select_fields.extend(fields)
        return self
    
    def from_table(self, table_name: str):
        """Ustaw tabelę FROM"""
        self._from_table = table_name
        return self
    
    def join(self, table: str, condition: str, join_type: str = "INNER"):
        """Dodaj JOIN"""
        self._joins.append(f"{join_type} JOIN {table} ON {condition}")
        return self
    
    def where(self, condition: str):
        """Dodaj warunek WHERE"""
        self._where_conditions.append(condition)
        return self
    
    def group_by(self, *fields):
        """Dodaj GROUP BY"""
        self._group_by.extend(fields)
        return self
    
    def having(self, condition: str):
        """Dodaj warunek HAVING"""
        self._having_conditions.append(condition)
        return self
    
    def order_by(self, field: str, direction: str = "ASC"):
        """Dodaj ORDER BY"""
        self._order_by.append(f"{field} {direction}")
        return self
    
    def limit(self, count: int):
        """Dodaj LIMIT"""
        self._limit_count = count
        return self
    
    def offset(self, count: int):
        """Dodaj OFFSET"""
        self._offset_count = count
        return self
    
    def build(self) -> str:
        """Zbuduj zapytanie SQL"""
        if not self._from_table:
            raise QueryExecutionError("FROM table is required")
        
        # SELECT
        select_clause = "SELECT " + (", ".join(self._select_fields) if self._select_fields else "*")
        
        # FROM
        from_clause = f"FROM {self._from_table}"
        
        # JOIN
        join_clause = " " + " ".join(self._joins) if self._joins else ""
        
        # WHERE
        where_clause = " WHERE " + " AND ".join(self._where_conditions) if self._where_conditions else ""
        
        # GROUP BY
        group_clause = " GROUP BY " + ", ".join(self._group_by) if self._group_by else ""
        
        # HAVING
        having_clause = " HAVING " + " AND ".join(self._having_conditions) if self._having_conditions else ""
        
        # ORDER BY
        order_clause = " ORDER BY " + ", ".join(self._order_by) if self._order_by else ""
        
        # LIMIT
        limit_clause = f" LIMIT {self._limit_count}" if self._limit_count else ""
        
        # OFFSET
        offset_clause = f" OFFSET {self._offset_count}" if self._offset_count else ""
        
        return select_clause + " " + from_clause + join_clause + where_clause + group_clause + having_clause + order_clause + limit_clause + offset_clause

class SQLTemplateEngine:
    """Silnik szablonów SQL"""
    
    @staticmethod
    def render_template(template: str, params: Dict[str, Any]) -> str:
        """Renderuj szablon SQL z parametrami"""
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            if isinstance(value, str):
                template = template.replace(placeholder, f"'{value}'")
            elif isinstance(value, (int, float)):
                template = template.replace(placeholder, str(value))
            elif isinstance(value, datetime):
                template = template.replace(placeholder, f"'{value.isoformat()}'")
            elif value is None:
                template = template.replace(placeholder, "NULL")
            else:
                template = template.replace(placeholder, str(value))
        
        return template
    
    @staticmethod
    def get_common_queries() -> Dict[str, str]:
        """Zwróć popularne szablony zapytań"""
        return {
            "count_records": "SELECT COUNT(*) as count FROM {table}",
            "table_info": "SELECT COUNT(*) as record_count, MAX({id_field}) as max_id FROM {table}",
            "recent_records": "SELECT * FROM {table} WHERE {date_field} >= '{start_date}' ORDER BY {date_field} DESC",
            "duplicate_check": "SELECT {field}, COUNT(*) as count FROM {table} GROUP BY {field} HAVING COUNT(*) > 1",
            "table_size": "SELECT COUNT(*) as rows, SUM(length({text_field})) as total_size FROM {table}",
            "active_records": "SELECT * FROM {table} WHERE {status_field} = 1 OR {status_field} = 'active'",
        }

class SQLAnalyzer:
    """Analizator zapytań SQL"""
    
    @staticmethod
    def analyze_query(sql: str) -> Dict[str, Any]:
        """Analizuj zapytanie SQL"""
        sql_upper = sql.upper().strip()
        
        analysis = {
            "type": SQLAnalyzer._get_query_type(sql_upper),
            "tables": SQLAnalyzer._extract_tables(sql),
            "is_read_only": SQLAnalyzer._is_read_only(sql_upper),
            "has_joins": "JOIN" in sql_upper,
            "has_subqueries": "(" in sql and "SELECT" in sql_upper,
            "complexity": SQLAnalyzer._assess_complexity(sql_upper)
        }
        
        return analysis
    
    @staticmethod
    def _get_query_type(sql_upper: str) -> str:
        """Określ typ zapytania"""
        if sql_upper.startswith("SELECT"):
            return "SELECT"
        elif sql_upper.startswith("INSERT"):
            return "INSERT"
        elif sql_upper.startswith("UPDATE"):
            return "UPDATE"
        elif sql_upper.startswith("DELETE"):
            return "DELETE"
        elif sql_upper.startswith("CREATE"):
            return "CREATE"
        elif sql_upper.startswith("DROP"):
            return "DROP"
        elif sql_upper.startswith("ALTER"):
            return "ALTER"
        else:
            return "OTHER"
    
    @staticmethod
    def _extract_tables(sql: str) -> List[str]:
        """Wyodrębnij nazwy tabel"""
        # Podstawowa ekstrakcja - można rozbudować
        pattern = r'\b(?:FROM|JOIN|INTO|UPDATE)\s+([a-zA-Z_]\w*)'
        matches = re.findall(pattern, sql, re.IGNORECASE)
        return list(set(matches))
    
    @staticmethod
    def _is_read_only(sql_upper: str) -> bool:
        """Sprawdź czy zapytanie jest tylko do odczytu"""
        write_operations = ["INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "TRUNCATE"]
        return not any(sql_upper.startswith(op) for op in write_operations)
    
    @staticmethod
    def _assess_complexity(sql_upper: str) -> str:
        """Oceń złożoność zapytania"""
        complexity_score = 0
        
        if "JOIN" in sql_upper:
            complexity_score += 1
        if "SUBQUERY" in sql_upper or sql_upper.count("SELECT") > 1:
            complexity_score += 2
        if "GROUP BY" in sql_upper:
            complexity_score += 1
        if "HAVING" in sql_upper:
            complexity_score += 1
        if "WINDOW" in sql_upper or "OVER" in sql_upper:
            complexity_score += 2
        
        if complexity_score == 0:
            return "SIMPLE"
        elif complexity_score <= 2:
            return "MEDIUM"
        else:
            return "COMPLEX"

@handle_database_errors("sql_execution")
def execute_sql_safely(engine: Engine, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Bezpieczne wykonanie SQL z logowaniem"""
    logger = get_db_logger()
    
    # Analizuj zapytanie
    analysis = SQLAnalyzer.analyze_query(sql)
    logger.logger.debug(f"Executing {analysis['type']} query on tables: {analysis['tables']}")
    
    start_time = datetime.now()
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            
            if analysis['is_read_only']:
                rows = result.fetchall()
                data = [dict(row._mapping) for row in rows]
                
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.log_query_execution(analysis['type'], ', '.join(analysis['tables']), len(data), execution_time)
                
                return data
            else:
                conn.commit()
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.log_query_execution(analysis['type'], ', '.join(analysis['tables']), result.rowcount, execution_time)
                
                return [{"affected_rows": result.rowcount}]
                
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        context = {
            'sql': sql,
            'params': params,
            'execution_time': execution_time,
            'analysis': analysis
        }
        raise QueryExecutionError(f"Failed to execute SQL: {str(e)}", context)

class SQLFormatter:
    """Formatter dla zapytań SQL"""
    
    @staticmethod
    def format_sql(sql: str, indent: str = "  ") -> str:
        """Sformatuj SQL z wcięciami"""
        keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 
                   'INNER JOIN', 'OUTER JOIN', 'GROUP BY', 'ORDER BY', 'HAVING', 
                   'LIMIT', 'OFFSET', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER']
        
        formatted = sql
        for keyword in keywords:
            formatted = re.sub(f'\\b{keyword}\\b', f'\n{keyword}', formatted, flags=re.IGNORECASE)
        
        lines = formatted.split('\n')
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if line:
                if any(line.upper().startswith(kw) for kw in keywords):
                    formatted_lines.append(line)
                else:
                    formatted_lines.append(indent + line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def minify_sql(sql: str) -> str:
        """Zminifikuj SQL usuwając zbędne spacje"""
        return re.sub(r'\s+', ' ', sql.strip())

def optimize_sql_query(sql: str) -> str:
    """Podstawowa optymalizacja zapytania SQL"""
    # Usuń zbędne spacje
    sql = re.sub(r'\s+', ' ', sql.strip())
    
    # Dodaj wskazówki optymalizacyjne dla SQLite
    if sql.upper().startswith('SELECT') and 'ORDER BY' in sql.upper():
        # Sugestia dodania indeksu w komentarzu
        sql += " -- Consider adding index on ORDER BY columns"
    
    return sql
