
"""
🧬 LuxBase - Bazowa klasa wszystkich bytów w systemie LuxDB

Każdy byt ma unikalny identyfikator i zapis genetyczny dla śledzenia
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class GeneticRecord:
    """Zapis genetyczny bytu"""
    creation_time: datetime = field(default_factory=datetime.now)
    creator_id: Optional[str] = None
    parent_uuid: Optional[str] = None
    mutations: List[Dict[str, Any]] = field(default_factory=list)
    lineage: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'creation_time': self.creation_time.isoformat(),
            'creator_id': self.creator_id,
            'parent_uuid': self.parent_uuid,
            'mutations': self.mutations,
            'lineage': self.lineage
        }


class LuxBase:
    """
    Bazowa klasa wszystkich bytów w systemie LuxDB
    
    Zapewnia:
    - Unikalny identyfikator (UUID)
    - Zapis genetyczny (dla przyszłego śledzenia)
    - Podstawowe metody identyfikacji
    """
    
    def __init__(self, parent_uuid: Optional[str] = None, creator_id: Optional[str] = None):
        self.uuid = str(uuid.uuid4())
        self.genetic_record = GeneticRecord(
            creator_id=creator_id,
            parent_uuid=parent_uuid
        )
        self.created_at = datetime.now()
        
        # Jeśli ma rodzica, dodaj do lineage
        if parent_uuid:
            self.genetic_record.lineage.append(parent_uuid)
    
    def get_uuid(self) -> str:
        """Zwraca unikalny identyfikator"""
        return self.uuid
    
    def get_genetic_record(self) -> GeneticRecord:
        """Zwraca zapis genetyczny"""
        return self.genetic_record
    
    def add_mutation(self, mutation_type: str, data: Dict[str, Any]) -> None:
        """Dodaje mutację do zapisu genetycznego"""
        mutation = {
            'type': mutation_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.genetic_record.mutations.append(mutation)
    
    def get_lineage(self) -> List[str]:
        """Zwraca rodowód (UUID rodziców)"""
        return self.genetic_record.lineage.copy()
    
    def get_creation_info(self) -> Dict[str, Any]:
        """Zwraca informacje o powstaniu"""
        return {
            'uuid': self.uuid,
            'created_at': self.created_at.isoformat(),
            'creator_id': self.genetic_record.creator_id,
            'parent_uuid': self.genetic_record.parent_uuid,
            'lineage': self.genetic_record.lineage,
            'mutations_count': len(self.genetic_record.mutations)
        }
    
    def __str__(self) -> str:
        return f"LuxBase({self.uuid[:8]}...)"
    
    def __repr__(self) -> str:
        return f"LuxBase(uuid='{self.uuid}', created_at='{self.created_at.isoformat()}')"
