__all__ = ["KeyCombination"]
from typing import Union, Optional, Dict, Tuple
import re
import carb
import carb.input

PREDEFINED_STRING_TO_KEYS: Dict[str, carb.input.Keyboard] = carb.input.KeyboardInput.__members__


class KeyCombination:
    """
    Key binding class.
    """
    def __init__(self, key: Union[str, carb.input.KeyboardInput], modifiers: int = 0, trigger_press: bool = True):
        """
        Create a key binding object.

        Args:
            key (Union[str, carb.input.KeyboardInput]): could be string or carb.input.KeyboardInput.
                if string, use "+" to join carb.input.KeyboardInput and modifiers, for example: "CTRL+D" or "CTRL+SHIFT+D"

        Keyword Args:
            modifiers (int): Represent combination of keyboard modifier flags, which could be:
                carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL
                carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT
                carb.input.KEYBOARD_MODIFIER_FLAG_ALT
                carb.input.KEYBOARD_MODIFIER_FLAG_SUPER

            trigger_press (bool): Trigger when key pressed if True. Otherwise trigger when key released. Default True.
        """
        self.key: Optional[carb.input.Keyboard] = None
        self.modifiers = 0

        if isinstance(key, str):
            (self.key, self.modifiers, self.trigger_press) = KeyCombination.from_string(key)
        else:
            self.modifiers = modifiers
            if key in [
                carb.input.KeyboardInput.LEFT_CONTROL,
                carb.input.KeyboardInput.RIGHT_CONTROL,
                carb.input.KeyboardInput.LEFT_SHIFT,
                carb.input.KeyboardInput.RIGHT_SHIFT,
                carb.input.KeyboardInput.LEFT_ALT,
                carb.input.KeyboardInput.RIGHT_ALT,
                carb.input.KeyboardInput.LEFT_SUPER,
                carb.input.KeyboardInput.RIGHT_SUPER,
            ]:
                self.key = ""
            else:
                self.key = key

        self.trigger_press = trigger_press

    @property
    def as_string(self) -> str:
        """
        Get string to describe key combination
        """
        if self.key is None:
            return ""
        descs = []
        if self.modifiers & carb.input.KEYBOARD_MODIFIER_FLAG_SUPER:
            descs.append("SUPER")
        if self.modifiers & carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT:
            descs.append("SHIFT")
        if self.modifiers & carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL:
            descs.append("CTRL")
        if self.modifiers & carb.input.KEYBOARD_MODIFIER_FLAG_ALT:
            descs.append("ALT")

        if self.key in PREDEFINED_STRING_TO_KEYS.values():
            key = list(PREDEFINED_STRING_TO_KEYS.keys())[list(PREDEFINED_STRING_TO_KEYS.values()).index(self.key)]
            # OM-67426: Remove "KEY_". For example, "KEY_1" to "1".
            if key.startswith("KEY_"):
                key = key[4:]
            descs.append(key)
        return " + ".join(descs)

    @property
    def id(self) -> str:  # noqa: A003
        """
        Identifier string of this key binding object.
        """
        return f"{self.as_string} (On " + ("Press" if self.trigger_press else "Release") + ")"

    @property
    def is_valid(self) -> bool:
        """
        If a valid key binding object.
        """
        return bool(self.key)

    def __repr__(self) -> str:
        return self.id

    def __eq__(self, other) -> bool:
        return isinstance(other, KeyCombination) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @staticmethod
    def from_string(key_string: str) -> Tuple[carb.input.KeyboardInput, int, bool]:
        """
        Get key binding information from a string.

        Args:
            key_string (str): String represent a key binding.

        Returns:
            Tuple of carb.input.KeyboardInput, modifiers and flag for press/release.
        """
        if key_string is None:
            carb.log_error("No key defined!")
            return (None, None, None)
        key_string = key_string.strip()
        if key_string == "":
            # Empty key string means no key
            return ("", 0, True)

        modifiers = 0
        key = None
        trigger_press = True

        m = re.search(r"(.*)\(on (press|release)\)", key_string, flags=re.IGNORECASE)
        if m:
            trigger = m.groups()[1]
            trigger_press = trigger.upper() == "PRESS"
            key_string = m.groups()[0]
        else:
            trigger_press = True

        key_descs = key_string.split("+")

        for desc in key_descs:
            desc = desc.strip().upper()
            if desc in ["CTRL", "CTL", "CONTROL"]:
                modifiers += carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL
            elif desc in ["SHIFT"]:
                modifiers += carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT
            elif desc in ["ALT"]:
                modifiers += carb.input.KEYBOARD_MODIFIER_FLAG_ALT
            elif desc in ["SUPER"]:
                modifiers += carb.input.KEYBOARD_MODIFIER_FLAG_SUPER
            elif desc in ["PRESS", "RELEASE"]:
                trigger_press = desc == "PRESS"
            elif desc in PREDEFINED_STRING_TO_KEYS:
                key = PREDEFINED_STRING_TO_KEYS[desc]
            elif desc in [str(i) for i in range(0, 10)]:
                # OM-67426: for numbers, convert to original key definition
                key = PREDEFINED_STRING_TO_KEYS["KEY_" + desc]
            elif desc == "":
                key = ""
            else:
                carb.log_warn(f"Unknown key definition '{desc}' in '{key_string}'")
                return (None, None, None)

        return (key, modifiers, trigger_press)

    @staticmethod
    def is_valid_key_string(key: str) -> bool:
        """
        If key string valid.

        Args:
            key (str): Key string to check.

        Returns:
            True if key string is valid. Otherwise False.
        """
        (key, modifiers, press) = KeyCombination.from_string(key)
        if key is None or modifiers is None or press is None:
            return False
        return True
