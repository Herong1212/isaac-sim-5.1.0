import omni.ext
from omni.kit.window.preferences import register_page, unregister_page

from .preference_page import ThumbnailPage


class ThunbnailGenerationExtension(omni.ext.IExt):
    def __init__(self):
        self._preference_page = None
        super().__init__()

    def on_startup(self, ext_id):
        self._preference_page = ThumbnailPage()
        register_page(self._preference_page)

    def on_shutdown(self):
        unregister_page(self._preference_page)
