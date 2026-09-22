# Copyright (c) 2021-2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
from typing import Any, Callable, Sequence

import carb
import omni.kit.app


class Capture:
    """Base capture delegate"""
    def __init__(self, *args, **kwargs):
        self.__future = asyncio.Future()

    def capture(self, aov_map, frame_info, hydra_texture, result_handle):
        carb.log_error("Capture used, but capture was not overriden")

    async def wait_for_result(self, completion_frames: int = 2):
        await self.__future
        while completion_frames:
            await omni.kit.app.get_app().next_update_async()
            completion_frames = completion_frames - 1
        return self.__future.result()

    def _set_completed(self, value: Any = True):
        if not self.__future.done():
            self.__future.set_result(value)


class RenderCapture(Capture):
    """Viewport capturing delegate that iterates over multiple aovs and calls user defined capture_aov method for all
    of interest"""
    def __init__(self, aov_names: Sequence[str], per_aov_data: Sequence[Any] = None,
                 frame_to_capture=None, viewport=None, **kwargs):
        super().__init__(**kwargs)

        # Accept a 1:1 mapping a 1:0 mapping or a N:1 mapping of AOV to data
        if per_aov_data is None:
            self.__aov_mapping = dict.fromkeys(aov_names, None)
        elif len(aov_names) == len(per_aov_data):
            self.__aov_mapping = dict(zip(aov_names, per_aov_data))
        else:
            if len(per_aov_data) != 1:
                assert len(aov_names) == len(per_aov_data), f"Mismatch between {len(aov_names)} aovs and {len(per_aov_data)} per_aov_data"
            self.__aov_mapping = {aov: per_aov_data for aov in aov_names}

        self.__frame_info = None
        self.__hydra_texture = None
        self.__result_handle = None
        self.__render_capture = None
        self.__frame_to_capture = frame_to_capture
        self.__viewport = viewport
        assert self.__frame_to_capture is None or self.__viewport is not None

    @property
    def aov_data(self):
        return self.__aov_mapping.values()

    @property
    def aov_names(self):
        return self.__aov_mapping.keys()

    @property
    def resolution(self):
        return self.__frame_info.get('resolution')

    @property
    def view(self):
        return self.__frame_info.get('view')

    @property
    def projection(self):
        return self.__frame_info.get('projection')

    @property
    def frame_number(self):
        return self.__frame_info.get('frame_number')

    @property
    def viewport_handle(self):
        return self.__frame_info.get('viewport_handle')

    @property
    def hydra_texture(self):
        return self.__hydra_texture

    @property
    def result_handle(self):
        return self.__result_handle

    @property
    def frame_info(self):
        return self.__frame_info

    @property
    def render_capture(self):
        if not self.__render_capture:
            try:
                import omni.renderer_capture
                self.__render_capture = omni.renderer_capture.acquire_renderer_capture_interface()
            except ImportError:
                carb.log_error("omni.renderer_capture extension must be loaded to use this interface")
                raise
        return self.__render_capture

    def capture(self, aov_map, frame_info, hydra_texture, result_handle):
        if self.__frame_to_capture is not None:
            swh_frame_number = frame_info["swh_frame_number"]
            if swh_frame_number is None:
                carb.log_error("No SWH frame number available while trying to capture frame {}".format(
                    self.__frame_to_capture))
                self._set_completed(None)
                return
            if swh_frame_number > self.__frame_to_capture:
                carb.log_error("Missed capturing frame {}, got frame {}".format(
                    self.__frame_to_capture, swh_frame_number))
                self._set_completed(None)
                return
            if swh_frame_number < self.__frame_to_capture:
                try:
                    self.__viewport.schedule_capture(self)
                except ReferenceError:
                    carb.log_error(f"Cannot capture frame {self.__frame_to_capture}, viewport reference expired")
                    self._set_completed(None)
                return

        try:
            self.__hydra_texture = hydra_texture
            self.__result_handle = result_handle
            self.__frame_info = frame_info
            color_data, color_data_set = None, False
            completed = []
            for aov_name, user_data in self.__aov_mapping.items():
                aov_data = aov_map.get(aov_name)
                if aov_data:
                    self.capture_aov(user_data, aov_data)
                    completed.append(aov_name)
                elif aov_name == "":
                    color_data, color_data_set = user_data, True

            if color_data_set:
                aov_name = "LdrColor"
                aov_data = aov_map.get(aov_name)
                if aov_data is None:
                    aov_name = "HdrColor"
                    aov_data = aov_map.get(aov_name)
                if aov_data:
                    self.capture_aov(color_data, aov_data)
                    completed.append(aov_name)
        finally:
            self.__hydra_texture = None
            self.__result_handle = None
            self.__render_capture = None
            self._set_completed(completed)

    def capture_aov(self, user_data, aov: dict):
        carb.log_error("RenderCapture used, but capture_aov was not overriden")

    def save_aov_to_file(self, file_path: str, aov: dict, format_desc: dict = None):
        if format_desc:
            if hasattr(self.render_capture, "capture_next_frame_rp_resource_to_file"):
                self.render_capture.capture_next_frame_rp_resource_to_file(file_path, aov["texture"]["rp_resource"],
                                                                           format_desc=format_desc,
                                                                           metadata=self.__frame_info.get("metadata"))
                return
            carb.log_error("Format description provided to capture, but not honored")

        self.render_capture.capture_next_frame_rp_resource(file_path, aov["texture"]["rp_resource"],
                                                           metadata=self.__frame_info.get("metadata"))

    def deliver_aov_buffer(self, callback_fn: Callable, aov: dict):
        self.render_capture.capture_next_frame_rp_resource_callback(callback_fn, aov["texture"]["rp_resource"],
                                                                    metadata=self.__frame_info.get("metadata"))

    def save_product_to_file(self, file_path: str, render_product: str):
        self.render_capture.capture_next_frame_using_render_product(self.viewport_handle, file_path, render_product)


class MultiAOVFileCapture(RenderCapture):
    """Class to capture multiple AOVs into multiple files"""
    def __init__(self, aov_names: Sequence[str], file_paths: Sequence[str], format_desc: dict = None, **kwargs):
        super().__init__(aov_names, file_paths, **kwargs)
        self.__format_desc = format_desc

    @property
    def format_desc(self):
        return self.__format_desc

    @format_desc.setter
    def format_desc(self, value: dict):
        self.__format_desc = value

    def capture_aov(self, file_path: str, aov: dict, format_desc: dict = None):  # noqa PLW0237
        self.save_aov_to_file(file_path, aov, self.__format_desc)


class MultiAOVByteCapture(RenderCapture):
    """Class to deliver multiple AOVs buffer/bytes to a callback function"""
    def __init__(self, aov_names: Sequence[str], callback_fns: Sequence[Callable] = None, **kwargs):
        super().__init__(aov_names, callback_fns, **kwargs)

    def capture_aov(self, callback_fn: Callable, aov: dict):  # noqa PLW0237
        self.deliver_aov_buffer(callback_fn or self.on_capture_completed, aov)

    def on_capture_completed(self, buffer, buffer_size, width, height, byte_format):
        pass


class FileCapture(MultiAOVFileCapture):
    """Class to capture a single AOVs (defaulting to color) into one file"""
    def __init__(self, file_path: str, aov_name: str = "", **kwargs):
        super().__init__([aov_name], [file_path], **kwargs)


class ByteCapture(MultiAOVByteCapture):
    """Class to capture a single AOVs (defaulting to color) to a user callback"""
    def __init__(self, callback_fn: Callable = None, aov_name: str = "", **kwargs):
        super().__init__([aov_name], [callback_fn], **kwargs)
