# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["DetailFrameController", "ExtendedFileInfo", "DetailView"]
import os
import omni.ui as ui
import asyncio
import omni.client
from omni.kit.async_engine import run_coroutine

from typing import Callable, List
from collections import namedtuple
from collections import OrderedDict
from carb import log_warn
from datetime import datetime
from omni.kit.helper.file_utils import asset_types
from omni.kit.widget.filebrowser import FileBrowserItem
from .style import get_style, ICON_PATH


class DetailFrameController:

    def __init__(self,
        glyph: str = None,
        build_fn: Callable[[], None] = None,
        selection_changed_fn: Callable[[List[str]], None] = None,
        filename_changed_fn: Callable[[str], None] = None,
        destroy_fn: Callable[[], None] = None,
        **kwargs
    ):
        """
        Initialize the Detail Frame. 
        
        Keyword Args:
            glyph (Optional[str]): The name of the glyph to use for the widget.
            build_fn (Callable): A function that will be called when build the detail frame.
                                    Function signature:void build_fn()
            selection_changed_fn (Callable): A function that will be called when the selection changes.
                                    Function signature:void selection_changed_fn(list[str])
            filename_changed_fn (Callable): A function that will be called when the filename of current item changes.
                                    Function signature:void filename_changed_fn(str)
            destroy_fn (Callable): A function that will be called when the widget is destroyed.
                                    Function signature:void destroy_fn()
        """
        self._frame = None
        self._glyph = glyph
        self._build_fn = build_fn
        self._selection_changed_fn = selection_changed_fn
        self._filename_changed_fn = filename_changed_fn
        self._destroy_fn = destroy_fn
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._mouse_double_clicked_fn = kwargs.get("mouse_double_clicked_fn", None)

    def build_header(self, collapsed: bool, title: str):
        """
        Builds the header. It is used to show the header of the DetailFrame.
        Args:
            collapsed (bool): True if the header is collapsed.
            title (str): title of the header to be shown.
        """
        with ui.HStack():
            if collapsed:
                ui.ImageWithProvider(f"{ICON_PATH}/arrow_right.svg", width=20, height=20)
            else:
                ui.ImageWithProvider(f"{ICON_PATH}/arrow_down.svg", width=20, height=20)
            ui.Label(title.capitalize(), style_type_name_override="DetailFrame.Header.Label")

    def build_ui(self, frame: ui.Frame):
        """
        Builds the UI. 
        Args:
            frame (ui.Frame): The frame that will be used to build the UI.
        """
        if not frame:
            return
        self._frame = frame
        with self._frame:
            try:
                self._build_fn()
            except Exception as e:
                log_warn(f"Error detail frame build_ui: {str(e)}")

    def on_selection_changed(self, selected: List[str] = []):
        """
         Called when the selection changes. It will rebuild the detail frame.
         
         Keywords Args:
              selected(List[str]): List of selected items's path.
        """
        if self._frame and self._selection_changed_fn:
            self._frame.set_build_fn(lambda: self._selection_changed_fn(selected))
            self._frame.rebuild()

    def on_filename_changed(self, filename: str):
        """
        Called when the filename has changed.It will rebuild the detail frame.
        
        Args:
            filename (str): The filename that has changed. 
        """
        if self._frame and self._filename_changed_fn:
            self._frame.set_build_fn(lambda: self._filename_changed_fn(filename))
            self._frame.rebuild()

    def destroy(self):
        """ Destructor """
        try:
            self._destroy_fn()
        except Exception:
            pass
        # NOTE: DO NOT dereference callbacks so that we can rebuild this object if desired.
        self._frame = None


