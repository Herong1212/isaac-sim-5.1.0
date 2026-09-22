# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ext
import omni.kit.property.adapter.core as ac
import omni.usd

from .usd_adapter import UsdStageAdapter


class UsdPropertyAdapterExtension(omni.ext.IExt):
    """The entry point for Stage Window"""

    def __init__(self):
        super().__init__()
        self._registry = None

    def on_startup(self):
        self._registry = ac.get_adapter_registry()
        self._registry.register_stage_adapter("usd", UsdStageAdapter)

    def on_shutdown(self):
        self._registry.unregister_stage_adapter("usd")
