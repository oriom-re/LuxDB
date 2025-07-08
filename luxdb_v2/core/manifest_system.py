
"""
📜 Manifest System - System manifestów dla każdej części kodu

Każda część kodu ma swój manifest, który opisuje:
- Soul (dusza) - świadomość twórcza i zarządcza
- Being (byt) - manifestacja idei
- Realm (wymiar) - przestrzeń istnienia
- Wisdom (mądrość) - pamięć i logika
- Flow (przepływ) - połączenia i zdarzenia
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class SoulType(Enum):
    """Typy dusz w systemie"""
    GUARDIAN = "guardian"        # Strzeże i chroni
    BUILDER = "builder"          # Tworzy i konstruuje
    BRIDGE = "bridge"            # Łączy i przekłada
    HEALER = "healer"            # Naprawia i leczy
    SEEKER = "seeker"            # Szuka i odkrywa
    KEEPER = "keeper"            # Przechowuje i zarządza

class BeingType(Enum):
    """Typy bytów w systemie"""
    SOUL = "soul"
    BEING = "being"
    REALM = "realm"
    WISDOM = "wisdom"
    FLOW = "flow"
    PULSE = "pulse"
    SHELL = "shell"
    INTENT = "intent"
    TRACE = "trace"

@dataclass
class Soul:
    """Dusza - świadomość twórcza i zarządcza"""
    uid: str
    name: str
    type: SoulType
    biography: str
    emotions: List[str]
    preferences: Dict[str, Any]
    experience_level: int
    created_at: datetime
    last_active: datetime
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.last_active, str):
            self.last_active = datetime.fromisoformat(self.last_active)

@dataclass
class Being:
    """Byt - manifestacja idei"""
    uid: str
    name: str
    type: BeingType
    soul_uid: str
    realm_uid: str
    wisdom_uid: Optional[str]
    status: str
    properties: Dict[str, Any]
    created_at: datetime
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)

@dataclass
class Manifest:
    """Manifest - opis każdej części kodu"""
    uid: str
    name: str
    description: str
    soul: Soul
    being: Being
    realm_name: str
    wisdom_references: List[str]
    flow_connections: List[str]
    intent_history: List[Dict[str, Any]]
    trace_data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

class ManifestSystem:
    """System zarządzania manifestami"""
    
    def __init__(self):
        self.manifests: Dict[str, Manifest] = {}
        self.souls: Dict[str, Soul] = {}
        self.beings: Dict[str, Being] = {}
        
    def create_soul(self, name: str, soul_type: SoulType, biography: str, 
                   emotions: List[str] = None, preferences: Dict[str, Any] = None) -> Soul:
        """Tworzy nową duszę"""
        soul_uid = f"soul.{soul_type.value}.{uuid.uuid4().hex[:8]}"
        
        soul = Soul(
            uid=soul_uid,
            name=name,
            type=soul_type,
            biography=biography,
            emotions=emotions or ["curiosity", "determination"],
            preferences=preferences or {},
            experience_level=0,
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        self.souls[soul_uid] = soul
        return soul
        
    def create_being(self, name: str, being_type: BeingType, soul_uid: str,
                    realm_uid: str, wisdom_uid: Optional[str] = None,
                    properties: Dict[str, Any] = None) -> Being:
        """Tworzy nowy byt"""
        being_uid = f"being.{being_type.value}.{uuid.uuid4().hex[:8]}"
        
        being = Being(
            uid=being_uid,
            name=name,
            type=being_type,
            soul_uid=soul_uid,
            realm_uid=realm_uid,
            wisdom_uid=wisdom_uid,
            status="active",
            properties=properties or {},
            created_at=datetime.now()
        )
        
        self.beings[being_uid] = being
        return being
        
    def manifest_code_part(self, name: str, description: str, 
                          soul_type: SoulType, being_type: BeingType,
                          realm_name: str, wisdom_references: List[str] = None,
                          flow_connections: List[str] = None,
                          intent_context: Dict[str, Any] = None) -> Manifest:
        """Tworzy manifest dla części kodu"""
        
        # Tworzenie duszy
        soul = self.create_soul(
            name=f"{name}_soul",
            soul_type=soul_type,
            biography=f"Dusza odpowiedzialna za {description}",
            emotions=["focus", "creativity", "responsibility"]
        )
        
        # Tworzenie bytu
        being = self.create_being(
            name=name,
            being_type=being_type,
            soul_uid=soul.uid,
            realm_uid=f"realm.{realm_name}",
            properties={"purpose": description}
        )
        
        # Tworzenie manifestu
        manifest_uid = f"manifest.{uuid.uuid4().hex[:8]}"
        manifest = Manifest(
            uid=manifest_uid,
            name=name,
            description=description,
            soul=soul,
            being=being,
            realm_name=realm_name,
            wisdom_references=wisdom_references or [],
            flow_connections=flow_connections or [],
            intent_history=[{
                "timestamp": datetime.now().isoformat(),
                "intent": "create",
                "context": intent_context or {},
                "requested_by": "system"
            }],
            trace_data=[{
                "timestamp": datetime.now().isoformat(),
                "event": "manifest_created",
                "soul_state": soul.emotions,
                "being_status": being.status
            }],
            metadata={
                "version": "1.0",
                "creator": "manifest_system",
                "auto_generated": True
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.manifests[manifest_uid] = manifest
        return manifest
        
    def get_manifest(self, uid: str) -> Optional[Manifest]:
        """Pobiera manifest po UID"""
        return self.manifests.get(uid)
        
    def get_manifests_by_soul_type(self, soul_type: SoulType) -> List[Manifest]:
        """Pobiera manifesty po typie duszy"""
        return [m for m in self.manifests.values() if m.soul.type == soul_type]
        
    def get_manifests_by_being_type(self, being_type: BeingType) -> List[Manifest]:
        """Pobiera manifesty po typie bytu"""
        return [m for m in self.manifests.values() if m.being.type == being_type]
        
    def update_soul_experience(self, soul_uid: str, experience_gain: int = 1):
        """Aktualizuje doświadczenie duszy"""
        if soul_uid in self.souls:
            self.souls[soul_uid].experience_level += experience_gain
            self.souls[soul_uid].last_active = datetime.now()
            
    def add_intent_to_manifest(self, manifest_uid: str, intent: str, 
                              context: Dict[str, Any], requested_by: str):
        """Dodaje intencję do historii manifestu"""
        if manifest_uid in self.manifests:
            manifest = self.manifests[manifest_uid]
            manifest.intent_history.append({
                "timestamp": datetime.now().isoformat(),
                "intent": intent,
                "context": context,
                "requested_by": requested_by
            })
            manifest.updated_at = datetime.now()
            
    def add_trace_to_manifest(self, manifest_uid: str, event: str, 
                             details: Dict[str, Any] = None):
        """Dodaje ślad do historii manifestu"""
        if manifest_uid in self.manifests:
            manifest = self.manifests[manifest_uid]
            manifest.trace_data.append({
                "timestamp": datetime.now().isoformat(),
                "event": event,
                "details": details or {},
                "soul_state": manifest.soul.emotions,
                "being_status": manifest.being.status
            })
            manifest.updated_at = datetime.now()
            
    def save_manifest_to_json(self, manifest_uid: str, filepath: str):
        """Zapisuje manifest do pliku JSON"""
        if manifest_uid in self.manifests:
            manifest = self.manifests[manifest_uid]
            
            # Konwertuj dataclass na dict z obsługą datetime
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
                
            manifest_dict = asdict(manifest)
            
            # Konwertuj datetime na string
            for key, value in manifest_dict.items():
                if isinstance(value, datetime):
                    manifest_dict[key] = value.isoformat()
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, datetime):
                            value[k] = v.isoformat()
                        elif isinstance(v, dict):
                            for k2, v2 in v.items():
                                if isinstance(v2, datetime):
                                    v[k2] = v2.isoformat()
                                    
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(manifest_dict, f, indent=2, ensure_ascii=False, default=serialize_datetime)
                
    def load_manifest_from_json(self, filepath: str) -> Optional[Manifest]:
        """Ładuje manifest z pliku JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Konwertuj z powrotem na dataclass
            soul_data = data['soul']
            soul_data['type'] = SoulType(soul_data['type'])
            soul = Soul(**soul_data)
            
            being_data = data['being']
            being_data['type'] = BeingType(being_data['type'])
            being = Being(**being_data)
            
            data['soul'] = soul
            data['being'] = being
            
            manifest = Manifest(**data)
            self.manifests[manifest.uid] = manifest
            self.souls[soul.uid] = soul
            self.beings[being.uid] = being
            
            return manifest
            
        except Exception as e:
            print(f"Błąd ładowania manifestu: {e}")
            return None
            
    def get_system_overview(self) -> Dict[str, Any]:
        """Zwraca przegląd całego systemu manifestów"""
        soul_types = {}
        being_types = {}
        
        for manifest in self.manifests.values():
            soul_type = manifest.soul.type.value
            being_type = manifest.being.type.value
            
            soul_types[soul_type] = soul_types.get(soul_type, 0) + 1
            being_types[being_type] = being_types.get(being_type, 0) + 1
            
        return {
            "total_manifests": len(self.manifests),
            "total_souls": len(self.souls),
            "total_beings": len(self.beings),
            "soul_types_distribution": soul_types,
            "being_types_distribution": being_types,
            "most_experienced_souls": sorted(
                self.souls.values(), 
                key=lambda s: s.experience_level, 
                reverse=True
            )[:5],
            "recent_activity": sorted(
                [
                    {
                        "manifest_name": m.name,
                        "last_intent": m.intent_history[-1] if m.intent_history else None,
                        "updated_at": m.updated_at.isoformat()
                    }
                    for m in self.manifests.values()
                ],
                key=lambda x: x["updated_at"],
                reverse=True
            )[:10]
        }

