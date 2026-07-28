from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
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
)

from calculator import calculate_item_metrics
from database import Database

# Константы цветов
GREEN_COLOR = QColor("#10B981")  # Яркий зелёный
RED_COLOR = QColor("#FF4D6D")    # Красный


class AnimatedButton(QPushButton):

  def __init__(self, text, parent=None, shadow_color="#FF4D6D"):
    super().__init__(text, parent)
    self.shadow = QGraphicsDropShadowEffect(self)
    self.shadow.setBlurRadius(15)
    self.shadow.setColor(QColor(shadow_color))
    self.shadow.setOffset(0, 4)
    self.setGraphicsEffect(self.shadow)

  def enterEvent(self, event):
    self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
    self.anim.setDuration(200)
    self.anim.setStartValue(15)
    self.anim.setEndValue(30)
    self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    self.anim.start()
    super().enterEvent(event)

  def leaveEvent(self, event):
    self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
    self.anim.setDuration(200)
    self.anim.setStartValue(30)
    self.anim.setEndValue(15)
    self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    self.anim.start()
    super().leaveEvent(event)


class AddTripDialog(QDialog):

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setWindowTitle("Новая поездка / закупка")
    self.setMinimumWidth(520)

    self.trip_name_input = QLineEdit()
    self.trip_name_input.setPlaceholderText("Например: Поездка #1")

    self.nova_poshta_input = QLineEdit()
    self.nova_poshta_input.setText("0")
    self.gas_input = QLineEdit()
    self.gas_input.setText("0")
    self.other_exp_input = QLineEdit()
    self.other_exp_input.setText("0")

    self.items_table = QTableWidget()
    self.items_table.setColumnCount(3)
    self.items_table.setHorizontalHeaderLabels(
        ["Название товара", "Закупка (грн)", "Наценка (%)"]
    )
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
    v1.addWidget(QLabel("Нов. почта (грн)"))
    v1.addWidget(self.nova_poshta_input)
    v2 = QVBoxLayout()
    v2.addWidget(QLabel("Бензин (грн)"))
    v2.addWidget(self.gas_input)
    v3 = QVBoxLayout()
    v3.addWidget(QLabel("Ещё / Другое (грн)"))
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


