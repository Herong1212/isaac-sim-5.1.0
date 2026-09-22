# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
""" Prompt window class to show when opening a read only file. """
__all__ = ["ReadOnlyOptionsWindow"]
import omni.ui as ui
from typing import Callable

ICON_PATH = "${omni.kit.window.file}/icons"


class ReadOnlyOptionsWindow:
    """
    Prompt window class to show when opening a read only file.

    Args:
        open_with_new_edit_fn (Callable): function to call when opening with a new edit layer.
        open_original_fn (Callable): function to call when opening original file.
    Keyword Args:
        modal (bool): True if window is modal.
    """
    def __init__(self, open_with_new_edit_fn: Callable[[], None], open_original_fn: Callable[[], None], modal=False):
        self._title = "Opening a Read Only File"
        self._modal = modal
        self._buttons = []
        self._content_buttons = [
            ("Open With New Edit Layer", "open_edit_layer.svg", open_with_new_edit_fn),
            ("Open Original File", "pencil.svg", open_original_fn),
        ]
        self._build_ui()

    def destroy(self):
        """ Destructor. """
        for button in self._buttons:
            button.set_clicked_fn(None)
        self._buttons.clear()

    def show(self):
        """ Show the window. """
        self._window.visible = True

    def hide(self):
        """ Hide the window. """
        self._window.visible = False

    def is_visible(self):
        """
        Return:
            Return True if window is visible.
        """
        return self._window.visible

    def _build_ui(self):
        self._window = ui.Window(
            self._title, visible=False, height=0, dockPreference=ui.DockPreference.DISABLED
        )
        self._window.flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_SCROLLBAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_MOVE
        )

        if self._modal:
            self._window.flags = self._window.flags | ui.WINDOW_FLAGS_MODAL

        button_style = {
            "Button": {"stack_direction": ui.Direction.LEFT_TO_RIGHT},
            "Button.Image": {"alignment": ui.Alignment.CENTER},
            "Button.Label": {"alignment": ui.Alignment.LEFT_CENTER}
        }

        def button_cliked_fn(button_fn):
            if button_fn:
                button_fn()
            self.hide()

        with self._window.frame:
            with ui.VStack(height=0):
                ui.Spacer(width=0, height=10)
                with ui.VStack(height=0):
                    ui.Spacer(height=0)
                    for button in self._content_buttons:
                        (button_text, button_icon, button_fn) = button
                        with ui.HStack():
                            ui.Spacer(width=40)
                            ui_button = ui.Button(
                                "  " + button_text,
                                image_url=f"{ICON_PATH}/{button_icon}",
                                image_width=24,
                                height=40,
                                clicked_fn=lambda a=button_fn: button_cliked_fn(a),
                                style=button_style
                            )
                            ui.Spacer(width=40)
                        ui.Spacer(height=5)
                        self._buttons.append(ui_button)
                    ui.Spacer(height=5)
                    with ui.HStack():
                        ui.Spacer()
                        cancel_button = ui.Button("Cancel", width=80, height=0)
                        cancel_button.set_clicked_fn(lambda: self.hide())
                        self._buttons.append(cancel_button)
                        ui.Spacer(width=40)
                    ui.Spacer(height=0)
                ui.Spacer(width=0, height=10)
