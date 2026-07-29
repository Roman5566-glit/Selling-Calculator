import os
import sys
from PySide6.QtWidgets import QApplication
from ui import MainWindow


def resource_path(relative_path):
  """Получает путь к файлу внутри временной папки PyInstaller"""
  if hasattr(sys, '_MEIPASS'):
    return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath('.'), relative_path)


if __name__ == '__main__':
  app = QApplication(sys.argv)

  # Путь к файлу стилей
  qss_path = resource_path('styles.qss')
  try:
    with open(qss_path, 'r', encoding='utf-8') as f:
      app.setStyleSheet(f.read())
  except Exception as e:
    print(f'Ошибка загрузки стилей: {e}')

  window = MainWindow()
  window.show()
  sys.exit(app.exec())