# Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
Support required by the Carbonite extension loader
"""
import omni.ext

from .widgets.timesample_editor import TimeSampleEditor
from .widgets.timesample_properties_widget import TimeSamplePropertiesWidget

# Any class derived from `omni.ext.IExt` in a top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when the extension is enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() will be called.


class PublicExtension(omni.ext.IExt):
    """Object that tracks the lifetime of the Python part of the extension loading"""

    def on_startup(self):

        try:
            import omni.kit.window.property as p
        except ImportError:
            # Likely running headless
            return

        w = p.get_window()
        if not w:
            return

        # self._shader_timesample_widget = TimeSamplePropertiesWidget("Shader", ["inputs:volume_density_texture"])

        import omni.kit.context_menu
        from omni.kit.property.usd.usd_attribute_model import SdfAssetPathAttributeModel

        def is_asset(object: dict = None) -> bool:
            if not object:
                return
            return isinstance(object["model"], SdfAssetPathAttributeModel)

        def show_editor(object):
            editor = TimeSampleEditor()
            editor.show(object["attribute_paths"][0])

        self._context_menu = omni.kit.context_menu.add_menu(
            {
                "name": "Edit Time Samples",
                "show_fn": is_asset,
                "onclick_fn": show_editor,
            },
            "attribute",
            "omni.kit.property.usd",
        )

    def on_shutdown(self):

        editor = TimeSampleEditor()
        editor.destroy()

        try:
            import omni.kit.window.property as p
        except ImportError:
            # Likely running headless
            return

        w = p.get_window()
        if not w:
            return

        # self._shader_timesample_widget.on_shutdown()
        # self._shader_timesample_widget = None

        self._context_menu = None
