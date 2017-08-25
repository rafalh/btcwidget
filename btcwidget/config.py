import btcwidget.exchanges

_MOCK = False
_USD_PLN = 3.61104691 # 25.08.2017

class Config:
	if _MOCK:
		markets = [
			{
				'provider': btcwidget.exchanges.factory.get('mock'),
				'market': 'BTCUSD',
				'graph': True,
				'wnd_title': True,
			},
		]
	else:
		markets = [
			{
				'provider': btcwidget.exchanges.factory.get('bitstamp.net'),
				'market': 'BTCUSD',
				'ticker': True,
				'graph': True,
				'wnd_title': False,
				'graph_price_mult': _USD_PLN,
			},
			{
				'provider': btcwidget.exchanges.factory.get('bitmarket.pl'),
				'market': 'BTCPLN',
				'ticker': True,
				'graph': True,
				'wnd_title': True,
			},
			{
				'provider': btcwidget.exchanges.factory.get('bitbay.net'),
				'market': 'BTCPLN',
				'ticker': True,
				'graph': False,
				'wnd_title': False,
			},
			{
				'provider': btcwidget.exchanges.factory.get('bitfinex.com'),
				'market': 'tBTCUSD',
				'ticker': True,
				'graph': True,
				'wnd_title': False,
				'graph_price_mult': _USD_PLN,
			},
		]
	update_interval_sec = 10 if not _MOCK else 1
	graph_interval_sec = 5*60 if not _MOCK else 10
	# show last 60 minutes
	graph_period_sec = 60*60
	graph_res = 200
	# time axis in minutes
	time_axis_div = 1
	dark_theme = False

	_callbacks = []

	def register_change_callback(func):
		Config._callbacks.append(func)

	def run_change_callbacks():
		for func in Config._callbacks:
			func()
