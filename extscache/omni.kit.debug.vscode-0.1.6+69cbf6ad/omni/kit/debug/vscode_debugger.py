"""A module providing integration with the VS Code Python debugger within the
Omni application, including a command to trigger breakpoints and a UI for
debugger status.
"""

__all__ = ["DebugBreak", "VSCodeExtension"]

from typing import Any
import carb
import omni.ext
import omni.kit.commands
import omni.ui as ui
import omni.kit.debug.python
from omni.kit.menu.utils import MenuHelperExtensionFull


SETTING_SHOW_STARTUP = "/exts/omni.kit.debug.vscode/visible_at_startup"


class DebugBreak(omni.kit.commands.Command):
    """A command to trigger a breakpoint in the Python debugger.

    This class is a custom command used within the Omni application to
    initiate a breakpoint inside the Python code. It leverages the Omni
    application's debugging tools to pause execution at the point where this
    command is executed. This allows developers to inspect the current state of
    the application and perform debugging tasks.
    """

    def do(self) -> None:
        """Triggers a breakpoint in the Python debugger.

        Returns:
            None
        """
        omni.kit.debug.python.trigger_breakpoint()


class VSCodeExtension(omni.ext.IExt, MenuHelperExtensionFull):
    """Extension to enable connection of VS Code python debugger. It enables it
    using python ptvsd module and shows status."""
    WINDOW_NAME = "VS Code Link"
    MENU_GROUP = "Window"
    ATTACH_DISPLAY = {
        True: ("VS Code Debugger Attached", 0xFFFFFF00),
        False: ("VS Code Debugger Unattached", 0xFF0000FF),
    }

    def __init__(self) -> None:
        super().__init__()
        self._attached: bool = False
        self._window: ui.Window | None = None
        self._status_label: ui.Label | None = None
        self._break_button: ui.Button | None = None

    def on_startup(self) -> None:
        """This method initializes the extension UI and sets up debugger
        status updates.

        Returns:
            None
        """
        self.menu_startup(
            lambda: ui.Window(VSCodeExtension.WINDOW_NAME,
                              width=270,
                              height=120,
                              auto_resize=True,
                              padding_x=10,
                              ),
            VSCodeExtension.WINDOW_NAME,
            VSCodeExtension.WINDOW_NAME,
            VSCodeExtension.MENU_GROUP)

        show_startup = carb.settings.get_settings().get(SETTING_SHOW_STARTUP)
        if show_startup:
            ui.Workspace.show_window(VSCodeExtension.WINDOW_NAME)
            self._show()

    def on_shutdown(self) -> None:
        """Shuts down the extension and cleans up menu items."""
        self.menu_shutdown()

    def _set_attached(self, attached: bool) -> None:
        if self._attached != attached:
            self._attached = attached
            if self._break_button and hasattr(self._break_button, "enabled"):
                self._break_button.enabled = attached
            if self._status_label:
                if hasattr(self._status_label, "text"):
                    self._status_label.text = \
                        VSCodeExtension.ATTACH_DISPLAY[self._attached][0]
                if hasattr(self._status_label, "set_style"):
                    color = VSCodeExtension.ATTACH_DISPLAY[self._attached][1]
                    self._status_label.set_style({"color": color})

    def _show(self) -> None:
        super()._show()

        def on_rebuild() -> None:
            """Rebuilds the window frame if it exists and has a
            frame attribute."""
            if self._window:
                if hasattr(self._window, "frame"):
                    self._window.frame.rebuild()
                self._window.flags = (ui.WINDOW_FLAGS_NO_RESIZE)

        if self._window:
            with self._window.frame:
                with ui.VStack(height=0):
                    with ui.HStack(height=20):
                        ui.Label("Status:", width=60)
                        self._status_label = ui.Label("")
                    with ui.HStack(height=20):
                        ui.Label("Address:", width=60)
                        info_label = ui.Label("")
                    with ui.HStack(height=20):
                        self._break_button = ui.Button(
                            "Break",
                            width=0,
                            tooltip="Pauses application execution at the current line. Waits for a debugger to attach if none is connected."
                        )
                        ui.Button("Refresh", width=0, clicked_fn=on_rebuild, tooltip="Refreshes the address and status of the debugger.")

            wait_info = omni.kit.debug.python.get_listen_address()
            info_label.text = f"Address: {wait_info}" if wait_info else "Error"

            def on_click(*_args: Any) -> None:
                omni.kit.commands.execute("DebugBreak")
                # Also refresh so the Status label is updated
                on_update()

            self._break_button.set_clicked_fn(on_click)

            # Monitor for attachment
            self._attached = False
            self._set_attached(False)

            def on_update() -> None:
                """Updates the debugger attachment status by checking if a
                debugger is currently connected."""
                self._set_attached(omni.kit.debug.python.is_attached())

            self._window.frame.set_build_fn(on_update)
