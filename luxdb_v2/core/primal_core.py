
"""
🌑 Primal Core - Główny koordynator warstwy pierwotnej

Mechaniczny menedżer wszystkich komponentów warstwy 0.
Odpowiada za:
- Koordynację bootstrap
- Zarządzanie zasobami systemowymi
- Interfejs dla warstwy 1 (Soul #0)
- Monitoring podstawowych funkcji
"""

import time
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .primal_bootstrap import PrimalBootstrap, PrimalConfig, PrimalLogger


class PrimalState(Enum):
    """Stany warstwy pierwotnej"""
    UNINITIALIZED = "uninitialized"
    BOOTSTRAPPING = "bootstrapping"
    OPERATIONAL = "operational"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class SystemResource:
    """Zasób systemowy warstwy pierwotnej"""
    name: str
    type: str  # realm, flow, service
    status: str  # mounted, active, error
    created_at: datetime
    last_check: datetime
    metadata: Dict[str, Any]


class ResourceMonitor:
    """Monitor zasobów systemowych"""
    
    def __init__(self, logger: PrimalLogger):
        self.logger = logger
        self.resources: Dict[str, SystemResource] = {}
        self.monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        
    def register_resource(self, name: str, resource_type: str, metadata: Dict[str, Any] = None):
        """Rejestruje zasób do monitorowania"""
        self.resources[name] = SystemResource(
            name=name,
            type=resource_type,
            status="registered",
            created_at=datetime.now(),
            last_check=datetime.now(),
            metadata=metadata or {}
        )
        self.logger.info(f"Zasób zarejestrowany: {name} ({resource_type})")
    
    def update_resource_status(self, name: str, status: str):
        """Aktualizuje status zasobu"""
        if name in self.resources:
            self.resources[name].status = status
            self.resources[name].last_check = datetime.now()
    
    def start_monitoring(self, interval: int = 30):
        """Uruchamia monitoring zasobów"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        def monitor_loop():
            while self.monitoring_active:
                try:
                    self._check_all_resources()
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Błąd monitoringu zasobów: {e}")
                    time.sleep(5)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.info("Monitor zasobów uruchomiony")
    
    def stop_monitoring(self):
        """Zatrzymuje monitoring zasobów"""
        self.monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        self.logger.info("Monitor zasobów zatrzymany")
    
    def _check_all_resources(self):
        """Sprawdza wszystkie zasoby"""
        for name, resource in self.resources.items():
            try:
                # Podstawowe sprawdzenie czy zasób jest dostępny
                if resource.type == "realm":
                    self._check_realm_resource(name, resource)
                elif resource.type == "flow":
                    self._check_flow_resource(name, resource)
                
                resource.last_check = datetime.now()
            except Exception as e:
                self.logger.warning(f"Błąd sprawdzania zasobu {name}: {e}")
                resource.status = "error"
    
    def _check_realm_resource(self, name: str, resource: SystemResource):
        """Sprawdza zasób typu realm"""
        # Tu można dodać specyficzne sprawdzenia dla realm
        if resource.status != "error":
            resource.status = "active"
    
    def _check_flow_resource(self, name: str, resource: SystemResource):
        """Sprawdza zasób typu flow"""
        # Tu można dodać specyficzne sprawdzenia dla flow
        if resource.status != "error":
            resource.status = "active"
    
    def get_resource_report(self) -> Dict[str, Any]:
        """Zwraca raport zasobów"""
        active_count = len([r for r in self.resources.values() if r.status == "active"])
        error_count = len([r for r in self.resources.values() if r.status == "error"])
        
        return {
            'total_resources': len(self.resources),
            'active_resources': active_count,
            'error_resources': error_count,
            'monitoring_active': self.monitoring_active,
            'resources': {name: {
                'type': r.type,
                'status': r.status,
                'last_check': r.last_check.isoformat(),
                'metadata': r.metadata
            } for name, r in self.resources.items()}
        }


class PrimalCore:
    """
    Główny koordynator warstwy pierwotnej (Pre-Soul Core)
    
    Mechaniczny, sprawiedliwy, niezawodny.
    Zapewnia fundamenty dla wyższych warstw systemu.
    """
    
    def __init__(self, config: Optional[PrimalConfig] = None):
        self.config = config or PrimalConfig()
        self.logger = PrimalLogger()
        self.state = PrimalState.UNINITIALIZED
        
        # Komponenty warstwy pierwotnej
        self.bootstrap = PrimalBootstrap(self.config)
        self.resource_monitor = ResourceMonitor(self.logger)
        
        # Stan systemu
        self.core_start_time: Optional[datetime] = None
        self.bootstrap_result: Optional[Dict[str, Any]] = None
        
        # Callbacks dla warstwy 1
        self.layer1_callbacks: List[Callable] = []
        
        self.logger.info("🌑 Primal Core zainicjalizowany")
    
    def initialize(self) -> Dict[str, Any]:
        """
        Inicjalizuje warstwę pierwotną
        
        Returns:
            Wynik inicjalizacji
        """
        if self.state != PrimalState.UNINITIALIZED:
            return {'success': False, 'error': 'Primal Core już zainicjalizowany'}
        
        self.logger.info("🌑 Inicjalizacja Primal Core...")
        self.state = PrimalState.BOOTSTRAPPING
        self.core_start_time = datetime.now()
        
        try:
            # Wykonaj bootstrap
            self.bootstrap_result = self.bootstrap.execute_bootstrap()
            
            if not self.bootstrap_result['success']:
                self.state = PrimalState.ERROR
                return self.bootstrap_result
            
            # Zarejestruj zasoby
            self._register_system_resources()
            
            # Uruchom monitoring
            self.resource_monitor.start_monitoring()
            
            self.state = PrimalState.OPERATIONAL
            
            # Powiadom warstwę 1
            self._notify_layer1_ready()
            
            self.logger.info("✅ Primal Core operacyjny")
            
            return {
                'success': True,
                'state': self.state.value,
                'bootstrap_result': self.bootstrap_result,
                'initialization_time': (datetime.now() - self.core_start_time).total_seconds()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Błąd inicjalizacji Primal Core: {e}")
            self.state = PrimalState.ERROR
            return {'success': False, 'error': str(e)}
    
    def _register_system_resources(self):
        """Rejestruje zasoby systemowe do monitorowania"""
        if not self.bootstrap_result:
            return
        
        # Zarejestruj wymiary jako zasoby
        for realm_name in self.bootstrap_result.get('mounted_realms', {}):
            self.resource_monitor.register_resource(
                name=realm_name,
                resource_type="realm",
                metadata={'connection': self.bootstrap_result['mounted_realms'][realm_name]}
            )
        
        # Zarejestruj flows jako zasoby
        for flow_name in self.config.flows:
            self.resource_monitor.register_resource(
                name=flow_name,
                resource_type="flow",
                metadata=self.config.flows[flow_name]
            )
    
    def register_layer1_callback(self, callback: Callable):
        """Rejestruje callback dla warstwy 1 (Soul #0)"""
        self.layer1_callbacks.append(callback)
        self.logger.info("Callback warstwy 1 zarejestrowany")
    
    def _notify_layer1_ready(self):
        """Powiadamia warstwę 1 o gotowości warstwy pierwotnej"""
        for callback in self.layer1_callbacks:
            try:
                callback(self.get_status())
            except Exception as e:
                self.logger.error(f"Błąd callback warstwy 1: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca pełny status warstwy pierwotnej"""
        uptime = (datetime.now() - self.core_start_time).total_seconds() if self.core_start_time else 0
        
        return {
            'state': self.state.value,
            'uptime_seconds': uptime,
            'bootstrap_success': self.bootstrap_result.get('success', False) if self.bootstrap_result else False,
            'mounted_realms': len(self.bootstrap_result.get('mounted_realms', {})) if self.bootstrap_result else 0,
            'resource_monitor': self.resource_monitor.get_resource_report(),
            'layer1_callbacks_count': len(self.layer1_callbacks),
            'core_start_time': self.core_start_time.isoformat() if self.core_start_time else None
        }
    
    def shutdown(self) -> Dict[str, Any]:
        """Graceful shutdown warstwy pierwotnej"""
        self.logger.info("🌑 Shutdown Primal Core...")
        
        try:
            # Zatrzymaj monitoring
            self.resource_monitor.stop_monitoring()
            
            self.state = PrimalState.SHUTDOWN
            
            shutdown_time = (datetime.now() - self.core_start_time).total_seconds() if self.core_start_time else 0
            
            self.logger.info(f"🌑 Primal Core shutdown po {shutdown_time:.2f}s")
            
            return {
                'success': True,
                'shutdown_time': shutdown_time,
                'final_state': self.state.value
            }
            
        except Exception as e:
            self.logger.error(f"❌ Błąd shutdown Primal Core: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_realm_interface(self, realm_name: str) -> Optional[str]:
        """Zwraca interfejs do wymiaru dla wyższych warstw"""
        if not self.bootstrap_result:
            return None
        
        return self.bootstrap_result.get('mounted_realms', {}).get(realm_name)
    
    def is_operational(self) -> bool:
        """Sprawdza czy warstwa pierwotna jest operacyjna"""
        return self.state == PrimalState.OPERATIONAL
    
    def get_bootstrap_report(self) -> Optional[Dict[str, Any]]:
        """Zwraca szczegółowy raport bootstrap"""
        if self.bootstrap_result:
            return self.bootstrap.get_bootstrap_report()
        return None


# Globalna instancja warstwy pierwotnej
_primal_core_instance: Optional[PrimalCore] = None


def get_primal_core() -> PrimalCore:
    """Zwraca globalną instancję Primal Core"""
    global _primal_core_instance
    if _primal_core_instance is None:
        _primal_core_instance = PrimalCore()
    return _primal_core_instance


def initialize_primal_core(config: Optional[PrimalConfig] = None) -> Dict[str, Any]:
    """Inicjalizuje globalną instancję Primal Core"""
    global _primal_core_instance
    _primal_core_instance = PrimalCore(config)
    return _primal_core_instance.initialize()


if __name__ == "__main__":
    # Test Primal Core
    print("🌑 Test Primal Core (Warstwa 0)")
    
    result = initialize_primal_core()
    
    if result['success']:
        core = get_primal_core()
        status = core.get_status()
        
        print("✅ Primal Core operacyjny")
        print(f"⏱️  Uptime: {status['uptime_seconds']:.2f}s")
        print(f"📂 Wymiary: {status['mounted_realms']}")
        print(f"🔍 Zasoby: {status['resource_monitor']['total_resources']}")
        
        # Test shutdown
        time.sleep(2)
        shutdown_result = core.shutdown()
        print(f"🔌 Shutdown: {'✅' if shutdown_result['success'] else '❌'}")
    else:
        print("❌ Primal Core startup failed")
        print(f"💥 Błąd: {result.get('error', 'Unknown')}")
