"""Extension management support"""

import omni.ext

__all__ = []


class _PublicExtension(omni.ext.IExt):
    """Dummy extension class that just serves to register and deregister the extension"""

    def on_startup(self):
        """Callback when the extension is starting up"""

    def on_shutdown(self):
        """Callback when the extension is shutting down"""
