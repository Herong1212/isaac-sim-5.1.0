# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["VisibilityColumnDelegate"]

from ..abstract_stage_column_delegate import AbstractStageColumnDelegate
from ..stage_model import StageModel, StageItemSortPolicy
from ..stage_item import StageItem
from ..stage_icons import StageIcons as Icons
from pxr import UsdGeom
from typing import List
from enum import Enum

import omni.ui as ui

# delay calculation for icon path
def _get_widget_styles():
    return {
        "Button.Image::visibility": {"image_url": Icons().get("eye_on"), "color": 0xFF8A8777},
        "Button.Image::visibility:checked": {"image_url": Icons().get("eye_off"), "color": 0x88DDDCCC},
        "Button.Image::visibility:disabled": {"color": 0x608A8777},
        "Button.Image::visibility:selected": {"color": 0xFFCCCCCC},
        "Button::visibility": {"background_color": 0x0, "margin": 0, "margin_width": 1},
        "Button::visibility:checked": {"background_color": 0x0},
        "Button::visibility:hovered": {"background_color": 0x0},
        "Button::visibility:pressed": {"background_color": 0x0},
    }

def _get_header_styles():
    return {
        "TreeView.Header::visibility_header": {"image_url": Icons().get("eye_header"), "color": 0xFF888888},
    }


class VisibilityColumnSortPolicy(Enum):
    DEFAULT = 0
    INVISIBLE_TO_VISIBLE = 1
    VISIBLE_TO_INVISIBLE = 2


# BEGIN-DOC-custom_column_delegate
class VisibilityColumnDelegate(AbstractStageColumnDelegate):
    """The column delegate that represents the visibility column"""

    def __init__(self):
        super().__init__()
        self.__visibility_layout = None
        self.__items_sort_policy = VisibilityColumnSortPolicy.DEFAULT
        self.__stage_model: StageModel = None

    def destroy(self):
        if self.__visibility_layout:
            self.__visibility_layout.set_mouse_pressed_fn(None)
            self.__visibility_layout = None

        self.__stage_model = None

    @property
    def initial_width(self):
        """The width of the column"""
        return ui.Pixel(24)
# END-DOC-custom_column_delegate

    def __initialize_policy_from_model(self):
        stage_model = self.__stage_model
        if not stage_model:
            return

        if stage_model.get_items_sort_policy() == StageItemSortPolicy.VISIBILITY_COLUMN_INVISIBLE_TO_VISIBLE:
            self.__items_sort_policy = VisibilityColumnSortPolicy.INVISIBLE_TO_VISIBLE
        elif stage_model.get_items_sort_policy() == StageItemSortPolicy.VISIBILITY_COLUMN_VISIBLE_TO_INVISIBLE:
            self.__items_sort_policy = VisibilityColumnSortPolicy.VISIBLE_TO_INVISIBLE
        else:
            self.__items_sort_policy = VisibilityColumnSortPolicy.DEFAULT

    def __on_policy_changed(self):
        stage_model = self.__stage_model
        if not stage_model:
            return

        if self.__items_sort_policy == VisibilityColumnSortPolicy.INVISIBLE_TO_VISIBLE:
            stage_model.set_items_sort_policy(StageItemSortPolicy.VISIBILITY_COLUMN_INVISIBLE_TO_VISIBLE)
        elif self.__items_sort_policy == VisibilityColumnSortPolicy.VISIBLE_TO_INVISIBLE:
            stage_model.set_items_sort_policy(StageItemSortPolicy.VISIBILITY_COLUMN_VISIBLE_TO_INVISIBLE)
        else:
            stage_model.set_items_sort_policy(StageItemSortPolicy.DEFAULT)

    def __on_visiblity_clicked(self, x, y, b, m):
        if b != 0 or not self.__stage_model:
            return

        if self.__items_sort_policy == VisibilityColumnSortPolicy.VISIBLE_TO_INVISIBLE:
            self.__items_sort_policy = VisibilityColumnSortPolicy.INVISIBLE_TO_VISIBLE
        elif self.__items_sort_policy == VisibilityColumnSortPolicy.INVISIBLE_TO_VISIBLE:
            self.__items_sort_policy = VisibilityColumnSortPolicy.DEFAULT
        else:
            self.__items_sort_policy = VisibilityColumnSortPolicy.VISIBLE_TO_INVISIBLE

        self.__on_policy_changed()

# BEGIN-DOC-custom_column_delegate_build_fn
    def build_header(self, **kwargs):
        """Build the header"""
        stage_model = kwargs.get("stage_model", None)
        self.__stage_model = stage_model
        self.__initialize_policy_from_model()
        if stage_model:
            self.__visibility_layout = ui.HStack(style=_get_header_styles())
            with self.__visibility_layout:
                ui.Spacer()
                with ui.VStack(width=0):
                    ui.Spacer()
                    ui.Image(width=22, height=14, name="visibility_header", style_type_name_override="TreeView.Header")
                    ui.Spacer()
                ui.Spacer()

            self.__visibility_layout.set_mouse_pressed_fn(self.__on_visiblity_clicked)
        else:
            with ui.HStack(style=_get_header_styles()):
                ui.Spacer()
                with ui.VStack(width=0):
                    ui.Spacer()
                    ui.Image(width=22, height=14, name="visibility_header", style_type_name_override="TreeView.Header")
                    ui.Spacer()
                ui.Spacer()

    async def build_widget(self, _, **kwargs):
        """Build the eye widget"""
        item = kwargs.get("stage_item", None)
        if not item or not item.prim or not item.prim.IsA(UsdGeom.Imageable):
            return

        with ui.ZStack(height=20, style=_get_widget_styles()):
            # Min size
            ui.Spacer(width=22)
            # TODO the way to make this widget grayed out
            ui.ToolButton(item.visibility_model, enabled=not item.instance_proxy and item.active, name="visibility")

    @property
    def order(self):
        # Ensure it's always to the leftmost column except the name column.
        return -101

    @property
    def sortable(self):
        return True

    def on_stage_items_destroyed(self, items: List[StageItem]):
        pass

    @property
    def minimum_width(self):
        return ui.Pixel(20)

    @property
    def resizable(self):
        return False
# END-DOC-custom_column_delegate_build_fn
