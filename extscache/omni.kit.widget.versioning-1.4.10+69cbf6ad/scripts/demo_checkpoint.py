# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui

from omni.kit.widget.versioning import CheckpointWidget, CheckpointCombobox, LAYOUT_TABLE_VIEW, LAYOUT_SLIM_VIEW

def create_checkpoint_view(url: str, layout: int):
    view = CheckpointWidget(url, layout=layout)
    view.add_context_menu(
        "Menu Action",
        "pencil.svg",
        lambda menu, cp: print(f"Apply '{menu}' to '{cp.get_relative_path()}'"),
        None,
    )
    view.set_mouse_double_clicked_fn(
        lambda b, k, cp: print(f"Double clicked '{cp.get_relative_path()}")
    )

if __name__ == "__main__":
    url = "omniverse://ov-rc/Users/mkarlsson@nvidia.com/sphere.usd"
    window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR
    window = ui.Window("DemoFileBrowser", width=800, height=500, flags=window_flags)
    with window.frame:
        with ui.VStack(style={"margin": 0}):
            ui.Label(url, height=30)
            with ui.HStack():
                create_checkpoint_view(url, LAYOUT_TABLE_VIEW)
                ui.Spacer(width=10)
                with ui.VStack(width=250):
                    create_checkpoint_view(url, LAYOUT_SLIM_VIEW)
                ui.Spacer(width=10)
                with ui.VStack(width=100, height=20):
                    combo_box = CheckpointCombobox(url, lambda sel: print(f"Selected: {sel.get_full_url()}"))
