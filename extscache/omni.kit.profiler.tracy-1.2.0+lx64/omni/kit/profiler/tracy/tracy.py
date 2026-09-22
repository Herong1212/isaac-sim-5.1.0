# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
import platform
import subprocess
import threading

import carb
import carb.profiler
import carb.settings

import omni.ext
import omni.kit.app
from functools import lru_cache
from .tracy_actions import register_actions, deregister_actions


_profiler_tracy = None


@lru_cache()
def is_windows():
    return platform.system().lower() == "windows"


def exe_ext():
    if is_windows():
        return ".exe"
    else:
        return ""


def launch_process_async(args) -> subprocess.Popen:
    carb.log_info(f"launch_process_async : {args}")
    return subprocess.Popen(args)


def launch_process_sync(args):
    p = subprocess.run(args)
    return p.returncode


def get_ext_path():
    return omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)


def start_tracy_profiling():
    # Ensure that carb.profiler-tracy.plugin is loaded and set the capture mask to 1 so it starts profiling.
    carb.get_framework().load_plugins(loaded_file_wildcards=["carb.profiler-tracy.plugin"], search_paths=["kernel/plugins"])
    global _profiler_tracy
    _profiler_tracy = carb.profiler.acquire_profiler_interface(plugin_name="carb.profiler-tracy.plugin")

    if _profiler_tracy:
        _profiler_tracy.set_capture_mask(1)


def launch_tracy(trace_to_open=None,connect_to_local_host=False):
    tracy_path = os.path.join(get_ext_path(), "bin", "Tracy" + exe_ext())
    if trace_to_open is not None:
        launch_process_async([tracy_path, trace_to_open])
    elif connect_to_local_host:
        launch_process_async([tracy_path, "-a", "127.0.0.1"])
        start_tracy_profiling()
    else:
        launch_process_async([tracy_path])


def convert_json_to_tracy(json_filename, tracy_filename):
    import_chrome_path = os.path.join(get_ext_path(), "bin", "import-chrome" + exe_ext())
    launch_process_sync([import_chrome_path, json_filename, tracy_filename])

