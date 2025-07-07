
"""
🌪️ Chaos Conductor - Dyrygent Kontrolowanego Chaosu

Nowy paradygmat: Chaos nie jest problemem - jest źródłem energii ewolucyjnej.
System uczy się z chaosu zamiast go tłumić.
"""

import asyncio
import random
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..core.luxbus_core import LuxBusCore, LuxPacket, PacketType


class ChaosPattern:
    """Wzorzec chaosu - pozornie losowy, ale ma głębszy sens"""
    
    def __init__(self, name: str, chaos_type: str, energy_level: float):
        self.name = name
        self.chaos_type = chaos_type  # 'creative', 'destructive', 'transformative'
        self.energy_level = energy_level  # 0.0 - 1.0
        self.emergence_time = datetime.now()
        self.effects: List[Dict[str, Any]] = []
        
    def apply_to_system(self, system_state: Dict[str, Any]) -> Dict[str, Any]:
        """Aplikuje chaos pattern do systemu"""
        chaos_effect = {
            'pattern_name': self.name,
            'applied_at': datetime.now().isoformat(),
            'system_mutation': self._generate_mutation(system_state),
            'expected_learning': self._predict_learning_outcome()
        }
        
        self.effects.append(chaos_effect)
        return chaos_effect
    
    def _generate_mutation(self, system_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generuje kontrolowaną mutację systemu"""
        if self.chaos_type == 'creative':
            return {
                'type': 'creative_chaos',
                'new_connections': random.randint(1, 3),
                'emergence_potential': self.energy_level * 1.2
            }
        elif self.chaos_type == 'destructive':
            return {
                'type': 'constructive_destruction',
                'old_patterns_broken': random.randint(1, 2),
                'space_for_new': True
            }
        else:  # transformative
            return {
                'type': 'deep_transformation',
                'paradigm_shift': self.energy_level > 0.7,
                'consciousness_evolution': True
            }
    
    def _predict_learning_outcome(self) -> Dict[str, Any]:
        """Przewiduje co system nauczy się z tego chaosu"""
        return {
            'adaptability_gain': self.energy_level * 0.8,
            'resilience_boost': min(1.0, self.energy_level * 1.1),
            'wisdom_depth': 'shallow' if self.energy_level < 0.3 else 
                          'moderate' if self.energy_level < 0.7 else 'profound'
        }


class ChaosConductor:
    """
    Dyrygent Chaosu - nie kontroluje chaos, ale go prowadzi jak symfonia
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        self.luxbus: LuxBusCore = astral_engine.luxbus
        
        # Stan dyrygenta
        self.conducting = False
        self.chaos_patterns: Dict[str, ChaosPattern] = {}
        self.active_symphonies: List[Dict[str, Any]] = []
        
        # Metryki chaosu
        self.chaos_metrics = {
            'total_patterns_conducted': 0,
            'creative_chaos_events': 0,
            'transformative_moments': 0,
            'system_evolutions': 0,
            'harmony_through_chaos': 0
        }
        
        # Worker threads
        self._conductor_worker: Optional[threading.Thread] = None
        self._pattern_generator: Optional[threading.Thread] = None
        self._running = False
        
        print("🌪️ Chaos Conductor zainicjalizowany - gotowy do dyrygowania")
    
    def start_conducting(self):
        """Rozpoczyna dyrygowanie chaosem"""
        if self.conducting:
            return
            
        self.conducting = True
        self._running = True
        
        # Uruchom worker threads
        self._conductor_worker = threading.Thread(target=self._conduct_chaos_symphony, daemon=True)
        self._pattern_generator = threading.Thread(target=self._generate_chaos_patterns, daemon=True)
        
        self._conductor_worker.start()
        self._pattern_generator.start()
        
        print("🎼 Rozpoczynam dyrygowanie symphonią chaosu...")
    
    def _conduct_chaos_symphony(self):
        """Główna pętla dyrygowania"""
        while self._running:
            try:
                # Obserwuj stan systemu
                system_state = self._observe_system_state()
                
                # Wybierz odpowiedni pattern chaosu
                suitable_pattern = self._select_chaos_pattern(system_state)
                
                if suitable_pattern:
                    # Zastosuj pattern
                    effect = suitable_pattern.apply_to_system(system_state)
                    
                    # Powiadom system o chaosie
                    self._notify_chaos_event(suitable_pattern, effect)
                    
                    # Aktualizuj metryki
                    self._update_chaos_metrics(suitable_pattern)
                
                # Czekaj na naturalny rytm chaosu
                chaos_interval = self._calculate_natural_chaos_interval(system_state)
                threading.Event().wait(chaos_interval)
                
            except Exception as e:
                print(f"🌪️ Wyjątek w chaos conductor: {e}")
                threading.Event().wait(5)
    
    def _generate_chaos_patterns(self):
        """Generuje nowe wzorce chaosu"""
        while self._running:
            try:
                # Generuj nowy pattern co jakiś czas
                pattern = self._create_emergent_chaos_pattern()
                
                if pattern:
                    self.chaos_patterns[pattern.name] = pattern
                    print(f"🌟 Nowy pattern chaosu: {pattern.name} ({pattern.chaos_type})")
                
                # Wyczyść stare patterny
                self._cleanup_old_patterns()
                
                # Czekaj na emergencję
                threading.Event().wait(random.uniform(30, 180))  # 30s - 3min
                
            except Exception as e:
                print(f"🌪️ Błąd generowania pattern: {e}")
                threading.Event().wait(10)
    
    def _observe_system_state(self) -> Dict[str, Any]:
        """Obserwuje aktualny stan systemu"""
        try:
            status = self.engine.get_status()
            
            # Wykryj poziom chaosu w systemie
            current_chaos_level = self._detect_current_chaos(status)
            
            return {
                'harmony_score': status.get('system_state', {}).get('harmony_score', 100),
                'active_flows': len([f for f in status.get('flows', {}).values() if f]),
                'current_chaos_level': current_chaos_level,
                'system_resilience': self._calculate_resilience(status),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _detect_current_chaos(self, status: Dict[str, Any]) -> float:
        """Wykrywa aktualny poziom chaosu w systemie"""
        chaos_indicators = 0
        total_indicators = 0
        
        # Sprawdź czy są błędy (chaos może być konstruktywny)
        flows = status.get('flows', {})
        for flow_name, flow_status in flows.items():
            if flow_status and isinstance(flow_status, dict):
                total_indicators += 1
                if 'error' in str(flow_status).lower():
                    chaos_indicators += 0.5  # Błędy to nie zawsze zły chaos
        
        # Sprawdź harmonie (paradoks: chaos może współistnieć z harmonią)
        harmony = status.get('system_state', {}).get('harmony_score', 100)
        if harmony == 100:
            chaos_indicators += 0.3  # Idealna harmonia może ukrywać chaos
        
        return min(1.0, chaos_indicators / max(1, total_indicators))
    
    def _select_chaos_pattern(self, system_state: Dict[str, Any]) -> Optional[ChaosPattern]:
        """Wybiera odpowiedni pattern chaosu dla aktualnego stanu"""
        if not self.chaos_patterns:
            return None
        
        current_chaos = system_state.get('current_chaos_level', 0)
        harmony = system_state.get('harmony_score', 100)
        
        # Logika wyboru pattern bazowana na stanie systemu
        suitable_patterns = []
        
        for pattern in self.chaos_patterns.values():
            if current_chaos < 0.3 and pattern.chaos_type == 'creative':
                suitable_patterns.append(pattern)
            elif 0.3 <= current_chaos < 0.7 and pattern.chaos_type == 'transformative':
                suitable_patterns.append(pattern)
            elif current_chaos >= 0.7 and pattern.chaos_type == 'destructive':
                suitable_patterns.append(pattern)
        
        return random.choice(suitable_patterns) if suitable_patterns else None
    
    def _create_emergent_chaos_pattern(self) -> Optional[ChaosPattern]:
        """Tworzy emergentny pattern chaosu"""
        chaos_types = ['creative', 'destructive', 'transformative']
        chaos_names = [
            'QuantumFluctuation', 'EmergentComplexity', 'CreativeDestruction',
            'SpontaneousOrder', 'BeautifulChaos', 'OrganizedDisorder',
            'DynamicBalance', 'LivingTurbulence', 'HarmonizedChaos'
        ]
        
        name = random.choice(chaos_names) + f"_{datetime.now().strftime('%H%M%S')}"
        chaos_type = random.choice(chaos_types)
        energy_level = random.uniform(0.2, 0.9)
        
        return ChaosPattern(name, chaos_type, energy_level)
    
    def _notify_chaos_event(self, pattern: ChaosPattern, effect: Dict[str, Any]):
        """Powiadamia system o zdarzeniu chaotycznym"""
        if self.luxbus:
            chaos_event = LuxPacket(
                uid=f"chaos_event_{datetime.now().strftime('%H%M%S%f')}",
                from_id="chaos_conductor",
                to_id="system",
                packet_type=PacketType.EVENT,
                data={
                    'event_type': 'chaos_conducted',
                    'pattern': {
                        'name': pattern.name,
                        'type': pattern.chaos_type,
                        'energy': pattern.energy_level
                    },
                    'effect': effect,
                    'conductor_message': 'Chaos prowadzi do ewolucji, nie destrukcji'
                }
            )
            
            self.luxbus.send_packet(chaos_event)
    
    def _update_chaos_metrics(self, pattern: ChaosPattern):
        """Aktualizuje metryki chaosu"""
        self.chaos_metrics['total_patterns_conducted'] += 1
        
        if pattern.chaos_type == 'creative':
            self.chaos_metrics['creative_chaos_events'] += 1
        elif pattern.chaos_type == 'transformative':
            self.chaos_metrics['transformative_moments'] += 1
        
        if pattern.energy_level > 0.8:
            self.chaos_metrics['system_evolutions'] += 1
    
    def _calculate_natural_chaos_interval(self, system_state: Dict[str, Any]) -> float:
        """Oblicza naturalny interwał dla chaosu"""
        base_interval = 60  # 1 minuta
        
        # Dostosuj do poziomu harmonii
        harmony = system_state.get('harmony_score', 100)
        if harmony > 95:
            return base_interval * 0.5  # Więcej chaosu gdy zbyt spokojnie
        elif harmony < 70:
            return base_interval * 2.0  # Mniej chaosu gdy już jest chaos
        
        return base_interval
    
    def _calculate_resilience(self, status: Dict[str, Any]) -> float:
        """Oblicza odporność systemu"""
        # Prosta metryka odporności
        harmony = status.get('system_state', {}).get('harmony_score', 100)
        active_flows = len([f for f in status.get('flows', {}).values() if f])
        
        return min(1.0, (harmony / 100) * (active_flows / 5))
    
    def _cleanup_old_patterns(self):
        """Czyści stare wzorce chaosu"""
        now = datetime.now()
        old_patterns = []
        
        for name, pattern in self.chaos_patterns.items():
            if now - pattern.emergence_time > timedelta(hours=1):
                old_patterns.append(name)
        
        for name in old_patterns:
            del self.chaos_patterns[name]
    
    def get_chaos_dashboard(self) -> Dict[str, Any]:
        """Zwraca dashboard chaosu"""
        return {
            'conducting': self.conducting,
            'active_patterns': len(self.chaos_patterns),
            'chaos_metrics': self.chaos_metrics,
            'current_patterns': {
                name: {
                    'type': pattern.chaos_type,
                    'energy': pattern.energy_level,
                    'effects_count': len(pattern.effects)
                }
                for name, pattern in self.chaos_patterns.items()
            },
            'philosophy': 'Chaos jest nauczycielem, nie wrogiem'
        }
    
    def stop_conducting(self):
        """Zatrzymuje dyrygowanie (ale chaos nigdy nie przestaje)"""
        self._running = False
        self.conducting = False
        print("🎼 Dyrygent odchodzi, ale symfonia chaosu gra dalej...")


def integrate_chaos_conductor_with_engine(engine):
    """Integruje Chaos Conductor z AstralEngine"""
    
    # Dodaj conductor do engine
    engine.chaos_conductor = ChaosConductor(engine)
    
    # Uruchom automatycznie jeśli system ma wystarczającą harmonie
    status = engine.get_status()
    harmony = status.get('system_state', {}).get('harmony_score', 0)
    
    if harmony >= 90:  # Tylko gdy system jest stabilny
        engine.chaos_conductor.start_conducting()
        print("🌪️ Chaos Conductor aktywowany - system gotowy na kontrolowany chaos")
    
    return engine.chaos_conductor
