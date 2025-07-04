
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
    metadata: Dict[str, Any] = None


class FederationKernel:
    """
    Kernel Federacji - centralny zarządca systemu
    """
    
    def __init__(self, config: FederationConfig):
        self.config = config
        self.logger = FederationLogger(config.logger)
        self.bus = FederationBus()
        
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
            
            # Dynamiczny import modułu
            module_path = f"modules.{module_name}"
            module_class_name = module_config.get('class', f"{module_name.title()}Module")
            
            module_mod = __import__(module_path, fromlist=[module_class_name])
            module_class = getattr(module_mod, module_class_name)
            
            # Inicjalizuj moduł
            module_instance = module_class(
                bus=self.bus,
                config=module_config,
                logger=self.logger
            )
            
            # Uruchom moduł
            await module_instance.start()
            
            self.modules[module_name] = module_instance
            self.module_statuses[module_name] = ModuleStatus(
                name=module_name,
                status='active',
                loaded_at=datetime.now(),
                metadata=module_config
            )
            
            self.logger.info(f"📦 Module loaded: {module_name}")
            
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
        while self.running:
            try:
                # Sprawdź stan modułów
                await self._health_check()
                
                # Przetwórz wiadomości z bus'a
                await self.bus.process_messages()
                
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ Error in main loop: {e}")
                await asyncio.sleep(5)
    
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
