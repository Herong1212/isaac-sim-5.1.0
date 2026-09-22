# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ext
from omni.kit.manipulator.prim.core import get_prim_data_accessor_registry

from .data_accessor import UsdDataAccessor


class ManipulatorPrim2UsdExt(omni.ext.IExt):
    """A class for registering and unregistering a USD data accessor.

    This class extends the `omni.ext.IExt` interface and is used to integrate a USD data accessor into the global registry. It handles the lifecycle of the USD data accessor by registering it on startup and unregistering it on shutdown.
    """

    def on_startup(self, ext_id):
        """Initializes the extension with a specific extension identifier.

        Args:
            ext_id (str): The identifier for the extension being started."""
        self._prim_data_accessor_registry = get_prim_data_accessor_registry()
        self._prim_data_accessor_registry.register_data_accessor(UsdDataAccessor, "USD")

    def on_shutdown(self):
        """Cleans up the extension by unregistering the data accessor and resetting the registry."""
        self._prim_data_accessor_registry.unregister_data_accessor("USD")
        self._prim_data_accessor_registry = None
