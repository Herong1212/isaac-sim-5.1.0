# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["OptionBox"]
import omni.ui as ui

from typing import Callable, List
from .style import get_style

class OptionBox:  # pragma: no cover # deprecated and not used any more
    def __init__(self, build_fn: Callable, **kwargs):
        """
         A helper class to initialize the OptionBox.
         
         Args:
              build_fn (Callable): Function that build real part in frame.
                Function signature: void build_fn(list[str])
        """
        self._frame = None
        self._build_fn = build_fn
        self._selection_changed_fn = kwargs.get("selection_changed_fn", None)
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._mouse_double_clicked_fn = kwargs.get("mouse_double_clicked_fn", None)
        self._build_ui()

    def _build_ui(self):
        self._frame = ui.Frame(visible=True, height=100, style=get_style())

    def rebuild(self, selected: List[str]):
        """
         Clear and rebuild the frame. 
         
         Args:
              selected (List[str]): List of filepath to show in option box.
        """
        if self._frame:
            self._frame.clear()
            with self._frame:
                self._build_fn(selected)

    def destroy(self):
        """ Destroy the widget. """
        self._build_fn = None
        self._selection_changed_fn = None
        self._mouse_pressed_fn = None
        self._mouse_double_clicked_fn = None
        self._frame = None

    @staticmethod
    def create_option_box(build_fn: Callable) -> 'OptionBox':
        """
         Create and return OptionBox widget. 

         Args:
              build_fn (Callable): Function that used to build the real part.
                Function signature: void build_fn(list[str])
         
         Returns: 
              An instance of  OptionBox.
        """
        widget = OptionBox(build_fn)
        return widget

    @staticmethod
    def on_selection_changed(widget: 'OptionBox', selected: List[str]):
        """
         Rebuild option box when selection changes. 
         
         Args:
              widget (:obj: 'OptionBox'): the widget that emitted the signal. 
              selected (List[str]): the list of selected filepath
        """
        if widget:
            widget.rebuild(selected)

    @staticmethod
    def delete_option_box(widget: 'OptionBox'):
        """
         Delete option box and its contents.
         
         Args:
              widget (:obj: 'OptionBox'): The widget to be delete.
        """
        if widget:
            widget.destroy()

