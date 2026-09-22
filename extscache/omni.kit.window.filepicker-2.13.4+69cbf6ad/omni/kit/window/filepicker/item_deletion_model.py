# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ConfirmItemDeletionListItem"]
import omni.ui as ui

from omni.kit.widget.filebrowser import FileBrowserItem


class ConfirmItemDeletionListItem(ui.AbstractItem):
    """Single item of the list of `FileBrowserItem`s to delete."""

    def __init__(self, item: FileBrowserItem):
        """
        Single item of the list of `FileBrowserItem`s to delete.

        Args:
            item (FileBrowserItem): The item of the File Browser which should be deleted.

        """
        super().__init__()
        self.path_model = ui.SimpleStringModel(item.path)


class ConfirmItemDeletionListModel(ui.AbstractItemModel):
    """Model representing a list of `FileBrowserItem`s to delete."""

    def __init__(self, items: [FileBrowserItem]):
        """
        Model representing a list of `FileBrowserItem`s to delete.

        Args:
            items ([FileBrowserItem]): List of File Browser items which should be deleted.

        """
        super().__init__()
        self._children = [ConfirmItemDeletionListItem(item) for item in items]

    def get_item_children(self, item: ConfirmItemDeletionListItem) -> [ConfirmItemDeletionListItem]:
        """
        Return the list of all children of the given item to present to the display widget.

        Args:
            item (ConfirmItemDeletionListItem): Item of the model.

        Returns:
            [ConfirmItemDeletionListItem]: The list of all children of the given item to present to the display widget.

        """
        if item is not None:
            # Since we are doing a flat list, we only return the list of items at the root-level.
            return []
        return self._children

    def get_item_value_model_count(self, item: ConfirmItemDeletionListItem) -> int:
        """
        Return the number of columns to display.

        Args:
            item (ConfirmItemDeletionListItem): Item of the model.

        Returns:
            int: The number of columns to display.

        """
        return 1

    def get_item_value_model(self, item: ConfirmItemDeletionListItem, column_id: int) -> ui.SimpleStringModel:
        """
        Return the value model for the given item at the given column index.

        Args:
            item (ConfirmItemDeletionListItem): Item of the model for which to return the model.
            column_id (int): Index of the column for which to return the model.

        Returns:
            ui.SimpleStringModel: The model for the given item at the given column index.

        """
        if item and isinstance(item, ConfirmItemDeletionListItem) and column_id == 0:
            return item.path_model
        return None
