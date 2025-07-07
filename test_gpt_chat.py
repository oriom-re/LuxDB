
#!/usr/bin/env python3
"""
🤖 Test GPT Flow - Komunikacja z Astrą przez LuxBus
"""

import asyncio
import uuid
from luxdb_v2.core.luxbus_core import get_luxbus_core, LuxPacket, PacketType

class LuxBusGPTTest:
    """Test komunikacji z GPT Flow przez LuxBus"""
    
    def __init__(self):
        self.luxbus = get_luxbus_core()
        self.test_id = f"gpt_test_{uuid.uuid4().hex[:8]}"
        self.responses = {}
        
        # Zarejestruj się jako moduł do odbierania odpowiedzi
        self.luxbus.register_module(self.test_id, self)
        self.setup_response_handler()
    
    def setup_response_handler(self):
        """Konfiguruje handler odpowiedzi"""
        def handle_gpt_response(packet: LuxPacket):
            """Obsługuje odpowiedzi z GPT Flow"""
            if packet.packet_type == PacketType.RESPONSE:
                # Zapisz odpowiedź
                self.responses[packet.uid] = packet.data
                print(f"✨ Astra odpowiada: {packet.data.get('astra_response', 'Brak odpowiedzi')[:200]}...")
                if packet.data.get('actions_executed', 0) > 0:
                    print(f"🎯 Wykonano {packet.data['actions_executed']} akcji astralnych")
        
        # Subskrybuj odpowiedzi skierowane do nas
        self.luxbus.subscribe_to_packets(self.test_id, handle_gpt_response)
    
    async def send_gpt_message(self, message: str, wait_for_response: bool = True):
        """Wysyła wiadomość do GPT Flow przez LuxBus"""
        packet_id = f"gpt_msg_{uuid.uuid4().hex[:8]}"
        
        # Stwórz pakiet z komendą chat
        packet = LuxPacket(
            uid=packet_id,
            from_id=self.test_id,
            to_id="flow_gpt",  # ID GPT Flow w systemie
            packet_type=PacketType.COMMAND,
            data={
                'command': 'chat',
                'params': {
                    'message': message,
                    'user_id': 'luxbus_test_user'
                }
            }
        )
        
        # Wyślij przez LuxBus
        success = self.luxbus.send_packet(packet)
        
        if wait_for_response:
            # Czekaj na odpowiedź (max 10 sekund)
            for i in range(50):  # 50 * 0.2s = 10s
                if packet_id in self.responses:
                    return self.responses[packet_id]
                await asyncio.sleep(0.2)
            
            print(f"❌ Timeout - brak odpowiedzi na pakiet {packet_id}")
            return None
        
        return success

async def test_luxbus_gpt_communication():
    """Testuje komunikację z Astrą przez LuxBus"""
    
    print("🚌 Testowanie komunikacji z Astrą przez LuxBus...")
    print("=" * 60)
    
    # Stwórz tester
    tester = LuxBusGPTTest()
    
    test_messages = [
        "Witaj Astro! Jak się dzisiaj czujesz?",
        "Pokaż mi status wszystkich wymiarów astralnych",
        "Stwórz nowego bytu o nazwie 'TestoweBłękitneŚwiatło'",
        "Znajdź wszystkie intencje związane z harmonią",
        "Wykonaj medytację systemu i powiedz mi co odkryłaś"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n💬 Test {i}: {message}")
        
        # Wyślij przez LuxBus
        response = await tester.send_gpt_message(message)
        
        if response is None:
            print("❌ Brak odpowiedzi z GPT Flow")
        
        # Krótka przerwa między testami
        await asyncio.sleep(1)
    
    print(f"\n🚌 Test LuxBus zakończony. Wysłano {len(test_messages)} wiadomości.")
    print("💡 Zaawansowane funkcje dostępne przez WebSocket i LuxBus!")
    print("🌐 REST API uproszczone do podstawowych zapytań o stan")

if __name__ == "__main__":
    asyncio.run(test_luxbus_gpt_communication())
