
"""
🔐 Secure Code Flow - Bezpieczne generowanie i wykonywanie kodu

System sandbox dla bytów logicznych z zabezpieczeniami przed złośliwym kodem.
Wszystkie pliki chronione - tylko niejawne funkcje w warstwach wymiarów.
"""

import ast
import sys
import uuid
import traceback
import subprocess
import tempfile
import os
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import threading
import signal

from ..beings.logical_being import LogicalBeing, LogicType, LogicalContext
from ..beings.intention_being import IntentionBeing
from ..beings.error_handler_being import ErrorHandlerBeing


class SecurityLevel(Enum):
    """Poziomy bezpieczeństwa sandbox"""
    MINIMAL = 1      # Podstawowe ograniczenia
    STANDARD = 2     # Standardowe zabezpieczenia  
    STRICT = 3       # Surowe ograniczenia
    PARANOID = 4     # Maksymalne zabezpieczenia


class CodeLanguage(Enum):
    """Obsługiwane języki w sandbox"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"  
    LUX_INTERNAL = "lux_internal"  # Wewnętrzny język Astry


@dataclass
class SandboxEnvironment:
    """Środowisko sandbox dla wykonywania kodu"""
    env_id: str
    security_level: SecurityLevel
    allowed_imports: List[str] = field(default_factory=list)
    blocked_functions: List[str] = field(default_factory=lambda: [
        'open', 'exec', 'eval', '__import__', 'compile', 'globals', 'locals',
        'input', 'raw_input', 'file', 'execfile', 'reload', 'exit', 'quit'
    ])
    max_execution_time: float = 5.0
    max_memory_mb: int = 50
    temp_dir: Optional[str] = None
    
    def __post_init__(self):
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix=f"astra_sandbox_{self.env_id}_")


@dataclass 
class GeneratedFunction:
    """Funkcja wygenerowana przez byt logiczny"""
    func_id: str
    name: str
    language: CodeLanguage
    code: str
    purpose: str
    created_by: str  # ID bytu który ją stworzył
    security_validated: bool = False
    execution_count: int = 0
    last_executed: Optional[datetime] = None
    dimension_layer: str = "niejawna"  # Warstwa wymiaru gdzie funkcja jest przechowywana


class SecureCodeFlow:
    """
    Flow do bezpiecznego generowania i wykonywania kodu przez byty logiczne
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        
        # Byt odpowiedzialny za zabezpieczenia
        self.security_guardian = LogicalBeing(
            LogicType.ANALYTICAL,
            LogicalContext(
                domain="security",
                specialization="code_validation"
            )
        )
        
        # Byt generujący kod
        self.code_architect = LogicalBeing(
            LogicType.CREATIVE,
            LogicalContext(
                domain="code_generation", 
                specialization="secure_functions"
            )
        )
        
        # Byt wykonujący kod
        self.execution_engine = LogicalBeing(
            LogicType.ADAPTIVE,
            LogicalContext(
                domain="code_execution",
                specialization="sandbox_runtime"
            )
        )
        
        # Środowiska sandbox
        self.sandbox_environments: Dict[str, SandboxEnvironment] = {}
        
        # Wygenerowane funkcje w warstwach wymiarów
        self.dimension_functions: Dict[str, Dict[str, GeneratedFunction]] = {
            'niejawna': {},      # Funkcje niejawne
            'pomocnicza': {},    # Funkcje pomocnicze
            'specjalna': {},     # Funkcje specjalne
            'krytyczna': {}      # Funkcje krytyczne
        }
        
        # Zabezpieczenia
        self.malicious_patterns = [
            '__import__', 'exec(', 'eval(', 'compile(',
            'os.system', 'subprocess', 'shutil.rmtree',
            'open(', 'file(', 'input(', 'raw_input(',
            'globals()', 'locals()', '.__', 'sys.exit'
        ]
        
        # Inicjalizuj domyślne środowisko
        self._create_default_sandbox()
    
    def _create_default_sandbox(self):
        """Tworzy domyślne środowisko sandbox"""
        default_env = SandboxEnvironment(
            env_id="default",
            security_level=SecurityLevel.STANDARD,
            allowed_imports=['math', 'datetime', 'json', 'uuid', 're'],
            max_execution_time=3.0,
            max_memory_mb=30
        )
        self.sandbox_environments['default'] = default_env
    
    def generate_secure_function(self, intention: IntentionBeing, 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generuje bezpieczną funkcję na podstawie intencji
        """
        try:
            # 1. Analiza intencji przez code_architect
            code_analysis = self.code_architect.process_intention(intention, context)
            
            if not code_analysis.get('code_generated'):
                return {'status': 'no_code_needed', 'message': 'Intencja nie wymaga generowania kodu'}
            
            # 2. Generowanie kodu
            generated_code = self._generate_code_for_intention(intention, code_analysis)
            
            # 3. Walidacja bezpieczeństwa
            security_result = self.security_guardian.process_intention(
                intention, 
                {'code': generated_code, 'analysis': code_analysis}
            )
            
            if not security_result.get('security_approved', False):
                self._report_security_violation(generated_code, security_result)
                return {
                    'status': 'security_rejected',
                    'reason': security_result.get('rejection_reason', 'Kod nie przeszedł walidacji bezpieczeństwa')
                }
            
            # 4. Stwórz funkcję w warstwie wymiaru
            func = GeneratedFunction(
                func_id=str(uuid.uuid4()),
                name=f"generated_{intention.essence.name}_{uuid.uuid4().hex[:8]}",
                language=CodeLanguage.PYTHON,
                code=generated_code,
                purpose=intention.duchowa.opis_intencji,
                created_by=intention.essence.soul_id,
                security_validated=True,
                dimension_layer=self._determine_dimension_layer(intention)
            )
            
            # 5. Zapisz w odpowiedniej warstwie wymiaru
            layer = func.dimension_layer
            self.dimension_functions[layer][func.func_id] = func
            
            self.engine.logger.info(f"🔐 Funkcja {func.name} wygenerowana w warstwie {layer}")
            
            return {
                'status': 'generated',
                'function_id': func.func_id,
                'function_name': func.name,
                'dimension_layer': layer,
                'security_level': 'validated'
            }
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd generowania funkcji: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def execute_dimension_function(self, func_id: str, args: List[Any] = None, 
                                 kwargs: Dict[str, Any] = None, 
                                 sandbox_env: str = "default") -> Dict[str, Any]:
        """
        Wykonuje funkcję z warstwy wymiaru w środowisku sandbox
        """
        args = args or []
        kwargs = kwargs or {}
        
        # Znajdź funkcję w warstwach wymiarów
        func = None
        for layer, functions in self.dimension_functions.items():
            if func_id in functions:
                func = functions[func_id]
                break
        
        if not func:
            return {'status': 'not_found', 'error': f'Funkcja {func_id} nie znaleziona'}
        
        if not func.security_validated:
            return {'status': 'security_error', 'error': 'Funkcja nie została zatwierdzona przez zabezpieczenia'}
        
        # Pobierz środowisko sandbox
        if sandbox_env not in self.sandbox_environments:
            sandbox_env = "default"
        
        env = self.sandbox_environments[sandbox_env]
        
        try:
            # Przetwórz przez execution_engine
            execution_intention = IntentionBeing({
                'duchowa': {
                    'opis_intencji': f'Wykonaj funkcję {func.name} w bezpiecznym środowisku',
                    'kontekst': f'Sandbox: {sandbox_env}, Args: {len(args)}, Kwargs: {len(kwargs)}',
                    'inspiracja': 'Bezpieczne wykonanie kodu w kontrolowanym środowisku',
                    'energia_duchowa': 85.0
                },
                'materialna': {
                    'zadanie': 'secure_code_execution',
                    'wymagania': ['sandbox_isolation', 'security_monitoring', 'resource_limits'],
                    'oczekiwany_rezultat': 'Bezpieczne wykonanie i zwrócenie wyniku'
                },
                'metainfo': {
                    'zrodlo': 'secure_code_flow',
                    'tags': ['code_execution', 'sandbox', 'security']
                }
            })
            
            execution_context = {
                'function': func,
                'args': args,
                'kwargs': kwargs,
                'sandbox_env': env
            }
            
            execution_result = self.execution_engine.process_intention(
                execution_intention, execution_context
            )
            
            # Wykonaj w rzeczywistości (symulacja sandbox)
            result = self._execute_in_sandbox(func, args, kwargs, env)
            
            # Aktualizuj statystyki funkcji
            func.execution_count += 1
            func.last_executed = datetime.now()
            
            return {
                'status': 'executed',
                'result': result,
                'function_id': func_id,
                'execution_count': func.execution_count,
                'sandbox_env': sandbox_env
            }
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd wykonania funkcji {func_id}: {e}")
            return {
                'status': 'execution_error', 
                'error': str(e),
                'function_id': func_id
            }
    
    def _generate_code_for_intention(self, intention: IntentionBeing, 
                                   analysis: Dict[str, Any]) -> str:
        """Generuje kod na podstawie analizy intencji"""
        
        # Przykład generowania kodu dla manifestu PDF
        if 'pdf' in intention.materialna.zadanie.lower():
            return '''
def generate_pdf_content(title, sections):
    """Generuje zawartość PDF na podstawie tytułu i sekcji"""
    content = []
    content.append("=" * 80)
    content.append(f"  {title.upper()}")
    content.append("=" * 80)
    content.append("")
    
    for i, (section_title, section_content) in enumerate(sections.items(), 1):
        content.append(f"{i}. {section_title.upper()}")
        content.append("")
        content.append(f"   {section_content}")
        content.append("")
    
    return "\\n".join(content)
'''
        
        # Przykład dla analizy danych
        elif 'analiz' in intention.duchowa.opis_intencji.lower():
            return '''
def analyze_data(data):
    """Analizuje przekazane dane"""
    if not data:
        return {"status": "no_data", "analysis": None}
    
    analysis = {
        "count": len(data) if hasattr(data, '__len__') else 1,
        "type": type(data).__name__,
        "summary": str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
    }
    
    return {"status": "analyzed", "analysis": analysis}
'''
        
        # Domyślna funkcja
        else:
            return '''
def process_intention(input_data):
    """Przetwarza dane zgodnie z intencją"""
    return {
        "status": "processed", 
        "input": input_data,
        "processed_at": "now"
    }
'''
    
    def _execute_in_sandbox(self, func: GeneratedFunction, args: List[Any], 
                          kwargs: Dict[str, Any], env: SandboxEnvironment) -> Any:
        """Wykonuje funkcję w środowisku sandbox (symulacja)"""
        
        # W rzeczywistej implementacji tutaj byłaby izolacja procesów,
        # ograniczenia zasobów itp. Na razie symulacja:
        
        local_vars = {
            'args': args,
            'kwargs': kwargs,
            'result': None
        }
        
        # Przygotuj kod do wykonania
        exec_code = func.code + f"\nresult = {func.name.split('_')[-1] if '_' in func.name else 'process_intention'}(*args, **kwargs)"
        
        # Wykonaj z ograniczeniami (symulacja)
        try:
            exec(exec_code, {}, local_vars)
            return local_vars.get('result', 'No result')
        except Exception as e:
            raise RuntimeError(f"Sandbox execution error: {e}")
    
    def _determine_dimension_layer(self, intention: IntentionBeing) -> str:
        """Określa warstwę wymiaru dla funkcji na podstawie intencji"""
        energy = intention.duchowa.energia_duchowa
        
        if energy >= 95:
            return 'krytyczna'
        elif energy >= 85:
            return 'specjalna'  
        elif energy >= 70:
            return 'pomocnicza'
        else:
            return 'niejawna'
    
    def _report_security_violation(self, code: str, security_result: Dict[str, Any]):
        """Raportuje naruszenie bezpieczeństwa"""
        self.engine.logger.warning(f"🚨 Kod odrzucony przez zabezpieczenia: {security_result.get('rejection_reason')}")
        
        # Można tutaj dodać więcej logiki raportowania
        violation_report = {
            'timestamp': datetime.now().isoformat(),
            'code_snippet': code[:200] + '...' if len(code) > 200 else code,
            'rejection_reason': security_result.get('rejection_reason'),
            'security_level': 'violation'
        }
    
    def list_dimension_functions(self, layer: Optional[str] = None) -> Dict[str, Any]:
        """Listuje funkcje w warstwach wymiarów"""
        if layer and layer in self.dimension_functions:
            return {
                'layer': layer,
                'functions': [
                    {
                        'id': fid,
                        'name': func.name,
                        'purpose': func.purpose,
                        'execution_count': func.execution_count,
                        'created_by': func.created_by
                    }
                    for fid, func in self.dimension_functions[layer].items()
                ]
            }
        else:
            return {
                'all_layers': {
                    layer_name: len(functions) 
                    for layer_name, functions in self.dimension_functions.items()
                },
                'total_functions': sum(len(funcs) for funcs in self.dimension_functions.values())
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status SecureCodeFlow"""
        return {
            'type': 'secure_code_flow',
            'sandbox_environments': len(self.sandbox_environments),
            'dimension_layers': {
                layer: len(functions)
                for layer, functions in self.dimension_functions.items()
            },
            'security_guardian': self.security_guardian.get_status()['logical_being_specific'],
            'code_architect': self.code_architect.get_status()['logical_being_specific'],
            'execution_engine': self.execution_engine.get_status()['logical_being_specific'],
            'total_generated_functions': sum(len(funcs) for funcs in self.dimension_functions.values())
        }
