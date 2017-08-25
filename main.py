#!/usr/bin/env python3

import gi, threading, time, signal
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk
from btcwidget.view import View
from btcwidget.config import Config
import btcwidget.exchanges

class UpdateThread(threading.Thread):

	def __init__(self, view):
		threading.Thread.__init__(self, daemon=True)
		self._view = view
		self._last_graph_update = 0
		self._graph_data_dict = {}
		Config.register_change_callback(self.clear)

	def run(self):
		while True:
			self._update_tickers()
			self._update_graph()
			time.sleep(Config.update_interval_sec)

	def _update_tickers(self):
		for i, market_config in enumerate(Config.markets):
			self._update_market_ticker(i)

	def _update_graph(self):
		now = time.time()
		update_graph = now - self._last_graph_update >= Config.graph_interval_sec
		if update_graph:
			print('Updating graph data')
		self._last_graph_update = now
		for i, market_config in enumerate(Config.markets):
			if market_config['graph']:
				if update_graph:
					self._update_market_graph_data(i)
				if i in self._graph_data_dict:
					self._view.set_graph_data(i, self._graph_data_dict[i])

	def _update_market_ticker(self, market_index):
		now = time.time()
		market_config = Config.markets[market_index]
		provider, market = market_config['provider'], market_config['market']
		price = provider.ticker(market)
		price_str = provider.format_price(price, market)
		print('{} {} ticker: {}'.format(provider.get_name(), market, price_str))
		self._view.set_current_price(market_index, price_str, market_config['wnd_title'])
		if not market_index in self._graph_data_dict:
			self._graph_data_dict[market_index] = []
		graph_data = self._graph_data_dict[market_index]
		graph_data.append({
			'time': now,
			'close': price,
		})

	def _update_market_graph_data(self, market_index):
		now = time.time()
		market_config = Config.markets[market_index]
		provider, market = market_config['provider'], market_config['market']
		graph_data = provider.graph(market, Config.graph_period_sec, Config.graph_res)
		graph_data = [t for t in graph_data if t['time'] > now - Config.graph_period_sec]
		self._graph_data_dict[market_index] = graph_data

	def clear(self):
		print('clear')
		self._last_graph_update = 0
		self._graph_data_dict = {}

def main():
	GObject.threads_init()
	view = View()
	thread = UpdateThread(view)
	thread.start()
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	Gtk.main()

if __name__ == '__main__':
	main()
