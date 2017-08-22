BTC Widget
==========

Introduction
------------
BTC Widget is simple Python application for checking Bitcoin value on multiple exchanges.
It is very simple now and supports following exchanges:

* BitMarket.pl
* BitBay.net
* Bitstamp.net

Application consist of Appindicator displaying current value in Tray area and window showing graph of value from last 24 hours.

Usage
-----
Install dependencies first:

	sudo apt-get install python3 python3-gi python3-matplotlib

Then you can run application:

	bitgui/main.py

If you want to run it in background:

	nohup bitgui/main.py &

Notice
------
Use BTC Widget at your own risk.
I'm not responsible of any loss of money resulting from using this application.

License
-------
The MIT license. See LICENSE.txt.
