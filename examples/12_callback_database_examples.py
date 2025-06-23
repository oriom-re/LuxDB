
#!/usr/bin/env python3
"""
Przykłady użycia systemu callbacków z bazą danych
Demonstruje persystencję, śledzenie wykonań i statystyki
"""

import time
import asyncio
from datetime import datetime
from luxdb.callback_system import get_astral_callback_manager

def demonstrate_callback_persistence():
    """Demonstracja persystencji callbacków w bazie danych"""
    print("\n" + "="*60)
    print("💾 DEMONSTRACJA PERSYSTENCJI CALLBACKÓW")
    print("="*60)
    
    manager = get_astral_callback_manager()
    # debug manager
    print(f"manager: {manager}")
    # Upewnij się, że baza danych jest włączona
    if not manager.database_enabled:
        print("❌ Baza danych nie jest włączona - nie można demonstruować persystencji")
    
    def persistent_callback(context):
        print(f"📝 Callback persystentny: {context.data}")
        return f"persisted_{context.data['message']}"
    
    # Zarejestruj callback (zostanie zapisany w bazie)
    callback_id = manager.on('persistent_event', persistent_callback)
    print(f"🎯 Zarejestrowano callback: {callback_id}")
    
    # Emituj event (wykonanie zostanie zapisane w bazie)
    results = manager.emit('persistent_event', {
        'message': 'test_persistence',
        'timestamp': datetime.now().isoformat()
    }, source='database_demo')
    
    print(f"📊 Wykonano {len(results)} callbacków")
    
    # Pokaż statystyki z bazy danych
    stats = manager.get_stats()
    if 'database_stats' in stats:
        db_stats = stats['database_stats']
        print(f"\n📈 Statystyki z bazy danych:")
        print(f"   Eventy: {db_stats.get('total_events', 0)}")
        print(f"   Wykonania: {db_stats.get('total_executions', 0)}")
        print(f"   Sukces: {db_stats.get('successful_executions', 0)}")
        print(f"   Błędy: {db_stats.get('failed_executions', 0)}")
        print(f"   Średni czas: {db_stats.get('avg_execution_time_ms', 0)}ms")

def demonstrate_execution_tracking():
    """Demonstracja śledzenia wykonań callbacków"""
    print("\n" + "="*60)
    print("🔍 DEMONSTRACJA ŚLEDZENIA WYKONAŃ")
    print("="*60)
    
    manager = get_astral_callback_manager()
    
    def tracked_callback(context):
        print(f"📍 Śledzony callback: {context.data}")
        time.sleep(2)  # Symuluj pracę
        return {"processed": True, "data": context.data}
    
    def error_callback(context):
        print(f"💥 Callback z błędem: {context.data}")
        raise Exception("Testowy błąd callback")
    
    # Zarejestruj callbacki
    manager.on('tracked_event', tracked_callback)
    manager.on('tracked_event', error_callback)
    
    # Emituj event
    print("🚀 Uruchamianie śledzonych callbacków...")
    results = manager.emit('tracked_event', {
        'task_id': 'tracking_test_001',
        'operation': 'data_processing'
    }, source='tracking_demo')
    
    print(f"📊 Wyniki: {len(results)} callbacków")
    
    # Poczekaj na zakończenie
    time.sleep(3)
    
    # Pokaż aktualne statystyki
    stats = manager.get_stats()
    print(f"\n📈 Aktualne statystyki:")
    print(f"   Całkowite wykonania: {stats.get('total_executions', 0)}")
    print(f"   Błędne wykonania: {stats.get('failed_executions', 0)}")

def demonstrate_async_tracking():
    """Demonstracja śledzenia asynchronicznych callbacków"""
    print("\n" + "="*60)
    print("🔄 DEMONSTRACJA ŚLEDZENIA ASYNC CALLBACKÓW")
    print("="*60)
    
    async def run_async_tracking():
        manager = get_astral_callback_manager()
        
        async def async_tracked_callback(context):
            print(f"⚡ Async śledzony callback: {context.data}")
            await asyncio.sleep(3)  # Symuluj async pracę
            return {"async_processed": True, "data": context.data}
        
        async def async_quick_callback(context):
            print(f"🏃 Szybki async callback: {context.data}")
            await asyncio.sleep(1)
            return {"quick_processed": True}
        
        # Zarejestruj async callbacki
        manager.on('async_tracked_event', async_tracked_callback)
        manager.on('async_tracked_event', async_quick_callback)
        
        # Emituj event
        print("🚀 Uruchamianie async śledzonych callbacków...")
        results = manager.emit('async_tracked_event', {
            'async_task_id': 'async_tracking_001',
            'operation': 'async_data_processing'
        }, source='async_tracking_demo')
        
        print(f"📊 Uruchomiono {len(results)} callbacków")
        
        # Śledzenie wyników w czasie rzeczywistym
        async for result_data in manager.stream_async_results(results):
            print(f"   ✅ Callback {result_data['index']} ukończony: {result_data['result']}")
    
    try:
        asyncio.run(run_async_tracking())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            print("🔄 Demo async tracking uruchomione w tle")
        else:
            print(f"❌ Błąd: {e}")

