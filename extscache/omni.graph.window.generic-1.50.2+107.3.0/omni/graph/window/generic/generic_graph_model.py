# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import carb.settings
from omni.graph.window.core import OmniGraphModel


class GenericGraphModel(OmniGraphModel):
    def cull_legacy_prims(self):
        """Return True if the OgnPrim nodes should not be created in the graph"""
        return not carb.settings.get_settings().get("/persistent/omnigraph/createPrimNodes")
