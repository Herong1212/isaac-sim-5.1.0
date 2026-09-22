"""This module provides commands for manipulating USD shade properties, including disconnection and setting info attributes."""

__all__ = ["UsdShadeDisconnectCommand", "SetUsdShadeInfoAttributeCommand"]

from .disconnect_command import UsdShadeDisconnectCommand
from .set_info_attribute_command import SetUsdShadeInfoAttributeCommand
