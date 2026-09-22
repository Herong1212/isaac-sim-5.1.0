# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["get_instance", "get_data_path_internal", "WidgetToolBarExtension"]

import carb
import omni.ext
import omni.kit.app
from functools import lru_cache
from pathlib import Path

from .toolbar import Toolbar

_toolbar_instance = None


@lru_cache()
def get_data_path_internal() -> Path:
    manager = omni.kit.app.get_app().get_extension_manager()
    extension_path = manager.get_extension_path_by_module("omni.kit.widget.toolbar")
    return Path(extension_path).joinpath("data")

def get_instance() -> Toolbar:
    """Get the instance of the toolbar."""
    return _toolbar_instance


class WidgetToolBarExtension(omni.ext.IExt):
    """omni.kit.widget.toolbar ext"""

    def on_startup(self, ext_id):
        global _toolbar_instance
        carb.log_info("[omni.kit.widget.toolbar] Startup")
        _toolbar_instance = Toolbar()

    def on_shutdown(self):
        carb.log_info("[omni.kit.widget.toolbar] Shutdown")
        global _toolbar_instance
        if _toolbar_instance:
            _toolbar_instance.destroy()
        _toolbar_instance = None
