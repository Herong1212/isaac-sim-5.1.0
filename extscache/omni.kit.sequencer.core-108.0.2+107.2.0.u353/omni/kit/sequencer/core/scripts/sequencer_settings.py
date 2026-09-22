import sys

import carb
import carb.settings

SNAP_TO_FRAME_KEY = "/persistent/exts/omni.kit.window.sequencer/snapToFrame"
USE_SEQUENCER_CAMERA = "/persistent/exts/omni.kit.window.sequencer/useSequencerCamera"

g_settings = carb.settings.get_settings()


def _get_setting(key: str, default_value):
    value = g_settings.get(key)
    if value is None:
        return default_value
    return value


class SequencerSettings:
    @property
    def snap_to_frame(self):
        return _get_setting(SNAP_TO_FRAME_KEY, True)

    @snap_to_frame.setter
    def snap_to_frame(self, value):
        g_settings.set(SNAP_TO_FRAME_KEY, value)

    @property
    def use_sequencer_camera(self):
        return _get_setting(USE_SEQUENCER_CAMERA, True)

    @use_sequencer_camera.setter
    def use_sequencer_camera(self, value=True):
        g_settings.set(USE_SEQUENCER_CAMERA, value)


# @property's cannot be implemented on modules - this is the way:
# https://stackoverflow.com/a/7668273/1955656

sys.modules[__name__] = SequencerSettings()
