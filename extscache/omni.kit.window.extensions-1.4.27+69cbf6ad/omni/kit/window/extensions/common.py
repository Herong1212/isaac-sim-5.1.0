# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides utilities for managing and interacting with extensions in the omni.kit.window.extensions framework."""

__all__ = []

import abc
import asyncio
import os
import os.path
from enum import Enum
from functools import lru_cache
from string import Template
from typing import Callable, Dict, List, Optional, Tuple

import carb.events
import carb.settings
import carb.tokens
import omni.kit.app

from . import ext_controller
from .utils import (
    change_setting,
    get_ext_info_dict,
    get_extpath_git_ext,
    get_setting,
    set_default_and_get_setting,
    show_ok_popup,
)

# Extension root path. Set when extension starts.
EXT_ROOT = None

REGISTRIES_CHANGED_GLOBAL_EVENT = "omni.kit.registry.nucleus.REGISTRIES_CHANGED_EVENT"
REGISTRIES_CHANGED_EVENT = carb.events.type_from_string(REGISTRIES_CHANGED_GLOBAL_EVENT)
omni.kit.app.register_event_alias(REGISTRIES_CHANGED_EVENT, REGISTRIES_CHANGED_GLOBAL_EVENT)

REGISTRIES_SETTING = "/exts/omni.kit.registry.nucleus/registries"
USER_REGISTRIES_SETTING = "/persistent/exts/omni.kit.registry.nucleus/userRegistries"

EXTENSION_PULL_STARTED_GLOBAL_EVENT = "omni.kit.window.extensions.EXTENSION_PULL_STARTED_EVENT"
EXTENSION_PULL_STARTED_EVENT = carb.events.type_from_string(EXTENSION_PULL_STARTED_GLOBAL_EVENT)
omni.kit.app.register_event_alias(EXTENSION_PULL_STARTED_EVENT, EXTENSION_PULL_STARTED_GLOBAL_EVENT)

COMMUNITY_TAB_TOGGLE_GLOBAL_EVENT = "omni.kit.window.extensions.COMMUNITY_TAB_TOGGLE_EVENT"
COMMUNITY_TAB_TOGGLE_EVENT = carb.events.type_from_string(COMMUNITY_TAB_TOGGLE_GLOBAL_EVENT)
omni.kit.app.register_event_alias(COMMUNITY_TAB_TOGGLE_EVENT, COMMUNITY_TAB_TOGGLE_GLOBAL_EVENT)

REMOTE_IMAGE_SUPPORTED_EXTS = {".png"}

# temporary until info is added to the toml's
core_exts_list = None
example_exts_list = None
deprecated_exts_list = None
internal_exts_list = None
version_locked_exts_list = None


def path_is_parent(parent_path, child_path):
    """Checks if the parent_path is a parent of child_path.

    Args:
        parent_path (str): The potential parent directory path.
        child_path (str): The path of the potential child."""
    try:
        return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])
    except ValueError:
        return False


def is_in_omni_documents(path):
    """Checks if the given path is within the Omni Documents directory.

    Args:
        path (str): The file system path to check."""
    return path_is_parent(get_omni_documents_path(), path)


@lru_cache()
def get_icons_path() -> str:
    assert EXT_ROOT is not None, "This function should be called only after EXT_ROOT is set"
    return f"{EXT_ROOT}/icons"


@lru_cache()
def get_omni_documents_path() -> str:
    return os.path.abspath(carb.tokens.get_tokens_interface().resolve("${omni_documents}"))


@lru_cache()
def get_kit_path() -> str:
    return os.path.abspath(carb.tokens.get_tokens_interface().resolve("${kit}"))


