# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ActivityProgressBarWindow"]


import omni.ui as ui
from omni.ui import scene as sc
import omni.kit.app
import asyncio
from functools import partial
import math
import pathlib
from .style import progress_window_style
from .activity_tree_delegate import ActivityProgressTreeDelegate
from .activity_menu import ActivityMenuOptions
from .activity_progress_model import ActivityProgressModel


TIMELINE_WINDOW_NAME = "Activity Timeline"
EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)


def convert_seconds_to_hms(sec):
    result = ""
    rest_sec = sec
    h = math.floor(rest_sec / 3600)
    if h > 0:
        if h < 10:
            result += "0"
        result += str(h) + ":"
        rest_sec -= h * 3600
    else:
        result += "00:"
    m = math.floor(rest_sec / 60)
    if m > 0:
        if m < 10:
            result += "0"
        result += str(m) + ":"
        rest_sec -= m * 60
    else:
        result += "00:"
    if rest_sec < 10:
        result += "0"
    result += str(rest_sec)
    return result


class Spinner(sc.Manipulator):
    def __init__(self, event):
        super().__init__()
        self.__deg = 0
        self.__spinning_event = event

    def on_build(self):
        self.invalidate()

        if self.__spinning_event.is_set():
            self.__deg = self.__deg % 360
            transform = sc.Matrix44.get_rotation_matrix(0, 0, -self.__deg, True)

            with sc.Transform(transform=transform):
                sc.Image(f"{EXTENSION_FOLDER_PATH}/data/progress.svg", width=2, height=2)
            self.__deg += 3


