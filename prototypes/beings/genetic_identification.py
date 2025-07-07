
"""
🧬 Genetic Identification - System Genetycznej Identyfikacji Argumentów

Zaawansowany system śledzenia i identyfikacji argumentów funkcji
z wykorzystaniem genetycznych wzorców i astralnych sygnatur.
"""

import hashlib
import uuid
import inspect
import functools
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ArgumentGenome:
    """Genom argumentu - genetyczna sygnatura parametru funkcji"""
    arg_name: str
    arg_type: type
    arg_value: Any
    genetic_hash: str
    astral_signature: str
    created_at: datetime = field(default_factory=datetime.now)
    mutation_count: int = 0
    parent_signatures: List[str] = field(default_factory=list)
    
    def mutate(self, new_value: Any) -> 'ArgumentGenome':
        """Mutacja genomu argumentu"""
        new_genome = ArgumentGenome(
            arg_name=self.arg_name,
            arg_type=type(new_value),
            arg_value=new_value,
            genetic_hash=self._generate_genetic_hash(new_value),
            astral_signature=self._generate_astral_signature(new_value),
            mutation_count=self.mutation_count + 1,
            parent_signatures=self.parent_signatures + [self.astral_signature]
        )
        return new_genome
    
    def _generate_genetic_hash(self, value: Any) -> str:
        """Generuje genetyczny hash wartości"""
        value_str = str(value) + str(type(value).__name__)
        return hashlib.sha256(value_str.encode()).hexdigest()[:16]
    
    def _generate_astral_signature(self, value: Any) -> str:
        """Generuje astralną sygnaturę argumentu"""
        base = f"{self.arg_name}:{type(value).__name__}:{str(value)[:50]}"
        return hashlib.md5(base.encode()).hexdigest()[:12]


@dataclass
class FunctionGenome:
    """Genom funkcji - kompletna genetyczna sygnatura wywołania"""
    function_name: str
    function_id: str
    arguments: Dict[str, ArgumentGenome]
    return_genome: Optional[ArgumentGenome] = None
    execution_time: Optional[float] = None
    astral_fingerprint: str = field(default="")
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.astral_fingerprint:
            self.astral_fingerprint = self._generate_fingerprint()
    
    def _generate_fingerprint(self) -> str:
        """Generuje unikalny odcisk palca funkcji"""
        arg_hashes = [genome.genetic_hash for genome in self.arguments.values()]
        combined = f"{self.function_name}:{''.join(sorted(arg_hashes))}"
        return hashlib.sha256(combined.encode()).hexdigest()[:20]


