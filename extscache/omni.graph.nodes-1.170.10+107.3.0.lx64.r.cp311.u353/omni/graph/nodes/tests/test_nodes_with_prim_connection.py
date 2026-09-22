import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.commands
import omni.kit.test
import omni.timeline
import omni.usd
from pxr import Gf, Sdf

from .fsd_helpers import get_rotation, get_transform, get_translation


# ======================================================================
class TestNodesWithPrimConnection(ogts.OmniGraphTestCase):
    """Tests node using a target connection to a prim"""

    TEST_GRAPH_PATH = "/World/TestGraph"

    # -----------------------------------------------------------------------------------
    async def setUp(self):
        await super().setUp()
        omni.timeline.get_timeline_interface().set_start_time(1.0)
        omni.timeline.get_timeline_interface().set_end_time(100000)
        omni.timeline.get_timeline_interface().set_play_every_frame(True)

    # -----------------------------------------------------------------------------------
    async def tearDown(self):
        omni.timeline.get_timeline_interface().stop()
        omni.timeline.get_timeline_interface().set_play_every_frame(False)
        await super().tearDown()

    # -----------------------------------------------------------------------------------
    async def test_read_prim_attribute_with_connected_prims(self):
        """
        Tests that ReadPrimAttributes nodes works correctly with their prim attribute is connected
        using a target attribute port
        """

        node = "omni.graph.nodes.ReadPrimAttribute"
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        (graph, (read_prim, _, _), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("ReadNode", node),
                    ("ToTarget", "omni.graph.nodes.ToTarget"),
                    ("ConstToken", "omni.graph.nodes.ConstantToken"),
                ],
                keys.CONNECT: [("ConstToken.inputs:value", "ToTarget.inputs:value")],
                keys.CREATE_PRIMS: [
                    ("/World/Cube1", {"dummy_prop": ("float", 1)}, "Cube"),
                    ("/World/Cube2", {"dummy_prop": ("float", 2)}, "Cube"),
                ],
                keys.SET_VALUES: [("ReadNode.inputs:name", "dummy_prop"), ("ConstToken.inputs:value", "/World/Cube2")],
            },
        )

        rel = stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/ReadNode.inputs:prim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/Cube1")

        # evaluate the unconnected graph with the first cube set directly
        await og.Controller.evaluate(graph)
        self.assertEquals(1, read_prim.get_attribute("outputs:value").get())

        # connect the PrimPathNode, which is set to the second cube
        controller.edit(self.TEST_GRAPH_PATH, {keys.CONNECT: [("ToTarget.outputs:converted", "ReadNode.inputs:prim")]})

        # validate the prim attribute is read from the correct attribute
        await og.Controller.evaluate(graph)
        self.assertEquals(2, read_prim.get_attribute("outputs:value").get())

    # -----------------------------------------------------------------------------------
    async def test_read_prim_attributes_with_connected_prims(self):
        """
        Tests that ReadPrimAttributes nodes works correctly with their prim attribute is connected
        using a target attribute port
        """

        node = "omni.graph.nodes.ReadPrimAttributes"
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        (graph, (_, _, _, to_string), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("ReadNode", node),
                    ("ToTarget", "omni.graph.nodes.ToTarget"),
                    ("ConstToken", "omni.graph.nodes.ConstantToken"),
                    ("ToString", "omni.graph.nodes.ToString"),  # the output needs to be connected
                ],
                keys.CREATE_PRIMS: [
                    ("/World/Cube1", "Cube"),
                    ("/World/Cube2", "Cube"),
                ],
                keys.CONNECT: [
                    ("ConstToken.inputs:value", "ToTarget.inputs:value"),
                ],
                keys.SET_VALUES: [
                    ("ReadNode.inputs:attrNamesToImport", "**"),
                    ("ConstToken.inputs:value", "/World/Cube2"),
                ],
            },
        )

        rel = stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/ReadNode.inputs:prim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/Cube1")

        # evaluate the unconnected graph with the first cube set directly
        await og.Controller.evaluate(graph)

        # ReadPrimAttribute only copies values on connected values
        controller.edit(
            self.TEST_GRAPH_PATH, {keys.CONNECT: [("ReadNode.outputs:sourcePrimPath", "ToString.inputs:value")]}
        )

        # run the graph again
        await og.Controller.evaluate(graph)
        self.assertEquals("/World/Cube1", og.Controller.get(("outputs:converted", to_string)))

        # connect the PrimPathNode, which is set to the second cube
        controller.edit(self.TEST_GRAPH_PATH, {keys.CONNECT: [("ToTarget.outputs:converted", "ReadNode.inputs:prim")]})
        await og.Controller.evaluate(graph)

        # reconnect the output (a change in prims changes the outputs)
        controller.edit(
            self.TEST_GRAPH_PATH, {keys.CONNECT: [("ReadNode.outputs:sourcePrimPath", "ToString.inputs:value")]}
        )
        await og.Controller.evaluate(graph)

        # validate the prim attribute is read from the correct attribute
        self.assertEquals("/World/Cube2", og.Controller.get(("outputs:converted", to_string)))

    # -----------------------------------------------------------------------------------
    async def _test_read_prim_node_with_connected_prims(self, node):

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        (graph, (_read_prim, _, _, extract_node, _extract_bundle, _extract_prim), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("ReadNode", node),
                    ("ToTarget", "omni.graph.nodes.ToTarget"),
                    ("ConstToken", "omni.graph.nodes.ConstantToken"),
                    ("ExtractAttr", "omni.graph.nodes.ExtractAttribute"),
                    ("ExtractBundle", "omni.graph.nodes.ExtractBundle"),
                    ("ExtractPrim", "omni.graph.nodes.ExtractPrim"),
                ],
                keys.CONNECT: [
                    ("ConstToken.inputs:value", "ToTarget.inputs:value"),
                    ("ReadNode.outputs_primsBundle", "ExtractPrim.inputs:prims"),
                    ("ExtractPrim.outputs_primBundle", "ExtractBundle.inputs:bundle"),
                    ("ExtractBundle.outputs_passThrough", "ExtractAttr.inputs:data"),
                ],
                keys.CREATE_PRIMS: [
                    ("/World/Cube1", {"dummy_prop": ("float", 1)}, "Cube"),
                    ("/World/Cube2", {"dummy_prop": ("float", 2)}, "Cube"),
                ],
                keys.SET_VALUES: [
                    ("ReadNode.inputs:attrNamesToImport", "dummy_prop"),
                    ("ExtractAttr.inputs:attrName", "dummy_prop"),
                    ("ExtractPrim.inputs:primPath", "/World/Cube1"),
                    ("ConstToken.inputs:value", "/World/Cube2"),
                ],
            },
        )

        rel = stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/ReadNode.inputs:prims")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/Cube1")

        # evaluate the unconnected graph with the first cube set directly
        await og.Controller.evaluate(graph)
        self.assertEquals(1, og.Controller.get(("outputs:output", extract_node)))

        # connect the PrimPathNode, which is set to the second cube
        controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CONNECT: [("ToTarget.outputs:converted", "ReadNode.inputs:prims")],
                keys.SET_VALUES: [("ExtractPrim.inputs:primPath", "/World/Cube2")],
            },
        )

        # validate the prim attribute is read from the correct attribute
        await og.Controller.evaluate(graph)
        self.assertEquals(2, og.Controller.get(("outputs:output", extract_node)))

    # -----------------------------------------------------------------------------------
    async def test_read_prims_with_connected_prims(self):
        """Tests that ReadPrims node can be connected at the prim port"""
        await self._test_read_prim_node_with_connected_prims("omni.graph.nodes.ReadPrims")

    # -----------------------------------------------------------------------------------
    async def test_read_prims_bundle_with_connected_prims(self):
        """Tests that ReadPrims node can be connected at the prim port"""
        await self._test_read_prim_node_with_connected_prims("omni.graph.nodes.ReadPrimsBundle")

    # -----------------------------------------------------------------------------------
    async def test_write_prim_attribute_with_connected_prim(self):
        """Test that WritePrimAttribute can be connected at the prim port"""

        node = "omni.graph.nodes.WritePrimAttribute"
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        (graph, (_write_prim, _, _, _), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("WriteNode", node),
                    ("ToTarget", "omni.graph.nodes.ToTarget"),
                    ("ConstToken", "omni.graph.nodes.ConstantToken"),
                    ("ConstValue", "omni.graph.nodes.ConstantFloat"),
                ],
                keys.CONNECT: [
                    ("ConstToken.inputs:value", "ToTarget.inputs:value"),
                    ("ConstValue.inputs:value", "WriteNode.inputs:value"),
                ],
                keys.CREATE_PRIMS: [
                    ("/World/Cube1", {"dummy_prop": ("float", 1)}, "Cube"),
                    ("/World/Cube2", {"dummy_prop": ("float", 2)}, "Cube"),
                ],
                keys.SET_VALUES: [
                    ("WriteNode.inputs:name", "dummy_prop"),
                    ("ConstToken.inputs:value", "/World/Cube2"),
                    ("ConstValue.inputs:value", 3.0),
                    ("WriteNode.inputs:usdWriteBack", True),
                ],
            },
        )

        rel = stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/WriteNode.inputs:prim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/Cube1")

        # evaluate the unconnected graph with the first cube set directly
        await og.Controller.evaluate(graph)
        self.assertEquals(3, stage.GetAttributeAtPath("/World/Cube1.dummy_prop").Get())

        # connect the PrimPathNode, which is set to the second cube
        controller.edit(self.TEST_GRAPH_PATH, {keys.CONNECT: [("ToTarget.outputs:converted", "WriteNode.inputs:prim")]})

        # validate the prim attribute is read from the correct attribute
        await og.Controller.evaluate(graph)
        self.assertEquals(3, stage.GetAttributeAtPath("/World/Cube2.dummy_prop").Get())

    # --------------------------------------------------------------------------------------
    async def _test_generic_with_connected_prim_setup(self, node_name, prim_input="prim", use_path="usePath"):
        """Creates a graph set with the given node, two prims (cubes) and sets the path to first prim"""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        (graph, (node, _, _), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Node", node_name),
                    ("ToTarget", "omni.graph.nodes.ToTarget"),
                    ("ConstToken", "omni.graph.nodes.ConstantToken"),
                ],
                keys.CONNECT: [
                    ("ConstToken.inputs:value", "ToTarget.inputs:value"),
                ],
                keys.CREATE_PRIMS: [
                    ("/World/Cube1", "Cube"),
                    ("/World/Cube2", "Cube"),
                ],
                keys.SET_VALUES: [
                    (f"Node.inputs:{use_path}", False),
                    ("ConstToken.inputs:value", "/World/Cube2"),
                ],
            },
        )

        # make sure the prims have the correct transform attributes
        for prim_path in ["/World/Cube1", "/World/Cube2"]:
            prim = stage.GetPrimAtPath(prim_path)
            prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
            prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
            prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(1.0, 1.0, 1.0))
            prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
                ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
            )

        rel = stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/Node.inputs:{prim_input}")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/Cube1")

        omni.timeline.get_timeline_interface().play()
        return (controller, graph, node)

    def _connect_prim_path_node(self, controller):
        """
        Helper to connect the prim path node from the graph created in _test_generic_with_connected_prim_setup
        """
        controller.edit(
            self.TEST_GRAPH_PATH,
            {
                og.Controller.Keys.CONNECT: [("ToTarget.outputs:converted", "Node.inputs:prim")],
            },
        )

    # --------------------------------------------------------------------------------------
    async def _advance(self, graph, delta_time=0.01):
        """
        Helper routine to wait for minimum amount of time to pass
        Requires the timeline to be playing
        """
        timeline = omni.timeline.get_timeline_interface()
        t = timeline.get_current_time() + delta_time
        await og.Controller.evaluate(graph)
        while timeline.get_current_time() < t:
            await omni.kit.app.get_app().next_update_async()
            if not timeline.is_playing():
                raise og.OmniGraphError("_advance expected the timeline to be playing")

    # --------------------------------------------------------------------------------------
    async def test_get_prim_direction_vector_with_connected_prim(self):
        """Test GetPrimDirectorVector works with a connected prim"""

        (controller, graph, node) = await self._test_generic_with_connected_prim_setup(
            "omni.graph.nodes.GetPrimDirectionVector"
        )

        # rotate the second cube
        stage = omni.usd.get_context().get_stage()
        stage.GetAttributeAtPath("/World/Cube2.xformOp:rotateXYZ").Set(Gf.Vec3d(0, 180, 0))

        # evaluate the unconnected graph with the first cube set directly
        await og.Controller.evaluate(graph)
        self.assertListEqual([0, 0, -1], list(og.Controller.get(("outputs:forwardVector", node))))

        # connect the PrimPathNode, which is set to the second cube
        self._connect_prim_path_node(controller)

        # connect the PrimPathNode, which is set to the second cube
        # validate the prim attribute is read from the correct attribute
        await og.Controller.evaluate(graph)
        vec = og.Controller.get(("outputs:forwardVector", node))
        self.assertAlmostEqual(0, vec[0])
        self.assertAlmostEqual(0, vec[1])
        self.assertAlmostEqual(1, vec[2])

    # --------------------------------------------------------------------------------------
    async def test_get_prim_local_to_world_with_connected_prim(self):
        """Test GetPrimLocalToWorldTransform works with a connected prim"""

        (controller, graph, node) = await self._test_generic_with_connected_prim_setup(
            "omni.graph.nodes.GetPrimLocalToWorldTransform"
        )

        # rotate the second cube
        stage = omni.usd.get_context().get_stage()
        stage.GetAttributeAtPath("/World/Cube2.xformOp:rotateXYZ").Set(Gf.Vec3d(0, 180, 0))

        # evaluate the unconnected graph with the first cube set directly
        await og.Controller.evaluate(graph)
        matrix = og.Controller.get(("outputs:localToWorldTransform", node))
        matrix = [round(i) for i in matrix]
        self.assertListEqual([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], matrix)

        # connect the PrimPathNode, which is set to the second cube
        self._connect_prim_path_node(controller)

        # validate the prim attribute is read from the correct attribute
        await og.Controller.evaluate(graph)
        matrix = og.Controller.get(("outputs:localToWorldTransform", node))
        matrix = [round(i) for i in matrix]
        self.assertListEqual([-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1], matrix)

    # --------------------------------------------------------------------------------------
    async def test_get_prim_relationship_with_connected_prim(self):
        """Test GetPrimRelationship works with a connected prim"""

        (controller, graph, node) = await self._test_generic_with_connected_prim_setup(
            "omni.graph.nodes.GetPrimRelationship"
        )
        self._connect_prim_path_node(controller)

        # set up a relationship from the connected to cube
        stage = omni.usd.get_context().get_stage()
        stage.GetPrimAtPath("/World/Cube2").CreateRelationship("dummy_rel").AddTarget("/World/Cube1")

        # mark the attribute
        og.Controller.set(("inputs:name", node), "dummy_rel")

        await og.Controller.evaluate(graph)

        self.assertEqual(["/World/Cube1"], og.Controller.get(("outputs:paths", node)))

    # --------------------------------------------------------------------------------------
    async def test_move_to_target_with_connected_prim(self):
        """Test MoveToTarget works with a connected prim"""
        (_controller, graph, node) = await self._test_generic_with_connected_prim_setup(
            "omni.graph.nodes.MoveToTarget", "sourcePrim", "useSourcePath"
        )

        # connect the destination
        stage = omni.usd.get_context().get_stage()
        rel = stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/Node.inputs:targetPrim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/Cube2")

        stage.GetAttributeAtPath("/World/Cube1.xformOp:translate").Set(Gf.Vec3d(1, 0, 0))
        stage.GetAttributeAtPath("/World/Cube2.xformOp:translate").Set(Gf.Vec3d(1000, 0, 0))
        og.Controller.set(("inputs:speed", node), 0.1)

        # validate the source cube is moving away from the source
        last_x = 0.99  # first frame is 1
        for _ in range(0, 5):
            await self._advance(graph)
            x = get_translation(stage.GetPrimAtPath("/World/Cube1"))[0]
            self.assertGreater(x, last_x)
            last_x = x

    # --------------------------------------------------------------------------------------
    async def test_move_to_transform_with_connected_prim(self):
        """Test MoveToTransform works with a connected prim"""
        (_controller, graph, node) = await self._test_generic_with_connected_prim_setup(
            "omni.graph.nodes.MoveToTransform"
        )

        # connect the destination
        stage = omni.usd.get_context().get_stage()

        stage.GetAttributeAtPath("/World/Cube1.xformOp:translate").Set(Gf.Vec3d(1, 0, 0))
        stage.GetPrimAtPath("/World/Cube1").CreateAttribute("xformOp:orient", Sdf.ValueTypeNames.Quatd, False).Set(
            Gf.Quatd(0)
        )
        stage.GetPrimAtPath("/World/Cube1").CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
            ["xformOp:translate", "xformOp:orient"]
        )

        og.Controller.set(("inputs:speed", node), 0.1)
        og.Controller.set(("inputs:target", node), Gf.Matrix4d(1).SetTranslate(Gf.Vec3d(1000, 0, 0)))

        # validate the source cube is moving away from the source
        last_x = 0.99  # first frame is 1
        for _ in range(0, 5):
            await self._advance(graph)
            x = get_translation(stage.GetPrimAtPath("/World/Cube1"))[0]
            self.assertGreater(x, last_x)
            last_x = x

    # --------------------------------------------------------------------------------------
    async def test_rotate_to_target_with_connected_prim(self):
        """Test RotateToTarget works with a connected prim"""
        (_controller, graph, node) = await self._test_generic_with_connected_prim_setup(
            "omni.graph.nodes.RotateToTarget", "sourcePrim", "useSourcePath"
        )

        # connect the destination
        stage = omni.usd.get_context().get_stage()
        rel = stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/Node.inputs:targetPrim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/Cube2")

        quat1 = Gf.Rotation().SetIdentity().GetQuat()
        quat2 = Gf.Rotation().SetAxisAngle(Gf.Vec3d.YAxis(), 180).GetQuat()
        stage.GetAttributeAtPath("/World/Cube1.xformOp:translate").Set(Gf.Vec3d(0, 0, 0))
        stage.GetAttributeAtPath("/World/Cube2.xformOp:translate").Set(Gf.Vec3d(0, 0, 0))
        stage.GetPrimAtPath("/World/Cube1").CreateAttribute("xformOp:orient", Sdf.ValueTypeNames.Quatd, False).Set(
            quat1
        )
        stage.GetPrimAtPath("/World/Cube2").CreateAttribute("xformOp:orient", Sdf.ValueTypeNames.Quatd, False).Set(
            quat2
        )
        stage.GetPrimAtPath("/World/Cube1").CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
            ["xformOp:translate", "xformOp:orient", "xformOp:scale"]
        )
        stage.GetPrimAtPath("/World/Cube2").CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
            ["xformOp:translate", "xformOp:orient", "xformOp:scale"]
        )
        og.Controller.set(("inputs:speed", node), 0.02)  # very slow moving

        last_rot = quat2
        for _ in range(0, 5):
            await self._advance(graph)
            rot = get_rotation(stage.GetPrimAtPath("/World/Cube1"))
            self.assertNotEqual(rot, last_rot)
            last_rot = rot

    # --------------------------------------------------------------------------------------
    async def test_rotate_to_orientation_with_connected_prim(self):
        """Test RotateToOrientation works with a connected prim"""
        (_controller, graph, node) = await self._test_generic_with_connected_prim_setup(
            "omni.graph.nodes.RotateToOrientation"
        )

        # connect the destination
        stage = omni.usd.get_context().get_stage()

        quat1 = Gf.Rotation().SetIdentity().GetQuat()
        stage.GetAttributeAtPath("/World/Cube1.xformOp:translate").Set(Gf.Vec3d(0, 0, 0))
        stage.GetPrimAtPath("/World/Cube1").CreateAttribute("xformOp:orient", Sdf.ValueTypeNames.Quatd, False).Set(
            quat1
        )
        stage.GetPrimAtPath("/World/Cube1").CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
            ["xformOp:translate", "xformOp:orient", "xformOp:scale"]
        )
        og.Controller.set(("inputs:speed", node), 0.02)  # very slow moving
        og.Controller.set(("inputs:target", node), (0, 180, 0))

        last_rot = Gf.Rotation().SetAxisAngle(Gf.Vec3d.YAxis(), 180).GetQuat()
        for _ in range(0, 5):
            await self._advance(graph)
            rot = get_rotation(stage.GetPrimAtPath("/World/Cube1"), True)
            self.assertNotEqual(rot, last_rot)
            last_rot = rot

    # --------------------------------------------------------------------------------------
    async def test_scale_to_size_with_connected_prim(self):
        """Test ScaleToSize works with a connected prim"""
        (_controller, graph, node) = await self._test_generic_with_connected_prim_setup("omni.graph.nodes.ScaleToSize")

        # connect the destination
        stage = omni.usd.get_context().get_stage()

        stage.GetAttributeAtPath("/World/Cube1.xformOp:scale").Set(Gf.Vec3d(1, 1, 1))
        og.Controller.set(("inputs:speed", node), 0.1)
        og.Controller.set(("inputs:target", node), (1000, 1000, 1000))

        # validate the source cube is moving away from the source
        last_x = 0.99  # first frame is 1
        for _ in range(0, 5):
            await self._advance(graph)
            cube1 = get_transform(stage.GetPrimAtPath("/World/Cube1"), True)
            x = cube1[0][0]
            self.assertGreater(x, last_x)
            last_x = x

    # --------------------------------------------------------------------------------------
    async def test_translate_to_target_with_connected_prim(self):
        """Test TranslateToTarget works with a connected prim"""
        (_controller, graph, node) = await self._test_generic_with_connected_prim_setup(
            "omni.graph.nodes.TranslateToTarget", "sourcePrim", "useSourcePath"
        )

        # connect the destination
        stage = omni.usd.get_context().get_stage()
        rel = stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/Node.inputs:targetPrim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/Cube2")

        stage.GetAttributeAtPath("/World/Cube1.xformOp:translate").Set(Gf.Vec3d(1, 0, 0))
        stage.GetAttributeAtPath("/World/Cube2.xformOp:translate").Set(Gf.Vec3d(1000, 0, 0))
        og.Controller.set(("inputs:speed", node), 0.1)

        # validate the source cube is moving away from the source
        last_x = 0.99  # first frame is 1
        for _ in range(0, 5):
            await self._advance(graph)
            cube1 = get_transform(stage.GetPrimAtPath("/World/Cube1"), True)
            x = cube1.ExtractTranslation()[0]
            self.assertGreater(x, last_x)
            last_x = x

    # --------------------------------------------------------------------------------------
    async def test_translate_to_location_with_connected_prim(self):
        """Test TranslateToLocation works with a connected prim"""
        (_controller, graph, node) = await self._test_generic_with_connected_prim_setup(
            "omni.graph.nodes.TranslateToLocation"
        )

        # connect the destination
        stage = omni.usd.get_context().get_stage()

        stage.GetAttributeAtPath("/World/Cube1.xformOp:translate").Set(Gf.Vec3d(1, 0, 0))
        stage.GetPrimAtPath("/World/Cube1").CreateAttribute("xformOp:orient", Sdf.ValueTypeNames.Quatd, False).Set(
            Gf.Quatd(0)
        )
        stage.GetPrimAtPath("/World/Cube1").CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
            ["xformOp:translate", "xformOp:orient"]
        )

        og.Controller.set(("inputs:speed", node), 0.1)
        og.Controller.set(("inputs:target", node), Gf.Vec3d(1000, 0, 0))

        # validate the source cube is moving away from the source
        last_x = 0.99  # first frame is 1
        for _ in range(0, 5):
            await self._advance(graph)
            x = get_translation(stage.GetPrimAtPath("/World/Cube1"), True)[0]
            self.assertGreater(x, last_x)
            last_x = x
