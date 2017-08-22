import btcwidget.exchanges

_MOCK = True

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
			# {
			# 	'provider': btcwidget.exchanges.factory.get('bitstamp.net'),
			# 	'market': 'BTCUSD',
			# 	'graph': False,
			# 	'wnd_title': False,
			# },
			{
				'provider': btcwidget.exchanges.factory.get('bitmarket.pl'),
				'market': 'BTCPLN',
				'graph': True,
				'wnd_title': False,
			},
			{
				'provider': btcwidget.exchanges.factory.get('bitbay.net'),
				'market': 'BTCPLN',
				'graph': True,
				'wnd_title': True,
			},
		]
	update_interval_sec = 10 if not _MOCK else 1
	graph_interval_sec = 5*60 if not _MOCK else 10
	# show last 10 minutes
	graph_period_sec = 10*60
	graph_res = 200
	# time axis in minutes
	time_axis_div = 1
