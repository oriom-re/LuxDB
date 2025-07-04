
#!/usr/bin/env python3
"""
🏛️ Federation Main - Punkt wejścia systemu federacyjnego

Uproszczona architektura oparta na kernel + bus + moduły
"""

import asyncio
import signal
import sys
from pathlib import Path

from core.kernel import FederationKernel
from core.config import FederationConfig


class Federation:
    """Główna klasa federacji"""
    
    def __init__(self):
        # Załaduj konfigurację
        config_path = Path("manifests/manifest.yaml")
        self.config = FederationConfig.from_manifest(config_path)
        
        # Utwórz kernel
        self.kernel = FederationKernel(self.config)
        
        # Obsługa sygnałów
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    async def start(self):
        """Uruchamia federację"""
        print("🏛️ Starting LuxDB Federation...")
        
        try:
            await self.kernel.start()
        except KeyboardInterrupt:
            print("\n⭐ Otrzymano sygnał przerwania...")
        except Exception as e:
            print(f"❌ Błąd federacji: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Zatrzymuje federację"""
        print("🕊️ Zatrzymywanie federacji...")
        await self.kernel.stop()
        print("✨ Federacja zatrzymana")
    
    def _signal_handler(self, signum, frame):
        """Obsługa sygnałów"""
        print(f"\n⭐ Otrzymano sygnał {signum}")
        # Asyncio będzie obsługiwało KeyboardInterrupt


async def main():
    """Główna funkcja"""
    federation = Federation()
    await federation.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Federation stopped")
