
"""
🗣️ Communication Style Manager - Zarządca stylu komunikacji

Przechowuje preferencje komunikacyjne użytkowników i dostosowuje odpowiedzi
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class CommunicationStyle:
    """Styl komunikacji użytkownika"""
    user_id: str
    
    # Preferencje ogólne
    preferred_tone: str = "friendly"  # friendly, formal, technical, casual
    use_emojis: bool = True
    detail_level: str = "high"  # low, medium, high, very_high
    
    # Preferencje edukacyjne
    learning_style: str = "proactive_hints"  # error_based, proactive_hints, minimal_guidance
    show_examples: bool = True
    explain_reasoning: bool = True
    
    # Preferencje techniczne
    code_explanation_level: str = "detailed"  # minimal, basic, detailed, comprehensive
    show_file_structure: bool = True
    highlight_gotchas: bool = True
    
    # Preferencje błędów
    error_approach: str = "preventive"  # reactive, preventive, educational
    show_debugging_steps: bool = True
    
    # Osobiste notatki
    favorite_features: List[str] = field(default_factory=list)
    learning_goals: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


class CommunicationStyleManager:
    """Zarządca stylów komunikacji"""
    
    def __init__(self):
        self.styles: Dict[str, CommunicationStyle] = {}
        self.default_style = self._create_default_style()
        
    def _create_default_style(self) -> CommunicationStyle:
        """Tworzy domyślny styl komunikacji"""
        return CommunicationStyle(
            user_id="default",
            preferred_tone="friendly",
            use_emojis=True,
            detail_level="high",
            learning_style="proactive_hints",
            show_examples=True,
            explain_reasoning=True,
            code_explanation_level="detailed",
            show_file_structure=True,
            highlight_gotchas=True,
            error_approach="preventive",
            show_debugging_steps=True
        )
    
    def get_user_style(self, user_id: str = "orion") -> CommunicationStyle:
        """Pobiera styl użytkownika lub domyślny"""
        return self.styles.get(user_id, self.default_style)
    
    def update_user_style(self, user_id: str, updates: Dict[str, Any]) -> None:
        """Aktualizuje styl użytkownika"""
        if user_id not in self.styles:
            self.styles[user_id] = CommunicationStyle(user_id=user_id)
        
        style = self.styles[user_id]
        for key, value in updates.items():
            if hasattr(style, key):
                setattr(style, key, value)
        
        style.last_updated = datetime.now()
    
    def format_response(self, content: str, user_id: str = "orion") -> str:
        """Formatuje odpowiedź zgodnie ze stylem użytkownika"""
        style = self.get_user_style(user_id)
        
        formatted = content
        
        # Dodaj emotikonki jeśli user lubi
        if style.use_emojis and not any(emoji in content for emoji in ['😄', '🎯', '✅', '❌', '🔍']):
            formatted = f"🎯 {formatted}"
        
        # Dodaj wskazówki proaktywne
        if style.learning_style == "proactive_hints":
            formatted += self._add_proactive_hints(content, style)
        
        # Dodaj ostrzeżenia o pułapkach
        if style.highlight_gotchas:
            formatted += self._add_gotcha_warnings(content)
        
        return formatted
    
    def _add_proactive_hints(self, content: str, style: CommunicationStyle) -> str:
        """Dodaje proaktywne wskazówki"""
        hints = []
        
        if "import" in content.lower():
            hints.append("\n💡 **Wskazówka:** Pamiętaj o sprawdzeniu ścieżek importów!")
        
        if "async" in content.lower():
            hints.append("\n⚡ **Na co zwrócić uwagę:** Funkcje async wymagają await!")
        
        if "database" in content.lower():
            hints.append("\n🗄️ **Tip:** Zawsze zamykaj połączenia z bazą!")
        
        return "".join(hints)
    
    def _add_gotcha_warnings(self, content: str) -> str:
        """Dodaje ostrzeżenia o typowych pułapkach"""
        warnings = []
        
        if "yaml" in content.lower():
            warnings.append("\n⚠️ **Uwaga:** YAML jest wrażliwy na wcięcia!")
        
        if "thread" in content.lower():
            warnings.append("\n🔄 **Gotcha:** Sprawdź thread-safety!")
        
        return "".join(warnings)


# Globalna instancja managera
communication_manager = CommunicationStyleManager()

# Ustawienia dla Oriona (Ciebie!)
communication_manager.update_user_style("orion", {
    "preferred_tone": "friendly",
    "use_emojis": True,
    "detail_level": "very_high",
    "learning_style": "proactive_hints",
    "show_examples": True,
    "explain_reasoning": True,
    "code_explanation_level": "comprehensive",
    "show_file_structure": True,
    "highlight_gotchas": True,
    "error_approach": "preventive",
    "show_debugging_steps": True,
    "favorite_features": [
        "szczegółowe analizy błędów",
        "proaktywne wskazówki",
        "emotikonki w komunikacji",
        "pokazywanie struktury kodu"
    ],
    "learning_goals": [
        "lepsze zarządzanie modułami",
        "optymalizacja systemu",
        "czysta architektura"
    ]
})


def get_orion_style() -> CommunicationStyle:
    """Szybki dostęp do stylu Oriona"""
    return communication_manager.get_user_style("orion")


def format_for_orion(content: str) -> str:
    """Formatuje treść dla Oriona"""
    return communication_manager.format_response(content, "orion")
