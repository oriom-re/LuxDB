
#!/usr/bin/env python3
"""
🤖 Przykłady użycia GPT Flow i Function Generator

Demonstruje komunikację z Astrą przez AI i system generowania funkcji
"""

import json
from luxdb_v2 import create_astral_app


def demonstrate_gpt_communication():
    """Demonstracja komunikacji z Astrą przez GPT"""
    print("🤖 Przykład komunikacji z Astrą przez GPT")
    print("=" * 60)
    
    # Konfiguracja z GPT (wymaga OPENAI_API_KEY w środowisku)
    config = {
        'realms': {
            'primary': 'sqlite://db/primary.db',
            'functions': 'sqlite://db/functions.db'
        },
        'flows': {
            'rest': {'port': 5000, 'host': '0.0.0.0'},
            'gpt': {
                'model': 'gpt-4',
                'max_tokens': 1000
            }
        },
        'consciousness_level': 'development'
    }
    
    # Utwórz aplikację astralną
    with create_astral_app(config) as engine:
        print("🔮 System astralny przebudzony z GPT Flow")
        
        # Sprawdź czy GPT jest dostępny
        if engine.gpt_flow:
            print("\n💬 Przykładowe rozmowy z Astrą:")
            
            # Przykład 1: Proste pytanie o status
            response1 = engine.gpt_flow.chat_with_astra(
                "Jaki jest stan systemu astralnego?",
                "demo_user"
            )
            print(f"Użytkownik: Jaki jest stan systemu astralnego?")
            print(f"Astra: {response1.get('astra_response', 'Brak odpowiedzi')}")
            
            # Przykład 2: Żądanie medytacji
            response2 = engine.gpt_flow.chat_with_astra(
                "Przeprowadź medytację systemu i powiedz mi o stanie harmonii",
                "demo_user"
            )
            print(f"\nUżytkownik: Przeprowadź medytację systemu")
            print(f"Astra: {response2.get('astra_response', 'Brak odpowiedzi')}")
            
            # Przykład 3: Tworzenie funkcji
            response3 = engine.gpt_flow.chat_with_astra(
                "Stwórz funkcję do obliczania podatku VAT",
                "demo_user"
            )
            print(f"\nUżytkownik: Stwórz funkcję do obliczania VAT")
            print(f"Astra: {response3.get('astra_response', 'Brak odpowiedzi')}")
            
            # Pokaż status GPT
            gpt_status = engine.gpt_flow.get_status()
            print(f"\n📊 Status GPT Flow:")
            print(f"   🗣️ Rozmowy: {gpt_status['conversations_count']}")
            print(f"   🎯 Tokeny użyte: {gpt_status['total_tokens_used']}")
            
        else:
            print("⚠️ GPT Flow nie jest aktywny (brak klucza OpenAI API)")


