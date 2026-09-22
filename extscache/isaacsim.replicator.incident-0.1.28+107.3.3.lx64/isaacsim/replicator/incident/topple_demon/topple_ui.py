# flake8: noqa

import omni
import omni.ui as ui
import carb
from pxr import UsdGeom, Gf, Usd, Sdf
import random, math


from .event_definitions import TARGET_KEY

from omni.kit.menu.utils import MenuHelperWindow
from omni.kit.viewport.utility import get_active_viewport_window
from omni.ui import scene as sc

from ..sceneview_ui_helper import BBoxDrawerHelper
from ..scene_tagging import SceneTaggingData, AttributeUSDTagger

from .event_definitions import TOPPLE_EVENT

import omni.anim.navigation.core as nav

from .topple_demon import ToppleEventManager


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
    attr.Set([r"{}".format(script_path)])


class ToppleUIManipulator(MenuHelperWindow):
    def __init__(self):
        super().__init__(title="ToppleDemonManipulator", width=250, height=500, dockPreference=ui.DockPreference.RIGHT)
        self._scene_tagging_data: SceneTaggingData = None
        self._bus = None
        self._selected_loose_items = None
        self.topple_prim_location: Gf.Vec3d = None
        self.target_location: Gf.Vec3d = None
        self.loose_item_type: str = None
        self._bbox_drawer: BBoxDrawerHelper = None

        self.setup()

    def destroy(self):
        self._bbox_drawer.destroy()
        self._scene_tagging_data: SceneTaggingData = None
        self._bus = None
        self._selected_loose_items = None
        self.topple_prim_location = None
        self.target_location = None
        self.loose_item_type: str = None
        self._bbox_drawer: BBoxDrawerHelper = None

    def get_tagged_items(self):
        usdTagger = AttributeUSDTagger()
        self._scene_tagging_data = usdTagger.Read()
        if not self._scene_tagging_data:
            return

    def select_topple_items(self):
        ctx = omni.usd.get_context()
        stage = ctx.get_stage()

        selection = ctx.get_selection().get_selected_prim_paths()

        self._selected_loose_items = None
        self.loose_item_type = None

        self.topple_prim_location = None

        if len(selection) == 0:
            carb.log_info("No item selected")
            return

        topple_prim_path = selection[0]
        topple_prim = stage.GetPrimAtPath(topple_prim_path)

        if not topple_prim.HasAttribute(AttributeUSDTagger.loose_item_tag):
            carb.log_info(f"Item {topple_prim_path} not a loose item")
            return
        loose_item_type = topple_prim.GetAttribute(AttributeUSDTagger.loose_item_tag).Get()

        if not loose_item_type in self._scene_tagging_data.loose_item_prim_paths_by_type:
            carb.log_info(f'Loose item type: "{loose_item_type}" not recognized')
            return

        if not topple_prim_path in self._scene_tagging_data.loose_item_prim_paths_by_type[loose_item_type]:
            carb.log_error(f'Scene data not current! {topple_prim_path} not registered as type "{loose_item_type}".')
            return

        self._selected_loose_items = set()
        self.loose_item_type = loose_item_type

        purposes = [UsdGeom.Tokens.default_]
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)
        bound = bbox_cache.ComputeWorldBound(topple_prim)
        # range = bound.ComputeAlignedBox()
        topple_prim_location = Gf.Vec3d(bound.ComputeCentroid())

        self.topple_prim_location = topple_prim_location

        for loose_item_type, prim_paths in self._scene_tagging_data.loose_item_prim_paths_by_type.items():
            for prim_path in prim_paths:
                prim = stage.GetPrimAtPath(Sdf.Path(prim_path))
                bound = bbox_cache.ComputeWorldBound(prim)
                # range = bound.ComputeAlignedBox()
                prim_location = Gf.Vec3d(bound.ComputeCentroid())

                if (prim_location - topple_prim_location).GetLength() < 1.50:
                    print(f"Adding loose_item script to item: {prim_path}")
                    self._selected_loose_items.add(prim_path)

        for prim_path in self._selected_loose_items:
            add_loose_item_behavior_script(prim_path)

    def locate_target(self):
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
        if not self.target_location:
            return
        self._bbox_drawer.clear_canvas()
        self._bbox_drawer.draw_AABB_box(
            self.target_location - Gf.Vec3d(0.1, 0.1, 0.1), self.target_location + Gf.Vec3d(0.1, 0.1, 0.1)
        )

    def locate_target_random(self):
        stage = omni.usd.get_context().get_stage()

        # Get world up axis from the stage metadata
        up_axis = UsdGeom.GetStageUpAxis(stage)

        dir_up = Gf.Vec3d(0, 1, 0)  # Y-up
        dir_1 = Gf.Vec3d(1, 0, 0)
        dir_2 = Gf.Vec3d(0, 0, 1)

        # Determine world up direction
        if up_axis == UsdGeom.Tokens.z:
            dir_up = Gf.Vec3d(0, 0, 1)  # Z-up
            dir_1 = Gf.Vec3d(1, 0, 0)
            dir_2 = Gf.Vec3d(0, 1, 0)

        # Determine world up direction
        if up_axis == UsdGeom.Tokens.x:
            dir_up = Gf.Vec3d(1, 0, 0)  # X-up
            dir_1 = Gf.Vec3d(0, 1, 0)
            dir_2 = Gf.Vec3d(0, 0, 1)

        theta = random.uniform(0, 2 * math.pi)
        dir = math.cos(theta) * dir_1 + math.sin(theta) * dir_2
        topple_prim_location = self.topple_prim_location
        self.target_location = Gf.Vec3d(topple_prim_location + 2 * dir)

    def locate_closest_sphere(self):
        stage = omni.usd.get_context().get_stage()
        prim_location = self.topple_prim_location
        sphere_paths = []

        for prim in stage.Traverse():
            if prim.HasAttribute(AttributeUSDTagger.topple_destination_tag):
                prim_path = str(prim.GetPrimPath())
                loose_item_type = prim.GetAttribute(AttributeUSDTagger.topple_destination_tag).Get()
                if loose_item_type == "Sphere":
                    sphere_paths.append(prim_path)

        print("191")
        for sphere_path in sphere_paths:
            print(sphere_path)
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
            print(f"sphere radius: {sphere_radius}")
            signed_distance = (self.topple_prim_location - sphere_center).GetLength() - sphere_radius
            print(f"signed distance: {signed_distance}")
            if signed_distance >= self.min_distance:
                continue

            self.min_distance = signed_distance

            if signed_distance < 0.00001:
                self.target_location = sphere_center
            else:
                self.target_location = prim_location + signed_distance * prim_to_sphere.GetNormalized()
            print(f"target location: {self.target_location}")

    def locate_closest_cube(self):
        stage = omni.usd.get_context().get_stage()
        prim_location = self.topple_prim_location
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
            local_center = Gf.Vec3d(0, 0, 0)  # Sphere's center in local space

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
        stage = omni.usd.get_context().get_stage()

        if not self.topple_prim_location:
            return

        self.min_distance = 100
        self.locate_closest_sphere()
        self.locate_closest_cube()

    def locate_target_navmesh(self):
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

    def topple_event(self):
        if not self._selected_loose_items:
            return

        if not self.target_location:
            return

        target = self.target_location

        payload = {
            loose_item_path.replace("/", "____"): {TARGET_KEY: [target[0], target[1], target[2]]}
            for loose_item_path in self._selected_loose_items
        }
        # print(payload)
        carb.log_info(f"Topple event sent.")
        self._bus.push(TOPPLE_EVENT, payload=payload)

    def setup(self):
        self._bus = omni.kit.app.get_app().get_message_bus_event_stream()

        with self.frame:
            with ui.VStack():

                def on_select_topple_target():
                    self._bbox_drawer = BBoxDrawerHelper("Navmesh")
                    self.get_tagged_items()
                    self.select_topple_items()
                    self.locate_target()

                ui.Button("Select topple target", clicked_fn=on_select_topple_target)

                def on_topple_command():
                    self.topple_event()

                ui.Button("Send topple event", clicked_fn=on_topple_command)


