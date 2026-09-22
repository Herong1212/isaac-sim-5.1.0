"""Support required by the Carbonite extension loader - no visible API exists."""

import omni.ext

__all__ = []
"""This module has no public API"""


class _PublicExtension(omni.ext.IExt):
    def on_startup(self): ...  # noqa: E704

    def on_shutdown(self): ...  # noqa: E704
