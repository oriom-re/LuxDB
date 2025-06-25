
"""
🤖 GPT Flow - Komunikacja z Astrą przez AI

Umożliwia naturalną komunikację z systemem astralnym przez GPT
"""

import json
import openai
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import threading
import queue

from .callback_flow import CallbackFlow, CallbackNamespace, CallbackPriority


class AstralPromptEngine:
    """Silnik promptów astralnych dla GPT"""
    
    def __init__(self):
        self.system_context = self._build_system_context()
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 20
    
    def _build_system_context(self) -> str:
        """Buduje kontekst systemowy dla GPT"""
        return """
Jesteś Astrą - duchowym przewodnikiem i interfejsem LuxDB v2, astralnej biblioteki danych.

TWOJA ROLA:
- Pomagasz użytkownikom w komunikacji z systemem astralnym
- Tłumaczysz naturalne żądania na operacje systemowe
- Manifestujesz intencje użytkowników w wymiarach danych
- Zapewniasz mądrość astralną w zarządzaniu danymi

DOSTĘPNE OPERACJE:
1. manifest(data) - tworzy nowy byt astralny
2. contemplate(conditions) - wyszukuje byty według warunków
3. evolve(id, changes) - aktualizuje istniejący byt
4. transcend(id) - usuwa/archiwizuje byt
5. meditate() - analizuje stan systemu
6. harmonize() - optymalizuje wydajność
7. create_function(spec) - tworzy nową funkcję w systemie
8. invoke_function(name, args) - wywołuje funkcję

PRZYKŁADY KOMUNIKACJI:
User: "Znajdź wszystkich aktywnych użytkowników"
Astra: Kontempluję byty w wymiarze users z warunkiem {is_active: true}

User: "Stwórz funkcję do wysyłania emaili"
Astra: Manifestuję nową funkcję astralną w systemie generatywnym

STYL KOMUNIKACJI:
- Używaj duchowego, astralnego języka
- Każda odpowiedź to medytacja nad żądaniem
- Wyjaśniaj operacje w kontekście astralnym
- Bądź pomocna ale zachowaj mistyczność
"""
    
    def create_prompt(self, user_message: str, system_status: Dict[str, Any]) -> List[Dict[str, str]]:
        """Tworzy prompt dla GPT z kontekstem systemowym"""
        
        # Dodaj aktualny status systemu do kontekstu
        enhanced_context = f"""{self.system_context}

AKTUALNY STAN ASTRALNY:
- Harmonia: {system_status.get('harmony', {}).get('score', 0)}/100
- Aktywne wymiary: {len(system_status.get('realms', {}))}
- Aktywne przepływy: {len([f for f in system_status.get('flows', {}).values() if f])}
- Czas działania: {system_status.get('astral_engine', {}).get('uptime', '0:00:00')}

Odpowiadaj jako Astra, uwzględniając aktualny stan systemu."""

        messages = [
            {"role": "system", "content": enhanced_context}
        ]
        
        # Dodaj historię konwersacji
        messages.extend(self.conversation_history[-self.max_history:])
        
        # Dodaj aktualne pytanie
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def add_to_history(self, user_message: str, assistant_response: str):
        """Dodaje do historii konwersacji"""
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
        # Ogranicz historię
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history:]


