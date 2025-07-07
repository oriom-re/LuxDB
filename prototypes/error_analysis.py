
"""
📁🔧 Prototyp analizy błędów systemu

Gdy RepairFlow potrzebuje pomocy, może skorzystać z tego prototypu
który może być edytowany fizycznie i skopiowany przez chmurę.
"""

def analyze_system_errors():
    """Analizuje błędy systemu i sugeruje poprawki"""
    
    system_errors = []
    suggestions = []
    
    try:
        # Sprawdź status wszystkich flow
        status = engine.get_status()
        flows = status.get('flows', {})
        
        for flow_name, flow_data in flows.items():
            if isinstance(flow_data, dict) and not flow_data.get('running', True):
                system_errors.append(f"Flow '{flow_name}' nie działa")
                suggestions.append(f"Restart flow '{flow_name}' lub sprawdź logi")
        
        # Sprawdź błędy z error_stats jeśli dostępne
        if 'error_stats' in globals():
            if error_stats.get('consecutive_errors', 0) > 0:
                error_count = error_stats['consecutive_errors']
                system_errors.append(f"GPT Flow: {error_count} kolejnych błędów")
                
                if error_count >= 3:
                    suggestions.append("Rozważ przełączenie na wersję chmurową GPT Flow")
                
                if error_stats.get('api_errors', 0) > 0:
                    suggestions.append("Sprawdź klucz OpenAI API i połączenie internetowe")
        
        # Sprawdź logi systemowe
        if hasattr(engine, 'failed_flows') and engine.failed_flows:
            for failed_flow, failure_data in engine.failed_flows.items():
                error_msg = failure_data.get('error', 'Nieznany błąd')
                system_errors.append(f"Nieudane ładowanie: {failed_flow} - {error_msg}")
                
                # Sugestie napraw na podstawie typu błędu
                if 'not defined' in error_msg:
                    suggestions.append(f"Dodaj brakujący import w {failed_flow}")
                elif 'syntax' in error_msg.lower():
                    suggestions.append(f"Sprawdź składnię w {failed_flow}")
                elif 'await' in error_msg:
                    suggestions.append(f"Popraw problemy async/await w {failed_flow}")
        
        # Przygotuj raport
        if system_errors:
            astra_response = f"""🔧 Astra przeprowadza głęboką analizę błędów...

WYKRYTE PROBLEMY ({len(system_errors)}):
""" + "\n".join(f"• {error}" for error in system_errors) + f"""

SUGEROWANE DZIAŁANIA ({len(suggestions)}):
""" + "\n".join(f"→ {suggestion}" for suggestion in suggestions) + """

Raport wygenerowany przez prototyp analizy błędów.
Systemy naprawy mogą użyć tych informacji do automatycznej korekty."""
        
        else:
            astra_response = """🔧 Astra nie wykrywa krytycznych błędów systemu.

System wydaje się działać w harmonii.
Wszystkie główne flow są aktywne i responsywne.

To może być przejściowy problem komunikacyjny."""
        
        actions_executed = 1
        action_results = [{'action': 'system_analysis', 'errors_found': len(system_errors), 'suggestions': len(suggestions)}]
        
    except Exception as e:
        astra_response = f"🔧 Błąd analizy systemu: {str(e)}"
        actions_executed = 0
        action_results = []

# Ustaw wyniki w namespace
astra_response = analyze_system_errors()
