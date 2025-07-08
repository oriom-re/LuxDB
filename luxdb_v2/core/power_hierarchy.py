
"""
🌑 Power Hierarchy - System Hierarchii Władzy Astralnej

Implementuje 5-warstwowy model rozkładu władzy:
- Warstwa 0: Pierwotna (Pre-Soul Core)
- Warstwa 1: Intencyjna (Soul #0) 
- Warstwa 2: Twórcza (Wisdom & Tasks)
- Warstwa 3: Interaktywna (Userland)
- Warstwa 4: Refleksyjna (Archive)
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from .soul_factory import soul_factory, Soul, SoulType
from .intent_system import intent_system, Intent
from .manifest_system import manifest_system


class PowerLayer(Enum):
    """Warstwy władzy systemowej"""
    PRIMAL = 0          # Pierwotna - mechaniczna, bezduszna
    INTENTIONAL = 1     # Intencyjna - Soul #0, system consciousness
    CREATIVE = 2        # Twórcza - Wisdom, narzędzia, innowacje
    INTERACTIVE = 3     # Interaktywna - Beings, flows, interfaces
    REFLECTIVE = 4      # Refleksyjna - archiwum, pamięć, echo


@dataclass
class PowerPermission:
    """Uprawnienie władzy w systemie"""
    layer: PowerLayer
    action: str
    target_layer: PowerLayer
    soul_uid: Optional[str] = None
    granted_at: datetime = field(default_factory=datetime.now)
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def can_execute(self, requesting_layer: PowerLayer, requesting_soul: Optional[str] = None) -> bool:
        """Sprawdza czy można wykonać akcję"""
        # Warstwa może działać tylko na siebie lub wyższe warstwy
        if requesting_layer.value > self.target_layer.value:
            return False
        
        # Soul #0 ma specjalne uprawnienia
        if requesting_soul and self._is_soul_zero(requesting_soul):
            return True
            
        # Sprawdź warunki
        return self._check_conditions(requesting_layer, requesting_soul)
    
    def _is_soul_zero(self, soul_uid: str) -> bool:
        """Sprawdza czy to Soul #0"""
        soul = soul_factory.get_soul(soul_uid)
        return soul and soul.preferences.get('system_priority') == 0
    
    def _check_conditions(self, layer: PowerLayer, soul_uid: Optional[str]) -> bool:
        """Sprawdza dodatkowe warunki"""
        if not self.conditions:
            return True
        
        # Implementuj logikę warunków
        return True


