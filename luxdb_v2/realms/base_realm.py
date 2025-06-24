"""
🌍 BaseRealm - Bazowy Wymiar Astralny

Abstrakcyjna klasa bazowa dla wszystkich wymiarów przechowujących dane w LuxDB v2
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import threading


class BaseRealm(ABC):
    """
    Bazowy wymiar astralny - abstrakcyjna klasa dla wszystkich wymiarów
    """

    def __init__(self, name: str, connection_string: str, astral_engine):
        self.name = name
        self.connection_string = connection_string
        self.engine = astral_engine
        self.created_at = datetime.now()
        self.is_connected = False
        self._lock = threading.Lock()
        self._being_count = 0

    @abstractmethod
    def connect(self) -> bool:
        """Nawiązuje połączenie z wymiarem"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Rozłącza z wymiarem"""
        pass

    @abstractmethod
    def manifest(self, being_data: Dict[str, Any]) -> Any:
        """
        Manifestuje nowy byt w wymiarze

        Args:
            being_data: Dane nowego bytu

        Returns:
            Zmanifestowany byt
        """
        pass

    @abstractmethod
    def contemplate(self, intention: str, **conditions) -> List[Any]:
        """
        Kontempluje (wyszukuje) byty w wymiarze

        Args:
            intention: Intencja zapytania
            **conditions: Warunki wyszukiwania

        Returns:
            Lista znalezionych bytów
        """
        pass

    @abstractmethod
    def transcend(self, being_id: Any) -> bool:
        """
        Transcenduje (usuwa) byt z wymiaru

        Args:
            being_id: ID bytu do usunięcia

        Returns:
            True jeśli sukces
        """
        pass

    @abstractmethod
    def evolve(self, being_id: Any, new_data: Dict[str, Any]) -> Any:
        """
        Ewoluuje (aktualizuje) byt

        Args:
            being_id: ID bytu
            new_data: Nowe dane

        Returns:
            Zaktualizowany byt
        """
        pass

    def is_healthy(self) -> bool:
        """Sprawdza zdrowie wymiaru"""
        return self.is_connected

    def is_active(self) -> bool:
        """Sprawdza czy wymiar jest aktywny"""
        return self.is_connected

    def count_beings(self) -> int:
        """Zwraca liczbę bytów w wymiarze"""
        return self._being_count

    def get_status(self) -> Dict[str, Any]:
        """Zwraca status wymiaru"""
        return {
            'name': self.name,
            'type': self.__class__.__name__,
            'connected': self.is_connected,
            'healthy': self.is_healthy(),
            'active': self.is_active(),
            'being_count': self.count_beings(),
            'created_at': self.created_at.isoformat(),
            'connection_string': self._mask_connection_string()
        }

    def _mask_connection_string(self) -> str:
        """Maskuje wrażliwe dane w connection string"""
        if '://' in self.connection_string:
            protocol, rest = self.connection_string.split('://', 1)
            if '@' in rest:
                credentials, location = rest.split('@', 1)
                return f"{protocol}://***@{location}"
        return self.connection_string

    def close(self) -> None:
        """Zamyka wymiar gracefully"""
        if self.is_connected:
            self.disconnect()

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', connected={self.is_connected})>"