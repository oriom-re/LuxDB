
"""
⚖️ Resource Governor - Monitor i zarządca zasobów systemu

Kontroluje CPU, RAM i kolejki eventów
Zapobiega przeciążeniom i zarządza wielordzeniowością
"""

import asyncio
import psutil
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class ResourceGovernor:
    """
    Zarządca zasobów systemu
    
    Monitoruje i kontroluje:
    - Użycie CPU i RAM
    - Liczba aktywnych wątków
    - Obciążenie kolejek
    - Wielordzeniowość
    """
    
    def __init__(self, config: Dict[str, Any], logger):
        self.config = config
        self.logger = logger
        self.running = False
        
        # Limity zasobów
        self.cpu_limit = config.get('cpu_limit', 80)  # %
        self.memory_limit = config.get('memory_limit', 80)  # %
        self.thread_limit = config.get('thread_limit', 100)
        
        # Statystyki
        self.stats = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'thread_count': 0,
            'checks_performed': 0,
            'warnings_issued': 0,
            'last_check': None
        }
        
        # Flagi ostrzeżeń
        self.cpu_warning = False
        self.memory_warning = False
        self.thread_warning = False
        
        # Mechanizm tłumienia ostrzeżeń
        self.warning_cooldown = 30  # sekundy
        self.last_cpu_warning = 0
        self.last_memory_warning = 0
        self.last_thread_warning = 0
        
        self.logger.debug("⚖️ Resource Governor initialized")
    
    async def start(self):
        """Uruchamia Resource Governor"""
        self.running = True
        self.logger.info("⚖️ Resource Governor started")
        
        # Uruchom monitoring w tle
        asyncio.create_task(self._monitoring_loop())
    
    async def stop(self):
        """Zatrzymuje Resource Governor"""
        self.running = False
        self.logger.info("⚖️ Resource Governor stopped")
    
    async def check_resources(self) -> Dict[str, Any]:
        """Sprawdza aktualne wykorzystanie zasobów"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Pamięć
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Wątki
            thread_count = threading.active_count()
            
            # Aktualizuj statystyki
            self.stats.update({
                'cpu_usage': cpu_percent,
                'memory_usage': memory_percent,
                'thread_count': thread_count,
                'checks_performed': self.stats['checks_performed'] + 1,
                'last_check': datetime.now().isoformat()
            })
            
            # Sprawdź limity
            status = self._check_limits(cpu_percent, memory_percent, thread_count)
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory_percent,
                'thread_count': thread_count,
                'cpu_available_cores': psutil.cpu_count(),
                'memory_available_gb': memory.available / (1024**3),
                'warnings': status['warnings'],
                'critical': status['critical']
            }
            
        except Exception as e:
            self.logger.error(f"❌ Resource check failed: {e}")
            return {'error': str(e), 'critical': True}
    
    def _check_limits(self, cpu_percent: float, memory_percent: float, thread_count: int) -> Dict[str, Any]:
        """Sprawdza czy zasoby przekraczają limity"""
        warnings = []
        critical = False
        current_time = time.time()
        
        # CPU
        if cpu_percent > self.cpu_limit:
            if not self.cpu_warning or (current_time - self.last_cpu_warning) > self.warning_cooldown:
                self.logger.warning(f"⚠️ CPU usage high: {cpu_percent:.1f}%")
                self.cpu_warning = True
                self.last_cpu_warning = current_time
                self.stats['warnings_issued'] += 1
            warnings.append(f"CPU: {cpu_percent:.1f}%")
            
            if cpu_percent > 98:  # Zwiększony próg krytyczny
                critical = True
        else:
            self.cpu_warning = False
        
        # Pamięć
        if memory_percent > self.memory_limit:
            if not self.memory_warning or (current_time - self.last_memory_warning) > self.warning_cooldown:
                self.logger.warning(f"⚠️ Memory usage high: {memory_percent:.1f}%")
                self.memory_warning = True
                self.last_memory_warning = current_time
                self.stats['warnings_issued'] += 1
            warnings.append(f"Memory: {memory_percent:.1f}%")
            
            if memory_percent > 95:
                critical = True
        else:
            self.memory_warning = False
        
        # Wątki
        if thread_count > self.thread_limit:
            if not self.thread_warning or (current_time - self.last_thread_warning) > self.warning_cooldown:
                self.logger.warning(f"⚠️ Thread count high: {thread_count}")
                self.thread_warning = True
                self.last_thread_warning = current_time
                self.stats['warnings_issued'] += 1
            warnings.append(f"Threads: {thread_count}")
        else:
            self.thread_warning = False
        
        return {
            'warnings': warnings,
            'critical': critical
        }
    
    async def _monitoring_loop(self):
        """Główna pętla monitorowania"""
        while self.running:
            try:
                await self.check_resources()
                await asyncio.sleep(10)  # Sprawdzaj co 10 sekund
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring loop error: {e}")
                await asyncio.sleep(15)
    
    def optimize_for_cpu_cores(self) -> Dict[str, Any]:
        """Optymalizuje ustawienia dla dostępnych rdzeni CPU"""
        cpu_count = psutil.cpu_count(logical=False)  # Fizyczne rdzenie
        cpu_logical = psutil.cpu_count(logical=True)  # Logiczne rdzenie
        
        recommendations = {
            'physical_cores': cpu_count,
            'logical_cores': cpu_logical,
            'recommended_workers': min(cpu_count * 2, 8),
            'recommended_thread_limit': cpu_logical * 10
        }
        
        self.logger.info(f"🔧 CPU optimization: {recommendations}")
        return recommendations
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Zwraca szczegółowe informacje o pamięci"""
        memory = psutil.virtual_memory()
        
        return {
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3),
            'used_gb': memory.used / (1024**3),
            'free_gb': memory.free / (1024**3),
            'percent': memory.percent,
            'buffers_gb': getattr(memory, 'buffers', 0) / (1024**3),
            'cached_gb': getattr(memory, 'cached', 0) / (1024**3)
        }
    
    async def is_healthy(self) -> bool:
        """Sprawdza czy Resource Governor jest zdrowy"""
        try:
            last_check = self.stats.get('last_check')
            if not last_check:
                return False
            
            # Sprawdź czy ostatni check był w ostatniej minucie
            last_check_time = datetime.fromisoformat(last_check)
            if datetime.now() - last_check_time > timedelta(minutes=1):
                return False
            
            return self.running
            
        except Exception:
            return False
    
    async def restart(self):
        """Restartuje Resource Governor"""
        self.logger.info("🔄 Restarting Resource Governor")
        await self.stop()
        await asyncio.sleep(0.5)
        await self.start()
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status Resource Governor"""
        return {
            'running': self.running,
            'stats': self.stats.copy(),
            'limits': {
                'cpu_limit': self.cpu_limit,
                'memory_limit': self.memory_limit,
                'thread_limit': self.thread_limit
            },
            'current_warnings': {
                'cpu': self.cpu_warning,
                'memory': self.memory_warning,
                'threads': self.thread_warning
            }
        }
