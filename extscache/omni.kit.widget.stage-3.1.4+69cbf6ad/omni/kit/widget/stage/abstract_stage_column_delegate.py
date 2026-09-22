# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["AbstractStageColumnDelegate", "StageColumnItem"]

from pxr import Sdf, Usd
from typing import List, Union
from .stage_item import StageItem

import abc
import omni.ui as ui


class StageColumnItem:  # pragma: no cover
    """
    A dataclass that manages information needed for building columns for a StageItem.
    It's not clear what data we need to pass to build_widget. Apart from path, there are potentially other information
    the column has. To keep the API unchanged over time, we pass in data as a struct. It also allows passing in custom
    data derived from this class.
    """

    def __init__(self, path: Sdf.Path, stage: Usd.Stage, enabled: bool, expanded: bool = True):
        """
        Constructor.

        Args:
            path (Sdf.Path): Full path of the item
            stage (Usd.Stage): USD Stage
            enabled (bool): When false, the widget should be grayed out

        Keyword Args:
            expanded (bool): Whether the item should be expanded.
        """

        self._path = path
        self._stage = stage
        self._enabled = enabled
        self._expanded = expanded

    @property
    def path(self) -> Sdf.Path:
        """
        The path of the item.

        Returns:
            Sdf.Path: The path of the item.
        """
        return self._path

    @property
    def stage(self) -> Usd.Stage:
        """
        The stage that the item belongs to.

        Returns:
            Usd.Stage: The stage that the item belongs to.
        """
        return self._stage

    @property
    def enabled(self) -> bool:
        """
        Whether the item is enabled.

        Returns:
            bool: Enabled or not
        """
        return self._enabled

    @property
    def expanded(self) -> bool:
        """
        Whether the item is expanded.

        Returns:
            bool: Expanded or not
        """
        return self._expanded


class AbstractStageColumnDelegate(metaclass=abc.ABCMeta):  # pragma: no cover
    """
    An abstract object that is used to build stage widget columns.
    """

    def destroy(self):
        """Place to release resources."""
        pass

    @property
    def initial_width(self) -> Union[ui.Pixel, ui.Fraction, ui.Percent]:
        """
        The initial width of the column.

        Returns:
            Union[ui.Pixel, ui.Fraction, ui.Percent]: Column width
        """
        return ui.Fraction(1)

    @property
    def minimum_width(self) -> Union[ui.Pixel, ui.Fraction, ui.Percent]:
        """
        The minimum width of the column.

        Returns:
            Union[ui.Pixel, ui.Fraction, ui.Percent]: Minimum column width
        """
        return ui.Pixel(10)

    def build_header(self, **kwargs):
        """
        Builds the header widget. If the column is sortable, stage widget will build a background rectangle with hover
        state to indicate users if the column is sortable, so that all columns delegates don't need to build that by
        themselves. This can be overriden to build customized widgets as column header.
        """
        pass

    @abc.abstractmethod
    async def build_widget(self, item: StageColumnItem, **kwargs):
        """
        Builds the widget for the given path. Works inside a ui.Frame in async mode.
        Once the widget is created, it will replace the content of the frame. It allows to await something for a while
        and creates the widget when the result is available.

        Args:
            item (StageColumnItem): DEPRECATED. It includes the non-cached simple prim
                information. It's better to use keyword argument `stage_item` instead, which
                provides cached rich information about the prim influened by this column.

        Keyword Args:
            stage_model (StageModel): The instance of current StageModel.
            stage_item (StageItem): The current StageItem to build. It's possible that
                stage_item is None when TreeView enabled display of root node.
        """
        pass

    def on_header_hovered(self, hovered: bool):
        """
        Callback when header area is hovered.

        Args:
            hovered (bool): Whether the header area is hovered.
        """
        pass

    def on_stage_items_destroyed(self, items: List[StageItem]):
        """
        Called when stage items are destroyed to give the opportunity for delegates to release corresponding resources.

        Args:
            items (List[StageItem]): Stage items to be destroyed.
        """
        pass

    @property
    def sortable(self) -> bool:
        """
        Whether this column is sortable or not. When it's True, stage widget will build header widget with hover and
        selection state to tell user it's sortable. This is only used to indicate to users that this column is sortable
        from the UX point of view.

        Returns:
            bool: sortable or not
        """
        return False

    @property
    def order(self) -> int:
        """
        The order to sort columns. The columns are sorted in ascending order from left to right of the stage widget.
        So the smaller the order is, the closer the column is to the left of the stage widget.

        Returns:
            int: sort order
        """
        return 0

    @property
    def resizable(self):
        """
        Whether the column is resizable. If it's True, the column can be resized by dragging its border lines. If it's
        False, the column can't be resized. The default value is True.

        Returns:
            bool: resizable or not
        """
        return True
