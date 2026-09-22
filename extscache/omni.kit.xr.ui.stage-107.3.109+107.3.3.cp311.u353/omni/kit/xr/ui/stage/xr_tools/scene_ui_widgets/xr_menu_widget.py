# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import List

import carb
import omni.ui
from omni.kit.xr.core import XRProfile
from omni.kit.xr.ui.window.profile import (
    XRMenuAdvancedFrame,
    XRMenuOutputFrame,
    XRMenuSystemInfo,
    XRSettingsFrame,
    XRSettingsStack,
)


class XRMenuWidget(omni.ui.Widget):
    # Don't display these types in the panel.
    FILTER_FRAME_TYPES: List[XRSettingsFrame] = [
        XRMenuSystemInfo,
        XRMenuOutputFrame,
    ]

    def __init__(self, profile: XRProfile, **kwargs):
        super().__init__(**kwargs)

        # Replicate the profile settings window, except filtering out some options.
        component_types = None
        icons = None
        config = profile.get_config()

        if "profile_settings_window" in config:
            settings_data = config["profile_settings_window"]
            if "component_list" in settings_data:
                component_types = settings_data["component_list"]

            if "icons" in settings_data:
                icons = settings_data["icons"]

        if component_types:
            # Don't display these types on any panels.
            filtered_settings = [profile.get_persistent_path() + "system/display"]

            # Note here that these CAN be tuples, but not necessarily.
            # If it is a tuple, the 0 index is the type.
            # The first index is a dictionary of parameters to instantiate the type with.
            def filter_component_type(component) -> bool:
                if isinstance(component, tuple):
                    return component[0] in XRMenuWidget.FILTER_FRAME_TYPES
                else:
                    return component in XRMenuWidget.FILTER_FRAME_TYPES

            filtered_comps = []
            for comp in component_types:
                if filter_component_type(comp):
                    continue

                if isinstance(comp, tuple):
                    comp[1].update({"filtered_settings": filtered_settings})
                else:
                    comp = (comp, {"filtered_settings": filtered_settings})

                if comp[0] is XRMenuAdvancedFrame:
                    # Remove the filtered types from the params that will be used for instantiated the XRMenuAdvancedFrame.
                    if "components" in comp[1]:
                        for filter_type in XRMenuWidget.FILTER_FRAME_TYPES:
                            if filter_type in comp[1]["components"]:
                                comp[1]["components"].remove(filter_type)

                filtered_comps.append(comp)

            component_types = filtered_comps

        carb_settings = carb.settings.get_settings()

        def _stop_profile() -> None:
            carb_settings.set(profile.get_non_persistent_path() + "enabled", False)

        # Much of this taken from omni.kit.xr.ui.window.profile\omni\kit\xr\ui\window\profile\xr_profile_settings_window.py
        with omni.ui.ZStack():
            omni.ui.Rectangle(style={"Rectangle": {"background_color": 0xFF454545, "border_radius": 3}})
            with omni.ui.ScrollingFrame():
                with omni.ui.HStack(spacing=0):
                    with omni.ui.VStack(height=0, spacing=10):
                        omni.ui.Spacer(height=1)
                        with omni.ui.ZStack(height=30):
                            icon = None
                            display_name = carb_settings.get(profile.get_non_persistent_path() + "displayName")
                            text = "Stop " + display_name
                            click_fn = _stop_profile
                            tooltip = "Click here to stop " + display_name
                            if icons is not None and len(icons) == 2:
                                icon = icons[1]
                            color = 0xFFFFAA66

                            omni.ui.Rectangle(
                                style={
                                    "Rectangle": {"background_color": 0xFF222222, "border_radius": 8},
                                    "Rectangle:hovered": {"background_color": 0xFF333333},
                                }
                            )
                            self._button = omni.ui.HStack(height=36, alignment=omni.ui.Alignment.CENTER)
                            self._button.set_mouse_released_fn(lambda *_: click_fn())
                            self._button.set_tooltip(tooltip)

                            with self._button:
                                style = {"Label": {"font_size": 20, "color": color}}

                                omni.ui.Spacer()
                                if icon is not None:
                                    omni.ui.Image(icon, width=28, height=36)
                                    omni.ui.Spacer(width=16)
                                self._button = omni.ui.Label(
                                    text, style=style, width=0, alignment=omni.ui.Alignment.CENTER
                                )
                                omni.ui.Spacer()

                        if component_types:
                            self.__settings_frame = XRSettingsStack(component_types)
                            self.__settings_frame.build_ui(profile)
                    omni.ui.Spacer(width=5)
