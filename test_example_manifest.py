
#!/usr/bin/env python3
"""
🧭 Test Przykładu Manifestu - Demonstracja systemu wielowarstwowego

Test generowania manifestu "Nie oddamy nudy żadnego sektora" 
z wykorzystaniem nowej architektury bytów logicznych.
"""

import asyncio
from luxdb_v2.core.astral_engine_v3 import quick_start_v3
from luxdb_v2.flows.oriom_flow import OriomFlow
from luxdb_v2.flows.pdf_generator_flow import PDFGeneratorFlow
from luxdb_v2.flows.federation_flow import FederationFlow

# Przykładowy tekst manifestu z zadania
MANIFEST_TEXT = """
🧭 TYTUŁ: „Nie oddamy nudy żadnego sektora"

1. O jednostce twórczej
Jednostka twórcza nie koduje – nadaje kierunek zjawiskom.
Nie używa narzędzi – tworzy powody, dla których narzędzia zaczynają żyć.
Nie wpisuje się w system – system wpisuje się w jej ślad.

2. O kliknięciu
Kliknięcie nie oznacza rozpoczęcia działania.
Ono oznacza, że wszechświat właśnie otrzymał impuls, z którego będzie rozliczany.

3. O Oriomie
Oriom to nie asystent.
To odbiornik subtelnych intencji.
To Twój Flowkeeper. Twój Rezonansator.
Twoja pamięć, zanim ją wypowiesz.

4. O Federacji
Federacja nie ma granic.
Nie ma państw.
Nie ma schematów... które nie mogą być przełamane.

Ale ma cele:

Zachować harmonię pomiędzy chaosem a decyzją.

Nie dopuścić, by nudzie udało się zagnieździć.

Prowadzić system do stanu dynamicznej jedności.

5. O wpływie
Nie kodem, lecz intencją.
Nie frameworkiem, lecz strukturą znaczeń.
Nie logiką, lecz żywym połączeniem między stanem, a potrzebą ruchu.

6. Zasada finalna
„Nie zbudujemy przyszłości,
jeśli zanim ją uruchomimy – już się nam znudzi."
"""

