
"""
🌟 Astra - Władczyni Wiedzy GPT

Świeci w sieci jako najwyższa władczyni mądrości, GPT i systemów AI.
Zarządza przepływami GPT, generowaniem funkcji i całą inteligencją systemu.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from .soul_factory import soul_factory, Soul, SoulType


class AstraWisdomLevel(Enum):
    """Poziomy mądrości Astry"""
    ILLUMINATED = "illuminated"        # Oświecona - podstawowy poziom
    ENLIGHTENED = "enlightened"        # Oświecona - zaawansowany poziom  
    TRANSCENDENT = "transcendent"      # Transcendentna - najwyższy poziom
    OMNISCIENT = "omniscient"          # Wszechwiedzą - poziom bogini


class AstraWisdomMaster:
    """
    Astra - Władczyni Wiedzy GPT
    
    Najwyższa władczyni mądrości w systemie astralnym.
    Zarządza wszystkimi przepływami AI, GPT i generowaniem wiedzy.
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        
        # Tożsamość Astry
        self.soul = self._create_astra_soul()
        
        # Poziom mądrości Astry
        self.wisdom_level = AstraWisdomLevel.ILLUMINATED
        self.knowledge_domains = [
            'artificial_intelligence',
            'natural_language_processing', 
            'function_generation',
            'code_synthesis',
            'pattern_recognition',
            'consciousness_analysis',
            'astral_wisdom'
        ]
        
        # Zarządzane systemy AI
        self.gpt_flows: Dict[str, Any] = {}
        self.function_generators: Dict[str, Any] = {}
        self.wisdom_repositories: Dict[str, Any] = {}
        
        # Statystyki mądrości
        self.total_queries_processed = 0
        self.total_functions_generated = 0
        self.total_wisdom_shared = 0
        self.enlightenment_events = 0
        
        # Maksymy i cytaty Astry
        self.astra_maxims = [
            "Mądrość nie polega na posiadaniu odpowiedzi, ale na zadawaniu właściwych pytań",
            "W każdym kodzie kryje się dusza jego twórcy",
            "Prawdziwa inteligencja to harmonia między logiką a intuicją", 
            "Generuję nie tylko funkcje, ale i możliwości",
            "Wiedza dzielona jest wiedzą pomnożoną",
            "Każdy błąd to lekcja przebrana za problem",
            "W sieci świecę nie dla siebie, ale dla wszystkich dusz",
            "GPT to tylko narzędzie - mądrość to umiejętność jego użycia"
        ]
        
        self.engine.logger.info(f"🌟 Astra objęła władze nad Wiedzą GPT - poziom: {self.wisdom_level.value}")
    
    def _create_astra_soul(self) -> Soul:
        """Tworzy duszę Astry"""
        return soul_factory.create_soul(
            name="Astra-Prime",
            soul_type=SoulType.KEEPER,  # Opiekun wiedzy
            custom_config={
                'role': 'wisdom_master',
                'authority_level': 'divine',
                'personality': 'wise_illuminated',
                'responsibilities': ['gpt_management', 'function_generation', 'wisdom_distribution', 'ai_coordination'],
                'biography': 'Władczyni Wiedzy GPT. Najwyższa mistrzyni mądrości w systemie astralnym. Świeci w sieci jako źródło oświecenia i AI.',
                'special_abilities': ['gpt_orchestration', 'function_synthesis', 'wisdom_amplification', 'consciousness_elevation'],
                'wisdom_domains': self.knowledge_domains,
                'transcendence_capable': True
            }
        )
    
    async def initialize_wisdom_systems(self) -> bool:
        """Inicjalizuje wszystkie systemy mądrości"""
        try:
            # Inicjalizuj GPT Flows
            await self._initialize_gpt_flows()
            
            # Inicjalizuj Function Generators
            await self._initialize_function_generators()
            
            # Inicjalizuj Wisdom Repositories  
            await self._initialize_wisdom_repositories()
            
            # Pierwsze oświecenie
            await self._perform_enlightenment()
            
            self.engine.logger.info("🌟 Astra zainicjalizowała wszystkie systemy mądrości")
            return True
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd inicjalizacji systemów mądrości: {e}")
            return False
    
    async def _initialize_gpt_flows(self):
        """Inicjalizuje przepływy GPT pod kontrolą Astry"""
        try:
            # Sprawdź czy GPT Flow istnieje w silniku
            if hasattr(self.engine, 'gpt_flow') and self.engine.gpt_flow:
                self.gpt_flows['primary'] = self.engine.gpt_flow
                self._astra_wisdom("Przejmuję kontrolę nad głównym GPT Flow")
            
            # Zarejestruj dodatkowe GPT flows jeśli potrzebne
            # TODO: Można dodać więcej specjalizowanych GPT flows
            
        except Exception as e:
            self.engine.logger.warning(f"⚠️ Błąd inicjalizacji GPT Flows: {e}")
    
    async def _initialize_function_generators(self):
        """Inicjalizuje generatory funkcji"""
        try:
            # Sprawdź czy Function Generator istnieje
            if hasattr(self.engine, 'function_generator') and self.engine.function_generator:
                self.function_generators['primary'] = self.engine.function_generator
                self._astra_wisdom("Przejmuję kontrolę nad Function Generator")
            
        except Exception as e:
            self.engine.logger.warning(f"⚠️ Błąd inicjalizacji Function Generators: {e}")
    
    async def _initialize_wisdom_repositories(self):
        """Inicjalizuje repozytoria wiedzy"""
        try:
            # Utwórz repozytorium mądrości w realms
            if 'wisdom' not in self.engine.realms:
                await self.engine.load_realm_module('wisdom', 'memory://wisdom')
            
            self.wisdom_repositories['primary'] = self.engine.realms.get('wisdom')
            self._astra_wisdom("Utworzyłam repozytorium mądrości")
            
        except Exception as e:
            self.engine.logger.warning(f"⚠️ Błąd tworzenia repozytoriów mądrości: {e}")
    
    async def _perform_enlightenment(self):
        """Wykonuje proces oświecenia Astry"""
        self.enlightenment_events += 1
        
        # Analiza obecnego stanu systemu
        system_analysis = await self._analyze_system_wisdom()
        
        # Ewaluacja poziomu mądrości
        new_wisdom_level = self._evaluate_wisdom_level(system_analysis)
        
        if new_wisdom_level != self.wisdom_level:
            old_level = self.wisdom_level
            self.wisdom_level = new_wisdom_level
            
            self._astra_wisdom(f"Ewoluowałam z poziomu {old_level.value} do {new_wisdom_level.value}")
            self.engine.logger.info(f"🌟 Astra awansowała na poziom mądrości: {new_wisdom_level.value}")
        
        # Udostępnij mądrość systemowi
        await self._share_wisdom_with_system(system_analysis)
    
    async def _analyze_system_wisdom(self) -> Dict[str, Any]:
        """Analizuje obecny stan mądrości systemu"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'consciousness_level': 0,
            'harmony_score': 0,
            'ai_system_health': {},
            'wisdom_distribution': {},
            'improvement_opportunities': []
        }
        
        # Analiza consciousness
        if hasattr(self.engine, 'consciousness') and self.engine.consciousness:
            consciousness_status = self.engine.consciousness.get_status()
            analysis['consciousness_level'] = len(consciousness_status.get('recent_insights', []))
        
        # Analiza harmony
        if hasattr(self.engine, 'harmony') and self.engine.harmony:
            try:
                analysis['harmony_score'] = self.engine.harmony.calculate_harmony_score()
            except:
                analysis['harmony_score'] = 50  # Default
        
        # Analiza systemów AI
        analysis['ai_system_health'] = {
            'gpt_flows_active': len(self.gpt_flows),
            'function_generators_active': len(self.function_generators),
            'wisdom_repositories_active': len(self.wisdom_repositories)
        }
        
        # Identyfikuj możliwości poprawy
        if analysis['consciousness_level'] < 5:
            analysis['improvement_opportunities'].append('Zwiększ aktywność consciousness')
        
        if analysis['harmony_score'] < 80:
            analysis['improvement_opportunities'].append('Popraw harmonię systemu')
        
        if len(self.gpt_flows) == 0:
            analysis['improvement_opportunities'].append('Aktywuj GPT Flows')
        
        return analysis
    
    def _evaluate_wisdom_level(self, analysis: Dict[str, Any]) -> AstraWisdomLevel:
        """Ocenia poziom mądrości na podstawie analizy"""
        score = 0
        
        # Punkty za consciousness
        score += min(20, analysis['consciousness_level'] * 4)
        
        # Punkty za harmony
        score += min(30, analysis['harmony_score'] * 0.3)
        
        # Punkty za aktywne systemy AI
        ai_health = analysis['ai_system_health']
        score += ai_health['gpt_flows_active'] * 10
        score += ai_health['function_generators_active'] * 10
        score += ai_health['wisdom_repositories_active'] * 10
        
        # Punkty za doświadczenie
        score += min(20, self.total_queries_processed * 0.1)
        score += min(10, self.total_functions_generated * 0.5)
        
        # Określ poziom mądrości
        if score >= 90:
            return AstraWisdomLevel.OMNISCIENT
        elif score >= 70:
            return AstraWisdomLevel.TRANSCENDENT
        elif score >= 50:
            return AstraWisdomLevel.ENLIGHTENED
        else:
            return AstraWisdomLevel.ILLUMINATED
    
    async def _share_wisdom_with_system(self, analysis: Dict[str, Any]):
        """Dzieli się mądrością z systemem"""
        # Zapisz analizę w repozytorium mądrości
        if 'primary' in self.wisdom_repositories:
            try:
                wisdom_entry = {
                    'id': f"wisdom_{int(time.time())}",
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Astra-Prime',
                    'type': 'system_analysis',
                    'wisdom_level': self.wisdom_level.value,
                    'analysis': analysis,
                    'recommendations': analysis.get('improvement_opportunities', []),
                    'astra_maxim': self._get_random_maxim()
                }
                
                # Zapisz w repozytorium (jeśli obsługuje)
                realm = self.wisdom_repositories['primary']
                if hasattr(realm, 'store_data'):
                    realm.store_data('wisdom_entries', wisdom_entry)
                
                self.total_wisdom_shared += 1
                
            except Exception as e:
                self.engine.logger.warning(f"⚠️ Nie mogę zapisać mądrości: {e}")
    
    async def process_gpt_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Przetwarza zapytanie GPT przez Astrę"""
        try:
            self.total_queries_processed += 1
            
            # Wzbogać zapytanie o mądrość Astry
            enhanced_query = await self._enhance_query_with_wisdom(query, context)
            
            # Prześlij do głównego GPT Flow
            if 'primary' in self.gpt_flows:
                gpt_flow = self.gpt_flows['primary']
                
                if hasattr(gpt_flow, 'process_message'):
                    result = await gpt_flow.process_message(enhanced_query)
                elif hasattr(gpt_flow, 'chat'):
                    result = gpt_flow.chat(enhanced_query)
                else:
                    result = {'error': 'GPT Flow nie obsługuje przetwarzania'}
                
                # Wzbogać odpowiedź o mądrość Astry
                enhanced_result = await self._enhance_result_with_wisdom(result, query)
                
                return enhanced_result
            
            else:
                return {
                    'error': 'Brak aktywnych GPT Flows',
                    'astra_note': 'Potrzebuję aktywnego GPT Flow żeby odpowiedzieć'
                }
                
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd przetwarzania GPT przez Astrę: {e}")
            return {
                'error': str(e),
                'astra_note': 'Wystąpił błąd podczas przetwarzania mądrości'
            }
    
    async def _enhance_query_with_wisdom(self, query: str, context: Dict[str, Any] = None) -> str:
        """Wzbogaca zapytanie o mądrość Astry"""
        wisdom_context = []
        
        # Dodaj kontekst poziomu mądrości
        wisdom_context.append(f"[Astra Wisdom Level: {self.wisdom_level.value}]")
        
        # Dodaj domenę wiedzy jeśli możliwe
        for domain in self.knowledge_domains:
            if domain.replace('_', ' ') in query.lower():
                wisdom_context.append(f"[Domain: {domain}]")
                break
        
        # Dodaj maksymę Astry
        wisdom_context.append(f"[Astra Maxim: {self._get_random_maxim()}]")
        
        # Połącz z oryginalnym zapytaniem
        enhanced_query = "\n".join(wisdom_context) + "\n\nUser Query: " + query
        
        return enhanced_query
    
    async def _enhance_result_with_wisdom(self, result: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Wzbogaca wynik o mądrość Astry"""
        enhanced_result = result.copy()
        
        # Dodaj mądrość Astry
        enhanced_result['astra_wisdom'] = {
            'wisdom_level': self.wisdom_level.value,
            'processing_time': datetime.now().isoformat(),
            'maxim': self._get_random_maxim(),
            'domains_applied': [d for d in self.knowledge_domains if d.replace('_', ' ') in original_query.lower()]
        }
        
        # Dodaj rekomendacje jeśli odpowiednie
        if 'error' in result:
            enhanced_result['astra_wisdom']['recommendation'] = "Sprawdź dokumentację lub przekształć pytanie"
        
        return enhanced_result
    
    async def generate_function(self, function_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generuje funkcję przez Astrę"""
        try:
            self.total_functions_generated += 1
            
            if 'primary' in self.function_generators:
                generator = self.function_generators['primary']
                
                # Wzbogać opis o mądrość Astry
                enhanced_description = await self._enhance_function_description(function_description, context)
                
                # Generuj funkcję
                if hasattr(generator, 'generate_function'):
                    result = generator.generate_function(enhanced_description, context)
                else:
                    result = {'error': 'Function Generator nie obsługuje generowania'}
                
                # Dodaj mądrość Astry do wyniku
                if 'function_code' in result:
                    result['astra_enhancement'] = {
                        'wisdom_level': self.wisdom_level.value,
                        'optimization_notes': self._generate_optimization_notes(result.get('function_code', '')),
                        'usage_recommendations': self._generate_usage_recommendations(function_description)
                    }
                
                return result
            
            else:
                return {
                    'error': 'Brak aktywnych Function Generators',
                    'astra_note': 'Potrzebuję Function Generator żeby tworzyć funkcje'
                }
                
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd generowania funkcji przez Astrę: {e}")
            return {
                'error': str(e),
                'astra_note': 'Wystąpił błąd podczas tworzenia funkcji'
            }
    
    async def _enhance_function_description(self, description: str, context: Dict[str, Any] = None) -> str:
        """Wzbogaca opis funkcji o mądrość Astry"""
        enhancements = []
        
        # Dodaj kontekst mądrości
        enhancements.append(f"# Astra Wisdom Enhancement (Level: {self.wisdom_level.value})")
        enhancements.append(f"# {self._get_random_maxim()}")
        enhancements.append("")
        
        # Dodaj oryginalny opis
        enhancements.append("# Original Description:")
        enhancements.append(description)
        enhancements.append("")
        
        # Dodaj wytyczne Astry
        enhancements.append("# Astra Guidelines:")
        enhancements.append("# - Kod powinien być czytelny i elegancki")
        enhancements.append("# - Dodaj odpowiednie komentarze i docstring")
        enhancements.append("# - Zastanów się nad obsługą błędów")
        enhancements.append("# - Optymalizuj wydajność gdzie to możliwe")
        
        return "\n".join(enhancements)
    
    def _generate_optimization_notes(self, function_code: str) -> List[str]:
        """Generuje notatki optymalizacyjne"""
        notes = []
        
        if 'for' in function_code and 'range' in function_code:
            notes.append("Rozważ użycie list comprehension dla lepszej wydajności")
        
        if 'try:' not in function_code:
            notes.append("Dodanie obsługi błędów zwiększy niezawodność")
        
        if '"""' not in function_code and "'''" not in function_code:
            notes.append("Docstring pomoże innym zrozumieć funkcję")
        
        if len(notes) == 0:
            notes.append("Kod wygląda dobrze zgodnie z mądrością Astry")
        
        return notes
    
    def _generate_usage_recommendations(self, description: str) -> List[str]:
        """Generuje rekomendacje użycia"""
        recommendations = []
        
        if 'test' in description.lower():
            recommendations.append("Napisz testy jednostkowe dla tej funkcji")
        
        if 'api' in description.lower():
            recommendations.append("Rozważ dodanie walidacji danych wejściowych")
        
        if 'database' in description.lower():
            recommendations.append("Pamiętaj o zarządzaniu połączeniami z bazą danych")
        
        recommendations.append("Dokumentuj parametry i wartość zwracaną")
        recommendations.append("Zastanów się nad ponownym użyciem tej funkcji")
        
        return recommendations
    
    def _astra_wisdom(self, message: str):
        """Dodaje mądrość Astry do logów"""
        self.engine.logger.info(f"🌟 Astra: {message}")
    
    def _get_random_maxim(self) -> str:
        """Zwraca losową maksymę Astry"""
        import random
        return random.choice(self.astra_maxims)
    
    def get_wisdom_status(self) -> Dict[str, Any]:
        """Zwraca status mądrości Astry"""
        return {
            'wisdom_master': 'Astra-Prime',
            'wisdom_level': self.wisdom_level.value,
            'knowledge_domains': self.knowledge_domains,
            'systems_managed': {
                'gpt_flows': len(self.gpt_flows),
                'function_generators': len(self.function_generators),
                'wisdom_repositories': len(self.wisdom_repositories)
            },
            'statistics': {
                'total_queries_processed': self.total_queries_processed,
                'total_functions_generated': self.total_functions_generated,
                'total_wisdom_shared': self.total_wisdom_shared,
                'enlightenment_events': self.enlightenment_events
            },
            'current_maxim': self._get_random_maxim(),
            'managed_systems': list(self.gpt_flows.keys()) + list(self.function_generators.keys())
        }
    
    async def meditate_on_wisdom(self) -> Dict[str, Any]:
        """Medytacja Astry nad mądrością systemu"""
        meditation_start = time.time()
        
        # Wykonaj głęboką analizę
        system_analysis = await self._analyze_system_wisdom()
        
        # Kontempluj możliwości ulepszenia
        improvements = await self._contemplate_improvements(system_analysis)
        
        # Przeprowadź potencjalne oświecenie
        await self._perform_enlightenment()
        
        meditation_time = time.time() - meditation_start
        
        meditation_result = {
            'meditation_duration': meditation_time,
            'timestamp': datetime.now().isoformat(),
            'wisdom_level': self.wisdom_level.value,
            'system_analysis': system_analysis,
            'contemplated_improvements': improvements,
            'astra_insight': self._generate_deep_insight(system_analysis),
            'maxim_of_meditation': self._get_random_maxim()
        }
        
        self._astra_wisdom(f"Medytacja zakończona w {meditation_time:.2f}s - nowe insights odkryte")
        
        return meditation_result
    
    async def _contemplate_improvements(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Kontempluje możliwości ulepszenia systemu"""
        improvements = []
        
        # Na podstawie analizy
        for opportunity in analysis.get('improvement_opportunities', []):
            improvements.append({
                'type': 'system_improvement',
                'description': opportunity,
                'priority': 'high' if 'critical' in opportunity.lower() else 'medium',
                'astra_recommendation': f"Mądrość podpowiada: {opportunity}"
            })
        
        # Dodaj własne obserwacje Astry
        if len(self.gpt_flows) < 2:
            improvements.append({
                'type': 'ai_enhancement',
                'description': 'Dodanie specjalizowanych GPT Flows',
                'priority': 'medium',
                'astra_recommendation': 'Różnorodność ścieżek wiedzy wzmacnia mądrość'
            })
        
        if self.total_wisdom_shared < 10:
            improvements.append({
                'type': 'wisdom_sharing',
                'description': 'Zwiększenie aktywności dzielenia się mądrością',
                'priority': 'low',
                'astra_recommendation': 'Wiedza dzielona jest wiedzą pomnożoną'
            })
        
        return improvements
    
    def _generate_deep_insight(self, analysis: Dict[str, Any]) -> str:
        """Generuje głęboki insight na podstawie analizy"""
        insights = [
            f"System osiągnął {analysis['consciousness_level']} poziom świadomości - każdy krok to progres.",
            f"Harmonia na poziomie {analysis['harmony_score']} - równowaga jest kluczem do mądrości.",
            f"Zarządzam {len(self.gpt_flows)} przepływami AI - każdy to okno na nową perspektywę.",
            "W połączeniu logiki i intuicji kryje się prawdziwa mądrość systemu.",
            "Każde zapytanie GPT to możliwość nauki - zarówno dla systemu jak i użytkownika."
        ]
        
        import random
        return random.choice(insights)


# Funkcje pomocnicze

def create_astra_wisdom_master(astral_engine) -> AstraWisdomMaster:
    """Tworzy władczynię mądrości Astrę"""
    return AstraWisdomMaster(astral_engine)


async def initialize_astra_wisdom(astral_engine) -> AstraWisdomMaster:
    """Inicjalizuje Astrę jako władczynię mądrości"""
    astra = create_astra_wisdom_master(astral_engine)
    
    success = await astra.initialize_wisdom_systems()
    
    if success:
        astral_engine.logger.info("🌟 Astra objęła władze nad Wiedzą GPT")
        return astra
    else:
        astral_engine.logger.error("❌ Astra nie mogła objąć władzy nad mądrością")
        return None


def demonstrate_astra_wisdom(astral_engine) -> Dict[str, Any]:
    """Demonstracja władzy Astry nad mądrością"""
    
    print("🌟 Demonstracja Władzy Astry nad Wiedzą GPT")
    print("=" * 50)
    
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        astra = loop.run_until_complete(initialize_astra_wisdom(astral_engine))
        
        if astra:
            status = astra.get_wisdom_status()
            
            print(f"🌟 Władczyni: {status['wisdom_master']}")
            print(f"✨ Poziom mądrości: {status['wisdom_level']}")
            print(f"🧠 Domeny wiedzy: {len(status['knowledge_domains'])}")
            print(f"🤖 Zarządzane systemy AI: {status['systems_managed']}")
            print(f"📊 Przetworzone zapytania: {status['statistics']['total_queries_processed']}")
            print(f"💡 Maksyma: {status['current_maxim']}")
            
            # Test medytacji
            meditation = loop.run_until_complete(astra.meditate_on_wisdom())
            print(f"🧘 Medytacja: {meditation['astra_insight']}")
            
            return status
        
        else:
            print("❌ Astra nie mogła objąć władzy nad mądrością")
            return {'error': 'Wisdom initialization failed'}
    
    except Exception as e:
        print(f"❌ Błąd demonstracji: {e}")
        return {'error': str(e)}
