# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module defines the ManipulatorPrim2Core class that initializes and manages core components for manipulator primitives in a 3D application, setting up registries and tools for viewport manipulators."""

import omni.ext

from .global_registry import (
    clean_prim_data_accessor_registry,
    get_prim_data_accessor_registry,
    set_prim_data_accessor_registry,
)
from .prim_data_accessor_registry import PrimDataAccessorRegistry
from .prim_transform_manipulator import PrimTransformManipulator
from .prim_transform_manipulator_registry import TransformManipulatorRegistry
from .reference_prim_marker import ReferencePrimMarker
from .tools import PrimManipTools


class ManipulatorPrim2Core(omni.ext.IExt):
    """A class responsible for initializing and managing core components for manipulator primitives in a 3D application.

    This extension class sets up the necessary registries and tools used for handling manipulator primitives. It creates a legacy manipulator for viewport 1 (VP1) and a manipulator registry for viewport 2 (VP2). It also handles the creation of a marker to reference primitives within the scene. Upon shutdown, it ensures that all created components are properly destroyed and the global registry is cleaned up.
    """

    def on_startup(self, ext_id):
        """Initializes the core manipulator systems and tools.

        Args:
            ext_id (str): External ID provided during startup."""
        set_prim_data_accessor_registry(PrimDataAccessorRegistry())
        self.prim_data_accessor_registry = get_prim_data_accessor_registry()
        self._tools = PrimManipTools()

        # For VP1
        self._legacy_manipulator = PrimTransformManipulator()
        self._legacy_marker = None
        try:
            from omni.kit.manipulator.viewport import ManipulatorFactory

            self._legacy_marker = ManipulatorFactory.create_manipulator(
                ReferencePrimMarker, usd_context_name="", manipulator_model=self._legacy_manipulator.model, legacy=True
            )
        except ModuleNotFoundError:
            pass

        # For VP2
        self._manipulator_registry = TransformManipulatorRegistry()

    # def get_prim_data_accessor_registry():
    #     return self.primDataAccessorRegistry

    def on_shutdown(self):
        """Cleans up all manipulator systems and tools upon shutdown."""
        if self._legacy_manipulator is not None:
            self._legacy_manipulator.destroy()
            self._legacy_manipulator = None

        if self._legacy_marker is not None:
            ManipulatorFactory.destroy_manipulator(self._legacy_marker)
            self._legacy_marker = None

        if self._manipulator_registry is not None:
            self._manipulator_registry.destroy()
            self._manipulator_registry = None

        if self._tools is not None:
            self._tools.destroy()
            self._tools = None

        global __prim_data_accessor_registry
        self.prim_data_accessor_registry.destroy()
        self.prim_data_accessor_registry = None
        clean_prim_data_accessor_registry()
