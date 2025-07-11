from typing import Any, Callable, Dict, List, Optional, Union

class LuxEntity:
    """
    Bazowa klasa dla encji w systemie Lux.
    Możesz rozszerzać ją o własne atrybuty i metody.
    """
    def __init__(self, id: str, meta: Optional[Dict[str, Any]] = None):
        self.id = id
        self.meta = meta or {}

    def __repr__(self):
        return f"<LuxEntity id={self.id}>"

class LuxFunction:
    """
    Typ reprezentujący funkcję w systemie Lux.
    """
    def __init__(self, uri: str, function: Callable):
        self.uri = uri
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __repr__(self):
        return f"<LuxFunction uri={self.uri}>"

# Typy pomocnicze do scenariuszy (możesz je rozwinąć lub zastąpić dataclassami)
ScenarioStep = Dict[str, Any]
Scenario = Dict[str, Union[str, List[ScenarioStep]]]
