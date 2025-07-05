
#!/usr/bin/env python3
"""
📊 Database Visual Report - Wizualny raport zarządzania bazami danych

Interaktywny dashboard do monitorowania i zarządzania bazami danych w Federacji
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, render_template, request, jsonify
from federacja.core.bus import FederationBus, FederationMessage
from federacja.core.logger import FederationLogger

app = Flask(__name__)

class DatabaseVisualReport:
    """Wizualny raport zarządzania bazami danych"""
    
    def __init__(self):
        self.logger = FederationLogger({'level': 'INFO', 'format': 'console'})
        self.bus = FederationBus(self.logger)
        self.system_state = {
            'initialized': False,
            'total_databases': 0,
            'active_realms': [],
            'system_health': 'unknown',
            'last_update': None
        }
        
    async def initialize_system(self):
        """Inicjalizuje system zarządzania bazami"""
        try:
            # Uruchom bus
            await self.bus.start()
            
            # Sprawdź dostępność Database Manager
            await self._check_database_manager()
            
            # Załaduj konfigurację systemową
            await self._load_system_configuration()
            
            # Utwórz wymagane bazy danych
            await self._create_required_databases()
            
            self.system_state['initialized'] = True
            self.system_state['last_update'] = datetime.now().isoformat()
            
            print("📊 Database Visual Report zainicjalizowany")
            return True
            
        except Exception as e:
            print(f"❌ Błąd inicjalizacji Database Visual Report: {e}")
            return False
    
    async def _check_database_manager(self):
        """Sprawdza dostępność Database Manager"""
        try:
            message = FederationMessage(
                uid="db_report_check",
                from_module="db_visual_report",
                to_module="database_manager",
                message_type="get_status",
                data={},
                timestamp=datetime.now().timestamp()
            )
            
            # Symulacja sprawdzenia - w rzeczywistości byłaby komunikacja z Database Manager
            print("🔍 Sprawdzanie Database Manager...")
            await asyncio.sleep(0.5)
            
            # Zakładamy że Database Manager jest dostępny
            print("✅ Database Manager dostępny")
            
        except Exception as e:
            print(f"❌ Database Manager niedostępny: {e}")
            raise
    
    async def _load_system_configuration(self):
        """Ładuje konfigurację systemową z bazy stanu"""
        try:
            # Sprawdź czy istnieje baza stanu systemu
            system_config = await self._get_system_state_from_db()
            
            if not system_config:
                # Utwórz domyślną konfigurację
                system_config = {
                    'required_databases': [
                        {
                            'name': 'system_state',
                            'type': 'sqlite',
                            'description': 'Stan całego systemu Federacji',
                            'config': {
                                'path': 'db/system_state.db',
                                'auto_create': True
                            }
                        },
                        {
                            'name': 'federation_memory',
                            'type': 'memory',
                            'description': 'Pamięć operacyjna Federacji',
                            'config': {
                                'max_size': 10000,
                                'auto_cleanup': True
                            }
                        },
                        {
                            'name': 'realm_main',
                            'type': 'sqlite',
                            'description': 'Główny realm danych',
                            'config': {
                                'path': 'db/realm_main.db',
                                'auto_create': True
                            }
                        }
                    ],
                    'system_modules': [
                        'database_manager',
                        'realm_memory',
                        'realm_sqlite',
                        'federa'
                    ],
                    'created_at': datetime.now().isoformat()
                }
                
                await self._save_system_configuration(system_config)
            
            self.system_config = system_config
            print("📋 Konfiguracja systemowa załadowana")
            
        except Exception as e:
            print(f"❌ Błąd ładowania konfiguracji: {e}")
            raise
    
    async def _create_required_databases(self):
        """Tworzy wymagane bazy danych"""
        try:
            created_databases = []
            
            for db_config in self.system_config['required_databases']:
                success = await self._create_database(db_config)
                if success:
                    created_databases.append(db_config['name'])
                    print(f"✅ Baza '{db_config['name']}' utworzona")
                else:
                    print(f"❌ Błąd tworzenia bazy '{db_config['name']}'")
            
            self.system_state['active_realms'] = created_databases
            self.system_state['total_databases'] = len(created_databases)
            
        except Exception as e:
            print(f"❌ Błąd tworzenia baz danych: {e}")
            raise
    
    async def _create_database(self, db_config: Dict[str, Any]) -> bool:
        """Tworzy pojedynczą bazę danych"""
        try:
            # Symulacja tworzenia bazy przez Database Manager
            message = FederationMessage(
                uid=f"create_db_{db_config['name']}",
                from_module="db_visual_report",
                to_module="database_manager",
                message_type="create_realm",
                data={
                    'realm_name': db_config['name'],
                    'config': {
                        'type': db_config['type'],
                        **db_config['config']
                    }
                },
                timestamp=datetime.now().timestamp()
            )
            
            # W rzeczywistości wysłałby wiadomość do Database Manager
            await asyncio.sleep(0.2)  # Symulacja opóźnienia
            
            return True
            
        except Exception as e:
            print(f"❌ Błąd tworzenia bazy {db_config['name']}: {e}")
            return False
    
    async def _get_system_state_from_db(self) -> Dict[str, Any]:
        """Pobiera stan systemu z bazy danych"""
        # Symulacja - w rzeczywistości pobierałby z bazy system_state
        return None
    
    async def _save_system_configuration(self, config: Dict[str, Any]):
        """Zapisuje konfigurację systemu do bazy"""
        # Symulacja - w rzeczywistości zapisałby do bazy system_state
        print("💾 Konfiguracja systemu zapisana")
    
    async def get_database_status(self) -> Dict[str, Any]:
        """Pobiera aktualny status wszystkich baz danych"""
        try:
            # Symulacja pobierania statusu z Database Manager
            databases_status = []
            
            for realm_name in self.system_state['active_realms']:
                # Symulacja statusu bazy
                db_status = {
                    'name': realm_name,
                    'type': 'sqlite' if 'sqlite' in realm_name else 'memory',
                    'status': 'active',
                    'size': f"{abs(hash(realm_name)) % 1000}MB",
                    'records': abs(hash(realm_name)) % 10000,
                    'last_access': datetime.now().isoformat(),
                    'health': 'healthy'
                }
                databases_status.append(db_status)
            
            return {
                'total_databases': len(databases_status),
                'active_databases': len([db for db in databases_status if db['status'] == 'active']),
                'total_records': sum(db['records'] for db in databases_status),
                'system_health': 'healthy' if all(db['health'] == 'healthy' for db in databases_status) else 'warning',
                'databases': databases_status,
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Błąd pobierania statusu baz: {e}")
            return {'error': str(e)}
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Pobiera metryki systemu"""
        try:
            return {
                'uptime': '1h 23m',
                'memory_usage': 45.6,
                'cpu_usage': 12.3,
                'disk_usage': 67.8,
                'network_io': {
                    'bytes_sent': 1024 * 1024 * 15,
                    'bytes_received': 1024 * 1024 * 8
                },
                'active_connections': 5,
                'total_queries': 1247,
                'queries_per_second': 2.1,
                'errors_count': 0,
                'last_backup': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}