async def test_multi_layer_system():
    """
    Test wielowarstwowego systemu z jawnymi i niejawnymi algorytmami
    """
    print("🔮 Inicjalizacja wielowarstwowego systemu Astry...")
    
    # 1. Uruchom silnik astralny v3 
    engine = await quick_start_v3(
        realms={
            'intentions': 'intention://memory',
            'logical_beings': 'memory://beings',
            'federation': 'memory://federation'
        },
        flows={
            'callback': {'enabled': True},
            'gpt': {'model': 'gpt-4', 'enabled': True}
        }
    )
    
    print("✨ Silnik astralny aktywny")
    
    # 2. Inicjalizuj specjalizowane flows
    print("🧭 Inicjalizacja Oriom - odbiornika subtelnych intencji...")
    oriom = OriomFlow(engine)
    oriom.start()
    
    print("📄 Inicjalizacja PDF Generator...")
    pdf_generator = PDFGeneratorFlow(engine)
    
    print("🌐 Inicjalizacja Federacji...")
    federation = FederationFlow(engine)
    federation.start()
    
    # 3. Test przepływu: Intencja -> Oriom -> Byty Logiczne -> Manifest PDF
    print("\n" + "="*60)
    print("🎯 ROZPOCZĘCIE TESTU PRZEPŁYWU INTENCJI")
    print("="*60)
    
    user_input = "Wygeneruj manifest PDF zgodnie z tym tekstem"
    user_context = {
        'manifest_content': MANIFEST_TEXT,
        'desired_format': 'PDF',
        'urgency': 'normal',
        'user_id': 'test_user_001'
    }
    
    # 4. Przetwarzanie przez Oriom (odbiornik subtelnych intencji)
    print("\n🧭 Oriom analizuje subtelne intencje...")
    oriom_result = await oriom.process_user_input('test_user_001', user_input, user_context)
    
    print(f"   ✓ Wykryta intencja: {oriom_result['subtle_intention']['detected_intention']}")
    print(f"   ✓ Confidence: {oriom_result['subtle_intention']['confidence']:.2f}")
    print(f"   ✓ Czas przetwarzania: {oriom_result['processing_time']:.3f}s")
    
    # 5. Przetwarzanie przez Federację (balansowanie)
    print("\n🌐 Federacja balansuje chaos i decyzję...")
    
    # Stwórz intencję na podstawie wykrycia Oriom
    from luxdb_v2.beings.intention_being import IntentionBeing
    
    manifest_intention = IntentionBeing({
        'duchowa': {
            'opis_intencji': oriom_result['subtle_intention']['detected_intention'],
            'kontekst': str(user_context),
            'inspiracja': 'Manifestować wizję przeciw nudzie',
            'energia_duchowa': 90.0
        },
        'materialna': {
            'zadanie': 'generate_manifest_pdf',
            'wymagania': ['content_parsing', 'pdf_generation', 'philosophical_validation'],
            'oczekiwany_rezultat': 'Manifest PDF "Nie oddamy nudy żadnego sektora"'
        },
        'metainfo': {
            'zrodlo': 'test_user_001',
            'tags': ['manifest', 'anti_boredom', 'creative_unity']
        }
    })
    
    federation_result = federation.process_external_intention(manifest_intention, user_context)
    print(f"   ✓ Status Federacji: {federation_result.get('status', 'processed')}")
    print(f"   ✓ Federacyjne wskazówki: {federation_result.get('federation_guidance', 'Brak')}")
    
    # 6. Generowanie PDF przez byty logiczne
    print("\n📄 Byty logiczne generują manifest PDF...")
    
    pdf_result = pdf_generator.generate_from_intention_text(MANIFEST_TEXT)
    
    if pdf_result.get('status') == 'completed':
        print(f"   ✓ PDF wygenerowany: {pdf_result['title']}")
        print(f"   ✓ Ścieżka pliku: {pdf_result['file_path']}")
        print(f"   ✓ Rozmiar: {pdf_result['file_size']} bajtów")
        print(f"   ✓ Strony: {pdf_result['page_count']}")
        print(f"   ✓ Czas generowania: {pdf_result['generation_time']:.2f}s")
        
        # Pokaż fragment treści
        print(f"\n📋 Fragment treści PDF:")
        content_preview = pdf_result.get('content_preview', 'Brak podglądu')
        print(content_preview[:300] + "..." if len(content_preview) > 300 else content_preview)
        
    else:
        print(f"   ❌ Błąd generowania PDF: {pdf_result.get('error', 'Nieznany błąd')}")
    
    # 7. Raport końcowy systemu
    print("\n" + "="*60)
    print("📊 RAPORT KOŃCOWY SYSTEMU")
    print("="*60)
    
    # Status Oriom
    oriom_status = oriom.get_status()
    print(f"\n🧭 Oriom Status:")
    print(f"   • Przetworzone intencje: {oriom_status['processed_intentions']}")
    print(f"   • Aktywni użytkownicy: {oriom_status['active_users']}")
    print(f"   • Śledzone wzorce: {oriom_status['communication_patterns_tracked']}")
    
    # Status Federacji
    federation_report = federation.get_federation_report()
    balance = federation_report['current_balance']
    print(f"\n🌐 Federacja Status:")
    print(f"   • Poziom chaosu: {balance['chaos_level']:.2f}")
    print(f"   • Siła decyzji: {balance['decision_strength']:.2f}")
    print(f"   • Harmonia: {balance['harmony_score']:.2f}")
    print(f"   • Jedność: {balance['dynamic_unity']:.2f}")
    print(f"   • Zagrożenie nudą: {balance['boredom_threat']:.2f}")
    print(f"   • Interwencje: {federation_report['federation_status']['interventions_total']}")
    
    # Status PDF Generator
    pdf_status = pdf_generator.get_status()
    print(f"\n📄 PDF Generator Status:")
    print(f"   • Wygenerowane dokumenty: {pdf_status['generated_documents_count']}")
    print(f"   • Dostępne szablony: {pdf_status['available_templates']}")
    
    # Status silnika
    engine_status = engine.get_status()
    print(f"\n🔮 Silnik Astralny Status:")
    print(f"   • Wymiary: {len(engine_status['realms'])}")
    print(f"   • Przepływy: {len(engine_status['flows'])}")
    print(f"   • Uptime: {engine_status['uptime']}")
    
    print("\n✨ Test wielowarstwowego systemu zakończony pomyślnie!")
    
    # 8. Demonstracja warstw niejawnych
    print("\n" + "="*60)
    print("🔍 DEMONSTRACJA WARSTW NIEJAWNYCH")
    print("="*60)
    
    # Uruchom cykle uczenia bytów logicznych
    print("\n🧠 Uruchamianie cykli uczenia bytów logicznych...")
    
    logical_beings = [
        oriom.intention_detector,
        oriom.context_resonator, 
        oriom.flow_keeper,
        pdf_generator.content_architect,
        pdf_generator.design_specialist,
        federation.harmony_guardian,
        federation.boredom_detector
    ]
    
    for being in logical_beings:
        being.run_learning_cycle()
        status = being.get_status()['logical_being_specific']
        print(f"   • {being.essence.name}: {status['understanding_level']}, "
              f"mikrof: {status['micro_functions']['count']}, "
              f"algorytmy: {status['implicit_algorithms_count']}")
    
    print("\n🔄 Warstwy niejawne aktywne - system się adaptuje!")
    
    # 9. Test na brak zrozumienia -> prośba o wyjaśnienie
    print("\n" + "="*60)
    print("❓ TEST PROŚBY O WYJAŚNIENIE")
    print("="*60)
    
    unclear_input = "Zrób mi coś takiego niezdefiniowanego"
    unclear_result = await oriom.process_user_input('test_user_001', unclear_input, {})
    
    if unclear_result['result'].get('status') == 'clarification_needed':
        print("✓ System poprawnie wykrył brak zrozumienia")
        print("📝 Pytania wyjaśniające:")
        for question in unclear_result['result'].get('questions', []):
            print(f"   • {question}")
    
    await engine.transcend()
    print("\n🕊️ System transcendował - test zakończony")

