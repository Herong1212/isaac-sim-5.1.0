import random
import omni.kit.test
import omni.kit.commands
import omni.kit.undo
from pxr import Usd, UsdGeom, Kind


class TestCommands(omni.kit.test.AsyncTestCase):
    def check_visibillity(self, visible_set, invisible_set):
        context = omni.usd.get_context()
        stage = context.get_stage()
        for prim in stage.TraverseAll():
            if prim and not prim.GetMetadata("hide_in_stage_window"):
                if stage.HasDefaultPrim() and stage.GetDefaultPrim() == prim:
                    continue
                imageable = UsdGeom.Imageable(prim)
                if imageable:
                    if imageable.ComputeVisibility() == UsdGeom.Tokens.invisible:
                        self.assertTrue((prim.GetPath().pathString in invisible_set))
                    else:
                        self.assertTrue((prim.GetPath().pathString in visible_set))

    def get_parent_prims(self, prim):
        stage = omni.usd.get_context().get_stage()
        parent_prims = []
        while prim.GetParent():
            parent_prims.append(prim.GetParent().GetPath().pathString)
            prim = prim.GetParent()
            if stage.HasDefaultPrim() and stage.GetDefaultPrim() == prim:
                break
        return parent_prims

    def get_all_children(self, prim, child_list):
        for child in prim.GetAllChildren():
            child_list.append(child.GetPath().pathString)
            self.get_all_children(child, child_list)

    def get_all_prims(self):
        all_prims = []
        stage = omni.usd.get_context().get_stage()
        for prim in stage.TraverseAll():
            if not prim.GetMetadata("hide_in_stage_window"):
                all_prims.append(prim.GetPath().pathString)
        return all_prims

    async def setUp(self):
        # Disable logging for the time of tests to avoid spewing errors
        await omni.usd.get_context().new_stage_async()
        omni.kit.selection.tests.create_test_stage()

    async def tearDown(self):
        pass

    async def test_command_select_all(self):
        context = omni.usd.get_context()
        selection = context.get_selection()
        stage = context.get_stage()

        all_root_prims = []
        all_prims = []
        material_prims = []
        cube_prims = []
        sphere_prims = []
        children_iterator = iter(stage.TraverseAll())
        for prim in children_iterator:
            all_root_prims.append(prim.GetPath().pathString)
            children_iterator.PruneChildren()

        for prim in stage.TraverseAll():
            if prim.GetMetadata("hide_in_stage_window"):
                continue
            all_prims.append(prim.GetPath().pathString)
            if prim.GetTypeName() == "Material":
                material_prims.append(prim.GetPath().pathString)
            if prim.GetTypeName() == "Cube":
                cube_prims.append(prim.GetPath().pathString)
            if prim.GetTypeName() == "Sphere":
                sphere_prims.append(prim.GetPath().pathString)

        subset_count = int(len(all_prims) >> 1)
        subset_prims = random.sample(all_prims, subset_count)

        # SelectAllCommand Execute and undo
        selection.set_selected_prim_paths(subset_prims, True)
        omni.kit.commands.execute("SelectAll")
        self.assertListEqual(selection.get_selected_prim_paths(), all_root_prims)
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), subset_prims)

        # SelectAllCommand "Material" Execute and undo
        selection.set_selected_prim_paths(subset_prims, True)
        omni.kit.commands.execute("SelectAll", type="Material")
        self.assertListEqual(selection.get_selected_prim_paths(), material_prims)
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), subset_prims)

        # SelectAllCommand "Cube" Execute and undo
        selection.set_selected_prim_paths(subset_prims, True)
        omni.kit.commands.execute("SelectAll", type="Cube")
        self.assertListEqual(selection.get_selected_prim_paths(), cube_prims)
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), subset_prims)

        # SelectAllCommand "Sphere" Execute and undo
        selection.set_selected_prim_paths(subset_prims, True)
        omni.kit.commands.execute("SelectAll", type="Sphere")
        self.assertListEqual(selection.get_selected_prim_paths(), sphere_prims)
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), subset_prims)

        # SelectSimilarCommand: "Sphere" and "Cube"
        prim_paths = [sphere_prims[0], cube_prims[0]]
        selection.set_selected_prim_paths(prim_paths, True)
        omni.kit.commands.execute("SelectSimilar")
        all_prims = sphere_prims.copy()
        all_prims.extend(cube_prims)
        self.assertListEqual(selection.get_selected_prim_paths(), all_prims)
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), prim_paths)

    async def test_command_select_none(self):
        context = omni.usd.get_context()
        selection = context.get_selection()
        stage = context.get_stage()

        all_prims = self.get_all_prims()

        subset_count = int(len(all_prims) >> 1)
        subset_prims = random.sample(all_prims, subset_count)
        inverse_prims = [item for item in all_prims if item not in subset_prims]

        # SelectNoneCommand Execute and undo
        selection.set_selected_prim_paths(subset_prims, True)
        omni.kit.commands.execute("SelectNone")
        self.assertListEqual(selection.get_selected_prim_paths(), [])
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), subset_prims)

    async def test_command_select_invert(self):
        context = omni.usd.get_context()
        selection = context.get_selection()
        stage = context.get_stage()

        all_prims = []
        for prim in stage.TraverseAll():
            if not prim.GetMetadata("hide_in_stage_window") and stage.HasDefaultPrim() and not stage.GetDefaultPrim() == prim:
                all_prims.append(prim.GetPath().pathString)

        # if selected path as children and none of the children are selected, then all the children are selected..
        subset_count = int(len(all_prims) >> 1)
        subset_prims = []
        for prim_path in sorted(random.sample(all_prims, subset_count), reverse=True):
            prim = stage.GetPrimAtPath(prim_path)
            if prim:
                subset_prims.append(prim_path)
                child_list = []
                self.get_all_children(prim, child_list)
                if not set(subset_prims).intersection(set(child_list)):
                    subset_prims += child_list

        # SelectInvertCommand Execute and undo
        selection.set_selected_prim_paths(subset_prims, True)
        omni.kit.commands.execute("SelectInvert")
        self.assertListEqual(selection.get_selected_prim_paths(), ['/World'])
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), subset_prims)

    async def test_command_hide_unselected(self):
        context = omni.usd.get_context()
        selection = context.get_selection()
        stage = context.get_stage()

        all_prims = self.get_all_prims()

        # if selected path as children and none of the children are selected, then all the children are selected..
        subset_prims = set()
        for prim_path in sorted(random.sample(all_prims, 3), reverse=True):
            #  we need to remove "/World" from the sampled result since it is the parent of all prims
            if prim_path == '/World':
                continue
            prim = stage.GetPrimAtPath(prim_path)
            if prim:
                subset_prims.add(prim_path)
                child_list = []
                self.get_all_children(prim, child_list)
                subset_prims.update(child_list)

        # HideUnselectedCommand Execute and undo
        visible_prims = set()
        for prim_path in subset_prims:
            prim = stage.GetPrimAtPath(prim_path)
            if prim:
                visible_prims.add(prim.GetPath().pathString)
                visible_prims.update(self.get_parent_prims(prim))
        invisible_prims = set([item for item in all_prims if item not in visible_prims])

        selection.set_selected_prim_paths(list(subset_prims), True)
        omni.kit.commands.execute("HideUnselected")
        self.check_visibillity(visible_prims, invisible_prims)
        omni.kit.undo.undo()
        self.check_visibillity(all_prims, [])

    async def test_command_select_parent(self):
        context = omni.usd.get_context()
        selection = context.get_selection()
        stage = context.get_stage()

        all_prims = self.get_all_prims()

        subset_count = int(len(all_prims) >> 1)
        subset_prims = random.sample(all_prims, subset_count)

        parent_prims = set()
        for prim_path in subset_prims:
            prim = stage.GetPrimAtPath(prim_path)
            if prim and prim.GetParent() is not None:
                parent_prims.add(prim.GetParent().GetPath().pathString)
        parent_prims = list(parent_prims)

        selection.set_selected_prim_paths(subset_prims, True)
        omni.kit.commands.execute("SelectParent")
        self.assertListEqual(selection.get_selected_prim_paths(), sorted(parent_prims))
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), subset_prims)

    async def test_command_select_kind(self):
        context = omni.usd.get_context()
        selection = context.get_selection()
        stage = context.get_stage()

        all_prims = []
        group_prims = []
        for prim in stage.TraverseAll():
            if Kind.Registry.IsA(Usd.ModelAPI(prim).GetKind(), "group"):
                group_prims.append(prim.GetPath().pathString)
            if not prim.GetMetadata("hide_in_stage_window"):
                all_prims.append(prim.GetPath().pathString)

        subset_count = int(len(all_prims) >> 1)
        subset_prims = random.sample(all_prims, subset_count)

        selection.set_selected_prim_paths(subset_prims, True)
        omni.kit.commands.execute("SelectKind", kind="group")
        self.assertListEqual(selection.get_selected_prim_paths(), sorted(group_prims))
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), subset_prims)

    async def test_command_select_hierarchy(self):
        context = omni.usd.get_context()
        selection = context.get_selection()

        selection.set_selected_prim_paths(['/World'], True)
        omni.kit.commands.execute("SelectHierarchy")
        self.assertListEqual(selection.get_selected_prim_paths(), sorted(self.get_all_prims()))
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), ['/World'])

    async def test_command_select_list(self):
        context = omni.usd.get_context()
        selection = context.get_selection()

        all_prims = self.get_all_prims()

        subset_count = int(len(all_prims) >> 1)
        subset_prims = random.sample(all_prims, subset_count)

        selection.set_selected_prim_paths(['/World'], True)
        self.assertListEqual(selection.get_selected_prim_paths(), ['/World'])
        # with no kwargs it should clear the selection
        omni.kit.commands.execute("SelectList")
        self.assertListEqual(selection.get_selected_prim_paths(), [])
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), ['/World'])
        # with kwarg it should swap the selection to the new list
        omni.kit.commands.execute("SelectList", selection=subset_prims)
        self.assertListEqual(sorted(selection.get_selected_prim_paths()), sorted(subset_prims))
        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), ['/World'])

    async def test_command_select_leaf(self):
        context = omni.usd.get_context()
        selection = context.get_selection()
        stage = context.get_stage()

        selection.set_selected_prim_paths(['/World'], True)
        omni.kit.commands.execute("SelectLeaf")
        selected = selection.get_selected_prim_paths()
        for leaf in selected:
            self.assertFalse(stage.GetPrimAtPath(leaf).GetChildren())

        omni.kit.undo.undo()
        self.assertListEqual(selection.get_selected_prim_paths(), ['/World'])
