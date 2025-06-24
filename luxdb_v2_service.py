
#!/usr/bin/env python3
"""
🌟 LuxDB v2 Service - Czysty Astralny Serwis

Nowa generacja serwisu LuxDB - elegancka, szybka, intuicyjna.
Uruchamia pełny stack LuxDB v2 w jednym, harmonijnym procesie.
"""

import os
import sys
import argparse
import signal
import time
import json
from typing import Optional
from pathlib import Path

# Dodaj ścieżkę do v2 jeśli jeszcze nie istnieje
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_v2_structure():
    """Tworzy podstawową strukturę LuxDB v2"""
    directories = [
        'luxdb_v2/core',
        'luxdb_v2/realms', 
        'luxdb_v2/beings',
        'luxdb_v2/flows',
        'luxdb_v2/wisdom',
        'luxdb_v2/migration',
        'luxdb_v2/tests',
        'db'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # Utwórz __init__.py w każdym module
        if directory.startswith('luxdb_v2/'):
            init_file = os.path.join(directory, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'"""LuxDB v2 - {directory.split("/")[-1]} module"""\n')


# Import LuxDB v2
try:
    from luxdb_v2 import (
        AstralEngine, 
        AstralConfig, 
        quick_start, 
        print_astral_banner,
        create_astral_app
    )
except ImportError as e:
    print(f"❌ Błąd importu LuxDB v2: {e}")
    print("🔧 Upewnij się, że zainstalowałeś psutil: uv add psutil")
    sys.exit(1)


class LuxDBv2Service:
    """
    Główny serwis LuxDB v2 - zarządza cyklem życia systemu astralnego
    """
    
    def __init__(self, config_file: Optional[str] = None, port: int = 5000, realm_type: str = 'sqlite'):
        self.config_file = config_file
        self.port = port
        self.realm_type = realm_type
        self.engine: Optional[AstralEngine] = None
        self._running = False
        
        # Ustawienia sygnałów
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def start(self):
        """Uruchamia serwis astralny"""
        try:
            print_astral_banner()
            print(f"🚀 Uruchamianie LuxDB v2 Service...")
            
            # Ładuj konfigurację
            config = self._load_config()
            
            # Utwórz silnik astralny
            if config:
                self.engine = create_astral_app(config)
            else:
                self.engine = quick_start(realm_type=self.realm_type, port=self.port)
            
            self._running = True
            
            # Uruchom przepływy
            print(f"🌊 Uruchamianie przepływów na porcie {self.port}...")
            self.engine.start_flows(debug=False)
            
            # Status systemu
            self._print_startup_status()
            
            # Główna pętla serwisu
            self._main_loop()
            
        except KeyboardInterrupt:
            print(f"\n⭐ Otrzymano sygnał przerwania...")
        except Exception as e:
            print(f"❌ Błąd podczas uruchamiania serwisu: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Zatrzymuje serwis astralny"""
        if self._running:
            print(f"🕊️ Zatrzymywanie LuxDB v2 Service...")
            self._running = False
            
            if self.engine:
                try:
                    self.engine.transcend()
                    print(f"✨ LuxDB v2 Service zatrzymany gracefully")
                except Exception as e:
                    print(f"⚠️ Błąd podczas zatrzymywania: {e}")
    
    def _load_config(self) -> Optional[AstralConfig]:
        """Ładuje konfigurację serwisu"""
        if self.config_file and Path(self.config_file).exists():
            try:
                print(f"📋 Ładowanie konfiguracji z: {self.config_file}")
                return AstralConfig.from_file(self.config_file)
            except Exception as e:
                print(f"⚠️ Błąd ładowania konfiguracji: {e}")
                print(f"🔄 Używam konfiguracji domyślnej...")
        
        return None
    
    def _print_startup_status(self):
        """Wyświetla status po uruchomieniu"""
        if not self.engine:
            return
        
        status = self.engine.get_status()
        
        print(f"\n{'='*60}")
        print(f"🌟 LuxDB v2 Service - Status Astralny")
        print(f"{'='*60}")
        print(f"🔮 Poziom świadomości: {status['astral_engine']['consciousness_level']}")
        print(f"⏱️ Czas działania: {status['astral_engine']['uptime']}")
        print(f"🌍 Aktywne wymiary: {len(status['realms'])}")
        
        for name, realm_status in status['realms'].items():
            print(f"   ▸ {name}: {realm_status['type']} ({'✓' if realm_status['connected'] else '✗'})")
        
        print(f"🌊 Aktywne przepływy:")
        for flow_name, flow_status in status['flows'].items():
            if flow_status:
                print(f"   ▸ {flow_name}: ✓")
        
        print(f"⚖️ Wynik harmonii: {status['harmony']['score']:.1f}/100")
        print(f"{'='*60}")
        print(f"🌐 REST API: http://0.0.0.0:{self.port}")
        print(f"📡 WebSocket: ws://0.0.0.0:{self.port + 1}")
        print(f"{'='*60}")
        print(f"💫 System astralny gotowy do pracy!")
        print(f"   Naciśnij Ctrl+C aby zatrzymać...")
        print(f"{'='*60}\n")
    
    def _main_loop(self):
        """Główna pętla serwisu"""
        last_status_time = time.time()
        status_interval = 300  # 5 minut
        
        while self._running:
            try:
                time.sleep(1)
                
                # Periodyczny status (co 5 minut)
                current_time = time.time()
                if current_time - last_status_time > status_interval:
                    self._print_periodic_status()
                    last_status_time = current_time
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️ Błąd w głównej pętli: {e}")
                time.sleep(5)
    
    def _print_periodic_status(self):
        """Wyświetla periodyczny status"""
        if not self.engine:
            return
        
        try:
            meditation = self.engine.meditate()
            harmony_score = meditation.get('harmony_score', 0)
            
            print(f"📊 Status astralny - Harmonia: {harmony_score:.1f}/100, "
                  f"Wymiary: {len(self.engine.realms)}, "
                  f"Manifestacje: {meditation['system_state']['total_manifestations']}")
            
        except Exception as e:
            print(f"⚠️ Błąd podczas pobierania statusu: {e}")
    
    def _signal_handler(self, signum, frame):
        """Obsługa sygnałów systemowych"""
        print(f"\n⭐ Otrzymano sygnał {signum}, zatrzymywanie...")
        self._running = False


def create_sample_config():
    """Tworzy przykładowy plik konfiguracyjny"""
    config = AstralConfig()
    
    # Dostosuj dla przykładu
    config.realms = {
        'primary': 'sqlite://db/astral_primary.db',
        'cache': 'memory://'
    }
    
    config.flows = {
        'rest': {'host': '0.0.0.0', 'port': 5000, 'enable_cors': True},
        'websocket': {'host': '0.0.0.0', 'port': 5001, 'enable_cors': True}
    }
    
    config_path = 'astral_config.json'
    config.to_file(config_path)
    
    print(f"📝 Utworzono przykładowy plik konfiguracyjny: {config_path}")
    return config_path


def main():
    """Główna funkcja programu"""
    parser = argparse.ArgumentParser(description='LuxDB v2 Service - Astralny Serwis Danych')
    
    parser.add_argument('--config', '-c', 
                       help='Ścieżka do pliku konfiguracyjnego')
    parser.add_argument('--port', '-p', type=int, default=5000,
                       help='Port dla REST API (domyślnie 5000)')
    parser.add_argument('--realm-type', '-r', default='sqlite',
                       choices=['sqlite', 'memory'],
                       help='Typ głównego wymiaru (domyślnie sqlite)')
    parser.add_argument('--create-config', action='store_true',
                       help='Utwórz przykładowy plik konfiguracyjny')
    parser.add_argument('--status', action='store_true',
                       help='Pokaż status działającego serwisu')
    parser.add_argument('--version', action='store_true',
                       help='Pokaż wersję')
    
    args = parser.parse_args()
    
    # Obsługa flag
    if args.version:
        print("LuxDB v2.0.0 - Astralna Biblioteka Danych Nowej Generacji")
        return
    
    if args.create_config:
        create_sample_config()
        return
    
    if args.status:
        # TODO: Implementuj sprawdzanie statusu przez API
        print("🔍 Sprawdzanie statusu serwisu...")
        try:
            import requests
            response = requests.get(f'http://localhost:{args.port}/status')
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Serwis działa - Harmonia: {status.get('harmony', {}).get('score', 'N/A')}")
            else:
                print(f"❌ Serwis nie odpowiada (kod: {response.status_code})")
        except Exception as e:
            print(f"❌ Nie można połączyć się z serwisem: {e}")
        return
    
    # Uruchom serwis
    service = LuxDBv2Service(
        config_file=args.config,
        port=args.port,
        realm_type=args.realm_type
    )
    
    try:
        service.start()
    except Exception as e:
        print(f"💥 Krytyczny błąd serwisu: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
