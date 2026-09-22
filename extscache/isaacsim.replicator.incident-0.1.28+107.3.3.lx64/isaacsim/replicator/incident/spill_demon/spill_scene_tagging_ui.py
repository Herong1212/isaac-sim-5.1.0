import omni
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperWindow
import carb

from ..sceneview_ui_helper import BBoxDrawerHelper
from omni.ui import color as cl
from pxr import UsdGeom, Usd

from .scene_tagging import SceneTaggingData, AttributeUSDTagger


class SpillSceneTaggingUIMenu(MenuHelperWindow):
    """
    This class is responsible for the UI for the scene tagging data.
    It is responsible for adding and removing spillable item and area tags.
    """

    def __init__(self):
        super().__init__(title="SceneTagPreviewer", width=250, height=500, dockPreference=ui.DockPreference.RIGHT)
        self.canvas = None
        self.scene_view = None

        self._scene_tagging_data: SceneTaggingData = None
        self._scene_tagging_data_viewer: SceneTaggingDataViewer = None
        self._USDTagger: AttributeUSDTagger = None

        self.load_scene()

        self.setup()

    def load_scene(self):
        """
        This function is responsible for loading the scene tagging data.
        It creates the scene tagging data, viewer, and USDTagger.
        It then reads the scene tagging data from the USDTagger.
        """
        self._scene_tagging_data = SceneTaggingData()
        self._scene_tagging_data_viewer = SceneTaggingDataViewer()
        self._USDTagger = AttributeUSDTagger()
        self._scene_tagging_data = self._USDTagger.Read()
        self.draw_scene_data()

    def draw_scene_data(self):
        self._scene_tagging_data_viewer.draw_scene_data(self._scene_tagging_data)

    def destroy(self):
        self._scene_tagging_data_viewer.destroy()

        self._scene_tagging_data: SceneTaggingData = None
        self._scene_tagging_data_viewer: SceneTaggingDataViewer = None
        self._USDTagger: AttributeUSDTagger = None

    def find_leakable_item_nested(self, prim_path, leakable_items):
        """
        This function is responsible for finding all leakable items nested in a prim.
        """
        ctx = omni.usd.get_context()
        stage = ctx.get_stage()

        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            carb.log_error("Invalid prim access")
            return

        if self._USDTagger.prim_has_leakable_item_tag(prim_path):
            leakable_items.append(prim_path)

        for child_prim in prim.GetChildren():
            child_prim_path = str(child_prim.GetPath())
            self.find_leakable_item_nested(child_prim_path, leakable_items)

    def find_spillable_area_nested(self, prim_path, spillable_areas):
        """
        This function is responsible for finding all spillable areas nested in a prim.
        """
        ctx = omni.usd.get_context()
        stage = ctx.get_stage()

        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            carb.log_error("Invalid prim access")
            return

        if self._USDTagger.prim_has_spillable_area_tag(prim_path):
            spillable_areas.append(prim_path)

        for child_prim in prim.GetChildren():
            child_prim_path = str(child_prim.GetPath())
            self.find_spillable_area_nested(child_prim_path, spillable_areas)

    def setup(self):  # noqa: C901, N802

        with self.frame:
            with ui.VStack():
                self.view_scene_tags_checkbox = None
                with ui.HStack():
                    self.view_scene_tags_checkbox = ui.CheckBox()
                    self.view_scene_tags_checkbox.model.set_value(True)
                    ui.Label("View Tagged Items?")

                def on_update_view(model=self.view_scene_tags_checkbox):
                    self._scene_tagging_data_viewer.clear_scene_ui()
                    if self.view_scene_tags_checkbox.model.get_value_as_bool():
                        self.draw_scene_data()
                    else:
                        self._scene_tagging_data_viewer.clear_scene_ui()

                self.view_scene_tags_checkbox.model.add_value_changed_fn(on_update_view)

                ui.Label("Edit tag from selection")

                def add_leakable_items(leakable_item_type):
                    """
                    This function is responsible for adding leakable item tags to the selected prims.
                    """
                    # print(loose_item_type)
                    self._scene_tagging_data = self._USDTagger.Read()

                    ctx = omni.usd.get_context()
                    selection = ctx.get_selection().get_selected_prim_paths()
                    if len(selection) == 0:
                        return

                    for prim_path in selection:
                        self._scene_tagging_data.add_leakable_item(prim_path, leakable_item_type)

                    self._USDTagger.Write(self._scene_tagging_data)
                    on_update_view()

                def remove_leakable_items():
                    """
                    This function is responsible for removing leakable item tags from the selected prims.
                    It finds all leakable items nested in the selected prims and removes them.
                    """
                    self._scene_tagging_data = self._USDTagger.Read()

                    ctx = omni.usd.get_context()
                    selection = ctx.get_selection().get_selected_prim_paths()
                    if len(selection) == 0:
                        return

                    leakable_items = []
                    for prim_path in selection:
                        self.find_leakable_item_nested(prim_path, leakable_items)
                    # print("loose items found: ", loose_items)
                    for prim_path in leakable_items:
                        leakable_item_type = self._USDTagger.get_leakable_item_tag(prim_path)
                        self._scene_tagging_data.remove_leakable_item(prim_path, leakable_item_type)

                    self._USDTagger.Write(self._scene_tagging_data)
                    on_update_view()

                def add_spillable_area(spillable_area_type):
                    """
                    This function is responsible for adding spillable area tags to the selected prims.
                    """
                    self._scene_tagging_data = self._USDTagger.Read()

                    ctx = omni.usd.get_context()
                    selection = ctx.get_selection().get_selected_prim_paths()
                    if len(selection) == 0:
                        return

                    for prim_path in selection:
                        self._scene_tagging_data.add_spillable_area(prim_path, spillable_area_type)

                    self._USDTagger.Write(self._scene_tagging_data)
                    on_update_view()

                def remove_spillable_area():
                    """
                    This function is responsible for removing spillable area tags from the selected prims.
                    """
                    self._scene_tagging_data = self._USDTagger.Read()

                    ctx = omni.usd.get_context()
                    selection = ctx.get_selection().get_selected_prim_paths()
                    if len(selection) == 0:
                        return

                    spillable_areas = []
                    for prim_path in selection:
                        self.find_spillable_area_nested(prim_path, spillable_areas)
                    for prim_path in spillable_areas:
                        spillable_area_type = self._USDTagger.get_spillable_area_tag(prim_path)
                        self._scene_tagging_data.remove_spillable_area(prim_path, spillable_area_type)

                    self._USDTagger.Write(self._scene_tagging_data)
                    on_update_view()

                with ui.VStack():
                    for leakable_item_type in AttributeUSDTagger.leakable_item_types:
                        ui.Button(
                            "Tag leakable items: " + leakable_item_type,
                            clicked_fn=lambda it=leakable_item_type: add_leakable_items(it),
                        )

                    ui.Button("Untag leakable items", clicked_fn=remove_leakable_items)

                    for spillable_area_type in AttributeUSDTagger.spillable_area_types:
                        ui.Button(
                            "Tag spillable areas: " + spillable_area_type,
                            clicked_fn=lambda it=spillable_area_type: add_spillable_area(it),
                        )

                    ui.Button("Untag spillable areas", clicked_fn=remove_spillable_area)


