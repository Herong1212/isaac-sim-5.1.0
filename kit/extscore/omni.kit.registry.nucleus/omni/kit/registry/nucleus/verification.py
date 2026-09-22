import carb
import carb.dictionary

import os
from typing import Tuple, List

from .utils.common import _error, _info, _get_setting, get_ext_fullname_version
from .utils.changelog_parser import parse_changelog
from .utils.semver import SemanticVersion


REQUIRED_FIELDS = [
    "package/version",
    "package/title",
    "package/description",
    "package/category",
]

REQUIRED_FIELDS_WITH_PATH = [
    "package/readme",
    "package/preview_image",
    "package/icon",
    "package/changelog",
]


def verify_and_get_package_id_for_publishing(ext_dict: dict) -> str:
    """Strict verification if extension can be published.

    Returns package id.

    This verification can not be disabled by user.
    """
    ext_id = ext_dict.get("package", {}).get("packageId", "")
    if not ext_id:
        raise Exception("can't publish extension without package id.")

    # verify ext id
    try:
        _, version = get_ext_fullname_version(ext_id)
        SemanticVersion.parse(version)
    except ValueError as e:
        raise Exception(f"Invalid extension id: '{ext_id}'. Not a valid semver. Error: {e}")

    return ext_id


def verify_extension_for_publishing(ext_dict: carb.dictionary.Item) -> Tuple[bool, str]:
    """Verify extension for publishing. Returns tuple of (is_valid, changelog_content)
    """
    failures = []

    ext_id = ext_dict.get("package/packageId", "")

    is_kit_file = ext_dict.get("isKitFile", False)

    # Do not verify changelog for kit files. Apps are not required to have changelogs.
    if is_kit_file:
        changelog_content = ""
    else:
        changelog_content = _verify_and_extract_changelog(ext_dict, failures)

    if _get_setting("/app/extensions/skipPublishVerification", False):
        return True, changelog_content

    def err(str):
        _error(f"Extension: {ext_id} publishing verification failed. Reason(s): {str}")

    config_path = ext_dict.get("configPath", "")

    # required fields
    for field in REQUIRED_FIELDS:
        if not ext_dict.get(field, None):
            failures.append(f"Required field '{field}' is not set.")

    # check paths
    ext_path = ext_dict.get("path", "")
    if not is_kit_file:
        for field in REQUIRED_FIELDS_WITH_PATH:
            path = ext_dict.get(field, None)
            if not path:
                failures.append(f"Required field '{field}' is not set.")
                continue

            # Is path (or multiline string)
            if "\n" not in path:
                if not os.path.exists(os.path.join(ext_path, path)):
                    failures.append(f"Required field '{field}' path: '{path}' does not exist in {ext_path}.")

    if failures:
        extra_message = f"Fix all errors in: {config_path} and try again."
        err("\n - ".join([""] + failures) + "\n" + extra_message)
        return False, changelog_content

    _info(f"Extension: {ext_id} publishing verification passed.")
    return True, changelog_content


def _verify_and_extract_changelog(ext_dict, failures: List[str] = []) -> List[str]:
    package_version = ext_dict.get("package/version", "")
    changelog = ext_dict.get("package/changelog", "")
    try:
        if "\n" not in changelog:
            # try to read from file
            changelog = open(os.path.join(ext_dict.get("path", ""), changelog)).read()

        for version, date, content in parse_changelog(changelog):
            if version == package_version:
                return content

    except Exception as e:
        failures.append(f"Failed to parse changelog: '{e}'")
        return None

    failures.append(
        f"Failed to find version '{package_version}' in changelog. Please update changelog file. Refer to https://keepachangelog.com/en/1.0.0/ for more info."
    )
    return None
