
#!/usr/bin/env python3
"""
Test dwukierunkowej komunikacji WebSocket w LuxDB
Przykład użycia LuxWSClient z LuxWSServer
"""

import time
import threading
from datetime import datetime
from luxdb.luxws_client import create_client, LuxWSClient

class BidirectionalWSTest:
    """Test dwukierunkowej komunikacji WebSocket"""
    
    def __init__(self, server_url: str = "http://data.luxunda.org"):
        self.server_url = server_url
        self.client = None
        self.test_results = []
        self.received_events = []
    
    def setup_client_callbacks(self):
        """Konfiguruje callbacki dla klienta"""
        
        def on_connect(data):
            print(f"✅ Połączono: {data}")
            self.test_results.append(("connect", True, data))
        
        def on_disconnect(data):
            print(f"❌ Rozłączono: {data}")
            self.test_results.append(("disconnect", True, data))
        
        def on_server_welcome(data):
            print(f"🎉 Powitanie od serwera: {data}")
            self.test_results.append(("server_welcome", True, data))
        
        def on_auth_success(data):
            print(f"🔐 Uwierzytelnienie udane: {data}")
            self.test_results.append(("auth_success", True, data))
        
        def on_auth_error(data):
            print(f"❌ Błąd uwierzytelniania: {data}")
            self.test_results.append(("auth_error", False, data))
        
        def on_room_joined(data):
            print(f"🏠 Dołączono do pokoju: {data}")
            self.test_results.append(("room_joined", True, data))
        
        def on_database_change(data):
            print(f"🔄 Zmiana w bazie: {data}")
            self.received_events.append(("database_change", data))
        
        def on_query_result(data):
            print(f"📊 Wynik zapytania: {data}")
            self.received_events.append(("query_result", data))
        
        def on_server_status(data):
            print(f"📈 Status serwera: {data}")
            self.received_events.append(("server_status", data))
        
        def on_server_heartbeat(data):
            print(f"💓 Heartbeat serwera: {data}")
            self.received_events.append(("heartbeat", data))
        
        def on_error(data):
            print(f"❌ Błąd: {data}")
            self.test_results.append(("error", False, data))
        
        # Rejestruj callbacki
        self.client.on('on_connect', on_connect)
        self.client.on('on_disconnect', on_disconnect)
        self.client.on('on_server_welcome', on_server_welcome)
        self.client.on('on_auth_success', on_auth_success)
        self.client.on('on_auth_error', on_auth_error)
        self.client.on('on_room_joined', on_room_joined)
        self.client.on('on_database_change', on_database_change)
        self.client.on('on_query_result', on_query_result)
        self.client.on('on_server_status', on_server_status)
        self.client.on('on_server_heartbeat', on_server_heartbeat)
        self.client.on('on_error', on_error)
    
    def run_connection_test(self):
        """Test podstawowego połączenia"""
        print("\n🧪 Test 1: Podstawowe połączenie")
        
        self.client = create_client(self.server_url, "test_client")
        self.setup_client_callbacks()
        
        # Połącz
        if self.client.connect_to_server():
            print("✅ Połączenie udane")
            
            # Czekaj na powitanie
            time.sleep(2)
            
            # Sprawdź heartbeat
            print("💓 Test heartbeat...")
            self.client.send_heartbeat()
            time.sleep(1)
            
            return True
        else:
            print("❌ Połączenie nieudane")
            return False
    
    def run_authentication_test(self, session_token: str = "test_token_123"):
        """Test uwierzytelniania"""
        print("\n🧪 Test 2: Uwierzytelnianie")
        
        if not self.client or not self.client.connected:
            print("❌ Brak połączenia")
            return False
        
        # Próba uwierzytelnienia
        success = self.client.authenticate(session_token)
        time.sleep(2)  # Czekaj na odpowiedź
        
        if success:
            print("✅ Uwierzytelnienie udane")
            return True
        else:
            print("❌ Uwierzytelnienie nieudane")
            return False
    
    def run_room_management_test(self):
        """Test zarządzania pokojami"""
        print("\n🧪 Test 3: Zarządzanie pokojami")
        
        if not self.client or not self.client.authenticated:
            print("❌ Wymagane uwierzytelnienie")
            return False
        
        try:
            # Dołącz do pokoju głównej bazy
            print("🏠 Dołączanie do pokoju 'main'...")
            self.client.join_database_room("main")
            time.sleep(1)
            
            # Pobierz status serwera
            print("📈 Pobieranie statusu serwera...")
            self.client.get_server_status()
            time.sleep(1)
            
            # Subskrybuj zdarzenia
            print("📢 Subskrypcja zdarzeń...")
            self.client.subscribe_to_events([
                "database_changes",
                "user_activity",
                "system_notifications"
            ])
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ Błąd testu pokoi: {e}")
            return False
    
    def run_query_test(self):
        """Test wykonywania zapytań"""
        print("\n🧪 Test 4: Wykonywanie zapytań")
        
        if not self.client or not self.client.authenticated:
            print("❌ Wymagane uwierzytelnienie")
            return False
        
        try:
            query_results = []
            
            def query_callback(result, error):
                if error:
                    print(f"❌ Błąd zapytania: {error}")
                    query_results.append(("error", error))
                else:
                    print(f"✅ Wynik zapytania: {result}")
                    query_results.append(("success", result))
            
            # Test 1: Informacje o bazie
            print("📊 Pobieranie informacji o bazie...")
            query_id1 = self.client.get_database_info("main", query_callback)
            
            # Test 2: Lista tabel
            print("📋 Pobieranie listy tabel...")
            query_id2 = self.client.list_tables("main", query_callback)
            
            # Test 3: Proste zapytanie SQL
            print("🔍 Wykonywanie zapytania SQL...")
            query_id3 = self.client.execute_sql(
                "main", 
                "SELECT COUNT(*) as total FROM users", 
                {},
                query_callback
            )
            
            # Czekaj na wyniki
            time.sleep(3)
            
            print(f"📊 Otrzymano {len(query_results)} wyników zapytań")
            return len(query_results) > 0
            
        except Exception as e:
            print(f"❌ Błąd testów zapytań: {e}")
            return False
    
    def run_stress_test(self, num_queries: int = 10):
        """Test obciążeniowy"""
        print(f"\n🧪 Test 5: Test obciążeniowy ({num_queries} zapytań)")
        
        if not self.client or not self.client.authenticated:
            print("❌ Wymagane uwierzytelnienie")
            return False
        
        try:
            completed_queries = 0
            query_lock = threading.Lock()
            
            def stress_callback(result, error):
                nonlocal completed_queries
                with query_lock:
                    completed_queries += 1
                    if completed_queries % 5 == 0:
                        print(f"📊 Ukończono {completed_queries}/{num_queries} zapytań")
            
            # Wyślij wiele zapytań jednocześnie
            start_time = time.time()
            
            for i in range(num_queries):
                self.client.execute_sql(
                    "main",
                    f"SELECT {i} as query_number, datetime('now') as timestamp",
                    {},
                    stress_callback
                )
                time.sleep(0.1)  # Małe opóźnienie między zapytaniami
            
            # Czekaj na ukończenie
            timeout = 30
            while completed_queries < num_queries and (time.time() - start_time) < timeout:
                time.sleep(0.5)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️  Czas testu: {duration:.2f}s")
            print(f"📊 Ukończone zapytania: {completed_queries}/{num_queries}")
            print(f"🚀 Zapytań na sekundę: {completed_queries/duration:.2f}")
            
            return completed_queries >= num_queries * 0.8  # 80% success rate
            
        except Exception as e:
            print(f"❌ Błąd testu obciążeniowego: {e}")
            return False
    
    def cleanup(self):
        """Czyści połączenia"""
        if self.client:
            print("\n🧹 Czyszczenie połączeń...")
            self.client.disconnect()
            self.client = None
    
    def run_full_test_suite(self, session_token: str = "test_token_123"):
        """Uruchamia pełny zestaw testów"""
        print("🚀 Uruchamianie pełnego zestawu testów LuxWS")
        print("=" * 60)
        
        test_results = {}
        
        try:
            # Test 1: Połączenie
            test_results["connection"] = self.run_connection_test()
            
            # Test 2: Uwierzytelnianie
            if test_results["connection"]:
                test_results["authentication"] = self.run_authentication_test(session_token)
            else:
                test_results["authentication"] = False
            
            # Test 3: Pokoje
            if test_results["authentication"]:
                test_results["rooms"] = self.run_room_management_test()
            else:
                test_results["rooms"] = False
            
            # Test 4: Zapytania
            if test_results["authentication"]:
                test_results["queries"] = self.run_query_test()
            else:
                test_results["queries"] = False
            
            # Test 5: Obciążenie
            if test_results["authentication"]:
                test_results["stress"] = self.run_stress_test()
            else:
                test_results["stress"] = False
            
            # Podsumowanie
            print("\n" + "=" * 60)
            print("📊 PODSUMOWANIE TESTÓW")
            print("=" * 60)
            
            passed = sum(1 for result in test_results.values() if result)
            total = len(test_results)
            
            for test_name, result in test_results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{test_name.upper():15} {status}")
            
            print("-" * 60)
            print(f"WYNIK KOŃCOWY: {passed}/{total} testów przeszło")
            
            if passed == total:
                print("🎉 Wszystkie testy przeszły pomyślnie!")
            elif passed >= total * 0.8:
                print("⚠️  Większość testów przeszła - sprawdź błędy")
            else:
                print("❌ Krytyczne błędy - sprawdź konfigurację")
            
            return test_results
            
        except Exception as e:
            print(f"❌ Krytyczny błąd testów: {e}")
            return test_results
        
        finally:
            self.cleanup()

