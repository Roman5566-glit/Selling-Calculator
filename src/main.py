import os
import sys
from PySide6.QtWidgets import QApplication

try:
    from src.ui import MainWindow
except ModuleNotFoundError:
    from ui import MainWindow


def resource_path(relative_path):
    """Возвращает путь к ресурсу, поддерживая PyInstaller и запуск из корня проекта."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, os.pardir))
    path_in_src = os.path.join(base_dir, relative_path)
    path_in_root = os.path.join(root_dir, relative_path)

    if os.path.exists(path_in_src):
        return path_in_src
    return path_in_root


if __name__ == '__main__':
    app = QApplication(sys.argv)

    qss_path = resource_path('styles.qss')
    try:
        with open(qss_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f'Ошибка загрузки стилей: {e}')

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
