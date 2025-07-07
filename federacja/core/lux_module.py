"""
🧩 LuxModule - Bazowa klasa wszystkich modułów w Federacji

Rozszerza LuxBase o:
- Wersjonowanie
- Typy modułów
- Zarządzanie eksperymentami
- Przechowywanie binarne
"""

import json
import pickle
import base64
from typing import Dict, Any, Optional, List, Type, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from .lux_base import LuxBase
from .bus import FederationBus, FederationMessage


class ModuleFormType(Enum):
    """Forma przechowywania modułu"""
    FILE = "file"              # Moduł z pliku
    BINARY = "binary"          # Moduł binarny z bazy


class ModuleType(Enum):
    """Typy modułów"""
    CORE = "core"              # Podstawowe moduły systemu
    REALM = "realm"            # Moduły wymiarów danych
    FLOW = "flow"              # Moduły przepływu danych
    INTELLIGENCE = "intelligence"  # Moduły inteligencji
    INTERFACE = "interface"    # Moduły interfejsów
    EXPERIMENTAL = "experimental"  # Moduły eksperymentalne
    PLUGIN = "plugin"          # Wtyczki
    SERVICE = "service"        # Usługi


class ModuleStability(Enum):
    """Poziomy stabilności modułów"""
    STABLE = "stable"          # Stabilny
    BETA = "beta"              # Beta
    ALPHA = "alpha"            # Alpha
    EXPERIMENTAL = "experimental"  # Eksperymentalny
    DEPRECATED = "deprecated"   # Przestarzały


@dataclass
class ModuleVersion:
    """Wersja modułu"""
    major: int = 1
    minor: int = 0
    patch: int = 0
    stability: ModuleStability = ModuleStability.STABLE
    build: Optional[str] = None

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.stability != ModuleStability.STABLE:
            version += f"-{self.stability.value}"
        if self.build:
            version += f"+{self.build}"
        return version

    def to_dict(self) -> Dict[str, Any]:
        return {
            'major': self.major,
            'minor': self.minor,
            'patch': self.patch,
            'stability': self.stability.value,
            'build': self.build
        }

    @classmethod
    def from_string(cls, version_str: str) -> 'ModuleVersion':
        """Parsuje wersję z stringa"""
        # Podstawowe parsowanie - można rozbudować
        parts = version_str.split('.')
        major = int(parts[0]) if len(parts) > 0 else 1
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0

        return cls(major=major, minor=minor, patch=patch)


@dataclass
class ModuleManifest:
    """Manifest modułu"""
    name: str
    module_type: ModuleType
    version: ModuleVersion
    description: str
    form_type: ModuleFormType = ModuleFormType.FILE
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    author: Optional[str] = None
    license: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'module_type': self.module_type.value,
            'version': self.version.to_dict(),
            'description': self.description,
            'form_type': self.form_type.value,
            'dependencies': self.dependencies,
            'capabilities': self.capabilities,
            'config_schema': self.config_schema,
            'author': self.author,
            'license': self.license
        }


