import omni
import omni.ui as ui

from omni.kit.viewport.utility import get_active_viewport, frame_viewport_selection
import carb

from ..sceneview_ui_helper import BBoxDrawerHelper
from omni.ui import color as cl
from pxr import UsdGeom, Usd, UsdPhysics

from .scene_tagging import SceneTaggingData, AttributeUSDTagger

from ..ui_definitions import get_collapsable_frame_style, LABEL_WIDTH

# TODO: [METROPERF-945] Consider refactoring to put common behavior between the scene taggers into it's own class
class ToppleSceneTaggingUIMenu:
    """
    This class is responsible for the UI for the scene tagging data.
    It is responsible for adding and removing loose item tags and topple destination tags.
    """

    def __init__(self):
        self.frame = None

        self._scene_tagging_data: SceneTaggingData = None
        self._scene_tagging_data_viewer: SceneTaggingDataViewer = None
        self._USDTagger: AttributeUSDTagger = None

        self.view_scene_tags_checkbox = None

        self._ctx = None
        self._stage = None

        self.read_scene_tagging_data_from_stage()


    def read_scene_tagging_data_from_stage(self):
        """
        This function creates the scene tagging data, viewer, and USDTagger.
        It then reads the scene tagging data from the USDTagger.
        Please call this on stage open.
        """
        self._ctx = omni.usd.get_context()
        self._stage = self._ctx.get_stage()

        if self._stage is None:
            return

        self._scene_tagging_data = SceneTaggingData()
        self._scene_tagging_data_viewer = SceneTaggingDataViewer()
        self._USDTagger = AttributeUSDTagger()
        self._scene_tagging_data = self._USDTagger.Read()
        self.draw_scene_data()

    def draw_scene_data(self):
        """
        This function draws the 3D UI from the current scene tagging data.
        """
        self._scene_tagging_data_viewer.draw_scene_data(self._scene_tagging_data)

    def destroy(self):
        """
        This function destroys the scene tagging data, viewer, and USDTagger.
        Please call this on stage close.
        """
        if self._scene_tagging_data_viewer:
            self._scene_tagging_data_viewer.destroy()

        self._scene_tagging_data: SceneTaggingData = None
        self._scene_tagging_data_viewer: SceneTaggingDataViewer = None
        self._USDTagger: AttributeUSDTagger = None

        self._ctx = None
        self._stage = None

        if self.frame:
            self.frame.clear()
            self.frame = None

    def get_ctx(self):
        return self._ctx

    def get_stage(self):
        return self._stage

    def find_rigid_body_nested(self, prim_path, rigid_bodies):
        """
        This function is responsible for finding all rigid bodies nested in a prim.
        It is used to find the rigid bodies that might be tagged as loose items.
        """
        stage = self.get_stage()

        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            carb.log_error(f"{type(self).__name__}: Invalid prim access for path {prim_path}")
            return

        if UsdPhysics.RigidBodyAPI.Get(stage, prim_path):
            # print(prim_path, " is a rigid body")
            rigid_bodies.append(prim_path)
            return

        for child_prim in prim.GetChildren():
            child_prim_path = str(child_prim.GetPath())
            self.find_rigid_body_nested(child_prim_path, rigid_bodies)


    # TODO: See earlier todo about code duplication. Similar functions exist in other demons.
    def find_loose_item_nested(self, prim_path, loose_items):
        """
        This function is responsible for finding all loose items nested in a prim.
        """
        stage = self.get_stage()

        prim = stage.GetPrimAtPath(prim_path)

        if self._USDTagger.prim_has_loose_item_tag(prim_path):
            loose_items.append(prim_path)

        for child_prim in prim.GetChildren():
            child_prim_path = str(child_prim.GetPath())
            self.find_loose_item_nested(child_prim_path, loose_items)

    def on_update_view(self):
        self._scene_tagging_data_viewer.clear_scene_ui()
        if self.view_scene_tags_checkbox.model.get_value_as_bool():
            self.draw_scene_data()
        else:
            self._scene_tagging_data_viewer.clear_scene_ui()

    def add_loose_items(self, loose_item_type):
        """
        This function is responsible for adding loose item tags to the selected prims.
        It finds all rigid bodies nested in the selected prims and adds them as loose items.
        If no rigid bodies are found, it adds the prim itself as a loose item.
        """
        # print(loose_item_type)
        self._scene_tagging_data = self._USDTagger.Read()

        ctx = self.get_ctx()
        selection = ctx.get_selection().get_selected_prim_paths()
        if len(selection) == 0:
            return

        rigid_body_prims = []
        for prim_path in selection:
            rigid_bodies = []
            self.find_rigid_body_nested(prim_path, rigid_bodies)
            if len(rigid_bodies) == 0:
                # no rigid bodies, just use the prim itself
                # print("No rigid bodies found on nested prims!")
                rigid_bodies.append(prim_path)
            rigid_body_prims.extend(rigid_bodies)

        self._scene_tagging_data.add_loose_items(rigid_body_prims, loose_item_type)
        self._USDTagger.Write(self._scene_tagging_data)
        self.on_update_view()

    def remove_loose_items(self):
        """
        This function is responsible for removing loose item tags from the selected prims.
        It finds all loose items nested in the selected prims and removes them.
        """
        self._scene_tagging_data = self._USDTagger.Read()

        ctx = self.get_ctx()
        selection = ctx.get_selection().get_selected_prim_paths()
        if len(selection) == 0:
            return

        loose_items = []
        for prim_path in selection:
            self.find_loose_item_nested(prim_path, loose_items)
        # print("loose items found: ", loose_items)
        for prim_path in loose_items:
            loose_item_type = self._USDTagger.get_loose_item_tag(prim_path)
            self._scene_tagging_data.remove_loose_item(prim_path, loose_item_type)

        self._USDTagger.Write(self._scene_tagging_data)
        self.on_update_view()

    def add_topple_destination(self, topple_destination_type):
        """
        This function is responsible for adding topple destination tags to the selected prims.
        """
        ctx = self.get_ctx()
        selection = ctx.get_selection().get_selected_prim_paths()
        if len(selection) == 0:
            return

        for prim_path in selection:
            self._scene_tagging_data.add_topple_destination(prim_path, topple_destination_type)

        self._USDTagger.Write(self._scene_tagging_data)
        self.on_update_view()

    def remove_topple_destinations(self):
        """
        This function is responsible for removing topple destination tags from the selected prims.
        """
        self._scene_tagging_data = self._USDTagger.Read()

        ctx = self.get_ctx()
        selection = ctx.get_selection().get_selected_prim_paths()
        if len(selection) == 0:
            return

        for prim_path in selection:
            prim = ctx.get_stage().GetPrimAtPath(prim_path)
            if not prim.HasAttribute(AttributeUSDTagger.topple_destination_tag):
                continue
            loose_item_type = prim.GetAttribute(AttributeUSDTagger.topple_destination_tag).Get()
            self._scene_tagging_data.remove_topple_destination(prim_path, loose_item_type)

        self._USDTagger.Write(self._scene_tagging_data)
        self.on_update_view()

    """
        This function adds a cube prim to the stage with a topple destination cube tag.
    """
    def add_topple_destination_prim(self):
        ctx = self.get_ctx()
        stage = self.get_stage()
        base_prim_path = "/World/ToppleDestinations/ToppleDestination"
        prim_path = omni.usd.get_stage_next_free_path(stage, base_prim_path, True)
        result, prim = omni.kit.commands.execute("CreatePrimCommand", prim_type="Cube", prim_path=prim_path, select_new_prim=True)
        if not result:
            carb.log_error("Failed to create topple destination prim")
            return
        viewport = get_active_viewport()
        if viewport:
            frame_viewport_selection(viewport)
        self._scene_tagging_data.add_topple_destination(prim_path, "Cube")



        self._USDTagger.Write(self._scene_tagging_data)
        self.on_update_view()



    def build_ui_frame(self):  # noqa: C901
        if self.frame == None:
            self.frame = ui.CollapsableFrame(
                title="Topple Tagging",
                height=0,
                collapsed=False,
                style=get_collapsable_frame_style(),
                name="subFrame",
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            )
        with self.frame:
            with ui.VStack(spacing=2): #**get_vstack_style()):
                self.view_scene_tags_checkbox = None
                with ui.HStack():
                    ui.Label("View tagged items?", width=LABEL_WIDTH,alignment=ui.Alignment.LEFT_CENTER)
                    self.view_scene_tags_checkbox = ui.CheckBox(alignment=ui.Alignment.LEFT_CENTER)
                    self.view_scene_tags_checkbox.model.set_value(True)
                    ui.Spacer(width=5)


                self.view_scene_tags_checkbox.model.add_value_changed_fn(lambda model: self.on_update_view())

                ui.Label("Edit tag from selection")

                for loose_item_type in AttributeUSDTagger.loose_item_types:
                    with ui.HStack():
                        ui.Label("Tag loose items: ", width=LABEL_WIDTH,alignment=ui.Alignment.LEFT_CENTER)
                        ui.Button(
                            loose_item_type,
                            clicked_fn=lambda it=loose_item_type: self.add_loose_items(it),
                            width=0,
                        )
                        ui.Spacer(width=5)

                ui.Button(
                    "UntagLooseItems",
                    clicked_fn=self.remove_loose_items,
                    width=LABEL_WIDTH,
                    alignment=ui.Alignment.CENTER,
                )
                ui.Spacer(height=5)

                ui.Button(
                    "AddWaypointPrim",
                    clicked_fn=self.add_topple_destination_prim,
                    width=LABEL_WIDTH,
                    alignment=ui.Alignment.CENTER,
                )
                ui.Spacer(height=30)
                # for loose_item_type in AttributeUSDTagger.topple_destination_types:
                #     ui.Button(
                #         "Tag topple destinations: " + loose_item_type,
                #         clicked_fn=lambda it=loose_item_type: self.add_topple_destination(it),
                #     )

                # ui.Button("Untag topple destinations", clicked_fn=self.remove_topple_destinations)


