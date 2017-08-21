import requests, json
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

	def get_name(self):
		return 'Bitstamp.net'

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
		print('getting transactions for {}'.format(time))
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

	def get_name(self):
		return 'BitBay.net'

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
	
	def get_name(self):
		return 'BitMarket.pl'

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