class GeneticIdentificationSystem:
    """System genetycznej identyfikacji argumentów i funkcji"""
    
    def __init__(self):
        self.genome_registry: Dict[str, FunctionGenome] = {}
        self.argument_lineage: Dict[str, List[ArgumentGenome]] = {}
        self.function_signatures: Dict[str, List[str]] = {}
        
    def register_function_call(self, func_name: str, args: tuple, kwargs: dict, 
                             result: Any = None, execution_time: float = None) -> FunctionGenome:
        """Rejestruje wywołanie funkcji z genetyczną identyfikacją"""
        function_id = str(uuid.uuid4())
        
        # Utwórz genomy argumentów
        arguments = {}
        
        # Pobierz nazwy parametrów funkcji
        sig = inspect.signature(self._get_function_by_name(func_name)) if hasattr(self, '_get_function_by_name') else None
        param_names = list(sig.parameters.keys()) if sig else []
        
        # Pozycyjne argumenty
        for i, arg_value in enumerate(args):
            arg_name = param_names[i] if i < len(param_names) else f"arg_{i}"
            genome = self._create_argument_genome(arg_name, arg_value)
            arguments[arg_name] = genome
            self._track_argument_lineage(arg_name, genome)
        
        # Argumenty słownikowe
        for arg_name, arg_value in kwargs.items():
            genome = self._create_argument_genome(arg_name, arg_value)
            arguments[arg_name] = genome
            self._track_argument_lineage(arg_name, genome)
        
        # Genom wyniku
        return_genome = None
        if result is not None:
            return_genome = self._create_argument_genome("__return__", result)
        
        # Utwórz genom funkcji
        func_genome = FunctionGenome(
            function_name=func_name,
            function_id=function_id,
            arguments=arguments,
            return_genome=return_genome,
            execution_time=execution_time
        )
        
        # Zarejestruj w rejestrze
        self.genome_registry[function_id] = func_genome
        
        # Śledź sygnatury funkcji
        if func_name not in self.function_signatures:
            self.function_signatures[func_name] = []
        self.function_signatures[func_name].append(func_genome.astral_fingerprint)
        
        return func_genome
    
    def _create_argument_genome(self, arg_name: str, arg_value: Any) -> ArgumentGenome:
        """Tworzy genom argumentu"""
        genetic_hash = hashlib.sha256(f"{str(arg_value)}{type(arg_value).__name__}".encode()).hexdigest()[:16]
        astral_signature = hashlib.md5(f"{arg_name}:{type(arg_value).__name__}:{str(arg_value)[:50]}".encode()).hexdigest()[:12]
        
        return ArgumentGenome(
            arg_name=arg_name,
            arg_type=type(arg_value),
            arg_value=arg_value,
            genetic_hash=genetic_hash,
            astral_signature=astral_signature
        )
    
    def _track_argument_lineage(self, arg_name: str, genome: ArgumentGenome):
        """Śledzi rodowód argumentu"""
        if arg_name not in self.argument_lineage:
            self.argument_lineage[arg_name] = []
        self.argument_lineage[arg_name].append(genome)
    
    def find_similar_calls(self, target_genome: FunctionGenome, similarity_threshold: float = 0.8) -> List[FunctionGenome]:
        """Znajduje podobne wywołania funkcji"""
        similar_calls = []
        
        for genome in self.genome_registry.values():
            if genome.function_name == target_genome.function_name:
                similarity = self._calculate_similarity(target_genome, genome)
                if similarity >= similarity_threshold:
                    similar_calls.append(genome)
        
        return sorted(similar_calls, key=lambda g: self._calculate_similarity(target_genome, g), reverse=True)
    
    def _calculate_similarity(self, genome1: FunctionGenome, genome2: FunctionGenome) -> float:
        """Oblicza podobieństwo między genomami funkcji"""
        if genome1.function_name != genome2.function_name:
            return 0.0
        
        common_args = set(genome1.arguments.keys()) & set(genome2.arguments.keys())
        total_args = set(genome1.arguments.keys()) | set(genome2.arguments.keys())
        
        if not total_args:
            return 1.0
        
        arg_similarity = 0.0
        for arg_name in common_args:
            arg1 = genome1.arguments[arg_name]
            arg2 = genome2.arguments[arg_name]
            
            # Porównaj typy
            type_match = 1.0 if arg1.arg_type == arg2.arg_type else 0.0
            
            # Porównaj wartości (podstawowe)
            value_match = 1.0 if str(arg1.arg_value) == str(arg2.arg_value) else 0.0
            
            arg_similarity += (type_match * 0.3 + value_match * 0.7)
        
        return (arg_similarity / len(total_args)) * (len(common_args) / len(total_args))
    
    def get_argument_evolution(self, arg_name: str) -> List[ArgumentGenome]:
        """Zwraca ewolucję argumentu w czasie"""
        return self.argument_lineage.get(arg_name, [])
    
    def get_function_statistics(self, func_name: str) -> Dict[str, Any]:
        """Zwraca statystyki wywołań funkcji"""
        function_calls = [g for g in self.genome_registry.values() if g.function_name == func_name]
        
        if not function_calls:
            return {'total_calls': 0}
        
        execution_times = [g.execution_time for g in function_calls if g.execution_time is not None]
        
        return {
            'total_calls': len(function_calls),
            'unique_signatures': len(set(g.astral_fingerprint for g in function_calls)),
            'avg_execution_time': sum(execution_times) / len(execution_times) if execution_times else None,
            'min_execution_time': min(execution_times) if execution_times else None,
            'max_execution_time': max(execution_times) if execution_times else None,
            'first_call': min(g.created_at for g in function_calls),
            'last_call': max(g.created_at for g in function_calls)
        }