class ExtendedFileInfo(DetailFrameController):
    """ Extended file info show in detail view"""
    MockListEntry = namedtuple("MockListEntry", "relative_path modified_time created_by modified_by size")
    _empty_list_entry = MockListEntry("File info", datetime.now(), "", "", 0)

    def __init__(self):
        super().__init__(
            build_fn=self._build_ui_impl,
            selection_changed_fn=self._on_selection_changed_impl,
            destroy_fn=self._destroy_impl)
        self._widget = None
        self._current_url = ""
        self._resolve_subscription = None
        self._time_label = None
        self._created_by_label = None
        self._modified_by_label = None
        self._size_label = None

    def build_header(self, collapsed: bool, title: str):
        """
        Builds the header. It is used to show the header of the file info.
        Args:
            collapsed (bool): True if the header is collapsed.
            title (str): title of the header to be shown.
        """
        with ui.HStack(style_type_name_override="DetailFrame.Header"):
            if collapsed:
                ui.ImageWithProvider(f"{ICON_PATH}/arrow_right.svg", width=20, height=20)
            else:
                ui.ImageWithProvider(f"{ICON_PATH}/arrow_down.svg", width=20, height=20)
            icon = asset_types.get_icon(title)
            if icon is not None:
                ui.ImageWithProvider(icon, width=18, style_type_name_override="DetailFrame.Header.Icon")
                ui.Spacer(width=4)
            ui.Label(title, elided_text=True, tooltip=title, style_type_name_override="DetailFrame.Header.Label")

    def _build_ui_impl(self, selected: List[str] = []):
        self._widget = ui.Frame()
        run_coroutine(self._build_ui_async(selected))

    async def _build_ui_async(self, selected: List[str] = []):
        entry = None
        if len(selected) == 0:
            self._frame.title = "No files selected"
        elif len(selected) > 1:
            self._frame.title = "Multiple files selected"
        else:
            result, entry = await omni.client.stat_async(selected[-1])
            if result == omni.client.Result.OK and entry:
                self._frame.title = entry.relative_path or os.path.basename(selected[-1])
                if self._current_url != selected[-1]:
                    self._current_url = selected[-1]
                    self._resolve_subscription = omni.client.resolve_subscribe_with_callback(
                            self._current_url, [self._current_url], None,
                            lambda result, event, entry, url: self._on_file_change_event(result, entry))
            else:
                self._frame.title = os.path.basename(selected[-1])
                entry = None

        entry = entry or self._empty_list_entry
        with self._widget:
            with ui.ZStack():
                ui.Rectangle()
                with ui.VStack():
                    ui.Rectangle(height=2, style_type_name_override="DetailFrame.Separator")
                    with ui.VStack(style_type_name_override="DetailFrame.Body"):
                        with ui.HStack(style_type_name_override="DetailFrame.LineItem", spacing=3):
                            ui.Label("Date Modified", width=0, name="left_aligned")
                            self._time_label = ui.Label(
                                FileBrowserItem.datetime_as_string(entry.modified_time), 
                                elided_text=True,
                                alignment=ui.Alignment.RIGHT_CENTER,
                                name="right_aligned"
                            )
                        with ui.HStack(style_type_name_override="DetailFrame.LineItem", spacing=3):
                            ui.Label("Created by", width=0, name="left_aligned")
                            self._created_by_label = ui.Label(entry.created_by, 
                                elided_text=True,
                                alignment=ui.Alignment.RIGHT_CENTER,
                                name="right_aligned"
                            )
                        with ui.HStack(style_type_name_override="DetailFrame.LineItem", spacing=3):
                            ui.Label("Modified by", width=0, name="left_aligned")
                            self._modified_by_label = ui.Label(
                                entry.modified_by, 
                                elided_text=True,
                                alignment=ui.Alignment.RIGHT_CENTER,
                                name="right_aligned"
                            )
                        with ui.HStack(style_type_name_override="DetailFrame.LineItem", spacing=3):
                            ui.Label("File size", width=0, name="left_aligned")
                            self._size_label = ui.Label(
                                FileBrowserItem.size_as_string(entry.size),
                                elided_text=True,
                                alignment=ui.Alignment.RIGHT_CENTER,
                                name="right_aligned"
                            )

    def _on_file_change_event(self, result: omni.client.Result, entry: omni.client.ListEntry):
        if result == omni.client.Result.OK and self._current_url:
            self._time_label.text = FileBrowserItem.datetime_as_string(entry.modified_time)
            self._created_by_label.text = entry.created_by
            self._modified_by_label.text = entry.modified_by
            self._size_label.text = FileBrowserItem.size_as_string(entry.size)

    def _on_selection_changed_impl(self, selected: List[str] = []):
        self._build_ui_impl(selected)

    def _destroy_impl(self, _):
        if self._widget:
            self._widget.destroy()
        self._widget = None
        self._resolve_subscription = None


