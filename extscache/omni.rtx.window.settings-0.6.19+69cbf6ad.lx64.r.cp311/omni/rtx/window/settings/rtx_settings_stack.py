__all__ = ["RTXSettingsStack"]

import omni.ui as ui
from omni.rtx.window.settings.settings_collection_frame import SettingsCollectionFrame


class RTXSettingsStack:
    """define a stack of Settings Widgets"""

    def __init__(self) -> None:
        self._stack: ui.VStack = None

    def set_visible(self, value: bool):
        if self._stack:
            self._stack.visible = value

    def get_visible(self) -> bool:
        if self._stack:
            return self._stack.visible
        return False

    def destroy(self):
        if self in SettingsCollectionFrame.parents:
            mySettingsFrames = SettingsCollectionFrame.parents[self]
            for frame in mySettingsFrames:
                frame.destroy()
            del SettingsCollectionFrame.parents[self]
