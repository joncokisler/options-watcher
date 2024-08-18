# This file contains code from Lienus10/yoptions.
# Licensed under the MIT License.

import urllib.request
import json
import datetime
from math import log, sqrt, exp

import xmltodict
from scipy.stats import norm
import pandas as pd


# Get basic bid/ask and greeks of an specific option. If no risk free interest rate is provided, it will be taken
# from the US treasury.
# Date format: 'YYYY-MM-DD'
# Option_type: 'c' - call or 'p' - put
def get_option_greeks(stock_ticker, expiration_date, option_type, strike, dividend_yield, risk_free_rate=None):
    expiration_date = str(int((datetime.datetime.strptime(expiration_date, "%Y-%m-%d")
                               + datetime.timedelta(hours=2)).timestamp()))

    # with urllib.request.urlopen(
    #         "https://query2.finance.yahoo.com/v6/finance/options/" + stock_ticker + '?date=' + expiration_date) as url:
    with urllib.request.urlopen(
            "https://query2.finance.yahoo.com/v6/finance/options/" + stock_ticker) as url:
        print("https://query2.finance.yahoo.com/v6/finance/options/" + stock_ticker + '?date=' + expiration_date)
        data = json.loads(url.read().decode())
    print("DATA")
    print(data)
    if option_type == 'c':
        type_data = data["optionChain"]["result"][0]["options"][0]["calls"]
    else:
        type_data = data["optionChain"]["result"][0]["options"][0]["puts"]

    chain = [x for x in type_data if x['strike'] == strike]

    print(f"Chain data for strike {strike}: {chain}")

    return __greeks(data, chain, option_type, risk_free_rate, dividend_yield)


def __greeks(data, chain, option_type, r=None, dividend_yield=None):
    underlying_price = data["optionChain"]["result"][0]["quote"]["regularMarketPrice"]
    expiration_date = datetime.datetime.fromtimestamp(data["optionChain"]["result"][0]["options"][0]["expirationDate"])
    today = datetime.datetime.now()

    if r is None:
        r = __risk_free((expiration_date - today).days)
        print("R", r)
    print("DIVIDEND YIELD", dividend_yield)

    contract_symbols = []
    last_traded = []
    strike = []
    last_price = []
    ask = []
    bid = []
    change = []
    perc_change = []
    volume = []
    open_interest = []
    implied_volatility = []
    delta = []
    gamma = []
    theta = []
    vega = []
    rho = []

    for i in chain:

        try:
            contract_symbols.append(i["contractSymbol"])
        except KeyError:
            contract_symbols.append('-')

        try:
            last_traded.append(str(datetime.datetime.fromtimestamp(i["lastTradeDate"])
                                   .strftime("%Y-%m-%d %I:%M:%S %p")))
        except KeyError:
            last_traded.append('-')

        try:
            strike.append(i["strike"])
        except KeyError:
            strike.append(-1)

        try:
            last_price.append(i["lastPrice"])
        except KeyError:
            last_price.append('-')

        try:
            ask.append(i["ask"])
        except KeyError:
            ask.append('-')

        try:
            bid.append(i["bid"])
        except KeyError:
            bid.append('-')

        try:
            change.append(i["change"])
        except KeyError:
            change.append('-')

        try:
            perc_change.append(i["percentChange"])
        except KeyError:
            perc_change.append('-')

        try:
            volume.append(i['volume'])
        except KeyError:
            volume.append('-')

        try:
            open_interest.append(i["openInterest"])
        except KeyError:
            open_interest.append('-')

        try:
            implied_volatility.append(i["impliedVolatility"])
        except KeyError:
            implied_volatility.append(-1)

        t = (expiration_date - today).days / 365
        v = implied_volatility[-1]
        t_sqrt = sqrt(t)

        if dividend_yield is not None:

            if option_type == 'c':
                print("HERE")
                if v != 0:
                    d1 = (log(float(underlying_price) / strike[-1]) + ((r - dividend_yield) + v * v / 2.) * t) / (
                            v * t_sqrt)
                    d2 = d1 - v * t_sqrt
                    delta.append(round(norm.cdf(d1), 4))
                    gamma.append(round(norm.pdf(d1) / (underlying_price * v * t_sqrt), 4))
                    theta.append(
                        round((-(underlying_price * v * norm.pdf(d1)) / (2 * t_sqrt) -
                               r * strike[-1] * exp(-r * t) * norm.cdf(d2)) / 365, 4))
                    vega.append(round(underlying_price * t_sqrt * norm.pdf(d1) / 100, 4))
                    rho.append(round(strike[-1] * t * exp(-r * t) * norm.cdf(d2) / 100, 4))
                else:
                    delta.append(0)
                    gamma.append(0)
                    theta.append(0)
                    vega.append(0)
                    rho.append(0)

            if option_type == 'p':
                d1 = (log(float(underlying_price) / strike[-1]) + r * t) / (v * t_sqrt) + 0.5 * v * t_sqrt
                d2 = d1 - (v * t_sqrt)
                delta.append(round(-norm.cdf(-d1), 4))
                gamma.append(round(norm.pdf(d1) / (underlying_price * v * t_sqrt), 4))
                theta.append(round(
                    (-(underlying_price * v * norm.pdf(d1)) / (2 * t_sqrt) + r * strike[-1] * exp(-r * t) * norm.cdf(
                        -d2)) / 365, 4))
                vega.append(round(underlying_price * t_sqrt * norm.pdf(d1) / 100, 4))
                rho.append(round(-strike[-1] * t * exp(-r * t) * norm.cdf(-d2) / 100, 4))

    if dividend_yield is None:
        return pd.DataFrame(
            list(zip(contract_symbols, last_traded, strike, last_price, bid, ask, change, perc_change, volume,
                     open_interest, implied_volatility)),
            columns=['Symbol', 'Last Trade', 'Strike', 'Last Price', 'Bid', 'Ask', 'Change', '% Change', 'Volume',
                     'Open Interest', 'Impl. Volatility'])

    else:
        return pd.DataFrame(
            list(zip(contract_symbols, strike, last_price, bid, ask, implied_volatility, delta, gamma, theta, vega,
                     rho)), columns=['Symbol', 'Strike', 'Last Price', 'Bid', 'Ask', 'Impl. Volatility', 'Delta',
                                     'Gamma', 'Theta', 'Vega', 'Rho'])


