import os, time, gi
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GObject, AppIndicator3
from btcwidget.config import Config
import btcwidget.graph
from definitions import ROOT_DIR

class View:

	APPINDICATOR_ID = 'btc-indicator'

	def __init__(self):
		self.labels = []
		self.labels_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		for market_config in Config.markets:
			provider, market = market_config['provider'], market_config['market']

			hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

			market_name = '{} - {}:'.format(provider.get_name(), market)
			name_label = Gtk.Label(market_name)
			name_label.set_size_request(150, 10)
			name_label.set_alignment(0, 0.5)
			hbox.pack_start(name_label, False, False, 10)
			val_label = Gtk.Label()
			hbox.pack_start(val_label, False, False, 10)
			self.labels.append(val_label)
			self.labels_vbox.pack_start(hbox, True, True, 2)

		self.graph = btcwidget.graph.Graph()

		self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.vbox.pack_start(self.labels_vbox, True, True, 5)
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
		self.labels[i].set_text(price_str)
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
		x = [int((e['time'] - now) / Config.time_axis_div) for e in graph_data]
		y = [e['close'] for e in graph_data]
		GObject.idle_add(self.graph.set_data, i, x, y)
