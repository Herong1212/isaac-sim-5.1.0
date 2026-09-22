from typing import Callable, Optional, List

import carb
from omni.kit.widget.filebrowser import FileBrowserItem, NucleusModel
from .collection_item import CollectionItem, AddNewItem
from ..style import ICON_PATH

class AddNucleusConnectionItem(AddNewItem):
    def add_new(self, on_success_fn: Callable[[str, str, bool, bool], None]) -> None:
        try:
            from omni.kit.widget.nucleus_connector import connect_with_dialog
            connect_with_dialog(on_success_fn=on_success_fn)
        except ImportError:
            carb.log_warn("omni.kit.widget.nucleus_connector is not enabled")


class NucleusCollectionItem(CollectionItem):
    def __init__(self):
        super().__init__("omniverse", "Omniverse", f"{ICON_PATH}/omniverse_logo_64.png", order=10)
        self._sort_connections = True

    @property
    def connections(self) -> List[FileBrowserItem]:
        """List[:obj:`FileBrowserItem`]: List of connections of this item."""
        return self.children_list

    def create_add_new_item(self) -> Optional[AddNucleusConnectionItem]:
        return AddNucleusConnectionItem(name="Add New Connection ...")

    def create_child_item(self, name: str, path: str, is_folder: bool = True) -> Optional[FileBrowserItem]:
        model = NucleusModel(name, path)
        return model.root