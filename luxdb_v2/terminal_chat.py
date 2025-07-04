"""
💬 LuxDB v2 Terminal Chat Interface

Interfejs terminalowy do komunikacji z systemem LuxDB przez LuxBus.
Umożliwia sterowanie systemem, modyfikację i debugging.
"""

import asyncio
import json
import uuid
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Import LuxBus
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.luxbus_core import LuxBusCore, LuxPacket, PacketType


class LuxTerminalChat:
    """
    Terminal chat dla systemu LuxDB
    Komunikuje się z AstralEngine przez LuxBus
    """

    def __init__(self):
        self.luxbus = LuxBusCore("terminal_chat")
        self.chat_id = f"chat_{uuid.uuid4().hex[:8]}"
        self.running = False
        self.command_history: List[str] = []

        # Response handlers
        self.pending_responses: Dict[str, asyncio.Future] = {}

        self.setup_handlers()

        print("💬 LuxDB Terminal Chat initialized")
        print(f"🆔 Chat ID: {self.chat_id}")

    def setup_handlers(self):
        """Konfiguruje handlery odpowiedzi"""

        def handle_response(packet: LuxPacket):
            """Obsługuje odpowiedzi z systemu"""
            # Sprawdź czy to odpowiedź na nasze żądanie
            original_uid = packet.uid.replace("engine_response_", "").replace("status_response_", "").replace("modules_response_", "")

            if original_uid in self.pending_responses:
                future = self.pending_responses[original_uid]
                if not future.done():
                    future.set_result(packet.data)
                del self.pending_responses[original_uid]
            else:
                # Wyświetl odpowiedź
                self.display_response(packet)

        def handle_event(packet: LuxPacket):
            """Obsługuje eventy z systemu"""
            event_data = packet.data
            event_type = event_data.get('event_type')
            data = event_data.get('data')

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n🔔 [{timestamp}] Event: {event_type}")

            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"   {key}: {value}")
            else:
                print(f"   Data: {data}")

            print("💬 ", end="", flush=True)  # Przywróć prompt

        # Subskrybuj odpowiedzi i eventy
        self.luxbus.subscribe_to_packets(self.chat_id, handle_response)
        self.luxbus.subscribe_to_packets("broadcast", handle_event)

    def display_response(self, packet: LuxPacket):
        """Wyświetla odpowiedź z systemu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n📨 [{timestamp}] Response from {packet.from_id}:")

        if isinstance(packet.data, dict):
            self.display_dict(packet.data, indent=1)
        else:
            print(f"   {packet.data}")

    def display_dict(self, data: Dict[str, Any], indent: int = 0):
        """Wyświetla słownik w czytelny sposób"""
        prefix = "   " * indent

        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{prefix}{key}:")
                self.display_dict(value, indent + 1)
            elif isinstance(value, list):
                print(f"{prefix}{key}: [{len(value)} items]")
                for i, item in enumerate(value[:3]):  # Pokaż tylko pierwsze 3
                    print(f"{prefix}  [{i}]: {item}")
                if len(value) > 3:
                    print(f"{prefix}  ... and {len(value) - 3} more")
            else:
                print(f"{prefix}{key}: {value}")

    async def send_command_and_wait(self, target: str, command: str, params: Any = None, timeout: float = 5.0) -> Any:
        """Wysyła komendę i czeka na odpowiedź"""
        packet_id = f"cmd_{uuid.uuid4().hex[:8]}"

        # Przygotuj future dla odpowiedzi
        future = asyncio.Future()
        self.pending_responses[packet_id] = future

        # Wyślij komendę
        packet = LuxPacket(
            uid=packet_id,
            from_id=self.chat_id,
            to_id=target,
            packet_type=PacketType.COMMAND,
            data={'command': command, 'params': params}
        )

        self.luxbus.send_packet(packet)

        try:
            # Czekaj na odpowiedź
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            if packet_id in self.pending_responses:
                del self.pending_responses[packet_id]
            return {'error': 'Timeout waiting for response'}

    async def process_command(self, command: str):
        """Przetwarza komendę użytkownika"""
        command = command.strip()

        if not command:
            return

        # Dodaj do historii
        self.command_history.append(command)

        # Parsuj komendę
        parts = command.split()
        cmd = parts[0].lower()

        try:
            if cmd in ['help', 'h']:
                self.show_help()

            elif cmd in ['status', 's']:
                target = parts[1] if len(parts) > 1 else 'system'
                response = await self.send_command_and_wait(target, 'get_status')
                print("\n📊 Status:")
                self.display_dict(response)

            elif cmd in ['awaken', 'wake']:
                response = await self.send_command_and_wait('astral_engine', 'awaken')
                print(f"\n🌅 Awaken result: {response}")

            elif cmd in ['transcend', 'stop']:
                response = await self.send_command_and_wait('astral_engine', 'transcend')
                print(f"\n🕊️ Transcend result: {response}")

            elif cmd in ['meditate', 'm']:
                response = await self.send_command_and_wait('astral_engine', 'meditate')
                print("\n🧘 Meditation result:")
                self.display_dict(response)

            elif cmd in ['modules', 'mod']:
                response = await self.send_command_and_wait('modules', 'get_modules')
                print("\n📦 Modules:")
                self.display_dict(response)

            elif cmd in ['load']:
                if len(parts) < 2:
                    print("❌ Usage: load <module_name> [config_json]")
                    return

                module_name = parts[1]
                config = {}

                if len(parts) > 2:
                    try:
                        config = json.loads(' '.join(parts[2:]))
                    except json.JSONDecodeError:
                        print("❌ Invalid JSON config")
                        return

                response = await self.send_command_and_wait('astral_engine', 'load_module', {
                    'module_name': module_name,
                    'config': config
                })
                print(f"\n📦 Load result: {response}")

            elif cmd in ['modify', 'mod']:
                if len(parts) < 2:
                    print("❌ Usage: modify <modification_json>")
                    return

                try:
                    modification = json.loads(' '.join(parts[1:]))
                except json.JSONDecodeError:
                    print("❌ Invalid JSON modification")
                    return

                response = await self.send_command_and_wait('astral_engine', 'modify_self', {
                    'modification': modification
                })
                print(f"\n🔧 Modification result: {response}")

            elif cmd in ['send']:
                if len(parts) < 4:
                    print("❌ Usage: send <target> <command> <params_json>")
                    return

                target = parts[1]
                command = parts[2]

                try:
                    params = json.loads(' '.join(parts[3:]))
                except json.JSONDecodeError:
                    print("❌ Invalid JSON params")
                    return

                response = await self.send_command_and_wait(target, command, params)
                print(f"\n📤 Send result: {response}")

            elif cmd in ['history', 'hist']:
                print("\n📚 Command History:")
                for i, hist_cmd in enumerate(self.command_history[-10:], 1):
                    print(f"   {i}. {hist_cmd}")

            elif cmd in ['clear', 'cls']:
                os.system('clear' if os.name == 'posix' else 'cls')

            elif cmd in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                self.running = False

            else:
                print(f"❌ Unknown command: {cmd}")
                print("💡 Type 'help' for available commands")

        except Exception as e:
            print(f"❌ Error processing command: {e}")

    def show_help(self):
        """Wyświetla pomoc"""
        print("""
