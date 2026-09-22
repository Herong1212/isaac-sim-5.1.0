# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import weakref
from typing import List, Optional

from omni.kit.converter.common import ICadCoreExtBase, is_asset_supported

from .filters import HOOPS_CORE_FILTER_DATA
from .helper import HoopsConverterHelper
from .options import HoopsOptions

__all__ = [
    "HoopsCoreConverter",
    "get_instance",
    "is_format_supported",
    "HOOPS_CORE_FILTER_DATA",
    "HoopsConverterHelper",
    "HoopsOptions",
]

_global_instance = None


class HoopsCoreConverter(ICadCoreExtBase):
    """Hoops Core Converter Extension"""

    FILTER_DATA = HOOPS_CORE_FILTER_DATA
    OPTIONS_CLS = HoopsOptions
    SERVICE_TITLE = "Hoops Converter"

    def on_startup(self, ext_id: str) -> None:
        """
        Initialize the Hoops Converter and/or un-registers the service
        """
        global _global_instance
        _global_instance = weakref.ref(self)
        super()._on_startup(ext_id)

    def on_shutdown(self) -> None:
        """
        Uninitialize the Hoops Converter and/or un-registers the service
        """
        global _global_instance
        _global_instance = None
        super()._on_shutdown()

    def create_converter_task(self, input_path: str, output_path: str, file_format_args: dict[str, str]):
        """
        Converts CAD file (import_path) to USD (output_path)

        Returns: An object containing the Path to the converted USD (str) and converter status (namedtuple).

        If the path is empty, the conversion has failed.

        The namedtuple contains error code (int) and error message (str).

        Args:
            input_path (str): Full path to the input file
            output_path (str): Full path to the output file
            file_format_args (dict[str,str]) : FileFormatArguments to pass to the converter
        """
        _helper = HoopsConverterHelper()
        ret = _helper.create_import_task(input_path, output_path, file_format_args)
        _helper.destroy()
        _helper = None
        return ret


def get_instance() -> Optional[HoopsCoreConverter]:
    """
    If available, returns the weakref pointer

    Returns: Optional[HoopsCoreConverter]
    """
    global _global_instance
    if _global_instance and _global_instance():
        return _global_instance()


def is_format_supported(input_file_path: str) -> bool:
    """
    Check if the file format is supported by the converter

    Args:
        input_file_path (str): Full path to the input file

    Returns: bool
    """
    extension_filters = []
    for extension in HOOPS_CORE_FILTER_DATA:
        extension_filters.extend(extension.filter_regexes)
    is_supported = is_asset_supported(input_file_path, extension_filters)
    return is_supported
