# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ManipulatorPrim2FabricExt"]

import carb
import omni.ext
from omni.kit.manipulator.prim.core import get_prim_data_accessor_registry

from .data_accessor import FabricDataAccessor


class ManipulatorPrim2FabricExt(omni.ext.IExt):
    """An extension class for manipulating primitive to Fabric data accessor registration.

    This class implements the `omni.ext.IExt` interface and is responsible for managing the
    registration and unregistration of a Fabric data accessor based on application settings.
    It watches for changes in the application's usage of the Fabric Scene Delegate and
    updates the registration status of the data accessor accordingly."""

    def on_startup(self, ext_id):
        """Initializes the extension with the given extension ID.

        Args:
            ext_id (str): The unique identifier for the extension."""
        self._settings = carb.settings.get_settings()
        self._prim_data_accessor_registry = get_prim_data_accessor_registry()
        self._sub_fabric_delegate_changed = omni.kit.app.SettingChangeSubscription(
            "/app/useFabricSceneDelegate", self._on_fabric_delegate_changed
        )
        if self._settings.get("/app/useFabricSceneDelegate") == True:
            self.register_data_accessor()
        else:
            carb.log_info("FSD is off: NOT register Fabric Data Accessor")

    def on_shutdown(self):
        """Shuts down the extension and cleans up resources."""
        self.unregister_data_accessor()
        self._sub_fabric_delegate_changed = None
        self._prim_data_accessor_registry = None

    def _on_fabric_delegate_changed(self, value: str, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            if self._settings.get("/app/useFabricSceneDelegate") == True:
                self.register_data_accessor()
            else:
                self.unregister_data_accessor()

    def register_data_accessor(self):
        """Registers the Fabric data accessor with the global registry."""
        carb.log_info("Register Fabric Data Accessor")
        self._prim_data_accessor_registry.register_data_accessor(FabricDataAccessor, "FABRIC")

    def unregister_data_accessor(self):
        """Unregisters the Fabric data accessor from the global registry."""
        carb.log_info("Unregister Fabric Data Accessor")
        self._prim_data_accessor_registry.unregister_data_accessor("FABRIC")
