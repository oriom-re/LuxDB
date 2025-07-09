from .routing import resolve_function

def run_step(step, locals_, functions=None):
    if 'function' in step:
        func_path = step['function']
        args = step.get('args', {})
        func = resolve_function(func_path)
        result = func(**args)
    elif 'call_remote' in step:
        remote_call = step['call_remote']
        service = remote_call['service']
        func_name = remote_call['function']
        args = remote_call.get('args', {})
        # call_remote to be implemented or imported
        result = call_remote(service, func_name, args)
    else:
        raise ValueError("Step must contain 'function' or 'call_remote'")
    if 'save_as' in step:
        locals_[step['save_as']] = result
    return result

def run_scenario(scenario, locals_=None, functions=None):
    locals_ = locals_ or {}
    for step in scenario['steps']:
        run_step(step, locals_, functions)
    return locals_
