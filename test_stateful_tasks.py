
#!/usr/bin/env python3
"""
🎯 Test StatefulTaskFlow - Demonstracja zadań z kontrolą stanu
"""

import asyncio
import json
import uuid
from luxdb_v2.core.astral_engine_v3 import quick_start_v3

async def simulate_chunked_processing(engine, task_id: str):
    """Symuluje przetwarzanie zadania z chunkami"""
    print(f"🔄 Rozpoczynam przetwarzanie zadania {task_id}")
    
    # Rozpocznij przetwarzanie
    await engine.stateful_task_flow.start_task_processing(task_id)
    
    # Symuluj dodawanie chunków
    chunks_data = [
        {"type": "analysis", "progress": 25, "data": "Analiza danych wejściowych..."},
        {"type": "processing", "progress": 50, "data": "Przetwarzanie głównych operacji..."},
        {"type": "optimization", "progress": 75, "data": "Optymalizacja wyników..."},
        {"type": "finalization", "progress": 100, "data": "Finalizacja i weryfikacja..."}
    ]
    
    for i, chunk_data in enumerate(chunks_data):
        await asyncio.sleep(1)  # Symulacja czasu przetwarzania
        
        chunk = await engine.stateful_task_flow.add_task_chunk(
            task_id, 
            chunk_data,
            {"step": i+1, "total_steps": len(chunks_data)}
        )
        
        if chunk:
            print(f"  📦 Dodano chunk {chunk.chunk_id}: {chunk_data['type']}")
    
    # Zakończ zadanie
    await asyncio.sleep(1)
    await engine.stateful_task_flow.complete_task(task_id, {
        "final_result": "Zadanie zakończone pomyślnie",
        "total_processing_time": "4 sekundy"
    })
    
    print(f"✅ Zadanie {task_id} zakończone")

async def test_stateful_task_flow():
    """Testuje StatefulTaskFlow"""
    print("🎯 Testowanie StatefulTaskFlow...")
    
    # Uruchom silnik astralny
    engine = await quick_start_v3(
        realms={
            'intentions': 'intention://memory'
        },
        flows={
            'callback': {'enabled': True}
        }
    )
    
    if not engine.stateful_task_flow:
        print("❌ StatefulTaskFlow nie jest dostępny")
        return
    
    # Symuluj żądanie klienta
    client_uid = f"test_client_{uuid.uuid4().hex[:8]}"
    request_data = {
        "description": "Analiza danych testowych z wieloetapowym przetwarzaniem",
        "task": "Przeprowadź kompleksową analizę",
        "requirements": ["analiza_danych", "optymalizacja", "raportowanie"],
        "expected_result": "Raport z analizy danych",
        "technical_details": {
            "input_size": "1000 rekordów",
            "expected_chunks": 4,
            "processing_mode": "async"
        }
    }
    
    print(f"👤 Klient: {client_uid}")
    print(f"📝 Żądanie: {request_data['description']}")
    
    # Utwórz zadanie
    task = await engine.stateful_task_flow.create_task_from_request(
        client_uid, request_data
    )
    
    print(f"🎯 Utworzono zadanie: {task.task_id}")
    print(f"🧠 Powiązana intencja: {task.intention.essence.name}")
    
    # Rozpocznij przetwarzanie w tle
    processing_task = asyncio.create_task(
        simulate_chunked_processing(engine, task.task_id)
    )
    
    # Symuluj klienta odbierającego chunki
    print("\n📡 Symulacja klienta odbierającego chunki...")
    
    # Monitoruj zadanie
    for _ in range(15):  # 15 sekund monitorowania
        await asyncio.sleep(1)
        
        # Pobierz aktualny stan zadania
        current_task = engine.stateful_task_flow.get_task(task.task_id)
        if not current_task:
            break
            
        print(f"📊 Stan: {current_task.state.value}, Chunki: {len(current_task.chunks)}")
        
        # Symuluj potwierdzanie chunków (z lekkim opóźnieniem)
        for chunk in current_task.chunks:
            if chunk.chunk_id not in current_task.confirmed_chunks:
                # Symuluj losowe opóźnienie potwierdzenia
                await asyncio.sleep(0.5)
                
                await engine.stateful_task_flow.confirm_chunk_receipt(
                    task.task_id, chunk.chunk_id, client_uid
                )
                print(f"  ✅ Potwierdzono chunk: {chunk.chunk_id}")
        
        # Sprawdź czy zadanie zakończone
        if current_task.state.value == "completed":
            print("🎉 Zadanie zakończone - symulacja potwierdzenia przez klienta")
            await asyncio.sleep(1)
            
            # Archiwizuj zadanie
            await engine.stateful_task_flow.archive_task(task.task_id, client_uid)
            print("📁 Zadanie zarchiwizowane")
            break
    
    # Poczekaj na zakończenie przetwarzania
    await processing_task
    
    # Pokaż statystyki
    stats = engine.stateful_task_flow.get_status()
    print(f"\n📈 Statystyki StatefulTaskFlow:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("🎯 Test StatefulTaskFlow zakończony")

if __name__ == "__main__":
    asyncio.run(test_stateful_task_flow())
