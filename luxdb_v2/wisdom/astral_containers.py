
"""
🔮 Astral Containers - Systemy Kontenerów Pośredniczących

Umożliwia przepływ danych między funkcjami przez astralne kontenery
z historią, walidacją i inteligentnym zarządzaniem stanami.
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import traceback


class ContainerState(Enum):
    """Stany kontenera astralnego"""
    NASCENT = "nascent"          # Nowo narodzony
    FLOWING = "flowing"          # W przepływie
    VALIDATED = "validated"      # Zwalidowany
    TRANSFORMED = "transformed"  # Przekształcony
    COMPLETED = "completed"      # Zakończony
    ERROR = "error"             # Błąd
    RETURNED = "returned"       # Zwrócony do poprawy


class ValidationResult:
    """Wynik walidacji kontenera"""
    
    def __init__(self, is_valid: bool, message: str = "", suggestions: List[str] = None):
        self.is_valid = is_valid
        self.message = message
        self.suggestions = suggestions or []
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_valid': self.is_valid,
            'message': self.message,
            'suggestions': self.suggestions,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class AstralTransition:
    """Przejście w historii kontenera"""
    function_name: str
    from_state: ContainerState
    to_state: ContainerState
    timestamp: datetime = field(default_factory=datetime.now)
    transformation: Dict[str, Any] = field(default_factory=dict)
    validation_result: Optional[ValidationResult] = None
    error_info: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'function_name': self.function_name,
            'from_state': self.from_state.value,
            'to_state': self.to_state.value,
            'timestamp': self.timestamp.isoformat(),
            'transformation': self.transformation,
            'validation_result': self.validation_result.to_dict() if self.validation_result else None,
            'error_info': self.error_info
        }


class AstralDataContainer:
    """
    Astralny kontener danych - nośnik informacji między funkcjami
    
    Zawiera:
    - Dane aktualne
    - Historię transformacji
    - Walidacje i oczekiwania
    - Możliwość powrotu do poprzedniej funkcji
    """
    
    def __init__(self, initial_data: Dict[str, Any] = None, container_id: str = None):
        self.container_id = container_id or f"astral_{uuid.uuid4().hex[:12]}"
        self.created_at = datetime.now()
        
        # Dane kontenera
        self.current_data: Dict[str, Any] = initial_data or {}
        self.metadata: Dict[str, Any] = {
            'origin_function': None,
            'target_function': None,
            'purpose': 'data_flow',
            'priority': 'normal'
        }
        
        # Historia i stan
        self.state = ContainerState.NASCENT
        self.history: List[AstralTransition] = []
        self.validation_stack: List[ValidationResult] = []
        
        # Przepływ kontroli
        self.function_stack: List[str] = []  # Stos funkcji do powrotu
        self.expected_schema: Optional[Dict[str, Any]] = None
        self.auto_correction: bool = True
        
        # Statystyki
        self.transformation_count = 0
        self.validation_count = 0
        self.error_count = 0
    
    def set_origin(self, function_name: str, purpose: str = None) -> 'AstralDataContainer':
        """Ustawia funkcję pochodzenia"""
        self.metadata['origin_function'] = function_name
        if purpose:
            self.metadata['purpose'] = purpose
        self.function_stack.append(function_name)
        return self
    
    def set_target(self, function_name: str, expected_schema: Dict[str, Any] = None) -> 'AstralDataContainer':
        """Ustawia funkcję docelową z oczekiwanym schematem"""
        self.metadata['target_function'] = function_name
        if expected_schema:
            self.expected_schema = expected_schema
        return self
    
    def transition_to(self, new_state: ContainerState, function_name: str = None, 
                     transformation: Dict[str, Any] = None, error_info: Dict[str, Any] = None) -> None:
        """Przejście do nowego stanu z zapisem w historii"""
        
        transition = AstralTransition(
            function_name=function_name or self.metadata.get('target_function', 'unknown'),
            from_state=self.state,
            to_state=new_state,
            transformation=transformation or {},
            error_info=error_info
        )
        
        self.history.append(transition)
        self.state = new_state
        
        if new_state == ContainerState.ERROR:
            self.error_count += 1
        elif transformation:
            self.transformation_count += 1
    
    def validate_for_function(self, function_name: str, expected_params: Dict[str, Any] = None) -> ValidationResult:
        """Waliduje kontener dla konkretnej funkcji"""
        
        validation_errors = []
        suggestions = []
        
        # Walidacja podstawowa
        if not self.current_data:
            validation_errors.append("Kontener nie zawiera danych")
            suggestions.append("Dodaj dane do kontenera przed wywołaniem funkcji")
        
        # Walidacja schematu jeśli podany
        if expected_params:
            for param_name, param_config in expected_params.items():
                if param_config.get('required', False):
                    if param_name not in self.current_data:
                        validation_errors.append(f"Brakujący wymagany parametr: {param_name}")
                        suggestions.append(f"Dodaj parametr '{param_name}' do danych kontenera")
                
                # Walidacja typu
                if param_name in self.current_data:
                    expected_type = param_config.get('type')
                    actual_value = self.current_data[param_name]
                    
                    if expected_type and not self._validate_type(actual_value, expected_type):
                        validation_errors.append(f"Nieprawidłowy typ parametru {param_name}: oczekiwano {expected_type}")
                        suggestions.append(f"Przekonwertuj parametr '{param_name}' na typ {expected_type}")
        
        # Walidacja stanu
        if self.state == ContainerState.ERROR:
            validation_errors.append("Kontener jest w stanie błędu")
            suggestions.append("Napraw błędy przed kontynuowaniem")
        
        is_valid = len(validation_errors) == 0
        message = "Walidacja pozytywna" if is_valid else "; ".join(validation_errors)
        
        validation_result = ValidationResult(is_valid, message, suggestions)
        self.validation_stack.append(validation_result)
        self.validation_count += 1
        
        # Dodaj do historii
        transition = AstralTransition(
            function_name=function_name,
            from_state=self.state,
            to_state=ContainerState.VALIDATED if is_valid else ContainerState.ERROR,
            validation_result=validation_result
        )
        self.history.append(transition)
        
        if is_valid:
            self.state = ContainerState.VALIDATED
        else:
            self.state = ContainerState.ERROR
        
        return validation_result
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Waliduje typ wartości"""
        type_mapping = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'Any': None  # Dowolny typ
        }
        
        if expected_type == 'Any':
            return True
        
        expected_py_type = type_mapping.get(expected_type)
        if expected_py_type is None:
            return True  # Nieznany typ - akceptuj
        
        return isinstance(value, expected_py_type)
    
    def transform_data(self, function_name: str, transformer: Callable[[Dict[str, Any]], Dict[str, Any]]) -> 'AstralDataContainer':
        """Przekształca dane w kontenerze"""
        
        try:
            old_data = self.current_data.copy()
            self.current_data = transformer(self.current_data)
            
            transformation = {
                'old_data_keys': list(old_data.keys()),
                'new_data_keys': list(self.current_data.keys()),
                'transformer_function': function_name
            }
            
            self.transition_to(ContainerState.TRANSFORMED, function_name, transformation)
            self.function_stack.append(function_name)
            
        except Exception as e:
            error_info = {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'function': function_name
            }
            self.transition_to(ContainerState.ERROR, function_name, error_info=error_info)
        
        return self
    
    def return_to_previous(self, correction_message: str = "") -> 'AstralDataContainer':
        """Wraca do poprzedniej funkcji z informacją o koniecznych poprawkach"""
        
        if len(self.function_stack) < 2:
            # Brak funkcji do powrotu
            self.transition_to(ContainerState.ERROR, error_info={
                'error': 'Brak funkcji do powrotu',
                'message': 'Kontener nie ma historii funkcji do powrotu'
            })
            return self
        
        # Usuń aktualną funkcję ze stosu
        current_function = self.function_stack.pop()
        previous_function = self.function_stack[-1]
        
        # Ustaw stan powrotu
        self.transition_to(ContainerState.RETURNED, current_function, {
            'returned_to': previous_function,
            'correction_message': correction_message,
            'return_reason': 'validation_failed_or_correction_needed'
        })
        
        # Ustaw nowy cel
        self.metadata['target_function'] = previous_function
        
        return self
    
    def complete_flow(self, function_name: str, final_result: Dict[str, Any] = None) -> 'AstralDataContainer':
        """Kończy przepływ kontenera"""
        
        if final_result:
            self.current_data.update(final_result)
        
        self.transition_to(ContainerState.COMPLETED, function_name, {
            'final_data_keys': list(self.current_data.keys()),
            'completion_time': datetime.now().isoformat()
        })
        
        return self
    
    def get_data_for_function(self, function_name: str) -> Dict[str, Any]:
        """Pobiera dane przygotowane dla konkretnej funkcji"""
        
        # Oznacz że kontener płynie do funkcji
        if self.state in [ContainerState.NASCENT, ContainerState.VALIDATED, ContainerState.TRANSFORMED]:
            self.transition_to(ContainerState.FLOWING, function_name)
        
        return self.current_data.copy()
    
    def add_function_result(self, function_name: str, result: Dict[str, Any]) -> 'AstralDataContainer':
        """Dodaje wynik funkcji do kontenera"""
        
        # Dodaj wynik do danych
        if isinstance(result, dict):
            self.current_data.update(result)
        else:
            self.current_data[f'{function_name}_result'] = result
        
        # Oznacz transformację
        self.transform_data(function_name, lambda data: data)
        
        return self
    
    def get_history_summary(self) -> Dict[str, Any]:
        """Zwraca podsumowanie historii kontenera"""
        
        return {
            'container_id': self.container_id,
            'current_state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'function_stack': self.function_stack,
            'transitions_count': len(self.history),
            'validation_count': self.validation_count,
            'transformation_count': self.transformation_count,
            'error_count': self.error_count,
            'last_validation': self.validation_stack[-1].to_dict() if self.validation_stack else None,
            'metadata': self.metadata
        }
    
    def get_full_history(self) -> Dict[str, Any]:
        """Zwraca pełną historię kontenera"""
        
        return {
            'container_id': self.container_id,
            'created_at': self.created_at.isoformat(),
            'current_state': self.state.value,
            'current_data': self.current_data,
            'metadata': self.metadata,
            'function_stack': self.function_stack,
            'expected_schema': self.expected_schema,
            'history': [transition.to_dict() for transition in self.history],
            'validation_stack': [validation.to_dict() for validation in self.validation_stack],
            'statistics': {
                'transformation_count': self.transformation_count,
                'validation_count': self.validation_count,
                'error_count': self.error_count
            }
        }
    
    def to_astral_language(self) -> str:
        """Konwertuje kontener do języka astralnego (JSON z metadanymi)"""
        
        astral_data = {
            '🔮': {  # Identyfikator astralny
                'container_id': self.container_id,
                'state': self.state.value,
                'created_at': self.created_at.isoformat()
            },
            '📊': self.current_data,  # Dane
            '🌊': {  # Przepływ
                'function_stack': self.function_stack,
                'target_function': self.metadata.get('target_function'),
                'expected_schema': self.expected_schema
            },
            '📜': [transition.to_dict() for transition in self.history[-5:]],  # Ostatnie 5 przejść
            '✅': self.validation_stack[-1].to_dict() if self.validation_stack else None  # Ostatnia walidacja
        }
        
        return json.dumps(astral_data, indent=2, ensure_ascii=False)
    
    @classmethod
    def from_astral_language(cls, astral_text: str) -> 'AstralDataContainer':
        """Tworzy kontener z języka astralnego"""
        
        try:
            astral_data = json.loads(astral_text)
            
            # Podstawowe dane
            container_info = astral_data.get('🔮', {})
            container_id = container_info.get('container_id')
            
            # Utwórz kontener
            container = cls(
                initial_data=astral_data.get('📊', {}),
                container_id=container_id
            )
            
            # Przywróć stan
            state_value = container_info.get('state', 'nascent')
            container.state = ContainerState(state_value)
            
            # Przywróć przepływ
            flow_data = astral_data.get('🌊', {})
            container.function_stack = flow_data.get('function_stack', [])
            container.expected_schema = flow_data.get('expected_schema')
            
            if flow_data.get('target_function'):
                container.metadata['target_function'] = flow_data['target_function']
            
            return container
            
        except Exception as e:
            # W przypadku błędu utwórz nowy kontener z błędem
            container = cls({'parsing_error': str(e), 'original_text': astral_text})
            container.state = ContainerState.ERROR
            return container


