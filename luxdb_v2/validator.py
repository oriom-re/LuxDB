import importlib
import importlib.util
import os

# Placeholder baza danych
FAKE_FUNCTION_DB = {
    "fn_validate_001": """
def fn(data):
    return {"valid": True if data else False}
"""
}

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
        "system/loader/load_env": "module://core.env:load_env"
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
