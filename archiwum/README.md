# 📦 ARCHIWUM FEDERACJI

*Repozytorium przeniesionych plików podczas reorganizacji struktury warstwowej*

## 📂 Struktura Archiwum

### 🧪 `stare_testy/`
**Stare testy systemowe** - nieaktualne lub zastąpione nowymi:
- `test.py` - pierwotny test
- `simple_test.py` - prosty test
- `test_dynamic_routing.py` - test routingu
- `test_routing_api.py` - test API routingu  
- `test_versioning.py` - test wersjonowania

### 🏗️ `stare_systemy/`
**Przestarzałe systemy** - zastąpione przez nową architekturę:
- `lux_core/` - pierwszy system LuxCore (v1)
- `scripts/` - stare skrypty pomocnicze

### 🔬 `prototypy/`
**Eksperymentalne komponenty** - prototypy i proof-of-concept:
- `examples/` - przykłady użycia
- `crypto/` - eksperymentalna kryptografia
- `luxbus/` - prototyp systemu komunikacji
- `inspiracja/` - folder inspiracji i wizualizacji
- `warstwa_0_pierwotna/` - pierwotny prototyp warstwy 0
- Pojedyncze pliki prototypowe:
  - `astral_dashboard.html`
  - `minimal_astra_config.py`
  - `start_astra_pure.py`
  - `ws_client_example.py`
  - `inspiracja.py`
  - `run_scenerio.py`
  - `validator.py`
  - `lux_terminal.py`
  - `repair_flow.py`
  - `self_healing_flow.py`
  - `cloud_flow_executor.py`

### 🎨 `wizualizacje/`
**Wizualizacje systemu** - dashboardy i mapy systemowe:
- `luxcore_dashboard.html`
- `luxcore_interactive_map.html`
- `luxcore_master_index.html`
- `luxcore_system_visualization.html`
- Generatory wizualizacji

## 🎯 Cel Reorganizacji

### ✅ Usunięte z głównej struktury:
1. **Duplikaty funkcjonalności** - usunięto przestarzałe wersje
2. **Eksperymentalne kody** - przeniesiono do archiwum prototypów
3. **Nieużywane testy** - zastąpione nowymi testami warstw
4. **Stare systemy** - LuxCore v1 i związane komponenty

### 🏛️ Zachowana struktura główna:
```
luxdb/
├── test_primal_layer.py     # ✅ Test warstwy 0
├── test_soul_realm.py       # ✅ Test warstwy 1
├── FEDERACJA_STRUCTURE.md   # ✅ Dokumentacja architektury
├── luxdb_v2/               # ✅ Główny system v2
│   ├── core/               # ✅ Rdzeń systemu
│   ├── flows/              # ✅ Podstawowe przepływy
│   ├── realms/             # ✅ Wymiary danych
│   ├── wisdom/             # ✅ Moduły mądrości
│   └── beings/             # ✅ System bytów
└── archiwum/               # 📦 Przeniesione komponenty
```

## 🔮 Możliwość Przywrócenia

Wszystkie przeniesione pliki mogą być przywrócone w razie potrzeby:
- **Prototypy** - można reaktywować jako eksperymentalne komponenty
- **Wizualizacje** - przydatne do monitorowania systemu
- **Stare testy** - referencja dla nowych implementacji

## 📝 Historia Reorganizacji

**Data**: 11 lipca 2025
**Cel**: Uporządkowanie struktury zgodnie z architekturą FEDERACJI
**Zachowane**: Wszystkie pliki kluczowe dla warstw 0-2
**Przeniesione**: Eksperymentalne, duplikowane i przestarzałe komponenty

---

*"Porządek to podstawa chaosu kontrolowanego"* - Zasada Federacji ✨