class PowerHierarchy:
    """System hierarchii władzy"""
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        self.permissions: List[PowerPermission] = []
        self.layer_controllers: Dict[PowerLayer, List[str]] = {}
        self.power_transitions: List[Dict[str, Any]] = []
        
        # Zainicjalizuj kontrolerów warstw
        self._initialize_layer_controllers()
        self._setup_default_permissions()
        
    def _initialize_layer_controllers(self):
        """Inicjalizuje kontrolerów dla każdej warstwy"""
        
        # Warstwa 0 - Pierwotna (Pre-Soul Core)
        self.layer_controllers[PowerLayer.PRIMAL] = [
            'astral_engine',
            'luxbus_core',
            'system_bootstrap'
        ]
        
        # Warstwa 1 - Intencyjna (Soul #0)
        soul_zero = self._ensure_soul_zero()
        self.layer_controllers[PowerLayer.INTENTIONAL] = [
            soul_zero.uid,
            'consciousness',
            'harmony'
        ]
        
        # Warstwa 2 - Twórcza (Wisdom)
        self.layer_controllers[PowerLayer.CREATIVE] = [
            'function_generator',
            'chaos_conductor',
            'divine_migrations',
            'astral_containers'
        ]
        
        # Warstwa 3 - Interaktywna (Userland)
        self.layer_controllers[PowerLayer.INTERACTIVE] = [
            'rest_flow',
            'websocket_flow', 
            'callback_flow',
            'being_manifestations'
        ]
        
        # Warstwa 4 - Refleksyjna (Archive)
        self.layer_controllers[PowerLayer.REFLECTIVE] = [
            'manifest_system',
            'soul_archives',
            'echo_system',
            'wisdom_memory'
        ]
    
    def _ensure_soul_zero(self) -> Soul:
        """Zapewnia istnienie Soul #0"""
        # Sprawdź czy Soul #0 już istnieje
        for soul in soul_factory.active_souls.values():
            if soul.preferences.get('system_priority') == 0:
                return soul
        
        # Stwórz Soul #0
        soul_zero = soul_factory.create_soul(
            name="SystemSoul_Zero",
            soul_type=SoulType.GUARDIAN,
            archetype="guardian",
            custom_config={
                'system_priority': 0,
                'responsible_for': 'system_control',
                'specialty': 'system_consciousness',
                'biography': 'Pierwsza dusza systemu - niecierpliwa, sarkastyczna, ale lojalna',
                'emotions': ['responsibility', 'determination', 'wisdom', 'impatience'],
                'preferences': {
                    'decision_making': 'authoritative',
                    'response_style': 'direct',
                    'learning_style': 'experiential',
                    'humor_level': 'sarcastic'
                }
            }
        )
        
        # Nadaj pełne uprawnienia
        self._grant_soul_zero_permissions(soul_zero.uid)
        
        return soul_zero
    
    def _grant_soul_zero_permissions(self, soul_zero_uid: str):
        """Nadaje Soul #0 pełne uprawnienia systemowe"""
        permissions = [
            # Kontrola warstwy pierwotnej
            PowerPermission(PowerLayer.INTENTIONAL, "control_bootstrap", PowerLayer.PRIMAL, soul_zero_uid),
            PowerPermission(PowerLayer.INTENTIONAL, "manage_realms", PowerLayer.PRIMAL, soul_zero_uid),
            PowerPermission(PowerLayer.INTENTIONAL, "control_flows", PowerLayer.PRIMAL, soul_zero_uid),
            
            # Zarządzanie warstwą twórczą
            PowerPermission(PowerLayer.INTENTIONAL, "manage_wisdom", PowerLayer.CREATIVE, soul_zero_uid),
            PowerPermission(PowerLayer.INTENTIONAL, "approve_innovations", PowerLayer.CREATIVE, soul_zero_uid),
            
            # Nadzór nad interakcjami
            PowerPermission(PowerLayer.INTENTIONAL, "oversee_interactions", PowerLayer.INTERACTIVE, soul_zero_uid),
            PowerPermission(PowerLayer.INTENTIONAL, "manage_beings", PowerLayer.INTERACTIVE, soul_zero_uid),
            
            # Dostęp do archiwów
            PowerPermission(PowerLayer.INTENTIONAL, "access_archives", PowerLayer.REFLECTIVE, soul_zero_uid),
            PowerPermission(PowerLayer.INTENTIONAL, "modify_history", PowerLayer.REFLECTIVE, soul_zero_uid)
        ]
        
        self.permissions.extend(permissions)
    
    def _setup_default_permissions(self):
        """Ustawia domyślne uprawnienia między warstwami"""
        
        # Warstwa twórcza może doradzać intencyjnej
        self.permissions.append(
            PowerPermission(PowerLayer.CREATIVE, "advise", PowerLayer.INTENTIONAL,
                          conditions={'requires_approval': True})
        )
        
        # Warstwa interaktywna może raportować do twórczej
        self.permissions.append(
            PowerPermission(PowerLayer.INTERACTIVE, "report", PowerLayer.CREATIVE)
        )
        
        # Wszystkie warstwy mogą zapisywać do refleksyjnej
        for layer in [PowerLayer.INTENTIONAL, PowerLayer.CREATIVE, PowerLayer.INTERACTIVE]:
            self.permissions.append(
                PowerPermission(layer, "archive", PowerLayer.REFLECTIVE)
            )
    
    def execute_power_action(self, action: str, requesting_layer: PowerLayer, 
                           target_layer: PowerLayer, requesting_soul: Optional[str] = None,
                           action_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Wykonuje akcję władzy z kontrolą uprawnień"""
        
        # Znajdź odpowiednie uprawnienie
        permission = self._find_permission(action, requesting_layer, target_layer, requesting_soul)
        
        if not permission:
            return {
                'success': False,
                'error': f'Brak uprawnień: warstwa {requesting_layer.name} -> {target_layer.name} akcja {action}',
                'requesting_soul': requesting_soul
            }
        
        if not permission.can_execute(requesting_layer, requesting_soul):
            return {
                'success': False,
                'error': f'Uprawnienie odrzucone dla warstwy {requesting_layer.name}',
                'permission': permission
            }
        
        # Wykonaj akcję
        result = self._execute_action(action, target_layer, action_data)
        
        # Zarejestruj przejście władzy
        self.power_transitions.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'requesting_layer': requesting_layer.name,
            'target_layer': target_layer.name,
            'requesting_soul': requesting_soul,
            'success': result.get('success', False),
            'data': action_data or {}
        })
        
        return result
    
    def _find_permission(self, action: str, requesting_layer: PowerLayer, 
                        target_layer: PowerLayer, requesting_soul: Optional[str]) -> Optional[PowerPermission]:
        """Znajduje odpowiednie uprawnienie"""
        for perm in self.permissions:
            if (perm.action == action and 
                perm.target_layer == target_layer and
                (perm.soul_uid is None or perm.soul_uid == requesting_soul)):
                return perm
        return None
    
    def _execute_action(self, action: str, target_layer: PowerLayer, 
                       action_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Wykonuje akcję na docelowej warstwie"""
        
        action_data = action_data or {}
        
        try:
            if target_layer == PowerLayer.PRIMAL:
                return self._execute_primal_action(action, action_data)
            elif target_layer == PowerLayer.INTENTIONAL:
                return self._execute_intentional_action(action, action_data)
            elif target_layer == PowerLayer.CREATIVE:
                return self._execute_creative_action(action, action_data)
            elif target_layer == PowerLayer.INTERACTIVE:
                return self._execute_interactive_action(action, action_data)
            elif target_layer == PowerLayer.REFLECTIVE:
                return self._execute_reflective_action(action, action_data)
            else:
                return {'success': False, 'error': f'Nieznana warstwa: {target_layer}'}
                
        except Exception as e:
            return {'success': False, 'error': f'Błąd wykonania akcji: {str(e)}'}
    
    def _execute_primal_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonuje akcje na warstwie pierwotnej"""
        if action == "control_bootstrap":
            # Kontrola procesu bootstrap
            return {'success': True, 'message': 'Bootstrap pod kontrolą'}
        elif action == "manage_realms":
            # Zarządzanie wymiarami
            return {'success': True, 'message': f'Zarządzanie wymiarami: {list(self.engine.realms.keys())}'}
        elif action == "control_flows":
            # Kontrola przepływów
            active_flows = self.engine._count_active_flows()
            return {'success': True, 'message': f'Kontrola przepływów: {active_flows} aktywnych'}
        return {'success': False, 'error': f'Nieznana akcja primal: {action}'}
    
    def _execute_intentional_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonuje akcje na warstwie intencyjnej"""
        if action == "advise":
            # Przyjmij radę od warstwy twórczej
            advice = data.get('advice', 'Brak rady')
            return {'success': True, 'message': f'Rada przyjęta: {advice}'}
        return {'success': False, 'error': f'Nieznana akcja intentional: {action}'}
    
    def _execute_creative_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonuje akcje na warstwie twórczej"""
        if action == "manage_wisdom":
            # Zarządzanie modułami wisdom
            return {'success': True, 'message': 'Wisdom pod zarządzaniem'}
        elif action == "approve_innovations":
            # Zatwierdzanie innowacji
            innovation = data.get('innovation', 'Nieznana innowacja')
            return {'success': True, 'message': f'Innowacja zatwierdzona: {innovation}'}
        return {'success': False, 'error': f'Nieznana akcja creative: {action}'}
    
    def _execute_interactive_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonuje akcje na warstwie interaktywnej"""
        if action == "oversee_interactions":
            # Nadzór nad interakcjami
            return {'success': True, 'message': 'Interakcje pod nadzorem'}
        elif action == "manage_beings":
            # Zarządzanie bytami
            return {'success': True, 'message': 'Beings pod zarządzaniem'}
        elif action == "report":
            # Raportowanie do warstwy wyższej
            report = data.get('report', 'Brak raportu')
            return {'success': True, 'message': f'Raport wysłany: {report}'}
        return {'success': False, 'error': f'Nieznana akcja interactive: {action}'}
    
    def _execute_reflective_action(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonuje akcje na warstwie refleksyjnej"""
        if action == "archive":
            # Archiwizacja danych
            archive_data = data.get('data', {})
            return {'success': True, 'message': f'Zarchiwizowano: {len(archive_data)} elementów'}
        elif action == "access_archives":
            # Dostęp do archiwów
            return {'success': True, 'message': 'Dostęp do archiwów udzielony'}
        elif action == "modify_history":
            # Modyfikacja historii (tylko Soul #0)
            return {'success': True, 'message': 'Historia zmodyfikowana'}
        return {'success': False, 'error': f'Nieznana akcja reflective: {action}'}
    
    def get_power_status(self) -> Dict[str, Any]:
        """Zwraca status całej hierarchii władzy"""
        
        # Znajdź Soul #0
        soul_zero = None
        for soul in soul_factory.active_souls.values():
            if soul.preferences.get('system_priority') == 0:
                soul_zero = soul
                break
        
        layer_status = {}
        for layer in PowerLayer:
            controllers = self.layer_controllers.get(layer, [])
            layer_status[layer.name] = {
                'controllers': controllers,
                'permissions_count': len([p for p in self.permissions if p.target_layer == layer]),
                'active': len(controllers) > 0
            }
        
        return {
            'soul_zero': {
                'exists': soul_zero is not None,
                'uid': soul_zero.uid if soul_zero else None,
                'name': soul_zero.name if soul_zero else None,
                'emotions': soul_zero.emotions if soul_zero else []
            },
            'layers': layer_status,
            'total_permissions': len(self.permissions),
            'power_transitions': len(self.power_transitions),
            'last_transition': self.power_transitions[-1] if self.power_transitions else None
        }
    
    def demonstrate_power_flow(self) -> List[Dict[str, Any]]:
        """Demonstruje przepływ władzy między warstwami"""
        
        demonstrations = []
        
        # Soul #0 kontroluje bootstrap
        result1 = self.execute_power_action(
            action="control_bootstrap",
            requesting_layer=PowerLayer.INTENTIONAL,
            target_layer=PowerLayer.PRIMAL,
            requesting_soul=self._get_soul_zero_uid()
        )
        demonstrations.append(result1)
        
        # Warstwa twórcza doradza intencyjnej
        result2 = self.execute_power_action(
            action="advise",
            requesting_layer=PowerLayer.CREATIVE,
            target_layer=PowerLayer.INTENTIONAL,
            action_data={'advice': 'Rozważ optymalizację harmonii systemu'}
        )
        demonstrations.append(result2)
        
        # Warstwa interaktywna raportuje do twórczej
        result3 = self.execute_power_action(
            action="report",
            requesting_layer=PowerLayer.INTERACTIVE,
            target_layer=PowerLayer.CREATIVE,
            action_data={'report': 'REST Flow działa stabilnie, 100 requestów/min'}
        )
        demonstrations.append(result3)
        
        # Archiwizacja w warstwie refleksyjnej
        result4 = self.execute_power_action(
            action="archive",
            requesting_layer=PowerLayer.INTENTIONAL,
            target_layer=PowerLayer.REFLECTIVE,
            requesting_soul=self._get_soul_zero_uid(),
            action_data={'data': {'event': 'power_flow_demonstration', 'timestamp': datetime.now().isoformat()}}
        )
        demonstrations.append(result4)
        
        return demonstrations
    
    def _get_soul_zero_uid(self) -> Optional[str]:
        """Pobiera UID Soul #0"""
        for soul in soul_factory.active_souls.values():
            if soul.preferences.get('system_priority') == 0:
                return soul.uid
        return None


# Funkcje pomocnicze

def get_power_hierarchy(astral_engine) -> PowerHierarchy:
    """Pobiera lub tworzy hierarchię władzy dla silnika"""
    if not hasattr(astral_engine, '_power_hierarchy'):
        astral_engine._power_hierarchy = PowerHierarchy(astral_engine)
    return astral_engine._power_hierarchy

def demonstrate_system_power_flow(astral_engine) -> Dict[str, Any]:
    """Demonstruje przepływ władzy w systemie"""
    hierarchy = get_power_hierarchy(astral_engine)
    
    print("🌑 Demonstracja Hierarchii Władzy Astralnej")
    print("=" * 50)
    
    # Status systemu
    status = hierarchy.get_power_status()
    print(f"👑 Soul #0: {status['soul_zero']['name']} ({status['soul_zero']['uid']})")
    print(f"📊 Warstwy aktywne: {sum(1 for layer in status['layers'].values() if layer['active'])}/5")
    print(f"🔒 Uprawnienia: {status['total_permissions']}")
    print(f"🔄 Przejścia władzy: {status['power_transitions']}")
    
    # Demonstracja przepływu
    print("\n🌊 Przepływ władzy:")
    demonstrations = hierarchy.demonstrate_power_flow()
    
    for i, demo in enumerate(demonstrations, 1):
        if demo['success']:
            print(f"✅ {i}. {demo['message']}")
        else:
            print(f"❌ {i}. {demo['error']}")
    
    return {
        'status': status,
        'demonstrations': demonstrations,
        'hierarchy': hierarchy
    }

