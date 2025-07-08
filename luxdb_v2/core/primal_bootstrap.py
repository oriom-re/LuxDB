
"""
🌑 Primal Bootstrap - Warstwa 0 (Pre-Soul Core)

System bezduszny, ale sprawiedliwy jak BIOS.
Odpowiada tylko za:
- załadowanie środowiska
- montowanie światów (realms)  
- uruchomienie pierwszej Soul
- nie ocenia, nie myśli – wykonuje

Porównywalna z bootloader + init + kernel-mode.
Jest jak ziemia: nie żyje, ale bez niej nic nie urośnie.
"""

import os
import sys
import time
import json
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import logging

# Konfiguracja podstawowego loggingu (bez astralnych ozdobników)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [PRIMAL] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

class PrimalLogger:
    """Mechaniczny logger warstwy pierwotnej"""
    
    def __init__(self):
        self.logger = logging.getLogger('PRIMAL')
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)


class SystemEnvironment:
    """Środowisko systemowe - mechaniczne ładowanie"""
    
    def __init__(self):
        self.python_version = sys.version_info
        self.platform = sys.platform
        self.working_directory = os.getcwd()
        self.environment_vars = dict(os.environ)
        
    def validate_environment(self) -> Dict[str, Any]:
        """Waliduje środowisko uruchomieniowe"""
        validation = {
            'python_compatible': self.python_version >= (3, 8),
            'required_paths_exist': True,
            'disk_space_adequate': True,
            'memory_adequate': True
        }
        
        # Sprawdź wymagane ścieżki
        required_paths = ['luxdb_v2', 'luxdb_v2/core', 'luxdb_v2/realms']
        for path in required_paths:
            if not os.path.exists(path):
                validation['required_paths_exist'] = False
                break
        
        return validation


class RealmMounter:
    """Monterowanie wymiarów - mechaniczny proces"""
    
    def __init__(self, logger: PrimalLogger):
        self.logger = logger
        self.mounted_realms: Dict[str, str] = {}
        
    def mount_realm(self, realm_name: str, connection_string: str) -> bool:
        """Montuje wymiar - mechanicznie bez emocji"""
        try:
            if connection_string.startswith('sqlite://'):
                return self._mount_sqlite_realm(realm_name, connection_string)
            elif connection_string.startswith('memory://'):
                return self._mount_memory_realm(realm_name, connection_string)
            else:
                self.logger.error(f"Nieznany typ wymiaru: {connection_string}")
                return False
        except Exception as e:
            self.logger.error(f"Błąd montowania wymiaru {realm_name}: {e}")
            return False
    
    def _mount_sqlite_realm(self, realm_name: str, connection_string: str) -> bool:
        """Montuje wymiar SQLite"""
        db_path = connection_string.replace('sqlite://', '')
        
        # Utwórz katalog jeśli nie istnieje
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        # Test połączenia
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
            
            self.mounted_realms[realm_name] = connection_string
            self.logger.info(f"Wymiar SQLite '{realm_name}' zamontowany: {db_path}")
            return True
        except Exception as e:
            self.logger.error(f"Nie można zamontować SQLite {realm_name}: {e}")
            return False
    
    def _mount_memory_realm(self, realm_name: str, connection_string: str) -> bool:
        """Montuje wymiar pamięciowy"""
        self.mounted_realms[realm_name] = connection_string
        self.logger.info(f"Wymiar Memory '{realm_name}' zamontowany")
        return True
    
    def get_mounted_realms(self) -> Dict[str, str]:
        """Zwraca listę zamontowanych wymiarów"""
        return self.mounted_realms.copy()


