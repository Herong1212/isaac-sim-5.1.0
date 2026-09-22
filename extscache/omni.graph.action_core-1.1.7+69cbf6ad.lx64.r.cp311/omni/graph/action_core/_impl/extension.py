"""Support required by the Carbonite extension loader"""

import omni.ext


class _PublicExtension(omni.ext.IExt):
    """Object that tracks the lifetime of the Python part of the extension loading"""
