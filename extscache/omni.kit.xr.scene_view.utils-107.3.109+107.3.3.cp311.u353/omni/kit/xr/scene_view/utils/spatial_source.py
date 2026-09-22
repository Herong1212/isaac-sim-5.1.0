# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = [
    "SpatialSource",
    "SpatialSourceBase",
    "TransformMatrixSpace",
    "TranslationSpace",
    "RotationSpace",
    "ScaleSpace",
    "LookAtCameraSpace",
    "PrimPathSpace",
    "ScreenScaleSpace",
]

from abc import ABC, abstractmethod
from typing import Any, Dict, TypeAlias, final

import omni.kit.xr.scene_view.core
import omni.ui.scene
from pxr import Gf, Sdf

MatrixType: TypeAlias = Gf.Matrix4f | Gf.Matrix4d
Vec3Type: TypeAlias = Gf.Vec3f | Gf.Vec3d
PrimPathType: TypeAlias = str | Sdf.Path


class SpatialSourceBase(ABC):
    @final
    def create_transform(self) -> omni.ui.scene.Transform:
        return omni.ui.scene.Transform(**self.make_transform_args())

    @abstractmethod
    def make_transform_args(self) -> Dict[str, Any]:  # pragma: no cover
        ...


class TransformMatrixSpace(SpatialSourceBase):
    """ """

    def __init__(self, matrix: MatrixType):
        self.__matrix = matrix

    def make_transform_args(self) -> Dict[str, Any]:
        # TODO: can I deconstruct a GfMatrix4f like this...? >_<;;
        matrix = omni.ui.scene.Matrix44(
            self.__matrix[0][0],
            self.__matrix[0][1],
            self.__matrix[0][2],
            self.__matrix[0][3],
            self.__matrix[1][0],
            self.__matrix[1][1],
            self.__matrix[1][2],
            self.__matrix[1][3],
            self.__matrix[2][0],
            self.__matrix[2][1],
            self.__matrix[2][2],
            self.__matrix[2][3],
            self.__matrix[3][0],
            self.__matrix[3][1],
            self.__matrix[3][2],
            self.__matrix[3][3],
        )
        return {"transform": matrix}


class TranslationSpace(SpatialSourceBase):
    """ """

    def __init__(self, position: Vec3Type):
        self.__position = position

    def make_transform_args(self) -> Dict[str, Any]:
        x = self.__position[0]
        y = self.__position[1]
        z = self.__position[2]
        return {"transform": omni.ui.scene.Matrix44.get_translation_matrix(x, y, z)}


class RotationSpace(SpatialSourceBase):
    """ """

    def __init__(self, euler: Vec3Type):
        self.__euler = euler

    def make_transform_args(self) -> Dict[str, Any]:
        x = self.__euler[0]
        y = self.__euler[1]
        z = self.__euler[2]
        return {"transform": omni.ui.scene.Matrix44.get_rotation_matrix(x, y, z)}


class ScaleSpace(SpatialSourceBase):
    """ """

    def __init__(self, scale: Vec3Type):
        self.__scale = scale

    def make_transform_args(self) -> Dict[str, Any]:
        x = self.__scale[0]
        y = self.__scale[1]
        z = self.__scale[2]
        return {"transform": omni.ui.scene.Matrix44.get_scale_matrix(x, y, z)}


class LookAtCameraSpace(SpatialSourceBase):
    """
    This causes the viewport camera transform to track the headset's transform, which is required for camera facing UI.
    """

    def make_transform_args(self) -> Dict[str, Any]:
        return {"look_at": omni.ui.scene.Transform.LookAt.CAMERA}


class PrimPathSpace(SpatialSourceBase):
    """ """

    def __init__(self, prim_path: PrimPathType):
        self.__prim_path = prim_path

    def make_transform_args(self) -> Dict[str, Any]:
        return {"basis": omni.kit.xr.scene_view.core.XRPrimPathTransformBasis(self.__prim_path)}


