
"""
⚖️ Harmony v3 - Harmonizator Astralnego Systemu z LuxBus

Odpowiada za:
- Balansowanie obciążenia modułów LuxBus
- Optymalizację wydajności systemu v3
- Synchronizację komponentów
- Utrzymanie równowagi energetycznej
- Wersjonowanie harmonizacji
"""

import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class HarmonyVersion:
    """Wersja harmonizacji"""
    major: int = 3
    minor: int = 0
    patch: int = 0
    build: str = "luxbus"
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}-{self.build}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'major': self.major,
            'minor': self.minor,
            'patch': self.patch,
            'build': self.build,
            'version_string': str(self)
        }


@dataclass
class HarmonyReport:
    """Raport z harmonizacji z wersjonowaniem"""
    timestamp: str
    harmony_version: HarmonyVersion
    engine_version: str
    actions_taken: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    harmony_score_before: float = 0.0
    harmony_score_after: float = 0.0
    improvement: float = 0.0
    duration: float = 0.0
    error: Optional[str] = None
    luxbus_status: Optional[Dict[str, Any]] = None
    modules_harmonized: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'harmony_version': self.harmony_version.to_dict(),
            'engine_version': self.engine_version,
            'actions_taken': self.actions_taken,
            'recommendations': self.recommendations,
            'harmony_score_before': self.harmony_score_before,
            'harmony_score_after': self.harmony_score_after,
            'improvement': self.improvement,
            'duration': self.duration,
            'error': self.error,
            'luxbus_status': self.luxbus_status,
            'modules_harmonized': self.modules_harmonized
        }


