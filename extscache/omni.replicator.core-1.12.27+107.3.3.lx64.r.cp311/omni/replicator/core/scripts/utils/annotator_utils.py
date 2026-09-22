# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ctypes
import json
import re
import sys
from typing import Dict, Tuple

import carb
import numpy as np
import omni.graph.core as og
import omni.kit.async_engine
import warp as wp
from omni.gpu_foundation_factory import TextureFormat
from omni.graph.scriptnode._impl.extension import SCRIPTNODE_OPT_IN_SETTING, is_check_enabled, verify_scriptnode_load

SEMANTIC_SPLIT_REGEX = r"\s(?=\w+:)"
NUMPY_TO_WARP_MAP = {
    np.int8: wp.int8,
    np.byte: wp.int8,
    np.int16: wp.int16,
    np.short: wp.int16,
    np.int32: wp.int32,
    np.intc: wp.int32,
    np.int64: wp.int64,
    np.uint8: wp.uint8,
    np.ubyte: wp.uint8,
    np.uint16: wp.uint16,
    np.ushort: wp.uint16,
    np.uint32: wp.int32,  # PyTorch does not support uint32
    np.uintc: wp.int32,  # PyTorch does not support uint32
    np.uint64: wp.uint64,
    np.float16: wp.float16,
    np.float32: wp.float32,
    np.float64: wp.float64,
}
BASEDATATYPE_TO_NUMPY_MAP = {
    og.BaseDataType.DOUBLE: np.float64,
    og.BaseDataType.FLOAT: np.float32,
    og.BaseDataType.HALF: np.float16,
    og.BaseDataType.INT: np.int32,
    og.BaseDataType.INT64: np.int64,
    og.BaseDataType.UCHAR: np.uint8,
    og.BaseDataType.UINT: np.uint32,
    og.BaseDataType.UINT64: np.uint64,
}
NORMAL_ATTRIBUTE_NAMES = [
    "exec",
    "height",
    "width",
    "bufferSize",
    "data",
    "dataPtr",
    "cudaStream",
    "format",
    "__device",
    "__do_array_copy",
    "cudaDeviceIndex",
    "strides",
    "Ptr",
    "dataType",
    "dataShape",
]
ARRAY_PARAMS = ["height", "width", "bufferSize"]
PTR_ARRAY_PARAMS = ["bufferSize", "ptr", "dataType", "dataShape", "strides", "cudaDeviceIndex", "height", "width"]
DATA_PARAMS = ["dataPtr", "data"]


def _channels_dtype_to_format(channels, dtype):
    if dtype in NUMPY_TO_WARP_MAP:
        dtype = NUMPY_TO_WARP_MAP[dtype]
    if channels > 4:
        # Unsupported
        return 0
    if dtype == wp.uint8:
        return [
            0,
            TextureFormat.R8_UINT,
            TextureFormat.RG8_UINT,
            0,
            TextureFormat.RGBA8_UINT,
        ][channels]
    elif dtype == wp.int8:
        return [
            0,
            TextureFormat.R8_SINT,
            TextureFormat.RG8_SINT,
            0,
            TextureFormat.RGBA8_SINT,
        ][channels]
    elif dtype == wp.int16:
        return [
            0,
            TextureFormat.R16_SINT,
            TextureFormat.RG16_SINT,
            0,
            TextureFormat.RGBA16_SINT,
        ][channels]
    elif dtype == wp.int16:
        return [
            0,
            TextureFormat.R16_UINT,
            TextureFormat.RG16_UINT,
            0,
            TextureFormat.RGBA16_UINT,
        ][channels]
    elif dtype == wp.float16:
        return [
            0,
            TextureFormat.R16_SFLOAT,
            TextureFormat.RG16_SFLOAT,
            0,
            TextureFormat.RGBA16_SFLOAT,
        ][channels]
    elif dtype == wp.int32:
        return [
            0,
            TextureFormat.R32_SINT,
            TextureFormat.RG32_SINT,
            TextureFormat.RGB32_SINT,
            TextureFormat.RGBA32_SINT,
        ][channels]
    elif dtype == wp.uint32:
        return [
            0,
            TextureFormat.R32_UINT,
            TextureFormat.RG32_UINT,
            TextureFormat.RGB32_UINT,
            TextureFormat.RGBA32_UINT,
        ][channels]
    elif dtype == wp.float32:
        return [
            0,
            TextureFormat.R32_SFLOAT,
            TextureFormat.RG32_SFLOAT,
            TextureFormat.RGB32_SFLOAT,
            TextureFormat.RGBA32_SFLOAT,
        ][channels]
    else:
        return 0


