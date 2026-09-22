```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.widget.searchable_combobox` extension provides a set of classes and functions to create and manage a searchable ComboBox widget within Omniverse Kit applications. It supports item filtering based on user input and allows for custom theming and item representations.

## Important API List
The module consists of the following main components:
- **SearchModel**: A value model that supports searching functionality in UI components.
- **SearchWidget**: A widget providing a customizable searchable combobox.
- **ComboBoxListItem**: Represents a single item in the ComboBox model.
- **ComboBoxListModel**: Manages a list of ComboBox items with filtering capabilities.
- **ComboBoxListDelegate**: A delegate for custom item representation in a TreeView.
- **ComboListBoxWidget**: A widget combining a search field with a list box for item selection.
- **build_searchable_combo_widget**: A function that creates a searchable combo box widget with specified options.

## General Use Case
The extension is used to add searchable drop-down lists to UIs in Omniverse Kit applications. Users can interact with the ComboBox to select items from a filterable list, which is useful in scenarios where long lists need to be navigated quickly. It supports customization of the widget's appearance and behavior through theming and delegates, enhancing the user experience in complex UIs. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)