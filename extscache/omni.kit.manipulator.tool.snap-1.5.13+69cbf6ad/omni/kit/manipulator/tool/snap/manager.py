# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Callable, Dict, List, Sequence, Union

import carb
import carb.settings
from omni.ui import scene as sc
from pxr import Gf, Sdf

from .provider import SnapProvider
from .registry import SnapProviderRegistry
from .settings_constants import (
    CONFORM_TO_TARGET_SETTING_PATH,
    CONFORM_UP_AXIS_SETTING_PATH,
    KEEP_SPACING_SETTING_PATH,
    SNAP_PROVIDER_NAME_SETTING_PATH,
)


class SnapProviderManager:
    """A manager that handles enabling, disabling, and updating snap functionality for providers in a viewport.

    This class manages a collection of snap providers, which are responsible for providing snapping behavior in the context of a 3D viewport. It subscribes to registry and settings changes to update the enabled providers accordingly.

    Args:
        viewport_api: The API object for interacting with the viewport.
    """

    def __init__(self, viewport_api):
        """Initializes the manager for snap providers.

        Args:
            viewport_api: The API object for interacting with the viewport."""
        self._viewport_api = viewport_api
        self._settings = carb.settings.get_settings()
        self._registry = SnapProviderRegistry.get_instance()
        self._providers: Dict[str, SnapProvider] = {}
        self._enabled_providers: List[SnapProvider] = []
        self._provider_registry_sub = self._registry.subscribe_to_registry_change(self._on_registry_changed)
        self._on_registry_changed()
        self._enabled_provider_sub = self._settings.subscribe_to_tree_change_events(
            SNAP_PROVIDER_NAME_SETTING_PATH, self._on_enabled_providers_changed
        )
        self._update_enabled_providers()

    def __del__(self):
        """Cleans up the manager and unsubscribes from registry changes."""
        self.destroy()

    def destroy(self):
        """Unsubscribes from registry and settings events, and cleans up the providers."""
        if self._provider_registry_sub:
            self._registry.unsubscribe_to_registry_change(self._provider_registry_sub)
            self._provider_registry_sub = None
        if self._enabled_provider_sub:
            self._settings.unsubscribe_to_change_events(self._enabled_provider_sub)
            self._enabled_provider_sub = None

    def _on_registry_changed(self):
        for _, provider in self._providers.items():
            provider.destroy()
        self._providers.clear()

        providers = self._registry.providers
        for name, provider_class in providers.items():
            self._providers[name] = provider_class(viewport_api=self._viewport_api)

        self._update_enabled_providers()

    def on_began(self, excluded_paths: List[Union[str, Sdf.Path]], **kwargs):
        """Notifies enabled snap providers that a snap operation has begun.

        Args:
            excluded_paths (List[Union[str, Sdf.Path]]): The list of paths to exclude from snapping.
            **kwargs: Additional keyword arguments that may be required by the providers."""
        for provider in self._enabled_providers:
            provider.on_began(excluded_paths, **kwargs)

    def on_ended(self, **kwargs):
        """Notifies enabled snap providers that a snap operation has ended.

        Args:
            **kwargs: Additional keyword arguments that may be required by the providers."""
        for provider in self._enabled_providers:
            provider.on_ended(**kwargs)

    def get_snap_pos(
        self,
        xform: Gf.Matrix4d,
        ndc_location: Sequence[float],
        scene_view: sc.SceneView,
        on_snapped: Callable,
    ) -> bool:
        """Iterates through enabled providers to find a snap position based on the provided transformation and location.

        Args:
            xform (Gf.Matrix4d): The transformation matrix of the object to snap.
            ndc_location (Sequence[float]): The location in normalized device coordinates where the snap is being requested.
            scene_view (sc.SceneView): The SceneView object where the snap is occurring.
            on_snapped (Callable): A callback function that is called when a snap occurs.

        Returns:
            bool: True if a snap position was found and handled by a provider, False otherwise."""
        for provider in self._enabled_providers:
            if provider.require_viewport_api() and ndc_location is None:
                carb.log_warn(f"Cannot use {provider.get_name()} snap in Viewport 1.0")
                continue

            want_orient = self._settings.get(CONFORM_TO_TARGET_SETTING_PATH)
            want_keep_spacing = self._settings.get(KEEP_SPACING_SETTING_PATH)
            conform_up_axis = self._settings.get(CONFORM_UP_AXIS_SETTING_PATH)
            if provider.on_snap(
                xform=xform,
                ndc_location=ndc_location,
                scene_view=scene_view,
                want_orient=want_orient,
                want_keep_spacing=want_keep_spacing,
                on_snapped=on_snapped,
                conform_up_axis=conform_up_axis,
                enabled_providers=self._enabled_providers,
            ):
                # return at the first provider that can provide a snap result
                return True
        return False

    def _on_enabled_providers_changed(self, tree_item, changed_item, event_type):
        self._update_enabled_providers()

    def _update_enabled_providers(self):
        provider_names = self._settings.get(SNAP_PROVIDER_NAME_SETTING_PATH) or []
        self._enabled_providers = []
        for name in provider_names:
            provider = self._providers.get(name, None)
            if provider:
                self._enabled_providers.append(provider)

        self._enabled_providers.sort(key=lambda provider: provider.get_order())
