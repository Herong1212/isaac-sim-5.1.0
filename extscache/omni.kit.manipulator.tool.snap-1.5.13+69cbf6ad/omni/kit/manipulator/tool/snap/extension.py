# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import traceback

import carb
import carb.settings
import omni.ext
import omni.kit.app

from .builtin_snap_tools import __name__ as n
from .menu import SnapMenu
from .provider import SnapProvider
from .registry import RegistrationHelper, SnapProviderRegistry
from .hotkey import SnapHotkey

LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH = "/exts/omni.kit.widget.toolbar/legacySnapButton/enabled"


class SnapToolExt(omni.ext.IExt):
    """An extension for enabling and managing snap tools in the application.

    This class is responsible for the initialization, management, and cleanup of snap tools. It registers and unregisters toolbar buttons, handles hotkeys, and sets up the necessary providers and menus for the snap tool functionality.
    """

    def on_startup(self, ext_id):
        """Initializes the snap tool extension.

        This method sets up the snap provider registry, registration helper, snap menu, hotkey,
        and hooks for the toolbar button.

        Args:
            ext_id (str): The identifier for the extension."""
        self._settings = carb.settings.get_settings()
        self._registry = SnapProviderRegistry()
        self._reg = RegistrationHelper(n, SnapProvider)
        self._menu = SnapMenu()
        self._snap_button_group = None

        def on_snap_hotkey_changed(hotkey: str):
            if self._snap_button_group:
                self._snap_button_group.get_button().tooltip = f"Snap ({hotkey})"

        self._hotkey = SnapHotkey(on_hotkey_changed_fn=on_snap_hotkey_changed)

        self._was_legacy_snap_button_enabled = None
        manager = omni.kit.app.get_app().get_extension_manager()
        self._hooks = manager.subscribe_to_extension_enable(
            lambda _: self._register_main_toolbar_button(),
            lambda _: self._unregister_main_toolbar_button(),
            ext_name="omni.kit.widget.toolbar",
            hook_name="omni.kit.manipulator.tool.snap listener",
        )

    def on_shutdown(self):
        """Cleans up the snap tool extension.

        This method unsubscribes from extension hooks, and destroys the snap button group,
        registration helper, snap menu, hotkey, and registry if they exist."""
        self._hooks = None
        if self._snap_button_group is not None:
            self._unregister_main_toolbar_button()

        if self._reg:
            self._reg.destroy()
            self._reg = None

        if self._menu:
            self._menu.destroy()
            self._menu = None

        if self._hotkey:
            self._hotkey.destroy()
            self._hotkey = None

        if self._registry:
            self._registry.destroy()
            self._registry = None

    def _register_main_toolbar_button(self):
        """Registers the main toolbar button for the snap tool.

        This private method creates and adds the snap button group to the main toolbar.
        It also handles the state of the legacy snap button."""
        try:
            if not self._snap_button_group:
                import omni.kit.widget.toolbar

                from .snap_button_group import SnapButtonGroup

                self._snap_button_group = SnapButtonGroup(self._hotkey, self._menu)

                toolbar = omni.kit.widget.toolbar.get_instance()
                toolbar.add_widget(self._snap_button_group, 11)

                self._was_legacy_snap_button_enabled = self._settings.get(LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH)
                self._settings.set(LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH, False)
        except Exception:
            carb.log_warn(traceback.format_exc())

    def _unregister_main_toolbar_button(self):
        """Unregisters the main toolbar button for the snap tool.

        This private method removes the snap button group from the main toolbar and restores
        the state of the legacy snap button if it was enabled prior to the registration of
        this tool."""
        try:
            if self._snap_button_group:
                import omni.kit.widget.toolbar

                toolbar = omni.kit.widget.toolbar.get_instance()
                toolbar.remove_widget(self._snap_button_group)
                self._snap_button_group.clean()
                self._snap_button_group = None

                if self._was_legacy_snap_button_enabled is not None:
                    self._settings.set(LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH, self._was_legacy_snap_button_enabled)

        except Exception:
            carb.log_warn(traceback.format_exc())
