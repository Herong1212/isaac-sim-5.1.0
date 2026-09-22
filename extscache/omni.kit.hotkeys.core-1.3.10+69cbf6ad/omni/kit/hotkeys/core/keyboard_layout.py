import abc
from typing import Dict, List, Optional
import weakref

import carb.input

from .key_combination import KeyCombination


class KeyboardLayoutDelegate(abc.ABC):
    """Base class for keyboard layout delegates and registry of these same delegate instances.
    Whenever an instance of this class is created, it is automatically registered.
    """

    __g_registered = []

    @classmethod
    def get_instances(cls) -> List["KeyboardLayoutDelegate"]:
        remove = []
        for wref in KeyboardLayoutDelegate.__g_registered:
            obj = wref()
            if obj:
                yield obj
            else:
                remove.append(wref)
        for wref in remove:
            KeyboardLayoutDelegate.__g_registered.remove(wref)

    @classmethod
    def get_instance(cls, name: str) -> Optional["KeyboardLayoutDelegate"]:
        for inst in KeyboardLayoutDelegate.get_instances():
            if inst.get_name() == name:
                return inst
        return None

    def __init__(self):
        self.__g_registered.append(weakref.ref(self, lambda r: KeyboardLayoutDelegate.__g_registered.remove(r)))  # noqa: PLW0108 # pylint: disable=unnecessary-lambda
        self._maps = self.get_maps()
        self._restore_maps = {value: key for (key, value) in self._maps.items()}

    def __del__(self):
        self.destroy()

    def destroy(self):
        for wref in KeyboardLayoutDelegate.__g_registered:
            if wref() == self:
                KeyboardLayoutDelegate.__g_registered.remove(wref)
                break

    @abc.abstractmethod
    def get_name(self) -> str:
        return ""

    @abc.abstractmethod
    def get_maps(self) -> dict:
        return {}

    def map_key(self, key: KeyCombination) -> Optional[KeyCombination]:
        return KeyCombination(self._maps[key.key], modifiers=key.modifiers, trigger_press=key.trigger_press) if key.key in self._maps else None

    def restore_key(self, key: KeyCombination) -> Optional[KeyCombination]:
        return KeyCombination(self._restore_maps[key.key], modifiers=key.modifiers, trigger_press=key.trigger_press) if key.key in self._restore_maps else None


class USKeyboardLayout(KeyboardLayoutDelegate):
    def get_name(self) -> str:
        return "U.S. QWERTY"

    def get_maps(self) -> Dict[carb.input.KeyboardInput, carb.input.KeyboardInput]:
        return {}


class GermanKeyboardLayout(KeyboardLayoutDelegate):
    def get_name(self) -> str:
        return "German QWERTZ"

    def get_maps(self) -> Dict[carb.input.KeyboardInput, carb.input.KeyboardInput]:
        return {
            carb.input.KeyboardInput.Z: carb.input.KeyboardInput.Y,
            carb.input.KeyboardInput.Y: carb.input.KeyboardInput.Z,
        }


class FrenchKeyboardLayout(KeyboardLayoutDelegate):
    def get_name(self) -> str:
        return "French AZERTY"

    def get_maps(self) -> Dict[carb.input.KeyboardInput, carb.input.KeyboardInput]:
        return {
            carb.input.KeyboardInput.Q: carb.input.KeyboardInput.A,
            carb.input.KeyboardInput.W: carb.input.KeyboardInput.Z,
            carb.input.KeyboardInput.A: carb.input.KeyboardInput.Q,
            carb.input.KeyboardInput.Z: carb.input.KeyboardInput.W,
        }
