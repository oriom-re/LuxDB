#!/usr/bin/env python3
"""
🧬 Przykłady Systemu Genetycznej Identyfikacji LuxDB v2

Demonstruje zaawansowane śledzenie argumentów i dekoratory funkcji
z wykorzystaniem genetycznych sygnatur astralnych.
"""

import time
import random
from typing import Dict, Any, List

from luxdb_v2 import create_astral_app
from luxdb_v2.beings.genetic_identification import (
    genetic_trace, astral_signature, get_genetic_system,
    analyze_function_genetics, find_genetic_patterns
)


# Przykładowe funkcje z genetycznym śledzeniem
@genetic_trace(include_args=True, include_return=True, track_performance=True)
def process_astral_data(data_type: str, energy_level: float, consciousness: str) -> Dict[str, Any]:
    """Funkcja przetwarzająca astralne dane"""
    time.sleep(random.uniform(0.1, 0.5))  # Symuluj przetwarzanie

    processed_result = {
        'data_type': data_type,
        'energy_amplified': energy_level * 1.5,
        'consciousness_evolved': consciousness + "_enhanced",
        'processing_timestamp': time.time(),
        'astral_resonance': random.uniform(0.5, 1.0)
    }

    return processed_result


@astral_signature('spell_name', 'power_level')
@genetic_trace(include_args=True, include_return=True)
def cast_astral_spell(spell_name: str, power_level: int, target: str = "self", 
                     components: List[str] = None) -> Dict[str, Any]:
    """Rzucanie astralnych zaklęć z genetycznym śledzeniem"""
    components = components or []

    spell_result = {
        'spell_cast': spell_name,
        'power_used': power_level,
        'target_affected': target,
        'components_consumed': len(components),
        'success_rate': min(0.95, power_level / 100),
        'magical_residue': f"essence_of_{spell_name.lower()}"
    }

    time.sleep(0.2)  # Symuluj czas rzucania
    return spell_result


@genetic_trace(track_performance=True)
def meditate_with_crystals(crystal_types: List[str], meditation_duration: int) -> Dict[str, Any]:
    """Medytacja z kryształami"""
    total_energy = sum(len(crystal) * 10 for crystal in crystal_types)

    time.sleep(meditation_duration * 0.1)  # Symuluj medytację

    return {
        'crystals_used': crystal_types,
        'duration_minutes': meditation_duration,
        'energy_generated': total_energy,
        'insights_gained': random.randint(1, 5),
        'astral_clarity': min(100, total_energy / len(crystal_types)) if crystal_types else 0
    }


def demonstrate_basic_genetic_tracking():
    """Podstawowa demonstracja genetycznego śledzenia"""
    print("🧬 Przykład 1: Podstawowe śledzenie genetyczne")
    print("=" * 60)

    # Różne wywołania tej samej funkcji
    test_calls = [
        ("light_essence", 75.0, "awakened"),
        ("dark_matter", 50.0, "enlightened"),
        ("void_energy", 100.0, "transcendent"),
        ("light_essence", 80.0, "awakened"),  # Podobne do pierwszego
        ("crystal_resonance", 65.0, "aware")
    ]

    print("🔮 Wykonywanie serii wywołań z genetycznym śledzeniem...")
    results = []

    for data_type, energy, consciousness in test_calls:
        result = process_astral_data(data_type, energy, consciousness)
        results.append(result)
        print(f"   ✨ Przetworzono: {data_type} (energia: {energy}, świadomość: {consciousness})")

    # Analiza genetyki funkcji
    print(f"\n📊 Analiza genetyczna funkcji 'process_astral_data':")
    genetics = analyze_function_genetics('process_astral_data')
    for key, value in genetics.items():
        print(f"   {key}: {value}")


