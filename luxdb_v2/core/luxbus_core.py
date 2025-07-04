
"""
🚌 LuxBus Core - Centralny System Komunikacji

Uniwersalny system komunikacji oparty o pakiety, obsługujący:
- Lokalne komunikacje między modułami
- WebSocket komunikację z klientami  
- Rozproszoną komunikację między bytami
- Self-modification capabilities
"""

import asyncio
import json
import uuid
import time
import threading
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import queue


class PacketType(Enum):
    COMMAND = "command"
    EVENT = "event"
    STREAM = "stream"
    RESPONSE = "response"
    ACK = "ack"


class PacketStatus(Enum):
    PENDING = "pending"
    ACK = "ack"
    MISSING = "missing"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class LuxPacket:
    """Podstawowy pakiet komunikacyjny LuxBus"""
    uid: str
    from_id: str
    to_id: str
    packet_type: PacketType
    data: Any
    timestamp: float = None
    chunk: int = 0
    of: int = 1
    is_final: bool = True
    status: PacketStatus = PacketStatus.PENDING
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje pakiet do słownika"""
        return {
            'uid': self.uid,
            'from': self.from_id,
            'to': self.to_id,
            'type': self.packet_type.value,
            'data': self.data,
            'timestamp': self.timestamp,
            'chunk': self.chunk,
            'of': self.of,
            'is_final': self.is_final,
            'status': self.status.value,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LuxPacket':
        """Tworzy pakiet ze słownika"""
        return cls(
            uid=data['uid'],
            from_id=data['from'],
            to_id=data['to'],
            packet_type=PacketType(data['type']),
            data=data['data'],
            timestamp=data.get('timestamp'),
            chunk=data.get('chunk', 0),
            of=data.get('of', 1),
            is_final=data.get('is_final', True),
            status=PacketStatus(data.get('status', 'pending')),
            metadata=data.get('metadata', {})
        )


class LuxStreamManager:
    """Zarządca strumieni danych - obsługuje chunki i rekonstrukcję"""
    
    def __init__(self):
        self.streams: Dict[str, Dict[int, LuxPacket]] = {}
        self.stream_metadata: Dict[str, Dict[str, Any]] = {}
        
    def add_chunk(self, packet: LuxPacket) -> Optional[Any]:
        """
        Dodaje chunk do strumienia. Zwraca kompletne dane jeśli strumień jest ukończony.
        """
        stream_id = packet.uid
        
        if stream_id not in self.streams:
            self.streams[stream_id] = {}
            self.stream_metadata[stream_id] = {
                'expected_chunks': packet.of,
                'received_chunks': 0,
                'started_at': time.time()
            }
        
        # Dodaj chunk
        self.streams[stream_id][packet.chunk] = packet
        self.stream_metadata[stream_id]['received_chunks'] += 1
        
        # Sprawdź czy strumień jest kompletny
        if self.stream_metadata[stream_id]['received_chunks'] == packet.of:
            return self._reconstruct_stream(stream_id)
        
        return None
    
    def _reconstruct_stream(self, stream_id: str) -> Any:
        """Rekonstruuje kompletne dane ze strumienia"""
        chunks = self.streams[stream_id]
        sorted_chunks = sorted(chunks.items(), key=lambda x: x[0])
        
        # Złącz dane z wszystkich chunków
        if len(sorted_chunks) == 1:
            reconstructed_data = sorted_chunks[0][1].data
        else:
            # Dla wielu chunków - złącz stringi lub listy
            first_chunk_data = sorted_chunks[0][1].data
            if isinstance(first_chunk_data, str):
                reconstructed_data = ''.join(chunk.data for _, chunk in sorted_chunks)
            elif isinstance(first_chunk_data, list):
                reconstructed_data = []
                for _, chunk in sorted_chunks:
                    reconstructed_data.extend(chunk.data)
            else:
                reconstructed_data = [chunk.data for _, chunk in sorted_chunks]
        
        # Wyczyść strumień z pamięci
        del self.streams[stream_id]
        del self.stream_metadata[stream_id]
        
        return reconstructed_data
    
    def get_missing_chunks(self, stream_id: str) -> List[int]:
        """Zwraca listę brakujących chunków"""
        if stream_id not in self.streams:
            return []
        
        expected = self.stream_metadata[stream_id]['expected_chunks']
        received = set(self.streams[stream_id].keys())
        all_chunks = set(range(expected))
        
        return list(all_chunks - received)


class LuxDispatcher:
    """Centralny dispatcher - przekazuje pakiety do odpowiednich odbiorców"""
    
    def __init__(self):
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.packet_buffer: Dict[str, List[LuxPacket]] = {}
        self.stream_manager = LuxStreamManager()
        self.running = False
        self.stats = {
            'packets_processed': 0,
            'packets_buffered': 0,
            'streams_completed': 0
        }
    
    def subscribe(self, recipient_id: str, callback: Callable[[LuxPacket], None]):
        """Subskrybuje callback dla konkretnego odbiorcy"""
        if recipient_id not in self.subscribers:
            self.subscribers[recipient_id] = set()
        self.subscribers[recipient_id].add(callback)
    
    def unsubscribe(self, recipient_id: str, callback: Callable):
        """Usuwa subskrypcję"""
        if recipient_id in self.subscribers:
            self.subscribers[recipient_id].discard(callback)
    
    def dispatch(self, packet: LuxPacket) -> bool:
        """
        Główna funkcja dispatchingu pakietów
        """
        self.stats['packets_processed'] += 1
        
        # Jeśli to pakiet streamowy
        if packet.of > 1:
            reconstructed_data = self.stream_manager.add_chunk(packet)
            if reconstructed_data is not None:
                # Strumień kompletny - utwórz nowy pakiet z kompletnymi danymi
                complete_packet = LuxPacket(
                    uid=packet.uid,
                    from_id=packet.from_id,
                    to_id=packet.to_id,
                    packet_type=packet.packet_type,
                    data=reconstructed_data,
                    status=PacketStatus.COMPLETE
                )
                self.stats['streams_completed'] += 1
                return self._deliver_packet(complete_packet)
            else:
                # Strumień niekompletny - wyślij ACK
                ack_packet = LuxPacket(
                    uid=f"ack_{packet.uid}_{packet.chunk}",
                    from_id="dispatcher",
                    to_id=packet.from_id,
                    packet_type=PacketType.ACK,
                    data={'ack_chunk': packet.chunk, 'stream_id': packet.uid}
                )
                return self._deliver_packet(ack_packet)
        else:
            # Pojedynczy pakiet
            return self._deliver_packet(packet)
    
    def _deliver_packet(self, packet: LuxPacket) -> bool:
        """Dostarcza pakiet do subskrybentów"""
        if packet.to_id in self.subscribers:
            # Dostarczenie do konkretnych subskrybentów
            for callback in self.subscribers[packet.to_id]:
                try:
                    callback(packet)
                except Exception as e:
                    print(f"❌ Błąd w callback dla {packet.to_id}: {e}")
            return True
        else:
            # Brak odbiorcy - buforuj pakiet
            if packet.to_id not in self.packet_buffer:
                self.packet_buffer[packet.to_id] = []
            self.packet_buffer[packet.to_id].append(packet)
            self.stats['packets_buffered'] += 1
            return False
    
    def flush_buffer(self, recipient_id: str):
        """Próbuje dostarczyć zbuforowane pakiety gdy pojawi się odbiorca"""
        if recipient_id in self.packet_buffer:
            buffered_packets = self.packet_buffer[recipient_id]
            delivered = 0
            
            for packet in buffered_packets:
                if self._deliver_packet(packet):
                    delivered += 1
            
            # Usuń dostarczone pakiety
            if delivered > 0:
                self.packet_buffer[recipient_id] = self.packet_buffer[recipient_id][delivered:]
                if not self.packet_buffer[recipient_id]:
                    del self.packet_buffer[recipient_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki dispatchera"""
        return {
            **self.stats,
            'active_subscribers': len(self.subscribers),
            'buffered_recipients': len(self.packet_buffer),
            'active_streams': len(self.stream_manager.streams)
        }