@lru_cache()
def get_categories() -> Dict:
    icons_path = get_icons_path()

    categories = {
        "animation": {"name": "Animation", "image": f"{icons_path}/data/category-animation.svg"},
        "graph": {"name": "Graph", "image": f"{icons_path}/data/category-graph.svg"},
        "rendering": {"name": "Lighting & Rendering", "image": f"{icons_path}/data/category-rendering.svg"},
        "audio": {"name": "Audio", "image": f"{icons_path}/data/category-audio.svg"},
        "simulation": {"name": "Simulation", "image": f"{icons_path}/data/category-simulation.svg"},
        "services": {"name": "Services", "image": f"{icons_path}/data/category-internal.svg"},
        "materials": {"name": "Materials", "image": f"{icons_path}/data/category-rendering.svg"},
        "utilities": {"name": "Utilities", "image": f"{icons_path}/data/category-other.svg"},
        "tools": {"name": "Tools", "image": f"{icons_path}/data/category-internal.svg"},
        "ui": {"name": "UI", "image": f"{icons_path}/data/category-core.svg"},
        "browsers": {"name": "Browsers", "image": f"{icons_path}/data/category-app.svg"},
        "other": {"name": "Other", "image": f"{icons_path}/data/category-internal.svg"},
        "app": {"name": "App", "image": f"{icons_path}/data/category-app.svg"},
    }

    return categories


# temporary until info is added to the toml's
def get_core_exts() -> list:
    """Retrieves a list of core extensions from the settings.

    Returns:
        The list of core extension identifiers.
    """
    global core_exts_list

    if not core_exts_list:
        core_exts_list = carb.settings.get_settings().get("/exts/omni.kit.window.extensions/core_exts")
    return core_exts_list


# temporary until info is added to the toml's
def get_example_exts() -> list:
    """Retrieves a list of example extensions from the application settings.

    Returns:
        list: A list containing the names of example extensions stored in the application settings."""
    global example_exts_list

    if not example_exts_list:
        example_exts_list = carb.settings.get_settings().get("/exts/omni.kit.window.extensions/example_exts")
    return example_exts_list


# temporary until info is added to the toml's
def get_internal_exts() -> list:
    """Retrieves a list of internal extensions.

    Returns:
        list: A list of internal extensions that have been marked as such within the application settings."""
    global internal_exts_list

    if not internal_exts_list:
        internal_exts_list = carb.settings.get_settings().get("/exts/omni.kit.window.extensions/internal_exts")
    return internal_exts_list


# temporary until info is added to the toml's
def get_deprecated_exts() -> list:
    """Retrieves a list of deprecated extensions.

    Returns:
        list: A list containing the identifiers of deprecated extensions."""
    global deprecated_exts_list

    if not deprecated_exts_list:
        deprecated_exts_list = carb.settings.get_settings().get("/exts/omni.kit.window.extensions/deprecated_exts")
    return deprecated_exts_list


def get_version_locked_exts() -> list:
    """Retrieves a list of version locked extensions.

    Returns:
        list: A list containing the identifiers of version locked extensions."""
    global version_locked_exts_list

    if version_locked_exts_list is None:
        appext = carb.settings.get_settings().get("/app/exts")
        version_locked_exts_list = []
        if appext.get("enabled"):
            version_locked_exts_list = appext["enabled"]
    return version_locked_exts_list


class ExtSource(Enum):
    NVIDIA = 0
    THIRD_PARTY = 1

    def get_ui_name(self):
        return "NVIDIA" if self == ExtSource.NVIDIA else "THIRD PARTY"


class ExtAuthorGroup(Enum):
    NVIDIA = 0
    PARTNER = 1
    COMMUNITY_VERIFIED = 2
    COMMUNITY_UNVERIFIED = 3
    USER = 4

    def get_ui_name(self):
        if self == ExtAuthorGroup.NVIDIA:
            return "NVIDIA"
        if self == ExtAuthorGroup.PARTNER:
            return "PARTNER"
        if self == ExtAuthorGroup.USER:
            return "USER"
        return "COMMUNITY"


