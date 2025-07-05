
"""
💡 Communication Hints - System proaktywnych wskazówek

Analizuje kod i kontekst, aby dostarczać proaktywne wskazówki
"""

from typing import List, Dict, Any
import re

class ProactiveHintsEngine:
    """Silnik proaktywnych wskazówek"""
    
    def __init__(self):
        self.hint_patterns = {
            'imports': {
                'pattern': r'import\s+\w+|from\s+\w+\s+import',
                'hints': [
                    "💡 Sprawdź czy wszystkie moduły są zainstalowane",
                    "🔍 Upewnij się, że ścieżki importów są poprawne",
                    "📦 Rozważ użycie względnych importów w pakietach"
                ]
            },
            'async_functions': {
                'pattern': r'async\s+def|await\s+',
                'hints': [
                    "⚡ Funkcje async muszą być wywołane z await",
                    "🔄 Sprawdź czy event loop jest uruchomiony",
                    "⚠️ Uważaj na blocking operations w async code"
                ]
            },
            'database_operations': {
                'pattern': r'session\.|db\.|cursor\.|connection\.',
                'hints': [
                    "🗄️ Pamiętaj o zamykaniu połączeń",
                    "🔒 Używaj transaction context managerów",
                    "💾 Sprawdź czy commit() został wywołany"
                ]
            },
            'file_operations': {
                'pattern': r'open\(|with\s+open',
                'hints': [
                    "📁 Używaj context managers (with) dla plików",
                    "🔐 Sprawdź uprawnienia do pliku",
                    "🛡️ Obsłuż wyjątki FileNotFoundError"
                ]
            },
            'thread_operations': {
                'pattern': r'Thread\(|threading\.|multiprocessing\.',
                'hints': [
                    "🔄 Sprawdź thread-safety współdzielonych zasobów",
                    "🔒 Używaj Lock() dla krytycznych sekcji",
                    "⚡ Rozważ AsyncIO zamiast threadów dla I/O"
                ]
            }
        }
    
    def analyze_code(self, code: str) -> List[str]:
        """Analizuje kod i zwraca odpowiednie wskazówki"""
        hints = []
        
        for category, config in self.hint_patterns.items():
            if re.search(config['pattern'], code, re.IGNORECASE):
                hints.extend(config['hints'])
        
        return list(set(hints))  # Usuń duplikaty
    
    def get_context_hints(self, context: str) -> List[str]:
        """Zwraca wskazówki oparte na kontekście"""
        context_hints = {
            'module_loading': [
                "🎯 **Na co zwrócić uwagę przy ładowaniu modułów:**",
                "• Sprawdź ścieżki w manifeście",
                "• Upewnij się, że klasy mają poprawne nazwy",
                "• Zweryfikuj struktur pakietów (__init__.py)"
            ],
            'database_management': [
                "🗄️ **Database Management - kluczowe punkty:**",
                "• Zawsze używaj connection pooling",
                "• Implementuj proper error handling",
                "• Pamiętaj o migracjach przy zmianie schema"
            ],
            'async_programming': [
                "⚡ **Async Programming - najważniejsze:**",
                "• Wszystkie async funkcje muszą być awaited",
                "• Nie blokuj event loop synchronicznym kodem",
                "• Używaj asyncio.gather() dla równoległych operacji"
            ]
        }
        
        return context_hints.get(context, [])


# Globalna instancja silnika wskazówek
hints_engine = ProactiveHintsEngine()


def get_code_hints(code: str) -> str:
    """Zwraca sformatowane wskazówki dla kodu"""
    hints = hints_engine.analyze_code(code)
    
    if not hints:
        return ""
    
    formatted = "\n\n🎯 **Proaktywne wskazówki:**\n"
    for hint in hints:
        formatted += f"• {hint}\n"
    
    return formatted


def get_context_advice(context: str) -> str:
    """Zwraca porady kontekstowe"""
    hints = hints_engine.get_context_hints(context)
    
    if not hints:
        return ""
    
    return "\n" + "\n".join(hints)
