import os, time, gi
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GObject, AppIndicator3
from btcwidget.config import Config
import btcwidget.graph
from definitions import ROOT_DIR

class View:

	APPINDICATOR_ID = 'btc-indicator'
	if Config.dark_theme:
		COLORS = ['#4444FF', '#00FF00', '#FF0000', '#FFFF00', '#00FFFF', '#FF00FF']
	else:
		COLORS = ['#0000CC', '#00CC00', '#CC0000', '#CCCC00', '#00CCCC', '#CC00CC']

	def __init__(self):

		self.labels = []
		self.labels_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		for i, market_config in enumerate(Config.markets):
			provider, market = market_config['provider'], market_config['market']

			hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

			market_name = '{} - {}:'.format(provider.get_name(), market)
			color = self._get_color(i)
			name_label = Gtk.Label(market_name)
			name_label.set_markup('<span color="{}">{}</span>'.format(color, market_name))
			name_label.set_size_request(150, 10)
			name_label.set_alignment(0, 0.5)
			hbox.pack_start(name_label, False, False, 10)
			val_label = Gtk.Label()
			hbox.pack_start(val_label, False, False, 10)
			self.labels.append(val_label)
			self.labels_vbox.pack_start(hbox, True, True, 2)

		self.graph = btcwidget.graph.Graph(Config.dark_theme)

		self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.vbox.pack_start(self.labels_vbox, False, False, 5)
		self.vbox.pack_start(self.graph, True, True, 0)

		self.icon_path = os.path.join(ROOT_DIR, 'icon.png')
		self.win = Gtk.Window()
		self.win.set_icon_from_file(self.icon_path)
		self.win.connect('delete-event', Gtk.main_quit)
		self.win.add(self.vbox)
		self.win.show_all()

		self.create_indicator()

	def create_indicator(self):
		self.menu = Gtk.Menu()
		self.menu_item = Gtk.MenuItem("Bitcoin")
		self.menu_item.show()
		self.menu_item.connect('activate', self.present_window)
		self.menu.append(self.menu_item)
		self.menu.show()

		category = AppIndicator3.IndicatorCategory.APPLICATION_STATUS
		self.indicator = AppIndicator3.Indicator.new(self.APPINDICATOR_ID, self.icon_path, category)
		self.indicator.set_title("Bitcoin Indicator")
		self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
		self.indicator.set_menu(self.menu)

	def _set_current_price_gui_thread(self, i, price_str, wnd_title):
		price_html = '<span color="{}">{}</span>'.format(self._get_color(i), price_str)
		self.labels[i].set_markup(price_html)
		if wnd_title:
			self.win.set_title(price_str)
			self.win.set_title(price_str)
			self.indicator.set_label(price_str, '20px')
			self.menu_item.set_label(price_str)

	def set_current_price(self, i, price_str, wnd_title):
		GObject.idle_add(self._set_current_price_gui_thread, i, price_str, wnd_title)

	def present_window(self, widget):
		self.win.present()

	def set_graph_data(self, i, graph_data):
		now = time.time()
		graph_price_mult = Config.markets[i].get('graph_price_mult', 1)
		x = [int((e['time'] - now) / Config.time_axis_div) for e in graph_data]
		y = [e['close'] * graph_price_mult for e in graph_data]
		GObject.idle_add(self.graph.set_data, i, x, y, self._get_color(i))

	def _get_color(self, i):
		return self.COLORS[i % len(self.COLORS)]
