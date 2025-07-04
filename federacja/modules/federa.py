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

        # System nadzoru modułów
        self.module_logs: Dict[str, List[Dict[str, Any]]] = {}
        self.initialization_results: Dict[str, Dict[str, Any]] = {}
        self.module_performance: Dict[str, Dict[str, Any]] = {}

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
                # Przeprowadź pełną diagnostykę systemu
                diagnostic_report = await self._perform_system_diagnosis()
                
                # Wyświetl raport diagnostyczny
                await self._display_diagnostic_report(diagnostic_report)
                
                # Wyświetl raport monitorowania jeśli są dane
                if self.initialization_results:
                    await self.display_monitoring_report()
                
                # Sprawdź czy można przejść do aktywnego zarządzania
                if diagnostic_report['can_manage']:
                    print("🔄 Federa wykryła gotowość systemu - przejmuje kontrolę!")
                    print("📊 Wszystkie kluczowe komponenty gotowe - rozpoczynam zarządzanie")
                    await self._full_initialization()
                    # Przejdź do aktywnego monitorowania
                    await self._active_monitoring()
                    break
                else:
                    # Zaproponuj naprawę
                    await self._suggest_repairs(diagnostic_report)
                
                # Co 30 sekund powtarzaj diagnostykę
                await asyncio.sleep(30)
                    
            except Exception as e:
                print(f"⚠️ Błąd w pasywnym monitorowaniu: {e}")
                # Nawet przy błędzie, spróbuj zdiagnozować problem
                await self._diagnose_monitoring_error(e)
                await asyncio.sleep(5)
    
    async def _active_monitoring(self):
        """Aktywne monitorowanie systemu"""
        print("🔍 Federa - aktywne monitorowanie systemu")
        
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
                # Zdiagnozuj błąd aktywnego monitorowania
                await self._diagnose_monitoring_error(e)
                await asyncio.sleep(5)

    async def _perform_system_diagnosis(self) -> Dict[str, Any]:
        """Przeprowadza pełną diagnostykę systemu"""
        diagnosis = {
            'timestamp': datetime.now().isoformat(),
            'can_manage': False,
            'issues': [],
            'working_components': [],
            'missing_components': [],
            'repair_suggestions': []
        }
        
        # 1. Sprawdź Database Manager
        db_status = await self._diagnose_database_manager()
        diagnosis.update(db_status)
        
        # 2. Sprawdź dostępne moduły
        modules_status = await self._diagnose_available_modules()
        diagnosis.update(modules_status)
        
        # 3. Sprawdź bus komunikacyjny
        bus_status = await self._diagnose_federation_bus()
        diagnosis.update(bus_status)
        
        # 4. Sprawdź konfigurację
        config_status = await self._diagnose_configuration()
        diagnosis.update(config_status)
        
        # 5. Określ czy można zarządzać
        diagnosis['can_manage'] = (
            db_status.get('database_available', False) and
            len(diagnosis['issues']) == 0
        )
        
        return diagnosis
    
    async def _diagnose_database_manager(self) -> Dict[str, Any]:
        """Diagnozuje stan Database Manager"""
        result = {
            'database_available': False,
            'database_status': 'unknown'
        }
        
        try:
            # Sprawdź czy Database Manager jest w bus'ie
            if 'database_manager' in self.bus.subscribers:
                # Spróbuj wysłać ping
                message = FederationMessage(
                    uid="federa_db_ping",
                    from_module="federa",
                    to_module="database_manager",
                    message_type="get_status",
                    data={},
                    timestamp=datetime.now().timestamp()
                )
                
                response = await self.bus.send_message(message, timeout=3)
                if response and response.get('active', False):
                    result['database_available'] = True
                    result['database_status'] = 'active'
                    result['working_components'] = ['database_manager']
                    return result
            
            # Sprawdź czy można zaimportować
            try:
                from .database_manager import DatabaseManager
                result['database_status'] = 'importable_but_not_running'
                result['issues'] = ['Database Manager nie jest uruchomiony']
                result['repair_suggestions'] = ['Uruchom Database Manager']
            except ImportError as e:
                result['database_status'] = 'import_error'
                result['issues'] = [f'Błąd importu Database Manager: {e}']
                result['repair_suggestions'] = ['Sprawdź ścieżkę do modułu database_manager.py']
                
        except Exception as e:
            result['database_status'] = 'error'
            result['issues'] = [f'Błąd diagnostyki Database Manager: {e}']
        
        if not result['database_available']:
            result['missing_components'] = ['database_manager']
            
        return result
    
    async def _diagnose_available_modules(self) -> Dict[str, Any]:
        """Diagnozuje dostępne moduły"""
        result = {
            'modules_discovered': 0,
            'modules_importable': 0,
            'module_import_errors': []
        }
        
        manifest = self.config.get('modules', {})
        importable_modules = []
        
        for module_name, module_config in manifest.items():
            if not module_config.get('enabled', True):
                continue
                
            # Nie sprawdzaj modułów statycznych - są zarządzane przez kernel
            if module_config.get('static_startup', False):
                continue
                
            result['modules_discovered'] += 1
            
            try:
                # Spróbuj zaimportować
                module_path = f"federacja.modules.{module_name}"
                module_class_name = module_config.get('class', f"{module_name.title()}Module")
                
                module_mod = __import__(module_path, fromlist=[module_class_name])
                module_class = getattr(module_mod, module_class_name)
                
                result['modules_importable'] += 1
                importable_modules.append(module_name)
                
            except Exception as e:
                result['module_import_errors'].append(f"{module_name}: {e}")
        
        result['importable_modules'] = importable_modules
        
        if result['module_import_errors']:
            result['issues'] = result['module_import_errors']
            result['repair_suggestions'] = [
                'Sprawdź ścieżki do modułów',
                'Upewnij się że wszystkie zależności są zainstalowane'
            ]
        
        return result
    
    async def _diagnose_federation_bus(self) -> Dict[str, Any]:
        """Diagnozuje stan bus'a federacji"""
        result = {}
        
        try:
            if self.bus and hasattr(self.bus, 'running') and self.bus.running:
                result['bus_status'] = 'running'
                result['subscribers_count'] = len(self.bus.subscribers)
                result['working_components'] = result.get('working_components', []) + ['federation_bus']
            else:
                result['bus_status'] = 'not_running'
                result['issues'] = result.get('issues', []) + ['Federation Bus nie działa']
                result['missing_components'] = result.get('missing_components', []) + ['federation_bus']
                
        except Exception as e:
            result['bus_status'] = 'error'
            result['issues'] = result.get('issues', []) + [f'Błąd diagnostyki bus\'a: {e}']
            
        return result
    
    async def _diagnose_configuration(self) -> Dict[str, Any]:
        """Diagnozuje konfigurację systemu"""
        result = {}
        
        try:
            # Sprawdź manifest
            manifest = self.config.get('modules', {})
            if not manifest:
                result['issues'] = result.get('issues', []) + ['Brak konfiguracji modułów w manifeście']
                result['repair_suggestions'] = result.get('repair_suggestions', []) + ['Sprawdź plik manifest.yaml']
            else:
                enabled_modules = [name for name, config in manifest.items() if config.get('enabled', True)]
                result['enabled_modules_count'] = len(enabled_modules)
                result['working_components'] = result.get('working_components', []) + ['configuration']
                
        except Exception as e:
            result['issues'] = result.get('issues', []) + [f'Błąd odczytu konfiguracji: {e}']
            
        return result
    
    async def _display_diagnostic_report(self, diagnosis: Dict[str, Any]):
        """Wyświetla raport diagnostyczny"""
        print("\n" + "="*60)
        print("🔍 RAPORT DIAGNOSTYCZNY FEDERY")
        print("="*60)
        print(f"⏰ Czas: {diagnosis['timestamp']}")
        print(f"🎯 Stan systemu: {'✅ Gotowy' if diagnosis['can_manage'] else '⚠️ Wymaga naprawy'}")
        
        # Działające komponenty
        if diagnosis.get('working_components'):
            print(f"\n✅ DZIAŁAJĄCE KOMPONENTY ({len(diagnosis['working_components'])}):")
            for component in diagnosis['working_components']:
                print(f"   • {component}")
        
        # Brakujące komponenty
        if diagnosis.get('missing_components'):
            print(f"\n❌ BRAKUJĄCE KOMPONENTY ({len(diagnosis['missing_components'])}):")
            for component in diagnosis['missing_components']:
                print(f"   • {component}")
        
        # Problemy
        if diagnosis.get('issues'):
            print(f"\n⚠️ WYKRYTE PROBLEMY ({len(diagnosis['issues'])}):")
            for i, issue in enumerate(diagnosis['issues'], 1):
                print(f"   {i}. {issue}")
        
        # Status bazy danych
        if 'database_status' in diagnosis:
            print(f"\n📊 STATUS BAZY DANYCH: {diagnosis['database_status']}")
        
        # Moduły
        if 'modules_discovered' in diagnosis:
            print(f"\n📦 MODUŁY:")
            print(f"   • Wykryte: {diagnosis['modules_discovered']}")
            print(f"   • Importowalne: {diagnosis['modules_importable']}")
        
        print("="*60)
    
    async def _suggest_repairs(self, diagnosis: Dict[str, Any]):
        """Sugeruje naprawy na podstawie diagnozy"""
        if not diagnosis.get('repair_suggestions'):
            return
            
        print("\n🔧 SUGESTIE NAPRAWCZE FEDERY:")
        print("-" * 40)
        
        for i, suggestion in enumerate(diagnosis['repair_suggestions'], 1):
            print(f"{i}. {suggestion}")
        
        # Specjalne sugestie dla typowych problemów
        if 'Database Manager nie jest uruchomiony' in diagnosis.get('issues', []):
            print("\n💡 AUTOMATYCZNA NAPRAWA:")
            print("   Federa może spróbować uruchomić Database Manager automatycznie")
            print("   gdy kernel będzie gotowy.")
        
        if diagnosis.get('module_import_errors'):
            print("\n💡 ROZWIĄZYWANIE PROBLEMÓW Z MODUŁAMI:")
            print("   • Sprawdź czy wszystkie pliki modułów istnieją")
            print("   • Upewnij się że nie ma błędów składni")
            print("   • Sprawdź dependencies w manifeście")
        
        print("-" * 40)
    
    async def _diagnose_monitoring_error(self, error: Exception):
        """Diagnozuje błędy monitorowania"""
        print(f"\n🚨 FEDERA - DIAGNOSTYKA BŁĘDU MONITOROWANIA:")
        print(f"   Typ błędu: {type(error).__name__}")
        print(f"   Opis: {str(error)}")
        
        # Analiza typowych błędów
        if isinstance(error, asyncio.TimeoutError):
            print("   💡 Sugestia: Problem z komunikacją - sprawdź czy moduły odpowiadają")
        elif isinstance(error, KeyError):
            print("   💡 Sugestia: Brakujący klucz w konfiguracji - sprawdź manifest")
        elif isinstance(error, ImportError):
            print("   💡 Sugestia: Problem z importem modułu - sprawdź ścieżki")
        elif isinstance(error, ConnectionError):
            print("   💡 Sugestia: Problem z połączeniem - sprawdź bus komunikacyjny")
        else:
            print("   💡 Sugestia: Nieznany błąd - sprawdź logi systemu")
        
        print("   🔄 Federa będzie kontynuować monitorowanie...")

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
        """Uruchamia pojedynczy moduł z pełnym nadzorem"""
        start_time = datetime.now()
        
        # Inicjalizuj struktury nadzoru
        self.module_logs[module_name] = []
        self.initialization_results[module_name] = {
            'start_time': start_time.isoformat(),
            'status': 'initializing',
            'steps': []
        }
        
        try:
            self._log_module_event(module_name, 'info', 'Rozpoczęcie inicjalizacji modułu')
            
            # Pobierz konfigurację modułu
            module_config = self.config.get('modules', {}).get(module_name, {})
            self._log_module_event(module_name, 'info', f'Konfiguracja załadowana: {len(module_config)} parametrów')
            
            # Sprawdź czy to moduł statyczny
            if module_config.get('static_startup', False):
                self._log_module_event(module_name, 'info', 'Moduł statyczny - już uruchomiony przez kernel')
                self._finalize_module_monitoring(module_name, True, 'Static module - already running')
                return True
            
            # Krok 1: Import modułu
            self._add_initialization_step(module_name, 'import', 'starting')
            module_path = f"federacja.modules.{module_name}"
            module_class_name = module_config.get('class', f"{module_name.title()}Module")
            
            self._log_module_event(module_name, 'debug', f'Importowanie: {module_path}.{module_class_name}')
            
            try:
                module_mod = __import__(module_path, fromlist=[module_class_name])
                module_class = getattr(module_mod, module_class_name)
                self._add_initialization_step(module_name, 'import', 'success')
                self._log_module_event(module_name, 'info', f'Klasa {module_class_name} zaimportowana pomyślnie')
            except Exception as import_error:
                self._add_initialization_step(module_name, 'import', 'failed', str(import_error))
                raise import_error
            
            # Krok 2: Tworzenie instancji
            self._add_initialization_step(module_name, 'instantiation', 'starting')
            self._log_module_event(module_name, 'debug', 'Tworzenie instancji modułu')
            
            try:
                module_instance = module_class(
                    config=module_config,
                    bus=self.bus
                )
                self._add_initialization_step(module_name, 'instantiation', 'success')
                self._log_module_event(module_name, 'info', 'Instancja modułu utworzona')
            except Exception as instance_error:
                self._add_initialization_step(module_name, 'instantiation', 'failed', str(instance_error))
                raise instance_error
            
            # Krok 3: Inicjalizacja/Start
            init_method = 'initialize' if hasattr(module_instance, 'initialize') else 'start'
            self._add_initialization_step(module_name, init_method, 'starting')
            self._log_module_event(module_name, 'debug', f'Wywoływanie metody {init_method}')
            
            try:
                if init_method == 'initialize':
                    success = await module_instance.initialize()
                else:
                    success = await module_instance.start()
                
                if success:
                    self._add_initialization_step(module_name, init_method, 'success')
                    self._log_module_event(module_name, 'info', f'Metoda {init_method} zakończona pomyślnie')
                    self._finalize_module_monitoring(module_name, True, 'Module started successfully')
                    return True
                else:
                    self._add_initialization_step(module_name, init_method, 'failed', 'Method returned False')
                    self._log_module_event(module_name, 'error', f'Metoda {init_method} zwróciła False')
                    self._finalize_module_monitoring(module_name, False, 'Initialization method returned False')
                    return False
                    
            except Exception as init_error:
                self._add_initialization_step(module_name, init_method, 'failed', str(init_error))
                raise init_error

        except Exception as e:
            self._log_module_event(module_name, 'error', f'Błąd inicjalizacji: {str(e)}')
            self._finalize_module_monitoring(module_name, False, str(e))
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
            'scale_system': self.scale_system,
            'get_module_logs': self.get_module_logs,
            'get_monitoring_summary': self.get_monitoring_summary,
            'clear_module_logs': self.clear_module_logs,
            'get_failed_modules_diagnostics': self.get_failed_modules_diagnostics
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
        elif command == 'get_module_logs':
            return await self.get_module_logs(data.get('module_name'))
        elif command == 'get_monitoring_summary':
            return await self.get_monitoring_summary()
        elif command == 'clear_module_logs':
            return await self.clear_module_logs(data.get('module_name'))
        else:
            return {'error': f'Nieznana komenda: {command}'}

    async def get_status(self) -> Dict[str, Any]:
        """Zwraca status Brain"""
        monitoring_summary = await self.get_monitoring_summary()
        
        return {
            'module_id': self.module_id,
            'personality_name': self.personality_name,
            'active': self.is_active,
            'active_modules': list(self.active_modules),
            'module_count': len(self.active_modules),
            'system_load': self.system_load,
            'healthy_modules': sum(1 for h in self.module_health.values() if h),
            'decision_count': len(self.decision_history),
            'auto_scaling': self.auto_scaling_enabled,
            'intelligent_routing': self.intelligent_routing,
            'monitoring': {
                'total_modules_monitored': monitoring_summary['summary']['total_modules_monitored'],
                'success_rate': monitoring_summary['summary']['success_rate'],
                'average_init_time': monitoring_summary['summary']['average_initialization_time'],
                'recent_failures_count': len(monitoring_summary['recent_failures'])
            }
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
    
    def _log_module_event(self, module_name: str, level: str, message: str):
        """Loguje wydarzenie związane z modułem"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'federa_monitoring': True
        }
        
        if module_name not in self.module_logs:
            self.module_logs[module_name] = []
        
        self.module_logs[module_name].append(event)
        
        # Wyświetl w konsoli z prefiksem Federy
        level_emoji = {
            'debug': '🔍',
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌'
        }
        
        emoji = level_emoji.get(level, 'ℹ️')
        print(f"🧠 Federa [{module_name}] {emoji} {message}")
    
    def _add_initialization_step(self, module_name: str, step_name: str, status: str, error_message: str = None):
        """Dodaje krok inicjalizacji do monitorowania"""
        step = {
            'name': step_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'error': error_message
        }
        
        if module_name in self.initialization_results:
            self.initialization_results[module_name]['steps'].append(step)
    
    def _finalize_module_monitoring(self, module_name: str, success: bool, final_message: str):
        """Finalizuje monitorowanie modułu"""
        end_time = datetime.now()
        start_time_str = self.initialization_results[module_name]['start_time']
        start_time = datetime.fromisoformat(start_time_str)
        duration = (end_time - start_time).total_seconds()
        
        self.initialization_results[module_name].update({
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'status': 'success' if success else 'failed',
            'final_message': final_message,
            'logs_count': len(self.module_logs.get(module_name, []))
        })
        
        # Zapisz metryki wydajności
        self.module_performance[module_name] = {
            'initialization_duration': duration,
            'steps_count': len(self.initialization_results[module_name]['steps']),
            'success': success,
            'timestamp': end_time.isoformat()
        }
        
        # Wyświetl podsumowanie
        status_emoji = '✅' if success else '❌'
        print(f"🧠 Federa [{module_name}] {status_emoji} Inicjalizacja zakończona w {duration:.2f}s - {final_message}")
    
    async def get_module_logs(self, module_name: str = None) -> Dict[str, Any]:
        """Zwraca logi modułów"""
        if module_name:
            return {
                'logs': self.module_logs.get(module_name, []),
                'initialization': self.initialization_results.get(module_name, {}),
                'performance': self.module_performance.get(module_name, {})
            }
        else:
            return {
                'all_logs': self.module_logs,
                'all_initialization_results': self.initialization_results,
                'all_performance': self.module_performance
            }
    
    async def get_monitoring_summary(self) -> Dict[str, Any]:
        """Zwraca podsumowanie monitorowania"""
        total_modules = len(self.initialization_results)
        successful_modules = sum(1 for result in self.initialization_results.values() 
                               if result.get('status') == 'success')
        failed_modules = sum(1 for result in self.initialization_results.values() 
                           if result.get('status') == 'failed')
        
        avg_duration = 0
        if self.module_performance:
            total_duration = sum(perf.get('initialization_duration', 0) 
                               for perf in self.module_performance.values())
            avg_duration = total_duration / len(self.module_performance)
        
        return {
            'summary': {
                'total_modules_monitored': total_modules,
                'successful_initializations': successful_modules,
                'failed_initializations': failed_modules,
                'success_rate': (successful_modules / max(total_modules, 1)) * 100,
                'average_initialization_time': avg_duration
            },
            'module_statuses': {
                name: result.get('status', 'unknown') 
                for name, result in self.initialization_results.items()
            },
            'recent_failures': [
                {
                    'module': name,
                    'error': result.get('final_message', 'Unknown error'),
                    'timestamp': result.get('end_time')
                }
                for name, result in self.initialization_results.items()
                if result.get('status') == 'failed'
            ][-5:]  # Ostatnie 5 błędów
        }
    
    async def clear_module_logs(self, module_name: str = None) -> Dict[str, Any]:
        """Czyści logi modułów"""
        if module_name:
            if module_name in self.module_logs:
                cleared_count = len(self.module_logs[module_name])
                self.module_logs[module_name] = []
                return {
                    'success': True, 
                    'cleared_logs': cleared_count,
                    'module': module_name
                }
            else:
                return {'success': False, 'error': f'Brak logów dla modułu {module_name}'}
        else:
            total_cleared = sum(len(logs) for logs in self.module_logs.values())
            self.module_logs.clear()
            return {
                'success': True,
                'cleared_logs': total_cleared,
                'modules_cleared': len(self.module_logs)
            }
    
    async def get_failed_modules_diagnostics(self) -> Dict[str, Any]:
        """Zwraca szczegółową diagnostykę modułów, które nie udało się uruchomić"""
        failed_modules = {}
        
        for module_name, result in self.initialization_results.items():
            if result.get('status') == 'failed':
                failed_steps = [
                    step for step in result.get('steps', [])
                    if step.get('status') == 'failed'
                ]
                
                failed_modules[module_name] = {
                    'final_error': result.get('final_message'),
                    'duration': result.get('duration_seconds', 0),
                    'failed_steps': failed_steps,
                    'all_steps': result.get('steps', []),
                    'logs': self.module_logs.get(module_name, [])
                }
        
        return {
            'failed_modules_count': len(failed_modules),
            'diagnostics': failed_modules,
            'common_failure_patterns': self._analyze_failure_patterns(failed_modules)
        }
    
    def _analyze_failure_patterns(self, failed_modules: Dict[str, Any]) -> Dict[str, Any]:
        """Analizuje wzorce błędów w modułach"""
        patterns = {
            'import_errors': 0,
            'instantiation_errors': 0,
            'initialization_errors': 0,
            'common_error_keywords': {}
        }
        
        for module_name, diagnostics in failed_modules.items():
            for step in diagnostics.get('failed_steps', []):
                step_name = step.get('name', '')
                if 'import' in step_name:
                    patterns['import_errors'] += 1
                elif 'instantiation' in step_name:
                    patterns['instantiation_errors'] += 1
                elif step_name in ['initialize', 'start']:
                    patterns['initialization_errors'] += 1
                
                # Analizuj słowa kluczowe w błędach
                error_msg = step.get('error', '').lower()
                for keyword in ['missing', 'not found', 'import', 'module', 'attribute']:
                    if keyword in error_msg:
                        patterns['common_error_keywords'][keyword] = patterns['common_error_keywords'].get(keyword, 0) + 1
        
        return patterns
    
    async def display_monitoring_report(self):
        """Wyświetla szczegółowy raport monitorowania"""
        print("\n" + "="*80)
        print("🧠 FEDERA - RAPORT MONITOROWANIA MODUŁÓW")
        print("="*80)
        
        summary = await self.get_monitoring_summary()
        
        # Podsumowanie ogólne
        print(f"\n📊 PODSUMOWANIE OGÓLNE:")
        print(f"   • Monitorowanych modułów: {summary['summary']['total_modules_monitored']}")
        print(f"   • Udanych inicjalizacji: {summary['summary']['successful_initializations']}")
        print(f"   • Nieudanych inicjalizacji: {summary['summary']['failed_initializations']}")
        print(f"   • Wskaźnik sukcesu: {summary['summary']['success_rate']:.1f}%")
        print(f"   • Średni czas inicjalizacji: {summary['summary']['average_initialization_time']:.2f}s")
        
        # Status modułów
        print(f"\n📦 STATUS MODUŁÓW:")
        for module_name, status in summary['module_statuses'].items():
            status_emoji = '✅' if status == 'success' else '❌' if status == 'failed' else '⏳'
            duration = self.module_performance.get(module_name, {}).get('initialization_duration', 0)
            print(f"   {status_emoji} {module_name}: {status} ({duration:.2f}s)")
        
        # Ostatnie błędy
        if summary['recent_failures']:
            print(f"\n⚠️ OSTATNIE BŁĘDY ({len(summary['recent_failures'])}):")
            for failure in summary['recent_failures']:
                print(f"   • {failure['module']}: {failure['error']}")
                print(f"     ⏰ {failure['timestamp']}")
        
        # Diagnostyka błędów
        if summary['summary']['failed_initializations'] > 0:
            diagnostics = await self.get_failed_modules_diagnostics()
            patterns = diagnostics['common_failure_patterns']
            
            print(f"\n🔍 ANALIZA WZORCÓW BŁĘDÓW:")
            print(f"   • Błędy importu: {patterns['import_errors']}")
            print(f"   • Błędy tworzenia instancji: {patterns['instantiation_errors']}")
            print(f"   • Błędy inicjalizacji: {patterns['initialization_errors']}")
            
            if patterns['common_error_keywords']:
                print(f"   • Najczęstsze słowa kluczowe w błędach:")
                for keyword, count in patterns['common_error_keywords'].items():
                    print(f"     - '{keyword}': {count} wystąpień")
        
        print("="*80)

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