# noqa: PLC0302

from typing import List

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test
from pxr import Sdf, Usd, UsdGeom

_debug = False


class TestReadPrimsIncremental(ogts.OmniGraphTestCase):
    """Unit tests for incremental behavior of the ReadPrimsV2 node in this extension"""

    async def test_read_prims_change_tracking_path_targets(self):
        """Test change tracking of omni.graph.nodes.ReadPrimsV2 using path targets"""
        await self._test_read_prims_change_tracking_impl(False)

    async def test_read_prims_change_tracking_path_pattern(self):
        """Test change tracking of omni.graph.nodes.ReadPrimsV2 using path pattern"""
        await self._test_read_prims_change_tracking_impl(True)

    async def _test_read_prims_change_tracking_impl(self, use_path_pattern):
        usd_context = omni.usd.get_context()
        stage: Usd.Stage = usd_context.get_stage()
        test_graph_path = "/World/TestGraph"

        controller = og.Controller()
        keys = og.Controller.Keys

        xcube = UsdGeom.Xform.Define(stage, "/XCube")
        UsdGeom.Xform.Define(stage, "/XCone")

        cube = ogts.create_cube(stage, "XCube/Cube", (1, 0, 0))
        cone = ogts.create_cone(stage, "XCone/Cone", (0, 1, 0))

        cube.GetAttribute("size").Set(100)
        cone.GetAttribute("radius").Set(50)
        cone.GetAttribute("height").Set(10)

        cube_path = str(cube.GetPath())
        cone_path = str(cone.GetPath())

        (graph, [read_prims_node, _], _, _) = controller.edit(
            test_graph_path,
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrimsV2"),
                    ("Inspector", "omni.graph.nodes.BundleInspector"),
                ],
                keys.CONNECT: [
                    ("Read.outputs_primsBundle", "Inspector.inputs:bundle"),
                ],
                keys.SET_VALUES: [
                    ("Inspector.inputs:print", False),
                ],
            },
        )

        if use_path_pattern:
            controller.edit(
                test_graph_path,
                {
                    keys.SET_VALUES: [
                        ("Read.inputs:pathPattern", "/X*/C*"),
                    ],
                },
            )
        else:
            omni.kit.commands.execute(
                "SetRelationshipTargets",
                relationship=stage.GetPropertyAtPath(f"{test_graph_path}/Read.inputs:prims"),
                targets=[cube_path, cone_path],
            )

        def get_attr(bundle, name):
            return bundle.get_attribute_by_name(name)

        def get_attr_value(bundle, name):
            return get_attr(bundle, name).get()

        def assert_attr_value(bundle, name, value):
            if isinstance(value, list):
                self.assertEqual(get_attr_value(bundle, name).tolist(), value)
            else:
                self.assertEqual(get_attr_value(bundle, name), value)

        def assert_attr_missing(bundle, name):
            self.assertFalse(get_attr(bundle, name).is_valid())

        def assert_stamp(bundle, stamp):
            assert_attr_value(bundle, "_debugStamp", stamp)

        def assert_stamp_missing(bundle):
            assert_attr_missing(bundle, "_debugStamp")

        def set_stamp(stamp):
            if _debug:
                print(f"### Setting debug stamp to {stamp}")
            controller.edit(test_graph_path, {keys.SET_VALUES: ("Read.inputs:_debugStamp", stamp)})

        def set_change_tracking(enable):
            controller.edit(test_graph_path, {keys.SET_VALUES: ("Read.inputs:enableChangeTracking", enable)})

        def get_expected_prim_attributes_count(prim, debug_stamp=False, bbox=False):
            n = len(prim.GetPropertyNames())
            n += 3  # sourcePrimPath, sourcePrimType, worldMatrix
            n -= 1  # remove "proxyPrim" which is skipped unless it has targets

            if debug_stamp:
                n += 1  # _debugStamp

            if bbox:
                n += 3  # bboxTransform, bboxCenter, bboxSize

            return n

        id_mat = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]

        # initial update
        set_stamp(10)

        await controller.evaluate()

        graph_context = graph.get_default_graph_context()

        container_rwbundle = graph_context.get_output_bundle(read_prims_node, "outputs_primsBundle")
        self.assertTrue(container_rwbundle.valid)
        self.assertFalse(container_rwbundle.is_read_only())

        bundle_factory = og.IBundleFactory.create()
        container = bundle_factory.get_const_bundle_from_path(graph_context, container_rwbundle.get_path())
        self.assertTrue(container.is_read_only())

        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 2)

        # check initial bundle output
        # full updates will have negative debug stamps on the container bundle
        assert_stamp(container, -10)

        cube_bundle = None
        cone_bundle = None

        for bundle in child_bundles:
            # reading attribute values from writable bundle will bump dirty ids, so make sure it is a read-only bundle.
            self.assertTrue(bundle.is_read_only())
            assert_stamp_missing(bundle)
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            path = get_attr_value(bundle, "sourcePrimPath")
            if path == cube_path:
                cube_bundle = bundle
                n_attrs = get_expected_prim_attributes_count(cube)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_attr_value(bundle, "sourcePrimType", "Cube")
                assert_attr_value(bundle, "size", 100)
                assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 0]])
            elif path == cone_path:
                cone_bundle = bundle
                n_attrs = get_expected_prim_attributes_count(cone)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_attr_value(bundle, "sourcePrimType", "Cone")
                assert_attr_value(bundle, "radius", 50)
                assert_attr_value(bundle, "height", 10)
                assert_attr_value(bundle, "primvars:displayColor", [[0, 1, 0]])
            else:
                self.fail(path)

        self.assertIsNotNone(cube_bundle)
        self.assertIsNotNone(cone_bundle)

        # empty update
        set_stamp(15)

        await controller.evaluate()

        # nothing should have been updated.
        assert_stamp(container, -10)

        container_bundle_name = container.get_name()
        cube_bundle_name = cube_bundle.get_name()
        cone_bundle_name = cone_bundle.get_name()

        dirtyid_interface = og._og_unstable.IDirtyID2.create(graph_context)  # noqa: PLW0212
        self.assertIsNotNone(dirtyid_interface)

        # dirty tracking is not activated for the output bundle
        entries = [container]
        entry_names = [container_bundle_name]

        for bundle in child_bundles:
            bundle_name = bundle.get_name()
            attrs = bundle.get_attributes()

            entries.append(bundle)
            entries.extend(attrs)

            entry_names.append(bundle_name)
            entry_names.extend([bundle_name + "." + attr.get_name() for attr in attrs])

        # invalid dirty ids expected
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid_validity(dirtyid_interface, entry_names, curr_dirtyids, False)

        # activate dirty tracking
        controller.edit(
            test_graph_path,
            {
                keys.SET_VALUES: [
                    ("Read.inputs:enableBundleChangeTracking", True),
                ],
            },
        )
        await controller.evaluate()

        # valid dirty ids expected
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid_validity(dirtyid_interface, entry_names, curr_dirtyids, True)

        for bundle in child_bundles:
            assert_stamp_missing(bundle)
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            path = get_attr_value(bundle, "sourcePrimPath")
            if path == cube_path:
                n_attrs = get_expected_prim_attributes_count(cube)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_attr_value(bundle, "sourcePrimType", "Cube")
                assert_attr_value(bundle, "size", 100)
                assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 0]])
            elif path == cone_path:
                n_attrs = get_expected_prim_attributes_count(cone)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_attr_value(bundle, "sourcePrimType", "Cone")
                assert_attr_value(bundle, "radius", 50)
                assert_attr_value(bundle, "height", 10)
                assert_attr_value(bundle, "primvars:displayColor", [[0, 1, 0]])
            else:
                self.fail(path)

        # no change before this evaluation
        await controller.evaluate()

        # the dirty ids shouldn't be bumped when there is no change
        prev_dirtyids = curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, [])

        # change just the cube size
        set_stamp(20)
        cube.GetAttribute("size").Set(200)

        await controller.evaluate()

        # check that only the cube bundle was updated
        assert_stamp(container, 20)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 2)

        for bundle in child_bundles:
            path = get_attr_value(bundle, "sourcePrimPath")
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            if path == cube_path:
                n_attrs = get_expected_prim_attributes_count(cube, debug_stamp=True)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_attr_value(bundle, "sourcePrimType", "Cube")
                assert_attr_value(bundle, "size", 200)
                assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 0]])
            elif path == cone_path:
                n_attrs = get_expected_prim_attributes_count(cone)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp_missing(bundle)
                assert_attr_value(bundle, "sourcePrimType", "Cone")
                assert_attr_value(bundle, "radius", 50)
                assert_attr_value(bundle, "height", 10)
                assert_attr_value(bundle, "primvars:displayColor", [[0, 1, 0]])
            else:
                self.fail(path)

        # only the changed entries will have the dirty ids bumped
        prev_dirtyids = curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        changed_entry_names = [container_bundle_name, cube_bundle_name, cube_bundle_name + ".size"]
        self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, changed_entry_names)

        # change just the cone radius and height
        set_stamp(30)
        cone.GetAttribute("radius").Set(300)
        cone.GetAttribute("height").Set(20)

        await controller.evaluate()

        # check that only the cone bundle was updated
        assert_stamp(container, 30)
        for bundle in child_bundles:
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            path = get_attr_value(bundle, "sourcePrimPath")
            if path == cube_path:
                n_attrs = get_expected_prim_attributes_count(cube, debug_stamp=True)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp(bundle, 20)
                assert_attr_value(bundle, "sourcePrimType", "Cube")
                assert_attr_value(bundle, "size", 200)
                assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 0]])
            elif path == cone_path:
                n_attrs = get_expected_prim_attributes_count(cone, debug_stamp=True)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp(bundle, 30)
                assert_attr_value(bundle, "sourcePrimType", "Cone")
                assert_attr_value(bundle, "radius", 300)
                assert_attr_value(bundle, "height", 20)
                assert_attr_value(bundle, "primvars:displayColor", [[0, 1, 0]])
            else:
                self.fail(path)

        # only the changed entries will have the dirty ids bumped
        prev_dirtyids = curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        changed_entry_names = [
            container_bundle_name,
            cone_bundle_name,
            cone_bundle_name + ".radius",
            cone_bundle_name + ".height",
        ]
        self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, changed_entry_names)

        # delete the cone, full update will be triggered for now
        set_stamp(40)

        removed_entries = []
        removed_entry_names = []

        for bundle in child_bundles:
            bundle_path = get_attr_value(bundle, "sourcePrimPath")
            if bundle_path == cone_path:
                bundle_name = bundle.get_name()
                attrs = bundle.get_attributes()

                removed_entries.append(bundle)
                removed_entries.extend(attrs)

                removed_entry_names.append(bundle_name)
                removed_entry_names.extend([bundle_name + "." + attr.get_name() for attr in attrs])

        stage.RemovePrim(cone_path)
        await controller.evaluate()

        # for now, deleting does a full update
        assert_stamp(container, -40)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp_missing(bundle)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            assert_attr_value(bundle, "size", 200)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 0]])

        # invalid dirty ids expected for removed entries
        self.assert_dirtyid_validity(
            dirtyid_interface, removed_entry_names, dirtyid_interface.get(removed_entries), False
        )

        # the dirty ids should be bumped for all remaining entries
        remaining_prev_dirtyids = []
        remaining_entries = []
        remaining_entry_names = []

        num_entries = len(entries)
        for i in range(num_entries):
            if entry_names[i] not in removed_entry_names:
                remaining_prev_dirtyids.append(curr_dirtyids[i])
                remaining_entries.append(entries[i])
                remaining_entry_names.append(entry_names[i])

        remaining_curr_dirtyids = dirtyid_interface.get(remaining_entries)
        self.assert_dirtyid(
            dirtyid_interface,
            remaining_entry_names,
            remaining_curr_dirtyids,
            remaining_prev_dirtyids,
            remaining_entry_names,
        )

        # create the cone again, using blue color now
        set_stamp(50)
        cone = ogts.create_cone(stage, "XCone/Cone", (0, 0, 1))
        cone.GetAttribute("radius").Set(400)
        cone.GetAttribute("height").Set(40)

        await controller.evaluate()

        # for now, creation does a full update
        assert_stamp(container, -50)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 2)

        for bundle in child_bundles:
            assert_stamp_missing(bundle)
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            path = get_attr_value(bundle, "sourcePrimPath")
            if path == cube_path:
                n_attrs = get_expected_prim_attributes_count(cube)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_attr_value(bundle, "size", 200)
                assert_attr_value(bundle, "sourcePrimType", "Cube")
                assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 0]])
            elif path == cone_path:
                n_attrs = get_expected_prim_attributes_count(cone)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_attr_value(bundle, "radius", 400)
                assert_attr_value(bundle, "height", 40)
                assert_attr_value(bundle, "sourcePrimType", "Cone")
                assert_attr_value(bundle, "primvars:displayColor", [[0, 0, 1]])
            else:
                self.fail(path)

        # for now, creation does a full update
        prev_dirtyids = curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, entry_names)

        # create a new cube attribute
        set_stamp(60)

        dummy_attr_name = "dummy"
        cube.CreateAttribute(dummy_attr_name, Sdf.ValueTypeNames.Float3Array).Set([(1, 2, 3)])

        await controller.evaluate()

        # only the cube should update, and should contain the new attribute
        assert_stamp(container, 60)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 2)

        for bundle in child_bundles:
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            path = get_attr_value(bundle, "sourcePrimPath")
            if path == cube_path:
                n_attrs = get_expected_prim_attributes_count(cube, debug_stamp=True)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp(bundle, 60)
                assert_attr_value(bundle, "size", 200)
                assert_attr_value(bundle, "sourcePrimType", "Cube")
                assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 0]])
                self.assertListEqual(get_attr_value(bundle, dummy_attr_name).tolist(), [[1, 2, 3]])
            elif path == cone_path:
                n_attrs = get_expected_prim_attributes_count(cone)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp_missing(bundle)
                assert_attr_value(bundle, "radius", 400)
                assert_attr_value(bundle, "height", 40)
                assert_attr_value(bundle, "sourcePrimType", "Cone")
                assert_attr_value(bundle, "primvars:displayColor", [[0, 0, 1]])
            else:
                self.fail(path)

        dummy_attr = get_attr(cube_bundle, dummy_attr_name)
        self.assertTrue(dummy_attr.is_valid())

        dummy_entry_name = cube_bundle_name + "." + dummy_attr_name

        dummy_dirtyids = dirtyid_interface.get([dummy_attr])
        self.assert_dirtyid_validity(dirtyid_interface, [dummy_entry_name], dummy_dirtyids, True)

        dummy_entries = entries + [dummy_attr]
        dummy_entry_names = entry_names + [dummy_entry_name]
        dummy_prev_dirtyids = curr_dirtyids + dummy_dirtyids
        dummy_curr_dirtyids = dirtyid_interface.get(dummy_entries)
        self.assert_dirtyid(
            dirtyid_interface,
            dummy_entry_names,
            dummy_curr_dirtyids,
            dummy_prev_dirtyids,
            [container_bundle_name, cube_bundle_name],
        )

        # clear new cube attribute
        set_stamp(70)
        cube.GetAttribute(dummy_attr_name).Clear()

        await controller.evaluate()

        # only the cube should update, and should contain the cleared attribute
        assert_stamp(container, 70)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 2)

        for bundle in child_bundles:
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            path = get_attr_value(bundle, "sourcePrimPath")
            if path == cube_path:
                n_attrs = get_expected_prim_attributes_count(cube, debug_stamp=True)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp(bundle, 70)
                assert_attr_value(bundle, "size", 200)
                assert_attr_value(bundle, "sourcePrimType", "Cube")
                assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 0]])
                self.assertListEqual(get_attr_value(bundle, dummy_attr_name).tolist(), [])
            elif path == cone_path:
                n_attrs = get_expected_prim_attributes_count(cone)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp_missing(bundle)
                assert_attr_value(bundle, "radius", 400)
                assert_attr_value(bundle, "height", 40)
                assert_attr_value(bundle, "sourcePrimType", "Cone")
                assert_attr_value(bundle, "primvars:displayColor", [[0, 0, 1]])
            else:
                self.fail(path)

        dummy_attr = get_attr(cube_bundle, dummy_attr_name)
        self.assertTrue(dummy_attr.is_valid())

        dummy_prev_dirtyids = curr_dirtyids + dummy_dirtyids
        dummy_curr_dirtyids = dirtyid_interface.get(dummy_entries)
        self.assert_dirtyid(
            dirtyid_interface,
            dummy_entry_names,
            dummy_curr_dirtyids,
            dummy_prev_dirtyids,
            [container_bundle_name, cube_bundle_name, dummy_entry_name],
        )

        # remove the new cube attribute
        set_stamp(80)
        cube.RemoveProperty(dummy_attr_name)
        await controller.evaluate()

        # only the cube should update, and should not contain the new attribute anymore
        assert_stamp(container, 80)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 2)

        for bundle in child_bundles:
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            path = get_attr_value(bundle, "sourcePrimPath")
            if path == cube_path:
                n_attrs = get_expected_prim_attributes_count(cube, debug_stamp=True)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp(bundle, 80)
                assert_attr_value(bundle, "size", 200)
                assert_attr_value(bundle, "sourcePrimType", "Cube")
                assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 0]])
                assert_attr_missing(bundle, dummy_attr_name)
            elif path == cone_path:
                n_attrs = get_expected_prim_attributes_count(cone)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp_missing(bundle)
                assert_attr_value(bundle, "radius", 400)
                assert_attr_value(bundle, "height", 40)
                assert_attr_value(bundle, "sourcePrimType", "Cone")
                assert_attr_value(bundle, "primvars:displayColor", [[0, 0, 1]])
            else:
                self.fail(path)

        dummy_attr = get_attr(cube_bundle, dummy_attr_name)
        self.assertFalse(dummy_attr.is_valid())

        prev_dirtyids = dummy_prev_dirtyids[:-1]
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid(
            dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, [container_bundle_name, cube_bundle_name]
        )

        curr_dummy_dirtyids = dirtyid_interface.get([dummy_attr])
        self.assert_dirtyid_validity(dirtyid_interface, [dummy_entry_name], curr_dummy_dirtyids, False)

        # remove the cone from the input paths
        if use_path_pattern:
            controller.edit(
                test_graph_path,
                {
                    keys.SET_VALUES: [
                        ("Read.inputs:pathPattern", cube_path),
                    ],
                },
            )
        else:
            omni.kit.commands.execute(
                "SetRelationshipTargets",
                relationship=stage.GetPropertyAtPath(f"{test_graph_path}/Read.inputs:prims"),
                targets=[cube.GetPath()],
            )

        set_stamp(90)
        await controller.evaluate()

        # for now, changing inputs:prims does a full update
        assert_stamp(container, -90)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp_missing(bundle)
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_value(bundle, "size", 200)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 0]])

        # invalid dirty ids expected for removed entries
        self.assert_dirtyid_validity(
            dirtyid_interface, removed_entry_names, dirtyid_interface.get(removed_entries), False
        )

        # the dirty ids should be bumped for all remaining entries
        remaining_prev_dirtyids = []
        remaining_entries = []
        remaining_entry_names = []

        num_entries = len(entries)
        for i in range(num_entries):
            if entry_names[i] not in removed_entry_names:
                remaining_prev_dirtyids.append(curr_dirtyids[i])
                remaining_entries.append(entries[i])
                remaining_entry_names.append(entry_names[i])

        remaining_curr_dirtyids = dirtyid_interface.get(remaining_entries)
        self.assert_dirtyid(
            dirtyid_interface,
            remaining_entry_names,
            remaining_curr_dirtyids,
            remaining_prev_dirtyids,
            remaining_entry_names,
        )

        # add the cone again to the input paths
        if use_path_pattern:
            controller.edit(
                test_graph_path,
                {
                    keys.SET_VALUES: [
                        ("Read.inputs:pathPattern", "/X*/C*"),
                    ],
                },
            )
        else:
            omni.kit.commands.execute(
                "SetRelationshipTargets",
                relationship=stage.GetPropertyAtPath(f"{test_graph_path}/Read.inputs:prims"),
                targets=[cube.GetPath(), cone.GetPath()],
            )

        set_stamp(100)
        await controller.evaluate()

        # for now, changing inputs:prims does a full update
        assert_stamp(container, -100)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 2)

        for bundle in child_bundles:
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            path = get_attr_value(bundle, "sourcePrimPath")
            if path == cube_path:
                n_attrs = get_expected_prim_attributes_count(cube)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp_missing(bundle)
                assert_attr_value(bundle, "size", 200)
                assert_attr_value(bundle, "sourcePrimType", "Cube")
            elif path == cone_path:
                n_attrs = get_expected_prim_attributes_count(cone)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp_missing(bundle)
                assert_attr_value(bundle, "radius", 400)
                assert_attr_value(bundle, "height", 40)
                assert_attr_value(bundle, "sourcePrimType", "Cone")

        # for now, changing inputs:prims does a full update
        prev_dirtyids = curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, entry_names)

        # modify, delete and create again, but don't evaluate the graph yet.
        set_stamp(110)

        cube.GetAttribute("size").Set(1000)
        cone.GetAttribute("height").Set(10)
        stage.RemovePrim(cube_path)
        cone.GetAttribute("radius").Set(10)
        stage.RemovePrim(cone_path)
        cube = ogts.create_cube(stage, "XCube/Cube", (0, 1, 1))
        cube.GetAttribute("size").Set(100)

        removed_entries = []
        removed_entry_names = []

        for bundle in child_bundles:
            bundle_path = get_attr_value(bundle, "sourcePrimPath")
            if bundle_path == cone_path:
                bundle_name = bundle.get_name()
                attrs = bundle.get_attributes()

                removed_entries.append(bundle)
                removed_entries.extend(attrs)

                removed_entry_names.append(bundle_name)
                removed_entry_names.extend([bundle_name + "." + attr.get_name() for attr in attrs])

        await controller.evaluate()

        # the multiple changes should have be collected together
        # but for now, deleting and creation does a full update unfortunately
        assert_stamp(container, -110)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp_missing(bundle)
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_value(bundle, "size", 100)
            assert_attr_value(bundle, "primvars:displayColor", [[0, 1, 1]])

        # invalid dirty ids expected for removed entries
        self.assert_dirtyid_validity(
            dirtyid_interface, removed_entry_names, dirtyid_interface.get(removed_entries), False
        )

        # the dirty ids should be bumped for all remaining entries
        remaining_prev_dirtyids = []
        remaining_entries = []
        remaining_entry_names = []

        num_entries = len(entries)
        for i in range(num_entries):
            if entry_names[i] not in removed_entry_names:
                remaining_prev_dirtyids.append(curr_dirtyids[i])
                remaining_entries.append(entries[i])
                remaining_entry_names.append(entry_names[i])

        remaining_curr_dirtyids = dirtyid_interface.get(remaining_entries)
        self.assert_dirtyid(
            dirtyid_interface,
            remaining_entry_names,
            remaining_curr_dirtyids,
            remaining_prev_dirtyids,
            remaining_entry_names,
        )

        # remove the Cube parent xform
        # this should remove the Cube from the bundle
        set_stamp(120)

        stage.RemovePrim("/XCube")

        await controller.evaluate()

        if use_path_pattern:
            # The path pattern matcher will not find any prim matches,
            # so the input paths will be empty.
            # In this case, the output bundle is just cleared.
            assert_stamp_missing(container)
        else:
            # The relationship still has a path to the delete cone
            # So the input paths won't change, but the deletion
            # will be detected by the change tracker
            assert_stamp(container, -120)

        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 0)

        container_prev_dirtyids = [remaining_curr_dirtyids[0]]
        container_curr_dirtyids = dirtyid_interface.get([container])
        self.assert_dirtyid(
            dirtyid_interface,
            [container_bundle_name],
            container_curr_dirtyids,
            container_prev_dirtyids,
            [container_bundle_name],
        )

        # create the cube again
        set_stamp(130)
        xcube = UsdGeom.Xform.Define(stage, "/XCube")
        cube = ogts.create_cube(stage, "XCube/Cube", (1, 0, 1))
        cube.GetAttribute("size").Set(100)

        await controller.evaluate()

        # for now creation of prims results in a full update
        assert_stamp(container, -130)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp_missing(bundle)
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", id_mat)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_value(bundle, "size", 100)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 1]])

        remaining_prev_dirtyids = remaining_curr_dirtyids
        remaining_curr_dirtyids = dirtyid_interface.get(remaining_entries)
        self.assert_dirtyid(
            dirtyid_interface,
            remaining_entry_names,
            remaining_curr_dirtyids,
            remaining_prev_dirtyids,
            remaining_entry_names,
        )

        # translate the cube through its parent xform
        set_stamp(140)
        UsdGeom.XformCommonAPI(xcube).SetTranslate((10.0, 10.0, 10.0))
        await controller.evaluate()

        # the cube bundle wordMatrix should have updated
        assert_stamp(container, 140)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube, debug_stamp=True)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp(bundle, 10000140)  # 1e7 means only world matrix was updated
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_missing(bundle, "bboxMaxCorner")
            assert_attr_missing(bundle, "bboxMinCorner")
            assert_attr_missing(bundle, "bboxTransform")
            assert_attr_value(bundle, "worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 10, 10, 1])
            assert_attr_value(bundle, "size", 100)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 1]])

        remaining_prev_dirtyids = remaining_curr_dirtyids
        remaining_curr_dirtyids = dirtyid_interface.get(remaining_entries)
        self.assert_dirtyid(
            dirtyid_interface,
            remaining_entry_names,
            remaining_curr_dirtyids,
            remaining_prev_dirtyids,
            [container_bundle_name, cube_bundle_name, cube_bundle_name + ".worldMatrix"],
        )

        # request bounding boxes
        set_stamp(150)
        controller.edit(
            test_graph_path,
            {
                keys.SET_VALUES: ("Read.inputs:computeBoundingBox", True),
            },
        )

        await controller.evaluate()

        # changing the computeBoundingBox causes a full update
        assert_stamp(container, -150)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube, bbox=True)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp_missing(bundle)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_value(bundle, "bboxMaxCorner", [50, 50, 50])
            assert_attr_value(bundle, "bboxMinCorner", [-50, -50, -50])
            assert_attr_value(bundle, "bboxTransform", id_mat)
            assert_attr_value(bundle, "worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 10, 10, 1])
            assert_attr_value(bundle, "size", 100)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 1]])

        remaining_prev_dirtyids = remaining_curr_dirtyids
        remaining_curr_dirtyids = dirtyid_interface.get(remaining_entries)
        self.assert_dirtyid(
            dirtyid_interface,
            remaining_entry_names,
            remaining_curr_dirtyids,
            remaining_prev_dirtyids,
            remaining_entry_names,
        )

        bbox_entries = [
            get_attr(cube_bundle, "bboxMaxCorner"),
            get_attr(cube_bundle, "bboxMinCorner"),
            get_attr(cube_bundle, "bboxTransform"),
        ]
        bbox_entry_names = [
            cube_bundle_name + ".bboxMaxCorner",
            cube_bundle_name + ".bboxMinCorner",
            cube_bundle_name + ".bboxTransform",
        ]
        bbox_curr_dirtyids = dirtyid_interface.get(bbox_entries)
        self.assert_dirtyid_validity(dirtyid_interface, bbox_entry_names, bbox_curr_dirtyids, True)

        # modify bounding box
        set_stamp(160)
        cube.GetAttribute("size").Set(200)

        await controller.evaluate()

        # check incremental update
        assert_stamp(container, 160)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube, debug_stamp=True, bbox=True)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp(bundle, 160)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_value(bundle, "bboxMaxCorner", [100, 100, 100])
            assert_attr_value(bundle, "bboxMinCorner", [-100, -100, -100])
            assert_attr_value(bundle, "bboxTransform", id_mat)
            assert_attr_value(bundle, "worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 10, 10, 1])
            assert_attr_value(bundle, "size", 200)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 1]])

        entries = remaining_entries + bbox_entries
        entry_names = remaining_entry_names + bbox_entry_names
        prev_dirtyids = remaining_curr_dirtyids + bbox_curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid(
            dirtyid_interface,
            entry_names,
            curr_dirtyids,
            prev_dirtyids,
            [
                container_bundle_name,
                cube_bundle_name,
                cube_bundle_name + ".size",
                cube_bundle_name + ".bboxMaxCorner",
                cube_bundle_name + ".bboxMinCorner",
            ],
        )

        # evaluate bbox without modification
        set_stamp(170)

        await controller.evaluate()

        # check nothing was updated
        assert_stamp(container, 160)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube, debug_stamp=True, bbox=True)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp(bundle, 160)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_value(bundle, "bboxMaxCorner", [100, 100, 100])
            assert_attr_value(bundle, "bboxMinCorner", [-100, -100, -100])
            assert_attr_value(bundle, "bboxTransform", id_mat)
            assert_attr_value(bundle, "worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 10, 10, 1])
            assert_attr_value(bundle, "size", 200)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 1]])

        prev_dirtyids = curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, [])

        # animate
        for timecode in range(10):
            set_stamp(180 + timecode)

            controller.edit(test_graph_path, {keys.SET_VALUES: ("Read.inputs:usdTimecode", timecode)})

            await controller.evaluate()

            # check a full update is done
            assert_stamp(container, -(180 + timecode))
            child_bundles = container.get_child_bundles()
            self.assertEqual(len(child_bundles), 1)

            for bundle in child_bundles:
                n_attrs = get_expected_prim_attributes_count(cube, bbox=True)
                self.assertEqual(bundle.get_attribute_count(), n_attrs)
                assert_stamp_missing(bundle)
                assert_attr_value(bundle, "sourcePrimPath", cube_path)
                assert_attr_value(bundle, "sourcePrimType", "Cube")
                assert_attr_value(bundle, "bboxMaxCorner", [100, 100, 100])
                assert_attr_value(bundle, "bboxMinCorner", [-100, -100, -100])
                assert_attr_value(bundle, "bboxTransform", id_mat)
                assert_attr_value(bundle, "worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 10, 10, 1])
                assert_attr_value(bundle, "size", 200)
                assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 1]])

            prev_dirtyids = curr_dirtyids
            curr_dirtyids = dirtyid_interface.get(entries)
            self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, entry_names)

        # switch back to non-animating
        set_stamp(200)

        controller.edit(test_graph_path, {keys.SET_VALUES: ("Read.inputs:usdTimecode", float("nan"))})

        # changes to the cube should not trigger an incremental update when switching
        cube.GetAttribute("size").Set(100)

        await controller.evaluate()

        # check a full update is done
        assert_stamp(container, -200)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube, bbox=True)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp_missing(bundle)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_value(bundle, "bboxMaxCorner", [50, 50, 50])
            assert_attr_value(bundle, "bboxMinCorner", [-50, -50, -50])
            assert_attr_value(bundle, "bboxTransform", id_mat)
            assert_attr_value(bundle, "worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 10, 10, 1])
            assert_attr_value(bundle, "size", 100)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 1]])

        prev_dirtyids = curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, entry_names)

        # change the cube again
        set_stamp(210)

        # changes to the cube should now trigger an incremental update
        cube.GetAttribute("size").Set(200)

        await controller.evaluate()

        # an incremental update should be done
        assert_stamp(container, 210)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube, debug_stamp=True, bbox=True)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp(bundle, 210)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_value(bundle, "bboxMaxCorner", [100, 100, 100])
            assert_attr_value(bundle, "bboxMinCorner", [-100, -100, -100])
            assert_attr_value(bundle, "bboxTransform", id_mat)
            assert_attr_value(bundle, "worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 10, 10, 1])
            assert_attr_value(bundle, "size", 200)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 1]])

        # disable change tracking
        set_change_tracking(False)
        set_stamp(220)
        await controller.evaluate()

        # the input change should trigger a full update
        assert_stamp(container, -220)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube, bbox=True)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp_missing(bundle)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_value(bundle, "bboxMaxCorner", [100, 100, 100])
            assert_attr_value(bundle, "bboxMinCorner", [-100, -100, -100])
            assert_attr_value(bundle, "bboxTransform", id_mat)
            assert_attr_value(bundle, "worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 10, 10, 1])
            assert_attr_value(bundle, "size", 200)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 1]])

        prev_dirtyids = curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, entry_names)

        # change the cube again, with change tracking disabled
        set_stamp(230)

        # changes to the cube should now trigger a full update
        cube.GetAttribute("size").Set(100)

        await controller.evaluate()

        assert_stamp(container, -230)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube, bbox=True)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp_missing(bundle)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_value(bundle, "bboxMaxCorner", [50, 50, 50])
            assert_attr_value(bundle, "bboxMinCorner", [-50, -50, -50])
            assert_attr_value(bundle, "bboxTransform", id_mat)
            assert_attr_value(bundle, "worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 10, 10, 1])
            assert_attr_value(bundle, "size", 100)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 1]])

        prev_dirtyids = curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, entry_names)

        # enable change tracking again
        set_change_tracking(True)
        set_stamp(250)
        await controller.evaluate()

        # the input change should trigger a full update
        assert_stamp(container, -250)

        for bundle in child_bundles:
            n_attrs = get_expected_prim_attributes_count(cube, bbox=True)
            self.assertEqual(bundle.get_attribute_count(), n_attrs)
            assert_stamp_missing(bundle)
            assert_attr_value(bundle, "sourcePrimPath", cube_path)
            assert_attr_value(bundle, "sourcePrimType", "Cube")
            assert_attr_value(bundle, "bboxMaxCorner", [50, 50, 50])
            assert_attr_value(bundle, "bboxMinCorner", [-50, -50, -50])
            assert_attr_value(bundle, "bboxTransform", id_mat)
            assert_attr_value(bundle, "worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 10, 10, 1])
            assert_attr_value(bundle, "size", 100)
            assert_attr_value(bundle, "primvars:displayColor", [[1, 0, 1]])

        prev_dirtyids = curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, entry_names)

        # create, remove and create the cone, in one go
        set_stamp(260)
        cone = ogts.create_cube(stage, "XCone/Cone", (1, 1, 1))
        stage.RemovePrim(cone_path)
        cone = ogts.create_cube(stage, "XCone/Cone", (1, 1, 1))

        await controller.evaluate()

        # the second removal should not cancel the last creation
        assert_stamp(container, -260)
        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 2)

        prev_dirtyids = curr_dirtyids
        curr_dirtyids = dirtyid_interface.get(entries)
        self.assert_dirtyid(dirtyid_interface, entry_names, curr_dirtyids, prev_dirtyids, entry_names)

    async def test_read_prims_change_tracking_no_debug_stamps(self):
        """omni.graph.nodes.ReadPrimsV2 change tracking should not add debug stamps unless requested"""
        usd_context = omni.usd.get_context()
        stage: Usd.Stage = usd_context.get_stage()
        test_graph_path = "/World/TestGraph"

        controller = og.Controller()
        keys = og.Controller.Keys

        xcube = UsdGeom.Xform.Define(stage, "/XCube")
        cube = ogts.create_cube(stage, "XCube/Cube", (1, 0, 0))

        cube.GetAttribute("size").Set(100)

        (graph, [read_prims_node, _], _, _) = controller.edit(
            test_graph_path,
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrimsV2"),
                    ("Inspector", "omni.graph.nodes.BundleInspector"),
                ],
                keys.CONNECT: [
                    ("Read.outputs_primsBundle", "Inspector.inputs:bundle"),
                ],
                keys.SET_VALUES: [
                    ("Inspector.inputs:print", False),
                ],
            },
        )

        omni.kit.commands.execute(
            "SetRelationshipTargets",
            relationship=stage.GetPropertyAtPath(f"{test_graph_path}/Read.inputs:prims"),
            targets=[cube.GetPath()],
        )

        def get_attr(bundle, name):
            return bundle.get_attribute_by_name(name)

        def assert_attr_missing(bundle, name):
            self.assertFalse(get_attr(bundle, name).is_valid())

        def assert_stamp_missing(bundle):
            assert_attr_missing(bundle, "_debugStamp")

        # initial update
        await controller.evaluate()

        graph_context = graph.get_default_graph_context()

        container = graph_context.get_output_bundle(read_prims_node, "outputs_primsBundle")
        self.assertTrue(container.valid)

        # no stamps should be added
        assert_stamp_missing(container)

        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            assert_stamp_missing(bundle)

        # trigger incremental empty update
        await controller.evaluate()

        # no stamps should be added
        assert_stamp_missing(container)

        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            assert_stamp_missing(bundle)

        # move the xform
        UsdGeom.XformCommonAPI(xcube).SetTranslate((10.0, 10.0, 10.0))

        # trigger incremental update, world matrices should be updated
        await controller.evaluate()

        # but no stamps should be added
        assert_stamp_missing(container)

        child_bundles = container.get_child_bundles()
        self.assertEqual(len(child_bundles), 1)

        for bundle in child_bundles:
            assert_stamp_missing(bundle)

    def assert_dirtyid_validity(
        self, dirtyid_interface: og._og_unstable.IDirtyID2, entry_names: List[str], curr_dirtyids: list, is_valid: bool
    ):
        self.assertEqual(len(entry_names), len(curr_dirtyids))

        if _debug:
            print()
            for entry_name, curr_dirty_id in zip(entry_names, curr_dirtyids):
                print(entry_name, curr_dirty_id)

        for entry_name, curr_dirty_id in zip(entry_names, curr_dirtyids):
            self.assertEqual(dirtyid_interface.is_valid(curr_dirty_id), is_valid, entry_name)

    def assert_dirtyid(
        self,
        dirtyid_interface: og._og_unstable.IDirtyID2,
        entry_names: List[str],
        curr_dirtyids: list,
        prev_dirtyids: list,
        changed_entry_names: List[str],
    ):
        self.assertEqual(len(entry_names), len(curr_dirtyids))
        self.assertEqual(len(entry_names), len(prev_dirtyids))

        if _debug:
            print()
            for entry_name, curr_dirty_id, prev_dirty_id in zip(entry_names, curr_dirtyids, prev_dirtyids):
                print(entry_name, curr_dirty_id, prev_dirty_id)

        for entry_name, curr_dirty_id, prev_dirty_id in zip(entry_names, curr_dirtyids, prev_dirtyids):
            self.assertTrue(dirtyid_interface.is_valid(curr_dirty_id), entry_name)
            self.assertTrue(dirtyid_interface.is_valid(prev_dirty_id), entry_name)

            if entry_name in changed_entry_names:
                self.assertGreater(curr_dirty_id, prev_dirty_id, entry_name)
            else:
                self.assertEqual(curr_dirty_id, prev_dirty_id, entry_name)
