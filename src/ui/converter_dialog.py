import re
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QComboBox,
    QPushButton,
)

try:
    from src.currency import convert_amount, CURRENCY_RATES, BASE_CURRENCY_KEY
    from src.ui.constants import CURRENCY_SYMBOLS
except ModuleNotFoundError:
    try:
        from currency import convert_amount, CURRENCY_RATES, BASE_CURRENCY_KEY
    except Exception:
        convert_amount = None
    try:
        from .constants import CURRENCY_SYMBOLS
    except Exception:
        from constants import CURRENCY_SYMBOLS


class ConverterDialog(QDialog):
    def __init__(self, parent=None, default_from=None, default_to=None):
        super().__init__(parent)
        self.setWindowTitle("Конвертер валют")
        self.setModal(True)

        layout = QVBoxLayout()

        row = QHBoxLayout()
        self.input_amount = QLineEdit()
        self.input_amount.setPlaceholderText("Сумма")
        self.input_amount.setFixedWidth(120)
        row.addWidget(self.input_amount)

        self.from_combo = QComboBox()
        self.from_combo.addItems(list(CURRENCY_SYMBOLS.keys()))
        if default_from:
            self.from_combo.setCurrentText(default_from)
        row.addWidget(self.from_combo)

        arrow = QLabel("→")
        row.addWidget(arrow)

        self.to_combo = QComboBox()
        self.to_combo.addItems(list(CURRENCY_SYMBOLS.keys()))
        if default_to:
            self.to_combo.setCurrentText(default_to)
        row.addWidget(self.to_combo)

        layout.addLayout(row)

        btn_row = QHBoxLayout()
        self.btn_convert = QPushButton("Конвертировать")
        self.btn_convert.clicked.connect(self.on_convert)
        btn_row.addWidget(self.btn_convert)

        self.btn_swap = QPushButton("Поменять")
        self.btn_swap.clicked.connect(self.on_swap)
        btn_row.addWidget(self.btn_swap)

        self.result_label = QLabel("")
        btn_row.addWidget(self.result_label)

        layout.addLayout(btn_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Close | QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def on_convert(self):
        if convert_amount is None:
            self.result_label.setText("Конвертер недоступен")
            return
        txt = self.input_amount.text().strip()
        try:
            amt = float(re.sub(r"[^\d.-]", "", txt)) if txt else 0.0
        except Exception:
            self.result_label.setText("Ошибка")
            return
        frm = self.from_combo.currentText()
        to = self.to_combo.currentText()
        try:
            res = convert_amount(amt, frm, to)
            sym = CURRENCY_SYMBOLS.get(to, "")
            self.result_label.setText(f"{res:.2f} {sym}")
        except Exception:
            self.result_label.setText("err")

    def on_swap(self):
        a = self.from_combo.currentText()
        b = self.to_combo.currentText()
        self.from_combo.setCurrentText(b)
        self.to_combo.setCurrentText(a)

    def selected_to(self):
        return self.to_combo.currentText()
