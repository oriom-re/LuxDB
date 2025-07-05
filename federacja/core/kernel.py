
"""
🏛️ Federation Kernel - Centralny Zarządca Federacji

Główny koordynator wszystkich modułów i przepływów
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from .bus import FederationBus
from .config import FederationConfig
from .logger import FederationLogger


@dataclass
class ModuleStatus:
    """Status modułu federacji"""
    name: str
    status: str  # 'loading', 'active', 'error', 'stopped'
    loaded_at: Optional[datetime] = None
    error: Optional[str] = None
    meta_data: Dict[str, Any] = None


class FederationKernel:
    """
    Kernel Federacji - centralny zarządca systemu
    """
    
    def __init__(self, config: FederationConfig):
        self.config = config
        self.logger = FederationLogger(config.logger)
        self.bus = FederationBus(self.logger)
        
        self.session_id = f"federation_{uuid.uuid4().hex[:8]}"
        self.modules: Dict[str, Any] = {}
        self.module_statuses: Dict[str, ModuleStatus] = {}
        self.running = False
        
        self.logger.info(f"🏛️ Federation Kernel initialized: {self.session_id}")
    
    async def start(self):
        """Uruchamia kernel federacji"""
        self.logger.info("🚀 Starting Federation Kernel...")
        
        # 1. Uruchom bus
        await self.bus.start()
        
        # 2. Załaduj moduły z manifestu
        await self._load_modules_from_manifest()
        
        # 3. Uruchom główną pętlę
        self.running = True
        await self._main_loop()
    
    async def stop(self):
        """Zatrzymuje kernel"""
        self.logger.info("🛑 Stopping Federation Kernel...")
        self.running = False
        
        # Zatrzymaj wszystkie moduły
        for module_name, module in self.modules.items():
            await self._stop_module(module_name, module)
        
        await self.bus.stop()
        self.logger.info("✅ Federation Kernel stopped")
    
    async def _load_modules_from_manifest(self):
        """Ładuje moduły z manifestu"""
        manifest_path = self.config.manifest_path
        
        try:
            import yaml
            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f)
            
            modules_config = manifest.get('modules', {})
            
            for module_name, module_config in modules_config.items():
                if module_config.get('enabled', True):
                    await self._load_module(module_name, module_config)
                    
        except Exception as e:
            self.logger.error(f"❌ Error loading manifest: {e}")
    
    async def _load_module(self, module_name: str, module_config: Dict[str, Any]):
        """Ładuje pojedynczy moduł"""
        try:
            self.module_statuses[module_name] = ModuleStatus(
                name=module_name,
                status='loading'
            )
            
            # Sprawdź czy to moduł statyczny
            is_static = module_config.get('static_startup', False)
            
            if not is_static:
                # Moduły niestatyczne są zarządzane przez Federę
                self.module_statuses[module_name] = ModuleStatus(
                    name=module_name,
                    status='managed_by_federa',
                    meta_data={'managed_by': 'federa', 'static_startup': False}
                )
                self.logger.info(f"📋 Module {module_name} - zarządzany przez Federę")
                return
            
            # Dynamiczny import modułu (obsługa zagnieżdżonych pakietów)
            module_path = f"federacja.modules.{module_name}"
            module_class_name = module_config.get('class', f"{module_name.split('.')[-1].title()}Module")
            
            module_mod = __import__(module_path, fromlist=[module_class_name])
            module_class = getattr(module_mod, module_class_name)
            
            # Inicjalizuj moduł statyczny
            module_instance = module_class(
                config=module_config, 
                bus=self.bus,
                name=module_name
            )
            
            # Uruchom moduł
            if hasattr(module_instance, 'initialize'):
                success = await module_instance.initialize()
            else:
                success = await module_instance.start()
            
            if success:
                self.modules[module_name] = module_instance
                self.module_statuses[module_name] = ModuleStatus(
                    name=module_name,
                    status='active',
                    loaded_at=datetime.now(),
                    meta_data={'static_startup': True}
                )
                
                self.logger.info(f"📦 Module loaded statically: {module_name}")
            else:
                self.module_statuses[module_name] = ModuleStatus(
                    name=module_name,
                    status='error',
                    error="Failed to start"
                )
                self.logger.error(f"❌ Static module failed to load: {module_name}")
                
        except Exception as e:
            self.module_statuses[module_name] = ModuleStatus(
                name=module_name,
                status='error',
                error=str(e)
            )
            self.logger.error(f"❌ Error loading module {module_name}: {e}")
    
    async def _stop_module(self, module_name: str, module: Any):
        """Zatrzymuje moduł"""
        try:
            if hasattr(module, 'stop'):
                await module.stop()
            self.module_statuses[module_name].status = 'stopped'
            self.logger.info(f"🛑 Module stopped: {module_name}")
        except Exception as e:
            self.logger.error(f"❌ Error stopping module {module_name}: {e}")
    
    async def _main_loop(self):
        """Główna pętla kernela"""
        heartbeat_interval = 2  # 2 sekundy
        health_check_interval = 10  # 10 sekund
        last_health_check = 0
        
        while self.running:
            try:
                current_time = asyncio.get_event_loop().time()
                
                # Wyślij heartbeat do wszystkich modułów
                await self._send_heartbeat()
                
                # Sprawdź stan modułów co 10 sekund
                if current_time - last_health_check >= health_check_interval:
                    await self._health_check()
                    last_health_check = current_time
                
                # Przetwórz wiadomości z bus'a
                await self.bus.process_messages()
                
                await asyncio.sleep(heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Error in main loop: {e}")
                await asyncio.sleep(5)
    
    async def _send_heartbeat(self):
        """Wysyła puls życia do wszystkich aktywnych modułów"""
        for module_name, module in self.modules.items():
            try:
                if hasattr(module, 'heartbeat'):
                    is_alive = await module.heartbeat()
                    if not is_alive:
                        self.logger.warning(f"💓 Module {module_name} heartbeat failed")
                        
            except Exception as e:
                self.logger.error(f"❌ Heartbeat error for {module_name}: {e}")
    
    async def _health_check(self):
        """Sprawdza stan wszystkich modułów"""
        for module_name, module in self.modules.items():
            if hasattr(module, 'health_check'):
                try:
                    is_healthy = await module.health_check()
                    if not is_healthy:
                        self.logger.warning(f"⚠️ Module unhealthy: {module_name}")
                except Exception as e:
                    self.logger.error(f"❌ Health check failed for {module_name}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status kernela"""
        return {
            'session_id': self.session_id,
            'running': self.running,
            'modules': {name: status.__dict__ for name, status in self.module_statuses.items()},
            'bus_status': self.bus.get_status()
        }
code = """
try:
    import math
except ImportError:
    print("Brak modułu math")
def calc():
    return math.sqrt(16)
result = calc()
"""

async def tasks():
    task = asyncio.get