class LuxModule(LuxBase):
    """
    Bazowa klasa wszystkich modułów w Federacji

    Rozszerza LuxBase o:
    - Wersjonowanie
    - Typy modułów
    - Zarządzanie stanem
    - Eksperymentalne funkcje
    """

    def __init__(self, 
                 name: str,
                 module_type: ModuleType,
                 version: Union[ModuleVersion, str] = "1.0.0",
                 config: Optional[Dict[str, Any]] = None,
                 bus: Optional[FederationBus] = None,
                 parent_uuid: Optional[str] = None,
                 creator_id: Optional[str] = None,
                 form_type: ModuleFormType = ModuleFormType.FILE):

        super().__init__(parent_uuid=parent_uuid, creator_id=creator_id)

        # Podstawowe informacje o module
        self.name = name
        self.module_type = module_type
        self.version = version if isinstance(version, ModuleVersion) else ModuleVersion.from_string(version)
        self.config = config or {}
        self.bus = bus
        self.form_type = form_type

        # Stan modułu
        self.is_active = False
        self.is_initialized = False
        self.is_experimental = self.version.stability == ModuleStability.EXPERIMENTAL
        self.error_count = 0
        self.max_errors = self.config.get('max_errors', 5)

        # Manifest
        self.manifest = ModuleManifest(
            name=self.name,
            module_type=self.module_type,
            version=self.version,
            description=self.config.get('description', f'{self.name} module'),
            form_type=self.form_type,
            dependencies=self.config.get('dependencies', []),
            capabilities=self.config.get('capabilities', []),
            author=self.config.get('author'),
            license=self.config.get('license')
        )

        # Statystyki
        self.start_time: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.operations_count = 0

        # Lifecycle management dla modułów binarnych
        self.last_used: Optional[datetime] = None
        self.usage_count = 0
        self.auto_remove_after_seconds = config.get('auto_remove_after_seconds', 3600)  # 1 godzina domyślnie
        self.memory_lifecycle_active = False

        # Dodaj mutację o stworzeniu modułu
        self.add_mutation('module_created', {
            'name': self.name,
            'type': self.module_type.value,
            'version': str(self.version)
        })

    async def initialize(self) -> bool:
        """Inicjalizuje moduł - override w klasach potomnych"""
        try:
            self.is_initialized = True
            self.start_time = datetime.now()

            # Rejestruj w bus'ie jeśli dostępny
            if self.bus:
                self.bus.register_module(f"{self.name}_{self.uuid[:8]}", self)

            self.add_mutation('module_initialized', {
                'success': True,
                'timestamp': datetime.now().isoformat()
            })

            return True

        except Exception as e:
            self.record_error(f"Initialization failed: {str(e)}")
            return False

    async def start(self) -> bool:
        """Uruchamia moduł - wywoływane przez kernel"""
        try:
            if not self.is_initialized:
                await self.initialize()

            self.is_active = True

            self.add_mutation('module_started', {
                'success': True,
                'timestamp': datetime.now().isoformat()
            })

            return True

        except Exception as e:
            self.record_error(f"Start failed: {str(e)}")
            return False

    async def stop(self) -> bool:
        """Zatrzymuje moduł - wywoływane przez kernel"""
        return await self.shutdown()

    async def heartbeat(self) -> bool:
        """Wspólny puls życia - wywoływany regularnie przez kernel"""
        try:
            # Override w klasach potomnych dla custom logic
            if self.is_active:
                self.operations_count += 1
                return True
            return False

        except Exception as e:
            self.record_error(f"Heartbeat failed: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """Sprawdza zdrowie modułu"""
        try:
            # Podstawowy health check
            if not self.is_active or not self.is_initialized:
                return False

            # Sprawdź czy nie przekroczył limitu błędów
            if self.error_count >= self.max_errors:
                return False

            return True

        except Exception:
            return False

    async def shutdown(self) -> bool:
        """Wyłącza moduł - override w klasach potomnych"""
        try:
            self.is_active = False
            self.is_initialized = False

            self.add_mutation('module_shutdown', {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'uptime': self.get_uptime()
            })

            return True

        except Exception as e:
            self.record_error(f"Shutdown failed: {str(e)}")
            return False

    def record_error(self, error: str) -> None:
        """Zapisuje błąd modułu"""
        self.error_count += 1
        self.last_error = error

        self.add_mutation('module_error', {
            'error': error,
            'error_count': self.error_count,
            'timestamp': datetime.now().isoformat()
        })

        # Jeśli to moduł eksperymentalny i przekroczył limit błędów
        if self.is_experimental and self.error_count >= self.max_errors:
            self.add_mutation('experimental_fallback', {
                'reason': 'Too many errors',
                'error_count': self.error_count,
                'max_errors': self.max_errors
            })

    def mark_used(self) -> None:
        """Oznacza moduł jako używany - przedłuża lifecycle"""
        self.last_used = datetime.now()
        self.usage_count += 1

        # Dodaj mutację o użyciu
        self.add_mutation('module_used', {
            'usage_count': self.usage_count,
            'timestamp': self.last_used.isoformat()
        })

    def should_be_removed(self) -> bool:
        """Sprawdza czy moduł binarny powinien zostać usunięty z pamięci"""
        if self.form_type != ModuleFormType.BINARY:
            return False

        if not self.last_used:
            return False

        seconds_since_last_use = (datetime.now() - self.last_used).total_seconds()
        return seconds_since_last_use > self.auto_remove_after_seconds

    def extend_lifecycle(self, additional_seconds: int = 3600) -> None:
        """Przedłuża lifecycle modułu binarnego"""
        if self.form_type == ModuleFormType.BINARY and self.last_used:
            # Symuluje użycie aby przedłużyć lifecycle
            self.mark_used()

            self.add_mutation('lifecycle_extended', {
                'additional_seconds': additional_seconds,
                'new_expiry': (datetime.now() + timedelta(seconds=additional_seconds)).isoformat()
            })

    def start_memory_lifecycle(self) -> None:
        """Uruchamia lifecycle management w pamięci"""
        if self.form_type == ModuleFormType.BINARY:
            self.memory_lifecycle_active = True
            self.last_used = datetime.now()

            self.add_mutation('memory_lifecycle_started', {
                'auto_remove_after_seconds': self.auto_remove_after_seconds,
                'started_at': self.last_used.isoformat()
            })

    def should_fallback_to_stable(self) -> bool:
        """Sprawdza czy moduł eksperymentalny powinien ustąpić stabilnemu"""
        return self.is_experimental and self.error_count >= self.max_errors

    def get_uptime(self) -> Optional[float]:
        """Zwraca czas działania modułu w sekundach"""
        if not self.start_time:
            return None
        return (datetime.now() - self.start_time).total_seconds()

    def get_status(self) -> Dict[str, Any]:
        """Zwraca pełny status modułu"""
        status = {
            'uuid': self.uuid,
            'name': self.name,
            'type': self.module_type.value,
            'version': str(self.version),
            'form_type': self.form_type.value,
            'active': self.is_active,
            'initialized': self.is_initialized,
            'experimental': self.is_experimental,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'uptime': self.get_uptime(),
            'operations_count': self.operations_count,
            'created_at': self.created_at.isoformat(),
            'genetic_info': self.get_creation_info(),
            'usage_count': self.usage_count
        }

        # Dodaj lifecycle info dla modułów binarnych
        if self.form_type == ModuleFormType.BINARY:
            status.update({
                'last_used': self.last_used.isoformat() if self.last_used else None,
                'memory_lifecycle_active': self.memory_lifecycle_active,
                'auto_remove_after_seconds': self.auto_remove_after_seconds,
                'should_be_removed': self.should_be_removed(),
                'seconds_until_removal': self.get_seconds_until_removal()
            })

        return status

    def get_seconds_until_removal(self) -> Optional[int]:
        """Zwraca liczbę sekund do usunięcia z pamięci"""
        if self.form_type != ModuleFormType.BINARY or not self.last_used:
            return None

        seconds_since_last_use = (datetime.now() - self.last_used).total_seconds()
        remaining = self.auto_remove_after_seconds - seconds_since_last_use
        return max(0, int(remaining))

    def get_manifest(self) -> ModuleManifest:
        """Zwraca manifest modułu"""
        return self.manifest

    def serialize_to_binary(self) -> str:
        """Serializuje moduł do formatu binarnego (base64)"""
        module_data = {
            'uuid': self.uuid,
            'name': self.name,
            'module_type': self.module_type.value,
            'version': self.version.to_dict(),
            'config': self.config,
            'manifest': self.manifest.to_dict(),
            'genetic_record': self.genetic_record.to_dict(),
            'created_at': self.created_at.isoformat(),
            'class_name': self.__class__.__name__,
            'module_path': self.__class__.__module__,
            'form_type': self.form_type.value,
            'auto_remove_after_seconds': self.auto_remove_after_seconds
        }

        # Serializuj do pickle, potem base64
        pickled = pickle.dumps(module_data)
        return base64.b64encode(pickled).decode('utf-8')

    @classmethod
    def deserialize_from_binary(cls, binary_data: str, bus: Optional[FederationBus] = None) -> 'LuxModule':
        """Deserializuje moduł z formatu binarnego"""
        try:
            # Dekoduj base64, potem pickle
            pickled = base64.b64decode(binary_data.encode('utf-8'))
            module_data = pickle.loads(pickled)

            # Odtwórz moduł
            version = ModuleVersion(**module_data['version'])
            module_type = ModuleType(module_data['module_type'])
            form_type = ModuleFormType(module_data.get('form_type', ModuleFormType.BINARY.value))

            # Utwórz instancję
            module = cls(
                name=module_data['name'],
                module_type=module_type,
                version=version,
                config=module_data['config'],
                bus=bus,
                form_type=form_type
            )

            # Przywróć UUID i dane genetyczne
            module.uuid = module_data['uuid']
            module.created_at = datetime.fromisoformat(module_data['created_at'])

            # Przywróć lifecycle settings
            module.auto_remove_after_seconds = module_data.get('auto_remove_after_seconds', 3600)

            # Uruchom lifecycle dla modułów binarnych
            if form_type == ModuleFormType.BINARY:
                module.start_memory_lifecycle()

            return module

        except Exception as e:
            raise ValueError(f"Failed to deserialize module: {str(e)}")

    def get_type_info(self) -> Dict[str, Any]:
        """Zwraca informacje o typie modułu dla Brain"""
        return {
            'uuid': self.uuid,
            'name': self.name,
            'class_name': self.__class__.__name__,
            'module_type': self.module_type.value,
            'version': str(self.version),
            'stability': self.version.stability.value,
            'experimental': self.is_experimental,
            'form_type': self.form_type.value,
            'capabilities': self.manifest.capabilities,
            'dependencies': self.manifest.dependencies,
            'base_class': 'LuxModule',
            'inheritance_chain': [cls.__name__ for cls in self.__class__.__mro__]
        }

    def __str__(self) -> str:
        return f"LuxModule({self.name} v{self.version})"

    def __repr__(self) -> str:
        return f"LuxModule(name='{self.name}', type={self.module_type.value}, version='{self.version}', uuid='{self.uuid}')"
"""
🧬 LuxModule - Bazowa klasa wszystkich modułów w federacji

Każdy moduł dziedziczy po LuxBase i ma dodatkowe funkcjonalności modułowe
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .lux_base import LuxBase
from .bus import FederationBus


class ModuleType(Enum):
    """Typy modułów"""
    CORE = "core"              # Podstawowe moduły systemu
    REALM = "realm"            # Moduły wymiarów danych
    FLOW = "flow"              # Moduły przepływu danych
    INTELLIGENCE = "intelligence"  # Moduły inteligencji
    INTERFACE = "interface"    # Moduły interfejsów
    EXPERIMENTAL = "experimental"  # Moduły eksperymentalne
    PLUGIN = "plugin"          # Wtyczki
    SERVICE = "service"        # Usługi
    UTILITY = "utility"
    PERSONALITY = "personality"