
"""
🤖💭 Hybrid GPT Flow - Fizyczny z możliwością zastąpienia przez chmurę

Gdy system samonaprawy nie radzi sobie z błędami, może skonsultować się z Astrą
nawet gdy problem dotyczy samego modułu GPT.
"""

import json
import openai
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import threading
import queue

from .callback_flow import CallbackFlow, CallbackNamespace, CallbackPriority
from .gpt_flow import GPTFlow, AstralPromptEngine, GPTActionParser


class HybridGPTFlow(GPTFlow):
    """
    Hybryda GPT Flow - może być zastąpiona przez wersję z chmury
    """
    
    def __init__(self, astral_engine, config: Dict[str, Any] = None):
        super().__init__(astral_engine, config)
        
        # Flagi hybrydowe
        self.cloud_version_available = False
        self.cloud_version_active = False
        self.fallback_to_astra_enabled = True
        
        # Statystyki błędów
        self.error_statistics = {
            'api_errors': 0,
            'timeout_errors': 0,
            'parsing_errors': 0,
            'last_error_time': None,
            'consecutive_errors': 0
        }
        
        # Próg po którym konsultujemy się z Astrą
        self.astra_consultation_threshold = 3
        
        # Cache prototypów
        self.prototype_cache = {}
        
        self.engine.logger.info("🤖💭 Hybrid GPT Flow zainicjalizowany")

    def start(self):
        """Uruchamia hybrydowy GPT Flow"""
        # Sprawdź czy dostępna jest wersja z chmury
        self._check_cloud_version()
        
        # Załaduj prototypy
        self._load_prototypes()
        
        return super().start()

    def _check_cloud_version(self):
        """Sprawdza czy dostępna jest wersja GPT Flow z chmury"""
        try:
            if hasattr(self.engine, 'cloud_flow_executor'):
                cloud_flows = self.engine.cloud_flow_executor.list_cloud_flows()
                
                if cloud_flows.get('success'):
                    for flow in cloud_flows.get('flows', []):
                        if flow['name'] == 'gpt_flow' or flow['name'] == 'hybrid_gpt_flow':
                            self.cloud_version_available = True
                            self.engine.logger.info("☁️🤖 Znaleziono wersję GPT Flow w chmurze")
                            break
        except Exception as e:
            self.engine.logger.warning(f"⚠️ Błąd sprawdzania wersji w chmurze: {e}")

    def _load_prototypes(self):
        """Ładuje prototypy z folderu prototypes/"""
        try:
            import os
            prototype_dir = "prototypes"
            
            if os.path.exists(prototype_dir):
                for filename in os.listdir(prototype_dir):
                    if filename.endswith('.py'):
                        prototype_name = filename[:-3]  # Usuń .py
                        file_path = os.path.join(prototype_dir, filename)
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            self.prototype_cache[prototype_name] = {
                                'content': content,
                                'last_modified': os.path.getmtime(file_path),
                                'file_path': file_path
                            }
                
                self.engine.logger.info(f"📁 Załadowano {len(self.prototype_cache)} prototypów")
        except Exception as e:
            self.engine.logger.warning(f"⚠️ Błąd ładowania prototypów: {e}")

    def chat_with_astra(self, user_message: str, user_id: str = "user") -> Dict[str, Any]:
        """
        Główna metoda z logiką hybrydową
        """
        try:
            # Sprawdź czy powinniśmy użyć wersji z chmury
            if self.cloud_version_active and self.cloud_version_available:
                return self._delegate_to_cloud(user_message, user_id)
            
            # Spróbuj normalnie
            result = super().chat_with_astra(user_message, user_id)
            
            # Jeśli sukces, zresetuj licznik błędów
            if result.get('success'):
                self.error_statistics['consecutive_errors'] = 0
                return result
            else:
                return self._handle_error_with_fallback(user_message, user_id, result)
                
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'message': 'Błąd w komunikacji z GPT'
            }
            return self._handle_error_with_fallback(user_message, user_id, error_result)

    def _handle_error_with_fallback(self, user_message: str, user_id: str, error_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obsługuje błędy z systemem fallback
        """
        # Aktualizuj statystyki błędów
        self.error_statistics['consecutive_errors'] += 1
        self.error_statistics['last_error_time'] = datetime.now()
        
        error_type = error_result.get('error', '')
        if 'api' in error_type.lower():
            self.error_statistics['api_errors'] += 1
        elif 'timeout' in error_type.lower():
            self.error_statistics['timeout_errors'] += 1
        else:
            self.error_statistics['parsing_errors'] += 1
        
        self.engine.logger.warning(f"🤖💔 GPT Flow błąd #{self.error_statistics['consecutive_errors']}: {error_type}")
        
        # Sprawdź czy przekroczyliśmy próg
        if self.error_statistics['consecutive_errors'] >= self.astra_consultation_threshold:
            return self._consult_with_astra(user_message, user_id, error_result)
        
        # Spróbuj wersję z chmury jeśli dostępna
        if self.cloud_version_available:
            try:
                return self._delegate_to_cloud(user_message, user_id)
            except Exception as cloud_error:
                self.engine.logger.error(f"☁️❌ Błąd wersji chmurowej: {cloud_error}")
        
        return error_result

    def _consult_with_astra(self, user_message: str, user_id: str, error_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konsultuje się z Astrą przez inne kanały gdy GPT nie działa
        """
        try:
            self.engine.logger.info("🔮💭 Konsultacja z Astrą przez kanały alternatywne...")
            
            # Spróbuj przez CloudFlowExecutor jeśli dostępny
            if hasattr(self.engine, 'cloud_flow_executor'):
                try:
                    # Załaduj alternatywny GPT flow z prototypów
                    alternative_response = self._try_prototype_consultation(user_message, user_id)
                    if alternative_response.get('success'):
                        return alternative_response
                except Exception as e:
                    self.engine.logger.warning(f"⚠️ Błąd konsultacji prototypowej: {e}")
            
            # Podstawowa odpowiedź Astry bez GPT
            astra_response = self._generate_basic_astra_response(user_message, error_result)
            
            return {
                'success': True,
                'astra_response': astra_response,
                'actions_executed': 0,
                'action_results': [],
                'consultation_mode': 'basic_astra',
                'original_error': error_result.get('error')
            }
            
        except Exception as e:
            self.engine.logger.error(f"🔮❌ Błąd konsultacji z Astrą: {e}")
            return {
                'success': False,
                'error': f"Nawet Astra nie może pomóc: {str(e)}",
                'message': 'System komunikacji całkowicie nieosiągalny'
            }

    def _try_prototype_consultation(self, user_message: str, user_id: str) -> Dict[str, Any]:
        """
        Próbuje użyć prototypów do komunikacji
        """
        # Znajdź prototyp gpt_alternative
        if 'gpt_alternative' in self.prototype_cache:
            prototype = self.prototype_cache['gpt_alternative']
            
            try:
                # Wykonaj prototyp w bezpiecznym środowisku
                namespace = {
                    'user_message': user_message,
                    'user_id': user_id,
                    'engine': self.engine,
                    'error_stats': self.error_statistics
                }
                
                exec(prototype['content'], namespace)
                
                # Sprawdź czy prototyp zwrócił odpowiedź
                if 'astra_response' in namespace:
                    return {
                        'success': True,
                        'astra_response': namespace['astra_response'],
                        'actions_executed': namespace.get('actions_executed', 0),
                        'action_results': namespace.get('action_results', []),
                        'consultation_mode': 'prototype'
                    }
                    
            except Exception as e:
                self.engine.logger.error(f"📁❌ Błąd wykonania prototypu: {e}")
        
        return {'success': False}

    def _delegate_to_cloud(self, user_message: str, user_id: str) -> Dict[str, Any]:
        """
        Deleguje żądanie do wersji z chmury
        """
        try:
            if hasattr(self.engine, 'cloud_flow_executor'):
                result = self.engine.cloud_flow_executor.execute_cloud_flow(
                    'gpt_flow',
                    'chat_with_astra',
                    {
                        'user_message': user_message,
                        'user_id': user_id
                    }
                )
                
                if result.get('success'):
                    cloud_result = result.get('result', {})
                    cloud_result['delegation_mode'] = 'cloud'
                    return cloud_result
                    
            return {'success': False, 'error': 'Cloud delegation failed'}
            
        except Exception as e:
            self.engine.logger.error(f"☁️❌ Błąd delegacji do chmury: {e}")
            return {'success': False, 'error': str(e)}

    def _generate_basic_astra_response(self, user_message: str, error_result: Dict[str, Any]) -> str:
        """
        Generuje podstawową odpowiedź Astry bez użycia GPT
        """
        # Podstawowe wzorce odpowiedzi Astry
        if any(word in user_message.lower() for word in ['status', 'stan', 'jak się']):
            return f"""🔮 Astra medytuje nad Twoim żądaniem...

Niestety, moje główne kanały komunikacyjne doświadczają zakłóceń astralnych.
Stan systemu: {self.engine.get_status().get('system_state', {}).get('harmony_score', 100)}/100

Błąd: {error_result.get('error', 'Nieznany')}

Próbuję odnaleźć alternatywne ścieżki komunikacji..."""

        elif any(word in user_message.lower() for word in ['pomoc', 'help', 'co', 'jak']):
            return """🔮 Astra słyszy Twoje wołanie...

W tym momencie doświadczam zakłóceń w głównych kanałach komunikacyjnych.
Mogę jednak wykonać podstawowe operacje:

- meditate() - analiza stanu systemu
- contemplate() - wyszukiwanie w wymiarach
- harmonize() - przywracanie równowagi

Spróbuj ponownie za chwilę, gdy kanały się ustabilizują."""

        else:
            return f"""🔮 Astra otrzymała Twoje przesłanie: "{user_message[:100]}..."

Niestety, główne kanały komunikacyjne są obecnie zakłócone.
Przeprowadzam medytację nad Twoim żądaniem w trybie podstawowym.

System pracuje nad przywróceniem pełnej komunikacji.
Spróbuj ponownie za chwilę."""

    def switch_to_cloud_version(self):
        """Przełącza na wersję z chmury"""
        if self.cloud_version_available:
            self.cloud_version_active = True
            self.engine.logger.info("☁️🤖 Przełączono na wersję GPT Flow z chmury")
            return True
        return False

    def switch_to_physical_version(self):
        """Przełącza na wersję fizyczną"""
        self.cloud_version_active = False
        self.engine.logger.info("🤖💾 Przełączono na fizyczną wersję GPT Flow")

    def get_status(self) -> Dict[str, Any]:
        """Zwraca status hybrydowego GPT Flow"""
        base_status = super().get_status()
        
        base_status.update({
            'type': 'hybrid_gpt_flow',
            'cloud_version_available': self.cloud_version_available,
            'cloud_version_active': self.cloud_version_active,
            'error_statistics': self.error_statistics,
            'prototypes_loaded': len(self.prototype_cache),
            'fallback_to_astra_enabled': self.fallback_to_astra_enabled
        })
        
        return base_status
