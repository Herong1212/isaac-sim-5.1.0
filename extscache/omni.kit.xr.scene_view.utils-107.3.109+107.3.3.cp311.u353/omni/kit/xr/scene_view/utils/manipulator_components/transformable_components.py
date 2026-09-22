# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = [
    "BaseTransformableComponent",
    "TranslationHandleComponent",
    "RotationHandleComponent",
    "ScaleHandleComponent",
    "Resize2DHandleComponent",
]

from abc import abstractmethod
from weakref import ProxyType, proxy

import carb
from omni.ui import scene as sc

from ..composable_manipulator import ComposableManipulator
from ..gestures import Resize2DGestureHandler, RotationGestureHandler, ScaleGestureHandler, TranslationGestureHandler
from ..transformable_manipulator import TransformableManipulator, TransformableManipulatorModel
from .area_2d_component import Area2DComponent


class BaseTransformableComponent(Area2DComponent):
    def _do_build(self, owner: "ProxyType[ComposableManipulator]") -> None:
        super()._do_build(owner)

        if not isinstance(owner, TransformableManipulator):
            carb.log_error(f"owner {owner} is not a TransformableManipulator")
            return

        if not isinstance(owner.model, TransformableManipulatorModel):
            carb.log_error(f"Model {owner.model} is not a TransformableManipulatorModel")
            return

        assert self.transform is not None, "BaseTransformableComponent should never have a None transform"
        with self.transform:
            self._build_handle_component()

    @abstractmethod
    def _build_handle_component(self): ...


class TranslationHandleComponent(BaseTransformableComponent):
    def _build_handle_component(self) -> None:
        assert self.owner is not None, "Owner was None"
        sc.Rectangle(
            self.width,
            self.height,
            gestures=[
                TranslationGestureHandler(
                    self.owner.model,
                    manager=self.owner.gesture_manager,
                    name="TranslationGestureHandler",  # type: ignore[arg-type, union-attr]
                ),
            ],
        )


class RotationHandleComponent(BaseTransformableComponent):
    def _build_handle_component(self) -> None:
        assert self.owner is not None, "Owner was None"
        sc.Rectangle(
            self.width,
            self.height,
            gestures=[
                RotationGestureHandler(
                    self.owner.model,
                    manager=self.owner.gesture_manager,
                    name="RotationGestureHandler",
                ),  # type: ignore[arg-type, union-attr]
            ],
        )


class ScaleHandleComponent(BaseTransformableComponent):
    def _build_handle_component(self) -> None:
        assert self.owner is not None, "Owner was None"
        sc.Rectangle(
            self.width,
            self.height,
            gestures=[
                ScaleGestureHandler(
                    self.owner.model,
                    manager=self.owner.gesture_manager,
                    name="ScaleGestureHandler",
                ),  # type: ignore[arg-type, union-attr]
            ],
        )


class Resize2DHandleComponent(BaseTransformableComponent):
    def __init__(self, target: Area2DComponent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__target = proxy(target)

    def _build_handle_component(self) -> None:
        assert self.owner is not None, "Owner was None"
        sc.Rectangle(
            self.width,
            self.height,
            gestures=[
                Resize2DGestureHandler(
                    self.owner.model,
                    self.__target,
                    manager=self.owner.gesture_manager,
                    name="Resize2DGestureHandler",  # type: ignore[arg-type, union-attr]
                )
            ],
        )
