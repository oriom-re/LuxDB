
"""
⚡ MemoryRealmModule - Moduł Wymiaru Pamięci w Federacji
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_realm import BaseRealmModule


class MemoryRealmModule(BaseRealmModule):
    """
    Moduł wymiaru pamięci - szybkie przechowywanie danych w RAM
    """
    
    def __init__(self, name: str, config: Dict[str, Any], bus):
        super().__init__(name, config, bus)
        
        # Słownik przechowujący byty
        self.beings: Dict[int, Dict[str, Any]] = {}
        self.next_soul_id = 1
        
        # Indeksy dla szybkiego wyszukiwania
        self._indices: Dict[str, Dict[Any, List[int]]] = {}
        
        # Konfiguracja
        self.max_beings = config.get('max_beings', 10000)
    
    async def connect(self) -> bool:
        """Nawiązuje połączenie z wymiarem pamięci"""
        try:
            self.is_connected = True
            print(f"⚡ Połączono z wymiarem pamięci: {self.module_id}")
            return True
        except Exception as e:
            print(f"❌ Błąd połączenia z wymiarem pamięci: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącza z wymiarem pamięci"""
        try:
            self.beings.clear()
            self._indices.clear()
            self.is_connected = False
            print(f"⚡ Rozłączono z wymiarem pamięci: {self.module_id}")
            return True
        except Exception as e:
            print(f"❌ Błąd rozłączania z wymiarem pamięci: {e}")
            return False
    
    async def manifest(self, being_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manifestuje nowy byt w wymiarze pamięci"""
        if len(self.beings) >= self.max_beings:
            raise RuntimeError(f"Wymiar pamięci osiągnął maksymalną pojemność: {self.max_beings}")
        
        # Przypisz unikalny soul_id
        soul_id = self.next_soul_id
        self.next_soul_id += 1
        
        # Dodaj metadane
        being = {
            'soul_id': soul_id,
            'created_at': datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat(),
            **being_data
        }
        
        # Zapisz byt
        self.beings[soul_id] = being
        self._being_count += 1
        
        # Zaktualizuj indeksy
        self._update_indices(soul_id, being)
        
        print(f"⚡ Manifestowano byt {soul_id} w wymiarze pamięci")
        return being
    
    async def contemplate(self, intention: str, **conditions) -> List[Dict[str, Any]]:
        """Kontempluje byty w wymiarze pamięci"""
        results = []
        
        # Jeśli brak warunków, zwróć wszystkie byty
        if not conditions:
            return list(self.beings.values())
        
        # Wyszukaj według warunków
        for soul_id, being in self.beings.items():
            match = True
            
            for key, value in conditions.items():
                if key not in being or being[key] != value:
                    match = False
                    break
            
            if match:
                results.append(being)
        
        print(f"⚡ Kontemplacja w wymiarze pamięci: {len(results)} bytów")
        return results
    
    async def transcend(self, being_id: Any) -> bool:
        """Transcenduje byt z wymiaru pamięci"""
        soul_id = int(being_id)
        
        if soul_id not in self.beings:
            return False
        
        # Usuń z indeksów
        being = self.beings[soul_id]
        self._remove_from_indices(soul_id, being)
        
        # Usuń byt
        del self.beings[soul_id]
        self._being_count -= 1
        
        print(f"⚡ Transcendowano byt {soul_id} z wymiaru pamięci")
        return True
    
    async def evolve(self, being_id: Any, new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ewoluuje byt w wymiarze pamięci"""
        soul_id = int(being_id)
        
        if soul_id not in self.beings:
            return None
        
        # Usuń stare indeksy
        old_being = self.beings[soul_id].copy()
        self._remove_from_indices(soul_id, old_being)
        
        # Aktualizuj byt
        self.beings[soul_id].update(new_data)
        self.beings[soul_id]['modified_at'] = datetime.now().isoformat()
        
        # Dodaj nowe indeksy
        self._update_indices(soul_id, self.beings[soul_id])
        
        print(f"⚡ Ewoluowano byt {soul_id} w wymiarze pamięci")
        return self.beings[soul_id]
    
    async def count_beings(self) -> int:
        """Zwraca liczbę bytów w wymiarze"""
        return len(self.beings)
    
    def _update_indices(self, soul_id: int, being: Dict[str, Any]):
        """Aktualizuje indeksy dla szybkiego wyszukiwania"""
        for key, value in being.items():
            if key not in self._indices:
                self._indices[key] = {}
            
            if value not in self._indices[key]:
                self._indices[key][value] = []
            
            if soul_id not in self._indices[key][value]:
                self._indices[key][value].append(soul_id)
    
    def _remove_from_indices(self, soul_id: int, being: Dict[str, Any]):
        """Usuwa byt z indeksów"""
        for key, value in being.items():
            if key in self._indices and value in self._indices[key]:
                if soul_id in self._indices[key][value]:
                    self._indices[key][value].remove(soul_id)
                
                # Usuń puste listy
                if not self._indices[key][value]:
                    del self._indices[key][value]