def demonstrate_astral_signatures():
    """Demonstracja astralnych sygnatur"""
    print("\n🌟 Przykład 2: Astralne sygnatury")
    print("=" * 60)

    spells = [
        ("Fireball", 80, "enemy", ["sulfur", "ruby_dust"]),
        ("Healing_Light", 60, "ally", ["moonstone", "silver_thread"]),
        ("Shield_of_Stars", 90, "self", ["obsidian", "star_metal"]),
        ("Fireball", 85, "enemy", ["sulfur", "phoenix_feather"]),  # Podobne zaklęcie
        ("Teleport", 70, "self", ["amethyst"])
    ]

    print("⚡ Rzucanie zaklęć z astralnymi sygnaturami...")
    for spell_name, power, target, components in spells:
        result = cast_astral_spell(spell_name, power, target, components)
        print(f"   🔥 Rzucono: {spell_name} (moc: {power}, cel: {target})")
        if hasattr(result, '__astral_signature__'):
            print(f"      🌌 Sygnatura astralna: {result.__astral_signature__}")

    # Znajdź wzorce genetyczne
    print(f"\n🔍 Wyszukiwanie wzorców genetycznych:")
    patterns = find_genetic_patterns('cast_astral_spell', 0.6)
    print(f"   Znalezionych wzorców: {patterns['patterns_found']}")
    print(f"   Przeanalizowanych wywołań: {patterns['total_calls_analyzed']}")


def demonstrate_meditation_genetics():
    """Demonstracja genetyki medytacji"""
    print("\n🧘 Przykład 3: Genetyka medytacji")
    print("=" * 60)

    meditation_sessions = [
        (["amethyst", "quartz"], 15),
        (["obsidian", "tourmaline", "labradorite"], 30),
        (["selenite"], 10),
        (["amethyst", "quartz", "citrine"], 20),  # Podobna sesja
        (["moonstone", "rose_quartz"], 25)
    ]

    print("🕯️ Przeprowadzanie sesji medytacyjnych...")
    for crystals, duration in meditation_sessions:
        result = meditate_with_crystals(crystals, duration)
        print(f"   🔮 Medytacja z {crystals} przez {duration} minut")
        print(f"      Energia: {result['energy_generated']}, Jasność: {result['astral_clarity']:.1f}")


def demonstrate_being_genetics():
    """Demonstracja genetyki bytów astralnych"""
    print("\n🌟 Przykład 4: Genetyka bytów astralnych")
    print("=" * 60)

    config = {
        'realms': {
            'genetic_realm': 'memory://genetic_testing'
        }
    }

    with create_astral_app(config) as engine:
        realm = engine.get_realm('genetic_realm')

        print("🌍 Manifestowanie bytów z genetycznym śledzeniem...")

        # Utwórz różne byty
        beings_data = [
            {'name': 'Alpha_Guardian', 'energy_level': 95, 'type': 'guardian'},
            {'name': 'Beta_Healer', 'energy_level': 70, 'type': 'healer'},
            {'name': 'Gamma_Warrior', 'energy_level': 85, 'type': 'warrior'},
            {'name': 'Delta_Guardian', 'energy_level': 90, 'type': 'guardian'},  # Podobny do Alpha
        ]

        beings = []
        for being_data in beings_data:
            being = realm.manifest(being_data)
            beings.append(being)
            print(f"   ✨ Zmanifestowano: {being_data['name']}")

        print(f"\n🧘 Medytacja wszystkich bytów...")
        for being in beings:
            print(f" type: {type(being)}")
            if hasattr(being, 'meditate'):
                meditation_result = being.meditate()
                print(f"   🌟 {being.essence.name}: energia {being.essence.energy_level}")

        print(f"\n🔄 Ewolucja bytów...")
        evolution_changes = [
            ({'skill_points': 10, 'experience': 100}, 0),
            ({'magic_resistance': 25, 'experience': 50}, 1),
            ({'attack_power': 15, 'experience': 75}, 2),
            ({'skill_points': 12, 'experience': 120}, 3),  # Podobna ewolucja
        ]

        for changes, being_idx in evolution_changes:
            if being_idx < len(beings):
                beings[being_idx].evolve(changes)
                print(f"   🔄 Ewoluował: {beings[being_idx].essence.name}")


