import math
from .exchange_client import ExchangeClient


class ExchangeController(object):
  """Exchange Controller"""
  def __init__(self, exchanges, logic):
    self.__demo = logic['demo']
    self.__open_margin = logic['open_margin']
    self.__close_margin = logic['close_margin']
    self.__clients = {}
    self.__position = {}
    for name, api in exchanges.items():
      if api['use']:
        client = ExchangeClient(name, api, self.__demo)
        self.__clients[name] = client
        self.__position[name] = 0.0
    self.__force_close_position = logic['force_close_position']

  def arbitrage(self, symbol):
    # update free balance
    self.__update_balance()
    # index 0:price, 1:volume, 2:name
    open_bid, open_ask, close_bid, close_ask = self.__fetch_order_book(symbol)
    # open position
    self.__open_position(symbol, open_bid, open_ask)
    # close position
    self.__close_position(symbol, close_bid, close_ask)

  def __update_balance(self):
    if not self.__demo:
      for _, client in self.__clients.items():
        client.update_balance()

  def __fetch_order_book(self, symbol):
    open_bid, close_bid = [-math.inf, 0.0], [-math.inf, 0.0]
    open_ask, close_ask = [+math.inf, 0.0], [+math.inf, 0.0]
    for name, client in self.__clients.items():
      bid, ask = client.fetch_order_book(symbol)
      if bid is not None:
        if bid[0] > open_bid[0]:
          open_bid = bid + [name]
        if self.__position[name] > 0 and bid[0] > close_bid[0]:
          close_bid = bid + [name]
      if ask is not None:
        if ask[0] < open_ask[0]:
          open_ask = ask + [name]
        if self.__position[name] < 0 and ask[0] < close_ask[0]:
          close_ask = ask + [name]
    if len(open_bid) == 3 and len(open_ask) == 3:
      return open_bid, open_ask, close_bid, close_ask
    else:
      raise RuntimeError('cannot get open_bid or open_ask')

  def __open_position(self, symbol, open_bid, open_ask):
    volume = min(open_bid[1], open_ask[1])
    rate = (open_bid[0] - open_ask[0]) / open_bid[0]  # rise and fall rate
    if rate > self.__open_margin:
      # create order
      if not self.__demo:
        self.__clients[open_bid[-1]].create_market_sell_order(symbol, volume)
        self.__clients[open_ask[-1]].create_market_buy_order(symbol, volume)
      # save position
      if self.__close_margin is not None:
        self.__position[open_bid[-1]] -= volume
        self.__position[open_ask[-1]] += volume
      # logger
      print ('OPEN {0} : {1} bid {2}, {3} ask {4}, profit {5}'.format(symbol, open_bid[-1], open_bid[0], open_ask[-1], open_ask[0], (open_bid[0] - open_ask[0]) * volume))

  def __close_position(self, symbol, close_bid, close_ask):
    if len(close_bid) == 3 and len(close_ask) == 3:
      volume = min(close_bid[1], close_ask[1], abs(self.__position[close_bid[-1]]), abs(self.__position[close_ask[-1]]))
      rate = (close_bid[0] - close_ask[0]) / close_bid[0]  # rise and fall rate
      if rate > self.__close_margin:
        # create order
        if not self.__demo:
          self.__clients[close_bid[-1]].create_market_sell_order(symbol, volume)
          self.__clients[close_ask[-1]].create_market_buy_order(symbol, volume)
        # save position
        self.__position[close_bid[-1]] -= volume
        self.__position[close_ask[-1]] += volume
        # logger
        print ('CLOSE {0} : {1} bid {2}, {3} ask {4}, profit {5}'.format(symbol, close_bid[-1], close_bid[0], close_ask[-1], close_ask[0], (close_bid[0] - close_ask[0]) * volume))

  def force_close_position(self, symbol):
    if not self.__demo and self.__force_close_position:
      for name, volume in self.__position.items():
        if volume > 0:
          self.__clients[name].create_market_sell_order(symbol, abs(volume))
        elif volume < 0:
          self.__clients[name].create_market_buy_order(symbol, abs(volume))
        else:
          pass