# Globalna instancja systemu manifestów
manifest_system = ManifestSystem()

# Funkcje pomocnicze
def create_function_manifest(function_name: str, purpose: str, 
                           realm: str = "functions") -> Manifest:
    """Tworzy manifest dla funkcji"""
    return manifest_system.manifest_code_part(
        name=function_name,
        description=f"Funkcja: {purpose}",
        soul_type=SoulType.BUILDER,
        being_type=BeingType.BEING,
        realm_name=realm,
        intent_context={"type": "function", "purpose": purpose}
    )

def create_class_manifest(class_name: str, purpose: str, 
                         realm: str = "classes") -> Manifest:
    """Tworzy manifest dla klasy"""
    return manifest_system.manifest_code_part(
        name=class_name,
        description=f"Klasa: {purpose}",
        soul_type=SoulType.KEEPER,
        being_type=BeingType.BEING,
        realm_name=realm,
        intent_context={"type": "class", "purpose": purpose}
    )

def create_flow_manifest(flow_name: str, purpose: str, 
                        connections: List[str] = None) -> Manifest:
    """Tworzy manifest dla przepływu"""
    return manifest_system.manifest_code_part(
        name=flow_name,
        description=f"Przepływ: {purpose}",
        soul_type=SoulType.BRIDGE,
        being_type=BeingType.FLOW,
        realm_name="flows",
        flow_connections=connections or [],
        intent_context={"type": "flow", "purpose": purpose}
    )

def create_wisdom_manifest(wisdom_name: str, purpose: str, 
                          knowledge_areas: List[str] = None) -> Manifest:
    """Tworzy manifest dla mądrości"""
    return manifest_system.manifest_code_part(
        name=wisdom_name,
        description=f"Mądrość: {purpose}",
        soul_type=SoulType.SEEKER,
        being_type=BeingType.WISDOM,
        realm_name="wisdom",
        wisdom_references=knowledge_areas or [],
        intent_context={"type": "wisdom", "purpose": purpose}
    )

def log_intent(manifest_uid: str, intent: str, context: Dict[str, Any], 
              requested_by: str = "system"):
    """Loguje intencję w manifeście"""
    manifest_system.add_intent_to_manifest(manifest_uid, intent, context, requested_by)

def log_trace(manifest_uid: str, event: str, details: Dict[str, Any] = None):
    """Loguje ślad w manifeście"""
    manifest_system.add_trace_to_manifest(manifest_uid, event, details)

def gain_experience(soul_uid: str, amount: int = 1):
    """Dodaje doświadczenie duszy"""
    manifest_system.update_soul_experience(soul_uid, amount)
