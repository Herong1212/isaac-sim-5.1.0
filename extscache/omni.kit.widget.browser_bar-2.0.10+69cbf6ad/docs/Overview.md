```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.widget.browser_bar` extension provides a UI widget named `BrowserBar`, designed to enhance navigation in directory-like structures by offering a browser-like history tracking and path selection mechanism. It extends the functionality of the `PathField` widget by allowing users to visit and revisit previously accessed paths, similar to using a web browser's navigation buttons. The module also includes classes for creating and managing a queue of string items (`StringQueueModel`) and a history of visited items (`VisitedHistory`).

## Important API List
- **BrowserBar**: A widget extending `PathField` with navigation history and branching options for directory browsing.

## General Use Case
The `BrowserBar` widget is used to navigate through directories or similar structures within an application. It provides users with an intuitive interface to move forward and backward in their navigation history, analogous to a web browser. Developers can integrate this widget into their applications to allow users to smoothly and efficiently traverse directories, paths, or other sequential data, with the ability to revisit past locations easily. The `StringQueueModel` and `VisitedHistory` classes are used to manage and track the navigation history within the `BrowserBar` widget. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](CHANGELOG)