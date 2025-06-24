
#!/usr/bin/env python3
"""
🧪 Testy jednostkowe AstralEngine

Testuje podstawową funkcjonalność silnika astralnego
"""

import unittest
import time
import threading
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from luxdb_v2 import AstralEngine, AstralConfig


class TestAstralEngine(unittest.TestCase):
    """Testy AstralEngine"""
    
    def setUp(self):
        """Przygotowanie przed każdym testem"""
        self.config = AstralConfig()
        self.config.realms = {
            'test_realm': 'memory://test_realm'
        }
        self.config.meditation_interval = 60  # Długi interval dla testów
        self.config.harmony_check_interval = 60
        
        self.engine = AstralEngine(self.config)
    
    def tearDown(self):
        """Sprzątanie po każdym teście"""
        if self.engine and self.engine._running:
            self.engine.transcend()
    
    def test_engine_initialization(self):
        """Test inicjalizacji silnika"""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.consciousness)
        self.assertIsNotNone(self.engine.harmony)
        self.assertEqual(len(self.engine.realms), 0)  # Przed awaken
    
    def test_engine_awaken(self):
        """Test przebudzenia silnika"""
        self.engine.awaken()
        
        self.assertTrue(self.engine._running)
        self.assertIsNotNone(self.engine.state.awakened_at)
        self.assertEqual(len(self.engine.realms), 1)
        self.assertIn('test_realm', self.engine.realms)
    
    def test_engine_transcend(self):
        """Test transcendencji (shutdown) silnika"""
        self.engine.awaken()
        self.assertTrue(self.engine._running)
        
        self.engine.transcend()
        self.assertFalse(self.engine._running)
        self.assertTrue(self.engine.state.is_transcended)
    
    def test_meditation(self):
        """Test funkcji medytacji"""
        self.engine.awaken()
        
        meditation = self.engine.meditate()
        
        self.assertIsInstance(meditation, dict)
        self.assertIn('timestamp', meditation)
        self.assertIn('system_state', meditation)
        self.assertIn('harmony_score', meditation)
        self.assertIn('recommendations', meditation)
        
        # Sprawdź czy harmonia jest liczbą między 0 a 100
        harmony = meditation['harmony_score']
        self.assertIsInstance(harmony, (int, float))
        self.assertGreaterEqual(harmony, 0)
        self.assertLessEqual(harmony, 100)
    
    def test_realm_operations(self):
        """Test operacji na wymiarach"""
        self.engine.awaken()
        
        # Test get_realm
        realm = self.engine.get_realm('test_realm')
        self.assertIsNotNone(realm)
        self.assertEqual(realm.name, 'test_realm')
        
        # Test list_realms
        realms = self.engine.list_realms()
        self.assertIn('test_realm', realms)
        
        # Test tworzenia nowego wymiaru
        new_realm = self.engine.create_realm('new_test_realm', 'memory://new_test')
        self.assertIsNotNone(new_realm)
        self.assertEqual(len(self.engine.realms), 2)
    
    def test_invalid_realm_access(self):
        """Test dostępu do nieistniejącego wymiaru"""
        self.engine.awaken()
        
        with self.assertRaises(ValueError):
            self.engine.get_realm('nonexistent_realm')
    
    def test_status_reporting(self):
        """Test raportowania statusu"""
        self.engine.awaken()
        
        status = self.engine.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('astral_engine', status)
        self.assertIn('system_state', status)
        self.assertIn('realms', status)
        self.assertIn('harmony', status)
        
        engine_status = status['astral_engine']
        self.assertEqual(engine_status['version'], '2.0.0')
        self.assertTrue(engine_status['running'])
    
    def test_context_manager(self):
        """Test użycia jako context manager"""
        with AstralEngine(self.config) as engine:
            self.assertTrue(engine._running)
            self.assertGreater(len(engine.realms), 0)
        
        self.assertFalse(engine._running)
    
    def test_concurrent_meditations(self):
        """Test współbieżnych medytacji"""
        self.engine.awaken()
        
        results = []
        
        def meditation_worker():
            result = self.engine.meditate()
            results.append(result)
        
        # Uruchom 3 równoczesne medytacje
        threads = []
        for i in range(3):
            thread = threading.Thread(target=meditation_worker)
            threads.append(thread)
            thread.start()
        
        # Poczekaj na zakończenie
        for thread in threads:
            thread.join()
        
        # Sprawdź wyniki
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIn('harmony_score', result)
    
    def test_configuration_loading(self):
        """Test ładowania różnych typów konfiguracji"""
        # Test z dict
        dict_config = {
            'realms': {'test': 'memory://test'},
            'consciousness_level': 'testing'
        }
        engine_dict = AstralEngine(dict_config)
        self.assertEqual(engine_dict.config.consciousness_level, 'testing')
        
        # Test z AstralConfig
        astral_config = AstralConfig()
        astral_config.consciousness_level = 'enlightened'
        engine_astral = AstralEngine(astral_config)
        self.assertEqual(engine_astral.config.consciousness_level, 'enlightened')
        
        # Test z None (domyślna konfiguracja)
        engine_none = AstralEngine(None)
        self.assertIsNotNone(engine_none.config)


class TestAstralEngineIntegration(unittest.TestCase):
    """Testy integracyjne AstralEngine"""
    
    def test_full_lifecycle(self):
        """Test pełnego cyklu życia systemu"""
        config = AstralConfig()
        config.realms = {
            'primary': 'memory://primary',
            'cache': 'memory://cache'
        }
        
        with AstralEngine(config) as engine:
            # System powinien być aktywny
            self.assertTrue(engine._running)
            self.assertEqual(len(engine.realms), 2)
            
            # Pierwsza medytacja
            meditation1 = engine.meditate()
            self.assertIsInstance(meditation1['harmony_score'], (int, float))
            
            # Operacje na wymiarze
            primary_realm = engine.get_realm('primary')
            test_data = {'test_id': 1, 'name': 'Integration Test'}
            being = primary_realm.manifest(test_data)
            self.assertIsNotNone(being)
            
            # Druga medytacja po operacji
            meditation2 = engine.meditate()
            self.assertIsInstance(meditation2['harmony_score'], (int, float))
            
            # Status systemu
            status = engine.get_status()
            self.assertTrue(status['astral_engine']['running'])
            self.assertEqual(len(status['realms']), 2)
        
        # Po wyjściu z context managera system powinien być zatrzymany
        self.assertFalse(engine._running)
    
    def test_error_recovery(self):
        """Test odzyskiwania po błędach"""
        config = AstralConfig()
        config.realms = {'test': 'memory://test'}
        
        with AstralEngine(config) as engine:
            # Symuluj błąd w wymiarze
            test_realm = engine.get_realm('test')
            
            # Nawet po błędzie system powinien działać
            try:
                # Próba nieprawidłowej operacji
                test_realm.evolve('nonexistent_id', {'data': 'test'})
            except Exception:
                pass  # Oczekiwany błąd
            
            # System nadal powinien być funkcjonalny
            meditation = engine.meditate()
            self.assertIsInstance(meditation, dict)
            self.assertIn('harmony_score', meditation)


if __name__ == '__main__':
    unittest.main()
