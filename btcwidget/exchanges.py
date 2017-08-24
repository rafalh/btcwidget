import time, requests, json
from itertools import groupby
import random, time, math # mock


class ExchangeProvider:
	"""Exchange data provider"""

	def get_name(self):
		"""Returns exchange name"""
		pass

	def get_markets(self):
		"""Returns list of supported market codes"""
		pass

	def ticker(self, market):
		"""Returns current price"""
		pass

	def graph(self, market, period_seconds, resolution):
		"""Returns price list for given period"""
		pass

	def format_price(self, price, market):
		"""Formats price for given market adding currency symbol"""
		return str(price)


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
		w = 2*math.pi*self.WAVE1_F
		x += self.WAVE1_A * math.sin(w*delta_time)
		w = 2*math.pi*self.WAVE2_F
		x += self.WAVE2_A * math.sin(w*delta_time)
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
	
	def format_price(self, price, market):
		return '${:.2f}'.format(price)


class BitstampExchangeProvider(ExchangeProvider):

	ID = 'bitstamp.net'

	def get_name(self):
		return "Bitstamp.net"

	def get_markets(self):
		return ['BTCUSD']

	def ticker(self, market):
		data = requests.get('https://www.bitstamp.net/api/v2/ticker/{}/'.format(market.lower())).json()
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
		transactions = resp.json()
		transactions = sorted(transactions, key= lambda t: int(t['date']))
		data = []
		step = int(period_seconds / resolution)
		for k, g in groupby(transactions, lambda t: int(int(t['date']) / step)*step):
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

	def format_price(self, price, market):
		return '${:.2f}'.format(price)


class BitBayExchangeProvider(ExchangeProvider):

	ID = 'bitbay.net'

	def get_name(self):
		return "BitBay.net"

	def get_markets(self):
		return ['BTCPLN']

	def ticker(self, market):
		data = requests.get('https://bitbay.net/API/Public/{}/ticker.json'.format(market)).json()
		return float(data['last'])

	def graph(self, market, period_seconds, resolution):
		# there should be some dedicated API...
		resp = requests.get('https://bitbay.net/API/Public/{}/trades.json?sort=desc'.format(market))
		transactions = resp.json()
		transactions = sorted(transactions, key= lambda t: int(t['date']))
		data = []
		step = int(period_seconds / resolution)
		for k, g in groupby(transactions, lambda t: int(int(t['date']) / step)*step):
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

	def format_price(self, price, market):
		return '{:.2f} PLN'.format(price)


class BitMarketExchangeProvider(ExchangeProvider):
	
	ID = 'bitmarket.pl'

	def get_name(self):
		return "BitMarket.pl"

	def get_markets(self):
		return ['BTCPLN']

	def ticker(self, market):
		data = requests.get('https://www.bitmarket.pl/json/{}/ticker.json'.format(market)).json()
		return data['last']

	def graph(self, market, period_seconds, resolution):
		m = 60
		h = 60*m
		d = 24*h
		if period_seconds <= 90*m:
			period = '90m'
		elif period_seconds <= 6*h:
			period = '6h'
		elif period_seconds <= 1*d:
			period = '1d'
		elif period_seconds <= 7*d:
			period = '7d'
		elif period_seconds <= 30*d:
			period = '1m'
		elif period_seconds <= 90*d:
			period = '3m'
		elif period_seconds <= 180*d:
			period = '6m'
		else:
			period = '1y'
		data = requests.get('https://www.bitmarket.pl/graphs/{}/{}.json'.format(market, period)).json()
		timestamps = [e['time'] for e in data]
		max_time = max(timestamps)
		min_time = max_time - period_seconds
		data = [e for e in data if e['time'] > min_time]
		return data

	def format_price(self, price, market):
		return '{:.2f} PLN'.format(price)

class BitfinexExchangeProvider(ExchangeProvider):

	ID = 'bitfinex.com'

	def get_name(self):
		return "Bitfinex.com"

	def get_markets(self):
		return ['tBTCUSD']

	def ticker(self, market):
		resp = requests.get('https://api.bitfinex.com/v2/ticker/{}'.format(market))
		data = resp.json()
		return data[6] # last price

	def _convert_period(self, period_seconds):
		# Available values: '1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D', '7D', '14D', '1M'
		m = 60
		h = 60*m
		d = 24*h
		periods = [
			(1*m,  '1m'),
			(5*m,  '5m'),
			(15*m, '15m'),
			(30*m, '30m'),
			(1*h,  '1h'),
			(3*h,  '3h'),
			(6*h,  '6h'),
			(12*h, '12h'),
			(1*d,  '1D'),
			(7*d,  '7D'),
			(14*d, '14D'),
			(None, '1M'),
		]
		for sec, code in periods:
			if not sec or sec >= period_seconds:
				return code

	def graph(self, market, period_seconds, resolution):
		period = self._convert_period(period_seconds / 100)
		start_ms = (time.time() - period_seconds) * 1000
		url = 'https://api.bitfinex.com/v2/candles/trade:{}:{}/hist?start={}&limit={}'.format(period, market, start_ms, resolution)
		resp = requests.get(url)
		data = resp.json()
		data = [{'time': e[0]/1000, 'open': e[1], 'close': e[2]} for e in data]
		data = sorted(data, key= lambda e: e['time'])
		return data

	def format_price(self, price, market):
		return '{:.2f} USD'.format(price)

class _ExchangeProviderFactory:

	def __init__(self):
		self.cache = {}

	def _create(self, id):
		if id == BitBayExchangeProvider.ID:
			return BitBayExchangeProvider()
		elif id == BitMarketExchangeProvider.ID:
			return BitMarketExchangeProvider()
		elif id == BitstampExchangeProvider.ID:
			return BitstampExchangeProvider()
		elif id == BitfinexExchangeProvider.ID:
			return BitfinexExchangeProvider()
		elif id == MockProvider.ID:
			return MockProvider()
		else:
			raise ValueError

	def get(self, id):
		if id not in self.cache:
			return self._create(id)
		return self.cache[id]

factory = _ExchangeProviderFactory()
