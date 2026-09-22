from datetime import datetime
from typing import Callable, Optional, List
from functools import partial

import omni.client
from omni.kit.widget.filebrowser import FileBrowserItem, NucleusItem, FileBrowserItemFields
import omni.ui as ui
from .collection_item import CollectionItem, AddNewItem
from .s3_connector_dialog import S3ConnectorDialog
from ..style import ICON_PATH


class AddS3ConnectionItem(AddNewItem):
    def add_new(self, on_success_fn: Callable[[str, str, bool, bool], None]) -> None:
        dialog = S3ConnectorDialog()
        dialog.show()

        def on_connect_server(
            on_success_fn: Callable,
            dialog: S3ConnectorDialog,
        ):
            name = dialog.get_value("name")
            url = dialog.get_value("url")
            url = url.rstrip("/")
            if url.startswith("https://"):
                url = url[8:]

            if not url:
                return
            
            if not name:
                name = url

            url = "https://" + url
            result, _ = omni.client.stat(url)
            if result == omni.client.Result.OK:
                dialog.hide()
                on_success_fn(name, url)
            else:
                dialog.show_alert(f"Failed to connect to '{url}'")
        dialog.set_okay_clicked_fn(partial(on_connect_server, on_success_fn))
    

class S3ConnectionItem(NucleusItem):
    """
    A item for a S3 connection
    Sub-classed from :obj:`NucleusItem`.

    Args:
        name (str): Name of the item.
        path (str): Path of the item.
    """
    def __init__(self, name: str, path: str):
        access = omni.client.AccessFlags.READ
        fields = FileBrowserItemFields(name, datetime.now(), 0, access)
        super().__init__(path, fields, is_folder=True)
        self._models = (ui.SimpleStringModel(name), datetime.now(), ui.SimpleStringModel(""))


class S3Collection(CollectionItem):
    def __init__(self):
        super().__init__("https", "S3", f"{ICON_PATH}/cloud.svg", access = omni.client.AccessFlags.READ, order=20)

    @property
    def connections(self) -> List[FileBrowserItem]:
        """List[:obj:`FileBrowserItem`]: List of connections of this item."""
        return self.children_list

    def create_add_new_item(self) -> Optional[AddNewItem]:
        return AddS3ConnectionItem(name="Add New Connection ...")

    def create_child_item(self, name: str, path: str, is_folder: bool = True) -> Optional[S3ConnectionItem]:
        return S3ConnectionItem(name, path)


