"""
⚙️ LuxDB v2 Configuration - Astralny System Konfiguracji

Zarządza konfiguracją wszystkich komponentów systemu astralnego
"""

import os
import json
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class FlowConfig:
    """Konfiguracja przepływu komunikacji"""
    host: str = "0.0.0.0"
    port: int = 5000
    enable_cors: bool = True
    max_connections: int = 1000
    timeout: int = 30


@dataclass
class WisdomConfig:
    """Konfiguracja modułu mądrości"""
    logging_level: str = "INFO"
    query_timeout: int = 30
    migration_backup: bool = True
    auto_optimize: bool = True


@dataclass
class AstralConfig:
    """
    Główna konfiguracja systemu astralnego LuxDB v2
    """

    # Podstawowe ustawienia
    consciousness_level: str = "enlightened"
    energy_conservation: bool = True
    auto_healing: bool = True
    meditation_interval: int = 60
    harmony_check_interval: int = 30
    consciousness_observation_interval: int = 15

    # Wymiary (realms)
    realms: Dict[str, str] = field(default_factory=lambda: {
        'primary': 'sqlite://db/astral.db'
    })

    # Przepływy (flows)
    flows: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'rest': {'host': '0.0.0.0', 'port': 5000, 'enable_cors': True},
        'websocket': {'host': '0.0.0.0', 'port': 5001, 'enable_cors': True},
        'callback': {'async_workers': 4, 'max_queue_size': 10000},
        'gpt': {
                'model': 'gpt-4',
                'max_tokens': 1000,
                'temperature': 0.7,
                'openai_api_key': None  # Pobrane z ENV
            }
    })

    # Mądrość (wisdom)
    wisdom: Dict[str, Any] = field(default_factory=lambda: {
        'logging_level': 'INFO',
        'query_timeout': 30,
        'migration_backup': True,
        'auto_optimize': True
    })

    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'AstralConfig':
        """
        Ładuje konfigurację z pliku

        Args:
            config_path: Ścieżka do pliku konfiguracyjnego

        Returns:
            Obiekt konfiguracji
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Plik konfiguracji nie istnieje: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() == '.json':
                data = json.load(f)
            else:
                raise ValueError("Obsługiwane są tylko pliki JSON")

        return cls(**data)

    @classmethod
    def from_env(cls, prefix: str = "LUXDB_") -> 'AstralConfig':
        """
        Ładuje konfigurację ze zmiennych środowiskowych

        Args:
            prefix: Prefiks zmiennych środowiskowych

        Returns:
            Obiekt konfiguracji
        """
        config_data = {}

        # Mapowanie zmiennych środowiskowych
        env_mapping = {
            f'{prefix}CONSCIOUSNESS_LEVEL': 'consciousness_level',
            f'{prefix}MEDITATION_INTERVAL': 'meditation_interval',
            f'{prefix}HARMONY_CHECK_INTERVAL': 'harmony_check_interval',
            f'{prefix}PRIMARY_REALM': ('realms', 'primary'),
            f'{prefix}REST_PORT': ('flows', 'rest', 'port'),
            f'{prefix}REST_HOST': ('flows', 'rest', 'host'),
            f'{prefix}WS_PORT': ('flows', 'websocket', 'port'),
            f'{prefix}LOG_LEVEL': ('wisdom', 'logging_level')
        }

        for env_var, config_path in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Konwertuj typy
                if env_var.endswith('_PORT') or env_var.endswith('_INTERVAL'):
                    value = int(value)
                elif env_var.endswith('_ENABLE') or value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'

                # Ustaw wartość w konfiguracji
                cls._set_nested_value(config_data, config_path, value)

        # Utwórz konfigurację z domyślnymi wartościami i nadpisz ze środowiska
        default_config = cls()
        default_dict = asdict(default_config)

        # Połącz z danymi ze środowiska
        cls._deep_merge(default_dict, config_data)

        return cls(**default_dict)

    @staticmethod
    def _set_nested_value(data: Dict, path: Union[str, tuple], value: Any) -> None:
        """Ustawia wartość w zagnieżdżonej strukturze"""
        if isinstance(path, str):
            data[path] = value
        else:
            current = data
            for key in path[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[path[-1]] = value

    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> None:
        """Głębokie łączenie słowników"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                AstralConfig._deep_merge(base[key], value)
            else:
                base[key] = value

    def to_file(self, config_path: Union[str, Path]) -> None:
        """
        Zapisuje konfigurację do pliku

        Args:
            config_path: Ścieżka do pliku konfiguracyjnego
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    def get_realm_config(self, realm_name: str) -> Optional[str]:
        """Zwraca konfigurację wymiaru"""
        return self.realms.get(realm_name)

    def get_flow_config(self, flow_name: str) -> Optional[Dict[str, Any]]:
        """Zwraca konfigurację przepływu"""
        return self.flows.get(flow_name)

    def get_wisdom_config(self, key: str, default: Any = None) -> Any:
        """Zwraca konfigurację mądrości"""
        return self.wisdom.get(key, default)

    def validate(self) -> List[str]:
        """
        Waliduje konfigurację

        Returns:
            Lista błędów walidacji (pusta jeśli wszystko OK)
        """
        errors = []

        # Sprawdź consciousness_level
        valid_levels = ['basic', 'aware', 'enlightened', 'transcendent']
        if self.consciousness_level not in valid_levels:
            errors.append(f"Nieprawidłowy poziom świadomości: {self.consciousness_level}. "
                         f"Dostępne: {valid_levels}")

        # Sprawdź interwały
        if self.meditation_interval <= 0:
            errors.append("Interwał medytacji musi być większy od 0")

        if self.harmony_check_interval <= 0:
            errors.append("Interwał sprawdzania harmonii musi być większy od 0")

        # Sprawdź wymiary
        if not self.realms:
            errors.append("Musisz zdefiniować przynajmniej jeden wymiar")

        for realm_name, realm_config in self.realms.items():
            if not isinstance(realm_config, str):
                errors.append(f"Konfiguracja wymiaru '{realm_name}' musi być stringiem")
            elif not self._is_valid_connection_string(realm_config):
                errors.append(f"Nieprawidłowy connection string dla wymiaru '{realm_name}': {realm_config}")

        # Sprawdź przepływy
        for flow_name, flow_config in self.flows.items():
            if not isinstance(flow_config, dict):
                errors.append(f"Konfiguracja przepływu '{flow_name}' musi być słownikiem")
            elif flow_name in ['rest', 'websocket']:
                if 'port' in flow_config:
                    port = flow_config['port']
                    if not isinstance(port, int) or port <= 0 or port > 65535:
                        errors.append(f"Nieprawidłowy port dla przepływu '{flow_name}': {port}")

        return errors

    def _is_valid_connection_string(self, connection_string: str) -> bool:
        """Sprawdza czy connection string jest prawidłowy"""
        valid_prefixes = ['sqlite://', 'postgresql://', 'memory://']
        return any(connection_string.startswith(prefix) for prefix in valid_prefixes)

    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje konfigurację na słownik"""
        return asdict(self)

    def __str__(self) -> str:
        return f"AstralConfig(consciousness_level='{self.consciousness_level}', " \
               f"realms={len(self.realms)}, flows={len(self.flows)})"


