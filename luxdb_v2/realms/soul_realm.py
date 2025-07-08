
"""
🕯️ SoulRealm - Wymiar Dusz

Przechowuje reprezentacje dusz w bazie danych zamiast w kodzie.
Każda dusza to JSON z definicją typu, roli, intencji i pamięci.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from .sqlite_realm import SqliteRealm


class SoulRealm(SqliteRealm):
    """
    Wymiar dusz - przechowuje dusze jako struktury JSON w bazie
    """
    
    def __init__(self, name: str, connection_string: str, astral_engine):
        super().__init__(name, connection_string, astral_engine)
        self.soul_schema = {
            'id': 'TEXT PRIMARY KEY',
            'type': 'TEXT NOT NULL',
            'role': 'TEXT',
            'intents': 'TEXT',  # JSON array
            'memory': 'TEXT',   # JSON object
            'sockets': 'TEXT',  # JSON object
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'status': 'TEXT DEFAULT "dormant"',
            'energy_level': 'REAL DEFAULT 100.0'
        }
    
    def connect(self) -> bool:
        """Nawiązuje połączenie i tworzy tabelę dusz"""
        if super().connect():
            try:
                # Tworzenie tabeli souls
                columns = []
                for column, definition in self.soul_schema.items():
                    columns.append(f"{column} {definition}")
                
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS souls (
                    {', '.join(columns)}
                )
                """
                
                self.cursor.execute(create_table_sql)
                self.connection.commit()
                
                self.engine.logger.info(f"🕯️ SoulRealm '{self.name}' połączony i gotowy")
                return True
                
            except Exception as e:
                self.engine.logger.error(f"❌ Błąd tworzenia tabeli dusz: {e}")
                return False
        return False
    
    def manifest_soul(self, soul_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manifestuje nową duszę w wymiarze"""
        if not self.is_connected:
            self.connect()
        
        try:
            # Walidacja i przygotowanie danych
            soul_id = soul_data.get('id')
            if not soul_id:
                raise ValueError("Dusza musi mieć ID")
            
            soul_type = soul_data.get('type', 'unknown')
            role = soul_data.get('role', '')
            intents = json.dumps(soul_data.get('intents', []))
            memory = json.dumps(soul_data.get('memory', {}))
            sockets = json.dumps(soul_data.get('sockets', {}))
            status = soul_data.get('status', 'dormant')
            energy_level = soul_data.get('energy_level', 100.0)
            
            # Wstaw do bazy
            insert_sql = """
            INSERT OR REPLACE INTO souls 
            (id, type, role, intents, memory, sockets, status, energy_level, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            
            self.cursor.execute(insert_sql, (
                soul_id, soul_type, role, intents, memory, sockets, status, energy_level
            ))
            self.connection.commit()
            
            # Pobierz pełną duszę z bazy
            manifested_soul = self.get_soul(soul_id)
            
            self.engine.logger.info(f"🕯️ Dusza '{soul_id}' zmanifestowana w wymiarze dusz")
            return manifested_soul
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd manifestacji duszy: {e}")
            raise
    
    def get_soul(self, soul_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera duszę po ID"""
        if not self.is_connected:
            self.connect()
        
        try:
            select_sql = "SELECT * FROM souls WHERE id = ?"
            self.cursor.execute(select_sql, (soul_id,))
            row = self.cursor.fetchone()
            
            if row:
                return self._row_to_soul(row)
            return None
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd pobierania duszy {soul_id}: {e}")
            return None
    
    def find_souls(self, soul_type: str = None, role: str = None, 
                   status: str = None, has_intent: str = None) -> List[Dict[str, Any]]:
        """Znajduje dusze według kryteriów"""
        if not self.is_connected:
            self.connect()
        
        try:
            conditions = []
            params = []
            
            if soul_type:
                conditions.append("type = ?")
                params.append(soul_type)
            
            if role:
                conditions.append("role = ?")
                params.append(role)
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if has_intent:
                conditions.append("intents LIKE ?")
                params.append(f'%"{has_intent}"%')
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            select_sql = f"SELECT * FROM souls{where_clause} ORDER BY created_at DESC"
            
            self.cursor.execute(select_sql, params)
            rows = self.cursor.fetchall()
            
            return [self._row_to_soul(row) for row in rows]
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd wyszukiwania dusz: {e}")
            return []
    
    def awaken_soul(self, soul_id: str) -> bool:
        """Budzi duszę (zmienia status na active)"""
        return self.update_soul_status(soul_id, 'active')
    
    def rest_soul(self, soul_id: str) -> bool:
        """Pozwala duszy odpocząć (zmienia status na dormant)"""
        return self.update_soul_status(soul_id, 'dormant')
    
    def focus_soul(self, soul_id: str, intent: str) -> bool:
        """Skupia duszę na intencji (zmienia status na focused)"""
        return self.update_soul_status(soul_id, 'focused')
    
    def update_soul_status(self, soul_id: str, new_status: str) -> bool:
        """Aktualizuje status duszy"""
        if not self.is_connected:
            self.connect()
        
        try:
            update_sql = """
            UPDATE souls 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """
            
            self.cursor.execute(update_sql, (new_status, soul_id))
            self.connection.commit()
            
            if self.cursor.rowcount > 0:
                self.engine.logger.info(f"🕯️ Dusza '{soul_id}' zmienila status na '{new_status}'")
                return True
            else:
                self.engine.logger.warning(f"⚠️ Nie znaleziono duszy '{soul_id}'")
                return False
                
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd aktualizacji statusu duszy {soul_id}: {e}")
            return False
    
    def add_memory_to_soul(self, soul_id: str, memory_type: str, memory_data: Any) -> bool:
        """Dodaje wspomnienie do duszy"""
        soul = self.get_soul(soul_id)
        if not soul:
            return False
        
        try:
            memory = json.loads(soul['memory'])
            
            if memory_type not in memory:
                memory[memory_type] = []
            
            memory[memory_type].append({
                'timestamp': datetime.now().isoformat(),
                'data': memory_data
            })
            
            # Ogranicz liczbę wspomnień (ostatnie 100)
            if len(memory[memory_type]) > 100:
                memory[memory_type] = memory[memory_type][-100:]
            
            return self.update_soul_memory(soul_id, memory)
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd dodawania pamięci do duszy {soul_id}: {e}")
            return False
    
    def update_soul_memory(self, soul_id: str, memory: Dict[str, Any]) -> bool:
        """Aktualizuje pamięć duszy"""
        if not self.is_connected:
            self.connect()
        
        try:
            update_sql = """
            UPDATE souls 
            SET memory = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """
            
            self.cursor.execute(update_sql, (json.dumps(memory), soul_id))
            self.connection.commit()
            
            return self.cursor.rowcount > 0
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd aktualizacji pamięci duszy {soul_id}: {e}")
            return False
    
    def _row_to_soul(self, row) -> Dict[str, Any]:
        """Konwertuje wiersz z bazy na strukturę duszy"""
        columns = [desc[0] for desc in self.cursor.description]
        soul_dict = dict(zip(columns, row))
        
        # Parsuj JSON fields
        try:
            soul_dict['intents'] = json.loads(soul_dict['intents']) if soul_dict['intents'] else []
            soul_dict['memory'] = json.loads(soul_dict['memory']) if soul_dict['memory'] else {}
            soul_dict['sockets'] = json.loads(soul_dict['sockets']) if soul_dict['sockets'] else {}
        except json.JSONDecodeError as e:
            self.engine.logger.warning(f"⚠️ Błąd parsowania JSON dla duszy {soul_dict['id']}: {e}")
            soul_dict['intents'] = []
            soul_dict['memory'] = {}
            soul_dict['sockets'] = {}
        
        return soul_dict
    
    def get_soul_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki wymiaru dusz"""
        if not self.is_connected:
            self.connect()
        
        try:
            stats_sql = """
            SELECT 
                COUNT(*) as total_souls,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_souls,
                COUNT(CASE WHEN status = 'dormant' THEN 1 END) as dormant_souls,
                COUNT(CASE WHEN status = 'focused' THEN 1 END) as focused_souls,
                AVG(energy_level) as avg_energy
            FROM souls
            """
            
            self.cursor.execute(stats_sql)
            row = self.cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                stats = dict(zip(columns, row))
                stats['avg_energy'] = round(stats['avg_energy'] or 0, 2)
                return stats
            
            return {
                'total_souls': 0,
                'active_souls': 0,
                'dormant_souls': 0,
                'focused_souls': 0,
                'avg_energy': 0
            }
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd pobierania statystyk dusz: {e}")
            return {}
    
    def clear_souls(self) -> int:
        """Czyści wszystkie dusze z wymiaru"""
        if not self.is_connected:
            self.connect()
        
        try:
            count_sql = "SELECT COUNT(*) FROM souls"
            self.cursor.execute(count_sql)
            count = self.cursor.fetchone()[0]
            
            delete_sql = "DELETE FROM souls"
            self.cursor.execute(delete_sql)
            self.connection.commit()
            
            self.engine.logger.info(f"🧹 Usunięto {count} dusz z wymiaru")
            return count
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd czyszczenia dusz: {e}")
            return 0
