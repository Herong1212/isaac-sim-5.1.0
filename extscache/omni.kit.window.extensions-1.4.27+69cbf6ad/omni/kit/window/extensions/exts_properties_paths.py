# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides a UI for managing extension paths with functionalities to add, remove, clean cache, and update Git-managed paths."""

__all__ = ["PathItem", "PathsModel", "EditableDelegate", "ExtsPathsWidget"]

import omni.kit.app
import omni.ui as ui

from .styles import get_style
from .utils import cleanup_folder, copy_text, get_extpath_git_ext

PATH_TYPE_TO_LABEL = {
    omni.ext.ExtensionPathType.COLLECTION: "[dir]",
    omni.ext.ExtensionPathType.COLLECTION_USER: "[user dir]",
    omni.ext.ExtensionPathType.COLLECTION_CACHE: "[cache dir]",
    omni.ext.ExtensionPathType.DIRECT_PATH: "[ext]",
    omni.ext.ExtensionPathType.EXT_1_FOLDER: "[exts 1.0]",
}

PATH_TYPE_TO_COLOR = {
    omni.ext.ExtensionPathType.COLLECTION: 0xFF29A9A9,
    omni.ext.ExtensionPathType.COLLECTION_USER: 0xFF1989A9,
    omni.ext.ExtensionPathType.COLLECTION_CACHE: 0xFFA9A929,
    omni.ext.ExtensionPathType.DIRECT_PATH: 0xFF29A929,
    omni.ext.ExtensionPathType.EXT_1_FOLDER: 0xFF2929A9,
}

PATHS_COLUMNS = ["", "name", "type", "edit"]


class PathItem(ui.AbstractItem):
    """A class representing a path item in a filesystem-like structure.

    This class encapsulates information about a path, including its type and whether it should be accompanied by a dummy element. It's used to model a single entry in a hierarchical file path representation.

    Args:
        path (str): The filesystem path represented by the item.
        path_type (:obj:`omni.ext.ExtensionPathType`): The type of path based on predefined constants.
        add_dummy (bool): Flag to indicate whether a dummy placeholder should be added."""

    def __init__(self, path, path_type: omni.ext.ExtensionPathType, add_dummy=False):
        """Initializes a new instance of PathItem with the provided path, path type, and an optional dummy flag."""
        super().__init__()
        self.path_model = ui.SimpleStringModel(path)
        self.type = path_type
        self.is_user = path_type == omni.ext.ExtensionPathType.COLLECTION_USER
        self.is_cache = path_type == omni.ext.ExtensionPathType.COLLECTION_CACHE
        self.add_dummy = add_dummy
        git_ext = get_extpath_git_ext()
        if git_ext and git_ext.is_git_path(path):
            self.is_git = True
            self.local_path = git_ext.get_local_path(path)
        else:
            self.is_git = False
            self.local_path = path


