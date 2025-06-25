
#!/usr/bin/env python3
"""
🔮 Przykłady użycia Astral Containers

Demonstruje przepływ danych między funkcjami przez astralne kontenery
z automatycznym logowaniem i analizą przez Astrę.

Filozofia: Każda funkcja = jedna mała operacja + przekazanie kontenera dalej
"""

import json
import time
from luxdb_v2 import create_astral_app, print_astral_banner
from luxdb_v2.wisdom.astral_containers import ContainerState


def demonstrate_micro_function_flow():
    """Demonstruje przepływ przez mikro-funkcje"""
    
    print("\n🔮 === Przepływ Mikro-Funkcji ===")
    
    with create_astral_app() as engine:
        
        # Utwórz kontener z początkowymi danymi
        container = engine.create_astral_container({
            'user_input': 'Hello World',
            'timestamp': '2024-01-01T12:00:00Z'
        }, origin_function='user_interface', purpose='text_processing')
        
        print(f"📦 Utworzono kontener: {container.container_id}")
        
        # FUNKCJA 1: Walidacja inputu
        print("\n🔍 Funkcja 1: Walidacja inputu")
        result1 = engine.invoke_function_with_container('validate_input', container, {
            'user_input': {'type': 'str', 'required': True}
        })
        
        if result1['success']:
            print(f"   ✅ Walidacja OK: {result1.get('result', {})}")
        else:
            print(f"   ⚠️ Błąd zalogowany: {result1.get('error', 'Unknown')}")
        
        # FUNKCJA 2: Normalizacja tekstu
        print("\n🔤 Funkcja 2: Normalizacja tekstu")
        result2 = engine.invoke_function_with_container('normalize_text', container, {
            'user_input': {'type': 'str', 'required': True}
        })
        
        if result2['success']:
            print(f"   ✅ Normalizacja OK: {result2.get('result', {})}")
        else:
            print(f"   ⚠️ Błąd zalogowany: {result2.get('error', 'Unknown')}")
        
        # FUNKCJA 3: Analiza sentymentu
        print("\n😊 Funkcja 3: Analiza sentymentu")
        result3 = engine.invoke_function_with_container('analyze_sentiment', container, {
            'normalized_text': {'type': 'str', 'required': True}
        })
        
        if result3['success']:
            print(f"   ✅ Analiza OK: {result3.get('result', {})}")
        else:
            print(f"   ⚠️ Błąd zalogowany: {result3.get('error', 'Unknown')}")
        
        # FUNKCJA 4: Zapisz wyniki
        print("\n💾 Funkcja 4: Zapisz wyniki")
        result4 = engine.invoke_function_with_container('save_results', container, {
            'sentiment_score': {'type': 'float', 'required': False},
            'processed_text': {'type': 'str', 'required': False}
        })
        
        if result4['success']:
            print(f"   ✅ Zapis OK: {result4.get('result', {})}")
        else:
            print(f"   ⚠️ Błąd zalogowany: {result4.get('error', 'Unknown')}")
        
        # Pokaż końcowy stan kontenera
        print(f"\n📊 Historia kontenera:")
        history = container.get_history_summary()
        print(f"   🔄 Liczba przejść: {history['transitions_count']}")
        print(f"   ✅ Walidacje: {history['validation_count']}")
        print(f"   🔧 Transformacje: {history['transformation_count']}")
        print(f"   ❌ Błędy: {history['error_count']}")
        
        # Wyślij do analizy astralnej (jeśli są błędy)
        if history['error_count'] > 0:
            print(f"\n🌟 Wysyłanie kontenera do analizy astralnej...")
            astral_analysis = engine.consciousness.analyze_container_errors(container)
            print(f"   🧠 Rekomendacje: {astral_analysis.get('recommendations', [])}")


