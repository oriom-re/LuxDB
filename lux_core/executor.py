from lux_core.routing import resolve

# run_step obsługuje uniwersalnie: uri, scene, steps (grupa)

def run_step(step, locals_, step_idx=0, parent_name=None, functions=None):
    try:
        step_name = step.get('name') or step.get('description') or step.get('uri') or step.get('scene', '')
        args = step.get('args', {})
        if 'uri' in step:
            uri = step['uri']
            func = resolve(uri)
            result = func(**args)
        elif 'scene' in step:
            import yaml
            with open(step['scene']) as f:
                sub_scenario = yaml.safe_load(f)
            result = run_scenario(sub_scenario, locals_)
        elif 'steps' in step:
            # Grupa kroków (pod-scenariusz)
            result = run_scenario(step, locals_, parent_name=step_name)
        else:
            raise ValueError("Step must contain 'uri', 'scene' or 'steps'")
        if 'save_as' in step:
            locals_[step['save_as']] = result
        # Szczegółowe logowanie przez logger://info
        resolve("logger://info")(
            message=f"[step {step_idx}] {parent_name or ''} | {step_name} | uri={step.get('uri', '')} | args={args} | result={result}"
        )
        return result
    except Exception as e:
        resolve("logger://error")(
            message=f"[step {step_idx}] {parent_name or ''} | {step_name} | uri={step.get('uri', '')} | args={args} | error={e}"
        )
        raise

def run_scenario(scenario, locals_=None, functions=None, parent_name=None):
    locals_ = locals_ or {}
    steps = scenario['steps']
    for idx, step in enumerate(steps, 1):
        run_step(step, locals_, step_idx=idx, parent_name=parent_name or scenario.get('name'), functions=functions)
    return locals_
