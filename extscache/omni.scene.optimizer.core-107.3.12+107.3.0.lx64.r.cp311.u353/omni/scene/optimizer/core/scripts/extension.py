__copyright__ = "Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""


__all__ = [
    "_PublicExtension",
    "SOPluginVersion",
    "ExecutionContext",
    "ISceneOptimizer",
    "acquire_interface",
    "release_interface",
]


import omni.ext

from ..bindings._omni_scene_optimizer_core import *
from .commands import Commands


class _PublicExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._interface = acquire_interface()
        self.commands = Commands(self._interface)

    def on_shutdown(self):  # pragma: no cover
        self.commands.shutdown()
        self.commands = None
        release_interface(self._interface)
