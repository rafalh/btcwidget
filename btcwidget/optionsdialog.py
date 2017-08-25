import os
from gi.repository import Gtk
from definitions import ROOT_DIR
from btcwidget.config import Config
import btcwidget.exchanges


class OptionsDialog(Gtk.Dialog):

	_NAME_COL = 0
	_TICKER_COL = 1
	_GRAPH_COL = 2
	_INDICATOR_COL = 3
	_PRICE_MULT_COL = 4
	_EXCHANGE_COL = 5
	_MARKET_COL = 6

	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "Options", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OK, Gtk.ResponseType.OK))

		box = self.get_content_area()

		self.update_interval_entry = Gtk.Entry(text=str(Config.update_interval_sec))
		self._add_label_and_widget("Update Interval (sec.):", self.update_interval_entry)

		self.graph_interval_entry = Gtk.Entry(text=str(Config.graph_interval_sec))
		self._add_label_and_widget("Graph Interval (sec.):", self.graph_interval_entry)

		self.graph_period_entry = Gtk.Entry(text=str(Config.graph_period_sec))
		self._add_label_and_widget("Graph Period (sec.):", self.graph_period_entry)

		self.dark_theme_check = Gtk.CheckButton("Dark Theme", active=Config.dark_theme)
		box.add(self.dark_theme_check)

		self.store = Gtk.TreeStore(str, bool, bool, bool, float, str, str)

		exchange_ids = btcwidget.exchanges.factory.list()
		market_config_dict = {}
		for market_config in Config.markets:
			market_config_dict[(market_config['provider'].ID, market_config['market'])] = market_config
		
		for id in exchange_ids:
			provider = btcwidget.exchanges.factory.get(id)
			markets = provider.get_markets()
			treeiter = self.store.append(None, [provider.get_name(), None, None, None, None, id, None])
			for market in provider.get_markets():
				market_config = market_config_dict.get((id, market), {})
				ticker = market_config.get('ticker', False)
				graph = market_config.get('graph', False)
				indicator = market_config.get('wnd_title', False)
				graph_price_mult = market_config.get('graph_price_mult', 1)

				self.store.append(treeiter, [market, ticker, graph, indicator, graph_price_mult, id, market])
		tree = Gtk.TreeView(self.store)

		renderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn("Exchange Market", renderer, text=self._NAME_COL)
		tree.append_column(column)

		renderer = Gtk.CellRendererToggle()
		column = Gtk.TreeViewColumn("Ticker", renderer, active=self._TICKER_COL)
		tree.append_column(column)
		renderer.connect("toggled", self._on_toggle_ticker)

		renderer = Gtk.CellRendererToggle()
		column = Gtk.TreeViewColumn("Graph", renderer, active=self._GRAPH_COL)
		tree.append_column(column)
		renderer.connect("toggled", self._on_toggle_graph)

		renderer = Gtk.CellRendererToggle()
		column = Gtk.TreeViewColumn("Indicator", renderer, active=self._INDICATOR_COL)
		tree.append_column(column)
		renderer.connect("toggled", self._on_toggle_indicator)

		renderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn("Price Multiplier", renderer, text=self._PRICE_MULT_COL)
		tree.append_column(column)
		renderer.set_property("editable", True)
		renderer.connect("edited", self._on_price_mult_edited)

		tree.expand_all()
		box.add(tree)

		self.show_all()

	def _on_toggle_ticker(self, renderer, path):
		treeiter = self.store.get_iter(path)
		if self.store[treeiter][self._MARKET_COL]:
			self.store[treeiter][self._TICKER_COL] = not self.store[treeiter][self._TICKER_COL]

	def _on_toggle_graph(self, renderer, path):
		treeiter = self.store.get_iter(path)
		if self.store[treeiter][self._MARKET_COL]:
			self.store[treeiter][self._GRAPH_COL] = not self.store[treeiter][self._GRAPH_COL]

	def _on_toggle_indicator(self, renderer, path):
		treeiter = self.store.get_iter(path)
		if self.store[treeiter][self._MARKET_COL]:
			self.store[treeiter][self._INDICATOR_COL] = not self.store[treeiter][self._INDICATOR_COL]

	def _on_price_mult_edited(self, renderer, path, text):
		treeiter = self.store.get_iter(path)
		if self.store[treeiter][self._MARKET_COL]:
			try:
				self.store[treeiter][self._PRICE_MULT_COL] = float(text)
			except ValueError as e:
				print(e) # ignore error

	def _add_label_and_widget(self, label_text, widget):
		hbox = Gtk.Box(spacing=6)
		label = Gtk.Label(label_text)
		hbox.pack_start(label, True, True, 0)
		hbox.pack_start(widget, True, True, 0)
		self.get_content_area().add(hbox)

	def update_config(self):
		try:
			Config.update_interval_sec = int(self.update_interval_entry.get_text())
			Config.graph_interval_sec = int(self.graph_interval_entry.get_text())
			Config.graph_period_sec = int(self.graph_period_entry.get_text())
			Config.dark_theme = self.dark_theme_check.get_active()

			Config.markets = []
			treeiter = self.store.get_iter_first()
			while treeiter:
				childiter = self.store.iter_children(treeiter)
				while childiter:
					row = self.store[childiter]
					if row[self._MARKET_COL]:
						provider = btcwidget.exchanges.factory.get(row[self._EXCHANGE_COL])
						market_config = {
							'provider': provider,
							'market': row[self._MARKET_COL],
							'ticker': row[self._TICKER_COL],
							'graph': row[self._GRAPH_COL],
							'wnd_title': row[self._INDICATOR_COL],
							'graph_price_mult': float(row[self._PRICE_MULT_COL]),
						}
						if market_config['ticker'] or market_config['graph'] or market_config['wnd_title']:
							Config.markets.append(market_config)
					childiter = self.store.iter_next(childiter)
				treeiter = self.store.iter_next(treeiter)

		except ValueError as e:
			print(e) # ignore errors