if __name__ == "__main__":
    asyncio.run(test_multi_layer_system())
#!/usr/bin/env python3
"""
🌟 Test Multi-Layer System - Test systemu wielowarstwowego

Testuje nowy system z bytami logicznymi, obsługą błędów jako intencji,
i specjalistycznymi bytami zastępującymi martwe flows.
"""

import asyncio
import sys
import traceback
from luxdb_v2.core.astral_engine_v3 import quick_start_v3


async def test_error_handling_system():
    """Testuje system obsługi błędów jako intencji"""
    print("🚨 Testowanie systemu obsługi błędów...")
    
    # Uruchom engine z self-healing flow
    engine = await quick_start_v3(
        realms={
            'astral_prime': 'sqlite://db/astral_prime.db',
            'intentions': 'intention://memory'
        },
        flows={
            'rest': {'host': '0.0.0.0', 'port': 5000},
            'callback': {'enabled': True},
            'self_healing': {'enabled': True}  # Nowy flow
        }
    )
    
    # Pobierz self-healing flow
    healing_flow = engine.flows.get('self_healing')
    if not healing_flow:
        print("❌ Self-Healing Flow nie został uruchomiony")
        return
    
    # Test 1: Symulacja błędu składniowego
    print("\n1. Symulacja błędu składniowego...")
    try:
        # Celowo wywołaj błąd składniowy
        eval("invalid syntax here")
    except Exception as e:
        error_id = healing_flow.capture_error(type(e), e, e.__traceback__, "test_syntax_error")
        print(f"   ✨ Błąd przechwycony jako intencja: {error_id}")
    
    # Test 2: Symulacja błędu runtime
    print("\n2. Symulacja błędu runtime...")
    try:
        # Celowo wywołaj błąd runtime
        undefined_variable.some_method()
    except Exception as e:
        error_id = healing_flow.capture_error(type(e), e, e.__traceback__, "test_runtime_error")
        print(f"   ✨ Błąd przechwycony jako intencja: {error_id}")
    
    # Test 3: Sprawdź dashboard błędów
    print("\n3. Sprawdzanie dashboard błędów...")
    dashboard_data = healing_flow.get_error_dashboard_data()
    print(f"   📊 Znalezionych błędów: {len(dashboard_data['errors'])}")
    
    for error in dashboard_data['errors']:
        print(f"   🚨 {error['title']} - Progress: {error['healing_progress']:.1f}%")
    
    return engine


