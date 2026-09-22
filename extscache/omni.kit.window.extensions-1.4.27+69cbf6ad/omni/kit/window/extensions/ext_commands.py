# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module defines a command for enabling or disabling extensions in the omni.kit application."""

__all__ = ["ToggleExtension"]

import omni.kit.app
import omni.kit.commands


class ToggleExtension(omni.kit.commands.Command):
    """Toggle extension **Command**.  Enables/disables an extension.

    Args:
        ext_id (str): Extension id.
        enable (bool): Enable or disable."""

    def __init__(self, ext_id: str, enable: bool):
        """Initializes the command to toggle an extension's enabled state."""
        self._ext_id = ext_id
        self._enable = enable
        self._ext_manager = omni.kit.app.get_app().get_extension_manager()

    def do(self):
        """Executes the command to enable or disable the specified extension."""
        manager = omni.kit.app.get_app().get_extension_manager()
        manager.set_extension_enabled_immediate(self._ext_id, self._enable)
        omni.kit.app.send_telemetry_event(
            "omni.kit.window.extensions@enable_ext", data1=self._ext_id, value1=float(self._enable)
        )
