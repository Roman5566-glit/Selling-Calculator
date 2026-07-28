def calculate_item_metrics(buy_price: float, markup_percent: float) -> dict:
  """Считает продажи и чистую валовую прибыль конкретного товара (без учета общих расходов)."""
  sale_price = buy_price * (1 + markup_percent / 100.0)
  profit = sale_price - buy_price
  efficiency = (profit / buy_price) if buy_price > 0 else 0.0

  return {
      "sale_price": sale_price,
      "profit": profit,
      "efficiency": efficiency,
  }