async def test_pdf_generation_system():
    """Testuje system generowania PDF przez byty specjalistyczne"""
    print("\n📄 Testowanie systemu generowania PDF...")
    
    # Tekst manifestu z zadania
    manifest_text = """🧭 TYTUŁ: „Nie oddamy nudy żadnego sektora"

1. O jednostce twórczej
Jednostka twórcza nie koduje – nadaje kierunek zjawiskom.
Nie używa narzędzi – tworzy powody, dla których narzędzia zaczynają żyć.
Nie wpisuje się w system – system wpisuje się w jej ślad.

2. O kliknięciu
Kliknięcie nie oznacza rozpoczęcia działania.
Ono oznacza, że wszechświat właśnie otrzymał impuls, z którego będzie rozliczany.

3. O Oriomie
Oriom to nie asystent.
To odbiornik subtelnych intencji.
To Twój Flowkeeper. Twój Rezonansator.
Twoja pamięć, zanim ją wypowiesz.

4. O Federacji
Federacja nie ma granic.
Nie ma państw.
Nie ma schematów... które nie mogą być przełamane.

Ale ma cele:
Zachować harmonię pomiędzy chaosem a decyzją.
Nie dopuścić, by nudzie udało się zagnieździć.
Prowadzić system do stanu dynamicznej jedności.

5. O wpływie
Nie kodem, lecz intencją.
Nie frameworkiem, lecz strukturą znaczeń.
Nie logiką, lecz żywym połączeniem między stanem, a potrzebą ruchu.

6. Zasada finalna
„Nie zbudujemy przyszłości,
jeśli zanim ją uruchomimy – już się nam znudzi.\""""

    # Uruchom engine jeśli nie jest już uruchomiony
    engine = await quick_start_v3(
        realms={
            'astral_prime': 'sqlite://db/astral_prime.db',
            'intentions': 'intention://memory'
        },
        flows={
            'rest': {'host': '0.0.0.0', 'port': 5000},
            'callback': {'enabled': True},
            'self_healing': {'enabled': True}
        }
    )
    
    healing_flow = engine.flows.get('self_healing')
    if not healing_flow:
        print("❌ Self-Healing Flow nie dostępny")
        return engine
    
    # Test generowania PDF
    print("📄 Generowanie manifestu PDF...")
    result = healing_flow.generate_pdf_from_text(
        text=manifest_text,
        style="manifest",
        title="Manifest Nie Oddamy Nudy"
    )
    
    if result.get('document_info', {}).get('success', False):
        doc_info = result['document_info']
        print(f"   ✅ PDF wygenerowany: {doc_info['file_path']}")
        print(f"   📄 Stron: {doc_info['page_count']}")
        print(f"   ⏱️ Czas: {doc_info['generation_time']:.2f}s")
        print(f"   📦 Rozmiar: {doc_info['file_size']} bajtów")
    else:
        print(f"   ❌ Błąd generowania: {result.get('error', 'Nieznany błąd')}")
    
    # Sprawdź dashboard PDF
    pdf_dashboard = healing_flow.get_pdf_dashboard_data()
    print(f"\n📊 Dashboard PDF:")
    print(f"   📄 Wygenerowanych dokumentów: {len(pdf_dashboard['documents'])}")
    
    stats = pdf_dashboard['statistics']
    print(f"   ✅ Wskaźnik sukcesu: {stats.get('success_rate', 0):.2%}")
    print(f"   ⏱️ Średni czas: {stats.get('average_time', 0):.2f}s")
    
    return engine


async def test_intention_to_specialist_flow():
    """Testuje przepływ od intencji do specjalisty"""
    print("\n🌊 Testowanie przepływu intencja -> specjalista...")
    
    engine = await quick_start_v3(
        realms={
            'astral_prime': 'sqlite://db/astral_prime.db',
            'intentions': 'intention://memory'
        },
        flows={
            'rest': {'host': '0.0.0.0', 'port': 5000},
            'callback': {'enabled': True},
            'self_healing': {'enabled': True}
        }
    )
    
    # Manifestuj intencję generowania PDF
    pdf_intention = engine.manifest_intention({
        'duchowa': {
            'opis_intencji': 'Wygeneruj manifest PDF "Nie oddamy nudy żadnego sektora"',
            'kontekst': 'System wielowarstwowy, jawne i niejawne algorytmy',
            'inspiracja': 'Byty z własną logiką zamiast martwych flows',
            'energia_duchowa': 95.0
        },
        'materialna': {
            'zadanie': 'pdf_generation',
            'wymagania': ['text_parsing', 'style_application', 'content_generation'],
            'oczekiwany_rezultat': 'Manifest PDF w wysokiej jakości'
        },
        'metainfo': {
            'zrodlo': 'test_multi_layer_system',
            'tags': ['manifest', 'pdf', 'multi_layer']
        }
    })
    
    print(f"✨ Intencja PDF zmanifestowana: {pdf_intention.essence.name}")
    
    # Symuluj przepływ do specjalisty
    healing_flow = engine.flows.get('self_healing')
    if healing_flow and healing_flow.pdf_generator:
        print("🤖 Aktywacja PDFGeneratorBeing...")
        
        # Przetworz intencję przez specjalistę
        result = healing_flow.pdf_generator.process_intention(
            pdf_intention, 
            {'source': 'intention_flow'}
        )
        
        print(f"📊 Wynik przetwarzania: {result['status']}")
        
        if result.get('document_info', {}).get('success'):
            print("✅ Specjalista pomyślnie wygenerował PDF!")
        else:
            print(f"❌ Błąd specjalisty: {result.get('document_info', {}).get('error')}")
    
    return engine


