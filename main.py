#!/usr/bin/env python3
import gi, threading, time, signal
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk
from btcwidget.view import View
from btcwidget.config import Config
import btcwidget.exchanges


def thread_proc(view, market_index):

	market_config = Config.markets[market_index]
	provider, market = market_config['provider'], market_config['market']
	last_graph_update = 0
	graph_data = []

	while True:
		price = provider.ticker(market)
		price_str = provider.format_price(price, market)
		print('{} {} ticker: {}'.format(provider.get_name(), market, price_str))
		view.set_current_price(market_index, price_str, market_config['wnd_title'])

		if market_config['graph']:
			now = time.time()
			if now - last_graph_update >= Config.graph_interval_sec:
				print('Updating graph data')
				graph_data = provider.graph(market, Config.graph_period_sec, Config.graph_res)
				last_graph_update = now

			graph_data.append({
				'time': now,
				'close': price,
			})

			if graph_data:
				view.set_graph_data(market_index, graph_data)

		time.sleep(Config.update_interval_sec)

def main():
	GObject.threads_init()
	view = View()

	for i, market_config in enumerate(Config.markets):
		thread = threading.Thread(target = thread_proc, args = (view,i, ), daemon = True)
		thread.start()

	signal.signal(signal.SIGINT, signal.SIG_DFL)
	Gtk.main()

if __name__ == '__main__':
	main()
