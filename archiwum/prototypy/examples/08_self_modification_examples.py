
#!/usr/bin/env python3
"""
🔧 LuxDB v3 Self-Modification Examples

Przykłady jak system może modyfikować sam siebie przez LuxBus
"""

import asyncio
import json
from datetime import datetime

from luxdb_v2.core.luxbus_core import create_luxbus_core, LuxPacket, PacketType
from luxdb_v2.core.astral_engine_v3 import quick_start_v3


async def example_add_custom_method():
    """Przykład dodania własnej metody do AstralEngine"""
    
    print("🔧 Example: Adding custom method to AstralEngine")
    
    # Uruchom system
    engine = await quick_start_v3()
    luxbus = engine.luxbus
    
    # Definicja nowej metody
    modification = {
        "type": "add_method",
        "method_name": "get_cosmic_time",
        "method_code": """
timestamp = datetime.now()
cosmic_factor = len(self.realms) * 42
return {
    'cosmic_time': timestamp.isoformat(),
    'cosmic_factor': cosmic_factor,
    'universe_harmony': cosmic_factor / 42,
    'message': f'Cosmic time calculated at {timestamp}'
}
        """
    }
    
    # Wyślij modyfikację
    packet = LuxPacket(
        uid="modify_example_1",
        from_id="example_client",
        to_id="astral_engine",
        packet_type=PacketType.COMMAND,
        data={
            'command': 'modify_self',
            'params': {'modification': modification}
        }
    )
    
    luxbus.send_packet(packet)
    
    print("✅ Modification sent - new method should be added")
    
    # Poczekaj chwilę na przetworzenie
    await asyncio.sleep(1)
    
    # Sprawdź czy metoda działa
    if hasattr(engine, 'get_cosmic_time'):
        result = engine.get_cosmic_time()
        print(f"🌌 Cosmic time result: {result}")
    else:
        print("❌ Method not added")
    
    await engine.transcend()
    return True


async def example_load_dynamic_module():
    """Przykład dynamicznego ładowania modułu"""
    
    print("📦 Example: Loading dynamic module")
    
    engine = await quick_start_v3()
    luxbus = engine.luxbus
    
    # Załaduj nowy realm
    packet = LuxPacket(
        uid="load_example_1",
        from_id="example_client", 
        to_id="astral_engine",
        packet_type=PacketType.COMMAND,
        data={
            'command': 'load_module',
            'params': {
                'module_name': 'realm_dynamic_test',
                'config': {'connection_string': 'memory://dynamic_test'}
            }
        }
    )
    
    luxbus.send_packet(packet)
    
    print("✅ Module load request sent")
    
    await asyncio.sleep(2)
    
    # Sprawdź status
    status = engine.get_status()
    print(f"📊 Current realms: {status['realms']}")
    
    await engine.transcend()
    return True


