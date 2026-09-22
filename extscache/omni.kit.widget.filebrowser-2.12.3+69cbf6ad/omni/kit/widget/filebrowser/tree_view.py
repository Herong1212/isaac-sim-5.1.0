# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
A generic Tree View Widget for File Systems.
"""
import asyncio
import carb

from omni import ui
from typing import List
from typing import Tuple
from functools import partial
from datetime import datetime
from carb import log_warn
from .view import FileBrowserView
from .model import FileBrowserItem, FileBrowserItemFields, FileBrowserModel
from .style import UI_STYLES, ICON_PATH
from .abstract_column_delegate import AbstractColumnDelegate, ColumnItem
from .column_delegate_registry import ColumnDelegateRegistry
from .date_format_menu import DatetimeFormatMenu
from . import ALERT_WARNING, ALERT_ERROR
from .clipboard import is_path_cut

__all__ = ["AwaitWithFrame", "FileBrowserTreeView", "FileBrowserTreeViewDelegate"]

class AwaitWithFrame:
    """
    A future-like object that runs the given future and makes sure it's
    always in the given frame's scope. It allows for creating widgets
    asynchronously.
    """

    def __init__(self, frame: ui.Frame, future: asyncio.Future):
        self._frame = frame
        self._future = future

    def __await__(self):
        # create an iterator object from that iterable
        iter_obj = iter(self._future.__await__())

        # infinite loop
        while True:
            try:
                with self._frame:
                    yield next(iter_obj)
            except StopIteration:
                break
            except Exception as e:
                log_warn(f"Error rendering frame: {str(e)}")
                break

        self._frame = None
        self._future = None


class FileBrowserTreeView(FileBrowserView):
    """
    UI Widget for display files or folders as icons in a directory in tree view.

    Keyword Args:
        root_visible (bool): Set to True to show the root item.
        header_visible (bool): Set to True to show the column headers.
        allow_multi_selection (bool): Optional argument to enable multi selection, defaults to True.
        selection_changed_fn (Callable): Function called when selection changed. Function signature:
            void selection_changed_fn(selections: List[:obj:`FileBrowserItem`])
        mouse_pressed_fn (Callable): Function called on mouse press. Function signature:
            void mouse_pressed_fn(item: :obj:`FileBrowserItem`, x: float, y: float, button: int, key_mode: int)
        mouse_double_clicked_fn (Callable): Function called on mouse double click. Function signature:
            void mouse_double_clicked_fn(item: :obj:`FileBrowserItem`, x: float, y: float,  button: int, key_mode: int)
        treeview_identifier (str): widget identifier for treeview, only used by tests.
    """
    def __init__(self, model: FileBrowserModel, **kwargs):
        import carb.settings

        self._tree_view: ui.TreeView = None
        self._delegate = None
        super().__init__(model)
        self._headers = FileBrowserItemFields._fields

        theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        use_default_style = carb.settings.get_settings().get_as_string("/persistent/app/window/useDefaultStyle") or False
        if use_default_style:
            self._style = {}
        else:
            self._style = UI_STYLES[theme]
        self._root_visible = kwargs.get("root_visible", True)
        self._header_visible = kwargs.get("header_visible", True)
        self._allow_multi_selection = kwargs.get("allow_multi_selection", True)
        self._selection_changed_fn = kwargs.get("selection_changed_fn", None)
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._mouse_double_clicked_fn = kwargs.get("mouse_double_clicked_fn", None)
        self._treeview_identifier = kwargs.get('treeview_identifier', None)

        # Callback when the tag registry is changed
        self._column_delegate_sub = ColumnDelegateRegistry().subscribe_delegate_changed(
            self._on_column_delegate_changed
        )

        kwargs["mouse_pressed_fn"] = self._on_mouse_pressed
        kwargs["mouse_double_clicked_fn"] = self._on_mouse_double_clicked
        kwargs["column_clicked_fn"] = lambda column_id: self._on_column_clicked(column_id)
        kwargs["datetime_format_changed_fn"] = self._on_datetime_format_changed
        kwargs["sort_by_column"] = self._headers.index(self._model.sort_by_field)
        kwargs["sort_ascending"] = self._model.sort_ascending
        kwargs["builtin_column_count"] = self._model.builtin_column_count
        self._delegate = FileBrowserTreeViewDelegate(self._headers, theme, **kwargs)
        name = "TableViewFrame"
        if self._treeview_identifier and self._treeview_identifier.endswith("_folder_view"):
            name = "ListViewFrame"
        self._widget = ui.ScrollingFrame(
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
            mouse_pressed_fn=partial(self._on_mouse_pressed, None),
            mouse_double_clicked_fn=partial(self._on_mouse_double_clicked, None),
            style_type_name_override="TreeView.ScrollingFrame",
            name=name,
            identifier=name,
        )

    def build_ui(self):
        """ Build the tree view. """
        with self._widget:
            selection_changed_fn = lambda selections: self._on_selection_changed(selections)

            self._tree_view = ui.TreeView(
                self._model,
                delegate=self._delegate,
                root_visible=self._root_visible,
                header_visible=self._header_visible,
                selection_changed_fn=selection_changed_fn,
                columns_resizable=True,
            )
            if self._treeview_identifier:
                self._tree_view.identifier = self._treeview_identifier

        # It should set the column widths and pass tag delegated to the main delegate
        self._on_column_delegate_changed()

    @property
    def tree_view(self):
        """ Get the tree view. """
        return self._tree_view

    @property
    def selections(self):
        """ Get selected items in the tree view. """
        if self._tree_view:
            return self._tree_view.selection
        return []

    def refresh_ui(self, item: FileBrowserItem = None):
        """
        Throttle the refreshes so that the UI can keep up with multiple refresh directives in succession.

        Args:
            item (:obj:`FileBrowserItem`): The item to refresh.
        """
        def update_view(item: FileBrowserItem):
            if self._tree_view:
                self._tree_view.dirty_widgets()

        if self._model:
            # NOTE: The following action is not publicized but is required for a proper redraw
            self._model._item_changed(item)

        self._throttled_refresh_ui(item=item, callback=update_view, throttle_frames=2)

    def is_expanded(self, item: FileBrowserItem) -> bool:
        """ Return True if the item is expanded. """
        if self._tree_view and item:
            return self._tree_view.is_expanded(item)
        return False

    def set_expanded(self, item: FileBrowserItem, expanded: bool, recursive: bool = False):
        """
        Set the expansion state of the given item.

        Args:
            item (:obj:`FileBrowserItem`): The item to effect.
            expanded (bool): True to expand, False to collapse.
            recursive (bool): Apply state recursively to descendent nodes. Default False.

        """
        if self._tree_view and item:
            self._tree_view.set_expanded(item, expanded, recursive)

    def select_and_center(self, item: FileBrowserItem):
        """
        Select and center the view on the given item.

        Args:
            item (:obj:`FileBrowserItem`): the item to set the new selection to.
        """
        if not self._visible:
            return

        item = item or self._model.root
        if not item:
            return

        def set_expanded_recursive(item: FileBrowserItem):
            if not item:
                return
            set_expanded_recursive(item.parent)
            self.set_expanded(item, True)

        set_expanded_recursive(item)
        self._tree_view.selection = [item]
        self.refresh_ui()

    def _on_mouse_pressed(self, item: FileBrowserItem, x, y, button, key_mod):
        if self._mouse_pressed_fn:
            self._mouse_pressed_fn(button, key_mod, item, x=x, y=y)

    def _on_mouse_double_clicked(self, item: FileBrowserItem, x, y, button, key_mod):
        if self._mouse_double_clicked_fn:
            self._mouse_double_clicked_fn(button, key_mod, item, x=x, y=y)

    def _on_selection_changed(self, selections: [FileBrowserItem]):
        if not self._allow_multi_selection:
            if selections:
                selections = selections[-1:]
                self._tree_view.selection = selections
        if self._model:
            self._model.drag_mime_data = [sel.path for sel in selections]
        if self._selection_changed_fn:
            self._selection_changed_fn(selections)

    def _on_column_clicked(self, column_id: int):
        column_id = min(column_id, len(FileBrowserItemFields._fields) - 1)
        if column_id == self._delegate.sort_by_column:
            self._delegate.sort_ascending = not self._delegate.sort_ascending
        else:
            self._delegate.sort_by_column = column_id
        if self._model:
            self._model.sort_by_field = self._headers[column_id]
            self._model.sort_ascending = self._delegate.sort_ascending
        self.refresh_ui()

    def _on_datetime_format_changed(self):
        self.refresh_ui()

    def _on_item_changed(self, model, item):
        """Called by the model when something is changed"""
        if self._delegate and item is None:
            self._delegate.clear_futures()

    def _on_model_changed(self, model):
        """Called by super when the model is changed"""
        if model and self._tree_view:
            self._tree_view.model = model
        if self._delegate:
            self._delegate.clear_futures()

    def _on_column_delegate_changed(self):
        """Called by ColumnDelegateRegistry"""
        # Single column should fill all available space
        if not self._model.single_column:
            column_delegate_names = ColumnDelegateRegistry().get_column_delegate_names()
            column_delegate_types = [ColumnDelegateRegistry().get_column_delegate(name) for name in column_delegate_names]
            # Create the tag delegates
            column_delegates = [delegate_type() for delegate_type in column_delegate_types]

            self._delegate.set_column_delegates(column_delegates)

            # Set column widths
            # OM-30768: Make file-name dominant and push with left list view separator
            self._tree_view.column_widths = [ui.Fraction(.75), ui.Fraction(0.15), ui.Fraction(0.1)] + [
                d.initial_width for d in column_delegates
            ]
        else:
            self._tree_view.column_widths = [ui.Fraction(1)]

        # Update the widget
        self._model._item_changed(None)

    def scroll_top(self):
        """Scroll the widget to top"""
        if self._widget:
            # Scroll to top upon refresh
            self._widget.scroll_y = 0.0

    def destroy(self):
        """ Destructor. """
        super().destroy()
        if self._model:
            self._model.destroy()
            self._model = None
        if self._tree_view:
            self._tree_view.destroy()
            self._tree_view = None
        if self._widget:
            self._widget.destroy()
            self._widget = None
        if self._delegate:
            self._delegate.destroy()
            self._delegate = None

        self._headers = None
        self._style = None
        self._selection_changed_fn = None
        self._mouse_pressed_fn = None
        self._mouse_double_clicked_fn = None
        self._column_delegate_sub = None


class FileBrowserTreeViewDelegate(ui.AbstractItemDelegate):
    """
    The delegate that manages building browser items under the model as widgets inside the tree view.

    Args:
        headers (Tuple[str]): Tuple of columns to show in the tree view.
        theme (str): The theme name to use.

    Keyword Args:
        mouse_pressed_fn (Callable): Function called on mouse press. Function signature:
            void mouse_pressed_fn(item: :obj:`FileBrowserItem`, x: float, y: float, button: int, key_mode: int)
        mouse_double_clicked_fn (Callable): Function called on mouse double click. Function signature:
            void mouse_double_clicked_fn(item: :obj:`FileBrowserItem`, x: float, y: float,  button: int, key_mode: int)
        column_clicked_fn (Callable): Function called when column clicked. Function signature:
            void column_clicked_fn(column_id: int)
        datetime_format_changed_fn (Callable): Function called when datetime format changed. Function signature:
            void datetime_format_changed_fn()
        sort_by_column (int): The column index to sort items, defaults to 0.
        sort_ascending (bool): Sort in ascending or otherwise descending order, defaults to ascending.
        builtin_columnt_count (int): Set count of builtin columns.
        icon_provider (object): Set this to override default icons.
    """
    def __init__(self, headers: Tuple[str], theme: str, **kwargs):
        super().__init__()
        self._headers = headers
        self._theme = theme
        use_default_style = carb.settings.get_settings().get_as_string("/persistent/app/window/useDefaultStyle") or False
        if use_default_style:
            self._style = {}
        else:
            self._style = UI_STYLES[theme]
        self._hide_files = not kwargs.get("files_visible", True)
        self._tooltip = kwargs.get("tooltip", False)
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._mouse_double_clicked_fn = kwargs.get("mouse_double_clicked_fn", None)
        self._column_clicked_fn = kwargs.get("column_clicked_fn", None)
        self._datetime_format_changed_fn = kwargs.get("datetime_format_changed_fn", None)
        self._sort_by_column = kwargs.get("sort_by_column", 0)
        self._sort_ascending = kwargs.get("sort_ascending", True)
        self._builtin_column_count = kwargs.get("builtin_column_count", 1)
        self._column_delegates = []
        self._icon_provider = kwargs.get("icon_provider", None)
        # The futures that are created by column delegates. We need to store
        # them to cancel when the model is changed.
        self._column_futures: List["Future"] = []
        self._date_format_menu = None

    def destroy(self):
        """ Destructor. """
        self.clear_futures()
        self._headers = None
        self._style = None
        self._mouse_pressed_fn = None
        self._mouse_double_clicked_fn = None
        self._column_clicked_fn = None
        self._column_delegates = None
        self._icon_provider = None
        if self._date_format_menu:
            self._date_format_menu.destroy()
            self._date_format_menu = None

    def clear_futures(self):
        """Stop and destroy all working futures"""
        for future in self._column_futures:
            if not future.done():
                future.cancel()
        self._column_futures = []

    @property
    def sort_by_column(self) -> int:
        """ Return the column index used for sorting. """
        return self._sort_by_column

    @sort_by_column.setter
    def sort_by_column(self, column_id: int):
        self._sort_by_column = column_id

    @property
    def sort_ascending(self) -> bool:
        """ Return True when sort in ascending order."""
        return self._sort_ascending

    @sort_ascending.setter
    def sort_ascending(self, value: bool):
        self._sort_ascending = value

    def _on_date_format_clicked(self):
        if not self._date_format_menu:
            self._date_format_menu = DatetimeFormatMenu(self._datetime_format_changed_fn)
        self._date_format_menu.visible = True
        self._date_format_menu.show_at(
            self._date_format_button.screen_position_x,
            self._date_format_button.screen_position_y+30
            )

    def build_header(self, column_id: int):
        """
        Build the given column.

        Args:
            column_id (int): ID of the column.
        """
        if column_id >= self._builtin_column_count:
            # Additional columns from the extensions.
            self._column_delegates[column_id - self._builtin_column_count].build_header()
            return

        def on_column_clicked(column_id):
            if self._column_clicked_fn:
                self._column_clicked_fn(column_id)

        with ui.ZStack(style=self._style):
            with ui.HStack():
                ui.Spacer(width=4)
                ui.Label(self._headers[column_id].capitalize(), height=20, style_type_name_override="TreeView.Header")
            # Invisible click area fills entire header frame
            if self._headers[column_id] == "date":
                with ui.HStack():
                    button = ui.Button(" ", height=20, style_type_name_override="TreeView.Column")
                    self._date_format_button = ui.Button(" ", width=30, height=20, style_type_name_override="TreeView.Column")
                    self._date_format_button.set_clicked_fn(lambda: self._on_date_format_clicked())
            else:
                button = ui.Button(" ", height=20, style_type_name_override="TreeView.Column")
            if column_id == self._sort_by_column:
                with ui.HStack():
                    ui.Spacer()
                    icon = (
                        f"{ICON_PATH}/{self._theme}/arrow_up.svg"
                        if self._sort_ascending
                        else f"{ICON_PATH}/{self._theme}/arrow_down.svg"
                    )
                    ui.ImageWithProvider(icon, width=30, style_type_name_override="TreeView.Column")
                    if self._headers[column_id] == "date":
                        icon_date = (
                            f"{ICON_PATH}/{self._theme}/date_format.svg"
                        )
                        ui.ImageWithProvider(icon_date, width=30, style_type_name_override="TreeView.Column")
            elif self._headers[column_id] == "date":
                with ui.HStack():
                    ui.Spacer()
                    icon_date = (
                        f"{ICON_PATH}/{self._theme}/date_format.svg"
                    )
                    ui.ImageWithProvider(icon_date, width=30, style_type_name_override="TreeView.Column")

            button.set_clicked_fn(lambda: on_column_clicked(column_id))

    def build_branch(self, model: FileBrowserModel, item: FileBrowserItem, column_id: int, level: int, expanded: bool):
        """
        Create a branch widget that opens or closes subtree.

        Args:
            model (:obj:`FileBrowserModel`): The model to build the branch with.
            item (:obj:`FileBrowserItem`): The item to build.
            column_id (int): ID of the column.
            level (int): level of the item inside the tree.
            expanded (bool): Set if the item is expanded.
        """
        def get_branch_icon(item: FileBrowserItem, expanded: bool) -> Tuple[str, str]:
            icon = "minus.svg" if expanded else "plus.svg"
            tooltip = ""
            if item.alert:
                sev, tooltip = item.alert
                if sev == ALERT_WARNING:
                    icon = "warn.svg"
                elif sev == ALERT_ERROR:
                    icon = "error.svg"
                else:
                    icon = "info.svg"
            return f"{ICON_PATH}/{self._theme}/{icon}", tooltip

        item_or_root = item or model.root
        if not item_or_root or not isinstance(item_or_root, FileBrowserItem):
            # Makes sure item has expected type, else may crash the process (See OM-34661).
            return

        if column_id == 0:
            with ui.HStack(width=20 * (level + 1), height=0):
                ui.Spacer()
                # don't create branch icon for unexpandable items
                if item_or_root.is_folder and item_or_root.expandable:
                    # Draw the +/- icon
                    icon, tooltip = get_branch_icon(item_or_root, expanded)
                    ui.ImageWithProvider(
                        icon, tooltip=tooltip, name="expand", width=10, height=10, style_type_name_override="TreeView.Icon"
                    )

    def build_widget(self, model: FileBrowserModel, item: FileBrowserItem, column_id: int, level: int, expanded: bool):
        """
        Create a widget per item.

        Args:
            model (:obj:`FileBrowserModel`): The model to build the widget with.
            item (:obj:`FileBrowserItem`): The item to build.
            column_id (int): ID of the column.
            level (int): level of the item inside the tree.
            expanded (bool): Set if the item is expanded.
        """
        item_or_root = item or model.root
        if not item_or_root or not isinstance(item_or_root, FileBrowserItem):
            # Makes sure item has expected type, else may crash the process (See OM-34661).
            return

        if column_id >= self._builtin_column_count:
            # Additional columns from the extensions.
            # Async run the delegate. The widget can be created later.
            future = self._column_delegates[column_id - self._builtin_column_count].build_widget(
                ColumnItem(item_or_root.path)
            )
            self._column_futures.append(asyncio.ensure_future(AwaitWithFrame(ui.Frame(), future)))
            return

        if self._hide_files and not item_or_root.is_folder and item_or_root.hideable:
            # Don't show file items
            return

        value_model = model.get_item_value_model(item_or_root, column_id)
        if not value_model:
            return

        style_variant = self._get_style_variant(item_or_root)
        # File Name Column
        if column_id == 0:
            def mouse_pressed_fn(item: FileBrowserItem, *args):
                if self._mouse_pressed_fn:
                    self._mouse_pressed_fn(item, *args)

            def mouse_double_clicked_fn(item: FileBrowserItem, *args):
                if self._mouse_double_clicked_fn:
                    self._mouse_double_clicked_fn(item, *args)

            with ui.HStack(height=20,
                mouse_pressed_fn=partial(mouse_pressed_fn, item_or_root),
                mouse_double_clicked_fn=partial(mouse_double_clicked_fn, item_or_root)):

                ui.Spacer(width=2)
                self._draw_item_icon(item_or_root, expanded)
                ui.Spacer(width=5)
                ui.Label(
                    value_model.get_value_as_string(),
                    tooltip=item_or_root.path if self._tooltip else "",
                    tooltip_offset=22,
                    style_type_name_override="TreeView.Item",
                    name=style_variant,
                )

        # Date Column
        elif column_id == 1:
            with ui.HStack():
                ui.Spacer(width=4)
                date_text = ""
                # OM-123876: Handle more value types to support customized delegates.(e.g.,search delegate.)
                if isinstance(value_model, datetime):
                    date_text = FileBrowserItem.datetime_as_string(value_model)
                elif hasattr(value_model, "get_value_as_string"):
                    date_text = value_model.get_value_as_string()
                elif isinstance(value_model, str):
                    date_text = value_model
                else:
                    log_warn(f"Unsupported type {type(value_model)} for Date Column: type must be one of datetime, string, or value model has get_value_as_string() method")
                ui.Label(date_text, style_type_name_override="TreeView.Item", name=style_variant)

        # Size Column
        elif column_id == 2:
            if not item_or_root.is_folder:
                with ui.HStack():
                    ui.Spacer(width=4)
                    size_text = ""
                    # OM-123876: Handle more value types to support customized delegates.(e.g.,search delegate.)
                    if hasattr(value_model, "get_value_as_string"):
                        size_text = value_model.get_value_as_string()
                    elif isinstance(value_model, str):
                        size_text = value_model
                    elif isinstance(value_model, int):
                        size_text = FileBrowserItem.size_as_string(value_model)
                    else:
                        log_warn(f"Unsupported type {type(value_model)} for Size Column: type must be one of integer, string, or value model has get_value_as_string() method")
                    ui.Label(size_text, style_type_name_override="TreeView.Item", name=style_variant)

    def set_column_delegates(self, delegates: List[AbstractColumnDelegate]):
        """Add custom columns"""
        self._column_delegates = delegates

    def _get_style_variant(self, item: FileBrowserItem):
        return "Cut" if is_path_cut(item.path) else ""

    def _draw_item_icon(self, item: FileBrowserItem, expanded: bool):
        if not item:
            return

        style_variant = self._get_style_variant(item)
        icon = item.icon
        if not icon and self._icon_provider:
            icon = self._icon_provider(item, expanded)
        if not icon:
            if item and not item.is_folder:
                icon = f"{ICON_PATH}/{self._theme}/file.svg"
            else:
                icon = (
                    f"{ICON_PATH}/{self._theme}/folder_open.svg"
                    if expanded
                    else f"{ICON_PATH}/{self._theme}/folder.svg"
                )

        with ui.ZStack(width=0):
            if icon:
                # Draw the icon
                with ui.HStack():
                    ui.Spacer(width=4)
                    ui.ImageWithProvider(icon, width=18, height=18, style_type_name_override="TreeView.Icon", name=style_variant)
            if not item.writeable:
                # Draw the lock
                lock_icon = f"{ICON_PATH}/{self._theme}/lock.svg"
                with ui.Placer(stable_size=True, offset_x=-1, offset_y=1):
                    with ui.HStack():
                        ui.ImageWithProvider(lock_icon, width=17, height=17, style_type_name_override="TreeView.Icon", name="shadow")
                        ui.Spacer()
                with ui.Placer(stable_size=True, offset_x=-2, offset_y=1):
                    with ui.HStack():
                        ui.ImageWithProvider(lock_icon, width=17, height=17, style_type_name_override="TreeView.Icon", name=style_variant)
                        ui.Spacer()
