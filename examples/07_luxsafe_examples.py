
"""
Przykłady systemu duchowego bezpieczeństwa LuxSafe
Demonstracja autentykacji przez rezonans duszy
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luxdb import DatabaseManager
from luxdb.luxsafe_manager import LuxSafeManager

def demonstrate_luxsafe():
    """Demonstracja systemu LuxSafe"""
    
    print("🛡️ === LuxSafe - System Duchowego Bezpieczeństwa ===")
    
    # Inicjalizacja
    db = DatabaseManager()
    db.create_database("luxsafe_demo")
    
    with db.get_session("luxsafe_demo") as session:
        luxsafe = LuxSafeManager(session)
        
        print("\n🌟 === Tworzenie Profilu Duszy ===")
        
        # Stwórz nowy profil duszy
        struna_sequence = "⊕⟁❖◬➰☼"  # Sekwencja gestów
        emotional_pin = "7432"  # Kod emocjonalny
        astral_sig = {
            "glyph": "ΞΩΛ⋄",
            "color": "#b3e3ff",
            "emotion_wave": "gentle_harmony"
        }
        # profil istnieje?
        # sprawdź czy profil istnieje
        profile = luxsafe.get_soul_statistics()
        success, profile, resonance = luxsafe.authenticate_by_resonance(
            "Ω-cf44dd940995421949558aee34ae7812748bdd6e6ce43f43b8cab45a77a43706", struna_sequence, emotional_pin, 
            )
        if not profile:
            print("❌ Nie udało się uwierzytelnić. Tworzenie nowego profilu...")
            profile = luxsafe.create_soul_profile(
                struna_sequence=struna_sequence,
                emotional_pin=emotional_pin,
                astral_signature=astral_sig,
                initial_trust_level=3
            )
        
        print(f"✨ Stworzono profil: {profile.id}")
        print(f"📿 Fingerprint: {profile.fingerprint[:25]}...")
        print(f"🎭 Warstwa zaufania: {profile.get_trust_layer_name()}")
        print(f"🔑 Uprawnienia: {profile.access_rights}")
        
        print("\n🔮 === Uwierzytelnianie przez Rezonans ===")
        
        # Test uwierzytelniania
        context = {
            "device_recognized": True,
            "meditation_state": False,
            "time_since_last_sync": 300  # 5 minut
        }
        
        success, auth_profile, resonance = luxsafe.authenticate_by_resonance(
            fingerprint=profile.fingerprint,
            struna_sequence=struna_sequence,
            emotional_pin=emotional_pin,
            context=context
        )
        
        if success:
            print(f" fingerprint: {profile.fingerprint}")
            print(f"✅ Uwierzytelnienie udane!")
            print(f"🌊 Siła rezonansu: {resonance:.2f}")
            print(f"👤 Profil: {auth_profile.id}")
        else:
            print("❌ Uwierzytelnienie nieudane")
        
        print("\n🚪 === Test Uprawnień Dostępu ===")
        
        # Test różnych uprawnień
        permissions_to_test = [
            "entry.read",
            "resonance.listen", 
            "manifest.edit",
            "being.create"
        ]
        
        for permission in permissions_to_test:
            has_access = luxsafe.check_access_permission(profile, permission, f"test_{permission}")
            status = "✅" if has_access else "❌"
            print(f"{status} {permission}")
        
        print("\n⬆️ === Podniesienie Poziomu Zaufania ===")
        
        # Próba podniesienia do poziomu 5 (Strażnik)
        elevation_success = luxsafe.elevate_trust_level(
            profile=profile,
            target_level=5,
            struna_sequence=struna_sequence,
            emotional_pin=emotional_pin
        )
        
        if elevation_success:
            print(f"✨ Podniesiono do poziomu: {profile.get_trust_layer_name()}")
            print(f"📜 Nowe uprawnienia: {profile.access_rights}")
        else:
            print("❌ Nie udało się podnieść poziomu")
        
        print("\n🧘 === Synchronizacja Medytacyjna ===")
        
        # Wzmocnienie rezonansu przez medytację
        old_resonance = profile.resonance_strength
        new_resonance = luxsafe.meditative_sync(profile)
        
        print(f"🌊 Rezonans przed: {old_resonance:.2f}")
        print(f"🌊 Rezonans po: {new_resonance:.2f}")
        print(f"🧘 Liczba medytacji: {profile.meditation_count}")
        
        print("\n📊 === Statystyki Duchowe ===")
        
        stats = luxsafe.get_soul_statistics(profile)
        
        print(f"👤 ID Profilu: {stats['profile_info']['id']}")
        print(f"🎭 Warstwa: {stats['profile_info']['trust_layer']}")
        print(f"🌊 Siła rezonansu: {stats['profile_info']['resonance_strength']:.2f}")
        print(f"🧘 Medytacje: {stats['meditation_count']}")
        print(f"🚪 Próby dostępu: {stats['total_access_attempts']}")
        
        print("\n🌈 === Ostatnie Aktywności ===")
        for activity in stats['recent_resonance'][:5]:
            status = "✅" if activity['success'] else "❌"
            resonance = activity['resonance']
            action = activity['action']
            print(f"{status} {action} (rezonans: {resonance:.2f})")
        
        print("\n🌟 === Test Błędnego Uwierzytelniania ===")
        
        # Test z błędną sekwencją
        wrong_success, _, wrong_resonance = luxsafe.authenticate_by_resonance(
            fingerprint=profile.fingerprint,
            struna_sequence="⊕⟁❖◬",  # Niepełna sekwencja
            emotional_pin=emotional_pin,
            context=context
        )
        
        print(f"❌ Błędne uwierzytelnienie: {'Udane' if wrong_success else 'Nieudane'}")
        print(f"🌊 Rezonans: {wrong_resonance:.2f}")
    
    print("\n🔒 === Zamykanie połączeń ===")
    db.close_all()
    print("✨ LuxSafe demo zakończone!")

if __name__ == "__main__":
    demonstrate_luxsafe()