def demonstrate_error_logging_flow():
    """Demonstruje automatyczne logowanie błędów w kontenerze"""
    
    print("\n⚠️ === Przepływ z Logowaniem Błędów ===")
    
    with create_astral_app() as engine:
        
        # Kontener z danymi które mogą powodować błędy
        container = engine.create_astral_container({
            'number_text': 'not_a_number',
            'divide_by': 0,
            'missing_required_field': None
        }, origin_function='error_demo', purpose='error_handling_demo')
        
        print(f"📦 Kontener testowy: {container.container_id}")
        
        # Lista mikro-funkcji do wykonania
        micro_functions = [
            ('parse_number', {'number_text': {'type': 'str', 'required': True}}),
            ('validate_divisor', {'divide_by': {'type': 'int', 'required': True}}),
            ('perform_division', {'number': {'type': 'float', 'required': True}, 'divisor': {'type': 'int', 'required': True}}),
            ('format_result', {'division_result': {'type': 'float', 'required': False}})
        ]
        
        # Wykonaj każdą funkcję, loguj błędy i uruchamiaj diagnostykę
        for func_name, params in micro_functions:
            print(f"\n🔧 Wywołanie: {func_name}")
            
            result = engine.invoke_function_with_container(func_name, container, params)
            
            if result['success']:
                print(f"   ✅ Sukces: {result.get('result', 'Brak rezultatu')}")
            else:
                print(f"   ❌ Błąd: {result.get('error', 'Nieznany błąd')}")
                
                # Sprawdź czy diagnostyka została uruchomiona
                if result.get('diagnostic_triggered'):
                    print(f"   🔬 Diagnostyka uruchomiona automatycznie")
                    print(f"   ⏳ Kontener oczekuje na poprawkę...")
                    
                    # Poczekaj chwilę na diagnostykę (w prawdziwej aplikacji byłoby to asynchroniczne)
                    time.sleep(1)
                    
                    # Sprawdź stan kontenera po diagnostyce
                    updated_container = engine.get_astral_container(container.container_id)
                    if updated_container:
                        latest_transition = updated_container.history[-1] if updated_container.history else None
                        if latest_transition and latest_transition.transformation.get('fix_applied'):
                            print(f"   🔧 Poprawka zastosowana automatycznie!")
                            print(f"   📋 Typ poprawki: {latest_transition.transformation.get('fix_type', 'unknown')}")
                        else:
                            print(f"   ⚠️ Poprawka jeszcze nie gotowa")
                else:
                    print(f"   ⚠️ Diagnostyka nie została uruchomiona")
            
            # Pokaż aktualny stan kontenera
            print(f"   🔮 Stan kontenera: {container.state.value}")
            
            # Dodatkowo, sprawdź logi błędów
            error_transitions = [t for t in container.history if t.to_state == ContainerState.ERROR]
            if error_transitions:
                latest_error = error_transitions[-1]
                if latest_error.error_info:
                    print(f"   📝 Ostatni błąd: {latest_error.error_info.get('error', 'Brak szczegółów')}")


