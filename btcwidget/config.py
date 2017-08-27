import json
import os

from definitions import ROOT_DIR

_MOCK = False


class _Config(dict):
    if _MOCK:
        _DEFAULT_MARKETS = [
            {
                'exchange': 'mock',
                'market': 'BTCUSD',
                'ticker': True,
                'graph': True,
                'indicator': True,
            },
        ]
    else:
        _DEFAULT_MARKETS = [
            {
                'exchange': 'bitfinex.com',
                'market': 'BTCUSD',
                'ticker': True,
                'graph': True,
                'indicator': True,
            },
            {
                'exchange': 'bitstamp.net',
                'market': 'BTCUSD',
                'ticker': True,
                'graph': True,
                'indicator': False,
            },
        ]

    _DEFAULT = {
        'update_interval_sec': 10 if not _MOCK else 1,
        'graph_interval_sec': 5 * 60 if not _MOCK else 10,
        # show last 60 minutes
        'graph_period_sec': 60 * 60,
        'graph_res': 200,
        'graph_currency': 'USD',
        # time axis in minutes
        'time_axis_div': 1,
        'dark_theme': False,
        'markets': _DEFAULT_MARKETS
    }

    CONFIG_PATH = os.path.join(ROOT_DIR, 'config.json')

    def __init__(self):
        dict.__init__(self, self._DEFAULT)
        self._callbacks = []

    def load(self):
        if _MOCK:
            return
        if not os.path.isfile(self.CONFIG_PATH):
            return
        with open(self.CONFIG_PATH, 'r') as config_file:
            self.update(json.load(config_file))

    def save(self):
        if _MOCK:
            return
        config_json = json.dumps(self, indent=4)
        with open(self.CONFIG_PATH, 'w') as config_file:
            config_file.write(config_json)

    def register_change_callback(self, func):
        self._callbacks.append(func)

    def run_change_callbacks(self):
        for func in self._callbacks:
            func()


config = _Config()
