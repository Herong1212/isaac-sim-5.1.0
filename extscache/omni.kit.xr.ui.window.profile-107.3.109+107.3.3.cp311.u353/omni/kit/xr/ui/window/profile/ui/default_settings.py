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

import carb.dictionary
import carb.settings


class XRSettingsDefaults:
    """
    Get default for XR settings
    """

    _settings = carb.settings.get_settings()
    _settings_dict = _settings.get_settings_dictionary("")

    @classmethod
    def _get_associated_defaults_path(cls, settings_path: str) -> str:
        if settings_path.startswith("/persistent"):
            return "/defaults" + settings_path[11:]
        return "/defaults" + settings_path

    def reset_setting_to_default(self, settings_path: str):
        defaultsPathStorage = self._get_associated_defaults_path(settings_path)
        defaultValue = self._settings.get(defaultsPathStorage)
        self._settings.set(settings_path, defaultValue)
