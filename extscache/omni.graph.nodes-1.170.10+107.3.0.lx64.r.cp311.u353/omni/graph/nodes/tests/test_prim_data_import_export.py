import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.app
import omni.kit.stage_template.core
import omni.kit.test
from pxr import UsdGeom


class TestPrimDataImportExport(ogts.OmniGraphTestCase):
    """Run a unit test to validate data flow through bundles."""

    TEST_GRAPH_PATH = "/TestGraph"

    TRANSLATE = (10.0, 20.0, 30.0)
    ROTATE = (90.0, 180.0, 270.0)
    SCALE = (400.0, 500.0, 600.0)

    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()

        self.controller = og.Controller()

        # Create ImportUSDPrim and ExportUSDPrim and connect them together.
        (
            self.graph,
            (self.importNode, self.exportNode),
            _,
            _,
        ) = self.controller.edit(
            self.TEST_GRAPH_PATH,
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("import_usd_prim_data", "omni.graph.ImportUSDPrim"),
                    ("export_usd_prim_data", "omni.graph.ExportUSDPrim"),
                ],
                og.Controller.Keys.CONNECT: [
                    (
                        "import_usd_prim_data.outputs_output",
                        "export_usd_prim_data.inputs:bundle",
                    )
                ],
            },
        )

        self.context = self.graph.get_default_graph_context()
        stage = omni.usd.get_context().get_stage()

        # Create two Xform nodes, one as input, the other as output.
        self.input_prim = og.Controller.create_prim("/World/input_prim", {}, "Xform")
        self.output_prim = og.Controller.create_prim("/World/output_prim", {}, "Xform")
        self.assertTrue(self.input_prim.IsValid())
        self.assertTrue(self.output_prim.IsValid())

        input_xform = UsdGeom.Xformable(self.input_prim)
        output_xform = UsdGeom.Xformable(self.output_prim)

        if not self.input_prim.HasAttribute("xformOp:translate"):
            input_xform.AddTranslateOp()
        if not self.input_prim.HasAttribute("xformOp:rotateXYZ"):
            input_xform.AddRotateXYZOp()
        if not self.input_prim.HasAttribute("xformOp:scale"):
            input_xform.AddScaleOp()

        if not self.output_prim.HasAttribute("xformOp:translate"):
            output_xform.AddTranslateOp()
        if not self.output_prim.HasAttribute("xformOp:rotateXYZ"):
            output_xform.AddRotateXYZOp()
        if not self.output_prim.HasAttribute("xformOp:scale"):
            output_xform.AddScaleOp()

        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(self.TEST_GRAPH_PATH + "/import_usd_prim_data.inputs:prim"),
            target=self.input_prim.GetPath(),
        )

        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(self.TEST_GRAPH_PATH + "/export_usd_prim_data.outputs:prim"),
            target=self.output_prim.GetPath(),
        )

    async def tearDown(self):
        """Tear down the test environment"""
        # let go of any previous references
        self.graph = None
        self.importNode = None
        self.exportNode = None
        self.controller = None
        self.context = None
        self.input_prim = None
        self.output_prim = None

        # clear the stage to workaround a shutdown issue
        await omni.kit.stage_template.core.new_stage_async()
        await super().tearDown()

    async def test_set_attributes(self):
        """Test whether attribute value changes of the input prim will be synced to the output prim."""

        # Assign new TRS values to the input prim.
        self.input_prim.GetAttribute("xformOp:translate").Set(self.TRANSLATE)
        self.input_prim.GetAttribute("xformOp:rotateXYZ").Set(self.ROTATE)
        self.input_prim.GetAttribute("xformOp:scale").Set(self.SCALE)

        # Before graph evaluation, the output prim is still with its default attribute values.
        self.assertFalse(self.output_prim.GetAttribute("xformOp:translate").Get() == self.TRANSLATE)
        self.assertFalse(self.output_prim.GetAttribute("xformOp:rotateXYZ").Get() == self.ROTATE)
        self.assertFalse(self.output_prim.GetAttribute("xformOp:scale").Get() == self.SCALE)

        # Trigger graph evaluation and wait for completion.
        await og.Controller.evaluate(self.graph)

        # After graph evaluation, the output prim has been fed with data from the input prim.
        self.assertTrue(self.output_prim.GetAttribute("xformOp:translate").Get() == self.TRANSLATE)
        self.assertTrue(self.output_prim.GetAttribute("xformOp:rotateXYZ").Get() == self.ROTATE)
        self.assertTrue(self.output_prim.GetAttribute("xformOp:scale").Get() == self.SCALE)

    async def test_bundle_attributes_and_metadata(self):
        """Test bundle attributes and metadata"""

        # Get the bundle from the import node.
        bundle = self.context.get_output_bundle(self.importNode, "outputs_output")
        self.assertTrue(bundle.is_valid())

        # Attribute names and types before evaluation.
        attr_names = bundle.get_attribute_names()
        attr_types = bundle.get_attribute_types()
        self.assertTrue(len(attr_names) == 0)
        self.assertTrue(len(attr_types) == 0)

        # Assign new TRS values to the input prim.
        self.input_prim.GetAttribute("xformOp:translate").Set(self.TRANSLATE)
        self.input_prim.GetAttribute("xformOp:rotateXYZ").Set(self.ROTATE)
        self.input_prim.GetAttribute("xformOp:scale").Set(self.SCALE)

        # Trigger graph evaluation and wait for completion.
        await og.Controller.evaluate(self.graph)

        # Attribute names and types after evaluation.
        attr_names = bundle.get_attribute_names()
        attr_types = bundle.get_attribute_types()
        self.assertTrue(len(attr_names) != 0)
        self.assertTrue(len(attr_types) != 0)

        # Internal attributes shouldn't be exposed.
        metadata_names = {
            "interpolation",
            "source",
            "bundlePrimIndexOffset",
        }
        self.assertTrue(metadata_names.isdisjoint(set(attr_names)))

        # Test metadata names.
        self.assertEqual(
            set(bundle.get_bundle_metadata_names()),
            {"bundlePrimIndexOffset"},
        )

    async def test_bundle_dirty_id(self):
        """Test whether bundleDirtyID bumps after graph evaluation."""

        # Get the output bundle from the importer and convert to IBundle2.
        output_bundle = self.context.get_output_bundle(self.importNode, "outputs_output")

        # Get the input bundle from the exporter and convert to IBundle2.
        input_bundle = self.context.get_input_bundle(self.exportNode, "inputs:bundle")

        # Trigger graph evaluation and wait for completion.
        await og.Controller.evaluate(self.graph)

        dirty_id = og._og_unstable.IDirtyID2.create(self.context)  # noqa: PLW0212

        # Get dirty id.
        output_dirty_id = dirty_id.get([output_bundle])[0]
        input_dirty_id = dirty_id.get([input_bundle])[0]

        # Trigger graph evaluation and wait for completion.
        await og.Controller.evaluate(self.graph)

        # The dirty id doesn't bump because nothing gets changed.
        self.assertEqual(output_dirty_id, dirty_id.get([output_bundle])[0])
        self.assertEqual(input_dirty_id, dirty_id.get([input_bundle])[0])

        # Assign new TRS values to the input prim.
        self.input_prim.GetAttribute("xformOp:translate").Set(self.TRANSLATE)
        self.input_prim.GetAttribute("xformOp:rotateXYZ").Set(self.ROTATE)
        self.input_prim.GetAttribute("xformOp:scale").Set(self.SCALE)

        # Trigger graph evaluation and wait for completion.
        await og.Controller.evaluate(self.graph)

        # The dirty id bumps because of TRS value changes.
        self.assertNotEqual(output_dirty_id, dirty_id.get([output_bundle])[0])
        self.assertNotEqual(input_dirty_id, dirty_id.get([input_bundle])[0])

    async def test_child_bundle_order(self):
        """Test whether the order of child bundles extracted from the output bundle is consistent with that of target prims."""
        graph_path = "/TestGraph2"
        cubes = [("/cube_1", 1.0), ("/cube_2", 2.0), ("/cube_3", 3.0), ("/cube_4", 4.0)]
        attr_name = "size"

        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (_, output_node),
            _,
            _,
        ) = controller.edit(
            graph_path,
            {
                keys.CREATE_NODES: [
                    ("import_usd_prim_data", "omni.graph.ImportUSDPrim"),
                    ("bundle_to_usda_text", "omni.graph.BundleToUSDA"),
                ],
                keys.CONNECT: [
                    ("import_usd_prim_data.outputs_output", "bundle_to_usda_text.inputs:bundle"),
                ],
                keys.SET_VALUES: ("import_usd_prim_data.inputs:attrNamesToImport", attr_name),
            },
        )

        # Create target prims and assign the size attribute with different values.
        for cube_path, cube_size in cubes:
            prim = og.Controller.create_prim(cube_path, {}, "Cube")
            prim.GetAttribute(attr_name).Set(cube_size)

        # Assign the target prims to the import node.
        stage = omni.usd.get_context().get_stage()
        omni.kit.commands.execute(
            "SetRelationshipTargets",
            relationship=stage.GetPropertyAtPath(graph_path + "/import_usd_prim_data.inputs:prim"),
            targets=[cube_path for cube_path, _ in cubes],
        )

        await og.Controller.evaluate(graph)

        expected_result = (
            'def Cube "cube_1"\n'
            "{\n"
            "    double size = 1.00000000000000000e+00\n"
            '    token sourcePrimPath = "/cube_1"\n'
            '    token sourcePrimType = "Cube"\n'
            "}\n"
            'def Cube "cube_2"\n'
            "{\n"
            "    double size = 2.00000000000000000e+00\n"
            '    token sourcePrimPath = "/cube_2"\n'
            '    token sourcePrimType = "Cube"\n'
            "}\n"
            'def Cube "cube_3"\n'
            "{\n"
            "    double size = 3.00000000000000000e+00\n"
            '    token sourcePrimPath = "/cube_3"\n'
            '    token sourcePrimType = "Cube"\n'
            "}\n"
            'def Cube "cube_4"\n'
            "{\n"
            "    double size = 4.00000000000000000e+00\n"
            '    token sourcePrimPath = "/cube_4"\n'
            '    token sourcePrimType = "Cube"\n'
            "}\n"
        )

        # Change timecode to trigger recompute. Run 60 times to eliminate random factor.
        for timecode in range(60):
            self.controller.edit(
                self.TEST_GRAPH_PATH,
                {og.Controller.Keys.SET_VALUES: ("import_usd_prim_data.inputs:usdTimecode", timecode)},
            )
            await og.Controller.evaluate(self.graph)

            output_attr = output_node.get_attribute("outputs:text")
            self.assertTrue(output_attr is not None and output_attr.is_valid())
            self.assertEqual(output_attr.get(), expected_result)

    async def test_nodes_emit_deprecation_warning(self):
        """Validate deprecated nodes emit the proper warning"""

        await og.Controller.evaluate(self.graph)
        self.assertTrue(any("deprecated" in x for x in self.importNode.get_compute_messages(og.Severity.WARNING)))
        self.assertTrue(any("deprecated" in x for x in self.exportNode.get_compute_messages(og.Severity.WARNING)))
