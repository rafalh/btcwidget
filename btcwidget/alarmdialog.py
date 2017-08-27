from gi.repository import Gtk

import btcwidget.currency
import btcwidget.exchanges
from btcwidget.config import config


class AlarmDialog(Gtk.Dialog):

    def _create_currency_combo(self, active):
        combo = Gtk.ComboBoxText()
        combo.set_entry_text_column(0)
        currencies = sorted(btcwidget.currency.service.list())
        for i, currency in enumerate(currencies):
            combo.append_text(currency)
            if currency == active:
                combo.set_active(i)
        return combo

    def _add_label_and_widget(self, label_text, widget):
        hbox = Gtk.Box(spacing=6)
        label = Gtk.Label(label_text)
        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(widget, True, True, 0)
        self.get_content_area().add(hbox)

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Alarm", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self._currency_combo = self._create_currency_combo(config['alarm_currency'])
        self._add_label_and_widget('Alarm Currency:', self._currency_combo)

        self._alarm_above_entry = Gtk.Entry(text=str(config['alarm_above'] or ''))
        self._add_label_and_widget('Alarm (above price):', self._alarm_above_entry)

        self._alarm_below_entry = Gtk.Entry(text=str(config['alarm_below'] or ''))
        self._add_label_and_widget('Alarm (below price):', self._alarm_below_entry)

        self.show_all()

    def update_config(self):
        try:
            config['alarm_currency'] = self._currency_combo.get_active_text()
            alarm_above = self._alarm_above_entry.get_text()
            config['alarm_above'] = int(alarm_above) if alarm_above != '' else None
            alarm_below = self._alarm_below_entry.get_text()
            config['alarm_below'] = int(alarm_below) if alarm_below != '' else None

        except ValueError as e:
            print(e)  # ignore errors

        config.save()
