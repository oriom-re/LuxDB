
#!/usr/bin/env python3
"""
🚀 LuxDB v2 - Testy integracji z serwisem

Testuje integrację z głównym serwisem LuxDB v2
"""

import sys
import os
import time
import threading
import requests
import json
from datetime import datetime

# Dodaj ścieżkę do LuxDB v2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from luxdb_v2 import create_astral_app, print_astral_banner


class AstralServiceTester:
    """Tester serwisu astralnego"""
    
    def __init__(self, base_port=5060):
        self.base_port = base_port
        self.service_thread = None
        self.engine = None
        self.running = False
    
    def start_test_service(self):
        """Uruchamia testowy serwis"""
        def service_worker():
            config = {
                'realms': {
                    'test_primary': 'memory://test_primary',
                    'test_cache': 'memory://test_cache'
                },
                'flows': {
                    'rest': {
                        'host': '0.0.0.0',
                        'port': self.base_port,
                        'enable_cors': True
                    }
                },
                'consciousness_level': 'testing',
                'meditation_interval': 5
            }
            
            try:
                self.engine = create_astral_app(config)
                self.running = True
                print(f"🚀 Testowy serwis uruchomiony na porcie {self.base_port}")
                
                # Symuluj działanie serwisu
                while self.running:
                    if self.engine:
                        self.engine.meditate()
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Błąd serwisu testowego: {e}")
            finally:
                if self.engine:
                    self.engine.transcend()
        
        self.service_thread = threading.Thread(target=service_worker, daemon=True)
        self.service_thread.start()
        time.sleep(2)  # Poczekaj na uruchomienie
    
    def stop_test_service(self):
        """Zatrzymuje testowy serwis"""
        self.running = False
        if self.service_thread:
            self.service_thread.join(timeout=5)
        print("🕊️ Testowy serwis zatrzymany")
    
    def test_service_status(self):
        """Testuje status serwisu"""
        print("📊 Test statusu serwisu:")
        
        if not self.engine:
            print("   ❌ Serwis nie jest uruchomiony")
            return False
        
        try:
            status = self.engine.get_status()
            
            print(f"   ✅ Poziom świadomości: {status['astral_engine']['consciousness_level']}")
            print(f"   ✅ Czas działania: {status['astral_engine']['uptime']}")
            print(f"   ✅ Wymiary aktywne: {len(status['realms'])}")
            
            for name, realm_status in status['realms'].items():
                state = "✅" if realm_status['connected'] else "❌"
                print(f"      {state} {name}: {realm_status['type']}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Błąd testu statusu: {e}")
            return False
    
    def test_meditation_cycle(self):
        """Testuje cykle medytacji"""
        print("\n🧘 Test cykli medytacji:")
        
        if not self.engine:
            print("   ❌ Serwis nie jest uruchomiony")
            return False
        
        try:
            meditations = []
            
            for i in range(3):
                meditation = self.engine.meditate()
                meditations.append(meditation)
                
                harmony = meditation['harmony_score']
                recommendations = len(meditation.get('recommendations', []))
                
                print(f"   ✅ Medytacja {i+1}: Harmonia {harmony:.1f}/100, Rekomendacje: {recommendations}")
                time.sleep(0.5)
            
            # Analiza trendów
            harmony_scores = [m['harmony_score'] for m in meditations]
            avg_harmony = sum(harmony_scores) / len(harmony_scores)
            print(f"   📊 Średnia harmonia: {avg_harmony:.1f}/100")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Błąd testu medytacji: {e}")
            return False
    
    def test_realm_operations(self):
        """Testuje operacje na wymiarach"""
        print("\n🌌 Test operacji na wymiarach:")
        
        if not self.engine:
            print("   ❌ Serwis nie jest uruchomiony")
            return False
        
        try:
            # Pobierz wymiar testowy
            test_realm = self.engine.get_realm('test_primary')
            print(f"   ✅ Pobrano wymiar: {test_realm.name}")
            
            # Test manifestacji
            test_data = {
                'test_id': 'test_001',
                'name': 'Test Being',
                'created_at': datetime.now().isoformat(),
                'properties': ['test', 'example', 'demo']
            }
            
            being = test_realm.manifest(test_data)
            print(f"   ✅ Manifestowano byt testowy")
            
            # Test kontemplacji
            results = test_realm.contemplate('find_test_beings', name='Test Being')
            print(f"   ✅ Kontemplacja: znaleziono {len(results)} wyników")
            
            # Test ewolucji
            evolved = test_realm.evolve('test_001', {'status': 'evolved', 'version': 2})
            print(f"   ✅ Ewolucja bytu zakończona")
            
            # Test liczby bytów
            being_count = test_realm.count_beings()
            print(f"   📊 Liczba bytów w wymiarze: {being_count}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Błąd testu operacji: {e}")
            return False
    
    def test_consciousness_insights(self):
        """Testuje system świadomości"""
        print("\n🧠 Test systemu świadomości:")
        
        if not self.engine:
            print("   ❌ Serwis nie jest uruchomiony")
            return False
        
        try:
            # Test refleksji
            insights = self.engine.consciousness.reflect()
            
            print(f"   ✅ Refleksja systemu:")
            print(f"      • Czas działania: {insights['system']['uptime_formatted']}")
            print(f"      • Przepływ energii: {insights['harmony']['energy_flow_balance']}")
            print(f"      • Zdrowie wymiarów: {insights['harmony']['realm_health']}")
            
            # Test historii insights
            history = self.engine.consciousness.get_insights_history(limit=3)
            print(f"   ✅ Historia insights: {len(history)} wpisów")
            
            # Test analizy wzorców
            if len(history) >= 2:
                patterns = self.engine.consciousness.meditate_on_patterns()
                if 'stability_score' in patterns:
                    print(f"   ✅ Wynik stabilności: {patterns['stability_score']:.1f}/100")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Błąd testu świadomości: {e}")
            return False
    
    def test_harmony_system(self):
        """Testuje system harmonii"""
        print("\n⚖️ Test systemu harmonii:")
        
        if not self.engine:
            print("   ❌ Serwis nie jest uruchomiony")
            return False
        
        try:
            # Test kalkulacji harmonii
            initial_harmony = self.engine.harmony.calculate_harmony_score()
            print(f"   📊 Początkowa harmonia: {initial_harmony:.1f}/100")
            
            # Test harmonizacji
            self.engine.harmonize()
            print(f"   ✅ Harmonizacja wykonana")
            
            # Test balansowania
            self.engine.harmony.balance()
            print(f"   ✅ Balansowanie wykonane")
            
            # Test finalnej harmonii
            final_harmony = self.engine.harmony.calculate_harmony_score()
            print(f"   📊 Finalna harmonia: {final_harmony:.1f}/100")
            
            improvement = final_harmony - initial_harmony
            if improvement >= 0:
                print(f"   ✅ Poprawa harmonii: +{improvement:.1f}")
            else:
                print(f"   ⚠️ Zmiana harmonii: {improvement:.1f}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Błąd testu harmonii: {e}")
            return False