def get_registries():
    """Retrieves a generator that yields registry information.

    Returns:
        Generator[Tuple[str, str, bool]]: A generator that produces tuples containing the registry name, the URL of the registry,
            and a boolean flag indicating whether the registry is a user registry."""
    settings = carb.settings.get_settings()
    settings_dict = settings.get_settings_dictionary("")
    for key, is_user in [(REGISTRIES_SETTING, False), (USER_REGISTRIES_SETTING, True)]:
        for r in settings_dict.get(key[1:], []):
            name = r.get("name", "")
            url = r.get("url", "")
            url = carb.tokens.get_tokens_interface().resolve(url)
            yield name, url, is_user


@lru_cache()
def get_registry_url(registry_name):
    version = get_setting("/app/extensions/registryVersion", "NOT_SET")
    for name, url, _ in get_registries():
        if name == registry_name:
            return f"{url}/{version}"
    return None


class ExtensionCommonInfo:
    """A class to store and manage common information about an extension.

    This class encapsulates various details about an extension such as its ID, information,
    whether it is local or not, and other metadata. It also contains methods to resolve
    extension dependencies and evaluate whether an extension can be toggled.

    Args:
        ext_id (str): The unique identifier for the extension.
        ext_info (dict): A dictionary containing information about the extension.
        is_local (bool): A flag indicating whether the extension is local."""

    def __init__(self, ext_id, ext_info, is_local):
        """Initializes the common information for an extension."""
        self.id: str = ext_id
        package_dict = ext_info.get("package", {})
        self.fullname: str = package_dict["name"]
        self.title: str = package_dict.get("title", "").upper() or self.fullname
        self.name: str = self.title.lower()  # used for sorting
        self.description: str = package_dict.get("description", "") or "No Description"
        self.version: Optional[str] = package_dict.get("version", None)
        self.keywords: list[str] = package_dict.get("keywords", [])
        self.toggleable: bool = package_dict.get("toggleable", True)
        self.feature: bool = ext_controller.is_kit_featured_ext(self.fullname) or package_dict.get("feature", False)
        self.authors: str = package_dict.get("authors", "")
        self.repository: str = package_dict.get("repository", "")
        self.package_id: str = package_dict.get("packageId", "")
        self.is_kit_file: bool = ext_info.get("isKitFile", False)
        self.is_app: bool = ("app" in self.keywords) or package_dict.get("app", self.is_kit_file)
        self.is_startup: bool = ext_controller.is_startup_ext(self.fullname)
        self.is_startup_version: bool = ext_controller.is_startup_ext(ext_id)
        self.is_featured: bool = ext_controller.is_featured_ext(self.fullname)
        self.is_local: bool = is_local
        state_dict = ext_info.get("state", {})
        self.failed: bool = state_dict.get("failed", False)
        self.enabled: bool = state_dict.get("enabled", False)
        self.reloadable: bool = state_dict.get("reloadable", False)
        self.is_pulled: bool = state_dict.get("isPulled", False)
        self.is_toggle_blocked: bool = (self.enabled and not self.reloadable) or (not self.toggleable)
        self.path: str = ext_info.get("path", "")
        self.provider_name: Optional[str] = None

        # get support level
        support_level = package_dict.get("support_level", "")
        if support_level:
            self.is_core: bool = support_level.lower() in ("enterprise", "core")
            self.is_sample: bool = support_level.lower() in ("example", "sample")
            self.is_internal: bool = support_level.lower() == "internal"
        else:
            # temporary until info is added to the toml's
            self.is_core: bool = self.fullname in get_core_exts()
            self.is_sample: bool = self.fullname in get_example_exts()
            self.is_internal: bool = self.fullname in get_internal_exts()

        if not self.is_core and not self.is_sample and not self.is_internal:
            self.is_sample = True

        # get deprecation_msg
        self.is_deprecated = False
        self.deprecation_msg: str = ""
        deprecation_dict = ext_info.get("deprecation", None)
        if deprecation_dict and "warning" in deprecation_dict:
            self.is_deprecated: bool = True
            self.deprecation_msg: str = deprecation_dict["warning"]
        else:
            # temporary until info is added to the toml's
            #
            # stand-in for getting deprecation string and core flag
            # Some extensions in registry added `[Deprecated]` into their extension title
            if "Deprecated" if (self.fullname in get_deprecated_exts() or "deprecated" in self.title.lower()) else "":
                self.is_deprecated: bool = True
                self.deprecation_msg: str = "Extension deprecated since Kit 106.0 and is no longer supported."

        # Only if solve_extensions is called
        self.non_toggleable_deps: list[str] = []
        self.solver_error: str = ""
        self.solver_result = None
        self.solver_exts = []

        self.category: str = package_dict.get("category", "other").lower()

        # Ext sources
        self.author_group: str = ""
        if package_dict.get("exchange", False):
            if package_dict.get("partner", False):
                self.author_group = ExtAuthorGroup.PARTNER
            else:
                self.author_group = ExtAuthorGroup.COMMUNITY_VERIFIED
        elif not package_dict.get("trusted", True):
            self.author_group = ExtAuthorGroup.COMMUNITY_UNVERIFIED
        else:
            self.author_group = ExtAuthorGroup.NVIDIA

        # Extension location tag for UI and user extensions
        self.location_tag: str = ""
        if is_local:
            abs_path = os.path.abspath(self.path)
            if ext_info.get("isInCache", False):
                self.location_tag = "INSTALLED"
            elif self.author_group == ExtAuthorGroup.NVIDIA and (
                ext_info.get("isUser", False) or is_in_omni_documents(abs_path)
            ):
                self.author_group = ExtAuthorGroup.USER
            else:
                git_ext = get_extpath_git_ext()
                if git_ext and path_is_parent(git_ext.get_cache_path(), abs_path):
                    self.location_tag = "GIT"

        # Finalize source
        self.ext_source: ExtSource = (
            ExtSource.NVIDIA if self.author_group == ExtAuthorGroup.NVIDIA else ExtSource.THIRD_PARTY
        )
        self.is_untrusted: bool = self.author_group == ExtAuthorGroup.COMMUNITY_UNVERIFIED

        # Remote exts
        if not is_local:
            self.location_tag = "REMOTE"
            self.provider_name = ext_info.get("registryProviderName", None)

        # categories
        categories = get_categories()

        # add app category
        if self.is_app:
            self.category = "app"

        # If unknown category -> fallback to other
        if self.category not in categories:
            self.category = "other"

        # For icon by default use category icon, can be overridden with custom:
        self.icon_path: str = self._build_image_resource_path(ext_info, "icon", categories[self.category]["image"])
        # For preview image there is no default
        self.preview_image_path: str = self._build_image_resource_path(ext_info, "preview_image")

    def _build_image_resource_path(self, ext_info, key, default_path=None):
        package_dict = ext_info.get("package", {})
        resource_path = default_path
        if self.is_local:
            path = package_dict.get(key, None)
            if path:
                icon_path = os.path.join(self.path, path)
                if os.path.exists(icon_path):
                    resource_path = icon_path
        else:
            try:
                from omni.kit.registry.nucleus import get_package_resource_url_by_key
            except ImportError:
                return default_path

            url = get_package_resource_url_by_key(key + "_remote", ext_info)
            if url and os.path.splitext(url)[1] in REMOTE_IMAGE_SUPPORTED_EXTS:
                return url

            return default_path
        return resource_path

    def solve_extensions(self):
        """Solves the extension dependencies to determine non-toggleable dependencies and potential solver errors."""
        # This function is costly, so we don't run it for each item. Only on demand when UI shows selected extension.
        manager = omni.kit.app.get_app().get_extension_manager()

        # Get all enabled extensions, but exclude itself
        exts = manager.get_extensions()
        exts_to_enable = [e["id"] for e in exts if e["enabled"] and e["name"] != self.fullname]
        exts_to_enable.append(self.id)

        # /app/extensions/maxSolverIterationCount = 10000000

        # Reduce max solver iterations to avoid long waits in worse scenario. The default is 10000000, make it 10 times faster:
        with change_setting("/app/extensions/maxSolverIterationCount", 1000000):
            self.solver_result, self.solver_exts, self.solver_error = manager.solve_extensions(
                exts_to_enable, add_enabled=False, return_only_disabled=True
            )
        if not self.solver_result:
            self.failed = True

        self.non_toggleable_deps = []
        if self.solver_result:
            for ext in self.solver_exts:
                ext_dict, _ = get_ext_info_dict(manager, ext)
                if not ext_dict.get("package", {}).get("toggleable", True):
                    self.non_toggleable_deps.append(ext["id"])


