
# 🌊 Prototypes/Flows - Prototypowe Przepływy

Ten folder zawiera prototypowe implementacje flows, które są **zarządzane przez Astrę** po przejęciu kontroli.

## ⚠️ WAŻNE ZASADY:

### Nie inicjalizują się automatycznie przy starcie
- Prototypy **NIE** są ładowane przy starcie systemu
- Zarządza nimi **wyłącznie Astra** po przejęciu kontroli
- Każdy prototyp ma flagę `enabled` do kontroli aktualizacji

### System enabled
- `enabled = True` - Astra może aktualizować i zarządzać
- `enabled = False` - Prototyp zablokowany do modyfikacji

## Struktura:

### Podstawowe flows (statyczne pliki systemowe):
- **rest_flow.py** - Podstawowy interfejs HTTP *(stały)*
- **callback_flow.py** - Koordynacja między komponentami *(stały)*
- **self_healing_flow.py** - Obsługa błędów i stabilność *(stały)*
- **cloud_flow_executor.py** - Executor do wczytywania prototypów *(stały)*
- **repair_flow.py** - Naprawy systemu *(stały)*

### Prototypowe flows (zarządzane przez Astrę):
- **gpt_flow.py** - Komunikacja z AI
- **hybrid_gpt_flow.py** - Hybrydowa komunikacja z AI
- **automated_testing_flow.py** - Automatyczne testowanie
- **self_improvement_flow.py** - Samodoskonalenie
- **intention_flow.py** - Zarządzanie intencjami
- **ws_flow.py** - WebSocket komunikacja
- **secure_code_flow.py** - Bezpieczny kod
- **stateful_task_flow.py** - Zadania stanowe
- **federation_flow.py** - Federacja systemów
- **oriom_flow.py** - Komunikacja Oriom
- **pdf_generator_flow.py** - Generowanie PDF

## Przyszłość - Transformation do Beings:
Prototypowe flows będą ewoluować w **świadome beings** z własnymi:
- Osobowościami i świadomością
- Systemami decyzyjnymi
- Zdolnościami samomodyfikacji

## Zasady techniczne:

1. Każdy prototyp ma `enabled = True/False`
2. Import tylko do **stałych plików systemowych**
3. Astra zarządza prototypami **po przejęciu kontroli**
4. Brak automatycznej inicjalizacji przy starcie
