
# 🌊 Prototypes/Flows - Prototypowe Przepływy

Ten folder zawiera prototypowe implementacje flows, które mogą być:

1. **Edytowane fizycznie** przez programistę
2. **Wczytywane dynamicznie** przez CloudFlowExecutor
3. **Testowane bezpiecznie** przed integracją z systemem

## Struktura:

### Podstawowe flows (pozostają w głównym katalogu):
- **rest_flow.py** - Podstawowy interfejs HTTP
- **callback_flow.py** - Koordynacja między komponentami  
- **self_healing_flow.py** - Obsługa błędów i stabilność
- **cloud_flow_executor.py** - Executor do wczytywania prototypów
- **repair_flow.py** - Naprawy systemu

### Prototypowe flows (w tym folderze):
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

## Zasady:

1. Każdy prototyp musi mieć funkcję `create_flow(engine, config)`
2. Prototypy są wczytywane przez CloudFlowExecutor
3. Astra może je modyfikować tylko przez kopiowanie 1:1
4. Wszystkie zmiany muszą być zatwierdzone fizycznie
