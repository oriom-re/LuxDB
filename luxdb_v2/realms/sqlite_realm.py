
"""
💎 SQLiteRealm - Lekki Wymiar SQLite

Wymiar danych oparty na SQLite - idealny dla rozwoju i małych aplikacji
"""

import sqlite3
import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from .base_realm import BaseRealm


class SQLiteRealm(BaseRealm):
    """
    Wymiar danych SQLite - lekki i szybki
    """
    
    def __init__(self, name: str, connection_string: str, astral_engine):
        super().__init__(name, connection_string, astral_engine)
        
        # Parsuj connection string
        if connection_string.startswith('sqlite://'):
            self.db_path = connection_string[9:]
        else:
            self.db_path = connection_string
        
        # Utwórz katalog jeśli nie istnieje
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
        
        self.connection: Optional[sqlite3.Connection] = None
        self._initialize_schema()
    
    def connect(self) -> bool:
        """Nawiązuje połączenie z bazą SQLite"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Umożliwia dostęp po nazwach kolumn
            self.is_connected = True
            
            # Inicjalizuj schemat
            self._create_beings_table()
            
            self.engine.logger.info(f"💎 Połączono z wymiarem SQLite: {self.name}")
            return True
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd połączenia z wymiarem SQLite {self.name}: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Rozłącza z bazą SQLite"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            self.is_connected = False
            self.engine.logger.info(f"💎 Rozłączono z wymiarem SQLite: {self.name}")
            return True
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd rozłączania z wymiarem SQLite {self.name}: {e}")
            return False
    
    def _initialize_schema(self):
        """Inicjalizuje schemat bazy danych"""
        if not self.is_connected:
            self.connect()
    
    def _create_beings_table(self):
        """Tworzy tabelę dla bytów"""
        if not self.connection:
            return
        
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS astral_beings (
                soul_id INTEGER PRIMARY KEY AUTOINCREMENT,
                soul_name TEXT,
                essence TEXT,  -- JSON z danymi bytu
                energy_level REAL DEFAULT 100.0,
                realm_affinity TEXT,
                manifestation_time TEXT,
                last_evolution TEXT
            )
        ''')
        
        # Indeksy dla wydajności
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_soul_name ON astral_beings(soul_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_energy_level ON astral_beings(energy_level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_realm_affinity ON astral_beings(realm_affinity)')
        
        self.connection.commit()
    
    def manifest(self, being_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manifestuje nowy byt w wymiarze SQLite"""
        if not self.connection:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        # Przygotuj dane
        soul_name = being_data.get('soul_name', f'being_{datetime.now().timestamp()}')
        essence = json.dumps(being_data)
        energy_level = being_data.get('energy_level', 100.0)
        realm_affinity = being_data.get('realm_affinity', 'neutral')
        manifestation_time = datetime.now().isoformat()
        
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO astral_beings 
            (soul_name, essence, energy_level, realm_affinity, manifestation_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (soul_name, essence, energy_level, realm_affinity, manifestation_time))
        
        soul_id = cursor.lastrowid
        self.connection.commit()
        
        # Zwiększ licznik
        self._being_count += 1
        
        # Zwróć zmanifestowany byt
        result = being_data.copy()
        result['soul_id'] = soul_id
        result['manifestation_time'] = manifestation_time
        
        self.engine.logger.debug(f"✨ Manifestowano byt '{soul_name}' w wymiarze {self.name}")
        return result
    
    def contemplate(self, intention: str, **conditions) -> List[Dict[str, Any]]:
        """Kontempluje (wyszukuje) byty w wymiarze"""
        if not self.connection:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        # Buduj zapytanie na podstawie warunków
        query = "SELECT * FROM astral_beings"
        params = []
        where_clauses = []
        
        # Podstawowe filtry
        if 'soul_name' in conditions:
            where_clauses.append("soul_name = ?")
            params.append(conditions['soul_name'])
        
        if 'energy_level_min' in conditions:
            where_clauses.append("energy_level >= ?")
            params.append(conditions['energy_level_min'])
        
        if 'energy_level_max' in conditions:
            where_clauses.append("energy_level <= ?")
            params.append(conditions['energy_level_max'])
        
        if 'realm_affinity' in conditions:
            where_clauses.append("realm_affinity = ?")
            params.append(conditions['realm_affinity'])
        
        # Dodaj WHERE jeśli są warunki
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Sortowanie
        if 'order_by' in conditions:
            query += f" ORDER BY {conditions['order_by']}"
        else:
            query += " ORDER BY manifestation_time DESC"
        
        # Limit
        if 'limit' in conditions:
            query += f" LIMIT {conditions['limit']}"
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Konwertuj na słowniki
        results = []
        for row in rows:
            being = dict(row)
            # Parsuj essence z JSON
            if being['essence']:
                try:
                    essence_data = json.loads(being['essence'])
                    being.update(essence_data)
                except json.JSONDecodeError:
                    pass
            
            results.append(being)
        
        self.engine.logger.debug(f"🔍 Kontemplacja '{intention}' zwróciła {len(results)} bytów")
        return results
    
    def transcend(self, being_id: int) -> bool:
        """Transcenduje (usuwa) byt z wymiaru"""
        if not self.connection:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM astral_beings WHERE soul_id = ?", (being_id,))
        
        if cursor.rowcount > 0:
            self.connection.commit()
            self._being_count = max(0, self._being_count - 1)
            self.engine.logger.debug(f"🕊️ Byt {being_id} transcendował z wymiaru {self.name}")
            return True
        else:
            return False
    
    def evolve(self, being_id: int, new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ewoluuje (aktualizuje) byt"""
        if not self.connection:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        # Pobierz aktualny byt
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM astral_beings WHERE soul_id = ?", (being_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Połącz stare i nowe dane
        current_data = dict(row)
        if current_data['essence']:
            try:
                essence_data = json.loads(current_data['essence'])
                current_data.update(essence_data)
            except json.JSONDecodeError:
                pass
        
        # Aktualizuj danymi
        current_data.update(new_data)
        
        # Przygotuj nową essence
        new_essence = json.dumps(new_data)
        energy_level = new_data.get('energy_level', current_data.get('energy_level', 100.0))
        soul_name = new_data.get('soul_name', current_data.get('soul_name'))
        realm_affinity = new_data.get('realm_affinity', current_data.get('realm_affinity'))
        last_evolution = datetime.now().isoformat()
        
        # Aktualizuj w bazie
        cursor.execute('''
            UPDATE astral_beings 
            SET soul_name = ?, essence = ?, energy_level = ?, 
                realm_affinity = ?, last_evolution = ?
            WHERE soul_id = ?
        ''', (soul_name, new_essence, energy_level, realm_affinity, last_evolution, being_id))
        
        self.connection.commit()
        
        # Zwróć zaktualizowany byt
        result = current_data.copy()
        result['last_evolution'] = last_evolution
        
        self.engine.logger.debug(f"🦋 Byt {being_id} ewoluował w wymiarze {self.name}")
        return result
    
    def count_beings(self) -> int:
        """Zwraca liczbę bytów w wymiarze"""
        if not self.connection:
            return 0
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM astral_beings")
        result = cursor.fetchone()
        
        count = result[0] if result else 0
        self._being_count = count
        return count
    
    def optimize(self) -> None:
        """Optymalizuje wydajność wymiaru"""
        if not self.connection:
            return
        
        cursor = self.connection.cursor()
        cursor.execute("VACUUM")
        cursor.execute("ANALYZE")
        self.connection.commit()
        
        self.engine.logger.debug(f"⚡ Zoptymalizowano wymiar SQLite: {self.name}")
    
    def test_connection(self) -> bool:
        """Testuje połączenie z wymiarem"""
        try:
            if not self.connection:
                return False
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            return True
            
        except Exception:
            return False
    
    def get_beings_sample(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Zwraca próbkę bytów z wymiaru"""
        return self.contemplate("sample_beings", limit=limit)
