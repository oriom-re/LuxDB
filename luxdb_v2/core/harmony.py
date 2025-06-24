
"""
⚖️ Harmony - Harmonizator Astralnego Systemu

Odpowiada za:
- Balansowanie obciążenia
- Optymalizację wydajności
- Synchronizację komponentów
- Utrzymanie równowagi energetycznej
"""

import time
import threading
from typing import Dict, Any, List
from datetime import datetime


class Harmony:
    """
    Harmonizator systemu - utrzymuje równowagę wszystkich komponentów
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        self.balance_history: List[Dict[str, Any]] = []
        self.last_harmonization = None
        self._lock = threading.Lock()
    
    def harmonize(self) -> Dict[str, Any]:
        """
        Główny proces harmonizacji systemu
        
        Returns:
            Raport z harmonizacji
        """
        with self._lock:
            start_time = time.time()
            
            # Przygotuj raport harmonizacji
            harmony_report = {
                'timestamp': datetime.now().isoformat(),
                'actions_taken': [],
                'recommendations': [],
                'harmony_score_before': self.calculate_harmony_score(),
                'duration': 0
            }
            
            try:
                # 1. Harmonizuj wymiary
                realm_actions = self._harmonize_realms()
                harmony_report['actions_taken'].extend(realm_actions)
                
                # 2. Harmonizuj przepływy
                flow_actions = self._harmonize_flows()
                harmony_report['actions_taken'].extend(flow_actions)
                
                # 3. Optymalizuj pamięć
                memory_actions = self._optimize_memory()
                harmony_report['actions_taken'].extend(memory_actions)
                
                # 4. Sprawdź integrację
                integration_recommendations = self._check_integration()
                harmony_report['recommendations'].extend(integration_recommendations)
                
                # Oblicz końcowy wynik harmonii
                harmony_report['harmony_score_after'] = self.calculate_harmony_score()
                harmony_report['improvement'] = (
                    harmony_report['harmony_score_after'] - 
                    harmony_report['harmony_score_before']
                )
                
            except Exception as e:
                harmony_report['error'] = str(e)
                harmony_report['actions_taken'].append(f"❌ Błąd harmonizacji: {e}")
            
            finally:
                harmony_report['duration'] = time.time() - start_time
                self.last_harmonization = datetime.now()
                
                # Zapisz w historii
                self.balance_history.append(harmony_report)
                if len(self.balance_history) > 50:
                    self.balance_history = self.balance_history[-50:]
            
            return harmony_report
    
    def balance(self) -> None:
        """Szybkie balansowanie - uproszczona wersja harmonize"""
        if not self.engine._running:
            return
        
        try:
            # Szybka kontrola wymiarów
            for realm_name, realm in self.engine.realms.items():
                if hasattr(realm, 'optimize'):
                    realm.optimize()
            
            # Kontrola przepływów
            if self.engine.rest_flow and hasattr(self.engine.rest_flow, 'balance_load'):
                self.engine.rest_flow.balance_load()
            
        except Exception as e:
            self.engine.logger.warning(f"⚠️ Błąd podczas szybkiego balansowania: {e}")
    
    def calculate_harmony_score(self) -> float:
        """
        Oblicza ogólny wynik harmonii systemu (0-100)
        
        Returns:
            Wynik harmonii w skali 0-100
        """
        if not self.engine.realms:
            return 0.0
        
        scores = []
        
        # 1. Wynik wymiarów (40% wagi)
        realm_score = self._calculate_realm_harmony()
        scores.append(('realms', realm_score, 0.4))
        
        # 2. Wynik przepływów (30% wagi)
        flow_score = self._calculate_flow_harmony()
        scores.append(('flows', flow_score, 0.3))
        
        # 3. Wynik wydajności (20% wagi)
        performance_score = self._calculate_performance_harmony()
        scores.append(('performance', performance_score, 0.2))
        
        # 4. Wynik integracji (10% wagi)
        integration_score = self._calculate_integration_harmony()
        scores.append(('integration', integration_score, 0.1))
        
        # Oblicz ważoną średnią
        total_score = sum(score * weight for _, score, weight in scores)
        
        return min(100.0, max(0.0, total_score))
    
    def _calculate_realm_harmony(self) -> float:
        """Oblicza harmonię wymiarów"""
        if not self.engine.realms:
            return 0.0
        
        total_score = 0.0
        
        for realm in self.engine.realms.values():
            realm_score = 100.0  # Bazowy wynik
            
            # Sprawdź czy wymiar jest aktywny
            if hasattr(realm, 'is_active') and not realm.is_active():
                realm_score -= 30.0
            
            # Sprawdź zdrowie połączenia
            if hasattr(realm, 'is_healthy') and not realm.is_healthy():
                realm_score -= 40.0
            
            # Sprawdź obciążenie
            if hasattr(realm, 'get_load') and realm.get_load() > 0.8:
                realm_score -= 20.0
            
            total_score += max(0.0, realm_score)
        
        return total_score / len(self.engine.realms)
    
    def _calculate_flow_harmony(self) -> float:
        """Oblicza harmonię przepływów"""
        flows = [
            self.engine.rest_flow,
            self.engine.ws_flow,
            self.engine.callback_flow
        ]
        
        active_flows = sum(1 for flow in flows if flow is not None)
        
        if active_flows == 0:
            return 0.0
        elif active_flows == 1:
            return 40.0
        elif active_flows == 2:
            return 70.0
        else:
            return 100.0
    
    def _calculate_performance_harmony(self) -> float:
        """Oblicza harmonię wydajności"""
        try:
            # Sprawdź insights z consciousness
            if hasattr(self.engine, 'consciousness'):
                insights = self.engine.consciousness.reflect()
                
                memory_percent = insights['system']['memory_usage']['percent']
                cpu_percent = insights['system']['cpu_usage']
                
                # Oblicz wynik na podstawie użycia zasobów
                memory_score = max(0, 100 - memory_percent)
                cpu_score = max(0, 100 - cpu_percent)
                
                return (memory_score + cpu_score) / 2
            else:
                return 75.0  # Domyślny wynik jeśli brak danych
                
        except Exception:
            return 50.0  # Bezpieczny domyślny wynik
    
    def _calculate_integration_harmony(self) -> float:
        """Oblicza harmonię integracji komponentów"""
        integration_score = 100.0
        
        # Sprawdź czy wszystkie główne komponenty są zintegrowane
        if not hasattr(self.engine, 'consciousness'):
            integration_score -= 25.0
        
        if not hasattr(self.engine, 'harmony'):
            integration_score -= 25.0
        
        if not self.engine.realms:
            integration_score -= 30.0
        
        # Sprawdź czy przepływy są właściwie skonfigurowane
        if not any([self.engine.rest_flow, self.engine.ws_flow, self.engine.callback_flow]):
            integration_score -= 20.0
        
        return max(0.0, integration_score)
    
    def _harmonize_realms(self) -> List[str]:
        """Harmonizuje wymiary danych"""
        actions = []
        
        for realm_name, realm in self.engine.realms.items():
            try:
                # Sprawdź czy wymiar potrzebuje optymalizacji
                if hasattr(realm, 'needs_optimization') and realm.needs_optimization():
                    if hasattr(realm, 'optimize'):
                        realm.optimize()
                        actions.append(f"✨ Zoptymalizowano wymiar '{realm_name}'")
                
                # Sprawdź połączenie
                if hasattr(realm, 'test_connection'):
                    if not realm.test_connection():
                        if hasattr(realm, 'reconnect'):
                            realm.reconnect()
                            actions.append(f"🔄 Odnowiono połączenie z wymiarem '{realm_name}'")
                
            except Exception as e:
                actions.append(f"❌ Błąd harmonizacji wymiaru '{realm_name}': {e}")
        
        return actions
    
    def _harmonize_flows(self) -> List[str]:
        """Harmonizuje przepływy komunikacji"""
        actions = []
        
        flows = [
            ('REST', self.engine.rest_flow),
            ('WebSocket', self.engine.ws_flow),
            ('Callback', self.engine.callback_flow)
        ]
        
        for flow_name, flow in flows:
            if flow is None:
                continue
                
            try:
                # Sprawdź stan przepływu
                if hasattr(flow, 'is_healthy') and not flow.is_healthy():
                    if hasattr(flow, 'heal'):
                        flow.heal()
                        actions.append(f"💚 Uzdrowiono przepływ {flow_name}")
                
                # Optymalizuj jeśli możliwe
                if hasattr(flow, 'optimize'):
                    flow.optimize()
                    actions.append(f"⚡ Zoptymalizowano przepływ {flow_name}")
                
            except Exception as e:
                actions.append(f"❌ Błąd harmonizacji przepływu {flow_name}: {e}")
        
        return actions
    
    def _optimize_memory(self) -> List[str]:
        """Optymalizuje użycie pamięci"""
        actions = []
        
        try:
            # Sprawdź czy consciousness może zwolnić pamięć
            if hasattr(self.engine, 'consciousness'):
                if len(self.engine.consciousness.observations) > 50:
                    self.engine.consciousness.observations = self.engine.consciousness.observations[-30:]
                    actions.append("🧠 Oczyszczono historię obserwacji consciousness")
            
            # Oczyszczenie historii harmonii
            if len(self.balance_history) > 30:
                self.balance_history = self.balance_history[-20:]
                actions.append("⚖️ Oczyszczono historię harmonizacji")
            
        except Exception as e:
            actions.append(f"❌ Błąd optymalizacji pamięci: {e}")
        
        return actions
    
    def _check_integration(self) -> List[str]:
        """Sprawdza integrację komponentów"""
        recommendations = []
        
        # Sprawdź czy wszystkie komponenty są aktywne
        if not self.engine.realms:
            recommendations.append("Utwórz przynajmniej jeden wymiar danych")
        
        if not any([self.engine.rest_flow, self.engine.ws_flow]):
            recommendations.append("Aktywuj przynajmniej jeden przepływ komunikacji")
        
        # Sprawdź czy consciousness działa
        if hasattr(self.engine, 'consciousness'):
            try:
                self.engine.consciousness.reflect()
            except Exception:
                recommendations.append("Sprawdź działanie modułu consciousness")
        
        return recommendations
    
    def get_harmony_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Zwraca historię harmonizacji"""
        return self.balance_history[-limit:]
    
    def get_harmony_trends(self) -> Dict[str, Any]:
        """Analizuje trendy harmonii"""
        if len(self.balance_history) < 3:
            return {'message': 'Potrzeba więcej danych historycznych'}
        
        recent_scores = [
            record.get('harmony_score_after', 0) 
            for record in self.balance_history[-10:]
        ]
        
        # Oblicz trend
        if len(recent_scores) >= 2:
            trend = 'improving' if recent_scores[-1] > recent_scores[0] else 'declining'
            if abs(recent_scores[-1] - recent_scores[0]) < 5:
                trend = 'stable'
        else:
            trend = 'unknown'
        
        return {
            'current_score': recent_scores[-1] if recent_scores else 0,
            'average_score': sum(recent_scores) / len(recent_scores) if recent_scores else 0,
            'trend': trend,
            'min_score': min(recent_scores) if recent_scores else 0,
            'max_score': max(recent_scores) if recent_scores else 0
        }
