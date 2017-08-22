BTC Widget
==========

Introduction
------------
BTC Widget is simple Python application for checking Bitcoin price on multiple exchanges.
It is very simple now and supports following exchanges:

* BitMarket.pl
* BitBay.net
* Bitstamp.net

Application consist of Appindicator displaying current value in Tray area and window showing chart from last 24 hours.

Application was developed with Linux in mind but should work on any system with GTK and Python installed.
Tested it only on Ubuntu 16.04 (Unity) and Linux Mint 18 (Cinnamon).

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
