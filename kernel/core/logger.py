
"""
📋 Kernel Logger - System logowania dla Kernela

Krytyczne logowanie z różnymi poziomami i formatami
"""

import logging
import sys
from typing import Dict, Any
from pathlib import Path
from datetime import datetime


class KernelLogger:
    """
    Logger Kernela z krytycznym logowaniem
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Główny logger
        self.logger = logging.getLogger('kernel')
        self.logger.setLevel(self._get_log_level())
        
        # Usuń istniejące handlery
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Dodaj handlery
        self._setup_handlers()
    
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
    
    def _setup_handlers(self):
        """Konfiguruje handlery"""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s [KERNEL] %(levelname)s %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler jeśli skonfigurowany
        log_file = self.config.get('file')
        if log_file:
            try:
                Path(log_file).parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_file)
                file_formatter = logging.Formatter(
                    '%(asctime)s [KERNEL] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f"⚠️ Failed to setup file logging: {e}")
    
    def debug(self, message: str):
        """Debug log"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Info log"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Warning log"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Error log"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Critical log"""
        self.logger.critical(message)
    
    def exception(self, message: str):
        """Log exception z traceback"""
        self.logger.exception(message)
