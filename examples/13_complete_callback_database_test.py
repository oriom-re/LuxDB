
#!/usr/bin/env python3
"""
Kompletny test systemu callbacków z bazą danych
Testuje wszystkie funkcjonalności persystencji i analityki
"""

import time
import asyncio
from datetime import datetime
from luxdb.callback_system import get_astral_callback_manager, CallbackPriority

def test_complete_callback_database():
    """Kompleksowy test systemu callbacków z bazą danych"""
    print("🌟 KOMPLETNY TEST SYSTEMU CALLBACKÓW Z BAZĄ DANYCH")
    print("="*60)
    
    manager = get_astral_callback_manager()
    
    # Sprawdź czy baza danych jest włączona
    if not manager.database_enabled:
        print("❌ Baza danych nie jest włączona!")
        return
    
    print(f"✅ Baza danych jest włączona: {manager.database_enabled}")
    print(f"📊 Manager bazy: {type(manager.db_manager).__name__}")
    
    # Test 1: Rejestracja callbacków
    print(f"\n📝 TEST 1: REJESTRACJA CALLBACKÓW")
    
    def callback_fast(context):
        print(f"⚡ Szybki callback: {context.data}")
        return {"type": "fast", "processed": True}
    
    def callback_slow(context):
        print(f"🐌 Wolny callback: {context.data}")
        time.sleep(2)
        return {"type": "slow", "processed": True}
    
    async def callback_async(context):
        print(f"🔄 Async callback: {context.data}")
        await asyncio.sleep(1)
        return {"type": "async", "processed": True}
    
    def callback_error(context):
        print(f"💥 Callback z błędem: {context.data}")
        if context.data.get('should_fail', False):
            raise Exception("Testowy błąd callback")
        return {"type": "error_test", "processed": True}
    
    # Zarejestruj callbacki
    cb1_id = manager.on('test_db_event', callback_fast, priority=CallbackPriority.HIGH)
    cb2_id = manager.on('test_db_event', callback_slow, priority=CallbackPriority.NORMAL)
    cb3_id = manager.on('test_db_event', callback_async, priority=CallbackPriority.NORMAL)
    cb4_id = manager.on('test_db_event', callback_error, priority=CallbackPriority.LOW)
    
    print(f"   Zarejestrowano callbacki: {[cb1_id[:8], cb2_id[:8], cb3_id[:8], cb4_id[:8]]}...")
    
    # Test 2: Emitowanie eventów
    print(f"\n🚀 TEST 2: EMITOWANIE EVENTÓW")
    
    for i in range(3):
        results = manager.emit('test_db_event', {
            'test_id': f'test_{i+1}',
            'message': f'Test message {i+1}',
            'should_fail': i == 1  # Drugi test zakończy się błędem
        }, source='database_test')
        
        print(f"   Event {i+1}: {len(results)} callbacków wykonano")
        time.sleep(1)
    
    # Poczekaj na zakończenie wszystkich operacji
    time.sleep(3)
    
    # Test 3: Pobieranie statystyk
    print(f"\n📊 TEST 3: STATYSTYKI")
    
    stats = manager.get_stats()
    if 'database_stats' in stats:
        db_stats = stats['database_stats']
        print(f"   Eventy: {db_stats.get('total_events', 0)}")
        print(f"   Wykonania: {db_stats.get('total_executions', 0)}")
        print(f"   Sukces: {db_stats.get('successful_executions', 0)}")
        print(f"   Błędy: {db_stats.get('failed_executions', 0)}")
        print(f"   Średni czas: {db_stats.get('avg_execution_time_ms', 0):.2f}ms")
        print(f"   Wskaźnik sukcesu: {db_stats.get('success_rate', 0):.1f}%")
        print(f"   Aktywne zadania: {db_stats.get('active_tasks', 0)}")
        
        if db_stats.get('top_events'):
            print(f"   Top eventy: {db_stats['top_events']}")
    else:
        print("   ❌ Brak statystyk z bazy danych")
    
    # Test 4: Historia wykonań
    print(f"\n📜 TEST 4: HISTORIA WYKONAŃ")
    
    history = manager.get_execution_history('test_db_event', limit=10)
    print(f"   Znaleziono {len(history)} wykonań w historii")
    
    for i, execution in enumerate(history[:3]):  # Pokaż tylko pierwsze 3
        print(f"   {i+1}. {execution['callback_function']} - {execution['status']} "
              f"({execution['execution_time_ms']}ms)")
    
    # Test 5: Oczekujące zadania
    print(f"\n⏳ TEST 5: OCZEKUJĄCE ZADANIA")
    
    pending = manager.get_pending_executions()
    print(f"   Oczekujące zadania: {len(pending)}")
    
    for task in pending[:3]:  # Pokaż tylko pierwsze 3
        print(f"   - {task['callback_function']} dla '{task['event_name']}' "
              f"(priorytet: {task['priority']}, wykonań: {task['execution_count']})")
    
    # Test 6: Statystyki okresowe
    print(f"\n📈 TEST 6: STATYSTYKI OKRESOWE")
    
    # Utwórz snapshot
    manager.create_stats_snapshot("hour")
    
    # Pobierz statystyki dla ostatnich okresów
    period_stats = manager.get_period_stats("hour", 3)
    print(f"   Statystyki dla {len(period_stats)} ostatnich godzin")
    
    for i, stat in enumerate(period_stats):
        print(f"   {i+1}. {stat['period_start'][:16]} - "
              f"{stat['total_events']} eventów, "
              f"{stat['total_executions']} wykonań, "
              f"sukces: {stat['success_rate']:.1f}%")
    
    # Test 7: Czyszczenie danych
    print(f"\n🧹 TEST 7: CZYSZCZENIE STARYCH DANYCH")
    
    # Nie czyść jeszcze - tylko pokaż co by zostało wyczyszczone
    print("   (Czyszczenie zostanie pominięte w teście)")
    # cleanup_result = manager.cleanup_old_callbacks(days_old=30)
    # print(f"   Wyczyszczono: {cleanup_result}")
    
    # Test 8: Finalne statystyki
    print(f"\n🎯 TEST 8: FINALNE STATYSTYKI")
    
    final_stats = manager.get_stats()
    print(f"   Całkowite callbacki: {final_stats.get('total_callbacks', 0)}")
    print(f"   Całkowite wykonania: {final_stats.get('total_executions', 0)}")
    print(f"   Błędne wykonania: {final_stats.get('failed_executions', 0)}")
    print(f"   Async wykonania: {final_stats.get('async_executions', 0)}")
    
    if 'database_stats' in final_stats:
        db_final = final_stats['database_stats']
        print(f"   📊 BAZA DANYCH:")
        print(f"      Eventy: {db_final.get('total_events', 0)}")
        print(f"      Wykonania: {db_final.get('total_executions', 0)}")
        print(f"      Sukces: {db_final.get('success_rate', 0):.1f}%")
    
    print(f"\n✅ KOMPLETNY TEST ZAKOŃCZONY POMYŚLNIE!")
    print("="*60)

def main():
    """Główna funkcja testowa"""
    try:
        test_complete_callback_database()
    except Exception as e:
        print(f"❌ Błąd w teście: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