class Profiler(omni.ext.IExt):
    _auto_capture_process = None
    _auto_capture_path = None
    _auto_capture_thread = None

    def on_startup(self, ext_id):
        # Register actions
        self._ext_name = omni.ext.get_extension_name(ext_id)
        register_actions(self._ext_name)

        # Add menu items
        self.add_menu_items()

        # Start automated capture if enabled
        self.start_auto_capture()

    def on_shutdown(self):
        # Stop automated capture if enabled
        self.stop_auto_capture()

        # Remove menu items
        self.remove_menu_items()

        # Deregister actions
        deregister_actions(self._ext_name)

        # Clear the cached tracy profiler interface
        global _profiler_tracy
        _profiler_tracy = None

    def add_menu_items(self):
        try:
            import omni.kit.menu.utils
            from omni.kit.menu.utils import MenuItemDescription

            self._menu_entry = [
                MenuItemDescription(name="Tracy", sub_menu=
                    [MenuItemDescription(
                        name="Launch",
                        onclick_action=("omni.kit.profiler.tracy", "launch_tracy"),
                    ),
                    MenuItemDescription(
                        name="Launch and Connect",
                        onclick_action=("omni.kit.profiler.tracy", "launch_tracy_and_connect"),
                    )]
                )
            ]
            omni.kit.menu.utils.add_menu_items(self._menu_entry, name="Profiler")
        except (AttributeError, ImportError, ModuleNotFoundError):
            self._menu_entry = None

    def remove_menu_items(self):
        try:
            import omni.kit.menu.utils

            omni.kit.menu.utils.remove_menu_items(self._menu_entry, name="Profiler")
        except (AttributeError, ImportError, ModuleNotFoundError):
            pass
        self._menu_entry = None

    def start_auto_capture(self):
        auto_capture_enable_setting = "/exts/omni.kit.profiler.tracy/enableAutoCapture"
        auto_capture_file_setting = "/exts/omni.kit.profiler.tracy/autoCaptureFile"
        auto_capture_duration_setting = "/exts/omni.kit.profiler.tracy/autoCaptureDurationInSec"
        auto_capture_upload_enable = "/exts/omni.kit.profiler.tracy/enableAutoCaptureUpload"
        profiler_backend_setting = "/app/profilerBackend"

        self._settings = carb.settings.get_settings()
        self._settings.set_default_bool(auto_capture_enable_setting, False)
        auto_capture_enabled = self._settings.get_as_bool(auto_capture_enable_setting)
        self._settings.set_default_string(auto_capture_file_setting, "")
        auto_capture_file_path = self._settings.get_as_string(auto_capture_file_setting)
        self._settings.set_default_int(auto_capture_duration_setting, 30)
        auto_capture_duration_in_sec = self._settings.get_as_int(auto_capture_duration_setting)
        profiler_backend = self._settings.get(profiler_backend_setting)
        self._settings.set_default_bool(auto_capture_upload_enable, False)

        if auto_capture_enabled:
            validSettings = True
            if auto_capture_file_path == "":
                carb.log_warn(f"Automatic Tracy capture is enabled but no file path provided (setting : '{auto_capture_file_setting}')")
                validSettings = False

            if auto_capture_duration_in_sec <= 0:
                carb.log_warn(f"Automatic Tracy capture is enabled but duration is invalid : {auto_capture_duration_in_sec}s (setting : '{auto_capture_duration_setting}')")
                validSettings = False

            # Could be 'tracy', or the mux profiler with multiple backends '[nvtx,tracy]'
            if not "tracy" in profiler_backend:
                carb.log_warn(f"Automatic Tracy capture is enabled but /app/profilerBackend does not enable 'tracy' : {profiler_backend}")
                validSettings = False

            if validSettings:
                self._auto_capture_path = os.path.abspath(auto_capture_file_path)
                directory_name = os.path.dirname(self._auto_capture_path)
                if not os.path.exists(directory_name):
                    os.makedirs(directory_name)
                    if not os.path.exists(directory_name):
                        carb.log_error(f"Failed creating missing dirs for path {directory_name}")
                        return

                self._auto_capture_thread = threading.Thread(target=self.auto_capture_thread, args=[auto_capture_duration_in_sec])
                self._auto_capture_thread.start()
            
    def stop_auto_capture(self):
        if self._auto_capture_thread is not None and self._auto_capture_thread.is_alive():
            # Wait a few seconds and terminate if it is still alive
            capture_timeout_on_shutdown = 10
            carb.log_info(f"Tracy capture thread is pending, will wait for {capture_timeout_on_shutdown}")
            self._auto_capture_hread.join(capture_timeout_on_shutdown)
            if self._auto_capture_thread.is_alive():
                carb.log_warn(f"Tracy capture thread timeout, will terminate")
                self._auto_capture_thread.terminate()
                self._auto_capture_thread.join()
                carb.log_warn(f"Tracy capture thread terminated")

    def auto_capture_thread(self, capture_duration):
        carb.log_info(f"Starting automated Tracy capture for {capture_duration}s, saving to {self._auto_capture_path}")
        tracy_cli_path = os.path.join(get_ext_path(), "bin", "capture" + exe_ext())
        return_code = launch_process_sync([tracy_cli_path, "-a", "127.0.0.1", "-o", self._auto_capture_path, "-f", "-s", str(capture_duration)])

        if return_code != 0:
            carb.log_error(f"Tracy capture process returned {return_code}")
            return
        
        auto_capture_upload_enable = "/exts/omni.kit.profiler.tracy/enableAutoCaptureUpload"
        auto_capture_upload_url_s3 = "/exts/omni.kit.profiler.tracy/autoCaptureUploadUrlS3"
        auto_capture_upload_key_s3 = "/exts/omni.kit.profiler.tracy/autoCaptureUploadKeyS3"
        auto_capture_upload_secret_s3 = "/exts/omni.kit.profiler.tracy/autoCaptureUploadSecretS3"
        
        self._settings.set_default_bool(auto_capture_upload_enable, False)
        upload_enabled = self._settings.get_as_bool(auto_capture_upload_enable)
        if upload_enabled == False:
            return

        self._settings.set_default_string(auto_capture_upload_url_s3, "")
        upload_url = self._settings.get_as_string(auto_capture_upload_url_s3)
        self._settings.set_default_string(auto_capture_upload_key_s3, "")
        upload_key = self._settings.get_as_string(auto_capture_upload_key_s3)
        self._settings.set_default_string(auto_capture_upload_secret_s3, "")
        upload_secret = self._settings.get_as_string(auto_capture_upload_secret_s3)

        if upload_url == "":
            carb.log_warn(f"Upload failed, url is empty (setting : '{auto_capture_upload_url_s3}')")
            return
        
        try:
            import boto3
        except ImportError as e:
            carb.log_error(f"Upload failed, cannot import boto3: {e}")
            return
        
        try:
            from botocore.exceptions import ClientError
        except ImportError as e:
            carb.log_error(f"Upload failed, cannot import botocore.exceptions: {e}")
            return
        
        try:
            from urllib.parse import urlparse
        except ImportError as e:
            carb.log_error(f"Upload failed, cannot import urlparse: {e}")
            return

        s3_uri = urlparse(upload_url)
        if not s3_uri.scheme == "s3":
            carb.log_warn(f"Upload failed, not an S3 url : '{upload_url}')")
            return

        try:
            s3_bucket = s3_uri.hostname
            s3_file = s3_uri.path[1:]
            s3_file = s3_file.replace('%h', platform.node())
 
            if upload_key != "" and upload_secret != "":
                s3_client = boto3.client('s3', aws_access_key_id=upload_key, aws_secret_access_key=upload_secret)
            else:
                s3_client = boto3.client('s3')
            
            if os.path.exists(self._auto_capture_path):
                size_mb = os.path.getsize(self._auto_capture_path) / 1024.0 / 1024.0
                carb.log_info(f"Uploading {self._auto_capture_path} ({size_mb:.2f} MBs) to S3 {s3_bucket}/{s3_file}")
                try:
                    s3_client.upload_file(self._auto_capture_path, s3_bucket, s3_file,
                                                     Callback=ProgressPercentage(self._auto_capture_path))
                except ClientError as e:
                    carb.log_error(f"Upload error : {e}")
                    return

                url = s3_client.generate_presigned_url('get_object', ExpiresIn=24*60*60, Params={'Bucket': s3_bucket, 'Key': s3_file})
                carb.log_info(f"Uploaded {self._auto_capture_path} to : {url}")

            else:
                carb.log_error(f"Failed to upload Tracy capture, expected file is missing {self._auto_capture_path}")
                return

        except Exception as e:
            carb.log_error(f"Exception while trying to upload automatic Tracy capture to S3 {upload_url} : {e}")

class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            carb.log_info(f"Upload Progress for file {self._filename} : {percentage:.1f}")