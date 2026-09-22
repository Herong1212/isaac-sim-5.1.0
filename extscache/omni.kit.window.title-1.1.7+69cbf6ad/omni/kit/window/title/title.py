# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb.eventdispatcher
import carb.settings
import carb.tokens
import carb.windowing

import omni.appwindow
import omni.ext
import omni.kit.app
import omni.usd

import time
import urllib.parse

main_window_title = None


def get_main_window_title():
    """Return the global main window title variable.

    Returns:
        object: The current main window title, which may be None or an instance set by WindowTitle.
    """
    return main_window_title


class WindowTitle(omni.ext.IExt):
    """A class for managing and updating the application window title.

    This class provides functionality to configure and update the title of an Omni UI application window by composing several components including the app name, the app version, title text, and additional title decor. It automatically observes events from the USD context such as stage opening, dirty state changes, and stage closing to ensure that the displayed title accurately reflects the current state of the application.

    The title is constructed using resolved values from Carb settings and tokens interfaces and is applied to the default application window through the windowing interface. Changes to any of the title components are immediately updated in the complete title string, which may include suffixes like a modified indicator or a read-only flag based on the stage state.

    Usage example:
    .. code-block:: python

      window_title = WindowTitle()
      window_title.set_app_name('MyApp')
      window_title.set_app_version('1.0.0')
      window_title.set_title('Main Interface')
      window_title.set_title_decor('- Running')

    This class ensures that the application window title is consistently maintained as the central point of reference for the application status.
    """

    def on_startup(self, ext_id):
        """Initializes extension and sets up window title components and event listeners.

        Args:
            ext_id (str): Extension identifier.
        """
        self._app_name = ""
        self._app_version = ""
        self._title = ""
        self._title_decor = ""
        self._full_title = ""
        self._listener = None

        self._app = omni.kit.app.get_app()
        self._settings = carb.settings.get_settings()

        self._usd_context = omni.usd.get_context()

        self._stage_event_sub = [
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                observer_name="omni.kit.window.title",
                event_name=self._usd_context.stage_event_name(event),
                on_event=func,
            )
            for event, func in (
                (omni.usd.StageEventType.OPENED, lambda _: self._update_title()),
                (omni.usd.StageEventType.DIRTY_STATE_CHANGED, lambda _: self._update_title()),
                (omni.usd.StageEventType.CLOSING, lambda _: self._on_stage_closing()),
            )
        ]
        if self._usd_context.get_stage_state() == omni.usd.StageState.OPENED:
            self._update_title()

        # default value
        tokens = carb.tokens.get_tokens_interface()
        self._app_name = tokens.resolve(self._settings.get("/app/window/title"))
        self._app_version = tokens.resolve(self._settings.get("/exts/omni.kit.window.title/version"))
        self._apply()

        # Default polling interval is 500ms (or 0.5s)
        self._settings.set_default("/exts/omni.kit.window.title/pollIntervalMS", 500.0)
        self._poll_interval_s = self._settings.get("/exts/omni.kit.window.title/pollIntervalMS") / 1000.0

        global main_window_title
        main_window_title = self

    @property
    def _windowing(self):
        carb.log_error("WindowTitle._windowing is deprecated, use carb.windowing.acquire_windowing_interface()")
        return carb.windowing.acquire_windowing_interface()

    @property
    def _window(self):
        carb.log_error("WindowTitle._window is deprecated, use omni.appwindow.get_default_app_window()")
        return omni.appwindow.get_default_app_window()

    def on_shutdown(self):
        """Performs shutdown tasks by clearing the main window title and stage event subscriptions."""
        global main_window_title
        main_window_title = None
        self._stage_event_sub = None

    def set_app_name(self, name: str):
        """Sets app name on title bar. This is the first element on the title bar string.

        Args:
            name (str): App name to be set to.
        """
        if self._app_name != name:
            self._app_name = name
            self._apply()

    def set_app_version(self, version: str):
        """Sets app version on title bar. This is the second element on the title bar string, after app name.

        Args:
            version (str): App version to be set to.
        """
        if self._app_version != version:
            self._app_version = version
            self._apply()

    def set_title(self, title: str):
        """Sets title text on title bar. This is the third element on the title bar string, after app name and version.

        Args:
            title (str): App title to be set to.
        """
        # OM-64018: need to unquote the chars in the title string
        title = urllib.parse.unquote(title)
        if self._title != title:
            self._title = title
            self._apply()

    def set_title_decor(self, title_decor: str):
        """Sets title decor on title bar. This is at the end of the title string.

        Args:
            title_decor (str): Title decor to be set to.
        """
        if self._title_decor != title_decor:
            self._title_decor = title_decor
            self._apply()

    def get_full_title(self):
        """Gets the full title.

        Returns:
            str: Full title string.
        """
        return self._full_title

    def _apply(self):
        self._full_title = self._app_name
        if self._app_version:
            self._full_title += f" {self._app_version}"
        if len(self._title) > 0:
            self._full_title += f" - {self._title}{self._title_decor}"

        window = omni.appwindow.get_default_app_window()
        if not window:
            carb.log_error("Cannot set window title without a default window")
            return False

        # Lack of a backing os window, just means no success; don't emit an error (for testing reasons as of now)
        window = window.get_window()
        if not window:
            carb.log_info("Cannot set window title on a virtual Window")
            return False

        # We don't have a way to acquire interface without throwing on missing implementation in Carbonite,
        # so for now we have to work this around with try/except block.
        windowing = None
        try:
            windowing = carb.windowing.acquire_windowing_interface()
            windowing.set_window_title(window, self._full_title)
            return True
        except:
            carb.log_error(
                "Could not set window title on default window, {}".format(
                    "set_window_title failed" if windowing else "carb.windowing interface not available"
                )
            )
        return False

    def set_title_url(self):
        """Sets the title on the title bar using the stage URL from USD context. If the stage is not writable, appends read-only status."""
        title = "New Stage" if self._usd_context.is_new_stage() else self._usd_context.get_stage_url()
        if not self._usd_context.is_writable():
            title += " (read-only)"
        self.set_title(title)

    def _on_stage_closing(self):
        self.set_title("")
        self.set_title_decor("")

    def _update_title(self):
        self.set_title_url()
        dirty = self._usd_context.has_pending_edit()
        if dirty and self._title_decor != "*":
            self.set_title_decor("*")
        elif not dirty and self._title_decor == "*":
            self.set_title_decor("")
