
"""
🔄 Passive Update Manager - Zarządzanie aktualizacjami i fallback

Obsługa aktualizacji z podwójnymi wersjami modułów i rollback
"""

import os
import json
import hashlib
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class PassiveUpdateManager:
    """
    Zarządca pasywnych aktualizacji
    
    Obsługuje:
    - Podwójne wersje modułów (active, fallback, next_stable)
    - Weryfikację integralności
    - Rollback w przypadku awarii
    """
    
    def __init__(self, config: Dict[str, Any], logger):
        self.config = config
        self.logger = logger
        
        # Konfiguracja
        self.auto_check = config.get('auto_check', True)
        self.check_interval = config.get('check_interval', 3600)
        self.backup_enabled = config.get('backup_enabled', True)
        self.rollback_enabled = config.get('rollback_enabled', True)
        
        # Ścieżki
        self.updates_dir = Path('kernel/updates')
        self.backup_dir = Path('kernel/backups')
        self.versions_file = Path('kernel/versions.json')
        
        # Statystyki
        self.stats = {
            'checks_performed': 0,
            'updates_applied': 0,
            'rollbacks_performed': 0,
            'last_check': None
        }
        
        # Inicjalizacja
        self._initialize_directories()
        self._load_versions()
        
        self.logger.debug("🔄 Passive Update Manager initialized")
    
    def _initialize_directories(self):
        """Inicjalizuje katalogi"""
        self.updates_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_versions(self):
        """Ładuje informacje o wersjach"""
        try:
            if self.versions_file.exists():
                with open(self.versions_file, 'r') as f:
                    self.versions = json.load(f)
            else:
                self.versions = {
                    'active': {},
                    'fallback': {},
                    'next_stable': {}
                }
        except Exception as e:
            self.logger.error(f"❌ Error loading versions: {e}")
            self.versions = {'active': {}, 'fallback': {}, 'next_stable': {}}
    
    def _save_versions(self):
        """Zapisuje informacje o wersjach"""
        try:
            with open(self.versions_file, 'w') as f:
                json.dump(self.versions, f, indent=2)
        except Exception as e:
            self.logger.error(f"❌ Error saving versions: {e}")
    
    async def check_updates(self):
        """Sprawdza dostępne aktualizacje"""
        self.stats['checks_performed'] += 1
        self.stats['last_check'] = datetime.now().isoformat()
        
        try:
            # Sprawdź czy są pliki aktualizacji
            update_files = list(self.updates_dir.glob('*.update'))
            
            if update_files:
                self.logger.info(f"🔄 Found {len(update_files)} updates")
                
                for update_file in update_files:
                    await self._process_update(update_file)
            else:
                self.logger.debug("🔄 No updates available")
                
        except Exception as e:
            self.logger.error(f"❌ Error checking updates: {e}")
    
    async def _process_update(self, update_file: Path):
        """Przetwarza pojedynczą aktualizację"""
        try:
            # Wczytaj metadane aktualizacji
            with open(update_file, 'r') as f:
                update_info = json.load(f)
            
            module_name = update_info.get('module')
            version = update_info.get('version')
            
            self.logger.info(f"🔄 Processing update: {module_name} v{version}")
            
            # Weryfikacja integralności
            if not self._verify_update_integrity(update_info):
                self.logger.error(f"❌ Update integrity check failed: {module_name}")
                return False
            
            # Dry run test
            if not await self._test_update(update_info):
                self.logger.error(f"❌ Update test failed: {module_name}")
                return False
            
            # Backup obecnej wersji
            if self.backup_enabled:
                self._backup_current_version(module_name)
            
            # Zastosuj aktualizację
            success = await self._apply_update(update_info)
            
            if success:
                self.logger.info(f"✅ Update applied successfully: {module_name} v{version}")
                self.stats['updates_applied'] += 1
                
                # Usuń plik aktualizacji
                update_file.unlink()
            else:
                self.logger.error(f"❌ Update failed: {module_name}")
                
                # Rollback jeśli włączony
                if self.rollback_enabled:
                    await self._rollback_update(module_name)
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error processing update: {e}")
            return False
    
    def _verify_update_integrity(self, update_info: Dict[str, Any]) -> bool:
        """Weryfikuje integralność aktualizacji"""
        try:
            # Sprawdź wymagane pola
            required_fields = ['module', 'version', 'files', 'checksum']
            if not all(field in update_info for field in required_fields):
                return False
            
            # Sprawdź checksum
            files_data = update_info.get('files', {})
            calculated_checksum = self._calculate_checksum(files_data)
            
            return calculated_checksum == update_info.get('checksum')
            
        except Exception as e:
            self.logger.error(f"❌ Integrity verification error: {e}")
            return False
    
    def _calculate_checksum(self, data: Any) -> str:
        """Oblicza checksum danych"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    async def _test_update(self, update_info: Dict[str, Any]) -> bool:
        """Testuje aktualizację (dry run)"""
        try:
            # Symulacja zastosowania aktualizacji
            self.logger.debug(f"🧪 Testing update: {update_info.get('module')}")
            
            # Tutaj mogłyby być dodatkowe testy
            # np. sprawdzenie kompatybilności, testowanie importów itp.
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Update test error: {e}")
            return False
    
    def _backup_current_version(self, module_name: str):
        """Tworzy backup obecnej wersji"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{module_name}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            # Tutaj byłaby logika kopiowania plików modułu
            # Na razie symulacja
            backup_path.mkdir(exist_ok=True)
            
            self.logger.info(f"💾 Backup created: {backup_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Backup error: {e}")
    
    async def _apply_update(self, update_info: Dict[str, Any]) -> bool:
        """Zastosowuje aktualizację"""
        try:
            module_name = update_info.get('module')
            version = update_info.get('version')
            
            # Przenieś z next_stable do active
            self.versions['fallback'][module_name] = self.versions['active'].get(module_name, '1.0.0')
            self.versions['active'][module_name] = version
            
            self._save_versions()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Apply update error: {e}")
            return False
    
    async def _rollback_update(self, module_name: str):
        """Wykonuje rollback aktualizacji"""
        try:
            if module_name in self.versions['fallback']:
                # Przywróć wersję fallback
                fallback_version = self.versions['fallback'][module_name]
                self.versions['active'][module_name] = fallback_version
                
                self._save_versions()
                
                self.logger.info(f"🔄 Rollback completed: {module_name} -> {fallback_version}")
                self.stats['rollbacks_performed'] += 1
                
                return True
            else:
                self.logger.error(f"❌ No fallback version available for: {module_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Rollback error: {e}")
            return False
    
    def get_version_info(self, module_name: str) -> Dict[str, Any]:
        """Zwraca informacje o wersjach modułu"""
        return {
            'active': self.versions['active'].get(module_name, 'unknown'),
            'fallback': self.versions['fallback'].get(module_name, 'none'),
            'next_stable': self.versions['next_stable'].get(module_name, 'none')
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki"""
        return self.stats.copy()
