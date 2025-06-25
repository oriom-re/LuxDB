
#!/usr/bin/env python3
"""
🔮 Przykłady użycia Astral Containers

Demonstruje przepływ danych między funkcjami przez astralne kontenery
z automatycznym logowaniem i analizą przez Astrę.

Filozofia: Każda funkcja = jedna mała operacja + przekazanie kontenera dalej
"""

import json
from luxdb_v2 import create_astral_app, print_astral_banner


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
        
        # Wykonaj każdą funkcję, loguj błędy, ale kontynuuj
        for func_name, params in micro_functions:
            print(f"\n🔧 Wywołanie: {func_name}")
            
            result = engine.invoke_function_with_container(func_name, container, params)
            
            if result['success']:
                print(f"   ✅ Sukces: {result.get('result', {})}")
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
