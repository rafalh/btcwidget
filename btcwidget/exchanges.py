import time, requests, json
from itertools import groupby
import random, time, math  # mock


class ExchangeProvider:
    """Exchange data provider interface"""

    def get_name(self):
        """Returns exchange name for use in user interface"""
        raise NotImplementedError()

    def get_markets(self):
        """Returns list of supported market codes.
        Each 6-letters code is built from two ISO 4217 currency codes used for trading."""
        raise NotImplementedError()

    def ticker(self, market):
        """Returns current price"""
        raise NotImplementedError()

    def graph(self, market, period_seconds, resolution):
        """Returns graph data for given period. Graph data is list of dicts with keys:
        'time' (UTC timestamp), 'open' (open price), 'close' (close price)."""
        raise NotImplementedError()


class MockProvider:
    """Provider used for testing"""

    ID = 'mock'

    AVG_PRICE = 4000
    NOISE = 20
    WAVE1_A = 300
    WAVE1_F = 0.0003
    WAVE2_A = 100
    WAVE2_F = 0.0011

    def __init__(self):
        self.start_time = time.time()

    def get_name(self):
        return "Mock"

    def get_markets(self):
        return ['BTCUSD']

    def _calc_price(self, timestamp):
        delta_time = timestamp - self.start_time
        x = random.gauss(self.AVG_PRICE, self.NOISE)
        w = 2 * math.pi * self.WAVE1_F
        x += self.WAVE1_A * math.sin(w * delta_time)
        w = 2 * math.pi * self.WAVE2_F
        x += self.WAVE2_A * math.sin(w * delta_time)
        return x

    def ticker(self, market):
        return self._calc_price(time.time())

    def graph(self, market, period_seconds, resolution):
        stop = int(time.time())
        start = int(stop - period_seconds)
        step = max(int(period_seconds / resolution), 1)
        data = []
        for i in range(start, stop, step):
            entry = {
                'time': i,
                'close': self._calc_price(i)
            }
            data.append(entry)
        return data


class BitfinexExchangeProvider(ExchangeProvider):
    ID = 'bitfinex.com'

    def get_name(self):
        return "Bitfinex.com"

    def get_markets(self):
        return ['BTCUSD']

    def ticker(self, market):
        resp = requests.get('https://api.bitfinex.com/v2/ticker/t{}'.format(market))
        resp.raise_for_status()
        data = resp.json()
        return data[6]  # last price

    def _convert_period(self, period_seconds):
        # Available values: '1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D', '7D', '14D', '1M'
        m = 60
        h = 60 * m
        d = 24 * h
        periods = [
            (1 * m, '1m'),
            (5 * m, '5m'),
            (15 * m, '15m'),
            (30 * m, '30m'),
            (1 * h, '1h'),
            (3 * h, '3h'),
            (6 * h, '6h'),
            (12 * h, '12h'),
            (1 * d, '1D'),
            (7 * d, '7D'),
            (14 * d, '14D'),
            (None, '1M'),
        ]
        for sec, code in periods:
            if not sec or sec >= period_seconds:
                return code

    def graph(self, market, period_seconds, resolution):
        period = self._convert_period(period_seconds / 100)
        start_ms = (time.time() - period_seconds) * 1000
        url = 'https://api.bitfinex.com/v2/candles/trade:{}:t{}/hist?start={}&limit={}'.format(period, market, start_ms,
                                                                                               resolution)
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        data = [{'time': e[0] / 1000, 'open': e[1], 'close': e[2]} for e in data]
        data = sorted(data, key=lambda e: e['time'])
        return data


class BitstampExchangeProvider(ExchangeProvider):
    ID = 'bitstamp.net'

    def get_name(self):
        return "Bitstamp.net"

    def get_markets(self):
        return ['BTCUSD']

    def ticker(self, market):
        resp = requests.get('https://www.bitstamp.net/api/v2/ticker/{}/'.format(market.lower()))
        resp.raise_for_status()
        data = resp.json()
        return float(data['last'])

    def graph(self, market, period_seconds, resolution):
        if period_seconds <= 60:
            time = 'minute'
        elif period_seconds <= 3600:
            time = 'hour'
        else:
            time = 'day'
        print('bitstamp.net: getting transactions for {}'.format(time))
        # there should be some dedicated API...
        resp = requests.get('https://www.bitstamp.net/api/v2/transactions/{}/?time={}'.format(market.lower(), time))
        resp.raise_for_status()
        transactions = resp.json()
        transactions = sorted(transactions, key=lambda t: int(t['date']))
        data = []
        step = int(period_seconds / resolution)
        for k, g in groupby(transactions, lambda t: int(int(t['date']) / step) * step):
            gt = list(g)
            e = {
                'time': k
            }
            if len(gt) == 0:
                e['open'] = e['close'] = data[-1]['close']
            else:
                e['open'] = float(gt[0]['price'])
                e['close'] = float(gt[-1]['price'])
            data.append(e)
        return data


