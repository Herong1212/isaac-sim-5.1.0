r"""
  _____   ______  _____   _____   ______  _____         _______  ______  _____
 |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
 | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
 | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
 | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
 |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/

 OgnWritePrims is deprecated. Use WritePrimsV2 instead.

 Unit tests for the OgnWritePrims (Legacy) node, kept for maintaining backward compatibility.

 For updated tests for OgnWritePrimsV2, find test_write_prims_node.py.

"""

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.commands
import omni.kit.test
import omni.timeline
import omni.usd
from pxr import Usd, UsdGeom
from usdrt import Usd as UsdRT


# ======================================================================
class TestLegacyWritePrimNodes(ogts.OmniGraphTestCase):
    TEST_GRAPH_PATH = "/World/TestGraph"

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_mpib(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims MPiB without bundle modification"""
        usd_context = omni.usd.get_context()
        stage: Usd.Stage = usd_context.get_stage()
        stage_rt = UsdRT.Stage.Attach(usd_context.get_stage_id())

        controller = og.Controller()
        keys = og.Controller.Keys

        cube1_prim = ogts.create_cube(stage, "Cube1", (1, 0, 0))
        cube2_prim = ogts.create_cube(stage, "Cube2", (0, 1, 0))

        (graph, [read_prims_node, _], _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrims"),
                    ("Write", "omni.graph.nodes.WritePrims"),
                ],
                keys.CONNECT: [
                    ("Read.outputs_primsBundle", "Write.inputs:primsBundle"),
                ],
            },
        )

        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Read.inputs:prims"),
            target=cube1_prim.GetPath(),
        )
        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Read.inputs:prims"),
            target=cube2_prim.GetPath(),
        )

        await self._evaluate_graph(graph, controller)
        self._assert_no_compute_messages(graph)

        # Reading the prim into a bundle again must leave the attributes intact, as we didn't modify anything
        await self._evaluate_graph(graph, controller)
        self._assert_no_compute_messages(graph)

        graph_context = graph.get_default_graph_context()

        output_prims_bundle = graph_context.get_output_bundle(read_prims_node, "outputs_primsBundle")
        self.assertTrue(output_prims_bundle.valid)

        child_bundles = output_prims_bundle.get_child_bundles()
        self.assertEqual(len(child_bundles), 2)

        expected_colors = {
            "/Cube1": [[1.0, 0.0, 0.0]],
            "/Cube2": [[0.0, 1.0, 0.0]],
        }

        for bundle in child_bundles:
            path = bundle.get_attribute_by_name("sourcePrimPath").get()

            expected_color = expected_colors[path]
            self.assertNotEqual(expected_color, None)

            # Check bundle values
            self.assertListEqual(bundle.get_attribute_by_name("primvars:displayColor").get().tolist(), expected_color)

            # Check USD prim values
            prim = stage.GetPrimAtPath(path)
            self.assertEqual([rgb[:] for rgb in prim.GetAttribute("primvars:displayColor").Get()], expected_color)

            # Check Fabric prim values
            prim_rt = stage_rt.GetPrimAtPath(path)
            self.assertEqual([rgb[:] for rgb in prim_rt.GetAttribute("primvars:displayColor").Get()], expected_color)

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_spib(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims SPiB without bundle modification"""
        usd_context = omni.usd.get_context()
        stage: Usd.Stage = usd_context.get_stage()
        stage_rt = UsdRT.Stage.Attach(usd_context.get_stage_id())

        controller = og.Controller()
        keys = og.Controller.Keys

        cube1_prim = ogts.create_cube(stage, "Cube1", (1, 0, 0))

        (graph, [read_prims_node, _, _], _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrims"),
                    ("ExtractCube1", "omni.graph.nodes.ExtractPrim"),
                    ("Write", "omni.graph.nodes.WritePrims"),
                ],
                keys.SET_VALUES: [
                    ("ExtractCube1.inputs:primPath", "/Cube1"),
                ],
                keys.CONNECT: [
                    ("Read.outputs_primsBundle", "ExtractCube1.inputs:prims"),
                    ("ExtractCube1.outputs_primBundle", "Write.inputs:primsBundle"),
                ],
            },
        )

        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Read.inputs:prims"),
            target=cube1_prim.GetPath(),
        )

        await self._evaluate_graph(graph, controller)
        self._assert_no_compute_messages(graph)

        # Reading the prim into a bundle again must leave the attributes intact, as we didn't modify anything
        await self._evaluate_graph(graph, controller)
        self._assert_no_compute_messages(graph)

        graph_context = graph.get_default_graph_context()

        output_prims_bundle = graph_context.get_output_bundle(read_prims_node, "outputs_primsBundle")
        self.assertTrue(output_prims_bundle.valid)

        child_bundles = output_prims_bundle.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        expected_colors = {
            "/Cube1": [[1.0, 0.0, 0.0]],
        }

        for bundle in child_bundles:
            path = bundle.get_attribute_by_name("sourcePrimPath").get()

            expected_color = expected_colors[path]
            self.assertNotEqual(expected_color, None)

            # Check bundle values
            self.assertListEqual(bundle.get_attribute_by_name("primvars:displayColor").get().tolist(), expected_color)

            # Check USD prim values
            prim = stage.GetPrimAtPath(path)
            self.assertEqual([rgb[:] for rgb in prim.GetAttribute("primvars:displayColor").Get()], expected_color)

            # Check Fabric prim values
            prim_rt = stage_rt.GetPrimAtPath(path)
            self.assertEqual([rgb[:] for rgb in prim_rt.GetAttribute("primvars:displayColor").Get()], expected_color)

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_int_to_fabric(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims for an integer attribute, Fabric only"""
        await self._read_write_prims_int(False)

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_int_to_usd(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims for an integer attribute, writing back to USD"""
        await self._read_write_prims_int(True)

    # ----------------------------------------------------------------------
    async def _read_write_prims_int(self, usd_write_back: bool):
        usd_context = omni.usd.get_context()
        stage: Usd.Stage = usd_context.get_stage()
        stage_rt = UsdRT.Stage.Attach(usd_context.get_stage_id())

        controller = og.Controller()
        keys = og.Controller.Keys

        cube1_prim = ogts.create_cube(stage, "Cube1", (1, 0, 0))
        cube2_prim = ogts.create_cube(stage, "Cube2", (0, 1, 0))

        (graph, [extract_cube1, extract_cube2, *_], _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("ExtractCube1", "omni.graph.nodes.ExtractPrim"),
                    ("ExtractCube2", "omni.graph.nodes.ExtractPrim"),
                    ("Read", "omni.graph.nodes.ReadPrims"),
                    ("Write", "omni.graph.nodes.WritePrims"),
                    ("SizeCube1", "omni.graph.nodes.ConstantDouble"),
                    ("SizeCube2", "omni.graph.nodes.ConstantDouble"),
                    ("InsertSizeCube1", "omni.graph.nodes.InsertAttribute"),
                    ("InsertSizeCube2", "omni.graph.nodes.InsertAttribute"),
                ],
                keys.SET_VALUES: [
                    ("ExtractCube1.inputs:primPath", "/Cube1"),
                    ("ExtractCube2.inputs:primPath", "/Cube2"),
                    ("SizeCube1.inputs:value", 200),
                    ("SizeCube2.inputs:value", 300),
                    ("InsertSizeCube1.inputs:outputAttrName", "size"),
                    ("InsertSizeCube2.inputs:outputAttrName", "size"),
                    ("Write.inputs:usdWriteBack", usd_write_back),
                ],
                keys.CONNECT: [
                    ("Read.outputs_primsBundle", "ExtractCube1.inputs:prims"),
                    ("Read.outputs_primsBundle", "ExtractCube2.inputs:prims"),
                    ("SizeCube1.inputs:value", "InsertSizeCube1.inputs:attrToInsert"),
                    ("SizeCube2.inputs:value", "InsertSizeCube2.inputs:attrToInsert"),
                    ("ExtractCube1.outputs_primBundle", "InsertSizeCube1.inputs:data"),
                    ("ExtractCube2.outputs_primBundle", "InsertSizeCube2.inputs:data"),
                    ("InsertSizeCube1.outputs_data", "Write.inputs:primsBundle"),
                    ("InsertSizeCube2.outputs_data", "Write.inputs:primsBundle"),
                ],
            },
        )

        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Read.inputs:prims"),
            target=cube1_prim.GetPath(),
        )
        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Read.inputs:prims"),
            target=cube2_prim.GetPath(),
        )

        await self._evaluate_graph(graph, controller)
        self._assert_no_compute_messages(graph)

        graph_context = graph.get_default_graph_context()

        # Because we have feedback, the extract_cube1 bundle should have picked up the written attributes.
        # TODO: Feedback will become optional one day!
        cube1_bundle = graph_context.get_output_bundle(extract_cube1, "outputs_primBundle")
        self.assertTrue(cube1_bundle.valid)
        self.assertEqual(cube1_bundle.get_attribute_by_name("size").get(), 200)

        # Because we have feedback, the extract_cube2 bundle should have picked up the written attributes.
        # TODO: Feedback will become optional one day!
        cube2_bundle = graph_context.get_output_bundle(extract_cube2, "outputs_primBundle")
        self.assertTrue(cube2_bundle.valid)
        self.assertEqual(cube2_bundle.get_attribute_by_name("size").get(), 300)

        # Check USD write-back
        self.assertEqual(cube1_prim.GetAttribute("size").Get(), 200 if usd_write_back else 1)
        self.assertEqual(cube2_prim.GetAttribute("size").Get(), 300 if usd_write_back else 1)

        # Check Fabric values
        self.assertEqual(stage_rt.GetPrimAtPath("/Cube1").GetAttribute("size").Get(), 200)
        self.assertEqual(stage_rt.GetPrimAtPath("/Cube2").GetAttribute("size").Get(), 300)

        # Make sure the prim-bundle internal attributes are not written to the USD prim
        for attr_name in ["sourcePrimPath", "sourcePrimType"]:
            self.assertEqual(cube1_prim.HasAttribute(attr_name), False)
            self.assertEqual(cube2_prim.HasAttribute(attr_name), False)

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_translate_only(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims using an attribute pattern to just translate"""
        await self._test_read_write_prims_patterns(
            "xformOp:trans*",
            None,
            None,
            [
                [(1.0, 2.0, 3.0), (0.0, 0.0, 0.0)],
                [(4.0, 5.0, 6.0), (0.0, 0.0, 0.0)],
            ],
        )

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_rotate_only(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims using an attribute pattern to just rotate"""
        await self._test_read_write_prims_patterns(
            "xformOp:rotate*",
            None,
            None,
            [
                [(0.0, 0.0, 0.0), (7.0, 8.0, 9.0)],
                [(0.0, 0.0, 0.0), (10.0, 11.0, 12.0)],
            ],
        )

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_xform_only(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims using an attribute pattern to translate and rotate"""
        await self._test_read_write_prims_patterns(
            "xformOp:*",
            None,
            None,
            [
                [(1.0, 2.0, 3.0), (7.0, 8.0, 9.0)],
                [(4.0, 5.0, 6.0), (10.0, 11.0, 12.0)],
            ],
        )

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_shape1_only(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims using an path pattern to limit writing to Shape1 only"""
        await self._test_read_write_prims_patterns(
            None,
            "/Shape1",
            None,
            [
                [(1.0, 2.0, 3.0), (7.0, 8.0, 9.0)],
                [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
            ],
        )

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_shape2_only(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims using an path pattern to limit writing to Shape2 only"""
        await self._test_read_write_prims_patterns(
            None,
            "/Shape2",
            None,
            [
                [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                [(4.0, 5.0, 6.0), (10.0, 11.0, 12.0)],
            ],
        )

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_both_shapes(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims using an path pattern to write to both shapes"""
        await self._test_read_write_prims_patterns(
            None,
            "/Shape*",
            None,
            [
                [(1.0, 2.0, 3.0), (7.0, 8.0, 9.0)],
                [(4.0, 5.0, 6.0), (10.0, 11.0, 12.0)],
            ],
        )

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_cube_only(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims using an path pattern to limit writing to cubes only"""
        await self._test_read_write_prims_patterns(
            None,
            None,
            "Cube",
            [
                [(1.0, 2.0, 3.0), (7.0, 8.0, 9.0)],
                [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
            ],
        )

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_cone_only(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims using an type pattern to limit writing to cones only"""
        await self._test_read_write_prims_patterns(
            None,
            None,
            "Cone",
            [
                [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
                [(4.0, 5.0, 6.0), (10.0, 11.0, 12.0)],
            ],
        )

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_cube_and_cone(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims using an type pattern to write to both cubes and cones"""
        await self._test_read_write_prims_patterns(
            None,
            None,
            "Cone;Cube",
            [
                [(1.0, 2.0, 3.0), (7.0, 8.0, 9.0)],
                [(4.0, 5.0, 6.0), (10.0, 11.0, 12.0)],
            ],
        )

    # ----------------------------------------------------------------------
    async def _test_read_write_prims_patterns(self, attr_pattern, path_pattern, type_pattern, expected_prim_values):
        # No need to test USD write back in this unit tests, other tests do this.
        usd_write_back = False

        usd_context = omni.usd.get_context()

        stage: Usd.Stage = usd_context.get_stage()
        stage_rt = UsdRT.Stage.Attach(usd_context.get_stage_id())

        controller = og.Controller()
        keys = og.Controller.Keys

        cube_prim = ogts.create_cube(stage, "Shape1", (1, 0, 0))
        cone_prim = ogts.create_cone(stage, "Shape2", (0, 1, 0))

        # add transforms with double precision
        xform_precision = UsdGeom.XformOp.PrecisionDouble
        for prim in [cube_prim, cone_prim]:
            UsdGeom.Xformable(prim).AddTranslateOp(xform_precision).Set((0, 0, 0))
            UsdGeom.Xformable(prim).AddRotateXYZOp(xform_precision).Set((0, 0, 0))
            UsdGeom.Xformable(prim).AddScaleOp(xform_precision).Set((1, 1, 1))

        set_values = [
            ("ExtractCube.inputs:primPath", "/Shape1"),
            ("ExtractCone.inputs:primPath", "/Shape2"),
            ("TranslateCube.inputs:value", (1, 2, 3)),
            ("TranslateCone.inputs:value", (4, 5, 6)),
            ("RotateCube.inputs:value", (7, 8, 9)),
            ("RotateCone.inputs:value", (10, 11, 12)),
            ("InsertTranslateCube.inputs:outputAttrName", "xformOp:translate"),
            ("InsertTranslateCone.inputs:outputAttrName", "xformOp:translate"),
            ("InsertRotateCube.inputs:outputAttrName", "xformOp:rotateXYZ"),
            ("InsertRotateCone.inputs:outputAttrName", "xformOp:rotateXYZ"),
            ("Write.inputs:usdWriteBack", usd_write_back),
        ]

        if attr_pattern:
            set_values.append(("Write.inputs:attrNamesToExport", attr_pattern))

        if path_pattern:
            set_values.append(("Write.inputs:pathPattern", path_pattern))

        if type_pattern:
            set_values.append(("Write.inputs:typePattern", type_pattern))

        (graph, [extract_cube, extract_cone, *_], _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("ExtractCube", "omni.graph.nodes.ExtractPrim"),
                    ("ExtractCone", "omni.graph.nodes.ExtractPrim"),
                    ("Read", "omni.graph.nodes.ReadPrims"),
                    ("Write", "omni.graph.nodes.WritePrims"),
                    ("TranslateCube", "omni.graph.nodes.ConstantDouble3"),
                    ("TranslateCone", "omni.graph.nodes.ConstantDouble3"),
                    ("RotateCube", "omni.graph.nodes.ConstantDouble3"),
                    ("RotateCone", "omni.graph.nodes.ConstantDouble3"),
                    ("InsertTranslateCube", "omni.graph.nodes.InsertAttribute"),
                    ("InsertTranslateCone", "omni.graph.nodes.InsertAttribute"),
                    ("InsertRotateCube", "omni.graph.nodes.InsertAttribute"),
                    ("InsertRotateCone", "omni.graph.nodes.InsertAttribute"),
                ],
                keys.CONNECT: [
                    ("Read.outputs_primsBundle", "ExtractCube.inputs:prims"),
                    ("Read.outputs_primsBundle", "ExtractCone.inputs:prims"),
                    ("TranslateCube.inputs:value", "InsertTranslateCube.inputs:attrToInsert"),
                    ("TranslateCone.inputs:value", "InsertTranslateCone.inputs:attrToInsert"),
                    ("RotateCube.inputs:value", "InsertRotateCube.inputs:attrToInsert"),
                    ("RotateCone.inputs:value", "InsertRotateCone.inputs:attrToInsert"),
                    ("ExtractCube.outputs_primBundle", "InsertTranslateCube.inputs:data"),
                    ("ExtractCone.outputs_primBundle", "InsertTranslateCone.inputs:data"),
                    ("InsertTranslateCube.outputs_data", "InsertRotateCube.inputs:data"),
                    ("InsertTranslateCone.outputs_data", "InsertRotateCone.inputs:data"),
                    ("InsertRotateCube.outputs_data", "Write.inputs:primsBundle"),
                    ("InsertRotateCone.outputs_data", "Write.inputs:primsBundle"),
                ],
                keys.SET_VALUES: set_values,
            },
        )

        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Read.inputs:prims"),
            target=cube_prim.GetPath(),
        )
        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Read.inputs:prims"),
            target=cone_prim.GetPath(),
        )

        await self._evaluate_graph(graph, controller)
        self._assert_no_compute_messages(graph)

        graph_context = graph.get_default_graph_context()

        cube_bundle = graph_context.get_output_bundle(extract_cube, "outputs_primBundle")
        cone_bundle = graph_context.get_output_bundle(extract_cone, "outputs_primBundle")

        prim_bundles = [cube_bundle, cone_bundle]
        prim_paths = ["/Shape1", "/Shape2"]

        # We will check these attributes
        attr_names = ["xformOp:translate", "xformOp:rotateXYZ"]

        # We need two lists of values, one for each prim
        self.assertEqual(len(expected_prim_values), 2)

        for prim_index, prim_bundle in enumerate(prim_bundles):
            expected_values = expected_prim_values[prim_index]

            # All attribute values must be passed
            self.assertEqual(len(expected_values), len(attr_names))

            prim_rt = stage_rt.GetPrimAtPath(prim_paths[prim_index])

            # Check attributes values in prim bundle
            for attr_index, expected_value in enumerate(expected_values):
                attr_name = attr_names[attr_index]
                # Because we have feedback, the bundle should have picked up the written attributes.
                # TODO: Feedback will become optional one day!
                actual_value = tuple(prim_bundle.get_attribute_by_name(attr_name).get())
                self.assertEqual(actual_value, expected_value)
                # Check Fabric values
                actual_value_rt = tuple(prim_rt.GetAttribute(attr_name).Get())
                self.assertEqual(actual_value_rt, expected_value)

        # Make sure the prim-bundle internal attributes are not written to the USD prim
        for attr_name in ["sourcePrimPath", "sourcePrimType"]:
            self.assertEqual(cube_prim.HasAttribute(attr_name), False)
            self.assertEqual(cone_prim.HasAttribute(attr_name), False)

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_array_new_attr_to_fabric(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims for a new array attribute, Fabric only"""
        await self._test_read_write_prims_vec3_array(False, False)

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_array_new_attr_to_usd(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims for a new array attribute, writing back to USD"""
        await self._test_read_write_prims_vec3_array(True, False)

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_array_attr_to_fabric(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims for an existing array attribute, Fabric only"""
        await self._test_read_write_prims_vec3_array(False, True)

    # ----------------------------------------------------------------------
    async def test_legacy_read_write_prims_array_attr_to_usd(self):
        """Test omni.graph.nodes.ReadPrims and WritePrims for an existing array attribute, writing back to USD"""
        await self._test_read_write_prims_vec3_array(True, True)

    # ----------------------------------------------------------------------
    async def _test_read_write_prims_vec3_array(self, usd_write_back: bool, add_new_attr: bool):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        stage_rt = UsdRT.Stage.Attach(usd_context.get_stage_id())

        cube_prim = ogts.create_cube(stage, "Cube", (1, 0, 0))

        controller = og.Controller()
        keys = og.Controller.Keys

        attr_name = "new_array_attr" if add_new_attr else "primvars:displayColor"

        (graph, nodes, _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrims"),
                    ("Write", "omni.graph.nodes.WritePrims"),
                    ("ExtractCube", "omni.graph.nodes.ExtractPrim"),
                    ("MakeArray", "omni.graph.nodes.ConstructArray"),
                    ("InsertAttribute", "omni.graph.nodes.InsertAttribute"),
                ],
                keys.SET_VALUES: [
                    ("ExtractCube.inputs:primPath", "/Cube"),
                    ("MakeArray.inputs:arraySize", 1),
                    ("MakeArray.inputs:arrayType", "float[3][]"),
                    ("MakeArray.inputs:input0", [0.25, 0.50, 0.75]),
                    ("InsertAttribute.inputs:outputAttrName", attr_name),
                    ("Write.inputs:usdWriteBack", usd_write_back),
                ],
                keys.CONNECT: [
                    ("Read.outputs_primsBundle", "ExtractCube.inputs:prims"),
                    ("ExtractCube.outputs_primBundle", "InsertAttribute.inputs:data"),
                    ("MakeArray.outputs:array", "InsertAttribute.inputs:attrToInsert"),
                    ("InsertAttribute.outputs_data", "Write.inputs:primsBundle"),
                ],
            },
        )

        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Read.inputs:prims"),
            target=cube_prim.GetPath(),
        )

        await self._evaluate_graph(graph, controller)
        self._assert_no_compute_messages(graph)

        graph_context = graph.get_default_graph_context()

        cube_bundle = graph_context.get_output_bundle(nodes[2], "outputs_primBundle")
        self.assertTrue(cube_bundle.valid)

        # Because we have feedback, the bundle should have picked up the written attributes.
        # TODO: Feedback will become optional one day!
        feedback_values = cube_bundle.get_attribute_by_name(attr_name).get()
        self.assertEqual(len(feedback_values), 1)
        self.assertEqual(tuple(feedback_values[0]), (0.25, 0.50, 0.75))

        # Check Fabric values
        fabric_values = stage_rt.GetPrimAtPath("/Cube").GetAttribute(attr_name).Get()
        self.assertEqual(len(fabric_values), 1)
        self.assertEqual(tuple(fabric_values[0]), (0.25, 0.50, 0.75))

        if usd_write_back:
            # With USD write back, the existing attribute should be updated in USD
            usd_values = stage.GetPrimAtPath("/Cube").GetAttribute(attr_name).Get()
            self.assertEqual(len(usd_values), 1)
            self.assertEqual(tuple(usd_values[0]), (0.25, 0.50, 0.75))
        elif add_new_attr:
            # Without USD write back, the new attribute should not exist in USD.
            self.assertFalse(stage.GetPrimAtPath("/Cube").HasAttribute(attr_name))
        else:
            # Without USD write back, the existing attribute should not be updated in USD
            usd_values = stage.GetPrimAtPath("/Cube").GetAttribute(attr_name).Get()
            self.assertEqual(len(usd_values), 1)
            self.assertEqual(tuple(usd_values[0]), (1, 0, 0))

    # ----------------------------------------------------------------------
    # Helpers
    def _assert_no_compute_messages(self, graph):
        graph_nodes = graph.get_nodes()
        for severity in [og.WARNING, og.ERROR]:
            for node in graph_nodes:
                self.assertEqual(node.get_compute_messages(severity), [])

    async def _evaluate_graph(self, graph, controller):
        await omni.kit.app.get_app().next_update_async()
        await controller.evaluate(graph)
