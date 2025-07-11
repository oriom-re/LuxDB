
#!/usr/bin/env python3
"""
🔌 Przykład klienta WebSocket dla StatefulTaskFlow
"""

import asyncio
import websockets
import json
import uuid

class StatefulTaskClient:
    """Klient WebSocket dla StatefulTaskFlow"""
    
    def __init__(self, ws_url: str = "ws://localhost:5001"):
        self.ws_url = ws_url
        self.client_uid = f"client_{uuid.uuid4().hex[:8]}"
        self.websocket = None
        self.received_chunks = {}
        self.confirmed_chunks = set()
    
    async def connect(self):
        """Połącz z serwerem WebSocket"""
        self.websocket = await websockets.connect(self.ws_url)
        print(f"🔌 Połączono z {self.ws_url}")
        
        # Nasłuchuj wiadomości
        asyncio.create_task(self._listen_for_messages())
    
    async def _listen_for_messages(self):
        """Nasłuchuje wiadomości z serwera"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self._handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Połączenie zamknięte")
        except Exception as e:
            print(f"❌ Błąd nasłuchiwania: {e}")
    
    async def _handle_message(self, data: dict):
        """Obsługuje wiadomości z serwera"""
        msg_type = data.get('type')
        
        if msg_type == 'welcome':
            print(f"👋 {data.get('message')}")
            
        elif msg_type == 'task_update':
            await self._handle_task_update(data)
            
        elif msg_type == 'task_created':
            print(f"🎯 Zadanie utworzone: {data.get('task', {}).get('task_id')}")
            
        elif msg_type == 'error':
            print(f"❌ Błąd: {data.get('message')}")
            
        else:
            print(f"📨 Odebrano: {msg_type}")
    
    async def _handle_task_update(self, data: dict):
        """Obsługuje aktualizacje zadania"""
        update_type = data.get('update_type')
        task_id = data.get('task_id')
        
        if update_type == 'chunk_available':
            chunk_data = data.get('data', {}).get('chunk', {})
            chunk_id = chunk_data.get('chunk_id')
            
            print(f"📦 Nowy chunk: {chunk_id}")
            
            # Zapisz chunk
            self.received_chunks[chunk_id] = chunk_data
            
            # Automatycznie potwierdź odbiór
            await self.confirm_chunk(task_id, chunk_id)
            
        elif update_type == 'task_completed':
            print(f"✅ Zadanie {task_id} zakończone")
            completion_data = data.get('data', {})
            print(f"   📊 Statystyki: {completion_data.get('final_stats', {})}")
            
            # Poczekaj chwilę i zarchiwizuj
            await asyncio.sleep(1)
            await self.archive_task(task_id)
            
        else:
            print(f"🔄 Aktualizacja zadania {task_id}: {update_type}")
    
    async def send_message(self, message: dict):
        """Wysyła wiadomość do serwera"""
        if self.websocket:
            await self.websocket.send(json.dumps(message))
    
    async def create_task(self, description: str, task_details: dict = None):
        """Tworzy nowe zadanie"""
        request_data = {
            "description": description,
            "task": task_details.get('task', description) if task_details else description,
            "requirements": task_details.get('requirements', []) if task_details else [],
            "expected_result": task_details.get('result', 'Pomyślne zakończenie') if task_details else 'Pomyślne zakończenie'
        }
        
        message = {
            'type': 'create_task',
            'client_uid': self.client_uid,
            'request_data': request_data
        }
        
        await self.send_message(message)
        print(f"📝 Wysłano żądanie utworzenia zadania: {description}")
    
    async def start_task(self, task_id: str):
        """Rozpoczyna przetwarzanie zadania"""
        message = {
            'type': 'start_task',
            'task_id': task_id
        }
        
        await self.send_message(message)
        print(f"🚀 Żądanie rozpoczęcia zadania: {task_id}")
    
    async def confirm_chunk(self, task_id: str, chunk_id: str):
        """Potwierdza odbiór chunka"""
        message = {
            'type': 'confirm_chunk',
            'task_id': task_id,
            'chunk_id': chunk_id
        }
        
        await self.send_message(message)
        self.confirmed_chunks.add(chunk_id)
        print(f"  ✅ Potwierdzono chunk: {chunk_id}")
    
    async def get_missing_chunks(self, task_id: str):
        """Pobiera brakujące chunki"""
        message = {
            'type': 'get_missing_chunks',
            'task_id': task_id
        }
        
        await self.send_message(message)
        print(f"🔍 Żądanie brakujących chunków dla: {task_id}")
    
    async def archive_task(self, task_id: str):
        """Archiwizuje zadanie"""
        message = {
            'type': 'archive_task',
            'task_id': task_id
        }
        
        await self.send_message(message)
        print(f"📁 Żądanie archiwizacji zadania: {task_id}")
    
    async def get_task_status(self, task_id: str):
        """Pobiera status zadania"""
        message = {
            'type': 'get_task_status',
            'task_id': task_id
        }
        
        await self.send_message(message)
        print(f"📊 Żądanie statusu zadania: {task_id}")
    
    async def close(self):
        """Zamyka połączenie"""
        if self.websocket:
            await self.websocket.close()
            print("🔌 Połączenie zamknięte")

async def demo_client():
    """Demonstracja klienta"""
    client = StatefulTaskClient()
    
    try:
        await client.connect()
        
        # Poczekaj na powitanie
        await asyncio.sleep(2)
        
        # Utwórz zadanie
        await client.create_task(
            "Analiza danych marketingowych Q3 2025",
            {
                'task': 'Przeanalizuj dane sprzedażowe i wygeneruj raport',
                'requirements': ['data_cleaning', 'statistical_analysis', 'visualization'],
                'result': 'Kompleksowy raport PDF z wykresami'
            }
        )
        
        # Poczekaj na zadanie i monitoruj
        await asyncio.sleep(20)
        
    except KeyboardInterrupt:
        print("\n👋 Kończenie...")
    finally:
        await client.close()

if __name__ == "__main__":
    print("🎯 StatefulTaskFlow WebSocket Client Demo")
    print("🔌 Łączenie z serwerem...")
    asyncio.run(demo_client())
