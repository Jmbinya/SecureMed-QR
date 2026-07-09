import importlib
mod = importlib.import_module('app.routes.responder')
print(mod.__file__)
print(hasattr(mod, 'scan'))
print(hasattr(mod, 'verify'))
print(hasattr(mod, 'view'))
print(mod.scan)
