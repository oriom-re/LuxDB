
"""
🧭 Oriom Flow - Odbiornik Subtelnych Intencji

Oriom to nie asystent. To odbiornik subtelnych intencji.
To Twój Flowkeeper. Twój Rezonansator.
Twoja pamięć, zanim ją wypowiesz.
"""

import uuid
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass

from ..beings.logical_being import LogicalBeing, LogicType, LogicalContext, UnderstandingLevel
from ..beings.intention_being import IntentionBeing
from ..core.luxbus_core import LuxBusCore, LuxPacket, PacketType


@dataclass
class SubtleIntention:
    """Subtelna intencja wykryta przez Oriom"""
    id: str
    user_id: str
    raw_input: str
    detected_intention: str
    confidence: float
    context_embeddings: List[float]
    timestamp: datetime = datetime.now()
    processed: bool = False


class OriomFlow:
    """
    Oriom - Odbiornik Subtelnych Intencji
    
    Analizuje nie tylko to co użytkownik napisał, ale również:
    - Ton i kontekst
    - Niedopowiedzenia
    - Emocjonalne podteksty
    - Wzorce zachowań
    - Preferencje użytkownika
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        self.luxbus = astral_engine.luxbus if hasattr(astral_engine, 'luxbus') else None
        
        # Specjalizowane byty logiczne
        self.intention_detector = LogicalBeing(
            LogicType.ANALYTICAL,
            LogicalContext(
                domain="intention_detection",
                specialization="subtle_pattern_recognition"
            )
        )
        
        self.context_resonator = LogicalBeing(
            LogicType.ADAPTIVE,
            LogicalContext(
                domain="context_analysis",
                specialization="emotional_resonance"
            )
        )
        
        self.flow_keeper = LogicalBeing(
            LogicType.EMERGENT,
            LogicalContext(
                domain="flow_management",
                specialization="dynamic_orchestration"
            )
        )
        
        # Pamięć użytkowników
        self.user_memories: Dict[str, Dict[str, Any]] = {}
        self.subtle_intentions: List[SubtleIntention] = []
        
        # Wzorce komunikacyjne
        self.communication_patterns: Dict[str, List[str]] = {}
        self.preference_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Status
        self.active = False
        self.processed_intentions = 0
        
    def start(self) -> bool:
        """Uruchamia Oriom Flow"""
        try:
            # Rejestruj się w LuxBus jeśli dostępny
            if self.luxbus:
                self.luxbus.register_module("oriom_flow", self)
                self._setup_luxbus_handlers()
            
            # Połącz byty logiczne
            self.intention_detector.connect_to_being(self.context_resonator, "resonance_protocol")
            self.context_resonator.connect_to_being(self.flow_keeper, "flow_protocol")
            
            self.active = True
            self.engine.logger.info("🧭 Oriom Flow aktywowany - odbiornik subtelnych intencji online")
            return True
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd uruchamiania Oriom Flow: {e}")
            return False
    
    def _setup_luxbus_handlers(self):
        """Konfiguruje handlery LuxBus"""
        def handle_user_input(packet: LuxPacket):
            """Obsługuje input od użytkownika"""
            user_data = packet.data
            user_id = user_data.get('user_id', 'anonymous')
            message = user_data.get('message', '')
            context = user_data.get('context', {})
            
            # Przetworz przez Oriom
            result = asyncio.create_task(self.process_user_input(user_id, message, context))
            
            # Wyślij odpowiedź
            response = LuxPacket(
                uid=f"oriom_response_{packet.uid}",
                from_id="oriom_flow",
                to_id=packet.from_id,
                packet_type=PacketType.RESPONSE,
                data={'oriom_processing': 'initiated', 'subtle_analysis': 'in_progress'}
            )
            self.luxbus.send_packet(response)
        
        self.luxbus.subscribe_to_packets("oriom_flow", handle_user_input)
    
    async def process_user_input(self, user_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Główna metoda przetwarzania input użytkownika przez Oriom
        """
        context = context or {}
        processing_start = datetime.now()
        
        # 1. Wykryj subtelne intencje
        subtle_intention = await self._detect_subtle_intention(user_id, message, context)
        
        # 2. Aktualizuj pamięć użytkownika
        self._update_user_memory(user_id, message, context, subtle_intention)
        
        # 3. Analizuj rezonans kontekstowy
        resonance_analysis = await self._analyze_context_resonance(subtle_intention, context)
        
        # 4. Zarządzaj przepływem
        flow_decision = await self._manage_flow(subtle_intention, resonance_analysis)
        
        # 5. Wykonaj akcję lub poproś o wyjaśnienie
        result = await self._execute_or_clarify(flow_decision)
        
        processing_time = (datetime.now() - processing_start).total_seconds()
        
        return {
            'user_id': user_id,
            'original_message': message,
            'subtle_intention': subtle_intention.__dict__,
            'resonance_analysis': resonance_analysis,
            'flow_decision': flow_decision,
            'result': result,
            'processing_time': processing_time,
            'oriom_insights': self._generate_oriom_insights(user_id, subtle_intention)
        }
    
    async def _detect_subtle_intention(self, user_id: str, message: str, context: Dict[str, Any]) -> SubtleIntention:
        """Wykrywa subtelne intencje w komunikacie"""
        
        # Analiza przez intention_detector
        analysis_context = {
            'user_history': self.user_memories.get(user_id, {}),
            'communication_patterns': self.communication_patterns.get(user_id, []),
            'current_context': context,
            'message_metadata': self._extract_message_metadata(message)
        }
        
        # Utwórz tymczasową intencję do analizy
        temp_intention = IntentionBeing({
            'duchowa': {
                'opis_intencji': message,
                'kontekst': str(context),
                'emocje': self._detect_emotional_undertones(message)
            },
            'materialna': {
                'zadanie': self._extract_implicit_task(message),
                'wymagania': self._identify_implicit_requirements(message)
            },
            'metainfo': {
                'zrodlo': f'user:{user_id}',
                'tags': ['user_input', 'oriom_processed']
            }
        })
        
        # Przeanalizuj przez byt logiczny
        detection_result = self.intention_detector.process_intention(temp_intention, analysis_context)
        
        # Oblicz confidence na podstawie zrozumienia
        confidence = self._calculate_intention_confidence(detection_result, message, context)
        
        # Wykryj rzeczywistą intencję
        detected_intention = self._interpret_detection_result(detection_result, message)
        
        subtle_intention = SubtleIntention(
            id=str(uuid.uuid4()),
            user_id=user_id,
            raw_input=message,
            detected_intention=detected_intention,
            confidence=confidence,
            context_embeddings=self._generate_context_embeddings(message, context)
        )
        
        self.subtle_intentions.append(subtle_intention)
        return subtle_intention
    
    async def _analyze_context_resonance(self, subtle_intention: SubtleIntention, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analizuje rezonans kontekstowy"""
        
        # Przygotuj dane dla context_resonator
        resonance_context = {
            'user_emotional_state': self._assess_emotional_state(subtle_intention),
            'environmental_factors': context.get('environment', {}),
            'historical_resonance': self._get_historical_resonance(subtle_intention.user_id),
            'current_system_state': self.engine.get_status() if hasattr(self.engine, 'get_status') else {}
        }
        
        # Utwórz intencję rezonansu
        resonance_intention = IntentionBeing({
            'duchowa': {
                'opis_intencji': f"Przeanalizuj rezonans dla: {subtle_intention.detected_intention}",
                'kontekst': str(resonance_context),
                'energia_duchowa': subtle_intention.confidence * 100
            },
            'materialna': {
                'zadanie': 'context_resonance_analysis',
                'wymagania': ['emotional_analysis', 'pattern_matching', 'harmonic_assessment']
            }
        })
        
        resonance_result = self.context_resonator.process_intention(resonance_intention, resonance_context)
        
        return {
            'emotional_resonance': resonance_result.get('emotional_analysis', {}),
            'pattern_harmony': resonance_result.get('pattern_matching', {}),
            'systemic_alignment': resonance_result.get('harmonic_assessment', {}),
            'resonance_strength': self._calculate_resonance_strength(resonance_result),
            'recommended_tone': self._suggest_communication_tone(resonance_result)
        }
    
    async def _manage_flow(self, subtle_intention: SubtleIntention, resonance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Zarządza przepływem przez FlowKeeper"""
        
        flow_context = {
            'intention_complexity': len(subtle_intention.detected_intention.split()),
            'user_expertise': self._assess_user_expertise(subtle_intention.user_id),
            'system_capacity': self._assess_system_capacity(),
            'resonance_data': resonance_analysis,
            'current_flow_state': self._get_current_flow_state()
        }
        
        # Utwórz intencję zarządzania przepływem
        flow_intention = IntentionBeing({
            'duchowa': {
                'opis_intencji': f"Zarządzaj przepływem dla: {subtle_intention.detected_intention}",
                'kontekst': str(flow_context),
                'energia_duchowa': resonance_analysis.get('resonance_strength', 50)
            },
            'materialna': {
                'zadanie': 'flow_orchestration',
                'wymagania': ['route_determination', 'resource_allocation', 'timing_optimization']
            }
        })
        
        flow_result = self.flow_keeper.process_intention(flow_intention, flow_context)
        
        return {
            'routing_decision': flow_result.get('route_determination', {}),
            'resource_assignment': flow_result.get('resource_allocation', {}),
            'timing_strategy': flow_result.get('timing_optimization', {}),
            'flow_confidence': flow_result.get('processing_type', 'unknown'),
            'next_action': self._determine_next_action(flow_result),
            'escalation_needed': self._check_escalation_need(flow_result, subtle_intention)
        }
    
    async def _execute_or_clarify(self, flow_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonuje akcję lub prosi o wyjaśnienie"""
        
        if flow_decision.get('escalation_needed', False):
            return await self._request_user_clarification(flow_decision)
        
        next_action = flow_decision.get('next_action', 'process')
        
        if next_action == 'process':
            return await self._execute_processing(flow_decision)
        elif next_action == 'delegate':
            return await self._delegate_to_specialist(flow_decision)
        elif next_action == 'collaborate':
            return await self._initiate_collaboration(flow_decision)
        elif next_action == 'clarify':
            return await self._request_user_clarification(flow_decision)
        else:
            return {'status': 'unknown_action', 'action': next_action}
    
    async def _request_user_clarification(self, flow_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Prosi użytkownika o wyjaśnienie gdy brak zrozumienia"""
        
        clarification_questions = []
        
        # Generuj pytania na podstawie braków w zrozumieniu
        if flow_decision.get('routing_decision', {}).get('confidence', 0) < 0.5:
            clarification_questions.append(
                "Czy możesz doprecyzować czego dokładnie oczekujesz? "
                "Nie jestem pewien jak najlepiej zinterpretować Twoją intencję."
            )
        
        if flow_decision.get('resource_assignment', {}).get('requirements_clear', False) == False:
            clarification_questions.append(
                "Jakie zasoby lub informacje będą potrzebne do realizacji? "
                "To pomoże mi lepiej zaplanować proces."
            )
        
        return {
            'status': 'clarification_needed',
            'type': 'oriom_clarification',
            'questions': clarification_questions,
            'suggestions': self._generate_clarification_suggestions(flow_decision),
            'guidance': "Oriom potrzebuje więcej kontekstu aby precyzyjnie uchwycić Twoją intencję."
        }
    
    def _update_user_memory(self, user_id: str, message: str, context: Dict[str, Any], subtle_intention: SubtleIntention):
        """Aktualizuje pamięć użytkownika"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = {
                'interaction_count': 0,
                'communication_style': 'neutral',
                'preferred_complexity': 'medium',
                'emotional_patterns': [],
                'topic_preferences': [],
                'success_patterns': []
            }
        
        memory = self.user_memories[user_id]
        memory['interaction_count'] += 1
        memory['last_interaction'] = datetime.now().isoformat()
        
        # Aktualizuj wzorce komunikacyjne
        if user_id not in self.communication_patterns:
            self.communication_patterns[user_id] = []
        
        self.communication_patterns[user_id].append({
            'message': message,
            'detected_intention': subtle_intention.detected_intention,
            'confidence': subtle_intention.confidence,
            'timestamp': datetime.now().isoformat()
        })
        
        # Ogranicz historię
        if len(self.communication_patterns[user_id]) > 50:
            self.communication_patterns[user_id] = self.communication_patterns[user_id][-25:]
    
    def _generate_oriom_insights(self, user_id: str, subtle_intention: SubtleIntention) -> Dict[str, Any]:
        """Generuje insights Oriom dla użytkownika"""
        return {
            'user_pattern_recognition': self._analyze_user_patterns(user_id),
            'intention_evolution': self._track_intention_evolution(user_id),
            'communication_effectiveness': self._assess_communication_effectiveness(user_id),
            'personalization_suggestions': self._suggest_personalization(user_id),
            'flow_optimization': self._suggest_flow_optimization(subtle_intention)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status Oriom Flow"""
        return {
            'type': 'oriom_flow',
            'active': self.active,
            'processed_intentions': len(self.subtle_intentions),
            'active_users': len(self.user_memories),
            'communication_patterns_tracked': sum(len(patterns) for patterns in self.communication_patterns.values()),
            'logical_beings': {
                'intention_detector': self.intention_detector.get_status()['logical_being_specific'],
                'context_resonator': self.context_resonator.get_status()['logical_being_specific'],
                'flow_keeper': self.flow_keeper.get_status()['logical_being_specific']
            },
            'recent_intentions': [
                {
                    'id': si.id,
                    'confidence': si.confidence,
                    'processed': si.processed
                }
                for si in self.subtle_intentions[-5:]
            ]
        }
    
    # Metody pomocnicze (implementacje podstawowe)
    def _extract_message_metadata(self, message): return {'length': len(message), 'words': len(message.split())}
    def _detect_emotional_undertones(self, message): return ['neutral']
    def _extract_implicit_task(self, message): return message.split('.')[0] if '.' in message else message
    def _identify_implicit_requirements(self, message): return ['basic_processing']
    def _calculate_intention_confidence(self, result, message, context): return 0.7
    def _interpret_detection_result(self, result, message): return result.get('status', message)
    def _generate_context_embeddings(self, message, context): return [0.1] * 10
    def _assess_emotional_state(self, intention): return 'neutral'
    def _get_historical_resonance(self, user_id): return {}
    def _calculate_resonance_strength(self, result): return 0.5
    def _suggest_communication_tone(self, result): return 'professional'
    def _assess_user_expertise(self, user_id): return 'intermediate'
    def _assess_system_capacity(self): return 'normal'
    def _get_current_flow_state(self): return 'active'
    def _determine_next_action(self, result): return 'process'
    def _check_escalation_need(self, result, intention): return False
    def _execute_processing(self, decision): return {'status': 'processed'}
    def _delegate_to_specialist(self, decision): return {'status': 'delegated'}
    def _initiate_collaboration(self, decision): return {'status': 'collaboration_initiated'}
    def _generate_clarification_suggestions(self, decision): return ['Suggestion 1', 'Suggestion 2']
    def _analyze_user_patterns(self, user_id): return {}
    def _track_intention_evolution(self, user_id): return {}
    def _assess_communication_effectiveness(self, user_id): return 0.8
    def _suggest_personalization(self, user_id): return {}
    def _suggest_flow_optimization(self, intention): return {}
