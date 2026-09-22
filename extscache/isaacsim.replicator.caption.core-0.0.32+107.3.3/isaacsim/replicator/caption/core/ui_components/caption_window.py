import omni.kit.app
import omni.ui as ui

from .data_collection_panel import DataCollectionPanel
from omni.kit.menu.utils import MenuHelperWindow
from ..settings import ReplicatorCaptionSettings

_extension_instance = None
_ext_id = None
_ext_path = None


def get_instance():
    return _extension_instance


def get_ext_id():
    return _ext_id


def get_ext_path():
    return _ext_path


class CaptionWindow(MenuHelperWindow):
    def __init__(self, ext_id):
        super().__init__(title="VLM Scene Captioning", width=300, height=600, dockPreference=ui.DockPreference.RIGHT)
        # this step is used to handle the warp issue in the recent version.
        # would be removed later.
        import warp

        warp.init()

        # Set instance
        global _extension_instance
        _extension_instance = self
        global _ext_id
        _ext_id = ext_id
        global _ext_path
        _ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id)
        ReplicatorCaptionSettings.EXT_PATH = get_ext_path()

        self.frame.set_build_fn(self._build_ui)

    def destroy(self):
        self._data_collection_panel = None

    def _build_ui(self):
        self.deferred_dock_in("Stage", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.dock_order = 5
        with self.frame:
            with ui.ScrollingFrame():
                with ui.VStack(spacing=0, height=0):
                    self._data_collection_panel = DataCollectionPanel()
