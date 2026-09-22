from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple
import carb.settings
from omni.kit.widget.filebrowser import FileBrowserModel, FileBrowserItem
import omni.ui as ui
from .collections.bookmark_collection import BookmarkCollectionItem
from .collections.collection_item import CollectionItem, CollectionItemFields
from .collections.nucleus_collection import NucleusCollectionItem
from .collections.filesystem_collection import FileSystemCollectionItem
from .collections.s3_collection import S3Collection
from .collections.collection_data import CollectionData


class NavigationModel(FileBrowserModel):
    def __init__(self, name: str, drop_fn: Callable, filter_fn: Callable, available_collections: str):
        """
        Model for the navigation tree view for collections and connections.

        Args:
            name (str): Name of the model.
            drop_fn (Callable): Drop function.
            filter_fn (Callable): Filter function.
            available_collections (str): Available collections. 
        """
        super().__init__(name=name, drop_fn=drop_fn, filter_fn=filter_fn)

        self._available_collections = available_collections
        self._collections: Dict[str, CollectionItem] = {}

        # Add default collections - may be ignored if not available
        default_collections = [
            BookmarkCollectionItem(),
            NucleusCollectionItem(),    
            S3Collection(),
            FileSystemCollectionItem(),
        ]
        for collection in default_collections:
            self.add_collection(collection)

        if self._available_collections is None:
            self._available_collections = [collection.identifier for collection in self._collections.values()]

    @property
    def collections(self) -> Dict[str, CollectionItem]:
        """dict[:obj:`CollectionItem`]: Available collections dict in the navigation model."""
        return {k: v for k, v in self._collections.items() if v.visible}

    @property
    def collection_items(self) -> List[FileBrowserItem]:
        """List[:obj:`FileBrowserItem`]: Available collection items in the navigation model."""
        return self.collections.values()

    @property
    def available_collections(self) -> List[str]:
        """List[str]: Available collections identifiers in the navigation model."""
        return self._available_collections
    
    @available_collections.setter
    def available_collections(self, values: List[str]):
        """Sets the available collections identifiers in the navigation model."""
        self._available_collections = values
        changed = False
        for identifier, collection_item in self._collections.items():
            visible = identifier in values
            if collection_item.visible != visible:
                changed = True
                collection_item.visible = visible
                if visible:
                    self._root.add_child(collection_item)
                else:
                    self._root.del_child(collection_item.title)    
        if changed:
            self._item_changed(self._root)

    def add_collection_by_data(self, collection_data: CollectionData) -> Optional[CollectionItem]:
        """
        Add a collection to the navigation model by CollectionData.

        Args:
            collection_data (:obj:`CollectionData`): Collection data.

        Returns:
            :obj:`CollectionItem`: The added collection item.
        """
        collection_item = CollectionItem(collection_data.identifier, collection_data.title, collection_data.path_to_icon)
        if collection_item:
            self.add_collection(collection_item)
            if collection_data.model:
                collection_item.add_child(collection_data.model.root)
            if collection_data.populate_fn:
                collection_data.populate_fn()
        return collection_item

    def add_collection(self, collection_item: CollectionItem) -> Optional[CollectionItem]:
        """
        Add a collection item to the navigation model.

        Args:
            collection_item (:obj:`CollectionItem`): Collection item.

        Returns:
            :obj:`CollectionItem`: The added collection item.
        """
        exist_collection = self._collections.get(collection_item.identifier, None)
        if exist_collection:
            if exist_collection.visible:
                carb.log_warn(f"{collection_item.identifier} already exists")
                return exist_collection
            else:
                self.remove_collection(collection_item.identifier)

        self._collections[collection_item.identifier] = collection_item

        # Always add the collection if it's available so that it could be eanbled later
        if self._available_collections and collection_item.identifier not in self._available_collections:
            carb.log_info(f"{collection_item.identifier} not available in {self._available_collections}")
            collection_item.visible = False
            return collection_item
        
        self._root.add_child(collection_item)
        self._item_changed(self._root)
        return collection_item

    def remove_collection(self, identifier: str) -> Optional[CollectionItem]:
        """
        Remove a collection from the navigation model.

        Args:
            identifier (str): Identifier of the collection.

        Returns:
            :obj:`CollectionItem`: The removed collection item.
        """
        item = self._collections.pop(identifier, None)
        if item:
            self._root.del_child(item.title)
            self._item_changed(self._root)
        return item

    def get_collection(self, identifier: str) -> Optional[CollectionItem]:
        """
        Get a collection from the navigation model.

        Args:
            identifier (str): Identifier of the collection.

        Returns:
            :obj:`CollectionItem`: The collection item.
        """
        return self.collections.get(identifier, None)

    def get_connections(self, identifier: str = None) -> List[FileBrowserItem]:
        """
        Returns all connections as items for the specified collection. If collection is 'None', then return connections
        from all collections.

        Args:
            identifier (str): Connection identifier. Default None.

        Returns:
            List[FileBrowserItem]: All connections found.

        """
        collections = [self.collections.get(identifier)] if identifier else self.collections.values()
        connections = []
        for collection in collections:
            # Note: We know that collections are initally expanded so we can safely retrieve its children
            # here without worrying about async delay.
            if collection and collection.children:
                connections.extend(collection.children_list)
        return connections

    def filter_collection(self, url: str = None) -> Optional[CollectionItem]:
        """
        Filter the collection based on the url.

        Args:
            url (str): The url to filter the collection.

        Returns:
            :obj:`CollectionItem`: The filtered collection.
        """
        for collection in self.collections.values():
            if collection.accept_url(url):
                return collection
        return None

    def add_path(self, name: str, path: str) -> Tuple[Optional[CollectionItem], Optional[FileBrowserItem]]:
        """
        Creates a :obj:`FileBrowserItem` at the given path.

        Args:
            name (str): Name, label really, of the path.
            path (str): Fullpath, e.g. "omniverse://ov-content". Paths to
                Omniverse servers should contain the prefix, "omniverse://".

        Returns:
            Tuple[:obj:`CollectionItem`, :obj:`FileBrowserItem`]: The added collection item and child item.

        Raises:
            :obj:`RuntimeWarning`: If unable to add path.

        """
        if not (name and path):
            raise RuntimeWarning(f"Error adding server, invalid name: '{name}', path: '{path}'.")

        collection = self.filter_collection(path)
        if not collection:
            carb.log_info(f"No collection found for '{path}'.")
            return (None, None)

        connection = collection.add_path(name, path)
        if connection:
            self._item_changed(collection)
        return (collection, connection)

    def create_root_item(self, name: str, path: str) -> FileBrowserItem:
        fields = CollectionItemFields(name, datetime.now(), 0, 0, 0)
        item = FileBrowserItem(path, fields, is_folder=True)
        item._models = (ui.SimpleStringModel(item.name), datetime.now(), ui.SimpleStringModel(""), ui.SimpleIntModel(0))
        item._enable_sorting = True
        item.sort_by_field = "order"
        item.populated = True
        return item
