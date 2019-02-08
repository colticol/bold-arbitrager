import sys
import time

from settings import settings
from exchange.exchange_controller import ExchangeController


class BoldArbitrager(object):
  """Arbitrager"""
  def __init__(self):
    self.__symbol  = settings['logic']['symbol']
    self.__interval = settings['logic']['interval']
    self.__exchange = ExchangeController(settings['exchange'], settings['logic'])

  def go(self):
    try:
      while True:
        self.__exchange.arbitrage(self.__symbol)
        time.sleep(self.__interval)
    except Exception as e:
      raise e
    finally:
      self.__exchange.force_close_position(self.__symbol)

if __name__ == '__main__':
  bot = BoldArbitrager()
  bot.go()
