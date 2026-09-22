# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["VisibilityModel"]

import omni.ui as ui
import omni.usd
import omni.timeline

from pxr import UsdGeom, Usd


class VisibilityModel(ui.AbstractValueModel):
    def __init__(self, stage_item):
        super().__init__()
        self.__stage_item = stage_item

    @property
    def stage_item(self):
        return self.__stage_item

    def destroy(self):
        self.__stage_item = None

    def get_value_as_bool(self) -> bool:
        """Reimplemented get bool"""
        # Invisible when it's checked.
        return not self.__stage_item.visible

    def _get_prim_visibility(self, prim):
        timeline = omni.timeline.get_timeline_interface()
        time = timeline.get_current_time()

        imageable = UsdGeom.Imageable(prim)
        visibility_attr = imageable.GetVisibilityAttr()

        time_sampled = visibility_attr.GetNumTimeSamples() > 1
        if time_sampled:
            curr_time_code = time * prim.GetStage().GetTimeCodesPerSecond()
        else:
            curr_time_code = Usd.TimeCode.Default()

        return imageable.ComputeVisibility(curr_time_code)

    def set_value(self, value: bool):
        """Reimplemented set bool"""
        prim = self.__stage_item.prim
        if not prim:
            return

        usd_context = omni.usd.get_context_from_stage(prim.GetStage())
        if usd_context:
            selection_paths = usd_context.get_selection().get_selected_prim_paths()
        else:
            selection_paths = []

        # If the updating prim path is one of the selection path, we change all selected path. Otherwise, only change itself
        prim_path = prim.GetPath()
        stage = prim.GetStage()
        update_paths = selection_paths if prim_path in selection_paths else [prim_path]

        imageable = UsdGeom.Imageable(prim)
        if imageable:
            visibility = self._get_prim_visibility(prim)
            visible = False if visibility == UsdGeom.Tokens.invisible else True
            omni.kit.commands.execute(
                "ToggleVisibilitySelectedPrims", selected_paths=update_paths, stage=stage, visible=not visible
            )
