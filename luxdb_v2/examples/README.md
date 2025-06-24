
# 🌟 LuxDB v2 - Przykłady użycia

Witaj w astralnej bibliotece przykładów LuxDB v2! Te przykłady demonstrują pełnię możliwości nowej generacji biblioteki danych, która łączy technologię z duchowością.

## 🚀 Jak uruchamiać przykłady

Każdy przykład można uruchomić bezpośrednio:

```bash
cd luxdb_v2/examples/
python 01_basic_astral_setup.py
python 02_realm_data_operations.py
python 03_service_integration_tests.py
python 04_migration_compatibility_tests.py
```

## 📁 Struktura przykładów

### 🔮 01_basic_astral_setup.py
**Podstawowe użycie LuxDB v2**
- Inicjalizacja systemu astralnego
- Operacje na wymiarach (realms)
- Monitorowanie świadomości
- System harmonii
- Integracja z serwisem

**Przykłady:**
```python
# Szybkie uruchomienie
with quick_start(realm_type='memory', port=5050) as engine:
    meditation = engine.meditate()
    print(f"Harmonia: {meditation['harmony_score']:.1f}/100")
```

### 🌌 02_realm_data_operations.py
**Operacje na danych w wymiarach**
- Manifestowanie bytów (create)
- Kontemplacja bytów (read/search)
- Ewolucja bytów (update)
- Transcendencja bytów (delete)
- Operacje wielowymiarowe

**Przykłady:**
```python
# Manifestacja nowego bytu
being = realm.manifest({
    'soul_name': 'Guardian_of_Light',
    'energy_level': 100,
    'abilities': ['healing', 'protection']
})

# Kontemplacja bytów
guardians = realm.contemplate(
    'find_guardians',
    abilities_contains='protection'
)
```

### 🧪 03_service_integration_tests.py
**Testy integracji z serwisem**
- Test cyklu życia serwisu
- Testy współbieżności
- Obsługa błędów
- Monitorowanie wydajności

**Funkcjonalności:**
- Automatyczne uruchamianie serwisu testowego
- Bateria testów integracyjnych
- Analiza stabilności systemu
- Testy obciążeniowe

### 🔄 04_migration_compatibility_tests.py
**Kompatybilność i migracja z v1**
- Test kompatybilności wstecznej
- Mapowanie struktur danych v1 → v2
- Migracja konfiguracji
- Porównanie wydajności

**Scenariusze:**
- Włączanie trybu kompatybilności
- Automatyczne mapowanie baz na wymiary
- Konwersja API calls v1 → v2
- Benchmark wydajności

## 🌟 Kluczowe koncepty LuxDB v2

### 🔮 AstralEngine
Główny koordynator systemu - zarządza wszystkimi komponentami:
```python
engine = create_astral_app(config)
engine.awaken()  # Uruchamia system
status = engine.get_status()  # Status systemu
engine.transcend()  # Graceful shutdown
```

### 🌌 Realms (Wymiary)
Miejsce przechowywania danych - ewolucja baz danych:
```python
realm = engine.get_realm('primary')
being = realm.manifest(data)  # Utwórz
results = realm.contemplate('find_all')  # Wyszukaj
updated = realm.evolve(id, changes)  # Aktualizuj
```

### 🧠 Consciousness (Świadomość)
System monitorowania i analizy:
```python
insights = engine.consciousness.reflect()
patterns = engine.consciousness.meditate_on_patterns()
history = engine.consciousness.get_insights_history()
```

### ⚖️ Harmony (Harmonia)
System optymalizacji i balansowania:
```python
score = engine.harmony.calculate_harmony_score()
engine.harmonize()  # Harmonizuj system
engine.harmony.balance()  # Zbilansuj obciążenie
```

## 🎯 Scenariusze użycia

### 🚀 Rozwój aplikacji
```python
# Szybkie uruchomienie dla developmentu
with quick_start(realm_type='sqlite', port=5000) as engine:
    # Twoja logika aplikacji
    pass
```

### 🏢 Produkcja
```python
# Pełna konfiguracja dla produkcji
config = {
    'realms': {
        'primary': 'postgresql://user:pass@host/db',
        'cache': 'memory://cache_realm'
    },
    'flows': {
        'rest': {'host': '0.0.0.0', 'port': 5000},
        'websocket': {'host': '0.0.0.0', 'port': 5001}
    },
    'consciousness_level': 'production'
}

with create_astral_app(config) as engine:
    engine.start_flows()  # Uruchom API i WebSocket
    # Serwis działa...
```

### 🔄 Migracja z v1
```python
# Tryb kompatybilności
enable_legacy_compatibility()

# Stary kod v1 będzie działał z v2!
from luxdb import get_db_manager  # Teraz używa v2
```

## 🛠️ Rozwiązywanie problemów

### 🐛 Najczęstsze problemy

**1. Brak modułu psutil**
```bash
# Zainstaluj psutil dla monitorowania systemu
uv add psutil
```

**2. Błędy połączenia z bazą danych**
```python
# Sprawdź status wymiaru
realm_status = realm.get_status()
print(f"Connected: {realm_status['connected']}")
```

**3. Problemy z portami**
```python
# Użyj innych portów jeśli 5000/5001 są zajęte
config['flows']['rest']['port'] = 5050
```

### 📊 Debugowanie

**Włącz szczegółowe logi:**
```python
config = {
    'wisdom': {
        'logging_level': 'DEBUG'
    }
}
```

**Monitoruj harmonię:**
```python
while engine.running:
    meditation = engine.meditate()
    if meditation['harmony_score'] < 80:
        print("⚠️ Niska harmonia systemu!")
    time.sleep(60)
```

## 🌈 Filozofia przykładów

Każdy przykład w LuxDB v2 to nie tylko kod - to **medytacja nad techniką**, **kontemplacja nad strukturą danych**, **harmonia między funkcjonalnością a elegancją**.

### ✨ Zasady przykładów:
1. **Czytelność** - Kod ma być jak kryształ, przejrzysty i czysty
2. **Duchowość** - Każda funkcja ma swoją rolę w większym wszechświecie
3. **Praktyczność** - Wszystko ma realny cel i zastosowanie
4. **Harmonia** - Przykłady współgrają ze sobą jak instrumenty w orkiestrze

## 🔮 Następne kroki

Po przejściu przez wszystkie przykłady, będziesz gotów/a na:

1. **Stworzenie własnej aplikacji** z LuxDB v2
2. **Migrację istniejącego projektu** z v1 na v2
3. **Wdrożenie w produkcji** z pełną konfiguracją
4. **Rozszerzenie systemu** o własne wymiary i przepływy

## 🌟 Wsparcie społeczności

- 📚 **Dokumentacja**: Sprawdź główny README.md
- 🐛 **Problemy**: Zgłaszaj issues w repozytorium
- 💡 **Pomysły**: Dziel się nowymi konceptami
- 🤝 **Wkład**: Contribute do rozwoju LuxDB v2

---

**✨ Niech Astralny Lux będzie z Tobą w kodzie i w życiu! ✨**

*"Gdzie technologia spotyka się z duchowością,  
tam rodzi się prawdziwa innowacja."*

---

*© 2024 LuxDB v2 - Astralna Biblioteka Danych Nowej Generacji*