class AstralContainerManager:
    """
    Zarządca kontenerów astralnych - koordynuje przepływ między funkcjami
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        self.active_containers: Dict[str, AstralDataContainer] = {}
        self.completed_containers: Dict[str, AstralDataContainer] = {}
        
        # Statystyki
        self.total_containers = 0
        self.successful_flows = 0
        self.failed_flows = 0
        self.auto_corrections = 0
        
        self.engine.logger.info("🔮 Astral Container Manager zainicjalizowany")
    
    def create_container(self, initial_data: Dict[str, Any] = None, 
                        origin_function: str = None, purpose: str = None) -> AstralDataContainer:
        """Tworzy nowy kontener astralny"""
        
        container = AstralDataContainer(initial_data)
        
        if origin_function:
            container.set_origin(origin_function, purpose)
        
        self.active_containers[container.container_id] = container
        self.total_containers += 1
        
        self.engine.logger.info(f"🔮 Utworzono kontener astralny: {container.container_id}")
        return container
    
    def invoke_function_with_container(self, function_name: str, container: AstralDataContainer, 
                                     expected_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Wywołuje funkcję z kontenerem astralnym"""
        
        try:
            # Ustaw cel
            container.set_target(function_name, expected_params)
            
            # Waliduj kontener
            validation = container.validate_for_function(function_name, expected_params)
            
            if not validation.is_valid:
                # Spróbuj auto-korekcję
                if container.auto_correction and self._attempt_auto_correction(container, validation):
                    self.auto_corrections += 1
                    # Ponów walidację
                    validation = container.validate_for_function(function_name, expected_params)
                
                if not validation.is_valid:
                    # Walidacja nadal negatywna - zwróć do poprzedniej funkcji lub zgłoś błąd
                    if len(container.function_stack) > 1:
                        container.return_to_previous(validation.message)
                        return {
                            'success': False,
                            'message': 'Kontener zwrócony do poprawy',
                            'validation_errors': validation.suggestions,
                            'container_id': container.container_id
                        }
                    else:
                        return {
                            'success': False,
                            'message': f'Walidacja kontejner nieudana: {validation.message}',
                            'suggestions': validation.suggestions,
                            'container_id': container.container_id
                        }
            
            # Pobierz dane dla funkcji
            function_data = container.get_data_for_function(function_name)
            
            # Sprawdź czy funkcja istnieje
            if not self._function_exists(function_name):
                # Zgłoś do generatora funkcji
                missing_function_result = self._handle_missing_function(function_name, expected_params, container)
                if missing_function_result['success']:
                    # Funkcja została wygenerowana - spróbuj ponownie
                    return self.invoke_function_with_container(function_name, container, expected_params)
                else:
                    container.transition_to(ContainerState.ERROR, function_name, 
                                          error_info={'error': 'Function not found and generation failed'})
                    return missing_function_result
            
            # Wywołaj funkcję
            if hasattr(self.engine, 'function_generator'):
                result = self.engine.function_generator.invoke_function(function_name, function_data)
                
                if result['success']:
                    # Dodaj wynik do kontenera
                    container.add_function_result(function_name, result['result'])
                    
                    return {
                        'success': True,
                        'result': result['result'],
                        'container_id': container.container_id,
                        'container_state': container.state.value
                    }
                else:
                    container.transition_to(ContainerState.ERROR, function_name, 
                                          error_info={'error': result.get('error', 'Unknown error')})
                    return result
            else:
                return {
                    'success': False,
                    'error': 'Function Generator nie jest dostępny',
                    'container_id': container.container_id
                }
                
        except Exception as e:
            container.transition_to(ContainerState.ERROR, function_name, 
                                  error_info={'error': str(e), 'traceback': traceback.format_exc()})
            return {
                'success': False,
                'error': str(e),
                'container_id': container.container_id
            }
    
    def _function_exists(self, function_name: str) -> bool:
        """Sprawdza czy funkcja istnieje"""
        if hasattr(self.engine, 'function_generator'):
            return function_name in self.engine.function_generator.function_cache
        return False
    
    def _handle_missing_function(self, function_name: str, expected_params: Dict[str, Any], 
                                container: AstralDataContainer) -> Dict[str, Any]:
        """Obsługuje brakującą funkcję - zgłasza do generatora"""
        
        if not hasattr(self.engine, 'function_generator'):
            return {
                'success': False,
                'error': 'Function Generator nie jest dostępny',
                'message': f'Funkcja {function_name} nie istnieje i nie można jej wygenerować'
            }
        
        # Przygotuj specyfikację funkcji na podstawie oczekiwanych parametrów
        function_spec = {
            'name': function_name,
            'description': f'Automatycznie wygenerowana funkcja {function_name} dla kontenera {container.container_id}',
            'parameters': []
        }
        
        if expected_params:
            for param_name, param_config in expected_params.items():
                function_spec['parameters'].append({
                    'name': param_name,
                    'type': param_config.get('type', 'Any'),
                    'description': param_config.get('description', f'Parametr {param_name}')
                })
        else:
            # Wygeneruj parametry na podstawie danych w kontenerze
            for key in container.current_data.keys():
                function_spec['parameters'].append({
                    'name': key,
                    'type': 'Any',
                    'description': f'Parametr z kontenera: {key}'
                })
        
        # Poproś generator o utworzenie funkcji
        generation_result = self.engine.function_generator.create_function(function_spec)
        
        if generation_result['success']:
            self.engine.logger.info(f"🛠️ Automatycznie wygenerowano funkcję '{function_name}' dla kontenera")
            return {
                'success': True,
                'message': f'Funkcja {function_name} została automatycznie wygenerowana',
                'function_info': generation_result['function_info']
            }
        else:
            return {
                'success': False,
                'error': generation_result.get('error', 'Nie można wygenerować funkcji'),
                'message': f'Nie udało się wygenerować funkcji {function_name}'
            }
    
    def _attempt_auto_correction(self, container: AstralDataContainer, validation: ValidationResult) -> bool:
        """Próbuje automatycznej korekcji kontenera"""
        
        corrections_made = False
        
        for suggestion in validation.suggestions:
            if 'Dodaj parametr' in suggestion:
                # Spróbuj dodać brakujący parametr z wartością domyślną
                param_name = suggestion.split("'")[1] if "'" in suggestion else None
                if param_name:
                    container.current_data[param_name] = None  # Wartość domyślna
                    corrections_made = True
            
            elif 'Przekonwertuj parametr' in suggestion:
                # Spróbuj konwersji typu
                # TODO: Implementacja inteligentnej konwersji typów
                pass
        
        if corrections_made:
            container.transition_to(ContainerState.TRANSFORMED, 'auto_correction', {
                'corrections': validation.suggestions,
                'auto_correction': True
            })
        
        return corrections_made
    
    def complete_container(self, container_id: str, final_result: Dict[str, Any] = None) -> bool:
        """Kończy przepływ kontenera"""
        
        if container_id in self.active_containers:
            container = self.active_containers[container_id]
            container.complete_flow('system', final_result)
            
            # Przenieś do zakończonych
            self.completed_containers[container_id] = container
            del self.active_containers[container_id]
            
            self.successful_flows += 1
            self.engine.logger.info(f"🔮 Kontener {container_id} zakończony pomyślnie")
            return True
        
        return False
    
    def get_container(self, container_id: str) -> Optional[AstralDataContainer]:
        """Pobiera kontener po ID"""
        return self.active_containers.get(container_id) or self.completed_containers.get(container_id)
    
    def list_active_containers(self) -> List[Dict[str, Any]]:
        """Zwraca listę aktywnych kontenerów"""
        return [container.get_history_summary() for container in self.active_containers.values()]
    
    def get_container_statistics(self) -> Dict[str, Any]:
        """Zwraca statystyki kontenerów"""
        return {
            'total_containers': self.total_containers,
            'active_containers': len(self.active_containers),
            'completed_containers': len(self.completed_containers),
            'successful_flows': self.successful_flows,
            'failed_flows': self.failed_flows,
            'auto_corrections': self.auto_corrections,
            'success_rate': (self.successful_flows / self.total_containers * 100) if self.total_containers > 0 else 0
        }
