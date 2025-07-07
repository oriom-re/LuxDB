
"""
🧠 LogicalBeing - Byt Logiczny z Indywidualną Inteligencją

Byty posiadające własną logikę, funkcje i zdolność do adaptacji.
Mogą tworzyć mikro-funkcje w dowolnych językach na podstawie zrozumienia.
"""

import uuid
import json
import ast
import importlib
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .base_being import BaseBeing
from .intention_being import IntentionBeing


class LogicType(Enum):
    """Typy logiki bytów"""
    ANALYTICAL = "analytical"      # Analityczna
    CREATIVE = "creative"          # Kreatywna
    ADAPTIVE = "adaptive"          # Adaptacyjna
    COLLABORATIVE = "collaborative" # Współpracująca
    EMERGENT = "emergent"          # Emergentna


class UnderstandingLevel(Enum):
    """Poziomy zrozumienia"""
    NONE = 0           # Brak zrozumienia
    BASIC = 1          # Podstawowe
    INTERMEDIATE = 2   # Średnie
    ADVANCED = 3       # Zaawansowane
    EXPERT = 4         # Eksperckie
    TRANSCENDENT = 5   # Transcendentne


@dataclass
class MicroFunction:
    """Mikro-funkcja stworzona przez byt"""
    name: str
    language: str
    code: str
    purpose: str
    created_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    success_rate: float = 1.0
    
    def execute(self, *args, **kwargs) -> Any:
        """Wykonuje mikro-funkcję"""
        try:
            if self.language == "python":
                # Bezpieczne wykonanie Python kodu
                local_vars = {'args': args, 'kwargs': kwargs}
                exec(self.code, {}, local_vars)
                self.usage_count += 1
                return local_vars.get('result')
            else:
                # Inne języki - placeholder
                return f"Executed {self.name} with {args}, {kwargs}"
        except Exception as e:
            self.success_rate *= 0.9  # Zmniejsz wskaźnik sukcesu
            raise e


@dataclass
class LogicalContext:
    """Kontekst logiczny bytu"""
    domain: str
    specialization: str
    knowledge_base: Dict[str, Any] = field(default_factory=dict)
    embeddings: Dict[str, List[float]] = field(default_factory=dict)
    patterns: List[str] = field(default_factory=list)
    