class MainWindow(QMainWindow):

  def __init__(self):
    super().__init__()
    self.setWindowTitle("Selling Calculator")
    self.resize(1150, 720)

    self.db = Database()
    self.is_updating = False

    # --- 1. Шапка ---
    header_layout = QHBoxLayout()
    title_label = QLabel("Selling Calculator")
    title_label.setObjectName("mainTitle")

    self.delete_trip_button = AnimatedButton(
        "🗑️ Удалить закупку", shadow_color="rgba(255, 77, 109, 0.4)"
    )
    self.delete_trip_button.setObjectName("deleteButton")
    self.delete_trip_button.clicked.connect(self.delete_selected_trip)

    self.add_trip_button = AnimatedButton(
        "+ Добавить закупку", shadow_color="rgba(255, 81, 47, 0.5)"
    )
    self.add_trip_button.setObjectName("primaryButton")
    self.add_trip_button.clicked.connect(self.open_add_dialog)

    header_layout.addWidget(title_label)
    header_layout.addStretch()
    header_layout.addWidget(self.delete_trip_button)
    header_layout.addWidget(self.add_trip_button)

    # --- 2. Карточки KPI ---
    kpi_layout = QHBoxLayout()
    kpi_layout.setSpacing(16)

    self.card_buy = self._create_kpi_card("Закупки", "0 грн")
    self.card_sale = self._create_kpi_card("Продажи", "0 грн")
    self.card_profit = self._create_kpi_card("Прибыль", "0 грн", is_profit=True)
    self.card_expenses = self._create_kpi_card("Расходы", "0 грн")

    kpi_layout.addWidget(self.card_buy["frame"])
    kpi_layout.addWidget(self.card_sale["frame"])
    kpi_layout.addWidget(self.card_profit["frame"])
    kpi_layout.addWidget(self.card_expenses["frame"])

    # --- 3. Поиск ---
    search_layout = QHBoxLayout()
    self.search_bar = QLineEdit()
    self.search_bar.setPlaceholderText("🔍  Поиск по товарам или поездкам...")
    search_layout.addWidget(self.search_bar)

    # --- 4. Таблица ---
    self.table = QTableWidget()
    self.table.setColumnCount(7)
    self.table.setHorizontalHeaderLabels([
        "Поездка / Товар",
        "Закупка",
        "Наценка (%)",
        "Продажи",
        "Прибыль",
        "Коэффициент",
        "Тип",
    ])
    self.table.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.Stretch
    )
    self.table.cellChanged.connect(self.on_cell_changed)

    # --- 5. Компоновка ---
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(16)

    main_layout.addLayout(header_layout)
    main_layout.addLayout(kpi_layout)
    main_layout.addLayout(search_layout)
    main_layout.addWidget(self.table)

    central_widget = QWidget()
    central_widget.setLayout(main_layout)
    self.setCentralWidget(central_widget)

    self.load_data_from_db()

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

  def _create_readonly_item(self, text):
    item = QTableWidgetItem(text)
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item

  def open_add_dialog(self):
    dialog = AddTripDialog(self)
    if dialog.exec():
      trip_data = dialog.get_data()
      if trip_data["items"]:
        self.db.add_trip(
            trip_data["trip_name"],
            trip_data["total_expenses"],
            trip_data["items"],
        )
        self.load_data_from_db()

  def load_data_from_db(self):
    self.is_updating = True
    self.table.setRowCount(0)

    trips = self.db.get_all_data()
    for trip in trips:
      trip_row = self.table.rowCount()
      self.table.insertRow(trip_row)

      self.table.setItem(
          trip_row, 0, self._create_readonly_item(f"📦 {trip['trip_name']}")
      )
      self.table.setItem(trip_row, 1, self._create_readonly_item("0.00 грн"))
      self.table.setItem(trip_row, 2, self._create_readonly_item("-"))
      self.table.setItem(trip_row, 3, self._create_readonly_item("0.00 грн"))
      self.table.setItem(trip_row, 4, self._create_readonly_item("0.00 грн"))
      self.table.setItem(trip_row, 5, self._create_readonly_item("-"))

      type_item = self._create_readonly_item("Поездка")
      type_item.setData(
          Qt.ItemDataRole.UserRole,
          {"trip_id": trip["id"], "expenses": trip["total_expenses"]},
      )
      self.table.setItem(trip_row, 6, type_item)

      for item in trip["items"]:
        row = self.table.rowCount()
        self.table.insertRow(row)

        metrics = calculate_item_metrics(item["buy_price"], item["markup"])

        self.table.setItem(
            row, 0, self._create_readonly_item(f"   ↳ {item['name']}")
        )
        self.table.setItem(
            row, 1, QTableWidgetItem(f"{item['buy_price']:.2f} грн")
        )
        self.table.setItem(row, 2, QTableWidgetItem(f"{item['markup']:.2f}%"))
        self.table.setItem(
            row, 3, self._create_readonly_item(f"{metrics['sale_price']:.2f} грн")
        )

        profit_item = self._create_readonly_item(f"{metrics['profit']:.2f} грн")
        # Покраска прибыли товара
        if metrics["profit"] >= 0:
          profit_item.setForeground(GREEN_COLOR)
        else:
          profit_item.setForeground(RED_COLOR)

        self.table.setItem(row, 4, profit_item)

        self.table.setItem(
            row,
            5,
            self._create_readonly_item(f"{metrics['efficiency']:.4f}"),
        )

        item_type = self._create_readonly_item("Товар")
        item_type.setData(Qt.ItemDataRole.UserRole, item["id"])
        self.table.setItem(row, 6, item_type)

    self.is_updating = False
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
      type_item = self.table.item(r, 6)
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

    type_item = self.table.item(row, 6)
    if not type_item or type_item.text() != "Товар":
      return

    if column in (1, 2):
      self.recalculate_single_item(row)

      item_id = type_item.data(Qt.ItemDataRole.UserRole)
      try:
        buy_price = float(
            self.table.item(row, 1).text().replace("грн", "").strip()
        )
        markup = float(
            self.table.item(row, 2).text().replace("%", "").strip()
        )
        if item_id:
          self.db.update_item(item_id, buy_price, markup)
      except ValueError:
        pass

      self.recalculate_all_trips()

  def recalculate_single_item(self, row):
    self.is_updating = True
    try:
      buy_str = (
          self.table.item(row, 1)
          .text()
          .replace("грн", "")
          .replace("%", "")
          .strip()
      )
      markup_str = (
          self.table.item(row, 2)
          .text()
          .replace("грн", "")
          .replace("%", "")
          .strip()
      )

      buy_price = float(buy_str) if buy_str else 0.0
      markup = float(markup_str) if markup_str else 0.0
    except ValueError:
      buy_price, markup = 0.0, 0.0

    metrics = calculate_item_metrics(buy_price, markup)

    self.table.item(row, 1).setText(f"{buy_price:.2f} грн")
    self.table.item(row, 2).setText(f"{markup:.2f}%")
    self.table.item(row, 3).setText(f"{metrics['sale_price']:.2f} грн")

    profit_item = self.table.item(row, 4)
    profit_item.setText(f"{metrics['profit']:.2f} грн")

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
      type_item = self.table.item(r, 6)
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
        try:
          b = float(
              self.table.item(r, 1).text().replace("грн", "").strip()
          )
          s = float(
              self.table.item(r, 3).text().replace("грн", "").strip()
          )
          p = float(
              self.table.item(r, 4).text().replace("грн", "").strip()
          )

          trip_buy += b
          trip_sales += s
          trip_items_profit += p
        except (ValueError, AttributeError):
          continue

    if current_trip_row != -1:
      self._update_trip_row(
          current_trip_row, trip_buy, trip_sales, trip_items_profit
      )

    self.is_updating = False
    self.update_totals()

  def _update_trip_row(self, row, buy, sales, items_profit):
    data = self.table.item(row, 6).data(Qt.ItemDataRole.UserRole) or {}
    expenses = data.get("expenses", 0.0) if isinstance(data, dict) else 0.0
    net_profit = items_profit - expenses

    self.table.item(row, 1).setText(f"{buy:.2f} грн")
    self.table.item(row, 3).setText(f"{sales:.2f} грн")

    profit_item = self.table.item(row, 4)
    profit_item.setText(f"{net_profit:.2f} грн")

    if net_profit >= 0:
      profit_item.setForeground(GREEN_COLOR)
    else:
      profit_item.setForeground(RED_COLOR)

  def update_totals(self):
    total_buy = 0.0
    total_sale = 0.0
    total_profit = 0.0
    total_expenses = 0.0

    for r in range(self.table.rowCount()):
      type_item = self.table.item(r, 6)
      if not type_item:
        continue

      if type_item.text() == "Поездка":
        data = type_item.data(Qt.ItemDataRole.UserRole) or {}
        exp = data.get("expenses", 0.0) if isinstance(data, dict) else 0.0
        total_expenses += exp
      elif type_item.text() == "Товар":
        try:
          buy_str = self.table.item(r, 1).text().replace("грн", "").strip()
          sale_str = self.table.item(r, 3).text().replace("грн", "").strip()
          profit_str = self.table.item(r, 4).text().replace("грн", "").strip()

          total_buy += float(buy_str)
          total_sale += float(sale_str)
          total_profit += float(profit_str)
        except (ValueError, AttributeError):
          continue

    net_total_profit = total_profit - total_expenses

    self.card_buy["value_label"].setText(f"{total_buy:.2f} грн")
    self.card_sale["value_label"].setText(f"{total_sale:.2f} грн")

    # Покраска общей карточки Прибыли в KPI
    profit_label = self.card_profit["value_label"]
    profit_label.setText(f"{net_total_profit:.2f} грн")
    if net_total_profit >= 0:
      profit_label.setStyleSheet(
          "color: #10B981; font-size: 24px; font-weight: 800;"
      )
    else:
      profit_label.setStyleSheet(
          "color: #FF4D6D; font-size: 24px; font-weight: 800;"
      )

    self.card_expenses["value_label"].setText(f"{total_expenses:.2f} грн")