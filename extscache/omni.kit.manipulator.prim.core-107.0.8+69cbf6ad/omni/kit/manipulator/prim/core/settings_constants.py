# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module defines constants and enums for manipulator placement settings and data registry event types in the omni.kit.manipulator.prim.core extension."""

__all__ = ["Constants", "DataRegistryEventTypes", "DataAccessorConstants"]

from enum import IntEnum, auto


class Constants:
    """A class containing constants related to manipulator settings.

    This class stores various constants used to configure the placement settings of manipulators in the application. These settings allow users to specify how manipulators are positioned relative to the selected objects. The constants include options for placing manipulators based on authored pivot points, selection centers, bounding box bases, bounding box centers, and reference primitives.
    """

    MANIPULATOR_PLACEMENT_SETTING = "/persistent/exts/omni.kit.manipulator.prim.core/manipulator/placement"
    """str: Path for manipulator placement settings."""
    MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT = "Authored Pivot"
    """str: Use last prim pivot for manipulator placement."""
    MANIPULATOR_PLACEMENT_SELECTION_CENTER = "Selection Center"
    """str: Use selection center for manipulator placement."""
    MANIPULATOR_PLACEMENT_BBOX_BASE = "Bounding Box Base"
    """str: Use bounding box base for manipulator placement."""
    MANIPULATOR_PLACEMENT_BBOX_CENTER = "Bounding Box Center"
    """str: Use bounding box center for manipulator placement."""
    MANIPULATOR_PLACEMENT_PICK_REF_PRIM = "Pick Reference Prim"
    """str: Use picked reference prim for manipulator placement."""


class DataRegistryEventTypes(IntEnum):
    """An enumeration for the types of events related to data registry.

    This enumeration defines the types of events that can be raised in relation to the data registry, such as when a data accessor is added or removed.
    """

    DATA_ACCESSOR_ADDED = auto()
    """int: Represents the event when a data accessor is added."""
    DATA_ACCESSOR_REMOVED = auto()
    """int: Represents the event when a data accessor is removed."""


class DataAccessorConstants:
    """A class for defining constants related to data access priorities.

    This class contains class attributes that represent the priority levels for different types of data accessors within the system. The attributes define unique string paths used to identify and categorize the accessors based on their intended usage or the data type they handle, such as 'fabric' and 'usd'. These constants are utilized to manage the order of operations and precedence among various data manipulation tasks.
    """

    DATA_ACCESSOR_PRIORITY_FABRIC = "/exts/omni.kit.manipulator.prim.core/accessor/priority/fabric"
    """str: Priority path for fabric data access."""
    DATA_ACCESSOR_PRIORITY_WRITE_FABRIC = "/exts/omni.kit.manipulator.prim.core/accessor/prioritywrite/fabric"
    """str: Priority path for fabric data write access."""
    DATA_ACCESSOR_PRIORITY_USD = "/exts/omni.kit.manipulator.prim.core/accessor/priority/usd"
    """str: Priority path for USD data access."""
    DATA_ACCESSOR_PRIORITY_WRITE_USD = "/exts/omni.kit.manipulator.prim.core/accessor/prioritywrite/usd"
    """str: Priority path for USD data write access."""
