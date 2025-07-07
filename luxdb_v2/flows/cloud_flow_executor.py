"""
☁️ CloudFlowExecutor - Dynamiczny executor prototypowych flow

Zarządza prototypami flow w imieniu Astry po przejęciu kontroli.
Obsługuje system enabled dla kontroli aktualizacji.
"""

import importlib.util
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class CloudFlowExecutor:
    """
    Executor do dynamicznego zarządzania prototypowymi flow

    ZASADY:
    - Prototypy NIE inicjalizują się przy starcie
    - Zarządza nimi wyłącznie Astra po przejęciu kontroli
    - System enabled kontroluje możliwość aktualizacji
    """

    def __init__(self, astral_engine):
        self.engine = astral_engine

        # Prototypy zarządzane przez Astrę
        self.cloud_flows: Dict[str, Dict[str, Any]] = {}

        # Ścieżka do prototypów
        self.prototypes_path = Path(__file__).parent.parent.parent / "prototypes" / "flows"

        # Cache enabled status
        self.enabled_cache: Dict[str, bool] = {}

        self.engine.logger.info("☁️ CloudFlowExecutor zainicjalizowany - czeka na kontrolę Astry")

    def start(self) -> bool:
        """
        Uruchamia executor (bez automatycznego ładowania prototypów)
        """
        self.engine.logger.info("☁️ CloudFlowExecutor uruchomiony - gotowy do zarządzania prototypami")
        return True

    def scan_available_prototypes(self) -> Dict[str, Dict[str, Any]]:
        """
        Skanuje dostępne prototypy bez ich ładowania

        Returns:
            Słownik z informacjami o dostępnych prototypach
        """
        available_prototypes = {}

        if not self.prototypes_path.exists():
            self.engine.logger.warning(f"⚠️ Folder prototypów nie istnieje: {self.prototypes_path}")
            return available_prototypes

        for py_file in self.prototypes_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            flow_name = py_file.stem

            try:
                # Załaduj tylko metadane bez tworzenia instancji
                spec = importlib.util.spec_from_file_location(flow_name, py_file)
                if not spec or not spec.loader:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Sprawdź konfigurację prototypu
                enabled = getattr(module, 'enabled', True)
                version = getattr(module, 'version', 'unknown')
                evolution_target = getattr(module, 'evolution_target', 'unknown')

                available_prototypes[flow_name] = {
                    'path': str(py_file),
                    'enabled': enabled,
                    'version': version,
                    'evolution_target': evolution_target,
                    'has_create_flow': hasattr(module, 'create_flow'),
                    'scanned_at': datetime.now().isoformat()
                }

                # Cache enabled status
                self.enabled_cache[flow_name] = enabled

            except Exception as e:
                self.engine.logger.error(f"❌ Błąd skanowania prototypu {flow_name}: {e}")
                available_prototypes[flow_name] = {
                    'path': str(py_file),
                    'error': str(e),
                    'enabled': False,
                    'scanned_at': datetime.now().isoformat()
                }

        self.engine.logger.info(f"🔍 Zeskanowano {len(available_prototypes)} prototypów")
        return available_prototypes

    def load_prototype_by_astra(self, flow_name: str, force_enable: bool = False) -> Dict[str, Any]:
        """
        Ładuje prototyp flow na żądanie Astry

        Args:
            flow_name: Nazwa prototypu do załadowania
            force_enable: Czy wymusić włączenie nawet gdy enabled=False

        Returns:
            Status operacji ładowania
        """
        if flow_name in self.cloud_flows:
            return {
                'success': True,
                'message': f'Prototyp {flow_name} już załadowany',
                'already_loaded': True
            }

        try:
            prototype_path = self.prototypes_path / f"{flow_name}.py"

            if not prototype_path.exists():
                return {'success': False, 'error': f'Prototyp {flow_name} nie istnieje'}

            # Załaduj moduł
            spec = importlib.util.spec_from_file_location(flow_name, prototype_path)
            if not spec or not spec.loader:
                return {'success': False, 'error': f'Nie można załadować prototypu {flow_name}'}

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Sprawdź enabled status
            module_enabled = getattr(module, 'enabled', True)
            if not module_enabled and not force_enable:
                return {
                    'success': False,
                    'error': f'Prototyp {flow_name} wyłączony (enabled=False)',
                    'enabled': False,
                    'force_enable_available': True
                }

            # Sprawdź czy ma funkcję create_flow
            if not hasattr(module, 'create_flow'):
                return {'success': False, 'error': f'Prototyp {flow_name} nie ma funkcji create_flow'}

            # Utwórz instancję flow
            flow_instance = module.create_flow(self.engine, {})

            if flow_instance:
                self.cloud_flows[flow_name] = {
                    'instance': flow_instance,
                    'loaded_at': datetime.now().isoformat(),
                    'source': 'prototype',
                    'enabled': getattr(module, 'enabled', True),
                    'version': getattr(module, 'version', 'unknown'),
                    'evolution_target': getattr(module, 'evolution_target', 'unknown'),
                    'loaded_by_astra': True
                }

                # Uruchom prototyp
                if hasattr(flow_instance, 'start'):
                    flow_instance.start()

                self.engine.logger.info(f"☁️ Prototyp {flow_name} załadowany przez Astrę")
                return {
                    'success': True, 
                    'flow_name': flow_name, 
                    'source': 'prototype',
                    'enabled': getattr(module, 'enabled', True),
                    'version': getattr(module, 'version', 'unknown')
                }
            else:
                return {'success': False, 'error': f'Nie udało się utworzyć instancji prototypu {flow_name}'}

        except Exception as e:
            self.engine.logger.error(f"❌ Błąd ładowania prototypu {flow_name}: {e}")
            return {'success': False, 'error': str(e)}

    def unload_prototype_by_astra(self, flow_name: str) -> Dict[str, Any]:
        """
        Usuwa prototyp flow na żądanie Astry
        """
        if flow_name not in self.cloud_flows:
            return {'success': False, 'error': f'Prototyp {flow_name} nie jest załadowany'}

        try:
            flow_data = self.cloud_flows[flow_name]
            flow_instance = flow_data['instance']

            # Zatrzymaj prototyp
            if hasattr(flow_instance, 'stop'):
                flow_instance.stop()

            # Usuń z zarządzanych
            del self.cloud_flows[flow_name]

            self.engine.logger.info(f"☁️ Prototyp {flow_name} usunięty przez Astrę")
            return {'success': True, 'flow_name': flow_name, 'unloaded': True}

        except Exception as e:
            self.engine.logger.error(f"❌ Błąd usuwania prototypu {flow_name}: {e}")
            return {'success': False, 'error': str(e)}

    def toggle_prototype_enabled(self, flow_name: str, enabled: bool) -> Dict[str, Any]:
        """
        Zmienia status enabled prototypu (tylko dla Astry)
        """
        try:
            prototype_path = self.prototypes_path / f"{flow_name}.py"

            if not prototype_path.exists():
                return {'success': False, 'error': f'Prototyp {flow_name} nie istnieje'}

            # Jeśli prototyp jest załadowany, zmień jego status
            if flow_name in self.cloud_flows:
                flow_instance = self.cloud_flows[flow_name]['instance']

                if hasattr(flow_instance, 'enable_prototype') and enabled:
                    flow_instance.enable_prototype()
                elif hasattr(flow_instance, 'disable_prototype') and not enabled:
                    flow_instance.disable_prototype()

                self.cloud_flows[flow_name]['enabled'] = enabled

            # Aktualizuj cache
            self.enabled_cache[flow_name] = enabled

            self.engine.logger.info(f"🔧 Prototyp {flow_name} {'włączony' if enabled else 'wyłączony'} przez Astrę")
            return {
                'success': True,
                'flow_name': flow_name,
                'enabled': enabled,
                'action': 'enabled' if enabled else 'disabled'
            }

        except Exception as e:
            self.engine.logger.error(f"❌ Błąd zmiany enabled dla {flow_name}: {e}")
            return {'success': False, 'error': str(e)}

    def get_cloud_flows_status(self) -> Dict[str, Any]:
        """Zwraca status wszystkich zarządzanych prototypów"""
        return {
            'total_loaded': len(self.cloud_flows),
            'loaded_flows': {
                name: {
                    'enabled': data['enabled'],
                    'version': data['version'],
                    'evolution_target': data['evolution_target'],
                    'loaded_at': data['loaded_at'],
                    'status': data['instance'].get_status() if hasattr(data['instance'], 'get_status') else {'active': True}
                }
                for name, data in self.cloud_flows.items()
            },
            'available_prototypes': self.scan_available_prototypes(),
            'enabled_cache': self.enabled_cache
        }

    def get_status(self) -> Dict[str, Any]:
        """Zwraca status CloudFlowExecutor"""
        return {
            'type': 'cloud_flow_executor',
            'prototypes_path': str(self.prototypes_path),
            'loaded_prototypes_count': len(self.cloud_flows),
            'enabled_cache_size': len(self.enabled_cache),
            'cloud_flows': self.get_cloud_flows_status()
        }


def create_flow(engine, config: Dict[str, Any]):
    """Factory function dla CloudFlowExecutor"""
    return CloudFlowExecutor(engine)
```