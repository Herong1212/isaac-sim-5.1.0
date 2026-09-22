# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ToolbarPlayButtonClickedCommand", "ToolbarPauseButtonClickedCommand",
           "ToolbarStopButtonClickedCommand", "ToolbarPlayFilterCheckedCommand", "ToolbarPlayFilterSelectAllCommand"]

import omni.kit.commands
import omni.timeline


class ToolbarPlayButtonClickedCommand(omni.kit.commands.Command):
    """
    On clicked toolbar play button **Command**.
    """

    def do(self):
        omni.timeline.get_timeline_interface().play()


class ToolbarPauseButtonClickedCommand(omni.kit.commands.Command):
    """
    On clicked toolbar pause button **Command**.
    """

    def do(self):
        omni.timeline.get_timeline_interface().pause()


class ToolbarStopButtonClickedCommand(omni.kit.commands.Command):
    """
    On clicked toolbar stop button **Command**.
    """

    def do(self):
        omni.timeline.get_timeline_interface().stop()


class ToolbarPlayFilterCheckedCommand(omni.kit.commands.Command):
    """
    Change settings depending on the status of play filter checkboxes **Command**.

    Args:
        path: Path to the setting to change.
        enabled: New value to change to.
    """

    def __init__(self, setting_path, enabled):
        self._setting_path = setting_path
        self._enabled = enabled

    def do(self):
        omni.kit.commands.execute("ChangeSetting", path=self._setting_path, value=self._enabled)

    def undo(self):
        pass


class ToolbarPlayFilterSelectAllCommand(omni.kit.commands.Command):
    """
    Sets all play filter settings to True **Command**.

    Args:
        settings: Paths to the settings.
    """

    def __init__(self, settings):
        self._settings = settings

    def do(self):
        for setting in self._settings:
            omni.kit.commands.execute("ChangeSetting", path=setting, value=True)

    def undo(self):
        pass


omni.kit.commands.register_all_commands_in_module(__name__)
