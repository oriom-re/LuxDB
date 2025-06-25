"""
🔮 AstralEngine - Główny Koordynator Energii Astralnej

Serce LuxDB v2 - koordynuje wszystkie komponenty systemu,
zarządza przepływem energii i utrzymuje harmonię.
"""

import time
import threading
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..config import AstralConfig
from .consciousness import Consciousness
from .harmony import Harmony
from ..realms.base_realm import BaseRealm
from ..realms.sqlite_realm import SQLiteRealm
from ..realms.memory_realm import MemoryRealm

try:
    from ..beings.base_being import BaseBeing
    from ..beings.manifestation import Manifestation
except ImportError:
    BaseBeing = None
    Manifestation = None


class SystemState:
    """Stan systemu astralnego"""

    def __init__(self):
        self.awakened_at: Optional[datetime] = None
        self.energy_level: float = 100.0
        self.active_realms: int = 0
        self.active_flows: int = 0
        self.total_manifestations: int = 0
        self.last_meditation: Optional[datetime] = None
        self.harmony_score: float = 100.0
        self.is_transcended: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'awakened_at': self.awakened_at.isoformat() if self.awakened_at else None,
            'energy_level': self.energy_level,
            'active_realms': self.active_realms,
            'active_flows': self.active_flows,
            'total_manifestations': self.total_manifestations,
            'last_meditation': self.last_meditation.isoformat() if self.last_meditation else None,
            'harmony_score': self.harmony_score,
            'is_transcended': self.is_transcended,
            'uptime': str(datetime.now() - self.awakened_at) if self.awakened_at else '0:00:00'
        }


class AstralLogger:
    """Prosty logger astralny"""

    def __init__(self, level: str = "INFO"):
        self.level = level

    def info(self, message: str):
        print(f"[INFO] {message}")

    def debug(self, message: str):
        if self.level == "DEBUG":
            print(f"[DEBUG] {message}")

    def warning(self, message: str):
        print(f"[WARNING] {message}")

    def error(self, message: str):
        print(f"[ERROR] {message}")


