import inspect
from typing import Callable, Any, Dict

class CommandRunner:
    def __init__(self):
        self.commands: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        self.commands[name] = func

    def run(self, command_name: str, **kwargs) -> Any:
        if command_name == "exec":
            return self._run_exec(**kwargs)

        if command_name not in self.commands:
            raise ValueError(f"Command '{command_name}' not found.")

        func = self.commands[command_name]
        sig = inspect.signature(func)
        bound_args = sig.bind_partial(**kwargs)
        bound_args.apply_defaults()

        # Debug info (opcjonalne)
        print(f"Running '{command_name}' with args: {bound_args.arguments}")

        return func(*bound_args.args, **bound_args.kwargs)

    def _run_exec(self, code: str, globals_dict: dict = None, locals_dict: dict = None) -> Any:
        """
        Special handler for 'exec' command to execute raw Python code.
        """
        globals_dict = globals_dict or {}
        locals_dict = locals_dict or {}
        try:
            exec(code, globals_dict, locals_dict)
            return locals_dict.get("_result")  # optional convention
        except Exception as e:
            return {"error": str(e)}
