# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["USDObjectModel"]

from typing import Any

import omni.kit.undo
import omni.ui as ui
from pxr import Sdf, Usd

from ..utils.usd_watch import subscribe as usd_watch_subscribe


class USDObjectModel(ui.AbstractValueModel):
    """A base-class model to watch changes on a UsdObject (UsdPrim, UsdProperty, UsdAttribute, UsdRelationship)."""

    # To be implemented by sub-classes to handle the Get/Set from USD
    def set_value(self, value: Any):
        """Set the value directly to USD"""
        raise RuntimeError("USDObjectModel.set_value is not implemented for the base class")

    def _get_value(self) -> Any:
        """Get the value directly from USD"""
        raise RuntimeError("USDObjectModel._get_value is not implemented for the base class")

    # Accessors that base-class owns but subclasses can read
    @property
    def stage(self):
        return self.__stage

    @property
    def path(self):
        return self.__path

    @property
    def time(self):
        return self.__time

    @property
    def draggable(self) -> bool:
        return self._draggable

    @draggable.setter
    def draggable(self, enable: bool) -> None:
        self._draggable = enable

    def __init__(self, stage: Usd.Stage, path: Sdf.Path, time: Usd.TimeCode = None, draggable: bool = False):
        super().__init__()
        self.__path = path
        self.__stage = stage
        self.__listener = usd_watch_subscribe(stage, path, self._on_usd_changed)  # noqa: PLW0238
        self.__time = Usd.TimeCode.Default() if time is None else time
        self._in_edit = False
        self._draggable = draggable

    def destroy(self):
        self.__stage = None
        self.__listener = None  # noqa: PLW0238
        self.__time = None

    def get_value_as_bool(self) -> bool:
        value = self._get_value()
        return bool(value) if value is not None else False

    def get_value_as_int(self) -> int:
        value = self._get_value()
        return int(value) if value is not None else 0

    def get_value_as_float(self) -> float:
        value = self._get_value()
        return float(value) if value is not None else 0.0

    def get_value_as_string(self) -> str:
        value = self._get_value()
        return str(value) if value is not None else ''

    def begin_edit(self):
        """
        Reimplemented from the base class.
        Called when the user starts editing.
        """
        self._in_edit = True
        omni.kit.undo.begin_group()
        super().begin_edit()

    def end_edit(self):
        """
        Set value when the user finishes editing.
        """
        self._in_edit = False
        super().end_edit()
        omni.kit.undo.end_group()

        # Update widget
        self._value_changed()

    def _on_usd_changed(self):
        """Called by UsdWatch"""
        if not self._in_edit or self._draggable:
            # OM-47170: donot upodate widget when editing
            self._value_changed()
