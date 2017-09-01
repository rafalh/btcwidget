import threading
import time
import sys
from gi.repository import GObject

import btcwidget.currency
import btcwidget.exchanges
import btcwidget.alarmmessage
from btcwidget.config import config


class UpdateThread(threading.Thread):
    def __init__(self, main_win):
        threading.Thread.__init__(self, daemon=True)
        self._main_win = main_win
        self._last_graph_update = 0
        self._graph_data_dict = {}
        self._last_ticer = {}
        config.register_change_callback(self.clear)

    def run(self):
        while True:
            self._update_tickers()
            self._update_graph()
            time.sleep(config['update_interval_sec'])

    def _update_tickers(self):
        for i, market_config in enumerate(config['markets']):
            try:
                self._update_market_ticker(i)
            except Exception as e:
                print('Failed to update ticker data for {}: {}'.format(market_config['exchange'], e), file=sys.stderr)

    def _update_graph(self):
        now = time.time()
        update_graph = now - self._last_graph_update >= config['graph_interval_sec']
        if update_graph:
            print('Updating graph data')
        self._last_graph_update = now
        for i, market_config in enumerate(config['markets']):
            if market_config['graph']:
                if update_graph:
                    try:
                        self._update_market_graph_data(i)
                    except Exception as e:
                        print('Failed to update graph data for {}: {}'.format(market_config['exchange'], e),
                              file=sys.stderr)

                if i in self._graph_data_dict:
                    graph_data = self._graph_data_dict[i]
                    GObject.idle_add(self._main_win.set_graph_data, i, graph_data)

    def _update_market_ticker(self, market_index):
        now = time.time()
        market_config = config['markets'][market_index]
        exchange, market = market_config['exchange'], market_config['market']
        provider = btcwidget.exchanges.factory.get(exchange)
        price = provider.ticker(market)
        price_str = btcwidget.currency.service.format_price(price, market[3:])
        print('{} {} ticker: {}'.format(provider.get_name(), market, price_str))
        GObject.idle_add(self._main_win.set_current_price, market_index, price_str)

        self._check_alarms(exchange, market, price)

        self._last_ticer[market_index] = {
            'time': now,
            'open': price,
            'close': price,
        }
        if market_index in self._graph_data_dict:
            graph_data = self._graph_data_dict[market_index]
            graph_data.append(self._last_ticer[market_index])
            graph_since_time = now - config['graph_period_sec']
            self._graph_data_dict[market_index] = [t for t in graph_data if t['time'] > graph_since_time]

    def _update_market_graph_data(self, market_index):
        now = time.time()
        market_config = config['markets'][market_index]
        exchange, market = market_config['exchange'], market_config['market']
        provider = btcwidget.exchanges.factory.get(exchange)
        graph_data = provider.graph(market, config['graph_period_sec'], config['graph_res'])
        if market_index in self._last_ticer:
            graph_data.append(self._last_ticer[market_index])
        graph_data = [t for t in graph_data if t['time'] > now - config['graph_period_sec']]
        self._graph_data_dict[market_index] = graph_data

    def clear(self):
        self._last_graph_update = 0
        self._graph_data_dict = {}
        self._last_ticer = {}

    def _check_alarms(self, exchange, market, price):
        for alarm in config['alarms']:
            if alarm['exchange'] == exchange and alarm['market'] == market:
                if alarm['type'] == 'A' and price >= alarm['price']:
                    self._trigger_alarm(alarm, price)
                if alarm['type'] == 'B' and price <= alarm['price']:
                    self._trigger_alarm(alarm, price)

    def _trigger_alarm(self, alarm, price):
        if alarm['type'] == 'A':
            GObject.idle_add(btcwidget.alarmmessage.alarm_above_message, alarm, price)
        else:
            GObject.idle_add(btcwidget.alarmmessage.alarm_below_message, alarm, price)
        config['alarms'].remove(alarm)
        config.save()
