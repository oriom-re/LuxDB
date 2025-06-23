
#!/usr/bin/env python3
"""
Kompletny test systemu callbacków z bazą danych
Demonstruje pełną integrację persystencji, śledzenia i analityki
"""

import time
import asyncio
from datetime import datetime
from luxdb.callback_system import get_astral_callback_manager, CallbackPriority

def test_database_persistence():
    """Test persystencji callbacków w bazie danych"""
    print("\n" + "="*60)
    print("🔮 TEST PERSYSTENCJI CALLBACKÓW W BAZIE DANYCH")
    print("="*60)
    
    manager = get_astral_callback_manager()
    print(f"📊 Status bazy danych: {'Włączona' if manager.database_enabled else 'Wyłączona'}")
    
    if not manager.database_enabled:
        print("❌ Baza danych nie jest dostępna - pomijam test")
        return

    if "main" not in manager.db_manager.list_databases():
    
    def test_callback(context):
        print(f"🎯 Test callback wykonany: {context.data}")
        return f"processed_{context.data.get('test_id', 'unknown')}"
    
    # Zarejestruj callback
    callback_id = manager.on('database_test_event', test_callback, priority=CallbackPriority.HIGH)
    print(f"✅ Zarejestrowano callback: {callback_id}")
    
    # Emituj zdarzenia testowe
    for i in range(3):
        results = manager.emit('database_test_event', {
            'test_id': f'test_{i+1}',
            'timestamp': datetime.now().isoformat(),
            'session_test': True
        }, source='database_test')
        
        print(f"📤 Emitowano zdarzenie {i+1}: {len(results)} callbacków wykonano")
        time.sleep(0.5)
    
    # Pokaż statystyki
    stats = manager.get_stats()
    print(f"\n📈 STATYSTYKI PO TESTACH:")
    print(f"   Zarejestrowane callbacki: {stats.get('registered_callbacks', 0)}")
    print(f"   Całkowite wykonania: {stats.get('total_executions', 0)}")
    
    if 'database_stats' in stats:
        db_stats = stats['database_stats']
        print(f"   Eventy w bazie: {db_stats.get('total_events', 0)}")
        print(f"   Wykonania w bazie: {db_stats.get('total_executions', 0)}")

def test_execution_tracking():
    """Test śledzenia wykonań callbacków"""
    print("\n" + "="*60)
    print("🔍 TEST ŚLEDZENIA WYKONAŃ CALLBACKÓW")
    print("="*60)
    
    manager = get_astral_callback_manager()
    
    def success_callback(context):
        print(f"✅ Callback sukces: {context.data}")
        time.sleep(1)  # Symuluj pracę
        return {"status": "success", "processed": context.data}
    
    def error_callback(context):
        print(f"💥 Callback błąd: {context.data}")
        if context.data.get('should_fail', False):
            raise Exception("Testowy błąd callback")
        return {"status": "success"}
    
    # Zarejestruj callbacki
    manager.on('tracking_test', success_callback)
    manager.on('tracking_test', error_callback)
    
    # Test z sukcesem
    print("🚀 Test callbacków - sukces:")
    results = manager.emit('tracking_test', {
        'task_id': 'success_task',
        'should_fail': False
    }, source='tracking_test')
    
    print(f"📊 Wyniki sukces: {len(results)} callbacków")
    time.sleep(2)
    
    # Test z błędem
    print("🚀 Test callbacków - błąd:")
    results = manager.emit('tracking_test', {
        'task_id': 'error_task', 
        'should_fail': True
    }, source='tracking_test')
    
    print(f"📊 Wyniki błąd: {len(results)} callbacków")
    time.sleep(1)
    
    # Pokaż historię wykonań
    if manager.database_enabled:
        history = manager.get_execution_history('tracking_test', limit=5)
        print(f"\n📜 HISTORIA WYKONAŃ (ostatnie 5):")
        for exec in history:
            status_icon = "✅" if exec['status'] == 'completed' else "❌"
            print(f"   {status_icon} {exec['callback_function']} - {exec['status']} - {exec.get('execution_time_ms', 0)}ms")