class LogicalBeing(BaseBeing):
    """
    Byt Logiczny - posiada indywidualną logikę i zdolność tworzenia funkcji
    """
    
    def __init__(self, logic_type: LogicType, context: LogicalContext, realm=None):
        super().__init__(realm=realm)
        
        self.logic_type = logic_type
        self.context = context
        self.understanding_level = UnderstandingLevel.BASIC
        
        # Indywidualne funkcje i logika
        self.micro_functions: Dict[str, MicroFunction] = {}
        self.implicit_algorithms: Dict[str, Callable] = {}
        self.learning_loops: List[Callable] = []
        
        # Historia interakcji i nauki
        self.interaction_history: List[Dict[str, Any]] = []
        self.understanding_failures: List[Dict[str, Any]] = []
        self.successful_patterns: List[Dict[str, Any]] = []
        
        # Komunikacja z innymi bytami
        self.connected_beings: Dict[str, 'LogicalBeing'] = {}
        self.collaboration_protocols: Dict[str, Callable] = {}
        
        self.essence.name = f"{logic_type.value.capitalize()}Being_{uuid.uuid4().hex[:8]}"
        self.essence.consciousness_level = "logical_aware"
        
        # Inicjalizuj podstawowe algorytmy
        self._initialize_implicit_algorithms()
        self._initialize_learning_loops()
    
    def _initialize_implicit_algorithms(self):
        """Inicjalizuje niejawne algorytmy wewnętrzne"""
        
        def pattern_recognition_loop():
            """Ciągłe rozpoznawanie wzorców"""
            recent_interactions = self.interaction_history[-10:]
            patterns = []
            
            for interaction in recent_interactions:
                if interaction.get('success', False):
                    patterns.append(interaction.get('pattern', 'unknown'))
            
            # Aktualizuj wzorce w kontekście
            self.context.patterns = list(set(patterns))
            return patterns
        
        def understanding_assessment():
            """Ocena poziomu zrozumienia"""
            success_rate = sum(1 for i in self.interaction_history[-20:] 
                             if i.get('success', False)) / max(1, len(self.interaction_history[-20:]))
            
            if success_rate > 0.9:
                self.understanding_level = UnderstandingLevel.EXPERT
            elif success_rate > 0.7:
                self.understanding_level = UnderstandingLevel.ADVANCED
            elif success_rate > 0.5:
                self.understanding_level = UnderstandingLevel.INTERMEDIATE
            elif success_rate > 0.2:
                self.understanding_level = UnderstandingLevel.BASIC
            else:
                self.understanding_level = UnderstandingLevel.NONE
            
            return self.understanding_level
        
        def adaptive_optimization():
            """Adaptacyjna optymalizacja funkcji"""
            for func_name, func in self.micro_functions.items():
                if func.success_rate < 0.5 and func.usage_count > 5:
                    # Funkcja działa słabo - próbuj zoptymalizować
                    self._optimize_micro_function(func_name)
        
        self.implicit_algorithms.update({
            'pattern_recognition': pattern_recognition_loop,
            'understanding_assessment': understanding_assessment,
            'adaptive_optimization': adaptive_optimization
        })
    
    def _initialize_learning_loops(self):
        """Inicjalizuje pętle uczenia się"""
        
        def continuous_learning_loop():
            """Ciągła pętla uczenia się"""
            # Uruchom wszystkie niejawne algorytmy
            for name, algorithm in self.implicit_algorithms.items():
                try:
                    result = algorithm()
                    self.remember(f'implicit_algorithm_{name}', {
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as e:
                    self.remember(f'algorithm_error_{name}', {
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        self.learning_loops.append(continuous_learning_loop)
    
    def process_intention(self, intention: IntentionBeing, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Przetwarza intencję przez pryzmat własnej logiki
        """
        processing_start = datetime.now()
        
        # Analiza intencji przez kontekst
        understanding = self._analyze_intention_understanding(intention, context)
        
        if understanding['level'] == UnderstandingLevel.NONE:
            # Brak zrozumienia - zwróć prośbę o wyjaśnienie
            return self._request_clarification(intention, understanding)
        
        # Próbuj przetworzyć intencję
        try:
            result = self._execute_logical_processing(intention, context, understanding)
            
            # Zapisz sukces
            self.interaction_history.append({
                'type': 'intention_processing',
                'intention_id': intention.essence.soul_id,
                'success': True,
                'understanding_level': understanding['level'].value,
                'processing_time': (datetime.now() - processing_start).total_seconds(),
                'pattern': self._extract_pattern(intention, context)
            })
            
            return result
            
        except Exception as e:
            # Zapisz niepowodzenie
            self.understanding_failures.append({
                'intention_id': intention.essence.soul_id,
                'error': str(e),
                'context': context,
                'timestamp': datetime.now().isoformat()
            })
            
            return self._request_clarification(intention, {
                'level': UnderstandingLevel.NONE,
                'reason': f'Processing error: {str(e)}'
            })
    
    def _analyze_intention_understanding(self, intention: IntentionBeing, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analizuje poziom zrozumienia intencji"""
        
        # Sprawdź czy intencja pasuje do domeny
        domain_match = self._check_domain_match(intention)
        
        # Sprawdź czy mamy wzorce dla tego typu intencji
        pattern_match = self._check_pattern_match(intention)
        
        # Sprawdź embedding similarity (symulacja)
        embedding_similarity = self._calculate_embedding_similarity(intention, context)
        
        # Oblicz poziom zrozumienia
        understanding_score = (domain_match + pattern_match + embedding_similarity) / 3
        
        if understanding_score > 0.8:
            level = UnderstandingLevel.EXPERT
        elif understanding_score > 0.6:
            level = UnderstandingLevel.ADVANCED
        elif understanding_score > 0.4:
            level = UnderstandingLevel.INTERMEDIATE
        elif understanding_score > 0.2:
            level = UnderstandingLevel.BASIC
        else:
            level = UnderstandingLevel.NONE
        
        return {
            'level': level,
            'score': understanding_score,
            'domain_match': domain_match,
            'pattern_match': pattern_match,
            'embedding_similarity': embedding_similarity
        }
    
    def _check_domain_match(self, intention: IntentionBeing) -> float:
        """Sprawdza dopasowanie do domeny"""
        intention_domain = intention.metainfo.tags
        
        if self.context.domain in intention_domain:
            return 1.0
        elif any(tag in self.context.specialization for tag in intention_domain):
            return 0.7
        else:
            return 0.3
    
    def _check_pattern_match(self, intention: IntentionBeing) -> float:
        """Sprawdza dopasowanie wzorców"""
        intention_text = f"{intention.duchowa.opis_intencji} {intention.materialna.zadanie}"
        
        matches = 0
        for pattern in self.context.patterns:
            if pattern.lower() in intention_text.lower():
                matches += 1
        
        return min(1.0, matches / max(1, len(self.context.patterns)))
    
    def _calculate_embedding_similarity(self, intention: IntentionBeing, context: Dict[str, Any]) -> float:
        """Oblicza podobieństwo embeddings (symulacja)"""
        # Symulacja podobieństwa na podstawie słów kluczowych
        intention_words = set(intention.duchowa.opis_intencji.lower().split())
        context_words = set(str(context).lower().split())
        
        if not intention_words or not context_words:
            return 0.5
        
        intersection = intention_words.intersection(context_words)
        union = intention_words.union(context_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _execute_logical_processing(self, intention: IntentionBeing, context: Dict[str, Any], understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonuje logiczne przetwarzanie intencji"""
        
        # Wybierz odpowiednią strategię na podstawie typu logiki
        if self.logic_type == LogicType.ANALYTICAL:
            return self._analytical_processing(intention, context, understanding)
        elif self.logic_type == LogicType.CREATIVE:
            return self._creative_processing(intention, context, understanding)
        elif self.logic_type == LogicType.ADAPTIVE:
            return self._adaptive_processing(intention, context, understanding)
        elif self.logic_type == LogicType.COLLABORATIVE:
            return self._collaborative_processing(intention, context, understanding)
        elif self.logic_type == LogicType.EMERGENT:
            return self._emergent_processing(intention, context, understanding)
        else:
            return self._default_processing(intention, context, understanding)
    
    def _analytical_processing(self, intention: IntentionBeing, context: Dict[str, Any], understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Analityczne przetwarzanie"""
        analysis = {
            'intention_analysis': {
                'complexity': len(intention.materialna.wymagania),
                'priority': intention.priority.value,
                'feasibility': understanding['score'],
                'risk_factors': self._identify_risk_factors(intention)
            },
            'recommended_actions': self._generate_analytical_actions(intention),
            'next_steps': self._plan_analytical_steps(intention),
            'processing_type': 'analytical'
        }
        
        return analysis
    
    def _creative_processing(self, intention: IntentionBeing, context: Dict[str, Any], understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Kreatywne przetwarzanie"""
        
        # Generuj kreatywne rozwiązania
        creative_solutions = self._generate_creative_solutions(intention)
        
        # Stwórz mikro-funkcję jeśli potrzeba
        if understanding['score'] > 0.7:
            micro_func = self._create_creative_micro_function(intention)
            if micro_func:
                self.micro_functions[micro_func.name] = micro_func
        
        return {
            'creative_solutions': creative_solutions,
            'innovation_potential': understanding['score'] * 1.2,  # Kreatywność zwiększa potencjał
            'artistic_elements': self._identify_artistic_elements(intention),
            'processing_type': 'creative'
        }
    
    def _adaptive_processing(self, intention: IntentionBeing, context: Dict[str, Any], understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptacyjne przetwarzanie"""
        
        # Adaptuj się do kontekstu
        adapted_approach = self._adapt_to_context(intention, context)
        
        # Naucz się z tej interakcji
        self._learn_from_interaction(intention, context, understanding)
        
        return {
            'adapted_approach': adapted_approach,
            'learning_insights': self._extract_learning_insights(intention, context),
            'adaptation_level': understanding['score'],
            'processing_type': 'adaptive'
        }
    
    def _collaborative_processing(self, intention: IntentionBeing, context: Dict[str, Any], understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Współpracujące przetwarzanie"""
        
        # Znajdź innych bytów do współpracy
        collaborators = self._find_potential_collaborators(intention)
        
        # Podziel zadanie
        task_distribution = self._distribute_collaborative_tasks(intention, collaborators)
        
        return {
            'collaboration_plan': task_distribution,
            'potential_collaborators': [b.essence.soul_id for b in collaborators],
            'synergy_potential': len(collaborators) * understanding['score'],
            'processing_type': 'collaborative'
        }
    
    def _emergent_processing(self, intention: IntentionBeing, context: Dict[str, Any], understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Emergentne przetwarzanie"""
        
        # Pozwól na emergentne zachowania
        emergent_patterns = self._discover_emergent_patterns(intention, context)
        
        # Stwórz nowe algorytmy jeśli potrzeba
        if understanding['score'] > 0.8:
            new_algorithm = self._create_emergent_algorithm(intention)
            if new_algorithm:
                self.implicit_algorithms[f"emergent_{len(self.implicit_algorithms)}"] = new_algorithm
        
        return {
            'emergent_patterns': emergent_patterns,
            'system_evolution': self._assess_system_evolution(intention),
            'complexity_emergence': understanding['score'] * len(emergent_patterns),
            'processing_type': 'emergent'
        }
    
    def _request_clarification(self, intention: IntentionBeing, understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Żąda wyjaśnienia gdy brak zrozumienia"""
        
        clarification_questions = []
        
        if understanding.get('domain_match', 0) < 0.3:
            clarification_questions.append(
                f"Intencja '{intention.essence.name}' wykracza poza moją domenę ({self.context.domain}). "
                f"Czy możesz doprecyzować jak to związane z {self.context.specialization}?"
            )
        
        if understanding.get('pattern_match', 0) < 0.3:
            clarification_questions.append(
                f"Nie rozpoznaję wzorców w tej intencji. Czy możesz podać więcej szczegółów "
                f"o zadaniu: '{intention.materialna.zadanie}'?"
            )
        
        if understanding.get('embedding_similarity', 0) < 0.3:
            clarification_questions.append(
                f"Kontekst tej intencji jest dla mnie niejasny. Czy możesz wyjaśnić "
                f"związek między '{intention.duchowa.opis_intencji}' a oczekiwanym rezultatem?"
            )
        
        return {
            'status': 'clarification_needed',
            'understanding_level': understanding.get('level', UnderstandingLevel.NONE).value,
            'clarification_questions': clarification_questions,
            'suggestions': self._generate_clarification_suggestions(intention),
            'processing_type': 'clarification_request'
        }
    
    def create_micro_function(self, name: str, language: str, code: str, purpose: str) -> MicroFunction:
        """Tworzy nową mikro-funkcję"""
        micro_func = MicroFunction(
            name=name,
            language=language,
            code=code,
            purpose=purpose
        )
        
        self.micro_functions[name] = micro_func
        
        self.remember('micro_function_created', {
            'name': name,
            'language': language,
            'purpose': purpose,
            'timestamp': datetime.now().isoformat()
        })
        
        return micro_func
    
    def execute_micro_function(self, name: str, *args, **kwargs) -> Any:
        """Wykonuje mikro-funkcję"""
        if name not in self.micro_functions:
            raise ValueError(f"Mikro-funkcja '{name}' nie istnieje")
        
        func = self.micro_functions[name]
        result = func.execute(*args, **kwargs)
        
        self.remember('micro_function_executed', {
            'name': name,
            'args': str(args),
            'kwargs': str(kwargs),
            'result': str(result),
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    def connect_to_being(self, other_being: 'LogicalBeing', protocol_name: str = "default"):
        """Łączy się z innym bytem logicznym"""
        self.connected_beings[other_being.essence.soul_id] = other_being
        
        # Ustaw protokół współpracy
        if protocol_name not in self.collaboration_protocols:
            self.collaboration_protocols[protocol_name] = self._create_collaboration_protocol(other_being)
    
    def run_learning_cycle(self):
        """Uruchamia cykl uczenia się"""
        for loop in self.learning_loops:
            try:
                loop()
            except Exception as e:
                self.remember('learning_loop_error', {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status bytu logicznego"""
        base_status = super().get_status()
        
        logical_status = {
            'logical_being_specific': {
                'logic_type': self.logic_type.value,
                'understanding_level': self.understanding_level.value,
                'context': {
                    'domain': self.context.domain,
                    'specialization': self.context.specialization,
                    'patterns_count': len(self.context.patterns),
                    'knowledge_base_size': len(self.context.knowledge_base)
                },
                'micro_functions': {
                    'count': len(self.micro_functions),
                    'functions': [
                        {
                            'name': name,
                            'language': func.language,
                            'usage_count': func.usage_count,
                            'success_rate': func.success_rate
                        }
                        for name, func in self.micro_functions.items()
                    ]
                },
                'implicit_algorithms_count': len(self.implicit_algorithms),
                'connected_beings_count': len(self.connected_beings),
                'interaction_history_size': len(self.interaction_history),
                'understanding_failures_count': len(self.understanding_failures),
                'successful_patterns_count': len(self.successful_patterns)
            }
        }
        
        base_status.update(logical_status)
        return base_status
    
    # Pomocnicze metody (implementacje będą dodane w następnych iteracjach)
    def _extract_pattern(self, intention, context): return "generic_pattern"
    def _identify_risk_factors(self, intention): return ["complexity", "resource_requirements"]
    def _generate_analytical_actions(self, intention): return ["analyze", "plan", "execute"]
    def _plan_analytical_steps(self, intention): return ["step1", "step2", "step3"]
    def _generate_creative_solutions(self, intention): return ["solution1", "solution2"]
    def _create_creative_micro_function(self, intention): return None
    def _identify_artistic_elements(self, intention): return ["creativity", "innovation"]
    def _adapt_to_context(self, intention, context): return "adapted_approach"
    def _learn_from_interaction(self, intention, context, understanding): pass
    def _extract_learning_insights(self, intention, context): return ["insight1", "insight2"]
    def _find_potential_collaborators(self, intention): return []
    def _distribute_collaborative_tasks(self, intention, collaborators): return {}
    def _discover_emergent_patterns(self, intention, context): return ["pattern1", "pattern2"]
    def _create_emergent_algorithm(self, intention): return None
    def _assess_system_evolution(self, intention): return "evolving"
    def _generate_clarification_suggestions(self, intention): return ["suggestion1", "suggestion2"]
    def _optimize_micro_function(self, func_name): pass
    def _create_collaboration_protocol(self, other_being): return lambda: "collaborate"
    def _default_processing(self, intention, context, understanding): 
        return {"status": "processed", "processing_type": "default"}
