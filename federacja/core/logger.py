
"""
📋 Federation Logger - System logowania dla Federacji

Zunifikowany system logowania z różnymi formatami i poziomami
"""

import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class FederationLogger:
    """
    Logger Federacji z możliwością konfiguracji formatów i poziomów
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {'level': 'INFO', 'format': 'console'}
        
        # Główny logger
        self.logger = logging.getLogger('federation')
        self.logger.setLevel(self._get_log_level())
        
        # Usuń istniejące handlery
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Dodaj odpowiedni handler
        self._setup_handler()
    
    def _get_log_level(self) -> int:
        """Zwraca poziom logowania"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(self.config.get('level', 'INFO'), logging.INFO)
    
    def _setup_handler(self):
        """Konfiguruje handler na podstawie formatu"""
        format_type = self.config.get('format', 'console')
        
        if format_type == 'console':
            handler = logging.StreamHandler(sys.stdout)
            formatter = self._get_console_formatter()
        elif format_type == 'file':
            log_file = self.config.get('file', 'logs/federation.log')
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(log_file)
            formatter = self._get_file_formatter()
        else:
            # Domyślnie console
            handler = logging.StreamHandler(sys.stdout)
            formatter = self._get_console_formatter()
        
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _get_console_formatter(self) -> logging.Formatter:
        """Formatter dla konsoli z kolorami"""
        return logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def _get_file_formatter(self) -> logging.Formatter:
        """Formatter dla pliku"""
        return logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def debug(self, message: str, *args, **kwargs):
        """Debug log"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Info log"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Warning log"""
        self.logger.warning(message, *args, **kwargs)
    
    def warn(self, message: str, *args, **kwargs):
        """Alias dla warning"""
        self.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Error log"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Critical log"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception z traceback"""
        self.logger.exception(message, *args, **kwargs)
    
    def log(self, level: int, message: str, *args, **kwargs):
        """Log z określonym poziomem"""
        self.logger.log(level, message, *args, **kwargs)
    
    def set_level(self, level: str):
        """Zmienia poziom logowania"""
        self.logger.setLevel(self._get_log_level())
    
    def add_file_handler(self, filename: str):
        """Dodaje dodatkowy handler do pliku"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(filename)
        handler.setFormatter(self._get_file_formatter())
        self.logger.addHandler(handler)
    
    def get_logger(self) -> logging.Logger:
        """Zwraca podstawowy logger"""
        return self.logger


# Globalna instancja dla łatwego użycia
_global_logger: Optional[FederationLogger] = None


def get_federation_logger(config: Optional[Dict[str, Any]] = None) -> FederationLogger:
    """Zwraca globalną instancję loggera"""
    global _global_logger
    if _global_logger is None:
        _global_logger = FederationLogger(config)
    return _global_logger


def setup_federation_logging(config: Dict[str, Any]) -> FederationLogger:
    """Konfiguruje globalny logger federacji"""
    global _global_logger
    _global_logger = FederationLogger(config)
    return _global_logger