class PathsModel(ui.AbstractItemModel):
    """A model for managing and interacting with filesystem paths within a user interface.

    This model is designed to work with a UI framework to display and manipulate paths related to extensions and their respective types, such as collections, user directories, cache directories, and direct paths. It supports operations like adding new paths, removing existing ones, cleaning cache directories, and updating git repositories. The model holds a list of path items and provides methods to perform actions on these items.
    """

    def __init__(self):
        """Initializes the model for managing paths in the application."""
        super().__init__()
        self._ext_manager = omni.kit.app.get_app().get_extension_manager()
        self._children = []
        self._load()
        self._add_dummy = PathItem("", omni.ext.ExtensionPathType.COLLECTION_USER, add_dummy=True)

    def destroy(self):
        """Clears all the children from the model."""
        self._children = []

    def get_item_children(self, item):
        """Returns all the children for the given item.

        Args:
            item: The item to retrieve children for."""
        if item is not None:
            return []

        return self._children + [self._add_dummy]

    def get_item_value_model_count(self, item):
        """Returns the number of columns in the model.

        Args:
            item: The item for which to count the value models."""
        return 4

    def get_item_value_model(self, item, column_id):
        """Retrieves the value model for a given item and column.

        Args:
            item: The item to retrieve the value model for.
            column_id: The column ID for which to retrieve the value model."""
        if column_id == 1:
            return item.path_model
        return None

    def _load(self):
        self._children = []

        folders = self._ext_manager.get_folders()
        for folder in folders:
            path = folder["path"]
            path_type = folder["type"]
            item = PathItem(path, path_type)
            self._children.append(item)

        self._item_changed(None)

    def add_empty(self):
        """Adds an empty path item to the model."""
        self._children.append(PathItem("", omni.ext.ExtensionPathType.COLLECTION_USER))
        self._item_changed(None)

    def remove_item(self, item):
        """Removes a specified item from the model.

        Args:
            item: The item to be removed."""
        self._children.remove(item)
        self.save()
        self._item_changed(None)

    def clean_cache(self, item):
        """Cleans the cache for a specified item.

        Args:
            item: The item whose cache to clean."""
        path = item.local_path
        print(f"Cleaning up cache: {path}")
        cleanup_folder(path)

    def update_git(self, item):
        """Updates the GIT path for a specified item.

        Args:
            item: The item whose GIT path to update."""
        path = item.path_model.as_string
        get_extpath_git_ext().update_git_path(path)

    def save(self):
        """Saves the current paths to the extension manager."""
        current = [
            folder["path"]
            for folder in self._ext_manager.get_folders()
            if folder["type"] == omni.ext.ExtensionPathType.COLLECTION_USER
        ]
        paths = [c.path_model.as_string for c in self._children if c.is_user]
        if current != paths:
            # remove and add again. We can only apply diff here, but then it is impossible to preserve the order.
            for p in current:
                self._ext_manager.remove_path(p)
            for p in paths:
                self._ext_manager.add_path(p, omni.ext.ExtensionPathType.COLLECTION_USER)

        get_extpath_git_ext.cache_clear()