def _format_to_elem_count(array_format):
    if array_format is None:
        return None
    format_name = TextureFormat(array_format).name
    if format_name.startswith("RGBA"):
        return 4
    elif format_name.startswith("RGB"):
        return 3
    elif format_name.startswith("RG"):
        return 2
    elif format_name.startswith("R"):
        return 1
    else:
        # unsupported
        return None


def _format_to_dtype(array_format: str):
    if array_format is None:
        return None
    format_name = TextureFormat(array_format).name
    if format_name.endswith("8_UINT"):
        return wp.uint8
    elif format_name.endswith("16_UINT"):
        return wp.uint16
    elif format_name.endswith("32_UINT"):
        return wp.uint32
    elif format_name.endswith("64_UINT"):
        return wp.uint64
    elif format_name.endswith("8_SINT"):
        return wp.int8
    elif format_name.endswith("16_SINT"):
        return wp.int16
    elif format_name.endswith("32_SINT"):
        return wp.int32
    elif format_name.endswith("64_SINT"):
        return wp.int64
    elif format_name.endswith("16_SFLOAT"):
        return wp.float16
    elif format_name.endswith("32_SFLOAT"):
        return wp.float32
    elif format_name.endswith("64_SFLOAT"):
        return wp.float64
    else:
        raise ValueError(f"Unexpected format name encountered: {format_name}")


def _get_dtypes(node_params: Dict, annotator_params: Dict = None, name: str = None):
    """Return a tuple containing the warp data type and the numpy data type

    Data type can be specified in one of three ways and in the following order:
    1. As a string token in the node parameter `dataType`
    2. As an integer representing the array format in the node parameter `format`
    3. As a parameter defined the the AnnotatorRegistry's `annotator_params`

    If no data format is specified, fallback to uint8.

    Args:
        node_params (Dict): _description_
        annotator_params (Dict, optional): _description_. Defaults to None.
        name: Annotator name that serves as an optional prefix. If none, "data" is used.

    Returns:
        _type_: _description_
    """
    if name is None:
        name = "data"
    data_type_attr = node_params.get(f"{name}Type")
    data_type_attr2 = node_params.get(f"{name}DataType")
    data_format_attr = node_params.get("format")
    if data_type_attr:
        try:
            resolved_data_type = _resolve_data_type(data_type_attr)
            return resolved_data_type["wp_dtype"], resolved_data_type["np_dtype"]
        except ValueError:
            # Fallback on next dtype specification
            pass
    if data_type_attr2:
        try:
            resolved_data_type = _resolve_data_type(data_type_attr2)
            return resolved_data_type["wp_dtype"], resolved_data_type["np_dtype"]
        except ValueError:
            # Fallback on next dtype specification
            pass
    if data_format_attr:
        data_format = data_format_attr.get()
        if data_format:
            try:
                wp_dtype = _format_to_dtype(data_format)
                return wp_dtype, wp.types.warp_type_to_np_dtype[wp_dtype]
            except ValueError:
                # No conversion from UNORM
                pass
    if annotator_params:
        # Fallback to annotator params
        if annotator_params.data_type in NUMPY_TO_WARP_MAP:
            return NUMPY_TO_WARP_MAP[annotator_params.data_type], annotator_params.data_type
        return wp.uint8, annotator_params.data_type
    # Fallback to uint8
    return wp.uint8, np.uint8


def _get_strides(strides_raw, warp_data_type):
    if np.all(strides_raw != 0):
        return (
            strides_raw[1],
            strides_raw[0],
            wp.types.type_size_in_bytes(warp_data_type),
        )
    else:
        return None


def _get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