def demonstrate_genetic_analysis():
    """Demonstracja analizy genetycznej systemu"""
    print("\n📊 Przykład 5: Analiza genetyczna systemu")
    print("=" * 60)

    genetic_system = get_genetic_system()

    print("🔬 Ogólne statystyki genetyczne:")
    print(f"   Zarejestrowanych genomów funkcji: {len(genetic_system.genome_registry)}")
    print(f"   Śledzonych rodowodów argumentów: {len(genetic_system.argument_lineage)}")
    print(f"   Funkcji z sygnaturami: {len(genetic_system.function_signatures)}")

    print(f"\n🧬 Analiza poszczególnych funkcji:")
    tracked_functions = set()
    for genome in genetic_system.genome_registry.values():
        tracked_functions.add(genome.function_name)

    for func_name in tracked_functions:
        stats = analyze_function_genetics(func_name)
        print(f"   📈 {func_name}:")
        print(f"      Wywołania: {stats.get('total_calls', 0)}")
        print(f"      Unikalne sygnatury: {stats.get('unique_signatures', 0)}")
        if stats.get('avg_execution_time'):
            print(f"      Średni czas wykonania: {stats['avg_execution_time']:.4f}s")

    print(f"\n🔍 Wzorce genetyczne:")
    for func_name in tracked_functions:
        patterns = find_genetic_patterns(func_name, 0.7)
        if patterns['patterns_found'] > 0:
            print(f"   🌌 {func_name}: {patterns['patterns_found']} wzorców w {patterns['total_calls_analyzed']} wywołaniach")


def demonstrate_engine_genetic_insights():
    """Demonstracja insights genetycznych z AstralEngine"""
    print("\n🎯 Przykład 6: Insights genetyczne AstralEngine")
    print("=" * 60)

    config = {
        'realms': {
            'insight_realm': 'memory://soul_dimension'
        }
    }

    with create_astral_app(config) as engine:
        realm = engine.get_realm('insight_realm')

        # Wykonaj różne operacje dla zbierania danych genetycznych
        for i in range(5):
            being_data = {
                'name': f'TestBeing_{i}',
                'energy_level': random.randint(50, 100),
                'type': random.choice(['warrior', 'mage', 'healer'])
            }
            being = realm.manifest(being_data)
            if hasattr(being, 'meditate'):
                being.meditate()
            if i % 2 == 0:
                being.evolve({'experience': random.randint(10, 50)})

        # Wykonaj medytację na wszystkich aktywnych bytach
        for being in realm.manifestation.active_beings.values():
            if hasattr(being, 'meditate'):
                being.meditate()

        # Pobierz insights genetyczne
        print("🧠 Pobieranie insights genetycznych z AstralEngine...")
        insights = engine.get_genetic_insights()

        print(f"   🌟 Wynik zdrowia genetycznego: {insights.get('genetic_health_score', 0):.2f}")

        if insights.get('insights'):
            print(f"   📊 Znalezione insights:")
            for insight in insights['insights']:
                print(f"      - {insight['function']}: różnorodność {insight['genetic_diversity']:.2f}")

        if insights.get('recommendations'):
            print(f"   💡 Rekomendacje:")
            for rec in insights['recommendations']:
                print(f"      - {rec}")


def main():
    """Główna funkcja demonstracyjna"""
    print("🧬✨ DEMONSTRACJA SYSTEMU GENETYCZNEJ IDENTYFIKACJI LuxDB v2 ✨🧬")
    print("=" * 80)

    try:
        # demonstrate_basic_genetic_tracking()
        # demonstrate_astral_signatures()
        # demonstrate_meditation_genetics()
        # demonstrate_being_genetics()
        # demonstrate_genetic_analysis()
        demonstrate_engine_genetic_insights()

        print(f"\n🌟 Wszystkie demonstracje zakończone pomyślnie!")
        print("🧬 System genetycznej identyfikacji działa w pełnej harmonii ✨")

    except Exception as e:
        print(f"❌ Błąd podczas demonstracji: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()