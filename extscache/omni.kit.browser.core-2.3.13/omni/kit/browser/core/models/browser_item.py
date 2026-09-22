from typing import List, Optional

from omni import ui


class BaseItem(ui.AbstractItem):
    """
    A common item for BrowserModel
    Args:
        name (str): item name
    """

    def __init__(self, name: str):
        super().__init__()
        self.name_model = ui.SimpleStringModel(name)

    @property
    def name(self) -> str:
        return self.name_model.as_string


class CollectionItem(BaseItem):
    """
    A single AbstractItem item that represents a single collection.
    Args:
        name (str): collection name
        url (str): collection url
    """

    def __init__(self, name: str, url: str):
        super().__init__(name)
        self.url = url

    def __repr__(self):
        return f'"[collection item] {self.name}, {self.url}"'


class CategoryItem(BaseItem):
    """
    A single AbstractItem item that represents a single category.
    Args:
        name (str): catetory name
        count (int): count of detail items in this category. Default is 0.
    """

    def __init__(self, name, count=0,
                 parent: Optional[BaseItem] = None,
                 is_last_child: Optional[bool] = False):
        super().__init__(name)
        self.count = count
        self.children: List[BaseItem] = []

        # Store the parent so we can find out if an ancestor is the last child among its siblings
        self.parent = parent
        self.is_last_child = is_last_child

        # TODO: is it necessary to put thumbnail in BaseItem?
        self.thumbnail: Optional[str] = None
        self.url: str = ""

        # Indicate category is loading - show loading icon in category view
        self.loading = False

    def filter(self, filter_words: Optional[List[str]]) -> bool:
        """
        Filter detail item. Return True if filtered otherwise False.
        Args:
            filter_words: A string list to filter detail items. None means filtering nothing.
        """
        if filter_words is None:
            return True
        else:
            for word in filter_words:
                if not word.lower() in self.name.lower():
                    return False
            else:
                return True

    def __repr__(self):
        return f'"[category item] {self.name}, {self.count}"'


class DetailItem(BaseItem):
    """
    A single AbstractItem item that represents a single detail item.
    Args:
        name (str): detail name
        url (str): detail url
        thumbnail (str): detail thumbnail url
    """

    def __init__(self, name: str, url: str, thumbnail: str = None):
        super().__init__(name)
        self._url = url
        self._thumbnail = thumbnail

    @property
    def url(self) -> str:
        return self._url

    @property
    def thumbnail(self) -> str:
        return self._thumbnail

    @url.setter
    def url(self, value: str):
        self._url = value

    @thumbnail.setter
    def thumbnail(self, value: str):
        self._thumbnail = value

    def filter(self, filter_words: Optional[List[str]]) -> bool:
        """
        Filter detail item. Return True if filtered otherwise False.
        Args:
            filter_words: A string list to filter detail items. None means filtering nothing.
        """
        if filter_words is None:
            return True
        else:
            for word in filter_words:
                if not word.lower() in self.name.lower():
                    return False
            else:
                return True

    def __repr__(self):
        return f'"[detail item] {self.name}, {self.url}, {self.thumbnail}"'
