import carb
import omni
import omni.kit.test
import omni.usd
import omni.client
import omni.kit.widget.layers

from omni.kit.usd.layers import LayerUtils
from omni.kit.widget.layers.prim_spec_item import PrimSpecItem, PrimSpecSpecifier
from pxr import Sdf, Usd, UsdGeom, Gf


class TestLayerNonUIBase(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self.usd_context = omni.usd.get_context()
        self.app = omni.kit.app.get_app()
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        await omni.usd.get_context().close_stage_async()


class TestLayerUIBase(omni.kit.test.AsyncTestCase):
    """Tests for layer model refresh reacted to usd stage changes."""

    # Before running each test
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self.usd_context = omni.usd.get_context()
        self.layers_instance = omni.kit.widget.layers.get_instance()
        self.app = omni.kit.app.get_app()
        token = carb.tokens.get_tokens_interface()
        self.temp_dir = token.resolve("${temp}")
        if not self.temp_dir.endswith("/"):
            self.temp_dir += "/"

    async def tearDown(self):
        if self.layers_instance.get_layer_model():
            self.layers_instance.get_layer_model().spec_linking_mode = False

        if self.usd_context.get_stage():
            await omni.usd.get_context().close_stage_async()

    def check_prim_spec_regular_fields(
        self, prim_spec_item, name, path, type_name="",
        specifier=PrimSpecSpecifier.DEF_ONLY, children=[],
        has_missing_reference=False, instanceable=False,
        filtered=False, has_children=False
    ):
        self.assertEqual(prim_spec_item.name, name)
        self.assertEqual(prim_spec_item.path, path)
        self.assertEqual(prim_spec_item.type_name, type_name)
        self.assertEqual(prim_spec_item.specifier, specifier)
        prim_spec_paths = self.get_all_prim_spec_paths(prim_spec_item)
        paths = set([])
        for path in children:
            paths.add(Sdf.Path(path))
        prim_spec_paths.discard(prim_spec_item.path)
        self.assertEqual(prim_spec_paths, paths)
        self.assertEqual(prim_spec_item.has_missing_reference, has_missing_reference)
        self.assertEqual(prim_spec_item.instanceable, instanceable)
        self.assertEqual(prim_spec_item.filtered, filtered)
        self.assertEqual(prim_spec_item.has_children, has_children)

    def check_layer_regular_fields(
        self, layer_item, name, identifier, missing=False, is_edit_target=False,
        reserved=False, read_only=False, sublayer_list=[], muted=False,
        muted_or_parent_muted=False, from_session_layer=False,
        dirty=False, anonymous=False, filtered=False,
        prim_spec_list=[], parent=None
    ):
        self.assertEqual(layer_item.name, name)
        self.assertEqual(layer_item.identifier, identifier)
        self.assertEqual(layer_item.missing, missing)
        self.assertEqual(layer_item.is_edit_target, is_edit_target)
        self.assertEqual(layer_item.reserved, reserved)
        self.assertEqual(layer_item.read_only_on_disk, read_only)
        self.assertEqual(layer_item.from_session_layer, from_session_layer)
        self.assertEqual(layer_item.muted, muted)
        self.assertEqual(layer_item.editable, not muted and not layer_item.read_only_on_disk and not layer_item.locked)
        if not anonymous:
            self.assertEqual(layer_item.dirty, dirty)
        self.assertEqual(layer_item.anonymous, anonymous)
        self.assertEqual(layer_item.filtered, filtered)
        self.assertEqual(layer_item.muted_or_parent_muted, muted_or_parent_muted)
        self.assertEqual(layer_item.parent, parent)

        paths = self.get_all_sublayer_identifiers(layer_item)
        self.assertEqual(paths, sublayer_list)

        prim_spec_paths = self.get_all_prim_spec_paths(layer_item.absolute_root_spec)
        expected_paths = set(prim_spec_list)
        self.assertEqual(prim_spec_paths, expected_paths)

    def create_flat_sublayers(self, root_layer, num):
        sublayers = []
        identifiers = []
        for i in range(num):
            layer = LayerUtils.create_sublayer(root_layer, i, "")
            sublayers.append(layer)
            identifiers.append(layer.identifier)

        return sublayers, identifiers

    def create_flat_prim_specs(self, stage, parent_path, num):
        prim_spec_paths = set([])
        for i in range(num):
            prim = stage.DefinePrim(parent_path.AppendElementString(f"xform{i}"), "Xform")
            translation = Gf.Vec3d(-200, 0.0, 0.0)
            common_api = UsdGeom.XformCommonAPI(prim)
            common_api.SetTranslate(translation)
            prim_spec_paths.add(prim.GetPath())

        return prim_spec_paths

    def get_all_prim_spec_items(self, prim_spec_item):
        prim_specs = set([])

        q = [prim_spec_item]
        if prim_spec_item.path != Sdf.Path.absoluteRootPath:
            prim_specs.add(prim_spec_item)
        while len(q) > 0:
            item = q.pop()
            specs = item.children
            for spec in specs:
                prim_specs.add(spec)
                q.append(spec)

        return prim_specs

    def get_all_prim_spec_paths(self, prim_spec_item):
        specs = self.get_all_prim_spec_items(prim_spec_item)
        paths = [spec.path for spec in specs]

        return set(paths)

    def get_all_sublayer_identifiers(self, layer_item):
        paths = []
        for sublayer in layer_item.sublayers:
            paths.append(sublayer.identifier)

        return paths

    def create_sublayers(self, root_layer, level=[]):
        if not level:
            return {}, {}

        sublayers, identifiers = self.create_flat_sublayers(root_layer, level[0])
        sublayers_map = {}
        identifiers_map = {}
        sublayers_map[root_layer.identifier] = sublayers
        identifiers_map[root_layer.identifier] = identifiers

        for sublayer in sublayers:
            lm, im = self.create_sublayers(sublayer, level[1:])
            sublayers_map.update(lm)
            identifiers_map.update(im)

        return sublayers_map, identifiers_map

    def create_prim_specs(self, stage, parent_prim_path, level=[]):
        if not level:
            return set([])

        prim_spec_paths = self.create_flat_prim_specs(stage, parent_prim_path, level[0])

        all_child_spec_paths = set([])
        for prim_spec_path in prim_spec_paths:
            all_child_spec_paths.update(self.create_prim_specs(stage, prim_spec_path, level[1:]))

        prim_spec_paths.update(all_child_spec_paths)

        return prim_spec_paths

    def check_sublayer_tree(self, layer_item, identifiers_map):
        layer_identifiers = identifiers_map.get(layer_item.identifier, [])
        sublayer_paths = self.get_all_sublayer_identifiers(layer_item)
        self.assertEqual(
            sublayer_paths, layer_identifiers,
            f"{layer_item.identifier}'s sublayers does not match"
        )

        for sublayer_item in layer_item.sublayers:
            self.check_sublayer_tree(sublayer_item, identifiers_map)

    def check_prim_spec_children(self, prim_spec_item: PrimSpecItem, expected_children_prim_paths):
        paths = set({})
        for child in prim_spec_item.children:
            paths.add(child.path)

        self.assertEqual(paths, set(expected_children_prim_paths))

    def check_prim_spec_tree(self, prim_spec_item, expected_prim_paths):
        paths = self.get_all_prim_spec_paths(prim_spec_item)
        self.assertEqual(paths, expected_prim_paths)

    async def prepare_empty_stage(self):
        root_layer = Sdf.Layer.CreateAnonymous("__root__")
        stage = Usd.Stage.Open(root_layer)
        await self.usd_context.attach_stage_async(stage)
        await self.app.next_update_async()
        await self.app.next_update_async()
        await self.app.next_update_async()
        return stage
