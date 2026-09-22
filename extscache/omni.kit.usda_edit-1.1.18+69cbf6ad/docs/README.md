# USDA Editor [omni.kit.usda_edit]

The tool to view end edit USD layers in a text editor.

Convert a USD file to the USD ASCII format in a temporary location and run an
editor on it. After saving the editor, the edited file will be converted back
to the original format and reload the corresponding layer in Kit, invoking
the stage's update.

The context menu to edit layer appears in Layers and Content windows.

The editor can be configured with a setting `/app/editor` or environment
variable `EDITOR`. By default, the editor is either `code` or
`notepad`/`gedit`, depending on the availability.

