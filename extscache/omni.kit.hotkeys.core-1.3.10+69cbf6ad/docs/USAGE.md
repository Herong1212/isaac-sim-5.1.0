# Usage Examples


## Register Hotkeys

```
hotkey_registry = omni.kit.hotkeys.core.get_hotkey_registry()

# Register a global hotkey: trigger action when CTRL + N pressed
hotkey_registry.register_hotkey(
    "your_extension_id",
    "CTRL + N",
    "execute_action_extension_id",
    "execute_action_id",
    filter=None,
)

# Register a local hotkey: trigger action only "Test Window" focused and CTRL + N pressed
hotkey_registry.register_hotkey(
    "your_extension_id",
    "CTRL + N",
    "execute_action_extension_id",
    "execute_action_id",
    filter=HotkeyFilter(windows=["Test Window"]),
)
```

## Deregister Hotkeys

```
hotkey_registry = omni.kit.hotkeys.core.get_hotkey_registry()

# Deregister a hotkey directly...
hotkey_registry.deregister_hotkey("your_extension_id", "CTRL + N", filter=None)

# or hotkeys registered from a special extension....
action_registry.deregister_all_hotkeys_for_extension("your_extension_id")
```
