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
        @self.app.route('/astral/containers', methods=['POST'])
        def create_container():
            """Tworzy nowy kontener astralny"""
            try:
                data = request.get_json() or {}
                initial_data = data.get('data', {})
                origin_function = data.get('origin_function')
                purpose = data.get('purpose', 'api_call')

                container = self.engine.create_astral_container(initial_data, origin_function, purpose)

                if container:
                    self.request_count += 1
                    return jsonify({
                        'success': True,
                        'container_id': container.container_id,
                        'container_summary': container.get_history_summary()
                    })
                else:
                    return jsonify({'success': False, 'error': 'Nie można utworzyć kontenera'}), 500

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/astral/containers/<container_id>', methods=['GET'])
        def get_container(container_id):
            """Pobiera informacje o kontenerze"""
            try:
                container = self.engine.get_astral_container(container_id)

                if container:
                    self.request_count += 1
                    return jsonify({
                        'success': True,
                        'container': container.get_full_history()
                    })
                else:
                    return jsonify({'success': False, 'error': 'Kontener nie znaleziony'}), 404

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/astral/containers', methods=['GET'])
        def list_containers():
            """Listuje aktywne kontenery"""
            try:
                containers = self.engine.list_astral_containers()
                self.request_count += 1
                return jsonify({
                    'success': True,
                    'containers': containers,
                    'statistics': self.engine.get_container_statistics()
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/astral/containers/<container_id>/invoke/<function_name>', methods=['POST'])
        def invoke_function_with_container(container_id, function_name):
            """Wywołuje funkcję z kontenerem astralnym"""
            try:
                data = request.get_json() or {}
                expected_params = data.get('expected_params')

                container = self.engine.get_astral_container(container_id)
                if not container:
                    return jsonify({'success': False, 'error': 'Kontener nie znaleziony'}), 404

                result = self.engine.invoke_function_with_container(function_name, container, expected_params)
                self.request_count += 1

                return jsonify(result)

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/astral/invoke/<function_name>', methods=['POST'])
        def smart_invoke_function(function_name):
            """Inteligentne wywołanie funkcji z automatycznym kontenerem"""
            try:
                data = request.get_json() or {}
                function_data = data.get('data', {})
                expected_params = data.get('expected_params')

                result = self.engine.invoke_function_with_container(function_name, function_data, expected_params)
                self.request_count += 1

                return jsonify(result)

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/astral/harmonize', methods=['POST'])
        def harmonize():
            """Harmonizuje system"""
            try:
                harmony_result = self.engine.harmony.harmonize()
                self.request_count += 1
                return jsonify({
                    'success': True,
                    'harmony': harmony_result
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

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

        @self.app.route('/realms/<realm_name>/beings', methods=['GET'])
        def list_beings(realm_name):
            """Lista bytów w wymiarze"""
            try:
                realm = self.engine.get_realm(realm_name)

                if hasattr(realm, 'manifestation'):
                    beings = realm.manifestation.active_beings
                    beings_data = {
                        soul_id: being.get_status() 
                        for soul_id, being in beings.items()
                    }

                    self.request_count += 1
                    return jsonify({
                        'success': True,
                        'realm': realm_name,
                        'beings': beings_data,
                        'count': len(beings_data)
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Wymiar nie obsługuje bytów'
                    }), 400

            except ValueError as e:
                return jsonify({'success': False, 'error': str(e)}), 404
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/realms/<realm_name>/beings', methods=['POST'])
        def manifest_being(realm_name):
            """Manifestuje nowy byt w wymiarze"""
            try:
                realm = self.engine.get_realm(realm_name)

                if not hasattr(realm, 'manifestation'):
                    return jsonify({
                        'success': False,
                        'error': 'Wymiar nie obsługuje manifestacji bytów'
                    }), 400

                data = request.get_json()
                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'Brak danych do manifestacji'
                    }), 400

                being = realm.manifestation.manifest(data)

                self.request_count += 1
                return jsonify({
                    'success': True,
                    'being': being.get_status(),
                    'message': f'Byt zmanifestowany w wymiarze {realm_name}'
                }), 201

            except ValueError as e:
                return jsonify({'success': False, 'error': str(e)}), 404
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/realms/<realm_name>/beings/<soul_id>', methods=['GET'])
        def get_being(realm_name, soul_id):
            """Pobiera konkretny byt"""
            try:
                realm = self.engine.get_realm(realm_name)

                if not hasattr(realm, 'manifestation'):
                    return jsonify({
                        'success': False,
                        'error': 'Wymiar nie obsługuje bytów'
                    }), 400

                being = realm.manifestation.find_being(soul_id)
                if not being:
                    return jsonify({
                        'success': False,
                        'error': 'Byt nie został znaleziony'
                    }), 404

                self.request_count += 1
                return jsonify({
                    'success': True,
                    'being': being.get_status()
                })

            except ValueError as e:
                return jsonify({'success': False, 'error': str(e)}), 404
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/realms/<realm_name>/beings/<soul_id>', methods=['PUT'])
        def evolve_being(realm_name, soul_id):
            """Ewoluuje byt"""
            try:
                realm = self.engine.get_realm(realm_name)

                if not hasattr(realm, 'manifestation'):
                    return jsonify({
                        'success': False,
                        'error': 'Wymiar nie obsługuje bytów'
                    }), 400

                data = request.get_json()
                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'Brak danych do ewolucji'
                    }), 400

                being = realm.manifestation.evolve_being(soul_id, data)
                if not being:
                    return jsonify({
                        'success': False,
                        'error': 'Byt nie został znaleziony'
                    }), 404

                self.request_count += 1
                return jsonify({
                    'success': True,
                    'being': being.get_status(),
                    'message': 'Byt uległ ewolucji'
                })

            except ValueError as e:
                return jsonify({'success': False, 'error': str(e)}), 404
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/realms/<realm_name>/beings/<soul_id>', methods=['DELETE'])
        def transcend_being(realm_name, soul_id):
            """Transcenduje byt"""
            try:
                realm = self.engine.get_realm(realm_name)

                if not hasattr(realm, 'manifestation'):
                    return jsonify({
                        'success': False,
                        'error': 'Wymiar nie obsługuje bytów'
                    }), 400

                result = realm.manifestation.transcend_being(soul_id)

                self.request_count += 1
                return jsonify({
                    'success': result['success'],
                    'transcendence': result
                })

            except ValueError as e:
                return jsonify({'success': False, 'error': str(e)}), 404
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/realms/<realm_name>/contemplate', methods=['POST'])
        def contemplate(realm_name):
            """Kontemplacja - wyszukiwanie bytów"""
            try:
                realm = self.engine.get_realm(realm_name)

                if not hasattr(realm, 'manifestation'):
                    return jsonify({
                        'success': False,
                        'error': 'Wymiar nie obsługuje kontemplacji'
                    }), 400

                data = request.get_json() or {}
                intention = data.get('intention', 'find_beings')
                criteria = data.get('criteria', {})

                beings = realm.manifestation.contemplate(intention, criteria)
                beings_data = [being.get_status() for being in beings]

                self.request_count += 1
                return jsonify({
                    'success': True,
                    'intention': intention,
                    'criteria': criteria,
                    'beings': beings_data,
                    'count': len(beings_data)
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
                    '/astral/meditate',
                    '/astral/harmonize',
                    '/realms',
                    '/realms/<realm_name>',
                    '/realms/<realm_name>/beings',
                    '/realms/<realm_name>/contemplate'
                ]
            }), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'success': False,
                'error': 'Błąd astralnej energii w serwerze',
                'message': 'Sprawdź logi systemu'
            }), 500

        @self.app.route('/gpt/chat', methods=['POST'])
        def chat_with_astra():
            """Chat z Astrą przez GPT"""
            try:
                data = request.get_json()
                user_message = data.get('message', '')
                user_id = data.get('user_id', 'anonymous')

                if not user_message:
                    return jsonify({
                        'success': False,
                        'error': 'Brak wiadomości'
                    }), 400

                if not self.engine.gpt_flow:
                    return jsonify({
                        'success': False,
                        'error': 'GPT Flow nie jest aktywny'
                    }), 503

                result = self.engine.gpt_flow.chat_with_astra(user_message, user_id)
                self.request_count += 1

                return jsonify(result)

            except Exception as e:
                self.request_count += 1
                print(f"🤖 Błąd GPT Flow: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/functions', methods=['GET'])
        def list_functions():
            """Lista dostępnych funkcji"""
            try:
                category = request.args.get('category')

                if not self.engine.function_generator:
                    return jsonify({
                        'success': False,
                        'error': 'Function Generator nie jest aktywny'
                    }), 503

                functions = self.engine.function_generator.list_functions(category)
                self.request_count += 1

                return jsonify({
                    'success': True,
                    'functions': functions,
                    'count': len(functions)
                })

            except Exception as e:
                self.request_count += 1
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/functions', methods=['POST'])
        def create_function():
            """Tworzy nową funkcję"""
            try:
                spec_data = request.get_json()

                if not spec_data:
                    return jsonify({
                        'success': False,
                        'error': 'Brak specyfikacji funkcji'
                    }), 400

                if not self.engine.function_generator:
                    return jsonify({
                        'success': False,
                        'error': 'Function Generator nie jest aktywny'
                    }), 503

                result = self.engine.function_generator.create_function(spec_data)
                self.request_count += 1

                return jsonify(result)

            except Exception as e:
                self.request_count += 1
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/functions/<function_name>', methods=['GET'])
        def get_function_info(function_name):
            """Informacje o funkcji"""
            try:
                if not self.engine.function_generator:
                    return jsonify({
                        'success': False,
                        'error': 'Function Generator nie jest aktywny'
                    }), 503

                info = self.engine.function_generator.get_function_info(function_name)
                self.request_count += 1

                if info:
                    return jsonify({
                        'success': True,
                        'function_info': info
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Funkcja nie znaleziona'
                    }), 404

            except Exception as e:
                self.request_count += 1
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/functions/<function_name>/invoke', methods=['POST'])
        def invoke_function(function_name):
            """Wywołuje funkcję"""
            try:
                args = request.get_json() or {}

                if not self.engine.function_generator:
                    return jsonify({
                        'success': False,
                        'error': 'Function Generator nie jest aktywny'
                    }), 503

                result = self.engine.function_generator.invoke_function(function_name, args)
                self.request_count += 1

                return jsonify(result)

            except Exception as e:
                self.request_count += 1
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/functions/<function_name>', methods=['DELETE'])
        def delete_function(function_name):
            """Usuwa funkcję"""
            try:
                if not self.engine.function_generator:
                    return jsonify({
                        'success': False,
                        'error': 'Function Generator nie jest aktywny'
                    }), 503

                success = self.engine.function_generator.delete_function(function_name)
                self.request_count += 1

                return jsonify({
                    'success': success,
                    'message': 'Funkcja usunięta' if success else 'Funkcja nie znaleziona'
                })

            except Exception as e:
                self.request_count += 1
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

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