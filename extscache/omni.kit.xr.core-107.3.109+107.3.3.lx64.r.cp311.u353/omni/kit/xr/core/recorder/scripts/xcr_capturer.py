from __future__ import annotations

import os
import platform
import tempfile
from typing import TYPE_CHECKING

import carb
from omni.kit.xr.core import XRCore

if TYPE_CHECKING:
    # depends on omni.ui only for type checking
    import omni.ui as ui

__all__ = ["get_xcr_capture_filepath", "on_capture_button_clicked"]


def on_capture_button_clicked(is_capture_started: bool, frame: ui.Frame):
    carb_setting = carb.settings.get_settings()
    if carb_setting.get("/xr/system/openxr/xcr/capture/enabled"):
        message_type = carb.events.type_from_string("xcr.on_capture_button_clicked")
        XRCore.get_singleton().get_message_bus().dispatch(
            message_type,
            payload={"is_capture_started": is_capture_started, "capture_directory_path": get_xcr_capture_filepath()},
        )
        frame.start_button.enabled, frame.stop_button.enabled = not is_capture_started, is_capture_started
    else:
        carb.log_warn("XCR Capture is disabled")


def get_xcr_capture_filepath():
    current_os = platform.system()
    if current_os == "Windows":
        capture_directory = get_xcr_capture_filepath_windows()
    elif current_os == "Linux":
        capture_directory = get_xcr_capture_filepath_linux()

    if not capture_directory:
        # Use system temp directory as fallback
        capture_directory = tempfile.gettempdir()
        carb.log_info(f"Using system temp directory as capture directory: {capture_directory}")

    return capture_directory


def get_xcr_capture_filepath_windows():
    try:
        import winreg

        # Open the registry key under HKEY_LOCAL_MACHINE for Windows
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\XCR")
        capture_layer_file_path, regtype = winreg.QueryValueEx(registry_key, "CaptureLayerPath")
        winreg.CloseKey(registry_key)

        if capture_layer_file_path:
            return capture_layer_file_path
        else:
            return "C:\\"  # default value hardcoded in XCR
    except Exception:
        return None


def get_xcr_capture_filepath_linux():
    # Retrieve the value from an environment variable for Linux
    return os.getenv("CAPTURE_LAYER_FILE_PATH")