def build_ext_info(ext_id, package_id=None) -> Tuple[ExtensionCommonInfo, dict]:
    """Builds extension information and creates an ExtensionCommonInfo instance.

    Args:
        ext_id (str): The unique identifier of the extension.
        package_id (Optional[str]): The package identifier, defaults to ext_id if not provided.

    Returns:
        Tuple[ExtensionCommonInfo, dict]: A tuple containing the ExtensionCommonInfo instance and the extension info dictionary.

    Raises:
        AssertionError: If the function is called before EXT_ROOT is set."""
    from .ext_data_fetcher import get_ext_data_fetcher

    ext_data_fetcher = get_ext_data_fetcher()

    manager = omni.kit.app.get_app().get_extension_manager()
    package_id = package_id or ext_id
    ext_info_remote = manager.get_registry_extension_dict(package_id)
    ext_info_local = manager.get_extension_dict(ext_id)

    # prefer full remote data if available
    if ext_info_remote:
        ext_info_remote_full = ext_data_fetcher.get_ext_data(ext_info_remote.get("package", {}).get("packageId"))
        ext_info_remote = ext_info_remote_full or ext_info_remote

    is_local = ext_info_local is not None
    ext_info = ext_info_local or ext_info_remote

    if not ext_info:
        return None, None

    if not isinstance(ext_info, dict):
        ext_info = ext_info.get_dict()  # convert to python dict to prolong lifetime

    return ExtensionCommonInfo(ext_id, ext_info, is_local), ext_info


