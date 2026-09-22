# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import carb
import omni.ui as ui
from omni.kit.xr.core import (
    XRAssetManager,
    XRGuiLayerComponentBase,
    XRInputDevice,
    XRInputDeviceEvent,
    XRTooltip,
    XRTooltipEvent,
    XRTransformType,
    XRUsdLayer,
)
from omni.kit.xr.scene_view.utils import Area2DComponent, SceneViewAttachMode, UiContainer, WidgetComponent
from omni.kit.xr.scene_view.utils.spatial_source import SpatialSource
from omni.ui import color
from pxr import Gf


@dataclass
class XRTextIcon:
    text: Optional[str] = None
    icon: Optional[str] = None


XR_USD_LAYER_KEY = "controllers"

XR_USER_HAND_LEFT = "/user/hand/left"
XR_USER_HAND_RIGHT = "/user/hand/right"

TOOLTIP_WIDTH_MULTIPLIER = 1.0
TOOLTIP_HEIGHT_MULTIPLIER = 2.6


class XRTooltipWidget(ui.Widget):
    def __init__(self, body: Union[XRTextIcon, List[XRTextIcon], None] = None, title: Optional[XRTextIcon] = None):
        super().__init__()

        style = {"font_size": 2, "color": color(224, 224, 224)}
        background_style = {"background_color": color(50, 52, 52), "border_radius": 0.5}
        icon_width = 3

        self._widget = ui.VStack()
        with self._widget:
            with ui.ZStack():
                ui.Rectangle(style=background_style)
                with ui.VStack():

                    if title is not None:
                        with ui.HStack():
                            if title.icon:
                                ui.Image(title.icon, width=icon_width)
                            else:
                                ui.Spacer(width=icon_width)
                            ui.Spacer(width=2)
                            ui.Label(title.text, style=style, alignment=ui.Alignment.LEFT)

                    if isinstance(body, XRTextIcon):
                        with ui.HStack():
                            if body.icon is not None:
                                ui.Image(body.icon, width=icon_width)
                            ui.Spacer(width=2)
                            ui.Label(body.text, style=style, alignment=ui.Alignment.LEFT)
                    elif body is not None:
                        for line in body:
                            with ui.HStack():
                                if line.icon:
                                    ui.Image(line.icon, width=icon_width)
                                else:
                                    ui.Spacer(width=icon_width)
                                ui.Spacer(width=2)
                                ui.Label(line.text, style=style, alignment=ui.Alignment.LEFT)


class XRTooltipState:

    def __init__(self):
        self.tooltips = {}
        self.subs = []


