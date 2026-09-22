from typing import Optional, Union
import carb

from omni.kit.actions.core import get_action_registry, Action

from .key_combination import KeyCombination
from .filter import HotkeyFilter


class Hotkey:
    """
    Hotkey object class.
    """
    def __init__(
        self,
        hotkey_ext_id: str,
        key: Union[str, KeyCombination],
        action_ext_id: str,
        action_id: str,
        filter: Optional[HotkeyFilter] = None  # noqa: A002 # pylint: disable=redefined-builtin
    ):
        """
        Define a hotkey object.

        Args:
            hotkey_ext_id (str): Extension id which owns the hotkey.
            key (Union[str, KeyCombination]): Key combination.
            action_ext_id (str): Extension id which owns the action assigned to the hotkey.
            action_id (str): Action id assigned to the hotkey.

        Keyword Args:
            filter (Optional[HotkeyFilter]): Hotkey filter. Default None

        Returns:
            The hotkey object that was created.
        """
        self.hotkey_ext_id = hotkey_ext_id
        if key:
            self.key_combination = KeyCombination(key) if isinstance(key, str) else key
        else:
            self.key_combination = None

        # For user defined action, the extension may not loaded yet
        # So only save action id instead get real action here
        self.action_ext_id = action_ext_id
        self.action_id = action_id
        self.filter = filter

    @property
    def id(self) -> str:  # noqa: A003
        """
        Identifier string of this hotkey.
        """
        hotkey_id = f"{self.hotkey_ext_id}.{self.action_text}"
        if self.filter:
            hotkey_id += "." + str(self.filter)
        return hotkey_id

    @property
    def key_text(self) -> str:
        """
        String of key bindings assigned to this hotkey.
        """
        return self.key_combination.as_string if self.key_combination else ""

    @property
    def action_text(self) -> str:
        """
        String of action object assigned to this hotkey.
        """
        return self.action_ext_id + "::" + self.action_id if self.action_ext_id or self.action_id else ""

    @property
    def filter_text(self) -> str:
        """
        String of filter object assigned to this hotkey.
        """
        return str(self.filter) if self.filter else ""

    @property
    def action(self) -> Action:
        """
        Action object assigned to this hotkey.
        """
        if self.action_ext_id and self.action_id:
            action = get_action_registry().get_action(self.action_ext_id, self.action_id)
            if action is None:
                carb.log_warn(f"[Hotkey] Action '{self.action_ext_id}::{self.action_id}' not FOUND!")
            return action
        return None

    def execute(self) -> None:
        """
        Execute action assigned to the hotkey
        """
        if self.action:
            self.action.execute()

    def __eq__(self, other) -> bool:
        return isinstance(other, Hotkey)\
            and self.hotkey_ext_id == other.hotkey_ext_id \
            and self.key_combination == other.key_combination \
            and self.action_ext_id == other.action_ext_id \
            and self.action_id == other.action_id \
            and self.filter == other.filter

    def __repr__(self):
        basic_info = f"[{self.hotkey_ext_id}] {self.action_text}.{self.key_text}"
        if self.filter is None:
            return f"Global {basic_info}"
        return f"Local {basic_info} for {self.filter}"
