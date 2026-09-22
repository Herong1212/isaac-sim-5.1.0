"""
omni.kit.window.property PropertyFilter base class.
"""

# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["PropertyFilter"]

import omni.ui as ui


class PropertyFilter:
    """User defined filters for properties. For now, just a substring filter on property names."""

    def __init__(self):
        """Initialize class function."""
        self._name = ui.SimpleStringModel()

    def matches(self, name: str) -> bool:
        """Returns True if name matches filter, so property should be visible.

        Args:
            name: name to match.

        Returns:
            bool: True if matched
        """
        return not self.name or self.name.lower() in name.lower()

    @property
    def name_model(self):
        """Model name getter function.

        Returns:
            str: name model.
        """
        return self._name

    @property
    def name(self):
        """Name getter function.

        Returns:
            str: name
        """
        return self._name.as_string

    @name.setter
    def name(self, name: str):
        """Name setter function.

        Args:
            name: name.
        """
        self._name.as_string = name