def demonstrate_callback_analytics():
    """Demonstracja analityki callbacków z bazy danych"""
    print("\n" + "="*60)
    print("📊 DEMONSTRACJA ANALITYKI CALLBACKÓW")
    print("="*60)
    
    manager = get_astral_callback_manager()
    
    # Utwórz różne typy callbacków dla analityki
    def analytics_callback_fast(context):
        print(f"⚡ Szybki callback: {context.data}")
        return "fast_result"
    
    def analytics_callback_slow(context):
        print(f"🐌 Wolny callback: {context.data}")
        time.sleep(1)
        return "slow_result"
    
    def analytics_callback_error(context):
        print(f"💥 Callback z błędem: {context.data}")
        if context.data.get('should_fail', False):
            raise Exception("Celowy błąd dla analityki")
        return "error_test_result"
    
    # Zarejestruj callbacki
    manager.on('analytics_test', analytics_callback_fast)
    manager.on('analytics_test', analytics_callback_slow)
    manager.on('analytics_test', analytics_callback_error)
    
    # Emituj różne eventy dla analityki
    print("🚀 Generowanie danych dla analityki...")
    
    for i in range(5):
        results = manager.emit('analytics_test', {
            'test_run': i + 1,
            'should_fail': i == 2  # Jeden błąd w środku
        }, source='analytics_demo')
        
        print(f"   📊 Test {i+1}: {len(results)} callbacków")
        time.sleep(0.5)
    
    # Pokaż szczegółowe statystyki
    stats = manager.get_stats()
    print(f"\n📈 SZCZEGÓŁOWE STATYSTYKI:")
    print(f"   Zarejestrowane callbacki: {stats.get('registered_callbacks', 0)}")
    print(f"   Całkowite wykonania: {stats.get('total_executions', 0)}")
    print(f"   Błędne wykonania: {stats.get('failed_executions', 0)}")
    print(f"   Async wykonania: {stats.get('async_executions', 0)}")
    
    if 'database_stats' in stats:
        db_stats = stats['database_stats']
        print(f"\n💾 STATYSTYKI Z BAZY DANYCH:")
        print(f"   Eventy: {db_stats.get('total_events', 0)}")
        print(f"   Wykonania: {db_stats.get('total_executions', 0)}")
        print(f"   Wskaźnik sukcesu: {db_stats.get('success_rate', 0):.1f}%")
        print(f"   Średni czas wykonania: {db_stats.get('avg_execution_time_ms', 0):.2f}ms")
        print(f"   Aktywne zadania: {db_stats.get('active_tasks', 0)}")

def demonstrate_cleanup():
    """Demonstracja czyszczenia starych danych"""
    print("\n" + "="*60)
    print("🧹 DEMONSTRACJA CZYSZCZENIA DANYCH")
    print("="*60)
    
    manager = get_astral_callback_manager()
    
    print("🗑️ Czyszczenie starych danych callbacków (starszych niż 30 dni)...")
    manager.cleanup_old_callbacks(days_old=30)
    
    print("✅ Czyszczenie zakończone")
    
    # Pokaż aktualne statystyki
    stats = manager.get_stats()
    if 'database_stats' in stats:
        db_stats = stats['database_stats']
        print(f"📊 Pozostało eventów: {db_stats.get('total_events', 0)}")
        print(f"📊 Pozostało wykonań: {db_stats.get('total_executions', 0)}")

def main():
    """Główna funkcja demonstracyjna"""
    print("🌟 SYSTEM CALLBACKÓW Z BAZĄ DANYCH LUXDB")
    print("Demonstracja persystencji, śledzenia i analityki")
    
    try:
        demonstrate_callback_persistence()
        time.sleep(1)
        
        # demonstrate_execution_tracking()
        # time.sleep(1)
        
        # demonstrate_async_tracking()
        # time.sleep(1)
        
        # demonstrate_callback_analytics()
        # time.sleep(1)
        
        demonstrate_cleanup()
        
        print("\n" + "="*60)
        print("✅ WSZYSTKIE DEMONSTRACJE ZAKOŃCZONE")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Błąd podczas demonstracji: {e}")

if __name__ == "__main__":
    main()
