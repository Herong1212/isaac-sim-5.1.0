# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["RTXSettingsWidget"]

import sys
import traceback
from pathlib import Path
from typing import Callable, Dict, List

import carb
import carb.events
import omni.client
import omni.kit.app
import omni.kit.commands
import omni.ui as ui
from omni.kit.widget.settings import get_style, get_ui_style_name
from omni.kit.window.file_exporter import get_file_exporter
from omni.kit.window.file_importer import get_file_importer

from .rtx_settings_stack import RTXSettingsStack
from .usd_serializer import USDSettingsSerialiser

CURRENT_PATH = Path(__file__).parent.absolute()
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("icons")
RENDERER_CHANGED_GLOBAL_EVT = "render_settings.renderer.CHANGED"
RENDERER_CHANGED_EVT = carb.events.type_from_string(RENDERER_CHANGED_GLOBAL_EVT)
RENDERER_EVT_PAYLOAD_KEY = "renderer"
carb.events.register_event_alias(
    RENDERER_CHANGED_EVT, RENDERER_CHANGED_GLOBAL_EVT + ":immediate", RENDERER_CHANGED_GLOBAL_EVT
)

# global renderers/stacks so any widget can use them
registered_renderers: Dict[str, List[str]] = {}
registered_stacks: Dict[str, Callable] = {}


