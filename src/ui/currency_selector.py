from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QDialogButtonBox,
    QLabel,
)
from PySide6.QtCore import Qt
try:
    from .constants import CURRENCY_SYMBOLS
except Exception:
    from constants import CURRENCY_SYMBOLS


class CurrencySelectorDialog(QDialog):
    def __init__(self, parent=None, current=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите валюту")
        self.resize(300, 360)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Выберите валюту для отображения:"))

        self.listw = QListWidget()
        for k in CURRENCY_SYMBOLS.keys():
            self.listw.addItem(k)

        if current:
            items = self.listw.findItems(current, Qt.MatchFlag.MatchExactly)
            if items:
                self.listw.setCurrentItem(items[0])

        layout.addWidget(self.listw)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def selected_currency(self):
        it = self.listw.currentItem()
        return it.text() if it else None
