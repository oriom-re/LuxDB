import importlib
import importlib.util
import os
from jinja2 import Template

def load_from_file(path_with_func):
    if path_with_func.endswith(".yaml"):
        # run_scenario do zaimportowania w executor.py
        from .executor import run_scenario
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
    # Placeholder DB, do podmiany na prawdziwą bazę
    FAKE_FUNCTION_DB = {
        "fn_validate_001": """
def fn(data):
    return {"valid": True if data else False}
"""
    }
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

def generate_ai_function(ai_path):
    def ai_generated_fn(**kwargs):
        print(f"[ai-generated] Simulating {ai_path} with {kwargs}")
        return {"result": "AI function output"}
    return ai_generated_fn

def render_template(value, context):
    if isinstance(value, str):
        return Template(value).render(**context)
    elif isinstance(value, dict):
        return {k: render_template(v, context) for k, v in value.items()}
    elif isinstance(value, list):
        return [render_template(v, context) for v in value]
    else:
        return value