class LuxBusCore:
    """
    Główny system LuxBus - centralny hub komunikacji
    """
    
    def __init__(self, node_id: str = None):
        self.node_id = node_id or f"luxnode_{uuid.uuid4().hex[:8]}"
        self.dispatcher = LuxDispatcher()
        self.modules: Dict[str, Any] = {}
        self.running = False
        
        # Kolejki komunikacji
        self.incoming_queue = asyncio.Queue()
        self.outgoing_queue = asyncio.Queue()
        
        # WebSocket klienci
        self.ws_clients: Set[Any] = set()
        
        # Handlery specjalne
        self.command_handlers: Dict[str, Callable] = {}
        
        self._setup_core_handlers()
        
        print(f"🚌 LuxBus Core zainicjalizowany: {self.node_id}")
    
    def _setup_core_handlers(self):
        """Konfiguruje podstawowe handlery systemowe"""
        
        def handle_system_status(packet: LuxPacket):
            """Handler statusu systemu"""
            status = {
                'node_id': self.node_id,
                'uptime': time.time(),
                'modules': list(self.modules.keys()),
                'dispatcher_stats': self.dispatcher.get_stats(),
                'queue_sizes': {
                    'incoming': self.incoming_queue.qsize(),
                    'outgoing': self.outgoing_queue.qsize()
                }
            }
            
            response = LuxPacket(
                uid=f"status_response_{uuid.uuid4().hex[:8]}",
                from_id=self.node_id,
                to_id=packet.from_id,
                packet_type=PacketType.RESPONSE,
                data=status
            )
            
            self.send_packet(response)
        
        def handle_module_list(packet: LuxPacket):
            """Handler listy modułów"""
            modules_info = {}
            for name, module in self.modules.items():
                if hasattr(module, 'get_info'):
                    modules_info[name] = module.get_info()
                else:
                    modules_info[name] = {'type': type(module).__name__}
            
            response = LuxPacket(
                uid=f"modules_response_{uuid.uuid4().hex[:8]}",
                from_id=self.node_id,
                to_id=packet.from_id,
                packet_type=PacketType.RESPONSE,
                data=modules_info
            )
            
            self.send_packet(response)
        
        # Rejestracja handlerów
        self.dispatcher.subscribe("system", handle_system_status)
        self.dispatcher.subscribe("modules", handle_module_list)
    
    def register_module(self, name: str, module: Any):
        """Rejestruje moduł w systemie"""
        self.modules[name] = module
        
        # Jeśli moduł ma metodę setup_luxbus_handlers, wywołaj ją
        if hasattr(module, 'setup_luxbus_handlers'):
            module.setup_luxbus_handlers(self)
        
        print(f"📦 Moduł zarejestrowany: {name}")
    
    def send_packet(self, packet: LuxPacket):
        """Wysyła pakiet przez dispatcher"""
        return self.dispatcher.dispatch(packet)
    
    def send_command(self, to_id: str, command: str, data: Any = None) -> str:
        """Wysyła komendę do modułu"""
        packet_id = f"cmd_{uuid.uuid4().hex[:8]}"
        
        packet = LuxPacket(
            uid=packet_id,
            from_id=self.node_id,
            to_id=to_id,
            packet_type=PacketType.COMMAND,
            data={'command': command, 'params': data}
        )
        
        self.send_packet(packet)
        return packet_id
    
    def send_event(self, event_type: str, data: Any, to_id: str = "broadcast"):
        """Wysyła event do systemu"""
        packet = LuxPacket(
            uid=f"event_{uuid.uuid4().hex[:8]}",
            from_id=self.node_id,
            to_id=to_id,
            packet_type=PacketType.EVENT,
            data={'event_type': event_type, 'data': data}
        )
        
        if to_id == "broadcast":
            # Broadcast do wszystkich modułów
            for module_name in self.modules.keys():
                packet.to_id = module_name
                self.send_packet(packet)
        else:
            self.send_packet(packet)
    
    def subscribe_to_packets(self, recipient_id: str, callback: Callable[[LuxPacket], None]):
        """Subskrybuje callback do odbierania pakietów"""
        self.dispatcher.subscribe(recipient_id, callback)
        
        # Spróbuj dostarczyć zbuforowane pakiety
        self.dispatcher.flush_buffer(recipient_id)
    
    async def process_incoming_packets(self):
        """Przetwarza pakiety przychodzące (głównie z WebSocket)"""
        while self.running:
            try:
                packet_data = await asyncio.wait_for(self.incoming_queue.get(), timeout=1.0)
                packet = LuxPacket.from_dict(packet_data)
                self.send_packet(packet)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ Błąd przetwarzania pakietu: {e}")
    
    async def process_outgoing_packets(self):
        """Przetwarza pakiety wychodzące (do WebSocket klientów)"""
        while self.running:
            try:
                packet = await asyncio.wait_for(self.outgoing_queue.get(), timeout=1.0)
                
                # Wyślij do wszystkich połączonych klientów WebSocket
                if self.ws_clients:
                    packet_json = json.dumps(packet.to_dict())
                    disconnected = set()
                    
                    for client in self.ws_clients:
                        try:
                            await client.send(packet_json)
                        except Exception as e:
                            print(f"⚠️ Klient WebSocket odłączony: {e}")
                            disconnected.add(client)
                    
                    # Usuń odłączone klienty
                    self.ws_clients -= disconnected
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ Błąd wysyłania pakietu: {e}")
    
    def add_ws_client(self, client):
        """Dodaje klienta WebSocket"""
        self.ws_clients.add(client)
        print(f"🔌 Nowy klient WebSocket połączony")
    
    def remove_ws_client(self, client):
        """Usuwa klienta WebSocket"""
        self.ws_clients.discard(client)
        print(f"🔌 Klient WebSocket odłączony")
    
    async def handle_ws_message(self, message: str):
        """Obsługuje wiadomość z WebSocket"""
        try:
            packet_data = json.loads(message)
            await self.incoming_queue.put(packet_data)
        except json.JSONDecodeError as e:
            print(f"❌ Błąd parsowania JSON: {e}")
        except Exception as e:
            print(f"❌ Błąd obsługi wiadomości WS: {e}")
    
    def start(self):
        """Uruchamia LuxBus Core"""
        self.running = True
        print(f"🚌 LuxBus Core uruchomiony: {self.node_id}")
    
    def stop(self):
        """Zatrzymuje LuxBus Core"""
        self.running = False
        print(f"🚌 LuxBus Core zatrzymany: {self.node_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status LuxBus Core"""
        return {
            'node_id': self.node_id,
            'running': self.running,
            'modules': list(self.modules.keys()),
            'ws_clients': len(self.ws_clients),
            'dispatcher_stats': self.dispatcher.get_stats()
        }


# Globalna instancja
_luxbus_core = None

def get_luxbus_core() -> LuxBusCore:
    """Pobiera globalną instancję LuxBus Core"""
    global _luxbus_core
    if _luxbus_core is None:
        _luxbus_core = LuxBusCore()
    return _luxbus_core

def create_luxbus_core(node_id: str = None) -> LuxBusCore:
    """Tworzy nową instancję LuxBus Core"""
    global _luxbus_core
    _luxbus_core = LuxBusCore(node_id)
    return _luxbus_core
