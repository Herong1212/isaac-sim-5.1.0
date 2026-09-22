"""Implementation of omni.kit.menu.common. This adds Help & Window menus."""

import omni.ext
import omni.kit.menu.utils

from .legacy_help import HelpExtension
from .legacy_window import WindowExtension


class CommonMenuExtension(omni.ext.IExt):
    """A class for managing common menu extensions.

    This class is responsible for initializing and shutting down legacy help and window extensions within the application. It extends the omni.ext.IExt interface and provides mechanisms to handle startup and shutdown events.
    """

    def __init__(self):
        """Initializes the CommonMenuExtension instance."""
        super().__init__()
        self._legacy_help = None
        self._legacy_window = None

    def on_startup(self, ext_id):
        """Handles startup procedures for the extension.

        Args:
            ext_id (str): The extension ID.
        """
        self._legacy_help = HelpExtension()
        self._legacy_window = WindowExtension()

    def on_shutdown(self):
        """Handles shutdown procedures for the extension."""
        del self._legacy_help
        del self._legacy_window
