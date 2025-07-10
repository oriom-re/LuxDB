from .loader import load_from_file, load_from_module, load_from_db, call_remote_function, generate_ai_function
from .registry import LUX_ROUTING
from .logger import log_event

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
    if "@" in lux_path:
        base, version = lux_path.split("@")
    else:
        base, version = lux_path, "latest"
    full_key = f"{base}@{version}"
    if full_key not in LUX_ROUTING:
        if version == "latest":
            available = [k for k in LUX_ROUTING.keys() if k.startswith(f"{base}@v")]
            if not available:
                raise ValueError(f"Nie znaleziono żadnej wersji dla {base}")
            latest = sorted(available, key=lambda k: int(k.split("@v")[-1]), reverse=True)[0]
            full_key = latest
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
