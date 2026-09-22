# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import os
import platform
from typing import Optional

import carb

OPENXR_MAJOR_VERSION = 1

_FALLBACK_CONFIG_DIRS = "/etc/xdg"


def get_openxr_runtime():
    runtime = carb.settings.get_settings().get_as_string("/persistent/xr/system/openxr/runtime")
    if runtime == "custom":
        return carb.settings.get_settings().get_as_string("/persistent/xr/system/openxr/activeRuntimeJSON")
    return None


def has_valid_openxr_runtime():
    runtime_type = carb.settings.get_settings().get_as_string("/persistent/xr/system/openxr/runtime")

    # If bundled CloudXR is selected, we don't need to check for a runtime JSON file
    if runtime_type == "cloudxr":
        return True

    # First check if it's overridden by the setting
    runtime_json = get_openxr_runtime()

    # If not, do platform specific checks
    if not runtime_json:
        if platform.system() == "Windows":
            runtime_json = get_active_openxr_runtime_windows()
        else:
            runtime_json = get_active_openxr_runtime_linux()

    # Runtime is valid if the JSON path exists
    return runtime_json and os.path.exists(runtime_json)


def get_available_openxr_runtimes():
    if platform.system() == "Windows":
        runtime_jsons = get_available_openxr_runtimes_windows()
    else:
        runtime_jsons = get_available_openxr_runtimes_linux()

    runtimes = []
    for r in runtime_jsons:
        import json
        import pathlib

        try:
            with open(r, "r") as f:
                data = json.load(f)
                runtimes.append((data["runtime"]["name"], r))
        except Exception:
            path = pathlib.Path(r)
            if path.is_file():
                runtimes.append((path.stem, r))
    return runtimes


def get_active_openxr_runtime_windows():
    # If the environment variable is set, we use that
    env_var = os.getenv("XR_RUNTIME_JSON")
    if env_var:
        return env_var

    # Otherwise check the registry as the last resort
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\\Khronos\\OpenXR\\1",
        ) as openxr_key:
            return winreg.QueryValueEx(openxr_key, "ActiveRuntime")[0]

    except Exception as e:
        return None


# Logic adapted from OpenXR loader source
def _get_xdg_env_home(name: str, fallback_path: str) -> Optional[str]:
    # Try requested env variable first
    env_var = os.getenv(name)
    if env_var:
        return env_var

    # Fallback to $HOME/{fallback_path}
    env_var = os.getenv("HOME")
    if env_var:
        env_var += "/" + fallback_path
        return env_var

    return None


def _get_xdg_env_absolute(name: str, fallback_dirs: Optional[str]) -> Optional[str]:
    env_var = os.getenv(name)
    if env_var:
        return env_var
    else:
        return fallback_dirs


def _find_xdg_config_file(relative_dir: str, major_version: int) -> Optional[str]:
    import platform

    def _find_active_runtime_file(prefix_path: str, major_version: int) -> Optional[str]:
        decorated_path = os.path.join(prefix_path, str(major_version), f"active_runtime.{platform.machine()}.json")
        if os.path.exists(decorated_path):
            return decorated_path

        undecorated_path = os.path.join(prefix_path, str(major_version), "active_runtime.json")
        if os.path.exists(undecorated_path):
            return undecorated_path

        return None

    prefix_path = _get_xdg_env_home("XDG_CONFIG_HOME", ".config")
    if prefix_path:
        prefix_path = os.path.join(prefix_path, relative_dir)
        active_runtime = _find_active_runtime_file(prefix_path, OPENXR_MAJOR_VERSION)
        if active_runtime:
            return active_runtime

    xdg_paths = _get_xdg_env_absolute("XDG_CONFIG_DIRS", _FALLBACK_CONFIG_DIRS)
    if xdg_paths:
        for path in xdg_paths.split(":"):
            if path:
                path = os.path.join(path, relative_dir)
                active_runtime = _find_active_runtime_file(path, OPENXR_MAJOR_VERSION)
                if active_runtime:
                    return active_runtime

    return None


def get_active_openxr_runtime_linux() -> Optional[str]:
    # If the environment variable is set, we use that
    env_var = os.getenv("XR_RUNTIME_JSON")
    if env_var:
        return env_var

    try:
        return _find_xdg_config_file("openxr", OPENXR_MAJOR_VERSION)

    except Exception as e:
        return None


def get_available_openxr_runtimes_windows():
    try:
        import winreg

        runtimes = []
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\\Khronos\\OpenXR\\1\\AvailableRuntimes",
        ) as openxr_key:
            for i in range(winreg.QueryInfoKey(openxr_key)[1]):
                runtimes.append(winreg.EnumValue(openxr_key, i)[0])
        return runtimes
    except Exception as e:
        return []


def get_available_openxr_runtimes_linux():
    # TODO
    return []


def is_xcr_capture_layer_requested():
    if platform.system() == "Windows":
        registry_path = r"SOFTWARE\\Khronos\\OpenXR\\1\\ApiLayers\\Explicit"
        json_file_to_find = "openxr_xcr_capture_layer.json"
        try:
            import winreg

            # Open the registry key
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
            max_entries = 30
            # Iterate through the first 'max_entries' registry values
            for index in range(max_entries):
                try:
                    # Get the value name and data (path to the JSON file)
                    value_name, _, _ = winreg.EnumValue(reg_key, index)
                    # Check if the JSON file path contains 'openxr_xcr_capture_layer.json'
                    if json_file_to_find in value_name and os.path.exists(value_name):
                        return True
                except OSError:
                    # No more registry values to iterate or out of bounds
                    break

        except FileNotFoundError:
            return False
        return False

    elif platform.system() == "Linux":
        enabled_layers = os.getenv("XR_ENABLE_API_LAYERS", "")
        api_layer_path = os.getenv("XR_API_LAYER_PATH", "")
        capture_to = os.getenv("CAPTURE_LAYER_FILE_PATH", "")
        return capture_to and "xcr_capture" in enabled_layers and os.path.exists(api_layer_path)

    else:
        raise NotImplementedError(f"XCR capture layer is not supported on {platform.system()}")