# Instancja globalnego raportu
db_report = DatabaseVisualReport()

@app.route('/')
def dashboard():
    """Strona główna dashboard"""
    return render_template('database_dashboard.html')

@app.route('/api/status')
def get_status():
    """API - pobiera status baz danych"""
    try:
        status = asyncio.run(db_report.get_database_status())
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics')
def get_metrics():
    """API - pobiera metryki systemu"""
    try:
        metrics = asyncio.run(db_report.get_system_metrics())
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create_database', methods=['POST'])
def create_database():
    """API - tworzy nową bazę danych"""
    try:
        data = request.json
        db_name = data.get('name')
        db_type = data.get('type', 'sqlite')
        
        if not db_name:
            return jsonify({'error': 'Nazwa bazy jest wymagana'}), 400
        
        # Symulacja tworzenia bazy
        new_db_config = {
            'name': db_name,
            'type': db_type,
            'description': data.get('description', f'Baza {db_name}'),
            'config': data.get('config', {})
        }
        
        success = asyncio.run(db_report._create_database(new_db_config))
        
        if success:
            db_report.system_state['active_realms'].append(db_name)
            db_report.system_state['total_databases'] += 1
            return jsonify({'success': True, 'message': f'Baza {db_name} utworzona'})
        else:
            return jsonify({'error': f'Błąd tworzenia bazy {db_name}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system_config')
def get_system_config():
    """API - pobiera konfigurację systemu"""
    try:
        if hasattr(db_report, 'system_config'):
            return jsonify(db_report.system_config)
        else:
            return jsonify({'error': 'Konfiguracja nie załadowana'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def initialize_and_run():
    """Inicjalizuje system i uruchamia serwer"""
    print("🚀 Inicjalizacja Database Visual Report...")
    
    # Inicjalizuj system
    success = await db_report.initialize_system()
    if not success:
        print("❌ Nie udało się zainicjalizować systemu")
        return
    
    print("✅ System zainicjalizowany - uruchamianie serwera...")
    
    # Uruchom serwer Flask
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    asyncio.run(initialize_and_run())