def demonstrate_function_generator():
    """Demonstracja systemu generowania funkcji"""
    print("\n🛠️ Przykład systemu generowania funkcji")
    print("=" * 60)
    
    config = {
        'realms': {
            'primary': 'sqlite://db/primary.db',
            'functions': 'sqlite://db/functions.db'
        },
        'flows': {
            'rest': {'port': 5000, 'host': '0.0.0.0'}
        },
        'consciousness_level': 'development'
    }
    
    with create_astral_app(config) as engine:
        if engine.function_generator:
            print("🔮 Function Generator aktywny")
            
            # Przykład 1: Prosta funkcja matematyczna
            math_spec = {
                'name': 'calculate_circle_area',
                'description': 'Oblicza pole powierzchni koła',
                'category': 'mathematics',
                'parameters': [
                    {'name': 'radius', 'type': 'float', 'description': 'Promień koła'}
                ],
                'return_type': 'Dict[str, Any]',
                'tags': ['geometry', 'math', 'circle']
            }
            
            result1 = engine.function_generator.create_function(math_spec)
            print(f"\n🎯 Utworzono funkcję matematyczną:")
            print(f"   Nazwa: {result1.get('function_name')}")
            print(f"   Status: {'✅' if result1.get('success') else '❌'}")
            
            if result1.get('success'):
                # Wywołaj funkcję
                invoke_result = engine.function_generator.invoke_function(
                    'calculate_circle_area', 
                    {'radius': 5.0}
                )
                print(f"   Wynik dla promienia 5.0: {invoke_result.get('result')}")
            
            # Przykład 2: Funkcja API
            api_spec = {
                'name': 'fetch_weather_data',
                'description': 'Pobiera dane pogodowe z API',
                'category': 'api',
                'parameters': [
                    {'name': 'city', 'type': 'str', 'description': 'Nazwa miasta'},
                    {'name': 'api_key', 'type': 'str', 'description': 'Klucz API', 'default': 'demo_key'}
                ],
                'return_type': 'Dict[str, Any]',
                'tags': ['weather', 'api', 'external']
            }
            
            result2 = engine.function_generator.create_function(api_spec)
            print(f"\n🌐 Utworzono funkcję API:")
            print(f"   Nazwa: {result2.get('function_name')}")
            print(f"   Status: {'✅' if result2.get('success') else '❌'}")
            
            # Przykład 3: Funkcja z własnym kodem
            custom_spec = {
                'name': 'generate_password',
                'description': 'Generuje bezpieczne hasło',
                'category': 'security',
                'parameters': [
                    {'name': 'length', 'type': 'int', 'default': 12},
                    {'name': 'include_symbols', 'type': 'bool', 'default': True}
                ],
                'code_template': '''
import random
import string
from typing import Dict, Any

def generate_password(length: int = 12, include_symbols: bool = True) -> Dict[str, Any]:
    """
    Generuje bezpieczne hasło
    
    Funkcja wygenerowana przez Function Generator
    """
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%^&*"
    
    password = ''.join(random.choice(chars) for _ in range(length))
    
    return {
        'success': True,
        'password': password,
        'length': len(password),
        'has_symbols': include_symbols,
        'strength': 'strong' if length >= 12 else 'medium'
    }
'''
            }
            
            result3 = engine.function_generator.create_function(custom_spec)
            print(f"\n🔐 Utworzono funkcję z kodem:")
            print(f"   Nazwa: {result3.get('function_name')}")
            print(f"   Status: {'✅' if result3.get('success') else '❌'}")
            
            if result3.get('success'):
                # Wywołaj funkcję generowania hasła
                password_result = engine.function_generator.invoke_function(
                    'generate_password',
                    {'length': 16, 'include_symbols': True}
                )
                print(f"   Wygenerowane hasło: {password_result.get('result', {}).get('password', 'N/A')}")
            
            # Lista wszystkich funkcji
            functions_list = engine.function_generator.list_functions()
            print(f"\n📋 Lista wszystkich funkcji ({len(functions_list)}):")
            for func in functions_list:
                print(f"   • {func['name']} ({func['category']}) - wykonano {func['execution_count']} razy")
            
            # Status generatora
            gen_status = engine.function_generator.get_status()
            print(f"\n📊 Status Function Generator:")
            print(f"   🏗️ Utworzono funkcji: {gen_status['functions_created']}")
            print(f"   ⚡ Wykonano funkcji: {gen_status['functions_executed']}")
            print(f"   💾 W cache: {gen_status['functions_in_cache']}")
            
        else:
            print("⚠️ Function Generator nie jest aktywny")


def demonstrate_integrated_workflow():
    """Demonstracja zintegrowanego workflow GPT + Functions"""
    print("\n🌟 Przykład zintegrowanego workflow")
    print("=" * 60)
    
    config = {
        'realms': {
            'primary': 'sqlite://db/primary.db',
            'functions': 'sqlite://db/functions.db'
        },
        'flows': {
            'rest': {'port': 5000, 'host': '0.0.0.0'},
            'gpt': {'model': 'gpt-4', 'max_tokens': 1000}
        },
        'consciousness_level': 'development'
    }
    
    with create_astral_app(config) as engine:
        if engine.gpt_flow and engine.function_generator:
            print("🔮 Zintegrowany system GPT + Functions aktywny")
            
            # Astra tworzy funkcję na żądanie
            response = engine.gpt_flow.chat_with_astra(
                "Stwórz funkcję do konwersji temperatury z Celsjusza na Fahrenheita",
                "demo_user"
            )
            
            print(f"💬 Rozmowa z Astrą o tworzeniu funkcji:")
            print(f"Astra: {response.get('astra_response', 'Brak odpowiedzi')}")
            
            if response.get('success') and response.get('actions_executed', 0) > 0:
                print(f"✅ Wykonano {response['actions_executed']} akcji")
                for result in response.get('action_results', []):
                    if result.get('success'):
                        print(f"   • {result['action']}: {result.get('message', 'OK')}")
            
            # Pokaż końcowy status
            final_functions = engine.function_generator.list_functions()
            print(f"\n📋 Funkcje po sesji z Astrą: {len(final_functions)}")
            
        else:
            print("⚠️ Nie wszystkie systemy są aktywne")


if __name__ == "__main__":
    print("🌟 LuxDB v2 - GPT i Function Generator Examples")
    print("=" * 80)
    
    # Uwaga o konfiguracji
    print("ℹ️  Uwaga: Dla GPT Flow potrzebny jest klucz OpenAI API w zmiennej OPENAI_API_KEY")
    print()
    
    # Demonstracje
    demonstrate_function_generator()
    demonstrate_gpt_communication()
    demonstrate_integrated_workflow()
    
    print("\n✨ Przykłady zakończone!")
