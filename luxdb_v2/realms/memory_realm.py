
"""
⚡ MemoryRealm - Szybki Wymiar Pamięci

Wymiar danych przechowywanych w pamięci - najszybszy, ale nietrwały
"""

import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from .base_realm import BaseRealm


class MemoryRealm(BaseRealm):
    """
    Wymiar danych w pamięci - najszybszy dostęp, ale dane nietrwałe
    """
    
    def __init__(self, name: str, connection_string: str, astral_engine):
        super().__init__(name, connection_string, astral_engine)
        
        # Przechowywanie danych w pamięci
        self.beings: Dict[int, Dict[str, Any]] = {}
        self.next_soul_id = 1
        self._indices: Dict[str, Dict[Any, List[int]]] = {
            'soul_name': {},
            'realm_affinity': {},
            'energy_level': {}
        }
    
    def connect(self) -> bool:
        """Nawiązuje połączenie z wymiarem pamięci"""
        try:
            # Połączenie jest zawsze dostępne dla wymiaru pamięci
            self.is_connected = True
            self.engine.logger.info(f"⚡ Połączono z wymiarem pamięci: {self.name}")
            return True
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd połączenia z wymiarem pamięci {self.name}: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Rozłącza z wymiarem pamięci"""
        try:
            # Opcjonalnie możemy wyczyścić dane
            # self.beings.clear()
            # self._indices = {'soul_name': {}, 'realm_affinity': {}, 'energy_level': {}}
            
            self.is_connected = False
            self.engine.logger.info(f"⚡ Rozłączono z wymiarem pamięci: {self.name}")
            return True
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd rozłączania z wymiarem pamięci {self.name}: {e}")
            return False
    
    def manifest(self, being_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manifestuje nowy byt w wymiarze pamięci"""
        if not self.is_connected:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        # Przygotuj dane
        soul_id = self.next_soul_id
        self.next_soul_id += 1
        
        soul_name = being_data.get('soul_name', f'being_{soul_id}')
        energy_level = being_data.get('energy_level', 100.0)
        realm_affinity = being_data.get('realm_affinity', 'neutral')
        manifestation_time = datetime.now().isoformat()
        
        # Utwórz byt
        being = being_data.copy()
        being.update({
            'soul_id': soul_id,
            'soul_name': soul_name,
            'energy_level': energy_level,
            'realm_affinity': realm_affinity,
            'manifestation_time': manifestation_time
        })
        
        # Zapisz w pamięci
        self.beings[soul_id] = being
        
        # Aktualizuj indeksy
        self._update_indices(soul_id, being)
        
        # Zwiększ licznik
        self._being_count += 1
        
        self.engine.logger.debug(f"✨ Manifestowano byt '{soul_name}' w wymiarze pamięci {self.name}")
        return being
    
    def contemplate(self, intention: str, **conditions) -> List[Dict[str, Any]]:
        """Kontempluje (wyszukuje) byty w wymiarze pamięci"""
        if not self.is_connected:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        # Zbierz wszystkie byty spełniające warunki
        results = []
        
        # Jeśli nie ma warunków, zwróć wszystkie byty
        if not conditions:
            results = list(self.beings.values())
        else:
            # Filtruj na podstawie warunków
            for being in self.beings.values():
                if self._matches_conditions(being, conditions):
                    results.append(being)
        
        # Sortowanie
        if 'order_by' in conditions:
            order_field = conditions['order_by']
            reverse = conditions.get('order_desc', False)
            
            results.sort(
                key=lambda x: x.get(order_field, 0),
                reverse=reverse
            )
        else:
            # Domyślnie sortuj po czasie manifestacji (najnowsze pierwsze)
            results.sort(
                key=lambda x: x.get('manifestation_time', ''),
                reverse=True
            )
        
        # Limit
        if 'limit' in conditions:
            limit = int(conditions['limit'])
            results = results[:limit]
        
        self.engine.logger.debug(f"🔍 Kontemplacja '{intention}' zwróciła {len(results)} bytów")
        return results
    
    def transcend(self, being_id: int) -> bool:
        """Transcenduje (usuwa) byt z wymiaru pamięci"""
        if not self.is_connected:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        if being_id in self.beings:
            being = self.beings[being_id]
            
            # Usuń z indeksów
            self._remove_from_indices(being_id, being)
            
            # Usuń z głównego słownika
            del self.beings[being_id]
            
            # Zmniejsz licznik
            self._being_count = max(0, self._being_count - 1)
            
            self.engine.logger.debug(f"🕊️ Byt {being_id} transcendował z wymiaru pamięci {self.name}")
            return True
        else:
            return False
    
    def evolve(self, being_id: int, new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ewoluuje (aktualizuje) byt w wymiarze pamięci"""
        if not self.is_connected:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        if being_id not in self.beings:
            return None
        
        # Pobierz aktualny byt
        current_being = self.beings[being_id]
        
        # Usuń z indeksów
        self._remove_from_indices(being_id, current_being)
        
        # Aktualizuj dane
        current_being.update(new_data)
        current_being['last_evolution'] = datetime.now().isoformat()
        
        # Zapisz zaktualizowany byt
        self.beings[being_id] = current_being
        
        # Aktualizuj indeksy
        self._update_indices(being_id, current_being)
        
        self.engine.logger.debug(f"🦋 Byt {being_id} ewoluował w wymiarze pamięci {self.name}")
        return current_being.copy()
    
    def count_beings(self) -> int:
        """Zwraca liczbę bytów w wymiarze"""
        self._being_count = len(self.beings)
        return self._being_count
    
    def _matches_conditions(self, being: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """Sprawdza czy byt spełnia warunki"""
        for key, value in conditions.items():
            # Pomiń specjalne klucze
            if key in ['order_by', 'order_desc', 'limit']:
                continue
            
            # Sprawdź różne typy warunków
            if key == 'soul_name':
                if being.get('soul_name') != value:
                    return False
            
            elif key == 'energy_level_min':
                if being.get('energy_level', 0) < value:
                    return False
            
            elif key == 'energy_level_max':
                if being.get('energy_level', 0) > value:
                    return False
            
            elif key == 'realm_affinity':
                if being.get('realm_affinity') != value:
                    return False
            
            elif key in being:
                # Ogólne dopasowanie
                if being[key] != value:
                    return False
        
        return True
    
    def _update_indices(self, soul_id: int, being: Dict[str, Any]) -> None:
        """Aktualizuje indeksy dla szybszego wyszukiwania"""
        # Indeks po soul_name
        soul_name = being.get('soul_name')
        if soul_name:
            if soul_name not in self._indices['soul_name']:
                self._indices['soul_name'][soul_name] = []
            self._indices['soul_name'][soul_name].append(soul_id)
        
        # Indeks po realm_affinity
        realm_affinity = being.get('realm_affinity')
        if realm_affinity:
            if realm_affinity not in self._indices['realm_affinity']:
                self._indices['realm_affinity'][realm_affinity] = []
            self._indices['realm_affinity'][realm_affinity].append(soul_id)
        
        # Indeks po energy_level (zaokrąglony do 10)
        energy_level = being.get('energy_level')
        if energy_level is not None:
            energy_bucket = int(energy_level // 10) * 10
            if energy_bucket not in self._indices['energy_level']:
                self._indices['energy_level'][energy_bucket] = []
            self._indices['energy_level'][energy_bucket].append(soul_id)
    
    def _remove_from_indices(self, soul_id: int, being: Dict[str, Any]) -> None:
        """Usuwa z indeksów"""
        # Usuń z indeksu soul_name
        soul_name = being.get('soul_name')
        if soul_name and soul_name in self._indices['soul_name']:
            if soul_id in self._indices['soul_name'][soul_name]:
                self._indices['soul_name'][soul_name].remove(soul_id)
            if not self._indices['soul_name'][soul_name]:
                del self._indices['soul_name'][soul_name]
        
        # Usuń z indeksu realm_affinity
        realm_affinity = being.get('realm_affinity')
        if realm_affinity and realm_affinity in self._indices['realm_affinity']:
            if soul_id in self._indices['realm_affinity'][realm_affinity]:
                self._indices['realm_affinity'][realm_affinity].remove(soul_id)
            if not self._indices['realm_affinity'][realm_affinity]:
                del self._indices['realm_affinity'][realm_affinity]
        
        # Usuń z indeksu energy_level
        energy_level = being.get('energy_level')
        if energy_level is not None:
            energy_bucket = int(energy_level // 10) * 10
            if energy_bucket in self._indices['energy_level']:
                if soul_id in self._indices['energy_level'][energy_bucket]:
                    self._indices['energy_level'][energy_bucket].remove(soul_id)
                if not self._indices['energy_level'][energy_bucket]:
                    del self._indices['energy_level'][energy_bucket]
    
    def optimize(self) -> None:
        """Optymalizuje wymiar pamięci"""
        # Wyczyść puste indeksy
        for index_name in self._indices:
            empty_keys = [k for k, v in self._indices[index_name].items() if not v]
            for key in empty_keys:
                del self._indices[index_name][key]
        
        self.engine.logger.debug(f"⚡ Zoptymalizowano wymiar pamięci: {self.name}")
    
    def test_connection(self) -> bool:
        """Testuje połączenie z wymiarem pamięci"""
        # Wymiar pamięci jest zawsze dostępny
        return True
    
    def clear(self) -> None:
        """Czyści wszystkie dane z wymiaru"""
        self.beings.clear()
        self._indices = {'soul_name': {}, 'realm_affinity': {}, 'energy_level': {}}
        self.next_soul_id = 1
        self._being_count = 0
        
        self.engine.logger.info(f"🧹 Wyczyszczono wymiar pamięci: {self.name}")
    
    def get_beings_sample(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Zwraca próbkę bytów z wymiaru"""
        return self.contemplate("sample_beings", limit=limit)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki użycia pamięci"""
        import sys
        
        total_size = sys.getsizeof(self.beings)
        for being in self.beings.values():
            total_size += sys.getsizeof(being)
        
        return {
            'beings_count': len(self.beings),
            'next_soul_id': self.next_soul_id,
            'indices_count': {
                name: len(index) for name, index in self._indices.items()
            },
            'estimated_memory_bytes': total_size,
            'estimated_memory_mb': total_size / (1024 * 1024)
        }