💬 LuxDB Terminal Chat - Available Commands:

📊 System Commands:
   status [target]     - Show system/module status
   awaken              - Awaken the AstralEngine
   transcend           - Gracefully stop the engine
   meditate            - Trigger system meditation

📦 Module Commands:
   modules             - List all modules
   load <name> [cfg]   - Load dynamic module
   send <tgt> <cmd> <params> - Send command to module

🔧 Self-Modification:
   modify <json>       - Apply self-modification

📚 Utility:
   history             - Show command history
   clear               - Clear screen
   help                - Show this help
   exit                - Exit chat

💡 Examples:
   status astral_engine
   load realm_test {"connection_string": "memory://"}
   modify {"type": "add_method", "method_name": "test", "method_code": "return 'hello'"}
   send consciousness reflect {}
        """)

    async def run(self):
        """Główna pętla chatu"""
        self.running = True
        self.luxbus.start()

        print("💬 LuxDB Terminal Chat started!")
        print("💡 Type 'help' for available commands")
        print("🔌 Connecting to LuxBus...")

        # Spróbuj połączyć się z systemem
        try:
            status = await self.send_command_and_wait('system', 'get_status', timeout=2.0)
            print(f"✅ Connected to LuxBus - Node: {status.get('node_id', 'unknown')}")
        except:
            print("⚠️ No existing system found - you can start one with 'awaken'")

        # Główna pętla
        while self.running:
            try:
                command = input("\n💬 ")

                if command.strip():
                    await self.process_command(command)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        # Cleanup
        self.luxbus.stop()


async def main():
    """Główna funkcja"""
    chat = LuxTerminalChat()
    await chat.run()


if __name__ == "__main__":
    # Jeśli uruchamiany bezpośrednio, dostosuj importy
    if __package__ is None:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))

        # Re-import z poprawionymi ścieżkami
        try:
            from luxdb_v2.core.astral_engine_v3 import AstralEngineV3, create_astral_engine_v3
            from luxdb_v2.core.luxbus_core import create_luxbus_core
            LUXDB_V3_AVAILABLE = True
        except ImportError as e:
            print(f"⚠️ LuxDB v3 nie jest dostępne: {e}")
            LUXDB_V3_AVAILABLE = False

        try:
            from luxdb_v2.core.astral_engine import AstralEngine
            from luxdb_v2 import Astral
            LUXDB_V2_AVAILABLE = True
        except ImportError as e:
            print(f"⚠️ LuxDB v2 nie jest dostępne: {e}")
            LUXDB_V2_AVAILABLE = False

    asyncio.run(main())