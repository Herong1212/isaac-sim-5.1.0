# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ActivityWindowExtension", "get_instance"]

from .activity_menu import ActivityMenuOptions
from .activity_model import ActivityModelDump, ActivityModelDumpForProgress, ActivityModelStageOpen, ActivityModelStageOpenForProgress
from .activity_progress_model import ActivityProgressModel
from .activity_progress_bar import ActivityProgressBarWindow, TIMELINE_WINDOW_NAME
from .activity_window import ActivityWindow
from .open_file_addon import OpenFileAddon
from .activity_actions import register_actions, deregister_actions
from .prompt_ui import Prompt

import asyncio
from functools import partial
import os
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
import weakref

import carb.profiler
import carb.settings
import carb.tokens
from carb.eventdispatcher import get_eventdispatcher
import carb.events
import omni.kit.app
import omni.activity.core
import omni.activity.profiler
import omni.ext
from omni.kit.window.file import register_open_stage_addon
import omni.ui as ui
import omni.usd_resolver
import omni.kit.commands


ASSET_DRAG_GLOBAL_EVENT: str = "omni.kit.widget.stage.DRAG_ASSET"
ASSET_DRAG_EVENT: int = carb.events.type_from_string(ASSET_DRAG_GLOBAL_EVENT)

STATUS_BAR_PROGRESS_EVENT = "omni.kit.window.status_bar@progress"
STATUS_BAR_ACTIVITY_EVENT = "omni.kit.window.status_bar@activity"
STATUS_BAR_CLICKED_EVENT = "omni.kit.window.status_bar@clicked"

AUTO_SAVE_LOCATION = "/exts/omni.activity.ui/auto_save_location"
STARTUP_ACTIVITY_FILENAME = "Startup"

g_singleton = None


def get_instance():
    return g_singleton


