import marshal, base64

def my_func(x):
    return x * 2 + 1

code_obj = my_func.__code__
byte_data = marshal.dumps(code_obj)
encoded = base64.b64encode(byte_data).decode('utf-8')

