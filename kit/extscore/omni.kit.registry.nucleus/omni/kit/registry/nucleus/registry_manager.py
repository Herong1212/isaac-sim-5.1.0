# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["RegistryManager", "start_index_changes_batching", "apply_index_changes_batch", "get_publish_results", "PublishResult"]

import carb
from carb.eventdispatcher import get_eventdispatcher
import omni.ext
import omni.kit.app

import logging
from string import Template

from .registry_provider import RegistryProvider
from .registry_globals import RegistryGlobals, PublishResult

logger = logging.getLogger(__name__)

REGISTRIES_SETTINGS = [
    "/exts/omni.kit.registry.nucleus/registries",
    "/persistent/exts/omni.kit.registry.nucleus/userRegistries",
]

REGISTRIES_CHANGED_GLOBAL_EVENT = "omni.kit.registry.nucleus.REGISTRIES_CHANGED_EVENT"
REGISTRIES_CHANGED_EVENT = carb.events.type_from_string(REGISTRIES_CHANGED_GLOBAL_EVENT)
omni.kit.app.register_event_alias(REGISTRIES_CHANGED_EVENT, REGISTRIES_CHANGED_GLOBAL_EVENT)


_manager_instance = None


def get_registry_manager_instance() -> "RegistryManager":
    """Get global registry manager instance."""
    global _manager_instance
    return _manager_instance


def start_index_changes_batching():
    """Stop updating index, all index changes will be accumulated until `apply_index_changes_batch` call."""
    _manager_instance.start_index_changes_batching()


def apply_index_changes_batch():
    """Update index and toggle off index changes batching mode."""
    return _manager_instance.apply_index_changes_batch()


def get_publish_results() -> dict:
    """Get publish results."""
    return _manager_instance._registry_globals.get_publish_results()


class RegistryManager:
    """Registry manager. Creates and keeps a registry instance for each registry in settings."""

    def __init__(self):
        # Own global instance
        global _manager_instance
        _manager_instance = self

        self._registry_globals = RegistryGlobals()

        # All registries (name -> registry instance)
        self._registries = {}

        # Toggle special mode where index is not updated, but changes batched instead (for performance)
        self._index_changes_batching = False

        def on_event(_):
            self._refresh_registries()
            # Initiate async sync with registries.
            omni.kit.app.get_app().get_extension_manager().refresh_registry()

        self._sub = get_eventdispatcher().observe_event(event_name=REGISTRIES_CHANGED_GLOBAL_EVENT, on_event=on_event)
        self._refresh_registries()

    def _get_extra_kit_version_tokens(self):
        # Add more kit version tokens. Temporarily, before we add it in IApp.
        v = omni.kit.app.get_app().get_kit_version()
        v, *_ = v.split("+", maxsplit=1)
        v = v.split("-")[0].split(".")
        major, minor, patch, *_ = v + ["0", "0", "0"]
        return {
            "kit_version_major": major,
            "kit_version_minor": minor,
            "kit_version_patch": patch,
        }

    def _refresh_registries(self):
        # Read all registries and create (if not existing already)
        # Settings python bindings doesn't support array of dicts currently, use carb.dictionary directly.
        # Note [1:], avoid '/' when working with dictionary directly.
        settings_dict = carb.settings.get_settings().get_settings_dictionary("")

        self._clear_registries()

        self._tokens = settings_dict.get("exts/omni.kit.registry.nucleus/tokens", {})
        self._tokens.update(self._get_extra_kit_version_tokens())

        for key in REGISTRIES_SETTINGS:
            registries = settings_dict.get(key[1:], [])
            for value in registries:
                # Get url
                url = value.get("url", None)
                if not url:
                    logger.warn(f"'url' key is not set for registry '{name}' in '{key}'. Skipping it.")
                    continue

                name = value.get("name", None)
                if not name:
                    logger.error(f"'name' key is not set for registry in '{key}'")
                    continue

                # Already created?
                if name in self._registries:
                    continue

                # Get if registry is needs extra security checks based on if trusted
                trusted = value.get("trusted", None)
                if trusted is None:
                    logger.info(f"'trusted' is not set for registry '{name}' in '{key}'")
                    trusted = True  # trusted by default. this should change in future.

                # Get if registry is optional
                optional = value.get("optional", False)

                # Support tokens in URL
                url = self._resolve_url(url)
                self._registries[name] = RegistryProvider(name, url, trusted, optional, self._registry_globals)

    def _resolve_url(self, url: str) -> str:
        # prefer our custom tokens over global carbonite tokens
        url = Template(url).safe_substitute(self._tokens)
        return carb.tokens.get_tokens_interface().resolve(url)

    def _clear_registries(self):
        for _, registry in self._registries.items():
            registry.shutdown()
        self._registries = {}

    def get_provider(self, name: str) -> RegistryProvider:
        """Get registry provider by name."""
        return self._registries.get(name, None)

    def start_index_changes_batching(self):
        """Stop updating index, all index changes will be accumulated until `apply_index_changes_batch` call."""
        self._registry_globals.set_index_changes_batching(True)

    def apply_index_changes_batch(self):
        """Update index and toggle off index changes batching mode."""
        if not self._registry_globals.is_index_changes_batching():
            return

        res = True
        for _, registry in self._registries.items():
            res &= registry.apply_index_changes_batch()

        self._registry_globals.set_index_changes_batching(False)

        return res

    def destroy(self):
        self._sub = None
        self._clear_registries()

        if self._registry_globals:
            self._registry_globals.destroy()
            self._registry_globals = None

        global _manager_instance
        _manager_instance = None
