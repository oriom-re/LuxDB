#!/usr/bin/env python3
"""
🧠 Kernel Manifest - Rdzeń Systemu LuxDB

Minimalny, niezależny moduł startowy systemu
Izolowany od zewnętrznych zależności, pasywny i odporny na awarie
"""

import asyncio
import signal
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Dodaj ścieżkę do kernela
sys.path.insert(0, str(Path(__file__).parent))

from core.event_bus import KernelEventBus
from core.resource_governor import ResourceGovernor
from core.watchdog import KernelWatchdog
from core.logger import KernelLogger
from core.function_cache import FunctionCache
from core.passive_update import PassiveUpdateManager
from memory.context_memory import ContextMemory
from fallback.safe_mode import SafeMode
from config.kernel_config import KernelConfig


class Kernel:
    """
    🧠 Rdzeń systemu LuxDB

    Minimalny, niezależny moduł startowy:
    - Inicjuje system i krytyczne moduły
    - Izolowany od zewnętrznych zależności
    - Pasywny i odporny na awarie
    - Zarządza zasobami i aktualizacjami
    """

    def __init__(self, config_path: Optional[str] = None):
        self.kernel_id = f"kernel_{datetime.now().strftime('%H%M%S')}"
        self.running = False
        self.safe_mode = False

        # Ładuj konfigurację
        self.config = KernelConfig(config_path or "kernel/config/kernel.yaml")

        # Logger jako pierwszy
        self.logger = KernelLogger(self.config.get('logging', {}))
        self.logger.info(f"🧠 Kernel initializing: {self.kernel_id}")

        # Wewnętrzny EventBus Kernela (izolowany)
        self.event_bus = KernelEventBus(self.logger)

        # Cache dla funkcji
        self.function_cache = FunctionCache(self.config.get('cache', {}))

        # Pamięć kontekstowa
        self.context_memory = ContextMemory(self.config.get('memory', {}))

        # Zarządca zasobów
        self.resource_governor = ResourceGovernor(
            self.config.get('resources', {}),
            self.logger
        )

        # Watchdog
        self.watchdog = KernelWatchdog(
            self.config.get('watchdog', {}),
            self.logger,
            self.event_bus
        )

        # Manager aktualizacji
        self.update_manager = PassiveUpdateManager(
            self.config.get('updates', {}),
            self.logger
        )

        # Tryb awaryjny
        self.safe_mode_manager = SafeMode(self.logger)

        # Obsługa sygnałów
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.logger.info("✅ Kernel core components initialized")

    async def start(self):
        """Uruchamia Kernel"""
        try:
            self.logger.info("🚀 Starting Kernel...")
            self.running = True

            # 1. Uruchom EventBus Kernela
            await self.event_bus.start()

            # 2. Uruchom Resource Governor
            await self.resource_governor.start()

            # 3. Uruchom Watchdog
            await self.watchdog.start()
            self.logger.info("🐕 Watchdog started")

            # 4. Sprawdź aktualizacje
            await self.update_manager.check_updates()

            # 5. Inicjuj pamięć kontekstową
            self.context_memory.initialize()
            self.logger.info("🧠 Context memory initialized")

            # 6. Uruchom główną pętlę
            await self._main_loop()

        except Exception as e:
            self.logger.error(f"❌ Critical error in Kernel: {e}")
            await self._enter_safe_mode()
        finally:
            await self.stop()

    async def stop(self):
        """Zatrzymuje Kernel"""
        if self.running:
            self.logger.info("🛑 Stopping Kernel...")
            self.running = False

            # Zatrzymaj komponenty w odwrotnej kolejności
            if hasattr(self, 'watchdog'):
                await self.watchdog.stop()

            if hasattr(self, 'resource_governor'):
                await self.resource_governor.stop()

            if hasattr(self, 'event_bus'):
                await self.event_bus.stop()

            self.logger.info("✨ Kernel stopped gracefully")

    async def _main_loop(self):
        """Główna pętla Kernela"""
        self.logger.info("🔄 Kernel main loop started")

        # Debug CPU measurement przy starcie
        if hasattr(self.resource_governor, 'debug_cpu_measurement'):
            await self.resource_governor.debug_cpu_measurement()

        # Główna pętla kernela
        while self.running:
            try:
                # Sprawdź stan systemu
                await self._health_check()

                # Przetwórz zdarzenia
                await self.event_bus.process_events()

                # Sprawdź zasoby
                resource_status = await self.resource_governor.check_resources()
                if resource_status.get('critical'):
                    self.logger.warning("⚠️ Critical resource usage detected")

                # Krótka przerwa
                await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in main loop: {e}")
                await asyncio.sleep(1)

    async def _health_check(self):
        """Sprawdza zdrowie systemu"""
        try:
            # Sprawdź komponenty
            components = {
                'event_bus': self.event_bus.is_healthy(),
                'resource_governor': await self.resource_governor.is_healthy(),
                'watchdog': self.watchdog.is_healthy(),
                'context_memory': self.context_memory.is_healthy()
            }

            # Jeśli któryś komponent jest niezdrowy
            unhealthy = [name for name, status in components.items() if not status]

            if unhealthy:
                self.logger.warning(f"⚠️ Unhealthy components: {unhealthy}")
                await self._handle_unhealthy_components(unhealthy)

        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")

    async def _handle_unhealthy_components(self, unhealthy: list):
        """Obsługuje niezdrowe komponenty"""
        for component in unhealthy:
            try:
                self.logger.info(f"🔧 Attempting to repair: {component}")

                if component == 'event_bus':
                    await self.event_bus.restart()
                elif component == 'resource_governor':
                    await self.resource_governor.restart()
                elif component == 'watchdog':
                    await self.watchdog.restart()
                elif component == 'context_memory':
                    self.context_memory.reset()

                self.logger.info(f"✅ Component repaired: {component}")

            except Exception as e:
                self.logger.error(f"❌ Failed to repair {component}: {e}")

    async def _enter_safe_mode(self):
        """Wchodzi w tryb awaryjny"""
        self.logger.critical("🚨 Entering Safe Mode")
        self.safe_mode = True

        try:
            await self.safe_mode_manager.activate()
            self.logger.info("🛡️ Safe Mode activated")

            # Minimalna funkcjonalność w trybie awaryjnym
            while self.safe_mode and self.running:
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.critical(f"💥 Safe Mode failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Zwraca status Kernela"""
        return {
            'kernel_id': self.kernel_id,
            'running': self.running,
            'safe_mode': self.safe_mode,
            'uptime': datetime.now().isoformat(),
            'components': {
                'event_bus': self.event_bus.is_healthy() if hasattr(self, 'event_bus') else False,
                'resource_governor': self.resource_governor.get_status() if hasattr(self, 'resource_governor') else {},
                'watchdog': self.watchdog.get_status() if hasattr(self, 'watchdog') else {},
                'context_memory': self.context_memory.get_status() if hasattr(self, 'context_memory') else {}
            }
        }

    def _signal_handler(self, signum, frame):
        """Obsługa sygnałów"""
        self.logger.info(f"📡 Signal {signum} received")
        self.running = False


async def main():
    """Główna funkcja uruchamiająca Kernel"""
    try:
        # Utwórz strukturę katalogów
        os.makedirs('kernel/config', exist_ok=True)
        os.makedirs('kernel/core', exist_ok=True)
        os.makedirs('kernel/memory', exist_ok=True)
        os.makedirs('kernel/fallback', exist_ok=True)

        # Uruchom Kernel
        kernel = Kernel()
        await kernel.start()

    except KeyboardInterrupt:
        print("\n⭐ Kernel stopped by user")
    except Exception as e:
        print(f"💥 Critical Kernel error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())