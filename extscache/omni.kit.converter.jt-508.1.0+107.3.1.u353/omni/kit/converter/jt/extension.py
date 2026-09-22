# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

from omni.kit.converter.common import ICadExtBase
from omni.kit.converter.jt_core import JT_CORE_FILTER_DATA

from .delegate import JtConverterDelegate

__all__ = ["JtConverter", "JtConverterDelegate", "get_instance"]

_global_instance = None


class JtConverter(ICadExtBase):
    DELEGATE = JtConverterDelegate
    FILTER_DATA = JT_CORE_FILTER_DATA

    def on_startup(self, ext_id):
        global _global_instance
        _global_instance = weakref.ref(self)
        super()._on_startup(ext_id)

    def on_shutdown(self):
        global _global_instance
        _global_instance = None
        super()._on_shutdown()


def get_instance() -> Optional[JtConverter]:
    """
    If available, returns the weakref pointer

    Returns: Optional[JtConverter]
    """
    global _global_instance
    if _global_instance and _global_instance():
        return _global_instance()