class EditableDelegate(ui.AbstractItemDelegate):
    """A delegate class for handling editable UI elements within a tree view structure.

    This delegate is responsible for managing interactive UI components such as buttons and text fields within a tree view. It enables actions such as opening file paths in the OS file explorer, editing item names directly within the UI, and triggering context menus for additional options like copying text. It also supports special functionalities for user-defined paths, cache management, and git repository updates.

    The delegate utilizes a context menu for copy actions and dynamically updates the UI based on user interactions, such as double-clicking to edit names or clicking buttons to add, remove, or clean items. It plays a crucial role in managing the appearance and functionality of editable items within the tree view, ensuring a responsive and intuitive user experience.
    """

    def __init__(self):
        """Initializes the EditableDelegate instance."""
        super().__init__()
        self._subscription = None
        self._context_menu = ui.Menu("Context menu")

    def destroy(self):
        """Cleans up resources and references held by the delegate instance."""
        self._subscription = None
        self._context_menu = None

    def _show_copy_context_menu(self, x, y, button, modifier, text):
        if button != 1:
            return

        self._context_menu.clear()
        with self._context_menu:
            ui.MenuItem("Copy", triggered_fn=lambda: copy_text(text))
        self._context_menu.show()

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per column per item

        Args:
            model (:obj:`ui.AbstractItemModel`): The model associated with the tree view.
            item (:obj:`ui.AbstractItem`): The item in the model for which to build the widget.
            column_id (int): The column index where the widget will be placed.
            level (int): The level of indentation for the item in the tree view.
            expanded (bool): Whether the item's children are currently expanded."""
        with ui.HStack(width=20):
            if column_id == 0 and not item.add_dummy:

                def open_path(item_=item):
                    # Import it here instead of on the file root because it has long import time.
                    path = item_.local_path
                    if path:
                        import webbrowser

                        webbrowser.open(path)

                ui.Button("open", width=0, clicked_fn=open_path, tooltip="Open path using OS file explorer.")
            elif column_id == 1 and not item.add_dummy:
                value_model = model.get_item_value_model(item, column_id)
                stack = ui.ZStack(height=20)
                with stack:
                    label = ui.Label(value_model.as_string, width=500, name=("config" if item.is_user else "builtin"))
                    field = ui.StringField(value_model, visible=False)

                    # Start editing when double clicked
                    stack.set_mouse_double_clicked_fn(
                        lambda x, y, b, _, f=field, l=label, m=model, i=item: self.on_double_click(  # noqa: E741
                            b, f, l, m, i
                        )
                    )
                    # Right click is copy menu
                    stack.set_mouse_pressed_fn(
                        lambda x, y, b, m, t=value_model.as_string: self._show_copy_context_menu(x, y, b, m, t)
                    )
            elif column_id == 2 and not item.add_dummy:
                ui.Label(PATH_TYPE_TO_LABEL[item.type], style={"color": PATH_TYPE_TO_COLOR[item.type]})
            elif column_id == 3:
                if item.is_user:

                    def on_click(item_=item):
                        if item.add_dummy:
                            model.add_empty()
                        else:
                            model.remove_item(item_)

                    ui.Spacer(width=10)
                    ui.Button(
                        name=("add" if item.add_dummy else "remove"),
                        style_type_name_override="ItemButton",
                        width=20,
                        height=20,
                        clicked_fn=on_click,
                    )
                    ui.Spacer(width=4)
                elif item.is_cache:

                    def clean_cache(item_=item):
                        model.clean_cache(item_)

                    ui.Spacer(width=10)
                    ui.Button(
                        name="clean",
                        style_type_name_override="ItemButton",
                        width=20,
                        height=20,
                        clicked_fn=clean_cache,
                    )
                    ui.Spacer(width=4)

                if item.is_git:

                    def update_git(item_=item):
                        model.update_git(item_)

                    ui.Button(
                        name="update",
                        style_type_name_override="ItemButton",
                        width=20,
                        height=20,
                        clicked_fn=update_git,
                        identifier="update_button",
                    )
                ui.Spacer()

    def on_double_click(self, button, field, label, model, item):
        """Called when the user double-clicked the item in TreeView

        Args:
            button (int): The mouse button clicked (0 for left-click).
            field (:obj:`ui.StringField`): The field to be edited on double-click.
            label (:obj:`ui.Label`): The label associated with the item.
            model (:obj:`ui.AbstractItemModel`): The model associated with the tree view.
            item (:obj:`ui.AbstractItem`): The item that was double-clicked."""
        if button != 0:
            return

        if item.add_dummy:
            return
        if not item.is_user:
            copy_text(field.model.as_string)
            return

        # Make Field visible when double clicked
        field.visible = True
        field.focus_keyboard()
        # When editing is finished (enter pressed of mouse clicked outside of the viewport)
        self._subscription = field.model.subscribe_end_edit_fn(
            lambda m, f=field, l=label, md=model: self.on_end_edit(m.as_string, f, l, md)  # noqa: E741
        )

    def on_end_edit(self, text, field, label, model):
        """Called when the user is editing the item and pressed Enter or clicked outside of the item

        Args:
            text (str): The new text entered into the field.
            field (:obj:`ui.StringField`): The text field that was being edited.
            label (:obj:`ui.Label`): The label associated with the item.
            model (:obj:`ui.AbstractItemModel`): The model to update with new text."""
        field.visible = False
        label.text = text
        self._subscription = None
        if text:
            model.save()

    def build_header(self, column_id):
        """Builds the header for a specified column in the tree view.

        Args:
            column_id (int): The column index for which to build the header."""
        with ui.HStack():
            ui.Spacer(width=10)
            ui.Label(PATHS_COLUMNS[column_id], name="header")


class ExtsPathsWidget:
    """A widget that displays and manages paths related to extension directories.

    This widget uses a tree view to list and edit extension paths. It allows users to open paths in the OS file explorer, copy paths to the clipboard, add new path entries, remove existing ones, clean cache directories, and update Git-managed paths. Changes to paths are saved persistently. The widget supports different path types, each with its own label and color coding.
    """

    def __init__(self):
        """Initializes the ExtsPathsWidget with a model and delegate, and creates the UI components."""
        self._model = PathsModel()
        self._delegate = EditableDelegate()

        with ui.VStack(style=get_style(self)):
            ui.Spacer(height=20)
            with ui.ScrollingFrame(
                height=400,
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                style_type_name_override="TreeView",
            ):
                tree_view = ui.TreeView(
                    self._model,
                    delegate=self._delegate,
                    root_visible=False,
                    header_visible=True,
                )
                tree_view.column_widths = [ui.Pixel(46), ui.Fraction(1), ui.Pixel(70), ui.Pixel(60)]

            ui.Spacer(height=10)

    def destroy(self):
        """Cleans up the resources used by the ExtsPathsWidget."""
        self._model.destroy()
        self._model = None
        self._delegate.destroy()
        self._delegate = None
