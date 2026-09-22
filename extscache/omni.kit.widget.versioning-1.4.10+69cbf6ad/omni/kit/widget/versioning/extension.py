# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ext

from functools import lru_cache
from pathlib import Path

ICON_PATH = ""

@lru_cache()
def get_icons_path() -> str:
    return ICON_PATH


class VerioningExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        manager = omni.kit.app.get_app().get_extension_manager()
        extension_path = manager.get_extension_path(ext_id)
        global ICON_PATH
        ICON_PATH = Path(extension_path).joinpath("data").joinpath("icons")

    def on_shutdown(self):
        pass
