
"""
💎 SQLiteRealmModule - Moduł Wymiaru SQLite w Federacji
"""

import sqlite3
import json
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_realm import BaseRealmModule


class SQLiteRealmModule(BaseRealmModule):
    """
    Moduł wymiaru SQLite - trwałe przechowywanie danych
    """
    
    def __init__(self, name: str, config: Dict[str, Any], bus):
        super().__init__(name, config, bus)
        
        # Konfiguracja
        self.db_path = config.get('db_path', f'db/{name}.db')
        self.table_name = config.get('table_name', 'beings')
        
        # Połączenie z bazą
        self.connection: Optional[sqlite3.Connection] = None
        
        # Upewnij się że folder istnieje
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    async def connect(self) -> bool:
        """Nawiązuje połączenie z wymiarem SQLite"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self.connection.row_factory = sqlite3.Row
            
            # Utwórz tabelę bytów
            await self._create_table()
            
            self.is_connected = True
            print(f"💎 Połączono z wymiarem SQLite: {self.module_id}")
            return True
            
        except Exception as e:
            print(f"❌ Błąd połączenia z wymiarem SQLite: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącza z wymiarem SQLite"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            
            self.is_connected = False
            print(f"💎 Rozłączono z wymiarem SQLite: {self.module_id}")
            return True
            
        except Exception as e:
            print(f"❌ Błąd rozłączania z wymiarem SQLite: {e}")
            return False
    
    async def _create_table(self):
        """Tworzy tabelę bytów"""
        cursor = self.connection.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                soul_id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.connection.commit()
    
    async def manifest(self, being_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manifestuje nowy byt w wymiarze SQLite"""
        cursor = self.connection.cursor()
        
        # Serializuj dane
        data_json = json.dumps(being_data)
        
        # Wstaw byt
        cursor.execute(f'''
            INSERT INTO {self.table_name} (data)
            VALUES (?)
        ''', (data_json,))
        
        soul_id = cursor.lastrowid
        self.connection.commit()
        
        # Pobierz pełny byt
        cursor.execute(f'''
            SELECT soul_id, data, created_at, modified_at
            FROM {self.table_name}
            WHERE soul_id = ?
        ''', (soul_id,))
        
        row = cursor.fetchone()
        being = {
            'soul_id': row['soul_id'],
            'created_at': row['created_at'],
            'modified_at': row['modified_at'],
            **json.loads(row['data'])
        }
        
        self._being_count += 1
        print(f"💎 Manifestowano byt {soul_id} w wymiarze SQLite")
        return being
    
    async def contemplate(self, intention: str, **conditions) -> List[Dict[str, Any]]:
        """Kontempluje byty w wymiarze SQLite"""
        cursor = self.connection.cursor()
        
        # Podstawowe zapytanie
        query = f'SELECT soul_id, data, created_at, modified_at FROM {self.table_name}'
        params = []
        
        # Dodaj warunki (proste - bez indeksowania JSON)
        if conditions:
            where_clauses = []
            for key, value in conditions.items():
                where_clauses.append(f"json_extract(data, '$.{key}') = ?")
                params.append(value)
            
            if where_clauses:
                query += ' WHERE ' + ' AND '.join(where_clauses)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Konwertuj na słowniki
        results = []
        for row in rows:
            being = {
                'soul_id': row['soul_id'],
                'created_at': row['created_at'],
                'modified_at': row['modified_at'],
                **json.loads(row['data'])
            }
            results.append(being)
        
        print(f"💎 Kontemplacja w wymiarze SQLite: {len(results)} bytów")
        return results
    
    async def transcend(self, being_id: Any) -> bool:
        """Transcenduje byt z wymiaru SQLite"""
        cursor = self.connection.cursor()
        
        cursor.execute(f'''
            DELETE FROM {self.table_name}
            WHERE soul_id = ?
        ''', (int(being_id),))
        
        success = cursor.rowcount > 0
        self.connection.commit()
        
        if success:
            self._being_count -= 1
            print(f"💎 Transcendowano byt {being_id} z wymiaru SQLite")
        
        return success
    
    async def evolve(self, being_id: Any, new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ewoluuje byt w wymiarze SQLite"""
        cursor = self.connection.cursor()
        
        # Pobierz aktualny byt
        cursor.execute(f'''
            SELECT data FROM {self.table_name}
            WHERE soul_id = ?
        ''', (int(being_id),))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Połącz stare i nowe dane
        current_data = json.loads(row['data'])
        current_data.update(new_data)
        
        # Zaktualizuj byt
        cursor.execute(f'''
            UPDATE {self.table_name}
            SET data = ?, modified_at = CURRENT_TIMESTAMP
            WHERE soul_id = ?
        ''', (json.dumps(current_data), int(being_id)))
        
        self.connection.commit()
        
        # Pobierz zaktualizowany byt
        cursor.execute(f'''
            SELECT soul_id, data, created_at, modified_at
            FROM {self.table_name}
            WHERE soul_id = ?
        ''', (int(being_id),))
        
        row = cursor.fetchone()
        being = {
            'soul_id': row['soul_id'],
            'created_at': row['created_at'],
            'modified_at': row['modified_at'],
            **json.loads(row['data'])
        }
        
        print(f"💎 Ewoluowano byt {being_id} w wymiarze SQLite")
        return being
    
    async def count_beings(self) -> int:
        """Zwraca liczbę bytów w wymiarze"""
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT COUNT(*) as count FROM {self.table_name}')
        result = cursor.fetchone()
        return result['count']
