```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The file picker extension provides a standardized dialog for picking files.  It is a wrapper around the {obj}`FileBrowserWidget`,
but with reasonable defaults for common settings, so it's a higher-level entry point to that interface.
Nevertheless, users will still have the ability to customize some parts but we've boiled them down to just the essential ones.
Why you should use this extension:

* Checkpoints fully supported if available on the server.

```{image} ../../../../source/extensions/omni.kit.window.filepicker/data/preview.png
---
align: center
---
```

## Quickstart

You can pop-up a dialog in just 2 steps.  First, create a dialog.

```
dialog = FilePickerDialog("Demo Filepicker")
```

Then, invoke its show_window method.

```
dialog.show()
```

## Customizing the Dialog

You can customize these parts of the dialog.

* Title - The title of the dialog.
* Collections - Which of these collections, ["bookmarks", "omniverse", "my-computer"] to display.
* Filename Url - Url of the file to process.
* Postfix options - Show only files of these content types.
* Extension options - Show only files with these filename extensions.
* Apply label - Label for the apply button.
* Apply handler - User provided callback to handle the apply process.

Note that these settings are applied when you show the window.  Therefore, each time it's displayed, the dialog can be tailored to
the use case.

## Filter files by type

The user has the option to filter what files get shown in the list view.

```{literalinclude} ../../../../source/extensions/omni.kit.window.filepicker/scripts/demo_filepicker.py
---
language: python
start-after: BEGIN-DOC-filter
end-before: END-DOC-filter
dedent: 0
---
```

## Options

A common need is to provide user options for the file picker. 

```{literalinclude} ../../../../source/extensions/omni.kit.window.filepicker/scripts/demo_filepicker.py
---
language: python
start-after: BEGIN-DOC-options_pane
end-before: END-DOC-options_pane
dedent: 0
---
```

## On apply handler

Provide a handler for when the ok button is clicked.  

```{literalinclude} ../../../../source/extensions/omni.kit.window.filepicker/scripts/demo_filepicker.py
---
language: python
start-after: BEGIN-DOC-click_open
end-before: END-DOC-click_open
dedent: 0
---
```

## Demo app

A complete demo, that includes the code snippets above, is included with this extension at [Python](USAGE_PYTHON.md).
