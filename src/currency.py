BASE_CURRENCY_KEY = "₴ UAH"

# Курсы относительно 1 UAH
CURRENCY_RATES = {
    "₴ UAH": 1.0,
    "$ USD": 0.027,
    "€ EUR": 0.025,
    "zł PLN": 0.11,
    "£ GBP": 0.021,
    "¥ CNY": 0.19,
    "₽ RUB": 2.7,
    "L MDL": 0.55,
    "lei RON": 0.13,
    "¥ JPY": 3.95,
    "₭ LAK": 307.0,
    "Fr CHF": 0.025,
    "$ CAD": 0.036,
    "$ AUD": 0.041,
}


def currency_to_base(amount: float, currency_key: str) -> float:
    """Конвертирует сумму из выбранной валюты в базовую валюту UAH."""
    rate = CURRENCY_RATES.get(currency_key, 1.0)
    if rate == 0:
        return amount
    return amount / rate


def base_to_currency(amount: float, currency_key: str) -> float:
    """Конвертирует сумму из базовой валюты UAH в заданную валюту."""
    rate = CURRENCY_RATES.get(currency_key, 1.0)
    return amount * rate


def convert_amount(amount: float, from_currency: str, to_currency: str) -> float:
    """Конвертирует сумму из одной валюты в другую через UAH."""
    base_amount = currency_to_base(amount, from_currency)
    return base_to_currency(base_amount, to_currency)