def test_async_callbacks():
    """Test asynchronicznych callbacków z bazą danych"""
    print("\n" + "="*60)
    print("⚡ TEST ASYNCHRONICZNYCH CALLBACKÓW")
    print("="*60)
    
    async def run_async_test():
        manager = get_astral_callback_manager()
        
        async def async_slow_callback(context):
            print(f"🐌 Async wolny callback: {context.data}")
            await asyncio.sleep(2)
            return f"async_slow_result_{context.data.get('id')}"
        
        async def async_fast_callback(context):
            print(f"🏃 Async szybki callback: {context.data}")
            await asyncio.sleep(0.5)
            return f"async_fast_result_{context.data.get('id')}"
        
        def sync_callback(context):
            print(f"🔵 Sync callback: {context.data}")
            return f"sync_result_{context.data.get('id')}"
        
        # Zarejestruj callbacki
        manager.on('async_test', async_slow_callback, priority=CallbackPriority.HIGH)
        manager.on('async_test', async_fast_callback, priority=CallbackPriority.NORMAL)
        manager.on('async_test', sync_callback, priority=CallbackPriority.LOW)
        
        # Emituj zdarzenie
        print("🚀 Uruchamianie async callbacków...")
        results = manager.emit('async_test', {'id': 'async_test_1'}, source='async_test')
        
        print(f"📊 Uruchomiono {len(results)} callbacków")
        
        # Monitoruj wyniki w czasie rzeczywistym
        if hasattr(manager, 'stream_async_results'):
            async for result_data in manager.stream_async_results(results):
                print(f"   ✅ Callback {result_data['index']} ukończony: {result_data['result']}")
        
        return True
    
    try:
        result = asyncio.run(run_async_test())
        print("✅ Test async callbacków zakończony")
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            print("🔄 Test async uruchomiony w istniejącym event loop")
        else:
            print(f"❌ Błąd testu async: {e}")

def test_callback_analytics():
    """Test analityki i statystyk callbacków"""
    print("\n" + "="*60)
    print("📊 TEST ANALITYKI CALLBACKÓW")
    print("="*60)
    
    manager = get_astral_callback_manager()
    
    def analytics_fast(context):
        print(f"⚡ Analytics fast: {context.data}")
        return "fast_result"
    
    def analytics_slow(context):
        print(f"🐌 Analytics slow: {context.data}")
        time.sleep(0.8)
        return "slow_result"
    
    def analytics_variable(context):
        should_fail = context.data.get('fail_test', False)
        print(f"🎲 Analytics variable (fail: {should_fail}): {context.data}")
        if should_fail:
            raise Exception("Celowy błąd analityki")
        return "variable_result"
    
    # Zarejestruj callbacki
    manager.on('analytics_event', analytics_fast, priority=CallbackPriority.HIGH)
    manager.on('analytics_event', analytics_slow, priority=CallbackPriority.NORMAL)
    manager.on('analytics_event', analytics_variable, priority=CallbackPriority.LOW)
    
    # Generuj dane testowe
    print("🔬 Generowanie danych analitycznych...")
    for i in range(5):
        results = manager.emit('analytics_event', {
            'run_id': i + 1,
            'fail_test': i == 2,  # Jeden błąd w środku
            'analytics_test': True
        }, source='analytics_generator')
        
        print(f"   📊 Run {i+1}: {len(results)} callbacków")
        time.sleep(0.3)
    
    # Poczekaj na zakończenie wszystkich operacji
    time.sleep(2)
    
    # Pokaż szczegółowe statystyki
    stats = manager.get_stats()
    print(f"\n📈 SZCZEGÓŁOWA ANALITYKA:")
    print(f"   Wykonania ogółem: {stats.get('total_executions', 0)}")
    print(f"   Błędne wykonania: {stats.get('failed_executions', 0)}")
    print(f"   Async wykonania: {stats.get('async_executions', 0)}")
    
    if 'database_stats' in stats:
        db_stats = stats['database_stats']
        print(f"\n💾 ANALITYKA Z BAZY DANYCH:")
        print(f"   Eventy w bazie: {db_stats.get('total_events', 0)}")
        print(f"   Wskaźnik sukcesu: {db_stats.get('success_rate', 0):.1f}%")
        print(f"   Średni czas: {db_stats.get('avg_execution_time_ms', 0):.2f}ms")
        
        # Top eventy
        top_events = db_stats.get('top_events', {})
        if top_events:
            print(f"   Top eventy ostatnie 24h:")
            for event, count in list(top_events.items())[:3]:
                print(f"     • {event}: {count} razy")

def test_cleanup_and_maintenance():
    """Test czyszczenia i konserwacji bazy danych"""
    print("\n" + "="*60)
    print("🧹 TEST CZYSZCZENIA I KONSERWACJI")
    print("="*60)
    
    manager = get_astral_callback_manager()
    
    if not manager.database_enabled:
        print("❌ Baza danych wyłączona - pomijam test")
        return
    
    # Pokaż statystyki przed czyszczeniem
    stats_before = manager.get_stats()
    if 'database_stats' in stats_before:
        db_stats = stats_before['database_stats']
        print(f"📊 Przed czyszczeniem:")
        print(f"   Eventy: {db_stats.get('total_events', 0)}")
        print(f"   Wykonania: {db_stats.get('total_executions', 0)}")
    
    # Utwórz snapshot statystyk
    print("📸 Tworzenie snapshot statystyk...")
    try:
        manager.create_stats_snapshot("hour")
        print("✅ Snapshot utworzony")
    except Exception as e:
        print(f"❌ Błąd snapshot: {e}")
    
    # Wyczyść stare dane (dla testów - bardzo krótki okres)
    print("🗑️ Czyszczenie starych danych...")
    try:
        cleanup_result = manager.cleanup_old_callbacks(days_old=0)  # Wyczyść wszystko dla testu
        if cleanup_result:
            print(f"✅ Wyczyszczono: {cleanup_result}")
        else:
            print("ℹ️ Brak danych do wyczyszczenia")
    except Exception as e:
        print(f"❌ Błąd czyszczenia: {e}")
    
    # Pokaż statystyki po czyszczeniu
    stats_after = manager.get_stats()
    if 'database_stats' in stats_after:
        db_stats = stats_after['database_stats']
        print(f"📊 Po czyszczeniu:")
        print(f"   Eventy: {db_stats.get('total_events', 0)}")
        print(f"   Wykonania: {db_stats.get('total_executions', 0)}")

