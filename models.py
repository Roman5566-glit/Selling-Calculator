from dataclasses import dataclass


@dataclass
class Item:

  id: int
  trip_id: int
  name: str
  buy_price: float
  markup: float


@dataclass
class Trip:

  id: int
  name: str
  expenses: float
  items: list