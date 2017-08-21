import gi
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GObject, AppIndicator3
from bitgui.config import Config
import bitgui.graph

class View:

	APPINDICATOR_ID = 'btc-indicator'

	def __init__(self):
		self.labels = []
		self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

		for market_config in Config.markets:
			provider, market = market_config['provider'], market_config['market']

			hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
			hbox.set_homogeneous(False)

			market_name = '{} - {}:'.format(provider.get_name(), market)
			name_label = Gtk.Label(market_name)
			hbox.pack_start(name_label, True, True, 10)
			val_label = Gtk.Label()
			hbox.pack_start(val_label, True, True, 10)
			self.labels.append(val_label)
			self.vbox.pack_start(hbox, True, True, 10)

		self.graph = bitgui.graph.Graph()
		self.vbox.pack_start(self.graph, True, True, 10)

		self.win = Gtk.Window()
		self.win.set_icon_from_file('icon.png')
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
		self.indicator = AppIndicator3.Indicator.new(self.APPINDICATOR_ID, 'icon.png', category)
		self.indicator.set_title("Bitcoin Indicator")
		self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
		self.indicator.set_menu(self.menu)

	def set_current_price(self, i, price_str, wnd_title):
		GObject.idle_add(self.labels[i].set_text, price_str)
		if wnd_title:
			GObject.idle_add(self.win.set_title, price_str)
			GObject.idle_add(self.indicator.set_label, price_str, '20px')
			GObject.idle_add(self.menu_item.set_label, price_str)

	def present_window(self, widget):
		self.win.present()

	def set_graph_data(self, i, x, y):
		GObject.idle_add(self.graph.set_data, i, x, y)
