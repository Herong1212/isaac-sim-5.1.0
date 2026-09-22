# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["XRCoreExtension"]

import carb
import omni.ext
import omni.kit.app
from omni.kit.window.preferences import register_page, unregister_page

from .xr_class_wrappers import XRAssetManager, XRCore
from .xr_preferences import XrPreferencesPage
from .xr_shutdown import XRShutdown


class XRCoreExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self._hooks = []
        self._preferences_page = None
        self.incompatible_features = (
            "/app/hydra/renderSettings/useUsdAttributes",
            "/app/hydra/renderSettings/useFabricAttributes",
        )
        self.disabled_features = []

    def on_startup(self, _ext_id) -> None:
        XRCore._start_singleton()

        # add a circular reference in shutdown to make sure a reference is kept until we're done shutting down
        XRShutdown.add_shutdown_function(lambda: None, self.__module__, "final shutdown")

        manager = omni.kit.app.get_app().get_extension_manager()
        self._hooks.append(
            manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self._register_preferences(),
                on_disable_fn=lambda _: self._unregister_preferences(),
                ext_name="omni.kit.window.preferences",
                hook_name="omni.kit.xr.core omni.kit.window.preferences listener",
            )
        )

        self.setup_compatibility()

    def setup_compatibility(self):
        def force_disable_incompatible_features():

            # Switch off reading render settings from USD/Fabric as it can take up to 10 seconds per frame
            # breaking any xr experience
            settings = carb.settings.get_settings()
            for feature in self.incompatible_features:
                if settings.get(feature):
                    settings.set_bool(feature, False)
                    self.disabled_features.append(feature)
                    carb.log_warn(f"{feature} is disabled at XR session start")

        def reenable_incompatible_features():
            settings = carb.settings.get_settings()
            for feature in self.disabled_features:
                settings.set_bool(feature, True)
                carb.log_warn(f"{feature} is re-enabled at XR session end")
            self.disabled_features.clear()

        message_bus = XRCore.get_singleton().get_message_bus()
        self.compatibility_xr_enable_subscription = message_bus.create_subscription_to_pop_by_type(
            carb.events.type_from_string("xr.enable"),
            lambda _: force_disable_incompatible_features(),
        )
        self.compatibility_xr_disable_subscription = message_bus.create_subscription_to_pop_by_type(
            carb.events.type_from_string("xr.disable"),
            lambda _: reenable_incompatible_features(),
        )

    def _register_preferences(self):
        self._preferences_page = register_page(XrPreferencesPage())

    def _unregister_preferences(self):
        unregister_page(self._preferences_page)
        self._preferences_page = None

    def on_shutdown(self) -> None:
        self._hooks.clear()

        # Run all shutdown tasks to ensure we're ready for a relaunch
        XRShutdown.run_shutdown_functions("omni.kit.xr.core")

        # Remove XRCore if it is still around
        XRCore._delete_singleton()
        XRAssetManager._delete_singleton()
