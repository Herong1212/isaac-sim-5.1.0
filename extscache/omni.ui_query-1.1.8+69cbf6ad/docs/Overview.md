```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

**omni.ui** Query API is an extension designed to simplify the retrieval of UI elements by allowing developers to query Omni UI widget trees using expressive strings. It streamlines the process of finding widgets by their paths, names, or types, making it useful for UI automation, testing, and troubleshooting in Omniverse Kit SDK. The extension provides a dedicated class with easy-to-use methods that return either individual widgets or collections based on query criteria.

## Concepts

- **Widget Queries:** The API is centered around the [OmniUIQuery](omni.ui_query/omni.ui_query.OmniUIQuery) class, which offers a set of class methods to traverse UI trees and identify widgets matching specific query strings.
- **Path Generation:** It allows users to generate and manipulate widget path strings, turning hierarchical UI structures into easily searchable expressions.

## Functionality

- **Finding Widgets:** Methods like find_widget, find_widgets, and find_first_widget let you search for widgets based on full paths or partial query criteria.
- **Mapping Paths:** The get_widget_path and get_window_widget_paths functions help in obtaining the complete path to a widget from a given window, which is useful for debugging and automation.
- **Legacy Support:** The find_menu_item method supports legacy queries targeting menu items, ensuring backward compatibility while paving the way for future enhancements.

## Relationships

- **Dependency:** This extension relies on the **omni.ui** module to interact with the UI framework, ensuring that it operates seamlessly within the Omniverse Kit SDK environment.
- **Integration:** By using standard query mechanisms, it integrates well with other UI-related extensions and tools, providing a consistent approach to UI element identification across the application.

## Considerations

- **Legacy Methods:** Some functions, such as find_menu_item, indicate legacy support and may be subject to updates in future releases.
- **Use Case Focus:** While the API is practical for test automation and diagnostics, its query expressions are designed for straightforward use cases rather than highly complex widget filtering.

```python
from omni.ui_query import OmniUIQuery

# Example: Find a widget using its full widget path.
widget = OmniUIQuery.find_widget("/Window/MainContainer/TargetWidget")
if widget:
    print("Widget found:", widget)
else:
    print("Widget not found.")
```

**omni.ui** Query API provides a practical and lightweight solution for developers needing to efficiently locate and work with UI components within the Omniverse Kit environment.