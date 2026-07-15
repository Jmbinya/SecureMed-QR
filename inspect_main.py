import importlib
mod = importlib.import_module('app.routes.main')
print('module:', mod)
print('module file:', getattr(mod, '__file__', None))
print('has main_bp:', hasattr(mod, 'main_bp'))
print('dict keys:', [k for k in mod.__dict__.keys() if 'main' in k.lower() or 'bp' in k.lower()])
print('main_bp value:', getattr(mod, 'main_bp', None))
