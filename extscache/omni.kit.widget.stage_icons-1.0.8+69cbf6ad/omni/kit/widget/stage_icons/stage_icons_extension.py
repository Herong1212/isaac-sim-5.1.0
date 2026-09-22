# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module defines the StageIconsExtension class to manage icon registration for primitives in the stage window."""

__all__ = []

from pathlib import Path
import carb.settings
import omni.ext


class StageIconsExtension(omni.ext.IExt):
    """This class extension adds icons for some primitive types in the state window."""

    _icons_registered = None

    @staticmethod
    def get_registered_icons():
        """Returns the list of registered icons.

        Returns:
            list: The list of registered icons or None if no icons have been registered."""
        return StageIconsExtension._icons_registered

    def register_icons(self):
        """Registers icons based on the SVG files found in the icons directory."""
        StageIconsExtension._icons_registered = []

        import omni.kit.widget.stage

        stage_icons = omni.kit.widget.stage.StageIcons()

        current_path = Path(__file__).parent
        icon_path = current_path.parent.parent.parent.parent.joinpath("icons")

        style = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"

        # Read all the svg files in the directory
        icons = {icon.stem: str(icon) for icon in icon_path.joinpath(style).glob("*.svg")}
        for prim_type, filename in icons.items():
            stage_icons.set(prim_type, filename)
            StageIconsExtension._icons_registered.append(prim_type)

    def on_startup(self, ext_id):
        """Extension startup callback function. This is called automatically when the Python side of this extension loads."""
        StageIconsExtension._icons_registered = None
        manager = omni.kit.app.get_app().get_extension_manager()
        self._hook = manager.subscribe_to_extension_enable(
            on_enable_fn=lambda _: self.register_icons(),
            ext_name="omni.kit.widget.stage",
            hook_name="omni.kit.widget.stage_icons",
        )

    def on_shutdown(self):
        """Extension shutdown callback function. This is called automatically when the Python side of this extension unloads."""
        self._hook = None
        if StageIconsExtension._icons_registered:
            try:
                import omni.kit.widget.stage
            except ImportError as e:
                return

            stage_icons = omni.kit.widget.stage.StageIcons()
            for prim_type in StageIconsExtension._icons_registered:
                stage_icons.set(prim_type, None)
