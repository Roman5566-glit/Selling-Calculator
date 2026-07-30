import os
import sqlite3
import tempfile
import unittest
from src.database import Database


class DatabaseTests(unittest.TestCase):

    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db = Database(db_name=self.db_file.name)

    def tearDown(self):
        try:
            os.remove(self.db_file.name)
        except OSError:
            pass

    def test_add_and_get_trip(self):
        trip_id = self.db.add_trip(
            'Test Trip', 100.0, [
                {'name': 'Item 1', 'buy_price': 50.0, 'markup': 20.0},
                {'name': 'Item 2', 'buy_price': 30.0, 'markup': 10.0},
            ]
        )

        rows = self.db.get_all_data()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['id'], trip_id)
        self.assertEqual(rows[0]['trip_name'], 'Test Trip')
        self.assertEqual(rows[0]['total_expenses'], 100.0)
        self.assertEqual(len(rows[0]['items']), 2)

    def test_update_item(self):
        trip_id = self.db.add_trip(
            'Trip', 10.0, [
                {'name': 'Item 1', 'buy_price': 10.0, 'markup': 5.0},
            ]
        )
        item_id = self.db.get_all_data()[0]['items'][0]['id']
        self.db.update_item(item_id, 15.0, 8.0)

        updated_item = self.db.get_all_data()[0]['items'][0]
        self.assertEqual(updated_item['buy_price'], 15.0)
        self.assertEqual(updated_item['markup'], 8.0)

    def test_delete_trip(self):
        trip_id = self.db.add_trip(
            'Trip', 10.0, [
                {'name': 'Item 1', 'buy_price': 10.0, 'markup': 5.0},
            ]
        )
        self.db.delete_trip(trip_id)
        rows = self.db.get_all_data()
        self.assertEqual(rows, [])


if __name__ == '__main__':
    unittest.main()
