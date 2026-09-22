# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""Abstract transform manipulator model and manipulator operations"""

from __future__ import annotations

from typing import List

from omni.ui import scene as sc

from .types import Operation


class AbstractTransformManipulatorModel(sc.AbstractManipulatorModel):
    """An abstract base class for transform manipulator models.

    This class provides a common interface for manipulation operations such as translate, rotate, and scale. Models derived from this class are responsible for updating the manipulator's state and reflecting changes onto the underlying data.

    Args:
        **kwargs: Arbitrary keyword arguments that will be passed to AbstractTransformManipulatorModel."""

    class OperationItem(sc.AbstractManipulatorItem):
        """A class representing an operation item for transform manipulators.

        Encapsulates an operation type to be used within transform manipulator models, such as translation, rotation, and scaling.

        Args:
            operation: Operation
                The specific transform operation this item represents."""

        def __init__(self, op: Operation):
            super().__init__()
            self._op = op

        @property
        def operation(self):
            return self._op

    def __init__(self, **kwargs):
        """Initialize an abstract base class for transform manipulator models."""
        super().__init__(**kwargs)

        self._translate_item = AbstractTransformManipulatorModel.OperationItem(Operation.TRANSLATE)
        self._rotate_item = AbstractTransformManipulatorModel.OperationItem(Operation.ROTATE)
        self._scale_item = AbstractTransformManipulatorModel.OperationItem(Operation.SCALE)
        self._transform_item = sc.AbstractManipulatorItem()
        self._translate_delta_item = AbstractTransformManipulatorModel.OperationItem(Operation.TRANSLATE_DELTA)
        self._rotate_delta_item = AbstractTransformManipulatorModel.OperationItem(Operation.ROTATE_DELTA)
        self._scale_delta_item = AbstractTransformManipulatorModel.OperationItem(Operation.SCALE_DELTA)

        self._items = {
            "translate": self._translate_item,
            "rotate": self._rotate_item,
            "scale": self._scale_item,
            "transform": self._transform_item,
            "translate_delta": self._translate_delta_item,
            "rotate_delta": self._rotate_delta_item,
            "scale_delta": self._scale_delta_item,
        }

    def get_as_floats(self, item: sc.AbstractManipulatorItem) -> List[float]:
        """
        Return the operation items as a list of floats. Called by manipulator to fetch item values.

        Args:
            item (sc.AbstractManipulatorItem): input manipulator item.

        Returns:
            List[float]: a composed Matrix4x4 transform in world space as a list of float.
        """
        ...

    def get_as_floats(self, item: sc.AbstractManipulatorItem) -> List[int]:
        """
        Return the operation items as a list of ints. Called by manipulator to fetch item values.

        Args:
            item (sc.AbstractManipulatorItem): input manipulator item.

        Returns:
            List[int]: a composed Matrix4x4 transform in world space as a list of int.
        """
        ...

    def get_item(self, name: str) -> sc.AbstractManipulatorItem:
        """
        Return manipulator item by name. See AbstractManipulatorItem.get_item

        Args:
            name: manipulator name.

        Returns:
            sc.AbstractManipulatorItem: manipulator item matches the input name.
        """
        return self._items.get(name, None)

    def widget_enabled(self):
        """
        Called by hosting manipulator widget(s) when they're enabled.
        It can be used to track if any hosting manipulator is active to skip background model update (i.e. running listener for changes).
        """
        ...

    def widget_disabled(self):
        """
        Called by hosting manipulator widget(s) when they're disabled.
        It can be used to track if any hosting manipulator is active to skip background model update (i.e. running listener for changes).
        """
        ...

    def set_floats(self, item: sc.AbstractManipulatorItem, value: List[float]):
        """
        Called when the manipulator is being dragged and value changes, or set by external code to overwrite the value.
        The model should update value to underlying data holder(s) (e.g. a USD prim(s)).

        Depending on the model implemetation, item and value can be customized to model's needs.

        Args:
            item (sc.AbstractManipulatorItem): input manipulator item.
            value (List[float]): a composed Matrix4x4 transform in world space as a list of float.
        """
        ...

    def set_ints(self, item: sc.AbstractManipulatorItem, value: List[int]):
        """
        Called when the manipulator is being dragged and value changes, or set by external code to overwrite the value.
        The model should update value to underlying data holder(s) (e.g. a USD prim(s)).

        Depending on the model implemetation, item and value can be customized to model's needs.

        Args:
            item (sc.AbstractManipulatorItem): input manipulator item.
            value (List[float]): a composed Matrix4x4 transform in world space as a list of int.
        """
        ...

    def get_operation(self) -> Operation:
        """
        Called by the manipulator to determine which operation is active.

        Returns:
            Operation: The specific transform operation this item represents.
        """
        ...

    def get_snap(self, item: sc.AbstractManipulatorItem):
        """
        Called by the manipulator, returns the minimal increment step for each operation. None if no snap should be performed.
        Different Operation requires different return values:
        - TRANSLATE: Tuple[float, float, float]. One entry for X/Y/Z axis.
        - ROTATE: float. Angle in degree.
        - SCALE: float

        Args:
            sc.AbstractManipulatorItem: input manipulator item.
        Returns:
            None
        """
        return None
