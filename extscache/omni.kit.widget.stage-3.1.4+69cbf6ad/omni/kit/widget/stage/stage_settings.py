# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# Selection Watch implementation has been moved omni.kit.widget.stage.
# Import it here for keeping back compatibility.
__all__ = ["StageSettings"]


class StageSettings:
    def __init__(self):
        super().__init__()

        self.show_prim_displayname = False
        self.show_inactive_prims = True
        self.auto_reload_prims = False
        self.children_reorder_supported = False
        self.flat_search = True
        self.show_undefined_prims = False
        self.show_abstract_prims = True
