import numpy as np
import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test
from pxr import Gf, Sdf, Usd, UsdGeom


class TestReadPrimsHierarchy(ogts.OmniGraphTestCase):
    """Unit tests for hierarchical behavior of the ReadPrimsV2 node in this extension"""

    async def test_read_prims_hierarchy_permutations(self):
        # We build a hierarchy, 4 levels deep.
        # Then we track each possible pair of prims in the hierarchy,
        # mutate every prim in the hierarchy (scaling),
        # and check if the pair USD and bundle world matrices and bounding boxes match.
        # TODO: Find out why this runs so slow!

        # Originally we ran 3 tests, optionally enabling matrix and/or bounds
        # But since the test runs so slowly, we only have one now.
        # The incremental tests will test the options anyway.
        # We keep these variables to selectively disable either one for debugging.
        compute_world_matrix = True
        compute_bounding_box = True

        usd_context = omni.usd.get_context()
        stage: Usd.Stage = usd_context.get_stage()
        test_graph_path = "/World/TestGraph"

        # Define the compute graph
        controller = og.Controller()
        keys = og.Controller.Keys

        (graph, [read_prims_node], _, _) = controller.edit(
            test_graph_path,
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrimsV2"),
                ],
                keys.SET_VALUES: [
                    ("Read.inputs:enableChangeTracking", True),
                    # TODO: Re-enable when OgnReadPrimsV2 gets computeWorldMatrix
                    # ("Read.inputs:computeWorldMatrix", compute_world_matrix),
                    ("Read.inputs:computeBoundingBox", compute_bounding_box),
                ],
            },
        )

        debug_stamp = 0
        debug_stamp_attribute = read_prims_node.get_attribute("inputs:_debugStamp")

        init_scale = Gf.Vec3f(0.5, 0.5, 0.5)
        test_scale = Gf.Vec3f(1.5, 1.5, 1.5)

        default_time = Usd.TimeCode.Default()

        # Defines 2 trees with 2 branches and 2 leaves (as spheres),
        # return the prim paths of all the nodes.
        # Optionally just define nodes that have the given prefix;
        # this is used to restore the hierarchy after deleting a subtree
        def define_hierarchies(prefix=None):
            tree_prims = []

            def add_prim(prim, x, y, z):
                tree_prims.append(prim)

                api = UsdGeom.XformCommonAPI(prim)
                api.SetTranslate(Gf.Vec3d(x, y, z))

                # We set the scale of each node to 0.5 instead of 1,
                # so that deleting the scale attribute (which resets the scale to 1)
                # is detected as a matrix and bounds change
                api.SetScale(init_scale)

            for tree_index in range(2):
                tree_path = f"/Tree{tree_index}"
                if prefix is None or Sdf.Path(tree_path).HasPrefix(prefix):
                    tree_prim = UsdGeom.Xform.Define(stage, tree_path)
                    add_prim(tree_prim, (tree_index - 0.5) * 20, 0, 0)
                for branch_index in range(2):
                    branch_path = f"{tree_path}/Branch{branch_index}"
                    if prefix is None or Sdf.Path(branch_path).HasPrefix(prefix):
                        branch_prim = UsdGeom.Xform.Define(stage, branch_path)
                        add_prim(branch_prim, 0, 10, 0)
                    for leaf_index in range(2):
                        leaf_path = f"{branch_path}/Leaf{leaf_index}"
                        if prefix is None or Sdf.Path(leaf_path).HasPrefix(prefix):
                            leaf_prim = UsdGeom.Sphere.Define(stage, leaf_path)
                            # The leaves are positioned in a diamond shape,
                            # so that deleting any leaf influences that ancestor bounds
                            if branch_index == 0:
                                add_prim(leaf_prim, (leaf_index - 0.5) * 5, 10, 0)
                            else:
                                add_prim(leaf_prim, 0, 10, (leaf_index - 0.5) * 5)

            return [p.GetPath() for p in tree_prims]

        def get_usd_matrix_bounds_pair(prim_path):
            xformable = UsdGeom.Xformable(stage.GetPrimAtPath(prim_path))
            self.assertTrue(xformable is not None)
            world_matrix = xformable.ComputeLocalToWorldTransform(default_time)
            local_bounds = xformable.ComputeLocalBound(default_time, UsdGeom.Tokens.default_, UsdGeom.Tokens.proxy)
            return (world_matrix, local_bounds)

        tree_prim_paths = define_hierarchies()

        # For debugging test failures, tweak the two variable below (should be lists of Sdf.Path)
        track_prim_paths = tree_prim_paths
        change_prim_paths = tree_prim_paths

        # The original matrix and bound pairs, before changes
        usd_matrix_bounds_originals = {path: get_usd_matrix_bounds_pair(path) for path in tree_prim_paths}

        async def check_bundles(changed_prim, tracked_paths, debug_stamp):
            changed_path = changed_prim.GetPath()

            controller.set(debug_stamp_attribute, debug_stamp)

            await controller.evaluate()

            graph_context = graph.get_default_graph_context()

            container = graph_context.get_output_bundle(read_prims_node, "outputs_primsBundle")
            self.assertTrue(container.valid)

            child_bundles = container.get_child_bundles()
            self.assertEqual(len(child_bundles), len(tracked_paths))

            for bundle in child_bundles:
                stamp_attr = bundle.get_attribute_by_name("_debugStamp")

                source_prim_path_attr = bundle.get_attribute_by_name("sourcePrimPath")
                self.assertTrue(source_prim_path_attr.is_valid())

                source_prim_path = Sdf.Path(source_prim_path_attr.get())

                self.assertTrue(
                    source_prim_path in tracked_paths,
                    f"{source_prim_path} not in {tracked_paths}!",
                )

                source_self_changed = source_prim_path == changed_path
                source_ancestor_changed = source_prim_path.HasPrefix(changed_path)
                source_descendant_changed = changed_path.HasPrefix(source_prim_path)

                (
                    usd_world_matrix_before_change,
                    usd_local_bounds_before_change,
                ) = usd_matrix_bounds_originals[source_prim_path]

                (
                    usd_world_matrix_after_change,
                    usd_local_bounds_after_change,
                ) = get_usd_matrix_bounds_pair(source_prim_path)

                usd_world_matrix_changed = usd_world_matrix_before_change != usd_world_matrix_after_change
                usd_local_bounds_changed = usd_local_bounds_before_change != usd_local_bounds_after_change

                # If the source is geometry (not an xform),
                # then changes to the ancestors will
                # NOT cause a change to the local bound
                source_prim = stage.GetPrimAtPath(source_prim_path)
                self.assertTrue(source_prim.IsValid())

                ancestor_changed_local_bound = source_ancestor_changed and source_prim.IsA(UsdGeom.Xform)

                # The logic below breaks for structural stage changes,
                # which is disabled by passing 0 for debug_stamp.
                if debug_stamp > 0:
                    # We add some tests to verify this complicated unit test itself
                    self.assertEqual(
                        usd_world_matrix_changed,
                        source_self_changed or source_ancestor_changed,
                        f"{source_prim_path} => expected world matrix change",
                    )
                    self.assertEqual(
                        usd_local_bounds_changed,
                        source_self_changed or source_descendant_changed or ancestor_changed_local_bound,
                        f"{source_prim_path} => expected local bounds change",
                    )

                expected_stamp = None

                world_matrix_attr = bundle.get_attribute_by_name("worldMatrix")
                if compute_world_matrix:
                    # Compare world matrix in USD and bundle
                    self.assertTrue(
                        world_matrix_attr.is_valid(),
                        f"Bundle for {source_prim_path} is missing worldMatrix",
                    )
                    bundle_world_matrix = np.array(world_matrix_attr.get())
                    stage_world_matrix = np.array(usd_world_matrix_after_change).flatten()
                    np.testing.assert_array_equal(
                        stage_world_matrix,
                        bundle_world_matrix,
                        f"{source_prim_path} worldMatrix mismatch",
                    )

                    if debug_stamp > 0:
                        # Check how the world matrix was changed
                        if source_self_changed:
                            expected_stamp = debug_stamp
                        elif source_ancestor_changed:
                            expected_stamp = debug_stamp + 10000000
                else:
                    self.assertFalse(
                        world_matrix_attr.is_valid(),
                        f"Bundle for {source_prim_path} should not contain worldMatrix",
                    )

                bbox_transform_attr = bundle.get_attribute_by_name("bboxTransform")
                bbox_min_corner_attr = bundle.get_attribute_by_name("bboxMinCorner")
                bbox_max_corner_attr = bundle.get_attribute_by_name("bboxMaxCorner")
                if compute_bounding_box:
                    # Compare local bound in USD and bundle
                    self.assertTrue(
                        bbox_transform_attr.is_valid(),
                        f"Bundle for {source_prim_path} is missing bboxTransform",
                    )
                    self.assertTrue(
                        bbox_min_corner_attr.is_valid(),
                        f"Bundle for {source_prim_path} is missing bboxMinCorner",
                    )
                    self.assertTrue(
                        bbox_max_corner_attr.is_valid(),
                        f"Bundle for {source_prim_path} is missing bboxMaxCorner",
                    )
                    bundle_bbox_transform = np.array(bbox_transform_attr.get())
                    bundle_bbox_min_corner = np.array(bbox_min_corner_attr.get())
                    bundle_bbox_max_corner = np.array(bbox_max_corner_attr.get())

                    stage_bbox = usd_local_bounds_after_change.GetBox()
                    stage_bbox_transform = np.array(usd_local_bounds_after_change.GetMatrix()).flatten()
                    stage_bbox_min_corner = np.array(stage_bbox.GetMin())
                    stage_bbox_max_corner = np.array(stage_bbox.GetMax())

                    np.testing.assert_array_equal(
                        stage_bbox_transform,
                        bundle_bbox_transform,
                        f"{source_prim_path} bbox_transform mismatch",
                    )
                    np.testing.assert_array_equal(
                        stage_bbox_min_corner,
                        bundle_bbox_min_corner,
                        f"{source_prim_path} bbox_min_corner mismatch",
                    )
                    np.testing.assert_array_equal(
                        stage_bbox_max_corner,
                        bundle_bbox_max_corner,
                        f"{source_prim_path} bbox_max_corner mismatch",
                    )

                    if debug_stamp > 0:
                        # Check how the local bounds were changed
                        if source_self_changed:
                            expected_stamp = debug_stamp
                        elif source_descendant_changed:
                            expected_stamp = debug_stamp + 1000000
                        elif ancestor_changed_local_bound:
                            expected_stamp = debug_stamp + 10000000
                else:
                    self.assertFalse(
                        bbox_transform_attr.is_valid(),
                        f"Bundle for {source_prim_path} should not contain bboxTransform",
                    )
                    self.assertFalse(
                        bbox_min_corner_attr.is_valid(),
                        f"Bundle for {source_prim_path} should not contain bboxMinCorner",
                    )
                    self.assertFalse(
                        bbox_max_corner_attr.is_valid(),
                        f"Bundle for {source_prim_path} should not contain bboxMaxCorner",
                    )

                if debug_stamp > 0:
                    # Check the debug stamp
                    actual_stamp = stamp_attr.get() if stamp_attr.is_valid() else 0

                    if expected_stamp is None:
                        self.assertNotEqual(
                            actual_stamp % 1000000,
                            debug_stamp,
                            f"{source_prim_path} shouldn't be stamped in this update!",
                        )
                    else:
                        self.assertEqual(
                            actual_stamp,
                            expected_stamp,
                            f"{source_prim_path} had a wrong stamp!",
                        )

        async def run_sub_tests(i, j, debug_stamp):
            # Track these two prims
            tracked_pair_paths = [track_prim_paths[i], track_prim_paths[j]]

            omni.kit.commands.execute(
                "SetRelationshipTargets",
                relationship=stage.GetPropertyAtPath(f"{test_graph_path}/Read.inputs:prims"),
                targets=tracked_pair_paths,
            )

            # We expect a full evaluation here, since we changed the input prims
            # We don't check that in this test that relates to hierarchy only
            await controller.evaluate()

            # Visit all prims in the hierarchy,
            # scale them, checking the bundle against the USD data (attr change test)
            # Then delete the scale attribute, and check again (attr resync remove test)
            # Then re-create the scale attribute, and check again (attr resync create test)
            # Then delete the prim (and subtree), and check again (prim resync remove test)
            # Then re-create the subtree, and check again (prim resync create test)
            for prim_path in change_prim_paths:
                prim = stage.GetPrimAtPath(prim_path)
                title = f"change_prim_paths={[prim_path]}, track_prim_paths={tracked_pair_paths}, debug_stamp={debug_stamp}..."

                with self.subTest(f"Change scale attr, {title}"):
                    # Change the scale
                    UsdGeom.XformCommonAPI(prim).SetScale(test_scale)

                    # Check that the change is picked up
                    debug_stamp += 1

                    await check_bundles(prim, tracked_pair_paths, debug_stamp)

                with self.subTest(f"Delete scale attr, {title}"):
                    # Delete the scale property.
                    # This should reset it back to one.
                    prim.RemoveProperty("xformOp:scale")

                    # Check that the change is picked up
                    debug_stamp += 1

                    await check_bundles(prim, tracked_pair_paths, debug_stamp)

                with self.subTest(f"Create scale attr, {title}"):
                    # Create the scale property back, and change it.
                    prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Float3, False).Set(test_scale)

                    # Check that the change is picked up
                    debug_stamp += 1

                    await check_bundles(prim, tracked_pair_paths, debug_stamp)

                with self.subTest(f"Delete prim, {title}"):
                    stage.RemovePrim(prim_path)

                    # The deleted prim might be a tracked one
                    valid_tracked_pair_paths = [
                        path for path in tracked_pair_paths if stage.GetPrimAtPath(path).IsValid()
                    ]

                    # Check that the change is picked up
                    debug_stamp += 1

                    # NOTE: If the deleted prim was a tracked prim,
                    # the ReadPrimsV2 node will currently do a full update
                    await check_bundles(
                        prim,
                        valid_tracked_pair_paths,
                        debug_stamp if len(valid_tracked_pair_paths) == 2 else 0,
                    )

                with self.subTest(f"Create prim, {title}"):
                    # Restore deleted sub-tree (and reset scale)
                    define_hierarchies(prim_path)

                    # Check that the change is picked up (wo stamp checking for now)
                    # TODO: We should also do stamp checking here, but couldn't get that working yet.
                    await check_bundles(prim, tracked_pair_paths, 0)

            return debug_stamp

        # Iterate over all possible pairs of tree prims
        for i in range(len(track_prim_paths) - 1):
            for j in range(i + 1, len(track_prim_paths)):
                debug_stamp = await run_sub_tests(i, j, debug_stamp)
