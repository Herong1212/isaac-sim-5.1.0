import omni, carb
from pxr import UsdGeom, Gf, Usd, Sdf
from typing import Callable

import math

from .event_definitions import TARGET_KEY, TOPPLE_EVENT, TOPPLE_RESPONSE_REQUEST_EVENT  # noqa: F401

from ..sceneview_ui_helper import BBoxDrawerHelper
from .scene_tagging import SceneTaggingData, AttributeUSDTagger

import omni.anim.navigation.core as nav

from .scripts.loose_item_mono_b_script import LooseItemMonoBScript

from ..event_defines import IncidentData, IncidentCarbEventHelper
from omni.metropolis.utils.semantics_util import SemanticsUtils


def clamp_vec3d(v, vmin, vmax):
    """How does this not exist in Gf???"""
    return Gf.Vec3d(
        max(vmin[0], min(v[0], vmax[0])), max(vmin[1], min(v[1], vmax[1])), max(vmin[2], min(v[2], vmax[2]))
    )


def add_loose_item_behavior_script(prim_path):
    script_path = (
        omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module("isaacsim.replicator.incident")
        + "/isaacsim/replicator/incident/topple_demon/scripts/loose_item.py"
    )

    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)

    omni.kit.commands.execute("ApplyScriptingAPICommand", paths=[Sdf.Path(prim_path)])
    attr = prim.GetAttribute("omni:scripting:scripts")
    script_list_usd = attr.Get()
    script_list = [r"{}".format(script_path)]

    if script_list_usd:
        for script_path in script_list_usd:
            script_list.append(script_path)

    attr.Set(script_list)


def add_dynamic_obstacle_behavior_script(prim_path):
    script_path = (
        omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module("omni.anim.people")
        + "/omni/anim/people/scripts/dynamic_obstacle.py"
    )

    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)

    omni.kit.commands.execute("ApplyScriptingAPICommand", paths=[Sdf.Path(prim_path)])
    attr = prim.GetAttribute("omni:scripting:scripts")
    script_list_usd = attr.Get()
    script_list = [r"{}".format(script_path)]

    if script_list_usd:
        for script_path in script_list_usd:
            script_list.append(script_path)

    attr.Set(script_list)