class AstralEngine:
    """
    Główny silnik astralny - koordynuje wszystkie aspekty systemu

    Odpowiedzialności:
    - Inicjalizacja i harmonizacja komponentów
    - Zarządzanie cyklem życia systemu
    - Koordynacja przepływów energii
    - Monitorowanie stanu astralnego
    """

    def __init__(self, config: Union[AstralConfig, Dict, str, None] = None):
        """
        Inicjalizuje silnik astralny

        Args:
            config: Konfiguracja - AstralConfig, dict, ścieżka do pliku lub None
        """
        self.config = self._load_config(config)
        self.state = SystemState()

        # Główne komponenty
        self.consciousness = Consciousness(self)
        self.harmony = Harmony(self)
        self.logger = AstralLogger(self.config.wisdom.get('logging_level', 'INFO'))

        # Wymiary (realms)
        self.realms: Dict[str, BaseRealm] = {}

        # Przepływy (flows) - zainicjowane jako None, będą ustawione gdy moduły będą dostępne
        self.rest_flow = None
        self.ws_flow = None
        self.callback_flow = None
        self.gpt_flow = None
        
        # System generatywny funkcji
        self.function_generator = None

        # Wątki medytacyjne
        self._meditation_thread: Optional[threading.Thread] = None
        self._harmony_thread: Optional[threading.Thread] = None
        self._running = False

        self.logger.info("🔮 AstralEngine zainicjalizowany")

    def _load_config(self, config: Union[AstralConfig, Dict, str, None]) -> AstralConfig:
        """Ładuje konfigurację astralną"""
        if config is None:
            return AstralConfig()
        elif isinstance(config, AstralConfig):
            return config
        elif isinstance(config, dict):
            return AstralConfig(**config)
        elif isinstance(config, str):
            # TODO: Ładowanie z pliku
            import json
            with open(config, 'r') as f:
                config_dict = json.load(f)
            return AstralConfig(**config_dict)
        else:
            raise ValueError("Nieprawidłowy typ konfiguracji")

    def awaken(self) -> None:
        """
        Przebudza wszystkie komponenty systemu
        Rozpoczyna cykl życia astralnego
        """
        self.logger.info("🌅 Przebudzenie systemu astralnego...")

        start_time = time.time()

        try:
            # 1. Ustaw stan początkowy
            self.state.awakened_at = datetime.now()
            self._running = True

            # 2. Inicjalizuj wymiary
            self._initialize_realms()

            # 3. Inicjalizuj przepływy
            self._initialize_flows()
            
            # 4. Inicjalizuj systemy AI
            self._initialize_ai_systems()

            # 4. Uruchom systemy monitorowania
            self._start_meditation_cycle()
            self._start_harmony_cycle()

            # 5. Pierwsza medytacja
            self.state.last_meditation = datetime.now()
            self.meditate()

            awaken_time = time.time() - start_time
            self.logger.info(f"✨ System przebudzony w {awaken_time:.2f}s")
            self.logger.info(f"🌟 Aktywne wymiary: {len(self.realms)}")
            self.logger.info(f"🌊 Aktywne przepływy: {self._count_active_flows()}")

        except Exception as e:
            self.logger.error(f"❌ Błąd podczas przebudzenia: {e}")
            raise

    def _initialize_realms(self) -> None:
        """Inicjalizuje wszystkie wymiary danych"""
        for realm_name, realm_config in self.config.realms.items():
            try:
                realm = self._create_realm(realm_name, realm_config)
                self.realms[realm_name] = realm
                self.state.active_realms += 1
                self.logger.info(f"🌍 Wymiar '{realm_name}' zmanifestowany")
            except Exception as e:
                self.logger.error(f"❌ Błąd manifestacji wymiaru '{realm_name}': {e}")
                raise

    def _create_realm(self, name: str, config: str) -> BaseRealm:
        """Tworzy wymiar na podstawie konfiguracji"""
        if config.startswith('sqlite://'):
            return SQLiteRealm(name, config, self)
        elif config.startswith('postgresql://'):
            # PostgresRealm będzie dodany później
            raise ValueError(f"PostgreSQL realm nie jest jeszcze zaimplementowany")
        elif config.startswith('memory://'):
            return MemoryRealm(name, config, self)
        elif config.startswith('intention://'):
            from ..realms.intention_realm import IntentionRealm
            return IntentionRealm(name, config, self)
        else:
            raise ValueError(f"Nieznany typ wymiaru: {config}")

    def _initialize_flows(self) -> None:
        """Inicjalizuje wszystkie przepływy komunikacji"""
        flow_config = self.config.flows

        # REST Flow - będzie dodany gdy moduł będzie gotowy
        if 'rest' in flow_config:
            try:
                from ..flows.rest_flow import RestFlow
                self.rest_flow = RestFlow(self, flow_config['rest'])
                self.state.active_flows += 1
                self.logger.info("🌐 Przepływ REST aktywowany")
            except ImportError:
                self.logger.warning("⚠️ Moduł RestFlow nie jest dostępny")

        # WebSocket Flow - będzie dodany gdy moduł będzie gotowy
        if 'websocket' in flow_config:
            try:
                from ..flows.ws_flow import WebSocketFlow
                self.ws_flow = WebSocketFlow(self, flow_config['websocket'])
                self.state.active_flows += 1
                self.logger.info("⚡ Przepływ WebSocket aktywowany")
            except ImportError:
                self.logger.warning("⚠️ Moduł WebSocketFlow nie jest dostępny")

        # Callback Flow - będzie dodany gdy moduł będzie gotowy
        if 'callback' in flow_config:
            try:
                from ..flows.callback_flow import CallbackFlow
                self.callback_flow = CallbackFlow(self, flow_config['callback'])
                self.state.active_flows += 1
                self.logger.info("🔄 Przepływ Callback aktywowany")
            except ImportError:
                self.logger.warning("⚠️ Moduł CallbackFlow nie jest dostępny")

        # Intention Flow - system intencji
        try:
            from ..flows.intention_flow import IntentionFlow
            self.intention_flow = IntentionFlow(self)
            self.intention_flow.initialize()
            self.state.active_flows += 1
            self.logger.info("🎯 Przepływ Intencji aktywowany")
        except ImportError:
            self.logger.warning("⚠️ Moduł IntentionFlow nie jest dostępny")
            self.intention_flow = None
    
    def _initialize_ai_systems(self) -> None:
        """Inicjalizuje systemy AI (GPT i Function Generator)"""
        
        # Function Generator
        try:
            from ..wisdom.function_generator import FunctionGenerator
            self.function_generator = FunctionGenerator(self)
            self.logger.info("🛠️ Function Generator aktywowany")
        except ImportError:
            self.logger.warning("⚠️ Moduł FunctionGenerator nie jest dostępny")
            self.function_generator = None
        
        # GPT Flow
        if 'gpt' in self.config.flows:
            try:
                from ..flows.gpt_flow import GPTFlow
                self.gpt_flow = GPTFlow(self, self.config.flows['gpt'])
                if self.gpt_flow.start():
                    self.state.active_flows += 1
                    self.logger.info("🤖 Przepływ GPT aktywowany")
            except ImportError:
                self.logger.warning("⚠️ Moduł GPTFlow nie jest dostępny")

    def _start_meditation_cycle(self) -> None:
        """Uruchamia cykl medytacyjny systemu"""
        def meditation_cycle():
            while self._running:
                try:
                    time.sleep(self.config.meditation_interval)
                    if self._running:
                        self.meditate()
                except Exception as e:
                    self.logger.error(f"❌ Błąd w cyklu medytacyjnym: {e}")

        self._meditation_thread = threading.Thread(target=meditation_cycle, daemon=True)
        self._meditation_thread.start()
        self.logger.info("🧘 Cykl medytacyjny uruchomiony")

    def _start_harmony_cycle(self) -> None:
        """Uruchamia cykl harmonizacji systemu"""
        def harmony_cycle():
            while self._running:
                try:
                    time.sleep(self.config.harmony_check_interval)
                    if self._running:
                        self.harmony.balance()
                except Exception as e:
                    self.logger.error(f"❌ Błąd w cyklu harmonii: {e}")

        self._harmony_thread = threading.Thread(target=harmony_cycle, daemon=True)
        self._harmony_thread.start()
        self.logger.info("⚖️ Cykl harmonii uruchomiony")

    def meditate(self) -> Dict[str, Any]:
        """
        Medytacja systemu - analiza stanu i optymalizacja

        Returns:
            Słownik z wynikami medytacji
        """
        meditation_start = time.time()

        try:
            # Obserwuj stan przez świadomość
            insights = self.consciousness.reflect()

            # Aktualizuj stan systemu
            self.state.last_meditation = datetime.now()
            self.state.harmony_score = self.harmony.calculate_harmony_score()
            self.state.total_manifestations = sum(
                realm.count_beings() for realm in self.realms.values()
            )

            # Optymalizuj jeśli potrzeba
            if self.state.harmony_score < 80:
                self.harmony.balance()

            meditation_time = time.time() - meditation_start

            meditation_result = {
                'timestamp': datetime.now().isoformat(),
                'duration': meditation_time,
                'system_state': self.state.to_dict(),
                'insights': insights,
                'harmony_score': self.state.harmony_score
            }

            self.logger.debug(f"🧘 Medytacja zakończona w {meditation_time:.3f}s")
            return meditation_result

        except Exception as e:
            self.logger.error(f"❌ Błąd podczas medytacji: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def harmonize(self) -> None:
        """Harmonizuje przepływ energii między komponentami"""
        self.harmony.harmonize()

    def create_realm(self, name: str, config: str) -> BaseRealm:
        """
        Tworzy nowy wymiar danych

        Args:
            name: Nazwa wymiaru
            config: Konfiguracja połączenia

        Returns:
            Nowy wymiar
        """
        if name in self.realms:
            raise ValueError(f"Wymiar '{name}' już istnieje")

        realm = self._create_realm(name, config)
        self.realms[name] = realm
        self.state.active_realms += 1

        self.logger.info(f"🌍 Nowy wymiar '{name}' zmanifestowany")
        return realm

    def get_realm(self, name: str) -> BaseRealm:
        """
        Pobiera wymiar po nazwie

        Args:
            name: Nazwa wymiaru

        Returns:
            Wymiar danych
        """
        if name not in self.realms:
            raise ValueError(f"Wymiar '{name}' nie istnieje")
        return self.realms[name]

    def list_realms(self) -> List[str]:
        """Zwraca listę wszystkich wymiarów"""
        return list(self.realms.keys())

    def start_flows(self, debug: bool = False) -> None:
        """
        Uruchamia wszystkie przepływy komunikacji

        Args:
            debug: Tryb debug
        """
        if self.rest_flow:
            self.rest_flow.start(debug=debug)

        if self.ws_flow:
            self.ws_flow.start(debug=debug)

        if self.callback_flow:
            self.callback_flow.start()

        self.logger.info("🌊 Wszystkie przepływy uruchomione")

    def manifest_intention(self, intention_data: Dict[str, Any], realm_name: str = "intentions") -> Any:
        """
        Manifestuje nową intencję w systemie
        
        Args:
            intention_data: Dane intencji z warstwami duchową i materialną
            realm_name: Nazwa wymiaru dla intencji
            
        Returns:
            Zmanifestowana intencja
        """
        try:
            # Pobierz lub utwórz wymiar intencji
            if realm_name not in self.realms:
                self.create_realm(realm_name, "intention://memory")
            
            realm = self.get_realm(realm_name)
            intention = realm.manifest(intention_data)
            
            self.logger.info(f"🎯 Intencja '{intention.essence.name}' zmanifestowana w wymiarze '{realm_name}'")
            return intention
            
        except Exception as e:
            self.logger.error(f"❌ Błąd manifestacji intencji: {e}")
            raise
    
    def interact_with_intention(self, intention_id: str, interaction_type: str, data: Dict[str, Any], user_id: str = "system", realm_name: str = "intentions") -> Dict[str, Any]:
        """
        Interakcja z intencją
        
        Args:
            intention_id: ID intencji
            interaction_type: Typ interakcji (wzmocnij, korektuj, realizuj, przypisz_opiekuna)
            data: Dane interakcji
            user_id: ID użytkownika
            realm_name: Nazwa wymiaru
            
        Returns:
            Wynik interakcji
        """
        try:
            if self.intention_flow:
                return self.intention_flow.process_interaction(intention_id, interaction_type, data, user_id)
            else:
                # Fallback - bezpośrednia interakcja przez realm
                realm = self.get_realm(realm_name)
                if hasattr(realm, 'interact_with_intention'):
                    return realm.interact_with_intention(intention_id, interaction_type, data, user_id)
                else:
                    return {'success': False, 'message': 'Realm nie obsługuje interakcji z intencjami'}
                    
        except Exception as e:
            self.logger.error(f"❌ Błąd interakcji z intencją: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_intention_status(self, intention_id: str, realm_name: str = "intentions") -> Dict[str, Any]:
        """
        Pobiera status intencji
        
        Args:
            intention_id: ID intencji
            realm_name: Nazwa wymiaru
            
        Returns:
            Status intencji
        """
        try:
            realm = self.get_realm(realm_name)
            if hasattr(realm, 'get_intention_by_id'):
                intention = realm.get_intention_by_id(intention_id)
                if intention:
                    return intention.get_status()
                else:
                    return {'error': 'Intencja nie znaleziona'}
            else:
                return {'error': 'Realm nie obsługuje intencji'}
                
        except Exception as e:
            self.logger.error(f"❌ Błąd pobierania statusu intencji: {e}")
            return {'error': str(e)}
    
    def contemplate_intentions(self, conditions: Dict[str, Any], realm_name: str = "intentions") -> List[Dict[str, Any]]:
        """
        Kontempluje intencje według warunków
        
        Args:
            conditions: Warunki wyszukiwania
            realm_name: Nazwa wymiaru
            
        Returns:
            Lista intencji
        """
        try:
            realm = self.get_realm(realm_name)
            intentions = realm.contemplate("find_intentions", **conditions)
            return [intention.get_status() for intention in intentions]
            
        except Exception as e:
            self.logger.error(f"❌ Błąd kontemplacji intencji: {e}")
            return []

    def transcend(self) -> None:
        """
        Gracefully zamyka system astralny
        Transcenduje do wyższego wymiaru (shutdown)
        """
        self.logger.info("🕊️ Rozpoczynam transcendencję...")

        self._running = False
        self.state.is_transcended = True

        # Zatrzymaj przepływy
        if self.rest_flow and hasattr(self.rest_flow, 'stop'):
            self.rest_flow.stop()
        if self.ws_flow and hasattr(self.ws_flow, 'stop'):
            self.ws_flow.stop()
        if self.callback_flow and hasattr(self.callback_flow, 'stop'):
            self.callback_flow.stop()
        if self.intention_flow and hasattr(self.intention_flow, 'stop'):
            self.intention_flow.stop()
        if self.gpt_flow and hasattr(self.gpt_flow, 'stop'):
            self.gpt_flow.stop()

        # Zamknij wymiary
        for realm in self.realms.values():
            if hasattr(realm, 'close'):
                realm.close()

        # Poczekaj na zakończenie wątków
        if self._meditation_thread and self._meditation_thread.is_alive():
            self._meditation_thread.join(timeout=5)
        if self._harmony_thread and self._harmony_thread.is_alive():
            self._harmony_thread.join(timeout=5)

        self.logger.info("✨ Transcendencja zakończona - system w wyższym wymiarze")

    def _count_active_flows(self) -> int:
        """Liczy aktywne przepływy"""
        count = 0
        if self.rest_flow and hasattr(self.rest_flow, 'is_running') and self.rest_flow.is_running():
            count += 1
        if self.ws_flow and hasattr(self.ws_flow, 'is_running') and self.ws_flow.is_running():
            count += 1
        if self.callback_flow and hasattr(self.callback_flow, 'is_running') and self.callback_flow.is_running():
            count += 1
        return count

    def get_status(self) -> Dict[str, Any]:
        """
        Zwraca pełny status systemu astralnego

        Returns:
            Słownik ze statusem systemu
        """
        # Genetyczna analiza systemu
        genetic_analysis = self._get_genetic_analysis()
        
        return {
            'astral_engine': {
                'version': '2.0.0',
                'consciousness_level': self.config.consciousness_level,
                'running': self._running,
                'uptime': str(datetime.now() - self.state.awakened_at) if self.state.awakened_at else '0:00:00',
                'genetic_analysis': genetic_analysis
            },
            'system_state': self.state.to_dict(),
            'realms': {
                name: realm.get_status() if hasattr(realm, 'get_status') else {'name': name, 'active': True}
                for name, realm in self.realms.items()
            },
            'flows': {
                'rest': self.rest_flow.get_status() if self.rest_flow and hasattr(self.rest_flow, 'get_status') else None,
                'websocket': self.ws_flow.get_status() if self.ws_flow and hasattr(self.ws_flow, 'get_status') else None,
                'callback': self.callback_flow.get_status() if self.callback_flow and hasattr(self.callback_flow, 'get_status') else None,
                'intention': self.intention_flow.get_status() if self.intention_flow and hasattr(self.intention_flow, 'get_status') else None,
                'gpt': self.gpt_flow.get_status() if self.gpt_flow and hasattr(self.gpt_flow, 'get_status') else None
            },
            'ai_systems': {
                'function_generator': self.function_generator.get_status() if self.function_generator and hasattr(self.function_generator, 'get_status') else None
            },
            'harmony': {
                'score': self.state.harmony_score,
                'last_check': self.state.last_meditation.isoformat() if self.state.last_meditation else None
            }
        }

    def __enter__(self):
        """Context manager entry"""
        self.awaken()
        return self

    def _get_genetic_analysis(self) -> Dict[str, Any]:
        """Pobiera analizę genetyczną systemu"""
        try:
            from ..beings.genetic_identification import get_genetic_system, analyze_function_genetics
            genetic_system = get_genetic_system()
            
            if not genetic_system:
                return {'status': 'not_available'}
            
            # Analizuj kluczowe funkcje
            key_functions = ['meditate', 'evolve', 'transcend', 'manifest', 'contemplate']
            function_analytics = {}
            
            for func_name in key_functions:
                stats = analyze_function_genetics(func_name)
                if stats.get('total_calls', 0) > 0:
                    function_analytics[func_name] = stats
            
            return {
                'status': 'active',
                'total_tracked_functions': len(genetic_system.genome_registry),
                'function_analytics': function_analytics,
                'argument_lineages': len(genetic_system.argument_lineage)
            }
            
        except ImportError:
            return {'status': 'module_not_available'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def get_genetic_insights(self) -> Dict[str, Any]:
        """Zwraca głębokie insights genetyczne systemu"""
        try:
            from ..beings.genetic_identification import get_genetic_system, find_genetic_patterns
            genetic_system = get_genetic_system()
            
            if not genetic_system:
                return {'insights': [], 'message': 'System genetyczny niedostępny'}
            
            insights = []
            key_functions = ['meditate', 'evolve', 'transcend']
            
            for func_name in key_functions:
                patterns = find_genetic_patterns(func_name, 0.6)
                if patterns['patterns_found'] > 0:
                    insights.append({
                        'function': func_name,
                        'pattern_count': patterns['patterns_found'],
                        'total_calls': patterns['total_calls_analyzed'],
                        'genetic_diversity': patterns['patterns_found'] / patterns['total_calls_analyzed'] if patterns['total_calls_analyzed'] > 0 else 0
                    })
            
            return {
                'insights': insights,
                'genetic_health_score': sum(i['genetic_diversity'] for i in insights) / len(insights) if insights else 0,
                'recommendations': self._generate_genetic_recommendations(insights)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_genetic_recommendations(self, insights: List[Dict]) -> List[str]:
        """Generuje rekomendacje na podstawie analizy genetycznej"""
        recommendations = []
        
        for insight in insights:
            if insight['genetic_diversity'] < 0.3:
                recommendations.append(f"Funkcja {insight['function']} wykazuje niską różnorodność genetyczną - rozważ zróżnicowanie wywołań")
            elif insight['genetic_diversity'] > 0.8:
                recommendations.append(f"Funkcja {insight['function']} ma wysoką różnorodność - dobry wskaźnik adaptacji")
            
            if insight['total_calls'] < 10:
                recommendations.append(f"Funkcja {insight['function']} ma mało wywołań - więcej danych poprawiłoby analizę")
        
        return recommendations

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.transcend()