class RTXSettingsWidget:
    engine_to_mode = {"iray": "/rtx/iray/rendermode", "rtx": "/rtx/rendermode", "pxr": "/pxr/rendermode"}
    rendermode_to_settings = {
        "RaytracedLighting": "Real-Time",
        "PathTracing": "Interactive (Path Tracing)",
        "RealTimePathTracing": "Real-Time 2.0",
        "iray": "Accurate (Iray)",
    }

    def __init__(self, frame):
        style = None
        use_default_style = carb.settings.get_settings().get_as_bool("/persistent/app/window/useDefaultStyle") or False
        if not use_default_style:
            style = get_style()

        ui_style_name = get_ui_style_name()
        if ui_style_name == "NvidiaLight":
            option_icon_style = {"image_url": f"{ICON_PATH}/NvidiaLight/options.svg", "color": 0xFF535354}
        else:
            option_icon_style = {"image_url": f"{ICON_PATH}/NvidiaDark/options.svg", "color": 0xFF8A8777}

        self._option_icon_style = option_icon_style
        self._style = style
        self._frame = frame
        self._stack_frame = None
        self._renderer_model = None

        self._visible_stacks: Dict[str, RTXSettingsStack] = {}
        self.picker_open = False
        self._folder_exist_popup = None

        def renderChangedSubscription(path):
            return omni.kit.app.SettingChangeSubscription(path, self.__active_renderer_changed)

        # If the viewport renderer is changed, update render settings to reflect it
        self._renderer_subscriptions = [renderChangedSubscription("/renderer/active")]
        # Also need to watch all engine-mode changes
        for _, path in self.engine_to_mode.items():
            self._renderer_subscriptions.append(renderChangedSubscription(path))

        # menu
        self._options_menu = ui.Menu("Options")
        with self._options_menu:
            ui.MenuItem("Load Settings", triggered_fn=self.load_from_usd)
            ui.MenuItem("Save Settings", triggered_fn=self.save_to_usd)
            ui.MenuItem("Reset Settings", triggered_fn=self.restore_all_settings)

    def destroy(self) -> None:
        for k, s in self._visible_stacks.items():
            s.destroy()
        self._renderer_subscriptions = None

    def get_current_viewport_renderer(self, hydra_engine: str = None, render_mode: str = None):
        settings = carb.settings.get_settings()
        if hydra_engine is None:
            hydra_engine = settings.get("/renderer/active")

        if hydra_engine in self.engine_to_mode:
            if render_mode is None:
                render_mode = settings.get(self.engine_to_mode[hydra_engine])
            # XXX: Delegate this to the render-settings-extension instance
            #      (i.e.) let omni.hydra.pxr map HdStormRenderPlugin => Storm
            return self.rendermode_to_settings.get(render_mode, render_mode)

        return None

    def set_render_settings_to_viewport_renderer(self, hydra_engine: str = None, render_mode: str = None):
        renderer = self.get_current_viewport_renderer(hydra_engine, render_mode)
        if not renderer or not self._renderer_model:
            return

        renderer_list = list(registered_renderers.keys())
        if renderer in renderer_list:
            index = renderer_list.index(renderer)
            self._renderer_model.get_item_value_model().set_value(index)

    def __active_renderer_changed(self, *args, **kwargs):
        self.set_render_settings_to_viewport_renderer()

    def build_ui(self) -> None:
        if not self._frame:
            return

        if self._style is not None:
            self._frame.set_style(self._style)

        self._frame.clear()
        with self._frame:
            with ui.VStack(spacing=5):
                ui.Spacer(height=5)
                with ui.HStack(height=20):
                    ui.Spacer(width=20)
                    ui.Label("Renderer", name="RenderLabel", width=80)
                    renderer_list = list(registered_renderers.keys())
                    index = 0
                    current_renderer = self.get_current_viewport_renderer()
                    # Set to the default renderer if it's there
                    if current_renderer in renderer_list:
                        index = renderer_list.index(current_renderer)
                    self._renderer_model = ui.ComboBox(index, *renderer_list, name="renderer_choice").model
                    self._renderer_model.add_item_changed_fn(
                        lambda i, m: self.renderer_item_changed()
                    )  # build_stacks())
                    ui.Spacer(width=10)
                    ui.Button(style=self._option_icon_style, width=20, clicked_fn=lambda: self._options_menu.show())
                    ui.Spacer(width=10)
                ui.Spacer(height=0)

                self._stack_frame = ui.VStack()

    def build_stacks(self):
        """
        "stacks" are the tabs in the Render Settings UI that contain groups of settings
        They can be reused amongst different renderers.

        This method is called every time the renderer is changed
        """
        if not self._stack_frame:
            return

        for k, s in self._visible_stacks.items():
            s.destroy()

        self._stack_frame.clear()

        if not registered_renderers:
            return

        current_renderer = self.get_current_renderer()
        current_renderer_stacks = registered_renderers.get(current_renderer, None)
        if not current_renderer_stacks:
            print("RTXSettingsWidget: renderer Not supported")
            return

        with self._stack_frame:
            # Build the stacks ("Common", "Ray Tracing" etc)
            self._collection = ui.RadioCollection()
            with ui.HStack(height=30):
                ui.Spacer(width=15)

                for name in current_renderer_stacks:
                    ui.RadioButton(
                        text=name,
                        radio_collection=self._collection,
                        clicked_fn=lambda p=name: self.show_stack_from_name(p),
                    )
                ui.Spacer(width=10)

            ui.Spacer(height=7)

            with ui.ScrollingFrame():

                # stack pages
                with ui.ZStack():
                    for name in current_renderer_stacks:
                        stack_class = registered_stacks.get(name, None)
                        if not stack_class:
                            continue
                        self._visible_stacks[name] = stack_class()

            ui.Spacer(height=1)

        # Assume we want to show the middle stack - the renderer specific one
        if len(current_renderer_stacks) > 1 and self.have_stack(current_renderer_stacks[1]):
            self.show_stack_from_name(current_renderer_stacks[1])

    def register_renderer(self, name: str, stacks_list: List[str]) -> None:
        registered_renderers[name] = stacks_list

    def register_stack(self, name: str, stack_class: Callable) -> None:
        registered_stacks[name] = stack_class
        self.build_stacks()

    def unregister_renderer(self, name):
        if name in registered_renderers:
            del registered_renderers[name]

    def unregister_stack(self, name):
        if name in registered_stacks:
            del registered_stacks[name]

    def set_current_renderer(self, renderer_name: str) -> None:
        """
        sets the current renderer and updates the UI model
        """
        if renderer_name in registered_renderers.keys():
            renderer_names = list(registered_renderers.keys())
            for cnt, r in enumerate(renderer_names):
                if r == renderer_name:
                    self._renderer_model.get_item_value_model().set_value(cnt)

    def get_registered_renderers(self):
        return list(registered_renderers.keys())

    def get_current_renderer(self) -> str:
        return list(registered_renderers.keys())[self._renderer_model.get_item_value_model().as_int]

    def have_stack(self, name: str) -> None:
        return name in self._visible_stacks.keys()

    def show_stack_from_name(self, name: str) -> None:
        if name not in self._visible_stacks.keys():
            print("RTXSettingsWidget: Error No Key of that Name ")
            return

        for _, stack in self._visible_stacks.items():
            stack.set_visible(False)

        # work out which index the named stack is in the current UI
        stack_index = 0
        current_renderer_stack_names = registered_renderers.get(self.get_current_renderer(), None)
        for cnt, curr_stack_name in enumerate(current_renderer_stack_names):
            if curr_stack_name == name:
                stack_index = cnt

        self._visible_stacks[name].set_visible(True)
        self._collection.model.set_value(stack_index)

    def get_current_stack(self) -> str:
        for name, stack in self._visible_stacks.items():
            if stack.get_visible():
                return name
        return ""

    def get_renderer_stacks(self, renderer_name):
        return registered_renderers.get(renderer_name, None)

    def restore_all_settings(btn_widget):
        omni.kit.commands.execute("RestoreDefaultRenderSettingSection", path="/rtx")

    @staticmethod
    def __write_render_settings(filepath: str):
        return USDSettingsSerialiser().save_to_usd(filepath)

    def save_to_usd(self):
        def save_handler(filename: str, dirname: str, extension: str = "", selections: List[str] = []):
            final_path = omni.client.combine_urls(dirname, filename + extension)
            result, _ = omni.client.stat(final_path)
            if result == omni.client.Result.OK:
                self.__overwrite_file(final_path)
            else:
                self.__write_render_settings(final_path)

        file_exporter = get_file_exporter()
        if file_exporter:
            file_exporter.show_window(
                title="Save USD File",
                export_button_label="Save",
                export_handler=save_handler,
                file_postfix_options=["settings"],
            )

    def load_from_usd(self):
        def load_handler(filename: str, dirname: str, selections: List[str]):
            final_path = omni.client.combine_urls(dirname, filename)
            try:
                serialiser = USDSettingsSerialiser()
                serialiser.load_from_usd(final_path)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback)

        file_importer = get_file_importer()
        if file_importer:
            file_importer.show_window(
                title="Load USD File",
                import_button_label="Load",
                import_handler=load_handler,
                file_postfix_options=["settings"],
            )

    def renderer_item_changed(self) -> None:
        try:
            self._emit_renderer_changed_event()
        finally:
            self.build_stacks()

    def _emit_renderer_changed_event(self) -> None:
        payload = {RENDERER_EVT_PAYLOAD_KEY: self.get_current_renderer()}
        omni.kit.app.queue_event(RENDERER_CHANGED_GLOBAL_EVT, payload=payload)

    def __overwrite_file(self, usd_path) -> bool:
        try:
            from omni.kit.widget.prompt import Prompt

            def on_confirm():
                self.__write_render_settings(usd_path)
                self._folder_exist_popup.hide()

            def on_cancel():
                self._folder_exist_popup.hide()

            if not self._folder_exist_popup:
                self._folder_exist_popup = Prompt(
                    "Overwrite",
                    "The file already exists, are you sure you want to overwrite it?",
                    "Overwrite",
                    "Cancel",
                    None,
                    None,
                    None,
                    None,
                )
            self._folder_exist_popup.set_confirm_fn(on_confirm)
            self._folder_exist_popup.set_cancel_fn(on_cancel)
            self._folder_exist_popup.show()
        except ModuleNotFoundError:
            self.__write_render_settings(usd_path)