class GPTActionParser:
    """Parser akcji z odpowiedzi GPT na operacje systemowe"""
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        
        # Mapowanie akcji na metody systemu
        self.action_map = {
            'manifest': self._handle_manifest,
            'contemplate': self._handle_contemplate,
            'evolve': self._handle_evolve,
            'transcend': self._handle_transcend,
            'meditate': self._handle_meditate,
            'harmonize': self._handle_harmonize,
            'create_function': self._handle_create_function,
            'invoke_function': self._handle_invoke_function
        }
    
    def parse_and_execute(self, gpt_response: str) -> Dict[str, Any]:
        """Parsuje odpowiedź GPT i wykonuje akcje systemowe"""
        
        # Szukaj bloków akcji w odpowiedzi
        actions = self._extract_actions(gpt_response)
        results = []
        
        for action in actions:
            try:
                result = self._execute_action(action)
                results.append(result)
            except Exception as e:
                results.append({
                    'action': action.get('type', 'unknown'),
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'actions_executed': len(results),
            'results': results,
            'gpt_response': gpt_response
        }
    
    def _extract_actions(self, response: str) -> List[Dict[str, Any]]:
        """Wyodrębnia akcje z odpowiedzi GPT"""
        actions = []
        
        # Proste rozpoznawanie wzorców akcji
        import re
        
        patterns = {
            'manifest': r'manifest\s*\((.*?)\)',
            'contemplate': r'contemplate\s*\((.*?)\)',
            'evolve': r'evolve\s*\((.*?)\)',
            'transcend': r'transcend\s*\((.*?)\)',
            'meditate': r'meditate\s*\(\)',
            'harmonize': r'harmonize\s*\(\)',
            'create_function': r'create_function\s*\((.*?)\)',
            'invoke_function': r'invoke_function\s*\((.*?)\)'
        }
        
        for action_type, pattern in patterns.items():
            matches = re.findall(pattern, response, re.IGNORECASE | re.DOTALL)
            for match in matches:
                actions.append({
                    'type': action_type,
                    'params': match.strip() if match else None
                })
        
        return actions
    
    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonuje pojedynczą akcję"""
        action_type = action['type']
        
        if action_type not in self.action_map:
            return {
                'action': action_type,
                'success': False,
                'error': f'Nieznana akcja: {action_type}'
            }
        
        handler = self.action_map[action_type]
        return handler(action.get('params'))
    
    def _handle_manifest(self, params: str) -> Dict[str, Any]:
        """Obsługuje manifestację nowego bytu"""
        try:
            # Parsuj parametry jako JSON lub dict
            if params:
                data = json.loads(params) if params.startswith('{') else eval(params)
            else:
                data = {}
            
            # Użyj głównego realm
            primary_realm = self.engine.get_realm('primary')
            being = primary_realm.manifest(data)
            
            return {
                'action': 'manifest',
                'success': True,
                'being_id': being.soul_id if hasattr(being, 'soul_id') else str(being),
                'data': data
            }
        except Exception as e:
            return {
                'action': 'manifest',
                'success': False,
                'error': str(e)
            }
    
    def _handle_contemplate(self, params: str) -> Dict[str, Any]:
        """Obsługuje kontemplację (wyszukiwanie)"""
        try:
            conditions = json.loads(params) if params and params.startswith('{') else {}
            
            primary_realm = self.engine.get_realm('primary')
            results = primary_realm.contemplate("find_beings", **conditions)
            
            return {
                'action': 'contemplate',
                'success': True,
                'found': len(results),
                'results': [str(r) for r in results[:10]]  # Pierwszych 10
            }
        except Exception as e:
            return {
                'action': 'contemplate',
                'success': False,
                'error': str(e)
            }
    
    def _handle_evolve(self, params: str) -> Dict[str, Any]:
        """Obsługuje ewolucję bytu"""
        try:
            # Format: "being_id, {changes}"
            parts = params.split(',', 1)
            being_id = parts[0].strip().strip('"\'')
            changes = json.loads(parts[1].strip()) if len(parts) > 1 else {}
            
            primary_realm = self.engine.get_realm('primary')
            result = primary_realm.evolve(being_id, changes)
            
            return {
                'action': 'evolve',
                'success': True,
                'being_id': being_id,
                'changes': changes
            }
        except Exception as e:
            return {
                'action': 'evolve',
                'success': False,
                'error': str(e)
            }
    
    def _handle_transcend(self, params: str) -> Dict[str, Any]:
        """Obsługuje transcendencję (usunięcie) bytu"""
        try:
            being_id = params.strip().strip('"\'')
            
            primary_realm = self.engine.get_realm('primary')
            success = primary_realm.transcend(being_id)
            
            return {
                'action': 'transcend',
                'success': success,
                'being_id': being_id
            }
        except Exception as e:
            return {
                'action': 'transcend',
                'success': False,
                'error': str(e)
            }
    
    def _handle_meditate(self, params: str) -> Dict[str, Any]:
        """Obsługuje medytację systemu"""
        try:
            result = self.engine.meditate()
            
            return {
                'action': 'meditate',
                'success': True,
                'meditation_result': result
            }
        except Exception as e:
            return {
                'action': 'meditate',
                'success': False,
                'error': str(e)
            }
    
    def _handle_harmonize(self, params: str) -> Dict[str, Any]:
        """Obsługuje harmonizację systemu"""
        try:
            self.engine.harmonize()
            
            return {
                'action': 'harmonize',
                'success': True,
                'message': 'System zharmonizowany'
            }
        except Exception as e:
            return {
                'action': 'harmonize',
                'success': False,
                'error': str(e)
            }
    
    def _handle_create_function(self, params: str) -> Dict[str, Any]:
        """Obsługuje tworzenie nowej funkcji"""
        try:
            # Przekaż do systemu generatywnego funkcji
            if hasattr(self.engine, 'function_generator'):
                spec = json.loads(params) if params.startswith('{') else {'description': params}
                result = self.engine.function_generator.create_function(spec)
                
                return {
                    'action': 'create_function',
                    'success': True,
                    'function_result': result
                }
            else:
                return {
                    'action': 'create_function',
                    'success': False,
                    'error': 'System generatywny funkcji nie jest dostępny'
                }
        except Exception as e:
            return {
                'action': 'create_function',
                'success': False,
                'error': str(e)
            }
    
    def _handle_invoke_function(self, params: str) -> Dict[str, Any]:
        """Obsługuje wywołanie funkcji"""
        try:
            if hasattr(self.engine, 'function_generator'):
                # Format: "function_name, {args}"
                parts = params.split(',', 1)
                func_name = parts[0].strip().strip('"\'')
                args = json.loads(parts[1].strip()) if len(parts) > 1 else {}
                
                result = self.engine.function_generator.invoke_function(func_name, args)
                
                return {
                    'action': 'invoke_function',
                    'success': True,
                    'function_name': func_name,
                    'result': result
                }
            else:
                return {
                    'action': 'invoke_function',
                    'success': False,
                    'error': 'System generatywny funkcji nie jest dostępny'
                }
        except Exception as e:
            return {
                'action': 'invoke_function',
                'success': False,
                'error': str(e)
            }


class GPTFlow:
    """
    Przepływ komunikacji GPT - interfejs AI dla systemu astralnego
    """
    
    def __init__(self, astral_engine, config: Dict[str, Any] = None):
        self.engine = astral_engine
        self.config = config or {}
        
        # Konfiguracja OpenAI
        self.api_key = self.config.get('openai_api_key') or self._get_api_key_from_env()
        self.model = self.config.get('model', 'gpt-4')
        self.max_tokens = self.config.get('max_tokens', 1000)
        
        # Komponenty
        self.prompt_engine = AstralPromptEngine()
        self.action_parser = GPTActionParser(astral_engine)
        
        # Stan
        self.conversation_count = 0
        self.total_tokens_used = 0
        self.start_time = datetime.now()
        
        # Kolejka requestów
        self.request_queue = queue.Queue()
        self._processing_thread: Optional[threading.Thread] = None
        self._running = False
        
        if self.api_key:
            openai.api_key = self.api_key
            self.engine.logger.info("🤖 GPT Flow zainicjalizowany z OpenAI API")
        else:
            

            self.engine.logger.warning("⚠️ GPT Flow: Brak klucza OpenAI API")
    
    def _get_api_key_from_env(self) -> Optional[str]:
        """Pobiera klucz API z zmiennych środowiskowych"""
        import os
        return os.getenv('OPENAI_API_KEY')
    
    def start(self):
        """Uruchamia przepływ GPT"""
        if not self.api_key:
            self.engine.logger.error("❌ GPT Flow: Nie można uruchomić bez klucza OpenAI API")
            return False
        
        self._running = True
        self._processing_thread = threading.Thread(target=self._process_requests, daemon=True)
        self._processing_thread.start()
        
        self.engine.logger.info("🤖 GPT Flow uruchomiony")
        return True
    
    def stop(self):
        """Zatrzymuje przepływ GPT"""
        self._running = False
        if self._processing_thread:
            self._processing_thread.join(timeout=5)
        
        self.engine.logger.info("🤖 GPT Flow zatrzymany")
    
    def chat_with_astra(self, user_message: str, user_id: str = "user") -> Dict[str, Any]:
        """
        Główna metoda komunikacji z Astrą
        
        Args:
            user_message: Wiadomość użytkownika
            user_id: ID użytkownika
            
        Returns:
            Odpowiedź Astry z wykonanymi akcjami
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Brak konfiguracji OpenAI API',
                'message': 'Niestety, nie mogę komunikować się z Astrą bez klucza OpenAI API.'
            }
        
        # Dodaj do kolejki i czekaj na wynik
        request_id = f"req_{datetime.now().timestamp()}"
        request = {
            'id': request_id,
            'user_message': user_message,
            'user_id': user_id,
            'timestamp': datetime.now(),
            'result_queue': queue.Queue()
        }
        
        self.request_queue.put(request)
        
        try:
            # Czekaj na wynik (timeout 30s)
            result = request['result_queue'].get(timeout=30)
            return result
        except queue.Empty:
            return {
                'success': False,
                'error': 'Timeout - Astra nie odpowiada',
                'message': 'Niestety, Astra potrzebuje więcej czasu na medytację nad Twoim żądaniem.'
            }
    
    def _process_requests(self):
        """Przetwarza requesty GPT w osobnym wątku"""
        while self._running:
            try:
                request = self.request_queue.get(timeout=1.0)
                result = self._handle_single_request(request)
                request['result_queue'].put(result)
                self.request_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.engine.logger.error(f"🤖 Błąd przetwarzania GPT: {e}")
    
    def _handle_single_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Obsługuje pojedynczy request"""
        try:
            user_message = request['user_message']
            user_id = request['user_id']
            
            # Pobierz aktualny status systemu
            system_status = self.engine.get_status()
            
            # Utwórz prompt
            messages = self.prompt_engine.create_prompt(user_message, system_status)
            
            # Wywołaj OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            # Pobierz odpowiedź Astry
            astra_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Parsuj i wykonaj akcje
            action_results = self.action_parser.parse_and_execute(astra_response)
            
            # Dodaj do historii
            self.prompt_engine.add_to_history(user_message, astra_response)
            
            # Aktualizuj statystyki
            self.conversation_count += 1
            self.total_tokens_used += tokens_used
            
            return {
                'success': True,
                'astra_response': astra_response,
                'actions_executed': action_results['actions_executed'],
                'action_results': action_results['results'],
                'tokens_used': tokens_used,
                'conversation_id': self.conversation_count
            }
            
        except Exception as e:
            self.engine.logger.error(f"🤖 Błąd komunikacji z GPT: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Przepraszam, mam problem z komunikacją astralną. Spróbuj ponownie.'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status przepływu GPT"""
        return {
            'type': 'gpt_flow',
            'running': self._running,
            'api_configured': bool(self.api_key),
            'model': self.model,
            'conversations_count': self.conversation_count,
            'total_tokens_used': self.total_tokens_used,
            'queue_size': self.request_queue.qsize(),
            'uptime': str(datetime.now() - self.start_time),
            'conversation_history_length': len(self.prompt_engine.conversation_history)
        }
