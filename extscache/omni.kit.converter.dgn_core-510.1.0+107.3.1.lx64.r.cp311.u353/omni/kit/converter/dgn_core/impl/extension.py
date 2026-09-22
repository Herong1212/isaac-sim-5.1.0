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

import omni.kit.app
from omni.kit.converter.common import ICadCoreExtBase

from .filters import DGN_CONVERTER_SUPPORTED_FORMATS, DGN_CORE_FILTER_DATA
from .helper import DgnConverterCoreHelper
from .options import OdaDgnOptions

kit_version = omni.kit.app.get_app().get_kit_version()
if kit_version.startswith("106.5"):
    from .csdk_utils import initialize_connect_sdk

__all__ = [
    "DgnConverter",
    "get_instance",
    "DGN_CONVERTER_SUPPORTED_FORMATS",
    "DGN_CORE_FILTER_DATA",
    "DgnConverterCoreHelper",
    "OdaDgnOptions",
]

_global_instance = None


class DgnConverter(ICadCoreExtBase):
    """
    DGN Core Converter Extension
    """

    FILTER_DATA = DGN_CORE_FILTER_DATA
    OPTIONS_CLS = OdaDgnOptions
    SERVICE_TITLE = "DGN Converter"

    def on_startup(self, ext_id):
        """
        Initialize the DGN Converter and/or registers the service
        """
        global _global_instance
        _global_instance = weakref.ref(self)
        super()._on_startup(ext_id)

    def on_shutdown(self):
        """
        Uninitialize the DGN Converter and/or un-registers the service
        """
        global _global_instance
        _global_instance = None
        super()._on_shutdown()

    def create_converter_task(self, input_path: str, output_path: str, file_format_args: dict[str, str]):
        if kit_version.startswith("106.5"):
            initialize_connect_sdk(self.get_ext_name())
        _helper = DgnConverterCoreHelper()
        ret = _helper._create_import_task(input_path, output_path, file_format_args)
        _helper.destroy()
        _helper = None
        return ret


def get_instance() -> Optional[DgnConverter]:
    """
    If available, returns the weakref pointer
    """
    global _global_instance
    if _global_instance and _global_instance():
        return _global_instance()
