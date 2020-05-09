#  Copyright 2020 Parakoopa
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
from typing import Iterable, Tuple, Optional

from gi.repository import GObject, GtkSource, Gtk

from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.ppmdu_config.script_data import *
from skytemple_files.script.ssb.constants import SsbConstant
from skytemple_ssb_debugger.model.completion.util import common_do_match, common_do_populate
from skytemple_ssb_debugger.model.constants import ICON_ACTOR, ICON_OBJECT, ICON_GLOBAL_SCRIPT


class GtkSourceCompletionSsbConstants(GObject.Object, GtkSource.CompletionProvider):
    def __init__(self, rom_data: Pmd2Data):
        super().__init__()
        self.all_constants = list(SsbConstant.collect_all(rom_data.script_data))

    def do_get_name(self) -> str:
        return "Constants"

    def do_get_priority(self) -> int:
        return 1

    def do_activate_proposal(self, proposal: GtkSource.CompletionProposal, textiter: Gtk.TextIter) -> bool:
        return False

    def do_get_activation(self) -> GtkSource.CompletionActivation:
        return GtkSource.CompletionActivation.INTERACTIVE | GtkSource.CompletionActivation.USER_REQUESTED

    # def do_get_info_widget(self, proposal: GtkSource.CompletionProposal) -> Gtk.Widget:
    #     pass

    # def do_update_info(self, proposal: GtkSource.CompletionProposal, info: GtkSource.CompletionInfo):
    #     pass

    def do_get_interactive_delay(self) -> int:
        return -1

    def do_get_gicon(self):
        return None

    def do_get_icon(self):
        return None

    def do_get_icon_name(self):
        return None

    def do_get_start_iter(self, context: GtkSource.CompletionContext, proposal: GtkSource.CompletionProposal) -> Tuple[bool, Optional[Gtk.TextIter]]:
        return False, None

    def do_match(self, context: GtkSource.CompletionContext) -> bool:
        return common_do_match(self._filter, self._all, context)

    def do_populate(self, context: GtkSource.CompletionContext):
        return common_do_populate(self, self._filter, self._all, context)

    def _all(self) -> Iterable[GtkSource.CompletionProposal]:
        return [self._build_item(s) for s in self.all_constants]

    def _filter(self, cond: str) -> Iterable[GtkSource.CompletionProposal]:
        return [self._build_item(s) for s in self.all_constants if s.name.startswith(cond)]

    def _build_item(self, const: SsbConstant) -> GtkSource.CompletionItem:
        item: GtkSource.CompletionItem = GtkSource.CompletionItem.new()
        item.set_text(const.name)
        item.set_label(const.name)

        if isinstance(const.value, Pmd2ScriptEntity):
            item.set_icon_name(ICON_ACTOR)
        elif isinstance(const.value, Pmd2ScriptObject):
            item.set_icon_name(ICON_OBJECT)
        elif isinstance(const.value, Pmd2ScriptRoutine):
            item.set_icon_name(ICON_GLOBAL_SCRIPT)
        elif isinstance(const.value, Pmd2ScriptFaceName):
            item.set_icon_name('face-smile-symbolic')
        elif isinstance(const.value, Pmd2ScriptFacePositionMode):
            item.set_icon_name('object-flip-horizontal')
        elif isinstance(const.value, Pmd2ScriptGameVar):
            item.set_icon_name('view-pin-symbolic')
        elif isinstance(const.value, Pmd2ScriptLevel):
            item.set_icon_name('image-x-generic-symbolic')
        elif isinstance(const.value, Pmd2ScriptMenu):
            item.set_icon_name('open-menu-symbolic')
        elif isinstance(const.value, Pmd2ScriptSpecial):
            item.set_icon_name('starred-symbolic')
        elif isinstance(const.value, Pmd2ScriptDirection):
            item.set_icon_name('media-playlist-consecutive-symbolic')
        
        return item