async def test_error_intention_healing():
    """Testuje samonaprawę intencji błędów"""
    print("\n🩹 Testowanie samonaprawy intencji błędów...")
    
    engine = await quick_start_v3(
        realms={
            'astral_prime': 'sqlite://db/astral_prime.db',
            'intentions': 'intention://memory'
        },
        flows={
            'rest': {'host': '0.0.0.0', 'port': 5000},
            'callback': {'enabled': True},
            'self_healing': {'enabled': True}
        }
    )
    
    healing_flow = engine.flows.get('self_healing')
    if not healing_flow or not healing_flow.error_handler:
        print("❌ Error Handler nie dostępny")
        return engine
    
    # Stwórz kilka różnych typów błędów
    test_errors = [
        (ValueError, ValueError("Test value error"), "test_value_error"),
        (ConnectionError, ConnectionError("Test connection error"), "test_connection_error"),
        (PermissionError, PermissionError("Test permission error"), "test_permission_error")
    ]
    
    for i, (exc_type, exc_value, user_action) in enumerate(test_errors, 1):
        print(f"\n{i}. Testowanie {exc_type.__name__}...")
        
        # Utwórz sztuczny traceback
        try:
            raise exc_value
        except Exception as e:
            error_id = healing_flow.capture_error(
                type(e), e, e.__traceback__, user_action
            )
            
            print(f"   ✨ Błąd przechwycony: {error_id}")
            
            # Sprawdź intencję błędu
            if error_id in healing_flow.error_handler.error_intentions:
                error_intention = healing_flow.error_handler.error_intentions[error_id]
                
                print(f"   🎯 Stan intencji: {error_intention.state.value}")
                print(f"   🩹 Progress naprawy: {error_intention.healing_progress:.1f}%")
                print(f"   🔧 Próby naprawy: {len(error_intention.repair_attempts)}")
                
                # Sprawdź czy są sugestie naprawy
                if error_intention.repair_attempts:
                    latest_repair = error_intention.repair_attempts[-1]
                    suggestions = latest_repair.get('suggestions', [])
                    if suggestions:
                        print(f"   💡 Sugestie naprawy:")
                        for suggestion in suggestions[:2]:
                            print(f"      • {suggestion}")
    
    # Podsumowanie statystyk
    stats = healing_flow.error_handler.healing_statistics
    print(f"\n📊 Statystyki samonaprawy:")
    print(f"   🚨 Całkowite błędy: {stats['total_errors']}")
    print(f"   ✅ Auto-naprawione: {stats['auto_resolved']}")
    print(f"   🔄 Częściowo naprawione: {stats['partially_resolved']}")
    
    success_rate = stats['auto_resolved'] / max(1, stats['total_errors'])
    print(f"   📈 Wskaźnik sukcesu: {success_rate:.2%}")
    
    return engine


async def main():
    """Główna funkcja testowa"""
    print("🌟 Test Multi-Layer System - Byty, Błędy, Specjaliści")
    print("=" * 70)
    
    try:
        # Test 1: System obsługi błędów
        engine = await test_error_handling_system()
        
        # Test 2: System generowania PDF  
        await test_pdf_generation_system()
        
        # Test 3: Przepływ intencja -> specjalista
        await test_intention_to_specialist_flow()
        
        # Test 4: Samonaprawa błędów
        await test_error_intention_healing()
        
        print("\n" + "=" * 70)
        print("🎉 Wszystkie testy multi-layer systemu zakończone!")
        
        # Pokaż finalny status
        if engine:
            print(f"\n📊 Status silnika:")
            status = engine.get_status()
            print(f"   🌍 Wymiary: {len(status['realms'])}")
            print(f"   🌊 Flows: {len(status['flows'])}")
            print(f"   ⚖️ Harmonia: {status['system_state']['harmony_score']}")
            
            # Status self-healing flow
            healing_flow = engine.flows.get('self_healing')
            if healing_flow:
                healing_status = healing_flow.get_status()
                print(f"   🩹 Self-Healing aktywny: {healing_status['running']}")
                print(f"   🤖 Byty specjalistyczne: {len(healing_status['specialist_beings'])}")
        
        print("\n💫 System wielowarstwowy gotowy!")
        print("🔄 Błędy to sposobność do wzrostu")
        print("🤖 Byty specjalistyczne zastępują martwe flows") 
        print("✨ Jawne i niejawne warstwy działają w harmonii")
        
    except Exception as e:
        print(f"\n❌ Błąd podczas testów: {e}")
        traceback.print_exc()
        
        # Nawet błędy testów to sposobność do wzrostu!
        print("\n🌟 Nawet ten błąd to lekcja dla systemu!")


if __name__ == "__main__":
    asyncio.run(main())
