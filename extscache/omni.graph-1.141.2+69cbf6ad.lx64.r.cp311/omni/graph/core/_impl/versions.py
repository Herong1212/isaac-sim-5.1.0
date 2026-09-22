"""Management of version compatibility information for the extensions (where not handled by the extension manager)"""

from __future__ import annotations

from enum import Enum, auto
from functools import lru_cache
from typing import Tuple

import carb
import omni.kit.app

# Version information returned from the extension manager
VersionType = Tuple[int, int, int]


class Compatibility(Enum):
    """Potential types of version compatibility"""

    Incompatible = auto()
    FullyCompatible = auto()
    MajorVersionCompatible = auto()


# ================================================================================
@lru_cache(maxsize=len(Compatibility) + 1)
def get_generator_extension_version(
    compatibility: Compatibility | VersionType = Compatibility.FullyCompatible,
) -> VersionType:
    """Returns the current version of the extension omni.graph.tools, raising AttributeError if it could not be found
    since the fact that this script is running dictates that there should be a valid enabled version of this extension.
    If a compatibility is specified then tweak the returned version to have the named compatibility with the current one
    """
    if not isinstance(compatibility, Compatibility):
        return compatibility

    if compatibility == Compatibility.Incompatible:
        return (0, 0, 0)

    if compatibility == Compatibility.MajorVersionCompatible:
        fully_compatible = get_generator_extension_version()
        return (fully_compatible[0], fully_compatible[1] + 1, fully_compatible[2])

    enabled_version = None
    mgr = omni.kit.app.get_app().get_extension_manager()
    for version in mgr.fetch_extension_versions("omni.graph.tools"):
        if version["enabled"]:
            enabled_version = version["version"]
    if enabled_version is None:
        carb.log_error("Failed to get the generator extension version")
        current_version = (0, 0, 0)
    else:
        current_version = enabled_version[:3]

    return current_version


# ================================================================================
@lru_cache(maxsize=len(Compatibility) + 1)
def get_target_extension_version(
    compatibility: Compatibility | VersionType = Compatibility.FullyCompatible,
) -> VersionType:
    """Returns the current version of the extension omni.graph.core, raising AttributeError if it could not be found
    since the fact that this script is running dictates that there should be a valid enabled version of this extension.
    If a compatibility is specified then tweak the returned version to have the named compatibility with the current one
    """
    if not isinstance(compatibility, Compatibility):
        return compatibility

    if compatibility == Compatibility.Incompatible:
        return (0, 0, 0)

    if compatibility == Compatibility.MajorVersionCompatible:
        fully_compatible = get_target_extension_version()
        return (fully_compatible[0], fully_compatible[1] + 1, fully_compatible[2])

    enabled_version = None
    mgr = omni.kit.app.get_app().get_extension_manager()
    for version in mgr.fetch_extension_versions("omni.graph.core"):
        if version["enabled"]:
            enabled_version = version["version"]
    if enabled_version is None:
        carb.log_error("Failed to get the target extension version")
        current_version = (0, 0, 0)
    else:
        current_version = enabled_version[:3]

    return current_version


# ==============================================================================================================
def check_version_compatibility(generator_version: VersionType, target_version: VersionType) -> Compatibility:
    """Checks to see how compatible the given versions are against the current extension versions enabled"""

    def __version_compatibility(actual_version: VersionType, expected_version: VersionType) -> Compatibility:
        """Returns the compatibility of the two versions, assumed to reference the same extension"""
        if actual_version[0] != expected_version[0]:
            return Compatibility.Incompatible
        if actual_version[1] != expected_version[1]:
            return Compatibility.MajorVersionCompatible
        return Compatibility.FullyCompatible

    # The target must at least be ABI compatible or we have real trouble
    if __version_compatibility(target_version, get_target_extension_version()) == Compatibility.Incompatible:
        return Compatibility.Incompatible

    # After that the generator is the one that determines what to do next with the generated file
    return __version_compatibility(generator_version, get_generator_extension_version())
