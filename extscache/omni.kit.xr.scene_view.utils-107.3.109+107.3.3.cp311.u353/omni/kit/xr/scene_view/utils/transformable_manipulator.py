# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TransformableManipulatorModel", "TransformableManipulator"]

import math
from collections.abc import Sequence
from typing import overload

from carb import Float3
from numpy.typing import ArrayLike
from omni.ui import scene as sc
from pxr import Gf

from .composable_manipulator import ComposableManipulator
from .gesture_managers import PreventGestureOverlap


class TransformableManipulatorModel(sc.AbstractManipulatorModel):
    class Vec3Item(sc.AbstractManipulatorItem):
        @overload
        def __init__(self, initial: Sequence = (0.0, 0.0, 0.0)): ...

        @overload
        def __init__(self, initial: ArrayLike = [0.0, 0.0, 0.0]): ...

        def __init__(self, initial=(0.0, 0.0, 0.0)):
            super().__init__()
            self.__value: Float3 = Float3(initial)

        @property
        def value(self) -> Float3:
            return self.__value

        @value.setter
        @overload
        def value(self, v: Sequence) -> None: ...

        @value.setter
        @overload
        def value(self, v: Float3) -> None: ...

        @value.setter
        def value(self, v) -> None:
            self.__value = Float3(v)

        @property
        def floats(self) -> list[float]:
            return [*self.value]

    class MatrixItem(sc.AbstractManipulatorItem):
        def __init__(self, initial: sc.Matrix44 = sc.Matrix44()):
            super().__init__()
            self.value: sc.Matrix44 = initial

        @property
        def floats(self) -> list[float]:
            return [*self.value]

        @property
        def matrix(self) -> sc.Matrix44:
            return self.value

    def __init__(self) -> None:
        super().__init__()
        self.__translation = TransformableManipulatorModel.Vec3Item()
        self.__rotation = TransformableManipulatorModel.Vec3Item()
        self.__scale = TransformableManipulatorModel.Vec3Item((1.0, 1.0, 1.0))
        self.__matrix = TransformableManipulatorModel.MatrixItem()

        self._update_matrix()

    def _update_matrix(self) -> None:
        t_mx = sc.Matrix44.get_translation_matrix(*self.__translation.value)
        r_mx = sc.Matrix44.get_rotation_matrix(*self.__rotation.value, degrees=False)
        s_mx = sc.Matrix44.get_scale_matrix(*self.__scale.value)

        self.__matrix.value = t_mx * r_mx * s_mx

        self._item_changed(self.__matrix)

    @property
    def translation(self) -> Vec3Item:
        return self.__translation

    @property
    def rotation(self) -> Vec3Item:
        return self.__rotation

    @property
    def scale(self) -> Vec3Item:
        return self.__scale

    @property
    def matrix_item(self) -> MatrixItem:
        return self.__matrix

    def set_matrix(self, matrix: sc.Matrix44):
        self.__matrix.value = matrix
        self._item_changed(self.__matrix)

    def get_item(self, identifier: str) -> Vec3Item | MatrixItem | None:
        match identifier:
            case "translation":
                return self.__translation
            case "rotation":
                return self.__rotation
            case "scale":
                return self.__scale
            case "matrix":
                return self.__matrix
            case _:
                return None

    def get_as_floats(self, item: Vec3Item | MatrixItem) -> list[float]:
        if item == self.__translation or item == self.__rotation or item == self.__scale or item == self.__matrix:
            return item.floats

        return []

    def set_floats(self, item: Vec3Item | MatrixItem, values: list[float]):
        if item == self.__translation or item == self.__rotation or item == self.__scale:
            assert isinstance(item, TransformableManipulatorModel.Vec3Item)
            item.value = values[:3]
            self._item_changed(item)
            self._update_matrix()
        elif item == self.__matrix:
            assert isinstance(item, TransformableManipulatorModel.MatrixItem)
            item.value = sc.Matrix44(*values[:16])

            # TODO: this needs to be tested!!!
            # Borrowed from https://docs.omniverse.nvidia.com/prod_services/prod_kit/programmer_ref/usd/transforms/get-world-transforms.html
            gf_matrix = Gf.Matrix4d(*values[:16])
            translation: Gf.Vec3d = gf_matrix.ExtractTranslation()
            self.__translation.value = Float3(translation[0], translation[1], translation[2])

            scale: Gf.Vec3d = Gf.Vec3d(*(v.GetLength() for v in gf_matrix.ExtractRotationMatrix()))
            self.__scale.value = Float3(scale[0], scale[1], scale[2])

            rotation: Gf.Rotation = gf_matrix.ExtractRotation()
            rotation = rotation.Decompose([1, 0, 0], [0, 1, 0], [0, 0, 1])
            self.__rotation.value = Float3(
                math.radians(rotation[0]),
                math.radians(rotation[1]),
                math.radians(rotation[2]),
            )

            self._item_changed(item)