def demonstrate_auto_healing_system():
    """Demonstruje system samo-naprawczy kontenerów"""
    
    print("\n🩹 === System Automatycznej Naprawy ===")
    
    with create_astral_app() as engine:
        print("🔧 Konfiguracja systemu diagnostycznego...")
        
        # Sprawdź czy callback flow jest aktywny
        if not engine.callback_flow:
            print("   ⚠️ Callback Flow nie jest dostępny")
            return
        
        if not engine.callback_flow.is_running():
            engine.callback_flow.start()
            print("   ✅ Callback Flow uruchomiony")
        
        # Kontener z danymi które gwarantowane wywołają błędy
        problematic_container = engine.create_astral_container({
            'text_number': 'definitely_not_a_number',
            'zero_divisor': 0,
            'missing_key_dict': {'other_key': 'value'},
            'invalid_type': 'should_be_list'
        }, origin_function='auto_healing_demo', purpose='self_healing_test')
        
        print(f"📦 Problematyczny kontener: {problematic_container.container_id}")
        
        # Lista funkcji które będą wywoływały różne typy błędów
        problematic_functions = [
            ('convert_to_integer', {'text_number': {'type': 'int', 'required': True}}),
            ('safe_division', {'number': {'type': 'float', 'required': True}, 'zero_divisor': {'type': 'float', 'required': True}}),
            ('access_specific_key', {'missing_key_dict': {'type': 'dict', 'required': True}}),
            ('process_list_data', {'invalid_type': {'type': 'list', 'required': True}})
        ]
        
        print("\n🔬 Test systemu auto-naprawy:")
        
        for func_name, expected_params in problematic_functions:
            print(f"\n   🧪 Test funkcji: {func_name}")
            
            # Pierwsze wywołanie - spodziewamy się błędu
            result = engine.invoke_function_with_container(func_name, problematic_container, expected_params)
            
            if result.get('diagnostic_triggered'):
                print(f"      🔬 Diagnostyka uruchomiona")
                print(f"      ⏱️ Oczekiwanie na automatyczną poprawkę...")
                
                # W prawdziwej aplikacji czekalibyśmy na callback
                # Tutaj symulujemy czas potrzebny na analizę
                time.sleep(2)
                
                # Sprawdź czy poprawka została zastosowana
                callback_stats = engine.callback_flow.get_namespace_stats('diagnostics')
                recent_events = callback_stats.get('recent_events', [])
                
                fix_events = [e for e in recent_events if e['event_type'] == 'fix_ready']
                if fix_events:
                    print(f"      ✅ Poprawka wygenerowana przez system diagnostyczny")
                    
                    # Spróbuj ponownie po poprawce
                    retry_result = engine.invoke_function_with_container(func_name, problematic_container, expected_params)
                    if retry_result.get('success'):
                        print(f"      🎉 Funkcja działa po automatycznej naprawie!")
                        print(f"      📊 Wynik: {retry_result.get('result', 'Brak wyniku')}")
                    else:
                        print(f"      ⚠️ Funkcja nadal nie działa: {retry_result.get('error')}")
                else:
                    print(f"      ⏳ Poprawka jeszcze nie gotowa")
            else:
                print(f"      ❌ Diagnostyka nie została uruchomiona")
            
            print(f"      📈 Aktualne błędy kontenera: {problematic_container.error_count}")
            print(f"      🔄 Transformacje: {problematic_container.transformation_count}")
        
        # Podsumowanie
        print(f"\n📊 Podsumowanie auto-naprawy:")
        container_history = problematic_container.get_history_summary()
        print(f"   🔢 Łączne błędy: {container_history['error_count']}")
        print(f"   🔄 Transformacje: {container_history['transformation_count']}")
        print(f"   ✅ Walidacje: {container_history['validation_count']}")
        
        # Statystyki systemu diagnostycznego
        diagnostic_stats = engine.callback_flow.get_namespace_stats('diagnostics')
        print(f"   🔬 Wydarzenia diagnostyczne: {diagnostic_stats.get('event_history_count', 0)}")
        print(f"   🛠️ Callbacki diagnostyczne: {diagnostic_stats.get('total_callbacks', 0)}")


