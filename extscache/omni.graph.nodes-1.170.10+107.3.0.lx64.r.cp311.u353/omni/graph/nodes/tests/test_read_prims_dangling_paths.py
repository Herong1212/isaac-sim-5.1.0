import unittest

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test
from carb import settings
from pxr import Sdf, Usd


def is_fsd_enabled():
    return settings.get_settings().get_as_bool("/app/useFabricSceneDelegate")


class TestReadPrimsDanglingPaths(ogts.OmniGraphTestCase):
    """Unit tests for dangling paths (aka refs to deleted paths) in the ReadPrimsV2 node in this extension"""

    @unittest.skipIf(is_fsd_enabled(), "Test causes errors in USDRT when FSD is enabled")
    async def test_read_prims_dangling_paths(self):
        usd_context = omni.usd.get_context()
        stage: Usd.Stage = usd_context.get_stage()
        test_graph_path = "/World/TestGraph"

        # ReadPrimsV2 had a bug (OM-98141) that didn't create
        # strong references to the matched paths.
        #
        # This caused access violation crashes in large stages.
        #
        # The reason this didn't surface in existing unit tests was two-fold:
        # - USD has an internal path cache with size 1024
        # - it only happens with instance proxy paths to shaders/materials
        #
        # So to check if the read prims node correctly handles path reference counting,
        # we must create a stage with a lot of instances of prototypes with a shader,
        # so that at least one path is not in the cache anymore.

        controller = og.Controller()
        keys = og.Controller.Keys

        # create stage
        context = omni.usd.get_context()
        stage = context.get_stage()

        layer = stage.GetRootLayer()

        def create_prim(prim_path, prim_type):
            prim = Sdf.CreatePrimInLayer(layer, prim_path)
            prim.specifier = Sdf.SpecifierDef
            prim.typeName = prim_type
            return prim

        with Sdf.ChangeBlock():
            create_prim("/prototype", "Xform")
            create_prim("/prototype/shader", "Shader")

            instance_count = 2048

            ref = Sdf.Reference("", "/prototype")

            for i in range(instance_count):
                prim = create_prim("/instance_" + str(i), "Xform")
                prim.referenceList.Prepend(ref)
                prim.instanceable = True

        # Create graph
        (graph, [read_prims_node], _, _) = controller.edit(
            {"graph_path": test_graph_path, "evaluator_name": "push"},
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrimsV2"),
                ],
                keys.SET_VALUES: [
                    ("Read.inputs:pathPattern", "/instance_*"),
                ],
            },
        )

        # Evaluate. This used to crash before fix OM-98141
        await controller.evaluate()

        graph_context = graph.get_default_graph_context()

        container_bundle = graph_context.get_output_bundle(read_prims_node, "outputs_primsBundle")
        self.assertTrue(container_bundle.valid)

        bundle_factory = og.IBundleFactory.create()
        container = bundle_factory.get_const_bundle_from_path(graph_context, container_bundle.get_path())

        child_bundles = container.get_child_bundles()

        # Times two because "/instance_n", "/instance_n/shader" both match "/instance_*"
        self.assertEqual(len(child_bundles), instance_count * 2)
