import sys

from gi.repository import Gtk

import btcwidget.currency
import btcwidget.exchanges
from btcwidget.config import config


def _add_label_and_widget(parent, label_text, widget):
    hbox = Gtk.Box(spacing=6)
    label = Gtk.Label(label_text)
    hbox.pack_start(label, False, False, 0)
    hbox.pack_start(widget, True, True, 0)
    parent.add(hbox)

def _int_or_default(text, default=None):
    try:
        return int(text)
    except ValueError as e:
        print(e, file=sys.stderr)
        return default


class AlarmDialog(Gtk.Dialog):
    _EXCHANGE_COL = 0
    _MARKET_COL = 1
    _TRIGGER_COL = 2
    _DATA_COL = 3

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Alarms", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self._store = Gtk.ListStore(str, str, str, object)
        for i, alarm in enumerate(config['alarms']):
            row = self._build_row(alarm)
            self._store.append(row)

        self._tree = Gtk.TreeView(self._store)
        self._selection = self._tree.get_selection()
        self._selection.connect("changed", self._on_tree_selection_changed)
        self._tree.set_size_request(300, 150)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Exchange", renderer, text=self._EXCHANGE_COL)
        self._tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Market", renderer, text=self._MARKET_COL)
        self._tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Alarm Trigger", renderer, text=self._TRIGGER_COL)
        self._tree.append_column(column)

        vbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)

        new_button = Gtk.Button.new_with_label("New Alarm")
        new_button.connect("clicked", self._on_new_button_clicked)
        vbox.pack_start(new_button, False, False, 0)

        self._remove_button = Gtk.Button.new_with_label("Remove Alarm")
        self._remove_button.connect("clicked", self._on_remove_button_clicked)
        vbox.pack_start(self._remove_button, False, False, 0)

        self._market_combo, self._market_store = self._create_market_combo()
        self._market_combo.connect("changed", self._on_market_changed)
        vbox.pack_start(self._market_combo, False, False, 0)

        self._above_radio = Gtk.RadioButton.new_with_label_from_widget(None, "Above")
        self._above_radio.connect("clicked", self._on_type_radio_clicked)
        self._below_radio = Gtk.RadioButton.new_with_label_from_widget(self._above_radio, "Below")
        self._below_radio.connect("clicked", self._on_type_radio_clicked)
        type_hbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        type_hbox.pack_start(self._above_radio, True, True, 0)
        type_hbox.pack_start(self._below_radio, True, True, 0)
        vbox.pack_start(type_hbox, False, False, 0)

        self._price_entry = Gtk.Entry()
        self._price_entry.connect("changed", self._on_price_changed)
        _add_label_and_widget(vbox, "Price:", self._price_entry)

        hbox = Gtk.Box(spacing=6)
        hbox.pack_start(self._tree, True, True, 0)
        hbox.pack_start(vbox, False, False, 0)

        self.get_content_area().add(hbox)
        self._set_inputs_sensitive(False)
        self.show_all()

    def _build_row(self, alarm):
        alarm = alarm.copy()
        provider = btcwidget.exchanges.factory.get(alarm['exchange']) if alarm['exchange'] else None
        currency = alarm['market'][3:] if alarm['market'] else 'USD'
        price_str = btcwidget.currency.service.format_price(alarm['price'], currency) if alarm['price'] else '?'
        if alarm['type'] == 'B':
            trigger = 'Below {}'.format(price_str)
        else:
            trigger = 'Above {}'.format(price_str)
        exchange_name = provider.get_name() if provider else '?'
        market_name = alarm['market'] if alarm['market'] else '?'
        return [exchange_name, market_name, trigger, alarm]

    def _set_inputs_sensitive(self, sensitive):
        self._market_combo.set_sensitive(sensitive)
        self._above_radio.set_sensitive(sensitive)
        self._below_radio.set_sensitive(sensitive)
        self._price_entry.set_sensitive(sensitive)
        self._remove_button.set_sensitive(sensitive)

    def _on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter:
            row = model[treeiter]
            alarm = row[self._DATA_COL]
            self._select_market(alarm['exchange'], alarm['market'])
            self._above_radio.set_active(alarm['type'] == 'A')
            self._below_radio.set_active(alarm['type'] == 'B')
            self._price_entry.set_text(str(alarm['price']) if alarm['price'] else '')
            sensitive = True
        else:
            sensitive = False
        self._set_inputs_sensitive(sensitive)

    def _on_new_button_clicked(self, widget):
        alarm = {
            'exchange': None,
            'market': None,
            'type': 'A',
            'price': None,
        }
        treeiter = self._store.append(self._build_row(alarm))
        self._tree.get_selection().select_iter(treeiter)

    def _on_remove_button_clicked(self, widget):
        model, treeiter = self._selection.get_selected()
        if treeiter:
            self._store.remove(treeiter)

    def _on_market_changed(self, widget):
        model, treeiter = self._selection.get_selected()
        if treeiter:
            alarm = model[treeiter][self._DATA_COL]
            iter = widget.get_active_iter()
            if iter:
                row = self._market_store[iter]
                alarm['exchange'], alarm['market'] = row[1], row[2]
                model[treeiter] = self._build_row(alarm)

    def _on_type_radio_clicked(self, widget):
        model, treeiter = self._selection.get_selected()
        if treeiter:
            alarm = model[treeiter][self._DATA_COL]
            alarm['type'] = 'A' if self._above_radio.get_active() else 'B'
            model[treeiter] = self._build_row(alarm)

    def _on_price_changed(self, widget):
        model, treeiter = self._selection.get_selected()
        if treeiter:
            alarm = model[treeiter][self._DATA_COL]
            text = widget.get_text()
            alarm['price'] = _int_or_default(text) if text != '' else None
            model[treeiter] = self._build_row(alarm)

    def _create_market_combo(self):
        store = Gtk.ListStore(str, str, str)
        for market_config in config['markets']:
            provider = btcwidget.exchanges.factory.get(market_config['exchange'])
            market_name = '{} - {}'.format(provider.get_name(), market_config['market'])
            store.append([market_name, market_config['exchange'], market_config['market']])
        combo = Gtk.ComboBox.new_with_model(store)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, "text", 0)
        return combo, store

    def _select_market(self, exchange, market):
        iter = self._market_store.get_iter_first()
        while iter:
            row = self._market_store[iter]
            if row[1] == exchange and row[2] == market:
                self._market_combo.set_active_iter(iter)
                return
            iter = self._market_store.iter_next(iter)
        self._market_combo.set_active(-1)

    def update_config(self):
        alarms = []
        for row in self._store:
            alarm = row[self._DATA_COL]
            if alarm['exchange'] and alarm['market'] and alarm['price']:
                alarms.append(alarm)
        config['alarms'] = alarms
        config.save()


def open_alarm_dialog(parent=None):
    dialog = AlarmDialog(parent)
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        dialog.update_config()
    dialog.destroy()
