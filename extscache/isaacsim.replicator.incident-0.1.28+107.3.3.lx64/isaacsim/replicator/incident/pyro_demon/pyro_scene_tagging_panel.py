import omni
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperWindow
import carb

from ..sceneview_ui_helper import BBoxDrawerHelper
from omni.ui import color as cl
from pxr import UsdGeom, Usd

from ..ui_definitions import get_collapsable_frame_style, LABEL_WIDTH

from .scene_tagging import SceneTaggingData, AttributeUSDTagger


class PyroSceneTaggingUIMenu:
    """
    This class is responsible for the UI for the scene tagging data.
    It is responsible for adding and removing flammable item tags.
    """

    def __init__(self):

        self._scene_tagging_data: SceneTaggingData = None
        self._scene_tagging_data_viewer: SceneTaggingDataViewer = None
        self._USDTagger: AttributeUSDTagger = None

        self.frame = None
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
        self._scene_tagging_data_viewer.draw_scene_data(self._scene_tagging_data)

    def destroy(self):
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

    def find_flammable_item_nested(self, prim_path, flammable_items):
        """
        This function is responsible for finding all flammable items nested in a prim.
        """
        stage = self.get_stage()

        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            carb.log_error("Invalid prim access")
            return

        if self._USDTagger.prim_has_flammable_item_tag(prim_path):
            flammable_items.append(prim_path)

        for child_prim in prim.GetChildren():
            child_prim_path = str(child_prim.GetPath())
            self.find_flammable_item_nested(child_prim_path, flammable_items)

    def on_update_view(self):
        self._scene_tagging_data_viewer.clear_scene_ui()
        if self.view_scene_tags_checkbox.model.get_value_as_bool():
            self.draw_scene_data()
        else:
            self._scene_tagging_data_viewer.clear_scene_ui()

    def add_flammable_items(self, flammable_item_type):
        """
        This function is responsible for adding flammable item tags to the selected prims.
        """
        # print(loose_item_type)
        self._scene_tagging_data = self._USDTagger.Read()

        ctx = self.get_ctx()
        selection = ctx.get_selection().get_selected_prim_paths()
        if len(selection) == 0:
            return

        for prim_path in selection:
            self._scene_tagging_data.add_flammable_item(prim_path, flammable_item_type)

        self._USDTagger.Write(self._scene_tagging_data)
        self.on_update_view()

    def remove_flammable_items(self):
        """
        This function is responsible for removing flammable item tags from the selected prims.
        It finds all flammable items nested in the selected prims and removes them.
        """
        self._scene_tagging_data = self._USDTagger.Read()

        ctx = self.get_ctx()
        selection = ctx.get_selection().get_selected_prim_paths()
        if len(selection) == 0:
            return

        flammable_items = []
        for prim_path in selection:
            self.find_flammable_item_nested(prim_path, flammable_items)
        # print("loose items found: ", loose_items)
        for prim_path in flammable_items:
            flammable_item_type = self._USDTagger.get_flammable_item_tag(prim_path)
            self._scene_tagging_data.remove_flammable_item(prim_path, flammable_item_type)

        self._USDTagger.Write(self._scene_tagging_data)
        self.on_update_view()

    def build_ui_frame(self):
        if self.frame == None:
            self.frame = ui.CollapsableFrame(
                title="Fire Tagging",
                height=0,
                collapsed=False,
                style=get_collapsable_frame_style(),
            )
        with self.frame:
            with ui.VStack(spacing=2):
                self.view_scene_tags_checkbox = None
                with ui.HStack():
                    ui.Label("View Tagged Items?", width=LABEL_WIDTH,alignment=ui.Alignment.LEFT_CENTER)
                    self.view_scene_tags_checkbox = ui.CheckBox(alignment=ui.Alignment.LEFT_CENTER)
                    self.view_scene_tags_checkbox.model.set_value(True)
                    ui.Spacer(width=5)

                self.view_scene_tags_checkbox.model.add_value_changed_fn(lambda model: self.on_update_view())

                ui.Label("Edit tag from selection")

                for flammable_item_type in AttributeUSDTagger.flammable_item_types:
                    with ui.HStack():
                        ui.Label("Tag flammable items: ", width=LABEL_WIDTH,alignment=ui.Alignment.LEFT_CENTER)
                        ui.Button(
                            flammable_item_type,
                            clicked_fn=lambda it=flammable_item_type: self.add_flammable_items(it),
                            width=0,
                        )

                ui.Button("UntagFlammableItems", clicked_fn=self.remove_flammable_items, width=LABEL_WIDTH)
                ui.Spacer(height=30)


class SceneTaggingDataViewer:
    """
    This class is responsible for drawing the scene tagging data in the scene view.
    """

    def __init__(self):
        self._bbox_drawer: BBoxDrawerHelper = BBoxDrawerHelper("PyroSceneTagDrawer")

        self.flammable_item_colors_by_type = {
            "Box": cl(1.0, 1.0, 1.0, 1.0),
        }

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
        for flammable_item_type, prim_paths in scene_tagging_data.flammable_item_prim_paths_by_type.items():
            for prim_path in prim_paths:
                # print("Drawing: " + str(prim_path))
                box_range = self._get_prim_range(prim_path, bbox_cache, ctx)
                bbox_max = box_range.GetMax()
                bbox_min = box_range.GetMin()

                color = self.flammable_item_colors_by_type[flammable_item_type]

                self._bbox_drawer.draw_AABB_box(bbox_min, bbox_max, color=color)
