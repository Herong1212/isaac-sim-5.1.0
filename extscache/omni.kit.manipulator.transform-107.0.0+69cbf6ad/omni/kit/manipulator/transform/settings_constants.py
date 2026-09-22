# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


class Constants:
    """A class containing constants for the transform manipulator settings.

    These constants are used for accessing and storing transform manipulator settings such as movement mode, rotation mode, operation type, and various configuration settings related to the manipulator tool.
    """

    TRANSFORM_MOVE_MODE_SETTING = "/app/transform/moveMode"
    """setting of transform move mode"""

    TRANSFORM_ROTATE_MODE_SETTING = "/app/transform/rotateMode"
    """setting of transform rotate mode"""

    TRANSFORM_MODE_GLOBAL = "global"
    """global transform mode name"""

    TRANSFORM_MODE_LOCAL = "local"
    """local transform mode name"""

    TRANSFORM_OP_SETTING = "/app/transform/operation"
    """transform operation setting path"""

    TRANSFORM_OP_SELECT = "select"
    """transform operation select name"""
    TRANSFORM_OP_MOVE = "move"
    """transform operation move name"""
    TRANSFORM_OP_ROTATE = "rotate"
    """transform operation rotate name"""
    TRANSFORM_OP_SCALE = "scale"
    """transform operation scale name"""

    MANIPULATOR_SCALE_SETTING = "/persistent/exts/omni.kit.manipulator.transform/manipulator/scaleMultiplier"
    """Sets the scale multiplier for the manipulator, affecting its visual representation size."""

    FREE_ROTATION_ENABLED_SETTING = "/persistent/exts/omni.kit.manipulator.transform/manipulator/freeRotationEnabled"
    """setting path of whether free rotation is enabled"""
    FREE_ROTATION_TYPE_SETTING = "/persistent/exts/omni.kit.manipulator.transform/manipulator/freeRotationType"
    """setting path of free rotation type"""
    FREE_ROTATION_TYPE_CLAMPED = "Clamped"
    """free rotation clamped type name"""
    FREE_ROTATION_TYPE_CONTINUOUS = "Continuous"
    """free rotation continuous type name"""

    OMNI_SCALE_DIR_SETTING = "/persistent/exts/omni.kit.manipulator.transform/manipulator/omniScaleDirection"
    """Configures the direction in which omni-scale can be performed (e.g., "X", "Y" or "XY")."""

    INTERSECTION_THICKNESS_SETTING = "/persistent/exts/omni.kit.manipulator.transform/manipulator/intersectionThickness"
    """Specifies the intersection thickness for the manipulator, affecting hit detection for interaction."""

    TOOLS_DEFAULT_COLLAPSED_SETTING = "/persistent/exts/omni.kit.manipulator.transform/tools/defaultCollapsed"
    """Indicates whether the toolbar should be collapsed by default."""


# backward compatibility
c = Constants