class SceneTaggingDataViewer:
    """
    This class is responsible for drawing the scene tagging data in the scene view.
    """

    def __init__(self):
        self._bbox_drawer: BBoxDrawerHelper = BBoxDrawerHelper("ToppleSceneTagDrawer")

        self.loose_item_colors_by_type = {
            "NavMesh": cl(1.0, 1.0, 1.0, 1.0),
            "RandomDir": cl(0.5, 1.0, 0.4, 1.0),
            "ClosestWaypoint": cl(0.7, 0.7, 1.0, 1.0),
        }

        self.topple_destination_color = cl(1.0, 0.3, 0.3, 1.0)
        self._ctx = omni.usd.get_context()

    def __del__(self):
        self.destroy()


    def destroy(self):
        if self._bbox_drawer:
            self._bbox_drawer.destroy()
        self._bbox_drawer = None
        self._ctx = None

    def clear_scene_ui(self):
        self._bbox_drawer.clear_canvas()

    def _get_prim_range(self, prim_path: str, bbox_cache: UsdGeom.BBoxCache, ctx):
        prim = ctx.get_stage().GetPrimAtPath(prim_path)
        bound = bbox_cache.ComputeWorldBound(prim)
        return bound.ComputeAlignedBox()

    def draw_scene_data(self, scene_tagging_data: SceneTaggingData):
        ctx = self._ctx

        purposes = [UsdGeom.Tokens.default_]
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)

        # print("Drawing Scene!")
        for loose_item_type, prim_paths in scene_tagging_data.loose_item_prim_paths_by_type.items():
            for prim_path in prim_paths:
                # print("Drawing: " + str(prim_path))
                box_range = self._get_prim_range(prim_path, bbox_cache, ctx)
                bbox_max = box_range.GetMax()
                bbox_min = box_range.GetMin()

                color = self.loose_item_colors_by_type[loose_item_type]

                self._bbox_drawer.draw_AABB_box(bbox_min, bbox_max, color=color)

        for _, prim_paths in scene_tagging_data.topple_destinations_by_type.items():
            for prim_path in prim_paths:
                # print("Drawing: " + str(prim_path))
                box_range = self._get_prim_range(prim_path, bbox_cache, ctx)
                bbox_max = box_range.GetMax()
                bbox_min = box_range.GetMin()

                color = self.topple_destination_color

                self._bbox_drawer.draw_AABB_box(bbox_min, bbox_max, color=color)
