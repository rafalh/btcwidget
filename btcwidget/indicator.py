import gi
import os

from definitions import ROOT_DIR

gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3


class Indicator:
    APPINDICATOR_ID = 'btc-indicator'
    _ICON_PATH = os.path.join(ROOT_DIR, 'icon.png')
    _CATEGORY = AppIndicator3.IndicatorCategory.APPLICATION_STATUS

    def __init__(self, main_win):
        self._main_win = main_win

        menu = self._create_menu()
        self._indicator = AppIndicator3.Indicator.new(self.APPINDICATOR_ID, self._ICON_PATH, self._CATEGORY)
        self._indicator.set_title("Bitcoin Indicator")
        self._indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self._indicator.set_menu(menu)

    def _create_menu(self):
        menu = Gtk.Menu()

        self._menu_item = Gtk.MenuItem("Bitcoin")
        self._menu_item.connect('activate', self._on_show_item_activate)
        menu.append(self._menu_item)

        options_menu_item = Gtk.MenuItem("Options...")
        options_menu_item.connect('activate', self._on_options_item_activate)
        menu.append(options_menu_item)

        quit_menu_item = Gtk.MenuItem("Quit")
        quit_menu_item.connect('activate', Gtk.main_quit)
        menu.append(quit_menu_item)

        menu.show_all()
        return menu

    def set_current_price(self, price_str):
        self._indicator.set_label(price_str, '20px')
        self._menu_item.set_label(price_str)

    def _on_show_item_activate(self, widget):
        self._main_win.present()

    def _on_options_item_activate(self, widget):
        self._main_win.open_options()
