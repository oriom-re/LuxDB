"""
Analysis: The code changes introduce new methods for searching and storing module metadata, utilizing a metadata manager.
"""
"""
🧠 Brain - Inteligentny Koordynator Federacji

Brain decyduje jakie moduły uruchomić i jak nimi zarządzać
"""

import asyncio
from typing import Dict, Any, List, Set, Type, Optional
from datetime import datetime

from ..core.bus import FederationBus, FederationMessage
from ..core.lux_module import LuxModule, ModuleType, ModuleVersion, ModuleStability


class BrainModule(LuxModule):
    """
    🧠 Federa - Inteligentna Koordynatorka Federacji

    Mądra, cierpliwa inteligencja, która decyduje jakie moduły uruchomić
    i jak nimi zarządzać. Federa to serce i umysł całej federacji.
    """

    def __init__(self, config: Dict[str, Any], bus: FederationBus):
        super().__init__(
            name="federa",  # Nowa nazwa!
            module_type=ModuleType.INTELLIGENCE,
            version=ModuleVersion(1, 0, 0, ModuleStability.STABLE),
            config=config,
            bus=bus,
            creator_id="federation_system"
        )

        self.module_id = "federa"
        self.personality_name = "Federa"

        # Stan systemu
        self.active_modules: Set[str] = set()
        self.module_dependencies: Dict[str, List[str]] = {}
        self.module_health: Dict[str, bool] = {}
        self.system_load = 0.0

        # Magazyn modułów
        self.available_modules: Dict[str, Type[LuxModule]] = {}
        self.binary_modules: Dict[str, str] = {}  # UUID -> binary data
        self.experimental_modules: Dict[str, LuxModule] = {}
        self.stable_fallbacks: Dict[str, LuxModule] = {}

        # Inteligencja Brain'a
        self.decision_history: List[Dict[str, Any]] = []
        self.auto_scaling_enabled = config.get('auto_scaling', True)
        self.intelligent_routing = config.get('intelligent_routing', True)

        # Rejestracja w bus'ie
        # self.bus.register_module(self.module_id, self)

        # Słownik modulemetadata manager
        self.metadata_manager = None

        print("🧠 Federa - Inteligentna Koordynatorka Federacji zainicjalizowana")

    async def start(self) -> bool:
        """Uruchamia Brain Module"""
        if not await super().start():
            return False

        print("🧠 Federa rozpoczyna analizę systemu...")
        return True

    async def heartbeat(self) -> bool:
        """Puls życia Brain Module"""
        if not await super().heartbeat():
            return False

        # Brain może tutaj wykonywać analizę systemu
        await self._analyze_system_health()
        return True

    async def _analyze_system_health(self):
        """Analizuje zdrowie systemu"""
        try:
            # Sprawdź obciążenie
            await self._check_system_load()

            # Adaptacyjne skalowanie
            await self._adaptive_scaling()

        except Exception as e:
            self.record_error(f"System analysis failed: {str(e)}")

    async def initialize(self) -> bool:
        """Inicjalizuje moduł Brain z inteligentnym zarządzaniem zależnościami"""
        try:
            print("🧠 Inicjalizacja Brain z kontrolą zależności...")

            # Analizuj dostępne moduły
            await self._analyze_available_modules()

            # Sprawdź czy można rozpocząć zarządzanie
            if not await self._can_start_management():
                print("⏳ Brain w trybie podstawowym - czeka na kluczowe moduły")
                # Uruchom monitoring bez aktywnego zarządzania
                asyncio.create_task(self._passive_monitoring())
                self.is_active = True
                return True

            # Pełne uruchomienie z zarządzaniem
            return await self._full_initialization()

        except Exception as e:
            print(f"❌ Błąd inicjalizacji Brain: {e}")
            # Nawet przy błędzie, próbuj uruchomić tryb podstawowy
            self.is_active = True
            asyncio.create_task(self._passive_monitoring())
            return True
    
    async def _can_start_management(self) -> bool:
        """Sprawdza czy Brain może rozpocząć aktywne zarządzanie"""
        # Sprawdź czy Database Manager jest dostępny
        database_available = await self._check_database_availability()
        
        # Sprawdź czy GPT jest skonfigurowany (opcjonalnie)
        gpt_configured = await self._check_gpt_configuration()
        
        # Brain może działać jeśli ma bazę danych
        can_manage = database_available
        
        print(f"🔍 Federa analizuje gotowość systemu:")
        print(f"   📊 Database Manager: {'✅' if database_available else '❌'}")
        print(f"   🤖 GPT Flow: {'✅' if gpt_configured else '⚠️ opcjonalny'}")
        print(f"   🧠 Federa może zarządzać: {'✅' if can_manage else '❌'}")
        
        return can_manage
    
    async def _check_database_availability(self) -> bool:
        """Sprawdza czy Database Manager jest dostępny"""
        try:
            # Sprawdź czy database_manager już działa w busie
            try:
                message = FederationMessage(
                    uid="federa_db_check",
                    from_module="federa",
                    to_module="database_manager",
                    message_type="get_status",
                    data={},
                    timestamp=datetime.now().timestamp()
                )
                
                response = await self.bus.send_message(message, timeout=2)
                if response.get('active', False):
                    return True
            except Exception:
                pass
            
            # Sprawdź czy database_manager jest w dostępnych modułach
            if 'database_manager' in self.available_modules:
                return True
            
            # Sprawdź czy można go załadować
            try:
                from .database_manager import DatabaseManager
                return True
            except ImportError:
                return False
                
        except Exception:
            return False
    
    async def _check_gpt_configuration(self) -> bool:
        """Sprawdza czy GPT Flow jest skonfigurowany"""
        try:
            import os
            return os.getenv('OPENAI_API_KEY') is not None
        except Exception:
            return False
    
    async def _full_initialization(self) -> bool:
        """Pełna inicjalizacja z aktywnym zarządzaniem"""
        print("🚀 Brain - pełna inicjalizacja z zarządzaniem modułami")
        
        # Podejmij decyzje o uruchomieniu
        startup_plan = await self._create_startup_plan()

        # Wykonaj plan
        success = await self._execute_startup_plan(startup_plan)

        # Rejestruj komendy
        await self._register_commands()

        # Uruchom aktywne monitorowanie
        asyncio.create_task(self._active_monitoring())

        print(f"🧠 Brain aktywny - zarządza {len(self.active_modules)} modułami")
        return success
    
    async def _passive_monitoring(self):
        """Pasywne monitorowanie - czeka na gotowość do zarządzania"""
        print("👁️ Federa w trybie obserwacji - cierpliwie czeka na gotowość systemu")
        
        while self.is_active:
            try:
                # Co 30 sekund sprawdzaj czy można przejść do aktywnego zarządzania
                await asyncio.sleep(30)
                
                if await self._can_start_management():
                    print("🔄 Federa wykryła gotowość systemu - przejmuje kontrolę!")
                    print("📊 Wykryto działający Database Manager - rozpoczynam zarządzanie")
                    await self._full_initialization()
                    # Przejdź do aktywnego monitorowania
                    await self._active_monitoring()
                    break
                    
            except Exception as e:
                print(f"⚠️ Błąd w pasywnym monitorowaniu: {e}")
                await asyncio.sleep(5)
    
    async def _active_monitoring(self):
        """Aktywne monitorowanie systemu"""
        print("🔍 Brain - aktywne monitorowanie systemu")
        
        while self.is_active:
            try:
                # Sprawdź zdrowie modułów
                await self._check_module_health()

                # Sprawdź obciążenie systemu
                await self._check_system_load()

                # Podejmij decyzje adaptacyjne
                if self.auto_scaling_enabled:
                    await self._adaptive_scaling()

                # Czekaj przed następnym cyklem
                await asyncio.sleep(10)  # Monitorowanie co 10 sekund

            except Exception as e:
                print(f"⚠️ Błąd w aktywnym monitorowaniu systemu: {e}")
                await asyncio.sleep(5)

    async def shutdown(self) -> bool:
        """Wyłącza moduł Brain"""
        try:
            print("🧠 Wyłączanie Brain...")

            # Stwórz plan wyłączenia
            shutdown_plan = await self._create_shutdown_plan()

            # Wykonaj plan
            await self._execute_shutdown_plan(shutdown_plan)

            self.is_active = False
            print("🧠 Brain wyłączony")
            return True

        except Exception as e:
            print(f"❌ Błąd wyłączania Brain: {e}")
            return False

    async def _analyze_available_modules(self):
        """Analizuje dostępne moduły z manifestu i klas"""
        manifest = self.config.get('modules', {})

        for module_name, module_config in manifest.items():
            if module_config.get('enabled', True):
                # Federa zarządza tylko modułami niestatycznymi
                is_static = module_config.get('static_startup', False)
                
                if is_static:
                    print(f"📋 Moduł {module_name} - statyczny, pomijany przez Federę")
                    continue
                
                dependencies = module_config.get('dependencies', [])
                self.module_dependencies[module_name] = dependencies
                self.module_health[module_name] = False  # Domyślnie nieaktywne

                # Spróbuj załadować klasę modułu
                await self._discover_module_class(module_name, module_config)

                print(f"🔍 Znaleziono moduł niestatyczny: {module_name} (deps: {dependencies})")

    async def _discover_module_class(self, module_name: str, module_config: Dict[str, Any]):
        """Odkrywa i analizuje klasę modułu"""
        try:
            # Spróbuj zaimportować moduł
            if 'path' in module_config:
                module_path = module_config['path'].replace('/', '.').replace('.py', '')
                module = __import__(f"federacja.{module_path}", fromlist=[module_name])

                # Szukaj klas dziedziczących po LuxModule
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, LuxModule) and 
                        attr != LuxModule):

                        self.available_modules[module_name] = attr

                        # Analizuj moduł
                        module_info = await self._analyze_module_class(attr)
                        print(f"📊 Moduł {module_name}: {module_info}")

                        break

        except Exception as e:
            print(f"⚠️ Nie udało się załadować modułu {module_name}: {e}")

    async def _analyze_module_class(self, module_class: Type[LuxModule]) -> Dict[str, Any]:
        """Analizuje klasę modułu"""
        # Utwórz tymczasową instancję dla analizy
        try:
            temp_instance = module_class(
                name="temp_analysis",
                module_type=ModuleType.CORE,  # Domyślny typ
                config={}
            )

            type_info = temp_instance.get_type_info()

            # Zapisz informacje o module
            analysis = {
                'class_name': module_class.__name__,
                'base_classes': [cls.__name__ for cls in module_class.__mro__],
                'is_lux_module': issubclass(module_class, LuxModule),
                'capabilities': type_info.get('capabilities', []),
                'module_type': type_info.get('module_type', 'unknown'),
                'experimental': type_info.get('experimental', False)
            }

            return analysis

        except Exception as e:
            return {
                'class_name': module_class.__name__,
                'error': str(e),
                'analyzable': False
            }

    async def register_binary_module(self, module_uuid: str, binary_data: str) -> bool:
        """Rejestruje moduł binarny w systemie"""
        try:
            # Spróbuj zdeserializować dla walidacji
            module = LuxModule.deserialize_from_binary(binary_data, self.bus)

            # Zapisz w magazynie
            self.binary_modules[module_uuid] = binary_data

            # Dodaj do dostępnych modułów
            self.available_modules[module.name] = module.__class__

            print(f"📦 Zarejestrowano moduł binarny: {module.name} (UUID: {module_uuid})")

            self.decision_history.append({
                'type': 'binary_module_registered',
                'timestamp': datetime.now().isoformat(),
                'module_name': module.name,
                'module_uuid': module_uuid
            })

            return True

        except Exception as e:
            print(f"❌ Błąd rejestracji modułu binarnego {module_uuid}: {e}")
            return False

    async def load_binary_module(self, module_uuid: str) -> Optional[LuxModule]:
        """Ładuje moduł z formatu binarnego"""
        if module_uuid not in self.binary_modules:
            return None

        try:
            binary_data = self.binary_modules[module_uuid]
            module = LuxModule.deserialize_from_binary(binary_data, self.bus)

            print(f"📂 Załadowano moduł binarny: {module.name}")
            return module

        except Exception as e:
            print(f"❌ Błąd ładowania modułu binarnego {module_uuid}: {e}")
            return None

    async def handle_experimental_module(self, module_name: str, experimental_module: LuxModule) -> bool:
        """Obsługuje moduł eksperymentalny z fallback do stabilnego"""
        try:
            # Spróbuj uruchomić eksperymentalny
            success = await experimental_module.initialize()

            if success:
                self.experimental_modules[module_name] = experimental_module
                self.active_modules.add(module_name)

                print(f"🧪 Uruchomiono moduł eksperymentalny: {module_name}")

                # Monitoruj błędy
                asyncio.create_task(self._monitor_experimental_module(module_name, experimental_module))

                return True
            else:
                # Fallback do stabilnego
                return await self._fallback_to_stable_module(module_name)

        except Exception as e:
            print(f"❌ Błąd modułu eksperymentalnego {module_name}: {e}")
            return await self._fallback_to_stable_module(module_name)

    async def _monitor_experimental_module(self, module_name: str, module: LuxModule):
        """Monitoruje moduł eksperymentalny"""
        while module.is_active and not module.should_fallback_to_stable():
            await asyncio.sleep(30)  # Sprawdzaj co 30 sekund

        if module.should_fallback_to_stable():
            print(f"🔄 Moduł eksperymentalny {module_name} przekroczył limit błędów - fallback")
            await self._fallback_to_stable_module(module_name)

    async def _fallback_to_stable_module(self, module_name: str) -> bool:
        """Przywraca stabilną wersję modułu"""
        try:
            # Wyłącz eksperymentalny jeśli aktywny
            if module_name in self.experimental_modules:
                await self.experimental_modules[module_name].shutdown()
                del self.experimental_modules[module_name]

            # Uruchom stabilny
            stable_module = await self._create_stable_module(module_name)
            if stable_module:
                success = await stable_module.initialize()
                if success:
                    self.stable_fallbacks[module_name] = stable_module
                    self.active_modules.add(module_name)

                    print(f"🛡️ Przywrócono stabilną wersję modułu: {module_name}")

                    self.decision_history.append({
                        'type': 'experimental_fallback',
                        'timestamp': datetime.now().isoformat(),
                        'module_name': module_name,
                        'reason': 'Experimental module failed'
                    })

                    return True

            return False

        except Exception as e:
            print(f"❌ Błąd fallback modułu {module_name}: {e}")
            return False

    async def _create_stable_module(self, module_name: str) -> Optional[LuxModule]:
        """Tworzy stabilną wersję modułu"""
        if module_name not in self.available_modules:
            return None

        try:
            module_class = self.available_modules[module_name]
            config = self.config.get('modules', {}).get(module_name, {})

            # Utwórz z flagą stabilności
            stable_version = ModuleVersion(1, 0, 0, ModuleStability.STABLE)

            module = module_class(
                name=module_name,
                module_type=ModuleType.CORE,  # Domyślny typ
                version=stable_version,
                config=config,
                bus=self.bus
            )

            return module

        except Exception as e:
            print(f"❌ Błąd tworzenia stabilnego modułu {module_name}: {e}")
            return None

    async def _create_startup_plan(self) -> List[str]:
        """Tworzy inteligentny plan uruchomienia modułów"""
        print("🧠 Tworzenie planu uruchomienia...")

        # Sortowanie topologiczne według zależności
        startup_order = []
        remaining_modules = set(self.module_dependencies.keys())

        while remaining_modules:
            # Znajdź moduły bez niespełnionych zależności
            ready_modules = []

            for module in remaining_modules:
                dependencies = self.module_dependencies[module]
                if all(dep in startup_order for dep in dependencies):
                    ready_modules.append(module)

            if not ready_modules:
                # Cykliczne zależności - uruchom pierwszy z listy
                print("⚠️ Wykryto możliwe cykliczne zależności")
                ready_modules = [list(remaining_modules)[0]]

            # Dodaj do planu
            for module in ready_modules:
                startup_order.append(module)
                remaining_modules.remove(module)

        print(f"📋 Plan uruchomienia: {startup_order}")

        # Zapisz decyzję
        self.decision_history.append({
            'type': 'startup_plan',
            'timestamp': datetime.now().isoformat(),
            'decision': startup_order,
            'reasoning': 'Topological sort of dependencies'
        })

        return startup_order

    async def _execute_startup_plan(self, startup_plan: List[str]) -> bool:
        """Wykonuje plan uruchomienia"""
        print("🚀 Wykonywanie planu uruchomienia...")

        success_count = 0

        for module_name in startup_plan:
            try:
                print(f"🔄 Uruchamianie modułu: {module_name}")

                # Wysłij komendę uruchomienia przez bus
                success = await self._start_module(module_name)

                if success:
                    self.active_modules.add(module_name)
                    self.module_health[module_name] = True
                    success_count += 1
                    print(f"✅ Moduł {module_name} uruchomiony")
                else:
                    print(f"❌ Nie udało się uruchomić modułu {module_name}")

                # Krótka pauza między modułami
                await asyncio.sleep(0.1)

            except Exception as e:
                print(f"❌ Błąd uruchamiania modułu {module_name}: {e}")

        print(f"📊 Uruchomiono {success_count}/{len(startup_plan)} modułów")
        return success_count > 0

    async def _start_module(self, module_name: str) -> bool:
        """Uruchamia pojedynczy moduł"""
        try:
            # Pobierz konfigurację modułu
            module_config = self.config.get('modules', {}).get(module_name, {})
            
            # Sprawdź czy to moduł statyczny - jeśli tak, już powinien być uruchomiony
            if module_config.get('static_startup', False):
                print(f"ℹ️ Moduł {module_name} - statyczny, już uruchomiony")
                return True
            
            # Dynamiczny import modułu
            module_path = f"federacja.modules.{module_name}"
            module_class_name = module_config.get('class', f"{module_name.title()}Module")
            
            module_mod = __import__(module_path, fromlist=[module_class_name])
            module_class = getattr(module_mod, module_class_name)
            
            # Inicjalizuj moduł zarządzany przez Federę
            module_instance = module_class(
                config=module_config,
                bus=self.bus
            )
            
            # Uruchom moduł
            if hasattr(module_instance, 'initialize'):
                success = await module_instance.initialize()
            else:
                success = await module_instance.start()
            
            if success:
                print(f"✅ Federa uruchomiła moduł: {module_name}")
                return True
            else:
                print(f"❌ Federa nie mogła uruchomić modułu: {module_name}")
                return False

        except Exception as e:
            print(f"❌ Błąd uruchamiania {module_name}: {e}")
            return False

    async def _create_shutdown_plan(self) -> List[str]:
        """Tworzy plan wyłączenia modułów (odwrotny do uruchomienia)"""
        shutdown_order = list(reversed(list(self.active_modules)))

        print(f"📋 Plan wyłączenia: {shutdown_order}")

        # Zapisz decyzję
        self.decision_history.append({
            'type': 'shutdown_plan',
            'timestamp': datetime.now().isoformat(),
            'decision': shutdown_order,
            'reasoning': 'Reverse dependency order'
        })

        return shutdown_order

    async def _execute_shutdown_plan(self, shutdown_plan: List[str]):
        """Wykonuje plan wyłączenia"""
        print("🛑 Wykonywanie planu wyłączenia...")

        for module_name in shutdown_plan:
            try:
                print(f"🔄 Wyłączanie modułu: {module_name}")

                success = await self._stop_module(module_name)

                if success:
                    self.active_modules.discard(module_name)
                    self.module_health[module_name] = False
                    print(f"✅ Moduł {module_name} wyłączony")
                else:
                    print(f"⚠️ Problem z wyłączeniem modułu {module_name}")

                await asyncio.sleep(0.1)

            except Exception as e:
                print(f"❌ Błąd wyłączania modułu {module_name}: {e}")

    async def _stop_module(self, module_name: str) -> bool:
        """Wyłącza pojedynczy moduł"""
        try:
            # Wysłij komendę wyłączenia przez bus
            message = FederationMessage(
                uid=f"brain_shutdown_{module_name}",
                from_module="brain",
                to_module=module_name,
                message_type="shutdown",
                data={},
                timestamp=datetime.now().timestamp()
            )

            response = await self.bus.send_message(message)
            return response.get('success', True)

        except Exception as e:
            print(f"❌ Błąd wyłączania {module_name}: {e}")
            return False

    async def _register_commands(self):
        """Rejestruje komendy Brain w bus'ie"""
        commands = {
            'get_status': self.get_status,
            'list_active_modules': self.list_active_modules,
            'module_health': self.get_module_health,
            'decision_history': self.get_decision_history,
            'restart_module': self.restart_module,
            'scale_system': self.scale_system
        }

        for cmd_name, cmd_func in commands.items():
            await self.bus.register_command(f"{self.module_id}.{cmd_name}", cmd_func)

    

    async def _check_module_health(self):
        """Sprawdza zdrowie wszystkich modułów"""
        for module_name in self.active_modules:
            try:
                # Wyślij ping do modułu
                message = FederationMessage(
                    uid=f"brain_health_{module_name}",
                    from_module="brain",
                    to_module=module_name,
                    message_type="health_check",
                    data={},
                    timestamp=datetime.now().timestamp()
                )

                response = await self.bus.send_message(message, timeout=5)
                self.module_health[module_name] = response.get('healthy', False)

            except Exception:
                self.module_health[module_name] = False

    async def _check_system_load(self):
        """Sprawdza obciążenie systemu"""
        # Prosty wskaźnik obciążenia na podstawie liczby aktywnych modułów
        max_modules = self.config.get('kernel', {}).get('max_modules', 50)
        self.system_load = len(self.active_modules) / max_modules

    async def _adaptive_scaling(self):
        """Adaptacyjne skalowanie systemu"""
        if self.system_load > 0.8:
            print("🚨 Wysokie obciążenie systemu - rozważam wyłączenie nieistotnych modułów")
        elif self.system_load < 0.3:
            print("📈 Niskie obciążenie - mogę uruchomić dodatkowe moduły")

    async def handle_message(self, message: FederationMessage) -> Any:
        """Obsługuje wiadomości z bus'a"""
        command = message.message_type
        data = message.data

        if command == 'get_status':
            return await self.get_status()
        elif command == 'list_active_modules':
            return await self.list_active_modules()
        elif command == 'module_health':
            return await self.get_module_health()
        elif command == 'decision_history':
            return await self.get_decision_history()
        elif command == 'restart_module':
            return await self.restart_module(data.get('module_name'))
        elif command == 'scale_system':
            return await self.scale_system(data.get('action'))
        else:
            return {'error': f'Nieznana komenda: {command}'}

    async def get_status(self) -> Dict[str, Any]:
        """Zwraca status Brain"""
        return {
            'module_id': self.module_id,
            'active': self.is_active,
            'active_modules': list(self.active_modules),
            'module_count': len(self.active_modules),
            'system_load': self.system_load,
            'healthy_modules': sum(1 for h in self.module_health.values() if h),
            'decision_count': len(self.decision_history),
            'auto_scaling': self.auto_scaling_enabled,
            'intelligent_routing': self.intelligent_routing
        }

    async def list_active_modules(self) -> List[str]:
        """Zwraca listę aktywnych modułów"""
        return list(self.active_modules)

    async def get_module_health(self) -> Dict[str, bool]:
        """Zwraca status zdrowia modułów"""
        return self.module_health.copy()

    async def get_decision_history(self) -> List[Dict[str, Any]]:
        """Zwraca historię decyzji Brain"""
        return self.decision_history[-10:]  # Ostatnie 10 decyzji

    async def restart_module(self, module_name: str) -> bool:
        """Restartuje moduł"""
        if module_name not in self.active_modules:
            return False

        print(f"🔄 Restartowanie modułu: {module_name}")

        # Wyłącz
        await self._stop_module(module_name)
        self.active_modules.discard(module_name)

        # Krótka pauza
        await asyncio.sleep(1)

        # Uruchom ponownie
        success = await self._start_module(module_name)
        if success:
            self.active_modules.add(module_name)
            self.module_health[module_name] = True

        # Zapisz decyzję
        self.decision_history.append({
            'type': 'module_restart',
            'timestamp': datetime.now().isoformat(),
            'module': module_name,
            'success': success
        })

        return success

    async def scale_system(self, action: str) -> bool:
        """Skaluje system w górę lub w dół"""
        if action == 'up':
            print("📈 Skalowanie systemu w górę")
            # Logika uruchamiania dodatkowych modułów
        elif action == 'down':
            print("📉 Skalowanie systemu w dół") 
            # Logika wyłączania zbędnych modułów

        return True

    async def search_modules(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Wyszukuje moduły na podstawie kryteriów"""
        if not self.metadata_manager:
            return []

        return await self.metadata_manager.search_modules(**criteria)

    async def store_module_metadata(self, module: LuxModule, binary_data: Optional[str] = None,
                                   file_path: Optional[str] = None) -> bool:
        """Przechowuje metadane modułu"""
        if not self.metadata_manager:
            return False

        return await self.metadata_manager.store_module_metadata(module, binary_data, file_path)