def demonstrate_container_evolution():
    """Demonstruje ewolucję kontenera przez błędy i naprawy"""
    
    print("\n🦋 === Ewolucja Kontenera ===")
    
    with create_astral_app() as engine:
        
        # Kontener który będzie ewoluował
        evolving_container = engine.create_astral_container({
            'raw_data': 'messy,data;with:different|separators',
            'config': {'strict_mode': True}
        })
        
        print(f"📦 Kontener ewolucyjny: {evolving_container.container_id}")
        
        # Sekwencja funkcji które wymuszą ewolucję
        evolution_steps = [
            ('parse_simple_csv', {'raw_data': {'type': 'str', 'required': True}}),
            ('handle_multiple_separators', {'raw_data': {'type': 'str', 'required': True}}),
            ('smart_data_parser', {'raw_data': {'type': 'str', 'required': True}, 'config': {'type': 'dict', 'required': False}}),
            ('adaptive_parser', {'raw_data': {'type': 'str', 'required': True}})
        ]
        
        print("\n🔄 Kroki ewolucji:")
        
        for i, (func_name, params) in enumerate(evolution_steps, 1):
            print(f"\n   Krok {i}: {func_name}")
            
            result = engine.invoke_function_with_container(func_name, evolving_container, params)
            
            if result['success']:
                print(f"      ✅ Sukces na pierwszej próbie")
            else:
                print(f"      ❌ Błąd: {result.get('error')}")
                
                if result.get('diagnostic_triggered'):
                    print(f"      🔬 Ewolucja w toku przez diagnostykę...")
                    time.sleep(1)  # Symulacja czasu analizy
                    
                    # Sprawdź historię kontnerów pod kątem ewolucji
                    evolution_history = [t for t in evolving_container.history 
                                       if t.transformation and t.transformation.get('fix_applied')]
                    
                    if evolution_history:
                        latest_evolution = evolution_history[-1]
                        print(f"      🦋 Ewolucja zastosowana: {latest_evolution.transformation.get('fix_type')}")
                    else:
                        print(f"      ⏳ Ewolucja jeszcze nie zakończona")
            
            # Pokaż stan ewolucji
            print(f"      📊 Stan: {evolving_container.state.value}")
            print(f"      🧬 Transformacje: {evolving_container.transformation_count}")
            print(f"      🔄 Przejścia: {len(evolving_container.history)}")
        
        # Finalny stan ewolucji
        final_history = evolving_container.get_full_history()
        print(f"\n🎯 Finalna ewolucja kontenera:")
        print(f"   ⚖️ Stosunek sukces/błąd: {(final_history['statistics']['transformation_count'] - final_history['statistics']['error_count'])}/{final_history['statistics']['error_count']}")
        print(f"   🧠 Poziom adaptacji: {(final_history['statistics']['validation_count'] / max(len(final_history['history']), 1)):.1%}")
        
        # Analiza astry (jeśli dostępna)
        if hasattr(engine, 'consciousness'):
            astral_analysis = engine.consciousness.reflect()
            print(f"   🔮 Analiza Astry:")
            print(f"      🌊 Harmonia systemu: {astral_analysis['harmony'].get('energy_flow_balance', 'unknown')}")
            print(f"      🧠 Rekomendacje: {astral_analysis.get('recommendations', [])}") Sukces: {result.get('result', {})}")
            else:
                # Błąd został zalogowany do kontenera - nie przerywamy
                print(f"   📝 Błąd zalogowany, kontynuujemy...")
                
                # Dodaj informację o błędzie do kontenera
                container.current_data[f'{func_name}_error'] = {
                    'error': result.get('error', 'Unknown error'),
                    'timestamp': container.get_history_summary()['transitions_count']
                }
        
        print(f"\n📋 Podsumowanie błędów w kontenerze:")
        error_fields = [k for k in container.current_data.keys() if k.endswith('_error')]
        for error_field in error_fields:
            error_info = container.current_data[error_field]
            print(f"   ❌ {error_field}: {error_info['error']}")
        
        # Teraz wyślij cały kontener do analizy
        print(f"\n🌟 Analiza astralna kontenera z błędami:")
        if hasattr(engine.consciousness, 'analyze_error_patterns'):
            analysis = engine.consciousness.analyze_error_patterns(container)
            print(f"   🔍 Wzorce błędów: {len(analysis.get('patterns', []))}")
            print(f"   💡 Sugerowane poprawki: {len(analysis.get('suggestions', []))}")