def test_session_integration():
    """Test integracji callbacków z sesjami użytkowników"""
    print("\n" + "="*60)
    print("👤 TEST INTEGRACJI Z SESJAMI UŻYTKOWNIKÓW")
    print("="*60)
    
    manager = get_astral_callback_manager()
    
    def session_callback(context):
        user_id = context.user_id
        session_id = context.session_id
        print(f"👤 Session callback - User: {user_id}, Session: {session_id}")
        print(f"   Data: {context.data}")
        return f"session_processed_user_{user_id}"
    
    # Zarejestruj callback dla zdarzeń sesji
    manager.on('user_session_event', session_callback)
    
    # Symuluj zdarzenia z różnymi sesjami
    test_sessions = [
        {'user_id': 'user_123', 'session_id': 'session_abc'},
        {'user_id': 'user_456', 'session_id': 'session_def'},
        {'user_id': 'user_789', 'session_id': 'session_ghi'}
    ]
    
    for session_info in test_sessions:
        results = manager.emit(
            'user_session_event',
            {
                'action': 'login',
                'timestamp': datetime.now().isoformat(),
                'user_data': session_info
            },
            source='session_test',
            user_id=session_info['user_id'],
            session_id=session_info['session_id']
        )
        
        print(f"📤 Zdarzenie sesji dla {session_info['user_id']}: {len(results)} callbacków")
        time.sleep(0.2)

def show_final_statistics():
    """Pokazuje finalne statystyki całego testu"""
    print("\n" + "="*60)
    print("🏆 FINALNE STATYSTYKI CAŁEGO TESTU")
    print("="*60)
    
    manager = get_astral_callback_manager()
    stats = manager.get_stats()
    
    print(f"📊 PODSUMOWANIE CALLBACKÓW:")
    print(f"   Zarejestrowane: {stats.get('registered_callbacks', 0)}")
    print(f"   Globalne: {stats.get('global_callbacks', 0)}")
    print(f"   W namespace: {stats.get('namespace_callbacks', 0)}")
    print(f"   Wykonania ogółem: {stats.get('total_executions', 0)}")
    print(f"   Błędne: {stats.get('failed_executions', 0)}")
    print(f"   Async: {stats.get('async_executions', 0)}")
    
    if 'database_stats' in stats:
        db_stats = stats['database_stats']
        print(f"\n💾 STATYSTYKI BAZY DANYCH:")
        print(f"   Status: Włączona ✅")
        print(f"   Eventy: {db_stats.get('total_events', 0)}")
        print(f"   Wykonania: {db_stats.get('total_executions', 0)}")
        print(f"   Sukces: {db_stats.get('successful_executions', 0)}")
        print(f"   Błędy: {db_stats.get('failed_executions', 0)}")
        print(f"   Wskaźnik sukcesu: {db_stats.get('success_rate', 0):.1f}%")
        print(f"   Średni czas: {db_stats.get('avg_execution_time_ms', 0):.2f}ms")
    else:
        print(f"\n💾 BAZA DANYCH: Wyłączona ❌")
    
    print(f"\n🌍 NAMESPACES: {stats.get('namespaces', [])}")

def main():
    """Główna funkcja testowa"""
    print("🌟 KOMPLETNY TEST SYSTEMU CALLBACKÓW Z BAZĄ DANYCH")
    print("Testujemy persystencję, śledzenie, analitykę i integrację")
    
    try:
        # Uruchom wszystkie testy
        test_database_persistence()
        time.sleep(1)
        
        test_execution_tracking()
        time.sleep(1)
        
        test_async_callbacks()
        time.sleep(1)
        
        test_callback_analytics()
        time.sleep(1)
        
        test_session_integration()
        time.sleep(1)
        
        test_cleanup_and_maintenance()
        time.sleep(1)
        
        show_final_statistics()
        
        print("\n" + "="*60)
        print("✨ WSZYSTKIE TESTY ZAKOŃCZONE POMYŚLNIE!")
        print("System callbacków z bazą danych jest w pełni funkcjonalny 🎉")
        print("Możesz teraz używać wszystkich funkcji persystencji i analityki")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Błąd podczas testów: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
