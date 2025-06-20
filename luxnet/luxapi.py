
"""
LuxAPI - REST API Server dla LuxDB
Zapewnia HTTP endpoints do zarządzania bazami danych
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
from datetime import datetime
from typing import Dict, List, Any, Optional

from .manager import get_db_manager
from .session_manager import get_session_manager
from .models import User, UserSession, Log
from .utils.error_handlers import LuxDBError, handle_database_errors
from .utils.logging_utils import get_db_logger

logger = get_db_logger()

class LuxAPI:
    """
    REST API serwer dla LuxDB z endpoints:
    - Zarządzanie bazami danych
    - CRUD operacje na danych
    - Uwierzytelnianie i sesje
    - Monitoring i statystyki
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'luxapi_secret_key_change_in_production'
        
        # Włącz CORS dla wszystkich endpoints
        CORS(self.app)
        
        self.host = host
        self.port = port
        self.db_manager = get_db_manager()
        self.session_manager = get_session_manager()
        
        self._setup_routes()
        self._setup_error_handlers()
    
    def _auth_required(self, f):
        """Dekorator wymagający uwierzytelnienia"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if token and token.startswith('Bearer '):
                token = token[7:]  # Usuń 'Bearer '
            
            if not token:
                return jsonify({'error': 'Brak tokenu autoryzacji'}), 401
            
            session_data = self.session_manager.validate_session(token)
            if not session_data:
                return jsonify({'error': 'Nieprawidłowy lub wygasły token'}), 401
            
            g.user_id = session_data['user_id']
            g.session_data = session_data
            return f(*args, **kwargs)
        return decorated_function
    
    def _setup_routes(self):
        """Konfiguruje wszystkie endpoints API"""
        
        # === AUTH ENDPOINTS ===
        @self.app.route('/api/auth/login', methods=['POST'])
        def login():
            """Logowanie użytkownika"""
            try:
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
                
                if not username or not password:
                    return jsonify({'error': 'Wymagane username i password'}), 400
                
                user_data = self.session_manager.authenticate_user(username, password)
                session_token = self.session_manager.create_session(
                    user_id=user_data['id'],
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
                
                return jsonify({
                    'success': True,
                    'token': session_token,
                    'user': user_data,
                    'expires_in': 86400  # 24 godziny
                }), 200
                
            except Exception as e:
                logger.log_error("Błąd logowania", e)
                return jsonify({'error': str(e)}), 400
        
        @self.app.route('/api/auth/logout', methods=['POST'])
        @self._auth_required
        def logout():
            """Wylogowanie użytkownika"""
            try:
                token = request.headers.get('Authorization')[7:]
                self.session_manager.destroy_session(token)
                return jsonify({'success': True, 'message': 'Wylogowano pomyślnie'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        @self.app.route('/api/auth/register', methods=['POST'])
        def register():
            """Rejestracja nowego użytkownika"""
            try:
                data = request.get_json()
                username = data.get('username')
                email = data.get('email')
                password = data.get('password')
                
                if not all([username, email, password]):
                    return jsonify({'error': 'Wymagane username, email i password'}), 400
                
                user_id = self.session_manager.create_user(username, email, password)
                return jsonify({
                    'success': True,
                    'user_id': user_id,
                    'message': 'Użytkownik utworzony pomyślnie'
                }), 201
                
            except Exception as e:
                logger.log_error("Błąd rejestracji", e)
                return jsonify({'error': str(e)}), 400
        
        @self.app.route('/api/auth/me', methods=['GET'])
        @self._auth_required
        def get_current_user():
            """Pobiera dane aktualnego użytkownika"""
            try:
                with self.session_manager.user_context(request.headers.get('Authorization')[7:]) as user:
                    return jsonify({
                        'success': True,
                        'user': {
                            'id': user['id'],
                            'username': user['username'],
                            'email': user['email']
                        }
                    }), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        # === DATABASE ENDPOINTS ===
        @self.app.route('/api/databases', methods=['GET'])
        @self._auth_required
        def list_databases():
            """Lista wszystkich baz danych"""
            try:
                databases = self.db_manager.list_databases()
                db_info = []
                
                for db_name in databases:
                    info = self.db_manager.get_database_info(db_name)
                    db_info.append(info)
                
                return jsonify({
                    'success': True,
                    'databases': db_info
                }), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/databases', methods=['POST'])
        @self._auth_required
        def create_database():
            """Tworzy nową bazę danych"""
            try:
                data = request.get_json()
                db_name = data.get('name')
                
                if not db_name:
                    return jsonify({'error': 'Wymagana nazwa bazy danych'}), 400
                
                success = self.db_manager.create_database(db_name)
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Baza danych {db_name} została utworzona'
                    }), 201
                else:
                    return jsonify({'error': 'Nie udało się utworzyć bazy danych'}), 500
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/databases/<db_name>', methods=['GET'])
        @self._auth_required
        def get_database_info(db_name):
            """Pobiera informacje o bazie danych"""
            try:
                info = self.db_manager.get_database_info(db_name)
                if info:
                    return jsonify({
                        'success': True,
                        'database': info
                    }), 200
                else:
                    return jsonify({'error': 'Baza danych nie istnieje'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/databases/<db_name>/optimize', methods=['POST'])
        @self._auth_required
        def optimize_database(db_name):
            """Optymalizuje bazę danych"""
            try:
                success = self.db_manager.optimize_database(db_name)
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Baza danych {db_name} została zoptymalizowana'
                    }), 200
                else:
                    return jsonify({'error': 'Nie udało się zoptymalizować bazy'}), 500
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/databases/<db_name>/export', methods=['POST'])
        @self._auth_required
        def export_database(db_name):
            """Eksportuje bazę danych"""
            try:
                data = request.get_json() or {}
                format = data.get('format', 'json')
                
                export_path = self.db_manager.export_database(db_name, format)
                if export_path:
                    return jsonify({
                        'success': True,
                        'export_path': export_path,
                        'message': f'Baza danych {db_name} została wyeksportowana'
                    }), 200
                else:
                    return jsonify({'error': 'Nie udało się wyeksportować bazy'}), 500
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # === SQL ENDPOINTS ===
        @self.app.route('/api/databases/<db_name>/query', methods=['POST'])
        @self._auth_required
        def execute_query(db_name):
            """Wykonuje zapytanie SQL"""
            try:
                data = request.get_json()
                sql = data.get('sql')
                params = data.get('params', {})
                
                if not sql:
                    return jsonify({'error': 'Wymagane zapytanie SQL'}), 400
                
                result = self.db_manager.execute_raw_sql(db_name, sql, params)
                return jsonify({
                    'success': True,
                    'result': result,
                    'row_count': len(result) if isinstance(result, list) else 0
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # === MIGRATION ENDPOINTS ===
        @self.app.route('/api/databases/<db_name>/migrate', methods=['POST'])
        @self._auth_required
        def create_migration(db_name):
            """Tworzy migrację bazy danych"""
            try:
                data = request.get_json()
                migration_sql = data.get('sql')
                description = data.get('description', '')
                
                if not migration_sql:
                    return jsonify({'error': 'Wymagany SQL migracji'}), 400
                
                success = self.db_manager.create_migration(db_name, migration_sql, description)
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Migracja wykonana pomyślnie'
                    }), 200
                else:
                    return jsonify({'error': 'Nie udało się wykonać migracji'}), 500
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # === HEALTH CHECK ===
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Sprawdzenie stanu serwera"""
            return jsonify({
                'status': 'healthy',
                'service': 'LuxAPI',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'databases': len(self.db_manager.list_databases())
            }), 200
        
        # === ROOT ===
        @self.app.route('/', methods=['GET'])
        def root():
            """Główny endpoint"""
            return jsonify({
                'service': 'LuxAPI',
                'version': '1.0.0',
                'description': 'REST API dla LuxDB - Astralnej Biblioteki Danych',
                'endpoints': {
                    'auth': '/api/auth/*',
                    'databases': '/api/databases/*',
                    'health': '/api/health'
                }
            }), 200
    
    def _setup_error_handlers(self):
        """Konfiguruje globalne handlery błędów"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint nie został znaleziony'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({'error': 'Wewnętrzny błąd serwera'}), 500
        
        @self.app.errorhandler(LuxDBError)
        def handle_luxdb_error(error):
            return jsonify({'error': str(error)}), 400
    
    def run(self, debug: bool = False):
        """Uruchamia serwer API"""
        logger.log_info(f"Uruchamianie LuxAPI na {self.host}:{self.port}")
        self.app.run(host="0.0.0.0", port=self.port, debug=debug)

# Singleton instance
_luxapi_instance = None

def get_luxapi() -> LuxAPI:
    """Zwraca singleton instance LuxAPI"""
    global _luxapi_instance
    if _luxapi_instance is None:
        _luxapi_instance = LuxAPI()
    return _luxapi_instance
