
"""
🔮 AstralEngine - Główny Koordynator Energii Astralnej

Serce LuxDB v2 - koordynuje wszystkie komponenty systemu,
zarządza przepływem energii i utrzymuje harmonię.
"""

import asyncio
import threading
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from .consciousness import Consciousness
from .harmony import Harmony
from ..realms.base_realm import BaseRealm
from ..realms.sqlite_realm import SQLiteRealm
from ..realms.postgres_realm import PostgresRealm
from ..realms.memory_realm import MemoryRealm
from ..flows.rest_flow import RestFlow
from ..flows.ws_flow import WebSocketFlow
from ..flows.callback_flow import CallbackFlow
from ..wisdom.astral_logging import AstralLogger

@dataclass
class AstralConfig:
    """Konfiguracja astralna systemu"""
    consciousness_level: str = 'enlightened'
    energy_conservation: bool = True
    auto_healing: bool = True
    meditation_interval: int = 60
    harmony_check_interval: int = 30
    
    realms: Dict[str, str] = field(default_factory=lambda: {
        'primary': 'sqlite://db/primary_realm.db'
    })
    
    flows: Dict[str, Dict] = field(default_factory=lambda: {
        'rest': {'port': 5000, 'host': '0.0.0.0'},
        'websocket': {'port': 5001, 'host': '0.0.0.0'},
        'callback': {'async_workers': 4}
    })
    
    wisdom: Dict[str, Any] = field(default_factory=lambda: {
        'logging_level': 'INFO',
        'query_timeout': 30,
        'migration_backup': True
    })

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
        
        # Przepływy (flows)
        self.rest_flow: Optional[RestFlow] = None
        self.ws_flow: Optional[WebSocketFlow] = None
        self.callback_flow: Optional[CallbackFlow] = None
        
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
            return PostgresRealm(name, config, self)
        elif config.startswith('memory://'):
            return MemoryRealm(name, config, self)
        else:
            raise ValueError(f"Nieznany typ wymiaru: {config}")
    
    def _initialize_flows(self) -> None:
        """Inicjalizuje wszystkie przepływy komunikacji"""
        flow_config = self.config.flows
        
        # REST Flow
        if 'rest' in flow_config:
            self.rest_flow = RestFlow(self, flow_config['rest'])
            self.state.active_flows += 1
            self.logger.info("🌐 Przepływ REST aktywowany")
        
        # WebSocket Flow
        if 'websocket' in flow_config:
            self.ws_flow = WebSocketFlow(self, flow_config['websocket'])
            self.state.active_flows += 1
            self.logger.info("⚡ Przepływ WebSocket aktywowany")
        
        # Callback Flow
        if 'callback' in flow_config:
            self.callback_flow = CallbackFlow(self, flow_config['callback'])
            self.state.active_flows += 1
            self.logger.info("🔄 Przepływ Callback aktywowany")
    
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
    
    def transcend(self) -> None:
        """
        Gracefully zamyka system astralny
        Transcenduje do wyższego wymiaru (shutdown)
        """
        self.logger.info("🕊️ Rozpoczynam transcendencję...")
        
        self._running = False
        self.state.is_transcended = True
        
        # Zatrzymaj przepływy
        if self.rest_flow:
            self.rest_flow.stop()
        if self.ws_flow:
            self.ws_flow.stop()
        if self.callback_flow:
            self.callback_flow.stop()
        
        # Zamknij wymiary
        for realm in self.realms.values():
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
        if self.rest_flow and self.rest_flow.is_running():
            count += 1
        if self.ws_flow and self.ws_flow.is_running():
            count += 1
        if self.callback_flow and self.callback_flow.is_running():
            count += 1
        return count
    
    def get_status(self) -> Dict[str, Any]:
        """
        Zwraca pełny status systemu astralnego
        
        Returns:
            Słownik ze statusem systemu
        """
        return {
            'astral_engine': {
                'version': '2.0.0',
                'consciousness_level': self.config.consciousness_level,
                'running': self._running,
                'uptime': str(datetime.now() - self.state.awakened_at) if self.state.awakened_at else '0:00:00'
            },
            'system_state': self.state.to_dict(),
            'realms': {
                name: realm.get_status() for name, realm in self.realms.items()
            },
            'flows': {
                'rest': self.rest_flow.get_status() if self.rest_flow else None,
                'websocket': self.ws_flow.get_status() if self.ws_flow else None,
                'callback': self.callback_flow.get_status() if self.callback_flow else None
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
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.transcend()
