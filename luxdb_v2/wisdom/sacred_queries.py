
"""
🔍 SacredQueries - System Świętych Zapytań

Zaawansowane narzędzia do budowania i wykonywania zapytań w systemie astralnym
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import re


@dataclass
class QueryResult:
    """Wynik świętego zapytania"""
    success: bool
    data: Any
    query_time: float
    total_results: int
    filtered_results: int
    metadata: Dict[str, Any]


class QueryBuilder:
    """Budowniczy świętych zapytań"""
    
    def __init__(self):
        self.conditions: List[Dict[str, Any]] = []
        self.sort_by: Optional[str] = None
        self.sort_direction: str = 'asc'
        self.limit_value: Optional[int] = None
        self.offset_value: int = 0
    
    def where(self, field: str, operator: str = 'eq', value: Any = None) -> 'QueryBuilder':
        """
        Dodaje warunek WHERE
        
        Args:
            field: Nazwa pola
            operator: Operator (eq, ne, gt, lt, gte, lte, in, contains, regex)
            value: Wartość do porównania
            
        Returns:
            Self dla method chaining
        """
        self.conditions.append({
            'field': field,
            'operator': operator,
            'value': value
        })
        return self
    
    def equals(self, field: str, value: Any) -> 'QueryBuilder':
        """Shortcut dla equals"""
        return self.where(field, 'eq', value)
    
    def not_equals(self, field: str, value: Any) -> 'QueryBuilder':
        """Shortcut dla not equals"""
        return self.where(field, 'ne', value)
    
    def greater_than(self, field: str, value: Any) -> 'QueryBuilder':
        """Shortcut dla greater than"""
        return self.where(field, 'gt', value)
    
    def less_than(self, field: str, value: Any) -> 'QueryBuilder':
        """Shortcut dla less than"""
        return self.where(field, 'lt', value)
    
    def contains(self, field: str, value: str) -> 'QueryBuilder':
        """Shortcut dla contains"""
        return self.where(field, 'contains', value)
    
    def in_list(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """Shortcut dla in list"""
        return self.where(field, 'in', values)
    
    def matches_regex(self, field: str, pattern: str) -> 'QueryBuilder':
        """Shortcut dla regex match"""
        return self.where(field, 'regex', pattern)
    
    def order_by(self, field: str, direction: str = 'asc') -> 'QueryBuilder':
        """
        Sortowanie wyników
        
        Args:
            field: Pole do sortowania
            direction: Kierunek (asc, desc)
            
        Returns:
            Self dla method chaining
        """
        self.sort_by = field
        self.sort_direction = direction.lower()
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """
        Ogranicza liczbę wyników
        
        Args:
            count: Maksymalna liczba wyników
            
        Returns:
            Self dla method chaining
        """
        self.limit_value = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """
        Pomija pierwsze N wyników
        
        Args:
            count: Liczba wyników do pominięcia
            
        Returns:
            Self dla method chaining
        """
        self.offset_value = count
        return self
    
    def build(self) -> Dict[str, Any]:
        """Buduje finalną strukturę zapytania"""
        return {
            'conditions': self.conditions,
            'sort_by': self.sort_by,
            'sort_direction': self.sort_direction,
            'limit': self.limit_value,
            'offset': self.offset_value
        }


class SacredQueries:
    """
    System świętych zapytań - zaawansowane wyszukiwanie i filtrowanie
    """
    
    def __init__(self, astral_engine=None):
        self.engine = astral_engine
        self.query_history: List[Dict[str, Any]] = []
    
    def create_query(self) -> QueryBuilder:
        """
        Tworzy nowy budowniczy zapytań
        
        Returns:
            Nowy QueryBuilder
        """
        return QueryBuilder()
    
    def execute_query(self, realm_name: str, query: Union[QueryBuilder, Dict[str, Any]], intention: str = "sacred_search") -> QueryResult:
        """
        Wykonuje święte zapytanie w wymiarze
        
        Args:
            realm_name: Nazwa wymiaru
            query: QueryBuilder lub słownik z zapytaniem
            intention: Intencja zapytania
            
        Returns:
            Wynik zapytania
        """
        start_time = datetime.now()
        
        try:
            # Pobierz wymiar
            if self.engine:
                realm = self.engine.get_realm(realm_name)
            else:
                raise ValueError("Brak dostępu do astral engine")
            
            # Sprawdź czy wymiar obsługuje zapytania
            if not hasattr(realm, 'manifestation'):
                return QueryResult(
                    success=False,
                    data=None,
                    query_time=0,
                    total_results=0,
                    filtered_results=0,
                    metadata={'error': 'Wymiar nie obsługuje zapytań'}
                )
            
            # Konwertuj QueryBuilder do słownika
            if isinstance(query, QueryBuilder):
                query_dict = query.build()
            else:
                query_dict = query
            
            # Pobierz wszystkie byty
            all_beings = list(realm.manifestation.active_beings.values())
            total_results = len(all_beings)
            
            # Zastosuj filtry
            filtered_beings = self._apply_filters(all_beings, query_dict['conditions'])
            
            # Sortowanie
            if query_dict['sort_by']:
                filtered_beings = self._apply_sorting(filtered_beings, query_dict['sort_by'], query_dict['sort_direction'])
            
            # Paginacja
            offset = query_dict.get('offset', 0)
            limit = query_dict.get('limit')
            
            if offset > 0:
                filtered_beings = filtered_beings[offset:]
            
            if limit:
                filtered_beings = filtered_beings[:limit]
            
            # Konwertuj do słowników
            results_data = [being.get_status() for being in filtered_beings]
            
            query_time = (datetime.now() - start_time).total_seconds()
            
            # Zapisz w historii
            self._save_query_history(realm_name, query_dict, intention, query_time, len(results_data))
            
            return QueryResult(
                success=True,
                data=results_data,
                query_time=query_time,
                total_results=total_results,
                filtered_results=len(results_data),
                metadata={
                    'realm': realm_name,
                    'intention': intention,
                    'conditions_applied': len(query_dict['conditions']),
                    'sorted': bool(query_dict['sort_by'])
                }
            )
            
        except Exception as e:
            query_time = (datetime.now() - start_time).total_seconds()
            
            return QueryResult(
                success=False,
                data=None,
                query_time=query_time,
                total_results=0,
                filtered_results=0,
                metadata={'error': str(e)}
            )
    
    def _apply_filters(self, beings: List, conditions: List[Dict[str, Any]]) -> List:
        """Stosuje filtry do listy bytów"""
        if not conditions:
            return beings
        
        filtered = []
        
        for being in beings:
            matches = True
            
            for condition in conditions:
                field = condition['field']
                operator = condition['operator']
                value = condition['value']
                
                # Pobierz wartość z bytu
                being_value = self._get_field_value(being, field)
                
                # Sprawdź warunek
                if not self._check_condition(being_value, operator, value):
                    matches = False
                    break
            
            if matches:
                filtered.append(being)
        
        return filtered
    
    def _get_field_value(self, being, field: str):
        """Pobiera wartość pola z bytu"""
        # Sprawdź w esencji
        if hasattr(being.essence, field):
            return getattr(being.essence, field)
        
        # Sprawdź w atrybutach
        if field in being.attributes:
            return being.attributes[field]
        
        # Sprawdź w specjalnych polach
        if field == 'memory_count':
            return len(being.memories)
        elif field == 'age_minutes':
            if being.essence.created_at:
                return (datetime.now() - being.essence.created_at).total_seconds() / 60
            return 0
        
        return None
    
    def _check_condition(self, being_value: Any, operator: str, condition_value: Any) -> bool:
        """Sprawdza czy wartość spełnia warunek"""
        if being_value is None:
            return operator == 'eq' and condition_value is None
        
        try:
            if operator == 'eq':
                return being_value == condition_value
            elif operator == 'ne':
                return being_value != condition_value
            elif operator == 'gt':
                return being_value > condition_value
            elif operator == 'lt':
                return being_value < condition_value
            elif operator == 'gte':
                return being_value >= condition_value
            elif operator == 'lte':
                return being_value <= condition_value
            elif operator == 'in':
                return being_value in condition_value
            elif operator == 'contains':
                return str(condition_value).lower() in str(being_value).lower()
            elif operator == 'regex':
                return bool(re.search(condition_value, str(being_value)))
            else:
                return False
        except (TypeError, ValueError):
            return False
    
    def _apply_sorting(self, beings: List, sort_by: str, direction: str) -> List:
        """Sortuje listę bytów"""
        try:
            reverse = direction.lower() == 'desc'
            
            return sorted(
                beings,
                key=lambda being: self._get_field_value(being, sort_by) or '',
                reverse=reverse
            )
        except Exception:
            return beings
    
    def _save_query_history(self, realm_name: str, query: Dict, intention: str, query_time: float, results_count: int):
        """Zapisuje zapytanie w historii"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'realm': realm_name,
            'intention': intention,
            'query': query,
            'query_time': query_time,
            'results_count': results_count
        }
        
        self.query_history.append(history_entry)
        
        # Ogranicz historię do 100 ostatnich zapytań
        if len(self.query_history) > 100:
            self.query_history = self.query_history[-100:]
    
    def get_query_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Zwraca historię zapytań"""
        return self.query_history[-limit:]
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki zapytań"""
        if not self.query_history:
            return {
                'total_queries': 0,
                'average_time': 0,
                'most_used_realms': [],
                'most_used_intentions': []
            }
        
        total_time = sum(q['query_time'] for q in self.query_history)
        average_time = total_time / len(self.query_history)
        
        # Najczęściej używane realms
        realm_counts = {}
        for q in self.query_history:
            realm = q['realm']
            realm_counts[realm] = realm_counts.get(realm, 0) + 1
        
        most_used_realms = sorted(realm_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Najczęściej używane intentions
        intention_counts = {}
        for q in self.query_history:
            intention = q['intention']
            intention_counts[intention] = intention_counts.get(intention, 0) + 1
        
        most_used_intentions = sorted(intention_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_queries': len(self.query_history),
            'average_time': round(average_time, 3),
            'most_used_realms': most_used_realms,
            'most_used_intentions': most_used_intentions,
            'recent_performance': [
                {
                    'timestamp': q['timestamp'],
                    'time': q['query_time'],
                    'results': q['results_count']
                }
                for q in self.query_history[-10:]
            ]
        }
    
    def clear_history(self) -> int:
        """Czyści historię zapytań"""
        count = len(self.query_history)
        self.query_history.clear()
        return count
    
    # Gotowe zapytania dla typowych przypadków
    def find_enlightened_beings(self, realm_name: str) -> QueryResult:
        """Znajduje oświecone byty"""
        query = self.create_query().equals('consciousness_level', 'enlightened')
        return self.execute_query(realm_name, query, 'find_enlightened')
    
    def find_high_energy_beings(self, realm_name: str, min_energy: float = 80.0) -> QueryResult:
        """Znajduje byty z wysoką energią"""
        query = self.create_query().greater_than('energy_level', min_energy)
        return self.execute_query(realm_name, query, 'find_high_energy')
    
    def find_recent_beings(self, realm_name: str, hours: int = 24) -> QueryResult:
        """Znajduje byty utworzone w ostatnich godzinach"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        query = self.create_query().greater_than('created_at', cutoff_time)
        return self.execute_query(realm_name, query, 'find_recent')
    
    def find_beings_by_name_pattern(self, realm_name: str, pattern: str) -> QueryResult:
        """Znajduje byty pasujące do wzorca nazwy"""
        query = self.create_query().contains('name', pattern)
        return self.execute_query(realm_name, query, 'find_by_name_pattern')
    
    def find_active_beings(self, realm_name: str) -> QueryResult:
        """Znajduje aktywne byty (z wysoką energią i niedawnymi medytacjami)"""
        query = (self.create_query()
                .greater_than('energy_level', 50.0)
                .order_by('last_meditation', 'desc'))
        return self.execute_query(realm_name, query, 'find_active')
