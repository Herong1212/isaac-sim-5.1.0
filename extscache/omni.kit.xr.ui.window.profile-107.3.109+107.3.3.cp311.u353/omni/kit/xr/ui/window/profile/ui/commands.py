# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import carb
import carb.dictionary
import carb.settings
import omni.kit.commands

from .default_settings import XRSettingsDefaults


class RestoreDefaultXRSettingCommand(omni.kit.commands.Command):
    """
    Restore default setting

    Args:
        path: Path to the setting to be reset.
    """

    def __init__(self, path: str):
        super().__init__()

        self._path = path
        self._settings = carb.settings.get_settings()

    def do(self):
        self._value = self._settings.get(self._path)
        XRSettingsDefaults().reset_setting_to_default(self._path)

    def undo(self):
        self._settings.set(self._path, self._value)


omni.kit.commands.register_all_commands_in_module(__name__)