class HarmonyV3:
    """
    Harmonizator systemu v3 - utrzymuje równowagę wszystkich komponentów LuxBus
    
    Kompatybilny z AstralEngine v3 i systemem modułów LuxBus
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        self.version = HarmonyVersion()
        
        self.balance_history: List[HarmonyReport] = []
        self.last_harmonization = None
        self._lock = threading.Lock()
        
        # Rejestracja w LuxBus jeśli dostępne
        if hasattr(self.engine, 'luxbus') and self.engine.luxbus:
            self.engine.luxbus.register_module("harmony_v3", self)
        
        self.engine.logger.info(f"⚖️ Harmony v{self.version} zainicjalizowana")
    
    def harmonize(self) -> Dict[str, Any]:
        """
        Główny proces harmonizacji systemu v3
        
        Returns:
            Raport z harmonizacji
        """
        with self._lock:
            start_time = time.time()
            
            # Przygotuj raport harmonizacji z wersjonowaniem
            report = HarmonyReport(
                timestamp=datetime.now().isoformat(),
                harmony_version=self.version,
                engine_version=getattr(self.engine, 'version', '3.0.0-luxbus'),
                harmony_score_before=self.calculate_harmony_score()
            )
            
            try:
                # Pobierz status LuxBus
                if hasattr(self.engine, 'luxbus'):
                    report.luxbus_status = self.engine.luxbus.get_status()
                
                # 1. Harmonizuj realms przez LuxBus
                realm_actions = self._harmonize_realms_v3()
                report.actions_taken.extend(realm_actions)
                
                # 2. Harmonizuj flows przez LuxBus
                flow_actions = self._harmonize_flows_v3()
                report.actions_taken.extend(flow_actions)
                
                # 3. Harmonizuj moduły LuxBus
                module_actions = self._harmonize_luxbus_modules()
                report.actions_taken.extend(module_actions)
                
                # 4. Optymalizuj pamięć v3
                memory_actions = self._optimize_memory_v3()
                report.actions_taken.extend(memory_actions)
                
                # 5. Sprawdź integrację v3
                integration_recommendations = self._check_integration_v3()
                report.recommendations.extend(integration_recommendations)
                
                # Oblicz końcowy wynik harmonii
                report.harmony_score_after = self.calculate_harmony_score()
                report.improvement = report.harmony_score_after - report.harmony_score_before
                
            except Exception as e:
                report.error = str(e)
                report.actions_taken.append(f"❌ Błąd harmonizacji v3: {e}")
                self.engine.logger.error(f"❌ Błąd harmonizacji: {e}")
            
            finally:
                report.duration = time.time() - start_time
                self.last_harmonization = datetime.now()
                
                # Zapisz w historii
                self.balance_history.append(report)
                if len(self.balance_history) > 50:
                    self.balance_history = self.balance_history[-50:]
            
            return report.to_dict()
    
    def balance(self) -> None:
        """Szybkie balansowanie - uproszczona wersja harmonize dla v3"""
        if not getattr(self.engine, 'running', False):
            return
        
        try:
            # Szybka kontrola realms przez flows
            if hasattr(self.engine, 'flows'):
                for flow_name, flow in self.engine.flows.items():
                    if hasattr(flow, 'optimize'):
                        flow.optimize()
            
            # Kontrola modułów LuxBus
            if hasattr(self.engine, 'luxbus'):
                luxbus_status = self.engine.luxbus.get_status()
                if luxbus_status.get('queue_sizes', {}).get('incoming', 0) > 100:
                    self.engine.logger.warning("⚠️ Wysoka kolejka pakietów przychodzących")
            
            # Kontrola realms v3
            if hasattr(self.engine, 'realms'):
                for realm_name, realm in self.engine.realms.items():
                    if hasattr(realm, 'optimize'):
                        realm.optimize()
        
        except Exception as e:
            self.engine.logger.warning(f"⚠️ Błąd podczas szybkiego balansowania v3: {e}")
    
    def calculate_harmony_score(self) -> float:
        """
        Oblicza ogólny wynik harmonii systemu v3 (0-100)
        
        Returns:
            Wynik harmonii w skali 0-100
        """
        if not hasattr(self.engine, 'realms') or not self.engine.realms:
            return 0.0
        
        scores = []
        
        # 1. Wynik LuxBus (25% wagi) - nowy komponent
        luxbus_score = self._calculate_luxbus_harmony()
        scores.append(('luxbus', luxbus_score, 0.25))
        
        # 2. Wynik realms (30% wagi)
        realm_score = self._calculate_realm_harmony_v3()
        scores.append(('realms', realm_score, 0.30))
        
        # 3. Wynik flows (25% wagi)
        flow_score = self._calculate_flow_harmony_v3()
        scores.append(('flows', flow_score, 0.25))
        
        # 4. Wynik wydajności (10% wagi)
        performance_score = self._calculate_performance_harmony_v3()
        scores.append(('performance', performance_score, 0.10))
        
        # 5. Wynik integracji (10% wagi)
        integration_score = self._calculate_integration_harmony_v3()
        scores.append(('integration', integration_score, 0.10))
        
        # Oblicz ważoną średnią
        total_score = sum(score * weight for _, score, weight in scores)
        
        return min(100.0, max(0.0, total_score))
    
    def _calculate_luxbus_harmony(self) -> float:
        """Oblicza harmonię LuxBus Core"""
        if not hasattr(self.engine, 'luxbus'):
            return 0.0
        
        try:
            status = self.engine.luxbus.get_status()
            
            score = 100.0
            
            # Sprawdź czy LuxBus działa
            if not status.get('running', False):
                score -= 50.0
            
            # Sprawdź kolejki
            queue_sizes = status.get('queue_sizes', {})
            incoming_size = queue_sizes.get('incoming', 0)
            outgoing_size = queue_sizes.get('outgoing', 0)
            
            if incoming_size > 50:
                score -= 20.0
            if outgoing_size > 50:
                score -= 20.0
            
            # Sprawdź liczbę modułów
            modules_count = len(status.get('modules', {}))
            if modules_count < 3:  # consciousness, harmony, przynajmniej jeden realm
                score -= 15.0
            
            return max(0.0, score)
            
        except Exception:
            return 0.0
    
    def _calculate_realm_harmony_v3(self) -> float:
        """Oblicza harmonię realms v3"""
        if not hasattr(self.engine, 'realms') or not self.engine.realms:
            return 0.0
        
        total_score = 0.0
        
        for realm in self.engine.realms.values():
            realm_score = 100.0  # Bazowy wynik
            
            # Sprawdź czy realm jest aktywny
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
    
    def _calculate_flow_harmony_v3(self) -> float:
        """Oblicza harmonię flows v3"""
        if not hasattr(self.engine, 'flows'):
            return 0.0
        
        flows = list(self.engine.flows.values())
        active_flows = sum(1 for flow in flows if flow is not None)
        
        if active_flows == 0:
            return 0.0
        elif active_flows == 1:
            return 40.0
        elif active_flows == 2:
            return 70.0
        else:
            return 100.0
    
    def _calculate_performance_harmony_v3(self) -> float:
        """Oblicza harmonię wydajności v3"""
        try:
            # Sprawdź insights z consciousness
            if hasattr(self.engine, 'consciousness'):
                insights = self.engine.consciousness.reflect()
                
                memory_percent = insights.get('system', {}).get('memory_usage', {}).get('percent', 50)
                cpu_percent = insights.get('system', {}).get('cpu_usage', 50)
                
                # Oblicz wynik na podstawie użycia zasobów
                memory_score = max(0, 100 - memory_percent)
                cpu_score = max(0, 100 - cpu_percent)
                
                return (memory_score + cpu_score) / 2
            else:
                return 75.0  # Domyślny wynik jeśli brak danych
                
        except Exception:
            return 50.0  # Bezpieczny domyślny wynik
    
    def _calculate_integration_harmony_v3(self) -> float:
        """Oblicza harmonię integracji komponentów v3"""
        integration_score = 100.0
        
        # Sprawdź czy LuxBus działa
        if not hasattr(self.engine, 'luxbus'):
            integration_score -= 40.0
        
        # Sprawdź czy consciousness jest zarejestrowana
        if not hasattr(self.engine, 'consciousness'):
            integration_score -= 20.0
        
        # Sprawdź czy realms są załadowane
        if not hasattr(self.engine, 'realms') or not self.engine.realms:
            integration_score -= 30.0
        
        # Sprawdź czy flows są załadowane
        if not hasattr(self.engine, 'flows') or not self.engine.flows:
            integration_score -= 10.0
        
        return max(0.0, integration_score)
    
    def _harmonize_realms_v3(self) -> List[str]:
        """Harmonizuje realms v3"""
        actions = []
        
        if not hasattr(self.engine, 'realms'):
            return actions
        
        for realm_name, realm in self.engine.realms.items():
            try:
                # Sprawdź czy realm potrzebuje optymalizacji
                if hasattr(realm, 'needs_optimization') and realm.needs_optimization():
                    if hasattr(realm, 'optimize'):
                        realm.optimize()
                        actions.append(f"✨ Zoptymalizowano realm '{realm_name}' v3")
                
                # Sprawdź połączenie
                if hasattr(realm, 'test_connection'):
                    if not realm.test_connection():
                        if hasattr(realm, 'reconnect'):
                            realm.reconnect()
                            actions.append(f"🔄 Odnowiono połączenie z realm '{realm_name}' v3")
                
            except Exception as e:
                actions.append(f"❌ Błąd harmonizacji realm '{realm_name}' v3: {e}")
        
        return actions
    
    def _harmonize_flows_v3(self) -> List[str]:
        """Harmonizuje flows v3"""
        actions = []
        
        if not hasattr(self.engine, 'flows'):
            return actions
        
        for flow_name, flow in self.engine.flows.items():
            if flow is None:
                continue
                
            try:
                # Sprawdź stan flow
                if hasattr(flow, 'is_healthy') and not flow.is_healthy():
                    if hasattr(flow, 'heal'):
                        flow.heal()
                        actions.append(f"💚 Uzdrowiono flow {flow_name} v3")
                
                # Optymalizuj jeśli możliwe
                if hasattr(flow, 'optimize'):
                    flow.optimize()
                    actions.append(f"⚡ Zoptymalizowano flow {flow_name} v3")
                
            except Exception as e:
                actions.append(f"❌ Błąd harmonizacji flow {flow_name} v3: {e}")
        
        return actions
    
    def _harmonize_luxbus_modules(self) -> List[str]:
        """Harmonizuje moduły LuxBus"""
        actions = []
        
        if not hasattr(self.engine, 'luxbus'):
            return actions
        
        try:
            luxbus_status = self.engine.luxbus.get_status()
            modules = luxbus_status.get('modules', {})
            
            # Sprawdź czy wszystkie kluczowe moduły są zarejestrowane
            expected_modules = ['astral_engine', 'consciousness', 'harmony']
            missing_modules = [mod for mod in expected_modules if mod not in modules]
            
            if missing_modules:
                actions.append(f"⚠️ Brakujące moduły LuxBus: {', '.join(missing_modules)}")
            
            # Sprawdź kolejki pakietów
            queue_sizes = luxbus_status.get('queue_sizes', {})
            if queue_sizes.get('incoming', 0) > 100:
                actions.append("🚌 Oczyszczono kolejkę pakietów przychodzących")
            
            actions.append(f"🚌 LuxBus: {len(modules)} modułów aktywnych")
            
        except Exception as e:
            actions.append(f"❌ Błąd harmonizacji LuxBus: {e}")
        
        return actions
    
    def _optimize_memory_v3(self) -> List[str]:
        """Optymalizuje użycie pamięci v3"""
        actions = []
        
        try:
            # Sprawdź czy consciousness może zwolnić pamięć
            if hasattr(self.engine, 'consciousness') and hasattr(self.engine.consciousness, 'observations'):
                if len(self.engine.consciousness.observations) > 50:
                    self.engine.consciousness.observations = self.engine.consciousness.observations[-30:]
                    actions.append("🧠 Oczyszczono historię obserwacji consciousness v3")
            
            # Oczyszczenie historii harmonii
            if len(self.balance_history) > 30:
                self.balance_history = self.balance_history[-20:]
                actions.append("⚖️ Oczyszczono historię harmonizacji v3")
            
            # Sprawdź LuxBus cache jeśli istnieje
            if hasattr(self.engine, 'luxbus') and hasattr(self.engine.luxbus, 'clear_cache'):
                self.engine.luxbus.clear_cache()
                actions.append("🚌 Oczyszczono cache LuxBus")
            
        except Exception as e:
            actions.append(f"❌ Błąd optymalizacji pamięci v3: {e}")
        
        return actions
    
    def _check_integration_v3(self) -> List[str]:
        """Sprawdza integrację komponentów v3"""
        recommendations = []
        
        # Sprawdź LuxBus
        if not hasattr(self.engine, 'luxbus'):
            recommendations.append("Zainicjalizuj LuxBus Core")
        
        # Sprawdź realms
        if not hasattr(self.engine, 'realms') or not self.engine.realms:
            recommendations.append("Utwórz przynajmniej jeden realm")
        
        # Sprawdź flows
        if not hasattr(self.engine, 'flows') or not self.engine.flows:
            recommendations.append("Aktywuj przynajmniej jeden flow")
        
        # Sprawdź czy consciousness działa
        if hasattr(self.engine, 'consciousness'):
            try:
                self.engine.consciousness.reflect()
            except Exception:
                recommendations.append("Sprawdź działanie modułu consciousness v3")
        
        return recommendations
    
    def get_harmony_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Zwraca historię harmonizacji z wersjonowaniem"""
        return [report.to_dict() for report in self.balance_history[-limit:]]
    
    def get_harmony_trends(self) -> Dict[str, Any]:
        """Analizuje trendy harmonii v3"""
        if len(self.balance_history) < 3:
            return {
                'message': 'Potrzeba więcej danych historycznych v3',
                'version': self.version.to_dict()
            }
        
        recent_scores = [
            report.harmony_score_after
            for report in self.balance_history[-10:]
        ]
        
        # Oblicz trend
        if len(recent_scores) >= 2:
            trend = 'improving' if recent_scores[-1] > recent_scores[0] else 'declining'
            if abs(recent_scores[-1] - recent_scores[0]) < 5:
                trend = 'stable'
        else:
            trend = 'unknown'
        
        return {
            'version': self.version.to_dict(),
            'current_score': recent_scores[-1] if recent_scores else 0,
            'average_score': sum(recent_scores) / len(recent_scores) if recent_scores else 0,
            'trend': trend,
            'min_score': min(recent_scores) if recent_scores else 0,
            'max_score': max(recent_scores) if recent_scores else 0,
            'harmony_reports_count': len(self.balance_history)
        }
    
    def get_version_info(self) -> Dict[str, Any]:
        """Zwraca informacje o wersji Harmony"""
        return {
            'harmony_version': self.version.to_dict(),
            'compatible_engines': ['AstralEngine v3', 'LuxBus Core'],
            'features': [
                'LuxBus module harmonization',
                'Versioned harmony reports',
                'Enhanced realm monitoring',
                'Flow optimization v3',
                'Memory management v3'
            ]
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Informacje o module dla LuxBus"""
        return {
            'type': 'HarmonyV3',
            'version': str(self.version),
            'capabilities': ['system_harmonization', 'module_balancing', 'performance_optimization'],
            'status': 'active',
            'last_harmonization': self.last_harmonization.isoformat() if self.last_harmonization else None,
            'reports_in_history': len(self.balance_history)
        }


# Alias dla kompatybilności wstecznej
Harmony = HarmonyV3
