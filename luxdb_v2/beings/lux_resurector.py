class LuxResurrector:
  def __init__(self, lux_gene: LuxGene):
      self.gene = lux_gene

  def express(self):
      self._check_env()
      return self._compile_func()

  def _check_env(self):
      # Sprawdź, czy środowisko się zgadza
      for dep in self.gene.environment.get("dependencies", []):
          if not self._is_installed(dep):
              print(f"[Thor] 🔧 Missing: {dep} — attempting reinstallation")
              self._install(dep)

  def _is_installed(self, requirement: str) -> bool:
      # To może być zaawansowane lub symboliczne (wstępnie)
      return False  # domyślnie: wszystko trzeba przywrócić

  def _install(self, dep: str):
      import subprocess
      subprocess.run(["pip", "install", dep])

  def _compile_func(self):
      import base64, marshal, types
      bytecode = base64.b64decode(self.gene.encoded_function)
      code = marshal.loads(bytecode)
      return types.FunctionType(code, globals(), self.gene.uid)