def load_config(
    config_file: Optional[Union[str, Path]] = None,
    env_prefix: str = "LUXDB_",
    use_env: bool = True
) -> AstralConfig:
    """
    Ładuje konfigurację z różnych źródeł

    Args:
        config_file: Ścieżka do pliku konfiguracyjnego
        env_prefix: Prefiks zmiennych środowiskowych
        use_env: Czy używać zmiennych środowiskowych

    Returns:
        Obiekt konfiguracji
    """
    if config_file and Path(config_file).exists():
        # Ładuj z pliku
        config = AstralConfig.from_file(config_file)
    elif use_env:
        # Ładuj ze zmiennych środowiskowych
        config = AstralConfig.from_env(env_prefix)
    else:
        # Użyj domyślnej konfiguracji
        config = AstralConfig()

    # Waliduj konfigurację
    errors = config.validate()
    if errors:
        error_msg = "Błędy konfiguracji:\n" + "\n".join(f"- {error}" for error in errors)
        raise ValueError(error_msg)

    return config


def create_default_config_file(config_path: Union[str, Path]) -> None:
    """
    Tworzy domyślny plik konfiguracyjny

    Args:
        config_path: Ścieżka do pliku konfiguracyjnego
    """
    default_config = AstralConfig()
    default_config.to_file(config_path)


# Globalna konfiguracja (lazy loading)
_global_config: Optional[AstralConfig] = None


def get_config() -> AstralConfig:
    """Zwraca globalną konfigurację"""
    global _global_config
    if _global_config is None:
        _global_config = load_config()
    return _global_config


def set_config(config: AstralConfig) -> None:
    """Ustawia globalną konfigurację"""
    global _global_config
    _global_config = config