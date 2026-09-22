# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["SceneViewUtilsExtension"]

from pydoc import locate
from types import NoneType
from typing import Optional, Type

import carb
import omni.ext

from .actiongraph_no_code_ui_integration import ActionGraphNoCodeUiIntegration
from .sceneview_utils import SceneViewUtils


class SceneViewUtilsExtension(omni.ext.IExt):
    __ag_integration_instance: Optional[ActionGraphNoCodeUiIntegration] = None

    @staticmethod
    def on_startup(ext_id: str) -> None:
        SceneViewUtils._set_extension_id(ext_id)

        carb.settings.get_settings().set_default_string("/xr/scene_ui/action_graph_integration_class", "")
        klass_name = carb.settings.get_settings().get_as_string("/xr/scene_ui/action_graph_integration_class")

        klass: Type[ActionGraphNoCodeUiIntegration] = locate(klass_name) if klass_name else NoneType  # type: ignore
        if not klass or not issubclass(klass, ActionGraphNoCodeUiIntegration):
            klass = ActionGraphNoCodeUiIntegration

        SceneViewUtilsExtension.__ag_integration_instance = klass()

    @staticmethod
    def on_shutdown() -> None:
        SceneViewUtils._shutdown_extension()
        SceneViewUtilsExtension.__ag_integration_instance = None
