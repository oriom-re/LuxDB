
#!/usr/bin/env python3
"""
🧪 LuxDB v2 - Kompletny Test Runner
Uruchamia serwer i wykonuje wszystkie testy
"""

import time
import threading
import subprocess
import requests
import json
import os
import sys
from typing import Dict, Any, List

class AstraTestRunner:
    """Kompletny runner testów dla Astry"""
    
    def __init__(self):
        self.server_process = None
        self.server_ready = False
        self.test_results = []
        self.base_url = "http://localhost:5000"
        
    def start_server(self) -> bool:
        """Uruchamia serwer Astry"""
        try:
            print("🚀 Uruchamianie serwera Astry...")
            self.server_process = subprocess.Popen(
                [sys.executable, "start_astra_pure.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Czekaj na uruchomienie serwera
            max_wait = 30
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self.base_url}/status", timeout=2)
                    if response.status_code == 200:
                        self.server_ready = True
                        print(f"✅ Serwer gotowy po {i+1} sekundach")
                        return True
                except:
                    pass
                time.sleep(1)
                print(f"⏳ Czekam na serwer... ({i+1}/{max_wait})")
            
            print("❌ Serwer nie wystartował w czasie")
            return False
            
        except Exception as e:
            print(f"❌ Błąd uruchamiania serwera: {e}")
            return False
    
    def stop_server(self):
        """Zatrzymuje serwer"""
        if self.server_process:
            print("🛑 Zatrzymywanie serwera...")
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ Serwer zatrzymany")
    
    def test_basic_endpoints(self) -> Dict[str, Any]:
        """Test podstawowych endpointów"""
        print("\n🔍 Test podstawowych endpointów")
        results = {"name": "basic_endpoints", "tests": []}
        
        endpoints = [
            ("/status", "GET", "Status systemu"),
            ("/realms", "GET", "Lista wymiarów"),
            ("/astral/meditate", "POST", "Medytacja systemu"),
        ]
        
        for endpoint, method, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}")
                else:
                    response = requests.post(f"{self.base_url}{endpoint}")
                
                success = response.status_code == 200
                results["tests"].append({
                    "endpoint": endpoint,
                    "method": method,
                    "description": description,
                    "status_code": response.status_code,
                    "success": success,
                    "response_size": len(response.text) if response.text else 0
                })
                
                status = "✅" if success else "❌"
                print(f"   {status} {method} {endpoint} - {description}")
                
            except Exception as e:
                results["tests"].append({
                    "endpoint": endpoint,
                    "method": method,
                    "description": description,
                    "error": str(e),
                    "success": False
                })
                print(f"   ❌ {method} {endpoint} - Błąd: {e}")
        
        return results
    
    def test_gpt_chat(self) -> Dict[str, Any]:
        """Test komunikacji GPT"""
        print("\n🤖 Test komunikacji GPT")
        results = {"name": "gpt_chat", "tests": []}
        
        test_messages = [
            "Witaj Astro! Jak się czujesz?",
            "Pokaż status systemu",
            "Wykonaj medytację",
            "Sprawdź wymiary astralne"
        ]
        
        for message in test_messages:
            try:
                response = requests.post(f"{self.base_url}/gpt/chat", json={
                    'message': message,
                    'user_id': 'test_user'
                })
                
                success = response.status_code == 200
                data = response.json() if success else {}
                
                results["tests"].append({
                    "message": message,
                    "status_code": response.status_code,
                    "success": success,
                    "response_length": len(data.get('astra_response', '')) if success else 0,
                    "actions_executed": data.get('actions_executed', 0) if success else 0
                })
                
                status = "✅" if success else "❌"
                print(f"   {status} '{message[:30]}...' -> {response.status_code}")
                
            except Exception as e:
                results["tests"].append({
                    "message": message,
                    "error": str(e),
                    "success": False
                })
                print(f"   ❌ '{message[:30]}...' -> Błąd: {e}")
        
        return results
    
    def test_intentions(self) -> Dict[str, Any]:
        """Test systemu intencji"""
        print("\n🎯 Test systemu intencji")
        results = {"name": "intentions", "tests": []}
        
        test_intentions = [
            {
                'essence': {
                    'name': 'TestHarmony',
                    'purpose': 'Test harmonii systemu',
                    'category': 'test'
                },
                'material': {
                    'test_level': 95,
                    'harmony_boost': True
                }
            },
            {
                'essence': {
                    'name': 'TestClarity',
                    'purpose': 'Test jasności systemu',
                    'category': 'test'
                },
                'material': {
                    'clarity_level': 85,
                    'focus_boost': True
                }
            }
        ]
        
        manifested_ids = []
        
        for intention_data in test_intentions:
            try:
                response = requests.post(f"{self.base_url}/astral/manifest", json=intention_data)
                
                success = response.status_code == 200
                data = response.json() if success else {}
                
                if success and data.get('success'):
                    manifested_ids.append(data.get('being_id'))
                
                results["tests"].append({
                    "intention_name": intention_data['essence']['name'],
                    "status_code": response.status_code,
                    "success": success,
                    "manifested": success and data.get('success', False),
                    "being_id": data.get('being_id') if success else None
                })
                
                status = "✅" if success else "❌"
                print(f"   {status} Manifestacja: {intention_data['essence']['name']}")
                
            except Exception as e:
                results["tests"].append({
                    "intention_name": intention_data['essence']['name'],
                    "error": str(e),
                    "success": False
                })
                print(f"   ❌ Manifestacja: {intention_data['essence']['name']} -> Błąd: {e}")
        
        # Test kontemplacji
        try:
            response = requests.post(f"{self.base_url}/realms/intentions/contemplate", json={
                'operation': 'find_all'
            })
            
            success = response.status_code == 200
            data = response.json() if success else {}
            
            results["tests"].append({
                "operation": "contemplate_all",
                "status_code": response.status_code,
                "success": success,
                "found_count": data.get('found', 0) if success else 0
            })
            
            status = "✅" if success else "❌"
            print(f"   {status} Kontemplacja wymiarów -> Znaleziono: {data.get('found', 0) if success else 0}")
            
        except Exception as e:
            results["tests"].append({
                "operation": "contemplate_all",
                "error": str(e),
                "success": False
            })
            print(f"   ❌ Kontemplacja wymiarów -> Błąd: {e}")
        
        return results
    
    def test_realms(self) -> Dict[str, Any]:
        """Test wymiarów astralnych"""
        print("\n🌍 Test wymiarów astralnych")
        results = {"name": "realms", "tests": []}
        
        try:
            response = requests.get(f"{self.base_url}/realms")
            
            success = response.status_code == 200
            data = response.json() if success else {}
            
            results["tests"].append({
                "operation": "list_realms",
                "status_code": response.status_code,
                "success": success,
                "realms_count": len(data) if success else 0,
                "realms": list(data.keys()) if success else []
            })
            
            status = "✅" if success else "❌"
            print(f"   {status} Lista wymiarów -> {len(data) if success else 0} wymiarów")
            
            if success:
                for realm_name, realm_info in data.items():
                    print(f"      🌟 {realm_name}: {realm_info.get('beings_count', '?')} bytów")
            
        except Exception as e:
            results["tests"].append({
                "operation": "list_realms",
                "error": str(e),
                "success": False
            })
            print(f"   ❌ Lista wymiarów -> Błąd: {e}")
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generuje raport z testów"""
        total_tests = 0
        passed_tests = 0
        
        for test_group in self.test_results:
            for test in test_group.get('tests', []):
                total_tests += 1
                if test.get('success', False):
                    passed_tests += 1
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_groups": self.test_results
        }
        
        return report
    
    def run_all_tests(self):
        """Uruchamia wszystkie testy"""
        print("🧪 LuxDB v2 - Kompletny Test Runner")
        print("=" * 60)
        
        # Uruchom serwer
        if not self.start_server():
            print("❌ Nie można uruchomić serwera - przerywam testy")
            return False
        
        try:
            # Uruchom testy
            self.test_results.append(self.test_basic_endpoints())
            self.test_results.append(self.test_gpt_chat())
            self.test_results.append(self.test_intentions())
            self.test_results.append(self.test_realms())
            
            # Generuj raport
            report = self.generate_report()
            
            # Wyświetl podsumowanie
            print("\n" + "="*60)
            print("📊 PODSUMOWANIE TESTÓW")
            print("="*60)
            print(f"🎯 Łącznie testów: {report['total_tests']}")
            print(f"✅ Zaliczone: {report['passed_tests']}")
            print(f"❌ Niezaliczone: {report['failed_tests']}")
            print(f"📈 Skuteczność: {report['success_rate']:.1f}%")
            
            # Zapisz raport
            with open('test_results.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Raport zapisany w: test_results.json")
            
            return report['success_rate'] > 50
            
        finally:
            self.stop_server()

if __name__ == "__main__":
    runner = AstraTestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 Testy zakończone pomyślnie!")
        sys.exit(0)
    else:
        print("\n⚠️ Niektóre testy nie przeszły")
        sys.exit(1)
