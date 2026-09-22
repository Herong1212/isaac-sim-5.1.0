```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension provides 2 types of menu, OptionsMenu and RadioMenu.

```{mermaid}
graph TD;
    subgraph AbstractPopupMenu
        OptionsMenu
        RadioMenu
    end
    OptionsMenu --> OptionsModel
    RadioMenu --> RadioModel
    subgraph AbstractOptionItem
        OptionItem
        OptionCustom
        OptionRadios
        OptionSeparator
    end
    OptionsModel --> AbstractOptionItem
```

## Important API List
The module consists of the following main components:

### Menus
- [OptionsMenu](omni.kit.widget.options_menu/omni.kit.widget.options_menu.OptionsMenu): Represents a menu to show various options with a header and list of menu items.
- [RadioMenu](omni.kit.widget.options_menu/omni.kit.widget.options_menu.RadioMenu): Represents a menu specifically for radio button groups.

### Models
- [OptionsModel](omni.kit.widget.options_menu/omni.kit.widget.options_menu.OptionsModel): Model for managing a collection of option items within a menu.
- [RadioModel](omni.kit.widget.options_menu/omni.kit.widget.options_menu.RadioModel): Represents a model for radio buttons, enabling single selection from a list.

### Items for OptionsModel
- [OptionCustom](omni.kit.widget.options_menu/omni.kit.widget.options_menu.OptionCustom): Represents a custom option item with a build function and optional model.
- [OptionItem](omni.kit.widget.options_menu/omni.kit.widget.options_menu.OptionItem): Represents a general item for options menus, supporting features like checkability and visibility toggling.
- [OptionRadios](omni.kit.widget.options_menu/omni.kit.widget.options_menu.OptionRadios): Represents a list of radio options within a menu.
- [OptionSeparator](omni.kit.widget.options_menu/omni.kit.widget.options_menu.OptionSeparator): Represents a separator in menu items, optionally with a title.

### Delegate for menu item managed by OptionsMenu
- [OptionLabelMenuItemDelegate](omni.kit.widget.options_menu/omni.kit.widget.options_menu.OptionLabelMenuItemDelegate): A delegate for a normal menu item with additional spacing.

## General Use Case
This module can be utilized to create complex and customizable menu structures within applications. Developers can leverage the provided classes to build options menus with various types of items (e.g., toggles, radio buttons, custom input fields), separators for grouping, and support for saving and retrieving settings. The module's flexibility allows for the creation of both simple and advanced user interfaces, making it suitable for settings panels, application preferences, feature toggles, and more. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)