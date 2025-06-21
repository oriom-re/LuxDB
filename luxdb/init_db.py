
#!/usr/bin/env python3
"""
LuxDB Database Initialization Service
Serwis inicjalizacji bazy danych dla środowiska VM
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List

# Dodaj ścieżkę do modułów LuxDB
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luxdb.config import DatabaseConfig, DatabaseType, DEFAULT_CONFIGS, Base
from luxdb.manager import DatabaseManager
from luxdb.models.luxsafe import LuxSafeProfile, SoulName, ClientIdentity
from luxdb.session_manager import SessionManager
from luxdb.utils.logging_utils import DatabaseLogger

class DatabaseInitService:
    """Serwis inicjalizacji i konfiguracji baz danych"""
    
    def __init__(self):
        self.logger = DatabaseLogger("DB_INIT_SERVICE")
        self.db_manager = DatabaseManager()
        self.session_manager = SessionManager()
        
    def create_database_configs(self) -> Dict[str, DatabaseConfig]:
        """Tworzy konfiguracje dla wszystkich baz danych"""
        configs = {
            # Baza uwierzytelniania
            "auth": DatabaseConfig(
                name="auth",
                type=DatabaseType.SQLITE,
                max_connections=15,
                backup_enabled=True,
                auto_optimize=True,
                connection_string="sqlite:///db/luxdb_auth.db"
            ),
            
            # Baza systemowa
            "system": DatabaseConfig(
                name="system",
                type=DatabaseType.SQLITE,
                max_connections=20,
                backup_enabled=True,
                auto_optimize=True,
                connection_string="sqlite:///db/luxdb_system.db"
            ),
            
            # Baza główna aplikacji
            "main": DatabaseConfig(
                name="main",
                type=DatabaseType.SQLITE,
                max_connections=25,
                backup_enabled=True,
                auto_optimize=True,
                connection_string="sqlite:///db/luxdb_main.db"
            ),
            
            # Baza analityczna
            "analytics": DatabaseConfig(
                name="analytics",
                type=DatabaseType.SQLITE,
                max_connections=10,
                backup_enabled=True,
                auto_optimize=True,
                connection_string="sqlite:///db/luxdb_analytics.db"
            ),
            
            # Baza cache'u
            "cache": DatabaseConfig(
                name="cache",
                type=DatabaseType.SQLITE,
                max_connections=5,
                backup_enabled=False,
                auto_optimize=False,
                connection_string="sqlite:///db/luxdb_cache.db"
            ),
            
            # Baza logów
            "logs": DatabaseConfig(
                name="logs",
                type=DatabaseType.SQLITE,
                max_connections=8,
                backup_enabled=True,
                auto_optimize=True,
                connection_string="sqlite:///db/luxdb_logs.db"
            )
        }
        
        return configs
    
    def ensure_database_directory(self):
        """Upewnia się, że katalog bazy danych istnieje"""
        db_dir = "db"
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            self.logger.log_info(f"Utworzono katalog bazy danych: {db_dir}")
    
    def initialize_databases(self) -> bool:
        """Inicjalizuje wszystkie bazy danych"""
        try:
            self.logger.log_info("🚀 Rozpoczynam inicjalizację baz danych LuxDB")
            
            # Upewnij się, że katalog istnieje
            self.ensure_database_directory()
            
            # Pobierz konfiguracje
            configs = self.create_database_configs()
            
            # Inicjalizuj każdą bazę danych
            for db_name, config in configs.items():
                self.logger.log_info(f"📊 Inicjalizuję bazę danych: {db_name}")
                
                try:
                    # Dodaj konfigurację do managera
                    self.db_manager.add_database(config)
                    
                    # Utwórz tabele
                    self.db_manager.create_tables(db_name)
                    
                    self.logger.log_info(f"✅ Baza danych '{db_name}' została zainicjalizowana")
                    
                except Exception as e:
                    self.logger.log_error(f"initialize_database_{db_name}", e, context={"database": db_name}, error_code="DB_INIT_ERROR")
                    return False
            
            # Wypełnij wstępnymi danymi
            self.populate_initial_data()
            
            self.logger.log_info("🌟 Wszystkie bazy danych zostały pomyślnie zainicjalizowane")
            return True
            
        except Exception as e:
            self.logger.log_error("initialize_databases", e, context={"operation": "full_initialization"}, error_code="INIT_GENERAL_ERROR")
            return False
    
    def populate_initial_data(self):
        """Wypełnia bazy danych wstępnymi danymi"""
        self.logger.log_info("📝 Wypełniam bazy danych wstępnymi danymi")
        
        try:
            # Inicjalizuj dane uwierzytelniania
            self._init_auth_data()
            
            # Inicjalizuj dane systemowe
            self._init_system_data()
            
            # Inicjalizuj dane analityczne
            self._init_analytics_data()
            
        except Exception as e:
            self.logger.log_error("populate_initial_data", e, context={"operation": "initial_data_population"}, error_code="DATA_POPULATION_ERROR")
    
    def _init_auth_data(self):
        """Inicjalizuje dane uwierzytelniania"""
        try:
            with self.db_manager.get_session("auth") as session:
                # Sprawdź czy istnieją już profile
                existing_profiles = session.query(LuxSafeProfile).count()
                
                if existing_profiles == 0:
                    # Utwórz administratora systemu
                    admin_profile = LuxSafeProfile(
                        struna_code="⊕⟁❖◬➰☼",
                        pin="7777",
                        trust_level=7,  # Najwyższy poziom
                        soul_mode="guardian",
                        access_rights=[
                            "admin.full",
                            "system.manage",
                            "auth.manage",
                            "database.admin",
                            "migration.execute"
                        ],
                        astral_signature={
                            "glyph": "ΩΞΛ⋄☆",
                            "color": "#gold",
                            "emotion_wave": "divine_protection"
                        },
                        resonance_strength=3.0
                    )
                    
                    session.add(admin_profile)
                    
                    # Dodaj nazwę duszy dla administratora
                    admin_soul_name = SoulName(
                        profile_id=admin_profile.id,
                        name="System_Guardian_Ω",
                        kind="primary",
                        source="system"
                    )
                    
                    session.add(admin_soul_name)
                    
                    # Utwórz profil gościa systemu
                    guest_profile = LuxSafeProfile(
                        struna_code="○◇△☽",
                        pin="1111",
                        trust_level=1,
                        soul_mode="visitor",
                        access_rights=[
                            "entry.read",
                            "public.view"
                        ],
                        astral_signature={
                            "glyph": "○◇△",
                            "color": "#silver",
                            "emotion_wave": "gentle_curiosity"
                        },
                        resonance_strength=1.0
                    )
                    
                    session.add(guest_profile)
                    
                    # Dodaj nazwę duszy dla gościa
                    guest_soul_name = SoulName(
                        profile_id=guest_profile.id,
                        name="Wanderer_Guest",
                        kind="primary",
                        source="system"
                    )
                    
                    session.add(guest_soul_name)
                    
                    session.commit()
                    self.logger.log_info("✨ Utworzono wstępne profile uwierzytelniania")
                
        except Exception as e:
            self.logger.log_error("init_auth_data", e, context={"operation": "auth_data_initialization"}, error_code="AUTH_INIT_ERROR")
    
    def _init_system_data(self):
        """Inicjalizuje dane systemowe"""
        try:
            # Tutaj można dodać wstępne konfiguracje systemowe
            # Np. tabele konfiguracyjne, ustawienia systemowe, itp.
            self.logger.log_info("⚙️ Zainicjalizowano dane systemowe")
            
        except Exception as e:
            self.logger.log_error("init_system_data", e, context={"operation": "system_data_initialization"}, error_code="SYSTEM_INIT_ERROR")
    
    def _init_analytics_data(self):
        """Inicjalizuje struktury analityczne"""
        try:
            # Tutaj można dodać wstępne struktury dla analityki
            # Np. tabele metryk, dashboardy, raporty
            self.logger.log_info("📈 Zainicjalizowano struktury analityczne")
            
        except Exception as e:
            self.logger.log_error("init_analytics_data", e, context={"operation": "analytics_data_initialization"}, error_code="ANALYTICS_INIT_ERROR")
    
    def verify_initialization(self) -> bool:
        """Weryfikuje poprawność inicjalizacji"""
        try:
            self.logger.log_info("🔍 Weryfikuję inicjalizację baz danych")
            
            # Sprawdź czy wszystkie bazy są dostępne
            databases = self.db_manager.list_databases()
            expected_databases = ["auth", "system", "main", "analytics", "cache", "logs"]
            
            for db_name in expected_databases:
                if db_name not in databases:
                    self.logger.log_error("verification", f"Baza {db_name} nie została znaleziona", context={"missing_database": db_name}, error_code="DB_MISSING_ERROR")
                    return False
            
            # Sprawdź czy tabele zostały utworzone
            with self.db_manager.get_session("auth") as session:
                profile_count = session.query(LuxSafeProfile).count()
                if profile_count < 2:  # Admin + Guest
                    self.logger.log_error("verification", "Niepoprawna liczba profili początkowych", context={"profile_count": profile_count}, error_code="PROFILE_COUNT_ERROR")
                    return False
            
            self.logger.log_info("✅ Weryfikacja zakończona pomyślnie")
            return True
            
        except Exception as e:
            self.logger.log_error("verify_initialization", e, context={"operation": "verification"}, error_code="VERIFICATION_ERROR")
            return False
    
    def get_status_report(self) -> Dict:
        """Zwraca raport statusu inicjalizacji"""
        try:
            databases = self.db_manager.list_databases()
            
            status = {
                "timestamp": datetime.now().isoformat(),
                "databases_count": len(databases),
                "databases": databases,
                "initialization_complete": len(databases) >= 6,
                "auth_profiles": 0,
                "system_status": "operational"
            }
            
            # Sprawdź profile uwierzytelniania
            try:
                with self.db_manager.get_session("auth") as session:
                    status["auth_profiles"] = session.query(LuxSafeProfile).count()
            except:
                status["auth_profiles"] = 0
            
            return status
            
        except Exception as e:
            self.logger.log_error("get_status_report", e, context={"operation": "status_report"}, error_code="STATUS_REPORT_ERROR")
            return {"error": str(e)}
    
    def cleanup_and_reinitialize(self):
        """Czyści i reinicjalizuje bazy danych (UWAGA: usuwa wszystkie dane!)"""
        self.logger.log_info("🗑️ UWAGA: Rozpoczynam pełne wyczyszczenie i reinicjalizację")
        
        try:
            # Zamknij wszystkie połączenia
            self.db_manager.close_all()
            
            # Usuń pliki baz danych
            db_files = [
                "db/luxdb_auth.db",
                "db/luxdb_system.db", 
                "db/luxdb_main.db",
                "db/luxdb_analytics.db",
                "db/luxdb_cache.db",
                "db/luxdb_logs.db"
            ]
            
            for db_file in db_files:
                if os.path.exists(db_file):
                    os.remove(db_file)
                    self.logger.log_info(f"🗑️ Usunięto: {db_file}")
            
            # Reinicjalizuj
            return self.initialize_databases()
            
        except Exception as e:
            self.logger.log_error("cleanup_and_reinitialize", e, context={"operation": "cleanup_and_reinit"}, error_code="CLEANUP_ERROR")
            return False

def main():
    """Główna funkcja serwisu inicjalizacji"""
    print("🌟 LuxDB Database Initialization Service")
    print("=" * 50)
    
    init_service = DatabaseInitService()
    
    # Sprawdź argumenty wiersza poleceń
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clean":
            print("⚠️ Czysto reinicjalizuję bazy danych...")
            if init_service.cleanup_and_reinitialize():
                print("✅ Reinicjalizacja zakończona pomyślnie")
            else:
                print("❌ Błąd podczas reinicjalizacji")
                sys.exit(1)
                
        elif command == "verify":
            print("🔍 Weryfikuję status baz danych...")
            if init_service.verify_initialization():
                print("✅ Wszystkie bazy danych są prawidłowo zainicjalizowane")
            else:
                print("❌ Problemy z inicjalizacją baz danych")
                sys.exit(1)
                
        elif command == "status":
            print("📊 Raport statusu:")
            status = init_service.get_status_report()
            for key, value in status.items():
                print(f"  {key}: {value}")
                
        else:
            print(f"❌ Nieznane polecenie: {command}")
            print("Dostępne polecenia: clean, verify, status")
            sys.exit(1)
    else:
        # Normalna inicjalizacja
        if init_service.initialize_databases():
            if init_service.verify_initialization():
                print("🎉 Inicjalizacja baz danych LuxDB zakończona pomyślnie!")
                
                # Pokaż raport statusu
                status = init_service.get_status_report()
                print("\n📊 Raport statusu:")
                print(f"  Bazy danych: {status['databases_count']}")
                print(f"  Profile uwierzytelniania: {status['auth_profiles']}")
                print(f"  Status systemu: {status['system_status']}")
            else:
                print("❌ Weryfikacja nie powiodła się")
                sys.exit(1)
        else:
            print("❌ Inicjalizacja nie powiodła się")
            sys.exit(1)

if __name__ == "__main__":
    main()
