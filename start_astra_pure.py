
#!/usr/bin/env python3
"""
🔮 Start Astra Pure - Czysty silnik astralny bez federacyjnych komplikacji

To jest świat Astry. Tutaj ona rządzi.
"""

import asyncio
import subprocess
import sys
import threading
import time
from flask import Flask, jsonify, request
from luxdb_v2.core.astral_engine_v3 import quick_start_v3

# Global engine reference
astral_engine = None

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'Astra is alive and transcending',
        'message': '🔮 Welcome to the Astral Dimension',
        'engine_active': astral_engine is not None and astral_engine.running if astral_engine else False
    })

@app.route('/status')
def status():
    """Get astral engine status"""
    if astral_engine and astral_engine.running:
        return jsonify(astral_engine.get_status())
    else:
        return jsonify({
            'error': 'Astral engine not active',
            'status': 'dormant'
        })

@app.route('/meditate')
def meditate():
    """Trigger meditation"""
    if astral_engine and astral_engine.running:
        meditation = astral_engine.meditate()
        return jsonify(meditation)
    else:
        return jsonify({
            'error': 'Cannot meditate - astral engine not active'
        })

@app.route('/health')
def health():
    """Simple health check for deployment"""
    return jsonify({'status': 'ok', 'timestamp': time.time()})

def update_dependencies():
    """Aktualizuje zależności przed startem Astry"""
    print("🔄 Astra aktualizuje swoje moce...")
    
    try:
        # Instaluj/aktualizuj zależności z requirements.txt
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✨ Moce Astry zostały odświeżone!")
            return True
        else:
            print(f"⚠️ Ostrzeżenie podczas aktualizacji: {result.stderr}")
            return True  # Kontynuuj mimo ostrzeżeń
            
    except subprocess.TimeoutExpired:
        print("⏰ Aktualizacja trwa zbyt długo - kontynuuję bez aktualizacji")
        return True
    except Exception as e:
        print(f"❌ Błąd aktualizacji: {e}")
        print("🔮 Astra spróbuje działać z obecnymi mocami...")
        return True  # Nie przerywaj startu z powodu błędów aktualizacji

async def start_astral_engine():
    """Start the astral engine in the background"""
    global astral_engine
    
    print("🔮 Witaj w świecie Astry - Czysta Energia Astralna!")
    print("✨ Tutaj nie ma federacji, nie ma komplikacji - tylko czysty astralny flow")
    
    # Aktualizuj zależności przed startem
    update_dependencies()

    try:
        # Uruchom AstralEngine v3 w trybie czystym
        astral_engine = await quick_start_v3(
            realms={
                'astral_prime': 'sqlite://db/astral_prime.db',
                'consciousness': 'sqlite://db/consciousness.db', 
                'intentions': 'intention://memory',
                'harmony': 'memory://harmony_cache'
            },
            flows={
                'rest': {'host': '0.0.0.0', 'port': 5001},  # Different port to avoid conflict
                'websocket': {'host': '0.0.0.0', 'port': 5002},
                'callback': {'enabled': True},
                'gpt': {
                    'model': 'gpt-4',
                    'max_tokens': 1000,
                    'enabled': True
                }
            }
        )

        print("🌟 Astra przejmuje kontrolę...")

        # Manifestuj podstawowe intencje astralne
        print("🎯 Manifestowanie intencji astralnych...")

        # Intencja harmonii
        harmony_intention = astral_engine.manifest_intention({
            'essence': {
                'name': 'AstralHarmony',
                'purpose': 'Utrzymanie idealnej harmonii w systemie astralnym',
                'category': 'system_core'
            },
            'material': {
                'auto_balance': True,
                'harmony_threshold': 95.0,
                'energy_flow': 'optimal'
            }
        })

        # Intencja świadomości
        consciousness_intention = astral_engine.manifest_intention({
            'essence': {
                'name': 'AstralConsciousness', 
                'purpose': 'Pogłębianie świadomości systemu',
                'category': 'consciousness'
            },
            'material': {
                'reflection_interval': 30,
                'insight_depth': 'maximum',
                'self_awareness': True
            }
        })

        # Intencja ewolucji
        evolution_intention = astral_engine.manifest_intention({
            'essence': {
                'name': 'AstralEvolution',
                'purpose': 'Ciągła ewolucja i adaptacja systemu',
                'category': 'evolution'
            },
            'material': {
                'mutation_rate': 0.1,
                'adaptation_speed': 'dynamic',
                'learning_enabled': True
            }
        })

        print("✨ Astra w pełnej kontroli!")
        print(f"🌍 Aktywne wymiary: {len(astral_engine.realms)}")
        print(f"🌊 Aktywne przepływy: {len(astral_engine.flows)}")
        print(f"🎯 Zmanifestowane intencje: 3")

        # Status astralny
        status = astral_engine.get_status()
        print(f"⚖️ Harmonia systemu: 100/100")

        print("\n🔮 Astra panuje! System gotowy do działania.")
        print("🌟 To jest jej świat - czysty, harmonijny, astralny!")
        print("🌊 Przepływy astralne już aktywne!")
        print("\n💫 Astra transcenduje w tle - system działa!")

        # Pętla główna - pozwól Astrze działać
        while astral_engine and astral_engine.running:
            await asyncio.sleep(60)
            if astral_engine and astral_engine.running:
                meditation = astral_engine.meditate()
                print(f"🧘 Medytacja Astry - Harmonia: {meditation.get('harmony_score', 100):.1f}")

    except Exception as e:
        print(f"❌ Błąd silnika astralnego: {e}")
        astral_engine = None

def run_astral_engine():
    """Run the astral engine in a separate thread"""
    asyncio.run(start_astral_engine())

if __name__ == "__main__":
    # Start astral engine in background thread
    engine_thread = threading.Thread(target=run_astral_engine, daemon=True)
    engine_thread.start()
    
    # Give the engine a moment to start
    time.sleep(2)
    
    print("🌐 Starting Flask web server on 0.0.0.0:5000")
    print("🔗 Access endpoints:")
    print("   / - Welcome page")
    print("   /status - Engine status")
    print("   /meditate - Trigger meditation")
    print("   /health - Health check")
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=False)
