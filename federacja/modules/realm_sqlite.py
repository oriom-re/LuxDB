
"""
💎 SQLiteRealmModule - Moduł Wymiaru SQLite w Federacji
"""

import sqlite3
import json
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .realm_base import BaseRealmModule


class SQLiteRealmModule(BaseRealmModule):
    """
    Moduł wymiaru SQLite - lekki i szybki
    """
    
    def __init__(self, name: str, config: Dict[str, Any], bus):
        super().__init__(name, config, bus)
        
        # Parsuj konfigurację
        self.db_path = config.get('connection_string', f'db/{name}.db')
        if self.db_path.startswith('sqlite://'):
            self.db_path = self.db_path[9:]
        
        # Utwórz katalog jeśli nie istnieje
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
        
        self.connection: Optional[sqlite3.Connection] = None
    
    async def connect(self) -> bool:
        """Nawiązuje połączenie z bazą SQLite"""
        try:
            # SQLite połączenie w async kontekście
            loop = asyncio.get_event_loop()
            self.connection = await loop.run_in_executor(
                None, 
                lambda: sqlite3.connect(self.db_path, check_same_thread=False)
            )
            self.connection.row_factory = sqlite3.Row
            self.is_connected = True
            
            # Inicjalizuj schemat
            await self._create_beings_table()
            
            print(f"💎 Połączono z wymiarem SQLite: {self.name}")
            return True
            
        except Exception as e:
            print(f"❌ Błąd połączenia z wymiarem SQLite {self.name}: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącza z bazą SQLite"""
        try:
            if self.connection:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.connection.close)
                self.connection = None
            self.is_connected = False
            print(f"💎 Rozłączono z wymiarem SQLite: {self.name}")
            return True
            
        except Exception as e:
            print(f"❌ Błąd rozłączania z wymiarem SQLite {self.name}: {e}")
            return False
    
    async def _create_beings_table(self):
        """Tworzy tabelę dla bytów"""
        if not self.connection:
            return
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._execute_schema_creation)
    
    def _execute_schema_creation(self):
        """Wykonuje tworzenie schematu (w executor)"""
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
    
    async def manifest(self, being_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manifestuje nowy byt w wymiarze SQLite"""
        if not self.connection:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        # Przygotuj dane
        soul_name = being_data.get('soul_name', f'being_{datetime.now().timestamp()}')
        essence = json.dumps(being_data)
        energy_level = being_data.get('energy_level', 100.0)
        realm_affinity = being_data.get('realm_affinity', 'neutral')
        manifestation_time = datetime.now().isoformat()
        
        loop = asyncio.get_event_loop()
        soul_id = await loop.run_in_executor(
            None,
            self._execute_manifest,
            soul_name, essence, energy_level, realm_affinity, manifestation_time
        )
        
        # Zwiększ licznik
        self._being_count += 1
        
        # Zwróć zmanifestowany byt
        result = being_data.copy()
        result['soul_id'] = soul_id
        result['manifestation_time'] = manifestation_time
        
        print(f"✨ Manifestowano byt '{soul_name}' w wymiarze {self.name}")
        return result
    
    def _execute_manifest(self, soul_name, essence, energy_level, realm_affinity, manifestation_time):
        """Wykonuje manifestację w executor"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO astral_beings 
            (soul_name, essence, energy_level, realm_affinity, manifestation_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (soul_name, essence, energy_level, realm_affinity, manifestation_time))
        
        soul_id = cursor.lastrowid
        self.connection.commit()
        return soul_id
    
    async def contemplate(self, intention: str, **conditions) -> List[Dict[str, Any]]:
        """Kontempluje (wyszukuje) byty w wymiarze"""
        if not self.connection:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            self._execute_contemplate,
            intention, conditions
        )
        
        print(f"🔍 Kontemplacja '{intention}' zwróciła {len(results)} bytów")
        return results
    
    def _execute_contemplate(self, intention: str, conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Wykonuje kontemplację w executor"""
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
        
        return results
    
    async def transcend(self, being_id: int) -> bool:
        """Transcenduje (usuwa) byt z wymiaru"""
        if not self.connection:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            None,
            self._execute_transcend,
            being_id
        )
        
        if success:
            self._being_count = max(0, self._being_count - 1)
            print(f"🕊️ Byt {being_id} transcendował z wymiaru {self.name}")
        
        return success
    
    def _execute_transcend(self, being_id: int) -> bool:
        """Wykonuje transcendencję w executor"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM astral_beings WHERE soul_id = ?", (being_id,))
        
        if cursor.rowcount > 0:
            self.connection.commit()
            return True
        else:
            return False
    
    async def evolve(self, being_id: int, new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ewoluuje (aktualizuje) byt"""
        if not self.connection:
            raise RuntimeError("Brak połączenia z wymiarem")
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._execute_evolve,
            being_id, new_data
        )
        
        if result:
            print(f"🦋 Byt {being_id} ewoluował w wymiarze {self.name}")
        
        return result
    
    def _execute_evolve(self, being_id: int, new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Wykonuje ewolucję w executor"""
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
        
        return result
    
    async def count_beings(self) -> int:
        """Zwraca liczbę bytów w wymiarze"""
        if not self.connection:
            return 0
        
        loop = asyncio.get_event_loop()
        count = await loop.run_in_executor(None, self._execute_count)
        self._being_count = count
        return count
    
    def _execute_count(self) -> int:
        """Wykonuje liczenie w executor"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM astral_beings")
        result = cursor.fetchone()
        return result[0] if result else 0
