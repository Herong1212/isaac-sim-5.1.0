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
from typing import Optional

from omni.kit.converter.common import ICadCoreExtBase

from .filters import JT_CORE_FILTER_DATA
from .helper import JtConverterHelper
from .options import JTConverterOptions

__all__ = ["JtCoreConverterExt", "get_instance", "JT_CORE_FILTER_DATA", "JtConverterHelper", "JTConverterOptions"]

_global_instance = None


class JtCoreConverterExt(ICadCoreExtBase):
    """JT Core Converter Extension"""

    FILTER_DATA = JT_CORE_FILTER_DATA
    OPTIONS_CLS = JTConverterOptions
    SERVICE_TITLE = "JT Converter"

    def on_startup(self, ext_id):
        """
        Initializes the JT Converter and/or registers the service
        """
        global _global_instance
        _global_instance = weakref.ref(self)
        super()._on_startup(ext_id)

    def on_shutdown(self):
        """
        Uninitialize the JT Converter and/or un-registers the service
        """
        global _global_instance
        _global_instance = None
        super()._on_shutdown()

    def create_converter_task(self, input_path: str, output_path: str, file_format_args: dict[str, str]):
        helper = JtConverterHelper()
        ret = helper.create_import_task(input_path, output_path, file_format_args)
        helper.destroy()
        helper = None
        return ret


def get_instance() -> Optional[JtCoreConverterExt]:
    """
    If available, returns the weakref pointer

    Returns: Optional[JTCoreConverterExt]

    """
    global _global_instance
    if _global_instance and _global_instance():
        return _global_instance()

    return None
