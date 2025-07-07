
"""
🎯 IntentionRealm - Wymiar Intencji Duchowo-Materialnych

Specjalizowany wymiar przechowujący i zarządzający intencjami
Z persystencją na wypadek blackout'u! 🔋
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

from .base_realm import BaseRealm
from ..beings.intention_being import IntentionBeing, IntentionState, IntentionPriority


class IntentionRealm(BaseRealm):
    """
    Wymiar Intencji - specjalizowany realm dla bytów IntentionBeing
    """
    
    def __init__(self, name: str, connection_string: str, astral_engine):
        super().__init__(name, connection_string, astral_engine)
        
        # Plik persystencji
        self.persistence_file = f"db/intentions_{name}.json"
        
        # Słownik aktywnych intencji
        self.active_intentions: Dict[str, IntentionBeing] = {}
        
        # Kategoryzacja intencji
        self.intentions_by_state: Dict[IntentionState, List[str]] = {
            state: [] for state in IntentionState
        }
        
        self.intentions_by_priority: Dict[IntentionPriority, List[str]] = {
            priority: [] for priority in IntentionPriority
        }
        
        # Statystyki
        self.total_intentions_created = 0
        self.total_intentions_completed = 0
        
        # Auto-connect dla intention realm
        self.connect()
    
    def connect(self) -> bool:
        """Nawiązuje połączenie z wymiarem intencji"""
        try:
            # Intention realm zawsze działa w pamięci + opcjonalnie persystencja
            self.is_connected = True
            
            # Załaduj persystencję jeśli istnieje
            self._load_persistence()
            
            if self.engine:
                self.engine.logger.info(f"🎯 Wymiar Intencji '{self.name}' aktywowany")
                if os.path.exists(self.persistence_file):
                    self.engine.logger.info(f"💾 Załadowano {len(self.active_intentions)} intencji z persystencji")
            
            return True
        except Exception as e:
            if self.engine:
                self.engine.logger.error(f"❌ Błąd połączenia z wymiarem intencji: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Rozłącza z wymiarem intencji"""
        try:
            # Zapisz persystencję przed rozłączeniem
            self._save_persistence()
            
            self.is_connected = False
            if self.engine:
                self.engine.logger.info(f"🎯 Wymiar Intencji '{self.name}' deaktywowany")
                self.engine.logger.info(f"💾 Zapisano {len(self.active_intentions)} intencji do persystencji")
            return True
        except Exception as e:
            if self.engine:
                self.engine.logger.error(f"❌ Błąd rozłączania wymiaru intencji: {e}")
            return False
    
    def manifest(self, intention_data: Dict[str, Any]) -> IntentionBeing:
        """
        Manifestuje nową intencję w wymiarze
        
        Args:
            intention_data: Dane intencji z warstwami duchową i materialną
            
        Returns:
            Nowa intencja
        """
        try:
            # Utwórz nowy byt intencji
            intention = IntentionBeing(intention_data, realm=self)
            
            # Dodaj do aktywnych intencji
            self.active_intentions[intention.essence.soul_id] = intention
            
            # Kategoryzuj
            self._categorize_intention(intention)
            
            # Aktualizuj statystyki
            self.total_intentions_created += 1
            self._being_count += 1
            
            # Utwórz kanał komunikacji
            self._create_communication_channel(intention)
            
            # Auto-save po dodaniu intencji
            self._save_persistence()
            
            # Emituj wydarzenie
            if self.engine and hasattr(self.engine, 'callback_flow') and self.engine.callback_flow:
                self.engine.callback_flow.emit_event('intentions', 'intention_manifested', {
                    'intention_id': intention.essence.soul_id,
                    'name': intention.essence.name,
                    'state': intention.state.value,
                    'priority': intention.priority.value,
                    'realm': self.name
                })
            
            if self.engine:
                self.engine.logger.info(f"🎯 Intencja '{intention.essence.name}' zmanifestowana")
            
            return intention
            
        except Exception as e:
            if self.engine:
                self.engine.logger.error(f"❌ Błąd manifestacji intencji: {e}")
            raise
    
    def _categorize_intention(self, intention: IntentionBeing):
        """Kategoryzuje intencję według stanu i priorytetu"""
        # Według stanu
        self.intentions_by_state[intention.state].append(intention.essence.soul_id)
        
        # Według priorytetu
        self.intentions_by_priority[intention.priority].append(intention.essence.soul_id)
    
    def _create_communication_channel(self, intention: IntentionBeing):
        """Tworzy kanał komunikacji dla intencji"""
        channel_name = intention.get_communication_channel()
        
        # Jeśli callback_flow istnieje, utwórz namespace
        if self.engine and hasattr(self.engine, 'callback_flow') and self.engine.callback_flow:
            intentions_ns = self.engine.callback_flow.create_namespace('intentions')
            
            # Callback dla interakcji z intencją
            def handle_intention_interaction(event):
                interaction_data = event.data
                intention_id = interaction_data.get('intention_id')
                
                if intention_id in self.active_intentions:
                    intention = self.active_intentions[intention_id]
                    return intention.add_interaction(
                        interaction_data.get('type'),
                        interaction_data.get('data', {}),
                        interaction_data.get('user_id', 'system')
                    )
                
                return {'success': False, 'message': 'Intencja nie znaleziona'}
            
            intentions_ns.on(f'interact_{intention.essence.soul_id}', handle_intention_interaction)
    
    def contemplate(self, intention: str, **conditions) -> List[IntentionBeing]:
        """
        Kontempluje (wyszukuje) intencje w wymiarze
        
        Args:
            intention: Intencja zapytania
            **conditions: Warunki wyszukiwania
            
        Returns:
            Lista znalezionych intencji
        """
        try:
            results = []
            
            # Filtrowanie według warunków
            for intention_being in self.active_intentions.values():
                if self._matches_conditions(intention_being, conditions):
                    results.append(intention_being)
            
            # Sortowanie jeśli określono
            if 'sort_by' in conditions:
                results = self._sort_intentions(results, conditions['sort_by'], conditions.get('order', 'asc'))
            
            # Limit jeśli określono
            if 'limit' in conditions:
                results = results[:conditions['limit']]
            
            return results
            
        except Exception as e:
            if self.engine:
                self.engine.logger.error(f"❌ Błąd kontemplacji intencji: {e}")
            return []
    
    def _matches_conditions(self, intention: IntentionBeing, conditions: Dict[str, Any]) -> bool:
        """Sprawdza czy intencja spełnia warunki"""
        for key, value in conditions.items():
            if key in ['sort_by', 'order', 'limit']:
                continue
                
            if key == 'state':
                if isinstance(value, str):
                    if intention.state.value != value:
                        return False
                elif isinstance(value, IntentionState):
                    if intention.state != value:
                        return False
                        
            elif key == 'priority':
                if isinstance(value, str):
                    if intention.priority.name != value:
                        return False
                elif isinstance(value, int):
                    if intention.priority.value != value:
                        return False
                elif isinstance(value, IntentionPriority):
                    if intention.priority != value:
                        return False
                        
            elif key == 'opiekun':
                if intention.metainfo.opiekun != value:
                    return False
                    
            elif key == 'tag':
                if value not in intention.metainfo.tags:
                    return False
                    
            elif key == 'min_success':
                if intention.metainfo.wskaznik_sukcesu < value:
                    return False
                    
            elif key == 'min_harmony':
                if intention._calculate_harmony() < value:
                    return False
        
        return True
    
    def _sort_intentions(self, intentions: List[IntentionBeing], sort_by: str, order: str) -> List[IntentionBeing]:
        """Sortuje intencje według określonego kryterium"""
        reverse = order.lower() == 'desc'
        
        if sort_by == 'created_at':
            return sorted(intentions, key=lambda i: i.essence.created_at, reverse=reverse)
        elif sort_by == 'priority':
            return sorted(intentions, key=lambda i: i.priority.value, reverse=reverse)
        elif sort_by == 'success':
            return sorted(intentions, key=lambda i: i.metainfo.wskaznik_sukcesu, reverse=reverse)
        elif sort_by == 'harmony':
            return sorted(intentions, key=lambda i: i._calculate_harmony(), reverse=reverse)
        elif sort_by == 'name':
            return sorted(intentions, key=lambda i: i.essence.name or '', reverse=reverse)
        else:
            return intentions
    
    def transcend(self, intention_id: str) -> bool:
        """
        Transcenduje (usuwa/archiwizuje) intencję z wymiaru
        
        Args:
            intention_id: ID intencji do transcendencji
            
        Returns:
            True jeśli sukces
        """
        try:
            if intention_id not in self.active_intentions:
                return False
            
            intention = self.active_intentions[intention_id]
            
            # Usuń z kategorii
            self._remove_from_categories(intention)
            
            # Usuń z aktywnych
            del self.active_intentions[intention_id]
            self._being_count -= 1
            
            # Jeśli zakończona - zwiększ licznik
            if intention.state == IntentionState.COMPLETED:
                self.total_intentions_completed += 1
            
            # Auto-save po transcendencji
            self._save_persistence()
            
            # Emituj wydarzenie
            if self.engine and hasattr(self.engine, 'callback_flow') and self.engine.callback_flow:
                self.engine.callback_flow.emit_event('intentions', 'intention_transcended', {
                    'intention_id': intention_id,
                    'final_state': intention.state.value,
                    'success_score': intention.metainfo.wskaznik_sukcesu
                })
            
            if self.engine:
                self.engine.logger.info(f"🕊️ Intencja '{intention.essence.name}' transcendowała")
            
            return True
            
        except Exception as e:
            if self.engine:
                self.engine.logger.error(f"❌ Błąd transcendencji intencji: {e}")
            return False
    
    def _remove_from_categories(self, intention: IntentionBeing):
        """Usuwa intencję z kategorii"""
        # Usuń ze stanu
        if intention.essence.soul_id in self.intentions_by_state[intention.state]:
            self.intentions_by_state[intention.state].remove(intention.essence.soul_id)
        
        # Usuń z priorytetu
        if intention.essence.soul_id in self.intentions_by_priority[intention.priority]:
            self.intentions_by_priority[intention.priority].remove(intention.essence.soul_id)
    
    def evolve(self, intention_id: str, new_data: Dict[str, Any]) -> IntentionBeing:
        """
        Ewoluuje (aktualizuje) intencję
        
        Args:
            intention_id: ID intencji
            new_data: Nowe dane
            
        Returns:
            Zaktualizowana intencja
        """
        try:
            if intention_id not in self.active_intentions:
                raise ValueError(f"Intencja {intention_id} nie istnieje")
            
            intention = self.active_intentions[intention_id]
            
            # Aktualizuj warstwy
            if 'duchowa' in new_data:
                for key, value in new_data['duchowa'].items():
                    if hasattr(intention.duchowa, key):
                        setattr(intention.duchowa, key, value)
            
            if 'materialna' in new_data:
                for key, value in new_data['materialna'].items():
                    if hasattr(intention.materialna, key):
                        setattr(intention.materialna, key, value)
            
            if 'metainfo' in new_data:
                for key, value in new_data['metainfo'].items():
                    if hasattr(intention.metainfo, key):
                        setattr(intention.metainfo, key, value)
            
            # Aktualizuj kategoryzację jeśli stan lub priorytet się zmienił
            if 'state' in new_data or 'priority' in new_data:
                self._remove_from_categories(intention)
                
                if 'state' in new_data:
                    intention.state = IntentionState(new_data['state'])
                if 'priority' in new_data:
                    intention.priority = IntentionPriority(new_data['priority'])
                
                self._categorize_intention(intention)
            
            # Zapamiętaj ewolucję
            intention.remember('intention_evolved', {
                'changes': new_data,
                'evolved_at': datetime.now().isoformat()
            })
            
            # Auto-save po ewolucji
            self._save_persistence()
            
            return intention
            
        except Exception as e:
            if self.engine:
                self.engine.logger.error(f"❌ Błąd ewolucji intencji: {e}")
            raise
    
    def get_intention_by_id(self, intention_id: str) -> Optional[IntentionBeing]:
        """Pobiera intencję po ID"""
        return self.active_intentions.get(intention_id)
    
    def get_intentions_by_state(self, state: IntentionState) -> List[IntentionBeing]:
        """Pobiera intencje w określonym stanie"""
        intention_ids = self.intentions_by_state[state]
        return [self.active_intentions[id] for id in intention_ids if id in self.active_intentions]
    
    def get_intentions_by_priority(self, priority: IntentionPriority) -> List[IntentionBeing]:
        """Pobiera intencje o określonym priorytecie"""
        intention_ids = self.intentions_by_priority[priority]
        return [self.active_intentions[id] for id in intention_ids if id in self.active_intentions]
    
    def interact_with_intention(self, intention_id: str, interaction_type: str, data: Dict[str, Any], user_id: str = "system") -> Dict[str, Any]:
        """
        Interakcja z intencją
        
        Args:
            intention_id: ID intencji
            interaction_type: Typ interakcji
            data: Dane interakcji
            user_id: ID użytkownika
            
        Returns:
            Wynik interakcji
        """
        if intention_id not in self.active_intentions:
            return {'success': False, 'message': 'Intencja nie znaleziona'}
        
        intention = self.active_intentions[intention_id]
        result = intention.add_interaction(interaction_type, data, user_id)
        
        # Emituj wydarzenie
        if self.engine and hasattr(self.engine, 'callback_flow') and self.engine.callback_flow:
            self.engine.callback_flow.emit_event('intentions', 'intention_interaction', {
                'intention_id': intention_id,
                'interaction_type': interaction_type,
                'user_id': user_id,
                'result': result
            })
        
        return result
    
    def count_beings(self) -> int:
        """Zwraca liczbę aktywnych intencji"""
        return len(self.active_intentions)
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status wymiaru intencji"""
        base_status = super().get_status()
        
        intention_stats = {
            'active_intentions': len(self.active_intentions),
            'total_created': self.total_intentions_created,
            'total_completed': self.total_intentions_completed,
            'completion_rate': (self.total_intentions_completed / self.total_intentions_created) if self.total_intentions_created > 0 else 0.0,
            'states_distribution': {
                state.value: len(ids) for state, ids in self.intentions_by_state.items()
            },
            'priority_distribution': {
                priority.name: len(ids) for priority, ids in self.intentions_by_priority.items()
            },
            'average_success_score': self._calculate_average_success_score(),
            'average_harmony': self._calculate_average_harmony()
        }
        
        base_status['intention_specific'] = intention_stats
        return base_status
    
    def _calculate_average_success_score(self) -> float:
        """Oblicza średni wskaźnik sukcesu"""
        if not self.active_intentions:
            return 0.0
        
        total_score = sum(intention.metainfo.wskaznik_sukcesu for intention in self.active_intentions.values())
        return total_score / len(self.active_intentions)
    
    def _calculate_average_harmony(self) -> float:
        """Oblicza średnią harmonię"""
        if not self.active_intentions:
            return 0.0
        
        total_harmony = sum(intention._calculate_harmony() for intention in self.active_intentions.values())
        return total_harmony / len(self.active_intentions)
    
    def _save_persistence(self):
        """Zapisuje stan intencji do pliku JSON"""
        try:
            # Utwórz folder db jeśli nie istnieje
            os.makedirs('db', exist_ok=True)
            
            persistence_data = {
                'realm_name': self.name,
                'saved_at': datetime.now().isoformat(),
                'total_intentions_created': self.total_intentions_created,
                'total_intentions_completed': self.total_intentions_completed,
                'intentions': {}
            }
            
            # Serializuj wszystkie intencje
            for intention_id, intention in self.active_intentions.items():
                persistence_data['intentions'][intention_id] = {
                    'essence': {
                        'soul_id': intention.essence.soul_id,
                        'name': intention.essence.name,
                        'created_at': intention.essence.created_at.isoformat(),
                        'consciousness_level': intention.essence.consciousness_level,
                        'energy_level': intention.essence.energy_level
                    },
                    'state': intention.state.value,
                    'priority': intention.priority.value,
                    'duchowa_warstwa': intention.duchowa.to_dict(),
                    'materialna_warstwa': intention.materialna.to_dict(),
                    'metainfo': intention.metainfo.to_dict(),
                    'interactions': intention.interactions,
                    'memory': intention.memory
                }
            
            # Zapisz do pliku
            with open(self.persistence_file, 'w', encoding='utf-8') as f:
                json.dump(persistence_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            if self.engine:
                self.engine.logger.error(f"❌ Błąd zapisywania persystencji: {e}")
    
    def _load_persistence(self):
        """Ładuje stan intencji z pliku JSON"""
        try:
            if not os.path.exists(self.persistence_file):
                return
            
            with open(self.persistence_file, 'r', encoding='utf-8') as f:
                persistence_data = json.load(f)
            
            # Przywróć statystyki
            self.total_intentions_created = persistence_data.get('total_intentions_created', 0)
            self.total_intentions_completed = persistence_data.get('total_intentions_completed', 0)
            
            # Przywróć intencje
            intentions_data = persistence_data.get('intentions', {})
            
            for intention_id, intention_data in intentions_data.items():
                try:
                    # Rekonstruuj dane intencji
                    restored_data = {
                        'nazwa': intention_data['essence']['name'],
                        'priority': intention_data['priority'],
                        'duchowa': intention_data['duchowa_warstwa'],
                        'materialna': intention_data['materialna_warstwa'],
                        'metainfo': intention_data['metainfo']
                    }
                    
                    # Utwórz intencję bez auto-save
                    intention = IntentionBeing(restored_data, realm=self)
                    
                    # Przywróć stan i właściwości
                    intention.essence.soul_id = intention_data['essence']['soul_id']
                    intention.essence.created_at = datetime.fromisoformat(intention_data['essence']['created_at'])
                    intention.essence.consciousness_level = intention_data['essence']['consciousness_level']
                    intention.essence.energy_level = intention_data['essence']['energy_level']
                    intention.state = IntentionState(intention_data['state'])
                    intention.priority = IntentionPriority(intention_data['priority'])
                    intention.interactions = intention_data.get('interactions', [])
                    intention.memory = intention_data.get('memory', [])
                    
                    # Dodaj do aktywnych bez triggerowania auto-save
                    self.active_intentions[intention_id] = intention
                    self._categorize_intention(intention)
                    self._being_count += 1
                    
                except Exception as e:
                    if self.engine:
                        self.engine.logger.error(f"❌ Błąd przywracania intencji {intention_id}: {e}")
                        
        except Exception as e:
            if self.engine:
                self.engine.logger.error(f"❌ Błąd ładowania persystencji: {e}")
    
    def force_save(self):
        """Wymusza zapisanie persystencji (publiczna metoda)"""
        self._save_persistence()
        if self.engine:
            self.engine.logger.info(f"💾 Wymuszone zapisanie {len(self.active_intentions)} intencji")
    
    def get_persistence_info(self) -> Dict[str, Any]:
        """Zwraca informacje o persystencji"""
        persistence_exists = os.path.exists(self.persistence_file)
        file_size = 0
        last_modified = None
        
        if persistence_exists:
            stat = os.stat(self.persistence_file)
            file_size = stat.st_size
            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        return {
            'persistence_file': self.persistence_file,
            'file_exists': persistence_exists,
            'file_size_bytes': file_size,
            'last_modified': last_modified,
            'active_intentions_count': len(self.active_intentions)
        }
