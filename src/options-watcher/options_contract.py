from typing import TypedDict
from datetime import datetime


class Greeks(TypedDict):
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


class OptionsContract:
    ticker: str
    expiration_date: str
    strike_price: float
    last_price: float
    ask: float
    bid: float
    greeks: Greeks
    last_updated: datetime

    def __init__(self, ticker: str, expiration_date: str, strike_price: float, last_price: float, ask: float,
                 bid: float, greeks: Greeks):
        self.ticker = ticker
        self.expiration_date = expiration_date
        self.strike_price = strike_price
        self.last_price = last_price
        self.ask = ask
        self.bid = bid
        self.greeks = greeks
        self.last_updated = datetime.now()

    def update_data(self, last_price: float, ask: float, bid: float, greeks: Greeks):
        """Update the option contract data and reset the last_updated timestamp."""
        self.last_price = last_price
        self.ask = ask
        self.bid = bid
        self.greeks = greeks
        self.last_updated = datetime.now()

