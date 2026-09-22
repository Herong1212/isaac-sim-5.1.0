```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The Omni Kit Hotkeys Core extension is a framework for creating, registering, and discovering hotkeys. Hotkeys are programmable objects include key binding, action and focus window. A hotkey can be created in one extension and then binded action can be executed when binded key pressed/released in desired window.

## Hotkeys

Hotkeys can be:
- Created, registered and discovered from any extension
- Edited, exported, imported

## Terms

- Local hotkey: Hotkey is executed in reference to an context rather that the application as a whole.
- Global hotkey: Hotkey will be executed no matter what "context" user is in
- Context: What window/tool/area the user is in. This is determined by Where the user's mouse is hover

Local Hotkeys can override (Global) Hotkeys. If same key binding defined in both local hotkey and global hotkey, it will trigger in order:
- Local hotkey if special window focused
- Otherwise global hotkey

## Hotkey Registry

The Hotkey Registry maintains a collection of all registered hotkeys and allows any extension to:
- Register new hotkeys.
- Deregister existing hotkeys.
- Discover registered hotkeys.
- Edit existing hotkeys to change key binding or associated window name

Here is an example of registering a global hokey from Python that execute action "omni.kit.window.file::new" to create a new file when CTRL + N pressed:

```
hotkey_registry = omni.kit.hotkeys.core.get_hotkey_registry()

hotkey_registry.register_hotkey(
    "your_extension_id",
    "CTRL + N",
    "omni.kit.window.file",
    "new",
    filter=None,
)
```

For more examples, please consult the [usage](USAGE) pages.
