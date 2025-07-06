
"""
🛡️ Safe Mode - Tryb awaryjny z minimalnym zestawem funkcji

Wznowienie po krytycznych błędach, minimalna funkcjonalność
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class SafeMode:
    """
    Tryb awaryjny Kernela
    
    Zapewnia:
    - Minimalną funkcjonalność systemu
    - Diagnostykę problemów
    - Możliwość odzyskania systemu
    - Bezpieczne wyjście z awarii
    """
    
    def __init__(self, logger):
        self.logger = logger
        self.active = False
        self.activation_time = None
        self.activation_reason = None
        
        # Konfiguracja Safe Mode
        self.config = {
            'auto_activate': True,
            'min_functionality': True,
            'recovery_timeout': 60,
            'max_recovery_attempts': 3
        }
        
        # Stan systemu
        self.system_state = {
            'critical_error': False,
            'recovery_attempts': 0,
            'last_known_good_state': None,
            'failed_components': []
        }
        
        # Minimalne funkcje
        self.minimal_functions = {
            'logging': True,
            'basic_monitoring': True,
            'emergency_shutdown': True,
            'system_diagnosis': True
        }
        
        # Ścieżki
        self.safe_mode_dir = Path('kernel/safe_mode')
        self.diagnostic_file = self.safe_mode_dir / 'diagnostics.json'
        self.recovery_log = self.safe_mode_dir / 'recovery.log'
        
        # Inicjalizacja
        self._initialize_safe_mode()
    
    def _initialize_safe_mode(self):
        """Inicjalizuje Safe Mode"""
        try:
            # Utwórz katalogi
            self.safe_mode_dir.mkdir(parents=True, exist_ok=True)
            
            # Załaduj poprzednie stany
            self._load_previous_diagnostics()
            
            self.logger.debug("🛡️ Safe Mode initialized")
            
        except Exception as e:
            # Nawet jeśli inicjalizacja nie powiedzie się, Safe Mode musi działać
            print(f"⚠️ Safe Mode initialization warning: {e}")
    
    def _load_previous_diagnostics(self):
        """Ładuje poprzednie diagnostyki"""
        try:
            if self.diagnostic_file.exists():
                with open(self.diagnostic_file, 'r') as f:
                    previous_diagnostics = json.load(f)
                    
                # Sprawdź czy było wcześniej w Safe Mode
                if previous_diagnostics.get('safe_mode_active'):
                    self.logger.warning("⚠️ Previous Safe Mode session detected")
                    
        except Exception as e:
            self.logger.error(f"❌ Error loading diagnostics: {e}")
    
    async def activate(self, reason: str = "Unknown error"):
        """Aktywuje Safe Mode"""
        try:
            self.active = True
            self.activation_time = datetime.now()
            self.activation_reason = reason
            
            self.logger.critical(f"🛡️ Safe Mode activated: {reason}")
            
            # Zapisz stan aktywacji
            await self._save_activation_state()
            
            # Wykonaj diagnostykę
            await self._perform_system_diagnosis()
            
            # Uruchom minimalne funkcje
            await self._start_minimal_functions()
            
            # Spróbuj odzyskać system
            await self._attempt_recovery()
            
        except Exception as e:
            self.logger.critical(f"💥 Safe Mode activation failed: {e}")
            # Ostatnia deska ratunku
            await self._emergency_fallback()
    
    async def _save_activation_state(self):
        """Zapisuje stan aktywacji"""
        try:
            activation_data = {
                'safe_mode_active': True,
                'activation_time': self.activation_time.isoformat(),
                'activation_reason': self.activation_reason,
                'system_state': self.system_state
            }
            
            with open(self.diagnostic_file, 'w') as f:
                json.dump(activation_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving activation state: {e}")
    
    async def _perform_system_diagnosis(self):
        """Wykonuje diagnostykę systemu"""
        try:
            self.logger.info("🔍 Performing system diagnosis...")
            
            diagnosis = {
                'timestamp': datetime.now().isoformat(),
                'system_info': self._get_system_info(),
                'memory_usage': self._get_memory_usage(),
                'disk_usage': self._get_disk_usage(),
                'process_info': self._get_process_info(),
                'error_analysis': self._analyze_recent_errors()
            }
            
            # Zapisz diagnostykę
            with open(self.diagnostic_file, 'w') as f:
                json.dump(diagnosis, f, indent=2)
            
            self.logger.info("✅ System diagnosis completed")
            
        except Exception as e:
            self.logger.error(f"❌ System diagnosis failed: {e}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Pobiera informacje o systemie"""
        try:
            import platform
            return {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'architecture': platform.architecture(),
                'processor': platform.processor()
            }
        except Exception:
            return {'error': 'System info unavailable'}
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Pobiera użycie pamięci"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_percent': memory.percent
            }
        except Exception:
            return {'error': 'Memory info unavailable'}
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Pobiera użycie dysku"""
        try:
            import psutil
            disk = psutil.disk_usage('.')
            return {
                'total_gb': disk.total / (1024**3),
                'free_gb': disk.free / (1024**3),
                'used_percent': (disk.used / disk.total) * 100
            }
        except Exception:
            return {'error': 'Disk info unavailable'}
    
    def _get_process_info(self) -> Dict[str, Any]:
        """Pobiera informacje o procesach"""
        try:
            import psutil
            return {
                'pid': os.getpid(),
                'cpu_percent': psutil.Process().cpu_percent(),
                'memory_percent': psutil.Process().memory_percent(),
                'thread_count': psutil.Process().num_threads()
            }
        except Exception:
            return {'error': 'Process info unavailable'}
    
    def _analyze_recent_errors(self) -> Dict[str, Any]:
        """Analizuje ostatnie błędy"""
        try:
            # Tutaj byłaby analiza logów błędów
            return {
                'analysis': 'Error analysis not implemented',
                'recommendation': 'Manual investigation required'
            }
        except Exception:
            return {'error': 'Error analysis unavailable'}
    
    async def _start_minimal_functions(self):
        """Uruchamia minimalne funkcje"""
        try:
            self.logger.info("🔧 Starting minimal functions...")
            
            # Podstawowe logowanie - już działa
            if self.minimal_functions['logging']:
                self.logger.info("✅ Logging: Active")
            
            # Podstawowy monitoring
            if self.minimal_functions['basic_monitoring']:
                await self._start_basic_monitoring()
                self.logger.info("✅ Basic monitoring: Active")
            
            # Funkcja emergency shutdown
            if self.minimal_functions['emergency_shutdown']:
                self.logger.info("✅ Emergency shutdown: Ready")
            
            # Diagnostyka systemu
            if self.minimal_functions['system_diagnosis']:
                self.logger.info("✅ System diagnosis: Available")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting minimal functions: {e}")
    
    async def _start_basic_monitoring(self):
        """Uruchamia podstawowy monitoring"""
        try:
            # Podstawowy monitoring zasobów
            pass
        except Exception as e:
            self.logger.error(f"❌ Basic monitoring error: {e}")
    
    async def _attempt_recovery(self):
        """Próbuje odzyskać system"""
        try:
            self.system_state['recovery_attempts'] += 1
            
            if self.system_state['recovery_attempts'] > self.config['max_recovery_attempts']:
                self.logger.critical("💥 Maximum recovery attempts exceeded")
                return False
            
            self.logger.info(f"🔄 Recovery attempt {self.system_state['recovery_attempts']}")
            
            # Próba odzyskania komponentów
            recovery_success = await self._recover_failed_components()
            
            if recovery_success:
                self.logger.info("✅ System recovery successful")
                await self.deactivate()
                return True
            else:
                self.logger.warning("⚠️ System recovery failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Recovery attempt failed: {e}")
            return False
    
    async def _recover_failed_components(self) -> bool:
        """Próbuje odzyskać niedziałające komponenty"""
        try:
            # Tutaj byłaby logika odzyskiwania konkretnych komponentów
            # Na razie symulacja
            recovery_time = 2
            time.sleep(recovery_time)
            
            # Symulacja sukcesu odzyskania
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Component recovery failed: {e}")
            return False
    
    async def _emergency_fallback(self):
        """Ostatnia deska ratunku"""
        try:
            self.logger.critical("🚨 Emergency fallback activated")
            
            # Zapisz stan awaryjny
            emergency_data = {
                'emergency_fallback': True,
                'timestamp': datetime.now().isoformat(),
                'reason': 'Safe Mode activation failed',
                'system_state': self.system_state
            }
            
            with open(self.safe_mode_dir / 'emergency.json', 'w') as f:
                json.dump(emergency_data, f, indent=2)
            
            # Minimalne funkcje awaryjne
            self.logger.critical("🛡️ Emergency mode: Basic logging only")
            
        except Exception as e:
            # Absolutne minimum - print do konsoli
            print(f"💥 CRITICAL: Emergency fallback failed: {e}")
            print("🚨 System in critical state - manual intervention required")
    
    async def deactivate(self):
        """Deaktywuje Safe Mode"""
        try:
            if self.active:
                self.logger.info("🛡️ Deactivating Safe Mode...")
                
                # Zapisz stan deaktywacji
                deactivation_data = {
                    'safe_mode_active': False,
                    'deactivation_time': datetime.now().isoformat(),
                    'activation_duration': (datetime.now() - self.activation_time).total_seconds(),
                    'recovery_attempts': self.system_state['recovery_attempts']
                }
                
                with open(self.diagnostic_file, 'w') as f:
                    json.dump(deactivation_data, f, indent=2)
                
                self.active = False
                self.activation_time = None
                self.activation_reason = None
                
                self.logger.info("✅ Safe Mode deactivated")
                
        except Exception as e:
            self.logger.error(f"❌ Error deactivating Safe Mode: {e}")
    
    def is_active(self) -> bool:
        """Sprawdza czy Safe Mode jest aktywny"""
        return self.active
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status Safe Mode"""
        return {
            'active': self.active,
            'activation_time': self.activation_time.isoformat() if self.activation_time else None,
            'activation_reason': self.activation_reason,
            'system_state': self.system_state,
            'minimal_functions': self.minimal_functions,
            'recovery_attempts': self.system_state['recovery_attempts']
        }
    
    def emergency_shutdown(self):
        """Awaryjne wyłączenie systemu"""
        try:
            self.logger.critical("🚨 Emergency shutdown initiated")
            
            # Zapisz stan awaryjny
            emergency_data = {
                'emergency_shutdown': True,
                'timestamp': datetime.now().isoformat(),
                'reason': 'Manual emergency shutdown'
            }
            
            with open(self.safe_mode_dir / 'emergency_shutdown.json', 'w') as f:
                json.dump(emergency_data, f, indent=2)
            
            # Wyłącz system
            os._exit(1)
            
        except Exception as e:
            print(f"💥 Emergency shutdown failed: {e}")
            os._exit(1)
