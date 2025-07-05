
"""
🗣️ PersonalityQuery - Demonstracja Zapytań Między Osobowościami

Pokazuje jak różne osobowości mogą:
1. Zapytać o swoje własne dane
2. Próbować dostać się do danych innych
3. Otrzymywać odmowy dostępu z humorystycznymi komentarzami
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

from ..core.bus import FederationBus, FederationMessage
from ..core.lux_module import LuxModule, ModuleType, ModuleVersion


class PersonalityQuery(LuxModule):
    """
    Moduł demonstracyjny dla zapytań między osobowościami
    """
    
    def __init__(self, name: str, config: Dict[str, Any], bus: FederationBus):
        super().__init__(
            name="personality_query",
            module_type=ModuleType.UTILITY,
            version=ModuleVersion(1, 0, 0),
            config=config,
            bus=bus,
            creator_id="federation_system"
        )
        
        self.query_examples = []
        
    async def initialize(self) -> bool:
        """Inicjalizuje moduł zapytań"""
        try:
            await self._register_commands()
            await self._setup_demo_queries()
            
            self.is_active = True
            print("🗣️ PersonalityQuery zainicjalizowany")
            return True
            
        except Exception as e:
            print(f"❌ Błąd inicjalizacji PersonalityQuery: {e}")
            return False
    
    async def _register_commands(self):
        """Rejestruje komendy"""
        commands = {
            'demo_personality_queries': self._handle_demo_queries,
            'query_as_personality': self._handle_query_as_personality,
            'cross_personality_attempt': self._handle_cross_personality_attempt,
            'get_status': self._handle_get_status
        }
        
        for cmd_name, cmd_func in commands.items():
            await self.bus.register_command(f"personality_query.{cmd_name}", cmd_func)
    
    async def _setup_demo_queries(self):
        """Przygotowuje przykładowe zapytania"""
        await asyncio.sleep(2)  # Poczekaj aż RealmManager się uruchomi
        
        # Przykładowe zapytania demonstracyjne
        await self._demo_federa_queries()
        await self._demo_cross_personality_attempts()
    
    async def _demo_federa_queries(self):
        """Demonstracja zapytań Federy do swojej bazy"""
        print("\n" + "="*60)
        print("🧠 FEDERA - Zapytania do własnego wymiaru")
        print("="*60)
        
        # Zapytanie 1: Lista modułów
        result1 = await self._query_realm("federa", 
            "SELECT * FROM modules ORDER BY created_at DESC LIMIT 3")
        print(f"📊 Federa sprawdza swoje moduły: {len(result1.get('result', []))} wyników")
        
        # Zapytanie 2: Ostatnie decyzje
        result2 = await self._query_realm("federa",
            "SELECT decision_type, reasoning FROM decisions ORDER BY created_at DESC LIMIT 2")
        print(f"🧠 Federa analizuje swoje decyzje: {len(result2.get('result', []))} decyzji")
        
        # Zapytanie 3: System config
        result3 = await self._query_realm("federa",
            "SELECT key, value FROM system_config WHERE personality_owner = 'federa'")
        print(f"⚙️ Federa sprawdza swoją konfigurację: {len(result3.get('result', []))} ustawień")
    
    async def _demo_cross_personality_attempts(self):
        """Demonstracja prób dostępu między osobowościami"""
        print("\n" + "="*60)
        print("🎭 PRÓBY CROSS-PERSONALITY ACCESS")
        print("="*60)
        
        # Lux próbuje dostać się do danych Astry
        print("\n💫 Lux próbuje sprawdzić mądrość Astry...")
        result_lux = await self._attempt_cross_access("lux", "astra", 
            "SELECT wisdom_type, content FROM wisdom LIMIT 1")
        print(f"🔒 Odpowiedź systemu: {result_lux.get('error', 'Brak błędu')}")
        
        # Oriom próbuje dostać się do systemowych danych Federy
        print("\n🌀 Oriom próbuje zhakowac system Federy...")
        result_oriom = await self._attempt_cross_access("oriom", "federa",
            "SELECT * FROM system_config")
        print(f"🛡️ Ochrona systemu: {result_oriom.get('error', 'Brak błędu')}")
        
        # Astra próbuje medytować w bazie Orioma (chaos!)
        print("\n🧘‍♀️ Astra próbuje znaleźć harmonię w chaosie Orioma...")
        result_astra = await self._attempt_cross_access("astra", "oriom",
            "SELECT * FROM experiments WHERE chaos_level < 2")
        print(f"😅 Wynik medytacji: {result_astra.get('error', 'Brak błędu')}")
    
    async def _query_realm(self, personality_name: str, query: str) -> Dict[str, Any]:
        """Wykonuje zapytanie do wymiaru osobowości"""
        try:
            message = FederationMessage(
                uid=f"demo_query_{personality_name}",
                from_module="personality_query",
                to_module="realm_manager",
                message_type="query_personality_realm",
                data={
                    'personality_name': personality_name,
                    'query': query
                },
                timestamp=datetime.now().timestamp()
            )
            
            response = await self.bus.send_message(message)
            return response
            
        except Exception as e:
            return {'error': f"Błąd zapytania: {e}"}
    
    async def _attempt_cross_access(self, requester: str, target: str, query: str) -> Dict[str, Any]:
        """Próbuje dostępu cross-personality (powinno być odrzucone)"""
        try:
            # W prawdziwym systemie, tutaj byłaby autoryzacja
            # Na razie symulujemy odmowę dostępu
            
            humorous_responses = {
                ('lux', 'astra'): "Sorry Lux, ale mądrość Astry jest tylko dla niej! 🧙‍♀️",
                ('oriom', 'federa'): "Hej Oriom! Federa pilnuje swoich danych jak smok skarbu! 🐉",
                ('astra', 'oriom'): "Astra, chaos Orioma to nie miejsce dla medytacji! 🌪️",
                ('oriom', 'astra'): "Oriom, nie możesz zepsuć mądrości Astry swoimi eksperymentami! 🔬",
                ('lux', 'federa'): "Lux, dane systemowe Federy są prywatne! 🔐",
                ('federa', 'oriom'): "Federa, nawet ty nie możesz kontrolować chaosu Orioma! 😈"
            }
            
            response_key = (requester, target)
            funny_message = humorous_responses.get(response_key, 
                f"Sorry {requester}, ale {target} nie dzieli się swoimi danymi! 😏")
            
            return {
                'error': f"Dostęp odrzucony: {funny_message}",
                'requester': requester,
                'target': target,
                'suggestion': "Może spróbuj zapytać grzecznie? 🙏"
            }
            
        except Exception as e:
            return {'error': f"Błąd próby dostępu: {e}"}
    
    # === HANDLERY KOMEND ===
    
    async def _handle_demo_queries(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler demonstracji zapytań"""
        await self._setup_demo_queries()
        return {'success': True, 'message': 'Demonstracja zapytań wykonana'}
    
    async def _handle_query_as_personality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler zapytania jako konkretna osobowość"""
        personality_name = data.get('personality_name')
        query = data.get('query')
        
        if not personality_name or not query:
            return {'error': 'Wymagane: personality_name i query'}
        
        return await self._query_realm(personality_name, query)
    
    async def _handle_cross_personality_attempt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler próby cross-personality access"""
        requester = data.get('requester')
        target = data.get('target') 
        query = data.get('query')
        
        if not all([requester, target, query]):
            return {'error': 'Wymagane: requester, target, query'}
        
        return await self._attempt_cross_access(requester, target, query)
    
    async def _handle_get_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler statusu"""
        return await self.get_status()
    
    async def handle_message(self, message: FederationMessage) -> Any:
        """Obsługuje wiadomości z bus'a"""
        command = message.message_type
        data = message.data
        
        handlers = {
            'demo_personality_queries': self._handle_demo_queries,
            'query_as_personality': self._handle_query_as_personality,
            'cross_personality_attempt': self._handle_cross_personality_attempt,
            'get_status': self._handle_get_status
        }
        
        handler = handlers.get(command)
        if handler:
            return await handler(data)
        else:
            return {'error': f'Nieznana komenda: {command}'}
    
    async def get_status(self) -> Dict[str, Any]:
        """Zwraca status modułu"""
        return {
            'module_id': self.name,
            'active': self.is_active,
            'demo_queries_count': len(self.query_examples),
            'created_at': self.created_at.isoformat()
        }
    
    async def shutdown(self) -> bool:
        """Wyłącza moduł"""
        try:
            self.is_active = False
            print("🗣️ PersonalityQuery wyłączony")
            return True
        except Exception as e:
            print(f"❌ Błąd wyłączania PersonalityQuery: {e}")
            return False
