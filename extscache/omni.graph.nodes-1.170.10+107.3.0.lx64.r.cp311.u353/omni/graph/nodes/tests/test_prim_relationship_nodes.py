import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.commands
import omni.kit.test
import OmniGraphSchemaTools


# ======================================================================
class TestPrimRelationshipNodes(ogts.OmniGraphTestCase):
    """Tests read and write prim relationship nodes"""

    TEST_GRAPH_PATH = "/World/TestGraph"

    # ----------------------------------------------------------------------
    async def test_read_prim_relationships(self):
        """Test the read prim relationship nodes that use the new target input/output types"""

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        # For the instanced test, setup a graph like this so that each graph instance looks at the material on a
        # different cube
        #
        # read_var -> to_token -> build_string -> find_prims -> read_prim_relationship
        (
            graph,
            (read, read_test_rel, _, _, _, _),
            (cone,),
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrimRelationship"),
                    ("ReadTestRel", "omni.graph.nodes.ReadPrimRelationship"),
                    ("ReadVar", "omni.graph.core.ReadVariable"),
                    ("ToToken", "omni.graph.nodes.ToToken"),
                    ("BuildString", "omni.graph.nodes.BuildString"),
                    ("FindPrims", "omni.graph.nodes.FindPrims"),
                ],
                keys.CREATE_PRIMS: [
                    ("/World/Cone", "Cone"),
                ],
                keys.SET_VALUES: [
                    ("Read.inputs:name", "material:binding"),
                    ("ReadTestRel.inputs:name", "test_rel"),
                    ("BuildString.inputs:a", "Cube_", og.Type(og.BaseDataType.TOKEN)),
                    ("ReadVar.inputs:variableName", "suffix"),
                    ("FindPrims.inputs:recursive", True),
                ],
                keys.CONNECT: [
                    ("ReadVar.outputs:value", "ToToken.inputs:value"),
                    ("ToToken.outputs:converted", "BuildString.inputs:b"),
                    ("BuildString.outputs:value", "FindPrims.inputs:namePrefix"),
                    ("FindPrims.outputs:prims", "Read.inputs:prim"),
                ],
            },
        )

        await og.Controller.evaluate(graph)

        var = graph.create_variable("suffix", og.Type(og.BaseDataType.INT))

        # Assign materials for instanced example
        num_instances = 3
        for i in range(0, num_instances):
            prim = stage.DefinePrim(f"/World/Cube_{i}", "Cube")
            mat = stage.DefinePrim(f"/World/Material_{i}", "Material")
            omni.kit.commands.execute(
                "AddRelationshipTarget", relationship=prim.CreateRelationship("material:binding"), target=mat.GetPath()
            )

        # Setup example with more than one relationship target
        rel = cone.CreateRelationship("test_rel")
        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(f"{self.TEST_GRAPH_PATH}/ReadTestRel.inputs:prim"),
            target=cone.GetPath(),
        )
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/Material_0")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/Cube_0")

        await controller.evaluate(graph)

        # verify that this works without instancing
        self.assertEqual(read.get_attribute("outputs:value").get(), ["/World/Material_0"])
        self.assertEqual(read_test_rel.get_attribute("outputs:value").get(), ["/World/Material_0", "/World/Cube_0"])

        # create instances
        for i in range(0, num_instances):
            prim_name = f"/World/Instance_{i}"
            stage.DefinePrim(prim_name)
            OmniGraphSchemaTools.applyOmniGraphAPI(stage, prim_name, self.TEST_GRAPH_PATH)
        await og.Controller.evaluate(graph)

        for i in range(0, num_instances):
            var.set(graph.get_default_graph_context(), value=i, instance_path=f"/World/Instance_{i}")
        await og.Controller.evaluate(graph)

        # rerun the graph, this time evaluating instances
        for i in range(0, num_instances):
            self.assertEqual(read.get_attribute("outputs:value").get(instance=i), [f"/World/Material_{i}"])

    # ----------------------------------------------------------------------
    async def test_basic_write_prim_relationships(self):
        """Basic test of write prim relationship node"""

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        # To deterministically schedule write-read operation nodes are split
        # into separate graphs: write and read.
        # That gives control over scheduling writing before reading.
        write_graph_path = "/World/TestGraphWrite"
        read_graph_path = "/World/TestGraphRead"

        (
            write_graph,
            (write,),
            (cone, cube),
            _,
        ) = controller.edit(
            write_graph_path,
            {
                keys.CREATE_NODES: [
                    ("Write", "omni.graph.nodes.WritePrimRelationship"),
                ],
                keys.CREATE_PRIMS: [
                    ("/World/Cone", "Cone"),
                    ("/World/Cube", "Cube"),
                ],
                keys.SET_VALUES: [
                    ("Write.inputs:name", "test_rel"),
                    ("Write.inputs:usdWriteBack", False),
                ],
            },
        )

        (
            read_graph,
            (read,),
            _,
            _,
        ) = controller.edit(
            read_graph_path,
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrimRelationship"),
                ],
                keys.SET_VALUES: [
                    ("Read.inputs:name", "test_rel"),
                ],
            },
        )

        # Setup Write
        rel = stage.GetPropertyAtPath(f"{write_graph_path}/Write.inputs:prim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=cone.GetPath())

        rel = stage.GetPropertyAtPath(f"{write_graph_path}/Write.inputs:value")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=cube.GetPath())

        # Setup Read
        rel = stage.GetPropertyAtPath(f"{read_graph_path}/Read.inputs:prim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target=cone.GetPath())

        # Evaluate write, then read
        await og.Controller.evaluate(write_graph)
        await og.Controller.evaluate(read_graph)

        out = read.get_attribute("outputs:value")
        self.assertEqual(out.get(), ["/World/Cube"])

        # usd write back is false, so this should fail
        self.assertEqual(cone.HasRelationship("test_rel"), False)

        # verify usd write back
        write.get_attribute("inputs:usdWriteBack").set(True)
        await og.Controller.evaluate(write_graph)
        await og.Controller.evaluate(read_graph)
        self.assertEqual(cone.HasRelationship("test_rel"), True)

        # test that relationship is cleared if value is empty
        rel = stage.GetPropertyAtPath(f"{write_graph_path}/Write.inputs:value")
        omni.kit.commands.execute("RemoveRelationshipTarget", relationship=rel, target=cube.GetPath())
        await og.Controller.evaluate(write_graph)
        await og.Controller.evaluate(read_graph)
        self.assertEqual(out.get(), [])

    # ----------------------------------------------------------------------
    async def test_write_prim_relationships_with_instancing(self):
        """Test the write prim relationship nodes wth instancing"""

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (write, read, _, _, _, _, _, _),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Write", "omni.graph.nodes.WritePrimRelationship"),
                    ("Read", "omni.graph.nodes.ReadPrimRelationship"),
                    ("ReadVar", "omni.graph.core.ReadVariable"),
                    ("ToToken", "omni.graph.nodes.ToToken"),
                    ("BuildStringCone", "omni.graph.nodes.BuildString"),
                    ("BuildStringCube", "omni.graph.nodes.BuildString"),
                    ("FindPrimsCone", "omni.graph.nodes.FindPrims"),
                    ("FindPrimsCube", "omni.graph.nodes.FindPrims"),
                ],
                keys.SET_VALUES: [
                    ("Write.inputs:name", "test_rel"),
                    ("Write.inputs:usdWriteBack", False),
                    ("Read.inputs:name", "test_rel"),
                    ("BuildStringCone.inputs:a", "Cone_", og.Type(og.BaseDataType.TOKEN)),
                    ("BuildStringCube.inputs:a", "Cube_", og.Type(og.BaseDataType.TOKEN)),
                    ("ReadVar.inputs:variableName", "suffix"),
                    ("FindPrimsCone.inputs:recursive", True),
                    ("FindPrimsCube.inputs:recursive", True),
                ],
                keys.CONNECT: [
                    ("ReadVar.outputs:value", "ToToken.inputs:value"),
                    ("ToToken.outputs:converted", "BuildStringCone.inputs:b"),
                    ("ToToken.outputs:converted", "BuildStringCube.inputs:b"),
                    ("BuildStringCone.outputs:value", "FindPrimsCone.inputs:namePrefix"),
                    ("BuildStringCube.outputs:value", "FindPrimsCube.inputs:namePrefix"),
                    ("FindPrimsCone.outputs:prims", "Write.inputs:prim"),
                    ("FindPrimsCube.outputs:prims", "Write.inputs:value"),
                    ("FindPrimsCone.outputs:prims", "Read.inputs:prim"),
                ],
            },
        )
        await og.Controller.evaluate(graph)

        var = graph.create_variable("suffix", og.Type(og.BaseDataType.INT))

        # create targets for instanced example
        num_instances = 3
        for i in range(0, num_instances):
            stage.DefinePrim(f"/World/Cone_{i}", "Cone")
            stage.DefinePrim(f"/World/Cube_{i}", "Cube")
        await og.Controller.evaluate(graph)

        # Setting the name input to something else and then back again is needed to trigger the prefetch of the prim
        # correctly. See OM-93232 for more details.  Once we get to the bottom of what's going on there, this should be
        # removed. I'm not entirely sure why this workaround is also not needed in test_basic_write_prim_relationships.
        # And the issue also doesn't happen when this code is run in Kit GUI via the script editor.
        read.get_attribute("inputs:name").set("foo")
        await og.Controller.evaluate(graph)
        read.get_attribute("inputs:name").set("test_rel")
        await og.Controller.evaluate(graph)

        # test without instancing...
        self.assertEqual(read.get_attribute("outputs:value").get(), ["/World/Cube_0"])

        # usd write back is false, so this should fail
        cone = stage.GetPrimAtPath("/World/Cone_0")
        self.assertEqual(cone.HasRelationship("test_rel"), False)

        # verify usd write back
        write.get_attribute("inputs:usdWriteBack").set(True)
        await og.Controller.evaluate(graph)
        self.assertEqual(cone.HasRelationship("test_rel"), True)

        # create instances
        for i in range(0, num_instances):
            prim_name = f"/World/Instance_{i}"
            stage.DefinePrim(prim_name)
            OmniGraphSchemaTools.applyOmniGraphAPI(stage, prim_name, self.TEST_GRAPH_PATH)
        await og.Controller.evaluate(graph)

        for i in range(0, num_instances):
            var.set(graph.get_default_graph_context(), value=i, instance_path=f"/World/Instance_{i}")
        await og.Controller.evaluate(graph)

        # Workaround. See OM-93232
        read.get_attribute("inputs:name").set("foo")
        await og.Controller.evaluate(graph)
        read.get_attribute("inputs:name").set("test_rel")
        await og.Controller.evaluate(graph)

        # rerun the graph, this time evaluating instances
        for i in range(0, num_instances):
            self.assertEqual(read.get_attribute("outputs:value").get(instance=i), [f"/World/Cube_{i}"])
