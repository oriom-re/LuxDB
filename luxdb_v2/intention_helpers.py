
"""
🎯 Intention Helpers - Pomocnicze funkcje dla systemu intencji

Zestaw wygodnych funkcji do pracy z intencjami w LuxDB v2
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .core.astral_engine import AstralEngine
from .beings.intention_being import IntentionState, IntentionPriority


def create_simple_intention(
    engine: AstralEngine,
    nazwa: str,
    opis_intencji: str,
    zadanie: str,
    priority: str = "NORMAL",
    realm_name: str = "intentions"
) -> Dict[str, Any]:
    """
    Tworzy prostą intencję z podstawowymi parametrami
    
    Args:
        engine: Silnik astralny
        nazwa: Nazwa intencji
        opis_intencji: Opis duchowy intencji
        zadanie: Konkretne zadanie do wykonania
        priority: Priorytet (LOW, NORMAL, HIGH, CRITICAL)
        realm_name: Nazwa wymiaru
        
    Returns:
        Status utworzonej intencji
    """
    intention_data = {
        'nazwa': nazwa,
        'priority': getattr(IntentionPriority, priority.upper(), IntentionPriority.NORMAL).value,
        'duchowa': {
            'opis_intencji': opis_intencji,
            'emocje': ['determination', 'focus'],
            'kontekst': f'Intencja utworzona {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'energia_duchowa': 100.0
        },
        'materialna': {
            'zadanie': zadanie,
            'wymagania': [],
            'oczekiwany_rezultat': f'Zrealizowanie: {zadanie}'
        },
        'metainfo': {
            'zrodlo': 'intention_helpers',
            'glebokosc': 1,
            'tags': ['simple', 'helper_created']
        }
    }
    
    intention = engine.manifest_intention(intention_data, realm_name)
    return intention.get_status()


def wzmocnij_intencje(
    engine: AstralEngine,
    intention_ids: List[str],
    power: int = 15,
    user_id: str = "system",
    realm_name: str = "intentions"
) -> Dict[str, Any]:
    """
    Wzmacnia listę intencji
    
    Args:
        engine: Silnik astralny
        intention_ids: Lista ID intencji
        power: Siła wzmocnienia
        user_id: ID użytkownika
        realm_name: Nazwa wymiaru
        
    Returns:
        Wyniki wzmocnień
    """
    results = {}
    
    for intention_id in intention_ids:
        result = engine.interact_with_intention(
            intention_id,
            'wzmocnij',
            {'power': power},
            user_id,
            realm_name
        )
        results[intention_id] = result
    
    return {
        'wzmocnione_intencje': len([r for r in results.values() if r.get('success')]),
        'nieudane': len([r for r in results.values() if not r.get('success')]),
        'details': results
    }


def znajdz_intencje_do_realizacji(
    engine: AstralEngine,
    realm_name: str = "intentions"
) -> List[Dict[str, Any]]:
    """
    Znajduje intencje gotowe do realizacji
    
    Args:
        engine: Silnik astralny
        realm_name: Nazwa wymiaru
        
    Returns:
        Lista intencji gotowych do realizacji
    """
    return engine.contemplate_intentions({
        'state': IntentionState.APPROVED.value,
        'min_harmony': 70.0,
        'sort_by': 'priority',
        'order': 'desc'
    }, realm_name)


def znajdz_stare_intencje(
    engine: AstralEngine,
    days_old: int = 7,
    realm_name: str = "intentions"
) -> List[Dict[str, Any]]:
    """
    Znajduje stare intencje do przeglądu
    
    Args:
        engine: Silnik astralny
        days_old: Wiek w dniach
        realm_name: Nazwa wymiaru
        
    Returns:
        Lista starych intencji
    """
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    # Tu byłaby logika filtrowania po dacie utworzenia
    # Na razie zwracamy wszystkie w stanie CONCEIVED starsze niż określony wiek
    return engine.contemplate_intentions({
        'state': IntentionState.CONCEIVED.value,
        'sort_by': 'created_at',
        'order': 'asc'
    }, realm_name)


def grupuj_intencje_po_priorytecie(
    intentions: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Grupuje intencje według priorytetu
    
    Args:
        intentions: Lista intencji
        
    Returns:
        Słownik pogrupowanych intencji
    """
    grouped = {
        'CRITICAL': [],
        'HIGH': [],
        'NORMAL': [],
        'LOW': []
    }
    
    for intention in intentions:
        intention_specific = intention.get('intention_specific', {})
        priority = intention_specific.get('priority', 2)  # NORMAL default
        
        # Konwertuj liczbę na nazwę
        priority_names = {4: 'CRITICAL', 3: 'HIGH', 2: 'NORMAL', 1: 'LOW'}
        priority_name = priority_names.get(priority, 'NORMAL')
        
        grouped[priority_name].append(intention)
    
    return grouped


