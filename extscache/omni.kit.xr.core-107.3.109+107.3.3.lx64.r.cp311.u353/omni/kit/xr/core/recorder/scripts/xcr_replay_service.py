# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import asyncio
import os
import pathlib
import platform
import tempfile
from typing import Final, Optional

import carb
import omni.kit.xr.core.test_utils as test_utils
from omni.kit.xr.core import XRCore, XRCoreEventType

# import C++ test xcr
from .._xr_xcr import XCRReplayAPI, XCRReplayServiceMainConfig

# In seconds that should be 90 fps
NINETY_FPS_FIXED_ELAPSED_TIME: Final = 0.0111


class XCRReplayService:
    """
    Wrapper class to contain all functionalities for XCR Replay OpenXR Runtime service completely.
    """

    def __init__(
        self,
        replay_filepath: str,
        xr_test: test_utils.XRTest,
        service_config: Optional[XCRReplayServiceMainConfig] = None,
    ):
        self._xcr_api = XCRReplayAPI()
        self._replay_filepath = replay_filepath
        self._xr_test = xr_test
        self._service_config = service_config
        self._xcr_runtime_json_path = test_utils.tests_directories.get_xcr_runtime_json()
        self._carb_settings = carb.settings.get_settings()

        if platform.system() == "Linux":
            if self.is_running_on_ci():
                # In Linux CI runner, monado service is spawned in the background and we should use "XRT_NO_STDIN"
                # to prevent the service from exiting immediately
                os.environ["XRT_NO_STDIN"] = "TRUE"

            xcr_temp_path = pathlib.Path(os.path.join(tempfile.gettempdir(), "runtime-user"))
            xcr_temp_path.mkdir(parents=True, exist_ok=True)
            for socket_path in [
                pathlib.Path(xcr_temp_path, "ipc_xcr"),
                pathlib.Path("/run", "user", f"{os.getuid()}", "ipc_xcr"),
            ]:
                if socket_path.exists():
                    carb.log_warn(f"Cleaning up socket [{socket_path}] (XCR service is running already?)")
                    os.remove(socket_path)

    def set_registry_value_for_windows(self):
        """Sets the XCR runtime as the active OpenXR runtime in the Windows registry."""
        try:
            import winreg  # Import winreg here for Windows-specific operations

            # Define the registry parameters
            registry_path = r"SOFTWARE\Khronos\OpenXR\1"
            value_name = "ActiveRuntime"
            value_data = test_utils.get_xcr_runtime_json()

            # Open or create the registry key with write access
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, registry_path)

            # Set the registry value
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)

            # Close the key
            winreg.CloseKey(key)

            carb.log_info(f"Successfully set '{value_name}' to '{value_data}' in the Windows registry.")
        except ImportError:
            carb.log_error("XCR cannot be set as OpenXR Active Runtime. Winreg module is only available on Windows.")
        except PermissionError:
            carb.log_error(
                "XCR cannot be set as OpenXR Active Runtime. Permission denied. Try running the script as an administrator."
            )
        except Exception as e:
            carb.log_error(f"XCR cannot be set as OpenXR Active Runtime. An error occurred: {e}")

    def clear_registry_value_for_windows(self):
        """Removes the ActiveRuntime entry from the Windows registry."""
        try:
            import winreg  # Import winreg here for Windows-specific operations

            # Define the registry parameters
            registry_path = r"SOFTWARE\Khronos\OpenXR\1"
            value_name = "ActiveRuntime"

            # Open the registry key with write access
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_SET_VALUE)

            # Delete the registry value
            winreg.DeleteValue(key, value_name)

            # Close the key
            winreg.CloseKey(key)

            carb.log_info(f"Successfully removed '{value_name}' from the Windows registry.")
        except FileNotFoundError:
            carb.log_warn(f"The registry value '{value_name}' does not exist. No action taken.")
        except PermissionError:
            carb.log_error(
                "XCR cannot be removed as OpenXR Active Runtime. Permission denied. Try running the script as an administrator."
            )
        except Exception as e:
            carb.log_error(f"An error occurred while clearing the registry: {e}")

    async def ensure_xcr_is_active_openxr_runtime(self):
        if (
            self._carb_settings.get("/persistent/xr/system/openxr/activeRuntimeJSON") != self._xcr_runtime_json_path
            or self._carb_settings.get("/persistent/xr/system/openxr/runtime") != "custom"
        ):
            self._carb_settings.set("/persistent/xr/system/openxr/runtime", "custom")
            self._carb_settings.set("/persistent/xr/system/openxr/activeRuntimeJSON", self._xcr_runtime_json_path)
            await self._xr_test.wait_post_sync_async(50)

    async def __aenter__(self):
        await self.ensure_xcr_is_active_openxr_runtime()
        await self._xr_test.wait_post_sync_async(1)

        if self._service_config:
            self._xcr_api.start_replay_service_with_config(self._replay_filepath, self._service_config)
        else:
            self._xcr_api.start_replay_service(self._replay_filepath)

        self._xcr_api.set_replay_frame(0)
        self._carb_settings.set("/xr/raycastsDeterministic", True)

        await self._xr_test.wait_post_sync_async(10)

        return self

    async def __aexit__(self, type, value, traceback):
        self._xcr_api.stop_replay_service_immediately()
        self.set_simulated_elapsed_time(0.0)

        # Clean up registry when running on Windows CI runner
        if self.is_running_on_ci() and platform.system() == "Windows":
            self.clear_registry_value_for_windows()

        await self._xr_test.wait_post_sync_async(1)

    def __del__(self):
        self._xcr_api = None
        self._replay_filepath = None
        self._xcr_runtime_json_path = None
        self._xr_test = None
        self._interaction_profile = None

    def get_xcr_api(self) -> XCRReplayAPI:
        return self._xcr_api

    def is_running_on_ci(self) -> bool:
        return os.getenv("GITLAB_CI") != None

    def set_simulated_elapsed_time(self, elapsed_time: float):
        self._carb_settings.set("/xr/replay/simulatedElapsedTime", elapsed_time)

    async def replay_frames_and_perform_golden_image_viewport_tests(
        self,
        capture_frequency: int,
        output_file_name: str,
        threshold: float,
        source_name: Optional[str],
        fixed_elapsed_time: Optional[float] = None,
        max_frame: Optional[int] = None,
    ):
        """
        Iterate through all frames with XCR and capture viewport & compare golden image.
        """

        future: asyncio.Future = asyncio.Future()
        xcr_api = self.get_xcr_api()
        frame_index = 0
        frames_count = xcr_api.get_replay_frame_count()

        if max_frame is not None and max_frame < frames_count:
            frames_count = max_frame

        all_file_names = []
        golden_image_test = test_utils.ViewportGoldenImageTest(self._xr_test.is_comparison_disabled())

        # If not None, then we use one concrete value for fixed elapsed time.
        if fixed_elapsed_time is not None:
            self.set_simulated_elapsed_time(fixed_elapsed_time)

        def after_presync_capture_and_compare_frame(ev: carb.events.IEvent):
            nonlocal frame_index
            if frame_index < frames_count:

                # If it is None, we calculate dynamic delta time based on frames times.
                if fixed_elapsed_time is None:
                    if frame_index == 0:
                        self.set_simulated_elapsed_time(NINETY_FPS_FIXED_ELAPSED_TIME)
                    else:
                        prev_frame_timestamp = xcr_api.get_replay_frame_timestamp(frame_index - 1)
                        cur_frame_timestamp = xcr_api.get_replay_frame_timestamp(frame_index)
                        self.set_simulated_elapsed_time(cur_frame_timestamp - prev_frame_timestamp)

                xcr_api.set_replay_frame(frame_index)
                if frame_index > 0 and frame_index % capture_frequency == 0:
                    file_paths, file_names = golden_image_test.prepare_paths(
                        f"{output_file_name}_{frame_index:04}", source_name
                    )
                    all_file_names.extend(file_names)
                    for file_path in file_paths:
                        XRCore.get_singleton().schedule_capture_viewport_frame(file_path)
            else:
                comparison_result = golden_image_test.compare_all_test_images(all_file_names, threshold, source_name)
                future.set_result(comparison_result)

            frame_index = frame_index + 1

        sub_pre_sync = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(
                XRCoreEventType.pre_sync_update,
                after_presync_capture_and_compare_frame,
                name="after_presync_capture_and_compare_frame",
                order=-1,
            )
        )

        result = await future
        sub_pre_sync = None  # noqa: F841
        return result
