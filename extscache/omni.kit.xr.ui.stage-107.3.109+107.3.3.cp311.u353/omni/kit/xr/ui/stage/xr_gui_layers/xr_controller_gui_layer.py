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

import carb
from omni.kit.xr.core import XRAssetManager, XRGuiLayerComponentBase, XRInputDeviceEvent, XRTransformType
from pxr import Gf, Sdf, Usd

XR_USD_LAYER_KEY = "controllers"

XR_USER_HAND_LEFT = "/user/hand/left"
XR_USER_HAND_RIGHT = "/user/hand/right"

XR_CONTROLLER_MODEL_GROUP = "controller_model"
XR_CONTROLLER_TOOLTIPS_GROUP = "controller_tooltips"
XR_CONTROLLER_ATTACHMENTS_GROUP = "controller_attachments"


# This is the layer that contains the model for the controllers.


class XRControllerGuiLayer(XRGuiLayerComponentBase):
    """
    XRGuiLayer for controllers (VR)
    """

    def __init__(self):

        # Initialize parent with the name of the layer
        super().__init__("controllers")

        # Keep track of the usd layer where we store the models
        self.__usd_layer = None

        # If the layer was already enabled (hot reload) run the enable function
        self.run_enable_if_enabled()

    def on_enable(self) -> None:
        """
        When Gui layer gets enabled.
        """

        # Find the usd layer where the UI is stored
        self.__usd_layer = self.get_usd_layer(XR_USD_LAYER_KEY)

        # Make sure that state of the layer is up to date
        self.update_all_controllers()

        # To know what the current controller models are, the application listens to events on the xr_input system.
        # The model_change message indicates that a new model may need to be rendered and the disable message indicates
        # that the controller is no longer active.

        # The last subscription in the list, listens to the setting that controls visibility

        # All these subscriptions are on the application's message bus. Deleting the subscriptions will stop the callbacks
        # from being called.

        self.__subs = [
            self.register_message_bus_event_handler("xr_input.user_hand_left.model_change", self.on_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_right.model_change", self.on_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_left.meta_data_change", self.on_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_right.meta_data_change", self.on_changed),
            self.register_message_bus_event_handler("xr_input.user_hand_left.disable", self.on_disabled),
            self.register_message_bus_event_handler("xr_input.user_hand_right.disable", self.on_disabled),
            self.register_setting_event_handler(
                self.get_persistent_profile_setting_path("controllers/visible"), self.update_all_controllers
            ),
        ]

    def on_disable(self) -> None:
        """
        When Gui layer gets disabled.
        """

        self.__subs = []

        self.clear_controller_model(XR_USER_HAND_LEFT)
        self.clear_controller_model(XR_USER_HAND_RIGHT)
        self.clear_attachment_points(XR_USER_HAND_LEFT)
        self.clear_attachment_points(XR_USER_HAND_RIGHT)
        self.__usd_layer = None

    def update_all_controllers(self) -> None:
        """
        Clear and then update all controller models.
        """
        self.clear_controller_model(XR_USER_HAND_LEFT)
        self.clear_controller_model(XR_USER_HAND_RIGHT)
        self.update_controller_model(XR_USER_HAND_LEFT)
        self.update_controller_model(XR_USER_HAND_RIGHT)

    def clear_controller_model(self, hand: str) -> None:
        """
        Clear the controller model shown.
        """

        # Remove the controller model shown
        if self.__usd_layer and self.__usd_layer.is_valid():
            self.__usd_layer.remove_group(XR_CONTROLLER_MODEL_GROUP + hand)

    def clear_attachment_points(self, hand: str) -> None:

        if self.__usd_layer and self.__usd_layer.is_valid():
            self.__usd_layer.remove_group(XR_CONTROLLER_ATTACHMENTS_GROUP + hand)

    def update_controller_model(self, hand: str) -> None:
        """
        Update the controller model shown.
        """

        # Check if the controller needs to be visible
        self.get_settings().set_default_bool(self.get_persistent_profile_setting_path("controllers/visible"), True)
        visible = self.get_settings().get_as_bool(self.get_persistent_profile_setting_path("controllers/visible"))

        if self.__usd_layer and self.__usd_layer.is_valid():

            self.__usd_layer.remove_group(XR_CONTROLLER_MODEL_GROUP + hand)

            # Even if the model is invisible we load the model to get the attachment points
            # The current model still stores them in the usd file as our openvr implementation does
            # not support getting aim/grip positions.

            # Get the input device
            input_device = self.get_xr_core().get_input_device(hand)

            # Check if input device is present (left or right hand controller)
            if input_device is None or input_device.get_hand_tracking_data_source() == "hand":
                return

            # Check if a model has been resolved
            model = input_device.get_model()
            if model is None:
                return

            # Get the asset name for the model
            asset_name = str(model.get_asset())
            if asset_name == "":
                return

            # Load the asset into the layer
            asset_path = XRAssetManager.get_singleton().resolve_asset_path(asset_name)

            device_path = self.__usd_layer.ensure_device_prim_path(hand)
            self.__usd_layer.add_asset(
                device_path + "/controller_model",
                visible=True,
                pickable=False,
                group=XR_CONTROLLER_MODEL_GROUP + hand,
                file_path=asset_path,
            )

            # Get the path of where the model inserted into the stage
            wrapped_prim_path = self.__usd_layer.get_wrapped_prim_path(device_path + "/controller_model")

            # The attachment anchors are stored in the usd file. In this next section we redefine them
            # in a path directly under the main prim of the device.

            # Path inside the usd asset
            attachment_path: str = wrapped_prim_path + "/Root/Attachments"

            # path outside of the usd asset
            gui_attachments_path: str = device_path + "/attachments"

            # Copy all the attachment point primitives out of the usd
            attachment_prim: Usd.Prim = self.__usd_layer.get_prim_at_path(attachment_path)
            if attachment_prim.IsValid():

                self.__usd_layer.remove_group(XR_CONTROLLER_ATTACHMENTS_GROUP + hand)

                self.__usd_layer.clear_meta_data(hand + "/attachments/")
                children = attachment_prim.GetAllChildren()

                for child in children:
                    child_name: Sdf.Path = child.GetName()
                    child_matrix: Gf.Matrix4d = self.__usd_layer.get_transform(
                        child, XRTransformType.stage, use_usd=True
                    )

                    transform_path = gui_attachments_path + "/" + child_name

                    if self.__usd_layer.is_managed_prim(transform_path):
                        self.__usd_layer.set_transform(
                            transform_path, child_matrix, XRTransformType.stage, use_usd=True
                        )
                    else:
                        self.__usd_layer.add_transform(
                            path=transform_path,
                            group=XR_CONTROLLER_ATTACHMENTS_GROUP + hand,
                            transform=child_matrix,
                            transform_type=XRTransformType.stage,
                        )
                    self.__usd_layer.set_meta_data(hand + "/attachments/" + child_name, transform_path)
            else:
                carb.log_warn("Controller model does not have attachment xforms")

            self.dispatch_message_bus_event(
                "xr_input." + self.translate_usd_name_to_event_name(hand) + ".attachments_change"
            )

            # Now do the same for the tooltip anchors

            tooltip_path = wrapped_prim_path + "/Root/Tooltips"
            gui_tooltips_path = device_path + "/tooltips"

            tooltip_prim: Usd.Prim = self.__usd_layer.get_prim_at_path(tooltip_path)
            if tooltip_prim.IsValid():
                children = tooltip_prim.GetAllChildren()

                self.__usd_layer.remove_group(XR_CONTROLLER_TOOLTIPS_GROUP + hand)

                for child in children:
                    child_name: Sdf.Path = child.GetName()
                    child_matrix: Gf.Matrix4d = self.__usd_layer.get_transform(
                        child, XRTransformType.stage, use_usd=True
                    )

                    transform_path = gui_tooltips_path + "/" + child_name

                    if self.__usd_layer.is_managed_prim(transform_path):
                        self.__usd_layer.set_transform(
                            transform_path, child_matrix, XRTransformType.stage, use_usd=True
                        )
                    else:
                        self.__usd_layer.add_transform(
                            path=transform_path,
                            group=XR_CONTROLLER_TOOLTIPS_GROUP + hand,
                            transform=child_matrix,
                            transform_type=XRTransformType.stage,
                        )
                    self.__usd_layer.set_meta_data(hand + "/tooltip/" + child_name, transform_path)
            else:
                carb.log_warn("Controller model does not have tooltip xforms")

            self.dispatch_message_bus_event(
                "xr_input." + self.translate_usd_name_to_event_name(hand) + ".tooltips_change"
            )

            # Annotate the usd layer to specify where the controller model can be found.
            # This is so other components can check what model is currently in use.
            self.__usd_layer.set_meta_data(hand, wrapped_prim_path)

            # Make controller visible or invisible
            if visible:
                self.__usd_layer.show(wrapped_prim_path + "/Root/Model")
            else:
                self.__usd_layer.hide(wrapped_prim_path + "/Root/Model")

    def on_changed(self, event: XRInputDeviceEvent) -> None:
        """
        Called when a new controller type was detected or
        the controller is enabled.
        """

        hand = event.input_device

        # Clear the old controller
        self.clear_controller_model(hand)

        # Load the new controller
        self.update_controller_model(hand)

    def on_disabled(self, event: XRInputDeviceEvent) -> None:
        """
        Called when the controller is disabled.
        """

        # Check the message for the input device that is being disabled
        hand = event.input_device
        self.clear_controller_model(hand)
