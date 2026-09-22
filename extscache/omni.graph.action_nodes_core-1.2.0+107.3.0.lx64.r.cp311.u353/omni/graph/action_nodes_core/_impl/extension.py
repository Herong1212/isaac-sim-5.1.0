"""Support required by the Carbonite extension loader - no visible API exists."""

from contextlib import suppress

import omni.ext

__all__ = []
"""This module has no public API"""


class _PublicExtension(omni.ext.IExt):
    """Object that tracks the lifetime of the Python part of the extension loading"""

    def __init__(self):
        super().__init__()
        with suppress(ImportError):
            import omni.kit.app  # noqa: PLW0621

            app = omni.kit.app.get_app()
            manager = app.get_extension_manager()
            # This is a bit of a hack to make the template directory visible to the OmniGraph UI extension
            # if it happens to already be enabled. The "hack" part is that this logic really should be in
            # omni.graph.ui, but it would be much more complicated there, requiring management of extensions
            # that both do and do not have dependencies on omni.graph.ui.
            if manager.is_extension_enabled("omni.graph.ui"):
                import omni.graph.ui  # noqa: PLW0621

                omni.graph.ui.ComputeNodeWidget.get_instance().add_template_path(__file__)

    def on_startup(self):
        pass

    def on_shutdown(self):
        pass
