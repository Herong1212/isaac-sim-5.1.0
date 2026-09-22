# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
An abstract column delegate class. Subclassed by column delegates used by :obj:`FileBrowserTreeView`.
"""
__all__ = ["ColumnItem", "AbstractColumnDelegate"]

import omni.ui as ui
import abc


class ColumnItem:
    """ Column Item class to be used with FileBrowserTreeView. """
    #It's not clear which data we need to pass to build_widget. It's path, but
    #there are potentially other interesting information the column has. To
    #keep API unchanged over the time, we pass data in a struct. It also allow
    #to pass custom data with deriving from this class.

    def __init__(self, path):
        self._path = path

    @property
    def path(self):
        """ Path of the item. """
        return self._path


class AbstractColumnDelegate(metaclass=abc.ABCMeta):
    """
    An abstract object that is used to put the widget to the file browser asynchronously.
    """

    @property
    def initial_width(self):
        """The width of the column"""
        return ui.Fraction(1)

    def build_header(self):
        """Build the header"""
        pass

    @abc.abstractmethod
    async def build_widget(self, item: ColumnItem):
        """
        Build the widget for the given path. Works inside Frame in async
        mode. Once the widget is created, it will replace the content of the
        frame. It allow to await something for a while and create the widget
        when the result is available.
        """
        pass
