__all__ = ["HotkeyRegistry"]
import copy
from typing import List, Optional, Union, Dict, Tuple
import carb
import carb.settings
import omni.kit.app
from .hotkey import Hotkey
from .key_combination import KeyCombination
from .filter import HotkeyFilter
from .storage import HotkeyStorage
from .event import HOTKEY_REGISTER_GLOBAL_EVENT, HOTKEY_DEREGISTER_GLOBAL_EVENT, HOTKEY_CHANGED_GLOBAL_EVENT
from .keyboard_layout import KeyboardLayoutDelegate

SETTING_DEFAULT_KEYBOARD_LAYOUT = "/exts/omni.kit.hotkeys.core/default_keyboard_layout"


class HotkeyRegistry:
    """
    Registry of hotkeys.
    """
    class Result:
        OK = "OK"
        ERROR_NO_ACTION = "No action defined"
        ERROR_ACTION_DUPLICATED = "Duplicated action definition"
        ERROR_KEY_INVALID = "Invalid key definition"
        ERROR_KEY_DUPLICATED = "Duplicated key definition"

    def __init__(self):
        """
        Define hotkey registry object.
        """
        self._hotkeys: List[Hotkey] = []
        self._hotkeys_by_key_and_context: Dict[KeyCombination, Dict[str, Hotkey]] = {}
        self._hotkeys_by_key_and_window: Dict[KeyCombination, Dict[str, Hotkey]] = {}
        self._global_hotkeys_by_key: Dict[KeyCombination, Hotkey] = {}
        self.__hotkey_storage = HotkeyStorage()
        self.__default_key_combinations: Dict[str, str] = {}
        self.__default_filters: Dict[str, HotkeyFilter] = {}
        self.__disabled_hotkeys: Dict[str, Hotkey] = {}
        self.__last_error = HotkeyRegistry.Result.OK
        self.__settings = carb.settings.get_settings()
        keyboard_layout = self.__settings.get("/persistent" + SETTING_DEFAULT_KEYBOARD_LAYOUT)
        if keyboard_layout is None:
            keyboard_layout = self.__settings.get(SETTING_DEFAULT_KEYBOARD_LAYOUT)
        self.__keyboard_layout = KeyboardLayoutDelegate.get_instance(keyboard_layout)

        # Here we only append user hotkeys.
        # For system hotkeys which is changed, update when registering.
        self.__append_user_hotkeys()

    @property
    def last_error(self) -> "HotkeyRegistry.Result":
        """
        Error code for last hotkey command.
        """
        return self.__last_error

    @property
    def keyboard_layout(self) -> Optional[KeyboardLayoutDelegate]:
        """
        Current keyboard layout object in using.
        """
        return self.__keyboard_layout

    def switch_layout(self, layout_name: str) -> None:
        """
        Change keyboard layout.

        Args:
            layout_name (str): Name of keyboard layout to use.
        """

        def __get_layout_keys() -> List[Hotkey]:
            # Ignore user hotkeys and modified hotkeys
            return [hotkey for hotkey in self._hotkeys if not self.is_user_hotkey(hotkey) and self.get_hotkey_default(hotkey)[0] == hotkey.key_combination.id]

        layout = KeyboardLayoutDelegate.get_instance(layout_name)
        if not layout or layout == self.__keyboard_layout:
            return

        carb.log_info(f"Change keyboard layout to {layout_name}")

        # Restore hotkey key combination to default
        pending_hotkeys = []
        for hotkey in __get_layout_keys():
            pending_register = False
            # Restore key combination
            if self.__keyboard_layout:
                restore_key_combination = self.__keyboard_layout.restore_key(hotkey.key_combination)
                if restore_key_combination:
                    pending_hotkeys.append((hotkey, hotkey.key_combination))
                    pending_register = True
                    hotkey.key_combination = restore_key_combination
                    self.__default_key_combinations[hotkey.id] = restore_key_combination.id

            # Map to new key combination
            new_key_combination = layout.map_key(hotkey.key_combination)
            if new_key_combination:
                if not pending_register:
                    pending_hotkeys.append((hotkey, hotkey.key_combination))
                hotkey.key_combination = new_key_combination
                self.__default_key_combinations[hotkey.id] = new_key_combination.id

        # Deregister old key combination all first
        # Otherwise new key combination may be deregistered (OMPE-21262)
        for update_hotkey, old_key_combination in pending_hotkeys:
            old_hotkey = copy.copy(update_hotkey)
            old_hotkey.key_combination = old_key_combination
            self.__deregister_hotkey_maps(old_hotkey)

        # Register new key combination and send update event
        for update_hotkey, _ in pending_hotkeys:
            self.__register_hotkey_maps(update_hotkey)
            self._send_event(HOTKEY_CHANGED_GLOBAL_EVENT, update_hotkey)

        self.__keyboard_layout = layout
        self.__settings.set("/persistent" + SETTING_DEFAULT_KEYBOARD_LAYOUT, layout_name)

    def register_hotkey(self, *args, **kwargs) -> Optional[Hotkey]:
        """
        Register hotkey by hotkey object or arguments.

        Args could be:

        .. code:: python

            register_hotkey(hotkey: Hotkey)

        or

        .. code:: python

            register_hotkey(
                hotkey_ext_id: str,
                key: Union[str, KeyCombination],
                action_ext_id: str,
                action_id: str,
                filter: Optional[HotkeyFilter] = None
            )

        Returns:
            Created hotkey object if register succeeded. Otherwise return None.
        """
        return self._register_hotkey_obj(args[0]) if len(args) == 1 else self._register_hotkey_args(*args, **kwargs)

    def edit_hotkey(
        self,
        hotkey: Hotkey,
        key: Union[str, KeyCombination],
        filter: Optional[HotkeyFilter]  # noqa: A002 # pylint: disable=redefined-builtin
    ) -> "HotkeyRegistry.Result":
        """
        Change key combination of hotkey object.

        Args:
            hotkey (Hotkey): Hotkey object to change.
            key (Union[str, KeyCombination]): New key combination.
            filter (Optional[HotkeyFiler]): New filter.

        Returns:
            Result code.
        """
        key_combination = KeyCombination(key) if isinstance(key, str) else key
        self.__last_error = self.verify_hotkey(hotkey, key_combination=key_combination, hotkey_filter=filter)
        if self.__last_error != HotkeyRegistry.Result.OK:
            return self.__last_error

        self.__edit_hotkey_internal(hotkey, key_combination, filter)

        self.__hotkey_storage.edit_hotkey(hotkey)

        return HotkeyRegistry.Result.OK

    def __edit_hotkey_internal(
        self,
        hotkey: Hotkey,
        key_combination: KeyCombination,
        filter: Optional[HotkeyFilter]  # noqa: A002 # pylint: disable=redefined-builtin
    ) -> None:
        self.__deregister_hotkey_maps(hotkey)
        hotkey.key_combination = key_combination
        hotkey.filter = filter
        self.__register_hotkey_maps(hotkey)
        self._send_event(HOTKEY_CHANGED_GLOBAL_EVENT, hotkey)

    def deregister_hotkey(self, *args, **kwargs) -> bool:
        """
        Deregister hotkey by hotkey object or arguments.

        Args could be:

        .. code:: python

            deregister_hotkey(hotkey: Hotkey)

        or

        .. code:: python

            deregister_hotkey(
                hotkey_ext_id: str,
                key: Union[str, KeyCombination],
                filter: Optional[HotkeyFilter] = None
            )

        Returns:
            True if hotkey found. Otherwise return False.
        """
        return self._deregister_hotkey_obj(args[0]) if len(args) == 1 else self._deregister_hotkey_args(*args, **kwargs)

    def deregister_hotkeys(self, hotkey_ext_id: str, key: Union[str, KeyCombination]) -> None:
        """
        Deregister hotkeys registered from a special extension with special key combination.

        Args:
            hotkey_ext_id (str): Extension id that hotkeys belongs to.
            key (Union[str, KeyCombination]): Key combination.
        """
        discovered_hotkeys = self.get_hotkeys(hotkey_ext_id, key)
        for hotkey in discovered_hotkeys:
            self._deregister_hotkey_obj(hotkey)

    def deregister_all_hotkeys_for_extension(self, hotkey_ext_id: Optional[str]) -> None:
        """
        Deregister hotkeys registered from a special extension.

        Args:
            hotkey_ext_id (Optional[str]): Extension id that hotkeys belongs to. If None, discover all global hotkeys
        """
        discovered_hotkeys = self.get_all_hotkeys_for_extension(hotkey_ext_id)
        for hotkey in discovered_hotkeys:
            self._deregister_hotkey_obj(hotkey)

    def deregister_all_hotkeys_for_filter(self, filter: HotkeyFilter) -> None:  # noqa: A002 # pylint: disable=redefined-builtin
        """
        Deregister hotkeys registered with speicial filter.

        Args:
            filter (HotkeyFilter): Hotkey HotkeyFilter.
        """
        discovered_hotkeys = self.get_all_hotkeys_for_filter(filter)
        for hotkey in discovered_hotkeys:
            self._deregister_hotkey_obj(hotkey)

    def get_hotkey(self, hotkey_ext_id: str, key: Union[str, KeyCombination], filter: Optional[HotkeyFilter] = None) -> Optional[Hotkey]:  # noqa: A002 # pylint: disable=redefined-builtin
        """
        Discover a registered hotkey.

        Args:
            hotkey_ext_id (str): Extension id which owns the hotkey.
            key (Union[str, KeyCombination]): Key combination.

        Keyword Args:
            filter (Optional[HotkeyFilter]): Hotkey filter. Default None

        Returns:
            Hotkey object if discovered. Otherwise None.
        """
        key_combination = KeyCombination(key) if isinstance(key, str) else key
        for hotkey in self._hotkeys:
            if hotkey.hotkey_ext_id == hotkey_ext_id and hotkey.key_combination == key_combination and hotkey.filter == filter:
                return hotkey
        return None

    def get_hotkey_for_trigger(self, key: Union[str, KeyCombination], context: Optional[str] = None, window: Optional[str] = None) -> Optional[Hotkey]:
        """
        Discover hotkey for trigger from key combination and filter.

        Args:
            key (Union[str, KeyCombination]): Key combination.

        Keyword Args:
            context (str): Context assigned to Hotkey
            window (str): Window assigned to Hotkey

        Returns:
            Hotkey object if discovered. Otherwise None.
        """
        key_combination = KeyCombination(key) if isinstance(key, str) else key
        if context:
            return (
                self._hotkeys_by_key_and_context[key_combination][context]
                if key_combination in self._hotkeys_by_key_and_context and context in self._hotkeys_by_key_and_context[key_combination]
                else None
            )
        if window:
            return (
                self._hotkeys_by_key_and_window[key_combination][window]
                if key_combination in self._hotkeys_by_key_and_window and window in self._hotkeys_by_key_and_window[key_combination]
                else None
            )
        return self._global_hotkeys_by_key[key_combination] if key_combination in self._global_hotkeys_by_key else None

    def get_hotkey_for_filter(self, key: Union[str, KeyCombination], filter: HotkeyFilter) -> Optional[Hotkey]:  # noqa: A002 # pylint: disable=redefined-builtin
        """
        Discover hotkey registered with special key combination and filter

        Args:
            key (Union[str, KeyCombination]): Key combination.
            filter (HotkeyFilter): Hotkey filter.

        Returns:
            First discovered hotkey. None if nothing found.
        """
        if filter:
            if filter.context:
                return self.get_hotkey_for_trigger(key, context=filter.context)
            if filter.windows:
                for window in filter.windows:
                    found = self.get_hotkey_for_trigger(key, window=window)
                    if found:
                        return found
                return None
        return self.get_hotkey_for_trigger(key)

    def get_hotkeys(self, hotkey_ext_id: str, key: Union[str, KeyCombination]) -> List[Hotkey]:
        """
        Discover hotkeys registered from a special extension with special key combination.

        Args:
            hotkey_ext_id (str): Extension id that hotkeys belongs to.
            key (Union[str, KeyCombination]): Key combination.

        Returns:
            List of discovered hotkeys.
        """
        key_combination = KeyCombination(key) if isinstance(key, str) else key
        return [hotkey for hotkey in self._hotkeys if hotkey.hotkey_ext_id == hotkey_ext_id and hotkey.key_combination == key_combination]

    def get_all_hotkeys(self) -> List[Hotkey]:
        """
        Discover all registered hotkeys.

        Returns:
            List of all registered hotkeys.
        """
        return self._hotkeys

    def get_all_hotkeys_for_extension(self, hotkey_ext_id: Optional[str]) -> List[Hotkey]:
        """
        Discover hotkeys registered from a special extension.

        Args:
            hotkey_ext_id (Optional[str]): Extension id that hotkeys belongs to. If None, discover all global hotkeys

        Returns:
            List of discovered hotkeys.
        """
        return [hotkey for hotkey in self._hotkeys if hotkey.filter is None] if hotkey_ext_id is None \
            else [hotkey for hotkey in self._hotkeys if hotkey.hotkey_ext_id == hotkey_ext_id]

    def get_all_hotkeys_for_key(self, key: Union[str, KeyCombination]) -> List[Hotkey]:
        """
        Discover hotkeys registered from a special key.

        Args:
            key (Union[str, KeyCombination]): Key combination.

        Returns:
            List of discovered hotkeys.
        """
        key_combination = KeyCombination(key) if isinstance(key, str) else key
        return [hotkey for hotkey in self._hotkeys if hotkey.key_combination == key_combination]

    def get_all_hotkeys_for_filter(self, filter: HotkeyFilter) -> List[Hotkey]:  # noqa: A002 # pylint: disable=redefined-builtin
        """
        Discover hotkeys registered with speicial filter.

        Args:
            filter (HotkeyFilter): Hotkey HotkeyFilter.

        Returns:
            List of discovered hotkeys.
        """
        return [hotkey for hotkey in self._hotkeys if hotkey.filter == filter]

    def disable_hotkey(self, hotkey: Hotkey) -> bool:
        """
        Disable a system hotkey.
        Disable means:
        - Deregister the hotkey immediately
        - If the hotkey is a system hotkey, do not make it work even register again until preset reset

        Args:
            hotkey [Hotkey]: Hotkey object

        Returns:
            True if hotkey found. Otherwise return False.
        """
        is_system_hotkey = not self.__hotkey_storage.is_user_hotkey(hotkey)
        if is_system_hotkey:
            default_key_combination = KeyCombination(self.__default_key_combinations[hotkey.id]) if hotkey.id in self.__default_key_combinations else None
        result = self._deregister_hotkey_obj(hotkey)
        if result and is_system_hotkey:
            self.__hotkey_storage.disable_hotkey(hotkey)
            # Restore key and save for restore defaults
            if default_key_combination:
                hotkey.key_combination = default_key_combination
            self.__disabled_hotkeys[hotkey.id] = hotkey
        return result

    def _register_hotkey_obj(self, hotkey: Hotkey) -> Optional[Hotkey]:
        self.__last_error = self.has_duplicated_hotkey(hotkey)
        if self.__last_error != HotkeyRegistry.Result.OK:
            carb.log_warn(f"[Hotkey] Cannot register {hotkey}, error code: {self.__last_error}")
            return None

        # Record default key binding and filter
        default_key_combination = hotkey.key_combination
        default_filter = hotkey.filter

        # Update key binding from keyboard layout
        if self.__keyboard_layout and not self.is_user_hotkey(hotkey):
            new_key_combination = self.__keyboard_layout.map_key(hotkey.key_combination)
            if new_key_combination:
                hotkey.key_combination = new_key_combination
                default_key_combination = new_key_combination

        # Update key binding/filter definition from storage
        user_hotkey = self.__hotkey_storage.get_hotkey(hotkey)
        if user_hotkey:
            if not user_hotkey.key_text:
                carb.log_info(f"[Hotkey] {hotkey.action_text}.{hotkey.key_text} is disabled")
                self.__default_key_combinations[hotkey.id] = default_key_combination.id
                self.__default_filters[hotkey.id] = default_filter
                self.__disabled_hotkeys[hotkey.id] = hotkey
                return None
            if hotkey.key_combination != user_hotkey.key_combination:
                carb.log_info(f"[Hotkey] Replace {hotkey.action_text}.{hotkey.key_text} with {user_hotkey.key_text}")
                hotkey.key_combination = user_hotkey.key_combination
            if hotkey.filter != user_hotkey.filter:
                carb.log_info(f"[Hotkey] Replace {hotkey.action_text}.{hotkey.filter_text} with {user_hotkey.filter_text}")
                hotkey.filter = user_hotkey.filter

        self.__last_error = self.verify_hotkey(hotkey)
        if self.__last_error != HotkeyRegistry.Result.OK:
            carb.log_warn(f"[Hotkey] Cannot register {hotkey}, error code: {self.__last_error}")
            return None

        # Append hotkey
        self._hotkeys.append(hotkey)
        self.__default_key_combinations[hotkey.id] = default_key_combination.id
        self.__default_filters[hotkey.id] = default_filter

        self.__register_hotkey_maps(hotkey)

        # Save to storage
        self.__hotkey_storage.register_user_hotkey(hotkey)

        self._send_event(HOTKEY_REGISTER_GLOBAL_EVENT, hotkey)
        return hotkey

    def _register_hotkey_args(
        self,
        hotkey_ext_id: str,
        key: Union[str, KeyCombination],
        action_ext_id: str,
        action_id: str,
        filter: Optional[HotkeyFilter] = None  # noqa: A002 # pylint: disable=redefined-builtin
    ) -> Optional[Hotkey]:
        hotkey = Hotkey(hotkey_ext_id, key, action_ext_id, action_id, filter=filter)
        return self._register_hotkey_obj(hotkey)

    def _deregister_hotkey_obj(self, hotkey: Hotkey) -> bool:
        if hotkey in self._hotkeys:
            self._hotkeys.remove(hotkey)
            self.__deregister_hotkey_maps(hotkey)
            self.__default_key_combinations.pop(hotkey.id)
            self.__default_filters.pop(hotkey.id)
            self.__hotkey_storage.deregister_hotkey(hotkey)

            self._send_event(HOTKEY_DEREGISTER_GLOBAL_EVENT, hotkey)
            return True
        return False

    def _deregister_hotkey_args(
        self,
        hotkey_ext_id: str,
        key: Union[str, KeyCombination],
        filter: Optional[HotkeyFilter] = None  # noqa: A002 # pylint: disable=redefined-builtin
    ) -> bool:
        hotkey = self.get_hotkey(hotkey_ext_id, key, filter=filter)
        return self._deregister_hotkey_obj(hotkey) if hotkey else False

    def _send_event(self, event: str, hotkey: Hotkey):
        omni.kit.app.queue_event(event, payload={
            "hotkey_ext_id": hotkey.hotkey_ext_id,
            "key": hotkey.key_combination.as_string,
            "trigger_press": hotkey.key_combination.trigger_press,
            "action_ext_id": hotkey.action.extension_id if hotkey.action else "",
            "action_id": hotkey.action.id if hotkey.action else "",
        })

    def __register_hotkey_maps(self, hotkey: Hotkey) -> None:
        if hotkey.key_combination.key == "":
            return
        if hotkey.filter is None:
            self._global_hotkeys_by_key[hotkey.key_combination] = hotkey
        else:
            if hotkey.filter.context:
                if hotkey.key_combination not in self._hotkeys_by_key_and_context:
                    self._hotkeys_by_key_and_context[hotkey.key_combination] = {}
                if hotkey.filter.context in self._hotkeys_by_key_and_context[hotkey.key_combination]:
                    carb.log_warn(f"Hotkey {hotkey.key_combination.as_string} to context {hotkey.filter.context} already exists: ")
                    old_hotkey = self._hotkeys_by_key_and_context[hotkey.key_combination][hotkey.filter.context]
                    carb.log_warn(f"    existing from {old_hotkey.hotkey_ext_id}")
                    carb.log_warn(f"    replace with the one from {hotkey.hotkey_ext_id}")
                self._hotkeys_by_key_and_context[hotkey.key_combination][hotkey.filter.context] = hotkey
            if hotkey.filter.windows:
                if hotkey.key_combination not in self._hotkeys_by_key_and_window:
                    self._hotkeys_by_key_and_window[hotkey.key_combination] = {}
                for window in hotkey.filter.windows:
                    if window in self._hotkeys_by_key_and_window[hotkey.key_combination]:
                        carb.log_warn(f"Hotkey {hotkey.key_combination.as_string} to window {window} already exists: ")
                        old_hotkey = self._hotkeys_by_key_and_window[hotkey.key_combination][window]
                        carb.log_warn(f"    existing from {old_hotkey.hotkey_ext_id}")
                        carb.log_warn(f"    replace with the one from {hotkey.hotkey_ext_id}")
                    self._hotkeys_by_key_and_window[hotkey.key_combination][window] = hotkey

    def __deregister_hotkey_maps(self, hotkey: Hotkey) -> bool:
        if hotkey.key_combination.key == "":
            return
        if hotkey.filter:
            if hotkey.filter.context \
                    and hotkey.filter.context in self._hotkeys_by_key_and_context[hotkey.key_combination] \
                    and self._hotkeys_by_key_and_context[hotkey.key_combination][hotkey.filter.context] == hotkey:
                self._hotkeys_by_key_and_context[hotkey.key_combination].pop(hotkey.filter.context)
            if hotkey.filter.windows:
                for window in hotkey.filter.windows:
                    if window in self._hotkeys_by_key_and_window[hotkey.key_combination] \
                            and self._hotkeys_by_key_and_window[hotkey.key_combination][window] == hotkey:
                        self._hotkeys_by_key_and_window[hotkey.key_combination].pop(window)
        else:
            if hotkey.key_combination in self._global_hotkeys_by_key:
                self._global_hotkeys_by_key.pop(hotkey.key_combination)

    def __append_user_hotkeys(self):
        user_hotkeys = self.__hotkey_storage.get_user_hotkeys()
        for hotkey in user_hotkeys:
            self._hotkeys.append(hotkey)
            self.__default_key_combinations[hotkey.id] = hotkey.key_combination.id
            self.__default_filters[hotkey.id] = hotkey.filter
            self.__register_hotkey_maps(hotkey)

    def clear_storage(self) -> None:
        """
        Clear user defined hotkeys.
        """
        user_hotkeys = self.__hotkey_storage.get_user_hotkeys()
        for hotkey in user_hotkeys:
            if hotkey in self._hotkeys:
                self._hotkeys.remove(hotkey)
                self.__deregister_hotkey_maps(hotkey)
                self.__default_key_combinations.pop(hotkey.id)
                self.__default_filters.pop(hotkey.id)
        self.__hotkey_storage.clear_hotkeys()

    def export_storage(self, url: str) -> None:
        """
        Export user defined hotkeys to file.

        Args:
            url (str): File path to export user defined hotkeys.
        """
        self.__hotkey_storage.save_preset(url)

    def import_storage(self, url: str) -> bool:
        """
        Import user defined hotkeys from file.

        Args:
            url (str): File path to import user defined hotkeys.
        """
        preset = self.__hotkey_storage.preload_preset(url)
        if preset is None:
            return False

        # First we need to restore all hotkeys
        self.restore_defaults()

        self.__hotkey_storage.load_preset(preset)
        # For system hotkeys, change to new definition in preset
        for hotkey in self._hotkeys:
            user_hotkey = self.__hotkey_storage.get_hotkey(hotkey)
            if user_hotkey:
                self.__deregister_hotkey_maps(hotkey)
                if hotkey.key_combination != user_hotkey.key_combination:
                    carb.log_info(f"[Hotkey] Replace {hotkey.action_text}.{hotkey.key_text} with {user_hotkey.key_text}")
                    hotkey.key_combination = user_hotkey.key_combination
                if hotkey.filter != user_hotkey.filter:
                    carb.log_info(f"[Hotkey] Replace {hotkey.action_text}.{hotkey.filter_text} with {user_hotkey.filter_text}")
                    hotkey.filter = user_hotkey.filter
                self.__register_hotkey_maps(hotkey)
        # Append user hotkeys
        self.__append_user_hotkeys()

        return True

    def has_duplicated_hotkey(self, hotkey: Hotkey) -> "HotkeyRegistry.Result":
        """
        Check if already have hotkey registered.

        Args:
            hotkey (Hotkey): Hotkey object to check.

        Returns:
            Result code.
        """
        exist_hotkey = self.__default_key_combinations.get(hotkey.id, None)
        if exist_hotkey and hotkey.id not in self.__disabled_hotkeys:
            carb.log_warn(f"[Hotkey] duplicated action as {exist_hotkey} with {hotkey.id}!")
            return HotkeyRegistry.Result.ERROR_ACTION_DUPLICATED
        return HotkeyRegistry.Result.OK

    def verify_hotkey(self, hotkey: Hotkey, key_combination: Optional[KeyCombination] = None, hotkey_filter: Optional[HotkeyFilter] = None) -> "HotkeyRegistry.Result":
        """
        Verify hotkey.
        """
        if not hotkey.action_text:
            return HotkeyRegistry.Result.ERROR_NO_ACTION

        if key_combination is None:
            key_combination = hotkey.key_combination
        if not key_combination.is_valid:
            return HotkeyRegistry.Result.ERROR_KEY_INVALID

        if key_combination.key != "":
            hotkey_filter = hotkey.filter if hotkey_filter is None else hotkey_filter
            found = self.get_hotkey_for_filter(key_combination, hotkey_filter)
            if found and found.id != hotkey.id:
                carb.log_warn(f"[Hotkey] duplicated key:'{key_combination}'")
                carb.log_warn(f"  -- {hotkey}")
                carb.log_warn(f"  -- {found}")
                return HotkeyRegistry.Result.ERROR_KEY_DUPLICATED

        return HotkeyRegistry.Result.OK

    def get_hotkey_default(self, hotkey: Hotkey) -> Tuple[str, HotkeyFilter]:
        """
        Discover hotkey default key binding and filter.

        Args:
            hotkey (Hotkey): Hotkey object.

        Returns:
            Tuple of key binding string and hotkey filter object.
        """
        return (
            self.__default_key_combinations.get(hotkey.id, None),
            self.__default_filters.get(hotkey.id, None)
        )

    def restore_defaults(self) -> None:
        """
        Clean user defined hotkeys and restore system hotkey to default
        """
        to_remove_hotkeys = []
        for hotkey in self._hotkeys:
            saved_hotkey = self.__hotkey_storage.get_hotkey(hotkey)
            if saved_hotkey:
                if self.__hotkey_storage.is_user_hotkey(hotkey):
                    # User-defined hotkey, remove later
                    self.__deregister_hotkey_maps(hotkey)
                    self.__default_key_combinations.pop(hotkey.id, None)
                    self.__default_filters.pop(hotkey.id, None)
                    to_remove_hotkeys.append(hotkey)
                    self._send_event(HOTKEY_DEREGISTER_GLOBAL_EVENT, hotkey)
                else:
                    # System hotkey, restore key-bindings and filter
                    self.__deregister_hotkey_maps(hotkey)
                    if hotkey.id in self.__default_key_combinations:
                        hotkey.key_combination = KeyCombination(self.__default_key_combinations[hotkey.id])
                    if hotkey.id in self.__default_filters:
                        hotkey.filter = self.__default_filters[hotkey.id]
                    self._send_event(HOTKEY_CHANGED_GLOBAL_EVENT, hotkey)
                    self.__register_hotkey_maps(hotkey)

        for hotkey in to_remove_hotkeys:
            self._hotkeys.remove(hotkey)

        self.__hotkey_storage.clear_hotkeys()

        # Register disabled system hotkeys
        for (_, hotkey) in self.__disabled_hotkeys.items():
            self._register_hotkey_obj(hotkey)

    def is_user_hotkey(self, hotkey: Hotkey) -> bool:
        """
        If a user defined hotkey.

        Args:
            hotkey (Hotkey): Hotkey object.

        Returns:
            True if user defined. Otherwise False.
        """
        return self.__hotkey_storage.is_user_hotkey(hotkey)
