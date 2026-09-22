"""
Tests that verify action UI-dependent nodes
"""

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test
import omni.usd
from omni.kit.viewport.utility import get_active_viewport
from omni.kit.viewport.utility.camera_state import ViewportCameraState
from pxr import Gf, UsdGeom


# ======================================================================
class TestOmniGraphAction(ogts.OmniGraphTestCase):
    """Encapsulate simple sanity tests"""

    # ----------------------------------------------------------------------
    async def setUp(self):
        await super().setUp()
        viewport_api = get_active_viewport()
        viewport_api.camera_path = "/OmniverseKit_Persp"

    # ----------------------------------------------------------------------
    async def _test_camera_nodes(self, use_prim_connections):
        """Test camera-related node basic functionality"""
        keys = og.Controller.Keys
        controller = og.Controller()

        viewport_api = get_active_viewport()
        active_cam = viewport_api.camera_path
        persp_cam = "/OmniverseKit_Persp"
        self.assertEqual(active_cam.pathString, persp_cam)

        (graph, _, _, _) = controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: [
                    ("OnTick", "omni.graph.action.OnTick"),
                    ("SetCam", "omni.graph.ui_nodes.SetActiveViewportCamera"),
                ],
                keys.SET_VALUES: [
                    ("SetCam.inputs:primPath", "/OmniverseKit_Top"),
                ],
                keys.CONNECT: [("OnTick.outputs:tick", "SetCam.inputs:execIn")],
            },
        )
        await controller.evaluate()
        active_cam = viewport_api.camera_path
        self.assertEqual(active_cam.pathString, "/OmniverseKit_Top")
        # be nice - set it back
        viewport_api.camera_path = persp_cam

        # Create a camera to test with
        stage = omni.usd.get_context().get_stage()
        camera_path = "/TestCam"
        _ = UsdGeom.Camera.Define(stage, camera_path)

        # Tests moving the camera and camera target
        controller.edit(
            graph,
            {
                keys.DISCONNECT: [("OnTick.outputs:tick", "SetCam.inputs:execIn")],
            },
        )
        await controller.evaluate()
        (graph, (_, _, get_pos, get_target), _, _) = controller.edit(
            graph,
            {
                keys.CREATE_NODES: [
                    ("SetPos", "omni.graph.ui_nodes.SetCameraPosition"),
                    ("SetTarget", "omni.graph.ui_nodes.SetCameraTarget"),
                    ("GetPos", "omni.graph.ui_nodes.GetCameraPosition"),
                    ("GetTarget", "omni.graph.ui_nodes.GetCameraTarget"),
                ],
                keys.SET_VALUES: [
                    ("SetPos.inputs:position", Gf.Vec3d(1.0, 2.0, 3.0)),
                    # Target should be different than position
                    ("SetTarget.inputs:target", Gf.Vec3d(-1.0, -2.0, -3.0)),
                ],
                keys.CONNECT: [
                    ("OnTick.outputs:tick", "SetPos.inputs:execIn"),
                    ("SetPos.outputs:execOut", "SetTarget.inputs:execIn"),
                ],
            },
        )

        if use_prim_connections:
            controller.edit(
                graph,
                {
                    keys.CREATE_NODES: [
                        ("ToTarget", "omni.graph.nodes.ToTarget"),
                        ("ConstToken", "omni.graph.nodes.ConstantToken"),
                    ],
                    keys.CONNECT: [
                        ("ConstToken.inputs:value", "ToTarget.inputs:value"),
                        ("ToTarget.outputs:converted", "SetPos.inputs:prim"),
                        ("ToTarget.outputs:converted", "SetTarget.inputs:prim"),
                        ("ToTarget.outputs:converted", "GetPos.inputs:prim"),
                        ("ToTarget.outputs:converted", "GetTarget.inputs:prim"),
                    ],
                    keys.SET_VALUES: [
                        ("SetPos.inputs:usePath", False),
                        ("SetTarget.inputs:usePath", False),
                        ("GetPos.inputs:usePath", False),
                        ("GetTarget.inputs:usePath", False),
                        ("ConstToken.inputs:value", camera_path),
                    ],
                },
            )
        else:
            controller.edit(
                graph,
                {
                    keys.SET_VALUES: [
                        ("SetPos.inputs:primPath", camera_path),
                        ("SetTarget.inputs:primPath", camera_path),
                        ("GetPos.inputs:primPath", camera_path),
                        ("GetTarget.inputs:primPath", camera_path),
                    ],
                },
            )

        await controller.evaluate()
        # XXX: May need to force these calls through legacy_viewport as C++ nodes call through to that interface.
        camera_state = ViewportCameraState(camera_path)  # , viewport=viewport_api, force_legacy_api=True)
        x, y, z = camera_state.position_world
        for a, b in zip([x, y, z], [1.0, 2.0, 3.0]):
            self.assertAlmostEqual(a, b, places=5)
        x, y, z = camera_state.target_world
        for a, b in zip([x, y, z], [-1.0, -2.0, -3.0]):
            self.assertAlmostEqual(a, b, places=5)
        # evaluate again, because push-evaluator may not have scheduled the getters after the setters
        await controller.evaluate()
        get_pos = og.Controller.get(controller.attribute(("outputs:position", get_pos)))
        for a, b in zip(get_pos, [1.0, 2.0, 3.0]):
            self.assertAlmostEqual(a, b, places=5)
        get_target = og.Controller.get(controller.attribute(("outputs:target", get_target)))
        for a, b in zip(get_target, [-1.0, -2.0, -3.0]):
            self.assertAlmostEqual(a, b, places=5)

    # ----------------------------------------------------------------------
    async def test_camera_nodes(self):
        await self._test_camera_nodes(use_prim_connections=False)

    # ----------------------------------------------------------------------
    async def test_camera_nodes_with_prim_connection(self):
        await self._test_camera_nodes(use_prim_connections=True)

    # ----------------------------------------------------------------------
    async def test_on_new_frame(self):
        """Test OnNewFrame node"""
        keys = og.Controller.Keys
        controller = og.Controller()
        # Check that the NewFrame node is getting updated when frames are being generated
        (_, (new_frame_node,), _, _) = controller.edit(
            "/TestGraph", {keys.CREATE_NODES: [("NewFrame", "omni.graph.ui_nodes.OnNewFrame")]}
        )
        attr = controller.attribute(("outputs:frameNumber", new_frame_node))
        await og.Controller.evaluate()
        frame_num = og.Controller.get(attr)
        # Need to tick Kit before evaluation in order to update
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()
        await og.Controller.evaluate()
        self.assertLess(frame_num, og.Controller.get(attr))

    # -------------------------------------------------------------------------
    async def test_get_active_camera_viewport_prim_output(self):
        """Tests the prim output on GetActiveCameraView node returns the correct value"""

        keys = og.Controller.Keys
        controller = og.Controller()

        (graph, (_cam_node, path_node), _, _) = controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: [
                    ("GetCamera", "omni.graph.ui_nodes.GetActiveViewportCamera"),
                    ("GetPrimPath", "omni.graph.nodes.GetPrimPath"),
                ],
                keys.CONNECT: [("GetCamera.outputs:cameraPrim", "GetPrimPath.inputs:prim")],
            },
        )

        await og.Controller.evaluate(graph)
        self.assertEqual(og.Controller.get(("outputs:primPath", path_node)), "/OmniverseKit_Persp")

    # -------------------------------------------------------------------------
    async def test_get_active_camera_viewport_from_file(self):
        """
        Test the prim output on GetActiveCameraView node exists and returns the correct value
        when an older version of the node is loaded from a file.
        """
        (result, error) = await ogts.load_test_file("GetActiveViewportCamera.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)

        # validate the node and attribute exist after loading. The attribute does not exist in the file
        cam_node = og.Controller.node("/World/Graph/get_active_camera")
        self.assertTrue(cam_node.is_valid())
        prim_output = og.Controller.attribute("/World/Graph/get_active_camera.outputs:cameraPrim")
        self.assertTrue(prim_output.is_valid())

        # modify the graph and evaluate it, to verify it gets the expected results
        keys = og.Controller.Keys
        controller = og.Controller()
        (graph, nodes, _, _) = controller.edit(
            "/World/Graph",
            {
                keys.CREATE_NODES: [
                    ("GetPrimPath", "omni.graph.nodes.GetPrimPath"),
                ],
            },
        )

        prim_inputs = nodes[0].get_attribute("inputs:prim")
        controller.connect(prim_output, prim_inputs)

        await og.Controller.evaluate(graph)
        self.assertEqual(og.Controller.get(("outputs:primPath", nodes[0])), "/OmniverseKit_Persp")
