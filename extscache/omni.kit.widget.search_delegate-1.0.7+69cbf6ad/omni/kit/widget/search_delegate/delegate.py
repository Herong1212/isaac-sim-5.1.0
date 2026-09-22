# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import abc


class SearchDelegate:
    """A base class for implementing search delegates in Omni UI.

    This abstract class defines the interface for search user interface components. It provides properties to determine if the search widget is visible and enabled, and to manage the search directory. Subclasses must implement the build_ui and destroy methods to create and remove UI elements appropriately.
    """

    def __init__(self):
        """Initializes a new SearchDelegate instance."""
        self._search_dir = None

    @property
    def visible(self):
        """Gets the visible property.

        Returns:
            bool: The visible property state.
        """
        return True  # pragma: no cover

    @property
    def enabled(self):
        """Gets the enabled property. Enable/disable Widget.

        Returns:
            bool: The enabled property state.
        """
        return True  # pragma: no cover

    @property
    def search_dir(self):
        """Gets the search_dir property.

        Returns:
            str: The current search directory.
        """
        return self._search_dir  # pragma: no cover

    @search_dir.setter
    def search_dir(self, search_dir: str):
        """Sets the search_dir property.

        Args:
            search_dir (str): The new search directory.
        """
        self._search_dir = search_dir  # pragma: no cover

    @abc.abstractmethod
    def build_ui(self):
        """Builds the user interface components for the search delegate."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def destroy(self):
        """Destroys any resources used by the search delegate."""
        pass  # pragma: no cover
