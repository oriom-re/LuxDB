from .loader import load_from_file, load_from_module, load_from_db, call_remote_function, generate_ai_function
from .registry import LUX_ROUTING
from .logger import log_event
from .decorators import discover_routes, get_route_info, DECORATED_ROUTES

# Centralny rejestr handlerów dla różnych typów URI
ROUTER_HANDLERS = {
    "file": load_from_file,
    "module": load_from_module,
    "db": load_from_db,
    "remote": call_remote_function,
    "lux": lambda path: resolve_lux_uri(path),
    "ai": generate_ai_function,
    "logger": lambda path_and_level: (lambda **kwargs: log_event(path_and_level, kwargs.get("message", ""))),
}

class LuxFunction:
    def __init__(self, uri: str):
        self.uri = uri
        self.function = resolve(uri)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __repr__(self):
        return f"LuxFunction(uri={self.uri})"

def resolve_lux_uri(lux_path):
    """
    Rozwiązuje lux:// URI, obsługując zarówno statyczne (registry) jak i dynamiczne (decorator) route
    """
    if "@" in lux_path:
        base, version = lux_path.split("@")
    else:
        base, version = lux_path, "latest"
    full_key = f"{base}@{version}"
    
    # Najpierw sprawdź w dynamicznych route (decorator)
    if full_key in DECORATED_ROUTES:
        return DECORATED_ROUTES[full_key]["function"]
    
    # Potem sprawdź w statycznym rejestrze
    if full_key not in LUX_ROUTING:
        if version == "latest":
            # Sprawdź w obu rejestrach
            available_static = [k for k in LUX_ROUTING.keys() if k.startswith(f"{base}@v")]
            available_dynamic = [k for k in DECORATED_ROUTES.keys() if k.startswith(f"{base}@v")]
            available = available_static + available_dynamic
            
            if not available:
                raise ValueError(f"Nie znaleziono żadnej wersji dla {base}")
            latest = sorted(available, key=lambda k: int(k.split("@v")[-1]), reverse=True)[0]
            full_key = latest
            
            # Zwróć funkcję z odpowiedniego rejestru
            if full_key in DECORATED_ROUTES:
                return DECORATED_ROUTES[full_key]["function"]
        else:
            raise ValueError(f"Brak zarejestrowanego path: {full_key}")
    
    return resolve(LUX_ROUTING[full_key])

def resolve(uri: str):
    """
    Centralny router dla wszystkich typów URI.
    """
    if "://" not in uri:
        raise ValueError(f"Invalid URI: {uri}")
    scheme, rest = uri.split("://", 1)
    handler = ROUTER_HANDLERS.get(scheme)
    if not handler:
        raise ValueError(f"No handler for scheme '{scheme}' in URI '{uri}'")
    return handler(rest)

def get_all_routes():
    """Zwraca wszystkie dostępne route (statyczne + dynamiczne)"""
    all_routes = {}
    
    # Statyczne route z registry
    for path, uri in LUX_ROUTING.items():
        all_routes[path] = {
            "type": "static",
            "uri": uri,
            "function": None,
            "metadata": {}
        }
    
    # Dynamiczne route z dekoratorów
    for path, info in DECORATED_ROUTES.items():
        all_routes[path] = {
            "type": "dynamic",
            "uri": f"lux://{path}",
            "function": info["function"],
            "metadata": {
                "description": info.get("description"),
                "permissions": info.get("permissions", []),
                "cache_ttl": info.get("cache_ttl"),
                "module": info.get("module"),
                "name": info.get("name")
            }
        }
    
    return all_routes

def register_dynamic_route(path: str, function: callable, metadata: dict = None):
    """Programowo rejestruje nową dynamiczną route"""
    DECORATED_ROUTES[path] = {
        "function": function,
        "description": metadata.get("description") if metadata else None,
        "permissions": metadata.get("permissions", []) if metadata else [],
        "cache_ttl": metadata.get("cache_ttl") if metadata else None,
        "module": function.__module__,
        "name": function.__name__
    }

def unregister_dynamic_route(path: str):
    """Usuwa dynamiczną route"""
    if path in DECORATED_ROUTES:
        del DECORATED_ROUTES[path]
        return True
    return False

def route_exists(path: str):
    """Sprawdza czy route istnieje (statyczna lub dynamiczna)"""
    return path in LUX_ROUTING or path in DECORATED_ROUTES

def get_route_metadata(path: str):
    """Zwraca metadane route"""
    if path in DECORATED_ROUTES:
        return DECORATED_ROUTES[path]
    elif path in LUX_ROUTING:
        return {"type": "static", "uri": LUX_ROUTING[path]}
    return None
