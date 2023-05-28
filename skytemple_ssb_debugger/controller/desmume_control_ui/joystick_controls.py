#  Copyright 2020-2022 Capypara and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import annotations
import os
from typing import Optional, List, Callable

from gi.repository import Gtk, Gdk
from skytemple_files.common.i18n_util import _
from skytemple_ssb_emulator import emulator_get_joy_number_connected, emulator_get_key_names, EmulatorKeys, \
    emulator_joy_get_set_key

from skytemple_ssb_debugger.controller.desmume_control_ui import widget_to_primitive, key_names_localized


class JoystickControlsDialogController:
    """This dialog shows the joystick controls."""
    def __init__(self, parent_window: Gtk.Window):
        path = os.path.abspath(os.path.dirname(__file__))
        # SkyTemple translation support
        try:
            from skytemple.core.ui_utils import make_builder
            self.builder = make_builder(os.path.join(path, "PyDeSmuMe_controls.glade"))
        except ImportError:
            self.builder = Gtk.Builder()
            self.builder.add_from_file(os.path.join(path, "PyDeSmuMe_controls.glade"))
        self.window: Gtk.Window = self.builder.get_object('wJoyConfDlg')
        self.window.set_transient_for(parent_window)
        self.window.set_attached_to(parent_window)
        self._joystick_cfg: Optional[List[int]] = None
        self.builder.connect_signals(self)

    def run(self,
            joystick_cfg: List[int],
            emulator_is_running: bool,
            callback: Callable[[List[int]], None]
        ):
        """Configure the joystick configuration provided using the dialog,
        is immediately changed in the debugger The new/old (if canceled) config is also returned."""
        def do_run(joy_number_connected):
            self._joystick_cfg = joystick_cfg
            if joy_number_connected < 1 or emulator_is_running:
                if joy_number_connected < 1:
                    text = _("You don't have any joypads!")
                else:
                    text = _("Can't configure joystick while the game is running!")

                md = Gtk.MessageDialog(None,
                                       Gtk.DialogFlags.DESTROY_WITH_PARENT | Gtk.DialogFlags.MODAL,
                                       Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.OK, text,
                                       title="Error!")
                md.set_position(Gtk.WindowPosition.CENTER)
                md.run()
                md.destroy()
            else:
                key_names = emulator_get_key_names()
                for i in range(0, EmulatorKeys.NB_KEYS):
                    b = self.builder.get_object(f"button_joy_{key_names[i]}")
                    b.set_label(f"{key_names_localized[i]} : {self._joystick_cfg[i]}")
                self.window.run()
                self.window.hide()

            callback(self._joystick_cfg)

        emulator_get_joy_number_connected(do_run)

    # KEYBOARD CONFIG / KEY DEFINITION
    def on_wKeyDlg_key_press_event(self, widget: Gtk.Widget, event: Gdk.EventKey, *args):
        pass  # not part of this

    def on_button_kb_key_clicked(self, w, *args):
        pass  # not part of this

    # Joystick configuration / Key definition
    def on_button_joy_key_clicked(self, w, *args):
        key = widget_to_primitive(w)
        dlg = self.builder.get_object("wJoyDlg")
        key -= 1  # key = bit position, start with
        dlg.show_now()
        # Need to force event processing. Otherwise, popup won't show up.
        while Gtk.events_pending():
            Gtk.main_iteration()

        joykey = emulator_joy_get_set_key(key)

        self._joystick_cfg[key] = joykey  # type: ignore

        self.builder.get_object(f"button_joy_{emulator_get_key_names()[key]}").set_label(f"{key_names_localized[key]} : {joykey}")

        dlg.hide()

    def gtk_widget_hide_on_delete(self, w: Gtk.Widget, *args):
        w.hide_on_delete()
        return True