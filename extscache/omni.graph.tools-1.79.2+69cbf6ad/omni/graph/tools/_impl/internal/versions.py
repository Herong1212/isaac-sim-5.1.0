"""Management of version compatibility information for the extensions (where not handled by the extension manager)"""

from __future__ import annotations  # For the nicer type specifiers, remove after Py 3.10

import re
from collections import defaultdict
from enum import Enum, auto
from functools import lru_cache
from pathlib import Path
from typing import Tuple

import omni.kit.app

__all__ = [
    "Compatibility",
    "ExtensionVersion_t",
    "get_generator_extension_version",
    "get_target_extension_version",
]


# ================================================================================
# Version information returned from the extension manager
ExtensionVersion_t = Tuple[int, int, int]


# ================================================================================
class Compatibility(Enum):
    """Potential types of version compatibility, mostly for testing purposes"""

    Incompatible = auto()
    FullyCompatible = auto()
    MajorVersionCompatible = auto()


# ================================================================================
@lru_cache(maxsize=len(Compatibility) + 1)
def get_generator_extension_version(
    compatibility: Compatibility | ExtensionVersion_t = Compatibility.FullyCompatible,
) -> ExtensionVersion_t:
    """Returns the current version of the extension omni.graph.tools, raising AttributeError if it could not be found
    since the fact that this script is running dictates that there should be a valid enabled version of this extension.
    If a compatibility is specified then tweak the returned version to have the named compatibility with the current one
    """
    if not isinstance(compatibility, Compatibility):  # pragma: no cover
        return compatibility

    if compatibility == Compatibility.Incompatible:
        return (0, 0, 0)

    if compatibility == Compatibility.MajorVersionCompatible:
        fully_compatible = get_generator_extension_version()
        return (fully_compatible[0], fully_compatible[1] - 1, fully_compatible[2])

    enabled_version = None
    mgr = omni.kit.app.get_app().get_extension_manager()
    for version in mgr.fetch_extension_versions("omni.graph.tools"):
        if version["enabled"]:
            enabled_version = version["version"]
    if enabled_version is None:  # pragma: no cover
        raise AttributeError("Failed to get the generator extension version")

    return enabled_version[:3]


# ================================================================================
@lru_cache(maxsize=len(Compatibility) + 1)
def get_target_extension_version(
    compatibility: Compatibility | ExtensionVersion_t = Compatibility.FullyCompatible,
) -> ExtensionVersion_t:
    """Returns the current version of the extension omni.graph.core, returning all 0s if it could not be found.
    This test may be running as part of the omni.graph.tools test suite, which will not enable omni.graph.core, so
    that is not an unexpected outcome.
    If a compatibility is specified then tweak the returned version to have the named compatibility with the current one
    """
    if not isinstance(compatibility, Compatibility):  # pragma: no cover
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
        current_version = (0, 0, 0)
    else:
        current_version = enabled_version[:3]

    return current_version


# ==============================================================================================================
def _version_compatibility(actual_version: ExtensionVersion_t, expected_version: ExtensionVersion_t) -> Compatibility:
    """Returns the compatibility of the two versions, assumed to reference the same extension"""
    if actual_version[0] != expected_version[0]:
        return Compatibility.Incompatible
    if actual_version[1] != expected_version[1]:
        return Compatibility.MajorVersionCompatible
    return Compatibility.FullyCompatible


# ==============================================================================================================
# !!! Do not change the enum values, they're used to extract properties from files by regex
class VersionProperties(Enum):
    """Enum containing the property names embedded by the generator into the database class definitions
    GENERATOR  Version of omni.graph.tools used to generate the file
    TARGET     Version of omni.graph.core ABI/API targeted by the generated code
    """

    GENERATOR = "GENERATOR_VERSION"
    TARGET = "TARGET_VERSION"


