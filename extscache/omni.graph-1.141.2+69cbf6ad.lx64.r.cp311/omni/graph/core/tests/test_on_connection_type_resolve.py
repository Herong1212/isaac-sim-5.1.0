"""Tests for OnConnectionTypeResolve callback"""

import omni.graph.core as og
import omni.graph.core.tests as ogts


# =============================================================================
class RegisteredNodeType:
    """Helper RAII class for registering node types"""

    def __init__(self, node_type_class):
        self._node_type_class = node_type_class
        self._node_type_name = node_type_class.get_node_type()
        self.active = False

    def __enter__(self):
        self.active = True
        og.register_node_type(self._node_type_class, 1)

    def __exit__(self, _exit_type, _value, _exit_traceback):
        if self.active:
            og.deregister_node_type(self._node_type_name)
        self.active = False


# =============================================================================
class TestOnConnectionTypeResolutions(ogts.OmniGraphTestCase):

    _resolve_call_count = 0

    # -------------------------------------------------------------------------
    async def test_on_connection_type_resolve(self):
        """
        Validates on_connection_type_resolve callback gets triggered when type
        resolution changes, or extended dynamic attributes are created or removed
        """
        self._resolve_call_count = 0

        # create a node with an extended attribute that takes integer scalar types
        class OgnConnectTypeTest:
            @staticmethod
            def compute(_context: og.GraphContext, _node: og.Node):
                return True

            @staticmethod
            def on_connection_type_resolve(node: og.Node):
                self._resolve_call_count = self._resolve_call_count + 1  # noqa: PLW0212

            @staticmethod
            def initialize_type(node_type: og.NodeType):
                node_type.add_extended_input("inputs:a", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)
                node_type.add_extended_input("inputs:b", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)

            @staticmethod
            def get_node_type() -> str:
                return "omni.graph.OgnConnectTypeTest"

        with RegisteredNodeType(OgnConnectTypeTest):
            (graph, (node,), _, _) = og.Controller.edit(
                "/TestGraph", {og.Controller.Keys.CREATE_NODES: [("Node", OgnConnectTypeTest.get_node_type())]}
            )

            await og.Controller.evaluate(graph)
            count = self._resolve_call_count

            # resolving an input should call on_connection_type_resolve
            node.get_attribute("inputs:a").set_resolved_type(og.Type(og.BaseDataType.INT))
            await og.Controller.evaluate(graph)
            self.assertGreater(self._resolve_call_count, count)
            count = self._resolve_call_count

            node.get_attribute("inputs:b").set_resolved_type(og.Type(og.BaseDataType.INT))
            await og.Controller.evaluate(graph)
            self.assertGreater(self._resolve_call_count, count)
            count = self._resolve_call_count

            # unresolving an input should call on_connection_type_resolve
            node.get_attribute("inputs:a").set_resolved_type(og.Type(og.BaseDataType.UNKNOWN))
            await og.Controller.evaluate(graph)
            self.assertGreater(self._resolve_call_count, count)
            count = self._resolve_call_count

            # creating a regular attribute should not call type resolve callback
            node.create_attribute(
                "inputs:c", og.Type(og.BaseDataType.INT), og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            )
            await og.Controller.evaluate(graph)
            self.assertEqual(self._resolve_call_count, count)
            count = self._resolve_call_count

            # creating an extended attribute should call the resolve callback
            node.create_attribute(
                "inputs:d",
                og.Type(og.BaseDataType.UNKNOWN),
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                None,
                og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION,
                "int, float",
            )
            await og.Controller.evaluate(graph)
            self.assertGreater(self._resolve_call_count, count)
            count = self._resolve_call_count

            # creating multiple inputs should enable one callback to resolve all
            node.create_attribute(
                "inputs:e",
                og.Type(og.BaseDataType.UNKNOWN),
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                None,
                og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY,
                "",
            )
            node.create_attribute(
                "inputs:f",
                og.Type(og.BaseDataType.UNKNOWN),
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                None,
                og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION,
                "int, float",
            )
            await og.Controller.evaluate(graph)
            self.assertEqual(self._resolve_call_count, count + 1)
            count = self._resolve_call_count

            # resolving a dynamic input should trigger the callback
            node.get_attribute("inputs:f").set_resolved_type(og.Type(og.BaseDataType.INT))
            await og.Controller.evaluate(graph)
            self.assertGreater(self._resolve_call_count, count)
            count = self._resolve_call_count

            # creating an extended attribute output should call the resolve callback
            node.create_attribute(
                "outputs:d",
                og.Type(og.BaseDataType.UNKNOWN),
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
                None,
                og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION,
                "int, float",
            )
            await og.Controller.evaluate(graph)
            self.assertGreater(self._resolve_call_count, count)
            count = self._resolve_call_count

            # creating an extended attribute state should call the resolve callback
            node.create_attribute(
                "state:d",
                og.Type(og.BaseDataType.UNKNOWN),
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE,
                None,
                og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION,
                "int, float",
            )
            await og.Controller.evaluate(graph)
            self.assertGreater(self._resolve_call_count, count)
            count = self._resolve_call_count

            # removing an extended attribute input, output or state should call the callback
            self.assertTrue(node.remove_attribute("inputs:f"))
            await og.Controller.evaluate(graph)
            self.assertGreater(self._resolve_call_count, count)
            count = self._resolve_call_count

            self.assertTrue(node.remove_attribute("outputs:d"))
            await og.Controller.evaluate(graph)
            self.assertGreater(self._resolve_call_count, count)
            count = self._resolve_call_count

            self.assertTrue(node.remove_attribute("state:d"))
            await og.Controller.evaluate(graph)
            self.assertGreater(self._resolve_call_count, count)
            count = self._resolve_call_count
