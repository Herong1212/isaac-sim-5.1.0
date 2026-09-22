# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = [
    "WidgetComponent",
    "UpdatePolicy",
]

import contextlib
from collections.abc import Iterable
from typing import Any, Callable, Dict, Generic, List, Tuple, Type, TypeAlias
from weakref import ProxyType

from omni import ui
from omni.kit.xr.core import XRWeakMethod
from omni.ui import scene as sc

from ..composable_manipulator import ComposableManipulator
from ..custom_types import _TWidget
from .area_2d_component import Area2DComponent

# Aliased and reexported more simply
UpdatePolicy: TypeAlias = sc.Widget.UpdatePolicy


class WidgetComponent(Area2DComponent, Generic[_TWidget]):
    """
    Container and component class for Widgets to show up in a Scene UI hierarchy.

    By specifying the UI class, it's possible to construct the component before it's needed
    for the UI hierarchy. This class will maintain the appropriate lifecycle for you.
    """

    def __init__(
        self,
        widget_type: Type[_TWidget],
        width: float = 100,
        height: float = 100,
        resolution_scale: float = 1.0,
        unit_to_pixel_scale: float = 1.0,
        construct_callback: Callable[[_TWidget], None] | None = None,
        transform_args: Dict[str, Any] | None = None,
        update_policy: UpdatePolicy = UpdatePolicy.ON_MOUSE_HOVERED,
        color: List[float] | None = None,
        widget_args: Tuple[Any, ...] | List[Any] | Any | None = None,
        widget_kwargs: Dict[str, Any] | None = None,
        **kwargs,
    ):
        """Construct a scene WidgetContainer for the specified widget_type.

        Args:
            widget_type:
                The class name of the UI widget that should be created and displayed in scene.
            width:
                The horizontal scene space to allow for the contained UI widget.
            height:
                The vertical scene space to allow for the contained UI widget.
            resolution_scale:
                The ratio of UI pixels to fit into one "unit" of world space. Higher numbers
                result in a higher-resolution (smoother) UI in the scene, similar to UI scaling on a display.
            unit_to_pixel_scale:
                Multiply how many UI pixels are represented in the same UI/scene space.
                Higher values result in smaller in-world UI details. (Smaller text, buttons, borders, etc).
            construct_callback:
                This will be called after the contained UI widget has been created, useful in case you need
                to do some additional setup with a live UI widget instance that cannot be done via args or
                kwargs.
            transform_args: Deprecated. Do not use.
            update_policy:
                How should the UI update be handled.
            color:
                Tints the whole UI widget this color. Default is white (no tint).
            widget_args:
                Args that need to be forwarded to the UI Widget class when it's created.
            widget_kwargs:
                Kwargs that need to be forwarded to the UI Widget class when it's created.
        """
        Area2DComponent.__init__(self, width, height, **kwargs)

        self.__widget_args: tuple[Any, ...]
        match widget_args:
            case str():
                self.__widget_args = (widget_args,)
            case Iterable():
                self.__widget_args = tuple(widget_args)
            case None:
                self.__widget_args = tuple()
            case _:
                self.__widget_args = (widget_args,)

        self.__scene_widget: sc.Widget | None = None
        self.__widget_type = widget_type
        self.__widget: _TWidget | None = None
        self.__resolution_scale: float = resolution_scale
        self.__unit_to_pixel_scale: float = unit_to_pixel_scale
        self.__callback = construct_callback
        self.__transform_args = transform_args
        self.__update_policy = update_policy
        self.__color: List[float] = color or [1.0]
        self.__widget_kwargs = widget_kwargs or {}

    def _update_dimensions(self):
        super()._update_dimensions()
        if self.__scene_widget is not None:
            self.__scene_widget.resolution_scale = self.resolution_scale

            pixel_res_scale = self.resolution_scale * self.unit_to_pixel_scale
            self._pixel_width = int(self.width * pixel_res_scale)
            self._pixel_height = int(self.height * pixel_res_scale)

            self.__scene_widget.resolution_width = self._pixel_width
            self.__scene_widget.resolution_height = self._pixel_height

            self.__scene_widget.width = self.width
            self.__scene_widget.height = self.height
            self.__scene_widget.invalidate()

    # ===== resolution_scale =====
    @property
    def resolution_scale(self) -> float:
        return self.__resolution_scale

    @resolution_scale.setter
    def resolution_scale(self, scale):
        self.__resolution_scale = scale
        self._update_dimensions()

    # ===== unit_to_pixel_scale =====
    @property
    def unit_to_pixel_scale(self) -> float:
        return self.__unit_to_pixel_scale

    @unit_to_pixel_scale.setter
    def unit_to_pixel_scale(self, scale: float):
        self.__unit_to_pixel_scale = scale
        self._update_dimensions()

    # ===== color =====
    @property
    def color(self) -> List[float] | None:
        """The color tint applied to the UI."""
        return self.__color

    @color.setter
    def color(self, color: List[float] | None):
        self.__color = color or [1.0]
        if self.__scene_widget is not None:
            self.__scene_widget.color = self.__color

    # ===== scene widget =====
    @property
    def scene_widget(self) -> sc.Widget | None:
        return self.__scene_widget

    # ===== widget =====
    @property
    def widget(self) -> _TWidget | None:
        """The underlying omni.ui.Widget instance."""
        return self.__widget

    def __build_ui_contents(self):
        # Inject a container to help some existing widgets work better
        with ui.Frame():
            self.__widget = self.__widget_type(*self.__widget_args, **self.__widget_kwargs)

        if self.__callback:
            self.__callback(self.__widget)

    def _do_build(self, owner: "ProxyType[ComposableManipulator]") -> None:
        with contextlib.ExitStack() as stack:
            # This has always been implemented inconsistently, and will be removed in the next MR
            if self.__transform_args is not None:
                stack.enter_context(sc.Transform(**self.__transform_args))

            # Execute the base build, which offsets the anchor and builds children,
            # then enter the base transform (for the anchor offset) and then we can
            # build the rest of the widget.
            super()._do_build(owner)
            if self.transform is not None:
                stack.enter_context(self.transform)

            # Widget must be created in the context (__enter__) of its containing transforms
            self.__scene_widget = sc.Widget(self.width, self.height)
            self.__scene_widget.update_policy = self.__update_policy

            # TODO: Can I reassign the widgets gestures to use the owner's gesture manager(s)?
            # for gesture in self.__scene_widget.gestures:
            #     gesture.manager = owner.gesture_manager

            # TODO: Would this handle varying Z/Y "up" axes?
            # self.__scene_widget.axis = ???

            # Resolution and scale can technically be set from anywhere, but here is fine
            self.__scene_widget.resolution_scale = self.__resolution_scale
            self.__scene_widget.resolution_width = int(
                self.width * self.__resolution_scale * self.__unit_to_pixel_scale
            )
            self.__scene_widget.resolution_height = int(
                self.height * self.__resolution_scale * self.__unit_to_pixel_scale
            )

            # Color works like a filter for the whole component
            self.__scene_widget.color = self.__color

            # Setting a build_fn function allows us to call `invalidate` on the holder when necessary
            weak_build_fn = XRWeakMethod(self.__build_ui_contents)
            self.__scene_widget.frame.set_build_fn(weak_build_fn)
