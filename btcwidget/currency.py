import json
import os
import requests
import time

from definitions import ROOT_DIR


class _CurrencyService:
    _CACHE_PATH = os.path.join(ROOT_DIR, 'currency.cache.json')

    def __init__(self):
        self._data = None

    def _get_current_date(self):
        return time.strftime('%Y-%m-%d')

    def _load(self):
        # try load from cache
        if os.path.isfile(self._CACHE_PATH):
            with open(self._CACHE_PATH, 'r') as file:
                self._data = json.load(file)
                # check if data is new enough
                if self._data['fetch_date'] == self._get_current_date():
                    return
        # fetch data from Internet
        print("Fetching currency exchange rates...")
        resp = requests.get('http://api.fixer.io/latest')
        resp.raise_for_status()
        self._data = resp.json()
        self._data['fetch_date'] = self._get_current_date()
        # update cache
        data_json = json.dumps(self._data, indent=4)
        with open(self._CACHE_PATH, 'w') as file:
            file.write(data_json)

    def convert(self, value, from_currency, to_currency):
        if not self._data:
            self._load()
        if from_currency != self._data['base']:
            value /= self._data['rates'][from_currency]
        if to_currency != self._data['base']:
            value *= self._data['rates'][to_currency]
        return value

    def list(self):
        if not self._data:
            self._load()
        return [self._data['base']] + list(self._data['rates'].keys())

    def format_price(self, price, currency):
        if currency == 'USD':
            return '${:.2f}'.format(price)
        else:
            return '{:.2f} {}'.format(price, currency)


service = _CurrencyService()
