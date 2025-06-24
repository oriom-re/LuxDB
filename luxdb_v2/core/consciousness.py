
"""
🧠 Consciousness - Świadomość Astralna LuxDB v2

Odpowiada za:
- Obserwację stanu systemu
- Analizę wydajności
- Wykrywanie anomalii
- Raportowanie insights
"""

import time
import psutil
from typing import Dict, Any, List
from datetime import datetime


class Consciousness:
    """
    Świadomość systemu - obserwuje i analizuje stan astralny
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        self.observations: List[Dict[str, Any]] = []
        self.start_time = time.time()
    
    def reflect(self) -> Dict[str, Any]:
        """
        Refleksja nad stanem systemu
        
        Returns:
            Słownik z insights o systemie
        """
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # Obserwacje systemowe
        system_insights = {
            'uptime_seconds': uptime,
            'uptime_formatted': self._format_uptime(uptime),
            'memory_usage': self._get_memory_usage(),
            'cpu_usage': self._get_cpu_usage(),
            'active_realms': len(self.engine.realms),
            'total_connections': self._count_connections()
        }
        
        # Obserwacje astralnej harmonii
        harmony_insights = {
            'energy_flow_balance': self._assess_energy_flow(),
            'realm_health': self._assess_realm_health(),
            'flow_efficiency': self._assess_flow_efficiency()
        }
        
        # Rekomendacje
        recommendations = self._generate_recommendations(system_insights, harmony_insights)
        
        insight_record = {
            'timestamp': datetime.now().isoformat(),
            'system': system_insights,
            'harmony': harmony_insights,
            'recommendations': recommendations
        }
        
        # Zachowaj obserwację
        self.observations.append(insight_record)
        
        # Ogranicz historię do ostatnich 100 obserwacji
        if len(self.observations) > 100:
            self.observations = self.observations[-100:]
        
        return insight_record
    
    def _format_uptime(self, seconds: float) -> str:
        """Formatuje czas działania"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """Pobiera informacje o użyciu pamięci"""
        try:
            memory = psutil.virtual_memory()
            return {
                'percent': memory.percent,
                'available_mb': memory.available / (1024 * 1024),
                'used_mb': memory.used / (1024 * 1024)
            }
        except:
            return {'percent': 0, 'available_mb': 0, 'used_mb': 0}
    
    def _get_cpu_usage(self) -> float:
        """Pobiera użycie CPU"""
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def _count_connections(self) -> int:
        """Liczy aktywne połączenia"""
        total = 0
        for realm in self.engine.realms.values():
            if hasattr(realm, 'active_connections'):
                total += realm.active_connections
        return total
    
    def _assess_energy_flow(self) -> str:
        """Ocenia przepływ energii w systemie"""
        if not self.engine.realms:
            return 'dormant'
        
        active_flows = 0
        if self.engine.rest_flow and hasattr(self.engine.rest_flow, 'is_running'):
            if self.engine.rest_flow.is_running():
                active_flows += 1
        
        if self.engine.ws_flow and hasattr(self.engine.ws_flow, 'is_running'):
            if self.engine.ws_flow.is_running():
                active_flows += 1
        
        if active_flows >= 2:
            return 'harmonious'
        elif active_flows == 1:
            return 'flowing'
        else:
            return 'stagnant'
    
    def _assess_realm_health(self) -> str:
        """Ocenia zdrowie wymiarów"""
        if not self.engine.realms:
            return 'empty'
        
        healthy_realms = 0
        for realm in self.engine.realms.values():
            if hasattr(realm, 'is_healthy') and realm.is_healthy():
                healthy_realms += 1
            else:
                healthy_realms += 1  # Zakładamy zdrowie jeśli nie ma metody
        
        health_ratio = healthy_realms / len(self.engine.realms)
        
        if health_ratio >= 0.9:
            return 'excellent'
        elif health_ratio >= 0.7:
            return 'good'
        elif health_ratio >= 0.5:
            return 'concerning'
        else:
            return 'critical'
    
    def _assess_flow_efficiency(self) -> str:
        """Ocenia efektywność przepływów"""
        # Prosta ocena na podstawie liczby aktywnych przepływów
        active_flows = sum([
            1 for flow in [self.engine.rest_flow, self.engine.ws_flow, self.engine.callback_flow]
            if flow is not None
        ])
        
        if active_flows >= 3:
            return 'optimal'
        elif active_flows >= 2:
            return 'efficient'
        elif active_flows >= 1:
            return 'basic'
        else:
            return 'inactive'
    
    def _generate_recommendations(self, system: Dict, harmony: Dict) -> List[str]:
        """Generuje rekomendacje na podstawie obserwacji"""
        recommendations = []
        
        # Rekomendacje systemowe
        if system['memory_usage']['percent'] > 80:
            recommendations.append("Rozważ optymalizację użycia pamięci")
        
        if system['cpu_usage'] > 80:
            recommendations.append("Wysokie użycie CPU - sprawdź obciążenie")
        
        # Rekomendacje harmonii
        if harmony['energy_flow_balance'] == 'stagnant':
            recommendations.append("Aktywuj więcej przepływów energii")
        
        if harmony['realm_health'] in ['concerning', 'critical']:
            recommendations.append("Sprawdź zdrowie wymiarów danych")
        
        if harmony['flow_efficiency'] == 'inactive':
            recommendations.append("Uruchom systemy komunikacji")
        
        if not recommendations:
            recommendations.append("System działa harmonijnie ✨")
        
        return recommendations
    
    def get_insights_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Zwraca historię insights"""
        return self.observations[-limit:]
    
    def meditate_on_patterns(self) -> Dict[str, Any]:
        """Medytuje nad wzorcami w obserwacjach"""
        if len(self.observations) < 5:
            return {'message': 'Potrzeba więcej obserwacji dla analizy wzorców'}
        
        recent = self.observations[-10:]
        
        # Analiza trendów
        memory_trend = self._analyze_trend([obs['system']['memory_usage']['percent'] for obs in recent])
        cpu_trend = self._analyze_trend([obs['system']['cpu_usage'] for obs in recent])
        
        return {
            'memory_trend': memory_trend,
            'cpu_trend': cpu_trend,
            'stability_score': self._calculate_stability_score(recent),
            'dominant_recommendations': self._get_dominant_recommendations(recent)
        }
    
    def _analyze_trend(self, values: List[float]) -> str:
        """Analizuje trend wartości"""
        if len(values) < 3:
            return 'insufficient_data'
        
        increases = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
        total_changes = len(values) - 1
        
        if increases / total_changes > 0.7:
            return 'increasing'
        elif increases / total_changes < 0.3:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_stability_score(self, observations: List[Dict]) -> float:
        """Oblicza wynik stabilności systemu"""
        if not observations:
            return 0.0
        
        stable_factors = 0
        total_factors = 0
        
        for obs in observations:
            # Sprawdź stabilność pamięci
            if obs['system']['memory_usage']['percent'] < 70:
                stable_factors += 1
            total_factors += 1
            
            # Sprawdź stabilność CPU
            if obs['system']['cpu_usage'] < 60:
                stable_factors += 1
            total_factors += 1
            
            # Sprawdź harmonię
            if obs['harmony']['realm_health'] in ['excellent', 'good']:
                stable_factors += 1
            total_factors += 1
        
        return (stable_factors / total_factors) * 100 if total_factors > 0 else 0.0
    
    def _get_dominant_recommendations(self, observations: List[Dict]) -> List[str]:
        """Znajduje najczęstsze rekomendacje"""
        rec_count = {}
        
        for obs in observations:
            for rec in obs.get('recommendations', []):
                rec_count[rec] = rec_count.get(rec, 0) + 1
        
        # Zwróć najczęstsze rekomendacje
        sorted_recs = sorted(rec_count.items(), key=lambda x: x[1], reverse=True)
        return [rec for rec, count in sorted_recs[:3]]
