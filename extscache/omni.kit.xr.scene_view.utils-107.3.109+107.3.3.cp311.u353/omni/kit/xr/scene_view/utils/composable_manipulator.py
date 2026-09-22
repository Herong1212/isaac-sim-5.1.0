# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ManipulatorComponent", "ComposableManipulator"]

import contextlib
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from weakref import ProxyType, ReferenceType, WeakMethod, proxy, ref

import carb
from omni.ui import scene as sc


class ManipulatorComponent(ABC):
    """
    An interface base class for building components that can be added to a ComposableManipulator.

    Declared the abstract method _do_build(...) which must be implemented by child classes.
    """

    @abstractmethod
    def _do_build(self, owner: "ProxyType[ComposableManipulator]") -> None: ...

    def __del__(self):
        carb.log_info("[XR] ManipulatorComponent being destroyed")


class ConfigurableManipulator(sc.Manipulator):
    """
    A mostly pass-through subclass of sc.Manipulator, but containing customizable build and model update callbacks,
    whereas the base class (as a bound C++ class) cannot have its on_build and on_model_updated functions overwritten.
    """

    def __init__(self):
        super().__init__()
        self.__build_callback_ref: WeakMethod[Callable[..., None]] | None = None
        self.__model_updated_callback_ref: WeakMethod[Callable[[Any], None]] | None = None

    # -------------------------------------------
    def on_build(self) -> None:
        """override sc.Manipulator.on_build"""
        if self.__build_callback_ref is not None:
            strong_callback = self.__build_callback_ref()
            if strong_callback is not None:
                strong_callback()
        super().on_build()

    @property
    def build_callback(self) -> Callable[..., None] | None:
        if self.__build_callback_ref is not None:
            return self.__build_callback_ref()
        return None

    @build_callback.setter
    def build_callback(self, callback: Callable[..., None] | None):
        if callback is not None:
            self.__build_callback_ref = WeakMethod(callback)
        else:
            self.__build_callback_ref = None

    # -------------------------------------------
    def on_model_updated(self, item: Any) -> None:
        """override sc.Manipulator.on_model_updated"""
        if self.__model_updated_callback_ref is not None:
            strong_callback = self.__model_updated_callback_ref()
            if strong_callback is not None:
                strong_callback(item)
        super().on_model_updated(item)

    @property
    def model_updated_callback(self) -> Callable[[Any], None] | None:
        if self.__model_updated_callback_ref is not None:
            return self.__model_updated_callback_ref()
        return None

    @model_updated_callback.setter
    def model_updated_callback(self, callback: Callable[[Any], None] | None):
        if callback is not None:
            self.__model_updated_callback_ref = WeakMethod(callback)
        else:
            self.__model_updated_callback_ref = None


@dataclass
class _ComponentInfo:
    component: ManipulatorComponent
    offset: sc.Matrix44 | None = None


class ComposableManipulator:
    """
    A wrapper around omni.ui.scene.Manipulator which can be given child components and automate building them and
    managing their life cycles.

    When dropped, ComposableManipulator attempts to clean up all the children as much as possible. Note that due to
    limitations with the omni.ui.scene library, it's not possible to completely clean up all the used memory when
    ComposableManipulator is garbage collected. It's semi-possible to do this yourself by instantiating
    ComposableManipulator inside the context of some other omni.ui.scene.AbstractContainer subclass instance and then
    calling the clear() method on that instance.
    """

    def __init__(self, gesture_manager: sc.GestureManager = sc.GestureManager()):
        # sc.Manipulator isn't garbage collected if it has children, so as a workaround, we hold one internally
        # so that we can clear its children when we're dropped normally so that it can be cleaned up properly.
        self.__internal_manipulator = ConfigurableManipulator()
        self.__internal_manipulator.build_callback = self.build_func
        self.__internal_manipulator.model_updated_callback = self.model_updated_func

        self.__components: list[_ComponentInfo] = list()
        self.__has_built: bool = False
        self._gesture_manager: sc.GestureManager = gesture_manager

    def __enter__(self):
        """Pass through to the owned manipulator object"""
        self.__internal_manipulator.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        """Pass through to the owned manipulator object"""
        self.__internal_manipulator.__exit__(exc_type, exc_value, traceback)

    @property
    def model(self) -> sc.AbstractManipulatorModel | None:
        return self.__internal_manipulator.model

    @model.setter
    def model(self, value: sc.AbstractManipulatorModel | None) -> None:
        # Model can absolutely be None, but the pybind .pyi just doesn't show that
        self.__internal_manipulator.model = value  # type: ignore

    @property
    def gestures(self) -> Any:
        return self.__internal_manipulator.gestures

    @gestures.setter
    def gestures(self, value: Any) -> None:
        self.__internal_manipulator.gestures = value

    def invalidate(self) -> None:
        self.__internal_manipulator.invalidate()

    def clear(self):
        self.__components.clear()
        self.__has_built = False
        self.__internal_manipulator.clear()
        self.__internal_manipulator.build_callback = None

    def add_component(self, component: ManipulatorComponent, offset: sc.Matrix44 | None = None) -> None:
        if offset is None:
            offset = sc.Matrix44.get_translation_matrix(0, 0, 0)
        self.__components.append(_ComponentInfo(component, offset))
        if self.__has_built:
            self.__internal_manipulator.invalidate()

    @property
    def gesture_manager(self) -> sc.GestureManager:
        return self._gesture_manager

    def build_func(self) -> None:
        for comp in self.__components:
            with contextlib.ExitStack() as stack:
                if comp.offset is not None:
                    stack.enter_context(sc.Transform(transform=comp.offset))
                comp.component._do_build(proxy(self))

        self.__has_built = True

    def model_updated_func(self, item) -> None:
        pass

    def _get_internal_manipulator_weakref(self) -> ReferenceType[ConfigurableManipulator]:
        return ref(self.__internal_manipulator)
