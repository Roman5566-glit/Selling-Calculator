import unittest
from PySide6.QtWidgets import QApplication
from src.ui.dialogs import AddTripDialog, EditExpensesDialog

app = QApplication([])


class DialogTests(unittest.TestCase):

    def test_add_trip_dialog_default_values(self):
        dialog = AddTripDialog('грн')
        self.assertEqual(dialog.trip_name_input.placeholderText(), 'Например: Поездка #1')
        self.assertEqual(dialog.nova_poshta_input.text(), '0')
        self.assertEqual(dialog.gas_input.text(), '0')
        self.assertEqual(dialog.other_exp_input.text(), '0')
        self.assertEqual(dialog.items_table.rowCount(), 1)

    def test_add_trip_dialog_get_data(self):
        dialog = AddTripDialog('грн')
        dialog.trip_name_input.setText('New Trip')
        dialog.items_table.item(0, 0).setText('Item A')
        dialog.items_table.item(0, 1).setText('10')
        dialog.items_table.item(0, 2).setText('20')

        data = dialog.get_data()
        self.assertEqual(data['trip_name'], 'New Trip')
        self.assertEqual(data['total_expenses'], 0.0)
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['name'], 'Item A')
        self.assertEqual(data['items'][0]['buy_price'], 10.0)
        self.assertEqual(data['items'][0]['markup'], 20.0)

    def test_edit_expenses_dialog_get_updated_expenses(self):
        trips = [
            {'id': 1, 'trip_name': 'Trip 1', 'total_expenses': 10.0},
            {'id': 2, 'trip_name': 'Trip 2', 'total_expenses': 20.0},
        ]
        dialog = EditExpensesDialog(trips, 'грн')
        self.assertEqual(dialog.table.rowCount(), 2)

        dialog.table.item(0, 1).setText('15')
        dialog.table.item(1, 1).setText('25')

        updated = dialog.get_updated_expenses()
        self.assertEqual(updated[1], 15.0)
        self.assertEqual(updated[2], 25.0)


if __name__ == '__main__':
    unittest.main()
