# noqa: PLC0302
"""Misc collection of tests for nodes in this extension"""

import math
import os
from functools import partial
from math import isnan
from typing import Callable, Set

import carb
import carb.settings
import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.commands
import omni.kit.test
import omni.timeline
import omni.usd
import OmniGraphSchemaTools
import usdrt
from omni.graph.core import ThreadsafetyTestUtils
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade


# ======================================================================
class TestNodes(ogts.OmniGraphTestCase):
    """Unit tests nodes in this extension"""

    PERSISTENT_SETTINGS_PREFIX = "/persistent"
    TEST_GRAPH_PATH = "/World/TestGraph"

    def val_compare(self, og_value, py_value):
        """Helper assert method to handle numpy/tuples/lists"""
        test_expected = list(py_value) if isinstance(py_value, tuple) else py_value
        if isinstance(test_expected, list):
            self.assertListEqual(list(og_value), test_expected)
        else:
            self.assertEqual(og_value, test_expected)

    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()

        # Ensure that Xform prims are created with the full set of xformOp attributes with consistent behavior.
        settings = carb.settings.get_settings()
        settings.set(self.PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/PrimCreationWithDefaultXformOps", True)
        settings.set(
            self.PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpType", "Scale, Rotate, Translate"
        )
        settings.set(self.PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultRotationOrder", "XYZ")
        settings.set(
            self.PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpOrder",
            "xformOp:translate, xformOp:rotate, xformOp:scale",
        )
        settings.set(self.PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpPrecision", "Double")

    # ----------------------------------------------------------------------
    async def test_getprimrelationship(self):
        """Test GetPrimRelationship node"""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        controller = og.Controller()
        keys = og.Controller.Keys
        (graph, (get_node,), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: ("Get", "omni.graph.nodes.GetPrimRelationship"),
                keys.CREATE_PRIMS: [("RelHolder", {}), ("TestPrimA", {}), ("TestPrimB", {})],
                keys.SET_VALUES: [("Get.inputs:name", "test_rel"), ("Get.inputs:usePath", False)],
            },
        )
        await controller.evaluate(graph)
        prim = stage.GetPrimAtPath("/RelHolder")
        rel = prim.CreateRelationship("test_rel")
        for prim_path in ("/TestPrimA", "/TestPrimB"):
            omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=Sdf.Path(prim_path))

        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Get.inputs:prim"),
            target=prim.GetPath(),
        )
        await controller.evaluate(graph)
        rel_paths = og.Controller.get(controller.attribute("outputs:paths", get_node))
        self.assertEqual(rel_paths, rel.GetTargets())

        controller.edit(
            self.TEST_GRAPH_PATH,
            {keys.SET_VALUES: [("Get.inputs:path", "/RelHolder"), ("Get.inputs:usePath", True)]},
        )
        await controller.evaluate(graph)
        rel_paths = og.Controller.get(controller.attribute("outputs:paths", get_node))
        self.assertEqual(rel_paths, rel.GetTargets())

    # ----------------------------------------------------------------------
    @ThreadsafetyTestUtils.make_threading_test
    def test_get_prim_path(self, test_instance_id: int = 0):
        """Test GetPrimPath node"""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        graph_path = self.TEST_GRAPH_PATH + str(test_instance_id)

        prim_path = "/World/TestPrim"
        ThreadsafetyTestUtils.add_to_threading_cache(test_instance_id, stage.DefinePrim(prim_path))

        controller = og.Controller()
        keys = og.Controller.Keys
        (_, (get_node,), _, _) = controller.edit(
            graph_path,
            {keys.CREATE_NODES: ("GetPrimPath", "omni.graph.nodes.GetPrimPath")},
        )

        rel = stage.GetPropertyAtPath(f"{graph_path}/GetPrimPath.inputs:prim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=prim_path)

        yield ThreadsafetyTestUtils.EVALUATION_ALL_GRAPHS
        rel_paths = og.Controller.get(controller.attribute("outputs:primPath", get_node))
        self.assertEqual(rel_paths, prim_path)

        ThreadsafetyTestUtils.single_evaluation_last_test_instance(
            test_instance_id, lambda: stage.RemovePrim(prim_path)
        )

    # ----------------------------------------------------------------------
    @ThreadsafetyTestUtils.make_threading_test
    def test_get_prim_paths(self, test_instance_id: int = 0):
        """Test GetPrimPaths node"""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        graph_path = self.TEST_GRAPH_PATH + str(test_instance_id)

        prim_paths = ["/World/TestPrim1", "/World/TestPrim2"]
        ThreadsafetyTestUtils.add_to_threading_cache(test_instance_id, stage.DefinePrim(prim_paths[0]))
        ThreadsafetyTestUtils.add_to_threading_cache(test_instance_id, stage.DefinePrim(prim_paths[1]))

        controller = og.Controller()
        keys = og.Controller.Keys

        (_, (get_node,), _, _) = controller.edit(
            graph_path,
            {keys.CREATE_NODES: ("GetPrimPaths", "omni.graph.nodes.GetPrimPaths")},
        )

        rel = stage.GetPropertyAtPath(f"{graph_path}/GetPrimPaths.inputs:prims")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=prim_paths[0])
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=prim_paths[1])

        yield ThreadsafetyTestUtils.EVALUATION_ALL_GRAPHS
        rel_paths = og.Controller.get(controller.attribute("outputs:primPaths", get_node))
        self.assertEqual(rel_paths, prim_paths)

        ThreadsafetyTestUtils.single_evaluation_last_test_instance(
            test_instance_id, lambda: stage.RemovePrim(prim_paths[0])
        )
        ThreadsafetyTestUtils.single_evaluation_last_test_instance(
            test_instance_id, lambda: stage.RemovePrim(prim_paths[1])
        )

    # ----------------------------------------------------------------------
    @ThreadsafetyTestUtils.make_threading_test
    def test_get_prims_at_path(self, test_instance_id: int = 0):
        """Test GetPrimAtPath node"""
        graph_path = self.TEST_GRAPH_PATH + str(test_instance_id)

        controller = og.Controller()
        prim_path = "/World/foo/bar"
        keys = og.Controller.Keys
        (_, (get_prim_at_path, get_prims_at_path, _, _), _, _) = controller.edit(
            graph_path,
            {
                keys.CREATE_NODES: [
                    ("GetPrimAtPath", "omni.graph.nodes.GetPrimsAtPath"),
                    ("GetPrimsAtPath", "omni.graph.nodes.GetPrimsAtPath"),
                    ("MakeArray", "omni.graph.nodes.ConstructArray"),
                    ("ConstToken", "omni.graph.nodes.ConstantToken"),
                ],
                keys.CONNECT: [
                    ("ConstToken.inputs:value", "GetPrimAtPath.inputs:path"),
                    ("MakeArray.outputs:array", "GetPrimsAtPath.inputs:path"),
                ],
                keys.SET_VALUES: [
                    ("MakeArray.inputs:arraySize", 3),
                    ("MakeArray.inputs:arrayType", "token[]"),
                    ("MakeArray.inputs:input0", prim_path),
                    ("ConstToken.inputs:value", prim_path),
                ],
            },
        )
        yield ThreadsafetyTestUtils.EVALUATION_ALL_GRAPHS
        out_path = og.Controller.get(controller.attribute("outputs:prims", get_prim_at_path))
        self.assertEqual(out_path, [usdrt.Sdf.Path(prim_path)])
        out_paths = og.Controller.get(controller.attribute("outputs:prims", get_prims_at_path))
        self.assertEqual(out_paths, [usdrt.Sdf.Path(prim_path)] * 3)

    # ----------------------------------------------------------------------
    @ThreadsafetyTestUtils.make_threading_test
    def test_to_target(self, test_instance_id: int = 0):
        """Test ToTarget node"""
        graph_path = self.TEST_GRAPH_PATH + str(test_instance_id)

        controller = og.Controller()
        prim_path = "/World/foo/bar"
        keys = og.Controller.Keys
        (_, (to_target, to_targets, _, _), _, _) = controller.edit(
            graph_path,
            {
                keys.CREATE_NODES: [
                    ("ToTarget", "omni.graph.nodes.ToTarget"),
                    ("ToTargets", "omni.graph.nodes.ToTarget"),
                    ("MakeArray", "omni.graph.nodes.ConstructArray"),
                    ("ConstToken", "omni.graph.nodes.ConstantToken"),
                ],
                keys.CONNECT: [
                    ("ConstToken.inputs:value", "ToTarget.inputs:value"),
                    ("MakeArray.outputs:array", "ToTargets.inputs:value"),
                ],
                keys.SET_VALUES: [
                    ("MakeArray.inputs:arraySize", 3),
                    ("MakeArray.inputs:arrayType", "token[]"),
                    ("MakeArray.inputs:input0", prim_path),
                    ("ConstToken.inputs:value", prim_path),
                ],
            },
        )
        yield ThreadsafetyTestUtils.EVALUATION_ALL_GRAPHS
        out_path = og.Controller.get(controller.attribute("outputs:converted", to_target))
        self.assertEqual(out_path, [usdrt.Sdf.Path(prim_path)])
        out_paths = og.Controller.get(controller.attribute("outputs:converted", to_targets))
        self.assertEqual(out_paths, [usdrt.Sdf.Path(prim_path)] * 3)

    # ----------------------------------------------------------------------
    @ThreadsafetyTestUtils.make_threading_test
    def test_constant_prims(self, test_instance_id: int = 0):
        """Test ConstantPrims node"""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        graph_path = self.TEST_GRAPH_PATH + str(test_instance_id)

        prim_paths = ["/World/TestPrim1", "/World/TestPrim2"]
        for prim_path in prim_paths:
            ThreadsafetyTestUtils.add_to_threading_cache(test_instance_id, stage.DefinePrim(prim_path))

        controller = og.Controller()
        keys = og.Controller.Keys
        (_, (_const_prims, prim_paths_node), _, _) = controller.edit(
            graph_path,
            {
                keys.CREATE_NODES: [
                    ("ConstantPrims", "omni.graph.nodes.ConstantPrims"),
                    ("GetPrimPath", "omni.graph.nodes.GetPrimPaths"),
                ],
                keys.CONNECT: [("ConstantPrims.inputs:value", "GetPrimPath.inputs:prims")],
            },
        )

        rel = stage.GetPropertyAtPath(f"{graph_path}/ConstantPrims.inputs:value")
        for prim_path in prim_paths:
            omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=prim_path)

        yield ThreadsafetyTestUtils.EVALUATION_ALL_GRAPHS

        out_paths = og.Controller.get(controller.attribute("outputs:primPaths", prim_paths_node))
        self.assertEqual(out_paths, prim_paths)

        for prim_path in prim_paths:
            ThreadsafetyTestUtils.single_evaluation_last_test_instance(
                test_instance_id, partial(stage.RemovePrim, prim_path)
            )

    # ----------------------------------------------------------------------
    @ThreadsafetyTestUtils.make_threading_test
    def test_constant_target(self, test_instance_id: int = 0):
        """Test ConstantTarget node"""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        graph_path = self.TEST_GRAPH_PATH + str(test_instance_id)

        prim_paths = ["/World/TestPrim1", "/World/TestPrim2"]
        for prim_path in prim_paths:
            ThreadsafetyTestUtils.add_to_threading_cache(test_instance_id, stage.DefinePrim(prim_path))

        controller = og.Controller()
        keys = og.Controller.Keys
        (_, (_const_target, prim_paths_node), _, _) = controller.edit(
            graph_path,
            {
                keys.CREATE_NODES: [
                    ("ConstantTarget", "omni.graph.nodes.ConstantTarget"),
                    ("GetPrimPath", "omni.graph.nodes.GetPrimPaths"),
                ],
                keys.CONNECT: [("ConstantTarget.inputs:value", "GetPrimPath.inputs:prims")],
            },
        )

        rel = stage.GetPropertyAtPath(f"{graph_path}/ConstantTarget.inputs:value")
        for prim_path in prim_paths:
            omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=prim_path)

        yield ThreadsafetyTestUtils.EVALUATION_ALL_GRAPHS

        out_paths = og.Controller.get(controller.attribute("outputs:primPaths", prim_paths_node))
        self.assertEqual(out_paths, prim_paths)

        for prim_path in prim_paths:
            ThreadsafetyTestUtils.single_evaluation_last_test_instance(
                test_instance_id, partial(stage.RemovePrim, prim_path)
            )

    # ----------------------------------------------------------------------
    async def test_constant_prims_loads_from_file(self):
        """
        Validation that connections are maintained when loading a graph from a file which uses ConstantPrims -
        which uses a target input attribute as its output
        """
        await ogts.load_test_file("TestConstantPrims.usda", use_caller_subdirectory=True)

        self.assertTrue(og.Controller.graph("/World/PushGraph").is_valid())
        self.assertTrue(og.Controller.node("/World/PushGraph/constant_prims").is_valid())
        self.assertTrue(og.Controller.node("/World/PushGraph/get_prim_paths").is_valid())
        attr_dst = og.Controller.attribute("/World/PushGraph/get_prim_paths.inputs:prims")
        attr_src = og.Controller.attribute("/World/PushGraph/constant_prims.inputs:value")
        self.assertTrue(attr_dst.is_valid())
        self.assertTrue(attr_src.is_valid())
        self.assertTrue(attr_dst.is_connected(attr_src))
        self.assertEqual(attr_dst.get_upstream_connection_count(), 1)
        self.assertEqual(attr_dst.get_upstream_connections()[0].get_path(), attr_src.get_path())
        actual_result = og.Controller.get(attr_dst)
        expected_result = [usdrt.Sdf.Path("/Environment"), usdrt.Sdf.Path("/Environment/defaultLight")]
        self.assertEqual(expected_result, actual_result)

    # ----------------------------------------------------------------------
    async def test_constant_target_loads_from_file(self):
        """
        Validation that connections are maintained when loading a graph from a file which uses ConstantTarget -
        which uses a target input attribute as its output
        """
        await ogts.load_test_file("TestConstantTarget.usda", use_caller_subdirectory=True)

        self.assertTrue(og.Controller.graph("/World/PushGraph").is_valid())
        self.assertTrue(og.Controller.node("/World/PushGraph/constant_target").is_valid())
        self.assertTrue(og.Controller.node("/World/PushGraph/get_prim_paths").is_valid())
        attr_dst = og.Controller.attribute("/World/PushGraph/get_prim_paths.inputs:prims")
        attr_src = og.Controller.attribute("/World/PushGraph/constant_target.inputs:value")
        self.assertTrue(attr_dst.is_valid())
        self.assertTrue(attr_src.is_valid())
        self.assertTrue(attr_dst.is_connected(attr_src))
        self.assertEqual(attr_dst.get_upstream_connection_count(), 1)
        self.assertEqual(attr_dst.get_upstream_connections()[0].get_path(), attr_src.get_path())
        actual_result = og.Controller.get(attr_dst)
        expected_result = [usdrt.Sdf.Path("/Environment"), usdrt.Sdf.Path("/Environment/defaultLight")]
        self.assertEqual(expected_result, actual_result)

    # ----------------------------------------------------------------------
    @ThreadsafetyTestUtils.make_threading_test
    def test_get_parent_prims(self, test_instance_id: int = 0):
        """Test GetParentPrims node"""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        graph_path = self.TEST_GRAPH_PATH + str(test_instance_id)

        prim_paths = ["/World/Test", "/World/Test/Test"]
        prim_parents = ["/World", "/World/Test"]
        for prim_path in prim_paths:
            ThreadsafetyTestUtils.add_to_threading_cache(test_instance_id, stage.DefinePrim(prim_path))

        controller = og.Controller()
        keys = og.Controller.Keys
        (_, (get_parent_prims,), _, _) = controller.edit(
            graph_path, {keys.CREATE_NODES: ("GetParentPrims", "omni.graph.nodes.GetParentPrims")}
        )

        rel = stage.GetPropertyAtPath(f"{graph_path}/GetParentPrims.inputs:prims")
        for prim_path in prim_paths:
            omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=prim_path)

        yield ThreadsafetyTestUtils.EVALUATION_ALL_GRAPHS
        out_paths = og.Controller.get(controller.attribute("outputs:parentPrims", get_parent_prims))
        self.assertEqual(out_paths, [usdrt.Sdf.Path(p) for p in prim_parents])

        for prim_path in prim_paths:
            ThreadsafetyTestUtils.single_evaluation_last_test_instance(
                test_instance_id, partial(stage.RemovePrim, prim_path)
            )

    # ----------------------------------------------------------------------
    async def test_prim_relationship_load(self):
        """Test that a prim relationship when loading does not create OgnPrim node"""

        async def do_test():
            await ogts.load_test_file("TestPrimRelationshipLoad.usda", use_caller_subdirectory=True)
            # Cube and Capsule are driving Sphere, Cylinder, Cone by various methods
            usd_context = omni.usd.get_context()
            stage = usd_context.get_stage()
            graph = og.get_graph_by_path("/World/PushGraph")
            controller = og.Controller()
            nodes = graph.get_nodes()
            node_paths = [n.get_prim_path() for n in nodes]

            # These prims are only connected by relationship, so should not show up in OG
            self.assertNotIn("/World/Cube", node_paths)
            self.assertNotIn("/World/Sphere", node_paths)
            self.assertNotIn("/World/Cylinder", node_paths)

            self.assertNotIn("/World/Cone", node_paths)

            # Sanity check that the rotate connections are working
            for p in ("Sphere", "Capsule", "Cylinder", "Cone"):
                rotate_xyz = stage.GetPrimAtPath("/World/" + p).GetAttribute("xformOp:rotateXYZ").Get()
                self.assertEqual(rotate_xyz[0], 0)
                self.assertEqual(rotate_xyz[1], 0)

            stage.GetPrimAtPath("/World/Cube").GetAttribute("xformOp:rotateXYZ").Set((100, 0, 0))
            stage.GetPrimAtPath("/World/Capsule").GetAttribute("xformOp:rotateXYZ").Set((100, 0, 0))
            await controller.evaluate(graph)
            for p in ("Sphere", "Cylinder", "Cone"):
                rotate_xyz = stage.GetPrimAtPath("/World/" + p).GetAttribute("xformOp:rotateXYZ").Get()
                if p == "Cone":
                    # /World/Cone is not loaded into Flatcache, so we expect this part of the
                    # graph to be non-functional (Cone will not change)
                    self.assertEqual(rotate_xyz[0], 0)
                self.assertEqual(rotate_xyz[1], 0)

        await do_test()

    # ----------------------------------------------------------------------
    @staticmethod
    def _get_expected_read_prims_property_names(prim) -> Set[str]:
        properties = set(prim.GetAuthoredPropertyNames())
        properties.update({"worldMatrix", "sourcePrimPath", "sourcePrimType"})
        return properties

    # ----------------------------------------------------------------------
    @staticmethod
    def _get_expected_read_prims_v2_property_names(prim) -> Set[str]:
        properties = set(prim.GetPropertyNames())
        properties.remove("proxyPrim")  # remove "proxyPrim" which is skipped unless it has targets
        properties.update({"worldMatrix", "sourcePrimPath", "sourcePrimType"})
        return properties

    # ----------------------------------------------------------------------
    async def test_read_prims_write_prim(self):
        """Test omni.graph.nodes.ReadPrims and WritePrim"""
        await self._read_prims_write_prim(
            "omni.graph.nodes.ReadPrims",
            False,
            compute_expected_property_names=self._get_expected_read_prims_property_names,
        )

    # ----------------------------------------------------------------------
    async def test_read_prims_write_prim_with_target(self):
        await self._read_prims_write_prim(
            "omni.graph.nodes.ReadPrims",
            True,
            compute_expected_property_names=self._get_expected_read_prims_property_names,
        )

    # ----------------------------------------------------------------------
    async def test_read_prims_v2_write_prim(self):
        """Test omni.graph.nodes.ReadPrimsV2 and WritePrim"""
        await self._read_prims_write_prim(
            "omni.graph.nodes.ReadPrimsV2",
            False,
            compute_expected_property_names=self._get_expected_read_prims_v2_property_names,
        )

    # ----------------------------------------------------------------------
    async def test_read_prims_v2_write_prim_with_target(self):
        await self._read_prims_write_prim(
            "omni.graph.nodes.ReadPrimsV2",
            True,
            compute_expected_property_names=self._get_expected_read_prims_v2_property_names,
        )

    # ----------------------------------------------------------------------
    async def test_read_prims_bundle_write_prim(self):
        """Test omni.graph.nodes.ReadPrimsBundle and WritePrim"""
        await self._read_prims_write_prim(
            "omni.graph.nodes.ReadPrimsBundle",
            False,
            compute_expected_property_names=self._get_expected_read_prims_property_names,
        )

    # ----------------------------------------------------------------------
    async def test_read_prims_bundle_write_prim_with_target(self):
        await self._read_prims_write_prim(
            "omni.graph.nodes.ReadPrimsBundle",
            True,
            compute_expected_property_names=self._get_expected_read_prims_property_names,
        )

    # ----------------------------------------------------------------------
    async def _read_prims_write_prim(
        self, read_prims_type, use_target_inputs, compute_expected_property_names: Callable
    ):
        """
        use_target_inputs will use the prim target input for the ExtractPrim nodes rather than the prim path input
        """
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        cube_prim = ogts.create_cube(stage, "Cube", (1, 1, 1))

        (
            graph,
            (read_node, write_node, _, _, extract_bundle_node),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Read", read_prims_type),
                    ("Write", "omni.graph.nodes.WritePrim"),
                    ("Add", "omni.graph.nodes.Add"),
                    ("ExtractPrim", "omni.graph.nodes.ExtractPrim"),
                    ("ExtractBundle", "omni.graph.nodes.ExtractBundle"),
                ],
                keys.SET_VALUES: [
                    ("ExtractPrim.inputs:primPath", "/Cube"),
                ],
                keys.CONNECT: [
                    ("Read.outputs_primsBundle", "ExtractPrim.inputs:prims"),
                    ("ExtractPrim.outputs_primBundle", "ExtractBundle.inputs:bundle"),
                ],
            },
        )

        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Read.inputs:prims"),
            target=cube_prim.GetPath(),
        )

        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Write.inputs:prim"),
            target=cube_prim.GetPath(),
        )
        await controller.evaluate(graph)

        if use_target_inputs:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/ExtractPrim.inputs:prim"),
                target=cube_prim.GetPath(),
            )
            await controller.evaluate(graph)

        factory = og.IBundleFactory.create()

        # Check MPiB output for Read
        bundle = graph.get_default_graph_context().get_output_bundle(read_node, "outputs_primsBundle")
        output_bundle2 = factory.get_bundle(graph.get_default_graph_context(), bundle)
        self.assertEqual(output_bundle2.get_child_bundle_count(), 1)

        # Attribute Count:
        # 2 - node: type, typeVersion,
        # 3 - inputs: bundle
        # 2 - outputs: passThrough,
        n_static_attribs_extract_bundle = 4

        # Attribute Count:
        # 2 - node: type, typeVersion,
        # 4 - inputs: prim, execIn, usdWriteBack, layerIdentifier
        # 1 - outputs: execOut,
        # 2 - state: layerIdentifier, resolvedLayerIdentifier
        n_static_attribs_write = 9

        extract_bundle_name = "outputs_passThrough"

        attribs = extract_bundle_node.get_attributes()
        found_size_attrib = False
        for attrib in attribs:
            if attrib.get_name() == "outputs:size" and attrib.get_resolved_type().base_type == og.BaseDataType.DOUBLE:
                found_size_attrib = True
        self.assertTrue(found_size_attrib)

        expected_property_names = compute_expected_property_names(cube_prim)

        bundle = graph.get_default_graph_context().get_output_bundle(extract_bundle_node, extract_bundle_name)

        attribute_names = set(bundle.get_attribute_names())
        self.assertEqual(attribute_names, expected_property_names)

        # Check we have the expected bundle attributes
        self.assertIn("size", attribute_names)
        self.assertIn("sourcePrimPath", attribute_names)
        self.assertIn("sourcePrimType", attribute_names)
        self.assertIn("worldMatrix", attribute_names)
        self.assertIn("primvars:displayColor", attribute_names)

        attribute_datas = bundle.get_attribute_data(False)
        self.assertEqual(
            next((a for a in attribute_datas if a.get_name() == "sourcePrimPath")).get(),
            cube_prim.GetPath().pathString,
        )

        # Check we have the expected dynamic attrib on WritePrim
        attribs = write_node.get_attributes()
        found_size_attrib = False
        for attrib in attribs:
            if attrib.get_name() == "inputs:size" and attrib.get_resolved_type().base_type == og.BaseDataType.DOUBLE:
                found_size_attrib = True
        self.assertTrue(found_size_attrib)

        # check that evaluations propagate in a read/write cycle as expected
        controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CONNECT: [
                    ("ExtractBundle.outputs:size", "Add.inputs:a"),
                    ("ExtractBundle.outputs:size", "Add.inputs:b"),
                    ("Add.outputs:sum", "Write.inputs:size"),
                ]
            },
        )

        await controller.evaluate(graph)
        attr = controller.attribute("outputs:size", extract_bundle_node)
        # it is now 2 on prim, but read node as not been executed after the write, so still has the old value
        self.assertEqual(og.Controller.get(attr), 1)
        await controller.evaluate(graph)
        # now it is 4 on the prim, and /Read as 2
        self.assertEqual(og.Controller.get(attr), 2)
        await controller.evaluate(graph)
        # now it is 8 on the prim, and /Read as 4
        self.assertEqual(og.Controller.get(attr), 4)

        # ReadPrim: Clear the inputs:prim attribute to trigger a reset of the ReadPrim node
        omni.kit.commands.execute(
            "RemoveRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Read.inputs:prims"),
            target=cube_prim.GetPath(),
        )
        await controller.evaluate(graph)

        # Verify that the stale dynamic and bundle attributes have been removed
        attribs = extract_bundle_node.get_attributes()
        self.assertEqual(len(attribs), n_static_attribs_extract_bundle)

        bundle = graph.get_default_graph_context().get_output_bundle(extract_bundle_node, extract_bundle_name)
        self.assertEqual(bundle.get_attribute_data_count(), 0)

        # WritePrim: Clear the inputs:prim attribute to trigger a reset of the WritePrim node
        omni.kit.commands.execute(
            "RemoveRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/Write.inputs:prim"),
            target=cube_prim.GetPath(),
        )
        await controller.evaluate(graph)

        # Verify that the stale dynamic and bundle attributes have been removed
        attribs = write_node.get_attributes()
        self.assertEqual(len(attribs), n_static_attribs_write)

        # Set it up again and re-verify things work
        omni.kit.undo.undo()  # Undo remove target from Write Prim

        # Following step is to undo disconnected and removed dynamic attributes inside of Extract Bundle.
        # When Extract Bundle's input change or recompute is called, we record
        omni.kit.undo.undo()  # Call to undo dynamic attribute removal and disconnection on read prim (compute)
        omni.kit.undo.undo()  # Call to undo dynamic attribute removal and disconnection on read prim (compute)
        omni.kit.undo.undo()  # Call to undo dynamic attribute removal and disconnection on read prim into bundle (compute)
        omni.kit.undo.undo()  # Call to undo dynamic attribute removal and disconnection on read prim into bundle (compute)

        await controller.evaluate(graph)

        # Check if MPiB is back to the output of ReadPrimIntoBundle
        bundle = graph.get_default_graph_context().get_output_bundle(read_node, "outputs_primsBundle")
        output_bundle2 = factory.get_bundle(graph.get_default_graph_context(), bundle)
        self.assertEqual(output_bundle2.get_child_bundle_count(), 1)

        # Verify we have the size attribute back and our bundle attribs
        attribs = write_node.get_attributes()

        found_size_attrib = False
        for attrib in attribs:
            if attrib.get_name() == "inputs:size" and attrib.get_resolved_type().base_type == og.BaseDataType.DOUBLE:
                found_size_attrib = True
        self.assertTrue(found_size_attrib)

        # Check output bundle attributes of ExtractBundle
        bundle = graph.get_default_graph_context().get_output_bundle(extract_bundle_node, extract_bundle_name)
        attribute_datas = bundle.get_attribute_data(False)
        attribute_names = [a.get_name() for a in attribute_datas]
        self.assertIn("size", attribute_names)
        self.assertIn("sourcePrimPath", attribute_names)
        self.assertIn("worldMatrix", attribute_names)
        self.assertIn("primvars:displayColor", attribute_names)

        attribs = extract_bundle_node.get_attributes()
        self.assertEqual(len(attribs) - n_static_attribs_extract_bundle, len(attribute_datas))

        # Reset the underlying prim attrib value and check the plumbing is still working
        # Use UsdRT to write as size is a special attribute. With FSD enabled, it may not get updated to Fabric
        cube_prim.GetAttribute("size").Set(1)
        cube_path = str(cube_prim.GetPath())
        usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
        usdrt_stage.GetPrimAtPath(cube_path).GetAttribute("size").Set(1)

        await controller.evaluate(graph)
        attr = controller.attribute("outputs:size", extract_bundle_node)
        self.assertEqual(og.Controller.get(attr), 1)
        await controller.evaluate(graph)
        self.assertEqual(og.Controller.get(attr), 2)
        await controller.evaluate(graph)
        self.assertEqual(og.Controller.get(attr), 4)

    # ----------------------------------------------------------------------
    async def test_findprims(self):
        """Test omni.graph.nodes.FindPrims corner cases"""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        cube_prim = ogts.create_cube(stage, "Cube1", (1, 1, 1))
        cube_prim2 = ogts.create_cube(stage, "Cube2", (1, 1, 1))
        cube_prim3 = ogts.create_cube(stage, "Cube3", (1, 1, 1))
        cube_prim3.CreateRelationship("test_rel").AddTarget(cube_prim.GetPrimPath())

        (graph, (read_node,), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: ("FindPrims", "omni.graph.nodes.FindPrims"),
                keys.SET_VALUES: ("FindPrims.inputs:namePrefix", "Cube"),
            },
        )
        await controller.evaluate(graph)
        paths_attr = controller.attribute("outputs:primPaths", read_node)
        paths = og.Controller.get(paths_attr)
        self.assertListEqual(paths, [p.GetPrimPath() for p in (cube_prim, cube_prim2, cube_prim3)])
        # set cube to inactive and verify it doesn't show up in the list
        cube_prim.SetActive(False)
        await controller.evaluate(graph)
        paths = og.Controller.get(paths_attr)
        self.assertListEqual(paths, [p.GetPrimPath() for p in (cube_prim2, cube_prim3)])

        # Test the relationship requirement works
        controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.SET_VALUES: [
                    ("FindPrims.inputs:requiredRelationship", "test_rel"),
                    # Not the right target
                    ("FindPrims.inputs:requiredRelationshipTarget", cube_prim2.GetPrimPath().pathString),
                ]
            },
        )
        await controller.evaluate(graph)
        paths = og.Controller.get(paths_attr)
        self.assertTrue(len(paths) == 0)

        controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.SET_VALUES: [
                    # The right target
                    ("FindPrims.inputs:requiredRelationshipTarget", cube_prim.GetPrimPath().pathString),
                ]
            },
        )
        await controller.evaluate(graph)
        paths = og.Controller.get(paths_attr)
        self.assertListEqual(paths, [p.GetPrimPath() for p in (cube_prim3,)])

    # ----------------------------------------------------------------------
    async def test_findprims_path_pattern(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        ogts.create_cube(stage, "Cube1", (1, 1, 1))
        ogts.create_cube(stage, "Cube2", (1, 1, 1))
        ogts.create_cube(stage, "Cube3", (1, 1, 1))
        ogts.create_cube(stage, "Cube44", (1, 1, 1))
        ogts.create_cube(stage, "AnotherCube1", (1, 1, 1))
        ogts.create_cube(stage, "AnotherCube2", (1, 1, 1))
        ogts.create_cube(stage, "AnotherCube3", (1, 1, 1))

        controller = og.Controller()
        keys = og.Controller.Keys

        (graph, (find_prims,), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: ("FindPrims", "omni.graph.nodes.FindPrims"),
                keys.SET_VALUES: [
                    ("FindPrims.inputs:recursive", True),
                    ("FindPrims.inputs:pathPattern", "/Cube?"),
                ],
            },
        )
        await controller.evaluate(graph)

        outputs_prim_paths = find_prims.get_attribute("outputs:primPaths")
        value = outputs_prim_paths.get()
        self.assertEqual(len(value), 3)  # Cube1, Cube2, Cube3 but not Cube44
        self.assertTrue(all(item in ["/Cube1", "/Cube2", "/Cube3"] for item in value))

        (graph, _, _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.SET_VALUES: ("FindPrims.inputs:pathPattern", "/*Cube?"),
            },
        )
        await controller.evaluate(graph)
        value = outputs_prim_paths.get()
        self.assertEqual(len(value), 6)  # AnotherCube1,2,3 and Cube1,2,3, but not Cube44
        required_cubes = ["/Cube1", "/Cube2", "/Cube3", "/AnotherCube1", "/AnotherCube2", "/AnotherCube3"]
        self.assertTrue(all(item in required_cubes for item in value))

        # get all /Cube?, but exclude /Cube2
        (graph, _, _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.SET_VALUES: ("FindPrims.inputs:pathPattern", "/Cube? ^/Cube2"),
            },
        )
        await controller.evaluate(graph)
        value = outputs_prim_paths.get()
        self.assertEqual(len(value), 2)  # Cube1,3, but not Cube2
        required_cubes = ["/Cube1", "/Cube3"]
        self.assertTrue(all(item in required_cubes for item in value))

        # get all /Cube? but exclude /Cube1 and /Cube2
        (graph, _, _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.SET_VALUES: ("FindPrims.inputs:pathPattern", "/Cube? ^/Cube1 ^/Cube2"),
            },
        )
        await controller.evaluate(graph)
        value = outputs_prim_paths.get()
        self.assertEqual(len(value), 1)  # Cube3, but not Cube1,2
        required_cubes = ["/Cube3"]
        self.assertTrue(all(item in required_cubes for item in value))

        # get all Cubes, but exclude all cubes that end with single digit
        (graph, _, _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.SET_VALUES: ("FindPrims.inputs:pathPattern", "*Cube* ^*Cube?"),
            },
        )
        await controller.evaluate(graph)
        value = outputs_prim_paths.get()
        self.assertEqual(len(value), 1)  # only Cube44
        required_cubes = ["/Cube44"]
        self.assertTrue(all(item in required_cubes for item in value))

        # get all Cubes, and exclude all cubes to produce empty set
        (graph, _, _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.SET_VALUES: ("FindPrims.inputs:pathPattern", "*Cube* ^*Cube*"),
            },
        )
        await controller.evaluate(graph)
        value = outputs_prim_paths.get()
        self.assertEqual(len(value), 0)

    # ----------------------------------------------------------------------
    async def test_getprims_path_pattern(self):
        """Test the path pattern matching feature of the GetPrims node."""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        (graph, (_, get_prims_node), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("ReadPrimsBundle", "omni.graph.nodes.ReadPrimsBundle"),
                    ("GetPrims", "omni.graph.nodes.GetPrims"),
                ],
                keys.CONNECT: [("ReadPrimsBundle.outputs_primsBundle", "GetPrims.inputs:bundle")],
            },
        )

        cube_paths = {"/Cube1", "/Cube2", "/Cube3", "/Cube44", "/AnotherCube1", "/AnotherCube2", "/AnotherCube3"}
        for cube_path in cube_paths:
            cube_name = cube_path.split("/")[-1]
            ogts.create_cube(stage, cube_name, (1, 1, 1))
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/ReadPrimsBundle.inputs:prims"),
                target=cube_path,
            )

        await controller.evaluate(graph)

        # Dictionary from each path pattern to its expected prim paths
        path_pattern_dict = {
            "*": cube_paths,
            "": set(),
            "/Cube?": {"/Cube1", "/Cube2", "/Cube3"},
            "/*Cube?": {"/Cube1", "/Cube2", "/Cube3", "/AnotherCube1", "/AnotherCube2", "/AnotherCube3"},
            "/* ^/Another*": {"/Cube1", "/Cube2", "/Cube3", "/Cube44"},
        }

        bundle_factory = og.IBundleFactory.create()

        bundle = graph.get_default_graph_context().get_output_bundle(get_prims_node, "outputs_bundle")
        output_bundle2 = bundle_factory.get_bundle(graph.get_default_graph_context(), bundle)

        for path_pattern, expected_prim_paths in path_pattern_dict.items():
            # Test path patterns with the "inverse" option off (by default)
            (graph, _, _, _) = controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.SET_VALUES: [
                        ("GetPrims.inputs:pathPattern", path_pattern),
                        ("GetPrims.inputs:inverse", False),
                    ]
                },
            )
            await controller.evaluate(graph)

            child_bundle_paths = set()

            child_bundle_count = output_bundle2.get_child_bundle_count()
            for i in range(child_bundle_count):
                child_bundle = output_bundle2.get_child_bundle(i)
                attr = child_bundle.get_attribute_by_name("sourcePrimPath")
                child_bundle_paths.add(attr.get())

            self.assertEqual(child_bundle_paths, expected_prim_paths)

            # Test path patterns with the "inverse" option on
            (graph, _, _, _) = controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.SET_VALUES: [
                        ("GetPrims.inputs:inverse", True),
                    ]
                },
            )
            await controller.evaluate(graph)

            child_bundle_paths = set()

            child_bundle_count = output_bundle2.get_child_bundle_count()
            for i in range(child_bundle_count):
                child_bundle = output_bundle2.get_child_bundle(i)
                attr = child_bundle.get_attribute_by_name("sourcePrimPath")
                child_bundle_paths.add(attr.get())

            self.assertEqual(child_bundle_paths, cube_paths.difference(expected_prim_paths))

    # ----------------------------------------------------------------------
    async def test_readtime(self):
        """Test omni.graph.nodes.ReadTime"""
        app = omni.kit.app.get_app()
        timeline = omni.timeline.get_timeline_interface()

        time_node_name = "Time"

        # setup initial timeline state and avoid possibility that running this test twice will give different results
        timeline.set_fast_mode(True)
        fps = 24.0
        timeline.set_time_codes_per_second(fps)
        timeline.set_start_time(-1.0)
        timeline.set_end_time(0.0)
        timeline.set_current_time(0.0)
        await app.next_update_async()

        keys = og.Controller.Keys
        (_, (time_node,), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH, {keys.CREATE_NODES: [(time_node_name, "omni.graph.nodes.ReadTime")]}
        )
        await app.next_update_async()
        await og.Controller.evaluate()
        self.assertGreater(og.Controller(og.Controller.attribute("outputs:deltaSeconds", time_node)).get(), 0.0)
        self.assertGreater(og.Controller(og.Controller.attribute("outputs:timeSinceStart", time_node)).get(), 0.0)
        self.assertFalse(og.Controller(og.Controller.attribute("outputs:isPlaying", time_node)).get())
        self.assertEqual(og.Controller(og.Controller.attribute("outputs:time", time_node)).get(), 0.0)
        self.assertEqual(og.Controller(og.Controller.attribute("outputs:frame", time_node)).get(), 0.0)

        timeline.set_start_time(1.0)
        timeline.set_end_time(10.0)
        timeline.play()
        await app.next_update_async()
        await app.next_update_async()
        await og.Controller.evaluate()

        # graph has been reloaded as a result of the fps change: we need re refetch the node
        time_node = og.get_node_by_path(self.TEST_GRAPH_PATH + "/" + time_node_name)

        self.assertTrue(og.Controller(og.Controller.attribute("outputs:isPlaying", time_node)).get())
        animation_time = og.Controller(og.Controller.attribute("outputs:time", time_node)).get()
        self.assertGreater(animation_time, 0.0)
        self.assertAlmostEqual(
            og.Controller(og.Controller.attribute("outputs:frame", time_node)).get(), fps * animation_time, places=2
        )
        timeline.stop()
        await app.next_update_async()

    # ----------------------------------------------------------------------
    async def test_read_and_write_prim_material(self):
        await self._read_and_write_prim_material(False)

    async def test_read_and_write_prim_material_with_target(self):
        await self._read_and_write_prim_material(True)

    async def _read_and_write_prim_material(self, use_target_inputs):
        """
        Test ReadPrimMaterial and WritePrimMaterial node. If use_target_inputs is true, use the prim target input rather
        than the prim path input
        """
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        mat_path = "/TestMaterial"
        prim_path_a = "/TestPrimA"
        prim_path_b = "/TestPrimB"

        (graph, (read_node, _), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrimMaterial"),
                    ("Write", "omni.graph.nodes.WritePrimMaterial"),
                ],
                keys.CREATE_PRIMS: [(mat_path, "Material"), (prim_path_a, "Cube"), (prim_path_b, "Cube")],
                keys.SET_VALUES: [
                    ("Read.inputs:primPath", prim_path_a),
                    ("Write.inputs:primPath", prim_path_b),
                    ("Write.inputs:materialPath", mat_path),
                ],
            },
        )
        await controller.evaluate(graph)

        if use_target_inputs:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/Read.inputs:prim"),
                target=prim_path_a,
            )
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/Write.inputs:prim"),
                target=prim_path_b,
            )
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/Write.inputs:material"),
                target=mat_path,
            )
            await controller.evaluate(graph)

        prim_a = stage.GetPrimAtPath(prim_path_a)
        rel_a = prim_a.CreateRelationship("material:binding")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel_a, target=Sdf.Path(mat_path))
        await controller.evaluate(graph)

        read_output = og.Controller.get(controller.attribute("outputs:material", read_node))
        self.assertEqual(read_output, mat_path)

        prim_b = stage.GetPrimAtPath(prim_path_b)
        mat_b, _ = UsdShade.MaterialBindingAPI(prim_b).ComputeBoundMaterial()
        write_output = mat_b.GetPath().pathString
        self.assertEqual(write_output, mat_path)

    # ----------------------------------------------------------------------
    async def test_read_prim_material_with_target_connections(self):
        """Test ReadPrimMaterial and WritePrimMaterial node"""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        mat_path = "/TestMaterial"
        prim_path_a = "/TestPrimA"

        (graph, (_, _, prim_node, _), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrimMaterial"),
                    ("GetPrimAtPath", "omni.graph.nodes.GetPrimsAtPath"),
                    ("GetPrimPath", "omni.graph.nodes.GetPrimPath"),
                    ("ConstToken", "omni.graph.nodes.ConstantToken"),
                ],
                keys.CREATE_PRIMS: [(mat_path, "Material"), (prim_path_a, "Cube")],
                keys.SET_VALUES: [("ConstToken.inputs:value", prim_path_a)],
                keys.CONNECT: [
                    ("Read.outputs:materialPrim", "GetPrimPath.inputs:prim"),
                    ("GetPrimAtPath.outputs:prims", "Read.inputs:prim"),
                    ("ConstToken.inputs:value", "GetPrimAtPath.inputs:path"),
                ],
            },
        )

        prim_a = stage.GetPrimAtPath(prim_path_a)
        rel_a = prim_a.CreateRelationship("material:binding")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel_a, target=Sdf.Path(mat_path))
        await controller.evaluate(graph)

        mat_output = og.Controller.get(("outputs:primPath", prim_node))
        self.assertEqual(mat_output, mat_path)

    # ----------------------------------------------------------------------
    async def test_read_write_prim_material_invalid(self):
        """Tests Read/WritePrimMaterial with invalid inputs"""

        # Test read, then write nodes
        node_types = ["omni.graph.nodes.ReadPrimMaterial", "omni.graph.nodes.WritePrimMaterial"]
        for i, node_type in enumerate(node_types):
            controller = og.Controller()
            keys = og.Controller.Keys

            # create an invalid path
            (graph, (mat_node,), _, _) = controller.edit(
                f"{self.TEST_GRAPH_PATH}{i}",
                {
                    keys.CREATE_NODES: [
                        (f"Mat{i}", node_type),
                    ],
                    keys.SET_VALUES: [
                        (f"Mat{i}.inputs:primPath", "This is a invalid prim path"),
                    ],
                },
            )

            # the two scenarios produce different messages but both are errors
            with ogts.ExpectedError():
                await controller.evaluate(graph)
            self.assertEqual(len(mat_node.get_compute_messages(og.ERROR)), 1)

            mat_node.get_attribute("inputs:primPath").set("/Valid/But/Not/Existant")
            with ogts.ExpectedError():
                await controller.evaluate(graph)
            errors = mat_node.get_compute_messages(og.ERROR)
            self.assertEqual(len(errors), 2)
            self.assertNotEqual(errors[0], errors[1])

        # add extra write node tests. Set a valid prim, but invalid material path
        prim_path = "/TestPrim"
        controller.edit(graph, {keys.CREATE_PRIMS: [(prim_path, "Cube")]})
        mat_node.get_attribute("inputs:primPath").set(prim_path)
        mat_node.get_attribute("inputs:materialPath").set("Invalid SDF Path")
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        errors = mat_node.get_compute_messages(og.ERROR)
        self.assertEqual(len(errors), 3)
        self.assertEqual(len(set(errors)), 3)

        # use a valid but non-existant material path
        mat_node.get_attribute("inputs:materialPath").set("/Invalid/Mat/Path")
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        errors = mat_node.get_compute_messages(og.ERROR)
        self.assertEqual(len(errors), 4)
        self.assertEqual(len(set(errors)), 4)

    # ----------------------------------------------------------------------
    async def test_read_and_write_settings(self):
        """Test ReadSetting and WriteSetting node"""
        settings = carb.settings.get_settings()

        setting_values = [
            (og.Type(og.BaseDataType.BOOL, 1, 0), "/omnigraph/testsetting/set_bool", False, True),
            (
                og.Type(og.BaseDataType.BOOL, 1, 1),
                "/omnigraph/testsetting/set_bool_array",
                [False, False],
                [True, True],
            ),
            (og.Type(og.BaseDataType.INT, 1, 0), "/omnigraph/testsetting/set_int", 1, 2),
            (og.Type(og.BaseDataType.INT, 2, 0), "/omnigraph/testsetting/set_int2", (1, 2), (3, 4)),
            (og.Type(og.BaseDataType.INT, 3, 0), "/omnigraph/testsetting/set_int3", (5, 6, 7), (8, 9, 0)),
            (og.Type(og.BaseDataType.INT, 4, 0), "/omnigraph/testsetting/set_int4", (1, 2, 3, 4), (5, 6, 7, 8)),
            (
                og.Type(og.BaseDataType.INT, 1, 1),
                "/omnigraph/testsetting/set_int_array",
                [1, 2, 3],
                [6, 7, 8, 9, 10, 11],
            ),
            (og.Type(og.BaseDataType.INT64, 1, 0), "/omnigraph/testsetting/set_int64", 5, 10),
            (og.Type(og.BaseDataType.INT64, 1, 1), "/omnigraph/testsetting/set_int64_array", [1], [2, 2]),
            (og.Type(og.BaseDataType.FLOAT, 1, 0), "/omnigraph/testsetting/set_float", 1.0, 2.0),
            (og.Type(og.BaseDataType.FLOAT, 2, 0), "/omnigraph/testsetting/set_float2", (2.0, 3.0), (4.0, 5.0)),
            (
                og.Type(og.BaseDataType.FLOAT, 3, 0),
                "/omnigraph/testsetting/set_float3",
                (6.0, 7.0, 8.0),
                (9.0, 0.0, 1.0),
            ),
            (
                og.Type(og.BaseDataType.FLOAT, 4, 0),
                "/omnigraph/testsetting/set_float4",
                (3.0, 4.0, 5.0, 6.0),
                (7.0, 8.0, 9.0, 0.0),
            ),
            (
                og.Type(og.BaseDataType.FLOAT, 1, 1),
                "/omnigraph/testsetting/set_float_array",
                [1.0, 2.0, 3.0, 4.0, 5.0],
                [6.0, 7.0, 8.0, 9.0, 10.0, 11.0],
            ),
            (og.Type(og.BaseDataType.DOUBLE, 1, 0), "/omnigraph/testsetting/set_double", 1.0, 2.0),
            (og.Type(og.BaseDataType.DOUBLE, 2, 0), "/omnigraph/testsetting/set_double2", (3.0, 4.0), (5.0, 6.0)),
            (
                og.Type(og.BaseDataType.DOUBLE, 3, 0),
                "/omnigraph/testsetting/set_double3",
                (7.0, 8.0, 9.0),
                (1.0, 2.0, 3.0),
            ),
            (
                og.Type(og.BaseDataType.DOUBLE, 4, 0),
                "/omnigraph/testsetting/set_double4",
                (4.0, 5.0, 6.0, 7.0),
                (8.0, 9.0, 0.0, 1.0),
            ),
            (
                og.Type(og.BaseDataType.DOUBLE, 1, 1),
                "/omnigraph/testsetting/set_double_array",
                [1.0, 2.0, 3.0, 4.0, 5.0],
                [6.0, 7.0, 8.0, 9.0, 10.0, 11.0],
            ),
            (og.Type(og.BaseDataType.TOKEN, 1, 0), "/omnigraph.testsettings/set_token", "def", "set"),
            (
                og.Type(og.BaseDataType.TOKEN, 1, 1),
                "/omnigraph.testsettings/set_token_array",
                ["def"],
                ["set1", "set2"],
            ),
        ]

        # set the default values
        for _, path, val, _ in setting_values:
            setting_path = self.PERSISTENT_SETTINGS_PREFIX + path
            settings.set(setting_path, val)

        controller = og.Controller()
        keys = controller.Keys

        # separate read and write graphs
        (read_graph, (read_node,), _, _) = controller.edit(
            f"{self.TEST_GRAPH_PATH}Read",
            {
                keys.CREATE_NODES: [("Read", "omni.graph.nodes.ReadSetting")],
            },
        )

        (write_graph, (write_node,), _, _) = controller.edit(
            f"{self.TEST_GRAPH_PATH}Write",
            {
                keys.CREATE_NODES: [("Write", "omni.graph.nodes.WriteSetting")],
            },
        )

        for _, path, val, new_val in setting_values:

            setting_path = self.PERSISTENT_SETTINGS_PREFIX + path

            # set the read node input
            read_node.get_attribute("inputs:settingPath").set(setting_path)

            # check the resolution of and set the write node input
            write_node.get_attribute("inputs:settingPath").set(setting_path)
            write_node_input = write_node.get_attribute("inputs:value")
            write_node_input.set(new_val)

            # Read the old value
            await controller.evaluate(read_graph)
            output_value = og.Controller.get(controller.attribute("outputs:value", read_node))

            # write the new value
            self.val_compare(output_value, val)
            await controller.evaluate(write_graph)

            # re-read the old value
            await controller.evaluate(read_graph)
            output_value = og.Controller.get(controller.attribute("outputs:value", read_node))
            self.val_compare(output_value, new_val)

    # ----------------------------------------------------------------------
    async def test_read_settings_conversion(self):
        """Test ReadSetting node value implicit type conversion"""
        settings = carb.settings.get_settings()

        setting_values = [
            {"path": "/omnigraph.testsettings/set_token_int", "value": "1", "cast_val": 1, "type": "int"},
            {
                "path": "/omnigraph.testsettings/set_token_int_array",
                "value": ["1", "2", "3", "4"],
                "cast_val": [1, 2, 3, 4],
                "type": "int",
            },
            {
                "path": "/omnigraph.testsettings/set_token_int4",
                "value": ("5", "6", "7", "8"),
                "cast_val": (5, 6, 7, 8),
                "type": "int4",
            },
            {"path": "/omnigraph.testsettings/set_token_double", "value": "1.111", "cast_val": 1.111, "type": "double"},
            {
                "path": "/omnigraph.testsettings/set_token_double_array",
                "value": ["1.111", "2.222", "3.333", "4.444"],
                "cast_val": [1.111, 2.222, 3.333, 4.444],
                "type": "double",
            },
            {
                "path": "/omnigraph.testsettings/set_token_double4",
                "value": ("5.555", "6.666", "7.777", "8.888"),
                "cast_val": (5.555, 6.666, 7.777, 8.888),
                "type": "double4",
            },
            {"path": "/omnigraph.testsettings/set_token_bool", "value": "True", "cast_val": True, "type": "bool"},
            {"path": "/omnigraph.testsettings/set_token_token", "value": "Foo", "cast_val": "Foo", "type": "token"},
        ]

        # set the default values
        for setting in setting_values:
            setting_path = self.PERSISTENT_SETTINGS_PREFIX + setting["path"]
            settings.set(setting_path, setting["value"])

        controller = og.Controller()
        keys = controller.Keys

        (
            read_cast_graph,
            (
                read_int_node,
                _,
                read_int4_node,
                _,
                read_double_node,
                _,
                read_double4_node,
                _,
                read_bool_node,
                _,
                read_token_node,
                _,
            ),
            _,
            _,
        ) = controller.edit(
            f"{self.TEST_GRAPH_PATH}Read",
            {
                keys.CREATE_NODES: [
                    ("ReadInt", "omni.graph.nodes.ReadSetting"),
                    ("Int", "omni.graph.nodes.ConstantInt"),
                    ("ReadInt4", "omni.graph.nodes.ReadSetting"),
                    ("Int4", "omni.graph.nodes.ConstantInt4"),
                    ("ReadDouble", "omni.graph.nodes.ReadSetting"),
                    ("Double", "omni.graph.nodes.ConstantDouble"),
                    ("ReadDouble4", "omni.graph.nodes.ReadSetting"),
                    ("Double4", "omni.graph.nodes.ConstantDouble4"),
                    ("ReadBool", "omni.graph.nodes.ReadSetting"),
                    ("Bool", "omni.graph.nodes.ConstantBool"),
                    ("ReadToken", "omni.graph.nodes.ReadSetting"),
                    ("Token", "omni.graph.nodes.ConstantToken"),
                ],
                keys.CONNECT: [
                    ("ReadInt.outputs:value", "Int.inputs:value"),
                    ("ReadInt4.outputs:value", "Int4.inputs:value"),
                    ("ReadDouble.outputs:value", "Double.inputs:value"),
                    ("ReadDouble4.outputs:value", "Double4.inputs:value"),
                    ("ReadBool.outputs:value", "Bool.inputs:value"),
                    ("ReadToken.outputs:value", "Token.inputs:value"),
                ],
            },
        )

        for setting in setting_values:
            setting_path = self.PERSISTENT_SETTINGS_PREFIX + setting["path"]

            match setting["type"]:
                case "int":
                    read_node = read_int_node
                case "int4":
                    read_node = read_int4_node
                case "double":
                    read_node = read_double_node
                case "double4":
                    read_node = read_double4_node
                case "bool":
                    read_node = read_bool_node
                case "token":
                    read_node = read_token_node
                case _:
                    self.assertTrue(False)

            # set the read node input
            read_node.get_attribute("inputs:settingPath").set(setting_path)

            await controller.evaluate(read_cast_graph)

            # Read the connected value on ReadSetting node -> should be cast to type
            output_value = og.Controller.get(controller.attribute("outputs:value", read_node))
            self.val_compare(output_value, setting["cast_val"])

    # ----------------------------------------------------------------------
    async def test_get_look_at_rotation(self):
        """Test GetLookAtRotation node"""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        # Get the scene up-vector.
        stage_up_axis = stage.GetMetadata("upAxis")
        if stage_up_axis.lower() == "x":
            up_vec = Gf.Vec3d.XAxis()
            fwd_vec = -Gf.Vec3d.ZAxis()
            right_vec = -Gf.Vec3d.YAxis()
            is_y_up = False
        elif stage_up_axis.lower() == "z":
            up_vec = Gf.Vec3d.ZAxis()
            fwd_vec = -Gf.Vec3d.XAxis()
            right_vec = Gf.Vec3d.YAxis()
            is_y_up = False
        else:
            up_vec = Gf.Vec3d.YAxis()
            fwd_vec = -Gf.Vec3d.ZAxis()
            right_vec = Gf.Vec3d.XAxis()
            is_y_up = True

        # Create a prim driven by a GetLookAtRotation node to always face its fwd_vec toward
        # the origin.

        distance_from_origin = 750.0

        # It's important that the up component be non-zero as that creates a difference between the local and
        # and world up-vectors, which is where problems can occur.
        up_offset = 100.0
        position = up_vec * up_offset - fwd_vec * distance_from_origin
        xform_path = "/World/xform"

        controller = og.Controller()
        keys = og.Controller.Keys
        (graph, (lookat_node, *_), (xform_prim, *_), _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("lookat", "omni.graph.nodes.GetLookAtRotation"),
                    ("write", "omni.graph.nodes.WritePrimAttribute"),
                ],
                keys.CREATE_PRIMS: [(xform_path, "Xform")],
                keys.CONNECT: [("lookat.outputs:rotateXYZ", "write.inputs:value")],
                keys.SET_VALUES: [
                    ("lookat.inputs:forward", fwd_vec),
                    ("lookat.inputs:start", position),
                    ("write.inputs:name", "xformOp:rotateXYZ"),
                    ("write.inputs:primPath", xform_path),
                    ("write.inputs:usePath", True),
                ],
            },
        )

        await controller.evaluate(graph)

        start_attr = lookat_node.get_attribute("inputs:start")
        fwd_attr = lookat_node.get_attribute("inputs:forward")
        up_attr = lookat_node.get_attribute("inputs:up")

        for _ in range(2):
            # Move the transform in a circle around the origin, keeping the up component constant.
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                position = right_vec * math.sin(rad) * distance_from_origin
                position -= fwd_vec * math.cos(rad) * distance_from_origin
                position += up_vec * up_offset
                start_attr.set(position)

                await controller.evaluate(graph)

                # Get the normalized vector from the current position to the origin.
                pos_vec = -Gf.Vec3d(position).GetNormalized()

                # The forward vector in world space should match the position vector.
                cache = UsdGeom.XformCache()
                xform = cache.GetLocalToWorldTransform(xform_prim)
                ws_fwd = xform.TransformDir(fwd_vec).GetNormalized()
                diff = Gf.Rotation(pos_vec, ws_fwd).GetAngle()
                self.assertAlmostEqual(
                    diff, 0.0, msg=f"at {angle} degree position, forward vector does not point at origin."
                )

                # The local and world up-vectors should remain within 8 degrees of each other.
                ws_up = xform.TransformDir(up_vec).GetNormalized()
                diff = Gf.Rotation(up_vec, ws_up).GetAngle()
                self.assertLess(abs(diff), 8.0, f"at {angle} degree position, up-vector has drifted too far")

            # The first pass used scene-up.
            # For the second pass we set an explicit up-vector, different from scene-up.
            if is_y_up:
                up_vec = Gf.Vec3d.ZAxis()
                fwd_vec = -Gf.Vec3d.XAxis()
                right_vec = Gf.Vec3d.YAxis()
            else:
                up_vec = Gf.Vec3d.YAxis()
                fwd_vec = -Gf.Vec3d.ZAxis()
                right_vec = Gf.Vec3d.XAxis()

            fwd_attr.set(fwd_vec)
            up_attr.set(up_vec)

    async def test_selection_nodes(self):
        """Test ReadStageSelection, IsPrimSelected nodes"""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        (graph, (read_node, check_node, check_target), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadStageSelection"),
                    ("IsSelected", "omni.graph.nodes.IsPrimSelected"),
                    ("IsSelectedWithTarget", "omni.graph.nodes.IsPrimSelected"),
                ],
                keys.SET_VALUES: [("IsSelected.inputs:primPath", f"{self.TEST_GRAPH_PATH}/Read")],
            },
        )
        await controller.evaluate(graph)

        rel = stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/IsSelectedWithTarget.inputs:prim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=f"{self.TEST_GRAPH_PATH}/Read")

        selection = usd_context.get_selection()

        self.assertFalse(og.Controller.get(controller.attribute("outputs:isSelected", check_node)))
        self.assertFalse(og.Controller.get(controller.attribute("outputs:isSelected", check_target)))
        selection.set_selected_prim_paths(
            [read_node.get_prim_path()],
            False,
        )
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        selected_paths = og.Controller.get(controller.attribute("outputs:selectedPrims", read_node))
        self.assertListEqual(selected_paths, selection.get_selected_prim_paths())
        self.assertTrue(og.Controller.get(controller.attribute("outputs:isSelected", check_node)))
        self.assertTrue(og.Controller.get(controller.attribute("outputs:isSelected", check_target)))

        selection.clear_selected_prim_paths()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        selected_paths = og.Controller.get(controller.attribute("outputs:selectedPrims", read_node))
        self.assertListEqual(selected_paths, selection.get_selected_prim_paths())
        self.assertFalse(og.Controller.get(controller.attribute("outputs:isSelected", check_node)))
        self.assertFalse(og.Controller.get(controller.attribute("outputs:isSelected", check_target)))

    # ----------------------------------------------------------------------
    async def test_parallel_read_write_prim_attribute(self):
        """Attempt to read and write prim attributes in parallel"""

        # ReadIndex -> Multiply
        #           /           \
        #         10             ------x--------> MakeTranslate -> WriteTranslate
        #                                      /
        # ReadTranslate -> BreakTranslate -yz-

        keys = og.Controller.Keys

        index_name = "testIndex"
        attr_name = "xformOp:translate"
        scale = 10

        cubes = []

        for i in range(64):
            graph_name = f"/graph{i}"
            obj_name = f"/obj{i}"
            controller = og.Controller()
            (graph, _, prims, _) = controller.edit(
                graph_name,
                {
                    keys.CREATE_NODES: [
                        ("ReadIndex", "omni.graph.nodes.ReadPrimAttribute"),
                        ("ReadTranslate", "omni.graph.nodes.ReadPrimAttribute"),
                        ("BreakTranslate", "omni.graph.nodes.BreakVector3"),
                        ("Multiply", "omni.graph.nodes.Multiply"),
                        ("MakeTranslate", "omni.graph.nodes.MakeVector3"),
                        ("WriteTranslate", "omni.graph.nodes.WritePrimAttribute"),
                    ],
                    keys.CREATE_PRIMS: [
                        (obj_name, "Cube"),
                    ],
                },
            )

            # we want to test parallel execution: prevent any merging
            graph.set_auto_instancing_allowed(False)

            attr = prims[0].CreateAttribute(index_name, Sdf.ValueTypeNames.Double)
            attr.Set(i)
            cubes.append(prims[0])

            controller.edit(
                graph_name,
                {
                    keys.SET_VALUES: [
                        ("ReadIndex.inputs:name", index_name),
                        ("ReadIndex.inputs:usePath", True),
                        ("ReadIndex.inputs:primPath", obj_name),
                        ("ReadTranslate.inputs:name", attr_name),
                        ("ReadTranslate.inputs:usePath", True),
                        ("ReadTranslate.inputs:primPath", obj_name),
                        ("WriteTranslate.inputs:name", attr_name),
                        ("WriteTranslate.inputs:usePath", True),
                        ("WriteTranslate.inputs:primPath", obj_name),
                        ("Multiply.inputs:b", scale, "double"),
                    ],
                },
            )

            controller.edit(
                graph_name,
                {
                    keys.CONNECT: [
                        ("ReadIndex.outputs:value", "Multiply.inputs:a"),
                        ("ReadTranslate.outputs:value", "BreakTranslate.inputs:tuple"),
                        ("Multiply.outputs:product", "MakeTranslate.inputs:x"),
                        ("BreakTranslate.outputs:y", "MakeTranslate.inputs:y"),
                        ("BreakTranslate.outputs:z", "MakeTranslate.inputs:z"),
                        ("MakeTranslate.outputs:tuple", "WriteTranslate.inputs:value"),
                    ],
                },
            )

        # cubes[0].GetStage().Export("c:/tmp/test.usda")

        for cube in cubes:
            translate = cube.GetAttribute(attr_name).Get()
            self.assertEqual(translate[0], 0)

        await og.Controller.evaluate()

        for cube in cubes:
            index = cube.GetAttribute(index_name).Get()
            translate = cube.GetAttribute(attr_name).Get()
            self.assertEqual(translate[0], index * scale)

    # ----------------------------------------------------------------------
    async def test_read_prim_node_default_time_code_upgrades(self):
        """
        Tests that read prim node variants property upgrade their time code property
        to use NAN as a default
        """
        app = omni.kit.app.get_app()

        nodes = [
            "ReadPrim",
            "ReadPrims",
            "ReadPrimAttribute",
            "ReadPrimAttributes",
            "ReadPrimBundle",
            "ReadPrimsBundle",
        ]

        # testing under different frame rates to validate the upgrade is correctly detected
        frame_rates = [12, 24, 30, 60]
        for frame_rate in frame_rates:
            with self.subTest(frame_rate=frame_rate):
                timeline = omni.timeline.get_timeline_interface()
                timeline.set_time_codes_per_second(frame_rate)
                await app.next_update_async()

                file_path = os.path.join(os.path.dirname(__file__), "data", "TestReadPrimNodeVariants.usda")
                stage = omni.usd.get_context().get_stage()

                # create a prim and add a file reference
                prim = stage.DefinePrim("/Ref")
                # when we make the references, there will be deprecation warnings
                prim.GetReferences().AddReference(file_path)

                self.assertEqual(stage.GetTimeCodesPerSecond(), frame_rate)

                await omni.kit.app.get_app().next_update_async()

                for node in nodes:
                    attr = og.Controller.attribute(f"/Ref/ActionGraph/{node}.inputs:usdTimecode")
                    self.assertTrue(isnan(attr.get()))

                await omni.usd.get_context().new_stage_async()

    # ----------------------------------------------------------------------
    async def test_is_prim_active(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        contents = Usd.Stage.CreateInMemory("payload.usd")
        contents.DefinePrim("/payload/A", "Xform")
        payload = stage.DefinePrim("/payload", "Xform")
        payload.GetPayloads().AddPayload(Sdf.Payload(contents.GetRootLayer().identifier, "/payload"))

        keys = og.Controller.Keys
        controller = og.Controller()
        (graph, (node,), _, _) = controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: [("IsActive", "omni.graph.nodes.IsPrimActive")],
            },
        )
        await controller.evaluate(graph)

        rel = stage.GetRelationshipAtPath("/TestGraph/IsActive.inputs:primTarget")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/payload/A")
        await controller.evaluate(graph)

        out = node.get_attribute("outputs:active")
        self.assertEqual(out.get(), True)

        # Note: currently the node will raise an error if the prim isn't in the stage as well as set active to false
        payload.Unload()
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        out = node.get_attribute("outputs:active")
        self.assertEqual(out.get(), False)

    # -------------------------------------------------------------------------------
    async def test_get_graph_target_prim(self):
        """Test that the GetGraphTargetPrim node outputs the expected graph target prim"""

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        (graph, (_graph_target_node, path_node), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("GetGraphTargetPrim", "omni.graph.nodes.GetGraphTargetPrim"),
                    ("GetPrimPath", "omni.graph.nodes.GetPrimPath"),
                ],
                keys.CONNECT: [("GetGraphTargetPrim.outputs:prim", "GetPrimPath.inputs:prim")],
            },
        )

        # no instances, it should return the graph prim
        await og.Controller.evaluate(graph)
        self.assertEqual(self.TEST_GRAPH_PATH, path_node.get_attribute("outputs:primPath").get())

        num_instances = 5

        # create instances
        for i in range(0, num_instances):
            prim_name = f"/World/Prim_{i}"
            stage.DefinePrim(prim_name)
            OmniGraphSchemaTools.applyOmniGraphAPI(stage, prim_name, self.TEST_GRAPH_PATH)

        # rerun the graph, this time evaluating instances
        await og.Controller.evaluate(graph)

        for i in range(0, num_instances):
            self.assertEqual(f"/World/Prim_{i}", path_node.get_attribute("outputs:primPath").get(instance=i))

    async def test_construct_array_invalid_array_size(self):
        """Test that setting an invalid value on OgnConstructArray.arraySize does not crash"""
        # Ideally this would be done with the following test in the .ogn file, but the node parser
        # applies the minimum / maximum attribute limits when parsing the tests, which means that
        # we cannot define tests for invalid inputs in the .ogn file
        # {
        #     "inputs:arraySize": -1, "inputs:arrayType": "Int64",
        #     "outputs:array": {"type": "int64[]", "value": []}
        # }
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            nodes,
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("ConstructArray", "omni.graph.nodes.ConstructArray")],
                keys.SET_VALUES: [
                    ("ConstructArray.inputs:arraySize", -1),
                    ("ConstructArray.inputs:arrayType", "int[]"),
                ],
            },
        )

        # Evaluate the graph once to ensure the node has a Database created
        await controller.evaluate(graph)

        result = nodes[0].get_attribute("outputs:array").get()
        expected: list[int] = []
        self.assertListEqual(expected, list(result))

    async def test_get_prim_local_to_world_empty(self):
        """Regression test for GetPrimLocalToWorldTransform"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            _,
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("TestWorld", "omni.graph.nodes.GetPrimLocalToWorldTransform")],
                keys.SET_VALUES: [
                    ("TestWorld.inputs:usePath", False),
                ],
            },
        )
        with ogts.ExpectedError():
            await controller.evaluate(graph)

    async def test_read_unauthored_schema_attrs(self):
        """Regression test for ReadPrimAttribute when reading unauthored schema attrs"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (read,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("Read", "omni.graph.nodes.ReadPrimAttribute")],
                keys.CREATE_PRIMS: [("/World/Points", "Points")],
                keys.SET_VALUES: [
                    ("Read.inputs:prim", "/World/Points"),
                    ("Read.inputs:name", "widths"),
                ],
            },
        )

        await controller.evaluate(graph)

        result = read.get_attribute("outputs:value").get()
        expected: list[float] = []
        self.assertListEqual(expected, list(result))

    async def test_write_unauthored_schema_attrs(self):
        """Regression test for WritePrimAttribute when writing unauthored schema attrs"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            _,
            (prim,),
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("Write", "omni.graph.nodes.WritePrimAttribute")],
                keys.CREATE_PRIMS: [("/World/Points", "Points")],
                keys.SET_VALUES: [
                    ("Write.inputs:prim", "/World/Points"),
                    ("Write.inputs:name", "widths"),
                    ("Write.inputs:value", [1.0, 2.0, 3.0]),
                ],
            },
        )

        await controller.evaluate(graph)

        result = prim.GetAttribute("widths").Get()
        expected: list[float] = [1.0, 2.0, 3.0]
        self.assertListEqual(expected, list(result))

    # -------------------------------------------------------------------------------
    async def test_repeat_resolve(self):
        """Regression test for OM-104677 - resolve outputs repeatedly"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            nodes,
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Ceil", "omni.graph.nodes.Ceil"),
                    ("Divide", "omni.graph.nodes.Divide"),
                    ("EachZero", "omni.graph.nodes.EachZero"),
                    ("Floor", "omni.graph.nodes.Floor"),
                    ("Noise", "omni.graph.nodes.Noise"),
                    ("Normalize", "omni.graph.nodes.Normalize"),
                    ("Compare", "omni.graph.nodes.Compare"),
                    ("ToBool", "omni.graph.nodes.ToBool"),
                    ("ToDouble", "omni.graph.nodes.ToDouble"),
                    ("ToFloat", "omni.graph.nodes.ToFloat"),
                    ("ToHalf", "omni.graph.nodes.ToHalf"),
                    ("ToInt", "omni.graph.nodes.ToInt"),
                    ("ToInt64", "omni.graph.nodes.ToInt64"),
                    ("ToUchar", "omni.graph.nodes.ToUchar"),
                    ("ToUint", "omni.graph.nodes.ToUint"),
                    ("ToUint64", "omni.graph.nodes.ToUint64"),
                    ("TransformVector", "omni.graph.nodes.TransformVector"),
                    ("RotateVector", "omni.graph.nodes.RotateVector"),
                ]
            },
        )
        await controller.evaluate(graph)

        node_data = {
            self.TEST_GRAPH_PATH
            + "/Ceil": {
                "in_attrs": [("inputs:a", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 3, 0))],
                "out_attr": ("outputs:result", og.Type(og.BaseDataType.INT), og.Type(og.BaseDataType.INT, 3, 0)),
            },
            self.TEST_GRAPH_PATH
            + "/Divide": {
                "in_attrs": [
                    ("inputs:a", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 3, 0)),
                    ("inputs:b", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 3, 0)),
                ],
                "out_attr": ("outputs:result", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 3, 0)),
            },
            self.TEST_GRAPH_PATH
            + "/EachZero": {
                "in_attrs": [("inputs:value", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 1, 1))],
                "out_attr": ("outputs:result", og.Type(og.BaseDataType.BOOL), og.Type(og.BaseDataType.BOOL, 1, 1)),
            },
            self.TEST_GRAPH_PATH
            + "/Floor": {
                "in_attrs": [("inputs:a", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 3, 0))],
                "out_attr": ("outputs:result", og.Type(og.BaseDataType.INT), og.Type(og.BaseDataType.INT, 3, 0)),
            },
            self.TEST_GRAPH_PATH
            + "/Noise": {
                "in_attrs": [("inputs:position", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 1, 1))],
                "out_attr": ("outputs:result", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 1, 1)),
            },
            self.TEST_GRAPH_PATH
            + "/Normalize": {
                "in_attrs": [
                    ("inputs:vector", og.Type(og.BaseDataType.FLOAT, 3, 0), og.Type(og.BaseDataType.FLOAT, 3, 1))
                ],
                "out_attr": (
                    "outputs:result",
                    og.Type(og.BaseDataType.FLOAT, 3, 0),
                    og.Type(og.BaseDataType.FLOAT, 3, 1),
                ),
            },
            self.TEST_GRAPH_PATH
            + "/Compare": {
                "in_attrs": [
                    ("inputs:a", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 1, 1)),
                    ("inputs:b", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 1, 1)),
                ],
                "out_attr": ("outputs:result", og.Type(og.BaseDataType.BOOL), og.Type(og.BaseDataType.BOOL, 1, 1)),
            },
            self.TEST_GRAPH_PATH
            + "/ToBool": {
                "in_attrs": [("inputs:value", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 1, 1))],
                "out_attr": ("outputs:converted", og.Type(og.BaseDataType.BOOL), og.Type(og.BaseDataType.BOOL, 1, 1)),
            },
            self.TEST_GRAPH_PATH
            + "/ToDouble": {
                "in_attrs": [("inputs:value", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 3, 0))],
                "out_attr": (
                    "outputs:converted",
                    og.Type(og.BaseDataType.DOUBLE),
                    og.Type(og.BaseDataType.DOUBLE, 3, 0),
                ),
            },
            self.TEST_GRAPH_PATH
            + "/ToFloat": {
                "in_attrs": [("inputs:value", og.Type(og.BaseDataType.DOUBLE), og.Type(og.BaseDataType.DOUBLE, 3, 0))],
                "out_attr": ("outputs:converted", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 3, 0)),
            },
            self.TEST_GRAPH_PATH
            + "/ToHalf": {
                "in_attrs": [("inputs:value", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 3, 0))],
                "out_attr": ("outputs:converted", og.Type(og.BaseDataType.HALF), og.Type(og.BaseDataType.HALF, 3, 0)),
            },
            self.TEST_GRAPH_PATH
            + "/ToInt": {
                "in_attrs": [("inputs:value", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 3, 0))],
                "out_attr": ("outputs:converted", og.Type(og.BaseDataType.INT), og.Type(og.BaseDataType.INT, 3, 0)),
            },
            self.TEST_GRAPH_PATH
            + "/ToInt64": {
                "in_attrs": [("inputs:value", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 1, 1))],
                "out_attr": ("outputs:converted", og.Type(og.BaseDataType.INT64), og.Type(og.BaseDataType.INT64, 1, 1)),
            },
            self.TEST_GRAPH_PATH
            + "/ToUchar": {
                "in_attrs": [("inputs:value", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 1, 1))],
                "out_attr": ("outputs:converted", og.Type(og.BaseDataType.UCHAR), og.Type(og.BaseDataType.UCHAR, 1, 1)),
            },
            self.TEST_GRAPH_PATH
            + "/ToUint": {
                "in_attrs": [("inputs:value", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 1, 1))],
                "out_attr": ("outputs:converted", og.Type(og.BaseDataType.UINT), og.Type(og.BaseDataType.UINT, 1, 1)),
            },
            self.TEST_GRAPH_PATH
            + "/ToUint64": {
                "in_attrs": [("inputs:value", og.Type(og.BaseDataType.FLOAT), og.Type(og.BaseDataType.FLOAT, 1, 1))],
                "out_attr": (
                    "outputs:converted",
                    og.Type(og.BaseDataType.UINT64),
                    og.Type(og.BaseDataType.UINT64, 1, 1),
                ),
            },
            self.TEST_GRAPH_PATH
            + "/TransformVector": {
                "in_attrs": [
                    (
                        "inputs:matrix",
                        og.Type(og.BaseDataType.DOUBLE, 16, 0, og.AttributeRole.MATRIX),
                        og.Type(og.BaseDataType.DOUBLE, 16, 1, og.AttributeRole.MATRIX),
                    ),
                    (
                        "inputs:vector",
                        og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.VECTOR),
                        og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.VECTOR),
                    ),
                ],
                "out_attr": (
                    "outputs:result",
                    og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.VECTOR),
                    og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.VECTOR),
                ),
            },
            self.TEST_GRAPH_PATH
            + "/RotateVector": {
                "in_attrs": [
                    (
                        "inputs:rotation",
                        og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.VECTOR),
                        og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.VECTOR),
                    ),
                    (
                        "inputs:vector",
                        og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.VECTOR),
                        og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.VECTOR),
                    ),
                ],
                "out_attr": (
                    "outputs:result",
                    og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.VECTOR),
                    og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.VECTOR),
                ),
            },
        }

        for node in nodes:
            data = node_data[node.get_prim_path()]
            out_data = data["out_attr"]
            out_attr = node.get_attribute(out_data[0])
            for in_data in data["in_attrs"]:
                in_attr = node.get_attribute(in_data[0])
                in_attr.set_resolved_type(in_data[1])

            await controller.evaluate(graph)
            self.assertEqual(out_attr.get_resolved_type(), out_data[1])

            for in_data in data["in_attrs"]:
                in_attr = node.get_attribute(in_data[0])
                in_attr.set_resolved_type(og.Type(og.BaseDataType.UNKNOWN))
                in_attr.set_resolved_type(in_data[2])

            await controller.evaluate(graph)
            self.assertEqual(out_attr.get_resolved_type(), out_data[2])

    # -------------------------------------------------------------------------------
    async def test_array_nodes_invalid_index(self):
        """Test that setting an invalid index on array nodes will return an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            nodes,
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("ArrayIndex", "omni.graph.nodes.ArrayIndex"),
                    ("ArrayRemoveIndex", "omni.graph.nodes.ArrayRemoveIndex"),
                    ("ArraySetIndex", "omni.graph.nodes.ArraySetIndex"),
                ],
                keys.SET_VALUES: [
                    ("ArrayIndex.inputs:array", {"type": "int[]", "value": [1, 2, 3]}),
                    ("ArrayRemoveIndex.inputs:array", {"type": "int[]", "value": [1, 2, 3]}),
                    ("ArraySetIndex.inputs:array", {"type": "int[]", "value": [1, 2, 3]}),
                ],
            },
        )

        await controller.evaluate(graph)

        # Set indices above and below the max ranges
        for node in nodes:
            og.Controller.set(("inputs:index", node), -4)
            with ogts.ExpectedError():
                await controller.evaluate(graph)
            og.Controller.set(("inputs:index", node), 4)
            with ogts.ExpectedError():
                await controller.evaluate(graph)
            self.assertEqual(len(node.get_compute_messages(og.ERROR)), 2)

    # -------------------------------------------------------------------------------
    async def test_construct_array_node(self):
        """Additional tests for make array node when 'auto' settings are used"""

        controller = og.Controller()
        keys = controller.Keys

        types = [
            ("Bool", "bool[]"),
            ("Double", "double[]"),
            ("Float", "float[]"),
            ("Half", "half[]"),
            ("Int", "int[]"),
            ("Int64", "int64[]"),
            ("Token", "token[]"),
            ("UChar", "uchar[]"),
            ("UInt", "uint[]"),
            ("UInt64", "uint64[]"),
            ("Double2", "double2[]"),
            ("Double3", "double3[]"),
            ("Double4", "double4[]"),
            ("Matrix2d", "matrix2d[]"),
            ("Matrix3d", "matrix3d[]"),
            ("Matrix4d", "matrix4d[]"),
            ("Float2", "float2[]"),
            ("Float3", "float3[]"),
            ("Float4", "float4[]"),
            ("Half2", "half2[]"),
            ("Half3", "half3[]"),
            ("Half4", "half4[]"),
            ("Int2", "int2[]"),
            ("Int3", "int3[]"),
            ("Int4", "int4[]"),
            ("Timecode", "timecode[]"),
            ("Frame", "frame4d[]"),
            ("Color3d", "color3d[]"),
            ("Color3f", "color3f[]"),
            ("Color3h", "color3h[]"),
            ("Color4d", "color4d[]"),
            ("Color4f", "color4f[]"),
            ("Color4h", "color4h[]"),
            ("Normal3d", "normal3d[]"),
            ("Normal3f", "normal3f[]"),
            ("Normal3h", "normal3h[]"),
            ("Point3d", "point3d[]"),
            ("Point3f", "point3f[]"),
            ("Point3h", "point3h[]"),
            ("Quatd", "quatd[]"),
            ("Quatf", "quatf[]"),
            ("Quath", "quath[]"),
            ("TexCoord2d", "texCoord2d[]"),
            ("TexCoord2f", "texCoord2f[]"),
            ("TexCoord2h", "texCoord2h[]"),
            ("TexCoord3d", "texCoord3d[]"),
            ("TexCoord3f", "texCoord3f[]"),
            ("TexCoord3h", "texCoord3h[]"),
            ("Vector3d", "vector3d[]"),
            ("Vector3f", "vector3f[]"),
            ("Vector3h", "vector3h[]"),
        ]

        (graph, _, _, node_map) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    (f"Const{i}", f"omni.graph.nodes.Constant{name}") for (i, (name, _)) in enumerate(types)
                ]
                + [(f"MakeArray{i}", "omni.graph.nodes.ConstructArray") for i in range(len(types))],
                keys.SET_VALUES: [(f"MakeArray{i}.inputs:arraySize", 2) for i in range(len(types))]
                + [(f"MakeArray{i}.inputs:arrayType", "auto") for i in range(len(types))],
                keys.CONNECT: [(f"Const{i}.inputs:value", f"MakeArray{i}.inputs:input0") for i in range(len(types))],
            },
        )

        await controller.evaluate(graph)

        # validate the resolved type of each array node is what is expected
        for i, (_, str_type) in enumerate(types):
            node = node_map[f"MakeArray{i}"]
            resolved_type = node.get_attribute("outputs:array").get_resolved_type()
            sdf_type = og.AttributeType.sdf_type_name_from_type(resolved_type)
            self.assertEquals(str_type, sdf_type)

    # -------------------------------------------------------------------------------
    async def test_string_nodes_invalid_index(self):
        """Test that setting an invalid index on string nodes will return an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            nodes,
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("GetString", "omni.graph.nodes.GetString"),
                    ("RemoveString", "omni.graph.nodes.RemoveString"),
                ],
                keys.SET_VALUES: [
                    ("GetString.inputs:string", {"type": "string", "value": "Test"}),
                    ("RemoveString.inputs:string", {"type": "string", "value": "Test"}),
                ],
            },
        )

        await controller.evaluate(graph)

        # Set indices above and below the max ranges
        for node in nodes:
            og.Controller.set(("inputs:index", node), -5)
            with ogts.ExpectedError():
                await controller.evaluate(graph)
            og.Controller.set(("inputs:index", node), 5)
            with ogts.ExpectedError():
                await controller.evaluate(graph)
            self.assertNotEqual(node.get_compute_messages(og.Severity.ERROR), [])

    async def test_capitalize_string_invalid_inputs(self):
        """Test that setting invalid inputs on CapitalizeString will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (node,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("CapitalizeString", "omni.graph.nodes.CapitalizeString")],
                keys.SET_VALUES: [
                    ("CapitalizeString.inputs:string", {"type": "string", "value": "Test"}),
                    ("CapitalizeString.inputs:operation", "UpperCase"),
                ],
            },
        )

        # Test that condition must match length of input values
        og.Controller.set(("inputs:operation", node), "INVALID")
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertNotEqual(node.get_compute_messages(og.Severity.ERROR), [])

    async def test_build_string_name_invalid_inputs(self):
        """Test that setting invalid inputs on BuildString will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (node,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("BuildString", "omni.graph.nodes.BuildString")],
                keys.SET_VALUES: [
                    ("BuildString.inputs:a", {"type": "token[]", "value": ["A", "B", "C"]}),
                    ("BuildString.inputs:b", {"type": "token[]", "value": ["A", "B", "C"]}),
                ],
            },
        )

        # Test that condition must match length of input values
        og.Controller.set(("inputs:b", node), ["A", "B"])
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertNotEqual(node.get_compute_messages(og.Severity.ERROR), [])

    async def test_build_string_name_invalid_resolve(self):
        """Test that setting inputs to invalid resolution combinations on BuildString will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (string_node, token_node, array_node, array_str_node),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("BuildString_string", "omni.graph.nodes.BuildString"),
                    ("BuildString_token", "omni.graph.nodes.BuildString"),
                    ("BuildString_array", "omni.graph.nodes.BuildString"),
                    ("BuildString_array_str", "omni.graph.nodes.BuildString"),
                ],
                keys.SET_VALUES: [
                    ("BuildString_string.inputs:b", {"type": "string", "value": "A"}),
                    ("BuildString_token.inputs:b", {"type": "token", "value": "B"}),
                    ("BuildString_array.inputs:b", {"type": "token[]", "value": ["A", "B", "C"]}),
                    ("BuildString_array_str.inputs:b", {"type": "string", "value": "A"}),
                ],
            },
        )

        await controller.evaluate(graph)

        # A:token B:string
        og.Controller.set(("inputs:a", string_node), {"type": "token", "value": "B"})
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertNotEqual(string_node.get_compute_messages(og.Severity.ERROR), [])

        # A:string B:token
        og.Controller.set(("inputs:a", token_node), {"type": "string", "value": "B"})
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertNotEqual(token_node.get_compute_messages(og.Severity.ERROR), [])

        # # A:string B:token[]
        og.Controller.set(("inputs:a", array_node), {"type": "string", "value": "B"})
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertNotEqual(array_node.get_compute_messages(og.Severity.ERROR), [])

        # # A:string B:token[]
        og.Controller.set(("inputs:a", array_str_node), {"type": "token[]", "value": ["A", "B", "C"]})
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertNotEqual(array_str_node.get_compute_messages(og.Severity.ERROR), [])

    async def test_append_string_name_invalid_inputs(self):
        """Test that setting invalid inputs on AppendString will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (node,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("AppendString", "omni.graph.nodes.AppendString")],
                keys.SET_VALUES: [
                    ("AppendString.inputs:value", {"type": "token[]", "value": ["A", "B", "C"]}),
                    ("AppendString.inputs:suffix", {"type": "token[]", "value": ["A", "B", "C"]}),
                ],
            },
        )

        # Test that condition must match length of input values
        og.Controller.set(("inputs:suffix", node), ["A", "B"])
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertNotEqual(node.get_compute_messages(og.Severity.ERROR), [])

    # -------------------------------------------------------------------------------
    async def test_target_nodes_invalid_index(self):
        """Test that setting an invalid index on target nodes will return an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            nodes,
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("GetTargets", "omni.graph.nodes.GetTargets"),
                    ("RemoveTarget", "omni.graph.nodes.RemoveTarget"),
                    ("SetTarget", "omni.graph.nodes.SetTarget"),
                ],
                keys.SET_VALUES: [
                    ("GetTargets.inputs:targets", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("RemoveTarget.inputs:targets", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("SetTarget.inputs:targets", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("SetTarget.inputs:setTarget", ["/World/Foo"]),
                ],
            },
        )

        await controller.evaluate(graph)

        # Set indices above and below the max ranges
        for node in nodes:
            with ogts.ExpectedError():
                og.Controller.set(("inputs:index", node), -4)
                await controller.evaluate(graph)
            with ogts.ExpectedError():
                og.Controller.set(("inputs:index", node), 4)
                await controller.evaluate(graph)
            self.assertEqual(len(node.get_compute_messages(og.ERROR)), 2)

    async def test_compare_targets_resolve(self):
        """Test compareEach on CompareTargets re-resolve output"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (node,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("CompareTargets", "omni.graph.nodes.CompareTargets")],
                keys.SET_VALUES: [
                    ("CompareTargets.inputs:a", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("CompareTargets.inputs:b", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                ],
            },
        )

        out_attr = node.get_attribute("outputs:result")

        # compare the entire array and output a single value
        await controller.evaluate(graph)
        self.assertEqual(out_attr.get_resolved_type(), og.Type(og.BaseDataType.BOOL))

        # compare each array per-element
        og.Controller.set(("inputs:compareEach", node), True)
        await controller.evaluate(graph)
        self.assertEqual(out_attr.get_resolved_type(), og.Type(og.BaseDataType.BOOL, 1, 1))

    async def test_compare_targets_invalid_inputs(self):
        """Test that setting invalid inputs on CompareTargets will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (bad_array, bad_op_array, bad_op_scalar),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("CompareTargets_bad_array", "omni.graph.nodes.CompareTargets"),
                    ("CompareTargets_bad_op_array", "omni.graph.nodes.CompareTargets"),
                    ("CompareTargets_bad_op_scalar", "omni.graph.nodes.CompareTargets"),
                ],
                keys.SET_VALUES: [
                    ("CompareTargets_bad_array.inputs:a", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("CompareTargets_bad_array.inputs:b", ["/World/Foo"]),
                    ("CompareTargets_bad_op_array.inputs:a", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("CompareTargets_bad_op_array.inputs:b", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("CompareTargets_bad_op_scalar.inputs:a", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("CompareTargets_bad_op_scalar.inputs:b", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                ],
            },
        )

        await controller.evaluate(graph)

        # Test that two inputs of different sizes will fail
        with ogts.ExpectedError():
            og.Controller.set(("inputs:compareEach", bad_array), True)
            await controller.evaluate(graph)
        self.assertEqual(len(bad_array.get_compute_messages(og.ERROR)), 1)

        # Test that a comparing two arrays element wise with an invalid operation will fail
        with ogts.ExpectedError():
            og.Controller.set(("inputs:compareEach", bad_op_array), True)
            og.Controller.set(("inputs:operation", bad_op_array), ">")
            await controller.evaluate(graph)
        self.assertEqual(len(bad_op_array.get_compute_messages(og.ERROR)), 1)

        # Test that a comparing two arrays with an invalid operation will fail
        with ogts.ExpectedError():
            og.Controller.set(("inputs:operation", bad_op_scalar), ">")
            await controller.evaluate(graph)
        self.assertEqual(len(bad_op_scalar.get_compute_messages(og.ERROR)), 1)

    async def test_select_target_if_invalid_inputs(self):
        """Test that setting invalid inputs on SelectTargetIf will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (node,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("SelectTargetIf", "omni.graph.nodes.SelectTargetIf")],
                keys.SET_VALUES: [
                    ("SelectTargetIf.inputs:ifTrue", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("SelectTargetIf.inputs:ifFalse", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("SelectTargetIf.inputs:condition", {"type": "bool[]", "value": [True, False, True]}),
                ],
            },
        )

        # Test that condition must match length of input values
        with ogts.ExpectedError():
            og.Controller.set(("inputs:condition", node), [True])
            await controller.evaluate(graph)
        self.assertEqual(len(node.get_compute_messages(og.ERROR)), 1)

    async def test_replace_targets_if_invalid_inputs(self):
        """Test that setting invalid inputs on ReplaceTargets will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (node,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("ReplaceTargets", "omni.graph.nodes.ReplaceTargets")],
                keys.SET_VALUES: [
                    ("ReplaceTargets.inputs:targets", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("ReplaceTargets.inputs:replaceTargets", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("ReplaceTargets.inputs:setTargets", ["/Foo", "/Bar", "/Rar"]),
                ],
            },
        )
        # Test that condition must match length of input values
        with ogts.ExpectedError():
            og.Controller.set(("inputs:setTargets", node), ["/Foo"])
            await controller.evaluate(graph)
        self.assertEqual(len(node.get_compute_messages(og.ERROR)), 1)

    async def test_append_target_paths_invalid_inputs(self):
        """Test that setting invalid inputs on AppendTargetPaths will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (node,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("AppendTargetPaths", "omni.graph.nodes.AppendTargetPaths")],
                keys.SET_VALUES: [
                    ("AppendTargetPaths.inputs:rootTargets", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("AppendTargetPaths.inputs:input0", {"type": "token[]", "value": ["A", "B", "C"]}),
                ],
            },
        )

        # Test that condition must match length of input values
        with ogts.ExpectedError():
            og.Controller.set(("inputs:input0", node), ["A"])
            await controller.evaluate(graph)
        self.assertEqual(len(node.get_compute_messages(og.ERROR)), 1)

    async def test_replace_target_name_invalid_inputs(self):
        """Test that setting invalid inputs on ReplaceTargetName will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (node,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("ReplaceTargetName", "omni.graph.nodes.ReplaceTargetName")],
                keys.SET_VALUES: [
                    ("ReplaceTargetName.inputs:targets", ["/World/Foo", "/World/Bar", "/World/Rar"]),
                    ("ReplaceTargetName.inputs:newName", {"type": "token[]", "value": ["A", "B", "C"]}),
                ],
            },
        )

        # Test that condition must match length of input values
        with ogts.ExpectedError():
            og.Controller.set(("inputs:newName", node), ["A"])
            await controller.evaluate(graph)
        self.assertEqual(len(node.get_compute_messages(og.ERROR)), 1)

    # -------------------------------------------------------------------------------
    async def test_compare_invalid_inputs(self):
        """Test that setting invalid inputs on Compare will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (bad_op, bad_op_token, bad_type, bad_tuples),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Compare_bad_op", "omni.graph.nodes.Compare"),
                    ("Compare_bad_op_token", "omni.graph.nodes.Compare"),
                    ("Compare_bad_base_type", "omni.graph.nodes.Compare"),
                    ("Compare_bad_tuples", "omni.graph.nodes.Compare"),
                ],
                keys.SET_VALUES: [
                    ("Compare_bad_op.inputs:a", {"type": "int", "value": 5}),
                    ("Compare_bad_op.inputs:b", {"type": "int", "value": 3}),
                    ("Compare_bad_op.inputs:operation", "=="),
                    ("Compare_bad_op_token.inputs:a", {"type": "token", "value": "abc"}),
                    ("Compare_bad_op_token.inputs:b", {"type": "token", "value": "def"}),
                    ("Compare_bad_op_token.inputs:operation", "=="),
                    ("Compare_bad_base_type.inputs:a", {"type": "int", "value": 5}),
                    ("Compare_bad_tuples.inputs:a", {"type": "int", "value": 5}),
                ],
            },
        )

        # Set a invalid operation
        og.Controller.set(("inputs:operation", bad_op), "%")
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertEqual(len(bad_op.get_compute_messages(og.ERROR)), 1)

        # Set a invalid operation for a token
        og.Controller.set(("inputs:operation", bad_op_token), ">")
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertEqual(len(bad_op_token.get_compute_messages(og.ERROR)), 1)

        # Set mismatched types
        og.Controller.set(("inputs:b", bad_type), {"type": "double", "value": 3})
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertEqual(len(bad_type.get_compute_messages(og.ERROR)), 1)

        # Set mismatched tuple counts
        og.Controller.set(("inputs:b", bad_tuples), {"type": "int[3]", "value": [1, 2, 3]})
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertEqual(len(bad_tuples.get_compute_messages(og.ERROR)), 1)

    async def test_construct_array_invalid_inputs(self):
        """Test that setting invalid inputs on ConstructArray will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (mixed_type, const_double, const_float, change_type),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("ConstructArray_mixed_types", "omni.graph.nodes.ConstructArray"),
                    ("ConstDouble", "omni.graph.nodes.ConstantDouble"),
                    ("ConstFloat", "omni.graph.nodes.ConstantFloat"),
                    ("ConstructArray_change_type", "omni.graph.nodes.ConstructArray"),
                ]
            },
        )
        # Evaluate the graph once to ensure the node has a Database created
        await controller.evaluate(graph)

        # create a new dynamic input
        controller.create_attribute(
            mixed_type,
            "inputs:input1",
            "any",
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
            None,
            og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY,
        )

        # Act: evaluate the graph
        await controller.evaluate(graph)

        # Connect mismatching base types
        with ogts.ExpectedError():
            double_out_attr = controller.attribute("inputs:value", const_double)
            float_out_attr = controller.attribute("inputs:value", const_float)
            input_0_attr = controller.attribute("inputs:input0", mixed_type)
            input_1_attr = controller.attribute("inputs:input1", mixed_type)
            og.Controller.connect(double_out_attr, input_0_attr)
            og.Controller.connect(float_out_attr, input_1_attr)
            await controller.evaluate(graph)
        self.assertEqual(len(mixed_type.get_compute_messages(og.ERROR)), 1)

        # change the array type after its been assumed
        with ogts.ExpectedError():
            input_0_attr = controller.attribute("inputs:input0", change_type)
            og.Controller.connect(double_out_attr, input_0_attr)
            og.Controller.set(("inputs:arrayType", change_type), "bool[]")
            await controller.evaluate(graph)
        self.assertEqual(len(change_type.get_compute_messages(og.ERROR)), 1)

    async def test_select_if_invalid_inputs(self):
        """Test that setting invalid inputs on SelectIf will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (node,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("SelectIf", "omni.graph.nodes.SelectIf")],
                keys.SET_VALUES: [
                    ("SelectIf.inputs:condition", {"type": "bool", "value": True}),
                    ("SelectIf.inputs:ifTrue", {"type": "int", "value": 5}),
                    ("SelectIf.inputs:ifFalse", {"type": "int[3]", "value": [1, 2, 3]}),
                ],
            },
        )

        # Test that condition must match length of input values
        with ogts.ExpectedError():
            await controller.evaluate(graph)
        self.assertEqual(len(node.get_compute_messages(og.ERROR)), 1)

    # -------------------------------------------------------------------------------
    async def test_log_invalid_inputs(self):
        """Test that setting invalid inputs on Logarithm node will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (node,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("Log", "omni.graph.nodes.Logarithm")],
                keys.SET_VALUES: [("Log.inputs:base", 3.0)],
            },
        )

        test_types = [
            {"type": "double", "value": 9.0},
            {"type": "double[3]", "value": [9.0, 9.0, 9.0]},
            {"type": "half", "value": 9.0},
            {"type": "half[3]", "value": [9.0, 9.0, 9.0]},
            {"type": "int", "value": 9},
            {"type": "int[3]", "value": [9, 9, 9]},
        ]

        await controller.evaluate(graph)

        # Set indices above and below the max ranges
        for test_type in test_types:
            og.Controller.set(("inputs:value", node), test_type)
            og.Controller.set(("inputs:base", node), -1)
            with ogts.ExpectedError():
                await controller.evaluate(graph)
            self.assertEqual(len(node.get_compute_messages(og.ERROR)), 1)
            og.Controller.set(("inputs:base", node), 0)
            with ogts.ExpectedError():
                await controller.evaluate(graph)
            self.assertEqual(len(node.get_compute_messages(og.ERROR)), 1)
            og.Controller.set(("inputs:base", node), 1)
            with ogts.ExpectedError():
                await controller.evaluate(graph)
            self.assertEqual(len(node.get_compute_messages(og.ERROR)), 1)

    # -------------------------------------------------------------------------------
    async def test_transform_nodes_invalid_rotation_order(self):
        """Test that setting invalid rotation order on transform nodes will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        (
            graph,
            (nodes),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("GetMatrix4Quaternion", "omni.graph.nodes.GetMatrix4Quaternion"),
                    ("GetMatrix4Rotation", "omni.graph.nodes.GetMatrix4Rotation"),
                    ("GetMatrix4RotationMatrix", "omni.graph.nodes.GetMatrix4RotationMatrix"),
                    ("MakeTransform", "omni.graph.nodes.MakeTransform"),
                    ("RotateVector", "omni.graph.nodes.RotateVector"),
                    ("SetMatrix4Rotation", "omni.graph.nodes.SetMatrix4Rotation"),
                ],
                keys.SET_VALUES: [
                    ("GetMatrix4Quaternion.inputs:matrix", {"type": "vectord[3]", "value": [1, 2, 3]}),
                    ("GetMatrix4Rotation.inputs:matrix", {"type": "quatd[4]", "value": [1, 2, 3, 4]}),
                    ("GetMatrix4RotationMatrix.inputs:matrix", {"type": "vectord[3]", "value": [1, 2, 3]}),
                    ("RotateVector.inputs:rotation", {"type": "vectord[3]", "value": [1, 2, 3]}),
                    ("RotateVector.inputs:vector", {"type": "vectord[3]", "value": [1, 2, 3]}),
                    ("SetMatrix4Rotation.inputs:matrix", {"type": "matrixd[4]", "value": matrix}),
                    ("SetMatrix4Rotation.inputs:rotationAngle", {"type": "vectord[3]", "value": [1, 2, 3]}),
                ],
            },
        )

        await controller.evaluate(graph)

        # Set rotation order to an invalid value should result in an error
        for node in nodes:
            og.Controller.set(("inputs:rotationOrder", node), "INVALID")
            with ogts.ExpectedError():
                await controller.evaluate(graph)

    async def test_rotate_vector_invalid_inputs(self):
        """Test that setting invalid inputs on RotateVector will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (bad_type_euler, bad_type_quat, bad_array, bad_array_half),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("bad_type_euler", "omni.graph.nodes.RotateVector"),
                    ("bad_type_quat", "omni.graph.nodes.RotateVector"),
                    ("bad_array", "omni.graph.nodes.RotateVector"),
                    ("bad_array_half", "omni.graph.nodes.RotateVector"),
                ],
                keys.SET_VALUES: [
                    ("bad_type_euler.inputs:rotation", {"type": "vectord[3]", "value": [1, 2, 3]}),
                    ("bad_type_quat.inputs:rotation", {"type": "quatd[4]", "value": [1, 2, 3, 4]}),
                    ("bad_array.inputs:rotation", {"type": "vectord[3][]", "value": [[1, 2, 3]]}),
                    ("bad_array_half.inputs:rotation", {"type": "vectorh[3][]", "value": [[1, 2, 3]]}),
                ],
            },
        )

        await controller.evaluate(graph)

        # Test that sending different types when using euler angles results in an error
        og.Controller.set(("inputs:vector", bad_type_euler), {"type": "vectorh[3]", "value": [1, 2, 3]})
        with ogts.ExpectedError():
            await controller.evaluate(graph)

        # Test that sending different types when using quaternions results in an error
        og.Controller.set(("inputs:vector", bad_type_quat), {"type": "vectorf[3]", "value": [1, 2, 3]})
        with ogts.ExpectedError():
            await controller.evaluate(graph)

        # Test that sending different array depths when using non half types results in an error
        og.Controller.set(("inputs:vector", bad_array), {"type": "vectord[3][]", "value": [[1, 2, 3], [1, 2, 3]]})
        with ogts.ExpectedError():
            await controller.evaluate(graph)

        # Test that sending different array depths when using half types results in an error
        og.Controller.set(("inputs:vector", bad_array_half), {"type": "vectorh[3][]", "value": [[1, 2, 3], [1, 2, 3]]})
        with ogts.ExpectedError():
            await controller.evaluate(graph)

    async def test_matrix_multiply_invalid_inputs(self):
        """Test that setting invalid inputs on MatrixMultiply will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (node,),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("MatrixMultiply", "omni.graph.nodes.MatrixMultiply")],
                keys.SET_VALUES: [("MatrixMultiply.inputs:a", {"type": "double[3]", "value": [0, 0, 0]})],
            },
        )

        await controller.evaluate(graph)

        # Test that setting mismatched tuples causes an error
        with ogts.ExpectedError():
            og.Controller.set(("inputs:b", node), {"type": "double[4]", "value": [1, 1, 1, 1]})
            await controller.evaluate(graph)

    async def test_set_matrix_rotation_invalid_inputs(self):
        """Test that setting invalid inputs on SetMatrix4Rotation will result in an error"""
        controller = og.Controller()
        keys = og.Controller.Keys

        matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        (
            graph,
            (bad_array_axis, bad_array_euler, bad_axis),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("bad_array_axis", "omni.graph.nodes.SetMatrix4Rotation"),
                    ("bad_array_euler", "omni.graph.nodes.SetMatrix4Rotation"),
                    ("bad_axis", "omni.graph.nodes.SetMatrix4Rotation"),
                ],
                keys.SET_VALUES: [
                    ("bad_array_axis.inputs:matrix", {"type": "matrixd[4][]", "value": [matrix]}),
                    ("bad_array_euler.inputs:matrix", {"type": "matrixd[4][]", "value": [matrix]}),
                    ("bad_axis.inputs:matrix", {"type": "matrixd[4]", "value": matrix}),
                    ("bad_axis.inputs:rotationAngle", {"type": "double", "value": 2.0}),
                ],
            },
        )

        await controller.evaluate(graph)

        # Test that sending different array lengths when using rotation axis results in an error
        og.Controller.set(("inputs:rotationAngle", bad_array_axis), {"type": "double[]", "value": [1, 2, 3]})
        with ogts.ExpectedError():
            await controller.evaluate(graph)

        # Test that sending different array lengths when using rotation axis results in an error
        og.Controller.set(
            ("inputs:rotationAngle", bad_array_euler), {"type": "vectord[3][]", "value": [[1, 2, 3], [1, 2, 3]]}
        )
        with ogts.ExpectedError():
            await controller.evaluate(graph)

        # Test that setting an invalid rotation axis
        og.Controller.set(("inputs:fixedRotationAxis", bad_axis), "INVALID")
        with ogts.ExpectedError():
            await controller.evaluate(graph)

    async def test_get_rotation_node_type_v1(self):
        """First version of GetMatrix4Rotation node used ZYX rotation order. Test that rotationOrder is set."""
        # load the test scene which contains a ReadPrim V1 node
        (result, error) = await ogts.load_test_file("TestGetMatrix4Rotation_v1.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)

        test_graph_path = "/World/TestGraph"
        test_graph = og.get_graph_by_path(test_graph_path)
        get_rotation = test_graph.get_node(test_graph_path + "/get_rotation")
        self.assertTrue(get_rotation.is_valid())

        self.assertEqual(get_rotation.get_attribute("inputs:rotationOrder").get(), "ZYX")
