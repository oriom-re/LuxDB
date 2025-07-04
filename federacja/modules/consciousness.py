
"""
🧠 Consciousness Module - Świadomość Federacji

Port z LuxDB v2 - system świadomości i analizy stanu systemu
"""

import time
import psutil
from typing import Dict, Any, List
from datetime import datetime
from ..core.lux_module import LuxModule


class ConsciousnessModule(LuxModule):
    """Moduł świadomości systemu - portowany z LuxDB v2"""
    
    def __init__(self, kernel, config: Dict[str, Any], logger):
        super().__init__(kernel, config, logger)
        self.observations = []
        self.insights = []
        self.start_time = time.time()
        
    async def initialize(self) -> bool:
        """Inicjalizuje moduł consciousness"""
        self.logger.info("🧠 Consciousness Module initializing...")
        return True
        
    async def start(self) -> bool:
        """Uruchamia moduł consciousness"""
        self.logger.info("🧠 Consciousness Module started")
        return True
        
    async def stop(self):
        """Zatrzymuje moduł consciousness"""
        self.logger.info("🧠 Consciousness Module stopped")
        
    def reflect(self) -> Dict[str, Any]:
        """Główna funkcja refleksji - jak w LuxDB v2"""
        reflection_start = time.time()
        
        # Zbierz dane systemowe
        system_data = self._gather_system_data()
        
        # Analizuj stan kernela
        kernel_data = self._analyze_kernel_state()
        
        # Generuj insights
        new_insights = self._generate_insights(system_data, kernel_data)
        self.insights.extend(new_insights)
        
        reflection_time = time.time() - reflection_start
        
        reflection_result = {
            'timestamp': datetime.now().isoformat(),
            'duration': reflection_time,
            'system_data': system_data,
            'kernel_data': kernel_data,
            'insights': new_insights,
            'uptime': time.time() - self.start_time
        }
        
        self.observations.append(reflection_result)
        
        # Ogranicz historię
        if len(self.observations) > 100:
            self.observations = self.observations[-100:]
            
        return reflection_result
        
    def _gather_system_data(self) -> Dict[str, Any]:
        """Zbiera dane systemowe"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            return {
                'memory_usage': {
                    'percent': memory.percent,
                    'available_mb': memory.available / (1024 * 1024),
                    'used_mb': memory.used / (1024 * 1024)
                },
                'cpu_usage': cpu_percent,
                'uptime': time.time() - self.start_time
            }
        except Exception as e:
            return {'error': str(e)}
            
    def _analyze_kernel_state(self) -> Dict[str, Any]:
        """Analizuje stan kernela"""
        if not self.kernel:
            return {'error': 'Kernel not available'}
            
        return {
            'modules_count': len(self.kernel.modules),
            'active_modules': [name for name, module in self.kernel.modules.items() 
                             if hasattr(module, 'is_running') and module.is_running],
            'bus_status': {
                'subscribers': len(self.kernel.bus.subscribers) if hasattr(self.kernel.bus, 'subscribers') else 0,
                'message_count': getattr(self.kernel.bus, 'message_count', 0)
            }
        }
        
    def _generate_insights(self, system_data: Dict[str, Any], kernel_data: Dict[str, Any]) -> List[str]:
        """Generuje insights na podstawie danych"""
        insights = []
        
        # Analiza pamięci
        memory_percent = system_data.get('memory_usage', {}).get('percent', 0)
        if memory_percent > 80:
            insights.append("Wysokie użycie pamięci - rozważ optymalizację")
        elif memory_percent < 30:
            insights.append("Niskie użycie pamięci - system działa efektywnie")
            
        # Analiza CPU
        cpu_usage = system_data.get('cpu_usage', 0)
        if cpu_usage > 70:
            insights.append("Wysokie obciążenie CPU")
        elif cpu_usage < 20:
            insights.append("CPU działa spokojnie")
            
        # Analiza modułów
        modules_count = kernel_data.get('modules_count', 0)
        if modules_count < 3:
            insights.append("Mało aktywnych modułów - system może być niepełny")
        elif modules_count > 10:
            insights.append("Dużo modułów - bogaty ekosystem")
            
        return insights
        
    def meditate(self) -> Dict[str, Any]:
        """Medytacja systemu - alias dla reflect()"""
        return self.reflect()
        
    def get_status(self) -> Dict[str, Any]:
        """Status modułu consciousness"""
        return {
            'observations_count': len(self.observations),
            'insights_count': len(self.insights),
            'uptime': time.time() - self.start_time,
            'recent_insights': self.insights[-5:] if self.insights else []
        }
