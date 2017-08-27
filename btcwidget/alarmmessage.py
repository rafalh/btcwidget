from gi.repository import Gtk
import btcwidget.currency


def alarm_above_message(current_price, alarm_price, currency):
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Price is ABOVE!")
    dialog.format_secondary_text(
        "Alarm! Price is above specified value: {} >= {}".format(
            btcwidget.currency.service.format_price(current_price, currency),
            btcwidget.currency.service.format_price(alarm_price, currency)))
    dialog.run()
    dialog.destroy()


def alarm_below_message(current_price, alarm_price, currency):
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Price is BELOW!")
    dialog.format_secondary_text(
        "Alarm! Price is below specified value: {} <= {}".format(
            btcwidget.currency.service.format_price(current_price, currency),
            btcwidget.currency.service.format_price(alarm_price, currency)))
    dialog.run()
    dialog.destroy()
