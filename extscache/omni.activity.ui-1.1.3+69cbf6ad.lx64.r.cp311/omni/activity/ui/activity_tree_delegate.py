# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ActivityTreeDelegate", "ActivityProgressTreeDelegate"]

from .activity_model import SECOND_MULTIPLIER, ActivityModelItem
import omni.kit.app
import omni.ui as ui
import pathlib
from urllib.parse import unquote

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)


class ActivityTreeDelegate(ui.AbstractItemDelegate):
    """
    The delegate for the bottom TreeView that displays details of the activity.
    """

    def __init__(self, **kwargs):
        super().__init__()
        self._on_expand = kwargs.pop("on_expand", None)
        self._initialize_expansion = kwargs.pop("initialize_expansion", None)

    def build_branch(self, model, item, column_id, level, expanded):
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
                        style_type_name_override="TreeView.Label",
                        mouse_pressed_fn=lambda x, y, b, a: self._on_expand(item)
                    )
                    ui.Spacer(width=5)

    def _build_header(self, column_id, headers, headers_tooltips):
        alignment = ui.Alignment.LEFT_CENTER if column_id == 0 else ui.Alignment.RIGHT_CENTER
        return ui.Label(
            headers[column_id], height=22, alignment=alignment, style_type_name_override="TreeView.Label", tooltip=headers_tooltips[column_id])

    def build_header(self, column_id: int):
        headers = ["  Name", "Dur", "Start", "End", "Size "]
        headers_tooltips = ["Activity Name", "Duration (second)", "Start Time (second)", "End Time (second)", "Size (MB)"]
        return self._build_header(column_id, headers, headers_tooltips)

    def _build_name(self, text, item, model):
        tooltip = f"{text}"

        short_name = unquote(text.split("/")[-1])
        children_size = len(model.get_item_children(item))
        label_text = short_name if children_size == 0 else short_name + " (" + str(children_size) + ")"

        with ui.HStack(spacing=5):
            icon_name = item.icon_name
            if icon_name != "undefined":
                ui.ImageWithProvider(style_type_name_override="Icon", name=icon_name, width=16)
            if icon_name != "material":
                ui.ImageWithProvider(style_type_name_override="Icon", name="file", width=12)
            label_style_name = icon_name if item.ended else "unfinished"
            ui.Label(label_text, name=label_style_name, tooltip=tooltip)

        # if text == "Materials" or text == "Textures":
        #     self._initialize_expansion(item, True)

    def _build_duration(self, item):
        duration = item.total_time / SECOND_MULTIPLIER
        ui.Label(f"{duration:.2f}", style_type_name_override="TreeView.Label.Right", tooltip=str(duration) + " sec")

    def _build_start_and_end(self, item, model, is_start):
        time_ranges = item.time_range
        if len(time_ranges) == 0:
            return
        time_begin = model.time_begin
        begin = (time_ranges[0].begin - time_begin) / SECOND_MULTIPLIER
        end = (time_ranges[-1].end - time_begin) / SECOND_MULTIPLIER
        if is_start:
            ui.Label(f"{begin:.2f}", style_type_name_override="TreeView.Label.Right", tooltip=str(begin) + " sec")
        else:
            ui.Label(f"{end:.2f}", style_type_name_override="TreeView.Label.Right", tooltip=str(end) + " sec")

    def _build_size(self, text, item):
        if text in ["Read", "Load", "Resolve"]:
            size = item.children_size
        else:
            size = item.size
        if size != 0:
            size *= 0.000001
            ui.Label(f"{size:.2f}", style_type_name_override="TreeView.Label.Right", tooltip=str(size) + " MB")     # from byte to MB

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per item"""
        if not hasattr(model, "time_begin") or not isinstance(item, ActivityModelItem):
            return

        text = model.get_item_value_model(item, column_id).get_value_as_string()
        with ui.VStack(height=20):
            if column_id == 0:
                self._build_name(text, item, model)
            elif column_id == 1:
                self._build_duration(item)
            elif column_id == 2 or column_id == 3:
                self._build_start_and_end(item, model, column_id == 2)
            elif column_id == 4:
                self._build_size(text, item)


class ActivityProgressTreeDelegate(ActivityTreeDelegate):
    def __init__(self, **kwargs):
        super().__init__()

    def build_header(self, column_id: int):
        headers = ["       Name", "Dur", "Size "]
        headers_tooltips = ["Activity Name", "Duration (second)", "Size (MB)"]
        return self._build_header(column_id, headers, headers_tooltips)

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per item"""
        if not hasattr(model, "time_begin") or not isinstance(item, ActivityModelItem):
            return

        text = model.get_item_value_model(item, column_id).get_value_as_string()
        with ui.VStack(height=20):
            if column_id == 0:
                self._build_name(text, item, model)
            elif column_id == 1:
                self._build_duration(item)
            elif column_id == 2:
                self._build_size(text, item)
