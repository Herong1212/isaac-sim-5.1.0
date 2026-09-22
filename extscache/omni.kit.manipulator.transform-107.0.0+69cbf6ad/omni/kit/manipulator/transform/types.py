# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""Type Classes needed for transformation manipulation"""

__all__ = ["Axis", "Operation"]
from enum import Enum, Flag, auto


class Axis(Flag):
    """An enumeration to represent different axes and their combinations for transformations.

    This Flag Enum is used to define axes for translation, rotation, and scaling operations in a 3D space. It allows combining multiple axes to define a plane or space.
    """

    X = auto()
    """Represents the X-axis."""
    Y = auto()
    """Represents the Y-axis."""
    Z = auto()
    """Represents the Z-axis."""
    SCREEN = auto()
    """Represents the screen space direction."""
    ALL = X | Y | Z | SCREEN
    """Represents all axes combined, including screen space."""


class Operation(Enum):
    """An enumeration to represent different types of manipulator operations.

    This Enum is used for specifying the type of operation that a manipulator should perform, such as translation, rotation, or scaling, including their delta variants.
    """

    TRANSLATE = auto()
    """translate operation"""
    ROTATE = auto()
    """rotate operation"""
    SCALE = auto()
    """translate operation"""
    NONE = auto()
    """no operation"""
    TRANSLATE_DELTA = auto()
    """translate delta operation"""
    ROTATE_DELTA = auto()
    """rotate delta operation"""
    SCALE_DELTA = auto()
    """scale delta operation"""