class ActivityWindowExtension(omni.ext.IExt):
    """The entry point for Activity Window"""

    PROGRESS_WINDOW_NAME = "Activity Progress"
    PROGRESS_MENU_PATH = f"Window/Utilities/{PROGRESS_WINDOW_NAME}"

    def on_startup(self, ext_id):
        import omni.kit.app

        # Register event aliases
        register_event_alias = omni.kit.app.register_event_alias
        type_from_string = carb.events.type_from_string
        register_event_alias(ASSET_DRAG_EVENT, ASSET_DRAG_GLOBAL_EVENT)
        register_event_alias(type_from_string(STATUS_BAR_PROGRESS_EVENT), STATUS_BAR_PROGRESS_EVENT)
        register_event_alias(type_from_string(STATUS_BAR_ACTIVITY_EVENT), STATUS_BAR_ACTIVITY_EVENT)
        register_event_alias(type_from_string(STATUS_BAR_CLICKED_EVENT), STATUS_BAR_CLICKED_EVENT)


        # true when we record the activity
        self.__activity_started = False

        self._activity_profiler = omni.activity.profiler.get_activity_profiler()
        self._activity_profiler_capture_mask_uid = 0

        # make sure the old activity widget is disabled before loading the new one
        ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
        old_activity_widget = "omni.kit.activity.widget.monitor"
        if ext_manager.is_extension_enabled(old_activity_widget):
            ext_manager.set_extension_enabled_immediate(old_activity_widget, False)

        self._timeline_window = None
        self._progress_bar = None
        self._addon = None
        self._asset_prompt = None
        self._current_path = None
        self._data = None
        self.__model = None
        self.__progress_model= None
        self.__flatten_model = None
        self._menu_entry = None
        self._activity_menu_option = ActivityMenuOptions(load_data=self.load_data, get_save_data=self.get_save_data)

        # The ability to show up the window if the system requires it. We use it
        # in QuickLayout.
        ui.Workspace.set_show_window_fn(TIMELINE_WINDOW_NAME, partial(self.show_window, None))
        ui.Workspace.set_show_window_fn(
            ActivityWindowExtension.PROGRESS_WINDOW_NAME, partial(self.show_progress_bar, None)
        )

        # add actions
        self._ext_name = omni.ext.get_extension_name(ext_id)
        register_actions(self._ext_name, self)

        # add new menu
        try:
            import omni.kit.menu.utils
            from omni.kit.menu.utils import MenuItemDescription

            self._menu_entry = [
                MenuItemDescription(name="Utilities", sub_menu=
                    [MenuItemDescription(
                        name=ActivityWindowExtension.PROGRESS_WINDOW_NAME,
                        ticked=True,
                        ticked_fn=self._is_progress_visible,
                        onclick_action=("omni.activity.ui", "show_activity_window"),
                    )]
                )
            ]
            omni.kit.menu.utils.add_menu_items(self._menu_entry, name="Window")
        except (ModuleNotFoundError, AttributeError):  # pragma: no cover
            pass

        # Listen for the app ready event
        self._app_ready_sub = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_APP_READY, on_event=self._on_app_ready, observer_name="Omni Activity"
        )

        # Listen to USD stage activity
        usd = omni.usd.get_context()
        self._stage_event_sub = [
            get_eventdispatcher().observe_event(
                observer_name="omni.activity.ui:activity_extension",
                event_name=usd.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.OPENING, self._on_stage_opening),
                (omni.usd.StageEventType.OPEN_FAILED, lambda _: self._on_stage_open_failed()),
                (omni.usd.StageEventType.ASSETS_LOADED, lambda _: self._on_stage_assets_loaded()),
            )
        ]

        self._asset_drag_event_sub = get_eventdispatcher().observe_event(event_name=ASSET_DRAG_GLOBAL_EVENT, on_event=self._on_asset_drag)


        self._activity_widget_subscription = register_open_stage_addon(self._open_file_addon)
        try:
            from omni.kit.usd.layers import get_live_syncing
            self._activity_widget_live_subscription = get_live_syncing().register_open_stage_addon(self._open_file_addon)
        except ModuleNotFoundError:
            carb.log_warn("omni.kit.usd.layers extension was not loaded, omni.activity.ui may not function as expected")
            
        # subscribe the callback to show the progress window when the prompt window disappears
        # self._show_window_subscription = register_open_stage_complete(self._show_progress_window)

        # message bus to update the status bar
        self.__subscription = None
        # subscribe the callback to show the progress window when user clicks the status bar's progress area
        self.__statusbar_click_subscription = get_eventdispatcher().observe_event(
            event_name=STATUS_BAR_CLICKED_EVENT, on_event=lambda _: self._show_progress_window())


        # watch the commands
        commands = ["AddReference", "CreatePayload", "CreateSublayer", "ReplacePayload", "ReplaceReference"]
        self.__command_callback_ids = [
            omni.kit.commands.register_callback(
                cb,
                omni.kit.commands.PRE_DO_CALLBACK,
                partial(ActivityWindowExtension._on_command, weakref.proxy(self), cb),
            )
            for cb in commands
        ]

        # Set up singleton instance
        global g_singleton
        g_singleton = self

    def _show_progress_window(self):
        ui.Workspace.show_window(ActivityWindowExtension.PROGRESS_WINDOW_NAME)
        self._progress_bar.focus()

    def _on_asset_drag(self, _):
        self.show_asset_load_prompt()
        if self._addon:
            self._addon.stop_timer()
        self._start_activity()

    def _on_app_ready(self, _):
        if not self.__activity_started:
            # Start an activity trace to measure the time between app ready and the first frame.
            # This may have already happened in _on_stage_event if an empty stage was opened at startup.
            self._start_activity(STARTUP_ACTIVITY_FILENAME, profiler_mask=omni.activity.profiler.CAPTURE_MASK_STARTUP)
        self._app_ready_sub = None

        context = omni.usd.get_context()
        self._new_frame_sub = get_eventdispatcher().observe_event(
            event_name=context.stage_rendering_event_name(omni.usd.StageRenderingEventType.NEW_FRAME),
            on_event=self._on_new_frame,
            observer_name="omni.activity.ui:ActivityWindowExtension"
        )

    def _on_new_frame(self, _):
        # Stop the activity trace measuring the time between app ready and the first frame.
        self._stop_activity(completed=True, filename=STARTUP_ACTIVITY_FILENAME)
        self._new_frame_sub = None

    def _on_stage_opening(self, event):
        path = event["val"]
        capture_mask = omni.activity.profiler.CAPTURE_MASK_SCENE_LOADING
        if self._app_ready_sub != None:
            capture_mask |= omni.activity.profiler.CAPTURE_MASK_STARTUP
            path = STARTUP_ACTIVITY_FILENAME
        self._start_activity(path, profiler_mask=capture_mask)

    def _on_stage_open_failed(self):
        self._stop_activity(completed=False)

    def _on_stage_assets_loaded(self):
        self._stop_activity(completed=True)
    def _model_changed(self, model, item):
        omni.kit.app.queue_event(STATUS_BAR_ACTIVITY_EVENT, {"text": str(model.latest_item)})
        omni.kit.app.queue_event(STATUS_BAR_PROGRESS_EVENT, {"progress": str(model.total_progress)})

    def on_shutdown(self):
        global g_singleton
        g_singleton = None

        import omni.kit.commands

        self._app_ready_sub = None
        self._new_frame_sub = None
        self._stage_event_sub = None
        self._asset_drag_event_sub = None
        self._progress_menu = None
        self._current_path = None
        self.__model = None
        self.__progress_model= None
        self.__flatten_model = None

        # remove actions
        deregister_actions(self._ext_name)

        # remove menu
        try:
            import omni.kit.menu.utils

            omni.kit.menu.utils.remove_menu_items(self._menu_entry, name="Window")
        except (ModuleNotFoundError, AttributeError):  # pragma: no cover
            pass
        self._menu_entry = None

        if self._timeline_window:
            self._timeline_window.destroy()
        self._timeline_window = None

        if self._progress_bar:
            self._progress_bar.destroy()
        self._progress_bar = None

        if self._asset_prompt:
            self._asset_prompt.destroy()
        self._asset_prompt = None

        self._addon = None

        if self._activity_menu_option:
            self._activity_menu_option.destroy()

        # Deregister the function that shows the window from omni.ui
        ui.Workspace.set_show_window_fn(TIMELINE_WINDOW_NAME, None)
        ui.Workspace.set_show_window_fn(ActivityWindowExtension.PROGRESS_WINDOW_NAME, None)

        self._activity_widget_subscription = None
        self._activity_widget_live_subscription = None
        self._show_window_subscription = None

        for callback_id in self.__command_callback_ids:
            omni.kit.commands.unregister_callback(callback_id)

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if hasattr(self, '_timeline_window') and self._timeline_window:
            self._timeline_window.destroy()
            self._timeline_window = None

    async def _destroy_progress_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._progress_bar:
            self._progress_bar.destroy()
            self._progress_bar = None

    def _visiblity_changed_fn(self, visible):
        # Called when the user pressed "X"
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def _progress_visiblity_changed_fn(self, visible):
        try:
            import omni.kit.menu.utils

            omni.kit.menu.utils.refresh_menu_items("Window")
        except (ModuleNotFoundError, AttributeError):  # pragma: no cover
            pass

        if not visible:
            # Destroy the window, since we are creating new window in show_progress_bar
            asyncio.ensure_future(self._destroy_progress_window_async())

    def _is_progress_visible(self) -> bool:
        return False if self._progress_bar is None else self._progress_bar.visible

    def show_window(self, menu, value):
        if value:
            self._timeline_window = ActivityWindow(
                TIMELINE_WINDOW_NAME,
                weakref.proxy(self.__model) if self.__model else None,
                activity_menu=self._activity_menu_option,
            )
            self._timeline_window.set_visibility_changed_fn(self._visiblity_changed_fn)
        elif self._timeline_window:
            self._timeline_window.visible = False

    def show_progress_bar(self, menu, value):
        if value:
            self._progress_bar = ActivityProgressBarWindow(
                ActivityWindowExtension.PROGRESS_WINDOW_NAME,
                self.__flatten_model,
                activity_menu=self._activity_menu_option,
                width=415,
                height=355,
            )
            self._progress_bar.set_visibility_changed_fn(self._progress_visiblity_changed_fn)
        elif self._progress_bar:
            self._progress_bar.visible = False

    def _open_file_addon(self):
        self._addon = OpenFileAddon()

    def show_asset_load_prompt(self):
        if not self._asset_prompt:
            self._asset_prompt = Prompt("Please Wait", "Loading Asset...", True, [self._open_file_addon])
        self._asset_prompt.show()

    def hide_asset_load_prompt(self):
        if self._asset_prompt:
            self._asset_prompt.hide()

    def get_save_data(self):
        """Save the current model to external file"""
        if not self.__model:
            return None

        return self.__model.get_data()

    def _save_current_activity(self, fullpath: Optional[str] = None, filename: Optional[str] = None):
        """
        Saves current activity.

        If the full path is not given it takes the stage name and saves it to the
        auto save location from settings. It can be URL or contain tokens.
        """
        if fullpath is None:
            settings = carb.settings.get_settings()
            auto_save_location = settings.get(AUTO_SAVE_LOCATION)

            if not auto_save_location:
                # No auto save location - nothing to do
                return

            # Resolve auto save location
            token = carb.tokens.get_tokens_interface()
            auto_save_location = token.resolve(auto_save_location)

            def remove_files():
                # only keep the latest 20 activity files, remove the old ones if necessary
                file_stays = 20
                sorted_files = [item for item in Path(auto_save_location).glob("*.activity")]
                if len(sorted_files) < file_stays:
                    return

                sorted_files.sort(key=lambda item: item.stat().st_mtime)
                for item in sorted_files[:-file_stays]:
                    os.remove(item)

            remove_files()

            if filename is None:

                # Extract filename
                # Current URL
                current_stage_url = omni.usd.get_context().get_stage_url()
                # Using clientlib to parse it
                current_stage_path = Path(omni.client.break_url(current_stage_url).path)
                # Some usd layers have ":" in name
                filename = current_stage_path.stem.split(":")[-1]

            # Construct the full path
            fullpath = omni.client.combine_urls(auto_save_location + "/", filename + ".activity")

        if not fullpath:
            return

        self._activity_menu_option.save(fullpath)

        carb.log_info(f"The activity log has been written to ${fullpath}.")

    def load_data(self, data):
        """Load the model from the data"""
        if self.__model:
            self.__flatten_model.destroy()
            self.__progress_model.destroy()
            self.__model.destroy()

        # Use separate models for Timeline and ProgressBar to mimic realtime model lifecycle. See _start_activity()
        self.__model = ActivityModelDump(data=data)
        self.__progress_model = ActivityModelDumpForProgress(data=data)
        self.__flatten_model = ActivityProgressModel(weakref.proxy(self.__progress_model))
        self.__flatten_model.finished_loading()

        if self._timeline_window:
            self._timeline_window._menu_new(weakref.proxy(self.__model))
        if self._progress_bar:
            self._progress_bar.new(self.__flatten_model)

    def _start_activity(self, path: Optional[str] = None, profiler_mask = 0):

        self.__activity_started = True

        self._activity_profiler_capture_mask_uid = self._activity_profiler.enable_capture_mask(profiler_mask)

        # reset all the windows
        if self.__model:
            self.__flatten_model.destroy()
            self.__progress_model.destroy()
            self.__model.destroy()
        self._current_path = None
        self.__model = ActivityModelStageOpen()
        self.__progress_model = ActivityModelStageOpenForProgress()
        self.__flatten_model = ActivityProgressModel(weakref.proxy(self.__progress_model))
        self.__subscription = None

        self.clear_status_bar()

        if self._timeline_window:
            self._timeline_window._menu_new(weakref.proxy(self.__model))
        if self._progress_bar:
            self._progress_bar.new(self.__flatten_model)
        if self._addon:
            self._addon.new(self.__flatten_model)
        if path:
            self.__subscription = self.__flatten_model.subscribe_item_changed_fn(self._model_changed)
            # only when we have a path, we start to record the activity
            self.__flatten_model.start_loading = True
            if self._progress_bar:
                self._progress_bar.start_timer()
            if self._addon:
                self._addon.start_timer()
            self.__model.set_path(path)
            self.__progress_model.set_path(path)
            self._current_path = path

    def _stop_activity(self, completed=True, filename: Optional[str] = None):
        # ASSETS_LOADED could be triggered by many things e.g. selection change
        # make sure we only enter this function once when the activity stops
        if not self.__activity_started:
            return

        self.__activity_started = False

        if self._activity_profiler_capture_mask_uid != 0:
            self._activity_profiler.disable_capture_mask(self._activity_profiler_capture_mask_uid)
            self._activity_profiler_capture_mask_uid = 0

        if self.__model:
            self.__model.end()
        if self.__progress_model:
            self.__progress_model.end()
        if self._current_path:
            if self._progress_bar:
                self._progress_bar.stop_timer()
            if self._addon:
                self._addon.stop_timer()
            if completed:
                # make sure the progress is 1 when assets loaded
                if self.__flatten_model:
                    self.__flatten_model.finished_loading()
                omni.kit.app.queue_event(STATUS_BAR_PROGRESS_EVENT, {"progress": "1.0"})
                self._save_current_activity(filename = filename)
            self.clear_status_bar()

        self.hide_asset_load_prompt()

    def clear_status_bar(self):
        # send an empty message to status bar
        omni.kit.app.queue_event(STATUS_BAR_ACTIVITY_EVENT, {"text": ""})
        # clear the progress bar widget
        omni.kit.app.queue_event(STATUS_BAR_PROGRESS_EVENT, {"progress": "-1"})

    def _on_command(self, command: str, kwargs: Dict[str, Any]):
        if command == "AddReference":
            path = kwargs.get("reference", None)
            if path:
                path = path.assetPath
            self._start_activity(path)
        elif command == "CreatePayload":
            path = kwargs.get("asset_path", None)
            self._start_activity(path)
        elif command == "CreateSublayer":
            path = kwargs.get("new_layer_path", None)
            self._start_activity(path)
        elif command == "ReplacePayload":
            path = kwargs.get("new_payload", None)
            if path:
                path = path.assetPath
            self._start_activity(path)
        elif command == "ReplaceReference":
            path = kwargs.get("new_reference", None)
            if path:
                path = path.assetPath
            self._start_activity(path)