def __risk_free(days):
    file = urllib.request.urlopen('https://home.treasury.gov/sites/default/files/interest-rates/yield.xml')
    data = file.read()
    file.close()

    data = xmltodict.parse(data)['QR_BC_CM']['LIST_G_WEEK_OF_MONTH']['G_WEEK_OF_MONTH']

    try:
        data = data[-1]['LIST_G_NEW_DATE']['G_NEW_DATE']
    except:
        data = data['LIST_G_NEW_DATE']['G_NEW_DATE']

    try:
        data = data[-1]['LIST_G_BC_CAT']['G_BC_CAT']
    except:
        data = data['LIST_G_BC_CAT']['G_BC_CAT']

    if days < 45:
        return float(data['BC_1MONTH'])
    else:
        if days < 75:
            return float(data['BC_2MONTH'])
        else:
            if days < 135:
                return float(data['BC_3MONTH'])
            else:
                if days < 165:
                    return float(data['BC_4MONTH'])
                else:
                    if days < 272:
                        return float(data['BC_6MONTH'])
                    else:
                        if days < 547:
                            return float(data['BC_1YEAR'])
                        else:
                            if days < 912:
                                return float(data['BC_2YEAR'])
                            else:
                                return float(data['BC_3YEAR'])


def get_chain_greeks(stock_ticker, dividend_yield, option_type, risk_free_rate=None):
    with urllib.request.urlopen("https://query2.finance.yahoo.com/v6/finance/options/" + stock_ticker) as url:
        data = json.loads(url.read().decode())

    return __get_chain(option_type, data, dividend_yield, risk_free_rate)


def __get_chain(option_type, data, dividend_yield=None, r=None):
    if not data["optionChain"]["result"]:
        return 'Error. No options for this symbol!'

    if option_type == 'c':
        chain = data["optionChain"]["result"][0]["options"][0]["calls"]
        return __greeks(data, chain, option_type, r, dividend_yield)
    else:
        if option_type == 'p':
            chain = data["optionChain"]["result"][0]["options"][0]["puts"]
            return __greeks(data, chain, option_type, r, dividend_yield)
        else:
            return 'Error. Check your entry!'
