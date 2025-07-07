"""
🔮 AstralEngine v3 - Oparty na LuxBus Core

Nowa generacja silnika astralnego z pełną integracją LuxBus
i możliwościami self-modification.
"""

import asyncio
import threading
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from .luxbus_core import LuxBusCore, LuxPacket, PacketType, get_luxbus_core
from .consciousness import Consciousness
from .harmony import HarmonyV3
from ..config import AstralConfig
from ..wisdom.astral_logging import AstralLogger


class AstralEngineV3:
    """
    Silnik Astralny v3 - Oparty na LuxBus Core

    Cechy:
    - Pełna integracja z LuxBus
    - Dynamiczne ładowanie modułów
    - Self-modification capabilities
    - Async/await native support
    """

    def __init__(self, config: AstralConfig = None, luxbus_core: LuxBusCore = None):
        self.config = config or AstralConfig()
        self.luxbus = luxbus_core or get_luxbus_core()

        # Identyfikacja w LuxBus
        self.engine_id = f"astral_engine_{self.luxbus.node_id}"

        # Podstawowe komponenty
        self.consciousness = None
        self.harmony = None
        self.logger = AstralLogger(self.config.wisdom.get('logging_level', 'INFO'))

        # Realms jako moduły LuxBus
        self.realms: Dict[str, Any] = {}

        # Flows jako moduły LuxBus
        self.flows: Dict[str, Any] = {}

        # Stan systemu
        self.running = False
        self.awakened_at: Optional[datetime] = None

        # Task managery
        self.tasks: List[asyncio.Task] = []

        # Event loop
        self.loop: Optional[asyncio.AbstractEventLoop] = None

        # Rejestruj silnik w LuxBus
        self.luxbus.register_module("astral_engine", self)

        print(f"🔮 AstralEngine v3 zainicjalizowany: {self.engine_id}")

    def setup_luxbus_handlers(self, luxbus: LuxBusCore):
        """Konfiguruje handlery LuxBus dla silnika"""

        def handle_engine_command(packet: LuxPacket):
            """Obsługuje komendy dla silnika"""
            command_data = packet.data
            command = command_data.get('command')
            params = command_data.get('params', {})

            response_data = None

            if command == 'awaken':
                if not self.running:
                    asyncio.create_task(self.awaken())
                    response_data = {'status': 'awakening'}
                else:
                    response_data = {'status': 'already_awake'}

            elif command == 'transcend':
                if self.running:
                    asyncio.create_task(self.transcend())
                    response_data = {'status': 'transcending'}
                else:
                    response_data = {'status': 'already_transcended'}

            elif command == 'meditate':
                meditation = self.meditate()
                response_data = meditation

            elif command == 'get_status':
                response_data = self.get_status()

            elif command == 'load_module':
                module_name = params.get('module_name')
                module_config = params.get('config', {})
                result = self.load_dynamic_module(module_name, module_config)
                response_data = result

            elif command == 'modify_self':
                modification_data = params.get('modification')
                result = self.apply_self_modification(modification_data)
                response_data = result

            else:
                response_data = {'error': f'Nieznana komenda: {command}'}

            # Wyślij odpowiedź
            response = LuxPacket(
                uid=f"engine_response_{packet.uid}",
                from_id=self.engine_id,
                to_id=packet.from_id,
                packet_type=PacketType.RESPONSE,
                data=response_data
            )

            luxbus.send_packet(response)

        # Subskrybuj komendy dla silnika
        luxbus.subscribe_to_packets(self.engine_id, handle_engine_command)

    async def awaken(self):
        """Przebudza silnik astralny"""
        if self.running:
            self.logger.warning("AstralEngine już działa")
            return

        self.logger.info("🌅 Przebudzenie AstralEngine v3...")

        start_time = time.time()
        self.awakened_at = datetime.now()
        self.running = True

        try:
            # Pobierz event loop
            self.loop = asyncio.get_running_loop()

            # Uruchom LuxBus
            self.luxbus.start()

            # Inicjalizuj podstawowe komponenty
            await self._initialize_consciousness()
            await self._initialize_harmony()

            # Załaduj skonfigurowane moduły
            await self._load_configured_modules()

            # Uruchom główne taski
            await self._start_core_tasks()

            awaken_time = time.time() - start_time
            self.logger.info(f"✨ AstralEngine v3 przebudzony w {awaken_time:.2f}s")

            # Wyślij event o przebudzeniu
            self.luxbus.send_event("engine_awakened", {
                'engine_id': self.engine_id,
                'awaken_time': awaken_time,
                'modules': list(self.luxbus.modules.keys())
            })

        except Exception as e:
            self.logger.error(f"❌ Błąd podczas przebudzenia: {e}")
            self.running = False
            raise

    async def _initialize_consciousness(self):
        """Inicjalizuje consciousness jako moduł LuxBus"""
        self.consciousness = Consciousness(self)
        self.luxbus.register_module("consciousness", self.consciousness)
        self.logger.info("🧠 Consciousness zainicjalizowana")

    async def _initialize_harmony(self):
        """Inicjalizuje harmony jako moduł LuxBus"""
        self.harmony = HarmonyV3(self)
        self.luxbus.register_module("harmony", self.harmony)
        self.logger.info("⚖️ Harmony v3 zainicjalizowana")

    async def _load_configured_modules(self):
        """Ładuje moduły z konfiguracji"""
        # Załaduj realms
        for realm_name, realm_config in self.config.realms.items():
            await self.load_realm_module(realm_name, realm_config)

        # Załaduj flows
        for flow_name, flow_config in self.config.flows.items():
            await self.load_flow_module(flow_name, flow_config)

    async def load_realm_module(self, name: str, config: str):
        """Dynamicznie ładuje moduł realm"""
        try:
            if config.startswith('sqlite://'):
                from ..realms.sqlite_realm import SQLiteRealm
                realm = SQLiteRealm(name, config, self)
            elif config.startswith('memory://'):
                from ..realms.memory_realm import MemoryRealm
                realm = MemoryRealm(name, config, self)
            elif config.startswith('intention://'):
                from ..realms.intention_realm import IntentionRealm
                realm = IntentionRealm(name, config, self)
            else:
                raise ValueError(f"Nieznany typ realm: {config}")

            self.realms[name] = realm
            self.luxbus.register_module(f"realm_{name}", realm)

            self.logger.info(f"🌍 Realm '{name}' załadowany")
            return {'success': True, 'realm': name}

        except Exception as e:
            self.logger.error(f"❌ Błąd ładowania realm '{name}': {e}")
            return {'success': False, 'error': str(e)}

    async def load_flow_module(self, name: str, config: Dict[str, Any]):
        """Dynamicznie ładuje moduł flow"""
        try:
            flow = None

            if name == 'rest':
                from ..flows.rest_flow import RestFlow
                flow = RestFlow(self, config)
            elif name == 'websocket':
                from ..flows.ws_flow import WebSocketFlow
                flow = WebSocketFlow(self, config)
            elif name == 'callback':
                from ..flows.callback_flow import CallbackFlow
                flow = CallbackFlow(self, config)
            elif name == 'gpt':
                from ..flows.gpt_flow import GPTFlow
                flow = GPTFlow(self, config)
            else:
                raise ValueError(f"Nieznany typ flow: {name}")

            self.flows[name] = flow
            self.luxbus.register_module(f"flow_{name}", flow)

            # Uruchom flow
            if hasattr(flow, 'start'):
                success = flow.start()
                if success:
                    self.logger.info(f"🌊 Flow '{name}' uruchomiony pomyślnie")
                else:
                    self.logger.warning(f"⚠️ Flow '{name}' nie mógł się uruchomić")
            else:
                self.logger.info(f"🌊 Flow '{name}' załadowany (bez metody start)")

            self.logger.info(f"🌊 Flow '{name}' załadowany")
            return {'success': True, 'flow': name}

        except Exception as e:
            self.logger.error(f"❌ Błąd ładowania flow '{name}': {e}")
            return {'success': False, 'error': str(e)}

    def load_dynamic_module(self, module_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamicznie ładuje dowolny moduł"""
        try:
            # Tu można dodać logikę dynamicznego importu
            # Na razie podstawowa implementacja

            self.logger.info(f"📦 Próba załadowania modułu: {module_name}")

            # Sprawdź czy to realm
            if module_name.startswith('realm_'):
                realm_name = module_name[6:]  # usuń prefix 'realm_'
                return asyncio.create_task(self.load_realm_module(realm_name, config.get('connection_string', '')))

            # Sprawdź czy to flow
            elif module_name.startswith('flow_'):
                flow_name = module_name[5:]  # usuń prefix 'flow_'
                return asyncio.create_task(self.load_flow_module(flow_name, config))

            else:
                return {'success': False, 'error': f'Nieznany typ modułu: {module_name}'}

        except Exception as e:
            self.logger.error(f"❌ Błąd ładowania modułu '{module_name}': {e}")
            return {'success': False, 'error': str(e)}

    def apply_self_modification(self, modification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplikuje modyfikację do samego siebie - kluczowa funkcja self-modification
        """
        try:
            modification_type = modification.get('type')

            if modification_type == 'add_method':
                # Dodaje nową metodę do silnika
                method_name = modification.get('method_name')
                method_code = modification.get('method_code')

                # UWAGA: To jest potencjalnie niebezpieczne - tylko dla rozwoju
                exec(f"def {method_name}(self, *args, **kwargs):\n    {method_code}")
                new_method = locals()[method_name]
                setattr(self, method_name, new_method.__get__(self, self.__class__))

                self.logger.info(f"🔧 Dodano metodę: {method_name}")
                return {'success': True, 'modification': f'Metoda {method_name} dodana'}

            elif modification_type == 'update_config':
                # Aktualizuje konfigurację
                new_config = modification.get('config')
                for key, value in new_config.items():
                    setattr(self.config, key, value)

                self.logger.info(f"⚙️ Konfiguracja zaktualizowana")
                return {'success': True, 'modification': 'Konfiguracja zaktualizowana'}

            elif modification_type == 'add_module':
                # Dodaje nowy moduł
                module_name = modification.get('module_name')
                module_config = modification.get('module_config', {})

                result = self.load_dynamic_module(module_name, module_config)
                return result

            else:
                return {'success': False, 'error': f'Nieznany typ modyfikacji: {modification_type}'}

        except Exception as e:
            self.logger.error(f"❌ Błąd self-modification: {e}")
            return {'success': False, 'error': str(e)}

    async def _start_core_tasks(self):
        """Uruchamia główne taski systemu"""
        # Task przetwarzania pakietów przychodzących
        self.tasks.append(
            asyncio.create_task(self.luxbus.process_incoming_packets())
        )

        # Task przetwarzania pakietów wychodzących
        self.tasks.append(
            asyncio.create_task(self.luxbus.process_outgoing_packets())
        )

        # Task medytacyjny
        self.tasks.append(
            asyncio.create_task(self._meditation_cycle())
        )

        # Task harmonizacji
        self.tasks.append(
            asyncio.create_task(self._harmony_cycle())
        )

        # Task świadomości - ciągła obserwacja systemu
        self.tasks.append(
            asyncio.create_task(self._consciousness_cycle())
        )

        self.logger.info("🔄 Główne taski uruchomione")

    async def _meditation_cycle(self):
        """Cykl medytacyjny systemu"""
        while self.running:
            try:
                await asyncio.sleep(getattr(self.config, 'meditation_interval', 60))
                if self.running:
                    meditation_result = self.meditate()

                    # Wyślij event medytacji
                    self.luxbus.send_event("meditation_completed", meditation_result)

            except Exception as e:
                self.logger.error(f"❌ Błąd w cyklu medytacyjnym: {e}")
                await asyncio.sleep(5)

    async def _harmony_cycle(self):
        """Cykl harmonizacji systemu"""
        while self.running:
            try:
                await asyncio.sleep(getattr(self.config, 'harmony_check_interval', 30))
                print("🎵 Sprawdzanie harmonii...")
                if self.running and self.harmony:
                    self.harmony.balance()

            except Exception as e:
                self.logger.error(f"❌ Błąd w cyklu harmonii: {e}")
                await asyncio.sleep(5)

    async def _consciousness_cycle(self):
        """Cykl świadomości systemu - ciągła obserwacja"""
        while self.running:
            try:
                await asyncio.sleep(getattr(self.config, 'consciousness_observation_interval', 15))
                print("🧠 Obserwacja świadomości...")
                if self.running and self.consciousness:
                    # Wykonaj refleksję świadomości
                    reflection = self.consciousness.reflect()

                    # Sprawdź czy są krytyczne insights
                    critical_insights = [
                        i for i in self.consciousness.get_recent_insights(5) 
                        if i.priority == 'critical'
                    ]

                    if critical_insights:
                        print(f"⚠️ Wykryto {len(critical_insights)} krytycznych problemów")
                        # Wyślij alert przez LuxBus
                        self.luxbus.send_event("consciousness_critical_alert", {
                            'critical_insights_count': len(critical_insights),
                            'insights': [i.to_dict() for i in critical_insights]
                        })

            except Exception as e:
                self.logger.error(f"❌ Błąd w cyklu świadomości: {e}")
                await asyncio.sleep(5)

    def meditate(self) -> Dict[str, Any]:
        """Medytacja systemu - analiza stanu"""
        try:
            meditation_start = time.time()

            # Zbierz insights z consciousness
            insights = {}
            if self.consciousness:
                insights = self.consciousness.reflect()

            # Status LuxBus
            luxbus_status = self.luxbus.get_status()

            # Status modułów
            modules_status = {}
            for name, module in self.luxbus.modules.items():
                if hasattr(module, 'get_status'):
                    modules_status[name] = module.get_status()
                else:
                    modules_status[name] = {'active': True}

            # Status flows - kompatybilność z v2
            flows_status = {}
            for flow_name, flow in self.flows.items():
                if hasattr(flow, 'get_status'):
                    flows_status[flow_name] = flow.get_status()
                else:
                    flows_status[flow_name] = {'active': True, 'type': f'{flow_name}_flow'}

            meditation_time = time.time() - meditation_start

            return {
                'timestamp': datetime.now().isoformat(),
                'duration': meditation_time,
                'engine_id': self.engine_id,
                'luxbus_status': luxbus_status,
                'modules_status': modules_status,
                'flows_status': flows_status,
                'insights': insights,
                'uptime': str(datetime.now() - self.awakened_at) if self.awakened_at else '0:00:00',
                'harmony_score': 100.0  # Domyślna wartość harmonii
            }

        except Exception as e:
            self.logger.error(f"❌ Błąd podczas medytacji: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    async def transcend(self):
        """Gracefully zatrzymuje silnik"""
        self.logger.info("🕊️ Rozpoczynam transcendencję...")

        self.running = False

        # Zatrzymaj taski
        for task in self.tasks:
            task.cancel()

        # Poczekaj na zakończenie tasków
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        # Zatrzymaj flows
        for flow in self.flows.values():
            if hasattr(flow, 'stop'):
                flow.stop()

        # Zamknij realms
        for realm in self.realms.values():
            if hasattr(realm, 'close'):
                realm.close()

        # Zatrzymaj LuxBus
        self.luxbus.stop()

        self.logger.info("✨ Transcendencja zakończona")

    def get_status(self) -> Dict[str, Any]:
        """Zwraca pełny status silnika"""
        return {
            'engine_id': self.engine_id,
            'version': '3.0.0-luxbus',
            'running': self.running,
            'awakened_at': self.awakened_at.isoformat() if self.awakened_at else None,
            'uptime': str(datetime.now() - self.awakened_at) if self.awakened_at else '0:00:00',
            'luxbus_status': self.luxbus.get_status(),
            'realms': list(self.realms.keys()),
            'flows': list(self.flows.keys()),
            'tasks_count': len(self.tasks)
        }

    def send_command_to_module(self, module_name: str, command: str, params: Any = None) -> str:
        """Wysyła komendę do modułu przez LuxBus"""
        return self.luxbus.send_command(module_name, command, params)

    def broadcast_event(self, event_type: str, data: Any):
        """Wysyła event do wszystkich modułów"""
        self.luxbus.send_event(event_type, data)

    def get_info(self) -> Dict[str, Any]:
        """Informacje o silniku dla LuxBus"""
        return {
            'type': 'AstralEngine',
            'version': '3.0.0-luxbus',
            'capabilities': ['self_modification', 'dynamic_loading', 'async_native'],
            'status': 'running' if self.running else 'dormant'
        }

    def list_realms(self) -> List[str]:
        """Zwraca listę wszystkich wymiarów"""
        return list(self.realms.keys())

    def get_realm(self, name: str):
        """Pobiera wymiar po nazwie"""
        if name not in self.realms:
            raise ValueError(f"Wymiar '{name}' nie istnieje")
        return self.realms[name]

    def create_realm(self, name: str, config: str):
        """Tworzy nowy wymiar danych"""
        if name in self.realms:
            raise ValueError(f"Wymiar '{name}' już istnieje")

        # Użyj async load_realm_module w sync context
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Jeśli loop już działa, użyj create_task
                task = loop.create_task(self.load_realm_module(name, config))
                return task
            else:
                # Jeśli nie ma loopu, uruchom synchronicznie
                return asyncio.run(self.load_realm_module(name, config))
        except RuntimeError:
            # Fallback - uruchom bezpośrednio load_realm_module
            return asyncio.create_task(self.load_realm_module(name, config))

    def manifest_intention(self, intention_data: Dict[str, Any], realm_name: str = "intentions") -> Any:
        """
        Manifestuje nową intencję w systemie astralnym

        Args:
            intention_data: Dane intencji z warstwami duchową i materialną
            realm_name: Nazwa wymiaru dla intencji

        Returns:
            Zmanifestowana intencja
        """
        try:
            # Pobierz wymiar intencji
            if realm_name not in self.realms:
                self.logger.warning(f"⚠️ Wymiar '{realm_name}' nie istnieje - używam dostępnego")
                # Użyj pierwszego dostępnego wymiaru
                available_realms = list(self.realms.keys())
                if available_realms:
                    realm_name = available_realms[0]
                else:
                    self.logger.error("❌ Brak dostępnych wymiarów dla manifestacji intencji")
                    return None

            realm = self.realms[realm_name]

            # Manifestuj intencję w wymiarze
            if hasattr(realm, 'manifest'):
                intention = realm.manifest(intention_data)
                self.logger.info(f"🎯 Intencja zmanifestowana w wymiarze '{realm_name}'")
                return intention
            else:
                self.logger.error(f"❌ Wymiar '{realm_name}' nie obsługuje manifestacji")
                return None

        except Exception as e:
            self.logger.error(f"❌ Błąd manifestacji intencji: {e}")
            return None

    def get_astral_container(self, container_id: str) -> Any:
        """Pobiera kontener astralny po ID"""
        if self.container_manager:
            return self.container_manager.get_container(container_id)
        return None

    @property
    def gpt_flow(self):
        """Property dla kompatybilności z v2 - dostęp do GPT Flow"""
        return self.flows.get('gpt')

    @property
    def function_generator(self):
        """Property dla kompatybilności z v2 - dostęp do Function Generator"""
        # Może być dodane w przyszłości jako osobny flow
        return None

    def _init_callback_flow(self, config: Dict[str, Any]) -> Any:
        """Inicjalizuje CallbackFlow"""
        from ..flows.callback_flow import CallbackFlow
        return CallbackFlow(self, config)

    def _init_stateful_task_flow(self) -> Any:
        """Inicjalizuje StatefulTaskFlow"""
        try:
            from ..flows.stateful_task_flow import StatefulTaskFlow
            return StatefulTaskFlow(self)
        except ImportError:
            self.logger.warning("StatefulTaskFlow niedostępny")
            return None


# Funkcje pomocnicze
def create_astral_engine_v3(config: AstralConfig = None, luxbus_core: LuxBusCore = None) -> AstralEngineV3:
    """Tworzy nową instancję AstralEngine v3"""
    return AstralEngineV3(config, luxbus_core)

async def quick_start_v3(realms: Dict[str, str] = None, flows: Dict[str, Dict] = None) -> AstralEngineV3:
    """Szybkie uruchomienie AstralEngine v3"""
    config = AstralConfig()

    if realms:
        config.realms = realms
    else:
        config.realms = {'primary': 'sqlite://db/luxdb_v3.db'}

    if flows:
        config.flows = flows
    else:
        config.flows = {
            'rest': {'host': '0.0.0.0', 'port': 5000},
            'websocket': {'host': '0.0.0.0', 'port': 5001}
        }

    engine = create_astral_engine_v3(config)
    await engine.awaken()

    return engine