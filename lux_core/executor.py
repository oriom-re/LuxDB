from lux_core.routing import resolve

# run_step obsługuje uniwersalnie: uri, function, call_remote

def run_step(step, locals_, functions=None):
    if 'uri' in step:
        uri = step['uri']
        args = step.get('args', {})
        func = resolve(uri)
        result = func(**args)
    elif 'function' in step:
        # Wsteczna kompatybilność
        uri = step['function']
        args = step.get('args', {})
        func = resolve(uri)
        result = func(**args)
    elif 'call_remote' in step:
        # call_remote jako zunifikowany remote://service.function
        remote_call = step['call_remote']
        service = remote_call['service']
        func_name = remote_call['function']
        args = remote_call.get('args', {})
        uri = f"remote://{service}.{func_name}"
        func = resolve(uri)
        result = func(**args)
    else:
        raise ValueError("Step must contain 'uri', 'function' or 'call_remote'")
    if 'save_as' in step:
        locals_[step['save_as']] = result
    return result

def run_scenario(scenario, locals_=None, functions=None):
    locals_ = locals_ or {}
    for step in scenario['steps']:
        run_step(step, locals_, functions)
    return locals_
