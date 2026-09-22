"""MainWindow extension"""

import omni.ext

from .main_window import MainWindow

global g_main_window
g_main_window = None


def get_main_window() -> MainWindow:
    """Returns the global instance of the MainWindow.

    This function allows access to the MainWindow instance that is created
    and managed by the MainWindowExtension. It uses a global variable to
    store the instance so it can be retrieved from anywhere within the
    application.

    Returns:
        MainWindow: The global MainWindow instance if it has been created,
        otherwise None.
    """
    global g_main_window
    return g_main_window


class MainWindowExtension(omni.ext.IExt):
    """An omni.ext.IExt extension to manage the main window of an application.

    This extension provides lifecycle management for the `MainWindow` instance, creating it upon startup and destroying it on shutdown. It ensures that there is a global access point to the main window through the `get_main_window` function.
    """

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        """Initializes the main window when the extension starts up.

        This method creates a new instance of the MainWindow class and assigns it
        to a global variable so that it can be accessed from anywhere within
        the application.

        Args:
            ext_id (str): The ID of the current extension.
        """
        global g_main_window
        self._main_window = MainWindow()
        g_main_window = self._main_window

    def on_shutdown(self):
        """Cleans up resources related to the main window when the extension shuts down.

        This method destroys the MainWindow instance if it exists and sets the
        global variable to None, ensuring that all resources are properly
        released.
        """
        global g_main_window

        if g_main_window:
            g_main_window.destroy()

        self._main_window = None
        g_main_window = None