class SpatialSource:
    """
    Describes a kind of space for a UI Container to live in. It's mostly correct to think of this
    as a transform space, though depending on the source, it may do things that typical "transform"
    setups wouldn't do without more direct intervention.
    """

    def __init__(self, source: SpatialSourceBase):
        """Create a custom spatial source.

        You must specify the source object yourself. This would be useful in cases where you intend
        to implement your own SpatialSourceBase, for example.

        Args:
            source:
                the source base that will be applied by this SpatialSource object
        """
        self.__source = source

        # Transform creation is deferred until __enter__, because Transforms created outside
        # of an omni.ui.scene.AbstractContainer context are meaningless and will never appear
        self.__transform: omni.ui.scene.Transform | None = None

    def __enter__(self):
        # Pretending to be the transform allows us to pre-construct spatial sources outside of
        # an omni.ui.scene.AbstractContainer context but then have them work within such contexts
        if self.__transform is None:
            self.__transform = self.__source.create_transform()
        self.__transform.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.__transform must have been created to have gotten here
        self.__transform.__exit__(exc_tb, exc_val, exc_tb)

    def __del__(self):
        # This doesn't seem like it should be necessary, but Transforms can leak their children otherwise
        if self.__transform is not None:
            self.__transform.clear()

    @property
    def source(self) -> SpatialSourceBase:
        return self.__source

    @source.setter
    def source(self, source: SpatialSourceBase):
        self.__source = source
        if self.__transform is not None:
            for k, v in self.__source.make_transform_args().items():
                if hasattr(self.__transform, k):
                    setattr(self.__transform, k, v)

    def clear(self):
        """Remove and release any children of this space.

        The space will still exist as a child of any existing hierarchy, meaning you can call this
        function, and then immediately reenter this space's context in order to create new children.
        """
        if self.__transform is not None:
            self.__transform.clear()

    def reset(self):
        """
        Remove and release any children of this space and recreate it as a child of a new parent
        the next time its context is entered.

        This would only be called if you intend to reuse this space under a different parent from
        which it was created.
        """
        self.clear()
        self.__transform = None

    @staticmethod
    def new_transform_matrix_source(matrix: MatrixType) -> "SpatialSource":
        """Create a new source, using a standard 3D transformation matrix to describe the space.

        Args:
            matrix:
                Any USD 4x4 matrix.

        Returns:
            A SpatialSource object described by the input matrix.
        """
        return SpatialSource(TransformMatrixSpace(matrix))

    @staticmethod
    def new_translation_source(position: Vec3Type) -> "SpatialSource":
        """Create a new source which is offset (relatively) by the position provided.

        Args:
            position:
                A position in 3D space.

        Returns:
            A SpatialSource object describing a translation to the relative position provided.
        """
        return SpatialSource(TranslationSpace(position))

    @staticmethod
    def new_rotation_source(euler: Vec3Type) -> "SpatialSource":
        """Create a new source which is rotated based on the angles provided.

        Args:
            euler:
                A rotation in 3D space described by rotation around X, Y, and Z axes.

        Returns:
            A SpatialSource object describing a rotaion around Euler axes using the values provided.
        """
        return SpatialSource(RotationSpace(euler))

    @staticmethod
    def new_scale_source(scale: Vec3Type) -> "SpatialSource":
        """Create a new source which is scaled by the vector provided.

        Args:
            scale:
                A 3D scale vector.

        Returns:
            A SpatialSource object describing a scale by the axis amounts provided.
        """
        return SpatialSource(ScaleSpace(scale))

    @staticmethod
    def new_look_at_camera_source() -> "SpatialSource":
        """Create a new source which will rotate to always face the view camera.

        This source will not alter the X/Y/Z offset in any way, but will inherit from preceding
        sources.

        Returns:
            A SpatialSource object for facing the view camera, with no offset from its source.
        """
        return SpatialSource(LookAtCameraSpace())

    @staticmethod
    def new_prim_path_source(prim_path: PrimPathType) -> "SpatialSource":
        """Create a new source described by a PrimPath or string.

        The space will match the transform of any USD Prim object at the specified path. This will
        override any and all space sources or transforms before this one in a list or hierarchy.

        Args:
            prim_path:
                A path to the prim you want to follow.

        Returns:
            A SpatialSource object for following the transform at the specified PrimPath.
        """
        return SpatialSource(PrimPathSpace(prim_path))
