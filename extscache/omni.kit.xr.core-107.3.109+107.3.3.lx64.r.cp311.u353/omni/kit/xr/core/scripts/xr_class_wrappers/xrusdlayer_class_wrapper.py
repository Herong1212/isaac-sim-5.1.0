# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

__all__ = ["XRUsdLayer"]

import re
from typing import Any, Iterable, Optional, Union

import carb
import omni.usd
from pxr import Gf, Sdf, Usd

from ..._xrcore import (
    XRAssetManager_Internal,
    XRCoordinateSystem,
    XROrientationAlignment,
    XRToken,
    XRTransformType,
    XRUsdLayer_Internal,
)
from .xrtargetinfo_class_wrapper import XRTargetInfo

# =================================================
# This file constructs a shim for the C++
# functionality exposed into python and adds
# types, type conversions, documentation, and
# improved python integration for these functions.
# =================================================

# ================================================
# XRUsdLayer class extensions
# ================================================


# pylint: disable=locally-disabled, multiple-statements
# noinspection PyProtectedMember


class XRUsdLayerInternalData:
    def __init__(self):
        self.meta_data = {}


class XRUsdLayer:
    _internal_data: dict[str, Any] = {}

    def __init__(self, internal: XRUsdLayer_Internal = None):
        if internal is None:
            self.__internal: XRUsdLayer_Internal = XRUsdLayer_Internal()
        else:
            self.__internal = internal

        if internal.get_id() in XRUsdLayer._internal_data:
            self.__internal_data = XRUsdLayer._internal_data[internal.get_id()]
        else:
            self.__internal_data = XRUsdLayerInternalData()
            XRUsdLayer._internal_data[internal.get_id()] = self.__internal_data

    def __eq__(self, other):
        if isinstance(other, XRUsdLayer):
            return self.__internal == other.__internal
        return False

    def __hash__(self):
        return self.__internal.__hash__()

    def get_id(self) -> int:
        """
        Get an unique id for this layer.

        Return:
            unique id
        """
        return self.__internal.get_id()

    def invalidate(self) -> None:
        """
        Invalidates the xr usd layer. The reference to this object remains, but all data
        on the usd layers will be deleted. When no reference in python exists the rest of
        the underlying usd layer infrastructure will be deleted.
        """

        self.__internal.invalidate()

    def is_valid(self) -> bool:
        """
        Check whether xr usd layer is valid. If layer was invalidated it should no longer be used.

        Return:
            whether layer is valid
        """

        return self.__internal.is_valid()

    def get_top_level_prim_path(self) -> str:
        """
        Returns the path to the top level prim for the xr usd layer.

        Return:
            usd prim path of top level prim
        """

        return self.__internal.get_top_level_prim_path()

    def get_top_level_prim(self) -> Usd.Prim:
        """
        Returns the top level prim for the xr usd layer.

        Return:
            top level prim
        """

        return omni.usd.get_context().get_stage().GetPrimAtPath(self.__internal.get_top_level_prim_path())

    def get_layer_name(self) -> str:
        # TODO: One of these two functions should be deprecated/removed, right?
        return self.get_ui_layer_name()

    def get_ui_layer_name(self) -> str:
        """
        Gets the usd layer name used for the xr usd layer's main ui skeleton.

        Return:
            name of ui layer (usd layer)
        """

        return self.__internal.get_ui_layer_name()

    def get_component_layer_name(self) -> str:
        """
        Gets the usd layer name used for the xr usd layer's imported usd components.

        Return:
            name of component layer (usd layer)
        """

        return self.__internal.get_component_layer_name()

    def get_layer(self) -> Sdf.Layer:
        # TODO: One of these two functions should be deprecated/removed, right?
        return self.get_ui_layer()

    def get_ui_layer(self) -> Sdf.Layer:
        """
        Get the layer that is used for the xr usd layer's ui skeleton.

        Return:
            usd layer
        """

        try:
            layer_name = self.get_ui_layer_name()
            return Sdf.Find(layer_name)
        except Exception:
            carb.log_error("Failed to get layer from stage")

        raise RuntimeError("Failed to find session layer in usd stage")

    def get_component_layer(self) -> Sdf.Layer:
        """
        Get the layer that is used for the xr usd layer's imported usd components.

        Return:
            usd layer
        """

        try:
            layer_name = self.get_ui_layer_name()
            return Sdf.Find(layer_name)
        except Exception:
            carb.log_error("Failed to get layer from stage")

        raise RuntimeError("Failed to find session layer in usd stage")

    def get_edit_context(self) -> Usd.EditContext:
        """
        Get an edit target context to make changes in the xr usd layer.
        This will direct changes to the ui layer and not the component layer.

        Return:
            edit Context for xr usd layer
        """

        return Usd.EditContext(omni.usd.get_context().get_stage(), Usd.EditTarget(self.get_layer()))

    def get_coordinate_system(self, path: Union[Usd.Prim, Sdf.Path, str, XRToken] = "") -> XRCoordinateSystem:
        """
        Returns coordinate system of the xr usd layer.

        Args:
            path:    (optional) prim path or prim

        Return:
            coordinate system of the usd layer
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return self.__internal.get_coordinate_system(str(path))

    def show(self, path: Union[Usd.Prim, Sdf.Path, str, XRToken] = "") -> None:
        """
        Make a prim at a path visible. If no path is given the
        top level prim of the xr usd layer will be made visible.

        Args:
            path:    (optional) prim path or prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        self.__internal.show(str(path))

    def hide(self, path: Union[Usd.Prim, Sdf.Path, str, XRToken] = "") -> None:
        """
        Make a prim at a path invisible. If no path is given the
        top level prim of the xr usd layer will be made invisible.

        Args:
            path:    (optional) prim path or prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        self.__internal.hide(str(path))

    def is_visible(self, path: Union[Usd.Prim, Sdf.Path, str, XRToken] = "") -> bool:
        """
        Returns whether a object is visible in the xr usd layer.
        If the path is empty, the visibility of the top level
        prim is returned.

        Args:
            path:    path of usd prim

        Return:
            True if layer/prim is visible
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return self.__internal.is_visible(str(path))

    def add_asset(
        self,
        path: Union[Sdf.Path, str, XRToken],
        group: str,
        file_path: str,
        layer_identifier: str = "",
        transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None,
        transform_type: XRTransformType = XRTransformType.local,
        pickable: bool = False,
        visible: bool = True,
    ) -> str:
        """
        Creates a persistent object to the xr usd layer that loads a usd asset.

        Args:
            path:             usd path at which to insert a model
            group:            name of xr usd object group
            file_path:        path to the usd file to include in the xr usd layer
            layer_identifier: optional identifier to an already loaded Sdf.Layer
            transform:        optional transformation matrix
            transform_type:   optional type of transform (default is LocalTransform)
            pickable:         optional whether to object is pickable (default is False)
            visible:          optional whether object is visible (default is True)

        Return:
            usd path of asset
        """

        if transform is None:
            transform = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

        self.__internal.add_asset(
            str(path),
            group,
            str(file_path),
            str(layer_identifier),
            transform,
            int(transform_type),
            pickable,
            visible,
        )

        return path

    def add_beam(
        self,
        path: Union[Sdf.Path, str, XRToken],
        group: str,
        material_reference: Union[Sdf.Path, str, XRToken],
        transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None,
        transform_type: XRTransformType | int = XRTransformType.local,
        max_length: float = 20.0,
        length: float = -1.0,
        tube_radius: float = 0.005,
        visible: bool = True,
    ) -> str:
        """
        Adds a persistent object to the xr usd layer that creates a selection beam.

        Args:
            path:               usd path at which to insert a beam
            group:              name of xr usd object group
            material_reference: path to the usd file to include in the xr usd layer
            transform:          optional transformation matrix (default is identity)
            transform_type:     optional type of transform (default is LocalTransform)
            max_length:         optional maximum length of the beam (default is 10m)
            length:             optional length of the beam (set to -1.0 to have it extent to the next object)
            tube_radius:        optional radius of the beam (default is 0.5cm)
            visible:            optional whether object is visible (default is True)

        Return:
            usd path of beam
        """

        if transform is None:
            transform = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

        self.__internal.add_beam(
            str(path),
            group,
            str(material_reference),
            transform,
            transform_type,
            max_length,
            tube_radius,
            length,
            visible,
        )

        return path

    def add_teleport_arc(
        self,
        path: Union[Sdf.Path, str, XRToken],
        group: str,
        material_reference: Union[Sdf.Path, str, XRToken],
        transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None,
        transform_type: XRTransformType | int = XRTransformType.local,
        max_height: float = 3.0,
        tube_radius: float = 0.02,
        num_segments: int = 120,
        visible: bool = True,
    ) -> str:
        """
        Adds a persistent object to the xr usd layer that creates a selection beam.

        Args:
            path:               usd path at which to insert a beam
            group:              name of xr usd object group
            material_reference: path to the usd file to include in the xr usd layer
            transform:          optional transformation matrix (default is identity)
            transform_type:     optional type of transform (default is LocalTransform)
            max_height:         optional max height of the arc when aimed straight up (default is 3m). This is used
                                to determine the "launch speed" of a particle tracing the arc's path. Note that
                                aiming at a 45deg angle on flat ground will give less height but a horizontal
                                distance of around double this value.
            tube_radius:        optional radius of the beam (default is 2cm)
            num_segments:       optional number of segments (default is 120)
            visible:            optional whether object is visible (default is True)

        Return:
            usd path of beam
        """

        if transform is None:
            transform = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

        self.__internal.add_teleport_arc(
            str(path),
            group,
            str(material_reference),
            transform,
            transform_type,
            max_height,
            tube_radius,
            num_segments,
            visible,
        )

        return path

    def add_transform(
        self,
        path: Union[Sdf.Path, str, XRToken],
        group: str,
        transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None,
        transform_type: XRTransformType = XRTransformType.local,
        visible: bool = True,
    ) -> str:
        """
        Adds a persistent usd object to the xr usd layer representing a transform.

        Args:
            path:            usd path at which to insert a transform
            group:           name of xr usd layer group
            transform:       optional transformation matrix (default is identity)
            transform_type:  optional type of transform (default is LocalTransform)
            visible:         optional whether object is visible (default is True)

        Return:
            usd path to transform
        """

        if transform is None:
            transform = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

        self.__internal.add_transform(str(path), group, transform, transform_type, visible)

        return path

    def add_reorient(
        self,
        path: Union[Sdf.Path, str, XRToken],
        group: str,
        alignment: XROrientationAlignment = XROrientationAlignment.world,
        input_device: Union[str, None, XRToken] = None,
        pose_name: Union[str, None, XRToken] = None,
        visible: bool = True,
    ) -> str:
        """
        Adds a persistent object to the xr usd layer that inserts an orientation pointing in a specific direction.

        Args:
            path:        usd path at which to insert a reorientation transform
            group:       name of xr usd layer group
            alignment:   optional alignment option to tell how orientation should be realigned (default world aligned)
            input_device:  optional for device alignment the device that orientation needs to be aligned to (default hmd)
            pose_name:     optional name of the pose to align with
            visible:     optional whether object is visible (default is True)

        Return:
            usd path to reorient
        """

        if input_device is None:
            input_device = "displayDevice"

        if pose_name is None:
            pose_name = ""

        self.__internal.add_reorient(str(path), group, alignment, input_device, pose_name, visible)

        return path

    def add_link(
        self,
        path: Union[Sdf.Path, str, XRToken],
        group: str,
        link_path: Union[Sdf.Path, str, Usd.Prim, XRToken],
        transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None,
        transform_type: XRTransformType | int = XRTransformType.local,
        visible: bool = True,
    ) -> str:
        """
        Adds a persistent object to the xr usd layer that links an object in another layer.
        This can be used to create a transformation override in the xr usd layer for an object.

        Args:
            path:            usd path at which to insert a link to another object
            group:           name of xr usd layer group
            link_path:       path to the other object that needs an override transform in this layer
            transform:       optional a transform at which location the link should be put or if not specified
                                initial location will match location of referenced object
            transform_type:  optional type of transform (default is LocalTransform)
            visible:         optional whether object is visible (default is True)

        Return:
            usd path to link
        """

        if transform is None:
            transform = ()

        if isinstance(link_path, Usd.Prim):
            link_path = link_path.GetPrimPath()

        self.__internal.add_link(str(path), group, str(link_path), transform, transform_type, visible)

        return path

    def add_link_to_input_device(
        self,
        path: Union[Sdf.Path, str, XRToken],
        group: str,
        input_device_name: Union[str, XRToken],
        pose_name: Union[str, XRToken],
        transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None,
        transform_type: XRTransformType | int = XRTransformType.local,
        visible: bool = True,
    ) -> str:
        """
        Adds a persistent object to the xr usd layer that links to an input device.
        This can be used to create a transformation override in the xr usd layer for an object.

        Args:
            path:            usd path at which to insert a link to another object
            group:           name of xr usd layer group
            input_device_name: name of the input device
            pose_name:       name of the pose to align with
            transform:       optional a transform at which location the link should be put or if not specified
                                initial location will match location of referenced object
            transform_type:  optional type of transform (default is LocalTransform)
            visible:         optional whether object is visible (default is True)

        Return:
            usd path to link
        """

        if transform is None:
            transform = ()

        self.__internal.add_link_to_input_device(
            str(path),
            group,
            input_device_name,
            pose_name,
            transform,
            transform_type,
            visible,
        )

        return path

    def add_reference(
        self,
        path: Union[Sdf.Path, str, XRToken],
        group: str,
        reference_path: Union[Sdf.Path, Usd.Prim, str, XRToken],
        transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None,
        transform_type: XRTransformType | int = XRTransformType.local,
        pickable: bool = False,
        visible: bool = True,
    ) -> str:
        """
        Creates a persistent object to the xr usd layer that references a different part of the xr usd layer.

        Args:
            path:            usd path at which to insert a model
            group:           name of xr usd layer group
            reference_path:  usd path to object that needs to be referenced here
            transform:       optional transformation matrix (default is identity)
            transform_type:  optional type of transform (default is LocalTransform)
            pickable:        optional whether to object is pickable (default is False)
            visible:         optional whether object is visible (default is True)

        Return:
            usd path of reference
        """

        if transform is None:
            transform = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

        if isinstance(reference_path, Usd.Prim):
            reference_path = reference_path.GetPrimPath()

        self.__internal.add_reference(
            str(path),
            group,
            str(reference_path),
            transform,
            transform_type,
            pickable,
            visible,
        )

        return path

    def remove(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> None:
        """
        Removes a prim from the xr usd layer.

        Args:
            path:    prim path or prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        self.__internal.remove(str(path))

    def remove_group(self, group: str) -> None:
        """
        Removes a group of prims from the xr usd layer.

        Args:
            group:    name of the group
        """

        self.__internal.remove_group(group)

    def is_managed_prim(self, path: Union[Usd.Prim, Sdf.Path, str, XRToken]) -> bool:
        """
        Checks if usd xr layer manages a prim at given path.

        Args:
            path:  string with prim path or the prim itself

        Return:
            whether the prim is a managed object
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return self.__internal.is_managed_prim(str(path))

    def clear(self) -> None:
        """
        Removes all managed objects from a xr usd layer.
        """

        self.__internal.clear()

    def set_transform(
        self,
        path: Union[Sdf.Path, Usd.Prim, str, XRToken],
        transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]],
        transform_type: XRTransformType | int = XRTransformType.local,
        use_usd: bool = False,
    ) -> None:
        """
        Sets the transform of a prim on the xr usd layer.

        Args:
            path:            prim path or prim
            transform:       new transform matrix for the prim
            transform_type:  the type of transform to return
            use_usd:         use usd to set transform instead of usdrt
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        self.__internal.set_transform(str(path), transform, transform_type, use_usd)

    def set_position(
        self,
        path: Union[Sdf.Path, Usd.Prim, str, XRToken],
        position: Union[Gf.Vec3d, Iterable[float]],
        transform_type: XRTransformType | int = XRTransformType.local,
        use_usd: bool = False,
    ) -> None:
        """
        Sets the transform of a prim on the xr usd layer.

        Args:
            path:            prim path or prim
            position:        new position
            transform_type:  the type of transform to return
            use_usd:         use usd to set transform instead of usdrt

        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        transform = Gf.Matrix4d(self.__internal.get_transform(str(path), transform_type))
        transform.SetTranslateOnly(Gf.Vec3d(position))
        self.__internal.set_transform(str(path), transform, transform_type, use_usd)

    def get_transform(
        self,
        path: Union[Sdf.Path, Usd.Prim, str, XRToken],
        transform_type: XRTransformType | int = XRTransformType.local,
        use_usd: bool = False,
    ) -> Gf.Matrix4d:
        """
        Returns the transform of a prim on the xr usd layer

        Args:
            path:            prim path or prim
            transform_type:  the type of transform to return
            use_usd:         use usd to set transform instead of usdrt

        Return:
            Gf.Matrix4d with transform
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return Gf.Matrix4d(*self.__internal.get_transform(str(path), transform_type, use_usd))

    def get_position(
        self,
        path: Union[Sdf.Path, Usd.Prim, str, XRToken],
        transform_type: XRTransformType | int = XRTransformType.local,
    ) -> Gf.Vec3d:
        """
        Returns the transform of a prim on the xs usd layer.

        Args:
            path:            prim path or prim
            transform_type:  the type of transform to return

        Return:
            Gf.Vec3d with position
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return Gf.Matrix4d(self.__internal.get_transform(str(path), transform_type)).ExtractTranslation()

    def set_file_path(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], file_path: str) -> None:
        """
        Sets the file path of the asset to load.

        Args:
            path:        prim path or prim
            file_path:   path to usd file
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        self.__internal.set_file_path(str(path), file_path)

    def get_file_path(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> str:
        """
        Returns the file path of a managed asset on the xr usd layer.

        Args:
            path:    prim path or prim

        Return:
            file path to the usd asset file
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return self.__internal.get_file_path(str(path))

    def get_wrapped_prim_path(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> str:
        """
        Returns the USD path to the prim wrapped inside this managed prim.
        This can be the referenced prim or the loaded asset.

        Args:
            path    prim path or prim

        Return:
            path to the prim that is wrapped inside this managed prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return self.__internal.get_wrapped_prim_path(path)

    def set_pickable(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], pickable: bool) -> None:
        """
        Sets whether managed prim on xr usd layer is pickable.

        Args:
            path:      prim path or prim
            pickable:  whether the object is pickable
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        self.__internal.set_pickable(str(path), pickable)

    def get_pickable(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> bool:
        """
        Returns whether managed prim is pickable.

        Args:
            path:      prim path or prim

        Return:
            Whether prim at prim path is pickable
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return self.__internal.get_pickable(str(path))

    def get_target_info(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> XRTargetInfo:
        """
        Get the target info of what was hit by the beam.

        Args:
            path:      prim path

        Return:
            target info
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return XRTargetInfo(self.__internal.get_target_info(str(path)))

    def set_length(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], length: float) -> None:
        """
        Sets the length of a managed prim (for beam: -1.0 auto scale to next object and cast a ray to determine which
        object will be hit).

        Args:
            path:      prim path or prim
            length:    the length of the beam
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        self.__internal.set_length(str(path), length)

    def get_length(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> float:
        """
        Returns the length of a managed prim  (if it auto scales to object, get distance to the object that was hit).

        Args:
            path:      prim path or prim

        Return:
            length of the beam
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return self.__internal.get_length(str(path))

    def set_radius(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], radius: float) -> None:
        """
        Sets the radius of a managed prim.

        Args:
            path:      prim path or prim
            radius:    the new radius of managed prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        self.__internal.set_radius(str(path), radius)

    def get_radius(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> float:
        """
        Gets the radius of managed prim

        Args:
            path:      prim path or prim

        Return:
            radius of a managed prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return self.__internal.get_radius(str(path))

    def set_max_length(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], max_length: float) -> None:
        """
        Sets the maximum length of a managed prim.

        Args:
            path:      prim path or prim
            max_length:  the maximum length of a managed prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        self.__internal.set_max_length(str(path), max_length)

    def get_max_length(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> float:
        """
        Returns the maximum length of a managed prim.

        Args:
            path:      prim path or prim

        Return:
            maximum length of a managed prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return self.__internal.get_max_length(str(path))

    def get_end_prim_path(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> str:
        """
        Returns the prim path of the end of the managed prim

        Args:
            path:      prim path or prim

        Return:
            prim path to the end of the managed prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return self.__internal.get_end_prim_path(str(path))

    def get_end_prim(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> Usd.Prim:
        """
        Returns the prim path of the end of the managed prim

        Args:
            path:      prim path or prim

        Return:
            prim at the end of the managed prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return omni.usd.get_context().get_stage().GetPrimAtPath(self.__internal.get_end_prim_path(str(path)))

    def get_begin_prim_path(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> str:
        """
        Returns the prim path of the begin of the managed prim

        Args:
            path:      prim path or prim

        Return:
            prim path to the begin of the managed prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return self.__internal.get_begin_prim_path(str(path))

    def get_begin_prim(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> Usd.Prim:
        """
        Returns the prim path of the begin of the managed prim

        Args:
            path:      prim path or prim

        Return:
            prim at the begin of the managed prim
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        return omni.usd.get_context().get_stage().GetPrimAtPath(self.__internal.get_begin_prim_path(str(path)))

    def commit_link_transform(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], layer: str = "") -> None:
        """
        Commits the current transform of a link to a different layer.

        Args:
            path:      prim path or prim
            layer:     (optional) name of the layer
        """

        if isinstance(path, Usd.Prim):
            path = path.GetPrimPath()

        self.__internal.commit_link_transform(str(path))

    def ensure_device_prim_path(self, input_device: Union[str, XRToken]) -> str:
        """
        Ensures that managed device transform exists and returns the path where
        transformable is located.

        Args:
            input_device:        device for which to query the device path

        Return:
            prim path to transform with device coordinates
        """

        return self.__internal.ensure_device_prim_path(input_device)

    def convert_vector_from_stage_to_session(self, vec: Gf.Vec3d) -> Gf.Vec3d:
        """
        Converts a vector in stage coordinates to session coordinates.
        It will scale the vector and permute the vector to ensure up vectors are aligned.

        Args:
            vec:  vector in stage coordinates

        Return:
            converted vector
        """

        return Gf.Vec3d(self.__internal.convert_vector_from_stage_to_session(vec))

    def convert_vector_from_session_to_stage(self, vec: Gf.Vec3d) -> Gf.Vec3d:
        """
        Converts a vector in session coordinates to stage coordinates.
        It will scale the vector and permute the vector to ensure up vectors are aligned.

        Args:
            vec:  vector in session coordinates

        Return:
            converted vector
        """

        return Gf.Vec3d(self.__internal.convert_vector_from_session_to_stage(vec))

    def convert_normal_vector_from_stage_to_session(self, vec: Gf.Vec3d) -> Gf.Vec3d:
        """
        Converts a vector in stage coordinates to session coordinates.
        It will scale the vector and permute the vector to ensure up vectors are aligned.

        Args:
            vec:  vector in stage coordinates

        Return:
            converted vector
        """

        return Gf.Vec3d(self.__internal.convert_normal_vector_from_stage_to_session(vec))

    def convert_normal_vector_from_session_to_stage(self, vec: Gf.Vec3d) -> Gf.Vec3d:
        """
        Converts a vector in session coordinates to stage coordinates.
        It will scale the vector and permute the vector to ensure up vectors are aligned.

        Args:
            vec:  vector in session coordinates

        Return:
            converted vector
        """

        return Gf.Vec3d(self.__internal.convert_normal_vector_from_session_to_stage(vec))

    def load_asset(self, asset_name: Union[str, XRToken]) -> str:
        """
        Load an asset from the asset manager into the usd layer object.
        This function will return the path where the usd asset is loaded.
        The asset by default will be invisible and should be referenced
        to the right location in the tree.

        Args:
            asset_name:  name of the asset that needs to be loaded

        Return:
            usd path to the loaded asset
        """

        asset_name = str(asset_name)
        usd_asset_name = re.sub("[^a-zA-Z0-9]", "_", asset_name)
        asset_path = XRAssetManager_Internal().resolve_asset_path(asset_name)

        usd_path = self.get_top_level_prim_path() + "/assets/" + usd_asset_name

        if not self.is_managed_prim(usd_path):
            self.add_asset(usd_path, visible=False, group="_assets", file_path=asset_path)

        return self.get_wrapped_prim_path(usd_path)

    def set_meta_data(self, key: str, value: str) -> None:
        """
        Set value in the usd layer meta data dictionary.

        Args:
            key:    key under which to store value
            value:  value to store
        """

        self.__internal_data.meta_data[key] = value

    def get_meta_data(self, key: str) -> Optional[str]:
        """
        Get value from usd layer meta data dictionary.

        Args:
            key:    key under which data is stored

        Return:
            value of meta data or None if no value was set
        """

        if key in self.__internal_data.meta_data:
            return self.__internal_data.meta_data[key]
        else:
            return None

    def clear_meta_data(self, key_prefix: str) -> None:
        """
        Clear keys with a given prefix.

        Args:
            key_prefix:
        """

        keys = list(self.__internal_data.meta_data.keys())
        for key in keys:
            if key.startswith(key_prefix):
                self.__internal_data.meta_data.pop(key)

    def get_prim_at_path(self, prim_path: Union[XRToken, str, Sdf.Path]):
        return omni.usd.get_context().get_stage().GetPrimAtPath(str(prim_path))

    def is_grabbable(self, prim: Union[Sdf.Path, Usd.Prim, str]) -> bool:
        """
        Check if prim is grabbable.

        Args:
            prim:   the prim to test

        Return:
            True if object is grabbable
        """

        stage = omni.usd.get_context().get_stage()

        if not isinstance(prim, Usd.Prim):
            prim = stage.GetPrimAtPath(Sdf.Path(str(prim)))

        while prim.IsValid():
            if prim.HasAttribute("xr:disable_grab"):
                attr = prim.GetAttribute("xr:disable_grab")
                if attr.Get() is True:
                    return False
                else:
                    return True
            if prim.IsPseudoRoot():
                break
            prim = prim.GetParent()

        return True

    def set_grabbable(self, prim: Union[Sdf.Path, Usd.Prim, str], grabbable: bool = True) -> None:
        """
        Set a prim to be grabbable or not grabbable.

        Args:
            prim:       the prim to set as grabbable
            grabbable:  whether it should be grabbable or not
        """

        stage = omni.usd.get_context().get_stage()

        if not isinstance(prim, Usd.Prim):
            prim = stage.GetPrimAtPath(Sdf.Path(str(prim)))

        if not prim.IsValid():
            prim = stage.DefinePrim(Sdf.Path(str(prim)))

        if prim.IsValid():

            if prim.HasAttribute("xr:disable_grab"):
                attr = prim.GetAttribute("xr:disable_grab")
                attr.Set(not grabbable)
            else:
                attr = prim.CreateAttribute("xr:disable_grab", Sdf.ValueTypeNames.Bool, True).Set(not grabbable)
