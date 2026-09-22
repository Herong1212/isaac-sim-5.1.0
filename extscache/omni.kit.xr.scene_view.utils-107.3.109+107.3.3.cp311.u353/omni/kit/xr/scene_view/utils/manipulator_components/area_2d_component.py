# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = [
    "Area2DComponent",
]

from dataclasses import dataclass
from weakref import ProxyType

import carb
from carb import Float2
from omni.ui import scene as sc

from ..composable_manipulator import ComposableManipulator, ManipulatorComponent


class Area2DComponent(ManipulatorComponent):
    """
    A base ManipulatorComponent which describes a 2D rectangle with width/height and center position ratio.

    Supports child Area2DComponent objects placed relative to this object's area.
    """

    CENTER = Float2(0.0, 0.0)
    LEFT = Float2(-1.0, 0.0)
    TOP_LEFT = Float2(-1.0, 1.0)
    TOP = Float2(0.0, 1.0)
    TOP_RIGHT = Float2(1.0, 1.0)
    RIGHT = Float2(1.0, 0.0)
    BOTTOM_RIGHT = Float2(1.0, -1.0)
    BOTTOM = Float2(0.0, -1.0)
    BOTTOM_LEFT = Float2(-1.0, -1.0)

    @dataclass
    class _ChildContainer:
        """
        component: Area2DComponent
        transform: sc.Transform created at build time by the parent
        placement: Float2
        """

        component: "Area2DComponent"
        transform: sc.Transform | None
        placement: Float2

    def __init__(
        self,
        width: float,
        height: float,
        origin: Float2 = CENTER,
        z_offset: float = 0.0,
        **kwargs,
    ) -> None:
        """Create an Area2DComponent, describing a 2D space.

        Args:
            width:
                The width of the area.
            height:
                The height of the area.
            origin:
                The point on the described area to be its origin. I.e., if CENTER, the area will extend
                equal distances horizontally, and equal distances vertically, from its position in space.
                If "TOP_LEFT", then the area's top-left corner will be at its spatial position and the
                described width and height will extend "right" and "down" from there the whole amount.
        """
        super().__init__(**kwargs)

        self.__width = width
        self.__height = height
        self.__origin = origin
        self.__child_z_offset = z_offset

        self.__transform: sc.Transform | None = None
        self.__owner: "ProxyType[ComposableManipulator] | None" = None

        self.__children: list["Area2DComponent._ChildContainer"] = []

        self.__calc_derived_dimensions()

    def __del__(self):
        if self.__transform:
            self.__transform.clear()
        # ManipulatorComponent is an ABC, and has no __del__ method to call

    def _update_dimensions(self):
        self.__calc_derived_dimensions()

    def __calc_derived_dimensions(self):
        self.__half_width = self.__width / 2.0
        self.__half_height = self.__height / 2.0
        self.__x_offset = -self.__origin.x * self.__half_width
        self.__y_offset = -self.__origin.y * self.__half_height

        if self.__transform is not None:
            self.__transform.transform = sc.Matrix44.get_translation_matrix(self.__x_offset, self.__y_offset, 0.0)

        for child in self.__children:
            if child.transform is not None:
                x_offset = child.placement.x * self.__half_width
                y_offset = child.placement.y * self.__half_height
                child.transform.transform = sc.Matrix44.get_translation_matrix(
                    x_offset, y_offset, self.__child_z_offset
                )

    @property
    def width(self) -> float:
        """The width of the described 2D area"""
        return self.__width

    @width.setter
    def width(self, width: float):
        self.__width = width
        self._update_dimensions()

    @property
    def height(self) -> float:
        """The height of the described 2D area"""
        return self.__height

    @height.setter
    def height(self, height: float):
        self.__height = height
        self._update_dimensions()

    @property
    def transform(self) -> sc.Transform | None:
        if self.__transform is None:
            carb.log_warn("transform wasn't set")
        return self.__transform

    @property
    def owner(self) -> "ProxyType[ComposableManipulator] | None":
        return self.__owner

    def add_child(self, child: "Area2DComponent", placement: Float2 = CENTER):
        """Add a child component to this area

        Children align their "origin" to the location described by the "placement" argument. For
        example, if a child has their "origin" set to BOTTOM and the "placement" argument is "TOP",
        then the child will sit along the top edge of the area, centered horizontally.

        Args:
            child:
                The component which will be added as a child of this area.
            placement:
                Where on the described area to align the child's "origin".
        """
        container = self._ChildContainer(child, None, placement)
        self.__children.append(container)

        if self.__transform is not None and self.__owner is not None:
            self.__owner.invalidate()

    def _do_build(self, owner: "ProxyType[ComposableManipulator]") -> None:
        # super() is an ABC where _do_build is marked abstract
        self.__owner = owner
        self.__transform = sc.Transform(
            transform=sc.Matrix44.get_translation_matrix(self.__x_offset, self.__y_offset, 0.0)
        )

        with self.__transform:
            for child in self.__children:
                x_offset = child.placement.x * self.__half_width
                y_offset = child.placement.y * self.__half_height
                child.transform = sc.Transform(
                    transform=sc.Matrix44.get_translation_matrix(x_offset, y_offset, self.__child_z_offset)
                )
                with child.transform:
                    child.component._do_build(self.__owner)
