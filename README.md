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
* LakeBTC.com (BTCUSD)

Application consist of AppIndicator displaying current price in Tray area and main window showing chart from last hour.

Application was developed with Linux in mind but should work on any system with GTK and Python installed.
It was tested Ubuntu 16.04 (Unity), Linux Mint 18 (Cinnamon) and Debian (GNOME Shell).

Usage
-----
Install dependencies first. On Debian-based distributions you can do it with command:

	sudo apt-get install python3 python3-gi python3-matplotlib gir1.2-appindicator3-0.1

On GNOME Shell you should also install and enable extension "KStatusNotifierItem/AppIndicator Support" to get indicator working.

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