class ProgressBarWidget:
    def __init__(self, model=None, activity_menu=None):
        self.__model = None
        self.__subscription = None

        self._finished_ui_build = False

        self.__frame = ui.Frame(build_fn=partial(self.__build, model))
        self.__frame.style = progress_window_style

        # for the menu
        self._activity_menu_option = activity_menu

        # for the timer
        self._start_event = asyncio.Event()
        self._stop_event = asyncio.Event()

        self.spinner = None
        self._progress_stack = None

    def reset_timer(self):
        if self._finished_ui_build:
            self.total_time.text = "00:00:00"
        self._start_event.set()

    def stop_timer(self):
        self._start_event.clear()

    def new(self, model=None):
        """Recreate the models and start recording"""
        self.__model = model
        self.__subscription = None
        self._start_event.clear()

        if self.__model:
            self.__subscription = self.__model.subscribe_item_changed_fn(self._model_changed)

            # this is for the add on widget, no need to update the model if the ui is not ready
            if self._finished_ui_build:
                self.update_by_model(self.__model)
                self.total_time.text = convert_seconds_to_hms(model.duration)
                self.__tree.model = self.__model

    def destroy(self):
        self.__model = None
        self.__subscription = None
        self.__tree_delegate = None

        self.__tree = None
        self.usd_number = None
        self.material_number = None
        self.texture_number = None
        self.total_number = None
        self.usd_progress = None
        self.material_progress = None
        self.texture_progress = None
        self.total_progress = None
        self.current_event = None
        self.total_progress_text = None

        self._stop_event.set()

    def show_stack_from_idx(self, idx):
        if idx == 0:
            self._activity_stack.visible = False
            self._progress_stack.visible = True
        elif idx == 1:
            self._activity_stack.visible = True
            self._progress_stack.visible = False

    def update_USD(self, model):
        if self._progress_stack:
            self.usd_number.text = str(model.usd_loaded_sum) + "/" + str(model.usd_sum)
            self.usd_progress.set_value(model.usd_progress)
            self.usd_size.text = str(round(model.usd_size, 2)) + " MB"
            self.usd_speed.text = str(round(model.usd_speed, 2)) + " MB/sec"

    def update_textures(self, model):
        if self._progress_stack:
            self.texture_number.text = str(model.texture_loaded_sum) + "/" + str(model.texture_sum)
            self.texture_progress.set_value(model.texture_progress)
            self.texture_size.text = str(round(model.texture_size, 2)) + " MB"
            self.texture_speed.text = str(round(model.texture_speed, 2)) + " MB/sec"

    def update_materials(self, model):
        if self._progress_stack:
            self.material_number.text = str(model.material_loaded_sum) + "/" + str(model.material_sum)
            self.material_progress.set_value(model.material_progress)

    def update_total(self, model):
        if self._progress_stack:
            self.total_number.text = "Total: " + str(model.total_loaded_sum) + "/" + str(model.total_sum)
            self.total_progress.set_value(model.total_progress)
            self.total_progress_text.text = f"{model.total_progress * 100 :.2f}%"
            if model.latest_item:
                self.current_event.text = "Loading " + model.latest_item
            elif model.latest_item is None:
                self.current_event.text = "Done"
            else:
                self.current_event.text = ""

    def update_by_model(self, model):
        self.update_USD(model)
        self.update_textures(model)
        self.update_materials(model)
        self.update_total(model)
        if self._progress_stack:
            self.total_time.text = convert_seconds_to_hms(model.duration)

    def _model_changed(self, model, item):
        self.update_by_model(model)

    def progress_stack(self):
        self._progress_stack = ui.VStack()
        with self._progress_stack:
            ui.Spacer(height=15)
            with ui.HStack():
                ui.Spacer(width=20)
                with ui.VStack(spacing=4):
                    with ui.HStack(height=30):
                        ui.ImageWithProvider(style_type_name_override="Icon", name="USD", width=23)
                        ui.Label("  USD", width=50)
                        ui.Spacer()
                        self.usd_size = ui.Label("0 MB", alignment=ui.Alignment.RIGHT_CENTER, width=120)
                        ui.Spacer()
                        self.usd_speed = ui.Label("0 MB/sec", alignment=ui.Alignment.RIGHT_CENTER, width=140)
                    with ui.HStack(height=22):
                        self.usd_number = ui.Label("0/0", width=60, alignment=ui.Alignment.RIGHT_CENTER)
                        ui.Spacer(width=10)
                        self.usd_progress = ui.ProgressBar(name="USD").model
                    with ui.HStack(height=30):
                        ui.ImageWithProvider(style_type_name_override="Icon", name="material", width=20)
                        ui.Label("  Material", width=50)
                        ui.Spacer()
                        self.material_size = ui.Label("", alignment=ui.Alignment.RIGHT_CENTER, width=120)
                        ui.Spacer()
                        self.material_speed = ui.Label("", alignment=ui.Alignment.RIGHT_CENTER, width=140)
                    with ui.HStack(height=22):
                        self.material_number = ui.Label("0/0", width=60, alignment=ui.Alignment.RIGHT_CENTER)
                        ui.Spacer(width=10)
                        self.material_progress = ui.ProgressBar(height=22, name="material").model
                    with ui.HStack(height=30):
                        ui.ImageWithProvider(style_type_name_override="Icon", name="texture", width=20)
                        ui.Label("  Texture", width=50)
                        ui.Spacer()
                        self.texture_size = ui.Label("0 MB", alignment=ui.Alignment.RIGHT_CENTER, width=120)
                        ui.Spacer()
                        self.texture_speed = ui.Label("0 MB/sec", alignment=ui.Alignment.RIGHT_CENTER, width=140)
                    with ui.HStack(height=22):
                        self.texture_number = ui.Label("0/0", width=60, alignment=ui.Alignment.RIGHT_CENTER)
                        ui.Spacer(width=10)
                        self.texture_progress = ui.ProgressBar(height=22, name="texture").model
                ui.Spacer(width=20)

    def activity_stack(self):
        self._activity_stack = ui.VStack()
        self.__tree_delegate = ActivityProgressTreeDelegate()
        with self._activity_stack:
            ui.Spacer(height=10)
            self.__tree = ui.TreeView(
                self.__model,
                delegate=self.__tree_delegate,
                root_visible=False,
                header_visible=True,
                column_widths=[ui.Fraction(1), 50, 50],
                columns_resizable=True,
            )

    async def infloop(self):
        while not self._stop_event.is_set():
            await asyncio.sleep(1)

            if self._stop_event.is_set():
                break

            if self._start_event.is_set():
                # cant use duration += 1 since when the ui is stuck, the function is not called, so we will get the
                # duration wrong
                if self.__model:
                    self.total_time.text = convert_seconds_to_hms(self.__model.duration)

    def __build(self, model):
        """
        The method that is called to build all the UI once the window is visible.
        """
        if self._activity_menu_option:
            self._options_menu = ui.Menu("Options")
            with self._options_menu:
                ui.MenuItem("Show Timeline", triggered_fn=lambda: ui.Workspace.show_window(TIMELINE_WINDOW_NAME))
                ui.Separator()
                ui.MenuItem("Open...", triggered_fn=self._activity_menu_option.menu_open)
                ui.MenuItem("Save...", triggered_fn=self._activity_menu_option.menu_save)
        self._collection = ui.RadioCollection()
        with ui.VStack():
            with ui.HStack(height=30):
                ui.Spacer()
                tab0 = ui.RadioButton(
                    text="Progress Bar",
                    width=0,
                    radio_collection=self._collection)
                ui.Spacer(width=12)
                with ui.VStack(width=3):
                    ui.Spacer()
                    ui.Rectangle(name="separator", height=16)
                    ui.Spacer()
                ui.Spacer(width=12)
                tab1 = ui.RadioButton(
                    text="Activity",
                    width=0,
                    radio_collection=self._collection)
                ui.Spacer()
                if self._activity_menu_option:
                    ui.Button(name="options", width=20, height=20, clicked_fn=lambda: self._options_menu.show())
            with ui.HStack():
                ui.Spacer(width=3)
                with ui.ScrollingFrame():
                    with ui.ZStack():
                        self.progress_stack()
                        self.activity_stack()
                        self._activity_stack.visible = False
                ui.Spacer(width=3)
            tab0.set_clicked_fn(lambda: self.show_stack_from_idx(0))
            tab1.set_clicked_fn(lambda: self.show_stack_from_idx(1))

            with ui.HStack(height=70):
                ui.Spacer(width=20)
                with ui.VStack(width=20):
                    ui.Spacer(height=12)
                    with sc.SceneView().scene:
                        self.spinner = Spinner(self._start_event)
                ui.Spacer(width=10)
                with ui.VStack():
                    with ui.HStack(height=30):
                        self.total_number = ui.Label("Total: 0/0")
                        self.total_time = ui.Label("00:00:00", width=0, alignment=ui.Alignment.RIGHT_CENTER)
                    with ui.ZStack(height=22):
                        self.total_progress = ui.ProgressBar(name="progress").model
                        with ui.HStack():
                            ui.Spacer(width=4)
                            self.current_event = ui.Label("", elided_text=True)
                            self.total_progress_text = ui.Label("0.00%", width=0, alignment=ui.Alignment.RIGHT_CENTER)
                            ui.Spacer(width=4)
                    asyncio.ensure_future(self.infloop())
                ui.Spacer(width=35)
        self._finished_ui_build = True
        # update ui with model, so that we keep tracking of the model even when the widget is not shown
        if model:
            self.new(model)
            if model.start_loading and not model.finish_loading:
                self._start_event.set()


class ActivityProgressBarWindow(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str, model, delegate=None, activity_menu=None, **kwargs):
        super().__init__(title, raster_policy=ui.RasterPolicy.NEVER, **kwargs)

        self.__widget = None
        self.deferred_dock_in("Property", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.frame.set_build_fn(lambda: self.__build(model, activity_menu))

    def destroy(self):
        if self.__widget:
            self.__widget.destroy()
        # It will destroy all the children
        super().destroy()

    def __build(self, model, activity_menu):
        self.__widget = ProgressBarWidget(model, activity_menu=activity_menu)

    def new(self, model):
        if self.__widget:
            self.__widget.new(model)

    def start_timer(self):
        if self.__widget:
            self.__widget.reset_timer()

    def stop_timer(self):
        if self.__widget:
            self.__widget.stop_timer()
