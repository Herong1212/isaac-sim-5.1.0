# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["TimestampWidget"]

import datetime
import omni.ui as ui
from .datetime import DateWidget, TimeWidget, TimezoneWidget
from typing import List
from .style import get_style


class TimestampWidget:
    def __init__(self, **kwargs):
        """
        Timestamp Widget.

        """
        self._url = None
        self._on_check_changed_fn = []
        self._checkpoint_widget = None

        self._frame = None
        self._timestamp_checkbox = None
        self._datetime_stack = None
        self._desc_text = None
        self._date = None
        self._time = None
        self._timezone = None
        self._selection_changed_fn = kwargs.get("selection_changed_fn", None)
        self._frame = ui.Frame(visible=True, height=100, style=get_style())
        self._frame.set_build_fn(self._build_ui)
        self._frame.rebuild()

    def __del__(self):
        self.destroy()    

    def destroy(self):
        """
        Destroy and clean up the widget.
        """

        self._on_check_changed_fn.clear()
        self._checkpoint_widget = None
        self._selection_changed_fn = None
        if self._timestamp_checkbox:
            self._timestamp_checkbox.model.remove_value_changed_fn(self._checkbox_fn_id)
            self._timestamp_checkbox = None
        self._datetime_stack = None
        self._frame = None
        if self._date:
            self._date.model.remove_value_changed_fn(self._date_fn_id)
            self._date.destroy()
            self._date = None
        if self._time:
            self._time.model.remove_value_changed_fn(self._time_fn_id)
            self._time.destroy()
            self._time = None
        if self._timezone:
            self._timezone.model.remove_value_changed_fn(self._timezone_fn_id)
            self._timezone.destroy()
            self._timezone = None
        

    def rebuild(self, selected: List[str]):
        """
         Rebuild the frame. This is called when the user clicks on the rebuild button. 
         Args:
              selected (List[str]): List of items that have been selected. 
        """
        self._frame.rebuild()

    def _build_ui(self):
        with ui.ZStack(height=32, width=0):
            self._datetime_stack = ui.VStack(visible=False)
            with self._datetime_stack:
                with ui.HStack(height=0, spacing=6):
                    self._timestamp_checkbox = ui.CheckBox(width=0)
                    self._checkbox_fn_id = self._timestamp_checkbox.model.add_value_changed_fn(self._on_timestamp_checked)
                    ui.Label("Resolve with")
                with ui.HStack(height=0, spacing=0):
                    ui.Label("Date:", width=0)
                    self._date = DateWidget()
                    self._date_fn_id = self._date.model.add_value_changed_fn(self._on_timestamp_changed)
                    ui.Label("Time:", width=0)
                    self._time = TimeWidget()
                    self._time_fn_id = self._time.model.add_value_changed_fn(self._on_timestamp_changed)
                    self._timezone = TimezoneWidget()
                    self._timezone_fn_id = self._timezone.model.add_value_changed_fn(self._on_timestamp_changed)
            self._desc_text = ui.Label("Unsupported")

    @staticmethod
    def create_timestamp_widget() -> 'TimestampWidget':
        """
         Create and return a TimestampWidget. 
         
         
         Returns: 
              :obj:'TimestampWidget': A TimestampWidget instance.
        """
        widget = TimestampWidget()
        return widget

    @staticmethod
    def delete_timestamp_widget(widget: 'TimestampWidget'):
        """
         Delete a TimestampWidget.
         
         Args:
              widget(:obj:'TimestampWidget'): The widget to be deleted. If None is passed no action is taken
        """
        if widget:
            widget.destroy()

    @staticmethod
    def on_selection_changed(widget: 'TimestampWidget', selected: List[str]):
        """
         Callback for when selection changes. 
         
         Args:
              widget (:obj:'TimestampWidget'): TimestampWidget that was toggled.
              selected (List[str]): List of items that were selected. If None is selected no change is made.
        """
        if not widget:
            return
        if selected:
            widget.set_url(selected[-1] or None)
        else:
            widget.set_url(None)

    # show timestamp status according to the checkpoint_widget status
    def set_checkpoint_widget(self, widget):
        """
         Set the checkpoint widget. This is used to provide feedback to the user when they want to check out the state of the experiment
         
         Args:
              widget(obj): The widget to be
        """
        self._checkpoint_widget = widget

    def on_list_checkpoint(self, select):
        """
         Called when user selects a checkpoint. 
         
         Args:
              select(str): selected item.
        """
        # Fix OM-85963: It seems this called without UI (not builded or destory?) in some test
        if self._datetime_stack:
            has_checkpoint = self._checkpoint_widget is not None and not self._checkpoint_widget.empty()
            self._datetime_stack.visible = has_checkpoint
            self._desc_text.visible = not has_checkpoint

    def set_url(self, url: str):
        """
         Set the url.
         
         Args:
              url(str): The URL to set.
        """
        self._url = url

    def get_timestamp_url(self, url: str) -> str:
        """
         Returns the URL to use for the timestamp. 
         
         Args:
              url (str): The url to use.
         
         Returns: 
              str: The url with the timestamp appended to it if the timestamp checkbox is checked. 
        """
        if url and url != self._url:
            return url
        
        if not self._timestamp_checkbox.model.as_bool:
            return self._url
        
        dt = datetime.datetime(
            self._date.model.year,
            self._date.model.month,
            self._date.model.day,
            self._time.model.hour,
            self._time.model.minute,
            self._time.model.second,
            tzinfo=self._timezone.model.timezone,
        )
        
        full_url = f"{self._url}?&timestamp={int(dt.timestamp())}"        
        return full_url

    def add_on_check_changed_fn(self, fn):
        """
         Add a function to be called when the check changes. The function will be called with the following arguments
         
         Args:
              fn (Callable): The function to be.
        """
        self._on_check_changed_fn.append(fn)

    def _on_timestamp_checked(self, model):
        full_url = self.get_timestamp_url(None)
        for fn in self._on_check_changed_fn:
            fn(full_url)

    def _on_timestamp_changed(self, model):
        if self._timestamp_checkbox.model.as_bool:
            self._on_timestamp_checked(None)

    @property
    def check(self) -> bool:
        """
         Get check box status of timestamp widget. 
         Returns: 
              bool: True if the timestamp is valid False otherwise.
        """
        if self._timestamp_checkbox:
            return self._timestamp_checkbox.model.as_bool
        return False

    @check.setter
    def check(self, value: bool):
        """
         Set the Check box status for the timestamp. 
         Args:
              value (bool): True if the timestamp should be checked False otherwise
        """
        # Set the timestamp checkbox to the current value
        if self._timestamp_checkbox:
            self._timestamp_checkbox.model.set_value(value)
