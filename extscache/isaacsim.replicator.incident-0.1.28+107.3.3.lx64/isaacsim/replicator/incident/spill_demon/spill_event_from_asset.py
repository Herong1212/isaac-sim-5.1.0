import omni.kit.commands
import omni.usd
import carb
from pxr import Usd, UsdGeom, Sdf, Gf

import os
from typing import Callable

from .scripts.spill_animator import SpillAnimator
from .spill_event_iface import SpillEventBase

from omni.metropolis.utils.semantics_util import SemanticsUtils

from omni.metropolis.utils.usd_util import USDUtil
from ..event_defines import IncidentData, IncidentCarbEventHelper


class SpillEventFromAsset(SpillEventBase):
    def __init__(
        self,
        spill_animator_factory: Callable[[str, float, float], SpillAnimator],
        data_path: str,
        name: str,
        selected_leakable_item_path: str,
        spillable_area_prim_paths: list[str],
        target_size: float = 1.0,
        leak_duration: float = 1.0,
    ):
        super().__init__()
        self.name = name
        self.selected_leakable_item_path = selected_leakable_item_path
        self.target_size = target_size
        self.leak_duration = leak_duration
        self.data_path = data_path
        self.spill_asset = None
        self.spill_animator_factory = spill_animator_factory
        self.spill_animator = None
        self.spillable_area_prim_paths = spillable_area_prim_paths
        self.on_create_spill()

    def on_create_spill(self):
        settings = carb.settings.get_settings()
        settings.set("/rtx/raytracing/fractionalCutoutOpacity", True)
        settings.set("/rtx/pathtracing/fractionalCutoutOpacity", True)

        stage = omni.usd.get_context().get_stage()
        purposes = [UsdGeom.Tokens.default_]
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)
        spill_asset_filepath = os.path.join(self.data_path, "Puddle", "Puddle.usd")

        self.asset_path = omni.usd.get_stage_next_free_path(stage, "/Spill", True)
        result, spill_prim = omni.kit.commands.execute(
            "CreatePayload",
            path_to=self.asset_path,
            asset_path=spill_asset_filepath,
            usd_context=omni.usd.get_context(),
            select_prim=False,
        )

        if not result:
            carb.log_error("Failed to create spill asset")
            return

        if not spill_prim:
            carb.log_error("Failed to create spill asset")
            return

        leakable_item_prim = stage.GetPrimAtPath(self.selected_leakable_item_path)
        position = bbox_cache.ComputeWorldBound(leakable_item_prim).ComputeCentroid()

        position = Gf.Vec3f(position[0], position[1], 0.0)

        def is_within_spill_area(box_range):
            position_2 = Gf.Vec2f(position[0], position[1])
            bbox_min_2 = Gf.Vec2f(box_range.GetMin()[0], box_range.GetMin()[1])
            bbox_max_2 = Gf.Vec2f(box_range.GetMax()[0], box_range.GetMax()[1])

            return (
                position_2[0] >= bbox_min_2[0]
                and position_2[0] <= bbox_max_2[0]
                and position_2[1] >= bbox_min_2[1]
                and position_2[1] <= bbox_max_2[1]
            )

        floor_found = False
        for spillable_area_prim_path in self.spillable_area_prim_paths:
            spillable_area_prim = stage.GetPrimAtPath(spillable_area_prim_path)
            world_bound = bbox_cache.ComputeWorldBound(spillable_area_prim)
            bbox_range = world_bound.ComputeAlignedBox()
            if is_within_spill_area(bbox_range):
                position[2] = world_bound.ComputeCentroid()[2]
                floor_found = True
                break
        if not floor_found:
            carb.log_error("[SpillFloorSearch] No floor found for spill event, assuming the floor is at height 0")

        puddle_base_path = self.asset_path + "/Puddle"

        self.spill_asset = stage.GetPrimAtPath(puddle_base_path)
        if not self.spill_asset or not self.spill_asset.IsValid():
            carb.log_error("[SpillEventFromAsset] Failed to find spill puddle base asset")
            return

        self.spill_asset.GetAttribute("xformOp:translate").Set(position)

        puddle_mesh_path = puddle_base_path + "/PuddleGlass"
        puddle_mesh = stage.GetPrimAtPath(puddle_mesh_path)
        if not puddle_mesh or not puddle_mesh.IsValid():
            carb.log_error("[SpillEventFromAsset] Failed to find spill puddle mesh asset")
            return

        puddle_mesh.GetAttribute("xformOp:scale").Set(Gf.Vec3f(0.0, 0.0, 0.0))

        self.spill_animator = self.spill_animator_factory(
            puddle_mesh_path, target_size=self.target_size, leak_duration=self.leak_duration
        )

    def on_trigger_spill(self):

        stage = omni.usd.get_context().get_stage()

        if not stage:
            carb.log_error("[SpillEventFromAsset] Failed to find stage")
            return

        if not self.spill_animator:
            carb.log_error("[SpillEventFromAsset] Failed to find spill animator")
            return

        self.spill_animator.activate()



        pos = USDUtil.get_prim_pos(prim=self.spill_asset, stage=stage, prim_path=None)
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(
            event_name=IncidentCarbEventHelper.carb_event_name(self.name),
            payload={
                "Payload": {
                    "event_data": IncidentData(event_name=self.name, event_type="spill event", event_position=pos)
                }
            },
        )
        carb.log_info(f"Trigger spill event '{self.name}' as {pos}.")
        leakable_item_prim = stage.GetPrimAtPath(self.selected_leakable_item_path)
        if leakable_item_prim:
            SemanticsUtils.add_update_prim_metrosim_semantics([leakable_item_prim], "class", "incident_leaking_item")
        if self.spill_asset and self.spill_asset.IsValid():
            SemanticsUtils.add_update_prim_metrosim_semantics([self.spill_asset], "class", "incident_liquid_spill")

    def on_reset_spill(self):
        if self.spill_animator:
            self.spill_animator.reset()

    def destroy(self):
        stage = omni.usd.get_context().get_stage()
        if not stage:
            carb.log_error("[SpillEventFromAsset] Failed to find stage. Things are about to go south.")
            super().destroy()
            return

        if self.spill_animator:
            self.spill_animator.destroy()
            self.spill_animator = None

        if self.asset_path:
            asset_prim = stage.GetPrimAtPath(self.asset_path)
            if asset_prim and asset_prim.IsValid():
                stage.RemovePrim(self.asset_path)

        if self.selected_leakable_item_path:
            leakable_item_prim = stage.GetPrimAtPath(self.selected_leakable_item_path)
            if leakable_item_prim and leakable_item_prim.IsValid():
                SemanticsUtils.remove_prim_metrosim_semantics([leakable_item_prim])

        super().destroy()