def check_can_be_toggled(ext_id: str):
    """Determines if an extension can be toggled."""

    ext_item, _ = build_ext_info(ext_id)

    if not ext_item:
        return False

    # already enabled?
    if ext_item.enabled:
        return True

    if ext_item:
        ext_item.solve_extensions()
        return not ext_item.failed
    return False


def check_can_be_toggled_with_popup(ext_id: str, for_autoload=False):
    """Determines if an extension can be toggled.

    Args:
        ext_id (str): Unique identifier of the extension.
        for_autoload (bool): If checking for auto-loading on startup.

    Returns:
        bool: True if the extension can be toggled, False otherwise."""
    ext_item, _ = build_ext_info(ext_id)
    if ext_item:
        # Below we want to run solver and check if extension can be enabled.
        # However, if user already has another version of the same extension enabled the solver will report a conflict.
        # To work it around we ask user to disable the other version first. But this is not possible for non-toggleable
        # extensions. For those we just skip that check. And rely on check of autoloaded extensions on startup.
        if for_autoload:
            if not ext_item.toggleable:
                return True

            # check other version already enabled
            manager = omni.kit.app.get_app().get_extension_manager()
            extensions = manager.fetch_extension_versions(ext_item.fullname)
            for e in extensions:
                if e["enabled"] and e["id"] != ext_id:
                    text = f"Extension {ext_item.fullname} already has another version enabled: {e['id']}.\n"
                    text += "Disable it first to set this version to autoload."
                    asyncio.ensure_future(show_ok_popup("Error", text))
                    return False

        ext_item.solve_extensions()

        # Error to solve?
        if ext_item.solver_error:
            text = "Failed to solve all extension dependencies:"
            text += f"\n{ext_item.solver_error}"
            asyncio.ensure_future(show_ok_popup("Error", text))
            return False

        if not for_autoload and ext_item.non_toggleable_deps:
            text = "This extension cannot be enabled at runtime.\n"
            text += "Some of dependencies require an app restart to be enabled (toggleable=false):\n\n"
            for ext in ext_item.non_toggleable_deps:
                text += f" * {ext}\n"
            text += "\n\n"
            text += "Set this extension to autoload and restart an app to enable it."
            asyncio.ensure_future(show_ok_popup("Warning", text))
            return False
    return True


