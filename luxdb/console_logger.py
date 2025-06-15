
import logging
from typing import Any, Dict
from luxerrors.error_handlers import LuxError

class SimpleConsoleLogger:
    """Prosty logger do wyświetlania błędów na konsoli"""
    
    def __init__(self):
        self.logger = logging.getLogger("LuxDB")
        self.logger.setLevel(logging.INFO)
        
        # Usuń istniejące handlery
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Dodaj prosty handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def error(self, message: str, error: Exception = None):
        """Wyświetl błąd w przyjazny sposób"""
        if isinstance(error, LuxError):
            self.logger.error(f"❌ {message}: {error.error_info.message}")
        elif error:
            self.logger.error(f"❌ {message}: {str(error)}")
        else:
            self.logger.error(f"❌ {message}")
    
    def success(self, message: str):
        """Wyświetl sukces"""
        self.logger.info(f"✅ {message}")
    
    def info(self, message: str):
        """Wyświetl informację"""
        self.logger.info(f"ℹ️  {message}")
    
    def warning(self, message: str):
        """Wyświetl ostrzeżenie"""
        self.logger.warning(f"⚠️  {message}")

# Globalna instancja
_console_logger = SimpleConsoleLogger()

def get_console_logger():
    """Pobierz globalny console logger"""
    return _console_logger
