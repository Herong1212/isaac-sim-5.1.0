"""Test cases for extension shutdown"""

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit


# ======================================================================
class TestExtensionShutdown(ogts.OmniGraphTestCase):
    """Testing for extension shutdown"""

    # ----------------------------------------------------------------------
    async def test_om_43835(self):
        """Verify safe ordering of node state release on extension shutdown.
        The test had to be put into this extension so that it could shut down the extension where the test node
        lives without unloading the test itself.
        """
        manager = omni.kit.app.get_app_interface().get_extension_manager()
        test_nodes_extension = "omni.graph.test"
        test_node_type = f"{test_nodes_extension}.TestGracefulShutdown"
        was_extension_enabled = manager.is_extension_enabled(test_nodes_extension)

        try:
            manager.set_extension_enabled_immediate(test_nodes_extension, True)
            self.assertTrue(manager.is_extension_enabled(test_nodes_extension))

            # Creating a node is all that it takes to set up the state information required by the test
            controller = og.Controller()
            (graph, _, _, _) = controller.edit(
                "/TestGraph",
                {
                    og.Controller.Keys.CREATE_NODES: ("TestNode", test_node_type),
                },
            )
            await controller.evaluate(graph)

            # Unloading the extension triggers the state release, which will test the necessary conditions
            manager.set_extension_enabled_immediate(test_nodes_extension, False)

            self.assertEqual(0, og.test_failure_count(), "Test failure was reported by the node state")
        finally:
            manager.set_extension_enabled_immediate(test_nodes_extension, was_extension_enabled)
