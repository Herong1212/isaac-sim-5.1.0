# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# BEGIN-DOC-whole_demo
import os
import omni.ui as ui

from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.widget.filebrowser import FileBrowserItem


# BEGIN-DOC-options_pane
def options_pane_build_fn(selected_items):
    with ui.CollapsableFrame("Reference Options"):
        with ui.HStack(height=0, spacing=2):
            ui.Label("Prim Path", width=0)
    return True
# END-DOC-options_pane

# BEGIN-DOC-filter
def on_filter_item(dialog: FilePickerDialog, item: FileBrowserItem) -> bool:
    if not item or item.is_folder:
        return True
    if dialog.current_filter_option == 0:
        # Show only files with listed extensions
        _, ext = os.path.splitext(item.path)
        if ext in [".usd", ".usda", ".usdc", ".usdz"]:
            return True
        else:
            return False
    else:
        # Show All Files (*)
        return True
# END-DOC-filter

# BEGIN-DOC-click_open
def on_click_open(dialog: FilePickerDialog, filename: str, dirname: str):
    """
    The meat of the App is done in this callback when the user clicks 'Accept'. This is
    a potentially costly operation so we implement it as an async operation.  The inputs
    are the filename and directory name. Together they form the fullpath to the selected
    file.
    """
    # Normally, you'd want to hide the dialog
    # dialog.hide()
    dirname = dirname.strip()
    if dirname and not dirname.endswith("/"):
        dirname += "/"
    fullpath = f"{dirname}{filename}"
    print(f"Opened file '{fullpath}'.")
# END-DOC-click_open

if __name__ == "__main__":
    item_filter_options = ["USD Files (*.usd, *.usda, *.usdc, *.usdz)", "All Files (*)"]

    dialog = FilePickerDialog(
        "Demo Filepicker",
        apply_button_label="Open",
        click_apply_handler=lambda filename, dirname: on_click_open(dialog, filename, dirname),
        item_filter_options=item_filter_options,
        item_filter_fn=lambda item: on_filter_item(dialog, item),
        options_pane_build_fn=options_pane_build_fn,
    )
    dialog.add_connections({"ov-content": "omniverse://ov-content", "ov-rc": "omniverse://ov-rc"})

    # Display dialog at pre-determined path
    dialog.show(path="omniverse://ov-content/NVIDIA/Samples/Astronaut/Astronaut.usd")
# END-DOC-whole_demo
