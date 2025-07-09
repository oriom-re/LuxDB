import importlib
import importlib.util
import os
from jinja2 import Template

# Placeholder baza danych
FAKE_FUNCTION_DB = {
    "fn_validate_001": """
def fn(data):
    return {"valid": True if data else False}
"""
}

# Placeholder dla mapowania lux:// na module://
lux_map_registry = {
    "system/loader/load_env": "module://core.env:load_env",
    "system/loader/validate_data": "module://core.validation:validate_data"
}

def run_scenario(scenario, locals=None, functions=None):
  locals = locals or {}
  for step in scenario['steps']:
      if 'function' in step:
          # lokalne wywołanie
          func_path = step['function']
          args = step.get('args', {})
          func = get_function(func_path, functions)
          
          module_name, func_name = func_path.rsplit('.', 1)
          module = __import__(module_name, fromlist=[func_name])
          func = getattr(module, func_name)
          result = func(**args)

      elif 'call_remote' in step:
          # zdalne wywołanie
          remote_call = step['call_remote']
          service = remote_call['service']
          func_name = remote_call['function']
          args = remote_call.get('args', {})
          result = call_remote(service, func_name, args)

      else:
          raise ValueError("Step must contain 'function' or 'call_remote'")

      if 'save_as' in step:
          locals[step['save_as']] = result

class LuxFunction:
    def __init__(self, uri: str):
        self.uri = uri
        self.function = resolve_function(uri)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __repr__(self):
        return f"LuxFunction(uri={self.uri})"

def resolve_function(uri: str):
    if uri.startswith("file://"):
        return load_from_file(uri.replace("file://", ""))
    elif uri.startswith("module://"):
        return load_from_module(uri.replace("module://", ""))
    elif uri.startswith("db://"):
        return load_from_db(uri.replace("db://", ""))
    elif uri.startswith("remote://"):
        return call_remote_function(uri.replace("remote://", ""))
    elif uri.startswith("lux://"):
        return resolve_lux_uri(uri.replace("lux://", ""))
    elif uri.startswith("ai://"):
        return generate_ai_function(uri.replace("ai://", ""))
    else:
        raise ValueError(f"Unknown URI scheme in '{uri}'")

# --- Implementation details ---

def load_from_file(path_with_func):
    if path_with_func.endswith(".yaml"):
        return lambda **kwargs: run_scenario(path_with_func, kwargs)
    if ":" not in path_with_func:
        raise ValueError(f"Invalid file path with function: {path_with_func}")
    
    path, func_name = path_with_func.split(":")
    module_name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, func_name)

def load_from_module(module_with_func):
    module_path, func_name = module_with_func.split(":")
    module = importlib.import_module(module_path)
    return getattr(module, func_name)

def load_from_db(fn_id):
    source_code = FAKE_FUNCTION_DB.get(fn_id)
    if not source_code:
        raise ValueError(f"Function ID '{fn_id}' not found in DB.")
    local_env = {}
    exec(source_code, {}, local_env)
    return local_env["fn"]

def call_remote_function(service_and_fn):
    def remote_wrapper(**kwargs):
        print(f"[remote call] Would send request to '{service_and_fn}' with args: {kwargs}")
        return {"result": f"Simulated response from {service_and_fn}"}
    return remote_wrapper

def resolve_lux_uri(lux_path):
    # Map lux://system/loader/load_env -> module://core.env:load_env
    mapping = {
        "system/loader/load_env": "module://core.env:load_env",
        "system/loader/load_env@v1": "module://core.env:load_env    ",
        "system/loader/validate_data@v1": "module://core.validation:validate_data",
        "system/loader/load_env@v2": "module://core.env:load_env_v2",
        "system/loader/validate_data@v2": "module://core.validation:validate_data_v2"
    }
    mapped_uri = mapping.get(lux_path)
    if not mapped_uri:
        raise ValueError(f"No mapping found for lux://{lux_path}")
    return resolve_function(mapped_uri)

def generate_ai_function(ai_path):
    # Placeholder — w prawdziwej wersji: prompt → model → funkcja
    def ai_generated_fn(**kwargs):
        print(f"[ai-generated] Simulating {ai_path} with {kwargs}")
        return {"result": "AI function output"}
    return ai_generated_fn
    
class LuxFunctionRouter:
    def __init__(self):
        self.lux_map_registry = {}

    def register_lux(self, lux_path: str, target_uri: str):
        self.lux_map_registry[lux_path] = target_uri

    def resolve_lux_uri(self, lux_path: str):
        if "@" in lux_path:
            base, version = lux_path.split("@")
        else:
            base, version = lux_path, "latest"

        # Szukaj w zarejestrowanych wersjach
        full_key = f"{base}@{version}"

        if full_key not in LUX_ROUTING:
            if version == "latest":
                # Znajdź najwyższą wersję
                available = [
                    k for k in LUX_ROUTING.keys() 
                    if k.startswith(f"{base}@v")
                ]
                if not available:
                    raise ValueError(f"Nie znaleziono żadnej wersji dla {base}")
                
                # Posortuj wersje i wybierz najwyższą
                latest = sorted(
                    available, 
                    key=lambda k: int(k.split("@v")[-1]), 
                    reverse=True
                )[0]
                full_key = latest
            else:
                raise ValueError(f"Brak zarejestrowanego path: {full_key}")

        return resolve_function(LUX_ROUTING[full_key])

class LuxBusClient:
    def __init__(self, client_id):
        self.client_id = client_id
        self.events = []

    def send_event(self, event):
        event["meta"] = {"client_id": self.client_id}
        self.events.append(event)
        return event
    
def render_template(value, context):
    if isinstance(value, str):
        return Template(value).render(**context)
    elif isinstance(value, dict):
        return {k: render_template(v, context) for k, v in value.items()}
    elif isinstance(value, list):
        return [render_template(v, context) for v in value]
    else:
        return value

class LuxBusFlow:
    def __init__(self):
        self.clients = {}
        self.tasks = {}

    def handle_event(self, event):
        uid = event.get("uid")
        client_id = event.get("meta", {}).get("client_id")
        lux_path = event.get("lux_path")
        params = event.get("params", {})

        # Resolve function
        func = resolve_function(lux_path)
        result = func(**params)

        # Store result per task
        self.tasks[uid] = {
            "client_id": client_id,
            "result": result
        }

        return result
    
# Przykładowa rejestracja funkcji
LUX_ROUTING = {
    "system/loader/load_env@v1": "module://core.env:load_env    ",
    "system/loader/validate_data@v1": "module://core.validation:validate_data",
    "system/loader/load_env@v2": "module://core.env:load_env_v2",
    "system/loader/validate_data@v2": "module://core.validation:validate_data_v2"
}

# przykładowe użycie funkcji

