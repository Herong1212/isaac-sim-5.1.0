# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""UI widget for navigating a filesystem."""
__all__ = ["FileBrowserWidget"]
from queue import Empty
import omni.kit.app
import carb
import omni.ui as ui
from carb import log_error, log_warn
from typing import Callable, List, Optional
from functools import partial
from . import LAYOUT_SINGLE_PANE_SLIM, LAYOUT_SINGLE_PANE_WIDE, LAYOUT_SPLIT_PANES, LAYOUT_DEFAULT, LAYOUT_SINGLE_PANE_LIST
from . import TREEVIEW_PANE, LISTVIEW_PANE
from . import ALERT_INFO, ALERT_WARNING, ALERT_ERROR

from .model import FileBrowserModel, FileBrowserItem, FileBrowserItemFactory
from .tree_view import FileBrowserTreeView
from .grid_view import FileBrowserGridView
from .zoom_bar import ZoomBar, SCALE_MAP
from .date_format_menu import DATETIME_FORMAT_SETTING
from .style import UI_STYLES, ICON_PATH
from .clipboard import get_clipboard_items, is_clipboard_cut


class FileBrowserWidget:
    """
    The basic UI widget for navigating a filesystem as a tree or grid view.
    The filesystem can either be from your local machine or the Omniverse Nucleus server.

    Args:
        title (str): Widget title. Default None.

    Keyword Args:
        layout (int): The overall layout of the window, one of: {LAYOUT_SPLIT_PANES, LAYOUT_SINGLE_PANE_SLIM,
            LAYOUT_SINGLE_PANE_WIDE, LAYOUT_DEFAULT}. Default LAYOUT_SPLIT_PANES.
        splitter_offset (int): Position of vertical splitter bar. Default 300.
        tooltip (bool): Display tooltips when hovering over items. Default False.
        allow_multi_selection (bool): Allow multiple items to be selected at once. Default True.
        mouse_pressed_fn (Callable): Function called on mouse press. Function signature:
            void mouse_pressed_fn(pane: int, button: int, key_mode: int, item: :obj:`FileBrowserItem`, x: float=0, y: float=0)
        mouse_double_clicked_fn (Callable): Function called on mouse double click. Function signature:
            void mouse_double_clicked_fn(pane: int, button: int, key_mode: int, item: :obj:`FileBrowserItem`, x: float=0, y: float=0)
        selection_changed_fn (Callable): Function called when selection changed. Function signature:
            void selection_changed_fn(pane: int, selections: list[:obj:`FileBrowserItem`])
        drop_fn (Callable): Function called to handle drag-n-drops. Function signature:
            void drop_fn(dst_item: :obj:`FileBrowserItem`, src_path: str)
        filter_fn (Callable): This user function should return True if the given tree view item is
            visible, False otherwise. Function signature: bool filter_fn(item: :obj:`FileBrowserItem`)
        show_grid_view (bool): If True, initialize the folder view to display icons. Default False.
        show_recycle_widget (bool): If True, show recycle view in the left bottom corner. Default False.
        grid_view_scale (int): Scales grid view, ranges from 0-5. Default 2.
        on_toggle_grid_view_fn (Callable): Callback after toggle grid view is executed. Default None.
        on_scale_grid_view_fn (Callable): Callback after scale grid view is executed. Default None.
        icon_provider (Callable): This callback provides an icon to replace the default one in the tree
            view. Signature: str icon_provider(item: :obj:`FileBrowserItem`, expanded: bool).
        thumbnail_provider (Callable): This callback returns the path to the item's thumbnail. If not specified,
            then a default thumbnail is used. Signature: str thumbnail_provider(item: :obj:`FileBrowserItem`).
        badges_provider (Callable): This callback provides the list of badges to layer atop the thumbnail
            in the grid view. Callback signature: List[str] badges_provider(item: :obj:`FileBrowserItem`)
        treeview_identifier (str): widget identifier for treeview, only used by tests.
        enable_zoombar (bool): Enables/disables zoombar. Default True.
    """

    def __init__(self, title: str, **kwargs):
        import carb.settings

        self._tree_view = None
        self._grid_view = None
        self._table_view = None
        self._zoom_bar = None

        self._theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        self._drop_fn = kwargs.get("drop_fn", None)
        self._filter_fn = kwargs.get("filter_fn", None)
        # Create model for tree view
        self._models = self.create_treeview_model(name=title, drop_fn=self._drop_fn, filter_fn=self._filter_fn)
        # Create the model for the list view
        self._listview_model = FileBrowserModel(drop_fn=self._drop_fn, filter_fn=self._filter_fn)
        # OM-70157: Added this selections for listview here, because we cannot aggregate and re-apply selection from
        #  grid view/list view if the switch grid view scale and toggle happened within one frame (i.e. if the user
        #  is dragging the zoombar from one end to another within one frame), because the grid view items are built
        #  one frame delay, the selection will be lost from the scale and switch; thus this is recorded at a higher
        #  level on this widget, as a source of truth for selections for both list view and grid view;
        self._listview_selections = []
        self._currently_visible_model = None

        self._style = UI_STYLES[self._theme]
        self._layout = kwargs.get("layout", LAYOUT_DEFAULT)
        self._splitter_offset = kwargs.get("splitter_offset", 300)
        self._tooltip = kwargs.get("tooltip", False)
        self._tree_root_visible = kwargs.get("tree_root_visible", True)
        self._allow_multi_selection = kwargs.get("allow_multi_selection", True)
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._mouse_double_clicked_fn = kwargs.get("mouse_double_clicked_fn", None)
        self._selection_changed_fn = kwargs.get("selection_changed_fn", None)
        self._show_grid_view = kwargs.get("show_grid_view", False)
        self._grid_view_scale = kwargs.get("grid_view_scale", 2)
        # OM-66270: Add callback to record show grid view settings in between sessions
        self._on_toggle_grid_view_fn = kwargs.get("on_toggle_grid_view_fn", None)
        self._on_scale_grid_view_fn = kwargs.get("on_scale_grid_view_fn", None)
        self._icon_provider = kwargs.get("icon_provider", None)
        self._thumbnail_provider = kwargs.get("thumbnail_provider", None)
        self._badges_provider = kwargs.get("badges_provider", None)
        self._treeview_identifier = kwargs.get('treeview_identifier', None)
        self._enable_zoombar = kwargs.get("enable_zoombar", True)
        self._datetime_format_updated_subscription = None
        self._notification_frame = None
        self._build_ui()

    @property
    def show_udim_sequence(self):
        """ Return True if the list model has UDIM sequence visible. """
        return self._listview_model.show_udim_sequence

    @show_udim_sequence.setter
    def show_udim_sequence(self, value: bool):
        self._listview_model.show_udim_sequence = value

    def create_treeview_model(self, name: str, drop_fn: Callable, filter_fn: Callable) -> FileBrowserModel:
        """
        Create the model for treeview. Override this method to create a custom model for treeview.

        Args:
            name (str): Name of the model.
            drop_fn (Callable): Drop function.
            filter_fn (Callable): Filter function.

        Returns:
            :obj:`FileBrowserModel`: The model for treeview.    
        """
        model = FileBrowserModel(name=name, drop_fn=drop_fn, filter_fn=filter_fn)
        model.root.icon = f"{ICON_PATH}/{self._theme}/cloud.svg"
        return model

    def _build_ui(self):
        if self._layout in [LAYOUT_SPLIT_PANES, LAYOUT_SINGLE_PANE_LIST, LAYOUT_DEFAULT]:
            self._tree_view = self._build_split_panes_view()
        else:
            slim_view = self._layout == LAYOUT_SINGLE_PANE_SLIM
            self._tree_view = self._build_tree_view(
                self._models,
                slim_view=slim_view,
                selection_changed_fn=partial(self._on_selection_changed, TREEVIEW_PANE),
            )

        def on_datetime_format_changed(_: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
            if event_type == carb.settings.ChangeEventType.CHANGED:
                self.refresh_ui(listview_only=True)

        self._datetime_format_updated_subscription = omni.kit.app.SettingChangeSubscription(
            DATETIME_FORMAT_SETTING, on_datetime_format_changed)

    def _build_split_panes_view(self) -> FileBrowserTreeView:
        show_grid_view = self._show_grid_view
        use_default_style = carb.settings.get_settings().get_as_string("/persistent/app/window/useDefaultStyle") or False
        if use_default_style:
            self._style = {}
        with ui.HStack(style=self._style):
            with ui.ZStack(width=0, visible=self._layout != LAYOUT_SINGLE_PANE_LIST):
                # Create navigation view as side pane
                self._models.single_column = True
                with ui.HStack():
                    with ui.VStack():
                        tree_view = self._build_tree_view(
                            self._models,
                            header_visible=False,
                            files_visible=False,
                            slim_view=True,
                            selection_changed_fn=partial(self._on_selection_changed, TREEVIEW_PANE),
                        )

                    ui.Spacer(width=2)

                with ui.Placer(offset_x=self._splitter_offset, draggable=True, drag_axis=ui.Axis.X):
                    ui.Rectangle(width=4, style_type_name_override="Splitter")

            with ui.ZStack():
                self._grid_view = self._build_grid_view(self._listview_model)
                self._table_view = self._build_table_view(self._listview_model)
                if self._enable_zoombar:
                    with ui.VStack():
                        ui.Spacer()
                        self._zoom_bar = ZoomBar(
                            show_grid_view=self._show_grid_view,
                            grid_view_scale=self._grid_view_scale,
                            on_toggle_grid_view_fn=self.toggle_grid_view,
                            on_scale_grid_view_fn=self.scale_grid_view
                        )
                        ui.Spacer(height=2)
                # OM-49484: Add a notification frame to list view stack, that could be used for showing notification
                self._notification_frame = ui.Frame()

        self.toggle_grid_view(show_grid_view)
        return tree_view

    def _build_tree_view(
        self,
        model: FileBrowserModel,
        header_visible: bool = True,
        files_visible: bool = True,
        slim_view: bool = True,
        selection_changed_fn: Callable = None,
    ) -> FileBrowserTreeView:

        if slim_view:
            model._single_column = True

        with ui.ZStack(style=self._style):
            ui.Rectangle(style_type_name_override="TreeView")
            view = FileBrowserTreeView(
                model,
                header_visible=header_visible,
                files_visible=files_visible,
                tooltip=self._tooltip,
                root_visible=self._tree_root_visible,
                allow_multi_selection=self._allow_multi_selection,
                mouse_pressed_fn=partial(self._on_mouse_pressed, TREEVIEW_PANE),
                mouse_double_clicked_fn=partial(self._on_mouse_double_clicked, TREEVIEW_PANE),
                selection_changed_fn=selection_changed_fn,
                icon_provider=self._icon_provider,
                treeview_identifier=f"{self._treeview_identifier}_folder_view",
            )
            view.build_ui()
        return view

    def _build_table_view(self, model: FileBrowserModel) -> FileBrowserTreeView:
        # Create detail view as table view
        view = FileBrowserTreeView(
            model,
            root_visible=False,
            tooltip=self._tooltip,
            allow_multi_selection=self._allow_multi_selection,
            mouse_pressed_fn=partial(self._on_mouse_pressed, LISTVIEW_PANE),
            mouse_double_clicked_fn=partial(self._on_mouse_double_clicked, LISTVIEW_PANE),
            selection_changed_fn=partial(self._on_selection_changed, LISTVIEW_PANE),
            icon_provider=self._icon_provider,
            treeview_identifier=self._treeview_identifier,
        )
        view.build_ui()
        return view

    def _build_grid_view(self, model: FileBrowserModel) -> FileBrowserGridView:
        # Create detail view as table view
        view = FileBrowserGridView(
            model,
            root_visible=False,
            tooltip=self._tooltip,
            allow_multi_selection=self._allow_multi_selection,
            mouse_pressed_fn=partial(self._on_mouse_pressed, LISTVIEW_PANE),
            mouse_double_clicked_fn=partial(self._on_mouse_double_clicked, LISTVIEW_PANE),
            selection_changed_fn=partial(self._on_selection_changed, LISTVIEW_PANE),
            drop_fn=self._drop_fn,
            thumbnail_provider=self._thumbnail_provider,
            badges_provider=self._badges_provider,
            treeview_identifier=f"{self._treeview_identifier}_grid_view",
        )
        view.build_ui()
        return view

    def _on_mouse_pressed(self, pane: int, button: int, key_mod: int, item: FileBrowserItem, x: float = 0, y: float = 0):
        if self._mouse_pressed_fn:
            self._mouse_pressed_fn(pane, button, key_mod, item, x=x, y=y)

    def _on_mouse_double_clicked(self, pane: int, button: int, key_mod: int, item: FileBrowserItem, x: float = 0, y: float = 0):
        if self._mouse_double_clicked_fn:
            self._mouse_double_clicked_fn(pane, button, key_mod, item, x=x, y=y)
        if item and item.is_folder:
            self._tree_view.select_and_center(item)

    def _on_selection_changed(self, pane: int, selected: List[FileBrowserItem]):
        if self._selection_changed_fn:
            self._selection_changed_fn(pane, selected)
        if pane == TREEVIEW_PANE and selected:
            item = selected[-1]
            if item.populated:
                # If entering an already populated folder, sync up to any folder changes that may
                # have been missed.
                self._models.sync_up_item_changes(item)
            # Refresh the folder in the list view
            self._listview_model.root = item
            self.show_model(self._listview_model)
            # Clear out list view selections
            self._listview_selections = []
            # Finally, set folder to auto-refresh
            self._auto_refresh_folder(item)
        if pane == LISTVIEW_PANE:
            # update list view selection on list view model
            self._listview_selections = selected
            # OM-103559: list view pane also should auto sync up and list item.
            if selected:
                item = selected[-1]
                if item and item.populated:
                    # If entering an already populated folder, sync up to any folder changes that may
                    # have been missed.
                    self._listview_model.sync_up_item_changes(item)
                if item:
                    self._listview_model.auto_refresh_item(item)

    def _auto_refresh_folder(self, item: FileBrowserItem):
        if item:
            self._models.auto_refresh_item(item)
            self._models.add_item_changed_fn(lambda model, item: self.refresh_ui(item, listview_only=True))

    def get_root(self, pane: int = None) -> FileBrowserItem:
        """ Get the root item of the treeview by pane. """
        if not pane:
            return self._models.root
        elif pane == TREEVIEW_PANE:
            return self._tree_view.model.root
        elif pane == LISTVIEW_PANE:
            return self._listview_model.root
        return None

    def toggle_grid_view(self, show_grid_view: bool):
        """ Toggle on/of grid view. """
        current_selections = self.get_selections(pane=LISTVIEW_PANE)
        if not (self._grid_view and self._table_view):
            return
        if show_grid_view:
            self._grid_view.visible = True
            self._table_view.visible = False
        else:
            self._grid_view.visible = False
            self._table_view.visible = True

        # OM-70157: maintain current selection when toggling between grid view and list view
        self.set_selections(current_selections, pane=LISTVIEW_PANE)

        # OM-86768: refresh UI if cut clipboard is not empty to maintain the cut style
        if is_clipboard_cut() and get_clipboard_items():
            self.refresh_ui(listview_only=True)

        self._show_grid_view = show_grid_view

        # OM-66270: Record show grid view settings in between sessions
        if self._on_toggle_grid_view_fn:
            self._on_toggle_grid_view_fn(show_grid_view)

    def hide_notification(self):
        """
        Hide the notification frame.
        """
        self._notification_frame.visible = False
        self._grid_view.visible = self.show_grid_view
        self._table_view.visible = not self.show_grid_view

    def show_notification(self):
        """
        Show the notification frame.
        """
        self._notification_frame.visible = True
        self._grid_view.visible = False
        self._table_view.visible = False

    @property
    def show_grid_view(self):
        """ Return True if grid view is visible. """
        return self._show_grid_view

    def scale_grid_view(self, scale: float):
        """ Set the scale of item inside grid view. """
        if not self._grid_view:
            return
        if scale < 0.5:
            self.toggle_grid_view(False)
        else:
            self.toggle_grid_view(True)
            self._grid_view.scale_view(scale)
            self._grid_view.build_ui(restore_selections=self._listview_selections)

        # OM-66270: Record grid view scale settings in between sessions
        if self._on_scale_grid_view_fn:
            scale_level = None
            # infer scale level from SCALE_MAP
            if scale in SCALE_MAP.values():
                scale_level = list(SCALE_MAP.keys())[list(SCALE_MAP.values()).index(scale)]
            self._on_scale_grid_view_fn(scale_level)

    def create_grouping_item(self, name: str, path: str, parent: FileBrowserItem = None) -> FileBrowserItem:
        """
        Create a folder item at the given path and add it as child to the tree view root model or the given parent item.

        Args:
            name (str): name of the item.
            path (str): path of the item.
            parent (str): If set, add the item as a child to this item instead of the tree view root model.
        """
        child = FileBrowserItemFactory.create_group_item(name, path)
        if child:
            item = parent or self._models.root
            item.add_child(child)
            self._models._item_changed(parent)
        return child

    def add_model_as_subtree(self, model: FileBrowserModel, parent: FileBrowserItem = None):
        """
        Add a new model as the subtree of the tree view root model or the given parent item.

        Args:
            model (:obj:`FileBrowserModel`): the model to add.
            parent (:obj:`FileBrowserItem`): If set, add the model as a child to this item instead of the tree view root model.
        """
        if model:
            parent = parent or self._models.root
            parent.add_child(model.root)
            # TODO: Remove it
            self.refresh_ui()

    def delete_child_by_name(self, item_name: str, parent: FileBrowserItem = None):
        """
        Delete an item from the tree view root model or the given parent item.

        Args:
            item_name (str): the item name to remove.
            parent (:obj:`FileBrowserItem`): If set, remove the item from this item instead of the tree view root model.
        """
        if item_name:
            parent = parent or self._models.root
            parent.del_child(item_name)
            # TODO: Remove it
            self.refresh_ui()

    def delete_child(self, item: FileBrowserItem, parent: FileBrowserItem = None):
        """
        Delete an item from the tree view root model or the given parent item.

        Args:
            model (:obj:`FileBrowserModel`): the item to remove.
            parent (:obj:`FileBrowserItem`): If set, remove the item from this item instead of the tree view root model.
        """
        if item:
            self.delete_child_by_name(item.name, parent)

    def link_views(self, src_widget: object):
        """
        Link this widget to the given widget, i.e. the 2 widgets will therafter display the same
        models but not necessarily share the same view.

        Args:
            src_widget (:obj:`FilePickerWidget`): The source widget.

        """
        if self._tree_view and src_widget._tree_view:
            src_model = src_widget._tree_view.model
            if src_model:
                self._tree_view.set_root(src_model.root)

    def set_item_alert(self, item: FileBrowserItem, alert_level: int, msg: str):
        """
        Set the alert message of the given item.

        Args:
            item (:obj:`FileBrowserItem`): Item to set alert.
            alert_level (int): level of alert.
            msg (str): message to alert.
        """
        if item:
            item.alert = (alert_level, msg)
            self.refresh_ui(item)

    def set_item_info(self, item: FileBrowserItem, msg: str):
        """
        Set the info message of the given item.

        Args:
            item (:obj:`FileBrowserItem`): Item to set alert.
            alert_level (int): level of alert.
            msg (str): message to alert.
        """
        self.set_item_alert(item, ALERT_INFO, msg)

    def set_item_warning(self, item: FileBrowserItem, msg: str):
        """
        Set the warning message of the given item.

        Args:
            item (:obj:`FileBrowserItem`): Item to set alert.
            alert_level (int): level of alert.
            msg (str): message to alert.
        """
        self.set_item_alert(item, ALERT_WARNING, msg)

    def set_item_error(self, item: FileBrowserItem, msg: str):
        """
        Set the error message of the given item.

        Args:
            item (:obj:`FileBrowserItem`): Item to set alert.
            alert_level (int): level of alert.
            msg (str): message to alert.
        """
        self.set_item_alert(item, ALERT_ERROR, msg)

    def clear_item_alert(self, item: FileBrowserItem):
        """
        Clear the alert of the given item.

        Args:
            item (:obj:`FileBrowserItem`): Item to clear the alert.
        """
        if item:
            item.alert = None
            self.refresh_ui(item)

    def refresh_ui(self, item: FileBrowserItem = None, listview_only: bool = False):
        """
        Redraw the subtree rooted at the given item. If item is None, then redraws entire tree.

        Args:
            item (:obj:`FileBrowserItem`): Root of subtree to redraw. Default None, i.e. root.

        """
        if not listview_only:
            if self._tree_view:
                self._tree_view.refresh_ui(item)
        if self._grid_view:
            self._grid_view.refresh_ui(item)
        if self._table_view:
            self._table_view.refresh_ui()

    def set_selections(self, selections: List[FileBrowserItem], pane: int = TREEVIEW_PANE):
        """
        Selected given items in given pane.

        ARGS:
            selections (list[:obj:`FileBrowserItem`]): list of selections.
            pane (int): One of TREEVIEW_PANE, LISTVIEW_PANE, or None for both. Default None.

        """
        if not pane or pane == TREEVIEW_PANE:
            if selections:
                self._tree_view.tree_view.selection = selections
            else:
                # Note: OM-23294 - Segfaults when selections cleared
                # self._tree_view.tree_view.clear_selection()
                pass
        if not pane or pane == LISTVIEW_PANE:
            if selections:
                self._table_view.tree_view.selection = selections
            else:
                # Note: OM-23294 - Segfaults when selections cleared
                self._table_view.tree_view.clear_selection()
                pass
            if self._grid_view:
                self._grid_view.selections = selections
            self._listview_selections = selections

    def get_selected_item(self, pane: int = TREEVIEW_PANE) -> FileBrowserItem:
        """
        Return last of selected item from the specified pane.

        ARGS:
            pane (int): One of TREEVIEW_PANE, LISTVIEW_PANE. Returns the union if None is specified.

        Returns:
            `FileBrowserItem` or None
        """
        selections = self.get_selections(pane)
        return selections[-1] if len(selections) > 0 else None

    def get_selections(self, pane: int = TREEVIEW_PANE) -> List[FileBrowserItem]:
        """
        Return list of selected items from the specified pane.

        ARGS:
            pane (int): One of TREEVIEW_PANE, LISTVIEW_PANE. Returns the union if None is specified.

        Returns:
            list[:obj:`FileBrowserItem`]
        """
        if not pane or pane == TREEVIEW_PANE:
            selections = self._tree_view.selections
        else:
            selections = []
        if not pane or pane == LISTVIEW_PANE:
            selections.extend(self._listview_selections)

        # Ensure selections are unique
        return list(set(selections))

    def select_and_center(self, selection: FileBrowserItem, pane: int = TREEVIEW_PANE):
        """
        Select and centers the tree view on the given item, expanding the tree if needed.

        Args:
            selection (:obj:`FileBrowserItem`): The selected item.
            pane (int): One of TREEVIEW_PANE, LISTVIEW_PANE.

        """
        if not pane or pane == TREEVIEW_PANE:
            self._tree_view.select_and_center(selection)
            if self._grid_view:
                self._grid_view.scroll_top()
            if self._table_view:
                self._table_view.scroll_top()
            # clear out listview model selections when selecting treeview items
            self._listview_selections = []
        if not pane or pane == LISTVIEW_PANE:
            if self._grid_view.visible:
                self._grid_view.select_and_center(selection)
            if self._table_view.visible:
                self._table_view.select_and_center(selection)
            self._listview_selections = [selection]

    def set_expanded(self, item: FileBrowserItem, expanded: bool, recursive: bool = False):
        """
        Set the expansion state of the given item.

        Args:
            item (:obj:`FileBrowserItem`): The item to effect.
            expanded (bool): True to expand, False to collapse.
            recursive (bool): Apply state recursively to descendent nodes. Default False.

        """
        if self._tree_view:
            self._tree_view.set_expanded(item, expanded, recursive)

    def show_model(self, model: FileBrowserModel):
        """
        Show the given model.
        """
        if model:
            new_model = model
            new_model.copy_presets(self._listview_model)
        else:
            new_model = self._listview_model

        if new_model != self._currently_visible_model:
            # Hack to remove model to avoid memory leaks
            # TODO: Find out how to create a model with no circular dependencies
            if self._currently_visible_model and self._currently_visible_model != self._listview_model:
                self._currently_visible_model.destroy()
            self._currently_visible_model = new_model

        if self._grid_view:
            self._grid_view.model = self._currently_visible_model
        if self._table_view:
            self._table_view.model = self._currently_visible_model

    def destroy(self):
        """
        Destructor. Called by extension before destroying this object. It doesn't happen automatically.
        Without this hot reloading doesn't work.

        """
        if self._tree_view:
            self._tree_view.destroy()
            self._tree_view = None
        if self._grid_view:
            self._grid_view.destroy()
            self._grid_view = None
        if self._table_view:
            self._table_view.destroy()
            self._table_view = None
        if self._listview_model:
            self._listview_model.destroy()
            self._listview_model = None
        self._listview_selections.clear()
        if self._notification_frame:
            self._notification_frame = None
        if self._zoom_bar:
            self._zoom_bar.destroy()
            self._zoom_bar = None
        if self._models:
            self._models.destroy()
            self._models = None
        self._currently_visible_model = None

        self._style = None
        self._drop_fn = None
        self._filter_fn = None
        self._mouse_pressed_fn = None
        self._mouse_double_clicked_fn = None
        self._selection_changed_fn = None
        self._icon_provider = None
        self._thumbnail_provider = None
        self._badges_provider = None
        self._datetime_format_updated_subscription = None