async def example_create_self_modifying_module():
    """Przykład stworzenia modułu który może modyfikować inne moduły"""
    
    print("🤖 Example: Self-modifying module")
    
    class SelfModifyingModule:
        def __init__(self, engine):
            self.engine = engine
            self.luxbus = engine.luxbus
            self.module_id = "self_modifier"
            
            # Zarejestruj siebie w LuxBus
            self.luxbus.register_module(self.module_id, self)
            self.setup_handlers()
            
        def setup_handlers(self):
            def handle_command(packet: LuxPacket):
                command_data = packet.data
                command = command_data.get('command')
                
                if command == 'evolve_system':
                    # Moduł może ewoluować cały system
                    self.evolve_system()
                elif command == 'add_intelligence':
                    # Dodaj inteligentną funkcję
                    self.add_intelligence()
                elif command == 'optimize_performance':
                    # Optymalizuj wydajność
                    self.optimize_performance()
            
            self.luxbus.subscribe_to_packets(self.module_id, handle_command)
        
        def evolve_system(self):
            """Ewoluuje system - dodaje nowe możliwości"""
            print("🧬 Evolving system...")
            
            # Dodaj nową metodę do engine
            modification = {
                "type": "add_method",
                "method_name": "evolve",
                "method_code": """
print('🧬 System is evolving...')
# Dodaj nowe realm
if 'evolution' not in self.realms:
    asyncio.create_task(self.load_realm_module('evolution', 'memory://evolution'))
return {'status': 'evolved', 'new_capabilities': ['evolution_tracking']}
                """
            }
            
            self.engine.apply_self_modification(modification)
            print("✅ System evolved!")
        
        def add_intelligence(self):
            """Dodaje inteligentne zachowania"""
            print("🧠 Adding intelligence...")
            
            # Modyfikuj consciousness
            if self.engine.consciousness:
                # Dodaj nowy typ obserwacji
                original_observe = self.engine.consciousness.observe
                
                def enhanced_observe(event):
                    # Rozszerzony observe z AI
                    result = original_observe(event)
                    if event.get('type') == 'critical':
                        print(f"🚨 AI detected critical event: {event}")
                    return result
                
                self.engine.consciousness.observe = enhanced_observe
                print("✅ Intelligence added!")
        
        def optimize_performance(self):
            """Optymalizuje wydajność systemu"""
            print("⚡ Optimizing performance...")
            
            # Sprawdź obciążenie i zoptymalizuj
            status = self.engine.get_status()
            luxbus_stats = self.luxbus.get_status()
            
            if luxbus_stats['dispatcher_stats']['packets_processed'] > 1000:
                print("📦 High packet volume detected - optimizing dispatcher")
                # Tu można dodać optymalizacje
            
            print("✅ Performance optimized!")
        
        def get_info(self):
            return {
                'type': 'SelfModifyingModule',
                'capabilities': ['system_evolution', 'intelligence_enhancement', 'performance_optimization'],
                'status': 'active'
            }
    
    # Uruchom system z self-modifying module
    engine = await quick_start_v3()
    
    # Dodaj self-modifying module
    modifier = SelfModifyingModule(engine)
    
    print("🤖 Self-modifying module loaded")
    
    # Przetestuj evolucję
    packet = LuxPacket(
        uid="evolve_test",
        from_id="test_client",
        to_id="self_modifier", 
        packet_type=PacketType.COMMAND,
        data={'command': 'evolve_system'}
    )
    
    engine.luxbus.send_packet(packet)
    
    await asyncio.sleep(2)
    
    # Przetestuj dodanie inteligencji
    packet = LuxPacket(
        uid="intelligence_test",
        from_id="test_client",
        to_id="self_modifier",
        packet_type=PacketType.COMMAND, 
        data={'command': 'add_intelligence'}
    )
    
    engine.luxbus.send_packet(packet)
    
    await asyncio.sleep(1)
    
    # Sprawdź czy nowa metoda działa
    if hasattr(engine, 'evolve'):
        result = engine.evolve()
        print(f"🧬 Evolution result: {result}")
    
    await engine.transcend()
    return True


async def example_terminal_chat_simulation():
    """Symuluje komendy z terminal chat"""
    
    print("💬 Example: Terminal chat simulation")
    
    engine = await quick_start_v3()
    luxbus = engine.luxbus
    
    # Symuluj komendy terminal chat
    commands = [
        {
            'command': 'get_status',
            'description': 'Get system status'
        },
        {
            'command': 'meditate', 
            'description': 'Trigger meditation'
        },
        {
            'command': 'load_module',
            'params': {
                'module_name': 'realm_chat_test',
                'config': {'connection_string': 'memory://chat_test'}
            },
            'description': 'Load new module'
        },
        {
            'command': 'modify_self',
            'params': {
                'modification': {
                    'type': 'add_method',
                    'method_name': 'greet_user',
                    'method_code': "return f'Hello from LuxDB v3! Time: {datetime.now()}'"
                }
            },
            'description': 'Add greeting method'
        }
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n💬 Command {i}: {cmd['description']}")
        
        packet = LuxPacket(
            uid=f"chat_cmd_{i}",
            from_id="chat_simulation",
            to_id="astral_engine",
            packet_type=PacketType.COMMAND,
            data={
                'command': cmd['command'],
                'params': cmd.get('params', {})
            }
        )
        
        luxbus.send_packet(packet)
        await asyncio.sleep(1)
    
    # Test nowej metody
    await asyncio.sleep(2)
    if hasattr(engine, 'greet_user'):
        greeting = engine.greet_user()
        print(f"👋 Greeting: {greeting}")
    
    await engine.transcend()
    return True


async def main():
    """Uruchom wszystkie przykłady"""
    
    examples = [
        ("Adding custom method", example_add_custom_method),
        ("Loading dynamic module", example_load_dynamic_module), 
        ("Self-modifying module", example_create_self_modifying_module),
        ("Terminal chat simulation", example_terminal_chat_simulation)
    ]
    
    print("🔧 LuxDB v3 Self-Modification Examples")
    print("=" * 50)
    
    for name, example_func in examples:
        print(f"\n📋 Running: {name}")
        print("-" * 30)
        
        try:
            success = await example_func()
            if success:
                print(f"✅ {name} completed successfully")
            else:
                print(f"⚠️ {name} completed with warnings")
        except Exception as e:
            print(f"❌ {name} failed: {e}")
        
        print(f"⏱️ Waiting before next example...")
        await asyncio.sleep(2)
    
    print("\n🎉 All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