def run_interactive_test():
    """Interaktywny test dwukierunkowej komunikacji"""
    print("🎯 Interaktywny test LuxWS Client-Server")
    
    server_url = input("URL serwera (http://0.0.0.0:5001): ").strip()
    if not server_url:
        server_url = "http://0.0.0.0:5001"
    
    session_token = input("Token sesji (test_token_123): ").strip()
    if not session_token:
        session_token = "test_token_123"
    
    test = BidirectionalWSTest(server_url)
    test.run_full_test_suite(session_token)

def run_automated_test():
    """Automatyczny test z domyślnymi parametrami"""
    print("🤖 Automatyczny test LuxWS")
    
    test = BidirectionalWSTest()
    results = test.run_full_test_suite()
    
    return results

def main():
    """Główna funkcja testu"""
    print("🧪 LuxDB WebSocket Bidirectional Communication Test")
    print("Upewnij się, że serwer LuxDB działa na porcie 5001")
    print()
    
    mode = input("Wybierz tryb testu:\n1. Interaktywny\n2. Automatyczny\nWybór (1/2): ").strip()
    
    if mode == "1":
        run_interactive_test()
    elif mode == "2":
        run_automated_test()
    else:
        print("❌ Nieprawidłowy wybór")

if __name__ == "__main__":
    main()