class BitBayExchangeProvider(ExchangeProvider):
    ID = 'bitbay.net'
    _TID_STEP = 300

    def __init__(self):
        self._min_time = float('inf')
        self._min_tid = float('inf')
        self._max_tid = None
        self._trades_cache = {}

    def get_name(self):
        return "BitBay.net"

    def get_markets(self):
        return ['BTCPLN']

    def ticker(self, market):
        resp = requests.get('https://bitbay.net/API/Public/{}/ticker.json'.format(market))
        resp.raise_for_status()
        data = resp.json()
        return float(data['last'])

    def _load_trades(self, market, since_tid=None):
        params = {}
        if since_tid:
            params['since'] = since_tid
        else:
            params['sort'] = 'desc'
        resp = requests.get('https://bitbay.net/API/Public/{}/trades.json'.format(market), params)
        resp.raise_for_status()
        trades = resp.json()
        tids = [int(t['tid']) for t in trades]
        timestamps = [int(t['date']) for t in trades]
        min_tid, max_tid = min(tids), max(tids)
        min_time, max_time = min(timestamps), max(timestamps)

        self._min_time = min(self._min_time, min_time)
        self._min_tid = min(self._min_tid, since_tid or min_tid)

        for t in trades:
            self._trades_cache[int(t['tid'])] = t

        print('bitbay.net trades tids {} - {} (since {})'.format(min_tid, max_tid, since_tid))
        print('bitbay.net trades timestamps {} - {} (period {})'.format(min_time, max_time, max_time - min_time))
        return min_tid, max_tid

    def _load_trades_tid_range(self, market, since_tid, until_tid):
        while since_tid < until_tid:
            min_tid, max_tid = self._load_trades(market, since_tid)
            since_tid = max_tid

    def _load_trades_since_time(self, market, since_time):
        # get newest
        self._load_trades(market, self._max_tid)

        print('bitbay.net should fetch trades: {} > {}?'.format(self._min_time, since_time))
        while self._min_time > since_time:
            since_tid = self._min_tid - self._TID_STEP
            self._load_trades_tid_range(market, since_tid, self._min_tid)

    def graph(self, market, period_seconds, resolution):
        since_time = time.time() - period_seconds
        self._load_trades_since_time(market, since_time)

        trades = [t for t in self._trades_cache.values() if t['date'] >= since_time]
        trades = sorted(trades, key=lambda t: int(t['date']))

        data = []
        step = int(period_seconds / resolution)
        for k, g in groupby(trades, lambda t: int(int(t['date']) / step) * step):
            gt = list(g)
            e = {
                'time': k
            }
            if len(gt) == 0:
                e['open'] = e['close'] = data[-1]['close']
            else:
                e['open'] = float(gt[0]['price'])
                e['close'] = float(gt[-1]['price'])
            data.append(e)

        return data


class BitMarketExchangeProvider(ExchangeProvider):
    ID = 'bitmarket.pl'

    def get_name(self):
        return "BitMarket.pl"

    def get_markets(self):
        return ['BTCPLN']

    def ticker(self, market):
        resp = requests.get('https://www.bitmarket.pl/json/{}/ticker.json'.format(market))
        resp.raise_for_status()
        data = resp.json()
        return data['last']

    def graph(self, market, period_seconds, resolution):
        period = self._convert_period(period_seconds)
        resp = requests.get('https://www.bitmarket.pl/graphs/{}/{}.json'.format(market, period))
        resp.raise_for_status()
        data = resp.json()
        timestamps = [e['time'] for e in data]
        max_time = max(timestamps)
        min_time = max_time - period_seconds
        data = [self._convert_graph_entry(e) for e in data if e['time'] > min_time]
        return data

    def _convert_period(self, period_seconds):
        m = 60
        h = 60 * m
        d = 24 * h
        if period_seconds <= 90 * m:
            period = '90m'
        elif period_seconds <= 6 * h:
            period = '6h'
        elif period_seconds <= 1 * d:
            period = '1d'
        elif period_seconds <= 7 * d:
            period = '7d'
        elif period_seconds <= 30 * d:
            period = '1m'
        elif period_seconds <= 90 * d:
            period = '3m'
        elif period_seconds <= 180 * d:
            period = '6m'
        else:
            period = '1y'
        return period

    def _convert_graph_entry(self, e):
        return {
            'time': e['time'],
            'open': float(e['open']),
            'close': float(e['close']),
        }

class LakeBTCExchangeProvider(ExchangeProvider):
    ID = 'lakebtc.com'

    def get_name(self):
        return "LakeBTC.com"

    def get_markets(self):
        return ['BTCUSD']

    def ticker(self, market):
        resp = requests.get('https://api.LakeBTC.com/api_v2/ticker')
        resp.raise_for_status()
        data = resp.json()
        return float(data['btcusd']['last'])

    def graph(self, market, period_seconds, resolution):
        resp = requests.get('https://api.lakebtc.com/api_v2/bctrades?symbol=btcusd'.format(market.lower()))
        resp.raise_for_status()
        data = resp.json()
        timestamps = [e['date'] for e in data]
        max_time = max(timestamps)
        min_time = max_time - period_seconds
        data = [self._convert_graph_entry(e) for e in data if e['date'] > min_time]
        return data

    def _convert_graph_entry(self, e):
        return {
            'time': e['date'],
            'open': float(e['price']),
            'close': float(e['price']),
        }

class _ExchangeProviderFactory:
    def __init__(self):
        self._cache = {}

    def _create(self, id):
        if id == BitBayExchangeProvider.ID:
            return BitBayExchangeProvider()
        elif id == BitMarketExchangeProvider.ID:
            return BitMarketExchangeProvider()
        elif id == BitstampExchangeProvider.ID:
            return BitstampExchangeProvider()
        elif id == BitfinexExchangeProvider.ID:
            return BitfinexExchangeProvider()
        elif id == LakeBTCExchangeProvider.ID:
            return LakeBTCExchangeProvider()
        elif id == MockProvider.ID:
            return MockProvider()
        else:
            raise ValueError

    def get(self, id):
        if id not in self._cache:
            return self._create(id)
        return self._cache[id]

    def list(self):
        return [
            BitBayExchangeProvider.ID,
            BitMarketExchangeProvider.ID,
            BitstampExchangeProvider.ID,
            BitfinexExchangeProvider.ID,
            LakeBTCExchangeProvider.ID
        ]


factory = _ExchangeProviderFactory()
