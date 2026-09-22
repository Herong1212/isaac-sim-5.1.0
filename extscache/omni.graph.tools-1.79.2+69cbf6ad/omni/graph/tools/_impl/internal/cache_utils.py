"""Utilities for dealing with the cache location used for on-demand generation.

This is part of the _internal module. Objects with a leading underscore are not intended to be used outside
of this module. All others may only be used for internal OmniGraph purposes.
"""

from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Any

import carb

from .logging_utils import LOG
from .versions import GenerationVersions, VersionProperties

# ==============================================================================================================
# Constant controlling the use of a temporary cache path location (mainly for testing).
_TEMPORARY_CACHE_PATH = None


# ==============================================================================================================
class TemporaryCacheLocation:
    """Context manager to temporarily redirect where the .ogn generated cache lives.
    with TemporaryCacheLocation(newcache_location):
        do_ogn_function()
    """

    def __init__(self, new_location: Path | str | None):
        self.__previous_location = _TEMPORARY_CACHE_PATH
        self.__new_location = new_location

    def __enter__(self):
        global _TEMPORARY_CACHE_PATH
        _TEMPORARY_CACHE_PATH = Path(self.__new_location) if self.__new_location is not None else None
        LOG.info("[Temporarily setting cache location to %s]", cache_location())
        return cache_location()

    def __exit__(self, exit_type: Any, value: Any, traceback: TracebackType):
        global _TEMPORARY_CACHE_PATH
        _TEMPORARY_CACHE_PATH = self.__previous_location
        LOG.info("[Restoring setting cache location to %s]", cache_location())
        self.__new_location = None
        self.__previous_location = None


# ==============================================================================================================
def cache_location() -> Path:
    """Returns the location of the normal OGN cache directory, taking into account any temporary override"""
    if _TEMPORARY_CACHE_PATH is None:
        return Path(carb.tokens.get_tokens_interface().resolve("${omni_cache}"))
    return _TEMPORARY_CACHE_PATH


# ==============================================================================================================
def full_cache_path(versions: GenerationVersions, ext_id: str, module_name: str) -> Path:
    """Finds the full cache path for an extension
    Args:
        versions: Versions of the OmniGraph extensions for which the cache is relevant
        ext_id: ID of the extension whose files are being cached, which is the name+version information
        module_name: Name of the module within the extension whose files are being cached
    Returns:
        Path to the root directory of the cache for the extension in the given generator version
    """
    # For now only the tools version is used in the construction of the cache path
    generator_version = ".".join(str(version) for version in versions[VersionProperties.GENERATOR])
    return cache_location() / "ogn_generated" / generator_version / ext_id / module_name / "ogn"
