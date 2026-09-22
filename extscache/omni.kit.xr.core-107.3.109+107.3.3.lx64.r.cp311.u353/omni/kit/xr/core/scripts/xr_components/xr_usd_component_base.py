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

from typing import Optional

import carb

from ..xr_class_wrappers import XRUsdLayer
from ..xr_selection_manager import XRSelectionManager
from ..xr_singleton import XRSingleton, XRSingletonType
from ..xr_tooltip_manager import XRTooltipManager
from .xr_component_base import XRComponentBase


@XRSingleton()
class XRUsdLayerManager(XRComponentBase, XRSingletonType):

    def __init__(self):

        super().__init__("usd_layer_manager")

        self.__usd_layers = {}
        self.__gui_enabled = False

        super().start("xr_gui")

    def on_enable(self):
        """
        Called when xr_gui.enable event is triggered.
        """

        # Mark that gui is enabled
        self.__gui_enabled = True

    def on_disable(self):
        """
        Called when xr_gui.disable event is triggered
        """

        # Clear out any existing layers
        # When xr_gui layer is disabled it means that
        # a new usd is loaded or xr mode is toggled
        # In either case the xr gui layers need to be
        # removed.

        for usd_layer in self.__usd_layers.values():
            usd_layer.invalidate()

        self.__usd_layers = {}
        self.__gui_enabled = False

    def get_usd_layer(self, layer_name: str) -> Optional[XRUsdLayer]:
        """
        Request a named gui layer.
        """

        if not self.__gui_enabled:
            carb.log_error("[XR] XRUsdLayerManager is requesting UsdLayer while Usd gui is not active.")
            return None

        if layer_name not in self.__usd_layers:
            usd_path = "/_xr/gui/" + layer_name
            self.__usd_layers[layer_name] = self.get_xr_core().create_xr_usd_layer(usd_path)

        return self.__usd_layers[layer_name]

    def has_usd_layer(self, layer_name: str) -> bool:
        """
        Check if named gui layer exists.
        """

        if layer_name not in self.__usd_layers:
            return False
        return True


class XRUsdComponentBase(XRComponentBase):

    def __init__(self, name: str):

        super().__init__(name)
        self.__selection_manager: XRSelectionManager = XRSelectionManager.get_singleton()
        self.__tooltip_manager: XRTooltipManager = XRTooltipManager.get_singleton()
        self.__usd_layer_manager: XRUsdLayerManager = XRUsdLayerManager.get_singleton()

    def get_usd_layer(self, layer_name: str) -> Optional[XRUsdLayer]:
        """
        Get usd layer that can be used to display ui components.
        """

        return self.__usd_layer_manager.get_usd_layer(layer_name)

    def has_usd_layer(self, layer_name: str) -> bool:
        """
        Check if usd layer exists.
        """

        return self.__usd_layer_manager.has_usd_layer(layer_name)

    def get_selection_manager(self) -> XRSelectionManager:
        """
        Get the selection manager.
        """

        return self.__selection_manager

    def get_tooltip_manager(self) -> XRTooltipManager:
        """
        Get the tooltip manager.
        """

        return self.__tooltip_manager