def raport_intencji(
    engine: AstralEngine,
    realm_name: str = "intentions"
) -> Dict[str, Any]:
    """
    Generuje raport o stanie intencji
    
    Args:
        engine: Silnik astralny
        realm_name: Nazwa wymiaru
        
    Returns:
        Pełny raport
    """
    wszystkie_intencje = engine.contemplate_intentions({}, realm_name)
    
    # Statystyki stanów
    stany = {}
    priorytety = {}
    suma_harmony = 0
    suma_success = 0
    
    for intention in wszystkie_intencje:
        intention_specific = intention.get('intention_specific', {})
        
        # Stan
        stan = intention_specific.get('state', 'unknown')
        stany[stan] = stany.get(stan, 0) + 1
        
        # Priorytet
        priority = intention_specific.get('priority', 2)
        priority_names = {4: 'CRITICAL', 3: 'HIGH', 2: 'NORMAL', 1: 'LOW'}
        priority_name = priority_names.get(priority, 'NORMAL')
        priorytety[priority_name] = priorytety.get(priority_name, 0) + 1
        
        # Średnie
        suma_harmony += intention_specific.get('harmony_score', 0)
        metainfo = intention_specific.get('metainfo', {})
        suma_success += metainfo.get('wskaznik_sukcesu', 0)
    
    total = len(wszystkie_intencje)
    
    return {
        'timestamp': datetime.now().isoformat(),
        'total_intencji': total,
        'rozkład_stanów': stany,
        'rozkład_priorytetów': priorytety,
        'średnia_harmonia': round(suma_harmony / max(1, total), 2),
        'średni_wskaźnik_sukcesu': round(suma_success / max(1, total), 2),
        'gotowe_do_realizacji': len([
            i for i in wszystkie_intencje 
            if i.get('intention_specific', {}).get('state') == 'approved'
        ]),
        'w_realizacji': len([
            i for i in wszystkie_intencje 
            if i.get('intention_specific', {}).get('state') == 'manifesting'
        ]),
        'zakończone': len([
            i for i in wszystkie_intencje 
            if i.get('intention_specific', {}).get('state') == 'completed'
        ])
    }


def automated_intention_workflow(
    engine: AstralEngine,
    intention_data: Dict[str, Any],
    auto_contemplate: bool = True,
    auto_approve_threshold: float = 0.8,
    auto_assign_guardian: Optional[str] = None,
    realm_name: str = "intentions"
) -> Dict[str, Any]:
    """
    Automatyczny workflow dla intencji
    
    Args:
        engine: Silnik astralny
        intention_data: Dane intencji
        auto_contemplate: Czy automatycznie kontemplować
        auto_approve_threshold: Próg dla automatycznego zatwierdzenia
        auto_assign_guardian: ID opiekuna do automatycznego przypisania
        realm_name: Nazwa wymiaru
        
    Returns:
        Pełny raport workflow
    """
    workflow_log = []
    
    # 1. Manifestuj intencję
    intention = engine.manifest_intention(intention_data, realm_name)
    intention_id = intention.essence.soul_id
    workflow_log.append(f"✨ Intencja '{intention.essence.name}' zmanifestowana")
    
    # 2. Automatyczna kontemplacja
    if auto_contemplate:
        # Symulacja kontemplacji przez dodanie interakcji
        engine.interact_with_intention(
            intention_id, 'wzmocnij', {'power': 20}, 'auto_workflow', realm_name
        )
        workflow_log.append("🧘 Automatyczna kontemplacja przeprowadzona")
    
    # 3. Przypisz opiekuna jeśli podano
    if auto_assign_guardian:
        result = engine.interact_with_intention(
            intention_id, 'przypisz_opiekuna', 
            {'opiekun_id': auto_assign_guardian}, 'auto_workflow', realm_name
        )
        if result.get('success'):
            workflow_log.append(f"👤 Opiekun {auto_assign_guardian} przypisany")
    
    # 4. Sprawdź czy można automatycznie zatwierdzić
    status = engine.get_intention_status(intention_id, realm_name)
    intention_specific = status.get('intention_specific', {})
    harmony_score = intention_specific.get('harmony_score', 0) / 100
    
    if harmony_score >= auto_approve_threshold:
        # Zmień stan na contemplated (normalnie byłoby to poprzez interakcje)
        # Tu symulujemy zatwierdzenie
        approve_result = engine.interact_with_intention(
            intention_id, 'zatwierdz', {}, 'auto_workflow', realm_name
        )
        if approve_result.get('success'):
            workflow_log.append(f"✅ Intencja automatycznie zatwierdzona (harmonia: {harmony_score:.2f})")
        else:
            workflow_log.append(f"⚠️ Nie udało się automatycznie zatwierdzić: {approve_result.get('message')}")
    else:
        workflow_log.append(f"📋 Intencja wymaga ręcznego zatwierdzenia (harmonia: {harmony_score:.2f} < {auto_approve_threshold})")
    
    # 5. Finalny status
    final_status = engine.get_intention_status(intention_id, realm_name)
    
    return {
        'intention_id': intention_id,
        'workflow_completed': True,
        'workflow_log': workflow_log,
        'final_status': final_status,
        'harmony_achieved': harmony_score,
        'auto_approved': harmony_score >= auto_approve_threshold
    }


# Szybkie funkcje pomocnicze
def quick_intention(engine: AstralEngine, description: str, task: str) -> str:
    """Szybkie utworzenie intencji - zwraca ID"""
    status = create_simple_intention(engine, f"Quick_{datetime.now().strftime('%H%M')}", description, task)
    return status['essence']['soul_id']


def boost_all_intentions(engine: AstralEngine, power: int = 10) -> int:
    """Wzmacnia wszystkie aktywne intencje - zwraca liczbę wzmocnionych"""
    intentions = engine.contemplate_intentions({})
    intention_ids = [i['essence']['soul_id'] for i in intentions]
    results = wzmocnij_intencje(engine, intention_ids, power)
    return results['wzmocnione_intencje']


def get_intention_summary(engine: AstralEngine) -> str:
    """Zwraca krótkie podsumowanie stanu intencji"""
    raport = raport_intencji(engine)
    return (f"📊 Intencje: {raport['total_intencji']} total, "
            f"{raport['gotowe_do_realizacji']} gotowe, "
            f"{raport['w_realizacji']} w realizacji, "
            f"średnia harmonia: {raport['średnia_harmonia']}")
