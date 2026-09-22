__all__ = ["CollectionData"]
from dataclasses import dataclass
from typing import Callable

from omni.kit.widget.filebrowser import FileBrowserModel

@dataclass
class CollectionData:
    """
    CollectionData holds data and callbacks used to contruct a registered collection type with the content browser.
        identifier:         Key identifier for the collection type
        title:              Title to display for the collection type in the content browser tree view
        path_to_icon:       Path to the (svg) icon used in the content browser tree view for the registered collection type
        model:              Data model inheriting FileBrowserModel for the collection
        populate_fn:        Callback function that populates the model with pre-existing content items
    """
    identifier: str
    title: str
    path_to_icon: str
    model: FileBrowserModel
    populate_fn: Callable[[], None]
