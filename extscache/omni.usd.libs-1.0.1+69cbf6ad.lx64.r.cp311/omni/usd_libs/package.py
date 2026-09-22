"""This module provides utilities for retrieving package information such as file paths, names, and versions from USD build's PACKAGE-INFO.yaml."""

import functools
import os
import typing
import json

import omni.kit.app
import omni.log


__all__ = ["get_info_path", "get_info_data", "get_name", "get_version"]


def get_info_path() -> str:
    """Returns the file path to the USD build's PACKAGE-INFO.yaml.

    This function retrieves the current USD build information from the extension manager
    and constructs the file path to PACKAGE-INFO.yaml, which contains metadata about
    the USD build.

    Returns:
        str: The file path to the USD build's PACKAGE-INFO.yaml."""
    app = omni.kit.app.get_app_interface()
    manager = app.get_extension_manager()

    # get the usd build information that is currently being built against
    usd_libs_ext_id = manager.get_enabled_extension_id("omni.usd.libs")
    usd_libs_path = manager.get_extension_path(usd_libs_ext_id)

    return os.path.join(usd_libs_path, "BUILD_INFO", "build_info.json")


@functools.lru_cache()
def get_info_data() -> typing.Optional[typing.Dict[str, object]]:
    """Retrieves the information from the USD build's PACKAGE-INFO.yaml.

    Returns:
        typing.Optional[typing.Dict[str, object]]: The info data dictionary extracted from the PACKAGE-INFO.yaml file. If
        the data is not available, will return None."""
    # get the current usd build information
    package_info_path = get_info_path()
    try:
        with open(package_info_path, "r") as file:
            json_data = json.load(file)
    except FileNotFoundError:
        omni.log.warn(f"{package_info_path} can not be found")
    except Exception as err:
        omni.log.warn(f"{package_info_path} can not be loaded: {err}")
    else:
        return json_data

    return None


def get_name() -> str:
    """Returns the name of the package from the package info data.

    Returns:
        str: The package name obtained from the package info data. If the package name
            is not found, returns an empty string."""
    package_info_data = get_info_data()
    return package_info_data.get("Package", "")


def get_version() -> str:
    """Retrieves the version information from the USD build's PACKAGE-INFO.yaml.

    Returns:
        str: The version string extracted from the PACKAGE-INFO.yaml file. If
        the version information is not available, an empty string is returned."""
    # get the current usd build information
    package_info_data = get_info_data()
    return package_info_data["usd_ver"]
