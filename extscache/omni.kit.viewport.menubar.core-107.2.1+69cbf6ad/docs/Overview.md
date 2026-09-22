```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension provides a comprehensive system for creating and managing custom menu bars and items within the viewport UI in Omniverse Kit applications. It includes a variety of utility classes and functions to create both simple and complex menu items, including sliders, checkboxes, combo boxes, and more.

## Important API List
The module consists of the following main components:
- **ViewportMenuBarExtension** : Manages the lifecycle of the viewport menubar and its items.
- **get_instance** : Retrieves the singleton instance of the viewport menubar core extension.

### Menubar Items
- **ViewportMenubar** : Represents a viewport menubar that can contain multiple menu items.
- **ViewportMenuSpacer** : A spacer item for layout purposes within a viewport menubar.
- **ViewportMenuContainer** : A menu container within a viewport menubar.
- **ViewportMenuItem** : A general menu item within a viewport menubar.
- **CategoryMenuContainer** : A menu container for category menu items.
- **FloatArraySettingColorMenuItem** : A menu item to show/change colors from carb.settings.
- **RadioMenuCollection** : A menu collection for radio menu items.
- **SelectableMenuItem** : A menu item can be selected.
- **ViewportButtonItem** : A menu item has a button with flyout window or drop-down menu.
- **ViewportMenuSeparator** : A separator item for layout purposes within a menubar.

### Menubar Delegates
- **ViewportMenuDelegate** : A basic menu delegate within a viewport menubar.
- **CategoryMenuDelegate** : A menu delegate for category within a viewport menubar.
- **CheckboxMenuDelegate** : A menu delegate that creates checkbox within a viewport menubar.
- **ColorMenuDelegate** : A menu delegate that creates color picker within a viewport menubar.
- **ComboBoxMenuDelegate** : A menu delegate that creates combobox within a viewport menubar.
- **IconMenuDelegate** : A menu delegate that creates icon and and optionally text within a viewport menubar.
- **LabelMenuDelegate** : A menu delegate that creates label within a viewport menubar.
- **SeparatorDelegate** : A menu delegate that creates separator between items within a viewport menubar.
- **SliderMenuDelegate** : A menu delegate that creates slider within a viewport menubar.
- **SpinnerMenuDelegate** : A menu delegate that creates spinner within a viewport menubar.

### Menubar Models
- **SettingModel** : A data model for simple scalar/POD carb.settings.
- **SettingModelWithDefaultValue** : A setting model with default value.
- **USDBoolAttributeModel** : A simple value model to watch the boolean attribute..
- **USDFloatAttributeModel** : A simple value model to watch the float attribute..
- **USDIntAttributeModel** :A simple value model to watch the integer attribute..
- **USDStringAttributeModel** : A simple value model to watch the string attribute.
- **USDMetadataModel** : "A simple value model to watch the specified metadata..
- **CategoryCollectionItem** : A data item for category collection with all/mixed/empty states.
- **CategoryCustomItem** : A data item for user-defined category.
- **CategoryStateItem** : A data item for managing category state (checked/unchecked).
- **SimpleCategoryModel** : A data model for managing category items.
- **ComboBoxItem** : A data item for a single item in combobox drop list.
- **ComboBoxModel** : A data model for items in combobox drop list.
- **SettingComboBoxModel** : A data model for items in combobox drop list and get/set value from/to a setting path.
- **SimpleListItem** : A single item in list model.
- **SimpleListModel** : A simple data model contains list of values.

## General Use Case
Developers can use this extension to create dynamic, customizable menu bars within the viewport UI of Omniverse Kit applications. Menu items can be linked to application settings, USD attributes, or other functionalities to provide users with interactive and convenient controls directly within the viewport. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)