def _get_pointer(param):
    data_view = og.AttributeValueHelper(param)
    data_view.gpu_ptr_kind = og.PtrToPtrKind.CPU
    data = data_view.get(on_gpu=True)
    return _get_address(data)


def _reshape_output_attr(
    attr,
    height,
    width,
    strides,
    buffer_size,
    elem_count,
    is2DArray,
    source_device,
    target_device,
    wp_dtype,
    np_dtype,
    output_array=None,
    **kwargs,
):
    if source_device.startswith("cuda"):
        ptr = _get_pointer(attr)
        return _reshape_output_ptr(
            ptr,
            height,
            width,
            strides,
            buffer_size,
            elem_count,
            source_device,
            target_device,
            wp_dtype,
            np_dtype,
            output_array,
        )
    else:
        data = attr.get_array(False, False, 0).copy()

        if not np_dtype:
            np_dtype = wp.types.warp_type_to_np_dtype[wp_dtype]

        if (data is None) or (len(data) < np.dtype(np_dtype).itemsize):
            if is2DArray:
                shape = (0, 0, elem_count) if elem_count > 1 else (0, 0)
            else:
                shape = (0, elem_count) if elem_count > 1 else (0)
            return np.empty(shape, np_dtype)

        # If datatype is default uchar, recast
        if data.dtype == np.uint8 and np_dtype != np.uint8:
            data = data.view(np_dtype)
        assert len(data) > 0
        if not is2DArray:
            return data.reshape(data.shape[0] // elem_count, elem_count) if elem_count > 1 else data

        data = np.squeeze(data.reshape(height, width, -1))
        if target_device == "cpu":
            return data
        else:
            return wp.array(data, device=target_device)


@carb.profiler.profile
def _reshape_output_ptr(
    ptr, height, width, strides, buffer_size, elem_count, source_device, target_device, wp_dtype, np_dtype, **kwargs
):
    type_size = wp.types.type_size_in_bytes(wp_dtype) if wp_dtype else np_dtype.itemsize
    if "shape" in kwargs:
        shape = tuple(kwargs.get("shape", 0))
        if len(shape) == 0:
            shape = 0
    elif height and width and elem_count:
        shape = (height, width, elem_count)
    elif buffer_size and width and height and wp_dtype:
        elem_count = buffer_size // height // width // type_size
        shape = (height, width, elem_count)
    else:
        shape = buffer_size // type_size
    carb.profiler.begin(1, "Wrap warp array")
    data = wp.types.array(
        dtype=wp_dtype, shape=shape, strides=strides, ptr=ptr, device=source_device, requires_grad=False
    )
    # If height is 1, squeeze the first dimension. This matches numpy squeeze behavior.
    # Calculate element count
    if buffer_size and width and height and type_size:
        elem_count = buffer_size // width // height // type_size

    # Data needs to be squeezed after retrieval otherwise strides don't match data
    if not data.is_contiguous:
        data = data.contiguous()
    if 0 in data.shape:
        data = data.reshape(0)
    elif 1 in data.shape:
        squeezed_shape = tuple(s for s in data.shape if s > 1) or (1,)
        data = data.reshape(squeezed_shape)
    carb.profiler.end(1)

    if not target_device.startswith("cuda"):
        if data.size > 0:  # TEMP fix because warp errors out when having empty array.
            data = data.numpy()

            # Squeeze 3rd dimension if possible
            if len(data.shape) == 3 and data.shape[-1] == 1:
                data = np.squeeze(data, axis=2)
            if len(data.shape) > 0 and data.shape[0] == 1:
                data = np.squeeze(data, axis=0)

            data = data.view(np_dtype)
            return data
        else:
            data = np.array([])
    return data


def _resolve_data_type(data_type_attr):
    try:
        data_params = {"np_dtype": None, "wp_dtype": None}
        resolved_type = data_type_attr.get_resolved_type()
        if resolved_type.base_type == og.BaseDataType.TOKEN:
            if data_type_attr.get():
                data_params["np_dtype"] = np.dtype("".join(data_type_attr.get())).type
            else:
                raise ValueError("dataType attribute is empty")
        else:
            data_params["np_dtype"] = BASEDATATYPE_TO_NUMPY_MAP[resolved_type.base_type]
            data_params["elem_count"] = resolved_type.tuple_count
        data_params["wp_dtype"] = wp.types.np_dtype_to_warp_type[np.dtype(data_params["np_dtype"])]
        return data_params
    except ValueError as e:
        raise ValueError(f"Error processing node attribute `{data_type_attr.get_name()}`: {e}")


def _update_params_for_data(data_params, node_params, data_name):
    if f"{data_name}Height" in node_params:
        data_params["height"] = node_params[f"{data_name}Height"].get()
    if f"{data_name}Width" in node_params:
        data_params["width"] = node_params[f"{data_name}Width"].get()
    if f"{data_name}BufferSize" in node_params:
        data_params["buffer_size"] = node_params[f"{data_name}BufferSize"].get()
    if f"{data_name}CudaDeviceIndex" in node_params:
        device_idx = node_params[f"{data_name}CudaDeviceIndex"].get()
        data_params["source_device"] = "cpu" if device_idx < 0 else f"cuda:{device_idx}"
    if f"{data_name}DataType" in node_params:
        data_params.update(_resolve_data_type(node_params[f"{data_name}DataType"]))
        if f"{data_name}Width" not in node_params:
            data_params["width"] = (
                data_params["buffer_size"]
                // wp.types.type_size_in_bytes(data_params["wp_dtype"])
                // data_params["elem_count"]
            )
    if f"{data_name}Strides" in node_params and "wp_dtype" in data_params:
        data_params["strides"] = _get_strides(node_params[f"{data_name}Strides"].get(), data_params["wp_dtype"])
    if f"{data_name}DataShape" in node_params:
        data_params["shape"] = node_params[f"{data_name}DataShape"].get()
    return data_params


# TODO: Temp fix, real fix should be in kit 109
def _resize_data_for_overscan(data, data_params):
    """Resize the output data for overscan"""
    settings = carb.settings.get_settings()
    datawindow_overscan_x = settings.get("/rtx/dataWindowNDC/0")
    datawindow_overscan_y = settings.get("/rtx/dataWindowNDC/1")
    datawindow_overscan_z = settings.get("/rtx/dataWindowNDC/2")  # x other direction
    datawindow_overscan_w = settings.get("/rtx/dataWindowNDC/3")  # y other direction

    if (
        (not settings.get_as_bool("/rtx/dataWindow/fitOutputToDataWindow"))
        and data_params["is2DArray"]
        and (
            datawindow_overscan_x != 0
            or datawindow_overscan_y != 0
            or datawindow_overscan_z != 0
            or datawindow_overscan_w != 0
        )
    ):

        data_original_width = round(data.shape[0] / (datawindow_overscan_z - datawindow_overscan_x))
        data_original_height = round(data.shape[1] / (datawindow_overscan_w - datawindow_overscan_y))

        data_offset_x = round(data_original_width * datawindow_overscan_x)
        data_offset_y = round(data_original_height * datawindow_overscan_y)
        data_offset_z = round(data_original_width * (datawindow_overscan_z - 1))
        data_offset_w = round(data_original_height * (datawindow_overscan_w - 1))

        return data[
            -data_offset_x : data_original_width + data_offset_z,
            -data_offset_y : data_original_height + data_offset_w,
        ]
    else:
        return data


class AnnotatorCache:
    """Cache static annotator parameters to improve performance

    Accessing OmniGraph attributes is relatively expensive. Cache static attributes where possible to improve
    performance in certain scenarios.
    """

    annotators = {}

    @classmethod
    @carb.profiler.profile
    def get_data(cls, annotator_id: int, node_params: Dict, annotator_params: Tuple, target_device: str, **kwargs):
        """Retrieve annotator array data.

        Args:
            annotator_id: Unique annotator identifier.
            node_params: Node parameters.
            annotator_params: Annotator parameters as an AnnotatorParams object.
            target_device: Target device onto white to return the data (eg. "cpu", "cuda:0")
        """
        use_common_params_cache = carb.settings.get_settings().get_as_bool(
            "/exts/omni.replicator/optim/useCachedParams"
        )
        params = cls.get_common_params(
            annotator_id, node_params, annotator_params, target_device, use_common_params_cache
        )
        device_idx = node_params["cudaDeviceIndex"].get() if "cudaDeviceIndex" in node_params else -1
        params["source_device"] = "cpu" if device_idx < 0 else f"cuda:{device_idx}"

        # Get alternate data names
        data_names = [n.split("Ptr")[0] for n in node_params if n.endswith("Ptr")]

        do_copy = kwargs.get("do_copy") if kwargs.get("do_copy") else params.get("do_array_copy")
        do_synchronize = False

        if data_names:
            data_outputs = {}
            for data_name in data_names:
                data_params = params.copy()
                data_params["ptr"] = node_params[f"{data_name}Ptr"].get()
                if data_name != "data":
                    # TODO jlafleche cache alternate data attributes
                    _update_params_for_data(data_params, node_params, data_name)

                # Get default parameters that shouldn't be cached
                wp_dtype, np_dtype = _get_dtypes(node_params, annotator_params, name=data_name)
                data_params.update({"wp_dtype": wp_dtype, "np_dtype": np_dtype})

                data, do_synchronize = cls._get_data_from_ptr(annotator_id, data_params, do_copy)

                # Handle overscan fit to window
                # TODO: Temp fix, real fix should be in kit 109
                data = _resize_data_for_overscan(data, data_params)

                if data.size == 0:
                    # Empty array, delete cache
                    cls.clear(annotator_id)
                data_outputs[data_name] = data
            return data_outputs, do_synchronize

        elif "data" in node_params and params["source_device"] != "cpu":
            params["ptr"] = _get_pointer(node_params["data"].get())
            data, do_synchronize = cls._get_data_from_ptr(annotator_id, params, do_copy)
            return {"data": data}, do_synchronize

        elif "data" in node_params:
            params["attr"] = node_params["data"]
            data = _reshape_output_attr(**params)

            if len(data) == 0:
                # Empty array, delete cache
                cls.clear(annotator_id)
            return {"data": data}, False
        else:
            return None, False

    @classmethod
    @carb.profiler.profile
    def _get_data_from_ptr(cls, annotator_id, params, do_copy):
        array = _reshape_output_ptr(**params)

        if do_copy:
            if isinstance(array, np.ndarray) and params.get("source_device", "").lower() == "cpu":
                # If warp array is on CPU, `.numpy()` is a zero-copy operation
                # and requires a copy to avoid buffer being overwritten
                return array.copy(), False

            elif isinstance(array, wp.array):
                # Create a copy array to manage lifetime
                cached_arrays = cls.annotators[annotator_id].get("output_array")

                # Check if attributes have changed and create a new cache if they have
                if (
                    not cached_arrays
                    or cached_arrays[0].shape != array.shape
                    or cached_arrays[0].dtype != array.dtype
                    or cached_arrays[0].strides != array.strides
                ):
                    cls.annotators[annotator_id]["output_array"] = []
                    cached_arrays = cls.annotators[annotator_id].get("output_array")

                cached_array = None
                for idx in range(len(cached_arrays)):
                    if sys.getrefcount(cached_arrays[idx]) == 2:
                        cached_array = cached_arrays[idx]
                        break

                if cached_array is None:
                    carb.profiler.begin(1, f"{annotator_id}: warp array allocation")
                    cached_array = wp.empty_like(array, device=params["target_device"])
                    cls.annotators[annotator_id].setdefault("output_array", []).append(cached_array)
                    carb.profiler.end(1)

                carb.profiler.begin(1, f"{annotator_id}: warp array copy")
                do_synchronize = str(cached_array.device) == "cpu" and str(array.device).startswith("cuda")
                wp.copy(cached_array, array)
                carb.profiler.end(1)
                return cached_array, do_synchronize
            else:
                return array, False
        else:
            return array, False

    @classmethod
    @carb.profiler.profile
    def get_common_params(
        cls, annotator_id: int, node_params: Dict, annotator_params: Tuple, target_device: str, use_cache: bool = False
    ):
        """Get annotator common parameters.

        Retrieves common parameters that rarely change so they can be cached for faster
        data retrieval.

        Args:
            annotator_id: Unique annotator identifier.
            node_params: Node parameters.
            annotator_params: Annotator parameters as an AnnotatorParams object.
            target_device: Target device onto white to return the data (eg. "cpu", "cuda:0")
            use_cache: If ``True``, cache common params for faster data retrieval. Defaults to ``False``.
        """
        if use_cache and annotator_id is not None and annotator_id in cls.annotators:
            common_params = cls.annotators[annotator_id]["common_params"].copy()
            if target_device:
                common_params["target_device"] = target_device
            return common_params
        else:
            wp_dtype, np_dtype = _get_dtypes(node_params, annotator_params=annotator_params)
            if "strides" in node_params:
                strides_raw = node_params["strides"].get()
                if np.all(strides_raw != 0):
                    strides = (
                        strides_raw[1],
                        strides_raw[0],
                        wp.types.type_size_in_bytes(wp_dtype),
                    )
                else:
                    strides = None
            else:
                strides = None

            elem_count = 1
            buffer_size = node_params["bufferSize"].get()
            height = node_params["height"].get()
            width = node_params["width"].get()
            is2DArray = annotator_params.is_2d_array if annotator_params else (width and height)

            if "format" in node_params and node_params["format"].get():
                array_format = node_params["format"].get()
                elem_count = _format_to_elem_count(array_format)
            elif buffer_size > 0 and height > 0 and width > 0:
                elem_count = buffer_size // height // width // wp.types.type_size_in_bytes(wp_dtype)

            if is2DArray and not buffer_size and elem_count:
                buffer_size = height * width * elem_count * wp.types.type_size_in_bytes(wp_dtype)

            if target_device is None:
                target_device = node_params["__device"].get()

            if target_device == "":
                target_device = "cpu"
            elif isinstance(target_device, str) and (
                target_device.lower() == "cpu" or target_device.lower().startswith("cuda")
            ):
                target_device = target_device.lower()
            else:
                raise ValueError(
                    f"Invalid device `{target_device}` specified. Device must be one of ['cpu', 'cuda', 'cuda:<device_index>']"
                )

            common_params = {
                "height": height,
                "width": width,
                "strides": strides,
                "buffer_size": buffer_size,
                "elem_count": elem_count,
                "is2DArray": is2DArray,
                "target_device": target_device,
                "wp_dtype": wp_dtype,
                "np_dtype": np_dtype,
                "do_array_copy": node_params["__do_array_copy"].get(),
            }

            # Add optional params
            if "dataShape" in node_params:
                shape = node_params["dataShape"].get()
                if len(shape) > 0:
                    common_params["shape"] = shape

            if annotator_id is None:
                return common_params
            else:
                cls.annotators.setdefault(annotator_id, {})["common_params"] = common_params
                return cls.annotators[annotator_id]["common_params"]

    @classmethod
    def clear(cls, annotator_id: int = None):
        """Clear cache

        Args:
            annotator_id: Optionally specify the annotator to clear from the cache. If `None`, clear entire cache.
                Defaults to `None`.
        """
        if annotator_id:
            if annotator_id in cls.annotators:
                cls.annotators.pop(annotator_id)
        else:
            cls.annotators = {}


def _get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


def _get_pointer(param):
    data_view = og.AttributeValueHelper(param)
    data_view.gpu_ptr_kind = og.PtrToPtrKind.CPU
    data = data_view.get(on_gpu=True)
    return _get_address(data)


@carb.profiler.profile
def get_extra_data(params: Dict):
    """Get all other annotator outputs, excluding array data.

    Args:
        params: Annotator parameters
    """
    data_names = [n.split("Ptr")[0] for n in params.keys() if n.endswith("Ptr")]
    data_exclusions = [f"{dn}{an[0].capitalize()}{an[1:]}" for dn in data_names for an in PTR_ARRAY_PARAMS]
    extra_data = {}
    for key in params.keys():
        if key in NORMAL_ATTRIBUTE_NAMES:
            continue

        if key in data_exclusions:
            continue

        if key.startswith("_"):
            continue

        item = params[key]
        if (
            item.get_type_name() == "string"
            and item.get_array(False, False, 0) is not None
            and ("idToLabels" in key or "idToSemantics" in key)
        ):
            array = item.get_array(False, False, 0)
            if len(array) == 0:
                id_to_labels = {}
            else:
                id_to_labels = json.loads("".join(array))
            extra_data[key] = id_to_labels
        elif (
            item.get_type_name() == "token[]"
            and item.get_array(False, False, 0) is not None
            and key == "labels"
            and "ids" in params
        ):
            if not params.get("ids"):
                raise ValueError("Label array is paired with id array, but id array is missing.")
            # TODO: Too specific. Need to handle more general case.
            label_array = item.get_array(False, False, 0)

            semantic_array = None
            if params.get("semantics"):
                semantic_array = params["semantics"].get_array(False, False, 0)

            id_to_labels = {}
            id_to_semantics = {}

            if len(label_array) != 0:
                id_array = params["ids"].get_array(False, False, 0).reshape((len(label_array), -1))
                for i in range(len(label_array)):
                    if len(id_array[i]) == 1:
                        key = int(id_array[i][0])
                    else:
                        key = tuple(id_array[i])

                    if params.get("_legacyIDs"):
                        key = str(key)

                    if ":" not in label_array[i]:  # Prim path
                        id_to_labels[key] = label_array[i]
                    else:
                        type_to_labels = {}

                        for type_to_label in re.split(SEMANTIC_SPLIT_REGEX, label_array[i]):
                            semantic_type, semantic_label = type_to_label.split(":", 1)
                            type_to_labels[semantic_type] = semantic_label
                        id_to_labels[key] = type_to_labels

                    if ":" not in label_array[i]:  # Prim path
                        id_to_labels[key] = label_array[i]
                    else:
                        type_to_labels = {}

                        for type_to_label in re.split(SEMANTIC_SPLIT_REGEX, label_array[i]):
                            semantic_type, semantic_label = type_to_label.split(":", 1)
                            type_to_labels[semantic_type] = semantic_label
                        id_to_labels[key] = type_to_labels

                    if semantic_array:
                        type_to_semantic = {}

                        for type_to_label in re.split(SEMANTIC_SPLIT_REGEX, semantic_array[i]):
                            semantic_type, semantic_label = type_to_label.split(":", 1)
                            type_to_semantic[semantic_type] = semantic_label

                        id_to_semantics[key] = type_to_semantic
                extra_data["idToLabels"] = id_to_labels
                if semantic_array:
                    extra_data["idToSemantics"] = id_to_semantics
            else:
                extra_data["idToLabels"] = {}

                if params.get("semantics"):
                    extra_data["idToSemantics"] = {}

        elif key == "ids" or key == "semantics":
            # Skip ids and semantics because it is handled with label array.
            continue
        else:
            data_type = item.get_resolved_type()
            if data_type.array_depth == 0:
                extra_data[key] = item.get()
            else:
                extra_data[key] = item.get_array(False, False, 0)
    return extra_data


@carb.profiler.profile
def _get_annotator_data(
    node_params: Dict,
    annotator_params: Tuple,
    device: str = None,
    annotator_id: Tuple[str] = None,
    do_copy: bool = False,
    use_legacy_structure: bool = True,
):
    # Handle additional keys
    extra_data = get_extra_data(node_params)
    # FIXME: Make height and width not a required params here, because not all annotators are 2D
    do_synchronize = False
    if all([a in node_params for a in ARRAY_PARAMS]) and any([a in node_params for a in DATA_PARAMS]):
        annotator_output, do_synchronize = AnnotatorCache.get_data(
            annotator_id, node_params, annotator_params, do_copy=do_copy, target_device=device
        )

        if use_legacy_structure:
            # For backwards compatibility, duplicate non-data keys to "info"
            for key in list(annotator_output.keys()):
                if key != "data":
                    extra_data[key] = annotator_output[key]

            if extra_data:
                annotator_output["info"] = extra_data
            elif len(annotator_output) == 1:
                annotator_output = annotator_output[next(iter(annotator_output))]
        elif extra_data:
            annotator_output.update(extra_data)
    else:
        annotator_output = extra_data
    return annotator_output, do_synchronize


@carb.profiler.profile
def get_annotator_data(
    node: og.Node,
    annotator_params: Tuple,
    from_inputs: bool = False,
    device: str = "cpu",
    annotator_id: Tuple[str] = None,
    do_copy: bool = False,
    use_legacy_structure: bool = True,
) -> Dict:
    """Retrieve data from annotator node.

    Args:
        node: The OmniGraph annotator node object from which to retrieve data.
        annotator_params: AnnotatorParams tuple specifying annotator metadata.
        from_inputs: If ``True``, annotator data is extracted from the node inputs. Defaults to ``False``.
        device: Specifies the device onto white to return array data.
            Valid values: ``["cpu", "cuda", "cuda:<index>"]`` Defaults to ``"cpu"``.
        annotator_id: Unique annotator identifier. Defaults to ``None``.
        do_copy: If ``True``, arrays are copied before being returned. This copy ensures that the data lifetime can
            be managed by downstream processes. Defaults to ``False``.
        use_legacy_structure: Specifies the output structure to return. If ``True``, the legacy structure is returned.
            The legacy structure changes depending on the data being returned:

                - only array data: <array>
                - only non-array data: {<anno_attribute_0>: <anno_output_0>, <anno_attribute_n>: <aanno_output_n>}
                - array data and non-array data: {"data": <array>, "info": {<anno_attribute_0>: <anno_output_0>, <anno_attribute_n>: <aanno_output_n>}}

            If ``False``, a consistent data structure is returned:

                - all cases: {<anno_attribute_0>: <anno_output_0>, <anno_attribute_n>: <anno_output_n>}

            Defaults to ``True``.
    """
    carb.profiler.begin(1, "get annotator attributes")
    prefix = "inputs" if from_inputs else "outputs"
    node_params = {}

    if isinstance(device, str) and (device.lower() == "cpu" or device.lower().startswith("cuda")):
        device = device.lower()
    elif device is not None:
        raise ValueError(
            f"Invalid device `{device}` specified. Device must be one of ['cpu', 'cuda', 'cuda:<device_index>']"
        )

    # FIXME: Because of OM-47286, can't pass a bundle for now.
    for attribute in node.get_attributes():
        name = attribute.get_name()

        if prefix not in name:
            continue
        attr_str = name.split(":")
        if len(attr_str) != 2:
            continue
        _, param = attr_str
        node_params[param] = attribute
    carb.profiler.end(1)
    try:
        data, do_synchronize = _get_annotator_data(
            node_params, annotator_params, device, annotator_id, do_copy, use_legacy_structure
        )
        if do_synchronize:
            wp.synchronize()
        return data
    except ValueError as e:
        carb.log_error(f"Encountered an error retrieving data from annotator {annotator_id}. {e}")


def script_node_check(nodes: list = []):
    """Prompt user before enabling a script node

    Call this script in any node capable of executing arbitrary scripts within the node's
    ``initialize()`` call.

    .. note::
        Only one prompt attempt is made per session

    """
    settings = carb.settings.get_settings()
    has_been_prompted = settings.get("/omni/replicator/scriptNodePrompted")
    if is_check_enabled() and not has_been_prompted:
        # Check is enabled - see user already opted-in
        scriptnode_opt_in = settings.get(SCRIPTNODE_OPT_IN_SETTING)

        if not scriptnode_opt_in:
            # The check is enabled but they opted out, or haven't been prompted yet
            try:
                import omni.kit.window.popup_dialog  # noqa
            except ImportError:
                # Don't prompt in headless mode
                return
            settings.set("/omni/replicator/scriptNodePrompted", True)

            async def prompt():
                verify_scriptnode_load(nodes)
                # Wait a few frames before re-enabling prompt
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                settings.set("/omni/replicator/scriptNodePrompted", False)

            omni.kit.async_engine.run_coroutine(prompt())


def check_should_run_script():
    return bool(carb.settings.get_settings().get(SCRIPTNODE_OPT_IN_SETTING))
