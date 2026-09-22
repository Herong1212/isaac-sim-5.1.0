"""Handle the mapping of OGN types onto the various attribute union groups"""

import json
from contextlib import suppress
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..utils import ParseError, is_comment, logger

UNION_DEFINITION_KEY = "unionDefinitions"
ATTRIBUTE_UNION_CONFIG_FILE_NAME = "AttributeUnionConfiguration.json"

UnionGroupType = Dict[str, List[str]]
EntryType = Union[List[str], str, Dict]
UnionFileType = Dict[str, EntryType]


# ============================================================================
def _unpack(item: EntryType, definition: UnionFileType, depth: int = 0) -> List[str]:
    """Unpacks a single entry in the attribute union table, performing substitutions
    as necessary

    Args:
        item - The item to unpack
        definition - the source table to perform look ups from
        depth - recursion guard, to avoid self-referenced or cross-referenced entries

    Returns:
        A list of strings representing the unpacked values.

    Exceptions:
        ParseError if the dictionary is not correctly formed.
    """
    if depth > 2 * len(definition.keys()):  # 2x accounts for dictionary lookups + possible entries
        raise ParseError(f"Recursion depth exceeded parsing {item}. Possible self-reference detected.")

    result = []
    if isinstance(item, list):
        for i in item:
            result = result + _unpack(i, definition, depth + 1)
    elif isinstance(item, str):
        if item in definition:
            result = _unpack(definition[item], definition, depth + 1)
        else:
            result.append(item)
    elif isinstance(item, dict):
        entries = item.get("entries", None)
        append = item.get("append", None)
        if entries is None:
            raise ParseError(f'Invalid entry. Expected "entries" key on {item}')
        if append is None or not isinstance(append, str):  # pragma: no cover   Firewall
            raise ParseError(f'Invalid entry. Expected "append" key with string value on {item}')
        unpacked_list = _unpack(entries, definition, depth + 1)
        result = [e + append for e in unpacked_list]
    else:
        raise ParseError(f"Invalid entry type on {item}")

    return result


# ==============================================================================================================
def _find_build_config_directory(current_path: Path) -> Optional[Path]:
    """
    Given a path, finds the build configuration path in parent hierarchy
    Returns None if not found.
    """
    try:
        path = next(parent_dir for parent_dir in current_path.parents if parent_dir.name == "exts")
    except StopIteration:  # pragma: no cover   Firewall
        return None

    # If using the Kit SDK this should be the path
    config_path = path.parent / "dev" / "ogn" / "config"
    if not config_path.is_dir():  # pragma: no cover   Old configuration
        # Inside of Kit
        inside_kit = True
        try:
            path = next(parent_dir for parent_dir in path.parents if parent_dir.name == "_build")
        except StopIteration:
            inside_kit = False
        # Using Kit Kernel
        if inside_kit:
            config_path = path / "ogn" / "config"
        else:
            # OM-124464: can't look for the config files in the extension directly when using kit-kernel
            try:
                path = next(parent_dir for parent_dir in current_path.parents if parent_dir.name == "omni")
            except StopIteration:
                return None
            config_path = path.parents[0] / "ogn"

    return config_path if config_path.is_dir() else None


# ==============================================================================================================
def get_attribute_union_configuration_file() -> Path:
    """Searches for the path to configuration file containing the list for the attribute unions
    It searches in:
        ogn_config directory in the package (useful if run from source directory and using kit-sdk)
        ogn directory in the package (useful if run from source directory and using kit-kernel)
        _build/ogn/config directory (if run from a build folder)
        ${kit}/dev/ogn/config if at runtime.

    Throws an exception if the file cannot be found in any one of the given paths
    """

    # the path to the local file if this is being run in the source directory
    with suppress(StopIteration):
        local_ext = next(parent_dir for parent_dir in Path(__file__).parents if parent_dir.name == "omni.graph.tools")
        local_path = (local_ext / "ogn_config" / ATTRIBUTE_UNION_CONFIG_FILE_NAME).resolve()
        if local_path.is_file():  # pragma: no cover   Old configuration
            return local_path
        # kit-kernel uses an alternate path.
        local_path = (local_ext / "ogn" / ATTRIBUTE_UNION_CONFIG_FILE_NAME).resolve()
        if local_path.is_file():  # pragma: no cover   Old configuration
            return local_path

    # next the path to the config file in the build directory
    build_dir = _find_build_config_directory(Path(__file__))
    if build_dir is not None:
        build_path = build_dir / ATTRIBUTE_UNION_CONFIG_FILE_NAME
        if build_path.is_file():
            return build_path

    # if we are part of the runtime try to get the configuration file from kit
    try:  # pragma: no cover   Old configuration
        import carb

        kit_path = Path(carb.tokens.get_tokens_interface().resolve("${kit}"))
        config_dir = kit_path / "dev" / "ogn" / "config"
        config_path = config_dir / ATTRIBUTE_UNION_CONFIG_FILE_NAME
        if not config_path.is_file():
            raise ModuleNotFoundError

        return config_path
    except ModuleNotFoundError:  # pragma: no cover   Old configuration
        raise FileNotFoundError("Could not find attribute union configuration file")  # noqa: PLW0707


# ============================================================================
def parse_union_definitions(definition: UnionFileType) -> UnionGroupType:
    """Parses the definition file, expanding the values as necessary
    Args:
        definition - the attributes union dictionary as read in from JSON
    Returns:
        A dictionary where the attribute union values have been flattened and
        transformed
    """

    # unpack the dictionary, flattening and performing any operations
    result = {}
    for key, value in definition.items():
        if not is_comment(key):
            result[key] = _unpack(value, definition)
    return result


# =============================================================================
def get_attribute_union_definitions(path_to_config_file: Path) -> UnionGroupType:
    """
    Loads the attribute configuration file from the given path
    Args:
        path_to_config_file - the path to the configuration file to open
    Returns:
        A dictionary representing the file on disk. Exceptions are passed directly
        to the caller
    """
    with path_to_config_file.open("r") as fp:
        definitions = json.load(fp)[UNION_DEFINITION_KEY]
    return parse_union_definitions(definitions)


# =============================================================================
def load_attribute_union_groups() -> UnionGroupType:
    """
    Loads and returns the dictionary of attribute union groupings.
    Logs errors and returns an empty dictionary if an error occurs
    """
    result = {}
    path = Path()
    try:
        path = get_attribute_union_configuration_file()
    except FileNotFoundError as err:
        logger.error("Could not load the configuration file for attribute unions: %s", err)
        return result

    try:
        result = get_attribute_union_definitions(path)
    except ParseError as err:
        logger.error("An error occurred parsing union group definitions: %s", err)
        result = {}

    return result
