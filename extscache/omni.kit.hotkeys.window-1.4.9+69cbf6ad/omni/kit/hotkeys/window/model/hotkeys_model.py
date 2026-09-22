# pylint: disable=unused-private-member, relative-beyond-top-level

__all__ = ["HotkeysModel"]

from typing import List, Dict, Optional, Union
import carb
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.actions.core import Action
from omni.kit.actions.window import AbstractActionsModel, ColumnRegistry
from omni.kit.hotkeys.core import Hotkey, HotkeyRegistry, KeyCombination, HotkeyFilter, get_hotkey_registry, HOTKEY_REGISTER_GLOBAL_EVENT, HOTKEY_DEREGISTER_GLOBAL_EVENT

from .hotkey_item import USER_HOTKEY_EXT_ID, HotkeyDetailItem, EmptyHotkeyItem, AbstractFilterItem, FilterWindowItem, FilterContextItem, GlobalFilterItem, EmptyFilterWindowItem, AddWindowItem
from .search_filter_flag import SearchFilterFlag


class HotkeysModel(AbstractActionsModel):
    def __init__(self, column_registry: ColumnRegistry):
        self._hotkey_registry = get_hotkey_registry()
        self._search_words: Optional[List[str]] = None
        self._hotkeys_by_filter: Dict[Optional[HotkeyFilter], List[Hotkey]] = {}
        self.__cached_hotkey_items: Dict[Optional[HotkeyFilter], List[HotkeyDetailItem]] = {}

        self.search_done = False
        self.search_filter_flags = [
            SearchFilterFlag("Windows", lambda filter, item, word: word.lower() in filter.id.lower()),
            SearchFilterFlag("Hotkeys", lambda filter, item, word: word.upper() in item.hotkey.key_combination.as_string),
            SearchFilterFlag("Actions", lambda filter, item, word: word.lower() in item.action.display_name.lower() if item.action else False),
            SearchFilterFlag("Show Only Modified", lambda filter, item, word: item.is_modified(), filter_by_keyword=False),
        ]
        for flag in self.search_filter_flags:
            flag.model.add_value_changed_fn(lambda m, f=flag: self.__on_filter_flag_changed(f))

        self.__empty_hotkey_item: Optional[EmptyHotkeyItem] = None
        self.__empty_window_filter_item: Optional[EmptyFilterWindowItem] = None
        self.__add_window_item = AddWindowItem()

        self.next_select_hotkey: Optional[Hotkey] = None

        self.__default_key_combinations: Dict[str, str] = {}
        self.__default_filer: Dict[str, HotkeyFilter] = {}

        self.__register_event_sub = get_eventdispatcher().observe_event(
            event_name=HOTKEY_REGISTER_GLOBAL_EVENT, on_event=self._on_hotkey_changed)
        self.__deregister_event_sub = get_eventdispatcher().observe_event(
            event_name=HOTKEY_DEREGISTER_GLOBAL_EVENT, on_event=self._on_hotkey_changed)

        # TODO: When edit hotkey from treeview, will trigger this change event and force to refresh treeview here
        # Disable it to keep treeview item stats no change
        # self.__change_event_sub = get_eventdispatcher().observe_event(
        #     event_name=HOTKEY_CHANGED_GLOBAL_EVENT, on_event=self._on_hotkey_changed)

        super().__init__(column_registry)

    def destroy(self):
        self.__register_event_sub = None
        self.__deregister_event_sub = None
        # self.__change_event_sub = None

    def get_ext_items(self) -> List[AbstractFilterItem]:
        all_hotkeys = self._hotkey_registry.get_all_hotkeys()
        self._hotkeys_by_filter: Dict[Optional[HotkeyFilter], List[Hotkey]] = {}
        self.__cached_hotkey_items = {}
        self._hotkeys_by_filter[GlobalFilterItem()] = []

        for hotkey in all_hotkeys:
            if not hotkey.action_ext_id or not hotkey.action_id:
                carb.log_warn(f"Invalid hotkey: {hotkey.action_ext_id}::{hotkey.action_id}")
                continue
            for filter_item in self.__get_filter_items(hotkey):
                self._hotkeys_by_filter[filter_item].append(hotkey)
            if hotkey.id not in self.__default_key_combinations:
                self.__default_key_combinations[hotkey.id] = hotkey.key_combination.id
            if hotkey.id not in self.__default_filer:
                self.__default_filer[hotkey.id] = hotkey.filter

        # Empty filter
        if self.__empty_window_filter_item:
            if not self.__is_filter_item_exists(self.__empty_window_filter_item):
                self._hotkeys_by_filter[self.__empty_window_filter_item] = []
            else:
                self.__empty_window_filter_item = None

        # No empty filer, show Add Window
        if not self.__empty_window_filter_item:
            self._hotkeys_by_filter[self.__add_window_item] = []

        avail_flags = [flag for flag in self.search_filter_flags if not flag.filter_by_keyword and flag.model.as_bool]
        if self._search_words or avail_flags:
            # If searching or filtering, only show items have result
            return [
                item for item in self._hotkeys_by_filter
                if isinstance(item, (AddWindowItem, EmptyFilterWindowItem)) or self.can_item_have_children(item)
            ]
        return list(self._hotkeys_by_filter.keys())

    def get_detail_items(self, item: AbstractFilterItem) -> List[HotkeyDetailItem]:
        if item in self.__cached_hotkey_items:
            return self.__cached_hotkey_items[item]

        if isinstance(item, AddWindowItem):
            return []

        hotkey_items = [
            HotkeyDetailItem(hotkey, highlight=self._search_words[0] if self._search_words else None)
            for hotkey in self._hotkeys_by_filter[item]
        ] if isinstance(item, AbstractFilterItem) else []
        filter_hotkey_items = [hotkey_item for hotkey_item in hotkey_items if self.__filter_item(item, hotkey_item)]

        filter_hotkey_items.sort(key=lambda i: i.hotkey.action.display_name.upper() if i.hotkey.action else i.hotkey.action_text.upper())
        if self.__empty_hotkey_item:
            filter_items = self.__get_filter_items(self.__empty_hotkey_item.hotkey)
            if item in filter_items:
                filter_hotkey_items.insert(0, self.__empty_hotkey_item)

        self.__cached_hotkey_items[item] = filter_hotkey_items
        return self.__cached_hotkey_items[item]

    def execute(self, item: HotkeyDetailItem) -> None:
        if item is None:
            return
        hotkey = item.hotkey
        hotkey.execute()

    def add_window_filter(self) -> None:
        self.__empty_window_filter_item = EmptyFilterWindowItem()
        self._item_changed(None)

    def edit_hotkey_filter_item(self, item: AbstractFilterItem, window_title: str = None):
        if window_title:
            item.id = window_title
        else:
            # Clear current empty window filter
            self.__empty_window_filter_item = None
            self._item_changed(None)

    def add_empty_hotkey(self, item: AbstractFilterItem) -> HotkeyDetailItem:
        self.__empty_hotkey_item = EmptyHotkeyItem(USER_HOTKEY_EXT_ID)
        if isinstance(item, FilterContextItem):
            self.__empty_hotkey_item.hotkey.filter = HotkeyFilter(context=item.id)
        elif isinstance(item, FilterWindowItem):
            self.__empty_hotkey_item.hotkey.filter = HotkeyFilter(windows=[item.id])
        self.next_select_hotkey = self.__empty_hotkey_item.hotkey

        self._item_changed(None)
        return self.__empty_hotkey_item

    def clear_empty_hotkey(self) -> None:
        if not self.__empty_hotkey_item:
            return
        filter_items = self.__get_filter_items(self.__empty_hotkey_item.hotkey)
        filter_item = filter_items[0] if filter_items else None
        if filter_item and filter_item in self.__cached_hotkey_items and len(self.__cached_hotkey_items[filter_item]) > 1:
            # First is empty
            self.next_select_hotkey = self.__cached_hotkey_items[filter_item][1].hotkey
        self.__empty_hotkey_item = None

        self._item_changed(None)

    def save_empty_action(self, action: Action) -> HotkeyDetailItem:
        self.__empty_hotkey_item.hotkey.action_ext_id = action.extension_id
        self.__empty_hotkey_item.hotkey.action_id = action.id

        return self.__empty_hotkey_item

    def save_empty_hotkey(self, key_combination: KeyCombination) -> HotkeyRegistry.Result:
        hotkey = self.__empty_hotkey_item.hotkey
        hotkey.key_combination = key_combination
        hotkey = self._hotkey_registry.register_hotkey(hotkey)
        if not hotkey:
            return self._hotkey_registry.last_error

        self.next_select_hotkey = self.__empty_hotkey_item.hotkey
        self.__empty_hotkey_item = None

        # Once a hotkey created, it is not a empty filter anymore
        if self.__empty_window_filter_item and hotkey.filter and hotkey.filter.windows:
            for window in hotkey.filter.windows:
                if window == self.__empty_window_filter_item.id:
                    self.__empty_window_filter_item = None
                    break

        self._item_changed(None)

        return HotkeyRegistry.Result.OK

    def get_item_by_key(self, key_combination: KeyCombination, hotkey_filter: HotkeyFilter) -> Optional[HotkeyDetailItem]:
        for filter_item in self.__get_filter_items(hotkey_filter):
            for registered_hotkey in self._hotkeys_by_filter[filter_item]:
                if registered_hotkey.key_combination == key_combination:
                    return HotkeyDetailItem(registered_hotkey)
        return None

    def delete_hotkey_item(self, item: HotkeyDetailItem) -> None:
        self._hotkey_registry.disable_hotkey(item.hotkey)

        # Set selected item when updated
        filter_items = self.__get_filter_items(item.hotkey)
        filter_item = filter_items[0] if filter_items else None
        if filter_item in self.__cached_hotkey_items \
                and self.__cached_hotkey_items[filter_item] \
                and item in self.__cached_hotkey_items[filter_item] \
                and len(self.__cached_hotkey_items[filter_item]) > 1:
            index = self.__cached_hotkey_items[filter_item].index(item) + 1
            if index >= len(self.__cached_hotkey_items[filter_item]):
                index -= 2
            if index >= 0:
                self.next_select_hotkey = self.__cached_hotkey_items[filter_item][index].hotkey

        self._item_changed(None)

    def edit_hotkey_item(
        self,
        item: HotkeyDetailItem,
        key_text: Optional[str] = None,
        trigger_press: Optional[bool] = None,
        window_title: Optional[str] = None,
    ) -> HotkeyRegistry.Result:
        key_combination = item.hotkey.key_combination
        if key_text is not None:
            key_combination = KeyCombination(key_text, trigger_press=item.hotkey.key_combination.trigger_press)
        if trigger_press is not None:
            key_combination = KeyCombination(key_combination.as_string, trigger_press=trigger_press)

        if isinstance(item, EmptyHotkeyItem):
            result = self.save_empty_hotkey(key_combination)
        else:
            result = self._hotkey_registry.edit_hotkey(item.hotkey, key_combination, filter=item.hotkey.filter)

        if result == HotkeyRegistry.Result.OK:
            self.next_select_hotkey = item.hotkey
            self._item_changed(None)
        return result

    def restore_item_key(self, item: HotkeyDetailItem) -> HotkeyRegistry.Result:
        result = self._hotkey_registry.edit_hotkey(item.hotkey, item.default_key_id, item.default_filter)
        if result != HotkeyRegistry.Result.OK:
            return result

        self.next_select_hotkey = item.hotkey
        self._item_changed(None)
        return HotkeyRegistry.Result.OK

    def replace_item_key(self, key_combination: KeyCombination, new_item: HotkeyDetailItem, duplicated_key: Hotkey):
        self._hotkey_registry.edit_hotkey(duplicated_key, KeyCombination("M", trigger_press=duplicated_key.key_combination.trigger_press), duplicated_key.filter)
        if isinstance(new_item, EmptyHotkeyItem):
            self.save_empty_hotkey(key_combination)
        else:
            self.edit_hotkey_item(new_item, key_text=key_combination.as_string)

    def _on_hotkey_changed(self, _):
        self._item_changed(None)

    def search(self, search_words: Optional[List[str]]):
        # Now could highlight one word in HighlightLabel, so combine the search words back to a single string
        self._search_words = [" ".join(search_words)] if search_words else None
        self.search_done = True
        self._item_changed(None)

    def __on_filter_flag_changed(self, flag: SearchFilterFlag):
        if self._search_words or not flag.filter_by_keyword:
            self.search_done = True
            self._item_changed(None)

    def __filter_item(self, filter_item: AbstractFilterItem, item: HotkeyDetailItem) -> bool:
        # First check fitler flag nothing to search words
        available_without_word_flags = [flag for flag in self.search_filter_flags if not flag.filter_by_keyword and flag.model.as_bool]
        if available_without_word_flags:
            for flag in available_without_word_flags:
                if not flag.filter(filter_item, item, None):
                    return False

        # Check filter flag with search words
        if self._search_words and not self._filter_item_by_keyword(filter_item, item):
            return False
        return True

    def _filter_item_by_keyword(self, filter_item: AbstractFilterItem, item: HotkeyDetailItem) -> bool:
        # Get available filter flags
        available_flags = [flag for flag in self.search_filter_flags if flag.filter_by_keyword and flag.model.as_bool]
        if not available_flags:
            # If no filter flag set, default for all
            available_flags = [flag for flag in self.search_filter_flags if flag.filter_by_keyword]

        # If in any enabled filter, consider found
        return any(flag.filter(filter_item, item, self._search_words) for flag in available_flags)

    def __get_filter_items(self, hotkey: Union[Hotkey, HotkeyFilter]) -> List[AbstractFilterItem]:
        hotkey_filter = hotkey.filter if isinstance(hotkey, Hotkey) else hotkey
        if hotkey_filter is None:
            for item in self._hotkeys_by_filter:
                if isinstance(item, GlobalFilterItem):
                    item.highlight = self._search_words[0] if self._search_words else None
                    return [item]
        else:
            if hotkey_filter.context:
                for item in self._hotkeys_by_filter:
                    if isinstance(item, FilterContextItem) and item.id == hotkey_filter.context:
                        return [item]
                context_filter_item = FilterContextItem(hotkey_filter.context)
                self._hotkeys_by_filter[context_filter_item] = []
                return [context_filter_item]
            if hotkey_filter.windows:
                filter_items = []
                for window in hotkey_filter.windows:
                    # Now only 1 window supprted
                    for item in self._hotkeys_by_filter:
                        if isinstance(item, FilterWindowItem) and item.id == window:
                            filter_items.append(item)
                            break
                    else:
                        window_filter_item = FilterWindowItem(window, highlight=self._search_words[0] if self._search_words else None)
                        if window_filter_item not in self._hotkeys_by_filter:
                            self._hotkeys_by_filter[window_filter_item] = []
                        filter_items.append(window_filter_item)
                    return filter_items
        return []

    def __is_filter_item_exists(self, item: AbstractFilterItem) -> bool:
        for filter_item in self._hotkeys_by_filter:
            if isinstance(item, FilterWindowItem):
                if isinstance(filter_item, FilterWindowItem) and item.id == filter_item.id:
                    return True
            elif isinstance(item, FilterContextItem) and isinstance(filter_item, FilterContextItem) and item.id == filter_item.id:
                return True

        return False
