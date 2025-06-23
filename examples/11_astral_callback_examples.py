
#!/usr/bin/env python3
"""
Przykłady użycia systemu callbacków astralnych w LuxDB
Demonstruje komunikację między bytami astralnymi i komponentami systemu
"""

import time
import asyncio
from datetime import datetime
from luxdb.callback_system import (
    get_astral_callback_manager, 
    CallbackPriority, 
    astral_callback,
    global_astral_callback
)
from luxdb.luxcore import get_luxcore

class AstralBeingSimulator:
    """Symulator bytu astralnego dla testów callbacków"""
    
    def __init__(self, being_name: str, realm: str = "neutral"):
        self.being_name = being_name
        self.realm = realm
        self.energy_level = 50.0
        self.callback_manager = get_astral_callback_manager()
        self.namespace = self.callback_manager.create_namespace(f"being_{being_name}")
        
        self._setup_being_callbacks()
    
    def _setup_being_callbacks(self):
        """Konfiguruje callbacki dla bytu astralnego"""
        
        def on_energy_received(context):
            """Callback dla otrzymanej energii"""
            energy_data = context.data
            received_amount = energy_data.get('amount', 0)
            self.energy_level += received_amount
            
            print(f"🌟 {self.being_name} otrzymał {received_amount} energii. "
                  f"Obecny poziom: {self.energy_level}")
            
            # Odpowiedz gratudą
            self.send_gratitude(energy_data.get('sender'))
        
        def on_communication_received(context):
            """Callback dla otrzymanej komunikacji"""
            comm_data = context.data
            sender = comm_data.get('sender')
            message = comm_data.get('message')
            
            print(f"💬 {self.being_name} otrzymał wiadomość od {sender}: '{message}'")
            
            # Automatyczna odpowiedź
            if "pytanie" in message.lower():
                print(f"💭 {self.being_name} odpowiada na pytanie od {sender}")
                # self.send_communication(sender, f"Odpowiadam na pytanie: {message}")
        
        def on_realm_shift(context):
            """Callback dla zmiany realmu"""
            shift_data = context.data
            new_realm = shift_data.get('new_realm')
            
            if new_realm != self.realm:
                print(f"🌌 {self.being_name} przemieszcza się z {self.realm} do {new_realm}")
                self.realm = new_realm
        
        # Rejestruj callbacki dla tego bytu
        self.namespace.on('energy_transfer', on_energy_received, 
                         priority=CallbackPriority.HIGH)
        self.namespace.on('astral_communication', on_communication_received,
                         priority=CallbackPriority.NORMAL)
        self.namespace.on('realm_shift', on_realm_shift,
                         priority=CallbackPriority.CRITICAL)
    
    def send_energy(self, target_being: str, amount: float):
        """Wysyła energię do innego bytu"""
        if self.energy_level >= amount:
            self.energy_level -= amount
            
            # Emituj zdarzenie transferu energii
            target_namespace = f"being_{target_being}"
            self.callback_manager.emit(
                event_name='energy_transfer',
                data={
                    'sender': self.being_name,
                    'amount': amount,
                    'energy_type': 'astral_light'
                },
                source=f"being_{self.being_name}",
                namespace=target_namespace
            )
            
            print(f"⚡ {self.being_name} wysłał {amount} energii do {target_being}")
        else:
            print(f"❌ {self.being_name} ma zbyt mało energii ({self.energy_level})")
    
    def send_communication(self, target_being: str, message: str):
        """Wysyła komunikację do innego bytu"""
        target_namespace = f"being_{target_being}"
        self.callback_manager.emit(
            event_name='astral_communication',
            data={
                'sender': self.being_name,
                'message': message,
                'frequency': self.get_astral_frequency()
            },
            source=f"being_{self.being_name}",
            namespace=target_namespace
        )
        
        print(f"📡 {self.being_name} wysłał: '{message}' do {target_being}")
    
    def send_gratitude(self, target_being: str):
        """Wysyła gratitudę do innego bytu"""
        self.send_communication(target_being, "Dziękuję za energię! 🙏✨")
    
    def get_astral_frequency(self) -> float:
        """Zwraca częstotliwość astralną bytu"""
        return self.energy_level * 0.1 + 432.0  # Bazowa częstotliwość + energia

# Przykład użycia decoratorów
@astral_callback('universal_event', priority=CallbackPriority.CRITICAL)
def on_universal_event(context):
    """Callback uniwersalny reagujący na ważne wydarzenia"""
    print(f"🌍 WYDARZENIE UNIWERSALNE: {context.event_name}")
    print(f"   Źródło: {context.source}")
    print(f"   Dane: {context.data}")
    print(f"   Czas: {context.timestamp}")

@global_astral_callback(priority=CallbackPriority.LOW)
def global_logger(context):
    """Globalny logger wszystkich zdarzeń astralnych"""
    print(f"📝 LOG: {context.event_name} z {context.source} o {context.timestamp}")