class XRTooltipsGuiLayer(XRGuiLayerComponentBase):
    """
    This implements the gui tooltip layer
    """

    def __init__(self):
        # Initialize gui layer component with layer name
        super().__init__("tooltips")

        # Usd layer with managed objects, that automatically get updated when XR is updated
        self.__usd_layer: XRUsdLayer = None

        # State with subscriptions and tooltip widgets
        self.__state: dict[str, XRTooltipState] = {}

        # If the layer was already enabled (hot reload), enable layer
        self.run_enable_if_enabled()

    def on_enable(self) -> None:
        """
        When Gui layer gets enabled.
        """

        # Get the usd layer, this one creates the layer if needed
        self.__usd_layer = self.get_usd_layer(XR_USD_LAYER_KEY)

        # Clear current state of tooltips per controller
        self.__state = {}
        self.__state[XR_USER_HAND_LEFT] = XRTooltipState()
        self.__state[XR_USER_HAND_RIGHT] = XRTooltipState()

        # Generate a new set of tooltips
        self.update_both_hands()

        # Register event handlers for when controller gets activated, the buttons on controller get updated, and when
        # controller gets disabled

        self.__subs = [
            self.register_message_bus_event_handler("xr_input.user_hand_left.enable", self.on_inputs_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_right.enable", self.on_inputs_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_left.inputs_change", self.on_inputs_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_right.inputs_change", self.on_inputs_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_left.tooltips_change", self.on_inputs_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_right.tooltips_change", self.on_inputs_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_left.disable", self.on_inputs_disabled),
            self.register_message_bus_event_handler("xr_input.user_hand_right.disable", self.on_inputs_disabled),
            self.register_setting_event_handler(
                self.get_persistent_profile_setting_path("tooltips/visible"), self.update_both_hands
            ),
        ]

    def on_disable(self) -> None:
        """
        When Gui layer gets disabled.
        """

        # Remove all subscriptions from layer
        self.__subs = []

        # Clear state
        self.__state[XR_USER_HAND_LEFT] = XRTooltipState()
        self.__state[XR_USER_HAND_RIGHT] = XRTooltipState()

        # Release managed usd layer handle
        self.__usd_layer = None

    def on_inputs_changed(self, event: XRInputDeviceEvent) -> None:
        """
        When new components are on the controller
        """

        # update all buttons
        self.update_components(str(event.input_device))

    def update_both_hands(self) -> None:
        """
        Update both hands
        """

        # update all buttons on both controllers
        self.update_components(XR_USER_HAND_LEFT)
        self.update_components(XR_USER_HAND_RIGHT)

    def update_components(self, hand: str) -> None:
        """
        Update the components on a given hand
        """

        carb.log_info(f"[XR] updating components for {hand}")

        # Get handle to the input device
        input_device: XRInputDevice = self.get_xr_core().get_input_device(hand)

        # Clear the current subscriptions
        self.__state[hand] = XRTooltipState()

        tooltips_enabled = self.get_settings().get_as_bool(self.get_persistent_profile_setting_path("tooltips/visible"))
        if not tooltips_enabled:
            return

        # Subscribe to events for each component that indicates
        # a tooltip is updated
        if input_device is not None:
            component_names = input_device.get_input_names()

            for component in component_names:
                # Subscription for when tooltip is changed
                self.__state[hand].subs.append(
                    self.register_message_bus_event_handler(
                        "xr_input."
                        + self.translate_usd_name_to_event_name(hand)
                        + "."
                        + str(component)
                        + ".tooltip_change",
                        self.on_update_tooltip,
                    )
                )
                # Update tooltip to latest state
                self.update_tooltip(hand, str(component))

    def clear_tooltip(self, hand: str, input: str) -> None:
        """
        Remove a given tooltip
        """
        carb.log_info(f"[XR] clearing tooltip for {hand} {input}")
        self.__state[hand].tooltips[input] = None

    def build_trackpad_thumbstick_tooltip(self, hand: str, input: str) -> None:
        """
        Build tooltips for joystick/trackpad
        """
        carb.log_info(f"[XR] building trackpad tooltip for {hand} {input}")

        input_device = self.get_xr_core().get_input_device(hand)
        tooltips = input_device.get_input_tooltips(input)

        usd_path = self.get_tooltip_usd_path(hand, input)
        if not self.__usd_layer.is_managed_prim(usd_path):
            return

        title = XRTextIcon(input.upper(), None)
        body = []

        if "tooltip_left" in tooltips:
            tooltip_def: XRTooltip = self.get_tooltip_manager().get_tooltip(tooltips["tooltip_left"])
            text = tooltip_def.text
            if isinstance(text, str):
                text = [text]
            for line in text:
                body.append(XRTextIcon(line, self.get_icon_file_path("Left.png")))

        if "tooltip_right" in tooltips:
            tooltip_def: XRTooltip = self.get_tooltip_manager().get_tooltip(tooltips["tooltip_right"])
            text = tooltip_def.text
            if isinstance(text, str):
                text = [text]
            for line in text:
                body.append(XRTextIcon(line, self.get_icon_file_path("Right.png")))

        if "tooltip_left_right" in tooltips:
            tooltip_def: XRTooltip = self.get_tooltip_manager().get_tooltip(tooltips["tooltip_left_right"])
            text = tooltip_def.text
            if isinstance(text, str):
                text = [text]
            for line in text:
                body.append(XRTextIcon(line, self.get_icon_file_path("Left_Right.png")))

        if "tooltip_up" in tooltips:
            tooltip_def: XRTooltip = self.get_tooltip_manager().get_tooltip(tooltips["tooltip_up"])
            text = tooltip_def.text
            if isinstance(text, str):
                text = [text]
            for line in text:
                body.append(XRTextIcon(line, self.get_icon_file_path("Up.png")))

        if "tooltip_down" in tooltips:
            tooltip_def: XRTooltip = self.get_tooltip_manager().get_tooltip(tooltips["tooltip_down"])
            text = tooltip_def.text
            if isinstance(text, str):
                text = [text]
            for line in text:
                body.append(XRTextIcon(line, self.get_icon_file_path("Down.png")))

        if "tooltip_up_down" in tooltips:
            tooltip_def: XRTooltip = self.get_tooltip_manager().get_tooltip(tooltips["tooltip_up_down"])
            text = tooltip_def.text
            if isinstance(text, str):
                text = [text]
            for line in text:
                body.append(XRTextIcon(line, self.get_icon_file_path("Up_Down.png")))

        if "tooltip_button" in tooltips:
            tooltip_def: XRTooltip = self.get_tooltip_manager().get_tooltip(tooltips["tooltip_button"])
            text = tooltip_def.text
            if isinstance(text, str):
                text = [text]
            for line in text:
                body.append(XRTextIcon(line, self.get_icon_file_path("Left_Right_Up_Down.png")))

        if len(body) == 0:
            return

        # Create the tooltip
        self.__state[hand].tooltips[input] = self.add_tooltip(usd_path, body, title)

    def build_button_tooltip(self, hand: str, input: str):
        """
        Build tooltip for a simple button
        """

        input_device = self.get_xr_core().get_input_device(hand)
        tooltips = input_device.get_input_tooltips(input)

        if "tooltip_button" not in tooltips:
            return

        carb.log_info(f"[XR] building button tooltip for {hand} {input}")

        tooltip_def: XRTooltip = self.get_tooltip_manager().get_tooltip(tooltips["tooltip_button"])

        usd_path = self.get_tooltip_usd_path(hand, input)

        if not self.__usd_layer.is_managed_prim(usd_path):
            return

        text = self.get_tooltip_prefix_text(input) + tooltip_def.text
        icon = self.get_tooltip_icon(input)

        if icon is None:
            icon = tooltip_def.icon

        self.__state[hand].tooltips[input] = self.add_tooltip(usd_path, XRTextIcon(text, icon), None)

    def on_update_tooltip(self, event: XRTooltipEvent) -> None:
        """
        Callback when tooltip has been updated on a given button
        """

        # device that generated the event
        hand = str(event.input_device)

        # button whose tooltip changed
        input = str(event.input)

        self.update_tooltip(hand, input)

    def update_tooltip(self, hand: str, input: str) -> None:
        """
        Update a given tooltip for a specific button and input device
        """

        if self.__usd_layer is None:
            return

        input_device: XRInputDevice = self.get_xr_core().get_input_device(hand)

        # remove the old tooltip
        self.clear_tooltip(hand, input)

        # check if input button exists
        if not input_device.has_input(input):
            return

        # We only put tooltips on the base components
        if input_device.has_input_base(input):
            # if it has a base it is not a base component
            return

        if input_device.has_input_gesture(input, "x") and input_device.has_input_gesture(input, "y"):
            # Thumbsticks and trackpads have special code path way
            self.build_trackpad_thumbstick_tooltip(hand, input)
        else:
            # Simple button
            self.build_button_tooltip(hand, input)

    def on_inputs_disabled(self, event: XRInputDeviceEvent) -> None:
        hand: str = str(event.input_device)
        self.__state[hand].tooltips = {}

    def add_tooltip(
        self, usd_path: Optional[str], body: Union[List[XRTextIcon], XRTextIcon, None], title: Union[XRTextIcon, None]
    ) -> Optional[UiContainer]:
        """
        Create the actual tooltip
        """

        carb.log_info(f"[XR] Creating tooltip at {usd_path}")

        if usd_path is None:
            return None

        local_translate: Gf.Vec3d = self.__usd_layer.get_transform(
            usd_path, XRTransformType.local, use_usd=True
        ).ExtractTranslation()

        # Estimate widget size.
        widget_width = 0
        widget_height = 0
        if title is not None:
            title_width = 0
            if title.text is not None:
                title_width = len(title.text)
            if title.icon is not None:
                title_width += 4

            widget_width = max(widget_width, title_width)
            widget_height += 1.1

        if isinstance(body, XRTextIcon):
            body_width = 0
            if body.text is not None:
                body_width = len(body.text)
            if body.icon is not None:
                body_width += 4

            widget_width = max(widget_width, body_width)
            widget_height += 1
        elif body is not None:
            for line in body:
                body_width = 0
                if line.text is not None:
                    body_width = len(line.text)
                if line.icon is not None:
                    body_width += 4

                widget_width = max(widget_width, body_width)
                widget_height += 1

        widget_width = widget_width * TOOLTIP_WIDTH_MULTIPLIER
        widget_height = widget_height * TOOLTIP_HEIGHT_MULTIPLIER

        origin = Area2DComponent.CENTER
        if local_translate[0] < -1:
            origin = Area2DComponent.RIGHT
        elif local_translate[0] > 1:
            origin = Area2DComponent.LEFT

        widget_component = WidgetComponent(
            XRTooltipWidget,
            widget_width,
            widget_height,
            20,
            widget_kwargs={"title": title, "body": body},
            origin=origin,
        )

        widget_container = UiContainer(
            widget_component,
            space_stack=[SpatialSource.new_prim_path_source(usd_path)],
            scene_view_args={"custom_base_path": self.__usd_layer.get_top_level_prim_path()},
            attach_mode=SceneViewAttachMode.DO_NOT_ATTACH_TO_MAIN_VIEWPORT,
        )
        widget_container.visible = True
        return widget_container

    def get_tooltip_usd_path(self, hand: str, component: str) -> Optional[str]:
        """
        Get path of usd prim anchor for the tooltip
        """

        return self.__usd_layer.get_meta_data(hand + "/tooltip/" + component)

    def get_tooltip_prefix_text(self, component: str) -> Optional[str]:
        """
        Get string that needs to be prepended to tooltip
        """
        return component.upper() + " - "

    def get_tooltip_icon(self, component: str) -> Optional[str]:
        """
        Get icon for some common buttons
        """
        if component == "trackpad":
            return None
        elif component == "thumbstick":
            return None
        elif component == "trigger":
            return self.get_icon_file_path("Trigger.png")
        elif component == "squeeze":
            return self.get_icon_file_path("Grip.png")
        elif component == "x":
            return self.get_icon_file_path("X.png")
        elif component == "y":
            return self.get_icon_file_path("Y.png")
        elif component == "a":
            return self.get_icon_file_path("A.png")
        elif component == "b":
            return self.get_icon_file_path("B.png")
        elif component == "menu":
            return self.get_icon_file_path("Menu.png")

        return None

    def get_icon_file_path(self, icon: str) -> Optional[str]:
        """
        Get path of where icons are stored
        """
        icon_path = Path(XRAssetManager.get_singleton().resolve_asset_path("{common.icons}/tooltips"))
        return str(icon_path.joinpath(icon))
