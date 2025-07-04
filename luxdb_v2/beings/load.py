# odtworzenie
import types
import marshal
import base64
from beings.base_being import BaseBeing

# beings/load.py
class Load(BaseBeing):
    def __init__(self, encoded):
decoded = base64.b64decode(encoded)
restored_code = marshal.loads(decoded)
restored_func = types.FunctionType(restored_code, globals())