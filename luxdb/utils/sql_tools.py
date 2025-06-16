"""
Narzędzia SQL dla LuxDB
"""

from typing import Dict, List, Any, Optional, Union
from sqlalchemy import text
from ..config import Base
from .error_handlers import handle_database_errors

class QueryBuilder:
    """Konstruktor zapytań SQL z intuicyjnym API"""

    def __init__(self, model_class=None):
        self.model_class = model_class
        self.session = None
        self._select_columns = []
        self._joins = []
        self._filters = []
        self._order_by = []
        self._group_by = []
        self._having = []
        self._limit_value = None
        self._offset_value = None

    def set_session(self, session):
        """Ustaw sesję SQLAlchemy"""
        self.session = session
        return self

    def select(self, *columns):
        """Wybierz kolumny do zapytania"""
        if columns:
            self._select_columns = list(columns)
        else:
            self._select_columns = [self.model_class] if self.model_class else []
        return self

    def filter(self, *conditions):
        """Dodaj warunki WHERE"""
        self._filters.extend(conditions)
        return self

    def join(self, *args, **kwargs):
        """Dodaj JOIN do zapytania"""
        self._joins.extend(args)
        return self

    def order_by(self, *columns):
        """Dodaj sortowanie"""
        self._order_by.extend(columns)
        return self

    def group_by(self, *columns):
        """Dodaj grupowanie"""
        self._group_by.extend(columns)
        return self

    def having(self, *conditions):
        """Dodaj warunki HAVING"""
        self._having.extend(conditions)
        return self

    def limit(self, count):
        """Ogranicz liczbę wyników"""
        self._limit_value = count
        return self

    def offset(self, count):
        """Pomiń określoną liczbę wyników"""
        self._offset_value = count
        return self

    def all(self):
        """Wykonaj zapytanie i zwróć wszystkie wyniki"""
        query = self._build_query()
        return query.all()

    def first(self):
        """Wykonaj zapytanie i zwróć pierwszy wynik"""
        query = self._build_query()
        return query.first()

    def count(self):
        """Policz wyniki"""
        from sqlalchemy import func
        if self.model_class:
            query = self.session.query(func.count(self.model_class.id))
        else:
            query = self.session.query(func.count())

        # Dodaj filtry
        for condition in self._filters:
            query = query.filter(condition)

        # Dodaj joins
        for join_target in self._joins:
            query = query.join(join_target)

        return query.scalar()

    def _build_query(self):
        """Zbuduj zapytanie SQLAlchemy"""
        if not self.session:
            raise ValueError("Sesja nie została ustawiona")

        # Wybierz kolumny
        if self._select_columns:
            query = self.session.query(*self._select_columns)
        elif self.model_class:
            query = self.session.query(self.model_class)
        else:
            raise ValueError("Nie określono modelu ani kolumn")

        # Dodaj joins
        for join_target in self._joins:
            query = query.join(join_target)

        # Dodaj filtry
        for condition in self._filters:
            query = query.filter(condition)

        # Dodaj grupowanie
        if self._group_by:
            query = query.group_by(*self._group_by)

        # Dodaj warunki HAVING
        for condition in self._having:
            query = query.having(condition)

        # Dodaj sortowanie
        if self._order_by:
            query = query.order_by(*self._order_by)

        # Dodaj limit i offset
        if self._limit_value is not None:
            query = query.limit(self._limit_value)

        if self._offset_value is not None:
            query = query.offset(self._offset_value)

        return query

    def reset(self):
        """Zresetuj konstruktor zapytań"""
        self._select_columns = []
        self._joins = []
        self._filters = []
        self._order_by = []
        self._group_by = []
        self._having = []
        self._limit_value = None
        self._offset_value = None
        return self

class SQLQueryBuilder:
    """Konstruktor zapytań SQL"""

    def __init__(self):
        self.query_parts = {
            'select': [],
            'from': '',
            'joins': [],
            'where': [],
            'group_by': [],
            'having': [],
            'order_by': [],
            'limit': None
        }

    def select(self, *columns):
        self.query_parts['select'] = list(columns)
        return self

    def from_table(self, table):
        self.query_parts['from'] = table
        return self

    def where(self, condition):
        self.query_parts['where'].append(condition)
        return self

    def build(self):
        """Zbuduj zapytanie SQL"""
        sql_parts = []

        # SELECT
        if self.query_parts['select']:
            sql_parts.append(f"SELECT {', '.join(self.query_parts['select'])}")

        # FROM
        if self.query_parts['from']:
            sql_parts.append(f"FROM {self.query_parts['from']}")

        # WHERE
        if self.query_parts['where']:
            sql_parts.append(f"WHERE {' AND '.join(self.query_parts['where'])}")

        return ' '.join(sql_parts)

class SQLTemplateEngine:
    """Silnik szablonów SQL"""

    def __init__(self):
        self.templates = {}

    def add_template(self, name: str, template: str):
        """Dodaj szablon SQL"""
        self.templates[name] = template

    def render(self, template_name: str, **kwargs) -> str:
        """Renderuj szablon z parametrami"""
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")

        template = self.templates[template_name]
        return template.format(**kwargs)

class SQLAnalyzer:
    """Analizator zapytań SQL"""

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analizuj zapytanie SQL"""
        return {
            'query': query,
            'type': self._get_query_type(query),
            'tables': self._extract_tables(query),
            'complexity': 'medium'
        }

    def _get_query_type(self, query: str) -> str:
        query_upper = query.strip().upper()
        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        return 'UNKNOWN'

    def _extract_tables(self, query: str) -> List[str]:
        # Prosta ekstrakcja tabel - można rozszerzyć
        return []

class SQLFormatter:
    """Formatowanie zapytań SQL"""

    def format(self, query: str, indent: str = "  ") -> str:
        """Formatuj zapytanie SQL"""
        lines = query.split('\n')
        formatted_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped:
                if any(stripped.upper().startswith(keyword) for keyword in ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY']):
                    formatted_lines.append(stripped)
                else:
                    formatted_lines.append(indent + stripped)

        return '\n'.join(formatted_lines)

    def minify(self, query: str) -> str:
        """Zminifikuj zapytanie SQL"""
        return ' '.join(query.split())