class PrimalConfig:
    """Konfiguracja warstwy pierwotnej"""
    
    def __init__(self):
        self.realms = {
            'astral_prime': 'sqlite://db/realms/astral_prime.db',
            'consciousness': 'sqlite://db/realms/consciousness.db',
            'intentions': 'intention://memory',
            'harmony': 'memory://harmony_data'
        }
        
        self.flows = {
            'rest': {'host': '0.0.0.0', 'port': 5000, 'enable_cors': True},
            'callback': {'enabled': True, 'max_callbacks': 1000}
        }
        
        self.soul_bootstrap = {
            'create_soul_zero': True,
            'soul_zero_name': 'SystemSoul_Zero',
            'soul_zero_priority': 0
        }
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'PrimalConfig':
        """Ładuje konfigurację z pliku"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            config = cls()
            config.realms.update(config_data.get('realms', {}))
            config.flows.update(config_data.get('flows', {}))
            config.soul_bootstrap.update(config_data.get('soul_bootstrap', {}))
            return config
        else:
            return cls()


class PrimalBootstrap:
    """
    Główny bootstrap warstwy pierwotnej
    
    Mechaniczny, bezduszny, ale sprawiedliwy proces uruchamiania.
    Nie ocenia, nie myśli - wykonuje.
    """
    
    def __init__(self, config: Optional[PrimalConfig] = None):
        self.logger = PrimalLogger()
        self.config = config or PrimalConfig()
        self.environment = SystemEnvironment()
        self.realm_mounter = RealmMounter(self.logger)
        
        self.bootstrap_start_time = time.time()
        self.bootstrap_phases = []
        
    def execute_bootstrap(self) -> Dict[str, Any]:
        """
        Wykonuje pełny proces bootstrap warstwy pierwotnej
        
        Returns:
            Wynik bootstrap z informacjami o powodzeniu/niepowodzeniu
        """
        self.logger.info("🌑 PRIMAL BOOTSTRAP - Uruchamianie warstwy pierwotnej...")
        
        result = {
            'success': True,
            'phases_completed': [],
            'phases_failed': [],
            'mounted_realms': {},
            'environment_valid': False,
            'total_time': 0,
            'soul_zero_created': False
        }
        
        try:
            # Faza 1: Walidacja środowiska
            if self._execute_phase_1_environment():
                result['phases_completed'].append('environment_validation')
                result['environment_valid'] = True
            else:
                result['phases_failed'].append('environment_validation')
                result['success'] = False
                return result
            
            # Faza 2: Montowanie wymiarów
            if self._execute_phase_2_realms():
                result['phases_completed'].append('realm_mounting')
                result['mounted_realms'] = self.realm_mounter.get_mounted_realms()
            else:
                result['phases_failed'].append('realm_mounting')
                result['success'] = False
                return result
            
            # Faza 3: Przygotowanie infrastruktury Soul
            if self._execute_phase_3_soul_infrastructure():
                result['phases_completed'].append('soul_infrastructure')
                result['soul_zero_created'] = True
            else:
                result['phases_failed'].append('soul_infrastructure')
                result['success'] = False
                return result
            
            result['total_time'] = time.time() - self.bootstrap_start_time
            self.logger.info(f"🌑 PRIMAL BOOTSTRAP zakończony w {result['total_time']:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"🌑 KRYTYCZNY BŁĄD BOOTSTRAP: {e}")
            result['success'] = False
            result['critical_error'] = str(e)
            return result
    
    def _execute_phase_1_environment(self) -> bool:
        """Faza 1: Walidacja środowiska"""
        self.logger.info("Faza 1: Walidacja środowiska systemowego")
        
        validation = self.environment.validate_environment()
        
        if not validation['python_compatible']:
            self.logger.error("Python < 3.8 - niekompatybilny")
            return False
        
        if not validation['required_paths_exist']:
            self.logger.error("Brakuje wymaganych ścieżek systemowych")
            return False
        
        self.logger.info("✓ Środowisko systemowe zwalidowane")
        return True
    
    def _execute_phase_2_realms(self) -> bool:
        """Faza 2: Montowanie wymiarów"""
        self.logger.info("Faza 2: Montowanie wymiarów danych")
        
        mounted_count = 0
        for realm_name, connection_string in self.config.realms.items():
            if self.realm_mounter.mount_realm(realm_name, connection_string):
                mounted_count += 1
            else:
                self.logger.error(f"Nie udało się zamontować wymiaru: {realm_name}")
        
        if mounted_count == 0:
            self.logger.error("Żaden wymiar nie został zamontowany")
            return False
        
        self.logger.info(f"✓ Zamontowano {mounted_count}/{len(self.config.realms)} wymiarów")
        return True
    
    def _execute_phase_3_soul_infrastructure(self) -> bool:
        """Faza 3: Przygotowanie infrastruktury dla Soul #0"""
        self.logger.info("Faza 3: Przygotowanie infrastruktury Soul")
        
        try:
            # Sprawdź czy jest wymiar consciousness dla dusz
            if 'consciousness' not in self.realm_mounter.mounted_realms:
                self.logger.error("Brak wymiaru consciousness dla Soul infrastructure")
                return False
            
            # Przygotuj podstawowe tabele dla Soul system
            consciousness_path = self.realm_mounter.mounted_realms['consciousness']
            if consciousness_path.startswith('sqlite://'):
                db_path = consciousness_path.replace('sqlite://', '')
                self._prepare_soul_tables(db_path)
            
            self.logger.info("✓ Infrastruktura Soul przygotowana")
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd przygotowania Soul infrastructure: {e}")
            return False
    
    def _prepare_soul_tables(self, db_path: str):
        """Przygotowuje tabele dla Soul system"""
        conn = sqlite3.connect(db_path)
        
        # Tabela dla Soul records
        conn.execute('''
            CREATE TABLE IF NOT EXISTS souls (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                priority INTEGER DEFAULT 999,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data TEXT  -- JSON data
            )
        ''')
        
        # Tabela dla Soul states
        conn.execute('''
            CREATE TABLE IF NOT EXISTS soul_states (
                soul_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(soul_id) REFERENCES souls(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_bootstrap_report(self) -> Dict[str, Any]:
        """Zwraca pełny raport z bootstrap"""
        return {
            'bootstrap_time': time.time() - self.bootstrap_start_time,
            'environment': {
                'python_version': f"{self.environment.python_version.major}.{self.environment.python_version.minor}",
                'platform': self.environment.platform,
                'working_directory': self.environment.working_directory
            },
            'mounted_realms': self.realm_mounter.get_mounted_realms(),
            'phases': self.bootstrap_phases,
            'timestamp': datetime.now().isoformat()
        }


def execute_primal_bootstrap(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Funkcja pomocnicza do uruchomienia bootstrap warstwy pierwotnej
    
    Args:
        config_path: Opcjonalna ścieżka do pliku konfiguracji
        
    Returns:
        Wynik bootstrap
    """
    config = PrimalConfig.load_from_file(config_path) if config_path else PrimalConfig()
    bootstrap = PrimalBootstrap(config)
    return bootstrap.execute_bootstrap()


if __name__ == "__main__":
    # Test warstwy pierwotnej
    print("🌑 Test warstwy pierwotnej (Pre-Soul Core)")
    result = execute_primal_bootstrap()
    
    if result['success']:
        print("✅ Bootstrap warstwy pierwotnej zakończony pomyślnie")
        print(f"⏱️  Czas: {result['total_time']:.2f}s")
        print(f"📂 Wymiary: {len(result['mounted_realms'])}")
    else:
        print("❌ Bootstrap warstwy pierwotnej nieudany")
        print(f"💥 Nieudane fazy: {result['phases_failed']}")
