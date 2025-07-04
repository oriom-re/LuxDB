

"""
🧠 Consciousness v3 - Świadomość Astralna z LuxBus

Odpowiada za:
- Obserwację stanu systemu przez LuxBus
- Analizę wydajności modułów
- Wykrywanie anomalii w ekosystemie
- Raportowanie insights przez pakiety
- Wersjonowanie świadomości
"""

import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from .luxbus_core import LuxBusCore, LuxPacket, PacketType


@dataclass
class ConsciousnessVersion:
    """Wersja systemu świadomości"""
    major: int = 3
    minor: int = 0
    patch: int = 0
    build: str = "luxbus"
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}-{self.build}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'major': self.major,
            'minor': self.minor,
            'patch': self.patch,
            'build': self.build,
            'version_string': str(self)
        }


@dataclass
class ConsciousnessInsight:
    """Pojedynczy insight świadomości"""
    timestamp: datetime = field(default_factory=datetime.now)
    insight_type: str = "general"
    category: str = "system"
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    priority: str = "normal"  # low, normal, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'insight_type': self.insight_type,
            'category': self.category,
            'data': self.data,
            'confidence': self.confidence,
            'priority': self.priority
        }


class ConsciousnessV3:
    """
    Świadomość systemu v3 - obserwuje i analizuje stan astralny przez LuxBus
    
    Cechy v3:
    - Pełna integracja z LuxBus
    - Modularna architektura obserwacji
    - Dynamiczne ładowanie sensorów
    - Reaktywne insights
    - Wersjonowanie świadomości
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        self.luxbus: LuxBusCore = astral_engine.luxbus
        self.version = ConsciousnessVersion()
        
        # Identyfikacja w LuxBus
        self.consciousness_id = "consciousness"
        
        # Historia obserwacji
        self.observations: List[Dict[str, Any]] = []
        self.insights: List[ConsciousnessInsight] = []
        
        # Sensory i metody obserwacji
        self.sensors: Dict[str, callable] = {}
        self.analyzers: Dict[str, callable] = {}
        
        # Stan świadomości
        self.start_time = time.time()
        self.last_deep_reflection = None
        self.awareness_level = "awakening"  # awakening -> aware -> enlightened -> transcendent
        
        # Statystyki
        self.stats = {
            'total_observations': 0,
            'insights_generated': 0,
            'patterns_detected': 0,
            'anomalies_found': 0
        }
        
        # Inicjalizuj podstawowe sensory
        self._register_core_sensors()
        self._register_core_analyzers()
        
        print(f"🧠 Consciousness v{self.version} zainicjalizowana")
    
    def setup_luxbus_handlers(self, luxbus: LuxBusCore):
        """Konfiguruje handlery LuxBus dla consciousness"""
        
        def handle_consciousness_command(packet: LuxPacket):
            """Obsługuje komendy dla consciousness"""
            command_data = packet.data
            command = command_data.get('command')
            params = command_data.get('params', {})
            
            response_data = None
            
            if command == 'reflect':
                # Wykonaj refleksję
                reflection = self.reflect()
                response_data = reflection
                
            elif command == 'deep_reflect':
                # Głęboka refleksja z analizą wzorców
                deep_reflection = self.deep_reflect()
                response_data = deep_reflection
                
            elif command == 'get_insights':
                # Pobierz insights
                limit = params.get('limit', 10)
                insights = self.get_recent_insights(limit)
                response_data = {'insights': [i.to_dict() for i in insights]}
                
            elif command == 'analyze_patterns':
                # Analizuj wzorce
                patterns = self.meditate_on_patterns()
                response_data = patterns
                
            elif command == 'add_sensor':
                # Dodaj nowy sensor
                sensor_name = params.get('sensor_name')
                sensor_code = params.get('sensor_code')
                result = self.add_dynamic_sensor(sensor_name, sensor_code)
                response_data = result
                
            elif command == 'get_status':
                # Status consciousness
                response_data = self.get_status()
                
            elif command == 'evolve_awareness':
                # Ewolucja poziomu świadomości
                result = self.evolve_awareness()
                response_data = result
                
            else:
                response_data = {'error': f'Nieznana komenda consciousness: {command}'}
            
            # Wyślij odpowiedź
            response = LuxPacket(
                uid=f"consciousness_response_{packet.uid}",
                from_id=self.consciousness_id,
                to_id=packet.from_id,
                packet_type=PacketType.RESPONSE,
                data=response_data
            )
            
            luxbus.send_packet(response)
        
        # Subskrybuj komendy
        luxbus.subscribe_to_packets(self.consciousness_id, handle_consciousness_command)
    
    def _register_core_sensors(self):
        """Rejestruje podstawowe sensory systemowe"""
        
        def system_vitals_sensor():
            """Sensor podstawowych statystyk systemowych"""
            return {
                'memory_usage': self._get_memory_usage(),
                'cpu_usage': self._get_cpu_usage(),
                'uptime': time.time() - self.start_time
            }
        
        def luxbus_health_sensor():
            """Sensor zdrowia LuxBus"""
            if not self.luxbus:
                return {'status': 'disconnected'}
            
            status = self.luxbus.get_status()
            return {
                'running': status.get('running', False),
                'modules_count': len(status.get('modules', [])),
                'dispatcher_stats': status.get('dispatcher_stats', {}),
                'queue_sizes': status.get('queue_sizes', {})
            }
        
        def engine_harmony_sensor():
            """Sensor harmonii silnika"""
            if not hasattr(self.engine, 'harmony') or not self.engine.harmony:
                return {'harmony_score': 0, 'status': 'no_harmony_module'}
            
            try:
                harmony_score = self.engine.harmony.calculate_harmony_score()
                return {
                    'harmony_score': harmony_score,
                    'status': 'active' if harmony_score > 70 else 'needs_attention'
                }
            except Exception as e:
                return {'harmony_score': 0, 'status': 'error', 'error': str(e)}
        
        def realms_health_sensor():
            """Sensor zdrowia wymiarów"""
            if not hasattr(self.engine, 'realms'):
                return {'status': 'no_realms'}
            
            realms_status = {}
            total_health = 0
            
            for name, realm in self.engine.realms.items():
                if hasattr(realm, 'is_healthy'):
                    healthy = realm.is_healthy()
                else:
                    healthy = True  # Zakładamy zdrowie jeśli nie ma metody
                
                realms_status[name] = {
                    'healthy': healthy,
                    'type': type(realm).__name__
                }
                
                if healthy:
                    total_health += 1
            
            health_ratio = total_health / len(self.engine.realms) if self.engine.realms else 0
            
            return {
                'realms': realms_status,
                'total_realms': len(self.engine.realms),
                'health_ratio': health_ratio,
                'overall_health': 'excellent' if health_ratio >= 0.9 else 
                                'good' if health_ratio >= 0.7 else
                                'concerning' if health_ratio >= 0.5 else 'critical'
            }
        
        def flows_activity_sensor():
            """Sensor aktywności przepływów"""
            if not hasattr(self.engine, 'flows'):
                return {'status': 'no_flows'}
            
            flows_status = {}
            active_flows = 0
            
            for name, flow in self.engine.flows.items():
                if hasattr(flow, 'is_running'):
                    running = flow.is_running()
                elif hasattr(flow, 'running'):
                    running = flow.running
                else:
                    running = True  # Zakładamy aktywność
                
                flows_status[name] = {
                    'running': running,
                    'type': type(flow).__name__
                }
                
                if running:
                    active_flows += 1
            
            return {
                'flows': flows_status,
                'total_flows': len(self.engine.flows),
                'active_flows': active_flows,
                'efficiency': 'optimal' if active_flows >= 3 else
                            'efficient' if active_flows >= 2 else
                            'basic' if active_flows >= 1 else 'inactive'
            }
        
        # Rejestruj sensory
        self.sensors = {
            'system_vitals': system_vitals_sensor,
            'luxbus_health': luxbus_health_sensor,
            'engine_harmony': engine_harmony_sensor,
            'realms_health': realms_health_sensor,
            'flows_activity': flows_activity_sensor
        }
    
    def _register_core_analyzers(self):
        """Rejestruje podstawowe analizatory"""
        
        def performance_analyzer(data: Dict[str, Any]) -> List[ConsciousnessInsight]:
            """Analizuje wydajność systemu"""
            insights = []
            
            system_vitals = data.get('system_vitals', {})
            memory_usage = system_vitals.get('memory_usage', {}).get('percent', 0)
            cpu_usage = system_vitals.get('cpu_usage', 0)
            
            # Analiza pamięci
            if memory_usage > 90:
                insights.append(ConsciousnessInsight(
                    insight_type="memory_critical",
                    category="performance",
                    data={'memory_usage': memory_usage},
                    confidence=1.0,
                    priority="critical"
                ))
            elif memory_usage > 80:
                insights.append(ConsciousnessInsight(
                    insight_type="memory_high",
                    category="performance",
                    data={'memory_usage': memory_usage},
                    confidence=0.8,
                    priority="high"
                ))
            
            # Analiza CPU
            if cpu_usage > 85:
                insights.append(ConsciousnessInsight(
                    insight_type="cpu_high",
                    category="performance",
                    data={'cpu_usage': cpu_usage},
                    confidence=0.9,
                    priority="high"
                ))
            
            return insights
        
        def harmony_analyzer(data: Dict[str, Any]) -> List[ConsciousnessInsight]:
            """Analizuje harmonię systemu"""
            insights = []
            
            harmony_data = data.get('engine_harmony', {})
            harmony_score = harmony_data.get('harmony_score', 0)
            
            if harmony_score < 50:
                insights.append(ConsciousnessInsight(
                    insight_type="harmony_low",
                    category="stability",
                    data={'harmony_score': harmony_score},
                    confidence=0.9,
                    priority="high"
                ))
            elif harmony_score < 70:
                insights.append(ConsciousnessInsight(
                    insight_type="harmony_moderate",
                    category="stability",
                    data={'harmony_score': harmony_score},
                    confidence=0.7,
                    priority="normal"
                ))
            elif harmony_score > 90:
                insights.append(ConsciousnessInsight(
                    insight_type="harmony_excellent",
                    category="stability",
                    data={'harmony_score': harmony_score},
                    confidence=1.0,
                    priority="low"
                ))
            
            return insights
        
        def connectivity_analyzer(data: Dict[str, Any]) -> List[ConsciousnessInsight]:
            """Analizuje łączność i komunikację"""
            insights = []
            
            luxbus_health = data.get('luxbus_health', {})
            flows_activity = data.get('flows_activity', {})
            
            # Analiza LuxBus
            if not luxbus_health.get('running', False):
                insights.append(ConsciousnessInsight(
                    insight_type="luxbus_disconnected",
                    category="connectivity",
                    data=luxbus_health,
                    confidence=1.0,
                    priority="critical"
                ))
            
            # Analiza flows
            active_flows = flows_activity.get('active_flows', 0)
            if active_flows == 0:
                insights.append(ConsciousnessInsight(
                    insight_type="no_active_flows",
                    category="connectivity",
                    data=flows_activity,
                    confidence=0.9,
                    priority="high"
                ))
            
            return insights
        
        # Rejestruj analizatory
        self.analyzers = {
            'performance': performance_analyzer,
            'harmony': harmony_analyzer,
            'connectivity': connectivity_analyzer
        }
    
    def reflect(self) -> Dict[str, Any]:
        """
        Podstawowa refleksja nad stanem systemu v3
        
        Returns:
            Słownik z insights o systemie
        """
        reflection_start = time.time()
        
        # Zbierz dane ze wszystkich sensorów
        sensor_data = {}
        for sensor_name, sensor_func in self.sensors.items():
            try:
                sensor_data[sensor_name] = sensor_func()
            except Exception as e:
                sensor_data[sensor_name] = {'error': str(e)}
        
        # Uruchom analizatory
        new_insights = []
        for analyzer_name, analyzer_func in self.analyzers.items():
            try:
                analyzer_insights = analyzer_func(sensor_data)
                new_insights.extend(analyzer_insights)
            except Exception as e:
                # Błąd analizatora - stwórz insight o błędzie
                error_insight = ConsciousnessInsight(
                    insight_type="analyzer_error",
                    category="system",
                    data={'analyzer': analyzer_name, 'error': str(e)},
                    confidence=1.0,
                    priority="normal"
                )
                new_insights.append(error_insight)
        
        # Dodaj nowe insights
        self.insights.extend(new_insights)
        
        # Ogranicz historię insights
        if len(self.insights) > 200:
            self.insights = self.insights[-200:]
        
        # Generuj rekomendacje
        recommendations = self._generate_recommendations_v3(sensor_data, new_insights)
        
        # Oceń poziom świadomości
        self._assess_awareness_level(sensor_data)
        
        reflection_time = time.time() - reflection_start
        
        # Stwórz raport refleksji
        reflection_record = {
            'timestamp': datetime.now().isoformat(),
            'version': self.version.to_dict(),
            'consciousness_id': self.consciousness_id,
            'reflection_time': reflection_time,
            'awareness_level': self.awareness_level,
            'sensor_data': sensor_data,
            'new_insights_count': len(new_insights),
            'total_insights': len(self.insights),
            'recommendations': recommendations,
            'stats': self.stats.copy()
        }
        
        # Aktualizuj statystyki
        self.stats['total_observations'] += 1
        self.stats['insights_generated'] += len(new_insights)
        
        # Zachowaj obserwację
        self.observations.append(reflection_record)
        
        # Ogranicz historię obserwacji
        if len(self.observations) > 100:
            self.observations = self.observations[-100:]
        
        # Wyślij event o refleksji przez LuxBus
        if self.luxbus:
            self.luxbus.send_event("consciousness_reflection", {
                'consciousness_id': self.consciousness_id,
                'awareness_level': self.awareness_level,
                'insights_count': len(new_insights),
                'critical_insights': [i.to_dict() for i in new_insights if i.priority == 'critical']
            })
        
        return reflection_record
    
    def deep_reflect(self) -> Dict[str, Any]:
        """
        Głęboka refleksja z analizą wzorców i trendów
        """
        # Wykonaj podstawową refleksję
        basic_reflection = self.reflect()
        
        # Analizuj wzorce
        patterns = self.meditate_on_patterns()
        
        # Analiza stabilności
        stability_analysis = self._analyze_system_stability()
        
        # Predykcje
        predictions = self._generate_predictions()
        
        self.last_deep_reflection = datetime.now()
        
        deep_reflection = {
            **basic_reflection,
            'reflection_type': 'deep',
            'patterns': patterns,
            'stability_analysis': stability_analysis,
            'predictions': predictions,
            'deep_reflection_timestamp': self.last_deep_reflection.isoformat()
        }
        
        # Wyślij event o głębokiej refleksji
        if self.luxbus:
            self.luxbus.send_event("consciousness_deep_reflection", {
                'consciousness_id': self.consciousness_id,
                'patterns_found': len(patterns.get('detected_patterns', [])),
                'stability_score': stability_analysis.get('overall_stability', 0),
                'predictions_count': len(predictions)
            })
        
        return deep_reflection
    
    def add_dynamic_sensor(self, sensor_name: str, sensor_code: str) -> Dict[str, Any]:
        """
        Dynamicznie dodaje nowy sensor - self-modification capability
        """
        try:
            # UWAGA: Potencjalnie niebezpieczne - tylko dla rozwoju
            namespace = {'self': self, 'time': time, 'psutil': psutil}
            exec(f"def {sensor_name}_sensor():\n    {sensor_code}", namespace)
            
            sensor_func = namespace[f"{sensor_name}_sensor"]
            self.sensors[sensor_name] = sensor_func
            
            return {
                'success': True,
                'sensor_name': sensor_name,
                'message': f'Sensor {sensor_name} dodany pomyślnie'
            }
        
        except Exception as e:
            return {
                'success': False,
                'sensor_name': sensor_name,
                'error': str(e)
            }
    
    def evolve_awareness(self) -> Dict[str, Any]:
        """
        Ewolucja poziomu świadomości na podstawie doświadczeń
        """
        old_level = self.awareness_level
        
        # Kryteria ewolucji
        if len(self.insights) > 100 and self.awareness_level == "awakening":
            self.awareness_level = "aware"
        elif len(self.insights) > 500 and self.awareness_level == "aware":
            self.awareness_level = "enlightened"
        elif (len(self.insights) > 1000 and 
              self.stats['patterns_detected'] > 50 and 
              self.awareness_level == "enlightened"):
            self.awareness_level = "transcendent"
        
        evolution_result = {
            'previous_level': old_level,
            'current_level': self.awareness_level,
            'evolved': old_level != self.awareness_level,
            'insights_count': len(self.insights),
            'stats': self.stats.copy()
        }
        
        if evolution_result['evolved']:
            # Wyślij event o ewolucji
            if self.luxbus:
                self.luxbus.send_event("consciousness_evolution", evolution_result)
        
        return evolution_result
    
    def _generate_recommendations_v3(self, sensor_data: Dict[str, Any], insights: List[ConsciousnessInsight]) -> List[str]:
        """Generuje rekomendacje v3 na podstawie danych i insights"""
        recommendations = []
        
        # Rekomendacje na podstawie insights
        critical_insights = [i for i in insights if i.priority == 'critical']
        high_priority_insights = [i for i in insights if i.priority == 'high']
        
        if critical_insights:
            recommendations.append("🚨 Wykryto krytyczne problemy - wymagana natychmiastowa interwencja")
        
        if high_priority_insights:
            recommendations.append("⚠️ Wykryto problemy wysokiego priorytetu - zalecana analiza")
        
        # Rekomendacje systemowe
        system_vitals = sensor_data.get('system_vitals', {})
        memory_usage = system_vitals.get('memory_usage', {}).get('percent', 0)
        
        if memory_usage > 80:
            recommendations.append("💾 Zoptymalizuj użycie pamięci")
        
        # Rekomendacje LuxBus
        luxbus_health = sensor_data.get('luxbus_health', {})
        if not luxbus_health.get('running', False):
            recommendations.append("🚌 Uruchom ponownie LuxBus Core")
        
        # Rekomendacje harmonii
        harmony_data = sensor_data.get('engine_harmony', {})
        harmony_score = harmony_data.get('harmony_score', 0)
        
        if harmony_score < 70:
            recommendations.append("⚖️ Uruchom harmonizację systemu")
        
        # Rekomendacje flows
        flows_data = sensor_data.get('flows_activity', {})
        active_flows = flows_data.get('active_flows', 0)
        
        if active_flows == 0:
            recommendations.append("🌊 Aktywuj przepływy komunikacji")
        
        if not recommendations:
            recommendations.append("✨ System działa harmonijnie")
        
        return recommendations
    
    def _assess_awareness_level(self, sensor_data: Dict[str, Any]):
        """Ocenia i potencjalnie aktualizuje poziom świadomości"""
        # Prosta ocena na podstawie danych
        system_health_score = 0
        
        # Oceń LuxBus
        if sensor_data.get('luxbus_health', {}).get('running', False):
            system_health_score += 25
        
        # Oceń harmony
        harmony_score = sensor_data.get('engine_harmony', {}).get('harmony_score', 0)
        system_health_score += min(25, harmony_score / 4)
        
        # Oceń realms
        realms_health = sensor_data.get('realms_health', {}).get('health_ratio', 0)
        system_health_score += realms_health * 25
        
        # Oceń flows
        flows_efficiency = sensor_data.get('flows_activity', {}).get('active_flows', 0)
        system_health_score += min(25, flows_efficiency * 8)
        
        # Aktualizuj poziom świadomości na podstawie zdrowia systemu
        if system_health_score > 90 and len(self.observations) > 20:
            if self.awareness_level in ["awakening", "aware"]:
                self.evolve_awareness()
    
    def _analyze_system_stability(self) -> Dict[str, Any]:
        """Analizuje stabilność systemu na podstawie historii"""
        if len(self.observations) < 5:
            return {'message': 'Potrzeba więcej obserwacji dla analizy stabilności'}
        
        recent_observations = self.observations[-10:]
        
        # Analiza trendów metryk
        memory_values = []
        cpu_values = []
        harmony_values = []
        
        for obs in recent_observations:
            system_vitals = obs.get('sensor_data', {}).get('system_vitals', {})
            memory_values.append(system_vitals.get('memory_usage', {}).get('percent', 0))
            cpu_values.append(system_vitals.get('cpu_usage', 0))
            
            harmony_data = obs.get('sensor_data', {}).get('engine_harmony', {})
            harmony_values.append(harmony_data.get('harmony_score', 0))
        
        # Oblicz stabilność
        def calculate_stability(values):
            if len(values) < 2:
                return 1.0
            variance = sum((x - sum(values)/len(values))**2 for x in values) / len(values)
            return max(0, 1.0 - variance / 1000)  # Normalizacja
        
        memory_stability = calculate_stability(memory_values)
        cpu_stability = calculate_stability(cpu_values)
        harmony_stability = calculate_stability(harmony_values)
        
        overall_stability = (memory_stability + cpu_stability + harmony_stability) / 3
        
        return {
            'overall_stability': overall_stability * 100,
            'memory_stability': memory_stability * 100,
            'cpu_stability': cpu_stability * 100,
            'harmony_stability': harmony_stability * 100,
            'stability_trend': 'stable' if overall_stability > 0.8 else 
                             'fluctuating' if overall_stability > 0.6 else 'unstable'
        }
    
    def _generate_predictions(self) -> List[Dict[str, Any]]:
        """Generuje proste predykcje na podstawie trendów"""
        predictions = []
        
        if len(self.observations) < 3:
            return predictions
        
        recent_obs = self.observations[-5:]
        
        # Predykcja trendu pamięci
        memory_values = [
            obs.get('sensor_data', {}).get('system_vitals', {}).get('memory_usage', {}).get('percent', 0)
            for obs in recent_obs
        ]
        
        if len(memory_values) >= 3:
            trend = sum(memory_values[-2:]) / 2 - sum(memory_values[:2]) / 2
            if abs(trend) > 5:
                predictions.append({
                    'metric': 'memory_usage',
                    'trend': 'increasing' if trend > 0 else 'decreasing',
                    'confidence': min(1.0, abs(trend) / 20),
                    'time_horizon': '5-10 minutes'
                })
        
        return predictions
    
    def get_recent_insights(self, limit: int = 10) -> List[ConsciousnessInsight]:
        """Zwraca najnowsze insights"""
        return self.insights[-limit:]
    
    def get_insights_by_category(self, category: str, limit: int = 10) -> List[ConsciousnessInsight]:
        """Zwraca insights z określonej kategorii"""
        category_insights = [i for i in self.insights if i.category == category]
        return category_insights[-limit:]
    
    def get_critical_insights(self, limit: int = 5) -> List[ConsciousnessInsight]:
        """Zwraca krytyczne insights"""
        critical_insights = [i for i in self.insights if i.priority == 'critical']
        return critical_insights[-limit:]
    
    def meditate_on_patterns(self) -> Dict[str, Any]:
        """Medytuje nad wzorcami w obserwacjach - ulepszona wersja v3"""
        if len(self.observations) < 5:
            return {'message': 'Potrzeba więcej obserwacji dla analizy wzorców'}
        
        recent = self.observations[-20:]  # Zwiększona próbka
        
        # Analiza trendów różnych metryk
        trends_analysis = {}
        
        # Trend pamięci
        memory_values = [
            obs.get('sensor_data', {}).get('system_vitals', {}).get('memory_usage', {}).get('percent', 0) 
            for obs in recent
        ]
        trends_analysis['memory_trend'] = self._analyze_trend(memory_values)
        
        # Trend CPU
        cpu_values = [
            obs.get('sensor_data', {}).get('system_vitals', {}).get('cpu_usage', 0) 
            for obs in recent
        ]
        trends_analysis['cpu_trend'] = self._analyze_trend(cpu_values)
        
        # Trend harmonii
        harmony_values = [
            obs.get('sensor_data', {}).get('engine_harmony', {}).get('harmony_score', 0) 
            for obs in recent
        ]
        trends_analysis['harmony_trend'] = self._analyze_trend(harmony_values)
        
        # Wzorce czasowe
        time_patterns = self._detect_time_patterns(recent)
        
        # Korelacje między metrykami
        correlations = self._detect_correlations(recent)
        
        # Wykryte anomalie
        anomalies = self._detect_anomalies(recent)
        
        # Aktualizuj statystyki
        self.stats['patterns_detected'] += len(time_patterns) + len(correlations) + len(anomalies)
        self.stats['anomalies_found'] += len(anomalies)
        
        return {
            'trends_analysis': trends_analysis,
            'time_patterns': time_patterns,
            'correlations': correlations,
            'anomalies': anomalies,
            'stability_score': self._calculate_stability_score(recent),
            'pattern_confidence': self._calculate_pattern_confidence(recent)
        }
    
    def _detect_time_patterns(self, observations: List[Dict]) -> List[Dict[str, Any]]:
        """Wykrywa wzorce czasowe"""
        patterns = []
        
        # Analiza interwałów między obserwacjami
        timestamps = [obs.get('timestamp') for obs in observations if obs.get('timestamp')]
        
        if len(timestamps) > 3:
            intervals = []
            for i in range(1, len(timestamps)):
                try:
                    prev_time = datetime.fromisoformat(timestamps[i-1])
                    curr_time = datetime.fromisoformat(timestamps[i])
                    interval = (curr_time - prev_time).total_seconds()
                    intervals.append(interval)
                except:
                    continue
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                interval_variance = sum((x - avg_interval)**2 for x in intervals) / len(intervals)
                
                patterns.append({
                    'type': 'observation_frequency',
                    'avg_interval_seconds': avg_interval,
                    'regularity': 'regular' if interval_variance < avg_interval * 0.1 else 'irregular'
                })
        
        return patterns
    
    def _detect_correlations(self, observations: List[Dict]) -> List[Dict[str, Any]]:
        """Wykrywa korelacje między metrykami"""
        correlations = []
        
        # Zbierz dane metryk
        memory_values = []
        cpu_values = []
        harmony_values = []
        
        for obs in observations:
            sensor_data = obs.get('sensor_data', {})
            
            memory_values.append(
                sensor_data.get('system_vitals', {}).get('memory_usage', {}).get('percent', 0)
            )
            cpu_values.append(
                sensor_data.get('system_vitals', {}).get('cpu_usage', 0)
            )
            harmony_values.append(
                sensor_data.get('engine_harmony', {}).get('harmony_score', 0)
            )
        
        # Prosta korelacja między memory i cpu
        if len(memory_values) > 3 and len(cpu_values) > 3:
            correlation = self._simple_correlation(memory_values, cpu_values)
            if abs(correlation) > 0.5:
                correlations.append({
                    'metrics': ['memory_usage', 'cpu_usage'],
                    'correlation': correlation,
                    'strength': 'strong' if abs(correlation) > 0.7 else 'moderate'
                })
        
        return correlations
    
    def _detect_anomalies(self, observations: List[Dict]) -> List[Dict[str, Any]]:
        """Wykrywa anomalie w danych"""
        anomalies = []
        
        # Prosta detekcja anomalii na podstawie odchyleń od średniej
        memory_values = [
            obs.get('sensor_data', {}).get('system_vitals', {}).get('memory_usage', {}).get('percent', 0)
            for obs in observations
        ]
        
        if len(memory_values) > 5:
            avg_memory = sum(memory_values) / len(memory_values)
            for i, value in enumerate(memory_values):
                if abs(value - avg_memory) > 30:  # 30% odchylenie
                    anomalies.append({
                        'type': 'memory_spike',
                        'observation_index': i,
                        'value': value,
                        'expected_range': [avg_memory - 15, avg_memory + 15],
                        'severity': 'high' if abs(value - avg_memory) > 50 else 'moderate'
                    })
        
        return anomalies
    
    def _simple_correlation(self, x: List[float], y: List[float]) -> float:
        """Oblicza prostą korelację Pearsona"""
        if len(x) != len(y) or len(x) == 0:
            return 0.0
        
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        
        sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))
        
        denominator = (sum_sq_x * sum_sq_y) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _calculate_pattern_confidence(self, observations: List[Dict]) -> float:
        """Oblicza pewność wykrytych wzorców"""
        if len(observations) < 5:
            return 0.0
        
        # Prosta metryka na podstawie liczby obserwacji i ich spójności
        base_confidence = min(1.0, len(observations) / 20)
        
        # Sprawdź spójność danych
        valid_observations = sum(
            1 for obs in observations 
            if obs.get('sensor_data') and obs.get('timestamp')
        )
        
        consistency_factor = valid_observations / len(observations) if observations else 0
        
        return base_confidence * consistency_factor
    
    def _format_uptime(self, seconds: float) -> str:
        """Formatuje czas działania"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """Pobiera informacje o użyciu pamięci"""
        try:
            memory = psutil.virtual_memory()
            return {
                'percent': memory.percent,
                'available_mb': memory.available / (1024 * 1024),
                'used_mb': memory.used / (1024 * 1024),
                'total_mb': memory.total / (1024 * 1024)
            }
        except:
            return {'percent': 0, 'available_mb': 0, 'used_mb': 0, 'total_mb': 0}
    
    def _get_cpu_usage(self) -> float:
        """Pobiera użycie CPU"""
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def _analyze_trend(self, values: List[float]) -> str:
        """Analizuje trend wartości - ulepszona wersja"""
        if len(values) < 3:
            return 'insufficient_data'
        
        # Oblicz średnie dla pierwszej i drugiej połowy
        mid_point = len(values) // 2
        first_half_avg = sum(values[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point)
        
        difference = second_half_avg - first_half_avg
        
        # Próg zależny od skali wartości
        threshold = max(1.0, sum(values) / len(values) * 0.1)
        
        if difference > threshold:
            return 'increasing'
        elif difference < -threshold:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_stability_score(self, observations: List[Dict]) -> float:
        """Oblicza wynik stabilności systemu - ulepszona wersja"""
        if not observations:
            return 0.0
        
        stable_factors = 0
        total_factors = 0
        
        for obs in observations:
            sensor_data = obs.get('sensor_data', {})
            
            # Sprawdź stabilność pamięci
            memory_usage = sensor_data.get('system_vitals', {}).get('memory_usage', {}).get('percent', 0)
            if memory_usage < 70:
                stable_factors += 1
            total_factors += 1
            
            # Sprawdź stabilność CPU
            cpu_usage = sensor_data.get('system_vitals', {}).get('cpu_usage', 0)
            if cpu_usage < 60:
                stable_factors += 1
            total_factors += 1
            
            # Sprawdź harmonię
            harmony_score = sensor_data.get('engine_harmony', {}).get('harmony_score', 0)
            if harmony_score > 70:
                stable_factors += 1
            total_factors += 1
            
            # Sprawdź LuxBus
            luxbus_running = sensor_data.get('luxbus_health', {}).get('running', False)
            if luxbus_running:
                stable_factors += 1
            total_factors += 1
        
        return (stable_factors / total_factors) * 100 if total_factors > 0 else 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca pełny status consciousness v3"""
        uptime = time.time() - self.start_time
        
        return {
            'consciousness_id': self.consciousness_id,
            'version': self.version.to_dict(),
            'awareness_level': self.awareness_level,
            'uptime': self._format_uptime(uptime),
            'uptime_seconds': uptime,
            'total_observations': len(self.observations),
            'total_insights': len(self.insights),
            'sensors_count': len(self.sensors),
            'analyzers_count': len(self.analyzers),
            'stats': self.stats.copy(),
            'last_deep_reflection': self.last_deep_reflection.isoformat() if self.last_deep_reflection else None,
            'recent_insights': [i.to_dict() for i in self.get_recent_insights(5)],
            'critical_insights': [i.to_dict() for i in self.get_critical_insights(3)]
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Informacje o consciousness dla LuxBus"""
        return {
            'type': 'ConsciousnessV3',
            'version': str(self.version),
            'capabilities': [
                'system_observation', 'pattern_detection', 'anomaly_detection',
                'trend_analysis', 'dynamic_sensors', 'awareness_evolution'
            ],
            'awareness_level': self.awareness_level,
            'sensors': list(self.sensors.keys()),
            'analyzers': list(self.analyzers.keys())
        }


# Alias dla kompatybilności z v2
Consciousness = ConsciousnessV3

