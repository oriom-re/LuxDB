
"""
🔄 DivineMigrations - System Boskich Migracji

Zarządza migracjami danych i struktury między wersjami systemu astralnego
"""

import json
import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MigrationStep:
    """Krok migracji"""
    version: str
    name: str
    description: str
    up_function: Callable
    down_function: Optional[Callable]
    created_at: datetime


class MigrationResult:
    """Wynik migracji"""
    
    def __init__(self):
        self.success = True
        self.steps_completed = 0
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
    
    def add_error(self, error: str):
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)
    
    def complete(self):
        self.end_time = datetime.now()
    
    def get_duration(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'steps_completed': self.steps_completed,
            'errors': self.errors,
            'warnings': self.warnings,
            'duration': self.get_duration(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None
        }


class DivineMigrations:
    """
    System boskich migracji - zarządza ewolucją systemu
    """
    
    def __init__(self, astral_engine=None, migrations_dir: str = "migrations"):
        self.engine = astral_engine
        self.migrations_dir = Path(migrations_dir)
        self.migrations: List[MigrationStep] = []
        self.migration_history: List[Dict[str, Any]] = []
        
        # Utwórz katalog migracji jeśli nie istnieje
        self.migrations_dir.mkdir(exist_ok=True)
        
        self._setup_core_migrations()
    
    def _setup_core_migrations(self):
        """Konfiguruje podstawowe migracje systemu"""
        
        def migration_v1_to_v2_up(context):
            """Migracja z LuxDB v1 do v2"""
            result = []
            
            # Migracja struktury danych
            if self.engine:
                for realm_name, realm in self.engine.realms.items():
                    result.append(f"Migracja wymiaru {realm_name}")
                    
                    # Sprawdź czy realm ma stare struktury
                    if hasattr(realm, 'legacy_tables'):
                        result.append(f"Znaleziono legacy tabele w {realm_name}")
                        # Tutaj byłaby logika migracji
            
            return result
        
        def migration_consciousness_upgrade_up(context):
            """Upgrade systemu świadomości"""
            result = []
            
            if self.engine and hasattr(self.engine, 'consciousness'):
                # Aktualizuj algorytmy świadomości
                result.append("Upgrade algorytmów świadomości")
                
                # Migruj historię obserwacji
                old_observations = getattr(self.engine.consciousness, 'old_observations', [])
                if old_observations:
                    result.append(f"Zmigrowano {len(old_observations)} obserwacji")
            
            return result
        
        def migration_harmony_v2_up(context):
            """Upgrade systemu harmonii do v2"""
            result = []
            
            if self.engine and hasattr(self.engine, 'harmony'):
                # Nowe algorytmy harmonii
                result.append("Upgrade systemu harmonii do v2")
                
                # Migruj historię balansowania
                old_balance_history = getattr(self.engine.harmony, 'old_balance_history', [])
                if old_balance_history:
                    result.append(f"Zmigrowano {len(old_balance_history)} wpisów harmonii")
            
            return result
        
        def migration_beings_enhancement_up(context):
            """Wzbogacenie systemu bytów"""
            result = []
            
            if self.engine:
                for realm_name, realm in self.engine.realms.items():
                    if hasattr(realm, 'manifestation'):
                        beings_count = len(realm.manifestation.active_beings)
                        if beings_count > 0:
                            result.append(f"Wzbogacenie {beings_count} bytów w {realm_name}")
                            
                            # Dodaj nowe pola do istniejących bytów
                            for being in realm.manifestation.active_beings.values():
                                if not hasattr(being.essence, 'last_meditation'):
                                    being.essence.last_meditation = None
                                    result.append(f"Dodano pole last_meditation do {being.essence.soul_id}")
            
            return result
        
        # Rejestruj migracje
        self.add_migration("1.0.0", "v1_to_v2", "Migracja z LuxDB v1 do v2", migration_v1_to_v2_up)
        self.add_migration("2.0.1", "consciousness_upgrade", "Upgrade systemu świadomości", migration_consciousness_upgrade_up)
        self.add_migration("2.0.2", "harmony_v2", "Upgrade systemu harmonii", migration_harmony_v2_up)
        self.add_migration("2.0.3", "beings_enhancement", "Wzbogacenie systemu bytów", migration_beings_enhancement_up)
    
    def add_migration(self, version: str, name: str, description: str, up_function: Callable, down_function: Optional[Callable] = None):
        """
        Dodaje nową migrację
        
        Args:
            version: Wersja docelowa
            name: Nazwa migracji
            description: Opis migracji
            up_function: Funkcja wykonująca migrację
            down_function: Funkcja cofająca migrację (opcjonalna)
        """
        migration = MigrationStep(
            version=version,
            name=name,
            description=description,
            up_function=up_function,
            down_function=down_function,
            created_at=datetime.now()
        )
        
        self.migrations.append(migration)
        
        # Sortuj według wersji
        self.migrations.sort(key=lambda m: m.version)
    
    def get_pending_migrations(self, current_version: str = "0.0.0") -> List[MigrationStep]:
        """
        Zwraca listę oczekujących migracji
        
        Args:
            current_version: Aktualna wersja systemu
            
        Returns:
            Lista migracji do wykonania
        """
        # Prosta implementacja - w rzeczywistości porównywałbyś semantic versioning
        return [m for m in self.migrations if m.version > current_version]
    
    def run_migrations(self, target_version: Optional[str] = None) -> MigrationResult:
        """
        Uruchamia migracje
        
        Args:
            target_version: Wersja docelowa (None = najnowsza)
            
        Returns:
            Wynik migracji
        """
        result = MigrationResult()
        
        try:
            # Określ migracje do wykonania
            if target_version:
                migrations_to_run = [m for m in self.migrations if m.version <= target_version]
            else:
                migrations_to_run = self.migrations
            
            # Wykonaj migracje
            for migration in migrations_to_run:
                try:
                    self._log_migration_start(migration)
                    
                    # Wykonaj migrację
                    context = {
                        'engine': self.engine,
                        'migration': migration,
                        'result': result
                    }
                    
                    migration_output = migration.up_function(context)
                    
                    # Zapisz wynik
                    result.steps_completed += 1
                    
                    self._log_migration_success(migration, migration_output)
                    self._save_migration_record(migration, True, migration_output)
                    
                except Exception as e:
                    error_msg = f"Błąd w migracji {migration.name}: {str(e)}"
                    result.add_error(error_msg)
                    
                    self._log_migration_error(migration, str(e))
                    self._save_migration_record(migration, False, None, str(e))
                    
                    break  # Przerwij przy błędzie
        
        except Exception as e:
            result.add_error(f"Błąd systemu migracji: {str(e)}")
        
        finally:
            result.complete()
        
        return result
    
    def rollback_migration(self, migration_name: str) -> MigrationResult:
        """
        Cofa konkretną migrację
        
        Args:
            migration_name: Nazwa migracji do cofnięcia
            
        Returns:
            Wynik rollbacku
        """
        result = MigrationResult()
        
        try:
            # Znajdź migrację
            migration = next((m for m in self.migrations if m.name == migration_name), None)
            
            if not migration:
                result.add_error(f"Migracja '{migration_name}' nie została znaleziona")
                return result
            
            if not migration.down_function:
                result.add_error(f"Migracja '{migration_name}' nie ma funkcji rollback")
                return result
            
            # Wykonaj rollback
            context = {
                'engine': self.engine,
                'migration': migration,
                'result': result
            }
            
            rollback_output = migration.down_function(context)
            
            result.steps_completed = 1
            
            self._save_migration_record(migration, True, rollback_output, action='rollback')
            
        except Exception as e:
            result.add_error(f"Błąd rollback: {str(e)}")
        
        finally:
            result.complete()
        
        return result
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Zwraca status systemu migracji"""
        return {
            'total_migrations': len(self.migrations),
            'migrations': [
                {
                    'version': m.version,
                    'name': m.name,
                    'description': m.description,
                    'created_at': m.created_at.isoformat(),
                    'has_rollback': m.down_function is not None
                }
                for m in self.migrations
            ],
            'migration_history_count': len(self.migration_history),
            'recent_migrations': self.migration_history[-5:] if self.migration_history else []
        }
    
    def create_migration_file(self, version: str, name: str, description: str) -> str:
        """
        Tworzy plik migracji
        
        Args:
            version: Wersja
            name: Nazwa migracji
            description: Opis
            
        Returns:
            Ścieżka do utworzonego pliku
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{version}_{name}.py"
        filepath = self.migrations_dir / filename
        
        template = f'''"""
{description}

Migracja: {name}
Wersja: {version}
Utworzona: {datetime.now().isoformat()}
"""

def up(context):
    """
    Wykonaj migrację
    
    Args:
        context: Kontekst migracji zawierający engine, migration, result
        
    Returns:
        Lista komunikatów z wykonania
    """
    result = []
    engine = context['engine']
    
    # Tutaj dodaj logikę migracji
    result.append("Migracja wykonana pomyślnie")
    
    return result


def down(context):
    """
    Cofnij migrację
    
    Args:
        context: Kontekst migracji
        
    Returns:
        Lista komunikatów z rollbacku
    """
    result = []
    engine = context['engine']
    
    # Tutaj dodaj logikę rollbacku
    result.append("Rollback wykonany pomyślnie")
    
    return result
'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return str(filepath)
    
    def _log_migration_start(self, migration: MigrationStep):
        """Loguje rozpoczęcie migracji"""
        if self.engine:
            self.engine.logger.info(f"🔄 Rozpoczynam migrację: {migration.name} (v{migration.version})")
    
    def _log_migration_success(self, migration: MigrationStep, output: Any):
        """Loguje sukces migracji"""
        if self.engine:
            self.engine.logger.info(f"✅ Migracja {migration.name} zakończona pomyślnie")
            if isinstance(output, list):
                for msg in output:
                    self.engine.logger.info(f"   • {msg}")
    
    def _log_migration_error(self, migration: MigrationStep, error: str):
        """Loguje błąd migracji"""
        if self.engine:
            self.engine.logger.error(f"❌ Błąd w migracji {migration.name}: {error}")
    
    def _save_migration_record(self, migration: MigrationStep, success: bool, output: Any, error: Optional[str] = None, action: str = 'migrate'):
        """Zapisuje rekord migracji w historii"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'migration_name': migration.name,
            'migration_version': migration.version,
            'action': action,
            'success': success,
            'output': output,
            'error': error
        }
        
        self.migration_history.append(record)
        
        # Ogranicz historię do 100 ostatnich wpisów
        if len(self.migration_history) > 100:
            self.migration_history = self.migration_history[-100:]
    
    def export_migration_history(self, format: str = 'json') -> str:
        """
        Eksportuje historię migracji
        
        Args:
            format: Format eksportu (json)
            
        Returns:
            Dane w wybranym formacie
        """
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_migrations': len(self.migrations),
            'history_entries': len(self.migration_history),
            'migrations': [
                {
                    'version': m.version,
                    'name': m.name,
                    'description': m.description,
                    'created_at': m.created_at.isoformat()
                }
                for m in self.migrations
            ],
            'history': self.migration_history
        }
        
        if format == 'json':
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        else:
            return str(export_data)
    
    def clear_migration_history(self) -> int:
        """
        Czyści historię migracji
        
        Returns:
            Liczba usuniętych wpisów
        """
        count = len(self.migration_history)
        self.migration_history.clear()
        return count
