from .loader import load_from_file, load_from_module, load_from_db, call_remote_function, generate_ai_function
from .registry import resolve_lux_uri

# Centralny rejestr handlerów dla różnych typów URI
ROUTER_HANDLERS = {
    "file": load_from_file,
    "module": load_from_module,
    "db": load_from_db,
    "remote": call_remote_function,
    "lux": resolve_lux_uri,
    "ai": generate_ai_function,
    # "entity": load_entity,  # Przykład na przyszłość
    # "data": load_data,
}

class LuxFunction:
    def __init__(self, uri: str):
        self.uri = uri
        self.function = resolve(uri)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __repr__(self):
        return f"LuxFunction(uri={self.uri})"

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