class ToppleEventSetup:
    """
    This class is responsible for setting up topple events in the scene.
    It is responsible for selecting the topple items, locating the target,
    and exposes a function for triggering the topple event.
    The trigger is sent over the message bus where a behavior script is expected to be listening for it.
    """

    def __init__(
        self,
        loose_item_mono_b_script_factory: Callable[[str], LooseItemMonoBScript],
        scene_tagging_data,
        event_name,
        topple_prim_path,
        random,
        topple_nearby_radius=0.0,
    ):

        self.event_name = event_name
        self.topple_prim_path = topple_prim_path
        self._scene_tagging_data: SceneTaggingData = scene_tagging_data
        self.selected_loose_items = None
        self.topple_prim_location: Gf.Vec3d = None
        self.target_location: Gf.Vec3d = None
        self.loose_item_type: str = None
        self._bbox_drawer: BBoxDrawerHelper = None  # BBoxDrawerHelper("ToppleEvent: " + event_name)

        self.random = random
        self.topple_nearby_radius = topple_nearby_radius
        self.loose_item_mono_b_scripts = []
        self.loose_item_mono_b_script_factory = loose_item_mono_b_script_factory
        self.select_topple_items()
        self.locate_target()

    def destroy(self):
        stage = omni.usd.get_context().get_stage()
        prims = [stage.GetPrimAtPath(prim_path) for prim_path in self.selected_loose_items]
        SemanticsUtils.remove_prim_metrosim_semantics(
            [prim for prim in prims if prim and prim.IsValid()]
        )
        self._scene_tagging_data: SceneTaggingData = None
        self.selected_loose_items = None
        self.topple_prim_location = None
        self.target_location = None
        self.loose_item_type: str = None
        if self._bbox_drawer:
            self._bbox_drawer.destroy()
        self._bbox_drawer: BBoxDrawerHelper = None
        for script in self.loose_item_mono_b_scripts:
            script.destroy()
        self.loose_item_mono_b_scripts = []

    def add_loose_item_mono_b_script(self, prim_path):
        carb.log_info(f"Adding loose item mono b script to {prim_path}")
        self.loose_item_mono_b_scripts.append(self.loose_item_mono_b_script_factory(prim_path))

    def select_topple_items(self):
        """
        This function is responsible for selecting the topple items.
        It locates the topple primitive, and then selects all items within a radius
        in the scene that are tagged as loose items.
        """
        ctx = omni.usd.get_context()
        stage = ctx.get_stage()

        # selection = ctx.get_selection().get_selected_prim_paths()

        self.selected_loose_items = None
        self.loose_item_type = None

        self.topple_prim_location = None

        topple_prim_path = self.topple_prim_path
        topple_prim = stage.GetPrimAtPath(topple_prim_path)

        if not topple_prim.HasAttribute(AttributeUSDTagger.loose_item_tag):
            carb.log_info(f"Item {topple_prim_path} not a loose item")
            return
        loose_item_type = topple_prim.GetAttribute(AttributeUSDTagger.loose_item_tag).Get()

        if loose_item_type not in self._scene_tagging_data.loose_item_prim_paths_by_type:
            carb.log_info(f'Loose item type: "{loose_item_type}" not recognized')
            return

        if topple_prim_path not in self._scene_tagging_data.loose_item_prim_paths_by_type[loose_item_type]:
            carb.log_error(f'Scene data not current! {topple_prim_path} not registered as type "{loose_item_type}".')
            return

        self.selected_loose_items = set()
        self.loose_item_type = loose_item_type

        purposes = [UsdGeom.Tokens.default_]
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)
        bound = bbox_cache.ComputeWorldBound(topple_prim)
        # range = bound.ComputeAlignedBox()
        topple_prim_location = Gf.Vec3d(bound.ComputeCentroid())

        self.topple_prim_location = topple_prim_location

        for prim_paths in self._scene_tagging_data.loose_item_prim_paths_by_type.values():
            for prim_path in prim_paths:
                prim = stage.GetPrimAtPath(Sdf.Path(prim_path))
                bound = bbox_cache.ComputeWorldBound(prim)
                # range = bound.ComputeAlignedBox()
                prim_location = Gf.Vec3d(bound.ComputeCentroid())

                if (prim_location - topple_prim_location).GetLength() < self.topple_nearby_radius:
                    carb.log_info(f"Adding loose_item script to item: {prim_path}")
                    self.selected_loose_items.add(prim_path)

        for prim_path in self.selected_loose_items:
            self.add_loose_item_mono_b_script(prim_path)
            # add_dynamic_obstacle_behavior_script(prim_path)

    def locate_target(self):
        """
        This function is responsible for locating the target to use a direction for the force.
        It locates the target based on the loose item type.
        """
        self.target_location = None
        if not self.loose_item_type:
            return

        if self.loose_item_type == "NavMesh":
            self.locate_target_navmesh()
        elif self.loose_item_type == "RandomDir":
            self.locate_target_random()
        elif self.loose_item_type == "ClosestWaypoint":
            self.locate_target_nearby_waypoint()
        else:
            carb.log_error(f"Unrecognized loose item type: {self.loose_item_type}")

        self.draw_target()

    def draw_target(self):
        """
        This function is responsible for drawing the target in the scene view.
        It is for debug purposes and does nothing if self._bbox_drawer is not set.
        """
        if not self._bbox_drawer:
            return
        if not self.target_location:
            return
        self._bbox_drawer.clear_canvas()
        self._bbox_drawer.draw_AABB_box(
            self.target_location - Gf.Vec3d(0.1, 0.1, 0.1), self.target_location + Gf.Vec3d(0.1, 0.1, 0.1)
        )
        purposes = [UsdGeom.Tokens.default_]
        ctx = omni.usd.get_context()
        stage = ctx.get_stage()
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)
        for prim_path in self.selected_loose_items:
            bound = bbox_cache.ComputeWorldBound(stage.GetPrimAtPath(prim_path))
            box_range = bound.ComputeAlignedBox()
            bbox_max = box_range.GetMax()
            bbox_min = box_range.GetMin()
            self._bbox_drawer.draw_AABB_box(bbox_min, bbox_max)

    def locate_target_random(self):
        """
        This function is responsible for locating the target to use a direction for the force
        as a random direction.
        """
        stage = omni.usd.get_context().get_stage()

        # Get world up axis from the stage metadata
        up_axis = UsdGeom.GetStageUpAxis(stage)

        # dir_up = Gf.Vec3d(0, 1, 0)  # Y-up # noqa: C901
        dir_1 = Gf.Vec3d(1, 0, 0)
        dir_2 = Gf.Vec3d(0, 0, 1)

        # Determine world up direction
        if up_axis == UsdGeom.Tokens.z:
            # dir_up = Gf.Vec3d(0, 0, 1)  # Z-up # noqa: C901
            dir_1 = Gf.Vec3d(1, 0, 0)
            dir_2 = Gf.Vec3d(0, 1, 0)

        # Determine world up direction
        if up_axis == UsdGeom.Tokens.x:
            # dir_up = Gf.Vec3d(1, 0, 0)  # X-up # noqa: C901
            dir_1 = Gf.Vec3d(0, 1, 0)
            dir_2 = Gf.Vec3d(0, 0, 1)

        theta = self.random.uniform(0, 2 * math.pi)
        direction = math.cos(theta) * dir_1 + math.sin(theta) * dir_2
        topple_prim_location = self.topple_prim_location
        self.target_location = Gf.Vec3d(topple_prim_location + 2 * direction)

    def locate_closest_sphere(self):
        """
        This function is responsible for locating the closest tagged sphere to the topple primitive.
        It locates the closest sphere to the topple primitive and sets the target location to the center of the sphere.
        """
        stage = omni.usd.get_context().get_stage()
        prim_location = self.topple_prim_location
        sphere_paths = []

        for prim in stage.Traverse():
            if prim.HasAttribute(AttributeUSDTagger.topple_destination_tag):
                prim_path = str(prim.GetPrimPath())
                loose_item_type = prim.GetAttribute(AttributeUSDTagger.topple_destination_tag).Get()
                if loose_item_type == "Sphere":
                    sphere_paths.append(prim_path)

        for sphere_path in sphere_paths:
            prim = stage.GetPrimAtPath(sphere_path)

            if not prim.IsA(UsdGeom.Sphere):
                carb.log_warn("topple destination: Sphere tag detected on a non-UsdGeom.Sphere object!")
                continue

            sphere = UsdGeom.Sphere(prim)
            local_center = Gf.Vec3d(0, 0, 0)  # Sphere's center in local space

            xformable = UsdGeom.Xformable(sphere)
            transform = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
            fancy_transform = Gf.Transform(transform)
            scale = fancy_transform.GetScale()[0]
            sphere_center = transform.Transform(local_center)
            prim_to_sphere = sphere_center - self.topple_prim_location
            sphere_radius = sphere.GetRadiusAttr().Get()
            sphere_radius *= scale
            signed_distance = (self.topple_prim_location - sphere_center).GetLength() - sphere_radius
            if signed_distance >= self.min_distance:
                continue

            self.min_distance = signed_distance

            if signed_distance < 0.00001:
                self.target_location = sphere_center
            else:
                self.target_location = prim_location + signed_distance * prim_to_sphere.GetNormalized()

    def locate_closest_cube(self):
        """
        This function is responsible for locating the closest tagged cube to the topple primitive.
        It locates the closest cube to the topple primitive and sets the target location to the closest point on the
        cube.
        """
        stage = omni.usd.get_context().get_stage()
        cube_paths = []

        for prim in stage.Traverse():
            if prim.HasAttribute(AttributeUSDTagger.topple_destination_tag):
                prim_path = str(prim.GetPrimPath())
                loose_item_type = prim.GetAttribute(AttributeUSDTagger.topple_destination_tag).Get()
                if loose_item_type == "Cube":
                    cube_paths.append(prim_path)

        for cube_path in cube_paths:
            prim = stage.GetPrimAtPath(cube_path)

            if not prim.IsA(UsdGeom.Cube):
                carb.log_warn("topple destination: Cube tag detected on a non-UsdGeom.Cube object!")
                continue

            cube = UsdGeom.Cube(prim)

            xformable = UsdGeom.Xformable(cube)
            transform = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
            edge_length = cube.GetSizeAttr().Get()
            topple_prim_local_coords = transform.GetInverse().Transform(self.topple_prim_location)
            if (
                abs(topple_prim_local_coords[0]) < edge_length / 2
                and abs(topple_prim_local_coords[1]) < edge_length / 2
                and abs(topple_prim_local_coords[2]) < edge_length / 2
            ):
                carb.log_info("topple box was detected inside a topple destination cube. Skipping this cube")
                continue

            closest_point_local_coords = clamp_vec3d(
                topple_prim_local_coords,
                Gf.Vec3d(-edge_length / 2, -edge_length / 2, -edge_length / 2),
                Gf.Vec3d(edge_length / 2, edge_length / 2, edge_length / 2),
            )
            closest_point = transform.Transform(closest_point_local_coords)

            distance = (self.topple_prim_location - closest_point).GetLength()
            if distance >= self.min_distance:
                continue

            self.min_distance = distance
            self.target_location = closest_point

    def locate_target_nearby_waypoint(self):
        """
        This function is responsible for locating the closest tagged waypoint to the topple primitive.
        It locates the closest waypoint to the topple primitive and sets the target location to the center of the
        waypoint.
        """

        if not self.topple_prim_location:
            return

        self.min_distance = 100
        self.locate_closest_sphere()
        self.locate_closest_cube()

    def locate_target_navmesh(self):
        """
        This function is responsible for locating the closest navmesh point to the topple primitive.
        It locates the closest navmesh point to the topple primitive and sets the target location to the navmesh point.
        """
        topple_prim_location = self.topple_prim_location
        self.target_location = None

        if not topple_prim_location:
            return

        carb_topple_prim_location = carb.Float3(
            topple_prim_location[0], topple_prim_location[1], topple_prim_location[2]
        )
        navmesh = nav.acquire_interface().get_navmesh()
        if not navmesh:
            carb.log_error("No navmesh is available")
            return

        carb_closest_navmesh_point = navmesh.query_closest_point(carb_topple_prim_location, agent_radius=0.5)[0]

        if not carb_closest_navmesh_point:
            carb.log_error("Couldn't get a closest navmesh point!")
            return

        closest_navmesh_point = Gf.Vec3d(
            carb_closest_navmesh_point[0], carb_closest_navmesh_point[1], carb_closest_navmesh_point[2]
        )

        carb.log_info(f"Closest navmesh point: {closest_navmesh_point}")
        self.target_location = closest_navmesh_point

    def trigger_topple_event(self):
        """
        This function is responsible for triggering the topple event.
        It sends the topple event over the message bus where a behavior script is expected to be listening for it.
        """
        if not self.selected_loose_items:
            return

        if not self.target_location:
            return

        target = self.target_location

        for script in self.loose_item_mono_b_scripts:
            script.on_topple_event(Gf.Vec3f(target[0], target[1], target[2]))

        stage = omni.usd.get_context().get_stage()
        SemanticsUtils.add_update_prim_metrosim_semantics(
            [stage.GetPrimAtPath(prim_path) for prim_path in self.selected_loose_items],
            "class",
            "incident_toppled_item",
        )

        # Carb event
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(
            event_name=IncidentCarbEventHelper.carb_event_name(self.event_name),
            payload={
                "Payload": {
                    "event_data": IncidentData(
                        event_name=self.event_name, event_type="topple event", event_position=self.target_location
                    )
                }
            },
        )
        carb.log_info(f"Trigger topple event '{self.event_name}' at {self.target_location}.")