class ToppleUIViewerWindow(MenuHelperWindow):
    def __init__(self):
        super().__init__(title="ToppleDemonPreviewer", width=250, height=500, dockPreference=ui.DockPreference.RIGHT)
        self.canvas = None
        self.scene_view = None

        self._bbox_drawer_helper: BBoxDrawerHelper = None
        self.setup_2()

    def setup(self):

        with self.frame:
            with ui.VStack():

                def draw_box():
                    self.viewport_window = get_active_viewport_window()

                    with self.viewport_window.get_frame("BBoxDrawerWUT"):
                        # Add the manipulator into the SceneView's scene
                        if not self.scene_view:
                            self.scene_view = sc.SceneView()
                        with self.scene_view.scene:
                            if not self.canvas:
                                self.canvas = sc.Transform()
                            with self.canvas:
                                sc.Line([0, 0, 0], [10, 0, 0], thickness=1.0)
                                sc.Line([10, 0, 0], [10, 10, 0], thickness=1.0)
                                sc.Line([10, 10, 0], [0, 10, 0], thickness=1.0)
                                sc.Line([0, 10, 0], [0, 0, 0], thickness=1.0)

                    self.viewport_window.viewport_api.add_scene_view(self.scene_view)

                ui.Button("Draw Box", clicked_fn=draw_box)

                def update():
                    self.canvas.clear()

                ui.Button("Update", clicked_fn=update)

    def setup_2(self):
        self._bbox_drawer_helper = BBoxDrawerHelper("Demo")

        with self.frame:
            with ui.VStack():

                def draw_demo_box():
                    # self._bbox_drawer_helper.demo_draw_box()
                    purposes = [UsdGeom.Tokens.default_]
                    # get scene bounding box
                    ctx = omni.usd.get_context()
                    selection = ctx.get_selection().get_selected_prim_paths()
                    if len(selection) == 0:
                        return
                    prim_path = selection[0]
                    prim = ctx.get_stage().GetPrimAtPath(prim_path)

                    bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)
                    bound = bbox_cache.ComputeWorldBound(prim)
                    range = bound.ComputeAlignedBox()
                    bbox_center = bound.ComputeCentroid()
                    bbox_max = range.GetMax()
                    bbox_min = range.GetMin()

                    self._bbox_drawer_helper.draw_AABB_box(bbox_min, bbox_max)

                ui.Button("Draw Demo Box", clicked_fn=draw_demo_box)

                def clear():
                    self._bbox_drawer_helper.clear_canvas()

                ui.Button("Clear", clicked_fn=clear)


class ToppleUIManipulator3(MenuHelperWindow):
    """
    This class is a debug class responsible for the UI for the topple demon manipulator.
    It is responsible for generating random topple events and sending topple events.
    It is likely broken and should be removed.
    """

    def __init__(self):
        super().__init__(title="ToppleDemonManipulator", width=250, height=500, dockPreference=ui.DockPreference.RIGHT)
        self.current_event_name = None

        self.setup()

    def setup(self):
        with self.frame:
            with ui.VStack():
                self.generate_random_topple_event_button = ui.Button("Generate Random Topple Target")
                self.send_topple_event_button = ui.Button("Send topple event")

                ui.Button("Refresh Scene", clicked_fn=lambda: self.refresh())

        self.refresh()

    def refresh(self):
        self.topple_event_manager = ToppleEventManager(1)

        def random_topple_event_callback():
            name = str(len(self.topple_event_manager.topple_events))
            self.current_event_name = name
            self.topple_event_manager.generate_random_topple_event(name)

        self.generate_random_topple_event_button.set_clicked_fn(random_topple_event_callback)

        self.send_topple_event_button.set_clicked_fn(
            lambda: self.topple_event_manager.trigger_topple_event(self.current_event_name)
        )