def demonstrate_container_evolution():
    """Demonstruje ewolucję kontenera przez cały pipeline"""
    
    print("\n🌱 === Ewolucja Kontenera ===")
    
    with create_astral_app() as engine:
        
        # Początkowy kontener
        container = engine.create_astral_container({
            'raw_data': [1, 2, 3, 4, 5, 'invalid', 7, 8, 9]
        }, origin_function='data_pipeline', purpose='data_cleaning_and_analysis')
        
        print(f"📦 Kontener początkowy: {container.container_id}")
        print(f"   📊 Dane wejściowe: {container.current_data['raw_data']}")
        
        # Pipeline obróbki danych - każda funkcja robi jedną rzecz
        pipeline = [
            'clean_data',           # Usuwa invalid values
            'calculate_statistics', # Oblicza podstawowe statystyki
            'detect_outliers',      # Wykrywa wartości odstające
            'normalize_values',     # Normalizuje dane
            'generate_summary'      # Generuje podsumowanie
        ]
        
        # Wykonaj każdy krok pipeline'u
        for step_name in pipeline:
            print(f"\n🔄 Krok: {step_name}")
            
            # Pokaż stan kontenera przed krokiem
            data_keys = list(container.current_data.keys())
            print(f"   📂 Klucze przed: {data_keys}")
            
            # Wykonaj krok
            result = engine.invoke_function_with_container(step_name, container)
            
            if result['success']:
                # Pokaż nowe klucze po kroku
                new_keys = [k for k in container.current_data.keys() if k not in data_keys]
                if new_keys:
                    print(f"   ➕ Dodano: {new_keys}")
                print(f"   ✅ Krok zakończony pomyślnie")
            else:
                print(f"   ⚠️ Błąd w kroku - kontynuujemy z logiem")
        
        # Pokaż końcową ewolucję
        print(f"\n🎯 Finalna ewolucja kontenera:")
        final_keys = list(container.current_data.keys())
        for key in final_keys:
            if key != 'raw_data':  # Pokaż wszystko oprócz danych wejściowych
                value = container.current_data[key]
                if isinstance(value, dict) and 'error' in value:
                    print(f"   ❌ {key}: BŁĄD - {value['error']}")
                else:
                    print(f"   ✅ {key}: {str(value)[:50]}...")
        
        # Historia transformacji
        history = container.get_history_summary()
        print(f"\n📈 Statystyki ewolucji:")
        print(f"   🔄 Transformacje: {history['transformation_count']}")
        print(f"   ✅ Walidacje: {history['validation_count']}")
        print(f"   ❌ Błędy: {history['error_count']}")
        print(f"   📊 Skuteczność: {((history['transformation_count'] - history['error_count']) / max(history['transformation_count'], 1) * 100):.1f}%")


def demonstrate_astral_language():
    """Demonstruje zapis i odczyt języka astralnego"""
    
    print("\n🌟 === Język Astralny Kontenerów ===")
    
    with create_astral_app() as engine:
        
        # Utwórz kontener i przepuść przez kilka funkcji
        container = engine.create_astral_container({
            'message': 'Astral message',
            'priority': 'high',
            'timestamp': '2024-01-01T00:00:00Z'
        })
        
        # Wykonaj kilka operacji dla historii
        engine.invoke_function_with_container('validate_message', container)
        engine.invoke_function_with_container('process_priority', container)
        engine.invoke_function_with_container('enrich_metadata', container)
        
        # Eksportuj do języka astralnego
        astral_text = container.to_astral_language()
        print("📝 Kontener w języku astralnym:")
        print(astral_text[:300] + "..." if len(astral_text) > 300 else astral_text)
        
        # Import z języka astralnego
        print("\n🔄 Odtwarzanie z języka astralnego:")
        
        from luxdb_v2.wisdom.astral_containers import AstralDataContainer
        restored_container = AstralDataContainer.from_astral_language(astral_text)
        
        print(f"   ✨ Odtworzony kontener: {restored_container.container_id}")
        print(f"   📊 Stan: {restored_container.state.value}")
        print(f"   🔄 Historia: {len(restored_container.history)} przejść")
        print(f"   📂 Dane: {list(restored_container.current_data.keys())}")


def main():
    """Główna funkcja demonstracyjna"""
    
    print_astral_banner()
    print("🔮 Astral Containers - Przepływ Mikro-Funkcji")
    print("=" * 60)
    
    demos = [
        demonstrate_micro_function_flow,
        demonstrate_error_logging_flow,
        demonstrate_auto_healing_system,
        demonstrate_container_evolution,
        demonstrate_astral_language
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"\n{'='*20} DEMO {i}/{len(demos)} {'='*20}")
        try:
            demo()
        except Exception as e:
            print(f"❌ Błąd w demo: {e}")
    
    print("\n" + "="*60)
    print("🌟 Filozofia Astral Containers:")
    print("   • Każda funkcja = jedna mała operacja")
    print("   • Błędy logujemy, ale nie przerywamy przepływu")
    print("   • Kontener ewoluuje przez każdą funkcję")
    print("   • Astra analizuje całą historię na końcu")
    print("🔮 Mikrooperacje tworzą potężny przepływ!")


if __name__ == "__main__":
    main()