class DetailView:
    """ Detail view that contains all detail frames"""
    def __init__(self, **kwargs):
        self._widget: ui.Widget = None
        self._view: ui.Widget = None
        self._file_info = None
        self._detail_frames: OrderedDict[str, DetailFrameController] = OrderedDict()
        self._build_ui()

    def _build_ui(self):
        self._widget = ui.Frame()
        with self._widget:
            with ui.ZStack(style=get_style()):
                ui.Rectangle(style_type_name_override="DetailView")
                self._view = ui.ScrollingFrame(
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    style_type_name_override="DetailView.ScrollingFrame"
                )
                self._build_detail_frames()

    def _build_detail_frames(self):
        async def build_frame_async(frame: ui.Frame, detail_frame: DetailFrameController):
            detail_frame.build_ui(frame)

        with self._view:
            with ui.VStack():
                self._file_info = ExtendedFileInfo()
                frame = ui.CollapsableFrame(title="File info", height=0, build_header_fn=self._file_info.build_header, style_type_name_override="DetailFrame")
                run_coroutine(build_frame_async(frame, self._file_info))
                for name, detail_frame in reversed(self._detail_frames.items()):
                    frame = ui.CollapsableFrame(title=name.capitalize(), height=0, build_header_fn=detail_frame.build_header, style_type_name_override="DetailFrame")
                    run_coroutine(build_frame_async(frame, detail_frame))

    def get_detail_frame(self, name: str) -> DetailFrameController:
        """
        Get the detail frame by given name. This method is thread safe. Use with caution
        
        Args:
            name: Name of the detail frame
        
        Returns: 
            :obj:'DetailFrameController' with given name or None if not found
        """
        if name:
            return self._detail_frames.get(name, None)
        return None

    def add_detail_frame(self,
        name: str, glyph: str,
        build_fn: Callable[[], ui.Widget],
        selection_changed_fn: Callable[[List[str]], None] = None,
        filename_changed_fn: Callable[[str], None] = None,
        destroy_fn: Callable[[ui.Widget], None] = None):
        """
        Adds sub-frame to the detail view, and populates it with a custom built widget.

        Args:
            name (str): Name of the widget sub-section, this name must be unique over all detail sub-sections.
            glyph (str): Associated glyph to display for this subj-section
            build_fn (Callable): This callback function builds the widget.

        Keyword Args:
            selection_changed_fn (Callable): This callback is invoked to handle selection changes.
            filename_changed_fn (Callable): This callback is invoked when filename is changed.
            destroy_fn (Callable): Cleanup function called when destroyed.

        """
        if not name:
            return
        elif name in self._detail_frames.keys():
            # Reject duplicates
            log_warn(f"Unable to add detail widget '{name}': already exists.")
            return

        detail_frame = DetailFrameController(
            glyph=glyph,
            build_fn=build_fn,
            selection_changed_fn=selection_changed_fn,
            filename_changed_fn=filename_changed_fn,
            destroy_fn=destroy_fn,
        )
        self.add_detail_frame_from_controller(name, detail_frame)

    def add_detail_frame_from_controller(self, name: str, detail_frame: DetailFrameController = None):
        """
        Adds sub-frame to the detail view, and populates it with a custom built widget.

        Args:
            name (str): Name of the widget sub-section, this name must be unique over all detail sub-sections.
            controller (:obj:`DetailFrameController`): Controller object that encapsulates all aspects of creating,
                updating, and deleting a detail frame widget.

        """
        if not name:
            return
        elif name in self._detail_frames.keys():
            # Reject duplicates
            log_warn(f"Unable to add detail widget '{name}': already exists.")
            return

        if detail_frame:
            self._detail_frames[name] = detail_frame
            self._build_detail_frames()

    def delete_detail_frame(self, name: str):
        """
        Deletes the specified detail frame.

        Args:
            name (str): Name of the detail frame.

        """
        if name in self._detail_frames.keys():
            del self._detail_frames[name]
            self._build_detail_frames()

    def on_selection_changed(self, selected: List[FileBrowserItem] = []):
        """
        When the user changes their filebrowser selection(s), invokes the callbacks for the detail frames.

        Args:
            selected (:obj:`FileBrowserItem`): List of new selections.

        """
        selected_paths = [sel.path for sel in selected if sel]
        if self._file_info:
            self._file_info.on_selection_changed(selected_paths)
        for _, detail_frame in self._detail_frames.items():
            detail_frame.on_selection_changed(selected_paths)

    def on_filename_changed(self, filename: str = ''):
        """
        When the user edits the filename, invokes the callbacks for the detail frames.

        Args:
            filename (str): Current filename.

        """
        for _, detail_frame in self._detail_frames.items():
            detail_frame.on_filename_changed(filename)

    def destroy(self):
        """ Destructor """
        for _, detail_frame in self._detail_frames.items():
            detail_frame.destroy()
        self._detail_frames.clear()
        self._widget = None
        self._view = None