@astral_callback('database_change', namespace='luxcore')
async def async_database_processor(context):
    """Asynchroniczny callback dla zmian w bazie"""
    await asyncio.sleep(0.1)  # Symuluj asynchroniczne przetwarzanie
    db_data = context.data
    print(f"🔄 ASYNC: Przetworzono zmianę w bazie {db_data.get('database')}")

def demonstrate_basic_callbacks():
    """Demonstracja podstawowych callbacków"""
    print("\n" + "="*60)
    print("🧪 DEMONSTRACJA PODSTAWOWYCH CALLBACKÓW")
    print("="*60)
    
    manager = get_astral_callback_manager()
    
    # Prosty callback
    def simple_callback(context):
        print(f"✅ Prosty callback: {context.data}")
    
    # Callback z filtrem
    def filtered_callback(context):
        print(f"🎯 Filtrowany callback: {context.data}")
    
    # Callback "once"
    def once_callback(context):
        print(f"1️⃣ Callback jednorazowy: {context.data}")
    
    # Rejestruj callbacki
    manager.on('test_event', simple_callback)
    manager.on('test_event', filtered_callback, 
               filters={'source': 'filtered_source'})
    manager.on('test_event', once_callback, once=True)
    
    # Testuj emitowanie
    print("\n🔄 Emitowanie zdarzeń testowych...")
    
    # Zdarzenie 1 - wszystkie callbacki
    manager.emit('test_event', {'message': 'Pierwsze zdarzenie'}, 
                source='normal_source')
    
    # Zdarzenie 2 - tylko filtrowany
    manager.emit('test_event', {'message': 'Zdarzenie filtrowane'}, 
                source='filtered_source')
    
    # Zdarzenie 3 - callback "once" już się nie wykona
    manager.emit('test_event', {'message': 'Trzecie zdarzenie'}, 
                source='normal_source')

def demonstrate_astral_beings():
    """Demonstracja komunikacji między bytami astralnymi"""
    print("\n" + "="*60)
    print("🌟 DEMONSTRACJA KOMUNIKACJI BYTÓW ASTRALNYCH")
    print("="*60)
    
    # Utwórz byty astralne
    oriom = AstralBeingSimulator("Oriom", "light_realm")
    shadow_guardian = AstralBeingSimulator("ShadowGuardian", "shadow_realm")
    neutral_observer = AstralBeingSimulator("NeutralObserver", "neutral_realm")
    
    print(f"\n🎭 Utworzono byty astralne:")
    print(f"   • Oriom (Światło) - energia: {oriom.energy_level}")
    print(f"   • ShadowGuardian (Cień) - energia: {shadow_guardian.energy_level}")
    print(f"   • NeutralObserver (Neutralny) - energia: {neutral_observer.energy_level}")
    
    time.sleep(1)

    # Test transferu energii
    print(f"\n⚡ TRANSFER ENERGII:")
    oriom.send_energy("ShadowGuardian", 10.0)
    time.sleep(0.5)

    shadow_guardian.send_energy("NeutralObserver", 15.0)
    time.sleep(0.5)
    
    # Test komunikacji
    print(f"\n💬 KOMUNIKACJA ASTRALNA:")
    # oriom.send_communication("NeutralObserver", "Jak się masz, przyjacielu?")
    time.sleep(0.5)

    neutral_observer.send_communication("Oriom", "Mam pytanie o naturę światła")
    time.sleep(0.5)

    # Test zmiany realmu
    print(f"\n🌌 ZMIANA REALMU:")
    manager = get_astral_callback_manager()
    manager.emit('realm_shift', 
                {'new_realm': 'interdimensional_space'}, 
                source='cosmic_force',
                namespace='being_NeutralObserver')

def demonstrate_websocket_integration():
    """Demonstracja integracji z WebSocket"""
    print("\n" + "="*60)
    print("🔗 DEMONSTRACJA INTEGRACJI WEBSOCKET")
    print("="*60)
    
    # Symuluj zdarzenia WebSocket
    manager = get_astral_callback_manager()
    ws_namespace = manager.create_namespace("luxws")
    
    def websocket_callback(context):
        print(f"🌐 WebSocket event: {context.event_name}")
        print(f"   Session: {context.session_id}")
        print(f"   Data: {context.data}")
    
    # Rejestruj callback dla zdarzeń WebSocket
    ws_namespace.on('client_connected', websocket_callback)
    ws_namespace.on('database_query', websocket_callback)
    
    # Symuluj zdarzenia
    ws_namespace.emit('client_connected', 
                     {'client_type': 'astral_interface'},
                     session_id='astral_session_123')
    
    ws_namespace.emit('database_query',
                     {'query': 'SELECT * FROM astral_beings', 'database': 'main'},
                     session_id='astral_session_123')

def demonstrate_luxcore_integration():
    """Demonstracja integracji z LuxCore"""
    print("\n" + "="*60)
    print("🏛️ DEMONSTRACJA INTEGRACJI LUXCORE")
    print("="*60)
    
    # Pobierz LuxCore i emituj zdarzenia
    luxcore = get_luxcore()
    
    # Symuluj start serwisu
    luxcore.emit_astral_event('service_startup', {
        'service': 'LuxWS',
        'port': 5001,
        'status': 'active'
    })
    
    time.sleep(0.5)
    
    # Symuluj operację na bazie
    luxcore.emit_astral_event('database_operation', {
        'database': 'astral_realm',
        'operation': 'create_table',
        'table': 'energy_readings',
        'broadcast': True
    })

