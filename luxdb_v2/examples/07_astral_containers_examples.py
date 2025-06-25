
#!/usr/bin/env python3
"""
🔮 Przykłady użycia Astral Containers

Demonstruje przepływ danych między funkcjami przez astralne kontenery
z historią, walidacją i inteligentnym zarządzaniem.
"""

import json
from luxdb_v2 import create_astral_app

def demonstrate_astral_containers():
    """Demonstruje system kontenerów astralnych"""
    
    print("🔮 === Przykłady Astral Containers ===")
    
    # Utwórz system astralny
    with create_astral_app() as engine:
        
        # === 1. Tworzenie kontenera astralnego ===
        print("\n1. 🌟 Tworzenie kontenera astralnego")
        
        container = engine.create_astral_container(
            initial_data={
                'user_id': 'user_123',
                'operation': 'process_data',
                'input_values': [1, 2, 3, 4, 5]
            },
            origin_function='user_input',
            purpose='data_processing_pipeline'
        )
        
        print(f"   ✨ Utworzono kontener: {container.container_id}")
        print(f"   📊 Stan początkowy: {container.state.value}")
        print(f"   🗂️ Dane: {container.current_data}")
        
        # === 2. Utworzenie funkcji dla przykładu ===
        print("\n2. 🛠️ Tworzenie funkcji dla pipeline")
        
        # Funkcja walidująca
        validator_spec = {
            'name': 'validate_input',
            'description': 'Waliduje dane wejściowe',
            'parameters': [
                {'name': 'input_values', 'type': 'list', 'required': True},
                {'name': 'user_id', 'type': 'str', 'required': True}
            ],
            'category': 'validator'
        }
        
        engine.function_generator.create_function(validator_spec)
        
        # Funkcja przetwarzająca
        processor_spec = {
            'name': 'process_numbers',
            'description': 'Przetwarza liczby i oblicza statystyki',
            'parameters': [
                {'name': 'input_values', 'type': 'list', 'required': True}
            ],
            'category': 'calculator'
        }
        
        engine.function_generator.create_function(processor_spec)
        
        # Funkcja formatująca wynik
        formatter_spec = {
            'name': 'format_results',
            'description': 'Formatuje wyniki do prezentacji',
            'parameters': [
                {'name': 'calculation_result', 'type': 'dict'},
                {'name': 'user_id', 'type': 'str'}
            ],
            'category': 'formatter'
        }
        
        engine.function_generator.create_function(formatter_spec)
        
        print("   ✅ Utworzono funkcje dla pipeline")
        
        # === 3. Pipeline z kontenerami ===
        print("\n3. 🌊 Wykonywanie pipeline z kontenerami")
        
        # Krok 1: Walidacja
        print("   📋 Krok 1: Walidacja danych")
        
        result1 = engine.invoke_function_with_container(
            'validate_input', 
            container,
            expected_params={
                'input_values': {'type': 'list', 'required': True},
                'user_id': {'type': 'str', 'required': True}
            }
        )
        
        print(f"      Wynik walidacji: {result1['success']}")
        if result1['success']:
            print(f"      Stan kontenera: {container.state.value}")
        
        # Krok 2: Przetwarzanie
        print("   ⚙️ Krok 2: Przetwarzanie danych")
        
        result2 = engine.invoke_function_with_container(
            'process_numbers',
            container,
            expected_params={
                'input_values': {'type': 'list', 'required': True}
            }
        )
        
        print(f"      Wynik przetwarzania: {result2['success']}")
        if result2['success']:
            print(f"      Obliczenia: {result2['result'].get('calculation_result', {})}")
        
        # Krok 3: Formatowanie
        print("   🎨 Krok 3: Formatowanie wyników")
        
        result3 = engine.invoke_function_with_container(
            'format_results',
            container,
            expected_params={
                'calculation_result': {'type': 'dict'},
                'user_id': {'type': 'str'}
            }
        )
        
        print(f"      Wynik formatowania: {result3['success']}")
        if result3['success']:
            print(f"      Format: {result3['result'].get('formatted_data', {})}")
        
        # === 4. Historia kontenera ===
        print("\n4. 📜 Historia kontenera")
        
        history = container.get_full_history()
        print(f"   🔄 Liczba przejść: {len(history['history'])}")
        print(f"   ✅ Walidacje: {len(history['validation_stack'])}")
        print(f"   📊 Transformacje: {history['statistics']['transformation_count']}")
        
        print("\n   📋 Ostatnie przejścia:")
        for transition in history['history'][-3:]:
            print(f"      {transition['function_name']}: {transition['from_state']} → {transition['to_state']}")
        
        # === 5. Język astralny ===
        print("\n5. ✨ Eksport do języka astralnego")
        
        astral_language = container.to_astral_language()
        print("   🔮 Kontener w języku astralnym:")
        print(astral_language[:300] + "..." if len(astral_language) > 300 else astral_language)
        
        # === 6. Automatyczne generowanie brakujących funkcji ===
        print("\n6. 🤖 Test automatycznego generowania funkcji")
        
        # Spróbuj wywołać nieistniejącą funkcję
        result_auto = engine.invoke_function_with_container(
            'nonexistent_analyzer',
            container,
            expected_params={
                'data': {'type': 'dict', 'required': True}
            }
        )
        
        print(f"   📝 Automatyczne generowanie: {result_auto['success']}")
        if result_auto['success']:
            print(f"   ✨ Funkcja została wygenerowana i wykonana!")
        else:
            print(f"   ❌ Błąd: {result_auto.get('error', 'Nieznany błąd')}")
        
        # === 7. Statystyki kontenerów ===
        print("\n7. 📊 Statystyki systemu kontenerów")
        
        stats = engine.get_container_statistics()
        print(f"   📦 Utworzone kontenery: {stats['total_containers']}")
        print(f"   🔄 Aktywne kontenery: {stats['active_containers']}")
        print(f"   ✅ Zakończone: {stats['completed_containers']}")
        print(f"   🎯 Wskaźnik sukcesu: {stats['success_rate']:.1f}%")
        print(f"   🔧 Auto-korekcje: {stats['auto_corrections']}")
        
        # === 8. Test powrotu do poprzedniej funkcji ===
        print("\n8. 🔄 Test mechanizmu powrotu do poprawy")
        
        # Utwórz kontener z błędnymi danymi
        bad_container = engine.create_astral_container(
            initial_data={'incomplete_data': True},
            origin_function='test_origin'
        )
        
        # Spróbuj wywołać funkcję z wymaganiami
        bad_result = engine.invoke_function_with_container(
            'validate_input',
            bad_container,
            expected_params={
                'input_values': {'type': 'list', 'required': True},
                'user_id': {'type': 'str', 'required': True}
            }
        )
        
        print(f"   ❌ Walidacja z błędnymi danymi: {bad_result['success']}")
        if not bad_result['success']:
            print(f"   💡 Sugestie: {bad_result.get('suggestions', [])}")
            print(f"   🔄 Stan kontenera: {bad_container.state.value}")

