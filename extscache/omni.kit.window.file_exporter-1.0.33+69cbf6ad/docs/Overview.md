```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The file_exporter extension provides a standardized dialog for exporting files.  It is a wrapper around the {obj}`FilePickerDialog`,
but with reasonable defaults for common settings, so it's a higher-level entry point to that interface.
Nevertheless, users will still have the ability to customize some parts but we've boiled them down to just the essential ones.
Why you should use this extension:

* Present a consistent file export experience across the app.
* Customize only the essential parts while inheriting sensible defaults elsewhere.
* Reduce boilerplate code.
* Inherit future improvements.
* Checkpoints fully supported if available on the server.

```{image} ../../../../source/extensions/omni.kit.window.file_exporter/data/preview.png
---
align: center
---
```

## Quickstart

You can pop-up a dialog in just 2 steps.  First, retrieve the extension.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_exporter/scripts/demo_file_exporter.py
---
language: python
start-after: BEGIN-DOC-get_instance
end-before: END-DOC-get_instance
dedent: 8
---
```

Then, invoke its show_window method.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_exporter/scripts/demo_file_exporter.py
---
language: python
start-after: BEGIN-DOC-show_window
end-before: END-DOC-show_window
dedent: 8
---
```

Note that the extension is a singleton, meaning there's only one instance of it throughout the app.  Basically, we are assuming that you'd 
never open more than one instance of the dialog at any one time.  The advantage is that we can channel any development through this 
single extension and all users will inherit the same changes.

## Customizing the Dialog

You can customize these parts of the dialog.

*  Title - The title of the dialog.
*  Collections - Which of these collections, ["bookmarks", "omniverse", "my-computer"] to display.
*  Filename Url - Url to open the dialog with.
*  Postfix options - List of content labels appended to the filename.
*  Extension options - List of filename extensions.
*  Export options - Options to apply during the export process.
*  Export label - Label for the export button.
*  Export handler - User provided callback to handle the export process.

Note that these settings are applied when you show the window.  Therefore, each time it's displayed, the dialog can be tailored
to the use case.

## Filename postfix options

Users might want to set up data libraries of just animations, materials, etc.  However, one challenge of working in Omniverse is that
everything is a USD file.   To facilitate this workflow, we suggest adding a postfix to the filename, e.g. "file.animation.usd".  The 
file bar contains a dropdown that lists the postfix labels.  A default list is provided but you can also provide your own.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_exporter/omni/kit/window/file_exporter/extension.py
---
language: python
start-after: BEGIN-DOC-file_postfix_options
end-before: END-DOC-file_postfix_options
dedent: 0
---
```

A list of file extensions, furthermore, allows the user to specify what flavor of USD to export.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_exporter/omni/kit/window/file_exporter/extension.py
---
language: python
start-after: BEGIN-DOC-file_extension_types
end-before: END-DOC-file_extension_types
dedent: 0
---
```

When the user selects a combination of postfix and extension types, the file view will filter out all other file types, leaving only
the matching ones.

## Export options

A common need is to provide user options for the export process.  You create the widget for accepting those inputs, 
then add it to the details pane of the dialog.  Do this by subclassing from {obj}`ExportOptionsDelegate`
and overriding the methods, :meth:`ExportOptionsDelegate._build_ui_impl` and (optionally) :meth:`ExportOptionsDelegate._destroy_impl`.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_exporter/scripts/demo_file_exporter.py
---
language: python
start-after: BEGIN-DOC-export_options
end-before: END-DOC-export_options
dedent: 0
---
```

Then provide the controller to the file picker for display.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_exporter/scripts/demo_file_exporter.py
---
language: python
start-after: BEGIN-DOC-add_export_options
end-before: END-DOC-add_export_options
dedent: 8
---
```

## Export handler

Pprovide a handler for when the Export button is clicked.  In additon to :attr:`filename` and :attr:`dirname`, the handler
should expect a list of :attr:`selections` made from the UI.

```{literalinclude} ../../../../source/extensions/omni.kit.window.file_exporter/scripts/demo_file_exporter.py
---
language: python
start-after: BEGIN-DOC-export_handler
end-before: END-DOC-export_handler
dedent: 4
---
```

## Demo app

A complete demo, that includes the code snippets above, is included with this extension at [Python](USAGE_PYTHON.md).
