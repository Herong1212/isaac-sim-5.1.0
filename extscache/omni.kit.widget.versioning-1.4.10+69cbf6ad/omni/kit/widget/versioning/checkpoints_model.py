# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import copy
import carb
import omni.client
import omni.kit.app
from omni.kit.async_engine import run_coroutine
import omni.ui as ui

from datetime import datetime


class DummyNoneNode:
    def __init__(self, entry: omni.client.ListEntry):
        self.relative_path = " <head>"
        self.access = entry.access
        self.flags = entry.flags
        self.size = entry.size
        self.modified_time = entry.modified_time
        self.created_time = entry.created_time
        self.modified_by = entry.modified_by
        self.created_by = entry.created_by
        self.version = entry.version
        self.comment = "<Not using Checkpoint>"


class CheckpointItem(ui.AbstractItem):
    """A class representing a checkpoint item.

    This class encapsulates a checkpoint entry and a URL without query parameters. It is used in the context of Omni UI to manage and display checkpoint information for files. The class provides access to the checkpoint comment, constructs the full URL by appending the entry's relative path when necessary, and retrieves a relative path when applicable. In addition, it offers two static methods: one for converting a file size value to a human-readable string and another for formatting datetime objects into a string representation.

    Args:
        entry (omni.client.ListEntry): The checkpoint entry containing metadata such as comment and relative path.
        url (str): The base URL without query parameters associated with the checkpoint.
    """

    def __init__(self, entry, url):
        """Initializes a CheckpointItem instance."""
        super().__init__()
        self.comment_elided = True
        self.url = url  # url without query
        self.entry = entry

    @property
    def comment(self):
        """Gets the comment associated with the entry.

        Returns:
            str: The comment if entry exists; otherwise, an empty string.
        """
        if self.entry:
            return self.entry.comment
        return ""

    def get_full_url(self):
        """Retrieves the complete url for the checkpoint, including query if applicable.

        Returns:
            str: The full url string for the checkpoint item.
        """
        if isinstance(self.entry, DummyNoneNode):
            return self.url
        return self.url + "?" + self.entry.relative_path

    def get_relative_path(self):
        """Obtains the relative path from the entry.

        Returns:
            Optional[str]: The relative path if available; otherwise, None.
        """
        if isinstance(self.entry, DummyNoneNode):
            return None
        return self.entry.relative_path

    @staticmethod
    def size_to_string(size: int):
        """Converts a numeric size into a human readable string representation.

        Args:
            size (int): The size value to be converted.

        Returns:
            str: The size represented as a string in GB, MB, or KB.
        """
        return (
            f"{size/1.e9:.2f} GB"
            if size > 1.0e9
            else (f"{size/1.e6:.2f} MB" if size > 1.0e6 else f"{size/1.e3:.2f} KB")
        )

    @staticmethod
    def datetime_to_string(dt: datetime):
        """Formats a datetime object into a string using a fixed format.

        Args:
            dt (datetime): The datetime object to format.

        Returns:
            str: The formatted string representation of the datetime.
        """
        return dt.strftime("%x %I:%M%p")


