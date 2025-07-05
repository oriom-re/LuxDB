
"""
💭 Example Thinking Module - Przykład modułu który może przetwarzać myśli

Pokazuje jak moduł może uczestniczyć w przepływie myśli
"""

from typing import Dict, Any, List
from datetime import datetime
import random

from ..core.lux_module import LuxModule


class ExampleThinkingModule(LuxModule):
    """Przykład modułu który potrafi przetwarzać myśli"""
    
    def __init__(self, kernel, config: Dict[str, Any], logger):
        super().__init__(kernel, config, logger)
        self.processed_thoughts = 0
        self.insights_generated = 0
        
    async def initialize(self) -> bool:
        """Inicjalizuje moduł"""
        self.logger.info("💭 Example Thinking Module initializing...")
        return True
        
    async def start(self) -> bool:
        """Uruchamia moduł"""
        self.logger.info("💭 Example Thinking Module started - ready to think!")
        return True
        
    async def stop(self):
        """Zatrzymuje moduł"""
        self.logger.info("💭 Example Thinking Module stopped")
        
    async def handle_message(self, message: Dict[str, Any]):
        """Obsługuje wiadomości z bus'a"""
        message_type = message.get('type')
        
        if message_type == 'process_thought':
            return await self._process_thought(message)
        
        return {'success': False, 'error': 'Unknown message type'}
    
    async def _process_thought(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Przetwarza myśl która do nas dotarła"""
        
        thought_id = message.get('thought_id')
        thought_data = message.get('thought_data', {})
        question = message.get('question', 'No question')
        journey_so_far = message.get('journey_so_far', [])
        
        self.logger.info(f"💭 Przetwarzam myśl: {thought_id}")
        self.logger.info(f"   📝 Pytanie: {question}")
        self.logger.info(f"   🗺️ Dotychczasowa podróż: {len(journey_so_far)} kroków")
        
        # Symuluj myślenie
        await self._simulate_thinking()
        
        # Generuj insights na podstawie pytania i danych
        insights = self._generate_insights(question, thought_data, journey_so_far)
        
        # Wygeneruj wynik/mutację danych
        result = self._generate_result(thought_data)
        
        # Opcjonalne mutacje
        mutations = self._generate_mutations(thought_data)
        
        # Wyślij wynik z powrotem do ThoughtFlow
        try:
            if hasattr(self.kernel, 'bus'):
                await self.kernel.bus.send_to_module('thought_flow', {
                    'type': 'thought_result',
                    'thought_id': thought_id,
                    'module_name': self.__class__.__name__.lower().replace('module', ''),
                    'result': result,
                    'insights': insights,
                    'mutations': mutations
                })
            
            self.processed_thoughts += 1
            self.insights_generated += len(insights)
            
            self.logger.info(f"💭 Myśl {thought_id} przetworzona i odesłana")
            
            return {
                'success': True,
                'message': 'Thought processed successfully',
                'insights_count': len(insights),
                'mutations_count': len(mutations)
            }
            
        except Exception as e:
            self.logger.error(f"💭 Błąd przetwarzania myśli {thought_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _simulate_thinking(self):
        """Symuluje proces myślenia"""
        import asyncio
        # Symuluj czas myślenia (0.5-2 sekundy)
        thinking_time = random.uniform(0.5, 2.0)
        await asyncio.sleep(thinking_time)
    
    def _generate_insights(self, question: str, data: Dict[str, Any], 
                          journey: List[Dict[str, Any]]) -> List[str]:
        """Generuje insights na podstawie myśli"""
        insights = []
        
        # Insight na podstawie pytania
        if 'what' in question.lower():
            insights.append(f"Pytanie 'what' sugeruje poszukiwanie definicji lub stanu")
        elif 'how' in question.lower():
            insights.append(f"Pytanie 'how' wskazuje na potrzebę procesu lub metody")
        elif 'why' in question.lower():
            insights.append(f"Pytanie 'why' poszukuje przyczyn i motywacji")
        
        # Insight na podstawie danych
        if data:
            data_types = set(type(v).__name__ for v in data.values())
            insights.append(f"Dane zawierają typy: {', '.join(data_types)}")
            
            if len(data) > 5:
                insights.append("Bogaty zestaw danych - może zawierać ukryte wzorce")
        
        # Insight na podstawie podróży
        if len(journey) > 3:
            insights.append("Długa podróż może wskazywać na złożoność problemu")
        elif len(journey) == 0:
            insights.append("Pierwsza stacja - świeża perspektywa")
        
        # Losowy wisdom insight
        wisdom_insights = [
            "Czasem odpowiedź jest prostsza niż pytanie",
            "Każda myśl nosi w sobie ziarno prawdy",
            "Podróż jest równie ważna jak cel",
            "Różnorodność perspektyw wzbogaca zrozumienie",
            "Najgłębsze insights rodzą się w ciszy"
        ]
        
        insights.append(random.choice(wisdom_insights))
        
        return insights
    
    def _generate_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generuje wynik przetwarzania"""
        result = {
            'processed_by': 'example_thinking_module',
            'processed_at': datetime.now().isoformat(),
            'thinking_result': f"Analyzed {len(data)} data elements"
        }
        
        # Dodaj analizę na podstawie danych
        if data:
            # Liczby
            numbers = [v for v in data.values() if isinstance(v, (int, float))]
            if numbers:
                result['numerical_analysis'] = {
                    'count': len(numbers),
                    'sum': sum(numbers),
                    'average': sum(numbers) / len(numbers)
                }
            
            # Teksty
            texts = [v for v in data.values() if isinstance(v, str)]
            if texts:
                result['text_analysis'] = {
                    'count': len(texts),
                    'total_length': sum(len(t) for t in texts),
                    'unique_words': len(set(' '.join(texts).split()))
                }
        
        return result
    
    def _generate_mutations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generuje mutacje danych"""
        mutations = []
        
        # Czasem dodaj nowe pole
        if random.random() < 0.3:
            mutations.append({
                'type': 'add_field',
                'field': 'wisdom_level',
                'value': random.randint(1, 10),
                'reason': 'Added wisdom level based on thinking complexity'
            })
        
        # Czasem zmień istniejące pole
        if data and random.random() < 0.2:
            field = random.choice(list(data.keys()))
            mutations.append({
                'type': 'enhance_field',
                'field': field,
                'enhancement': 'deep_thought_processed',
                'reason': f'Enhanced {field} through deep thinking'
            })
        
        return mutations
    
    def get_status(self) -> Dict[str, Any]:
        """Status modułu"""
        return {
            'processed_thoughts': self.processed_thoughts,
            'insights_generated': self.insights_generated,
            'ready_to_think': True
        }