def toggle_extension(ext_id: str, enable: bool):
    """Toggles the state of an extension.

    Args:
        ext_id (str): The unique identifier of the extension to toggle.
        enable (bool): Whether to enable (`True`) or disable (`False`) the extension.
    """
    if enable and not check_can_be_toggled_with_popup(ext_id):
        return False

    if ext_id.startswith("omni.kit.window.extensions-") or ext_id.startswith(
        "omni.kit.widget.ext_win.dependency_graph-"
    ):

        async def toggle_self(ext_id):
            if not enable:
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
            omni.kit.commands.execute("ToggleExtension", ext_id=ext_id, enable=enable)

        asyncio.ensure_future(toggle_self(ext_id))
        return True

    omni.kit.commands.execute("ToggleExtension", ext_id=ext_id, enable=enable)
    return True


async def pull_extension_async(ext_item: ExtensionCommonInfo, on_pull_started_fn: Callable = None):
    """Pulls an extension asynchronously.

    Args:
        ext_item (:obj:`ExtensionCommonInfo`): The extension to be pulled.
        on_pull_started_fn (Callable): Optional; function to call when pull starts."""

    if ext_item.is_untrusted:
        cancel = False

        def on_cancel(dialog):
            nonlocal cancel
            cancel = True
            dialog.hide()

        message = """
    ATTENTION: UNVERIFIED COMMUNITY EXTENSION

    This extension will be installed directly from the repository (see "Repo Url").
    It is not verified by NVIDIA and may contain bugs or malicious code. Do you want to proceed?
    """
        await show_ok_popup(
            "Warning",
            message,
            ok_label="Install",
            cancel_label="Cancel",
            disable_cancel_button=False,
            cancel_handler=on_cancel,
            width=600,
        )

        if cancel:
            return

    ext_manager = omni.kit.app.get_app().get_extension_manager()
    ext_manager.pull_extension_async(ext_item.id)
    # if we know the list of dependencies, we can start pulling them too:
    if ext_item.solver_result:
        for ext in ext_item.solver_exts:
            ext_manager.pull_extension_async(ext["id"])
    omni.kit.app.queue_event(EXTENSION_PULL_STARTED_GLOBAL_EVENT)
    if on_pull_started_fn:
        on_pull_started_fn()


async def pull_extension_async_by_name(ext_name: str):
    """Pulls the extension with the specified name asynchronously.

    Args:
        ext_name (str): The name of the extension to pull."""
    manager = omni.kit.app.get_app().get_extension_manager()

    # Fetch extension versions, to pick the latest compatible to install
    extensions = manager.fetch_extension_versions(ext_name)
    if not extensions:
        await show_ok_popup("Error", f"Can't install: no compatible packages of extension {ext_name} found.")
        return
    # First version is the latest in that list
    default_ext = extensions[0]
    ext_item, _ = build_ext_info(default_ext["id"], default_ext["package_id"])
    if not ext_item:
        await show_ok_popup("Error", f"Can't install: extension {ext_name} not found.")
        return
    # Install it
    await pull_extension_async(ext_item)


class SettingBoolValue:
    """A class for managing a boolean setting value.

    This class encapsulates a boolean setting, providing methods to get and set the value, while also handling the persistence of the setting.

    Args:
        path (str): The setting path in the settings registry.
        default (bool): The default boolean value to use if the setting is not already set."""

    def __init__(self, path: str, default: bool):
        """Initializes the SettingBoolValue with a specific settings path and default value."""
        self._path = path
        self._value = set_default_and_get_setting(path, default)

    def get(self) -> bool:
        """Returns the current boolean value of the setting."""
        return self._value

    def set_bool(self, value: bool):
        """Sets the boolean value of the setting and updates the application settings.

        Args:
            value (bool): The new boolean value to set for the setting."""
        self._value = value
        carb.settings.get_settings().set(self._path, self._value)

    def __bool__(self):
        return self.get()


