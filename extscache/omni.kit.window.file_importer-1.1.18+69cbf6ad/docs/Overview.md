```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The file_importer extension provides a standardized dialog for importing files.  It is a wrapper around the {obj}`FilePickerDialog`,
but with reasonable defaults for common settings, so it's a higher-level entry point to that interface.
Nevertheless, users will still have the ability to customize some parts but we've boiled them down to just the essential ones.
Why you should use this extension:

* Present a consistent file import experience across the app.
* Customize only the essential parts while inheriting sensible defaults elsewhere.
* Reduce boilerplate code.
* Inherit future improvements.
* Checkpoints fully supported if available on the server.

```{image} ../../../../source/extensions/omni.kit.window.file_importer/data/preview.png
---
align: center
---
```

## Quickstart

You can pop-up a dialog in just 2 steps.  First, retrieve the extension.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_importer/scripts/demo_file_importer.py
---
language: python
start-after: BEGIN-DOC-get_instance
end-before: END-DOC-get_instance
dedent: 8
---
```

Then, invoke its show_window method.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_importer/scripts/demo_file_importer.py
---
language: python
start-after: BEGIN-DOC-show_window
end-before: END-DOC-show_window
dedent: 8
---
```

Note that the extension is a singleton, meaning there's only one instance  of it throughout the app.  Basically, we are assuming that you'd
never open more than one instance of the dialog at any one time.  The advantage is that we can channel any development through this 
single extension and all users will inherit the same changes.

## Customizing the Dialog

You can customize these parts of the dialog.

* Title - The title of the dialog.
* Collections - Which of these collections, ["bookmarks", "omniverse", "my-computer"] to display.
* Filename Url - Url of the file to import.
* Postfix options - Show only files of these content types.
* Extension options - Show only files with these filename extensions.
* Import label - Label for the import button.
* Import handler - User provided callback to handle the import process.

Note that these settings are applied when you show the window.  Therefore, each time it's displayed, the dialog can be tailored to
the use case.

## Filter files by type

The user has the option to filter what files get shown in the list view.

One challenge of working in Omniverse is that everything is a USD file.  An expected use case is to show only files of a
particular content type.  To facilitate this workflow, we suggest adding a postfix to the filename, e.g. "file.animation.usd".
The file bar contains a dropdown that lists the default postfix labels, so you can filter by these. You have the option to
override this list.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_importer/omni/kit/window/file_importer/extension.py
---
language: python
start-after: BEGIN-DOC-file_postfix_options
end-before: END-DOC-file_postfix_options
dedent: 0
---
```

You can also filter by filename extension.  By default, we provide the option to show only USD files.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_importer/omni/kit/window/file_importer/extension.py
---
language: python
start-after: BEGIN-DOC-file_extension_types
end-before: END-DOC-file_extension_types
dedent: 0
---
```

If you override either of the lists above, then you'll also need to provide a filter handler.  The handler is called to decide whether
or not to display a given file.  The default handler is shown below as an example.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_importer/omni/kit/window/file_importer/extension.py
---
language: python
start-after: BEGIN-DOC-file_filter_handler
end-before: END-DOC-file_filter_handler
dedent: 0
---
```

## Import options

A common need is to provide user options for the import process.  You create the widget for accepting those inputs,
then add it to the details pane of the dialog.  Do this by subclassing from {obj}`ImportOptionsDelegate`
and overriding the methods, {meth}`ImportOptionsDelegate._build_ui_impl` and (optionally) {meth}`ImportOptionsDelegate._destroy_impl`.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_importer/scripts/demo_file_importer.py
---
language: python
start-after: BEGIN-DOC-import_options
end-before: END-DOC-import_options
dedent: 0
---
```

Then provide the controller to the file picker for display.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_importer/scripts/demo_file_importer.py
---
language: python
start-after: BEGIN-DOC-add_import_options
end-before: END-DOC-add_import_options
dedent: 8
---
```

## Import handler

Provide a handler for when the Import button is clicked.  The handler should expect a list of :attr:`selections` made from the UI.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_importer/scripts/demo_file_importer.py
---
language: python
start-after: BEGIN-DOC-import_handler
end-before: END-DOC-import_handler
dedent: 4
---
```

## Demo app

A complete demo, that includes the code snippets above, is included with this extension at [Python](USAGE_PYTHON.md).