# Globalna instancja systemu
_genetic_system = GeneticIdentificationSystem()


def genetic_trace(include_args: bool = True, include_return: bool = True, 
                 track_performance: bool = True):
    """
    Dekorator do genetycznego śledzenia funkcji
    
    Args:
        include_args: Czy śledzić argumenty
        include_return: Czy śledzić wartość zwracaną
        track_performance: Czy mierzyć czas wykonania
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now() if track_performance else None
            
            try:
                # Wykonaj funkcję
                result = func(*args, **kwargs)
                
                # Oblicz czas wykonania
                execution_time = None
                if track_performance and start_time:
                    execution_time = (datetime.now() - start_time).total_seconds()
                
                # Zarejestruj wywołanie
                genome = _genetic_system.register_function_call(
                    func_name=func.__name__,
                    args=args if include_args else (),
                    kwargs=kwargs if include_args else {},
                    result=result if include_return else None,
                    execution_time=execution_time
                )
                
                # Dodaj genom do wyniku jeśli to możliwe
                if hasattr(result, '__dict__'):
                    result.__genetic_genome__ = genome
                
                return result
                
            except Exception as e:
                # Zarejestruj błąd
                error_genome = _genetic_system.register_function_call(
                    func_name=func.__name__,
                    args=args if include_args else (),
                    kwargs=kwargs if include_args else {},
                    result=f"ERROR: {str(e)}",
                    execution_time=None
                )
                raise
        
        # Dodaj metadane do funkcji
        wrapper.__genetic_traced__ = True
        wrapper.__genetic_config__ = {
            'include_args': include_args,
            'include_return': include_return,
            'track_performance': track_performance
        }
        
        return wrapper
    return decorator


def astral_signature(*signature_args, **signature_kwargs):
    """
    Dekorator do tworzenia astralnych sygnatur funkcji
    Pozwala na predefiniowanie kluczowych argumentów do śledzenia
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Filtruj argumenty według sygnatury
            filtered_args = signature_args if signature_args else args
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in signature_kwargs} if signature_kwargs else kwargs
            
            # Utwórz specjalną sygnaturę
            astral_hash = hashlib.sha256(
                f"{func.__name__}:{str(filtered_args)}:{str(filtered_kwargs)}".encode()
            ).hexdigest()[:16]
            
            # Wykonaj funkcję z genetycznym śledzeniem
            result = func(*args, **kwargs)
            
            # Dodaj astralną sygnaturę
            if hasattr(result, '__dict__'):
                result.__astral_signature__ = astral_hash
            
            return result
        
        wrapper.__astral_signature_config__ = {
            'signature_args': signature_args,
            'signature_kwargs': signature_kwargs
        }
        
        return wrapper
    return decorator


def get_genetic_system() -> GeneticIdentificationSystem:
    """Zwraca globalną instancję systemu genetycznego"""
    return _genetic_system


def analyze_function_genetics(func_name: str) -> Dict[str, Any]:
    """Analizuje genetykę funkcji"""
    return _genetic_system.get_function_statistics(func_name)


def find_genetic_patterns(func_name: str, pattern_threshold: float = 0.7) -> Dict[str, Any]:
    """Znajduje genetyczne wzorce w wywołaniach funkcji"""
    function_calls = [g for g in _genetic_system.genome_registry.values() if g.function_name == func_name]
    
    if len(function_calls) < 2:
        return {'patterns_found': 0, 'message': 'Zbyt mało wywołań do analizy wzorców'}
    
    patterns = {}
    for i, genome1 in enumerate(function_calls):
        similar_calls = _genetic_system.find_similar_calls(genome1, pattern_threshold)
        if len(similar_calls) > 1:  # Więcej niż samo siebie
            pattern_key = f"pattern_{i}"
            patterns[pattern_key] = {
                'base_genome': genome1.astral_fingerprint,
                'similar_calls': len(similar_calls),
                'call_ids': [g.function_id for g in similar_calls]
            }
    
    return {
        'patterns_found': len(patterns),
        'total_calls_analyzed': len(function_calls),
        'patterns': patterns
    }
