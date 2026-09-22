# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
Omni Kit Hotkeys Core
---------------------

Omni Kit Hotkeys Core is a framework for creating, registering, and discovering hotkeys.

Here is an example of registering an hokey from Python that execute action "omni.kit.window.file::new" to create a new file when CTRL + N pressed:

.. code-block::

    hotkey_registry = omni.kit.hotkeys.core.get_hotkey_registry()

    hotkey_registry.register_hotkey(
        "your_extension_id",
        "CTRL + N",
        "omni.kit.window.file",
        "new",
        filter=None,
    )

For more examples, please consult the Usage Examples page.
"""

from .key_combination import KeyCombination
from .hotkey import Hotkey
from .registry import HotkeyRegistry
from .filter import HotkeyFilter
from .extension import HotkeysExtension, get_hotkey_context, get_hotkey_registry
from .event import HOTKEY_REGISTER_EVENT, HOTKEY_REGISTER_GLOBAL_EVENT, HOTKEY_DEREGISTER_EVENT, HOTKEY_DEREGISTER_GLOBAL_EVENT, HOTKEY_CHANGED_EVENT, HOTKEY_CHANGED_GLOBAL_EVENT
from .keyboard_layout import KeyboardLayoutDelegate


__all__ = [
    "KeyCombination",
    "Hotkey",
    "HotkeyRegistry",
    "HotkeyFilter",
    "KeyboardLayoutDelegate",
    "get_hotkey_context",
    "get_hotkey_registry",
    "HOTKEY_REGISTER_EVENT",
    "HOTKEY_REGISTER_GLOBAL_EVENT",
    "HOTKEY_DEREGISTER_EVENT",
    "HOTKEY_DEREGISTER_GLOBAL_EVENT",
    "HOTKEY_CHANGED_EVENT",
    "HOTKEY_CHANGED_GLOBAL_EVENT",
]
