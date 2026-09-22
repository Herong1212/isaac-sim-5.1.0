# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

# Experimental preview layer for displaying hand model when han

import carb
from omni.kit.xr.core import XRAssetManager, XRGuiLayerComponentBase, XRInputDeviceEvent, XRTransformType
from pxr import Gf, Sdf, Usd

XR_USD_LAYER_KEY = "hands"

XR_USER_HAND_LEFT = "/user/hand/left"
XR_USER_HAND_RIGHT = "/user/hand/right"

XR_HAND_MODEL_GROUP = "hand_model"


class XRHandGuiLayer(XRGuiLayerComponentBase):
    """
    XRGuiLayer for hands (VR)
    """

    def __init__(self):
        super().__init__("hands")

        self.__usd_layer = None

        # If hand tracking isn't active, we skip this layer
        if self.get_settings().get_as_bool("/xr/openxr/components/omni.kit.xr.openxr.ext.hand_tracking/active"):
            self.run_enable_if_enabled()

    def on_enable(self) -> None:
        """
        When Gui layer gets enabled.
        """

        self.__usd_layer = self.get_usd_layer(XR_USD_LAYER_KEY)

        self.update_all_hands()

        self.__subs = [
            self.register_message_bus_event_handler("xr_input.user_hand_left.model_change", self.on_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_right.model_change", self.on_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_left.disable", self.on_disabled),
            self.register_message_bus_event_handler("xr_input.user_hand_right.disable", self.on_disabled),
            self.register_message_bus_event_handler("xr_input.user_hand_left.meta_data_change", self.on_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_right.meta_data_change", self.on_changed),
            self.register_setting_event_handler(
                self.get_persistent_profile_setting_path("controllers/visible"),
                self.update_all_hands,
            ),
        ]

    def on_disable(self) -> None:
        """
        When Gui layer gets disabled.
        """

        self.__subs = []

        self.clear_hand_model(XR_USER_HAND_LEFT)
        self.clear_hand_model(XR_USER_HAND_RIGHT)
        self.clear_attachment_points(XR_USER_HAND_LEFT)
        self.clear_attachment_points(XR_USER_HAND_RIGHT)
        self.__usd_layer = None

    def update_all_hands(self) -> None:
        self.clear_hand_model(XR_USER_HAND_LEFT)
        self.clear_hand_model(XR_USER_HAND_RIGHT)
        self.update_hand_model(XR_USER_HAND_LEFT)
        self.update_hand_model(XR_USER_HAND_RIGHT)

    def clear_hand_model(self, hand: str) -> None:
        """
        Clear the hand model shown
        """

        # Remove the hand model shown
        if self.__usd_layer and self.__usd_layer.is_valid():
            self.__usd_layer.remove_group(XR_HAND_MODEL_GROUP + hand)

    def clear_attachment_points(self, hand: str) -> None:
        if self.__usd_layer and self.__usd_layer.is_valid():
            self.__usd_layer.remove_group(XR_HAND_MODEL_GROUP + hand + "/attachment")

    def update_hand_model(self, hand: str) -> None:
        """
        Update the hand model shown.
        """

        self.get_settings().set_default_bool(self.get_persistent_profile_setting_path("hands/visible"), True)
        visible = self.get_settings().get_as_bool(self.get_persistent_profile_setting_path("hands/visible"))

        if self.__usd_layer and self.__usd_layer.is_valid():
            input_device = self.get_xr_core().get_input_device(hand)

            # Check if input device is present (left or right hand controller)
            if input_device is None or input_device.get_hand_tracking_data_source() != "hand":
                return

            side = "left" if "left" in hand else "right"

            # TODO: make this not hard coded
            asset_name = "{generic.hands}/" + side + "/model.usd"
            asset_path = XRAssetManager.get_singleton().resolve_asset_path(asset_name)

            # Load the asset into the layer
            device_path = self.__usd_layer.ensure_device_prim_path(hand)
            self.__usd_layer.add_asset(
                device_path + "/hand_model",
                visible=True,
                pickable=False,
                group=XR_HAND_MODEL_GROUP + hand,
                file_path=asset_path,
            )

            wrapped_prim_path = self.__usd_layer.get_wrapped_prim_path(device_path + "/hand_model")

            # Link hand joint poses to geometry
            joints_path: str = wrapped_prim_path + f"/Root/Model/model_geo/hand_{side}/joints"
            joints_prim: Usd.Prim = self.__usd_layer.get_prim_at_path(joints_path)
            if joints_prim.IsValid():
                children = joints_prim.GetAllChildren()
                for child in children:
                    child_name: Sdf.Path = child.GetName()
                    child_path: Sdf.Path = child.GetPath()
                    self.__usd_layer.add_link_to_input_device(
                        path=child_path,
                        group=XR_HAND_MODEL_GROUP + hand + "/joints",
                        input_device_name=hand,
                        pose_name=child_name,
                    )

            attachment_path: str = wrapped_prim_path + "/Root/Attachments"
            gui_attachments_path: str = device_path + "/attachments"

            attachment_prim: Usd.Prim = self.__usd_layer.get_prim_at_path(attachment_path)
            if attachment_prim.IsValid():
                self.__usd_layer.clear_meta_data(hand + "/attachments/")
                children = attachment_prim.GetAllChildren()

                for child in children:
                    child_name: Sdf.Path = child.GetName()
                    child_matrix: Gf.Matrix4d = self.__usd_layer.get_transform(child, XRTransformType.stage)

                    transform_path = gui_attachments_path + "/" + child_name

                    if self.__usd_layer.is_managed_prim(transform_path):
                        self.__usd_layer.set_transform(transform_path, child_matrix, XRTransformType.stage)
                    else:
                        self.__usd_layer.add_transform(
                            path=transform_path,
                            group=XR_HAND_MODEL_GROUP + hand + "/transform",
                            transform=child_matrix,
                            transform_type=XRTransformType.stage,
                        )
                    self.__usd_layer.set_meta_data(hand + "/attachments/" + child_name, transform_path)

            tooltip_path = wrapped_prim_path + "/Root/Tooltips"
            gui_tooltips_path = device_path + "/tooltips"

            tooltip_prim: Usd.Prim = self.__usd_layer.get_prim_at_path(tooltip_path)
            if tooltip_prim.IsValid():
                children = tooltip_prim.GetAllChildren()

                for child in children:
                    child_name: Sdf.Path = child.GetName()
                    child_matrix: Gf.Matrix4d = self.__usd_layer.get_transform(child, XRTransformType.stage)

                    transform_path = gui_tooltips_path + "/" + child_name

                    if self.__usd_layer.is_managed_prim(transform_path):
                        self.__usd_layer.set_transform(transform_path, child_matrix, XRTransformType.stage)
                    else:
                        self.__usd_layer.add_transform(
                            path=transform_path,
                            group=XR_HAND_MODEL_GROUP + hand + "/transform",
                            transform=child_matrix,
                            transform_type=XRTransformType.stage,
                        )
                    self.__usd_layer.set_meta_data(hand + "/tooltip/" + child_name, transform_path)

            # Annotate the usd layer to specify where the hand model can be found.
            # This is so other components can check what model is currently in use.
            self.__usd_layer.set_meta_data(hand, wrapped_prim_path)

            if visible:
                self.__usd_layer.show(wrapped_prim_path + "/Root/Model")
            else:
                self.__usd_layer.hide(wrapped_prim_path + "/Root/Model")

    def on_changed(self, event: XRInputDeviceEvent) -> None:
        """
        Called when the hand is enabled.
        """

        hand = event.input_device
        self.clear_hand_model(hand)
        self.update_hand_model(hand)

    def on_disabled(self, event: XRInputDeviceEvent) -> None:
        """
        Called when the hand is disabled.
        """

        hand = event.input_device
        self.clear_hand_model(hand)
