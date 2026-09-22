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
from omni.kit.converter.hoops_core import HOOPS_CORE_FILTER_DATA

from .delegate import HoopsConverterDelegate

__all__ = ["HoopsConverter", "HoopsConverterDelegate", "get_instance"]

_global_instance = None


class HoopsConverter(ICadExtBase):
    DELEGATE = HoopsConverterDelegate
    FILTER_DATA = HOOPS_CORE_FILTER_DATA

    def on_startup(self, ext_id):
        global _global_instance
        _global_instance = weakref.ref(self)
        super()._on_startup(ext_id)

    def on_shutdown(self):
        global _global_instance
        _global_instance = None
        super()._on_shutdown()


def get_instance() -> Optional[HoopsConverter]:
    """
    If available, returns the weakref pointer

    Returns: Optional[HoopsConverter]
    """
    global _global_instance
    if _global_instance and _global_instance():
        return _global_instance()
