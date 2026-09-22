from .command import*

import omni.ext
import omni.anim.navigation.core as nav


class Extension(omni.ext.IExt):
    def __init__(self) -> None:
        super().__init__()

    def on_startup(self, ext_id):
        self._iface = nav.acquire_interface()

    def on_shutdown(self):
        nav.release_interface(self._iface)