def build_doc_urls(ext_item: ExtensionCommonInfo) -> List[str]:
    """Produce possible candidates for doc urls

    Args:
        ext_item (:obj:`ExtensionCommonInfo`): The extension to generate documentation URLs for.

    Returns:
        List[str]: A list of possible documentation URLs."""

    # Base url
    if omni.kit.app.get_app().is_app_external():
        doc_url = get_setting("/exts/omni.kit.window.extensions/docUrlExternal", "")
    else:
        doc_url = get_setting("/exts/omni.kit.window.extensions/docUrlInternal", "")
    if not doc_url:
        return []

    # Build candidates. Prefer exact version, fallback to just a link to latest
    candidates = []
    for v in [ext_item.version, "latest", ""]:
        candidates.append(Template(doc_url).safe_substitute({"version": v, "extName": ext_item.fullname}))

    return candidates


@lru_cache()
def is_community_tab_always_enabled() -> bool:
    return get_setting("/exts/omni.kit.window.extensions/communityTabEnabled", True)


def is_community_tab_enabled_as_option() -> bool:
    """Checks if the community tab is enabled as an option in the application settings.

    Returns:
        bool: True if the community tab is enabled as an option, False otherwise."""
    if is_community_tab_always_enabled():
        return False
    return get_setting("/exts/omni.kit.window.extensions/communityTabOption", True)


class ExtOptions:
    """A class for managing extension options within the application.

    This class encapsulates various settings and preferences related to the handling and presentation of extensions in the application. It includes options for enabling or disabling the community tab, as well as managing publishing settings. The settings are stored persistently across sessions.
    """

    def __init__(self):
        """Initializes the ExtOptions with settings for community tab and publishing preferences."""
        self.community_tab = None
        if is_community_tab_enabled_as_option():
            self.community_tab = SettingBoolValue(
                "/persistent/exts/omni.kit.window.extensions/communityTabEnabled", default=False
            )

        self.publishing = SettingBoolValue(
            "/persistent/exts/omni.kit.window.extensions/publishingEnabled", default=False
        )

        # Stop showing update button on the list by default, it is not correct.
        # For performance reasons we can't run solver for each item in the list to figure out if it can be updated:
        self.show_update_icon = SettingBoolValue(
            "/persistent/exts/omni.kit.window.extensions/showUpdateIcon", default=False
        )


@lru_cache()
def get_options() -> ExtOptions:
    return ExtOptions()


def is_community_tab_enabled() -> bool:
    """Checks if the community tab is enabled in the application.

    Returns:
        bool: True if the community tab is enabled, False otherwise."""
    # Can be either always enabled, or as a toggleable preference
    if is_community_tab_always_enabled():
        return True

    return get_options().community_tab is not None and get_options().community_tab


@lru_cache()
def get_open_example_links():
    return get_setting("/exts/omni.kit.window.extensions/openExampleLinks", [])


class PageBase:
    """
    Interface for any classes adding Tabs to the Extension Manager UI
    """

    @abc.abstractmethod
    def build_tab(self, ext_info: dict, ext_item: ExtensionCommonInfo) -> None:
        """Builds the tab for the given extension information.

        Args:
            ext_info (dict): The extension information.
            ext_item (:obj:`ExtensionCommonInfo`): The common extension item."""

    @abc.abstractmethod
    def destroy(self) -> None:
        """Destroys the tab, releasing any resources or subscriptions."""

    @staticmethod
    @abc.abstractmethod
    def get_tab_name() -> str:
        """Retrieves the name of the tab.

        Returns:
            str: The name of the tab."""

    @abc.abstractmethod
    def sort_index(self):
        return "999LastPage"
