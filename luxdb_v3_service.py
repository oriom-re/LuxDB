
#!/usr/bin/env python3
"""
🚌 LuxDB v3 Service - Astralny System oparty na LuxBus

Nowa generacja serwisu z pełną integracją LuxBus Core
i możliwościami self-modification.
"""

import asyncio
import argparse
import signal
import sys
import os
from datetime import datetime

# Dodaj ścieżkę do modułów
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from luxdb_v2.core.luxbus_core import create_luxbus_core
from luxdb_v2.core.astral_engine_v3 import create_astral_engine_v3, quick_start_v3
from luxdb_v2.config import AstralConfig


class LuxDBv3Service:
    """
    Główny serwis LuxDB v3 - zarządza systemem astralnym opartym na LuxBus
    """
    
    def __init__(self, port: int = 5000):
        self.port = port
        self.engine = None
        self.luxbus = None
        self.running = False
        
        # Obsługa sygnałów
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    async def start(self):
        """Uruchamia serwis LuxDB v3"""
        try:
            print("🚌 Starting LuxDB v3 Service...")
            print(f"🌌 Initializing LuxBus Core...")
            
            # Utwórz LuxBus Core
            self.luxbus = create_luxbus_core(f"luxdb_v3_{datetime.now().strftime('%H%M%S')}")
            
            # Szybkie uruchomienie AstralEngine v3
            print(f"🔮 Starting AstralEngine v3...")
            self.engine = await quick_start_v3(
                realms={'primary': 'sqlite://db/luxdb_v3.db'},
                flows={
                    'rest': {'host': '0.0.0.0', 'port': self.port},
                    'websocket': {'host': '0.0.0.0', 'port': self.port + 1}
                }
            )
            
            self.running = True
            
            # Wyświetl status startowy
            self._print_startup_status()
            
            # Główna pętla serwisu
            await self._main_loop()
            
        except KeyboardInterrupt:
            print(f"\n⭐ Otrzymano sygnał przerwania...")
        except Exception as e:
            print(f"❌ Błąd podczas uruchamiania: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Zatrzymuje serwis"""
        if self.running:
            print(f"🕊️ Zatrzymywanie LuxDB v3 Service...")
            self.running = False
            
            if self.engine:
                try:
                    await self.engine.transcend()
                    print(f"✨ LuxDB v3 Service zatrzymany gracefully")
                except Exception as e:
                    print(f"⚠️ Błąd podczas zatrzymywania: {e}")
    
    def _print_startup_status(self):
        """Wyświetla status po uruchomieniu"""
        if not self.engine:
            return
        
        status = self.engine.get_status()
        luxbus_status = self.luxbus.get_status()
        
        print(f"\n{'='*70}")
        print(f"🚌 LuxDB v3 Service - Status Astralny")
        print(f"{'='*70}")
        print(f"🆔 Engine ID: {status['engine_id']}")
        print(f"🚌 LuxBus Node: {luxbus_status['node_id']}")
        print(f"⏱️ Uruchomiony: {status.get('awakened_at', 'Unknown')}")
        print(f"🌍 Realms: {', '.join(status['realms'])}")
        print(f"🌊 Flows: {', '.join(status['flows'])}")
        print(f"📦 Moduły LuxBus: {luxbus_status['modules']}")
        print(f"⚖️ Status: Running")
        print(f"{'='*70}")
        print(f"🌐 REST API: http://0.0.0.0:{self.port}")
        print(f"📡 WebSocket: ws://0.0.0.0:{self.port + 1}")
        print(f"💬 Terminal Chat: python luxdb_v2/terminal_chat.py")
        print(f"{'='*70}")
        print(f"💫 System astralny v3 gotowy do pracy!")
        print(f"   Naciśnij Ctrl+C aby zatrzymać...")
        print(f"{'='*70}\n")
    
    async def _main_loop(self):
        """Główna pętla serwisu"""
        last_status_time = asyncio.get_event_loop().time()
        status_interval = 300  # 5 minut
        
        while self.running:
            try:
                await asyncio.sleep(1)
                
                # Periodyczny status (co 5 minut)
                current_time = asyncio.get_event_loop().time()
                if current_time - last_status_time > status_interval:
                    await self._print_periodic_status()
                    last_status_time = current_time
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ Błąd w głównej pętli: {e}")
                await asyncio.sleep(5)
    
    async def _print_periodic_status(self):
        """Wyświetla periodyczny status"""
        if not self.engine:
            return
        
        try:
            meditation = self.engine.meditate()
            luxbus_stats = self.luxbus.get_status()
            
            print(f"📊 Status astralny v3 - "
                  f"Moduły: {len(luxbus_stats['modules'])}, "
                  f"Uptime: {meditation.get('uptime', 'unknown')}, "
                  f"LuxBus packets: {luxbus_stats.get('dispatcher_stats', {}).get('packets_processed', 0)}")
                  
        except Exception as e:
            print(f"⚠️ Błąd podczas pobierania statusu: {e}")
    
    def _signal_handler(self, signum, frame):
        """Obsługa sygnałów systemowych"""
        print(f"\n⭐ Otrzymano sygnał {signum}, zatrzymywanie...")
        self.running = False


async def main():
    """Główna funkcja"""
    parser = argparse.ArgumentParser(description='LuxDB v3 Service - Astralny System oparty na LuxBus')
    
    parser.add_argument('--port', '-p', type=int, default=5000,
                       help='Port dla REST API (domyślnie 5000)')
    parser.add_argument('--version', action='store_true',
                       help='Pokaż wersję')
    
    args = parser.parse_args()
    
    if args.version:
        print("LuxDB v3.0.0-luxbus - Astralna Biblioteka Danych z LuxBus Core")
        return
    
    # Uruchom serwis
    service = LuxDBv3Service(port=args.port)
    
    try:
        await service.start()
    except Exception as e:
        print(f"💥 Krytyczny błąd serwisu: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 LuxDB v3 Service stopped")
