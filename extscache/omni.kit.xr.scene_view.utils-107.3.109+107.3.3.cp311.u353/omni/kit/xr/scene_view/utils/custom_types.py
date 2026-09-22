# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["_TWidget", "_TSceneView"]

from typing import TypeVar

import omni.ui as ui
import omni.ui.scene as sc

_TWidget = TypeVar("_TWidget", bound=ui.Widget)
_TSceneView = TypeVar("_TSceneView", bound=sc.SceneView)
