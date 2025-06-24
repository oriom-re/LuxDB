
"""
✨ Manifestation - System Manifestacji Bytów

Odpowiada za tworzenie, modyfikację i zarządzanie manifestacjami bytów w wymiarach
"""

from typing import Dict, Any, List, Optional, Type
from datetime import datetime
import json

from .base_being import BaseBeing


class Manifestation:
    """
    Manifestacja - konkretne wcielenie bytu w wymiarze
    
    Zarządza cyklem życia bytu:
    - Manifestacja (utworzenie)
    - Ewolucja (modyfikacja)
    - Transcendencja (usunięcie/transformacja)
    """
    
    def __init__(self, realm, being_class: Type[BaseBeing] = None):
        self.realm = realm
        self.being_class = being_class or BaseBeing
        self.active_beings: Dict[str, BaseBeing] = {}
        self.manifestation_history: List[Dict[str, Any]] = []
    
    def manifest(self, data: Dict[str, Any], being_class: Optional[Type[BaseBeing]] = None) -> BaseBeing:
        """
        Manifestuje nowy byt w wymiarze
        
        Args:
            data: Dane bytu do manifestacji
            being_class: Klasa bytu (opcjonalna)
            
        Returns:
            Nowo zmanifestowany byt
        """
        being_class = being_class or self.being_class
        
        # Utwórz nowy byt
        being = being_class(data, realm=self.realm)
        
        # Zarejestruj w aktywnych bytach
        self.active_beings[being.essence.soul_id] = being
        
        # Zapisz historię manifestacji
        manifestation_record = {
            'action': 'manifest',
            'soul_id': being.essence.soul_id,
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'being_class': being_class.__name__
        }
        
        self.manifestation_history.append(manifestation_record)
        being.remember('manifestation', manifestation_record)
        
        # Powiadom realm o nowej manifestacji
        if hasattr(self.realm, 'on_being_manifested'):
            self.realm.on_being_manifested(being)
        
        return being
    
    def find_being(self, soul_id: str) -> Optional[BaseBeing]:
        """
        Znajduje byt po soul_id
        
        Args:
            soul_id: Identyfikator duszy
            
        Returns:
            Byt lub None jeśli nie znaleziono
        """
        return self.active_beings.get(soul_id)
    
    def contemplate(self, intention: str, criteria: Optional[Dict[str, Any]] = None) -> List[BaseBeing]:
        """
        Kontemplacja - duchowe wyszukiwanie bytów
        
        Args:
            intention: Intencja wyszukiwania
            criteria: Kryteria filtrowania
            
        Returns:
            Lista znalezionych bytów
        """
        results = list(self.active_beings.values())
        
        if not criteria:
            return results
        
        filtered_results = []
        
        for being in results:
            matches = True
            
            for key, value in criteria.items():
                # Sprawdź w esencji
                if hasattr(being.essence, key):
                    being_value = getattr(being.essence, key)
                    if not self._matches_criteria(being_value, value):
                        matches = False
                        break
                
                # Sprawdź w atrybutach
                elif key in being.attributes:
                    being_value = being.attributes[key]
                    if not self._matches_criteria(being_value, value):
                        matches = False
                        break
                
                else:
                    matches = False
                    break
            
            if matches:
                # Zapamiętaj że byt był przedmiotem kontemplacji
                being.remember('contemplation', {
                    'intention': intention,
                    'criteria': criteria,
                    'found': True
                })
                filtered_results.append(being)
        
        return filtered_results
    
    def _matches_criteria(self, being_value: Any, criteria_value: Any) -> bool:
        """Sprawdza czy wartość bytu spełnia kryterium"""
        if isinstance(criteria_value, dict):
            operator = criteria_value.get('operator', 'eq')
            value = criteria_value.get('value')
            
            if operator == 'eq':
                return being_value == value
            elif operator == 'ne':
                return being_value != value
            elif operator == 'gt':
                return being_value > value
            elif operator == 'lt':
                return being_value < value
            elif operator == 'gte':
                return being_value >= value
            elif operator == 'lte':
                return being_value <= value
            elif operator == 'contains':
                return value in str(being_value)
            elif operator == 'in':
                return being_value in value
            else:
                return being_value == value
        else:
            return being_value == criteria_value
    
    def evolve_being(self, soul_id: str, new_data: Dict[str, Any]) -> Optional[BaseBeing]:
        """
        Ewoluuje byt - aktualizuje jego dane
        
        Args:
            soul_id: Identyfikator duszy
            new_data: Nowe dane
            
        Returns:
            Zaktualizowany byt lub None
        """
        being = self.find_being(soul_id)
        if not being:
            return None
        
        # Wykonaj ewolucję
        being.evolve(new_data)
        
        # Zapisz w historii
        evolution_record = {
            'action': 'evolve',
            'soul_id': soul_id,
            'timestamp': datetime.now().isoformat(),
            'new_data': new_data
        }
        
        self.manifestation_history.append(evolution_record)
        
        # Powiadom realm
        if hasattr(self.realm, 'on_being_evolved'):
            self.realm.on_being_evolved(being, new_data)
        
        return being
    
    def transcend_being(self, soul_id: str) -> Optional[Dict[str, Any]]:
        """
        Transcenduje byt - usuwa go z wymiaru lub transformuje
        
        Args:
            soul_id: Identyfikator duszy
            
        Returns:
            Raport z transcendencji
        """
        being = self.find_being(soul_id)
        if not being:
            return {'success': False, 'message': 'Byt nie został znaleziony'}
        
        # Próba transcendencji
        transcendence_result = being.transcend()
        
        if transcendence_result['success']:
            # Usuń z aktywnych bytów
            del self.active_beings[soul_id]
            
            # Zapisz w historii
            transcendence_record = {
                'action': 'transcend',
                'soul_id': soul_id,
                'timestamp': datetime.now().isoformat(),
                'final_state': being.get_status()
            }
            
            self.manifestation_history.append(transcendence_record)
            
            # Powiadom realm
            if hasattr(self.realm, 'on_being_transcended'):
                self.realm.on_being_transcended(being)
        
        return transcendence_result
    
    def meditate_all(self) -> Dict[str, Any]:
        """
        Medytacja wszystkich bytów w wymiarze
        
        Returns:
            Zbiorczy raport z medytacji
        """
        meditation_results = []
        total_energy_before = 0
        total_energy_after = 0
        
        for being in self.active_beings.values():
            total_energy_before += being.essence.energy_level
            result = being.meditate()
            total_energy_after += being.essence.energy_level
            meditation_results.append(result)
        
        collective_meditation = {
            'timestamp': datetime.now().isoformat(),
            'total_beings': len(self.active_beings),
            'total_energy_before': total_energy_before,
            'total_energy_after': total_energy_after,
            'energy_gain': total_energy_after - total_energy_before,
            'individual_results': meditation_results
        }
        
        return collective_meditation
    
    def get_manifestation_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki manifestacji"""
        if not self.active_beings:
            return {
                'total_beings': 0,
                'consciousness_levels': {},
                'average_energy': 0,
                'total_memories': 0
            }
        
        consciousness_counts = {}
        total_energy = 0
        total_memories = 0
        
        for being in self.active_beings.values():
            # Poziomy świadomości
            level = being.essence.consciousness_level
            consciousness_counts[level] = consciousness_counts.get(level, 0) + 1
            
            # Energia
            total_energy += being.essence.energy_level
            
            # Wspomnienia
            total_memories += len(being.memories)
        
        return {
            'total_beings': len(self.active_beings),
            'consciousness_levels': consciousness_counts,
            'average_energy': total_energy / len(self.active_beings),
            'total_memories': total_memories,
            'history_entries': len(self.manifestation_history)
        }
    
    def export_beings(self, format: str = 'json') -> str:
        """
        Eksportuje wszystkie byty
        
        Args:
            format: Format eksportu ('json', 'yaml')
            
        Returns:
            Dane w wybranym formacie
        """
        beings_data = {
            soul_id: being.to_dict() 
            for soul_id, being in self.active_beings.items()
        }
        
        export_package = {
            'timestamp': datetime.now().isoformat(),
            'realm': self.realm.name if self.realm else 'unknown',
            'total_beings': len(beings_data),
            'beings': beings_data,
            'manifestation_history': self.manifestation_history[-50:]  # Ostatnie 50 wpisów
        }
        
        if format == 'json':
            return json.dumps(export_package, indent=2, ensure_ascii=False)
        else:
            return str(export_package)  # Fallback
    
    def clear_transcended(self) -> int:
        """
        Czyści wszystkie transcendowane byty z historii
        
        Returns:
            Liczba usuniętych wpisów
        """
        initial_count = len(self.manifestation_history)
        self.manifestation_history = [
            record for record in self.manifestation_history 
            if record.get('action') != 'transcend'
        ]
        
        return initial_count - len(self.manifestation_history)
