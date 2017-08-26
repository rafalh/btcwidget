#!/usr/bin/env python3
import gi, signal
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk
from btcwidget.mainwindow import MainWindow
from btcwidget.logic import UpdateThread
from btcwidget.config import config

def main():
	config.load()
	GObject.threads_init()
	main_win = MainWindow()
	thread = UpdateThread(main_win)
	thread.start()
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	Gtk.main()

if __name__ == '__main__':
	main()
