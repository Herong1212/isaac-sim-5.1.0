# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""Provides functionality to manage extension autoload preferences and to asynchronously load extensions in the omni.kit.window.extensions module."""

__all__ = []

from functools import lru_cache

import carb
import carb.settings
import omni.kit.app

from .utils import ext_id_to_fullname, set_default_and_get_setting

DEFERRED_LOAD_SETTING_KEY = "/exts/omni.kit.window.extensions/deferredLoadExts"
AUTOLOAD_SETTING_KEY = "/persistent/app/exts/enabled"
FEATURED_EXT_SETTING_KEY = "/exts/omni.kit.window.extensions/featuredExts"
KIT_FEATURED_EXT_SETTING_KEY = "/exts/omni.kit.window.extensions/kit_featured_exts"
WAIT_FRAMES_SETTING_KEY = "/exts/omni.kit.window.extensions/waitFramesBetweenEnable"
DEFAULT_SEARCH_SETTING_KEY = "/exts/omni.kit.window.extensions/default_search_words"

_autoload_exts = None
_startup_exts = set()
_startup_ext_ids = set()


def _get_autoload_exts():
    global _autoload_exts
    if _autoload_exts is None:
        _autoload_exts = set(set_default_and_get_setting(AUTOLOAD_SETTING_KEY, []))
    return _autoload_exts


@lru_cache()
def _get_featured_exts():
    return set(set_default_and_get_setting(FEATURED_EXT_SETTING_KEY, []))


@lru_cache()
def _get_kit_featured_exts():
    return set(set_default_and_get_setting(KIT_FEATURED_EXT_SETTING_KEY, []))


def get_default_search_words():
    return set_default_and_get_setting(DEFAULT_SEARCH_SETTING_KEY, [])


def _save():
    exts = _get_autoload_exts()
    carb.settings.get_settings().set(AUTOLOAD_SETTING_KEY, list(exts))


def toggle_autoload(ext_id: str, toggle: bool):
    """Toggles the autoload state of an extension.

    Args:
        ext_id (str): Identifier for the extension to toggle.
        toggle (bool): True to enable, False to disable autoload."""
    exts = _get_autoload_exts()
    if toggle:
        # Disable all other versions
        ext_manager = omni.kit.app.get_app().get_extension_manager()
        extensions = ext_manager.fetch_extension_versions(ext_id_to_fullname(ext_id))
        for e in extensions:
            exts.discard(e["id"])

        exts.add(ext_id)
    else:
        exts.discard(ext_id)
    _save()


def is_autoload_enabled(ext_id: str) -> bool:
    """Checks if auto-loading is enabled for a given extension.

    Args:
        ext_id (str): The unique identifier of the extension."""
    exts = _get_autoload_exts()
    return ext_id in exts


def is_startup_ext(ext_name: str) -> bool:
    """Checks if the given extension name is a startup extension.

    Args:
        ext_name (str): The name of the extension to check.

    Returns:
        bool: True if the extension is a startup extension, False otherwise."""
    return ext_name in _startup_exts


def is_startup_ext_id(ext_id: str) -> bool:
    """Checks if an extension ID is in the startup extensions set.

    Args:
        ext_id (str): The ID of the extension to check."""
    return ext_id in _startup_ext_ids


def is_featured_ext(ext_name: str) -> bool:
    """Checks if the given extension name is featured.

    Args:
        ext_name (str): The name of the extension to check."""
    return ext_name in _get_featured_exts()


def is_kit_featured_ext(ext_name: str) -> bool:
    """Checks if the given extension name is featured.

    Args:
        ext_name (str): The name of the extension to check."""

    return ext_name in _get_kit_featured_exts()


def are_featured_exts_enabled() -> bool:
    """Checks if featured extensions are enabled.

    Returns:
        bool: True if there are featured extensions enabled, False otherwise."""
    return len(_get_featured_exts()) > 0


async def autoload_extensions():
    """Loads and enables extensions that are marked for autoload.

    This function is called asynchronously and ensures that all extensions marked for
    autoload in the settings are loaded and enabled after the core application has completed
    its initial update cycle. It will also delay enabling each deferred extension to allow
    for a frame update in between, based on a configurable wait time."""
    # Delay for one update until everything else of a core app is loaded
    await omni.kit.app.get_app().next_update_async()

    ext_manager = omni.kit.app.get_app().get_extension_manager()

    wait_frames = set_default_and_get_setting(WAIT_FRAMES_SETTING_KEY, 1)

    # Enable all deferered extension, one by one. Wait for next frame inbetween each.
    for ext_id in set_default_and_get_setting(DEFERRED_LOAD_SETTING_KEY, []):
        ext_manager.set_extension_enabled_immediate(ext_id, True)
        for _ in range(wait_frames):
            await omni.kit.app.get_app().next_update_async()

    # Build list of startup extensions (those that were started by this point)
    _autoload_exts = _get_autoload_exts()
    for ext_info in ext_manager.get_extensions():
        if ext_info["enabled"] and ext_info["id"] not in _autoload_exts:
            _startup_exts.add(ext_info["name"])
            _startup_ext_ids.add(ext_info["id"])
