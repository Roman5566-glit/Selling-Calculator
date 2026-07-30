import re
from PySide6.QtCore import Qt
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QPieSeries,
    QPieSlice,
)
from PySide6.QtGui import QBrush, QColor, QPainter
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QMenu,
)

from .constants import GREEN_COLOR, RED_COLOR, CURRENCY_SYMBOLS
from .dialogs import AddTripDialog, EditExpensesDialog
from .widgets import AnimatedButton

try:
    from src.calculator import calculate_item_metrics
    from src.database import Database
    from src.currency import convert_amount, CURRENCY_RATES, BASE_CURRENCY_KEY
except ModuleNotFoundError:
    from calculator import calculate_item_metrics
    from database import Database
    from currency import convert_amount, CURRENCY_RATES, BASE_CURRENCY_KEY

try:
    from src.exporter import TableExporter
except ModuleNotFoundError:
    from exporter import TableExporter


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selling Calculator")
        self.resize(1200, 750)

        self.db = Database()
        self.is_updating = False

        header_layout = QHBoxLayout()
        title_label = QLabel("Selling Calculator")
        title_label.setObjectName("mainTitle")

        # Currency pair selector: from -> to
        self.currency_from_combo = QComboBox()
        self.currency_from_combo.addItems(list(CURRENCY_SYMBOLS.keys()))
        self.currency_from_combo.setCurrentText(BASE_CURRENCY_KEY)
        self.currency_from_combo.currentTextChanged.connect(self.on_currency_changed)

        self.currency_to_combo = QComboBox()
        self.currency_to_combo.addItems(list(CURRENCY_SYMBOLS.keys()))
        # default display currency keeps showing UAH -> USD conversion initially
        # set target to USD if available, else keep base
        self.currency_to_combo.setCurrentText("$ USD" if "$ USD" in CURRENCY_SYMBOLS else BASE_CURRENCY_KEY)
        self.currency_to_combo.currentTextChanged.connect(self.on_currency_changed)

        self.currency_rate_label = QLabel("")
        self.currency_rate_label.setObjectName("currencyRateLabel")

        self.edit_trip_button = AnimatedButton(
            "✏️ Изменить расходы", shadow_color="rgba(59, 130, 246, 0.4)"
        )
        self.edit_trip_button.setObjectName("secondaryButton")
        self.edit_trip_button.clicked.connect(self.edit_selected_trip_expenses)

        self.delete_trip_button = AnimatedButton(
            "🗑️ Удалить", shadow_color="rgba(255, 77, 109, 0.4)"
        )
        self.delete_trip_button.setObjectName("deleteButton")
        self.delete_trip_button.clicked.connect(self.delete_selected_trip)

        self.add_trip_button = AnimatedButton(
            "+ Добавить закупку", shadow_color="rgba(255, 81, 47, 0.5)"
        )
        self.add_trip_button.setObjectName("primaryButton")
        self.add_trip_button.clicked.connect(self.open_add_dialog)

        self.btn_export = QPushButton("📥 Экспорт")
        export_menu = QMenu(self)
        action_excel = export_menu.addAction("📊 Сохранить в Excel (.xlsx)")
        action_csv = export_menu.addAction("📄 Сохранить в CSV (.csv)")
        self.btn_export.setMenu(export_menu)
        action_excel.triggered.connect(
            lambda: TableExporter.export_to_excel(self, self.table)
        )
        action_csv.triggered.connect(
            lambda: TableExporter.export_to_csv(self, self.table)
        )

        # chart refresh button removed (charts hidden by user request)

        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Toggle button opens currency selector dialog and applies chosen display currency
        self.toggle_currency_btn = QPushButton("Переключить валюту")
        self.toggle_currency_btn.setObjectName("secondaryButton")
        self.toggle_currency_btn.clicked.connect(self.toggle_currencies)
        header_layout.addWidget(self.toggle_currency_btn)

        self.open_converter_btn = QPushButton("Конвертер")
        self.open_converter_btn.setObjectName("secondaryButton")
        self.open_converter_btn.clicked.connect(self.open_converter_dialog)
        header_layout.addWidget(self.open_converter_btn)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.edit_trip_button)
        header_layout.addWidget(self.delete_trip_button)
        header_layout.addWidget(self.add_trip_button)
        header_layout.addWidget(self.btn_export)

        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(16)

        curr_sym = self.get_currency_symbol()
        self.card_buy = self._create_kpi_card("Закупки (Всего)", f"0 {curr_sym}")
        self.card_sale = self._create_kpi_card("Продажи (Факт)", f"0 {curr_sym}")
        self.card_profit = self._create_kpi_card(
            "Чистая Прибыль", f"0 {curr_sym}", is_profit=True
        )
        self.card_expenses = self._create_kpi_card("Расходы", f"0 {curr_sym}")

        kpi_layout.addWidget(self.card_buy["frame"])
        kpi_layout.addWidget(self.card_sale["frame"])
        kpi_layout.addWidget(self.card_profit["frame"])
        kpi_layout.addWidget(self.card_expenses["frame"])

        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(
            "🔍  Быстрый поиск по товарам или поездкам..."
        )
        self.search_bar.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Поездка / Товар",
            "Закупка",
            "Наценка (%)",
            "Продажи",
            "Прибыль",
            "Коэффициент",
            "Статус",
            "Тип",
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.verticalHeader().setVisible(False)
        self.table.cellChanged.connect(self.on_cell_changed)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        main_layout.addLayout(header_layout)
        main_layout.addLayout(kpi_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table, 4)

        # charts removed per user request; table occupies main area

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.load_data_from_db()

    def open_converter_dialog(self):
        try:
            from .converter_dialog import ConverterDialog
        except Exception:
            try:
                from ui.converter_dialog import ConverterDialog
            except Exception:
                ConverterDialog = None
        if ConverterDialog is None:
            QMessageBox.warning(self, "Ошибка", "Не удалось открыть конвертер")
            return
        dlg = ConverterDialog(parent=self, default_from=self.selected_currency_from(), default_to=self.selected_currency_to())
        if dlg.exec_():
            # if user changed target in dialog, reflect it
            new_to = dlg.selected_to()
            if new_to and new_to != self.selected_currency_to():
                self.currency_to_combo.setCurrentText(new_to)
                self.on_currency_changed()

    def selected_currency_from(self):
        return self.currency_from_combo.currentText()

    def selected_currency_to(self):
        return self.currency_to_combo.currentText()

    def get_currency_symbol(self):
        """Symbol used for displayed values (target currency)."""
        return CURRENCY_SYMBOLS.get(self.selected_currency_to(), "$")

    def update_currency_rate_label(self):
        """Show conversion rate from selected 'from' to 'to' currency."""
        frm = self.selected_currency_from()
        to = self.selected_currency_to()
        try:
            rate = convert_amount(1.0, frm, to)
        except Exception:
            rate = 1.0
        self.currency_rate_label.setText(f"Курс: 1 {frm} = {rate:.4f} {to}")

    def toggle_currencies(self):
        """Open a compact currency selector dialog and apply chosen currency globally."""
        try:
            from .currency_selector import CurrencySelectorDialog
        except Exception:
            try:
                from ui.currency_selector import CurrencySelectorDialog
            except Exception:
                CurrencySelectorDialog = None

        if CurrencySelectorDialog is None:
            QMessageBox.warning(self, "Ошибка", "Не удалось открыть селектор валют")
            return

        dlg = CurrencySelectorDialog(parent=self, current=self.selected_currency_to())
        if dlg.exec_():
            chosen = dlg.selected_currency()
            if chosen:
                # set display currency to chosen and reload
                self.currency_to_combo.setCurrentText(chosen)
                # keep base as from currency
                self.currency_from_combo.setCurrentText(BASE_CURRENCY_KEY)
                self.on_currency_changed()

    def convert_from_base(self, amount):
        """Convert amount from base currency (UAH) to display (to) currency."""
        to = self.selected_currency_to()
        return convert_amount(amount, BASE_CURRENCY_KEY, to)

    def convert_to_base(self, amount):
        """Convert displayed amount (to currency) back to base (UAH) for storage."""
        to = self.selected_currency_to()
        return convert_amount(amount, to, BASE_CURRENCY_KEY)

    def _clean_number(self, text):
        if not text:
            return 0.0
        cleaned = re.sub(r"[^\d.-]", "", text)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def _create_kpi_card(self, title, default_val, is_profit=False):
        frame = QFrame()
        frame.setObjectName("kpiCard")
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 16, 18, 16)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("kpiTitle")
        lbl_value = QLabel(default_val)
        lbl_value.setObjectName("kpiValue")

        if is_profit:
            lbl_value.setStyleSheet(
                "color: #10B981; font-size: 24px; font-weight: 800;"
            )

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        frame.setLayout(layout)
        return {"frame": frame, "value_label": lbl_value}

    # chart footer removed per user request

    def refresh_chart(self):
        # charts removed; keep this as a no-op hook
        self.update_currency_rate_label()
    
    def _create_readonly_item(self, text):
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def filter_table(self, query):
        query = query.lower().strip()
        current_trip_visible = True

        for r in range(self.table.rowCount()):
            type_item = self.table.item(r, 7)
            if not type_item:
                continue

            if type_item.text() == "Поездка":
                trip_name = self.table.item(r, 0).text().lower()
                current_trip_visible = query in trip_name
                self.table.setRowHidden(r, not current_trip_visible)
            else:
                item_name = self.table.item(r, 0).text().lower()
                is_match = query in item_name or current_trip_visible
                self.table.setRowHidden(r, not is_match)

    def on_currency_changed(self):
        if self.is_updating:
            return
        self.load_data_from_db()

    def open_add_dialog(self):
        dialog = AddTripDialog(self.get_currency_symbol(), self)
        if dialog.exec():
            trip_data = dialog.get_data()
            if trip_data["items"]:
                trip_data["total_expenses"] = self.convert_to_base(
                    trip_data["total_expenses"]
                )
                for item in trip_data["items"]:
                    item["buy_price"] = self.convert_to_base(item["buy_price"])

                self.db.add_trip(
                    trip_data["trip_name"],
                    trip_data["total_expenses"],
                    trip_data["items"],
                )
                self.load_data_from_db()

    def edit_selected_trip_expenses(self):
        trips = self.db.get_all_data()
        if not trips:
            QMessageBox.information(
                self, "Информация", "Список поездок пока пуст!"
            )
            return

        converted_trips = []
        for trip in trips:
            converted_trips.append({
                **trip,
                "total_expenses": self.convert_from_base(trip["total_expenses"]),
            })

        dialog = EditExpensesDialog(converted_trips, self.get_currency_symbol(), self)
        if dialog.exec():
            updated_expenses = dialog.get_updated_expenses()

            for r in range(self.table.rowCount()):
                type_item = self.table.item(r, 7)
                if type_item and type_item.text() == "Поездка":
                    data = type_item.data(Qt.ItemDataRole.UserRole) or {}
                    trip_id = data.get("trip_id")

                    if trip_id in updated_expenses:
                        new_exp_display = updated_expenses[trip_id]
                        new_exp_base = self.convert_to_base(new_exp_display)
                        data["expenses"] = new_exp_base
                        type_item.setData(Qt.ItemDataRole.UserRole, data)

                        if hasattr(self.db, "update_trip_expenses"):
                            self.db.update_trip_expenses(trip_id, new_exp_base)

            self.recalculate_all_trips()

    def on_cell_double_clicked(self, row, column):
        type_item = self.table.item(row, 7)
        if type_item and type_item.text() == "Поездка":
            self.edit_selected_trip_expenses()

    def load_data_from_db(self):
        self.is_updating = True
        self.table.setRowCount(0)

        sym = self.get_currency_symbol()
        trips = self.db.get_all_data()

        for trip in trips:
            trip_row = self.table.rowCount()
            self.table.insertRow(trip_row)

            self.table.setItem(
                trip_row, 0, self._create_readonly_item(f"📦 {trip['trip_name']}")
            )
            self.table.setItem(
                trip_row, 1, self._create_readonly_item(f"0.00 {sym}")
            )
            self.table.setItem(trip_row, 2, self._create_readonly_item("-"))
            self.table.setItem(
                trip_row, 3, self._create_readonly_item(f"0.00 {sym}")
            )
            self.table.setItem(
                trip_row, 4, self._create_readonly_item(f"0.00 {sym}")
            )
            self.table.setItem(trip_row, 5, self._create_readonly_item("-"))
            self.table.setItem(trip_row, 6, self._create_readonly_item("-"))

            type_item = self._create_readonly_item("Поездка")
            type_item.setData(
                Qt.ItemDataRole.UserRole,
                {"trip_id": trip["id"], "expenses": trip["total_expenses"]},
            )
            self.table.setItem(trip_row, 7, type_item)

            for item in trip["items"]:
                row = self.table.rowCount()
                self.table.insertRow(row)

                converted_buy = self.convert_from_base(item["buy_price"])
                metrics = calculate_item_metrics(converted_buy, item["markup"])
                converted_sale = metrics["sale_price"]
                converted_profit = metrics["profit"]

                self.table.setItem(
                    row, 0, self._create_readonly_item(f"   ↳ {item['name']}")
                )
                self.table.setItem(
                    row, 1, QTableWidgetItem(f"{converted_buy:.2f} {sym}"))
                self.table.setItem(
                    row, 2, QTableWidgetItem(f"{item['markup']:.2f}%")
                )
                self.table.setItem(
                    row,
                    3,
                    self._create_readonly_item(f"{converted_sale:.2f} {sym}"),
                )

                profit_item = self._create_readonly_item(
                    f"{converted_profit:.2f} {sym}"
                )
                if converted_profit >= 0:
                    profit_item.setForeground(GREEN_COLOR)
                else:
                    profit_item.setForeground(RED_COLOR)
                self.table.setItem(row, 4, profit_item)

                self.table.setItem(
                    row,
                    5,
                    self._create_readonly_item(f"{metrics['efficiency']:.4f}"),
                )

                status_combo = QComboBox()
                status_combo.addItems(["В наличии 📦", "Продано ✅"])
                # restore status from DB if present
                status_idx = int(item.get("status", 0)) if isinstance(item, dict) else 0
                status_combo.setCurrentIndex(status_idx)
                # save status on change
                status_combo.currentIndexChanged.connect(
                    lambda idx, r=row: self.on_status_changed(r, idx)
                )
                self.table.setCellWidget(row, 6, status_combo)

                item_type = self._create_readonly_item("Товар")
                item_type.setData(Qt.ItemDataRole.UserRole, item["id"])
                self.table.setItem(row, 7, item_type)

        self.is_updating = False
        self.recalculate_all_trips()
        self.update_currency_rate_label()

    def on_status_changed(self, row, idx=None):
        # Persist status change when user toggles status combobox
        try:
            if self.is_updating:
                return

            # find item id in this row
            type_item = self.table.item(row, 7)
            if not type_item or type_item.text() != "Товар":
                # for trip rows, no-op
                return

            item_id = type_item.data(Qt.ItemDataRole.UserRole)
            if item_id and idx is not None:
                # save to DB
                if hasattr(self.db, "update_item_status"):
                    self.db.update_item_status(item_id, idx)

            self.recalculate_all_trips()
        except Exception:
            self.recalculate_all_trips()

    def delete_selected_trip(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self,
                "Внимание",
                "Пожалуйста, выделите строку с поездкой или товаром для удаления!",
            )
            return

        trip_id = None
        trip_name = ""

        for r in range(current_row, -1, -1):
            type_item = self.table.item(r, 7)
            if type_item and type_item.text() == "Поездка":
                data = type_item.data(Qt.ItemDataRole.UserRole)
                trip_id = data["trip_id"] if data else None
                trip_name = self.table.item(r, 0).text()
                break

        if trip_id is None:
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы действительно хотите удалить {trip_name} и все её товары?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.db.delete_trip(trip_id)
            self.load_data_from_db()

    def on_cell_changed(self, row, column):
        if self.is_updating:
            return

        type_item = self.table.item(row, 7)
        if not type_item or type_item.text() != "Товар":
            return

        if column in (1, 2):
            self.recalculate_single_item(row)

            item_id = type_item.data(Qt.ItemDataRole.UserRole)
            try:
                displayed_buy_price = self._clean_number(self.table.item(row, 1).text())
                markup = self._clean_number(self.table.item(row, 2).text())
                if item_id:
                    base_buy_price = self.convert_to_base(displayed_buy_price)
                    self.db.update_item(item_id, base_buy_price, markup)
            except ValueError:
                pass

            self.recalculate_all_trips()

    def recalculate_single_item(self, row):
        self.is_updating = True
        sym = self.get_currency_symbol()

        buy_price = self._clean_number(self.table.item(row, 1).text())
        markup = self._clean_number(self.table.item(row, 2).text())

        metrics = calculate_item_metrics(buy_price, markup)

        self.table.item(row, 1).setText(f"{buy_price:.2f} {sym}")
        self.table.item(row, 2).setText(f"{markup:.2f}%")
        self.table.item(row, 3).setText(f"{metrics['sale_price']:.2f} {sym}")

        profit_item = self.table.item(row, 4)
        profit_item.setText(f"{metrics['profit']:.2f} {sym}")

        if metrics["profit"] >= 0:
            profit_item.setForeground(GREEN_COLOR)
        else:
            profit_item.setForeground(RED_COLOR)

        self.table.item(row, 5).setText(f"{metrics['efficiency']:.4f}")
        self.is_updating = False

    def recalculate_all_trips(self):
        self.is_updating = True

        current_trip_row = -1
        trip_buy = 0.0
        trip_sales = 0.0
        trip_items_profit = 0.0

        for r in range(self.table.rowCount()):
            type_item = self.table.item(r, 7)
            if not type_item:
                continue

            if type_item.text() == "Поездка":
                if current_trip_row != -1:
                    self._update_trip_row(
                        current_trip_row, trip_buy, trip_sales, trip_items_profit
                    )

                current_trip_row = r
                trip_buy = 0.0
                trip_sales = 0.0
                trip_items_profit = 0.0

            elif type_item.text() == "Товар":
                status_widget = self.table.cellWidget(r, 6)
                is_sold = status_widget and status_widget.currentIndex() == 1

                b = self._clean_number(self.table.item(r, 1).text())
                s = self._clean_number(self.table.item(r, 3).text())
                p = self._clean_number(self.table.item(r, 4).text())

                trip_buy += b
                if is_sold:
                    trip_sales += s
                    trip_items_profit += p

        if current_trip_row != -1:
            self._update_trip_row(
                current_trip_row, trip_buy, trip_sales, trip_items_profit
            )

        self.is_updating = False
        self.update_totals()

    def _update_trip_row(self, row, buy, sales, items_profit):
        sym = self.get_currency_symbol()
        data = self.table.item(row, 7).data(Qt.ItemDataRole.UserRole) or {}
        expenses_base = data.get("expenses", 0.0) if isinstance(data, dict) else 0.0
        expenses = self.convert_from_base(expenses_base)
        net_profit = items_profit - expenses

        self.table.item(row, 1).setText(f"{buy:.2f} {sym}")
        self.table.item(row, 3).setText(f"{sales:.2f} {sym}")

        profit_item = self.table.item(row, 4)
        profit_item.setText(f"{net_profit:.2f} {sym}")

        if net_profit >= 0:
            profit_item.setForeground(GREEN_COLOR)
        else:
            profit_item.setForeground(RED_COLOR)

    def update_totals(self):
        sym = self.get_currency_symbol()
        total_buy = 0.0
        total_sold_sale = 0.0
        total_sold_profit = 0.0
        total_expenses = 0.0

        for r in range(self.table.rowCount()):
            type_item = self.table.item(r, 7)
            if not type_item:
                continue

            if type_item.text() == "Поездка":
                data = type_item.data(Qt.ItemDataRole.UserRole) or {}
                exp_base = data.get("expenses", 0.0) if isinstance(data, dict) else 0.0
                exp = self.convert_from_base(exp_base)
                total_expenses += exp
            elif type_item.text() == "Товар":
                b = self._clean_number(self.table.item(r, 1).text())
                total_buy += b

                status_widget = self.table.cellWidget(r, 6)
                if status_widget and status_widget.currentIndex() == 1:
                    s = self._clean_number(self.table.item(r, 3).text())
                    p = self._clean_number(self.table.item(r, 4).text())
                    total_sold_sale += s
                    total_sold_profit += p

        net_total_profit = total_sold_profit - total_expenses

        self.card_buy["value_label"].setText(f"{total_buy:.2f} {sym}")
        self.card_sale["value_label"].setText(f"{total_sold_sale:.2f} {sym}")

        profit_label = self.card_profit["value_label"]
        profit_label.setText(f"{net_total_profit:.2f} {sym}")
        if net_total_profit >= 0:
            profit_label.setStyleSheet(
                "color: #10B981; font-size: 24px; font-weight: 800;"
            )
        else:
            profit_label.setStyleSheet(
                "color: #FF4D6D; font-size: 24px; font-weight: 800;"
            )

        self.card_expenses["value_label"].setText(f"{total_expenses:.2f} {sym}")
