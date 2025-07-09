


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