# ==============================================================================================================
class GenerationVersions:
    """Manages the version-related information for the node registration and generation"""

    # Helper for finding the version information in the generated database file. The first pattern is for the
    # Python database file, the second is for the C++ database file.
    VERSION_PATTERNS = {
        VersionProperties.GENERATOR: [
            re.compile(r"\s*GENERATOR_VERSION\s*=\s*\((.*)\)"),
            re.compile(r".*sm_generatorVersion.*make_tuple\(([0-9]+,[0-9]+,[0-9]+)\)"),
        ],
        VersionProperties.TARGET: [
            re.compile(r"\s*TARGET_VERSION\s*=\s*\((.*)\)"),
            re.compile(r".*sm_targetVersion.*make_tuple\(([0-9]+,\s*[0-9]+,\s*[0-9]+)\)"),
        ],
    }

    # --------------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        compatibility: Compatibility = None,
        generator_version: ExtensionVersion_t = None,
        target_version: ExtensionVersion_t = None,
    ):
        """Create a descriptor for generation versioning. No parameters mean create an invalid one. Specify just
        the compatibility to set both versions to something with that compatibility to the current versions. Add
        explicit generator or target versions to override the defaults.
        """
        self._versions = defaultdict(lambda: None)
        if compatibility is not None:
            self._versions[VersionProperties.GENERATOR] = get_generator_extension_version(compatibility)
            self._versions[VersionProperties.TARGET] = get_target_extension_version(compatibility)
        # Allow specification of conflicting keywords where the more specific ones win
        if generator_version is not None:
            self._versions[VersionProperties.GENERATOR] = tuple(generator_version)
        if target_version is not None:
            self._versions[VersionProperties.TARGET] = tuple(target_version)

    # --------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        return ", ".join(f"{version_type} = {version_value}" for version_type, version_value in self._versions.items())

    # --------------------------------------------------------------------------------------------------------------
    def __eq__(self, rhs: GenerationVersions) -> bool:
        """Implement the equal-to operator by comparing the generator version"""
        if rhs is None:
            return False
        return self._versions[VersionProperties.GENERATOR] == rhs._versions[VersionProperties.GENERATOR]

    # --------------------------------------------------------------------------------------------------------------
    def __ne__(self, rhs: GenerationVersions) -> bool:
        """Implement the not-equal-to operator by comparing the generator version"""
        if rhs is None:
            return True
        return self._versions[VersionProperties.GENERATOR] != rhs._versions[VersionProperties.GENERATOR]

    # --------------------------------------------------------------------------------------------------------------
    def __lt__(self, rhs: GenerationVersions) -> bool:
        """Implement the less-than operator, using only the generator version for comparison for now"""
        if rhs is None:
            return False
        my_version = self._versions[VersionProperties.GENERATOR]
        their_version = rhs._versions[VersionProperties.GENERATOR]
        if my_version is None:
            return their_version is not None
        if their_version is None:
            return False
        if my_version[0] < their_version[0]:
            return True
        if my_version[1] < their_version[1]:
            return True
        if my_version[2] < their_version[2]:
            return True
        return False  # pragma: no cover

    # --------------------------------------------------------------------------------------------------------------
    def __le__(self, rhs: GenerationVersions) -> bool:
        """Implement the less-than-or-equal-to operator, using only the generator version for comparison for now"""
        if rhs is None:
            return False
        my_version = self._versions[VersionProperties.GENERATOR]
        their_version = rhs._versions[VersionProperties.GENERATOR]
        if my_version is None:
            return True
        if their_version is None:
            return False
        if my_version[0] < their_version[0]:
            return True
        if my_version[1] < their_version[1]:
            return True
        if my_version[2] < their_version[2]:
            return True
        return True  # pragma: no cover

    # --------------------------------------------------------------------------------------------------------------
    def __gt__(self, rhs: GenerationVersions) -> bool:
        """Implement the greater-than operator, using only the generator version for comparison for now"""
        if rhs is None:
            return False
        my_version = self._versions[VersionProperties.GENERATOR]
        their_version = rhs._versions[VersionProperties.GENERATOR]
        if my_version is None:
            return False
        if their_version is None:
            return True
        if my_version[0] > their_version[0]:
            return True
        if my_version[1] > their_version[1]:
            return True
        if my_version[2] > their_version[2]:
            return True
        return False  # pragma: no cover

    # --------------------------------------------------------------------------------------------------------------
    def __ge__(self, rhs: GenerationVersions) -> bool:
        """Implement the greater-than-or-equal-to operator, using only the generator version for comparison for now"""
        if rhs is None:
            return False
        my_version = self._versions[VersionProperties.GENERATOR]
        their_version = rhs._versions[VersionProperties.GENERATOR]
        if my_version is None:
            return their_version is None
        if their_version is None:
            return True
        if my_version[0] > their_version[0]:
            return True
        if my_version[1] > their_version[1]:
            return True
        if my_version[2] > their_version[2]:
            return True
        return True  # pragma: no cover

    # --------------------------------------------------------------------------------------------------------------
    def __getitem__(self, version_of_what: VersionProperties) -> ExtensionVersion_t | None:
        """Allow [] lookup of the version type associated with the given version property"""
        return self._versions[version_of_what]

    # --------------------------------------------------------------------------------------------------------------
    def set_versions_from_database(self, database_path: Path):
        """Extract the version information from the file at the given path. If none available leave the unchanged"""
        versions_found = 0
        versions_needed = len(self.VERSION_PATTERNS)
        with open(database_path, "r", encoding="utf-8") as db_fd:
            for line in db_fd:
                for version_type, version_type_res in self.VERSION_PATTERNS.items():
                    if database_path.suffix == ".py":
                        version_type_re = version_type_res[0]
                    else:
                        version_type_re = version_type_res[1]
                    match = version_type_re.search(line)
                    if match:
                        self._versions[version_type] = tuple(
                            int(version) for version in f"{match.group(1)},0,0,0".replace(" ", "").split(",")[0:3]
                        )
                        versions_found += 1
                        if versions_found == versions_needed:
                            break

    # --------------------------------------------------------------------------------------------------------------
    def set_version(self, version_type: VersionProperties, version_number: ExtensionVersion_t):
        """Define an explicit version number for the given type"""
        self._versions[version_type] = tuple(version_number)

    # --------------------------------------------------------------------------------------------------------------
    def has_version(self) -> bool:
        """Returns True iff any version type has a valid version number"""
        return any(number is not None for number in self._versions.keys())

    # --------------------------------------------------------------------------------------------------------------
    def compatibility(self, rhs: GenerationVersions) -> Compatibility:
        """Returns the compatibility of this version versus the one passed in.
        The compatibility hierarchy is:
            - if any are incompatible the union is
            - else if any are only major version compatible the union is
            - else the union is fully compatibility
        """
        overall_compatibility = Compatibility.FullyCompatible
        for version_type in VersionProperties:
            type_compatibility = _version_compatibility(
                self._versions[version_type], rhs._versions[version_type]  # noqa: PLW0212
            )
            if type_compatibility == Compatibility.Incompatible:
                return Compatibility.Incompatible
            if type_compatibility == Compatibility.MajorVersionCompatible:
                overall_compatibility = type_compatibility
        return overall_compatibility
