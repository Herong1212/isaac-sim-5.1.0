# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["TypeColumnDelegate"]

from ..abstract_stage_column_delegate import AbstractStageColumnDelegate
from ..stage_model import StageModel, StageItemSortPolicy
from ..stage_item import StageItem
from typing import List
from enum import Enum

import omni.ui as ui


WIDGET_STYLES = {
    "TreeView.Image::object_icon_grey": {"color": 0x80FFFFFF},
    "TreeView.Item::object_name_grey": {"color": 0xFF4D4B42},
    "TreeView.Item::object_name_missing": {"color": 0xFF6F72FF},
}


class TypeColumnSortPolicy(Enum):
    DEFAULT = 0
    A_TO_Z = 1
    Z_TO_A = 2


class TypeColumnDelegate(AbstractStageColumnDelegate):
    """The column delegate that represents the type column"""

    def __init__(self):
        super().__init__()

        self.__name_label_layout = None
        self.__name_label = None
        self.__items_sort_policy = TypeColumnSortPolicy.DEFAULT
        self.__stage_model: StageModel = None

    def destroy(self):
        if self.__name_label_layout:
            self.__name_label_layout.set_mouse_pressed_fn(None)

    @property
    def initial_width(self):
        """The width of the column"""
        return ui.Pixel(100)

    def __initialize_policy_from_model(self):
        stage_model = self.__stage_model
        if not stage_model:
            return

        if stage_model.get_items_sort_policy() == StageItemSortPolicy.TYPE_COLUMN_A_TO_Z:
            self.__items_sort_policy = TypeColumnSortPolicy.A_TO_Z
        elif stage_model.get_items_sort_policy() == StageItemSortPolicy.TYPE_COLUMN_Z_TO_A:
            self.__items_sort_policy = TypeColumnSortPolicy.Z_TO_A
        else:
            self.__items_sort_policy = TypeColumnSortPolicy.DEFAULT

        self.__update_label_from_policy()

    def __update_label_from_policy(self):
        if not self.__name_label:
            return

        if self.__name_label:
            if self.__items_sort_policy == TypeColumnSortPolicy.A_TO_Z:
                name = "Type (A to Z)"
            elif self.__items_sort_policy == TypeColumnSortPolicy.Z_TO_A:
                name = "Type (Z to A)"
            else:
                name = "Type"

            self.__name_label.text = name

    def __on_policy_changed(self):
        stage_model = self.__stage_model
        if not stage_model:
            return

        if self.__items_sort_policy == TypeColumnSortPolicy.A_TO_Z:
            stage_model.set_items_sort_policy(StageItemSortPolicy.TYPE_COLUMN_A_TO_Z)
        elif self.__items_sort_policy == TypeColumnSortPolicy.Z_TO_A:
            stage_model.set_items_sort_policy(StageItemSortPolicy.TYPE_COLUMN_Z_TO_A)
        else:
            stage_model.set_items_sort_policy(StageItemSortPolicy.DEFAULT)

        self.__update_label_from_policy()

    def __on_name_label_clicked(self, x, y, b, m):
        stage_model = self.__stage_model
        if b != 0 or not stage_model:
            return

        if self.__items_sort_policy == TypeColumnSortPolicy.A_TO_Z:
            self.__items_sort_policy = TypeColumnSortPolicy.Z_TO_A
        elif self.__items_sort_policy == TypeColumnSortPolicy.Z_TO_A:
            self.__items_sort_policy = TypeColumnSortPolicy.DEFAULT
        else:
            self.__items_sort_policy = TypeColumnSortPolicy.A_TO_Z

        self.__on_policy_changed()

    def build_header(self, **kwargs):
        """Build the header"""

        stage_model = kwargs.get("stage_model", None)
        self.__stage_model = stage_model
        if stage_model:
            self.__name_label_layout = ui.HStack()
            with self.__name_label_layout:
                ui.Spacer(width=10)
                self.__name_label = ui.Label(
                    "Type", name="columnname", style_type_name_override="TreeView.Header"
                )
                self.__initialize_policy_from_model()

            self.__name_label_layout.set_mouse_pressed_fn(self.__on_name_label_clicked)
        else:
            self.__name_label_layout.set_mouse_pressed_fn(None)
            with ui.HStack():
                ui.Spacer(width=10)
                ui.Label("Type", name="columnname", style_type_name_override="TreeView.Header")

    async def build_widget(self, _, **kwargs):
        """Build the type widget"""
        item = kwargs.get("stage_item", None)
        if not item or not item.prim:
            return

        with ui.HStack(enabled=not item.instance_proxy and item.active, spacing=4, height=20, style=WIDGET_STYLES):
            ui.Spacer(width=4)
            ui.Label(item.type_name, width=0, name="object_name", style_type_name_override="TreeView.Item")

    def on_stage_items_destroyed(self, items: List[StageItem]):
        pass

    @property
    def sortable(self):
        return True

    @property
    def order(self):
        return -100

    @property
    def minimum_width(self):
        return ui.Pixel(20)
