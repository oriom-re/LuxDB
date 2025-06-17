
#!/usr/bin/env python3
"""
Przykład klienta REST API dla LuxDB
Testuje endpointy HTTP i zarządzanie sesjami
"""

import requests
import json
import time
from datetime import datetime

class LuxAPIClient:
    """Przykładowy klient REST API dla LuxDB"""
    
    def __init__(self, base_url="http://0.0.0.0:5000"):
        self.base_url = base_url
        self.session_token = None
        self.user_info = None
    
    def health_check(self):
        """Sprawdza status serwera"""
        try:
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                print("✅ Serwer działa poprawnie")
                print(f"   Status: {response.json()}")
                return True
            else:
                print(f"❌ Serwer zwrócił kod: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Błąd połączenia: {e}")
            return False
    
    def test_root_endpoint(self):
        """Testuje główny endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            print(f"📄 Root endpoint: {response.status_code}")
            if response.status_code == 200:
                print(f"   Content: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ Błąd root endpoint: {e}")
    
    def login_test_user(self, username="testuser", password="testpass123"):
        """Loguje się jako użytkownik testowy"""
        print(f"🔐 Próba logowania użytkownika: {username}")
        
        # Uwaga: Ten endpoint może nie istnieć jeszcze w LuxAPI
        # To przykład jak powinien wyglądać
        try:
            response = requests.post(f"{self.base_url}/api/auth/login", json={
                "username": username,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get('session_token')
                self.user_info = data.get('user')
                print("✅ Logowanie udane")
                print(f"   User: {self.user_info}")
                return True
            else:
                print(f"❌ Błąd logowania: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Błąd połączenia podczas logowania: {e}")
            return False
    
    def get_session_info(self):
        """Pobiera informacje o sesji"""
        if not self.session_token:
            print("❌ Brak tokenu sesji")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            response = requests.get(f"{self.base_url}/api/auth/session", headers=headers)
            
            if response.status_code == 200:
                print("✅ Informacje o sesji:")
                print(f"   {response.json()}")
                return True
            else:
                print(f"❌ Błąd pobierania sesji: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Błąd: {e}")
            return False
    
    def list_databases(self):
        """Pobiera listę baz danych"""
        try:
            headers = {}
            if self.session_token:
                headers["Authorization"] = f"Bearer {self.session_token}"
            
            response = requests.get(f"{self.base_url}/api/databases", headers=headers)
            
            if response.status_code == 200:
                databases = response.json()
                print("📊 Lista baz danych:")
                for db in databases.get('databases', []):
                    print(f"   - {db}")
                return True
            else:
                print(f"❌ Błąd pobierania baz: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Błąd: {e}")
            return False
    
    def get_database_info(self, db_name="main"):
        """Pobiera informacje o konkretnej bazie danych"""
        try:
            headers = {}
            if self.session_token:
                headers["Authorization"] = f"Bearer {self.session_token}"
            
            response = requests.get(f"{self.base_url}/api/databases/{db_name}", headers=headers)
            
            if response.status_code == 200:
                info = response.json()
                print(f"📋 Informacje o bazie '{db_name}':")
                print(f"   Tables: {info.get('tables', [])}")
                print(f"   Engine: {info.get('engine', 'unknown')}")
                return True
            else:
                print(f"❌ Błąd pobierania info o bazie: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Błąd: {e}")
            return False
    
    def logout(self):
        """Wylogowuje użytkownika"""
        if not self.session_token:
            print("❌ Już wylogowany")
            return True
        
        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            response = requests.post(f"{self.base_url}/api/auth/logout", headers=headers)
            
            if response.status_code == 200:
                print("✅ Wylogowano pomyślnie")
                self.session_token = None
                self.user_info = None
                return True
            else:
                print(f"❌ Błąd wylogowania: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Błąd: {e}")
            return False
    
    def run_interactive_test(self):
        """Uruchamia interaktywny test API"""
        while True:
            print("\n" + "="*50)
            print("🧪 LuxAPI Test Client")
            print("1. Sprawdź status serwera")
            print("2. Test root endpoint")
            print("3. Zaloguj się")
            print("4. Informacje o sesji")
            print("5. Lista baz danych")
            print("6. Info o bazie 'main'")
            print("7. Wyloguj się")
            print("0. Wyjście")
            
            try:
                choice = input("\nWybierz opcję (0-7): ").strip()
                
                if choice == "1":
                    self.health_check()
                elif choice == "2":
                    self.test_root_endpoint()
                elif choice == "3":
                    username = input("Username (testuser): ").strip() or "testuser"
                    password = input("Password (testpass123): ").strip() or "testpass123"
                    self.login_test_user(username, password)
                elif choice == "4":
                    self.get_session_info()
                elif choice == "5":
                    self.list_databases()
                elif choice == "6":
                    db_name = input("Nazwa bazy (main): ").strip() or "main"
                    self.get_database_info(db_name)
                elif choice == "7":
                    self.logout()
                elif choice == "0":
                    break
                else:
                    print("❌ Nieprawidłowa opcja")
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n👋 Przerwano przez użytkownika")
                break
            except Exception as e:
                print(f"❌ Błąd: {e}")
        
        print("👋 Test zakończony")

def run_automated_test():
    """Uruchamia automatyczny test API"""
    print("🤖 Uruchamianie automatycznego testu API...")
    
    client = LuxAPIClient()
    
    # Test 1: Status serwera
    print("\n1. Test statusu serwera:")
    if not client.health_check():
        print("❌ Serwer nie odpowiada, kończę test")
        return
    
    # Test 2: Root endpoint
    print("\n2. Test root endpoint:")
    client.test_root_endpoint()
    
    # Test 3: Próba logowania
    print("\n3. Test logowania:")
    if client.login_test_user():
        print("✅ Logowanie udane, kontynuuję testy...")
        
        # Test 4: Informacje o sesji
        print("\n4. Test informacji o sesji:")
        client.get_session_info()
        
        # Test 5: Lista baz danych
        print("\n5. Test listy baz:")
        client.list_databases()
        
        # Test 6: Informacje o bazie
        print("\n6. Test info o bazie:")
        client.get_database_info("main")
        
        # Test 7: Wylogowanie
        print("\n7. Test wylogowania:")
        client.logout()
    else:
        print("❌ Logowanie nieudane, pomijam pozostałe testy")
    
    print("\n🤖 Test automatyczny zakończony")

def main():
    """Główna funkcja testu"""
    print("🧪 LuxDB REST API Client Test")
    print("Upewnij się, że serwer LuxDB działa na porcie 5000")
    print()
    
    mode = input("Wybierz tryb testu:\n1. Interaktywny\n2. Automatyczny\nWybór (1/2): ").strip()
    
    if mode == "1":
        client = LuxAPIClient()
        client.run_interactive_test()
    elif mode == "2":
        run_automated_test()
    else:
        print("❌ Nieprawidłowy wybór")

if __name__ == "__main__":
    main()
