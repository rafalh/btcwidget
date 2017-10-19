from gi.repository import Gtk
import btcwidget.currency
import btcwidget.exchanges


def alarm_above_message(alarm, price):
    currency = alarm['market'][3:]
    provider = btcwidget.exchanges.factory.get(alarm['exchange'])
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Alarm: Price is ABOVE!")
    dialog.format_secondary_text(
        "Alarm! Current price ({}) is above defined threshold {} ({} - {})".format(
            btcwidget.currency.service.format_price(price, currency),
            btcwidget.currency.service.format_price(alarm['price'], currency),
            provider.get_name(), alarm['market']))
    dialog.run()
    dialog.destroy()


def alarm_below_message(alarm, price):
    currency = alarm['market'][3:]
    provider = btcwidget.exchanges.factory.get(alarm['exchange'])
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Alarm: Price is BELOW!")
    dialog.format_secondary_text(
        "Alarm! Current price ({}) is below defined threshold {} ({} - {})".format(
            btcwidget.currency.service.format_price(price, currency),
            btcwidget.currency.service.format_price(alarm['price'], currency),
            provider.get_name(), alarm['market']))
    dialog.run()
    dialog.destroy()
