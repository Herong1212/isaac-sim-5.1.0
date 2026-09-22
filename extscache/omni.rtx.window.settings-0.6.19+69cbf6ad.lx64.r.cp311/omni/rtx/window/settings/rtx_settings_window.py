__all__ = ["RTXSettingsWindow"]

from typing import Callable, Dict, List

import carb
import omni.ui as ui
import omni.usd

from .rtx_settings_widget import RTXSettingsWidget


class RTXSettingsWindow:
    def __init__(self, usd_context_name=""):
        self._window = None
        self.__usd_context_name = usd_context_name
        self.__ui_requested = False
        self.__stacks_requested = False
        self.__new_frame_sub = None
        self.__window_ready = not bool(
            carb.settings.get_settings().get("/exts/omni.rtx.window.settings/startup/waitForHydra1stFrame")
        )

        if carb.settings.get_settings().get("/exts/omni.rtx.window.settings/startup/autoCreateWindow"):
            self._window = ui.Window(
                "Render Settings", width=600, height=600, dockPreference=ui.DockPreference.RIGHT_TOP
            )
            self._window.deferred_dock_in("Stage", ui.DockPolicy.TARGET_WINDOW_IS_ACTIVE)
            self._settings_widget = RTXSettingsWidget(self._window.frame)
            self.__ensure_window_ready(True, False)
        else:
            # placeholder window, so _build_ui & _build_stacks won't do anything
            self._settings_widget = RTXSettingsWidget(None)
            self.__ensure_window_ready(False, False)

    def register_renderer(self, name: str, stacks_list: List[str]) -> None:
        return self._settings_widget.register_renderer(name, stacks_list)

    def get_registered_renderers(self):
        return self._settings_widget.get_registered_renderers()

    def get_current_renderer(self):
        return self._settings_widget.get_current_renderer()

    def set_current_renderer(self, renderer_name: str) -> None:
        return self._settings_widget.set_current_renderer(renderer_name)

    def register_stack(self, name: str, stack_class: Callable) -> None:
        return self._settings_widget.register_stack(name, stack_class)

    def show_stack_from_name(self, name: str) -> None:
        return self._settings_widget.show_stack_from_name(name)

    def get_renderer_stacks(self, renderer_name):
        return self._settings_widget.get_renderer_stacks(renderer_name)

    def get_current_stack(self) -> str:
        return self._settings_widget.get_current_stack()

    def unregister_renderer(self, name):
        return self._settings_widget.unregister_renderer(name)

    def unregister_stack(self, name):
        return self._settings_widget.unregister_stack(name)

    def set_visibility_changed_listener(self, listener):
        if self._window:
            self._window.set_visibility_changed_fn(listener)

    def set_render_settings_to_viewport_renderer(self, *args, **kwargs):
        return self._settings_widget.set_render_settings_to_viewport_renderer(*args, **kwargs)

    def set_visible(self, value: bool) -> None:
        if self._window:
            self._window.visible = value

    def destroy(self) -> None:
        """ """
        self._settings_widget.destroy()
        self._settings_widget = None
        self._window = None

    def _build_ui(self) -> None:
        """ """
        self.__ensure_window_ready(True, True)

    def _build_stacks(self) -> None:
        """
        "stacks" are the tabs in the Render Settings UI that contain groups of settings
        They can be reused amongst different renderers.

        This method is called every time the renderer is changed
        """
        self.__ensure_window_ready(False, True)

    def __ensure_window_ready(self, ui_requested: bool, stacks_requested: bool):
        # Store the current request or-ed with any previous ones
        #
        self.__ui_requested = ui_requested or self.__ui_requested
        self.__stacks_requested = stacks_requested or self.__stacks_requested

        # If waiting for renderer to complete setup, defer the requests until that is done
        #
        if self.__new_frame_sub:
            return

        def process_request(*args, **kwargs):
            self.__new_frame_sub = None
            self.__window_ready = True
            if self.__ui_requested:
                self.__ui_requested = False
                self._settings_widget.build_ui()
            if self.__stacks_requested:
                self.__stacks_requested = False
                self._settings_widget.build_stacks()

        # Window is already valid, process the requests now
        #
        if self.__window_ready:
            process_request()
            return

        # Subscribe to the event to wait for 1st frame delivery
        #
        usd_context = omni.usd.get_context(self.__usd_context_name)
        self.__new_frame_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=usd_context.stage_rendering_event_name(omni.usd.StageRenderingEventType.NEW_FRAME, True),
            on_event=process_request,
            observer_name="omni.rtx.window.settings:RTXSettingsWindow",
        )
