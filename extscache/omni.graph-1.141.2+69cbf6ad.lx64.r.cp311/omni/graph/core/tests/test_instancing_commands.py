import omni.graph.core as og
import omni.graph.core.tests as ogt
import omni.kit
import omni.usd
import OmniGraphSchema


class TestInstancingCommands(ogt.OmniGraphTestCase):
    """Class that creates tests for OmniGraph instancing commands"""

    # -------------------------------------------------------------------------
    async def test_apply_omni_graph_api(self):
        """Unit tests for commands that apply OmniGraph Commands"""
        num_prims = 5
        prim_paths = [f"/World/Prim{i}" for i in range(0, num_prims)]
        (graph, _, _, _) = og.Controller.edit(
            "/World/TestGraph", {og.Controller.Keys.CREATE_PRIMS: [(prim_path, "Cube") for prim_path in prim_paths]}
        )

        stage = omni.usd.get_context().get_stage()

        def validate_has_api():
            for path in prim_paths:
                prim = stage.GetPrimAtPath(path)
                self.assertTrue(prim.IsValid(), f"Expected prim at f{path}")
                self.assertTrue(prim.HasAPI(OmniGraphSchema.OmniGraphAPI), f"Expected {path} to have API schema")
                schema_prim = OmniGraphSchema.OmniGraphAPI(prim)
                self.assertTrue(bool(schema_prim))
                rel = schema_prim.GetOmniGraphsRel()
                self.assertTrue(rel.IsValid())
                self.assertEqual(
                    rel.GetTargets(),
                    [graph.get_path_to_graph()],
                    f"Expected {path} to have graph path as target {rel.GetTargets()}",
                )

        def validate_no_api():
            for path in prim_paths:
                prim = stage.GetPrimAtPath(path)
                self.assertTrue(prim.IsValid(), f"Expected prim at f{path}")
                self.assertFalse(prim.HasAPI(OmniGraphSchema.OmniGraphAPI), f"Expected {path} to have API schema")

        # run the command
        og.cmds.ApplyOmniGraphAPI(paths=prim_paths, graph_path=graph.get_path_to_graph())
        validate_has_api()

        # undo the command
        omni.kit.undo.undo()
        validate_no_api()

        # redo
        omni.kit.undo.redo()
        validate_has_api()

        # run the removal command
        og.cmds.RemoveOmniGraphAPI(paths=prim_paths)
        validate_no_api()

        # undo
        omni.kit.undo.undo()
        validate_has_api()

        # redo
        omni.kit.undo.redo()
        validate_no_api()
