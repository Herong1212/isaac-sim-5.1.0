# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
import weakref
import omni.kit.app
import omni.ui as ui
import carb

from typing import List, Callable
from . import LAYOUT_SLIM_VIEW, LAYOUT_TABLE_VIEW, LAYOUT_DEFAULT
from .checkpoints_model import CheckpointModel, CheckpointItem
from .table_view import CheckpointTableView
from .slim_view import CheckpointSlimView
from .context_menu import ContextMenu
from .style import get_style


class CheckpointWidget:
    """A widget for displaying and managing checkpoints for a file using Omni UI.

    This class constructs a visual widget that integrates a checkpoint model to list and manage file checkpoints. It supports different layout modes and provides callbacks for selection, mouse press, and double-click events. The widget also displays a context menu with customizable options based on the current state of checkpointing for a file.

    Args:
        url (str): The URL of the file to retrieve checkpoints from.
        show_none_entry (bool): Whether to include a dummy entry indicating no checkpoint is selected.

    Keyword Args:
        layout (int): Layout style to use. Defaults to a default layout if not provided.
        on_list_checkpoint_fn (Callable): Callback function to invoke after listing checkpoints to handle selection updates.
        mouse_pressed_fn (Callable): Callback function to execute on mouse press events for a checkpoint item.
        mouse_double_clicked_fn (Callable): Callback function to execute on mouse double-click events for a checkpoint item.
    """

    def __init__(self, url: str = "", show_none_entry=False, **kwargs):
        """Initializes a CheckpointWidget instance. Builds UI and sets up model configuration."""
        self._model = CheckpointModel(show_none_entry)
        self._model.set_on_list_checkpoint_fn(self._on_list_checkpoint)
        self._view = None
        self._checkpoint_stack = None
        self._notify_stack = None
        self._labels = {}
        self._context_menu = None

        self._theme = carb.settings.get_settings().get("/persistent/app/window/uiStyle") or "NvidiaDark"
        self._layout = kwargs.get("layout", LAYOUT_DEFAULT)
        self._on_selection_changed_fn = []
        self._on_list_checkpoint_fn = kwargs.get("on_list_checkpoint_fn", None)
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._mouse_double_clicked_fn = kwargs.get("mouse_double_clicked_fn", None)
        self._build_ui()
        self.set_url(url)

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Releases resources and destroys widget components."""
        self._view = None
        self._labels = None
        self._checkpoint_stack = None
        self._notify_stack = None
        if self._model:
            self._model.destroy()
            self._model = None
        if self._context_menu:
            self._context_menu.destroy()
            self._content_menu = None
        self._on_selection_changed_fn.clear()

    def set_mouse_pressed_fn(self, mouse_pressed_fn: Callable):
        """Sets the callback for mouse pressed event.

        Args:
            mouse_pressed_fn (Callable): Function invoked on mouse press event.
        """
        self._mouse_pressed_fn = mouse_pressed_fn

    def set_mouse_double_clicked_fn(self, mouse_double_clicked_fn: Callable):
        """Sets the callback for mouse double clicked event.

        Args:
            mouse_double_clicked_fn (Callable): Function invoked on double click event.
        """
        self._mouse_double_clicked_fn = mouse_double_clicked_fn

    def set_multi_select(self, state: bool):
        """Sets multi-select mode for the checkpoint model.

        Args:
            state (bool): Boolean value indicating multi-select state.
        """
        self._model.set_multi_select(state)

    def set_url(self, url: str):
        """Updates the URL in the checkpoint model.

        Args:
            url (str): URL to set for the model.
        """
        self._model.set_url(url)

    def set_search(self, keywords):
        """Performs search on checkpoints using provided keywords.

        Args:
            keywords (str): Keywords used for filtering checkpoints.
        """
        self._model.set_search(keywords)

    def add_on_selection_changed_fn(self, fn):
        """Registers a callback to handle selection changes.

        Args:
            fn (Callable): Callback function executed when selection changes.
        """
        self._on_selection_changed_fn.append(fn)

    def set_on_list_checkpoint_fn(self, fn):
        """Assigns a callback for listing checkpoints.

        Args:
            fn (Callable): Callback for when the checkpoint list is updated.
        """
        self._on_list_checkpoint_fn = fn

    def empty(self):
        """Checks if the checkpoint model is empty.

        Returns:
            bool: True if no checkpoints exist, False otherwise.
        """
        return self._model.empty()

    def _build_ui(self):
        with ui.Frame(visible=True, style=get_style()):
            with ui.ZStack():
                self._notify_stack = ui.VStack(style_type_name_override="Notification", visible=False)
                with self._notify_stack:
                    ui.Spacer(height=20)
                    with ui.HStack(height=0):
                        ui.Spacer()
                        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
                        thumbnail = f"{ext_path}/data/icons/{self._theme}/select_file.png"
                        ui.ImageWithProvider(
                            thumbnail, width=100, height=100, fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT
                        )
                        ui.Spacer()
                    ui.Spacer(height=20)
                    with ui.HStack(height=0):
                        ui.Spacer()
                        with ui.HStack(width=150):
                            self._labels["default"] = ui.Label(
                                "Select a file to see Checkpoints.",
                                word_wrap=True,
                                style_type_name_override="Notification.Label",
                                visible=True,
                            )
                            self._labels["cp_not_suppored"] = ui.Label(
                                "Location does not support Checkpoints.",
                                word_wrap=True,
                                style_type_name_override="Notification.Label",
                                visible=False,
                            )
                            self._labels["multi_select"] = ui.Label(
                                "Checkpoints Cannot Be Displayed For Multiple Items.",
                                word_wrap=True,
                                style_type_name_override="Notification.Label",
                                visible=False,
                            )
                            self._labels["no_checkpoint"] = ui.Label(
                                "Selected file has no Checkpoints.",
                                word_wrap=True,
                                style_type_name_override="Notification.Label",
                                visible=False,
                            )
                        ui.Spacer()
                    ui.Spacer()

                self._checkpoint_stack = ui.VStack(visible=False)
                with self._checkpoint_stack:
                    if self._layout in [LAYOUT_SLIM_VIEW, LAYOUT_DEFAULT]:
                        self._model.single_column = True
                        self._view = CheckpointSlimView(
                            self._model,
                            selection_changed_fn=self._on_selection_changed,
                            mouse_pressed_fn=self._on_mouse_pressed,
                            mouse_double_clicked_fn=self._on_mouse_double_clicked,
                        )
                    else:
                        self._view = CheckpointTableView(
                            self._model,
                            selection_changed_fn=self._on_selection_changed,
                            mouse_pressed_fn=self._on_mouse_pressed,
                            mouse_double_clicked_fn=self._on_mouse_double_clicked,
                        )

        # Create popup menus
        self._context_menu = ContextMenu()

        self._on_list_checkpoint(
            supports_checkpointing=False, has_checkpoints=False, current_checkpoint=None, multi_select=False
        )

    def _on_selection_changed(self, selections: List[CheckpointItem]):
        for selection_changed_fn in self._on_selection_changed_fn:
            selection_changed_fn(selections[0] if selections else None)

    def _on_mouse_pressed(self, button: int, key_mod: int, item: CheckpointItem):
        if button == 1:
            # Right mouse button: display context menu
            self._context_menu.show(item)
        if self._mouse_pressed_fn:
            self.mouse_pressed_fn(button, key_mod, item)

    def _on_mouse_double_clicked(self, button: int, key_mod: int, item: CheckpointItem):
        if self._mouse_double_clicked_fn:
            self._mouse_double_clicked_fn(button, key_mod, item)

    def _on_list_checkpoint(self, supports_checkpointing, has_checkpoints, current_checkpoint, multi_select):
        if has_checkpoints and not multi_select:
            self._checkpoint_stack.visible = True
            self._notify_stack.visible = False
        else:
            self._checkpoint_stack.visible = False
            self._notify_stack.visible = True

        if self._notify_stack.visible:
            self._labels["default"].visible = False
            if multi_select:
                self._labels["no_checkpoint"].visible = False
                self._labels["cp_not_suppored"].visible = False
                self._labels["multi_select"].visible = True
            elif not supports_checkpointing:
                self._labels["no_checkpoint"].visible = False
                self._labels["cp_not_suppored"].visible = True
                self._labels["multi_select"].visible = False
            else:
                self._labels["no_checkpoint"].visible = not has_checkpoints
                self._labels["cp_not_suppored"].visible = False
                self._labels["multi_select"].visible = False

        # Must delay the selection for one frame so that treeview is synced with model for scroll to selection to work.
        async def delayed_selection(weak_view, callback):
            view = weak_view()
            if not view:
                return

            await omni.kit.app.get_app().next_update_async()

            if current_checkpoint:
                view.selection = [current_checkpoint]
            else:
                view.selection = []

            if callback:
                callback(view.selection)

        asyncio.ensure_future(delayed_selection(weakref.ref(self._view), self._on_list_checkpoint_fn))

    @staticmethod
    def create_checkpoint_widget() -> "CheckpointWidget":
        """Creates and returns a new CheckpointWidget instance with a dummy head entry.

        Returns:
            CheckpointWidget: A new checkpoint widget instance.
        """
        widget = CheckpointWidget(show_none_entry=True)
        return widget

    @staticmethod
    def on_model_url_changed(widget: "CheckpointWidget", urls: List[str]):
        """Handles changes to the model URL. Updates widget URL and multi-select mode based on provided URLs.

        Args:
            widget (CheckpointWidget): The widget instance to update.
            urls (List[str]): List of URLs for updating the widget.
        """
        if not widget:
            return
        if urls:
            widget.set_url(urls[-1] or None)
            widget.set_multi_select(len(urls) > 1)
        else:
            widget.set_url(None)
            widget.set_multi_select(False)

    @staticmethod
    def delete_checkpoint_widget(widget: "CheckpointWidget"):
        """Deletes a checkpoint widget by calling its destroy method.

        Args:
            widget (CheckpointWidget): The widget instance to delete.
        """
        if widget:
            widget.destroy()

    def add_context_menu(self, name: str, glyph: str, click_fn: Callable, enable_fn: Callable, index: int = -1) -> str:
        """Adds a context menu item with the specified callbacks.

        Args:
            name (str): Unique name for the menu item.
            glyph (str): Glyph associated with the menu item.
            click_fn (Callable): Callback executed on menu item click. Signature: void fn(name, path).
            enable_fn (Callable): Function to determine menu item state. Signature: bool fn(name, item).
            index (int): Position to insert the menu item.

        Returns:
            str: Name of the menu item if successful, None otherwise.
        """
        if self._context_menu:
            return self._context_menu.add_menu_item(name, glyph, click_fn, enable_fn, index=index)
        return None

    def delete_context_menu(self, name: str):
        """Removes a context menu item identified by its name.

        Args:
            name (str): Unique name of the menu item to delete.
        """
        if self._context_menu:
            self._context_menu.delete_menu_item(name)
