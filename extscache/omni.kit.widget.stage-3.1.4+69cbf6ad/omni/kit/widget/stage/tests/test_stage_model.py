import carb
import os
import tempfile
import omni
import omni.kit.test
import omni.usd
import omni.client
import string
import random
import omni.ui as ui

# Don't remove. Including those two deprecated modules for code coverage.
from omni.kit.widget.stage.stage_helper import *
from omni.kit.widget.stage.usd_property_watch import *

from omni.kit.widget.stage import StageWidget
from omni.kit.widget.stage import StageItem, StageItemSortPolicy
from omni.kit.widget.stage import StageColumnDelegateRegistry, AbstractStageColumnDelegate, StageColumnItem
from pxr import Sdf, Usd, UsdGeom, Gf


SETTINGS_KEEP_CHILDREN_ORDER = "/persistent/ext/omni.usd/keep_children_order"


class TestColumnDelegate(AbstractStageColumnDelegate):
    def __init__(self):
        super().__init__()

    def destroy(self):
        pass

    @property
    def initial_width(self):
        """The width of the column"""
        return ui.Pixel(20)

    def build_header(self, **kwargs):
        """Build the header"""
        pass

    async def build_widget(self, item: StageColumnItem, **kwargs):
        pass


class TestStageModel(omni.kit.test.AsyncTestCase):

    # Before running each test
    async def setUp(self):
        self.usd_context = omni.usd.get_context()
        await self.usd_context.new_stage_async()
        self.stage = self.usd_context.get_stage()
        self.stage.GetRootLayer().Clear()
        self.stage_widget = StageWidget(self.stage)
        self.app = omni.kit.app.get_app()
        self.old_keep_children_order = carb.settings.get_settings().get(SETTINGS_KEEP_CHILDREN_ORDER)

    async def tearDown(self):
        if self.old_keep_children_order is not None:
            carb.settings.get_settings().set(SETTINGS_KEEP_CHILDREN_ORDER, self.old_keep_children_order)
        self.stage_widget.destroy()
        self.stage_widget = None
        await self.usd_context.close_stage_async()

    async def test_show_undefined_prims(self):
        self.stage_widget.show_undefined_prims = False
        prim = self.stage.OverridePrim("/test")
        prim2 = self.stage.DefinePrim("/test2", "Xform")
        await self.__wait()

        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 1)
        self.assertEqual(stage_items[0].path, prim2.GetPath())

        self.stage_widget.show_undefined_prims = True
        await self.__wait()
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 2)
        self.assertEqual(stage_items[0].path, prim.GetPath())
        self.assertEqual(stage_items[1].path, prim2.GetPath())

    async def test_show_inactive_prims(self):
        self.stage_widget.show_inactive_prims = False
        prim = self.stage.DefinePrim("/testinactive", "Xform")
        prim2 = self.stage.DefinePrim("/test2", "Xform")
        prim.SetActive(False)
        prim2.SetActive(True)
        await self.__wait()

        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 1)
        self.assertEqual(stage_items[0].path, prim2.GetPath())

        self.stage_widget.show_inactive_prims = True
        await self.__wait()
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 2)
        self.assertEqual(stage_items[0].path, prim.GetPath())
        self.assertEqual(stage_items[1].path, prim2.GetPath())
    
    async def test_show_abstract_prims(self):
        self.stage_widget.show_abstract_prims = False
        prim = self.stage.DefinePrim("/test_class")
        prim.SetSpecifier(Sdf.SpecifierClass)
        prim2 = self.stage.DefinePrim("/test", "Xform")
        await self.__wait()

        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 1)
        self.assertEqual(stage_items[0].path, prim2.GetPath())

        self.stage_widget.show_abstract_prims = True
        await self.__wait()
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 2)
        self.assertEqual(stage_items[0].path, prim.GetPath())
        self.assertEqual(stage_items[1].path, prim2.GetPath())

    async def test_prim_item_api(self):
        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root
        self.assertTrue(root_stage_item.visibility_model)
        self.assertTrue(root_stage_item.type_model)
        self.assertTrue(root_stage_item.name_model)

    async def test_show_prim_displayname(self):
        self.stage_widget.show_prim_display_name = False
        prim = self.stage.DefinePrim("/test", "Xform")
        self.stage.DefinePrim("/test100", "Xform")
        self.stage.DefinePrim("/test200", "Xform")
        omni.usd.editor.set_display_name(prim, "display name test测试★")
        await self.__wait(1)

        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertTrue(stage_items)
        prim_item = stage_items[0]
        self.assertTrue(prim_item)
        self.assertEqual(prim_item.name, "test")
        self.assertEqual(prim_item.display_name, "display name test测试★")
        self.assertEqual(prim_item.name_model.get_value_as_string(), "test")

        # Change it to display name will show its display name instead
        self.stage_widget.show_prim_display_name = True
        await self.__wait()
        self.assertEqual(prim_item.name, "test")
        self.assertEqual(prim_item.display_name, "display name test测试★")
        self.assertEqual(prim_item.name_model.get_value_as_string(), prim_item.display_name)

        # Empty display name will show path name instead
        omni.usd.editor.set_display_name(prim, "")
        await self.__wait()
        self.assertEqual(prim_item.name, "test")
        self.assertEqual(prim_item.display_name, prim_item.name)
        self.assertEqual(prim_item.name_model.get_value_as_string(), prim_item.display_name)

        # Emulate rename, it will rename prim name when it shows displayName.
        stage_items = stage_model.get_item_children(root_stage_item)

        omni.usd.editor.set_display_name(prim, "display name test")
        await self.__wait(1)
        prim_item.name_model.begin_edit()
        prim_item.name_model.set_value("test3ÄßÖÜäöü")
        prim_item.name_model.end_edit()
        await self.__wait(5)
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertTrue(stage_items)
        prim_item = stage_items[0]
        self.assertEqual(prim_item.name, "test")
        self.assertEqual(prim_item.display_name, "test3ÄßÖÜäöü")
        self.assertEqual(prim_item.name_model.get_value_as_string(), prim_item.display_name)
        # Make sure change display name will not influence prim path.
        self.assertTrue(self.stage.GetPrimAtPath("/test"))
        self.assertFalse(self.stage.GetPrimAtPath("/testÄßÖÜäöü"))
        self.assertEqual(stage_items[0].path, Sdf.Path("/test"))
        self.assertEqual(stage_items[1].path, Sdf.Path("/test100"))
        self.assertEqual(stage_items[2].path, Sdf.Path("/test200"))

        self.stage_widget.show_prim_display_name = False
        prim_item.name_model.begin_edit()
        prim_item.name_model.set_value("test2")
        prim_item.name_model.end_edit()
        await self.__wait()
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertTrue(stage_items)
        prim_item = stage_items[-1]
        self.assertEqual(prim_item.name, "test2")
        self.assertEqual(prim_item.display_name, "test3ÄßÖÜäöü")
        self.assertEqual(prim_item.name_model.get_value_as_string(), prim_item.name)
        self.assertFalse(self.stage.GetPrimAtPath("/test"))
        self.assertTrue(self.stage.GetPrimAtPath("/test2"))

        # Search display name even in flat mode. It's expected that the prim that matches the
        # displayName returned and in non-flat mode.
        self.stage_widget.show_prim_display_name = True
        stage_model.flat = True
        stage_model.filter_by_text("test3")
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 1)
        self.assertEqual(stage_items[0].name, "test2")
        self.assertEqual(stage_items[0].display_name, "test3ÄßÖÜäöü")
        self.assertEqual(stage_items[0].name_model.get_value_as_string(), stage_items[0].display_name)
        self.assertFalse(stage_model.flat)
        stage_model.filter_by_text("")

    def create_flat_prims(self, stage, parent_path, num):
        prim_paths = set([])
        for i in range(num):
            prim = stage.DefinePrim(parent_path.AppendElementString(f"xform{i}"), "Xform")
            translation = Gf.Vec3d(-200, 0.0, 0.0)
            common_api = UsdGeom.XformCommonAPI(prim)
            common_api.SetTranslate(translation)
            prim_paths.add(prim.GetPath())

        return prim_paths

    def get_all_stage_items(self, stage_item: StageItem):
        stage_items = set()

        q = [stage_item]
        if stage_item.path != Sdf.Path.absoluteRootPath:
            stage_items.add(stage_item)
        while len(q) > 0:
            item = q.pop()
            # Populating it if it's not.
            children = item.stage_model.get_item_children(item)
            for child in children:
                stage_items.add(child)
                q.append(child)

        return stage_items

    def get_all_stage_item_paths(self, stage_item):
        stage_items = self.get_all_stage_items(stage_item)
        paths = [item.path for item in stage_items]

        return set(paths)

    def create_prims(self, stage, parent_prim_path, level=[]):
        if not level:
            return set()

        prim_paths = self.create_flat_prims(stage, parent_prim_path, level[0])

        all_child_paths = set()
        for prim_path in prim_paths:
            all_child_paths.update(self.create_prims(stage, prim_path, level[1:]))

        prim_paths.update(all_child_paths)

        return prim_paths

    def check_prim_children(self, prim_item: StageItem, expected_children_prim_paths):
        paths = set()
        children = prim_item.stage_model.get_item_children(prim_item)
        for child in children:
            paths.add(child.path)

        if children:
            self.assertTrue(prim_item.stage_model.can_item_have_children(prim_item))
        else:
            self.assertFalse(prim_item.stage_model.can_item_have_children(prim_item))
        self.assertEqual(paths, set(expected_children_prim_paths))

    def check_prim_tree(self, prim_item: StageItem, expected_prim_paths):
        paths = self.get_all_stage_item_paths(prim_item)
        self.assertEqual(set(paths), set(expected_prim_paths))

    async def test_prims_create(self):
        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root

        prim_paths = self.create_prims(self.stage, Sdf.Path.absoluteRootPath, [3, 2, 3, 2])
        await self.__wait()

        self.check_prim_tree(root_stage_item, prim_paths)

    async def test_prims_edits(self):
        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root

        prim_paths = self.create_prims(self.stage, Sdf.Path.absoluteRootPath, [3, 2, 3, 2])
        await self.__wait()

        # Populate children of root prim
        stage_model.get_item_children(None)
        prim1_of_root = root_stage_item.children[0].path
        omni.kit.commands.execute(
            "DeletePrims",
            paths=[prim1_of_root]
        )
        await self.__wait(1)

        changed_prims = prim_paths.copy()
        for path in prim_paths:
            if path.HasPrefix(prim1_of_root):
                changed_prims.discard(path)

        self.check_prim_tree(root_stage_item, changed_prims)
        omni.kit.undo.undo()
        await self.__wait()
        self.check_prim_tree(root_stage_item, prim_paths)

    async def test_layer_flush(self):
        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root

        prim_paths = self.create_prims(self.stage, Sdf.Path.absoluteRootPath, [10, 5, 4, 2])
        await self.__wait(1)
        self.check_prim_tree(root_stage_item, prim_paths)

        self.stage.GetRootLayer().Clear()
        await self.__wait(1)
        self.check_prim_tree(root_stage_item, set())

    async def test_parenting_prim_refresh(self):
        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root

        # Creates 3 prims
        prim_paths = list(self.create_prims(self.stage, Sdf.Path.absoluteRootPath, [3]))
        await self.__wait(1)
        self.check_prim_tree(root_stage_item, set(prim_paths))

        # Moves first two prims as the children of the 3rd one.
        new_path0 = prim_paths[2].AppendElementString(prim_paths[0].name)
        new_path1 = prim_paths[2].AppendElementString(prim_paths[1].name)
        omni.kit.commands.execute("MovePrim", path_from=prim_paths[0], path_to=new_path0)
        omni.kit.commands.execute("MovePrim", path_from=prim_paths[1], path_to=new_path1)
        await self.__wait()

        self.assertEqual(len(root_stage_item.children), 1)
        self.assertEqual(root_stage_item.children[0].path, prim_paths[2])
        self.check_prim_children(root_stage_item.children[0], set([new_path0, new_path1]))

        omni.kit.undo.undo()
        await self.__wait(1)
        self.check_prim_children(root_stage_item, set(prim_paths[1:3]))
        self.check_prim_tree(root_stage_item, set([new_path0, prim_paths[1], prim_paths[2]]))

        omni.kit.undo.undo()
        await self.__wait()
        self.check_prim_tree(root_stage_item, set(prim_paths))

    async def test_filter_prim(self):
        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root

        prim_paths = self.create_prims(self.stage, Sdf.Path.absoluteRootPath, [10, 5, 4, 2])
        await self.__wait()

        # Flat search
        stage_model.flat = True
        stage_model.filter_by_text("xform")
        self.check_prim_children(root_stage_item, prim_paths)

        children = root_stage_item.children
        for child in children:
            self.assertTrue(not child.children)

        children = stage_model.get_item_children(root_stage_item)
        paths = []
        for child in children:
            paths.append(child.path)

        self.assertEqual(set(paths), set(prim_paths))

        expected_paths = set()
        for path in prim_paths:
            if str(path).endswith("xform0"):
                expected_paths.add(path)

        stage_model.filter_by_text("xform0")
        children = stage_model.get_item_children(root_stage_item)
        paths = []
        for child in children:
            paths.append(child.path)
        self.assertEqual(set(paths), set(expected_paths))

        # Non-flat search
        stage_model.flat = False
        stage_model.filter_by_text("xform")
        self.check_prim_tree(root_stage_item, prim_paths)
        children = root_stage_item.children
        for child in children:
            self.assertFalse(not child.children)

        # Filtering with lambda
        # Reset all states
        stage_model.filter_by_text(None)
        stage_model.filter(add={"Camera" : lambda prim: prim.IsA(UsdGeom.Camera)})
        self.check_prim_tree(root_stage_item, [])

        stage_model.filter(remove=["Camera"])
        self.check_prim_tree(root_stage_item, prim_paths)
        children = root_stage_item.children
        for child in children:
            self.assertFalse(not child.children)

        stage_model.filter(add={"Xform" : lambda prim: prim.IsA(UsdGeom.Xform)})
        self.check_prim_tree(root_stage_item, prim_paths)

        camera = self.stage.DefinePrim("/new_group/camera0", "Camera")
        await self.__wait()

        # Adds new camera will still not be filtered as only xform is filtered currently
        self.check_prim_tree(root_stage_item, prim_paths)

        # Filters camera also
        stage_model.filter(add={"Camera" : lambda prim: prim.IsA(UsdGeom.Camera)})
        all_paths = []
        all_paths.extend(prim_paths)
        all_paths.append(camera.GetPath())
        # Needs to add parent also as it's in non-flat mode
        all_paths.append(camera.GetPath().GetParentPath())
        self.check_prim_tree(root_stage_item, all_paths)

        # Creates another camera and filter it.
        camera1 = self.stage.DefinePrim("/new_group2/camera1", "Camera")
        all_paths.append(camera1.GetPath())
        all_paths.append(camera1.GetPath().GetParentPath())
        await self.__wait()
        self.check_prim_tree(root_stage_item, all_paths)

        # Filters with both types and texts.
        stage_model.filter_by_text("camera")
        all_paths = [
            camera.GetPath(), camera.GetPath().GetParentPath(),
            camera1.GetPath(), camera1.GetPath().GetParentPath()
        ]
        self.check_prim_tree(root_stage_item, all_paths)

        # Add new reference layer will be filtered also
        reference_layer = Sdf.Layer.CreateAnonymous()
        ref_stage = Usd.Stage.Open(reference_layer)
        prim = ref_stage.DefinePrim("/root/camera_reference", "Camera")
        default_prim = prim.GetParent()
        ref_stage.SetDefaultPrim(default_prim)
        reference_prim = self.stage.DefinePrim("/root", "Xform")
        reference_prim.GetReferences().AddReference(reference_layer.identifier)
        await self.__wait()

        all_paths.append(prim.GetPath())
        all_paths.append(default_prim.GetPath())
        self.check_prim_tree(root_stage_item, all_paths)

        # Add new sublayer too.
        reference_layer = Sdf.Layer.CreateAnonymous()
        sublayer_stage = Usd.Stage.Open(reference_layer)
        prim = sublayer_stage.DefinePrim("/root/camera_sublayer", "Camera")
        self.stage.GetRootLayer().subLayerPaths.append(reference_layer.identifier)
        await self.__wait()

        all_paths.append(prim.GetPath())
        self.check_prim_tree(root_stage_item, all_paths)

        # Clear all
        stage_model.filter(clear=True)
        stage_model.filter_by_text("")
        prim_paths.update(all_paths)
        self.check_prim_tree(root_stage_item, prim_paths)

        # Test filter with prim path
        stage_model.filter(clear=True)
        stage_model.flat = True
        prim = self.stage.DefinePrim("/root/parent", "Xform")
        prim = self.stage.DefinePrim("/root/parent/child1", "Xform")
        prim = self.stage.DefinePrim("/root/parent/child1/child2", "Xform")
        await self.__wait(1)
        stage_model.filter_by_text("/root/parent")
        children = stage_model.get_item_children(stage_model.root)
        parent_item = stage_model.find("/root/parent")
        child1 = stage_model.find("/root/parent/child1")
        child2 = stage_model.find("/root/parent/child1/child2")
        self.assertEqual(len(children), 3)
        self.assertEqual(set(children), set([parent_item, child1, child2]))

        stage_model.filter_by_text("/root/parent/")
        children = stage_model.get_item_children(stage_model.root)
        child1 = stage_model.find("/root/parent/child1")
        child2 = stage_model.find("/root/parent/child1/child2")
        self.assertEqual(len(children), 2)
        self.assertEqual(set(children), set([child1, child2]))

        # Change flat mode will switch the prim tree.
        stage_model.filter_by_text("")
        stage_model.flat = False
        stage_model.filter_by_text("/root/parent")
        self.check_prim_tree(root_stage_item, [Sdf.Path("/root"), Sdf.Path("/root/parent")])

        # In non-flat mode, searching with slash will return parent and all its children.
        stage_model.flat = False
        stage_model.filter_by_text("/root/parent/")
        children = stage_model.get_item_children(stage_model.root)
        root_item = stage_model.find("/root")
        child1 = stage_model.find("/root/parent/child1")
        child2 = stage_model.find("/root/parent/child1/child2")
        self.assertEqual(len(children), 1)
        self.assertEqual(set(children), set([root_item]))

        children = stage_model.get_item_children(children[0])
        self.assertEqual(len(children), 1)
        self.assertEqual(set(children), set([parent_item]))

        children = stage_model.get_item_children(children[0])
        self.assertEqual(len(children), 1)
        self.assertEqual(set(children), set([child1]))

        children = stage_model.get_item_children(children[0])
        self.assertEqual(len(children), 1)
        self.assertEqual(set(children), set([child2]))

    async def test_find_full_chain(self):
        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root

        self.create_prims(self.stage, Sdf.Path.absoluteRootPath, [4, 3, 3, 2])
        await self.__wait()

        path = Sdf.Path("/xform0/xform0/xform0/xform0")
        full_chain = stage_model.find_full_chain("/xform0/xform0/xform0/xform0")
        self.assertEqual(len(full_chain), 5)
        self.assertEqual(full_chain[0], root_stage_item)

        prefixes = path.GetPrefixes()
        for i in range(len(prefixes)):
            self.assertEqual(full_chain[i + 1].path, prefixes[i])

    async def test_has_missing_references(self):
        stage_model = self.stage_widget.get_model()

        self.create_prims(self.stage, Sdf.Path.absoluteRootPath, [1])
        path = Sdf.Path("/xform0")
        full_chain = stage_model.find_full_chain(path)
        self.assertEqual(len(full_chain), 2)

        # Prim /xform0
        prim_item = full_chain[1]
        self.assertFalse(prim_item.has_missing_references)

        prim = self.stage.GetPrimAtPath(path)
        prim.GetReferences().AddReference("./face-invalid-non-existed-file.usd")
        await self.__wait()
        self.assertTrue(prim_item.has_missing_references)

    async def test_instanceable_flag_change(self):
        # OM-70714: Change instanceable flag will refresh children's instance_proxy flag.
        with tempfile.TemporaryDirectory() as tmpdirname:
            # save the file
            tmp_file_path = os.path.join(tmpdirname, "tmp.usda")
            result = await omni.usd.get_context().save_as_stage_async(tmp_file_path)
            self.assertTrue(result)

            stage = omni.usd.get_context().get_stage()
            prim = stage.DefinePrim("/World/cube", "Xform")
            stage.SetDefaultPrim(prim)
            stage.Save()

            await omni.usd.get_context().new_stage_async()

        stage = omni.usd.get_context().get_stage()
        prim = stage.DefinePrim("/World/Reference", "Xform")
        prim.GetReferences().AddReference(tmp_file_path)

        omni.kit.commands.execute("CopyPrim", path_from="/World/Reference", path_to="/World/Reference2")

        prim2 = stage.GetPrimAtPath("/World/Reference2")
        self.assertTrue(prim2)

        prim.SetInstanceable(True)
        prim2.SetInstanceable(True)
        await self.__wait()

        self.stage_widget = StageWidget(stage)
        stage_model = self.stage_widget.get_model()
        # Populate all childrens
        stage_model.find_full_chain("/World/Reference/cube")
        stage_model.find_full_chain("/World/Reference2/cube")

        reference_item = stage_model.find("/World/Reference")
        reference2_item = stage_model.find("/World/Reference2")
        self.assertTrue(reference_item and reference2_item)
        for item in [reference_item, reference2_item]:
            self.assertTrue(item.instanceable)
            for child in item.children:
                self.assertTrue(child.instance_proxy)

        prim2.SetInstanceable(False)
        await self.__wait(1)
        for child in reference_item.children:
            self.assertTrue(child.instance_proxy)

        for child in reference2_item.children:
            self.assertFalse(child.instance_proxy)

    async def _test_sorting_internal(self, prim_paths, sort_policy, sort_func, reverse):
        self.stage_widget = StageWidget(self.stage)
        stage_model = self.stage_widget.get_model()
        stage_model.set_items_sort_policy(sort_policy)

        await self.__wait()
        # Checks all items to see if their children are sorted correctly.
        root_stage_item = stage_model.root
        queue = [root_stage_item]
        while queue:
            item = queue.pop()
            children = stage_model.get_item_children(item)
            if not children:
                continue

            queue.extend(children)

            if item == root_stage_item:
                expected_children_paths = list(prim_paths.keys())
            else:
                expected_children_paths = list(prim_paths[str(item.path)])

            if sort_func:
                expected_children_paths.sort(key=sort_func, reverse=reverse)
            elif reverse:
                expected_children_paths.reverse()

            children_paths = [str(child.path) for child in children]
            self.assertEqual(children_paths, expected_children_paths)

    async def test_sorting(self):
        # Generating test data
        prim_paths = {}
        types = ["Cube", "Cone", "Sphere", "Xform", "Cylinder", "Capsule"]
        prim_types = {}
        prim_visibilities = {}
        with Sdf.ChangeBlock():
            for i in range(0, 26):
                letter = random.choice(string.ascii_letters)
                parent_path = f"/{letter}{i}"
                prim_type = random.choice(types)
                spec = Sdf.CreatePrimInLayer(self.stage.GetRootLayer(), parent_path)
                spec.typeName = prim_type
                children_paths = []
                prim_types[parent_path] = prim_type
                prim_visibilities[parent_path] = True
                for j in range(0, 50):
                    letter = random.choice(string.ascii_letters)
                    prim_type = random.choice(types)
                    spec = Sdf.CreatePrimInLayer(self.stage.GetRootLayer(), f"{parent_path}/{letter}{j}")
                    spec.typeName = prim_type
                    children_paths.append(str(spec.path))
                    prim_types[str(spec.path)] = prim_type
                    visible = random.choice([True, False])
                    prim_visibilities[str(spec.path)] = visible

                prim_paths[parent_path] = children_paths

        for path, value in prim_visibilities.items():
            prim = self.stage.GetPrimAtPath(path)
            if prim:
                imageable = UsdGeom.Imageable(prim)
                if not value:
                    imageable.MakeInvisible()

        await self._test_sorting_internal(prim_paths, StageItemSortPolicy.DEFAULT, None, False)
        await self._test_sorting_internal(prim_paths, StageItemSortPolicy.NAME_COLUMN_OLD_TO_NEW, None, False)
        await self._test_sorting_internal(prim_paths, StageItemSortPolicy.NAME_COLUMN_NEW_TO_OLD, None, True)
        await self._test_sorting_internal(
            prim_paths,
            StageItemSortPolicy.NAME_COLUMN_A_TO_Z, lambda x: Sdf.Path(x).name.lower(), False
        )
        await self._test_sorting_internal(
            prim_paths,
            StageItemSortPolicy.NAME_COLUMN_Z_TO_A, lambda x: Sdf.Path(x).name.lower(), True
        )
        await self._test_sorting_internal(
            prim_paths,
            StageItemSortPolicy.TYPE_COLUMN_A_TO_Z,
            lambda x, p=prim_types: p[x].lower(),
            False
        )
        await self._test_sorting_internal(
            prim_paths,
            StageItemSortPolicy.TYPE_COLUMN_Z_TO_A,
            lambda x, p=prim_types: p[x].lower(),
            True,
        )
        await self._test_sorting_internal(
            prim_paths,
            StageItemSortPolicy.VISIBILITY_COLUMN_INVISIBLE_TO_VISIBLE,
            lambda x, p=prim_visibilities: 1 if p[x] else 0,
            False
        )
        await self._test_sorting_internal(
            prim_paths,
            StageItemSortPolicy.VISIBILITY_COLUMN_VISIBLE_TO_INVISIBLE,
            lambda x, p=prim_visibilities: 0 if p[x] else 1,
            False
        )

    async def test_column_delegate(self):
        _ = StageColumnDelegateRegistry().register_column_delegate("test", TestColumnDelegate)
        self.assertEqual(StageColumnDelegateRegistry().get_column_delegate("test"), TestColumnDelegate)
        names = StageColumnDelegateRegistry().get_column_delegate_names()
        self.assertTrue("test" in names)

    async def test_item_destroy(self):
        destroyed_paths = []

        def on_items_destroyed(items):
            nonlocal destroyed_paths
            for item in items:
                destroyed_paths.append(item.path)

        stage_model = self.stage_widget.get_model()
        prim_paths = list(self.create_prims(self.stage, Sdf.Path.absoluteRootPath, [3]))
        root_stage_item = stage_model.root
        # Populate root node
        stage_model.get_item_children(root_stage_item)
        _ = stage_model.subscribe_stage_items_destroyed(on_items_destroyed)

        self.stage.RemovePrim(prim_paths[0])
        await self.__wait()

        self.assertTrue(len(destroyed_paths) == 1)
        self.assertEqual(destroyed_paths[0], prim_paths[0])

    async def test_stage_item_properties(self):
        stage_model = self.stage_widget.get_model()
        stage = stage_model.stage
        xform_prim = stage.DefinePrim("/test_prim", "Xform")

        await self.__wait()
        # Populate root node
        stage_model.get_item_children(stage_model.root)
        stage_item = stage_model.find(xform_prim.GetPath())
        self.assertTrue(stage_item)
        self.assertEqual(stage_item.name, "test_prim")
        self.assertEqual(stage_item.type_name, "Xform")
        self.assertTrue(stage_item.active)
        self.assertFalse(stage_item.has_missing_references)
        self.assertFalse(stage_item.payrefs)
        self.assertFalse(stage_item.is_default)
        self.assertFalse(stage_item.is_outdated)
        self.assertFalse(stage_item.in_session)
        self.assertFalse(stage_item.auto_reload)
        self.assertEqual(stage_item.root_identifier, stage.GetRootLayer().identifier)
        self.assertFalse(stage_item.instance_proxy)
        self.assertFalse(stage_item.instanceable)
        self.assertTrue(stage_item.visible)
        self.assertFalse(stage_item.payloads)
        self.assertFalse(stage_item.references)
        self.assertTrue(stage_item.prim)

        stage.SetDefaultPrim(xform_prim)
        xform_prim.SetInstanceable(True)
        await self.__wait()
        self.assertTrue(stage_item.is_default)
        self.assertTrue(stage_item.instanceable)

        xform_prim.SetActive(False)
        await self.__wait()
        self.assertFalse(stage_item.active)
        xform_prim = stage.GetPrimAtPath("/test_prim")
        xform_prim.SetActive(True)
        xform_prim = stage.GetPrimAtPath("/test_prim")

        # Changes active property will resync stage_item
        stage_model.get_item_children(stage_model.root)
        stage_item = stage_model.find(xform_prim.GetPath())

        UsdGeom.Imageable(xform_prim).MakeInvisible()
        await self.__wait()
        self.assertFalse(stage_item.visible)

        UsdGeom.Imageable(xform_prim).MakeVisible()
        await self.__wait()
        self.assertTrue(stage_item.visible)

        xform_prim.GetReferences().AddReference("__non_existed_reference.usd")
        xform_prim.GetReferences().AddInternalReference("/non_existed_prim")
        await self.__wait()
        self.assertTrue(stage_item.has_missing_references)
        self.assertEqual(stage_item.payrefs, ["__non_existed_reference.usd"])
        self.assertTrue(stage_item.references)
        self.assertFalse(stage_item.payloads)

        xform_prim.GetPayloads().AddPayload("__non_existed_payload.usd")
        await self.__wait()
        self.assertTrue(stage_item.has_missing_references)
        # Internal references will not be listed.
        self.assertEqual(
            set(stage_item.payrefs),
            set(["__non_existed_reference.usd", "__non_existed_payload.usd"])
        )
        self.assertTrue(stage_item.references)
        self.assertTrue(stage_item.payloads)

    async def __wait(self, n_frames=2):
        for _ in range(n_frames):
            await self.app.next_update_async()

    async def test_reorder_prim(self):
        self.stage_widget.children_reorder_supported = True
        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root

        # Creates 3 prims
        prim_paths = list(self.create_prims(self.stage, Sdf.Path.absoluteRootPath, [3]))
        await self.__wait(1)
        self.check_prim_tree(root_stage_item, set(prim_paths))

        # Moves first two prims as the children of the 3rd one.
        self.assertTrue(stage_model.drop_accepted(root_stage_item, root_stage_item.children[0], drop_location=2))
        self.assertTrue(stage_model.drop_accepted(root_stage_item, root_stage_item.children[0], drop_location=1))
        self.assertFalse(stage_model.drop_accepted(root_stage_item, root_stage_item.children[0], drop_location=-1))
        children = root_stage_item.children
        prim_paths = [item.path for item in children]
        stage_model.drop(root_stage_item, root_stage_item.children[0], drop_location=2)
        await self.__wait(10)

        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 3)
        self.assertEqual(stage_items[0].path, prim_paths[1])
        self.assertEqual(stage_items[1].path, prim_paths[0])
        self.assertEqual(stage_items[2].path, prim_paths[2])

        omni.kit.undo.undo()
        await self.__wait(1)

        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 3)
        self.assertEqual(stage_items[0].path, prim_paths[0])
        self.assertEqual(stage_items[1].path, prim_paths[1])
        self.assertEqual(stage_items[2].path, prim_paths[2])

        # Disable reorder
        self.stage_widget.children_reorder_supported = False
        self.assertFalse(stage_model.drop_accepted(root_stage_item, root_stage_item.children[0], drop_location=2))
        self.assertFalse(stage_model.drop_accepted(root_stage_item, root_stage_item.children[0], drop_location=1))
        self.assertFalse(stage_model.drop_accepted(root_stage_item, root_stage_item.children[0], drop_location=-1))
        self.stage_widget.children_reorder_supported = True
        await self.__wait(5)
        # Renaming prim will still keep the location of prim.
        # Enable setting to keep children order after rename.
        carb.settings.get_settings().set(SETTINGS_KEEP_CHILDREN_ORDER, True)
        stage_item = root_stage_item.children[0]
        stage_item.name_model.begin_edit()
        stage_item.name_model.set_value("renamed_item")
        stage_item.name_model.end_edit()
        await self.__wait()
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 3)
        self.assertEqual(stage_items[0].path, Sdf.Path("/renamed_item"))
        self.assertEqual(stage_items[1].path, prim_paths[1])
        self.assertEqual(stage_items[2].path, prim_paths[2])

        omni.kit.undo.undo()
        await self.__wait(1)
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 3)
        self.assertEqual(stage_items[0].path, prim_paths[0])
        self.assertEqual(stage_items[1].path, prim_paths[1])
        self.assertEqual(stage_items[2].path, prim_paths[2])

        with tempfile.TemporaryDirectory() as tmpdirname:
            # save the file
            tmp_file_path = os.path.join(tmpdirname, "tmp.usda")
            layer = Sdf.Layer.CreateNew(tmp_file_path)
            stage = Usd.Stage.Open(layer)
            prim = stage.DefinePrim("/World/cube", "Xform")
            stage.SetDefaultPrim(prim)
            stage.Save()
            stage = None
            layer = None

            stage_model.drop(root_stage_item, tmp_file_path, drop_location=3)
            await self.__wait(5)
            stage_items = stage_model.get_item_children(root_stage_item)
            self.assertEqual(len(stage_items), 4)
            self.assertEqual(stage_items[0].path, prim_paths[0])
            self.assertEqual(stage_items[1].path, prim_paths[1])
            self.assertEqual(stage_items[2].path, prim_paths[2])
            self.assertEqual(stage_items[3].path, Sdf.Path("/tmp"))

            stage_model.drop(root_stage_item, tmp_file_path, drop_location=1)
            await self.__wait(10)
            stage_items = stage_model.get_item_children(root_stage_item)
            self.assertEqual(len(stage_items), 5)
            self.assertEqual(stage_items[1].path, Sdf.Path("/tmp_01"))

            await omni.usd.get_context().new_stage_async()

    async def test_multiple_drag_and_drop(self):
        stage = omni.usd.get_context().get_stage()
        prim = stage.DefinePrim("/test1", "Xform")
        prim2 = stage.DefinePrim("/test2", "Xform")
        prim3 = stage.DefinePrim("/test3", "Xform")

        await self.__wait(2)

        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root
        stage_items = stage_model.get_item_children(root_stage_item)
        self.assertEqual(len(stage_items), 3)
        self.assertEqual(
            [prim.GetPath(), prim2.GetPath(), prim3.GetPath()],
            [stage_items[0].path, stage_items[1].path, stage_items[2].path]
        )

        # Select prim one by one to check if the drag mime data is changed accordingly.
        selected_prim_paths = []
        for prim_path in [str(prim.GetPath()), str(prim2.GetPath()), str(prim3.GetPath())]:
            selected_prim_paths.append(prim_path)
            omni.usd.get_context().get_selection().set_selected_prim_paths(selected_prim_paths, True)
            await self.__wait(2)

            expected_mime_data = "\n".join(selected_prim_paths)
            self.assertEqual(expected_mime_data, stage_model.get_drag_mime_data(root_stage_item))

        # Clear them
        omni.usd.get_context().get_selection().clear_selected_prim_paths()
        await self.__wait(2)
        self.assertEqual(str(stage_items[0].path), stage_model.get_drag_mime_data(stage_items[0]))

    async def test_rename_display_name(self):
        # OM-85989: while showing display name and rename an item, white space should not be replaced with '_'
        prim = self.stage.DefinePrim("/test", "Xform")

        stage_model = self.stage_widget.get_model()
        root_stage_item = stage_model.root
        stage_items = stage_model.get_item_children(root_stage_item)
        test_item = stage_items[0]
        self.assertEqual(test_item.name, "test")
        self.assertEqual(test_item.display_name, "test")

        self.stage_widget.show_prim_display_name = False
        test_item.name_model.begin_edit()
        test_item.name_model.set_value("test 1")
        test_item.name_model.end_edit()
        await self.__wait(5)
        self.assertEqual(test_item.name_model.get_value_as_string(), "test_1")

        self.stage_widget.show_prim_display_name = True
        test_item.name_model.begin_edit()
        test_item.name_model.set_value("test 2")
        test_item.name_model.end_edit()
        await self.__wait(5)

        self.assertEqual(test_item.name_model.get_value_as_string(), "test 2")

    async def test_selection(self):
        # Make sure all loading is resolved (necessary to run this test by itself)
        await self.__wait()

        stage_model = self.stage_widget.get_model()

        selected_items = []
        def _on_items_selected():
            nonlocal selected_items
            selected_items = stage_model.get_selected_stage_items()

        _ = stage_model.subscribe_stage_items_selection_changed(_on_items_selected)
        selection = self.usd_context.get_selection()

        xform_a = UsdGeom.Xform.Define(self.stage, "/A/B/C/D")
        xform_b = UsdGeom.Xform.Define(self.stage, "/E/B/C/D")

        # Wait one frame to be sure other objects created after initialization
        await self.__wait(1)

        # Creates and gets two items without expanding their parent
        item_a = stage_model._get_stage_item_from_cache(xform_a.GetPath(), True)
        item_b = stage_model._get_stage_item_from_cache(xform_b.GetPath(), True)

        # Selects the two items to ensure their parents are expanded
        stage_model.set_selected_stage_items([item_a, item_b])
        self.assertEqual(set(stage_model.get_selected_stage_items()), set([item_a, item_b]))
        self.assertEqual(set(selected_items), set([item_a, item_b]))
        self.assertEqual(set(selection.get_selected_prim_paths()), set([xform_a.GetPath().pathString, xform_b.GetPath().pathString]))

        # There appears to be a bug in IEvents (fixed in IEventDispatcher) that stage_model takes advantage
        # of here, where asyncio coroutines can be finished out-of-order. Wait here to fix it.
        await self.__wait(1)
        self.stage.RemovePrim(xform_a.GetPath())
        await self.__wait()
        self.assertEqual(stage_model.get_selected_stage_items(), [item_b])
        self.assertEqual(selected_items, [item_b])
        self.assertEqual(selection.get_selected_prim_paths(), [xform_b.GetPath().pathString])

        xform_a = UsdGeom.Xform.Define(self.stage, "/A/B/C/D")
        item_a = stage_model._get_stage_item_from_cache(xform_a.GetPath(), True)
        item_b = stage_model._get_stage_item_from_cache(xform_b.GetPath(), True)
        xform_a.GetPrim().SetActive(False)
        await self.__wait()
        stage_model.set_selected_stage_items([item_a, item_b])
        await self.__wait()

        # It can select deactivated prims also
        self.assertEqual(set(stage_model.get_selected_stage_items()), set([item_a, item_b]))
        self.assertEqual(set(selected_items), set([item_a, item_b]))
        # But omni.kit.selection only selects active paths.
        self.assertEqual(selection.get_selected_prim_paths(), [xform_b.GetPath().pathString])
