# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ActivityReportWindow"]

import asyncio
import omni.kit.app
import omni.ui as ui
from omni.ui import color as cl
import math
import pathlib
from typing import Callable

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)


def exec_after_redraw(callback: Callable, wait_frames: int = 2):
    async def exec_after_redraw_async(callback: Callable, wait_frames: int):
        # Wait some frames before executing
        for _ in range(wait_frames):
            await omni.kit.app.get_app().next_update_async()
        callback()

    asyncio.ensure_future(exec_after_redraw_async(callback, wait_frames))


class ReportItem(ui.AbstractItem):
    """Single item of the model"""

    def __init__(self, text, value, size, parent):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)
        self.value_model = ui.SimpleFloatModel(value)
        self.size_model = ui.SimpleFloatModel(size)
        self.parent = parent
        self.children = []
        self.filtered_children = []


class ReportModel(ui.AbstractItemModel):
    """
    Represents the model for the report
    """

    def __init__(self, data, treeview_size):
        super().__init__()
        self._children = []
        self._parents = []
        self.root = None
        self.load(data)
        self._sized_children = self._children[:treeview_size]

    def destroy(self):
        self._children = []
        self._parents = []
        self.root = None
        self._sized_children = []

    def load(self, data):
        if data and "root" in data:
            self.root = ReportItem("root", 0, 0, None)
            self.set_data(data["root"], self.root)
        # sort the data with duration
        self._children.sort(key=lambda item: item.value_model.get_value_as_float(), reverse=True)

    def set_data(self, data, parent):
        parent_name = parent.name_model.as_string
        for child in data["children"]:
            size = child["size"] if "size" in child else 0
            item = ReportItem(child["name"], child["duration"], size, parent)
            # put the item we cares to the self._children

            if parent_name in ["Resolve", "Read", "Meshes", "Textures", "Materials"]:
                self._children.append(item)

            parent.children.append(item)
            self.set_data(child, item)

    def get_item_children(self, item):
        if item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return item.filtered_children

        # clear previous results
        for p in self._parents:
            p.filtered_children = []
        self._parents = []

        for child in self._sized_children:
            parent = child.parent
            parent.filtered_children.append(child)
            if parent not in self._parents:
                self._parents.append(parent)

        return self._parents

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 2

    def get_item_value_model(self, item, column_id):
        if column_id == 0:
            return item.name_model
        else:
            return item.value_model


class ReportTreeDelegate(ui.AbstractItemDelegate):
    def __init__(self):
        super().__init__()

    def build_branch(self, model, item, column_id, level, expanded=True):
        """Create a branch widget that opens or closes subtree"""
        if column_id == 0:
            with ui.HStack(width=20 * (level + 1), height=0):
                ui.Spacer()
                if model.can_item_have_children(item):
                    # Draw the +/- icon
                    image_name = "Minus" if expanded else "Plus"
                    ui.ImageWithProvider(
                        f"{EXTENSION_FOLDER_PATH}/data/{image_name}.svg",
                        width=10,
                        height=10,
                    )
                    ui.Spacer(width=5)

    def build_header(self, column_id: int):
        headers = ["Name", "Duration (HH:MM:SS)"]
        return ui.Label(headers[column_id], height=22)

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per column per item"""
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

        if column_id == 1 and level == 1:
            return
        value_model = model.get_item_value_model(item, column_id)
        value = value_model.as_string

        if column_id == 0 and level == 1:
            value += " (" + str(len(model.get_item_children(item))) + ")"
        elif column_id == 1:
            value = convert_seconds_to_hms(value_model.as_int)
        with ui.VStack(height=20):
            ui.Label(value, elided_text=True)


class ActivityReportWindow(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str, delegate=None, **kwargs):
        super().__init__(title, raster_policy=ui.RasterPolicy.NEVER, **kwargs)
        self.__expand_task = None
        self._current_path = kwargs.pop("path", "")
        self._data = kwargs.pop("data", "")
        # Set the function that is called to build widgets when the window is visible
        self.frame.set_build_fn(self.__build)

    def destroy(self):
        # It will destroy all the children
        super().destroy()

        if self.__expand_task is not None:
            self.__expand_task.cancel()
            self.__expand_task = None

        if self._report_model:
            self._report_model.destroy()
            self._report_model = None

    def __build(self):
        """
        The method that is called to build all the UI once the window is
        visible.
        """
        treeview_size = 10

        def set_treeview_size(model, size):
            model._sized_children = model._children[:size]
            model._item_changed(None)

        with ui.VStack():
            ui.Label(f"Report for opening {self._current_path}", height=70, alignment=ui.Alignment.CENTER)
            self._report_model = ReportModel(self._data, treeview_size)
            ui.Line(height=12, style={"color": cl.red})
            root_children = []
            if self._report_model.root:
                root_children = self._report_model.root.children

            file_children = []
            # time
            for child in root_children:
                name = child.name_model.as_string
                if name in ["USD", "Meshes", "Textures", "Materials"]:
                    file_children += [child]
                with ui.HStack(height=0):
                    ui.Label(f"Total Time of {name}")
                    ui.Label(f" {child.value_model.as_string} ")
                color = cl.red if child == root_children[-1] else cl.black
                ui.Line(height=12, style={"color": color})

            # number
            for file in file_children:
                with ui.HStack(height=0):
                    name = file.name_model.as_string.split(" ")[0]
                    ui.Label(f"Total Number of {name}")
                    ui.Label(f" {len(file.children)} ")
                color = cl.red if file == file_children[-1] else cl.black
                ui.Line(height=12, style={"color": color})
            # size
            for file in file_children:
                size = 0
                for c in file.children:
                    s = c.size_model.as_float
                    if s > 0:
                        size += s
                with ui.HStack(height=0):
                    name = file.name_model.as_string.split(" ")[0]
                    ui.Label(f"Total Size of {name} (MB)")
                    ui.Label(f" {size * 0.000001} ")
                color = cl.red if file == file_children[-1] else cl.black
                ui.Line(height=12, style={"color": color})
            ui.Spacer(height=10)
            # field which can change the size of the treeview
            with ui.HStack(height=0):
                ui.Label("The top ", width=0)
                field = ui.IntField(width=60)
                field.model.set_value(treeview_size)
                ui.Label(f" most time consuming task{'s' if treeview_size > 1 else ''}")
            ui.Spacer(height=3)
            # treeview
            with ui.ScrollingFrame(
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                style_type_name_override="TreeView",
                style={"Field": {"background_color": cl.black}},
            ):
                self._name_value_delegate = ReportTreeDelegate()
                self.treeview = ui.TreeView(
                    self._report_model,
                    delegate=self._name_value_delegate,
                    root_visible=False,
                    header_visible=True,
                    column_widths=[ui.Fraction(1), 130],
                    columns_resizable=True,
                    style={"TreeView.Item": {"margin": 4}},
                )
                field.model.add_value_changed_fn(lambda m: set_treeview_size(self._report_model, m.get_value_as_int()))

                def expand_collections():
                    for item in self._report_model.get_item_children(None):
                        self.treeview.set_expanded(item, True, False)
                # Finally, expand collection nodes in treeview after UI becomes ready
                self.__expand_task = exec_after_redraw(expand_collections, wait_frames=2)
