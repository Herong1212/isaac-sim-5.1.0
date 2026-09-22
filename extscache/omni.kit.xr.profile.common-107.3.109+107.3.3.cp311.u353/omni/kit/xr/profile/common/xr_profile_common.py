# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

from typing import Any, List, Union

import carb
import omni.appwindow
import omni.ui
from omni.kit.xr.advertise import XRAdvertizer
from omni.kit.xr.core import XRCore, XRCoreEventType, XRProfile, XRWeakMethod
from omni.kit.xr.ui.window.profile import XRProfileSettingsWindow

from .xr_disable_save import XRDisableSave


class XRProfileCommon:
    def __init__(self):
        super().__init__()

        components = self.__module__.split(".")
        name = components[4]
        extension_name = ".".join(components[0:5])

        self.__name = name
        self.__extension_name = extension_name
        self.__window = None
        self.__profile = XRCore.get_singleton().get_profile(self.__name)
        self.__subs = []
        self.__previous_content_path = None
        self.__previous_layout = None
        self.__active = False
        self.__need_unset = False
        self.__reset_fullscreen = False

        activate_profile_fn = XRWeakMethod(self._activate_profile)
        deactivate_profile_fn = XRWeakMethod(self._deactivate_profile)

        open_file_fn = XRWeakMethod(self._open_file)
        update_fn = XRWeakMethod(self._on_update)

        core_event_stream = XRCore.get_singleton().get_message_bus()

        self.__subs.append(
            core_event_stream.create_subscription_to_pop_by_type(
                XRCoreEventType.post_sync_update,
                lambda *_: update_fn(),
                name="XRViewportController Post Sync Update",
            )
        )

        self.__subs.append(
            core_event_stream.create_subscription_to_pop_by_type(
                XRCoreEventType.profile_enable(self.__profile.get_name()), lambda *_: activate_profile_fn()
            )
        )

        self.__subs.append(
            core_event_stream.create_subscription_to_pop_by_type(
                XRCoreEventType.profile_disable(self.__profile.get_name()), lambda *_: deactivate_profile_fn()
            )
        )

        self.__subs.append(
            omni.usd.get_context()
            .get_stage_event_stream()
            .create_subscription_to_pop_by_type(
                omni.usd.StageEventType.SETTINGS_LOADED, lambda *_: open_file_fn(), 10, name="On open while in XR"
            )
        )

    def on_profile_startup(self) -> None:
        pass

    def on_profile_shutdown(self) -> None:
        pass

    def on_startup(self) -> None:
        self.on_profile_startup()

    def on_shutdown(self) -> None:

        self.__subs = []
        self._reset_settings()
        self.__profile._reset_settings_ar()

        self.on_profile_shutdown()
        self.destroy()

    def setup_settings_window(
        self, components: Any, icons: Union[None, List[str]] = None, show_message: bool = False
    ) -> XRProfileSettingsWindow:
        """
        Create a settings window for this profile
        """
        self.__window = XRProfileSettingsWindow(
            self.__name,
            self.__extension_name,
            components,
            icons,
            show_message,
        )

        return self.__window

    def setup_zero_conf(self):
        self.__zero_conf = XRAdvertizer()
        self.__zero_conf.set_profile_name(self.__name)

    def set_ar_mode(self, ar_mode):
        self.__profile.set_ar_mode(ar_mode)

    def disable_saving(self):
        """
        Disable saving when profile is enabled
        """
        XRDisableSave.get_singleton().add_profile(self.__name)

    def get_default_render_quality_items(self) -> dict:
        """
        Get the default render quality items
        """
        return {
            "Performance": "performance",
            "Balanced": "balanced",
            "Quality": "quality",
            "Stage": "off",
        }

    def get_name(self) -> str:
        """
        Get the name of the profile
        """
        return self.__name

    def get_extension_name(self) -> str:
        """
        Get the name of the extension this profile is defined
        """
        return self.__extension_name

    def get_profile_name(self) -> str:
        """
        Get name of profile
        """
        return self.__profile.get_name()

    def get_profile_path(self) -> str:
        return self.__profile.get_profile_path()

    def get_persistent_path(self) -> str:
        """
        Get path to the persistent settings in profile
        """
        return self.__profile.get_persistent_path()

    def get_non_persistent_path(self) -> str:
        """
        Get path to the non persistent settings in profile
        """
        return self.__profile.get_non_persistent_path()

    def get_scene_persistent_path(self) -> str:
        """
        Get path to the stage persistent settings in profile
        """
        return self.__profile.get_scene_persistent_path()

    def get_profile(self) -> XRProfile:
        """
        Get the underlying profile class
        """
        return self.__profile

    def get_window_name(self) -> str:
        """
        Get the name of the window
        """
        return self.__window.get_display_name()

    def destroy(self):
        """
        Destroy all subscriptions and windows
        """

        self.__window = None
        self.__subs = None
        XRDisableSave.get_singleton().remove_profile(self.__name)

    def on_activate_profile(self) -> None:
        """
        Override this class to add function to be called when profile is activated.
        """
        pass

    def on_deactivate_profile(self) -> None:
        """
        Override this class to add function to be called when profile is deactivated.
        """

        pass

    def on_open_file(self) -> None:
        """
        Override this class to add function to be called when a file is opened in XR
        """
        pass

    def _activate_profile(self) -> None:
        """
        Called internally when this profile is activated
        """

        self.__active = True

        self._activate_layout()

        self._update_settings()
        self.__profile._update_settings_ar()

        self.on_activate_profile()

    def _deactivate_profile(self) -> None:
        """
        Called when this profile is deactivated
        """

        self.__active = False

        self._reset_settings()
        self.__profile._reset_settings_ar()

        self._deactivate_layout()

        self.on_deactivate_profile()

    def _on_update(self) -> None:

        if self.__profile.get_ar_mode() and self.__active:
            settings = carb.settings.get_settings()
            settings.set("/rtx/post/backgroundZeroAlpha/enabled", True)

    def _open_file(self) -> None:
        """
        Called when a file is opened
        """

        if self.__active:

            self._update_settings()
            self.__profile._update_settings_ar()

            self.on_open_file()

    def _get_current_browser_directory(self):
        import omni.kit.window.content_browser

        instance = omni.kit.window.content_browser.extension.get_instance()
        if instance is not None:
            return instance.get_current_directory()
        return None

    def _activate_layout(self) -> None:
        """
        Activate a specific layout
        """
        guiMode = carb.settings.get_settings().get(self.get_persistent_path() + "app/guiMode")

        if guiMode == "current" or guiMode is None:
            return

        if guiMode == "fullscreen":
            # Need status bar to give an easy way out of fullscreen mode
            carb.settings.get_settings().set("/xr/status/fullscreen", True)
            app_window = omni.appwindow.get_default_app_window()

            self.__old_fullscreen = app_window.is_fullscreen()
            self.__reset_fullscreen = True

            app_window.set_fullscreen(True)
            carb.settings.get_settings().set("/app/window/hideUi", True)

            return

        self.__previous_layout = omni.ui.Workspace.dump_workspace()

        # short workaround to restore content browser path
        self.__previous_content_path = self._get_current_browser_directory()

        window_names = ["DockSpace", "Viewport", self.get_window_name()]
        lower_window_names = [x.lower() for x in window_names]
        for w in omni.ui.Workspace.get_windows():
            omni.ui.Workspace.show_window(w.title, w.title.lower() in lower_window_names)

    def _deactivate_layout(self) -> None:
        """
        Deactivate specific layout
        """

        if self.__reset_fullscreen is True:

            app_window = omni.appwindow.get_default_app_window()
            carb.settings.get_settings().set("/app/window/hideUi", False)
            app_window.set_fullscreen(self.__old_fullscreen)
            self.__reset_fullscreen = False

        if self.__previous_layout is not None:
            previous_layout = self.__previous_layout
            self.__previous_layout = None

            # short workaround to restore content browser path
            previous_content_path = self.__previous_content_path
            self.__previous_content_path = None

            # Changes need to be made in update cycle
            # otherwise omni.ui may crash

            async def revert_layout():
                import omni.kit.app

                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()

                omni.ui.Workspace.restore_workspace(previous_layout)

                await omni.kit.app.get_app().next_update_async()
                import omni.kit.window.content_browser

                current_content_path = omni.kit.window.content_browser.extension.get_instance().get_current_directory()
                if previous_content_path is not None and current_content_path is None:
                    omni.kit.window.content_browser.extension.get_instance().navigate_to(previous_content_path)

            import asyncio

            asyncio.ensure_future(revert_layout())

    def _update_settings(self) -> None:
        """
        Called on activation
        """
        settings = carb.settings.get_settings()

        self.__need_unset = True
        self.__old_viewport_grid_enabled = settings.get("/app/viewport/grid/enabled")
        self.__old_viewport_outline_enabled = settings.get("/app/viewport/outline/enabled")

        hideGrid: bool = carb.settings.get_settings().get(self.get_persistent_path() + "viewport/grid/hidden")
        if hideGrid:
            settings.set("/app/viewport/grid/enabled", False)

        hideOutline: bool = carb.settings.get_settings().get(self.get_persistent_path() + "viewport/outline/hidden")
        if hideOutline:
            settings.set("/app/viewport/outline/enabled", False)

    def _reset_settings(self) -> None:
        if self.__need_unset:
            settings = carb.settings.get_settings()
            settings.set("/app/viewport/grid/enabled", self.__old_viewport_grid_enabled)
            settings.set("/app/viewport/outline/enabled", self.__old_viewport_outline_enabled)

    def _set_override_value(self, setting_path, value):
        settings = carb.settings.get_settings()

        render_quality_modes = ["performance", "balanced", "quality", "off"]
        changed = False
        for mode in render_quality_modes:
            root = self.__profile.get_non_persistent_path() + "rendersettings/" + mode
            path = root + setting_path
            old_val = settings.get(path)
            if value is not None:
                settings.set(path, value)
            else:
                settings.destroy_item(path)
            changed = changed or (old_val != value)
        return changed
