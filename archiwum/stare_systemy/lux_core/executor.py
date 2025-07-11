from lux_core.routing import resolve
from functools import wraps

# Rejestr tasków
class TaskRegistry:
    def __init__(self):
        self.tasks = {}

    def register(self, task_id, task_data):
        """Rejestruje nowy task w rejestrze."""
        self.tasks[task_id] = task_data

    def get(self, task_id):
        """Pobiera task z rejestru po jego ID."""
        return self.tasks.get(task_id)

    def update(self, task_id, task_data):
        """Aktualizuje istniejący task."""
        if task_id in self.tasks:
            self.tasks[task_id].update(task_data)

    def remove(self, task_id):
        """Usuwa task z rejestru."""
        if task_id in self.tasks:
            del self.tasks[task_id]

# Globalny rejestr tasków
TASK_REGISTRY = TaskRegistry()

# Dekorator do rejestracji tasków
def task_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        task_id = kwargs.get('task_id')
        parent_task = kwargs.get('parent_task')

        # Wywołanie oryginalnej funkcji
        result = func(*args, **kwargs)

        # Rejestracja taska
        TASK_REGISTRY.register(task_id, {
            'name': func.__name__,
            'args': kwargs,
            'result': result,
            'parent': parent_task,
        })

        return result
    return wrapper

# run_step obsługuje uniwersalnie: uri, scene, steps (grupa)

@task_decorator
def run_step(step, locals_, step_idx=0, parent_name=None, functions=None, task_id=None, parent_task=None):
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
        result = run_scenario(sub_scenario, locals_, parent_name=step_name, start_idx=step_idx, parent_task=task_id)
    elif 'steps' in step:
        # Grupa kroków (pod-scenariusz)
        result = run_scenario(step, locals_, parent_name=step_name, start_idx=step_idx, parent_task=task_id)
    else:
        raise ValueError("Step must contain 'uri', 'scene' or 'steps'")

    if 'save_as' in step:
        locals_[step['save_as']] = result

    # Szczegółowe logowanie przez logger://info
    resolve("logger://info")(
        message=f"[step {step_idx}] {parent_name or ''} | {step_name} | uri={step.get('uri', '')} | args={args} | result={result}"
    )
    return result

# Aktualizacja funkcji run_scenario
@task_decorator
def run_scenario(scenario, locals_=None, functions=None, parent_name=None, start_idx=0, parent_task=None):
    locals_ = locals_ or {}
    steps = scenario['steps']
    for idx, step in enumerate(steps, start=start_idx + 1):
        resolve("logger://info")(
            message=f"Running step {idx} in scenario {parent_name or scenario.get('name', 'Unnamed')}"
        )
        run_step(step, locals_, step_idx=idx, parent_name=parent_name or scenario.get('name'), functions=functions, task_id=f"{parent_name or 'root'}:{idx}", parent_task=parent_task)
    return locals_
