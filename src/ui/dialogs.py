import re
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from .widgets import AnimatedButton


class EditExpensesDialog(QDialog):
    """Диалоговое окно со списком всех поездок для редактирования их расходов"""

    def __init__(self, trips_data, currency_symbol="грн", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование расходов по поездкам")
        self.setMinimumSize(480, 350)
        self.currency_symbol = currency_symbol

        layout = QVBoxLayout()

        lbl = QLabel("Укажите расходы для каждой поездки:")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(
            ["Поездка", f"Расходы ({self.currency_symbol})"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)

        self.table.setRowCount(len(trips_data))
        for row, trip in enumerate(trips_data):
            name_item = QTableWidgetItem(trip["trip_name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, trip["id"])
            self.table.setItem(row, 0, name_item)

            exp_item = QTableWidgetItem(f"{trip['total_expenses']:.2f}")
            self.table.setItem(row, 1, exp_item)

        layout.addWidget(self.table)

        self.save_btn = AnimatedButton(
            "Сохранить все изменения", shadow_color="rgba(255, 81, 47, 0.4)"
        )
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.clicked.connect(self.accept)

        layout.addSpacing(10)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

    def get_updated_expenses(self):
        """Возвращает словарь {trip_id: new_expense_val}"""
        results = {}
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            exp_item = self.table.item(row, 1)

            trip_id = name_item.data(Qt.ItemDataRole.UserRole)
            val_str = exp_item.text() if exp_item else "0"

            cleaned = re.sub(r"[^\d.-]", "", val_str)
            try:
                val = float(cleaned)
            except ValueError:
                val = 0.0

            results[trip_id] = val
        return results


class AddTripDialog(QDialog):

    def __init__(self, currency_symbol="грн", parent=None):
        super().__init__(parent)
        self.currency_symbol = currency_symbol
        self.setWindowTitle("Новая поездка / закупка")
        self.setMinimumWidth(540)

        self.trip_name_input = QLineEdit()
        self.trip_name_input.setPlaceholderText("Например: Поездка #1")

        self.nova_poshta_input = QLineEdit("0")
        self.gas_input = QLineEdit("0")
        self.other_exp_input = QLineEdit("0")

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels([
            "Название товара",
            f"Закупка ({self.currency_symbol})",
            "Наценка (%)",
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.add_row_btn = QPushButton("+ Добавить товар в список")
        self.add_row_btn.setObjectName("secondaryButton")
        self.add_row_btn.clicked.connect(self.add_empty_row)

        self.save_button = AnimatedButton(
            "Сохранить поездку", shadow_color="rgba(255, 81, 47, 0.4)"
        )
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        layout.addWidget(QLabel("Название поездки / Закупки"))
        layout.addWidget(self.trip_name_input)

        exp_layout = QHBoxLayout()
        v1 = QVBoxLayout()
        v1.addWidget(QLabel(f"Доставка ({self.currency_symbol})"))
        v1.addWidget(self.nova_poshta_input)
        v2 = QVBoxLayout()
        v2.addWidget(QLabel(f"Топливо ({self.currency_symbol})"))
        v2.addWidget(self.gas_input)
        v3 = QVBoxLayout()
        v3.addWidget(QLabel(f"Другое ({self.currency_symbol})"))
        v3.addWidget(self.other_exp_input)

        exp_layout.addLayout(v1)
        exp_layout.addLayout(v2)
        exp_layout.addLayout(v3)
        layout.addLayout(exp_layout)

        layout.addWidget(QLabel("Список товаров:"))
        layout.addWidget(self.items_table)
        layout.addWidget(self.add_row_btn)
        layout.addSpacing(10)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.add_empty_row()

    def add_empty_row(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        self.items_table.setItem(row, 0, QTableWidgetItem(""))
        self.items_table.setItem(row, 1, QTableWidgetItem("0"))
        self.items_table.setItem(row, 2, QTableWidgetItem("0"))

    def get_data(self):
        trip_name = (
            self.trip_name_input.text().strip() or "Поездка без названия"
        )

        def parse_val(val_str):
            try:
                return float(val_str.strip() or 0.0)
            except ValueError:
                return 0.0

        total_expenses = (
            parse_val(self.nova_poshta_input.text())
            + parse_val(self.gas_input.text())
            + parse_val(self.other_exp_input.text())
        )

        items = []
        for r in range(self.items_table.rowCount()):
            name_item = self.items_table.item(r, 0)
            buy_item = self.items_table.item(r, 1)
            markup_item = self.items_table.item(r, 2)

            name = name_item.text().strip() if name_item else ""
            if not name:
                continue

            items.append({
                "name": name,
                "buy_price": parse_val(buy_item.text() if buy_item else "0"),
                "markup": parse_val(markup_item.text() if markup_item else "0"),
            })

        return {
            "trip_name": trip_name,
            "total_expenses": total_expenses,
            "items": items,
        }
