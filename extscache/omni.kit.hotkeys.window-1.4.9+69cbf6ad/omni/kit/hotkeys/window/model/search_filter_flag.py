__all__ = ["SearchFilterFlag"]
from typing import Callable, List
from omni.kit.widget.options_menu import OptionItem

from .hotkey_item import HotkeyDetailItem, AbstractFilterItem  # pylint: disable=relative-beyond-top-level


class SearchFilterFlag(OptionItem):
    """
    Filter flag for searching.
    Args:
        name (str): Flag name.
        filter_fn (Callable[[AbstractFilterItem, HotkeyDetailItem, str], bool]): Callback function to check if word in hotkey.
    Kwargs:
        default (bool): Flag enabled. Default False.
        filter_by_keyword (bool): If filter with search words
    """

    def __init__(
        self,
        name: str,
        filter_fn: Callable[[HotkeyDetailItem, str], bool],
        default: bool = False,
        filter_by_keyword: bool = True
    ):
        self.filter_by_keyword = filter_by_keyword
        self.__filter_fn = filter_fn
        super().__init__(name, default=default)

    def filter(self, filter_item: AbstractFilterItem, item: HotkeyDetailItem, search_words: List[str]) -> bool:  # noqa: A003
        """
        Search list of string.
        Return if one word not found.
        """
        if self.filter_by_keyword:
            if search_words:
                for word in search_words:
                    if not self.__filter_fn(filter_item, item, word):
                        return False
            return True
        return self.__filter_fn(filter_item, item, None)
