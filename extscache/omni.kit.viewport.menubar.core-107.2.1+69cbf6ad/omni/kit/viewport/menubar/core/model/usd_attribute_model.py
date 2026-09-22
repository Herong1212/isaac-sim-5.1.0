# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["USDAttributeModel", "USDIntAttributeModel", "USDFloatAttributeModel", "USDStringAttributeModel"]

import math
from typing import Any, Optional

import omni.kit.commands
import omni.usd
from pxr import Gf, Sdf, Usd, UsdUtils

from .usd_object_model import USDObjectModel


class USDAttributeModel(USDObjectModel):
    """A simple value model to watch the specified attribute."""

    def __init__(self, stage: Usd.Stage, path: Sdf.Path, prop_name: str, prop_type: Sdf.ValueTypeNames = None, draggable: bool = False):
        """
        Constructor.

        Args:
            stage (Usd.Stage): USD stage.
            path (Sdf.Path): Path in stage.
            prop_name (str): Attribute name.

        Keyword Args:
            prop_type (Sdf.ValueTypeNames): Attribute type, defaults to None means get type from attribute value.
            draggable (bool): Widget that model bind to can be dragged, defaults to False.
        """
        super().__init__(stage, path.AppendProperty(prop_name), draggable=draggable)
        self.__prop_type = prop_type

        stage_id = UsdUtils.StageCache.Get().GetId(stage)
        if not stage_id.IsValid():
            self.__stage_id = None
        else:
            self.__stage_id = stage_id.ToLongInt()

    def get_type_name(self, value: Any) -> Optional[Sdf.ValueTypeNames]:
        """Return the explicitly requested property type, or one auto-deduced from the value"""
        if self.__prop_type is not None:
            return self.__prop_type

        if isinstance(value, bool):
            return Sdf.ValueTypeNames.Bool
        if isinstance(value, int):
            return Sdf.ValueTypeNames.Int
        if isinstance(value, float):
            return Sdf.ValueTypeNames.Float
        if isinstance(value, str):
            return Sdf.ValueTypeNames.String
        if isinstance(value, Gf.Vec2f):
            return Sdf.ValueTypeNames.Vector2f
        if isinstance(value, Gf.Vec2d):
            return Sdf.ValueTypeNames.Vector2d
        if isinstance(value, Gf.Vec3f):
            return Sdf.ValueTypeNames.Vector3f
        if isinstance(value, Gf.Vec3d):
            return Sdf.ValueTypeNames.Vector3d
        if isinstance(value, Gf.Vec4f):
            return Sdf.ValueTypeNames.Vector4f
        if isinstance(value, Gf.Vec4d):
            return Sdf.ValueTypeNames.Vector4d

        return None

    def set_value(self, value: Any) -> None:
        """
        Set the value directly to USD.

        Args:
            value (Any): Value to set.
        """
        prev = self._get_value()
        # Only change value when changed
        if self._is_value_changed(prev, value):
            usd_context = ''
            if self.__stage_id is not None:
                usd_context = omni.usd.get_context_from_stage_id(self.__stage_id)
            omni.kit.commands.execute('ChangePropertyCommand',
                                      prop_path=self.path, value=value, prev=prev, timecode=self.time,
                                      type_to_create_if_not_exist=self.get_type_name(value),
                                      usd_context_name=usd_context)

    def _get_value(self) -> Any:
        """Get the value directly from USD"""
        obj = self.stage.GetPropertyAtPath(self.path) if self.stage else None
        return obj.Get(self.time) if obj else None

    def _is_value_changed(self, prev, current):
        return prev != current


class USDBoolAttributeModel(USDAttributeModel):
    """A simple value model to watch the boolean attribute."""
    def __init__(self, stage: Usd.Stage, path: Sdf.Path, prop_name: str):
        """
        Constructor.

        Args:
            stage (Usd.Stage): USD stage.
            path (Sdf.Path): Path in stage.
            prop_name (str): Attribute name.
        """
        super().__init__(stage, path, prop_name, Sdf.ValueTypeNames.Bool)

    def set_value(self, value: bool):
        """
        Set the value directly to USD.

        Args:
            value (bool): New value to set.
        """
        super().set_value(bool(value))


class USDIntAttributeModel(USDAttributeModel):
    """A simple value model to watch the integer attribute."""
    def __init__(self, stage: Usd.Stage, path: Sdf.Path, prop_name: str):
        """
        Constructor.

        Args:
            stage (Usd.Stage): USD stage.
            path (Sdf.Path): Path in stage.
            prop_name (str): Attribute name.
        """
        super().__init__(stage, path, prop_name, Sdf.ValueTypeNames.Int)

    def set_value(self, value: int):
        """
        Set the value directly to USD.

        Args:
            value (int): New value to set.
        """
        super().set_value(int(value))


class USDFloatAttributeModel(USDAttributeModel):
    """A simple value model to watch the float attribute."""
    def __init__(self, stage: Usd.Stage, path: Sdf.Path, prop_name: str, draggable: bool = False):
        """
        Constructor.

        Args:
            stage (Usd.Stage): USD stage.
            path (Sdf.Path): Path in stage.
            prop_name (str): Attribute name.

        Keyword Args:
            draggable (bool): Widget that model bind to can be dragged, defaults to False.
        """
        super().__init__(stage, path, prop_name, Sdf.ValueTypeNames.Float, draggable=draggable)

    def set_value(self, value: float):
        """
        Set the value directly to USD.

        Args:
            value (float): New value to set.
        """
        try:
            value = float(value)
        except (ValueError, TypeError):
            value = 0.0
        super().set_value(value)

    def _is_value_changed(self, prev, current):
        return True if prev is None else not math.isclose(prev, current, rel_tol=1e-5)


class USDStringAttributeModel(USDAttributeModel):
    """A simple value model to watch the string attribute."""
    def __init__(self, stage: Usd.Stage, path: Sdf.Path, prop_name: str):
        """
        Constructor.

        Args:
            stage (Usd.Stage): USD stage.
            path (Sdf.Path): Path in stage.
            prop_name (str): Attribute name.
        """
        super().__init__(stage, path, prop_name, Sdf.ValueTypeNames.String)

    def set_value(self, value: str):
        """
        Set the value directly to USD.

        Args:
            value (str): New value to set.
        """
        super().set_value(str(value))

# TODO: UsdTokenAttribute using allowedTokens to model an enum
