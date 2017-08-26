import os, time, gi
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GObject, AppIndicator3
from btcwidget.config import config
import btcwidget.graph, btcwidget.exchanges
from btcwidget.optionsdialog import OptionsDialog
from definitions import ROOT_DIR

class View:

	APPINDICATOR_ID = 'btc-indicator'
	if config['dark_theme']:
		COLORS = ['#4444FF', '#00FF00', '#FF0000', '#FFFF00', '#00FFFF', '#FF00FF']
	else:
		COLORS = ['#0000CC', '#00CC00', '#CC0000', '#CC8800', '#00CCCC', '#CC00CC']

	def __init__(self):

		self._ticker_labels = {}
		self._tickers_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self._create_ticker_labels()

		self._graph = btcwidget.graph.Graph(config['dark_theme'])

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		vbox.pack_start(self._tickers_vbox, False, False, 5)
		vbox.pack_start(self._graph, True, True, 0)

		self._icon_path = os.path.join(ROOT_DIR, 'icon.png')
		self._win = Gtk.Window()
		self._win.set_icon_from_file(self._icon_path)
		self._win.connect('delete-event', Gtk.main_quit)
		self._win.add(vbox)
		self._win.show_all()

		self.create_indicator()
		#self.open_options_window(None)

	def _create_ticker_labels(self):
		self._tickers_vbox.forall(lambda w: w.destroy())
		self._ticker_labels = {}

		for i, market_config in enumerate(config['markets']):
			if market_config['ticker']:
				hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
				exchange, market = market_config['exchange'], market_config['market']
				provider = btcwidget.exchanges.factory.get(exchange)
				market_name = '{} - {}:'.format(provider.get_name(), market)
				color = self._get_color(i)
				name_label = Gtk.Label(market_name)
				name_label.set_markup('<span color="{}">{}</span>'.format(color, market_name))
				name_label.set_size_request(150, 10)
				name_label.set_alignment(0, 0.5)
				hbox.pack_start(name_label, False, False, 10)
				price_label = Gtk.Label()
				hbox.pack_start(price_label, False, False, 10)
				self._ticker_labels[i] = price_label
				self._tickers_vbox.pack_start(hbox, True, True, 2)

		self._tickers_vbox.show_all()

	def create_indicator(self):
		menu = Gtk.Menu()

		self._menu_item = Gtk.MenuItem("Bitcoin")
		self._menu_item.connect('activate', self.present_window)
		menu.append(self._menu_item)

		options_menu_item = Gtk.MenuItem("Options...")
		options_menu_item.connect('activate', self.open_options_window)
		menu.append(options_menu_item)

		menu.show_all()

		category = AppIndicator3.IndicatorCategory.APPLICATION_STATUS
		self._indicator = AppIndicator3.Indicator.new(self.APPINDICATOR_ID, self._icon_path, category)
		self._indicator.set_title("Bitcoin Indicator")
		self._indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
		self._indicator.set_menu(menu)

	def _set_current_price_gui_thread(self, i, price_str, wnd_title):
		price_html = '<span color="{}">{}</span>'.format(self._get_color(i), price_str)
		if i in self._ticker_labels:
			self._ticker_labels[i].set_markup(price_html)
		if wnd_title:
			self._win.set_title(price_str)
			self._win.set_title(price_str)
			self._indicator.set_label(price_str, '20px')
			self._menu_item.set_label(price_str)

	def set_current_price(self, i, price_str, wnd_title):
		GObject.idle_add(self._set_current_price_gui_thread, i, price_str, wnd_title)

	def present_window(self, widget):
		self._win.present()

	def open_options_window(self, widget):
		dialog = OptionsDialog(self._win)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			dialog.update_config()
			self._on_config_change()
		dialog.destroy()

	def _on_config_change(self):
		self._graph.set_dark(config['dark_theme'])
		self._create_ticker_labels()
		self._graph.clear()
		config.run_change_callbacks()

	def set_graph_data(self, i, graph_data):
		now = time.time()
		graph_price_mult = config['markets'][i].get('graph_price_mult', 1)
		x = [int((e['time'] - now) / config['time_axis_div']) for e in graph_data]
		y = [float(e['close']) * graph_price_mult for e in graph_data]
		GObject.idle_add(self._graph.set_data, i, x, y, self._get_color(i))

	def _get_color(self, i):
		return self.COLORS[i % len(self.COLORS)]
