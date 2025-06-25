
#!/usr/bin/env python3
"""
🧪 Test Klienta LuxDB v2 - WebSocket i REST API

Kompleksowe testy połączeń z serwerem LuxDB v2:
- REST API endpoints
- WebSocket komunikacja real-time
- Testy lokalne i zdalne (VM)
- Integracja z systemem intencji
"""

import requests
import socketio
import json
import time
import threading
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional


class LuxDBRestClient:
    """Klient REST API dla LuxDB v2"""
    
    def __init__(self, base_url: str = "http://0.0.0.0:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def test_astral_status(self) -> Dict[str, Any]:
        """Test statusu systemu astralnego"""
        try:
            response = self.session.get(f"{self.base_url}/astral/status")
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_meditation(self) -> Dict[str, Any]:
        """Test medytacji systemu"""
        try:
            response = self.session.post(f"{self.base_url}/astral/meditate")
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_harmonize(self) -> Dict[str, Any]:
        """Test harmonizacji systemu"""
        try:
            response = self.session.post(f"{self.base_url}/astral/harmonize")
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_list_realms(self) -> Dict[str, Any]:
        """Test listowania wymiarów"""
        try:
            response = self.session.get(f"{self.base_url}/realms")
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_realm_status(self, realm_name: str = "primary") -> Dict[str, Any]:
        """Test statusu konkretnego wymiaru"""
        try:
            response = self.session.get(f"{self.base_url}/realms/{realm_name}")
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_manifest_being(self, realm_name: str = "primary", being_data: Dict = None) -> Dict[str, Any]:
        """Test manifestacji bytu"""
        if being_data is None:
            being_data = {
                'soul_name': f'TestBeing_{int(time.time())}',
                'essence': {
                    'type': 'test_entity',
                    'energy_level': 100,
                    'attributes': {
                        'power': 75,
                        'wisdom': 80,
                        'harmony': 90
                    }
                }
            }
        
        try:
            response = self.session.post(
                f"{self.base_url}/realms/{realm_name}/beings",
                json=being_data
            )
            return {
                'success': response.status_code == 201,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 201 else None,
                'error': response.text if response.status_code != 201 else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_list_beings(self, realm_name: str = "primary") -> Dict[str, Any]:
        """Test listowania bytów w wymiarze"""
        try:
            response = self.session.get(f"{self.base_url}/realms/{realm_name}/beings")
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_contemplate(self, realm_name: str = "primary", criteria: Dict = None) -> Dict[str, Any]:
        """Test kontemplacji (wyszukiwania)"""
        if criteria is None:
            criteria = {
                'intention': 'find_beings',
                'criteria': {'essence.type': 'test_entity'}
            }
        
        try:
            response = self.session.post(
                f"{self.base_url}/realms/{realm_name}/contemplate",
                json=criteria
            )
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class LuxDBWebSocketClient:
    """Klient WebSocket dla LuxDB v2"""
    
    def __init__(self, server_url: str = "http://0.0.0.0:5001"):
        self.server_url = server_url
        self.sio = socketio.Client()
        self.connected = False
        self.messages_received = []
        self.events_log = []
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Konfiguruje handlery eventów WebSocket"""
        
        @self.sio.event
        def connect():
            self.connected = True
            self.events_log.append({
                'event': 'connect',
                'timestamp': datetime.now().isoformat(),
                'data': None
            })
        
        @self.sio.event
        def disconnect():
            self.connected = False
            self.events_log.append({
                'event': 'disconnect',
                'timestamp': datetime.now().isoformat(),
                'data': None
            })
        
        @self.sio.event
        def welcome(data):
            self.messages_received.append({
                'type': 'welcome',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.sio.event
        def status_response(data):
            self.messages_received.append({
                'type': 'status_response',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.sio.event
        def meditation_response(data):
            self.messages_received.append({
                'type': 'meditation_response',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.sio.event
        def meditation_event(data):
            self.messages_received.append({
                'type': 'meditation_event',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.sio.event
        def manifestation_response(data):
            self.messages_received.append({
                'type': 'manifestation_response',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.sio.event
        def being_manifested(data):
            self.messages_received.append({
                'type': 'being_manifested',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.sio.event
        def contemplation_response(data):
            self.messages_received.append({
                'type': 'contemplation_response',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.sio.event
        def subscription_confirmed(data):
            self.messages_received.append({
                'type': 'subscription_confirmed',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.sio.event
        def error(data):
            self.messages_received.append({
                'type': 'error',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
    
    def connect_to_server(self, timeout: int = 10) -> bool:
        """Łączy się z serwerem WebSocket"""
        try:
            self.sio.connect(self.server_url, wait_timeout=timeout)
            time.sleep(1)  # Poczekaj na welcome message
            return self.connected
        except Exception as e:
            print(f"❌ Błąd połączenia WebSocket: {e}")
            return False
    
    def disconnect_from_server(self):
        """Rozłącza się z serwerem"""
        if self.connected:
            self.sio.disconnect()
    
    def test_get_status(self) -> bool:
        """Test żądania statusu"""
        try:
            self.sio.emit('get_status', {})
            time.sleep(2)
            return any(msg['type'] == 'status_response' for msg in self.messages_received)
        except Exception as e:
            print(f"❌ Błąd test_get_status: {e}")
            return False
    
    def test_meditate(self) -> bool:
        """Test medytacji przez WebSocket"""
        try:
            self.sio.emit('meditate', {})
            time.sleep(3)
            return any(msg['type'] == 'meditation_response' for msg in self.messages_received)
        except Exception as e:
            print(f"❌ Błąd test_meditate: {e}")
            return False
    
    def test_subscribe_realm(self, realm_name: str = "primary") -> bool:
        """Test subskrypcji wymiaru"""
        try:
            self.sio.emit('subscribe_realm', {'realm_name': realm_name})
            time.sleep(2)
            return any(msg['type'] == 'subscription_confirmed' for msg in self.messages_received)
        except Exception as e:
            print(f"❌ Błąd test_subscribe_realm: {e}")
            return False
    
    def test_manifest_being(self, realm_name: str = "primary") -> bool:
        """Test manifestacji bytu przez WebSocket"""
        try:
            being_data = {
                'soul_name': f'WSTestBeing_{int(time.time())}',
                'essence': {
                    'type': 'websocket_entity',
                    'energy_level': 95,
                    'connection_type': 'real_time'
                }
            }
            
            self.sio.emit('manifest_being', {
                'realm_name': realm_name,
                'being_data': being_data
            })
            time.sleep(3)
            return any(msg['type'] == 'manifestation_response' for msg in self.messages_received)
        except Exception as e:
            print(f"❌ Błąd test_manifest_being: {e}")
            return False
    
    def test_contemplate(self, realm_name: str = "primary") -> bool:
        """Test kontemplacji przez WebSocket"""
        try:
            self.sio.emit('contemplate', {
                'realm_name': realm_name,
                'intention': 'find_beings',
                'criteria': {'essence.type': 'websocket_entity'}
            })
            time.sleep(2)
            return any(msg['type'] == 'contemplation_response' for msg in self.messages_received)
        except Exception as e:
            print(f"❌ Błąd test_contemplate: {e}")
            return False


class LuxDBTestSuite:
    """Kompletna suita testów dla LuxDB v2"""
    
    def __init__(self, rest_url: str = "http://0.0.0.0:5000", ws_url: str = "http://0.0.0.0:5001"):
        self.rest_client = LuxDBRestClient(rest_url)
        self.ws_client = LuxDBWebSocketClient(ws_url)
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_rest_tests(self) -> Dict[str, Any]:
        """Uruchamia testy REST API"""
        print("🌐 Uruchamianie testów REST API...")
        
        rest_results = {}
        
        # Test 1: Status astralny
        print("   📊 Test: Status astralny...")
        result = self.rest_client.test_astral_status()
        rest_results['astral_status'] = result
        print(f"      {'✅' if result['success'] else '❌'} Status: {result['success']}")
        
        # Test 2: Medytacja
        print("   🧘 Test: Medytacja systemu...")
        result = self.rest_client.test_meditation()
        rest_results['meditation'] = result
        print(f"      {'✅' if result['success'] else '❌'} Medytacja: {result['success']}")
        
        # Test 3: Harmonizacja
        print("   ⚖️ Test: Harmonizacja...")
        result = self.rest_client.test_harmonize()
        rest_results['harmonize'] = result
        print(f"      {'✅' if result['success'] else '❌'} Harmonizacja: {result['success']}")
        
        # Test 4: Lista wymiarów
        print("   🌍 Test: Lista wymiarów...")
        result = self.rest_client.test_list_realms()
        rest_results['list_realms'] = result
        print(f"      {'✅' if result['success'] else '❌'} Lista wymiarów: {result['success']}")
        
        # Test 5: Status wymiaru
        print("   🔮 Test: Status wymiaru primary...")
        result = self.rest_client.test_realm_status("primary")
        rest_results['realm_status'] = result
        print(f"      {'✅' if result['success'] else '❌'} Status wymiaru: {result['success']}")
        
        # Test 6: Manifestacja bytu
        print("   ✨ Test: Manifestacja bytu...")
        result = self.rest_client.test_manifest_being("primary")
        rest_results['manifest_being'] = result
        print(f"      {'✅' if result['success'] else '❌'} Manifestacja: {result['success']}")
        
        # Test 7: Lista bytów
        print("   📋 Test: Lista bytów...")
        result = self.rest_client.test_list_beings("primary")
        rest_results['list_beings'] = result
        print(f"      {'✅' if result['success'] else '❌'} Lista bytów: {result['success']}")
        
        # Test 8: Kontemplacja
        print("   🤔 Test: Kontemplacja...")
        result = self.rest_client.test_contemplate("primary")
        rest_results['contemplate'] = result
        print(f"      {'✅' if result['success'] else '❌'} Kontemplacja: {result['success']}")
        
        return rest_results
    
    def run_websocket_tests(self) -> Dict[str, Any]:
        """Uruchamia testy WebSocket"""
        print("⚡ Uruchamianie testów WebSocket...")
        
        ws_results = {}
        
        # Test połączenia
        print("   🔌 Test: Połączenie WebSocket...")
        connected = self.ws_client.connect_to_server()
        ws_results['connection'] = connected
        print(f"      {'✅' if connected else '❌'} Połączenie: {connected}")
        
        if not connected:
            return ws_results
        
        # Test 1: Status przez WebSocket
        print("   📊 Test: Status przez WebSocket...")
        result = self.ws_client.test_get_status()
        ws_results['get_status'] = result
        print(f"      {'✅' if result else '❌'} Status WS: {result}")
        
        # Test 2: Medytacja przez WebSocket
        print("   🧘 Test: Medytacja przez WebSocket...")
        result = self.ws_client.test_meditate()
        ws_results['meditate'] = result
        print(f"      {'✅' if result else '❌'} Medytacja WS: {result}")
        
        # Test 3: Subskrypcja wymiaru
        print("   📡 Test: Subskrypcja wymiaru...")
        result = self.ws_client.test_subscribe_realm("primary")
        ws_results['subscribe_realm'] = result
        print(f"      {'✅' if result else '❌'} Subskrypcja: {result}")
        
        # Test 4: Manifestacja przez WebSocket
        print("   ✨ Test: Manifestacja przez WebSocket...")
        result = self.ws_client.test_manifest_being("primary")
        ws_results['manifest_being'] = result
        print(f"      {'✅' if result else '❌'} Manifestacja WS: {result}")
        
        # Test 5: Kontemplacja przez WebSocket
        print("   🤔 Test: Kontemplacja przez WebSocket...")
        result = self.ws_client.test_contemplate("primary")
        ws_results['contemplate'] = result
        print(f"      {'✅' if result else '❌'} Kontemplacja WS: {result}")
        
        # Rozłącz
        self.ws_client.disconnect_from_server()
        
        return ws_results
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """Uruchamia pełną suitę testów"""
        print("🧪 Uruchamianie pełnej suity testów LuxDB v2")
        print("=" * 60)
        
        self.start_time = datetime.now()
        
        # Uruchom testy REST
        rest_results = self.run_rest_tests()
        
        print()  # Separator
        
        # Uruchom testy WebSocket
        ws_results = self.run_websocket_tests()
        
        self.end_time = datetime.now()
        
        # Podsumowanie
        self.test_results = {
            'rest_api': rest_results,
            'websocket': ws_results,
            'test_duration': str(self.end_time - self.start_time),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }
        
        self._print_summary()
        return self.test_results
    
    def _print_summary(self):
        """Wyświetla podsumowanie testów"""
        print("\n" + "=" * 60)
        print("📊 PODSUMOWANIE TESTÓW LUXDB V2")
        print("=" * 60)
        
        # Statystyki REST
        rest_tests = self.test_results['rest_api']
        rest_passed = sum(1 for test in rest_tests.values() if isinstance(test, dict) and test.get('success', False))
        rest_total = len(rest_tests)
        
        print(f"🌐 REST API Tests: {rest_passed}/{rest_total} passed ({rest_passed/rest_total*100:.1f}%)")
        
        # Statystyki WebSocket
        ws_tests = self.test_results['websocket']
        ws_passed = sum(1 for test in ws_tests.values() if test is True)
        ws_total = len(ws_tests)
        
        print(f"⚡ WebSocket Tests: {ws_passed}/{ws_total} passed ({ws_passed/ws_total*100:.1f}%)")
        
        # Ogólne statystyki
        total_passed = rest_passed + ws_passed
        total_tests = rest_total + ws_total
        
        print(f"🎯 Total Tests: {total_passed}/{total_tests} passed ({total_passed/total_tests*100:.1f}%)")
        print(f"⏱️ Test Duration: {self.test_results['test_duration']}")
        
        # Status końcowy
        if total_passed == total_tests:
            print("\n✅ Wszystkie testy przeszły pomyślnie! 🎉")
        else:
            print(f"\n⚠️ {total_tests - total_passed} testów nie powiodło się")
        
        print("=" * 60)
    
    def save_results_to_file(self, filename: str = None):
        """Zapisuje wyniki do pliku JSON"""
        if filename is None:
            filename = f"luxdb_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"💾 Wyniki zapisane do: {filename}")
        except Exception as e:
            print(f"❌ Błąd zapisu wyników: {e}")


def test_local_server():
    """Test lokalnego serwera"""
    print("🏠 Testowanie lokalnego serwera LuxDB v2")
    suite = LuxDBTestSuite("http://0.0.0.0:5000", "http://0.0.0.0:5001")
    results = suite.run_full_test_suite()
    suite.save_results_to_file("luxdb_local_test_results.json")
    return results


def test_vm_server(vm_ip: str):
    """Test serwera na VM"""
    print(f"☁️ Testowanie serwera LuxDB v2 na VM: {vm_ip}")
    rest_url = f"http://{vm_ip}:5000"
    ws_url = f"http://{vm_ip}:5001"
    
    suite = LuxDBTestSuite(rest_url, ws_url)
    results = suite.run_full_test_suite()
    suite.save_results_to_file(f"luxdb_vm_test_results_{vm_ip.replace('.', '_')}.json")
    return results


def interactive_test():
    """Interaktywny test klienta"""
    print("🎮 Interaktywny test klienta LuxDB v2")
    print("=" * 50)
    
    while True:
        print("\nOpcje testowania:")
        print("1. Test lokalnego serwera (0.0.0.0)")
        print("2. Test serwera na VM (podaj IP)")
        print("3. Test niestandardowych URL")
        print("4. Test tylko REST API")
        print("5. Test tylko WebSocket")
        print("0. Wyjście")
        
        choice = input("\nWybierz opcję (0-5): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            test_local_server()
        elif choice == "2":
            vm_ip = input("Podaj IP serwera VM: ").strip()
            if vm_ip:
                test_vm_server(vm_ip)
        elif choice == "3":
            rest_url = input("REST API URL (http://0.0.0.0:5000): ").strip() or "http://0.0.0.0:5000"
            ws_url = input("WebSocket URL (http://0.0.0.0:5001): ").strip() or "http://0.0.0.0:5001"
            suite = LuxDBTestSuite(rest_url, ws_url)
            suite.run_full_test_suite()
        elif choice == "4":
            rest_url = input("REST API URL (http://0.0.0.0:5000): ").strip() or "http://0.0.0.0:5000"
            suite = LuxDBTestSuite(rest_url, "")
            suite.run_rest_tests()
        elif choice == "5":
            ws_url = input("WebSocket URL (http://0.0.0.0:5001): ").strip() or "http://0.0.0.0:5001"
            suite = LuxDBTestSuite("", ws_url)
            suite.run_websocket_tests()
        else:
            print("❌ Nieprawidłowa opcja")
    
    print("👋 Zakończono testy")


def main():
    """Główna funkcja"""
    print("🧪 LuxDB v2 Client Test Suite")
    print("Comprehensive testing for REST API and WebSocket connections")
    print()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "local":
            test_local_server()
        elif command == "vm" and len(sys.argv) > 2:
            vm_ip = sys.argv[2]
            test_vm_server(vm_ip)
        elif command == "interactive":
            interactive_test()
        else:
            print("Użycie:")
            print("  python test_luxdb_client.py local              # Test lokalny")
            print("  python test_luxdb_client.py vm <IP>            # Test VM")
            print("  python test_luxdb_client.py interactive        # Tryb interaktywny")
    else:
        interactive_test()


if __name__ == "__main__":
    main()
