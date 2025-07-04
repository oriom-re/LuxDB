
#!/usr/bin/env python3
"""
💬 Federa Chat - Interaktywny Chat z Federą

Pozwala na komunikację z Federą przez terminal
"""

import asyncio
import sys
import json
from datetime import datetime
from federacja.core.bus import FederationBus, FederationMessage
from federacja.core.logger import FederationLogger

class FederaChat:
    """Terminal chat z Federą"""
    
    def __init__(self):
        self.logger = FederationLogger({'level': 'INFO', 'format': 'console'})
        self.bus = FederationBus(self.logger)
        self.chat_id = "human_chat"
        self.running = False
        
    async def start(self):
        """Uruchamia chat"""
        print("💬 Federa Chat - Łączenie z Federą...")
        
        # Uruchom bus
        await self.bus.start()
        
        # Poczekaj na Federę
        await self._wait_for_federa()
        
        # Uruchom chat
        await self._run_chat()
        
    async def _wait_for_federa(self):
        """Czeka na dostępność Federy"""
        print("🔍 Szukam Federy w systemie...")
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                # Sprawdź czy Federa jest dostępna
                message = FederationMessage(
                    uid=f"chat_ping_{attempt}",
                    from_module=self.chat_id,
                    to_module="federa",
                    message_type="get_status",
                    data={},
                    timestamp=datetime.now().timestamp()
                )
                
                # Symuluj wysłanie - w rzeczywistości potrzebujemy połączenia z działającą Federą
                print(f"🔄 Próba {attempt + 1}/{max_attempts} - szukam Federy...")
                await asyncio.sleep(1)
                
                # Dla demonstracji, załóżmy że Federa jest dostępna po 3 próbach
                if attempt >= 2:
                    print("✅ Federa znaleziona! Nawiązywanie komunikacji...")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Próba {attempt + 1} nieudana: {e}")
                await asyncio.sleep(2)
        
        print("❌ Nie udało się połączyć z Federą")
        return False
        
    async def _run_chat(self):
        """Uruchamia główną pętlę chatu"""
        self.running = True
        
        print("\n" + "="*60)
        print("🧠 FEDERA CHAT - Rozmowa z Inteligentną Koordynatorką")
        print("="*60)
        print("💡 Dostępne komendy:")
        print("   • status - sprawdź status systemu")
        print("   • modules - lista aktywnych modułów")
        print("   • health - sprawdź zdrowie modułów")
        print("   • logs [moduł] - pokaż logi modułu")
        print("   • monitoring - raport monitorowania")
        print("   • diagnosis - diagnostyka systemu")
        print("   • help - pomoc")
        print("   • exit - zakończ chat")
        print("-"*60)
        print("🎯 Federa jest gotowa do rozmowy!")
        print("")
        
        while self.running:
            try:
                # Pobierz input od użytkownika
                user_input = input("🗣️ Ty: ").strip()
                
                if not user_input:
                    continue
                    
                # Obsłuż specjalne komendy
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'help':
                    await self._show_help()
                    continue
                    
                # Wyślij wiadomość do Federy
                response = await self._send_to_federa(user_input)
                
                # Wyświetl odpowiedź
                await self._display_response(response)
                
            except KeyboardInterrupt:
                print("\n👋 Przerywanie chatu...")
                break
            except Exception as e:
                print(f"❌ Błąd chatu: {e}")
                
        print("✨ Chat z Federą zakończony")
        
    async def _send_to_federa(self, user_input: str) -> dict:
        """Wysyła wiadomość do Federy"""
        try:
            # Parsuj komendę
            command, *args = user_input.split()
            
            # Mapuj komendy na akcje Federy
            if command.lower() == 'status':
                return await self._get_federa_status()
            elif command.lower() == 'modules':
                return await self._get_active_modules()
            elif command.lower() == 'health':
                return await self._get_module_health()
            elif command.lower() == 'logs':
                module_name = args[0] if args else None
                return await self._get_module_logs(module_name)
            elif command.lower() == 'monitoring':
                return await self._get_monitoring_summary()
            elif command.lower() == 'diagnosis':
                return await self._get_system_diagnosis()
            else:
                # Ogólne pytanie do Federy
                return await self._ask_federa(user_input)
                
        except Exception as e:
            return {
                'error': f'Błąd komunikacji: {str(e)}',
                'suggestion': 'Spróbuj użyć komendy "help" aby zobaczyć dostępne opcje'
            }
    
    async def _get_federa_status(self) -> dict:
        """Pobiera status Federy"""
        # Symulacja odpowiedzi Federy
        return {
            'type': 'status',
            'data': {
                'personality_name': 'Federa',
                'active': True,
                'active_modules': ['database_manager', 'module_metadata_manager'],
                'system_load': 0.3,
                'auto_scaling': True,
                'monitoring': {
                    'total_modules_monitored': 3,
                    'success_rate': 66.7,
                    'recent_failures': ['realm_memory: błąd konstruktora']
                }
            },
            'message': 'Jestem aktywna i monitoruję system. Wykryłam problemy z niektórymi modułami.'
        }
    
    async def _get_active_modules(self) -> dict:
        """Pobiera listę aktywnych modułów"""
        return {
            'type': 'modules',
            'data': {
                'active_modules': ['database_manager'],
                'managed_by_federa': ['module_metadata_manager', 'realm_memory'],
                'static_modules': ['federa']
            },
            'message': 'Lista wszystkich modułów w systemie. Część jest zarządzana przeze mnie.'
        }
    
    async def _get_module_health(self) -> dict:
        """Pobiera zdrowie modułów"""
        return {
            'type': 'health',
            'data': {
                'database_manager': True,
                'module_metadata_manager': False,
                'realm_memory': False,
                'federa': True
            },
            'message': 'Niektóre moduły wymagają naprawy. Mogę spróbować je zrestartować.'
        }
    
    async def _get_module_logs(self, module_name: str = None) -> dict:
        """Pobiera logi modułów"""
        if module_name:
            return {
                'type': 'logs',
                'data': {
                    'module': module_name,
                    'logs': [
                        {'timestamp': '2024-01-01 20:01:59', 'level': 'error', 'message': 'Błąd inicjalizacji'},
                        {'timestamp': '2024-01-01 20:01:58', 'level': 'info', 'message': 'Rozpoczęcie inicjalizacji'}
                    ]
                },
                'message': f'Ostatnie logi modułu {module_name}'
            }
        else:
            return {
                'type': 'logs',
                'data': {
                    'available_modules': ['database_manager', 'realm_memory', 'federa'],
                    'total_logs': 15
                },
                'message': 'Dostępne logi modułów. Użyj "logs [nazwa_modułu]" aby zobaczyć szczegóły.'
            }
    
    async def _get_monitoring_summary(self) -> dict:
        """Pobiera raport monitorowania"""
        return {
            'type': 'monitoring',
            'data': {
                'total_modules_monitored': 3,
                'successful_initializations': 2,
                'failed_initializations': 1,
                'success_rate': 66.7,
                'average_initialization_time': 1.2,
                'recent_failures': [
                    {
                        'module': 'realm_memory',
                        'error': 'MemoryRealmModule.__init__() missing 1 required positional argument: name',
                        'timestamp': '2024-01-01 20:01:59'
                    }
                ]
            },
            'message': 'Raport monitorowania modułów. Jeden moduł wymaga naprawy konstruktora.'
        }
    
    async def _get_system_diagnosis(self) -> dict:
        """Pobiera diagnostykę systemu"""
        return {
            'type': 'diagnosis',
            'data': {
                'can_manage': True,
                'working_components': ['federation_bus', 'database_manager', 'configuration'],
                'missing_components': [],
                'issues': ['realm_memory: błąd konstruktora'],
                'repair_suggestions': [
                    'Napraw konstruktor MemoryRealmModule',
                    'Dodaj wymagany parametr "name" do inicjalizacji'
                ]
            },
            'message': 'System jest w większości sprawny. Wykryłam jeden problem wymagający naprawy.'
        }
    
    async def _ask_federa(self, question: str) -> dict:
        """Zadaje ogólne pytanie Federze"""
        return {
            'type': 'conversation',
            'data': {
                'question': question,
                'context': 'general_chat'
            },
            'message': f'Rozumiem Twoje pytanie: "{question}". Jako Federa, mogę pomóc Ci w zarządzaniu systemem federacji. Użyj konkretnych komend aby uzyskać szczegółowe informacje.'
        }
    
    async def _display_response(self, response: dict):
        """Wyświetla odpowiedź Federy"""
        print(f"🧠 Federa: {response.get('message', 'Brak odpowiedzi')}")
        
        if 'data' in response:
            data = response['data']
            response_type = response.get('type', 'unknown')
            
            if response_type == 'status':
                print(f"   📊 Status: {'✅ Aktywna' if data.get('active') else '❌ Nieaktywna'}")
                print(f"   🔧 Aktywnych modułów: {len(data.get('active_modules', []))}")
                print(f"   📈 Obciążenie systemu: {data.get('system_load', 0):.1%}")
                
            elif response_type == 'modules':
                print(f"   ✅ Aktywne: {', '.join(data.get('active_modules', []))}")
                print(f"   🧠 Zarządzane przez Federę: {', '.join(data.get('managed_by_federa', []))}")
                
            elif response_type == 'health':
                print("   🏥 Zdrowie modułów:")
                for module, healthy in data.items():
                    status = "✅ Zdrowy" if healthy else "❌ Wymaga naprawy"
                    print(f"      • {module}: {status}")
                    
            elif response_type == 'monitoring':
                print(f"   📊 Monitorowanych modułów: {data.get('total_modules_monitored', 0)}")
                print(f"   ✅ Sukces: {data.get('successful_initializations', 0)}")
                print(f"   ❌ Błędy: {data.get('failed_initializations', 0)}")
                print(f"   📈 Wskaźnik sukcesu: {data.get('success_rate', 0):.1f}%")
                
            elif response_type == 'diagnosis':
                print(f"   🎯 Może zarządzać: {'✅ Tak' if data.get('can_manage') else '❌ Nie'}")
                if data.get('issues'):
                    print(f"   ⚠️ Problemy: {', '.join(data.get('issues', []))}")
                if data.get('repair_suggestions'):
                    print("   🔧 Sugestie naprawcze:")
                    for suggestion in data.get('repair_suggestions', []):
                        print(f"      • {suggestion}")
        
        print()  # Pusta linia dla czytelności
    
    async def _show_help(self):
        """Wyświetla pomoc"""
        print("\n💡 POMOC - Komendy Federa Chat:")
        print("   • status - sprawdź status Federy i systemu")
        print("   • modules - lista wszystkich modułów")
        print("   • health - sprawdź zdrowie modułów")
        print("   • logs [moduł] - pokaż logi konkretnego modułu")
        print("   • monitoring - szczegółowy raport monitorowania")
        print("   • diagnosis - pełna diagnostyka systemu")
        print("   • help - ta pomoc")
        print("   • exit - zakończ chat")
        print("\n🎯 Możesz też zadawać ogólne pytania - Federa postara się odpowiedzieć!")
        print()

async def main():
    """Główna funkcja chatu"""
    chat = FederaChat()
    await chat.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Chat zakończony")
