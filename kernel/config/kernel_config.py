
"""
🔧 Kernel Config - Zarządzanie konfiguracją Kernela

Minimalna konfiguracja z fallback do wartości domyślnych
"""

import yaml
import os
from typing import Dict, Any
from pathlib import Path


class KernelConfig:
    """
    Konfiguracja Kernela
    
    Ładuje z pliku YAML lub używa wartości domyślnych
    """
    
    def __init__(self, config_path: str = "kernel/config/kernel.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Ładuje konfigurację z pliku lub tworzy domyślną"""
        
        # Domyślna konfiguracja
        default_config = {
            'logging': {
                'level': 'INFO',
                'format': 'console',
                'file': 'kernel/logs/kernel.log'
            },
            'resources': {
                'cpu_limit': 80,
                'memory_limit': 80,
                'thread_limit': 100,
                'monitoring_interval': 5
            },
            'cache': {
                'max_size': 1000,
                'ttl_seconds': 3600,
                'cleanup_interval': 300
            },
            'memory': {
                'max_context_size': 10000,
                'cleanup_threshold': 8000,
                'compression_enabled': True
            },
            'watchdog': {
                'mode': 'passive',  # passive, active, strict
                'check_interval': 10,
                'restart_threshold': 3,
                'component_timeout': 30
            },
            'updates': {
                'auto_check': True,
                'check_interval': 3600,
                'backup_enabled': True,
                'rollback_enabled': True
            },
            'safe_mode': {
                'auto_activate': True,
                'min_functionality': True,
                'recovery_timeout': 60
            }
        }
        
        # Spróbuj załadować z pliku
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f)
                
                # Merge z domyślną konfiguracją
                merged_config = self._merge_configs(default_config, file_config)
                return merged_config
                
            except Exception as e:
                print(f"⚠️ Error loading config from {self.config_path}: {e}")
                print("🔄 Using default configuration")
        
        # Utwórz plik konfiguracyjny jeśli nie istnieje
        self._create_default_config_file(default_config)
        
        return default_config
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merguje konfigurację załadowaną z domyślną"""
        merged = default.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _create_default_config_file(self, config: Dict[str, Any]):
        """Tworzy domyślny plik konfiguracyjny"""
        try:
            # Utwórz katalog jeśli nie istnieje
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            
            print(f"📝 Created default config file: {self.config_path}")
            
        except Exception as e:
            print(f"❌ Failed to create config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Pobiera wartość z konfiguracji"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Ustawia wartość w konfiguracji"""
        keys = key.split('.')
        config_ref = self.config
        
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        config_ref[keys[-1]] = value
    
    def save(self):
        """Zapisuje konfigurację do pliku"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return False
    
    def reload(self):
        """Przeładowuje konfigurację z pliku"""
        self.config = self._load_config()
    
    def to_dict(self) -> Dict[str, Any]:
        """Zwraca całą konfigurację jako słownik"""
        return self.config.copy()
