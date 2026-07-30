import sqlite3


class Database:

  def __init__(self, db_name="shop_calculator.db"):
    self.db_name = db_name
    self.init_db()

  def get_connection(self):
    return sqlite3.connect(self.db_name)

  def init_db(self):
    with self.get_connection() as conn:
      cursor = conn.cursor()
      # Таблица поездок
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS trips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    expenses REAL NOT NULL
                )
            """)
      # Таблица товаров, связанных с поездкой (FOREIGN KEY)
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trip_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    buy_price REAL NOT NULL,
                    markup REAL NOT NULL,
                    status INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE
                )
            """)
      conn.commit()

      # Migration: ensure 'status' column exists for older DBs
      cursor.execute("PRAGMA table_info(items)")
      cols = [row[1] for row in cursor.fetchall()]
      if "status" not in cols:
        try:
          cursor.execute("ALTER TABLE items ADD COLUMN status INTEGER NOT NULL DEFAULT 0")
        except Exception:
          pass
      conn.commit()

  def add_trip(self, name: str, expenses: float, items: list) -> int:
    """Сохраняет поездку и её товары в БД, возвращает ID поездки."""
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO trips (name, expenses) VALUES (?, ?)", (name, expenses)
      )
      trip_id = cursor.lastrowid

      for item in items:
        status = int(item.get("status", 0))
        cursor.execute(
          """
              INSERT INTO items (trip_id, name, buy_price, markup, status)
              VALUES (?, ?, ?, ?, ?)
            """,
          (trip_id, item["name"], item["buy_price"], item["markup"], status),
        )

      conn.commit()
      return trip_id

  def delete_trip(self, trip_id: int):
    """Удаляет поездку и все входящие в неё товары."""
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute("DELETE FROM items WHERE trip_id = ?", (trip_id,))
      cursor.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
      conn.commit()

  def update_item(self, item_id: int, buy_price: float, markup: float):
    """Обновляет закупку и наценку конкретного товара."""
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute(
          """
                UPDATE items 
                SET buy_price = ?, markup = ?
                WHERE id = ?
            """,
          (buy_price, markup, item_id),
      )
      conn.commit()

  def update_item_status(self, item_id: int, status: int):
    """Update item status (0 - in stock, 1 - sold)."""
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute("UPDATE items SET status = ? WHERE id = ?", (int(status), item_id))
      conn.commit()

  def update_trip_expenses(self, trip_id: int, expenses: float):
    """Обновляет общие расходы по поездке."""
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute(
          "UPDATE trips SET expenses = ? WHERE id = ?",
          (expenses, trip_id),
      )
      conn.commit()

  def get_all_data(self):
    """Возвращает все поездки вместе со списком их товаров."""
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute("SELECT id, name, expenses FROM trips ORDER BY id ASC")
      trips_rows = cursor.fetchall()

      result = []
      for t_id, t_name, t_exp in trips_rows:
        cursor.execute(
          """
              SELECT id, name, buy_price, markup, status 
              FROM items WHERE trip_id = ? ORDER BY id ASC
            """,
          (t_id,),
        )
        items_rows = cursor.fetchall()

        items = [
          {"id": i_id, "name": i_name, "buy_price": i_buy, "markup": i_markup, "status": int(i_status)}
          for i_id, i_name, i_buy, i_markup, i_status in items_rows
        ]

        result.append({
            "id": t_id,
            "trip_name": t_name,
            "total_expenses": t_exp,
            "items": items,
        })

      return result