def demonstrate_async_callbacks():
    """Demonstracja asynchronicznych callbacków"""
    print("\n" + "="*60)
    print("🔄 DEMONSTRACJA ASYNCHRONICZNYCH CALLBACKÓW")
    print("="*60)
    
    async def run_async_demo():
        manager = get_astral_callback_manager()
        
        async def async_heavy_processing(context):
            """Symuluje ciężkie przetwarzanie asynchroniczne"""
            print(f"🔄 Rozpoczynam asynchroniczne przetwarzanie: {context.data}")
            await asyncio.sleep(1)  # Symuluj długie przetwarzanie
            print(f"✅ Zakończono asynchroniczne przetwarzanie: {context.data}")
            return f"processed_{context.data}"
        
        def sync_callback(context):
            """Synchroniczny callback"""
            print(f"⚡ Synchroniczny callback: {context.data}")
            return f"sync_processed_{context.data}"
        
        # Rejestruj oba typy callbacków
        manager.on('heavy_task', async_heavy_processing, priority=CallbackPriority.HIGH)
        manager.on('heavy_task', sync_callback, priority=CallbackPriority.NORMAL)
        
        # Emituj zdarzenie
        results = manager.emit('heavy_task', {'task': 'process_astral_data'})
        print(f"📊 Pierwotne wyniki: {len(results)} callbacków wykonano")
        
        # Oczekuj na wyniki asynchroniczne
        final_results = await manager.wait_for_async_results(results)
        print(f"✨ Finalne wyniki po oczekiwaniu na async:")
        for i, result in enumerate(final_results):
            print(f"   {i+1}. {result}")
    
    # Uruchom w event loop
    try:
        asyncio.run(run_async_demo())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            # Jeśli już jest aktywny loop, utwórz task
            loop = asyncio.get_event_loop()
            task = loop.create_task(run_async_demo())
            # Dla demonstracji - nie czekamy na wynik
            print("🔄 Zadanie asynchroniczne zostało uruchomione w tle")
        else:
            print(f"❌ Błąd uruchamiania async demo: {e}")

def demonstrate_priorities():
    """Demonstracja priorytetów callbacków"""
    print("\n" + "="*60)
    print("🎯 DEMONSTRACJA PRIORYTETÓW CALLBACKÓW")
    print("="*60)
    
    manager = get_astral_callback_manager()
    
    def critical_callback(context):
        print("🚨 CRITICAL: Najważniejszy callback")
    
    def high_callback(context):
        print("🔴 HIGH: Wysoki priorytet")
    
    def normal_callback(context):
        print("🟡 NORMAL: Normalny priorytet")
    
    def low_callback(context):
        print("🟢 LOW: Niski priorytet")
    
    def background_callback(context):
        print("🔵 BACKGROUND: W tle")
    
    # Rejestruj w różnej kolejności (ale sortowanie według priorytetu)
    manager.on('priority_test', normal_callback, priority=CallbackPriority.NORMAL)
    manager.on('priority_test', critical_callback, priority=CallbackPriority.CRITICAL)
    manager.on('priority_test', background_callback, priority=CallbackPriority.BACKGROUND)
    manager.on('priority_test', high_callback, priority=CallbackPriority.HIGH)
    manager.on('priority_test', low_callback, priority=CallbackPriority.LOW)
    
    print("\n🔄 Wykonywanie callbacków w kolejności priorytetów:")
    manager.emit('priority_test', {'test': 'priority_order'})

def show_statistics():
    """Pokazuje statystyki systemu callbacków"""
    print("\n" + "="*60)
    print("📊 STATYSTYKI SYSTEMU CALLBACKÓW")
    print("="*60)
    
    manager = get_astral_callback_manager()
    stats = manager.get_stats()
    
    for key, value in stats.items():
        print(f"   {key}: {value}")

def main():
    """Główna funkcja demonstracyjna"""
    print("🌟 SYSTEM CALLBACKÓW ASTRALNYCH LUXDB")
    print("Demonstracja komunikacji między bytami astralnymi")
    
    try:
        # Uruchom wszystkie demonstracje
        # demonstrate_basic_callbacks()
        time.sleep(1)
        
        # demonstrate_astral_beings()
        time.sleep(1)
        
        # demonstrate_websocket_integration()
        # time.sleep(1)
        
        # demonstrate_luxcore_integration()
        # time.sleep(1)
        
        demonstrate_async_callbacks()
        # time.sleep(1)
        
        # demonstrate_priorities()
        # time.sleep(1)
        
        # show_statistics()
        
        print("\n" + "="*60)
        print("✨ DEMONSTRACJA ZAKOŃCZONA POMYŚLNIE")
        print("System callbacków astralnych jest gotowy do użycia!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Błąd podczas demonstracji: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
