
#!/usr/bin/env python3
"""
Przykład klienta WebSocket dla LuxDB
Testuje komunikację real-time z serwerem
"""

import socketio
import json
import time
import threading
from datetime import datetime

class LuxWSClient:
    """Przykładowy klient WebSocket dla LuxDB"""
    
    def __init__(self, server_url="data.luxunda.org:5001"):
        self.server_url = server_url
        self.sio = socketio.Client()
        self.connected = False
        self.authenticated = False
        self.client_id = None
        
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Konfiguruje handlery eventów"""
        
        @self.sio.event
        def connect():
            print("🔗 Połączono z LuxWS")
            self.connected = True
        
        @self.sio.event
        def disconnect():
            print("❌ Rozłączono z LuxWS")
            self.connected = False
            self.authenticated = False
        
        @self.sio.event
        def connection_established(data):
            print(f"✅ Połączenie potwierdzone: {data}")
            self.client_id = data.get('client_id')
        
        @self.sio.event
        def authenticated(data):
            print(f"🔐 Uwierzytelniono: {data}")
            self.authenticated = True
        
        @self.sio.event
        def auth_error(data):
            print(f"❌ Błąd uwierzytelniania: {data}")
        
        @self.sio.event
        def joined_database(data):
            print(f"📊 Dołączono do bazy: {data}")
        
        @self.sio.event
        def left_database(data):
            print(f"🚪 Opuszczono bazę: {data}")
        
        @self.sio.event
        def database_change(data):
            print(f"🔄 Zmiana w bazie: {data}")
        
        @self.sio.event
        def query_result(data):
            print(f"📋 Wynik zapytania: {json.dumps(data, indent=2)}")
        
        @self.sio.event
        def query_error(data):
            print(f"❌ Błąd zapytania: {data}")
        
        @self.sio.event
        def server_status(data):
            print(f"📊 Status serwera: {json.dumps(data, indent=2)}")
        
        @self.sio.event
        def error(data):
            print(f"❌ Błąd: {data}")
    
    def connect_to_server(self):
        """Łączy się z serwerem WebSocket"""
        try:
            print(f"🔌 Łączenie z {self.server_url}...")
            self.sio.connect(self.server_url)
            return True
        except Exception as e:
            print(f"❌ Błąd połączenia: {e}")
            return False
    
    def authenticate_with_test_user(self):
        """Uwierzytelnia się jako użytkownik testowy"""
        # W rzeczywistej aplikacji token otrzymasz z API po logowaniu
        # Tu symulujemy proces uwierzytelniania
        print("🔐 Próba uwierzytelniania...")
        
        # Najpierw musielibyśmy się zalogować przez API aby otrzymać token
        # Na potrzeby testu używamy pustego tokenu (serwer powinien obsłużyć błąd)
        test_token = "test_session_token_123"
        
        self.sio.emit('authenticate', {
            'session_token': test_token
        })
    
    def join_database(self, db_name="main"):
        """Dołącza do pokoju bazy danych"""
        if not self.authenticated:
            print("❌ Wymagane uwierzytelnienie")
            return
        
        print(f"📊 Dołączanie do bazy {db_name}...")
        self.sio.emit('join_database', {
            'database': db_name
        })
    
    def query_database_info(self, db_name="main"):
        """Pobiera informacje o bazie danych"""
        print(f"📋 Pobieranie informacji o bazie {db_name}...")
        self.sio.emit('query_database', {
            'database': db_name,
            'type': 'get_info'
        })
    
    def get_server_status(self):
        """Pobiera status serwera"""
        print("📊 Pobieranie statusu serwera...")
        self.sio.emit('get_server_status')
    
    def run_interactive_test(self):
        """Uruchamia interaktywny test klienta"""
        if not self.connect_to_server():
            return
        
        # Czekaj na połączenie
        time.sleep(1)
        
        while self.connected:
            print("\n" + "="*50)
            print("🧪 LuxWS Test Client")
            print("1. Uwierzytelnij się")
            print("2. Dołącz do bazy 'main'")
            print("3. Pobierz informacje o bazie")
            print("4. Pobierz status serwera")
            print("5. Opuść bazę")
            print("6. Rozłącz się")
            print("0. Wyjście")
            
            try:
                choice = input("\nWybierz opcję (0-6): ").strip()
                
                if choice == "1":
                    self.authenticate_with_test_user()
                elif choice == "2":
                    self.join_database("main")
                elif choice == "3":
                    self.query_database_info("main")
                elif choice == "4":
                    self.get_server_status()
                elif choice == "5":
                    self.sio.emit('leave_database', {'database': 'main'})
                elif choice == "6":
                    self.sio.disconnect()
                    break
                elif choice == "0":
                    break
                else:
                    print("❌ Nieprawidłowa opcja")
                
                time.sleep(0.5)  # Krótka pauza
                
            except KeyboardInterrupt:
                print("\n👋 Przerwano przez użytkownika")
                break
            except Exception as e:
                print(f"❌ Błąd: {e}")
        
        if self.connected:
            self.sio.disconnect()
        
        print("👋 Test zakończony")

def run_automated_test():
    """Uruchamia automatyczny test funkcjonalności"""
    print("🤖 Uruchamianie automatycznego testu WebSocket...")
    
    client = LuxWSClient()
    
    if client.connect_to_server():
        print("✅ Połączenie nawiązane")
        
        # Test 1: Pobierz status serwera
        time.sleep(1)
        client.get_server_status()
        
        # Test 2: Spróbuj dołączyć do bazy bez uwierzytelnienia
        time.sleep(1)
        client.join_database("main")
        
        # Test 3: Spróbuj się uwierzytelnić
        time.sleep(1)
        client.authenticate_with_test_user()
        
        # Poczekaj chwilę na odpowiedzi
        time.sleep(3)
        
        client.sio.disconnect()
        print("🤖 Test automatyczny zakończony")
    else:
        print("❌ Nie udało się połączyć z serwerem")

def main():
    """Główna funkcja testu"""
    print("🧪 LuxDB WebSocket Client Test")
    print("Upewnij się, że serwer LuxDB działa na porcie 5001")
    print()
    
    mode = input("Wybierz tryb testu:\n1. Interaktywny\n2. Automatyczny\nWybór (1/2): ").strip()
    
    if mode == "1":
        client = LuxWSClient()
        client.run_interactive_test()
    elif mode == "2":
        run_automated_test()
    else:
        print("❌ Nieprawidłowy wybór")

if __name__ == "__main__":
    main()
