import omni.ext

from .sequence_player import _Player, g_sequence_player
from .usd_sequencer import *


class SequencerUsdExtension(omni.ext.IExt):
    def on_startup(self):
        self._player: _Player = g_sequence_player
        self._player.on_startup()

    def on_shutdown(self):
        self._player.on_shutdown()
        self._player = None
