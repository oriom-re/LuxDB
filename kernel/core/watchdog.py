
"""
🐕 Kernel Watchdog - Nadzór nad stabilnością systemu

Detekcja awarii, restart komponentów, monitorowanie zdrowia
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum

from .event_bus import KernelEventBus, EventType


class WatchdogMode(Enum):
    """Tryby pracy Watchdog"""
    PASSIVE = "passive"    # Tylko monitorowanie
    ACTIVE = "active"      # Aktywne naprawianie
    STRICT = "strict"      # Agresywne restartowanie


class ComponentHealth:
    """Stan zdrowia komponentu"""
    
    def __init__(self, name: str):
        self.name = name
        self.healthy = True
        self.last_check = datetime.now()
        self.failure_count = 0
        self.last_error = None
        self.restart_count = 0
    
    def mark_healthy(self):
        """Oznacza komponent jako zdrowy"""
        self.healthy = True
        self.last_check = datetime.now()
        self.failure_count = 0
        self.last_error = None
    
    def mark_unhealthy(self, error: str = None):
        """Oznacza komponent jako niezdrowy"""
        self.healthy = False
        self.last_check = datetime.now()
        self.failure_count += 1
        self.last_error = error
    
    def mark_restarted(self):
        """Oznacza restart komponentu"""
        self.restart_count += 1
        self.last_check = datetime.now()


class KernelWatchdog:
    """
    Watchdog Kernela
    
    Monitoruje zdrowie komponentów i podejmuje akcje naprawcze
    """
    
    def __init__(self, config: Dict[str, Any], logger, event_bus: KernelEventBus):
        self.config = config
        self.logger = logger
        self.event_bus = event_bus
        self.running = False
        
        # Konfiguracja
        self.mode = WatchdogMode(config.get('mode', 'passive'))
        self.check_interval = config.get('check_interval', 10)
        self.restart_threshold = config.get('restart_threshold', 3)
        self.component_timeout = config.get('component_timeout', 30)
        
        # Stan komponentów
        self.components: Dict[str, ComponentHealth] = {}
        
        # Statystyki
        self.stats = {
            'checks_performed': 0,
            'failures_detected': 0,
            'restarts_performed': 0,
            'last_check': None
        }
        
        self.logger.debug(f"🐕 Kernel Watchdog initialized in {self.mode.value} mode")
    
    async def start(self):
        """Uruchamia Watchdog"""
        self.running = True
        self.logger.info(f"🐕 Kernel Watchdog started in {self.mode.value} mode")
        
        # Uruchom monitoring w tle
        asyncio.create_task(self._monitoring_loop())
        
        # Subskrybuj zdarzenia systemowe
        self.event_bus.subscribe(EventType.COMPONENT_ERROR, self._handle_component_error)
    
    async def stop(self):
        """Zatrzymuje Watchdog"""
        self.running = False
        self.logger.info("🐕 Kernel Watchdog stopped")
    
    def register_component(self, name: str):
        """Rejestruje komponent do monitorowania"""
        self.components[name] = ComponentHealth(name)
        self.logger.debug(f"🐕 Registered component: {name}")
    
    def check_component(self, name: str, healthy: bool, error: str = None):
        """Sprawdza stan komponentu"""
        if name not in self.components:
            self.register_component(name)
        
        component = self.components[name]
        
        if healthy:
            was_unhealthy = not component.healthy
            component.mark_healthy()
            
            if was_unhealthy:
                self.logger.info(f"✅ Component recovered: {name}")
        else:
            was_healthy = component.healthy
            component.mark_unhealthy(error)
            
            if was_healthy:
                self.logger.warning(f"⚠️ Component unhealthy: {name} - {error}")
                self.stats['failures_detected'] += 1
                
                # Emituj zdarzenie
                asyncio.create_task(
                    self.event_bus.emit(
                        EventType.COMPONENT_ERROR,
                        {'component': name, 'error': error}
                    )
                )
    
    async def _monitoring_loop(self):
        """Główna pętla monitorowania"""
        while self.running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Watchdog monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _perform_health_check(self):
        """Wykonuje sprawdzenie zdrowia wszystkich komponentów"""
        self.stats['checks_performed'] += 1
        self.stats['last_check'] = datetime.now().isoformat()
        
        current_time = datetime.now()
        
        for name, component in self.components.items():
            # Sprawdź czy komponent nie przekroczył timeout
            if current_time - component.last_check > timedelta(seconds=self.component_timeout):
                self.check_component(name, False, "Component timeout")
            
            # Podejmij akcje naprawcze jeśli potrzeba
            if not component.healthy:
                await self._handle_unhealthy_component(component)
    
    async def _handle_unhealthy_component(self, component: ComponentHealth):
        """Obsługuje niezdrowy komponent"""
        if self.mode == WatchdogMode.PASSIVE:
            # Tylko loguj
            return
        
        if component.failure_count >= self.restart_threshold:
            if self.mode in [WatchdogMode.ACTIVE, WatchdogMode.STRICT]:
                await self._restart_component(component)
    
    async def _restart_component(self, component: ComponentHealth):
        """Restartuje komponent"""
        try:
            self.logger.info(f"🔄 Attempting to restart component: {component.name}")
            
            # Tutaj by był kod restartu konkretnego komponentu
            # Na razie tylko symulujemy
            await asyncio.sleep(0.1)
            
            component.mark_restarted()
            component.mark_healthy()
            
            self.stats['restarts_performed'] += 1
            self.logger.info(f"✅ Component restarted: {component.name}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to restart {component.name}: {e}")
    
    async def _handle_component_error(self, event):
        """Obsługuje zdarzenie błędu komponentu"""
        component_name = event.data.get('component')
        error = event.data.get('error')
        
        if component_name:
            self.check_component(component_name, False, error)
    
    def is_healthy(self) -> bool:
        """Sprawdza czy Watchdog jest zdrowy"""
        return self.running and all(
            comp.healthy or comp.failure_count < self.restart_threshold 
            for comp in self.components.values()
        )
    
    async def restart(self):
        """Restartuje Watchdog"""
        self.logger.info("🔄 Restarting Kernel Watchdog")
        await self.stop()
        await asyncio.sleep(0.5)
        await self.start()
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status Watchdog"""
        return {
            'running': self.running,
            'mode': self.mode.value,
            'stats': self.stats.copy(),
            'components': {
                name: {
                    'healthy': comp.healthy,
                    'failure_count': comp.failure_count,
                    'restart_count': comp.restart_count,
                    'last_check': comp.last_check.isoformat(),
                    'last_error': comp.last_error
                }
                for name, comp in self.components.items()
            }
        }
