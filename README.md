BTC Widget
==========

Introduction
------------

![Preview](screenshots/main_win.png?raw=true)

BTC Widget is simple Python application for checking Bitcoin price on multiple exchanges.
It currently supports following exchanges:

* Bitfinex.com (BTCUSD)
* Bitstamp.net (BTCUSD)
* BitMarket.pl (BTCPLN)
* BitBay.net (BTCPLN)

Application consist of Appindicator displaying current price in Tray area and window showing chart from last 24 hours.

Application was developed with Linux in mind but should work on any system with GTK and Python installed.
Tested it only on Ubuntu 16.04 (Unity) and Linux Mint 18 (Cinnamon).

Usage
-----
Install dependencies first:

	sudo apt-get install python3 python3-gi python3-matplotlib


If you are getting error related to lack of indicator:

    Namespace AppIndicator3 not available

You must install following library by running this command:

    apt-get install gir1.2-appindicator3-0.1

This error will probably appear for environments without AppIndicator available (Gnome Shell)

Additionally for gnome shell you must install and enable following extension allowing to add AppIndicators:

    KStatusNotifierItem/AppIndicator Support


Then you can run the application:

	btcwidget/main.py

If you want to run it in background:

	nohup btcwidget/main.py &

Notice
------
Use BTC Widget at your own risk.
I'm not responsible of any loss of money resulting from using this application.

License
-------
The MIT license. See LICENSE.txt.
