"""
omni.kit.window.property PropertyWidget base class
"""

# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["PropertyWidget"]

from abc import abstractmethod
from typing import Optional

from .property_filter import PropertyFilter


# Base class of a property widget
class PropertyWidget:
    """
    Base class to create a group of widgets in Property Window
    """

    def __init__(self, title: str):
        """Initialize class function"""
        self._title = title
        # Ensure we always have a valid filter because PropertyWidgets may be created outside PropertyWindow
        self._filter = PropertyFilter()

    @abstractmethod
    def clean(self):
        """Clean up function to be called before destroying the object."""

    @abstractmethod
    def reset(self):
        """Clean up function to be called when previously built widget is no longer visible given new scheme/payload."""

    @abstractmethod
    def build_impl(self):
        """Main function to creates the UI elements."""

    @abstractmethod
    def on_new_payload(self, payload) -> bool:
        """
        Called when a new payload is delivered. PropertyWidget can take this opportunity to update its ui models,
        or schedule full UI rebuild.

        Args:
            payload: The new payload to refresh UI or update model.

        Return:
            True if the UI needs to be rebuilt. build_impl will be called as a result.
            False if the UI does not need to be rebuilt. build_impl will not be called.
        """

    def build(self, filter_cls: Optional[PropertyFilter] = None):
        """UI builder function.

        Args:
            filter_cls (PropertyFilter): filter to use while building UI.
        """

        # TODO some other decoration/styling here
        if filter_cls:
            self._filter = filter_cls
        self.build_impl()
