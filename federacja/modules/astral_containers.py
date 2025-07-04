
"""
🔮 Astral Containers Module - Inteligentne kontenery danych

Port z LuxDB v2 - system przepływu danych między funkcjami
"""

import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from ..core.lux_module import LuxModule


class ContainerState(Enum):
    """Stany kontenera astralnego"""
    NASCENT = "nascent"
    FLOWING = "flowing"
    VALIDATED = "validated"
    TRANSFORMED = "transformed"
    COMPLETED = "completed"
    ERROR = "error"


class AstralDataContainer:
    """Kontener danych astralnych - port z LuxDB v2"""
    
    def __init__(self, initial_data: Dict[str, Any] = None, container_id: str = None):
        self.container_id = container_id or f"astral_{uuid.uuid4().hex[:12]}"
        self.created_at = datetime.now()
        self.current_data = initial_data or {}
        self.state = ContainerState.NASCENT
        self.history = []
        self.function_stack = []
        
    def transition_to(self, new_state: ContainerState, function_name: str = None):
        """Przejście do nowego stanu"""
        transition = {
            'from_state': self.state.value,
            'to_state': new_state.value,
            'function_name': function_name,
            'timestamp': datetime.now().isoformat()
        }
        self.history.append(transition)
        self.state = new_state
        
    def get_data_for_function(self, function_name: str) -> Dict[str, Any]:
        """Pobiera dane dla funkcji"""
        self.transition_to(ContainerState.FLOWING, function_name)
        self.function_stack.append(function_name)
        return self.current_data.copy()
        
    def add_function_result(self, function_name: str, result: Dict[str, Any]):
        """Dodaje wynik funkcji"""
        if isinstance(result, dict):
            self.current_data.update(result)
        else:
            self.current_data[f'{function_name}_result'] = result
        self.transition_to(ContainerState.TRANSFORMED, function_name)
        
    def complete_flow(self, function_name: str = None):
        """Kończy przepływ"""
        self.transition_to(ContainerState.COMPLETED, function_name)
        
    def get_history_summary(self) -> Dict[str, Any]:
        """Podsumowanie historii"""
        return {
            'container_id': self.container_id,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'transitions_count': len(self.history),
            'function_stack': self.function_stack
        }


class AstralContainersModule(LuxModule):
    """Moduł kontenerów astralnych - portowany z LuxDB v2"""
    
    def __init__(self, kernel, config: Dict[str, Any], logger):
        super().__init__(kernel, config, logger)
        self.active_containers: Dict[str, AstralDataContainer] = {}
        self.completed_containers: Dict[str, AstralDataContainer] = {}
        self.total_containers = 0
        
    async def initialize(self) -> bool:
        """Inicjalizuje moduł"""
        self.logger.info("🔮 Astral Containers Module initializing...")
        return True
        
    async def start(self) -> bool:
        """Uruchamia moduł"""
        self.logger.info("🔮 Astral Containers Module started")
        return True
        
    async def stop(self):
        """Zatrzymuje moduł"""
        self.logger.info("🔮 Astral Containers Module stopped")
        
    def create_container(self, initial_data: Dict[str, Any] = None, 
                        origin_function: str = None) -> AstralDataContainer:
        """Tworzy nowy kontener"""
        container = AstralDataContainer(initial_data)
        
        if origin_function:
            container.function_stack.append(origin_function)
            
        self.active_containers[container.container_id] = container
        self.total_containers += 1
        
        self.logger.info(f"🔮 Utworzono kontener: {container.container_id}")
        return container
        
    def get_container(self, container_id: str) -> Optional[AstralDataContainer]:
        """Pobiera kontener po ID"""
        return (self.active_containers.get(container_id) or 
                self.completed_containers.get(container_id))
                
    def complete_container(self, container_id: str) -> bool:
        """Kończy kontener"""
        if container_id in self.active_containers:
            container = self.active_containers[container_id]
            container.complete_flow('system')
            
            self.completed_containers[container_id] = container
            del self.active_containers[container_id]
            
            self.logger.info(f"🔮 Kontener {container_id} zakończony")
            return True
        return False
        
    def list_active_containers(self) -> List[Dict[str, Any]]:
        """Lista aktywnych kontenerów"""
        return [container.get_history_summary() 
                for container in self.active_containers.values()]
                
    def get_statistics(self) -> Dict[str, Any]:
        """Statystyki kontenerów"""
        return {
            'total_containers': self.total_containers,
            'active_containers': len(self.active_containers),
            'completed_containers': len(self.completed_containers)
        }
        
    def get_status(self) -> Dict[str, Any]:
        """Status modułu"""
        return {
            'active_containers': len(self.active_containers),
            'completed_containers': len(self.completed_containers),
            'total_created': self.total_containers
        }