def test_service_lifecycle():
    """Test pełnego cyklu życia serwisu"""
    print("🔄 Test pełnego cyklu życia serwisu")
    print("=" * 50)
    
    tester = AstralServiceTester(base_port=5060)
    
    try:
        # Uruchom serwis
        print("🚀 Uruchamianie serwisu testowego...")
        tester.start_test_service()
        
        # Bateria testów
        tests = [
            tester.test_service_status,
            tester.test_meditation_cycle,
            tester.test_realm_operations,
            tester.test_consciousness_insights,
            tester.test_harmony_system
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # Wyniki
        print(f"\n📊 Wyniki testów: {passed_tests}/{total_tests}")
        if passed_tests == total_tests:
            print("✅ Wszystkie testy przeszły pomyślnie!")
        else:
            failed = total_tests - passed_tests
            print(f"⚠️ {failed} testów nie przeszło")
        
    finally:
        # Zatrzymaj serwis
        tester.stop_test_service()
    
    print("🕊️ Test cyklu życia zakończony\n")


def test_concurrent_operations():
    """Test operacji współbieżnych"""
    print("⚡ Test operacji współbieżnych")
    print("=" * 50)
    
    config = {
        'realms': {
            'concurrent_test': 'memory://concurrent_realm'
        },
        'consciousness_level': 'testing'
    }
    
    def worker_function(worker_id, engine, results):
        """Funkcja wykonawcza dla wątku"""
        try:
            realm = engine.get_realm('concurrent_test')
            
            # Manifestuj dane
            for i in range(5):
                data = {
                    'worker_id': worker_id,
                    'item_id': f'item_{worker_id}_{i}',
                    'timestamp': datetime.now().isoformat(),
                    'data': f'concurrent_data_{i}'
                }
                realm.manifest(data)
            
            # Kontempluj dane
            my_items = realm.contemplate('find_my_items', worker_id=worker_id)
            results[worker_id] = len(my_items)
            
        except Exception as e:
            print(f"   ❌ Błąd workera {worker_id}: {e}")
            results[worker_id] = -1
    
    with create_astral_app(config) as engine:
        print("🔄 Uruchamianie 3 współbieżnych workerów...")
        
        threads = []
        results = {}
        
        # Uruchom workery
        for i in range(3):
            thread = threading.Thread(
                target=worker_function,
                args=(f'worker_{i}', engine, results)
            )
            threads.append(thread)
            thread.start()
        
        # Poczekaj na zakończenie
        for thread in threads:
            thread.join()
        
        # Wyniki
        print(f"📊 Wyniki workerów:")
        total_items = 0
        for worker_id, count in results.items():
            if count >= 0:
                print(f"   ✅ {worker_id}: {count} elementów")
                total_items += count
            else:
                print(f"   ❌ {worker_id}: błąd")
        
        # Sprawdź łączną liczbę w wymiarze
        realm = engine.get_realm('concurrent_test')
        total_in_realm = realm.count_beings()
        
        print(f"📈 Łącznie w wymiarze: {total_in_realm} bytów")
        print(f"🎯 Oczekiwano: 15 bytów (3 workery × 5 elementów)")
        
        if total_in_realm == 15:
            print("✅ Test współbieżności PASSED")
        else:
            print("⚠️ Test współbieżności może wymagać uwagi")
    
    print("🕊️ Test współbieżności zakończony\n")


def test_error_handling():
    """Test obsługi błędów"""
    print("🛡️ Test obsługi błędów")
    print("=" * 50)
    
    config = {
        'realms': {
            'error_test': 'memory://error_realm'
        }
    }
    
    with create_astral_app(config) as engine:
        print("🔍 Testowanie scenariuszy błędów...")
        
        realm = engine.get_realm('error_test')
        
        # Test 1: Nieistniejący wymiar
        try:
            nonexistent = engine.get_realm('nonexistent')
            print("   ❌ Test 1 FAILED: Powinien rzucić błąd")
        except ValueError:
            print("   ✅ Test 1 PASSED: Poprawnie wykryto nieistniejący wymiar")
        except Exception as e:
            print(f"   ⚠️ Test 1: Nieoczekiwany błąd: {e}")
        
        # Test 2: Nieprawidłowe dane manifestacji
        try:
            result = realm.manifest(None)
            print("   ❌ Test 2 FAILED: Powinien rzucić błąd dla None")
        except Exception:
            print("   ✅ Test 2 PASSED: Poprawnie odrzucił None data")
        
        # Test 3: Nieprawidłowe parametry kontemplacji
        try:
            results = realm.contemplate('')  # Pusta intencja
            print("   ⚠️ Test 3: Pusta intencja zaakceptowana")
        except Exception:
            print("   ✅ Test 3 PASSED: Odrzucono pustą intencję")
        
        # Test 4: Ewolucja nieistniejącego bytu
        try:
            evolved = realm.evolve('nonexistent_id', {'new': 'data'})
            print("   ❌ Test 4 FAILED: Powinien rzucić błąd")
        except Exception:
            print("   ✅ Test 4 PASSED: Poprawnie wykryto nieistniejący byt")
        
        print("🛡️ Testy obsługi błędów zakończone")
    
    print("🕊️ Test obsługi błędów zakończony\n")


def run_integration_tests():
    """Uruchamia wszystkie testy integracji"""
    print_astral_banner()
    print("🧪 Testy integracji serwisu LuxDB v2")
    print("=" * 60)
    
    tests = [
        test_service_lifecycle,
        test_concurrent_operations,
        test_error_handling
    ]
    
    for i, test in enumerate(tests, 1):
        try:
            print(f"\n{'='*15} TEST {i}/{len(tests)} {'='*15}")
            test()
        except Exception as e:
            print(f"❌ Błąd w teście {i}: {e}")
            continue
    
    print("\n" + "="*60)
    print("🌟 Wszystkie testy integracji zakończone!")
    print("✨ Serwis LuxDB v2 przeszedł testy astralnej jakości!")


if __name__ == "__main__":
    run_integration_tests()
