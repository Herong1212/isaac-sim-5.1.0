# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ext
from .registry_manager import RegistryManager


class RegistryProviderExt(omni.ext.IExt):
    def on_startup(self):
        self._registry_manager = RegistryManager()

    def on_shutdown(self):
        self._registry_manager.destroy()
        self._registry_manager = None