class TransformableManipulator(ComposableManipulator):
    def __init__(self):
        super().__init__(gesture_manager=PreventGestureOverlap())
        model = TransformableManipulatorModel()

        self.__transform: sc.Transform | None = None
        self.__matrix_item: TransformableManipulatorModel.MatrixItem = model.matrix_item

        self.model = model

    # @override
    def clear(self):
        super().clear()
        self.model = None

    def _get_model_floats(
        self,
        item: TransformableManipulatorModel.Vec3Item | TransformableManipulatorModel.MatrixItem,
    ) -> list[float]:
        assert self.model is not None
        return self.model.get_as_floats(item)

    def _set_model_floats(
        self,
        item: TransformableManipulatorModel.Vec3Item | TransformableManipulatorModel.MatrixItem,
        floats: list[float],
    ) -> None:
        assert self.model is not None
        self.model.set_floats(item, floats)

    @property
    def matrix(self) -> Gf.Matrix4d:
        return Gf.Matrix4d.Set(*self._get_model_floats(self.__matrix_item))

    @matrix.setter
    def matrix(self, matrix: list[float] | Gf.Matrix4d):
        floats: list[float]
        match matrix:
            case Gf.Matrix4d():
                floats = [
                    matrix[0][0],
                    matrix[0][1],
                    matrix[0][2],
                    matrix[0][3],
                    matrix[1][0],
                    matrix[1][1],
                    matrix[1][2],
                    matrix[1][3],
                    matrix[2][0],
                    matrix[2][1],
                    matrix[2][2],
                    matrix[2][3],
                    matrix[3][0],
                    matrix[3][1],
                    matrix[3][2],
                    matrix[3][3],
                ]
            case _:
                floats = matrix
        self._set_model_floats(self.__matrix_item, floats)

    @property
    def scale(self) -> Float3:
        """

        Returns:
            the manipulator model's scale part as a carb.Float3
        """
        floats = self._get_model_floats(self.transform_model.scale)
        assert len(floats) == 3, f"Length of scale floats should be 3, not {len(floats)}"
        return Float3(*floats)

    @scale.setter
    def scale(self, scale: Float3):
        """

        Args:
            scale:
        """
        self._set_model_floats(self.transform_model.scale, [scale.x, scale.y, scale.z])

    @property
    def rotation_radians(self) -> Float3:
        """

        Returns:
            the manipulator model's scale part as a carb.Float3, in radians
        """
        floats = self._get_model_floats(self.transform_model.rotation)
        assert len(floats) == 3, f"Length of rotation floats should be 3, not {len(floats)}"
        return Float3(*floats)

    @rotation_radians.setter
    def rotation_radians(self, rotation: Float3) -> None:
        """

        Args:
            rotation:
        """
        self._set_model_floats(self.transform_model.rotation, [rotation.x, rotation.y, rotation.z])

    @property
    def rotation_degrees(self) -> Float3:
        """

        Returns:
            the manipulator model's rotation part as a carb.Float3, in degrees
        """
        rot_rad = self.rotation_radians
        return Float3(math.degrees(rot_rad.x), math.degrees(rot_rad.y), math.degrees(rot_rad.z))

    @rotation_degrees.setter
    def rotation_degrees(self, rotation: Float3) -> None:
        """

        Args:
            rotation:
        """
        rot_rad = Float3(math.radians(rotation.x), math.radians(rotation.y), math.radians(rotation.z))
        self.rotation_radians = rot_rad

    @property
    def translation(self) -> Float3:
        """

        Returns:
            the manipulator model's translation part as a carb.Float3
        """
        floats = self._get_model_floats(self.transform_model.translation)
        assert len(floats) == 3, f"Length of translation floats should be 3, not {len(floats)}"
        return Float3(*floats)

    @translation.setter
    def translation(self, translation: Float3):
        """

        Args:
            translation:
        """
        self._set_model_floats(
            self.transform_model.translation,
            [translation.x, translation.y, translation.z],
        )

    @property
    def transform_model(self) -> TransformableManipulatorModel:
        model = self.model
        assert isinstance(model, TransformableManipulatorModel), (
            f"TransformableManipulator's model isn't a " f"TransformableManipulatorModel; it's {model}"
        )
        return model

    def build_func(self) -> None:
        self.__transform = sc.Transform(transform=self.__matrix_item.matrix)
        with self.__transform:
            super().build_func()

    def model_updated_func(self, item) -> None:
        if not self.model:
            return

        if item == self.__matrix_item:
            if self.__transform is not None:
                self.__transform.transform = self.__matrix_item.matrix
