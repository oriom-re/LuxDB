
"""
🛠️ Function Generator - Generatywny System Budowania Funkcji

Dynamicznie tworzy, zarządza i przechowuje funkcje w bazie funkcyjnej
"""

import json
import inspect
import hashlib
import importlib
import types
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
import ast
import textwrap

from ..realms.base_realm import BaseRealm


class FunctionSpec:
    """Specyfikacja funkcji do wygenerowania"""
    
    def __init__(self, spec_data: Dict[str, Any]):
        self.name = spec_data.get('name', 'generated_function')
        self.description = spec_data.get('description', '')
        self.parameters = spec_data.get('parameters', [])
        self.return_type = spec_data.get('return_type', 'Any')
        self.category = spec_data.get('category', 'general')
        self.dependencies = spec_data.get('dependencies', [])
        self.code_template = spec_data.get('code_template')
        self.examples = spec_data.get('examples', [])
        
        # Metadane
        self.created_at = datetime.now()
        self.version = spec_data.get('version', '1.0.0')
        self.author = spec_data.get('author', 'FunctionGenerator')
        self.tags = spec_data.get('tags', [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje spec do słownika"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'return_type': self.return_type,
            'category': self.category,
            'dependencies': self.dependencies,
            'code_template': self.code_template,
            'examples': self.examples,
            'created_at': self.created_at.isoformat(),
            'version': self.version,
            'author': self.author,
            'tags': self.tags
        }


class GeneratedFunction:
    """Klasa reprezentująca wygenerowaną funkcję"""
    
    def __init__(self, spec: FunctionSpec, source_code: str, compiled_func: Callable):
        self.spec = spec
        self.source_code = source_code
        self.compiled_func = compiled_func
        
        # Metadane wykonania
        self.execution_count = 0
        self.last_executed = None
        self.average_execution_time = 0.0
        self.error_count = 0
        self.last_error = None
        
        # Hash funkcji dla wersjonowania
        self.function_hash = self._calculate_hash()
        
        # Status
        self.is_active = True
        self.created_at = datetime.now()
    
    def _calculate_hash(self) -> str:
        """Oblicza hash funkcji na podstawie kodu źródłowego"""
        return hashlib.sha256(self.source_code.encode()).hexdigest()[:16]
    
    def execute(self, *args, **kwargs) -> Any:
        """Wykonuje funkcję z monitorowaniem"""
        import time
        
        start_time = time.time()
        
        try:
            result = self.compiled_func(*args, **kwargs)
            
            # Aktualizuj statystyki
            execution_time = time.time() - start_time
            self.execution_count += 1
            self.last_executed = datetime.now()
            self.average_execution_time = (
                (self.average_execution_time * (self.execution_count - 1) + execution_time) 
                / self.execution_count
            )
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.last_error = {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'args': str(args),
                'kwargs': str(kwargs)
            }
            raise
    
    def get_info(self) -> Dict[str, Any]:
        """Zwraca informacje o funkcji"""
        return {
            'name': self.spec.name,
            'description': self.spec.description,
            'parameters': self.spec.parameters,
            'return_type': self.spec.return_type,
            'category': self.spec.category,
            'function_hash': self.function_hash,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'execution_count': self.execution_count,
            'last_executed': self.last_executed.isoformat() if self.last_executed else None,
            'average_execution_time': self.average_execution_time,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'source_code': self.source_code
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje funkcję do słownika dla bazy danych"""
        return {
            'spec': self.spec.to_dict(),
            'source_code': self.source_code,
            'function_hash': self.function_hash,
            'execution_stats': {
                'execution_count': self.execution_count,
                'average_execution_time': self.average_execution_time,
                'error_count': self.error_count,
                'last_executed': self.last_executed.isoformat() if self.last_executed else None,
                'last_error': self.last_error
            },
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }


class CodeTemplateEngine:
    """Silnik szablonów kodu dla generowania funkcji"""
    
    def __init__(self):
        self.templates = {
            'basic_function': self._basic_function_template,
            'api_call': self._api_call_template,
            'data_processor': self._data_processor_template,
            'validator': self._validator_template,
            'formatter': self._formatter_template,
            'calculator': self._calculator_template
        }
    
    def generate_code(self, spec: FunctionSpec) -> str:
        """Generuje kod funkcji na podstawie specyfikacji"""
        
        # Wybierz szablon na podstawie kategorii lub opisu
        template_name = self._select_template(spec)
        template_func = self.templates.get(template_name, self.templates['basic_function'])
        
        # Wygeneruj kod
        code = template_func(spec)
        
        # Formatuj i zwaliduj
        formatted_code = self._format_code(code)
        self._validate_code(formatted_code)
        
        return formatted_code
    
    def _select_template(self, spec: FunctionSpec) -> str:
        """Wybiera odpowiedni szablon dla funkcji"""
        description_lower = spec.description.lower()
        category_lower = spec.category.lower()
        
        if 'api' in description_lower or 'request' in description_lower:
            return 'api_call'
        elif 'validate' in description_lower or 'check' in description_lower:
            return 'validator'
        elif 'format' in description_lower or 'convert' in description_lower:
            return 'formatter'
        elif 'calculate' in description_lower or 'compute' in description_lower:
            return 'calculator'
        elif 'process' in description_lower or 'transform' in description_lower:
            return 'data_processor'
        else:
            return 'basic_function'
    
    def _basic_function_template(self, spec: FunctionSpec) -> str:
        """Podstawowy szablon funkcji"""
        
        # Przygotuj parametry
        params = []
        for param in spec.parameters:
            param_name = param.get('name', 'param')
            param_type = param.get('type', 'Any')
            default_value = param.get('default')
            
            if default_value is not None:
                params.append(f"{param_name}: {param_type} = {repr(default_value)}")
            else:
                params.append(f"{param_name}: {param_type}")
        
        params_str = ', '.join(params)
        
        # Podstawowa implementacja
        basic_impl = """
    # Podstawowa implementacja
    result = {
        'function_name': '{}',
        'parameters': locals(),
        'timestamp': datetime.now().isoformat(),
        'message': 'Funkcja wykonana pomyślnie'
    }
    
    return result
        """.format(spec.name)
        
        return f"""
from typing import Any, Dict
from datetime import datetime

def {spec.name}({params_str}) -> {spec.return_type}:
    '''
    {spec.description}
    
    Wygenerowane automatycznie przez FunctionGenerator
    '''
    {basic_impl}
"""
    
    def _api_call_template(self, spec: FunctionSpec) -> str:
        """Szablon dla funkcji API"""
        params_str = ', '.join([f"{p.get('name', 'param')}: {p.get('type', 'Any')}" for p in spec.parameters])
        
        return f"""
import requests
from typing import Any, Dict
from datetime import datetime

def {spec.name}({params_str}) -> {spec.return_type}:
    '''
    {spec.description}
    
    API call function - wygenerowane automatycznie
    '''
    try:
        # Podstawowe wywołanie API
        response = requests.get('https://api.example.com/endpoint', 
                              params=locals(),
                              timeout=30)
        response.raise_for_status()
        
        return {{
            'success': True,
            'data': response.json(),
            'status_code': response.status_code,
            'function_name': '{spec.name}'
        }}
        
    except Exception as e:
        return {{
            'success': False,
            'error': str(e),
            'function_name': '{spec.name}'
        }}
"""
    
    def _data_processor_template(self, spec: FunctionSpec) -> str:
        """Szablon dla funkcji przetwarzania danych"""
        params_str = ', '.join([f"{p.get('name', 'data')}: {p.get('type', 'Any')}" for p in spec.parameters])
        
        return f"""
from typing import Any, Dict, List
from datetime import datetime

def {spec.name}({params_str}) -> {spec.return_type}:
    '''
    {spec.description}
    
    Data processor function - wygenerowane automatycznie
    '''
    processed_data = {{}}
    
    # Podstawowe przetwarzanie danych
    for key, value in locals().items():
        if key != 'processed_data':
            processed_data[f'processed_{{key}}'] = value
    
    return {{
        'success': True,
        'processed_data': processed_data,
        'timestamp': datetime.now().isoformat(),
        'function_name': '{spec.name}'
    }}
"""
    
    def _validator_template(self, spec: FunctionSpec) -> str:
        """Szablon dla funkcji walidacji"""
        params_str = ', '.join([f"{p.get('name', 'value')}: {p.get('type', 'Any')}" for p in spec.parameters])
        
        return f"""
from typing import Any, Dict, List
from datetime import datetime

def {spec.name}({params_str}) -> {spec.return_type}:
    '''
    {spec.description}
    
    Validator function - wygenerowane automatycznie
    '''
    validation_results = []
    
    # Podstawowa walidacja
    for key, value in locals().items():
        if key != 'validation_results':
            validation_results.append({{
                'field': key,
                'value': value,
                'valid': value is not None,
                'message': 'OK' if value is not None else 'Wartość nie może być None'
            }})
    
    is_valid = all(r['valid'] for r in validation_results)
    
    return {{
        'valid': is_valid,
        'results': validation_results,
        'timestamp': datetime.now().isoformat(),
        'function_name': '{spec.name}'
    }}
"""
    
    def _formatter_template(self, spec: FunctionSpec) -> str:
        """Szablon dla funkcji formatowania"""
        params_str = ', '.join([f"{p.get('name', 'data')}: {p.get('type', 'Any')}" for p in spec.parameters])
        
        return f"""
from typing import Any, Dict
from datetime import datetime
import json

def {spec.name}({params_str}) -> {spec.return_type}:
    '''
    {spec.description}
    
    Formatter function - wygenerowane automatycznie
    '''
    try:
        # Podstawowe formatowanie
        formatted_data = {{}}
        
        for key, value in locals().items():
            if key != 'formatted_data':
                formatted_data[key] = str(value) if value is not None else ''
        
        return {{
            'success': True,
            'formatted_data': formatted_data,
            'json_output': json.dumps(formatted_data, indent=2),
            'timestamp': datetime.now().isoformat(),
            'function_name': '{spec.name}'
        }}
        
    except Exception as e:
        return {{
            'success': False,
            'error': str(e),
            'function_name': '{spec.name}'
        }}
"""
    
    def _calculator_template(self, spec: FunctionSpec) -> str:
        """Szablon dla funkcji obliczeniowych"""
        params_str = ', '.join([f"{p.get('name', 'value')}: {p.get('type', 'float')}" for p in spec.parameters])
        
        return f"""
from typing import Any, Dict
from datetime import datetime
import math

def {spec.name}({params_str}) -> {spec.return_type}:
    '''
    {spec.description}
    
    Calculator function - wygenerowane automatycznie
    '''
    try:
        # Podstawowe obliczenia
        values = [v for k, v in locals().items() if isinstance(v, (int, float))]
        
        if values:
            result = {{
                'sum': sum(values),
                'average': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }}
        else:
            result = {{'message': 'Brak wartości numerycznych do obliczenia'}}
        
        return {{
            'success': True,
            'calculation_result': result,
            'input_values': values,
            'timestamp': datetime.now().isoformat(),
            'function_name': '{spec.name}'
        }}
        
    except Exception as e:
        return {{
            'success': False,
            'error': str(e),
            'function_name': '{spec.name}'
        }}
"""
    
    def _format_code(self, code: str) -> str:
        """Formatuje kod funkcji"""
        return textwrap.dedent(code).strip()
    
    def _validate_code(self, code: str) -> bool:
        """Waliduje składnię kodu"""
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            raise ValueError(f"Błąd składni w wygenerowanym kodzie: {e}")


class FunctionDatabase:
    """Baza danych funkcji - przechowuje wygenerowane funkcje"""
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        self.realm_name = 'functions'
        self._ensure_functions_realm()
    
    def _ensure_functions_realm(self) -> None:
        """Zapewnia istnienie realm'u dla funkcji"""
        if self.realm_name not in self.engine.realms:
            self.engine.create_realm(self.realm_name, 'sqlite://db/functions.db')
    
    def save_function(self, generated_func: GeneratedFunction) -> str:
        """Zapisuje funkcję w bazie"""
        try:
            realm = self.engine.get_realm(self.realm_name)
            
            # Przygotuj dane do zapisu
            function_data = {
                'soul_name': generated_func.spec.name,
                'function_hash': generated_func.function_hash,
                'category': generated_func.spec.category,
                'description': generated_func.spec.description,
                'function_data': generated_func.to_dict(),
                'is_active': generated_func.is_active,
                'created_at': generated_func.created_at.isoformat()
            }
            
            # Zapisz w realm
            being = realm.manifest(function_data)
            
            self.engine.logger.info(f"🛠️ Funkcja '{generated_func.spec.name}' zapisana w bazie")
            return being.soul_id if hasattr(being, 'soul_id') else str(being)
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd zapisu funkcji: {e}")
            raise
    
    def load_function(self, function_name: str) -> Optional[GeneratedFunction]:
        """Ładuje funkcję z bazy po nazwie"""
        try:
            realm = self.engine.get_realm(self.realm_name)
            
            # Znajdź funkcję
            results = realm.contemplate('find_function', soul_name=function_name, is_active=True)
            
            if not results:
                return None
            
            # Rekonstruuj funkcję z danych
            function_being = results[0]
            function_data = function_being.function_data
            
            # Odtwórz spec
            spec = FunctionSpec(function_data['spec'])
            
            # Skompiluj kod
            compiled_func = self._compile_function_code(function_data['source_code'], spec.name)
            
            # Utwórz obiekt funkcji
            generated_func = GeneratedFunction(spec, function_data['source_code'], compiled_func)
            
            # Przywróć statystyki
            stats = function_data.get('execution_stats', {})
            generated_func.execution_count = stats.get('execution_count', 0)
            generated_func.average_execution_time = stats.get('average_execution_time', 0.0)
            generated_func.error_count = stats.get('error_count', 0)
            generated_func.last_error = stats.get('last_error')
            
            if stats.get('last_executed'):
                generated_func.last_executed = datetime.fromisoformat(stats['last_executed'])
            
            return generated_func
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd ładowania funkcji '{function_name}': {e}")
            return None
    
    def _compile_function_code(self, source_code: str, function_name: str) -> Callable:
        """Kompiluje kod funkcji do obiektu callable"""
        try:
            # Utwórz namespace dla funkcji
            func_namespace = {}
            
            # Wykonaj kod w namespace
            exec(source_code, func_namespace)
            
            # Pobierz funkcję z namespace
            if function_name in func_namespace:
                return func_namespace[function_name]
            else:
                raise ValueError(f"Funkcja '{function_name}' nie znaleziona w kodzie")
                
        except Exception as e:
            raise ValueError(f"Błąd kompilacji funkcji '{function_name}': {e}")
    
    def list_functions(self, category: str = None, active_only: bool = True) -> List[Dict[str, Any]]:
        """Zwraca listę funkcji w bazie"""
        try:
            realm = self.engine.get_realm(self.realm_name)
            
            # Przygotuj warunki wyszukiwania
            conditions = {}
            if active_only:
                conditions['is_active'] = True
            if category:
                conditions['category'] = category
            
            # Wyszukaj funkcje
            results = realm.contemplate('list_functions', **conditions)
            
            # Przygotuj listę
            functions_list = []
            for function_being in results:
                func_data = function_being.function_data
                functions_list.append({
                    'name': func_data['spec']['name'],
                    'description': func_data['spec']['description'],
                    'category': func_data['spec']['category'],
                    'created_at': func_data['created_at'],
                    'execution_count': func_data.get('execution_stats', {}).get('execution_count', 0),
                    'function_hash': func_data['function_hash'],
                    'is_active': func_data['is_active']
                })
            
            return functions_list
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd listowania funkcji: {e}")
            return []
    
    def update_function_stats(self, function_name: str, generated_func: GeneratedFunction) -> bool:
        """Aktualizuje statystyki funkcji w bazie"""
        try:
            realm = self.engine.get_realm(self.realm_name)
            
            # Znajdź funkcję
            results = realm.contemplate('find_function', soul_name=function_name)
            
            if not results:
                return False
            
            function_being = results[0]
            
            # Aktualizuj dane
            updated_data = {
                'function_data': generated_func.to_dict()
            }
            
            # Zapisz aktualizację
            realm.evolve(function_being.soul_id, updated_data)
            
            return True
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd aktualizacji statystyk funkcji: {e}")
            return False


class FunctionGenerator:
    """
    Główny system generatywny funkcji
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        
        # Komponenty
        self.code_engine = CodeTemplateEngine()
        self.function_db = FunctionDatabase(astral_engine)
        
        # Cache funkcji
        self.function_cache: Dict[str, GeneratedFunction] = {}
        
        # Statystyki
        self.functions_created = 0
        self.functions_executed = 0
        self.total_execution_time = 0.0
        self.start_time = datetime.now()
        
        self.engine.logger.info("🛠️ Function Generator zainicjalizowany")
    
    def create_function(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tworzy nową funkcję na podstawie specyfikacji
        
        Args:
            spec_data: Specyfikacja funkcji
            
        Returns:
            Informacje o utworzonej funkcji
        """
        try:
            # Utwórz specyfikację
            spec = FunctionSpec(spec_data)
            
            # Sprawdź czy funkcja już istnieje
            if spec.name in self.function_cache:
                return {
                    'success': False,
                    'message': f'Funkcja {spec.name} już istnieje',
                    'existing_function': self.function_cache[spec.name].get_info()
                }
            print("🛠️ Specyfikacja funkcji utworzona pomyślnie")
            # Wygeneruj kod
            if spec.code_template:
                source_code = spec.code_template
            else:
                source_code = self.code_engine.generate_code(spec)
            print("🛠️ Kod funkcji wygenerowany pomyślnie")
            # Skompiluj funkcję
            compiled_func = self._compile_function(source_code, spec.name)
            print("🛠️ Funkcja skompilowana pomyślnie")
            # Utwórz obiekt funkcji
            generated_func = GeneratedFunction(spec, source_code, compiled_func)
            print("🛠️ Funkcja utworzona pomyślnie")
            # Zapisz w bazie i cache
            function_id = self.function_db.save_function(generated_func)
            self.function_cache[spec.name] = generated_func
            
            # Aktualizuj statystyki
            self.functions_created += 1
            
            self.engine.logger.info(f"🛠️ Funkcja '{spec.name}' wygenerowana pomyślnie")
            
            return {
                'success': True,
                'function_name': spec.name,
                'function_id': function_id,
                'function_info': generated_func.get_info(),
                'source_code': source_code
            }
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd tworzenia funkcji: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def invoke_function(self, function_name: str, args: Dict[str, Any] = None) -> Any:
        """
        Wywołuje funkcję po nazwie
        
        Args:
            function_name: Nazwa funkcji
            args: Argumenty funkcji
            
        Returns:
            Wynik wykonania funkcji
        """
        args = args or {}
        
        try:
            # Sprawdź cache
            if function_name not in self.function_cache:
                # Spróbuj załadować z bazy
                loaded_func = self.function_db.load_function(function_name)
                if loaded_func:
                    self.function_cache[function_name] = loaded_func
                else:
                    return {
                        'success': False,
                        'error': f'Funkcja {function_name} nie została znaleziona'
                    }
            
            # Wykonaj funkcję
            generated_func = self.function_cache[function_name]
            result = generated_func.execute(**args)
            
            # Aktualizuj statystyki globalne
            self.functions_executed += 1
            self.total_execution_time += generated_func.average_execution_time
            
            # Aktualizuj statystyki w bazie (co 10 wykonań)
            if generated_func.execution_count % 10 == 0:
                self.function_db.update_function_stats(function_name, generated_func)
            
            return {
                'success': True,
                'result': result,
                'execution_info': {
                    'function_name': function_name,
                    'execution_count': generated_func.execution_count,
                    'average_time': generated_func.average_execution_time
                }
            }
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd wykonania funkcji '{function_name}': {e}")
            return {
                'success': False,
                'error': str(e),
                'function_name': function_name
            }
    
    def _compile_function(self, source_code: str, function_name: str) -> Callable:
        """Kompiluje kod funkcji"""
        try:
            func_namespace = {}
            exec(source_code, func_namespace)
            
            if function_name in func_namespace:
                return func_namespace[function_name]
            else:
                raise ValueError(f"Funkcja '{function_name}' nie znaleziona w kodzie")
                
        except Exception as e:
            raise ValueError(f"Błąd kompilacji funkcji '{function_name}': {e}")
    
    def list_functions(self, category: str = None) -> List[Dict[str, Any]]:
        """Zwraca listę dostępnych funkcji"""
        return self.function_db.list_functions(category)
    
    def get_function_info(self, function_name: str) -> Optional[Dict[str, Any]]:
        """Zwraca informacje o funkcji"""
        if function_name in self.function_cache:
            return self.function_cache[function_name].get_info()
        
        # Spróbuj załadować z bazy
        loaded_func = self.function_db.load_function(function_name)
        if loaded_func:
            return loaded_func.get_info()
        
        return None
    
    def delete_function(self, function_name: str) -> bool:
        """Usuwa funkcję (dezaktywuje)"""
        try:
            # Usuń z cache
            if function_name in self.function_cache:
                del self.function_cache[function_name]
            
            # Dezaktywuj w bazie
            realm = self.engine.get_realm('functions')
            results = realm.contemplate('find_function', soul_name=function_name)
            
            if results:
                function_being = results[0]
                realm.evolve(function_being.soul_id, {'is_active': False})
                
                self.engine.logger.info(f"🛠️ Funkcja '{function_name}' dezaktywowana")
                return True
            
            return False
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd usuwania funkcji '{function_name}': {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status generatora funkcji"""
        return {
            'functions_created': self.functions_created,
            'functions_executed': self.functions_executed,
            'functions_in_cache': len(self.function_cache),
            'total_execution_time': self.total_execution_time,
            'average_execution_time': (self.total_execution_time / self.functions_executed) if self.functions_executed > 0 else 0,
            'uptime': str(datetime.now() - self.start_time),
            'available_templates': list(self.code_engine.templates.keys())
        }
