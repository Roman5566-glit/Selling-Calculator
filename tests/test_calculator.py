import unittest
from src.calculator import calculate_item_metrics


class CalculatorTests(unittest.TestCase):

    def test_calculate_item_metrics_positive_markup(self):
        metrics = calculate_item_metrics(100.0, 25.0)
        self.assertAlmostEqual(metrics['sale_price'], 125.0)
        self.assertAlmostEqual(metrics['profit'], 25.0)
        self.assertAlmostEqual(metrics['efficiency'], 0.25)

    def test_calculate_item_metrics_zero_markup(self):
        metrics = calculate_item_metrics(100.0, 0.0)
        self.assertAlmostEqual(metrics['sale_price'], 100.0)
        self.assertAlmostEqual(metrics['profit'], 0.0)
        self.assertAlmostEqual(metrics['efficiency'], 0.0)

    def test_calculate_item_metrics_zero_buy_price(self):
        metrics = calculate_item_metrics(0.0, 50.0)
        self.assertAlmostEqual(metrics['sale_price'], 0.0)
        self.assertAlmostEqual(metrics['profit'], 0.0)
        self.assertAlmostEqual(metrics['efficiency'], 0.0)


if __name__ == '__main__':
    unittest.main()
