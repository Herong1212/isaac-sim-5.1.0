import omni.ext

from .play_manager import PlayManager

_g_instance = None


def get_play_manager() -> PlayManager:
    if _g_instance:
        return _g_instance._play_manager
    else:
        return None


class PlaylistCoreExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._play_manager = PlayManager()

        global _g_instance
        _g_instance = self

    def on_shutdown(self):
        global _g_instance
        _g_instance = None

        self._play_manager.destroy()
        self._play_manager = None
