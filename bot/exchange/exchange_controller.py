import math
from .exchange_client import ExchangeClient


class ExchangeController(object):
  """Exchange Controller"""
  def __init__(self, exchanges, logic):
    self.__demo = logic['demo']
    self.__margin = logic['margin']
    self.__clients = {}
    for name, api in exchanges.items():
      if api['use']:
        client = ExchangeClient(name, api, self.__demo)
        self.__clients[name] = client

  def arbitrage(self, symbol):
    # index 0:price, 1:volume, 2:name
    max_bid, min_ask = self.__fetch_order_book(symbol)
    # create order
    volume = min(max_bid[1], min_ask[1])
    rate = (max_bid[0] - min_ask[0]) / max_bid[0]  # rise and fall rate
    if not self.__demo and rate > self.__margin:
      self.__clients[max_bid[-1]].create_limit_sell_order(symbol, volume, max_bid[0])
      self.__clients[min_ask[-1]].create_limit_buy_order(symbol, volume, min_ask[0])
      self.__clients[max_bid[-1]].update_balance()
      self.__clients[min_ask[-1]].update_balance()
    # logger
    if rate > self.__margin:
      print ('{0} : {1} bid {2}, {3} ask {4}, profit {5}'.format(symbol, max_bid[-1], max_bid[0], min_ask[-1], min_ask[0], (max_bid[0] - min_ask[0]) * volume))

  def __fetch_order_book(self, symbol):
    max_bid = [-math.inf, 0.0]
    min_ask = [+math.inf, 0.0]
    for name, client in self.__clients.items():
      bid, ask = client.fetch_order_book(symbol)
      if bid is not None and bid[0] > max_bid[0]:
        max_bid = bid + [name]
      if ask is not None and ask[0] < min_ask[0]:
        min_ask = ask + [name]
    if len(max_bid) == 3 and len(min_ask) == 3:
      return max_bid, min_ask
    else:
      raise RuntimeError('cannot get max_bid or min_ask')
