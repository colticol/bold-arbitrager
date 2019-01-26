import sys
import time

from settings import settings
from exchange.exchange_controller import ExchangeController


class BoldArbitrager(object):
  """Arbitrager"""
  def __init__(self):
    self.__symbols  = settings['logic']['symbols'].split(';')
    self.__interval = settings['logic']['interval']
    self.__exchange = ExchangeController(settings['exchange'], settings['logic'])

  def go(self):
    try:
      while True:
        for symbol in self.__symbols:
          self.__exchange.arbitrage(symbol)
        time.sleep(self.__interval)
    except Exception as e:
      raise e

if __name__ == '__main__':
  bot = BoldArbitrager()
  bot.go()
