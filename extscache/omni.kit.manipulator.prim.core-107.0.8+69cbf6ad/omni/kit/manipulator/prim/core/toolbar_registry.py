# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides access to a singleton ToolbarRegistry instance for manipulator toolbars."""


from omni.kit.manipulator.transform import ToolbarRegistry

_toolbar_registry = ToolbarRegistry()


def get_toolbar_registry() -> ToolbarRegistry:
    """Returns the singleton instance of the ToolbarRegistry.

    Returns:
        :obj:`ToolbarRegistry`: The singleton instance of the ToolbarRegistry."""
    return _toolbar_registry
