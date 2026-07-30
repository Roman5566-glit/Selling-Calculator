import importlib.util
spec = importlib.util.find_spec('PySide6.QtCharts')
print('FOUND' if spec else 'MISSING')
