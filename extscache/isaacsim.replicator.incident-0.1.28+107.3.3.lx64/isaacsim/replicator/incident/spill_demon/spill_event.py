# import omni.kit.commands
# from pxr import Usd, UsdGeom

# import os
# from typing import Callable
# import omni.replicator.core as rep

# from .scripts.spill_animator import SpillAnimator
# from omni.metropolis.utils.time_trigger_util import TriggerSub

# from omni.metropolis.utils.semantics_util import SemanticsUtils


# class SpillEvent:
#     def __init__(
#         self,
#         spill_animator_factory: Callable[[str, float, float], SpillAnimator],
#         name: str,
#         selected_leakable_item_path: str,
#         spillable_area_prim_paths: list[str],
#         target_size: float = 1.0,
#         leak_duration: float = 1.0,
#     ):
#         self.name = name
#         self.selected_leakable_item_path = selected_leakable_item_path
#         self.target_size = target_size
#         self.leak_duration = leak_duration
#         self.projection_cube = None
#         self.spill_animator_factory = spill_animator_factory
#         self.spillable_area_prim_paths = spillable_area_prim_paths
#         self.trigger_sub = None
#         self.on_create_spill()

#     def on_create_spill(self):
#         stage = omni.usd.get_context().get_stage()
#         purposes = [UsdGeom.Tokens.default_]
#         bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)
#         prim = stage.GetPrimAtPath(self.selected_leakable_item_path)
#         bbox = bbox_cache.ComputeWorldBound(prim)

#         #  TODO filter spillable area prim paths to only include the ones that near the leakable item
#         self.projection_cube = self.create_spill(self.spillable_area_prim_paths, position=bbox.ComputeCentroid())

#         if not self.projection_cube:
#             print("Failed to create projection cube")
#             return

#         self.spill_animator = self.spill_animator_factory(
#             self.projection_cube, target_size=self.target_size, leak_duration=self.leak_duration
#         )

#     def set_trigger_sub(self, trigger_sub: TriggerSub):
#         self.trigger_sub = trigger_sub

#     def on_trigger_spill(self):
#         self.spill_animator.activate()
#         stage = omni.usd.get_context().get_stage()
#         leaking_prim = stage.GetPrimAtPath(self.selected_leakable_item_path)
#         if leaking_prim:
#             SemanticsUtils.add_update_semantics_timecode(leaking_prim, "leaking_item")

#         spill_prim = stage.GetPrimAtPath(self.projection_cube)
#         if spill_prim:
#             SemanticsUtils.add_update_semantics_timecode(spill_prim, "liquid_spill")

#     def on_reset_spill(self):
#         if self.spill_animator:
#             self.spill_animator.reset()

#     def destroy(self):
#         if self.trigger_sub:
#             self.trigger_sub = None
#         self.on_stop_spill()
#         if self.projection_cube:
#             rep.delete.prims(self.projection_cube)
#             self.projection_cube = None

#     def create_single_projection(
#         self,
#         target_prim_path,
#         position,
#         diffuse_path,
#         normal_path,
#         roughness,
#         projection_offset=(0, 0, 0),
#         parent_handle=None,
#     ):
#         cube = rep.create.cube(
#             visible=False,
#             semantics=[("class", "cube")],
#             position=position,
#             rotation=(0, 0, 0) if parent_handle else (0, -90, 0),
#             scale=(1, 1, 1),
#             parent=parent_handle,
#         )
#         cube_path = rep.utils.get_node_targets(cube.node, "inputs:primsIn")[0]
#         sem = [("class", "shape")]

#         proj = rep.create.projection_material(cube, sem, input_prims=[target_prim_path])
#         with proj:
#             rep.modify.projection_material(
#                 diffuse=diffuse_path,
#                 normal=normal_path,
#                 roughness=roughness,
#             )
#         return cube_path  # noqa: R504

#     def create_projection(self, targets, position, diffuse_path, normal_path, roughness):
#         if len(targets) == 0:
#             return
#         else:
#             handle1 = self.create_single_projection(targets[0], position, diffuse_path, normal_path, roughness)
#             for target in targets[1:]:
#                 self.create_single_projection(
#                     target, (0, 0, 0), diffuse_path, normal_path, roughness, parent_handle=handle1
#                 )
#             return handle1

#     def create_spill(self, ground_prim_paths, position=(0, 0, 0)):
#         diffuse_path = os.path.join(os.path.dirname(__file__), "assets", "albedo.png")
#         normal_path = os.path.join(os.path.dirname(__file__), "assets", "normal.png")
#         roughness = 0.0
#         return self.create_projection(ground_prim_paths, position, diffuse_path, normal_path, roughness)