class SceneTaggingDataViewer:
    """
    This class is responsible for drawing the scene tagging data in the scene view.
    """

    def __init__(self):
        self._bbox_drawer: BBoxDrawerHelper = BBoxDrawerHelper("SceneTagDrawer")

        self.leakable_item_colors_by_type = {
            "Item": cl(1.0, 1.0, 1.0, 1.0),
        }
        self.spillable_area_colors_by_type = {
            "Floor": cl(0.2, 0.2, 1.0, 1.0),
        }

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self._bbox_drawer:
            self._bbox_drawer.destroy()
        self._bbox_drawer = None

    def clear_scene_ui(self):
        self._bbox_drawer.clear_canvas()

    def _get_prim_range(self, prim_path: str, bbox_cache: UsdGeom.BBoxCache, ctx):
        prim = ctx.get_stage().GetPrimAtPath(prim_path)
        bound = bbox_cache.ComputeWorldBound(prim)
        return bound.ComputeAlignedBox()

    def draw_scene_data(self, scene_tagging_data: SceneTaggingData):
        ctx = omni.usd.get_context()

        purposes = [UsdGeom.Tokens.default_]
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)

        # print("Drawing Scene!")
        for leakable_item_type, prim_paths in scene_tagging_data.leakable_item_prim_paths_by_type.items():
            for prim_path in prim_paths:
                # print("Drawing: " + str(prim_path))
                box_range = self._get_prim_range(prim_path, bbox_cache, ctx)
                bbox_max = box_range.GetMax()
                bbox_min = box_range.GetMin()

                color = self.leakable_item_colors_by_type.get(leakable_item_type, None)
                if color is None:
                    carb.log_error("No color found for leakable item type: " + leakable_item_type)
                    return

                self._bbox_drawer.draw_AABB_box(bbox_min, bbox_max, color=color)

        for spillable_area_type, prim_paths in scene_tagging_data.spillable_area_prim_paths_by_type.items():
            for prim_path in prim_paths:
                box_range = self._get_prim_range(prim_path, bbox_cache, ctx)
                bbox_max = box_range.GetMax()
                bbox_min = box_range.GetMin()
                color = self.spillable_area_colors_by_type.get(spillable_area_type, None)
                if color is None:
                    carb.log_error("No color found for spillable area type: " + spillable_area_type)
                    return

                self._bbox_drawer.draw_AABB_box(bbox_min, bbox_max, color=color)