def demonstrate_container_language():
    """Demonstruje język astralny kontenerów"""
    
    print("\n🌟 === Język Astralny Kontenerów ===")
    
    with create_astral_app() as engine:
        
        # Utwórz kontener z przykładowymi danymi
        container = engine.create_astral_container({
            'message': 'Hello from astral realm',
            'timestamp': '2024-01-01T00:00:00Z',
            'data': [1, 2, 3, 4, 5]
        })
        
        # Wykonaj kilka operacji
        container.set_target('example_function')
        container.transition_to(container.state.__class__.FLOWING, 'test_function')
        
        # Eksportuj do języka astralnego
        astral_text = container.to_astral_language()
        print("📝 Kontener w języku astralnym:")
        print(astral_text)
        
        # Import z języka astralnego
        print("\n🔄 Odtwarzanie kontenera z języka astralnego:")
        
        from luxdb_v2.wisdom.astral_containers import AstralDataContainer
        restored_container = AstralDataContainer.from_astral_language(astral_text)
        
        print(f"   ✨ Odtworzony kontener: {restored_container.container_id}")
        print(f"   📊 Stan: {restored_container.state.value}")
        print(f"   🗂️ Dane: {restored_container.current_data}")

if __name__ == "__main__":
    demonstrate_astral_containers()
    demonstrate_container_language()
