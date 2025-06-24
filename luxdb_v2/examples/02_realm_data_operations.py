
#!/usr/bin/env python3
"""
🌌 LuxDB v2 - Operacje na danych w wymiarach

Demonstruje manifestowanie, kontemplację i ewolucję bytów
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Dodaj ścieżkę do LuxDB v2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from luxdb_v2 import create_astral_app, print_astral_banner


def example_being_manifestation():
    """Przykład manifestowania bytów w wymiarach"""
    print("✨ Przykład 1: Manifestowanie bytów")
    print("=" * 50)
    
    config = {
        'realms': {
            'souls': 'memory://soul_dimension',
            'artifacts': 'memory://artifact_dimension'
        }
    }
    
    with create_astral_app(config) as engine:
        # Pobierz wymiar dusz
        soul_realm = engine.get_realm('souls')
        
        print("🌟 Manifestowanie dusz w wymiarze...")
        
        # Manifestuj dusze
        souls_data = [
            {
                'soul_name': 'Guardian_of_Light',
                'energy_level': 100,
                'abilities': ['healing', 'protection', 'wisdom'],
                'realm_of_origin': 'celestial',
                'manifestation_time': datetime.now().isoformat()
            },
            {
                'soul_name': 'Shadow_Walker',
                'energy_level': 85,
                'abilities': ['stealth', 'shadow_manipulation', 'intuition'],
                'realm_of_origin': 'umbral',
                'manifestation_time': datetime.now().isoformat()
            },
            {
                'soul_name': 'Cosmic_Sage',
                'energy_level': 120,
                'abilities': ['cosmic_knowledge', 'telepathy', 'time_perception'],
                'realm_of_origin': 'astral',
                'manifestation_time': datetime.now().isoformat()
            }
        ]
        
        manifested_beings = []
        for soul_data in souls_data:
            try:
                being = soul_realm.manifest(soul_data)
                manifested_beings.append(being)
                print(f"   ✨ Manifestowano: {soul_data['soul_name']}")
            except Exception as e:
                print(f"   ❌ Błąd manifestacji {soul_data['soul_name']}: {e}")
        
        print(f"\n📊 Zmanifestowano {len(manifested_beings)} bytów")
        print(f"🌌 Liczba bytów w wymiarze: {soul_realm.count_beings()}")
        
        time.sleep(1)
    
    print("🕊️ Wymiar dusz transcended\n")


def example_being_contemplation():
    """Przykład kontemplacji (wyszukiwania) bytów"""
    print("🔍 Przykład 2: Kontemplacja bytów")
    print("=" * 50)
    
    config = {
        'realms': {
            'library': 'memory://knowledge_library'
        }
    }
    
    with create_astral_app(config) as engine:
        library_realm = engine.get_realm('library')
        
        print("📚 Tworzenie biblioteki wiedzy astralnej...")
        
        # Manifestuj księgi wiedzy
        books_data = [
            {
                'title': 'Chronicles of Astral Harmony',
                'author': 'Ancient Sage',
                'category': 'philosophy',
                'power_level': 'legendary',
                'pages': 777,
                'created_at': datetime.now() - timedelta(days=1000)
            },
            {
                'title': 'Secrets of Dimensional Travel',
                'author': 'Void Walker',
                'category': 'magic',
                'power_level': 'epic',
                'pages': 333,
                'created_at': datetime.now() - timedelta(days=500)
            },
            {
                'title': 'Meditation Techniques for Cosmic Consciousness',
                'author': 'Enlightened Master',
                'category': 'philosophy',
                'power_level': 'rare',
                'pages': 108,
                'created_at': datetime.now() - timedelta(days=100)
            },
            {
                'title': 'Combat Magic of the Seven Realms',
                'author': 'Battle Mage Supreme',
                'category': 'magic',
                'power_level': 'legendary',
                'pages': 666,
                'created_at': datetime.now() - timedelta(days=750)
            }
        ]
        
        # Manifestuj księgi
        for book in books_data:
            library_realm.manifest(book)
            print(f"   📖 Dodano: {book['title']}")
        
        print(f"\n🔍 Kontemplacja biblioteki...")
        
        # Przykłady kontemplacji
        contemplations = [
            {
                'intention': 'find_philosophy_books',
                'description': 'Wyszukaj księgi filozoficzne',
                'conditions': {'category': 'philosophy'}
            },
            {
                'intention': 'find_legendary_tomes',
                'description': 'Wyszukaj legendarne tomy',
                'conditions': {'power_level': 'legendary'}
            },
            {
                'intention': 'find_ancient_knowledge',
                'description': 'Wyszukaj starożytną wiedzę (>500 dni)',
                'conditions': {'min_age_days': 500}
            }
        ]
        
        for contemplation in contemplations:
            print(f"\n   🧘 {contemplation['description']}:")
            try:
                results = library_realm.contemplate(
                    contemplation['intention'],
                    **contemplation['conditions']
                )
                
                print(f"   📋 Znaleziono: {len(results)} wyników")
                for result in results[:2]:  # Pokaż max 2 wyniki
                    if hasattr(result, 'get'):
                        title = result.get('title', 'Unknown')
                        author = result.get('author', 'Unknown')
                        print(f"      • {title} - {author}")
                
            except Exception as e:
                print(f"   ❌ Błąd kontemplacji: {e}")
        
        time.sleep(1)
    
    print("🕊️ Biblioteka wiedzy transcended\n")


def example_being_evolution():
    """Przykład ewolucji (aktualizacji) bytów"""
    print("🔄 Przykład 3: Ewolucja bytów")
    print("=" * 50)
    
    config = {
        'realms': {
            'heroes': 'memory://hero_realm'
        }
    }
    
    with create_astral_app(config) as engine:
        hero_realm = engine.get_realm('heroes')
        
        print("🦸 Manifestowanie bohaterów...")
        
        # Początkowi bohaterowie
        heroes_data = [
            {
                'hero_id': 'hero_001',
                'name': 'Astral Knight',
                'level': 1,
                'experience': 0,
                'skills': ['sword_mastery'],
                'equipment': ['iron_sword', 'leather_armor'],
                'location': 'starting_village'
            },
            {
                'hero_id': 'hero_002', 
                'name': 'Mystic Healer',
                'level': 1,
                'experience': 0,
                'skills': ['basic_healing'],
                'equipment': ['wooden_staff', 'cloth_robe'],
                'location': 'starting_village'
            }
        ]
        
        # Manifestuj bohaterów
        for hero_data in heroes_data:
            hero_realm.manifest(hero_data)
            print(f"   🦸 Manifestowano: {hero_data['name']}")
        
        print(f"\n⚡ Symulacja przygód i ewolucji...")
        
        # Ewolucje bohaterów
        evolutions = [
            {
                'hero_id': 'hero_001',
                'evolution_type': 'level_up',
                'changes': {
                    'level': 5,
                    'experience': 1500,
                    'skills': ['sword_mastery', 'battle_tactics', 'leadership'],
                    'equipment': ['silver_sword', 'chain_armor', 'magic_shield'],
                    'location': 'mystic_forest'
                }
            },
            {
                'hero_id': 'hero_002',
                'evolution_type': 'skill_evolution',
                'changes': {
                    'level': 3,
                    'experience': 800,
                    'skills': ['basic_healing', 'advanced_healing', 'purification'],
                    'equipment': ['crystal_staff', 'blessed_robe', 'healing_amulet'],
                    'location': 'sacred_temple'
                }
            }
        ]
        
        for evolution in evolutions:
            print(f"\n   ⚡ Ewolucja bohatera {evolution['hero_id']}:")
            print(f"      Typ: {evolution['evolution_type']}")
            
            try:
                evolved_hero = hero_realm.evolve(
                    evolution['hero_id'],
                    evolution['changes']
                )
                
                print(f"      ✅ Ewolucja zakończona pomyślnie")
                if hasattr(evolved_hero, 'get'):
                    new_level = evolved_hero.get('level', 'unknown')
                    new_location = evolved_hero.get('location', 'unknown')
                    print(f"      📊 Nowy poziom: {new_level}")
                    print(f"      📍 Nowa lokacja: {new_location}")
                
            except Exception as e:
                print(f"      ❌ Błąd ewolucji: {e}")
        
        # Kontemplacja po ewolucji
        print(f"\n🔍 Kontemplacja rozwiniętych bohaterów...")
        try:
            advanced_heroes = hero_realm.contemplate(
                'find_advanced_heroes',
                min_level=3
            )
            print(f"📋 Bohaterowie 3+ poziom: {len(advanced_heroes)}")
        except Exception as e:
            print(f"❌ Błąd kontemplacji: {e}")
        
        time.sleep(1)
    
    print("🕊️ Królestwo bohaterów transcended\n")


def example_multi_realm_operations():
    """Przykład operacji na wielu wymiarach"""
    print("🌌 Przykład 4: Operacje wielowymiarowe")
    print("=" * 50)
    
    config = {
        'realms': {
            'users': 'memory://user_realm',
            'sessions': 'memory://session_realm',
            'logs': 'memory://log_realm'
        }
    }
    
    with create_astral_app(config) as engine:
        print("🏗️ Tworzenie systemu wielowymiarowego...")
        
        user_realm = engine.get_realm('users')
        session_realm = engine.get_realm('sessions')
        log_realm = engine.get_realm('logs')
        
        # Manifestuj użytkowników
        users = [
            {'user_id': 'u001', 'username': 'astral_wanderer', 'email': 'wanderer@astral.dev'},
            {'user_id': 'u002', 'username': 'cosmic_sage', 'email': 'sage@cosmic.dev'},
            {'user_id': 'u003', 'username': 'shadow_walker', 'email': 'walker@shadow.dev'}
        ]
        
        print("👥 Manifestowanie użytkowników...")
        for user in users:
            user_realm.manifest(user)
            print(f"   👤 {user['username']}")
        
        # Manifestuj sesje
        sessions = [
            {'session_id': 's001', 'user_id': 'u001', 'created_at': datetime.now(), 'active': True},
            {'session_id': 's002', 'user_id': 'u002', 'created_at': datetime.now(), 'active': True},
            {'session_id': 's003', 'user_id': 'u001', 'created_at': datetime.now() - timedelta(hours=2), 'active': False}
        ]
        
        print("\n🔐 Manifestowanie sesji...")
        for session in sessions:
            session_realm.manifest(session)
            status = "aktywna" if session['active'] else "nieaktywna"
            print(f"   🔑 {session['session_id']} ({status})")
        
        # Manifestuj logi
        logs = [
            {'log_id': 'l001', 'user_id': 'u001', 'action': 'login', 'timestamp': datetime.now()},
            {'log_id': 'l002', 'user_id': 'u002', 'action': 'login', 'timestamp': datetime.now()},
            {'log_id': 'l003', 'user_id': 'u001', 'action': 'data_query', 'timestamp': datetime.now()},
            {'log_id': 'l004', 'user_id': 'u003', 'action': 'failed_login', 'timestamp': datetime.now()}
        ]
        
        print("\n📊 Manifestowanie logów...")
        for log in logs:
            log_realm.manifest(log)
            print(f"   📝 {log['action']} - {log['user_id']}")
        
        # Statystyki systemowe
        print(f"\n📈 Statystyki systemu:")
        print(f"   👥 Użytkownicy: {user_realm.count_beings()}")
        print(f"   🔐 Sesje: {session_realm.count_beings()}")
        print(f"   📊 Logi: {log_realm.count_beings()}")
        
        # Kontemplacja międzywymiarowa
        print(f"\n🔍 Analiza międzywymiarowa...")
        try:
            active_sessions = session_realm.contemplate('find_active_sessions', active=True)
            print(f"   ✅ Aktywne sesje: {len(active_sessions)}")
            
            recent_logins = log_realm.contemplate('find_logins', action='login')
            print(f"   🔐 Niedawne logowania: {len(recent_logins)}")
            
        except Exception as e:
            print(f"   ❌ Błąd analizy: {e}")
        
        time.sleep(1)
    
    print("🕊️ System wielowymiarowy transcended\n")


def run_data_examples():
    """Uruchamia wszystkie przykłady operacji na danych"""
    print_astral_banner()
    print("🌌 Przykłady operacji na danych w wymiarach LuxDB v2")
    print("=" * 60)
    
    examples = [
        example_being_manifestation,
        example_being_contemplation,
        example_being_evolution,
        example_multi_realm_operations
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            print(f"\n{'='*20} PRZYKŁAD {i}/{len(examples)} {'='*20}")
            example()
        except Exception as e:
            print(f"❌ Błąd w przykładzie {i}: {e}")
            continue
    
    print("\n" + "="*60)
    print("🌟 Wszystkie przykłady operacji na danych zakończone!")
    print("✨ Niech dane płyną w harmonii astralnej!")


if __name__ == "__main__":
    run_data_examples()
