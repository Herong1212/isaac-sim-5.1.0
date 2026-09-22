"""MainWindow class"""

import asyncio
import carb.settings
import omni.kit.app
import omni.ui as ui


class MainWindow(object):
    """A class that represents the main application window in OmniKit.

    This class manages the initialization, display, and cleanup of the main window. It provides methods to toggle the
    visibility of the main menu and status bar, as well as to asynchronously dock various application windows at startup.
    The main window is set up with custom settings that are retrieved from the application's settings.
    """

    def __init__(self):
        """Initializes the main window with customized settings and potentially starts window docking.

        The main window is initialized with a gray foreground to hide undocked windows during the first several frames.
        The visibility of the main menu bar is set based on the application's release status. Settings for margins,
        background color, and whether to dock windows on startup are retrieved and applied to the main window.
        If docking is enabled, an asynchronous task is created to dock the windows.
        """
        # Show gray color the first several frames. It will hode the windows
        # that are not yet docked.
        self._ui_main_window = ui.MainWindow(show_foreground=True)
        # this will be False for Release
        self.get_main_menu_bar().visible = False

        settings = carb.settings.get_settings()
        margin_width = settings.get_as_float("ext/omni.kit.mainwindow/margin/width")
        margin_height = settings.get_as_float("ext/omni.kit.mainwindow/margin/height")
        background_color = settings.get_as_int("ext/omni.kit.mainwindow/backgroundColor")
        dock_windows = settings.get_as_bool("ext/omni.kit.mainwindow/startup/dockWindows")

        self._ui_main_window.main_frame.set_style(
            {"margin_width": margin_width, "margin_height": margin_height, "background_color": background_color}
        )

        if dock_windows:
            self._setup_window_task = asyncio.ensure_future(self._dock_windows())

    def destroy(self):
        """Cleans up the main window by setting its reference and setup window task to None."""
        self._ui_main_window = None
        self._setup_window_task = None

    def get_main_menu_bar(self) -> ui.MenuBar:
        """Returns the main menu bar.

        Returns:
            ui.MenuBar: The main menu bar."""
        return self._ui_main_window.main_menu_bar

    def get_status_bar_frame(self) -> ui.Frame:
        """Returns the frame containing the status bar.

        Returns:
            ui.Frame: The frame containing the status bar."""
        return self._ui_main_window.status_bar_frame

    def show_hide_menu(self):
        """Toggles the visibility of the main menu bar."""
        self.get_main_menu_bar().visible = not self.get_main_menu_bar().visible

    def show_hide_status_bar(self):
        """Toggles the visibility of the status bar."""
        self.get_status_bar_frame().visible = not self.get_status_bar_frame().visible

    async def _dock_windows(self):
        """Asynchronously docks the various windows (Stage, Viewport, Property, Toolbar, Console) in the main window.

        This method waits for the windows to become available and then docks them in the appropriate positions.
        It also hides the foreground overlay after a few frames to ensure that the windows are visible.
        """
        stage_win = None
        viewport = None
        property_win = None
        toolbar = None
        console = None

        frames = 3
        while frames > 0:
            # setup the docking Space
            if not stage_win:
                stage_win = ui.Workspace.get_window("Stage")
            if not viewport:
                viewport = ui.Workspace.get_window("Viewport")
            if not property_win:
                property_win = ui.Workspace.get_window("Property")
            if not toolbar:
                toolbar = ui.Workspace.get_window("Main ToolBar")
            if not console:
                console = ui.Workspace.get_window("Console")

            if stage_win and viewport and property_win and toolbar and console:
                break  # early out

            frames = frames - 1
            await omni.kit.app.get_app().next_update_async()

        main_dockspace = ui.Workspace.get_window("DockSpace")

        if viewport:
            viewport.dock_in(main_dockspace, ui.DockPosition.SAME)

        if stage_win:
            stage_win.dock_in(viewport, ui.DockPosition.RIGHT, 0.3)

        if property_win:
            if stage_win:
                property_win.dock_in(stage_win, ui.DockPosition.BOTTOM, 0.5)
            else:
                property_win.dock_in(viewport, ui.DockPosition.RIGHT, 0.3)

        if console:
            console.dock_in(viewport, ui.DockPosition.BOTTOM, 0.3)

        if toolbar:
            toolbar.dock_in(viewport, ui.DockPosition.LEFT)

        self._setup_window_task = None

        # Hide foreground after 5 frames. It's enough for windows to appear.
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()

        self._ui_main_window.show_foreground = False
