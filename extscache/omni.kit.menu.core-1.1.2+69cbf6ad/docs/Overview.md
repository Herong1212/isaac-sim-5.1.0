```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.menu.core` module provides a set of tools and classes for creating and managing menus and used by omni.kit.menu.utils and omni.kit.context_menu. This includes support for read-only dictionaries, specialized menu items, icons with full paths and menu delegates with customizable styles and behaviors.

## Important API List
The module consists of the following main components:
- [DictReadOnly](omni.kit.menu.core/omni.kit.menu.core.DictReadOnly): A read-only dictionary that prevents accidental modifications.
- [IconMenuBaseDelegate](omni.kit.menu.core/omni.kit.menu.core.IconMenuBaseDelegate): A delegate class for creating menus with icons and customizable styles.
- [MenuEventType](omni.kit.menu.core/omni.kit.menu.core.MenuEventType): An enumeration class defining constants for various menu activation events.
- [has_delegate_func](omni.kit.menu.core/omni.kit.menu.core.has_delegate_func): A utility function to check if a delegate has a specific function.
- [uiMenu](omni.kit.menu.core/omni.kit.menu.core.uiMenu): A subclass of `ui.Menu` with additional properties for glyphs, checkable menus, hotkey texts, and submenus.
- [uiMenuItem](omni.kit.menu.core/omni.kit.menu.core.uiMenuItem): A subclass of `ui.MenuItem` with properties for glyphs, checkable menu items, hotkey texts, and parent menus.

## General Use Case
Users can utilize this module to create sophisticated and highly customizable menus within the Omniverse Kit SDK environment. The `DictReadOnly` class ensures that certain data remains immutable, which can be useful for configuration settings. The `IconMenuBaseDelegate` allows for the design of visually appealing menus with icons and various styling options. `MenuEventType` helps in managing different types of menu activation events. The `has_delegate_func` function is useful for dynamically checking the presence of methods in delegate objects. The `uiMenu` and `uiMenuItem` classes extend the basic menu and menu item functionalities provided by the Omniverse Kit SDK, enabling the creation of more complex and feature-rich menus. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)
- [](SETTINGS)
