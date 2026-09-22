# USD Material MDL Export.

This extension adds a context menu item "Export to MDL" to the stage window. It shows when right-clicking a (single) selected material node. When the new menu item is chosen, the user is prompted for a destination MDL filename. The selected USD material is then converted to an MDL material and saved to the selected destination in a new MDL module.

## Issues and limitation

- The USD material needs to be bound to geometry in order to be fully available to the renderer and ready for export.
- Resources that are exported with the material are not overridden if files with the name exists already. Instead, new filenames are generated for those resources. This also applies when exporting a USD material to the same MDL file multiple times.

## Screenshot
