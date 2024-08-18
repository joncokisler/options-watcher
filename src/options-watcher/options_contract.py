from typing import TypedDict
from datetime import datetime
import yfinance as yf
import yoptions as yo
from greeks import get_option_greeks, get_chain_greeks

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


class OptionsContractFactory:
    ticker: str
    expiration_date: str
    strike_price: float
    contract_type: str

    VALID_CONTRACT_TYPES_CALLS = ["call", "calls", "c"]
    VALID_CONTRACT_TYPES_PUTS = ["put", "puts", "p"]

    def create_options_contract(self, ticker: str, expiration_date: str, strike_price: float, contract_type: str):
        stock = yf.Ticker(ticker)
        dividend_yield = stock.info.get("dividendYield")
        print(stock.info.get("dividendYield"))
        print(stock.option_chain(expiration_date).calls)
        selected_option_type = ""

        if contract_type.lower() in self.VALID_CONTRACT_TYPES_CALLS:
            print(stock.option_chain().calls.head)
            greeks = get_option_greeks(ticker, expiration_date, "c", strike_price, dividend_yield)
            greek2 = get_chain_greeks(stock_ticker= ticker, dividend_yield=0.44, option_type='c',
                                      risk_free_rate=None)
            print("GREEKS", greeks["Theta"])
            print("GREEKS2", greek2)
            greek2.to_csv("greek2.csv")
            # greeks.to_csv("LOL.csv")
        elif contract_type.lower() in self.VALID_CONTRACT_TYPES_PUTS:
            stock.option_chain().puts
            greeks = get_option_greeks(ticker, expiration_date, "p", strike_price, dividend_yield)

        else:
            raise ValueError(f"Wrong contract type entered: {contract_type}")


        print(stock.option_chain().columns)

        # lastPrice
        # bid
        # ask

fact = OptionsContractFactory()
fact.create_options_contract("AAPL", "2024-08-23", 225.00, "Call")
