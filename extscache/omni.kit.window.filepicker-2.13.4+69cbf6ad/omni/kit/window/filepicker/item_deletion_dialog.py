# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ConfirmItemDeletionDialog"]
from typing import Callable

from typing import List
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.window.popup_dialog import PopupDialog
import omni.ui as ui

from .item_deletion_model import ConfirmItemDeletionListModel
from .style import get_style


class ConfirmItemDeletionDialog(PopupDialog):
    """Dialog prompting the User to confirm the deletion of the provided list of files and folders."""

    def __init__(
            self,
            items: List[FileBrowserItem],
            title: str="Confirm File Deletion",
            message: str="You are about to delete",
            message_fn: Callable[[None], None]=None,
            parent: ui.Widget=None, # OBSOLETE
            width: int=500,
            ok_handler: Callable[[PopupDialog], None]=None,
            cancel_handler: Callable[[PopupDialog], None]=None,
        ):
        """
        Dialog prompting the User to confirm the deletion of the provided list of files and folders.

        Args:
            items ([FileBrowserItem]): List of files and folders to delete.
            title (str): Title of the dialog. Default "Confirm File Deletion".
            message (str): Basic message. Default "You are about to delete".
            message_fn (Callable[[None], None]): Message build function.
            parent (:obj:`omni.ui.Widget`): OBSOLETE. If specified, the dialog position is relative to this widget. Default `None`.
            width (int): Dialog width. Default `500`.
            ok_handler (Callable): Function to execute upon clicking the "Yes" button. Function signature:
                void ok_handler(dialog: :obj:`PopupDialog`)
            cancel_handler (Callable): Function to execute upon clicking the "No" button. Function signature:
                void cancel_handler(dialog: :obj:`PopupDialog`)

        """
        super().__init__(
            width=width,
            title=title,
            ok_handler=ok_handler,
            ok_label="Yes",
            cancel_handler=cancel_handler,
            cancel_label="No",
        )
        self._items = items
        self._message = message
        self._message_fn = message_fn
        self._list_model = ConfirmItemDeletionListModel(items)
        self._tree_view = None
        self._build_ui()
        self.hide()

    def _build_ui(self) -> None:
        with self._window.frame:
            with ui.ZStack(style=get_style()):
                ui.Rectangle(style_type_name_override="Background")
                with ui.VStack(style_type_name_override="Dialog", spacing=6):
                    if self._message_fn:
                        self._message_fn()
                    else:
                        prefix_message = self._message + " this item:" if len(self._items) == 1 else f"these {len(self._items)} items:"
                        ui.Label(prefix_message)
                    scrolling_frame = ui.ScrollingFrame(
                        height=150,
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    )
                    with scrolling_frame:
                        self._tree_view = ui.TreeView(
                            self._list_model,
                            root_visible=False,
                            header_visible=False,
                            style={"TreeView.Item": {"margin": 4}},
                        )
                    ui.Label("Are you sure you wish to proceed?")
                    self._build_ok_cancel_buttons()

    def destroy(self) -> None:
        """Destructor."""
        if self._list_model:
            self._list_model = None
        if self._tree_view:
            self._tree_view = None
        self._window = None

    def rebuild_ui(self, message_fn: Callable[[None], None]) -> None:
        """
        Rebuild ui widgets with new message

        Args:
            message_fn (Callable[[None], None]): Message build function.
        """
        self._message_fn = message_fn

        # Reset window or new height with new message
        self._window.height = 0
        self._window.frame.clear()

        self._build_ui()
