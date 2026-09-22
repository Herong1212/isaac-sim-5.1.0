"""Support required by the Carbonite extension loader - no visible API exists."""

import carb
import omni.ext

__all__ = []
"""This module has no public API"""


class _PublicExtension(omni.ext.IExt):
    def on_startup(self):
        carb.log_warn(
            "omni.graph.io is deprecated. Nodes in this extension have been moved to omni.graph.nodes. Update any dependencies accordingly."
        )

    def on_shutdown(self):
        pass
