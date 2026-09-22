# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides a registry for managing PrimTransformManipulatorScene instances, handling their lifecycle within a scene."""


__all__ = ["TransformManipulatorRegistry"]

import weakref

from omni.kit.viewport.registry import RegisterScene

from .prim_transform_manipulator import PrimTransformManipulator
from .reference_prim_marker import ReferencePrimMarker


class PrimTransformManipulatorScene:
    def __init__(self, desc: dict):
        usd_context_name = desc.get("usd_context_name")
        self.__transform_manip = PrimTransformManipulator(
            usd_context_name=usd_context_name, viewport_api=desc.get("viewport_api")
        )
        self.__reference_prim_marker = ReferencePrimMarker(
            usd_context_name=usd_context_name, manipulator_model=weakref.proxy(self.__transform_manip.model)
        )

    def destroy(self):
        if self.__transform_manip:
            self.__transform_manip.destroy()
            self.__transform_manip = None

        if self.__reference_prim_marker:
            self.__reference_prim_marker.destroy()
            self.__reference_prim_marker = None

    # PrimTransformManipulator & TransformManipulator don't have their own visibility
    @property
    def visible(self):
        return True

    @visible.setter
    def visible(self, value):
        pass

    @property
    def categories(self):
        return ("manipulator",)

    @property
    def name(self):
        return "Prim Transform"


class TransformManipulatorRegistry:
    """A registry for managing instances of :obj:`PrimTransformManipulatorScene` within a scene.

    This class is responsible for the lifecycle management of the :obj:`PrimTransformManipulatorScene` instances. It registers the :obj:`PrimTransformManipulatorScene` with the scene, ensuring that manipulators for transforming primitives are properly managed and destroyed when no longer needed.
    """

    def __init__(self):
        """Initializes the TransformManipulatorRegistry instance."""
        self._scene = RegisterScene(PrimTransformManipulatorScene, "omni.kit.manipulator.prim.core")

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Cleans up resources used by the TransformManipulatorRegistry instance."""
        self._scene = None
