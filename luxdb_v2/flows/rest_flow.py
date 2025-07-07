"""
🌐 RestFlow - Przepływ REST API

Zapewnia dostęp do systemu astralnego przez HTTP/REST
"""

import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import threading
import time


class RestFlow:
    """
    Przepływ REST - udostępnia funkcjonalność systemu przez HTTP API
    """

    def __init__(self, astral_engine, config: Dict[str, Any]):
        self.engine = astral_engine
        self.config = config
        self.app = Flask(__name__)

        # Konfiguracja CORS
        if config.get('enable_cors', True):
            CORS(self.app)

        self.host = config.get('host', '0.0.0.0')
        self.port = config.get('port', 5000)
        self.debug = config.get('debug', False)

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._setup_routes()

        self.request_count = 0
        self.start_time: Optional[datetime] = None

    def _setup_routes(self):
        """Konfiguruje wszystkie endpointy REST API"""

        @self.app.route('/astral/status', methods=['GET'])
        def get_status():
            """Status systemu astralnego"""
            try:
                status = self.engine.get_status()
                self.request_count += 1
                return jsonify({
                    'success': True,
                    'status': status,
                    'flow_info': {
                        'requests_served': self.request_count,
                        'uptime': str(datetime.now() - self.start_time) if self.start_time else '0:00:00'
                    }
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/astral/meditate', methods=['POST'])
        def meditate():
            """Medytacja systemu"""
            try:
                result = self.engine.meditate()
                self.request_count += 1
                return jsonify({
                    'success': True,
                    'meditation': result
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        # Endpointy dla kontenerów astralnych
        @self.app.route('/astral/ping', methods=['GET'])
        def ping():
            """Prosty ping do sprawdzenia dostępności"""
            return jsonify({
                'success': True,
                'message': 'Astra odpowiada',
                'timestamp': datetime.now().isoformat()
            })

        @self.app.route('/astral/health', methods=['GET'])
        def health_check():
            """Sprawdzanie zdrowia systemu"""
            try:
                # Podstawowe info o systemie
                health_info = {
                    'status': 'healthy',
                    'uptime': str(datetime.now() - self.start_time) if self.start_time else '0:00:00',
                    'active_realms': len(self.engine.realms),
                    'active_flows': self._count_active_flows(),
                    'requests_served': self.request_count
                }
                
                self.request_count += 1
                return jsonify({
                    'success': True,
                    'health': health_info
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        def _count_active_flows(self):
            """Liczy aktywne przepływy"""
            count = 0
            for flow_name, flow in self.engine.flows.items():
                if hasattr(flow, 'is_running') and flow.is_running():
                    count += 1
            return count

        @self.app.route('/realms', methods=['GET'])
        def list_realms():
            """Lista wszystkich wymiarów"""
            try:
                realms = self.engine.list_realms()
                realm_details = {}

                for realm_name in realms:
                    realm = self.engine.get_realm(realm_name)
                    if hasattr(realm, 'get_status'):
                        realm_details[realm_name] = realm.get_status()
                    else:
                        realm_details[realm_name] = {'name': realm_name, 'type': 'unknown'}

                self.request_count += 1
                return jsonify({
                    'success': True,
                    'realms': realm_details
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/realms/<realm_name>', methods=['GET'])
        def get_realm_status(realm_name):
            """Status konkretnego wymiaru"""
            try:
                realm = self.engine.get_realm(realm_name)
                status = realm.get_status() if hasattr(realm, 'get_status') else {'name': realm_name}

                self.request_count += 1
                return jsonify({
                    'success': True,
                    'realm': status
                })
            except ValueError as e:
                return jsonify({'success': False, 'error': str(e)}), 404
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/realms/<realm_name>/info', methods=['GET'])
        def get_realm_info(realm_name):
            """Podstawowe informacje o wymiarze (tylko do odczytu)"""
            try:
                realm = self.engine.get_realm(realm_name)
                
                # Tylko podstawowe info
                info = {
                    'name': realm_name,
                    'type': type(realm).__name__,
                    'supports_beings': hasattr(realm, 'manifestation')
                }
                
                if hasattr(realm, 'manifestation'):
                    info['beings_count'] = len(realm.manifestation.active_beings)
                
                self.request_count += 1
                return jsonify({
                    'success': True,
                    'realm_info': info
                })
                
            except ValueError as e:
                return jsonify({'success': False, 'error': str(e)}), 404
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'success': False,
                'error': 'Endpoint nie został znaleziony w astralnym przestrzeni',
                'available_endpoints': [
                    '/astral/status',
                    '/astral/ping',
                    '/astral/health',
                    '/astral/meditate',
                    '/realms',
                    '/realms/<realm_name>',
                    '/realms/<realm_name>/info',
                    '/flows/status'
                ]
            }), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'success': False,
                'error': 'Błąd astralnej energii w serwerze',
                'message': 'Sprawdź logi systemu'
            }), 500

        # Prosty endpoint do sprawdzania czy GPT Flow jest aktywny
        @self.app.route('/flows/status', methods=['GET'])
        def flows_status():
            """Status przepływów - tylko do odczytu"""
            try:
                flows_info = {}
                
                for flow_name, flow in self.engine.flows.items():
                    if hasattr(flow, 'get_status'):
                        flows_info[flow_name] = {
                            'type': flow.get_status().get('type', 'unknown'),
                            'running': flow.get_status().get('running', False)
                        }
                    else:
                        flows_info[flow_name] = {
                            'type': 'unknown',
                            'running': True  # Założenie że działa jeśli jest w słowniku
                        }
                
                self.request_count += 1
                return jsonify({
                    'success': True,
                    'flows': flows_info,
                    'count': len(flows_info)
                })

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

    def start(self, debug: bool = False) -> bool:
        """
        Uruchamia przepływ REST

        Args:
            debug: Tryb debug Flask
            
        Returns:
            True jeśli uruchomiono pomyślnie
        """
        if self._running:
            self.engine.logger.warning("RestFlow już działa")
            return True

        self.start_time = datetime.now()
        self._running = True

        def run_server():
            try:
                self.app.run(
                    host=self.host,
                    port=self.port,
                    debug=debug and self.debug,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                self.engine.logger.error(f"Błąd REST Flow: {e}")
                self._running = False

        self._thread = threading.Thread(target=run_server, daemon=True)
        self._thread.start()

        # Poczekaj na uruchomienie
        time.sleep(1)

        self.engine.logger.info(f"🌐 REST Flow aktywny na http://{self.host}:{self.port}")
        return True

    def stop(self) -> None:
        """Zatrzymuje przepływ REST"""
        self._running = False
        # Flask nie ma built-in sposobu na graceful shutdown w wątkach
        # W produkcji używałbyś gunicorn lub podobnego
        self.engine.logger.info("🌐 REST Flow zatrzymany")

    def is_running(self) -> bool:
        """Sprawdza czy przepływ działa"""
        return self._running

    def get_status(self) -> Dict[str, Any]:
        """Zwraca status przepływu"""
        return {
            'type': 'rest_flow',
            'running': self._running,
            'host': self.host,
            'port': self.port,
            'requests_served': self.request_count,
            'uptime': str(datetime.now() - self.start_time) if self.start_time else '0:00:00',
            'endpoints_count': len(self.app.url_map._rules)
        }

    def balance_load(self) -> None:
        """Balansuje obciążenie przepływu"""
        # Podstawowa implementacja - w przyszłości można dodać cache, rate limiting itp.
        if self.request_count > 1000:
            self.engine.logger.info("🌐 REST Flow: Wysokie obciążenie, rozważ optymalizację")