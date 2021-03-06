import yaml
import ccxt

with open('exchange/fee.yml', 'r') as f:
  FEE = yaml.load(f)


class ExchangeClient(object):
  """Exchange Client"""
  def __init__(self, name, api, demo=False):
    self.__exchange = eval('ccxt.' + name + '()')
    self.__exchange.apiKey = api['api_key']
    self.__exchange.secret = api['api_secret']
    self.__fee = FEE[name]
    self.__balance = None
    self.__bid = None
    self.__ask = None
    self.__demo = demo

  def bid(self):
    return self.__bid

  def ask(self):
    return self.__ask

  def update_balance(self):
    if not self.__demo:
      try:
        self.__balance = self.__exchange.fetch_free_balance()
      except Exception as e:
        self.__balance = None

  def fetch_order_book(self, symbol):
    # fetch_order_book
    try:
      orderbook = self.__exchange.fetch_order_book(symbol)
    except Exception as e:
      self.__bid, self.__ask = None, None
      return None, None
    # bid adjustment
    try:
      bid = orderbook['bids'][0]
      bid = self.__adjust_balance(symbol, bid, order='bid')
      bid = self.__adjust_fee(symbol, bid, order='bid')
    except Exception as e:
      bid = None
    # ask adjustment
    try:
      ask = orderbook['asks'][0]
      ask = self.__adjust_balance(symbol, ask, order='ask')
      ask = self.__adjust_fee(symbol, ask, order='ask')
    except Exception as e:
      ask = None
    self.__bid, self.__ask = bid, ask
    return bid, ask

  def create_market_buy_order(self, symbol, volume):
    if not self.__demo:
      self.__exchange.create_market_buy_order(symbol, volume)

  def create_market_sell_order(self, symbol, volume):
    if not self.__demo:
      self.__exchange.create_market_sell_order(symbol, volume)

  def create_limit_buy_order(self, symbol, volume, price):
    if not self.__demo:
      self.__exchange.create_limit_buy_order(symbol, volume, price)

  def create_limit_sell_order(self, symbol, volume, price):
    if not self.__demo:
      self.__exchange.create_limit_sell_order(symbol, volume, price)

  def __adjust_balance(self, symbol, pv, order='bid'):
    if self.__demo:
      return pv
    # balance volume
    pair = symbol.split('/')
    if order == 'bid':
      possible = self.__balance[pair[0]]
    elif order == 'ask':
      possible = self.__balance[pair[1]] / pv[0]
    # update volume
    if possible == 0.0:
      return None
    else:
      pv[1] = min(pv[1], possible)
      return pv

  def __adjust_fee(self, symbol, pv, order='bid'):
    # fee
    if symbol in self.__fee:
      fee = self.__fee[symbol]
    elif 'ELSE' in self.__fee:
      fee = self.__fee['ELSE']
    else:
      fee = 0
    # order
    if order == 'bid':
      pv[1] = (1.0 - fee) * pv[1]
    elif order == 'ask':
      pv[1] = (1.0 + fee) * pv[1]
    return pv
