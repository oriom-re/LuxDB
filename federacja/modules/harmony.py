
"""
⚖️ Harmony Module - Harmonizacja Federacji

Port z LuxDB v2 - system balansowania i optymalizacji
"""

import time
from typing import Dict, Any, List
from datetime import datetime
from ..core.lux_module import LuxModule


class HarmonyModule(LuxModule):
    """Moduł harmonizacji systemu - portowany z LuxDB v2"""
    
    def __init__(self, kernel, config: Dict[str, Any], logger):
        super().__init__(kernel, config, logger)
        self.balance_history = []
        self.last_harmonization = None
        
    async def initialize(self) -> bool:
        """Inicjalizuje moduł harmony"""
        self.logger.info("⚖️ Harmony Module initializing...")
        return True
        
    async def start(self) -> bool:
        """Uruchamia moduł harmony"""
        self.logger.info("⚖️ Harmony Module started")
        return True
        
    async def stop(self):
        """Zatrzymuje moduł harmony"""
        self.logger.info("⚖️ Harmony Module stopped")
        
    def harmonize(self) -> Dict[str, Any]:
        """Główny proces harmonizacji"""
        start_time = time.time()
        
        actions_taken = []
        recommendations = []
        
        # Oceń stan przed harmonizacją
        harmony_before = self.calculate_harmony_score()
        
        try:
            # Harmonizuj moduły
            module_actions = self._harmonize_modules()
            actions_taken.extend(module_actions)
            
            # Optymalizuj pamięć
            memory_actions = self._optimize_memory()
            actions_taken.extend(memory_actions)
            
            # Sprawdź komunikację
            comm_recommendations = self._check_communication()
            recommendations.extend(comm_recommendations)
            
        except Exception as e:
            actions_taken.append(f"❌ Błąd harmonizacji: {e}")
            
        # Oceń stan po harmonizacji
        harmony_after = self.calculate_harmony_score()
        improvement = harmony_after - harmony_before
        
        duration = time.time() - start_time
        self.last_harmonization = datetime.now()
        
        harmony_report = {
            'timestamp': self.last_harmonization.isoformat(),
            'duration': duration,
            'harmony_before': harmony_before,
            'harmony_after': harmony_after,
            'improvement': improvement,
            'actions_taken': actions_taken,
            'recommendations': recommendations
        }
        
        self.balance_history.append(harmony_report)
        
        # Ogranicz historię
        if len(self.balance_history) > 50:
            self.balance_history = self.balance_history[-50:]
            
        return harmony_report
        
    def calculate_harmony_score(self) -> float:
        """Oblicza wynik harmonii systemu (0-100)"""
        if not self.kernel:
            return 0.0
            
        scores = []
        
        # Wynik modułów (40% wagi)
        module_score = self._calculate_module_harmony()
        scores.append(('modules', module_score, 0.4))
        
        # Wynik komunikacji (30% wagi)  
        comm_score = self._calculate_communication_harmony()
        scores.append(('communication', comm_score, 0.3))
        
        # Wynik wydajności (20% wagi)
        perf_score = self._calculate_performance_harmony()
        scores.append(('performance', perf_score, 0.2))
        
        # Wynik konfiguracji (10% wagi)
        config_score = self._calculate_config_harmony()
        scores.append(('config', config_score, 0.1))
        
        # Oblicz ważoną średnią
        total_score = sum(score * weight for _, score, weight in scores)
        
        return min(100.0, max(0.0, total_score))
        
    def _calculate_module_harmony(self) -> float:
        """Oblicza harmonię modułów"""
        if not self.kernel.modules:
            return 0.0
            
        total_score = 0.0
        active_modules = 0
        
        for name, module in self.kernel.modules.items():
            module_score = 100.0
            
            # Sprawdź czy moduł działa
            if hasattr(module, 'is_running') and not module.is_running:
                module_score -= 50.0
                
            # Sprawdź czy ma błędy
            if hasattr(module, 'has_errors') and module.has_errors():
                module_score -= 30.0
                
            total_score += max(0.0, module_score)
            active_modules += 1
            
        return total_score / active_modules if active_modules > 0 else 0.0
        
    def _calculate_communication_harmony(self) -> float:
        """Oblicza harmonię komunikacji"""
        if not hasattr(self.kernel, 'bus'):
            return 0.0
            
        score = 100.0
        
        # Sprawdź czy bus działa
        if not getattr(self.kernel.bus, 'is_running', True):
            score -= 50.0
            
        # Sprawdź liczbę subskrybentów
        subscribers = getattr(self.kernel.bus, 'subscribers', {})
        if len(subscribers) < 2:
            score -= 20.0
            
        return max(0.0, score)
        
    def _calculate_performance_harmony(self) -> float:
        """Oblicza harmonię wydajności"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
            
            # Wynik na podstawie użycia zasobów
            memory_score = max(0, 100 - memory.percent)
            cpu_score = max(0, 100 - cpu)
            
            return (memory_score + cpu_score) / 2
        except:
            return 75.0  # Domyślny wynik
            
    def _calculate_config_harmony(self) -> float:
        """Oblicza harmonię konfiguracji"""
        if not hasattr(self.kernel, 'config'):
            return 50.0
            
        score = 100.0
        
        # Sprawdź czy konfiguracja jest kompletna
        config = self.kernel.config
        if not hasattr(config, 'kernel_name') or not config.kernel_name:
            score -= 25.0
            
        return max(0.0, score)
        
    def _harmonize_modules(self) -> List[str]:
        """Harmonizuje moduły"""
        actions = []
        
        for name, module in self.kernel.modules.items():
            try:
                # Sprawdź czy moduł potrzebuje restartu
                if hasattr(module, 'needs_restart') and module.needs_restart():
                    if hasattr(module, 'restart'):
                        module.restart()
                        actions.append(f"🔄 Restart modułu '{name}'")
                        
                # Sprawdź czy moduł potrzebuje optymalizacji
                if hasattr(module, 'optimize'):
                    module.optimize()
                    actions.append(f"✨ Optymalizacja modułu '{name}'")
                    
            except Exception as e:
                actions.append(f"❌ Błąd harmonizacji modułu '{name}': {e}")
                
        return actions
        
    def _optimize_memory(self) -> List[str]:
        """Optymalizuje użycie pamięci"""
        actions = []
        
        try:
            # Wyczyść stare obserwacje z consciousness
            consciousness = self.kernel.modules.get('consciousness')
            if consciousness and hasattr(consciousness, 'observations'):
                if len(consciousness.observations) > 50:
                    consciousness.observations = consciousness.observations[-30:]
                    actions.append("🧠 Oczyszczono historię consciousness")
                    
            # Wyczyść historię harmonii
            if len(self.balance_history) > 30:
                self.balance_history = self.balance_history[-20:]
                actions.append("⚖️ Oczyszczono historię harmonizacji")
                
        except Exception as e:
            actions.append(f"❌ Błąd optymalizacji pamięci: {e}")
            
        return actions
        
    def _check_communication(self) -> List[str]:
        """Sprawdza komunikację między modułami"""
        recommendations = []
        
        if not hasattr(self.kernel, 'bus'):
            recommendations.append("Brak systemu komunikacji - rozważ implementację")
            return recommendations
            
        bus = self.kernel.bus
        
        # Sprawdź subskrybentów
        subscribers = getattr(bus, 'subscribers', {})
        if len(subscribers) < len(self.kernel.modules):
            recommendations.append("Nie wszystkie moduły subskrybują komunikaty")
            
        return recommendations
        
    def balance(self) -> None:
        """Szybkie balansowanie - uproszczona wersja harmonize"""
        try:
            # Szybka kontrola modułów
            for name, module in self.kernel.modules.items():
                if hasattr(module, 'quick_check'):
                    module.quick_check()
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Błąd podczas szybkiego balansowania: {e}")
            
    def get_status(self) -> Dict[str, Any]:
        """Status modułu harmony"""
        return {
            'last_harmonization': self.last_harmonization.isoformat() if self.last_harmonization else None,
            'current_harmony_score': self.calculate_harmony_score(),
            'balance_history_count': len(self.balance_history),
            'recent_improvements': [h['improvement'] for h in self.balance_history[-5:]]
        }
