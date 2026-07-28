import sys
from PySide6.QtWidgets import QApplication
from ui import MainWindow

if __name__ == "__main__":
  app = QApplication(sys.argv)

  # Загрузка и применение стилей
  try:
    with open("styles.qss", "r", encoding="utf-8") as f:
      app.setStyleSheet(f.read())
  except FileNotFoundError:
    pass

  window = MainWindow()
  window.show()
  sys.exit(app.exec())