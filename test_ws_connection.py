
#!/usr/bin/env python3
"""
Prosty test połączenia WebSocket z LuxDB
Sprawdza podstawową komunikację z serwerem LuxWS
"""

import socketio
import time
import threading
from datetime import datetime

class SimpleWSTest:
    """Prosty test klient WebSocket"""
    
    def __init__(self, server_url="wss://data.luxunda.org"):
        self.server_url = server_url
        self.sio = socketio.Client()
        self.connected = False
        self.messages_received = []
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Konfiguruje podstawowe handlery"""
        
        @self.sio.event
        def connect():
            print(f"✅ Połączono z {self.server_url}")
            self.connected = True
        
        @self.sio.event
        def disconnect():
            print("❌ Rozłączono")
            self.connected = False
        
        @self.sio.event
        def connection_established(data):
            print(f"🔗 Potwierdzone połączenie: {data}")
            self.messages_received.append(('connection_established', data))
        
        @self.sio.event
        def server_status(data):
            print(f"📊 Status serwera: {data}")
            self.messages_received.append(('server_status', data))
        
        @self.sio.event
        def error(data):
            print(f"❌ Błąd: {data}")
            self.messages_received.append(('error', data))
    
    def test_connection(self):
        """Testuje podstawowe połączenie"""
        print(f"🔌 Próba połączenia z {self.server_url}...")
        
        try:
            # Połącz się z serwerem
            self.sio.connect(self.server_url)
            
            if self.connected:
                print("✅ Połączenie nawiązane")
                
                # Poczekaj chwilę na wiadomość powitania
                time.sleep(1)
                
                # Sprawdź status serwera
                print("📊 Pobieranie statusu serwera...")
                self.sio.emit('get_server_status')
                
                # Poczekaj na odpowiedź
                time.sleep(2)
                
                # Podsumowanie
                print(f"\n📋 Otrzymano {len(self.messages_received)} wiadomości:")
                for event_type, data in self.messages_received:
                    print(f"   - {event_type}: {data}")
                
                # Rozłącz się
                self.sio.disconnect()
                print("👋 Test zakończony pomyślnie")
                return True
            else:
                print("❌ Nie udało się nawiązać połączenia")
                return False
                
        except Exception as e:
            print(f"❌ Błąd podczas testu: {e}")
            return False

def quick_test():
    """Szybki test połączenia"""
    print("🧪 Prosty test połączenia WebSocket z LuxDB")
    print("=" * 50)
    
    tester = SimpleWSTest()
    success = tester.test_connection()
    
    if success:
        print("\n✅ Test przeszedł pomyślnie!")
    else:
        print("\n❌ Test nie powiódł się")
        print("💡 Upewnij się, że serwer LuxDB działa (python server.py)")

if __name__ == "__main__":
    quick_test()
