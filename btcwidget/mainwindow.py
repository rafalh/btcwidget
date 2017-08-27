import os
import time
from gi.repository import Gtk

import btcwidget.currency
import btcwidget.exchanges
import btcwidget.graph
from btcwidget.config import config
from btcwidget.indicator import Indicator
from btcwidget.optionsdialog import open_options_dialog
from definitions import ROOT_DIR


class MainWindow(Gtk.Window):
    if config['dark_theme']:
        _COLORS = ['#4444FF', '#00FF00', '#FF0000', '#FFFF00', '#00FFFF', '#FF00FF']
    else:
        _COLORS = ['#0000CC', '#00CC00', '#CC0000', '#CC8800', '#00CCCC', '#CC00CC']

    _ICON_PATH = os.path.join(ROOT_DIR, 'icon.png')

    def __init__(self):
        Gtk.Window.__init__(self, title="BTC Widget")

        self._ticker_labels = {}
        self._tickers_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._create_ticker_labels()

        self._graph = btcwidget.graph.Graph(config['dark_theme'])

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(self._tickers_vbox, False, False, 5)
        vbox.pack_start(self._graph, True, True, 0)

        self.set_icon_from_file(self._ICON_PATH)
        self.connect('delete-event', Gtk.main_quit)
        self.add(vbox)
        self.show_all()

        self._indicator = Indicator(self)

    # self.open_options()

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

    def set_current_price(self, i, price_str):
        price_html = '<span color="{}">{}</span>'.format(self._get_color(i), price_str)
        if i in self._ticker_labels:
            self._ticker_labels[i].set_markup(price_html)
        market_config = config['markets'][i]
        if market_config['indicator']:
            self.set_title(price_str)
            self._indicator.set_current_price(price_str)

    def open_options(self):
        if open_options_dialog(self):
            self._on_config_change()

    def _on_config_change(self):
        self._graph.set_dark(config['dark_theme'])
        self._create_ticker_labels()
        self._graph.clear()
        config.run_change_callbacks()

    def set_graph_data(self, i, graph_data):
        now = time.time()
        market = config['markets'][i]['market']
        market_currency = market[3:]
        graph_currency = config['graph_currency']
        graph_price_mult = btcwidget.currency.service.convert(1, market_currency, graph_currency)
        x = [int((e['time'] - now) / config['time_axis_div']) for e in graph_data]
        y = [float(e['close']) * graph_price_mult for e in graph_data]
        self._graph.set_data(i, x, y, self._get_color(i))

    def _get_color(self, i):
        return self._COLORS[i % len(self._COLORS)]