class CheckpointModel(ui.AbstractItemModel):
    """A model for managing file checkpoints using Omni UI.

    This class provides an interface for listing, filtering, and restoring checkpoints for files. It handles asynchronous operations to retrieve checkpoint data from the server and updates the checkpoint list in response to file events. It supports search filtering, single column display mode, and both single and multi selection of checkpoints. Additionally, it manages internal state and task cancellation to ensure efficient updates when the underlying file or connection status changes.

    Args:
        show_none_entry (bool): Indicates whether a dummy entry representing no checkpoint should be included in the list.
    """

    def __init__(self, show_none_entry):
        """Initializes a new instance of CheckpointModel."""
        super().__init__()
        self._show_none_entry = show_none_entry
        self._checkpoints = []
        self._checkpoints_filtered = []
        self._url = ""
        self._incoming_url = ""
        self._url_without_query = ""
        self._search_kw = ""
        self._checkpoint = None
        self._on_list_checkpoint_fn = None
        self._single_column = False
        self._list_task = None
        self._restore_task = None
        self._set_url_task = None
        self._multi_select = False
        self._file_status_request = omni.client.register_file_status_callback(self._on_file_status)
        self._resolve_subscription = None
        self._run_loop = asyncio.get_event_loop()

    def reset(self):
        """Resets checkpoint lists and cancels pending tasks, if any."""
        self._checkpoints = []
        self._checkpoints_filtered = []
        if self._list_task:
            self._list_task.cancel()
            self._list_task = None
        if self._restore_task:
            self._restore_task.cancel()
            self._restore_task = None

    def destroy(self):
        """Releases resources, resets state and cancels pending tasks."""
        self._on_list_checkpoint_fn = None
        self.reset()
        self._file_status_request = None
        self._resolve_subscription = None
        self._run_loop = None
        if self._set_url_task:
            self._set_url_task.cancel()
            self._set_url_task = None

    @property
    def single_column(self):
        """Gets the single_column property value.

        Returns:
            bool: True if single column mode is active, False otherwise.
        """
        return self._single_column

    @single_column.setter
    def single_column(self, value: bool):
        """Sets the single_column property.

        Args:
            value (bool): New state for single column mode.
        """
        self._single_column = not not value
        self._item_changed(None)

    def empty(self):
        """Checks if the model has no items to display."""
        return not self.get_item_children(None)

    def set_multi_select(self, state: bool):
        """Sets the multi select state.

        Args:
            state (bool): Multi select state value.
        """
        self._multi_select = state

    def set_url(self, url):
        """Updates the incoming URL and refreshes checkpoints asynchronously.

        Args:
            url (str): New URL to set.
        """
        self._incoming_url = url

        # In file dialog, if select file A, then select file B, it emits selection event of "file A", "None", "file B"
        # Do a async task to eat the "None" event to avoid flickering
        async def delayed_set_url():
            await omni.kit.app.get_app().next_update_async()
            if self._url != self._incoming_url:
                self._url = self._incoming_url
                self.reset()
                if self._url:
                    client_url = omni.client.break_url(self._url)
                    if client_url.query:
                        _, self._checkpoint = omni.client.get_branch_and_checkpoint_from_query(client_url.query)
                    else:
                        self._checkpoint = 0
                    self._url_without_query = omni.client.make_url(
                        scheme=client_url.scheme,
                        user=client_url.user,
                        host=client_url.host,
                        port=client_url.port,
                        path=client_url.path,
                        fragment=client_url.fragment,
                    )
                    self.list_checkpoint()
                    self._resolve_subscription = omni.client.resolve_subscribe_with_callback(
                        self._url_without_query,
                        [self._url_without_query],
                        None,
                        lambda result, event, entry, url: self._on_file_change_event(result),
                    )
                else:
                    self._no_checkpoint(True)

            self._set_url_task = None

        if not self._set_url_task:
            self._set_url_task = run_coroutine(delayed_set_url())

    def _on_file_change_event(self, result: omni.client.Result):
        if result == omni.client.Result.OK:

            async def set_url():
                """Updates the incoming URL and refreshes checkpoints asynchronously.

                Args:
                    url (str): New URL to set.
                """
                self.list_checkpoint()

            # must run on main thread as this one does not have async loop...
            asyncio.run_coroutine_threadsafe(set_url(), loop=self._run_loop)

    def get_url(self):
        """Gets the current URL used by the model."""
        return self._url

    def set_search(self, keywords):
        """Updates the search keywords and triggers filtering.

        Args:
            keywords (str): Search keywords to filter items.
        """
        if self._search_kw != keywords:
            self._search_kw = keywords
            self._re_filter()

    def set_on_list_checkpoint_fn(self, fn):
        """Sets a callback function for when checkpoints are listed.

        Args:
            fn (callable): Callback function for checkpoint listing.
        """
        self._on_list_checkpoint_fn = fn

    def on_list_checkpoints(self, file_entry, checkpoints_entries):
        """Processes listed checkpoints, updates internal state and triggers callback.

        Args:
            file_entry (object): File entry reference for checkpoint processing.
            checkpoints_entries (list): List of checkpoint entries.
        """
        self._checkpoints = []
        current_cp_item = None
        for cp in checkpoints_entries:
            item = CheckpointItem(cp, self._url_without_query)
            self._checkpoints.append(item)
            if not current_cp_item and str(self._checkpoint) == cp.relative_path[1:]:
                current_cp_item = item
        # OM-45546: Add back the <head> dummy option for files with checkpoints
        if self._show_none_entry:
            none_entry = DummyNoneNode(file_entry)
            item = CheckpointItem(none_entry, self._url_without_query)
            self._checkpoints.append(item)
            if self._checkpoint == 0:
                current_cp_item = item

        # newest checkpoints at top
        self._checkpoints.reverse()
        self._re_filter()
        self._item_changed(None)
        if self._on_list_checkpoint_fn:
            self._on_list_checkpoint_fn(
                supports_checkpointing=True,
                has_checkpoints=len(self._checkpoints),
                current_checkpoint=current_cp_item,
                multi_select=self._multi_select,
            )

    def get_item_children(self, item):
        """Returns all the children when the widget asks it.

        Args:
            item (object): Item for which children are returned.
        """
        if item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return []

        return self._checkpoints if self._search_kw == "" else self._checkpoints_filtered

    def get_item_value_model_count(self, item):
        """The number of columns.

        Args:
            item (object): Item for which columns count is requested.

        Returns:
            int: Number of columns (1 for single column mode, otherwise 5).
        """
        if self._single_column:
            return 1
        return 5

    def list_checkpoint(self):
        """Initiates an asynchronous task to list available checkpoints."""
        self._list_task = run_coroutine(self._list_checkpoint_async())

    def restore_checkpoint(self, file_path, checkpoint_path):
        """Restores a checkpoint by copying the specified checkpoint to a file.

        Args:
            file_path (str): Destination file path for the checkpoint.
            checkpoint_path (str): Source checkpoint path to restore.
        """
        self._restore_task = run_coroutine(self._restore_checkpoint(file_path, checkpoint_path))

    def get_drag_mime_data(self, item):
        """Returns Multipurpose Internet Mail Extensions (MIME) data for be able to drop this item somewhere.

        Args:
            item (object): Source item for which MIME data is generated.

        Returns:
            str: MIME data string.
        """
        return item.get_full_url()

    async def _list_checkpoint_async(self):
        # TODO: double check here, don't need to change any thing
        if self._url_without_query == "omniverse://":
            support_checkpointing = True
        else:
            client_url = omni.client.break_url(self._url_without_query)
            server_url = omni.client.make_url(scheme=client_url.scheme, host=client_url.host, port=client_url.port)
            result, server_info = await omni.client.get_server_info_async(server_url)
            support_checkpointing = True if result and server_info and server_info.checkpoints_enabled else False

        result, server_info = await omni.client.get_server_info_async(self._url_without_query)

        if not result or not server_info or not server_info.checkpoints_enabled:
            self._no_checkpoint(support_checkpointing)
            return
        # Have to use async version. _with_callback comes from a different thread
        result, entry = await omni.client.stat_async(self._url_without_query)
        if entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN:
            # Can't have checkpoint on folder
            self._no_checkpoint(support_checkpointing)
            return
        result, entries = await omni.client.list_checkpoints_async(self._url_without_query)
        if result != omni.client.Result.OK:
            carb.log_warn(f"Failed to get checkpoints for {self._url_without_query}: {result}")

        self.on_list_checkpoints(entry, entries)
        self._list_task = None

    def _on_file_status(self, url, status, percent):
        if status == omni.client.FileStatus.WRITING and percent == 100 and url == self._url_without_query:

            async def set_url():
                """Updates the incoming URL and refreshes checkpoints asynchronously.

                Args:
                    url (str): New URL to set.
                """
                self.list_checkpoint()

            # must run on main thread as this one does not have async loop...
            asyncio.run_coroutine_threadsafe(set_url(), loop=self._run_loop)

    def _no_checkpoint(self, support_checkpointing):
        self._checkpoints.clear()
        self._item_changed(None)
        if self._on_list_checkpoint_fn:
            self._on_list_checkpoint_fn(
                supports_checkpointing=support_checkpointing,
                has_checkpoints=False,
                current_checkpoint=None,
                multi_select=self._multi_select,
            )

    async def _restore_checkpoint(self, file_path, checkpoint_path):
        id = checkpoint_path.rfind("&") + 1
        relative_path = checkpoint_path[id:] if id > 0 else ""
        result = await omni.client.copy_async(
            checkpoint_path, file_path, message=f"Restored checkpoint #{relative_path}"
        )
        carb.log_warn(f"Restore checkpoint {checkpoint_path} to {file_path}: {result}")
        if result:
            self.list_checkpoint()

    def _re_filter(self):
        self._checkpoints_filtered.clear()
        if self._search_kw == "":
            self._checkpoints_filtered = copy.copy(self._checkpoints)
        else:
            kws = self._search_kw.split(" ")
            for cp in self._checkpoints:
                for kw in kws:
                    if kw.lower() in cp.entry.comment.lower():
                        self._checkpoints_filtered.append(cp)
                        break
                    if kw.lower() in cp.entry.relative_path.lower():
                        self._checkpoints_filtered.append(cp)
                        break
        self._item_changed(None)
