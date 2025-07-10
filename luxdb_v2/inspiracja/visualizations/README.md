# 🎨 LuxCore Visualizations - Inspiracja

## Co to jest?

To folder zawiera generatory wizualizacji systemu LuxCore, które zostały przeniesione z głównego katalogu projektu do sekcji "inspiracji".

## Zawartość

### 📊 Generatory
- `generate_system_visualization.py` - Generator podstawowej wizualizacji architektury
- `generate_interactive_map.py` - Generator interaktywnej mapy route (vis.js)
- `generate_dashboard.py` - Generator dashboardu z metrykami (Chart.js)
- `generate_all_visualizations.py` - Master generator - tworzy wszystkie wizualizacje

### 🌐 Wygenerowane HTML
- `luxcore_system_visualization.html` - Statyczna wizualizacja systemu
- `luxcore_interactive_map.html` - Interaktywna mapa sieci route
- `luxcore_dashboard.html` - Dashboard z wykresami i metrykami
- `luxcore_master_index.html` - Strona główna z linkami do wszystkich

## Kiedy używać?

Te narzędzia służą do:
- **Analizy architektury systemu** - zobaczenie jak wygląda struktura route
- **Debugowania routingu** - wizualna analiza połączeń i zależności  
- **Monitorowania wydajności** - wykresy i metryki systemu
- **Prezentacji systemu** - ładne wizualizacje dla dokumentacji

## Jak uruchomić?

```bash
# Wygeneruj wszystkie wizualizacje
cd /var/home/oriom/Dokumenty/Federacja/luxdb/luxdb_v2/inspiracja/visualizations
python generate_all_visualizations.py

# Lub pojedyncze generatory
python generate_dashboard.py
python generate_interactive_map.py
python generate_system_visualization.py
```

## Stan systemu

Generatory działają na **aktualnym stanie systemu** - czytają routing, moduły, statystyki i generują wizualizacje w czasie rzeczywistym.

## Przyszłość

W przyszłości te narzędzia mogą zostać:
- Zintegrowane z głównym systemem jako route
- Rozszerzone o live monitoring  
- Połączone z WebSocket dla real-time updates
- Wbudowane w panel administracyjny

---

💡 **Inspiracja** - te narzędzia pokazują potencjał systemu LuxCore w obszarze wizualizacji i monitorowania. Można je wykorzystać jako punkt wyjścia dla bardziej zaawansowanych rozwiązań.
