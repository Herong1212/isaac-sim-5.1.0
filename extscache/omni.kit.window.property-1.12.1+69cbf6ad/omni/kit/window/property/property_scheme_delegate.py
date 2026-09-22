"""
omni.kit.window.property PropertySchemeDelegate base class
"""

# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["PropertySchemeDelegate"]

from abc import abstractmethod
from typing import List


class PropertySchemeDelegate:
    """
    PropertySchemeDelegate is a class to test given payload and determine what widgets to be drawn in what order.
    """

    @abstractmethod
    def get_widgets(self, payload) -> List[str]:
        """
        Tests the payload and gathers widgets in interest to be drawn in specific order.

        Args:
            payload (PrimSelectionPayload): payload.

        Returns:
            list: list of widgets to build.
        """
        return []

    def get_unwanted_widgets(self, payload) -> List[str]:
        """
        Tests the payload and returns a list of widget names which this delegate does not want to include.
        Note that if there is another PropertySchemeDelegate returning widget in its get_widgets that conflicts with
        names in get_unwanted_widgets, get_widgets always wins (i.e. the Widget will be drawn).

        This function is optional.

        Args:
            payload (PrimSelectionPayload): payload.

        Returns:
            list: list of unwanted widgets.
        """
        return []
