# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import math
from typing import Any, Callable, Dict, Generic, List, Type

from carb import Float2, Float3
from omni.kit.app import deprecated
from omni.ui import scene

from .custom_types import _TWidget
from .manipulator_components.widget_component import WidgetComponent
from .transformable_manipulator import TransformableManipulator


class SceneWidgetManipulator(TransformableManipulator, Generic[_TWidget]):  # pragma: no cover
    @deprecated("Please use UiContainer instead")
    def __init__(self, widget_type: Type[_TWidget], *args, **kwargs):
        TransformableManipulator.__init__(self)  # type: ignore

        self._widget_holder: scene.Widget | None = None
        self._widget_type: Type[_TWidget] = widget_type
        self._build_callback: Callable[[_TWidget], None] | None = None
        self._size = Float2(100, 100)
        self._res_scale: float = 1.0
        self._unit_pixel_scale: float = 1.0

        self._color: List[float] = [1.0]

        self._transform_args: Dict[str, Any] = {}

        self._update_policy: scene.Widget.UpdatePolicy = scene.Widget.UpdatePolicy.ON_DEMAND

        self._widget_component: WidgetComponent[_TWidget] | None = None
        self._widget_args = args
        self._widget_kwargs = kwargs

    # ===== Size =====
    @property
    def size(self) -> Float2:
        return self._size

    @size.setter
    def size(self, size: Float2) -> None:
        """
        Set the contained widget's world size

        This is in world units, which is typically centimeters (for the sake of things like XR).

        ### Arguments
            `size : Tuple[float, float]`
                The size in (width, height) to allocate for displaying the contained widget
        """
        self._size = size
        if self._widget_component is not None:
            self._widget_component.width = self._size[0]
            self._widget_component.height = self._size[1]

    # ===== Resolution Scale =====
    @property
    def resolution_scale(self) -> float:
        return self._res_scale

    @resolution_scale.setter
    def resolution_scale(self, scale: float) -> None:
        """
        Set the contained widget's resolution scale

        Affects how much texture space is used and allotted when drawing the UI. Larger
        scales will result in a more dense texture being used as well as generally smoother
        UI appearing in the scene.

        ### Arguments
            `resolution_scale : float`
                The scale to set for drawing the widget's UI
        """
        self._res_scale = scale
        if self._widget_component is not None:
            self._widget_component.resolution_scale = self._res_scale

    @property
    def unit_pixel_scale(self) -> float:
        return self._unit_pixel_scale

    @unit_pixel_scale.setter
    def unit_pixel_scale(self, scale: float):
        self._unit_pixel_scale = scale
        if self._widget_component is not None:
            self._widget_component.unit_to_pixel_scale = self._unit_pixel_scale

    # ===== Rotation =====
    def set_rotation_radians(self, rot_vec: Float3) -> None:
        """
        Set the contained widget's rotation in radians along (x, y, z) in the scene

        ### Arguments
            `rotation_vec : Tuple[float, float, float]`
                The rotation values (in radians).
        """
        model = self.transform_model
        scale_item = model.rotation
        model.set_floats(scale_item, [rot_vec.x, rot_vec.y, rot_vec.z])

    def set_rotation_degrees(self, rot_vec: Float3) -> None:
        """
        Set the contained widget's rotation in radians along (x, y, z) in the scene

        ### Arguments
            `rotation_vec : Tuple[float, float, float]`
                The rotation values (in degrees).
        """
        radians = (math.radians(rot_vec[0]), math.radians(rot_vec[1]), math.radians(rot_vec[2]))
        model = self.transform_model
        scale_item = model.rotation
        model.set_floats(scale_item, [radians[0], radians[1], radians[2]])

    # ===== Color Tint =====
    @property
    def color(self) -> List[float]:
        return self._color

    @color.setter
    def color(self, color: List[float] | None):
        self._color = color or [1.0]
        if self._widget_component is not None:
            self._widget_component.color = self._color

    # ===== Transform =====
    def add_transform(self, kwargs: Dict[str, Any]) -> None:
        """ """
        self._transform_args = kwargs

    @property
    def update_policy(self):
        return self._update_policy

    @update_policy.setter
    def update_policy(self, update_policy: scene.Widget.UpdatePolicy) -> None:
        """ """
        self._update_policy = update_policy

    # ===== Callback =====
    def set_build_callback(self, callback: Callable[[_TWidget], None]) -> None:
        """
        Set a build callback function for the contained


        When the widget gets built, this function will be called and passed a reference
        to the newly created widget as an argument.

        ### Arguments
            `arg : type`
                desc
        """
        self._build_callback = callback

    def build_func(self) -> None:
        self._widget_component = WidgetComponent(
            self._widget_type,
            int(self._size.x),
            int(self._size.y),
            self._res_scale,
            self._unit_pixel_scale,
            self._build_callback,
            self._transform_args,
            self._update_policy,
            self._color,
            self._widget_args,
            self._widget_kwargs,
        )
        self.add_component(self._widget_component)

        super().build_func()

    def redraw(self):
        self.invalidate()

    def get_widget(self) -> _TWidget | None:
        """
        Get a reference to the actual underlying widget

        If it has not been created already, returns `None`

        ### Returns
            The contained widget, or None if it has not been initialized yet
        """
        if not self._widget_component:
            return None

        return self._widget_component.widget
