"""Tests for the runtime node type definition functionality"""

import logging
from contextlib import suppress

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.graph.tools.ogn as ogn
import omni.kit
from omni.graph.core._impl.unstable.attribute_spec import AttributeSpec
from omni.graph.core._impl.unstable.runtime_node_types import (
    NodeTypeCreationError,
    all_runtime_node_types,
    define_node_type,
    deregister_runtime_node_type,
)

_logger = logging.getLogger("OGRuntime")


# ==============================================================================================================
class TestRuntimeNodeTypes(ogts.OmniGraphTestCase):
    # --------------------------------------------------------------------------------------------------------------
    def _print_current_registrations(self):
        """Print out the list of currently registered node types - for debugging"""
        registered = all_runtime_node_types()
        _logger.info("Currently registered runtime node types: %s", len(registered))
        for name, definition in registered.items():
            _logger.info("  %s = %s", name, definition)
            node_type = og.get_node_type(name)
            if node_type is None or not node_type.is_valid():
                _logger.info("  -> Not registered with OmniGraph")
            else:
                _logger.info("  -> Registered with OmniGraph as variant %s", node_type.get_metadata("variant"))

    # --------------------------------------------------------------------------------------------------------------
    async def test_illegal_definitions(self):
        """Test that passing illegal values to create a node type results in errors"""
        # Set of illegal parameters in calls to define_node_type. The arguments are listed with the first four
        # positional arguments (name, version, description, extension) and the optional keyword arguments separate.
        good_args = ("name", 1, "description", "extension")
        illegal_configurations = [
            ((1, 1, "description", "extension"), {}),
            ((["illegal name"], 1, "description", "extension"), {}),
            (("name", -1, "description", "extension"), {}),
            (("name", "version", "description", "extension"), {}),
            (("name", "version", 1, "extension"), {}),
            (("name", 1, {"illegal": "description"}, "extension"), {}),
            (("name", "version", "description", 1), {}),
            (("name", "version", "description", {"illegal": "extension"}), {}),
            (good_args, {"attributes": "None"}),
            (good_args, {"attributes": 1}),
            (good_args, {"attributes": ["BadType"]}),
            (good_args, {"ui_name": 1}),
            (good_args, {"ui_name": ["None"]}),
            (good_args, {"metadata": "None"}),
            (good_args, {"metadata": ["key", "value"]}),
            (good_args, {"method_overrides": 1}),
            (good_args, {"method_overrides": "None"}),
            (good_args, {"method_overrides": ["None"]}),
            (good_args, {"method_overrides": {"not a": "function"}}),
        ]
        for args, kwargs in illegal_configurations:
            with self.assertRaises(NodeTypeCreationError, msg=f"Test arguments {args} {kwargs}"):
                define_node_type(*args, **kwargs)
            # Also check that the faster but unsafe path works, modulo assertions
            with suppress(TypeError, AttributeError):
                define_node_type(*args, **kwargs, bypass_safety_checks=True)

    # --------------------------------------------------------------------------------------------------------------
    async def test_definitions(self):
        """Test basic node type definitions without registering the actual type"""
        # Attribute spec is checked elsewhere so any legal value will do here
        input_spec = AttributeSpec("attrName", og.AttributePortType.INPUT, "float", "Attr description")
        output_spec = AttributeSpec("attrName", og.AttributePortType.OUTPUT, "float", "Attr description")

        # Set of legal parameters in calls to define_node_type. The arguments are listed with the first four
        # positional arguments (name, version, description, extension) and the optional keyword arguments separate.
        good_args = ("name", 1, "description", "extension")
        legal_configurations = [
            (("name", 1, "This is a description", "omni.my.extension"), {}),
            (("omni.my.extension.name", 0, "This is a description", "omni.my.extension"), {}),
            (good_args, {}),
            (good_args, {"attributes": []}),
            (good_args, {"attributes": [input_spec]}),
            (good_args, {"attributes": [input_spec, output_spec]}),
            (good_args, {"ui_name": "This Is A Name"}),
            (good_args, {"ui_name": good_args[0]}),
            (good_args, {"metadata": {}}),
            (good_args, {"metadata": {"hand": "left"}}),
            (good_args, {"metadata": {"eyes": 2}}),
            (good_args, {"metadata": {"nose": "Voldemort", "ears": "Elrond"}}),
            (good_args, {"method_overrides": {}}),
            (good_args, {"method_overrides": {"self_reference": self.test_definitions}}),
        ]

        for args, kwargs in legal_configurations:
            legal_definition = define_node_type(*args, **kwargs)
            self.assertEqual(legal_definition.name, args[0])
            self.assertEqual(legal_definition.version, args[1])
            self.assertEqual(legal_definition.description, args[2])
            self.assertEqual(legal_definition.extension, args[3])

            # If a kwarg was specified then verify it got the right value, else verify it got the default
            if "attributes" in kwargs:
                self.assertCountEqual(list(legal_definition.attribute_dict.values()), kwargs["attributes"])
            else:
                self.assertEqual(legal_definition.attribute_dict, {})
            if "ui_name" in kwargs:
                self.assertEqual(legal_definition.ui_name, kwargs["ui_name"])
            else:
                self.assertEqual(legal_definition.ui_name, "Name")
            if "metadata" in kwargs:
                self.assertEqual(legal_definition.metadata, kwargs["metadata"])
            else:
                self.assertEqual(legal_definition.metadata, {})
            if "method_overrides" in kwargs:
                self.assertEqual(legal_definition.method_overrides, kwargs["method_overrides"])
            else:
                self.assertEqual(legal_definition.method_overrides, {})

            # Make sure the implementation has all required and requested methods
            legal_definition._rebuild_implementation()  # noqa: protected-access
            implementation = legal_definition._implementation  # noqa: protected-access
            self.assertTrue(hasattr(implementation, "compute"))
            self.assertTrue(hasattr(implementation, "get_node_type"))
            for method_name, method_override in kwargs.get("method_overrides", {}).items():
                self.assertEqual(getattr(implementation, method_name, None), method_override)

    # --------------------------------------------------------------------------------------------------------------
    async def test_registrations(self):
        """Test that simple node type definitions get registered"""
        name = "omni.graph.RuntimeTestNode"
        definition = define_node_type(name, 1, "Test node", "omni.graph")
        definition.register()
        try:
            self.assertTrue(name in og.get_registered_nodes())

            (_, (node,), _, _) = og.Controller.edit(
                "/TestGraph", {og.Controller.Keys.CREATE_NODES: ("RuntimeNode", name)}
            )
            await og.Controller.evaluate()
            node_type = node.get_node_type()
            self.assertTrue(node_type.defined_at_runtime())
            self.assertTrue(node_type.is_valid())
            self.assertEqual(node_type.get_node_type(), name)
            self.assertEqual(node, og.get_node_by_path("/TestGraph/RuntimeNode"))
        finally:
            definition.deregister()
        self.assertFalse(name in og.get_registered_nodes())

        await og.Controller.evaluate()
        self.assertTrue(node_type.is_valid())

        # Confirm that registering the same node type again still works
        definition = define_node_type(name, 1, "Test node", "omni.graph")
        definition.register()
        try:
            self.assertTrue(name in og.get_registered_nodes())

            # Confirm that attempting to register the same definition twice fails
            with self.assertRaises(NodeTypeCreationError, msg="Registering the same definition twice"):
                definition.register()

            # Confirm that attempting to register a node type with the same name fails
            duplicate_type = define_node_type(name, 1, "Test node", "omni.graph")
            with self.assertRaises(
                NodeTypeCreationError, msg="Registering a node type of the same name as a registered type"
            ):
                duplicate_type.register()
        finally:
            definition.deregister()

        self.assertFalse(name in og.get_registered_nodes())

    # --------------------------------------------------------------------------------------------------------------
    async def test_metadata(self):
        """Test that metadata is correctly added to the node type definitions"""
        name = "omni.graph.RuntimeTestNode"
        description = "Test node"
        extension = "omni.graph"
        definition = define_node_type(name, 1, description, extension)
        node_type = og.get_node_type(name)
        # Until it is registered the node type should not be available
        self.assertFalse(node_type.is_valid())

        definition.register()
        try:
            node_type = og.get_node_type(name)
            self.assertTrue(node_type.is_valid())

            # Check the default metadata added to every definition
            self.assertEqual(node_type.get_metadata(ogn.MetadataKeys.DESCRIPTION), description)
            self.assertEqual(node_type.get_metadata(ogn.MetadataKeys.EXTENSION), extension)
            self.assertEqual(node_type.get_metadata(ogn.MetadataKeys.LANGUAGE), "Python")
        finally:
            definition.deregister()

        # Create a node type with various metadata values set and confirm they are added
        ui_name = "Runtime Test Node"
        definition = define_node_type(
            name,
            1,
            description,
            extension,
            ui_name=ui_name,
            metadata={ogn.MetadataKeys.HIDDEN: 1, "author": "JRR"},
        )
        definition.register()
        try:
            node_type = og.get_node_type(name)

            self.assertEqual(node_type.get_metadata(ogn.MetadataKeys.HIDDEN), "1")
            self.assertEqual(node_type.get_metadata(ogn.MetadataKeys.UI_NAME), ui_name)
            self.assertEqual(node_type.get_metadata("author"), "JRR")
            self.assertIsNone(node_type.get_metadata("UnSetMetadata"))
        finally:
            definition.deregister()

    # --------------------------------------------------------------------------------------------------------------
    async def test_attribute_additions(self):
        """Test that attributes are correctly added to the node type definitions"""
        input_spec = AttributeSpec("attrName", og.AttributePortType.INPUT, "float", "Input attr description")
        output_spec = AttributeSpec("attrName", og.AttributePortType.OUTPUT, "float", "Output attr description")
        state_spec = AttributeSpec("attrName", og.AttributePortType.STATE, "flout", "State attr description")

        name = "omni.graph.RuntimeTestNode"

        # The typo in the type should make this creation fail
        with self.assertRaises(NodeTypeCreationError, msg="Defining node type with illegal attribute type"):
            _ = define_node_type(name, 1, "Test node", "omni.graph", attributes=[state_spec])
        state_spec.type_name = "float"

        definition = define_node_type(
            name, 1, "Test node", "omni.graph", attributes=[input_spec, output_spec, state_spec]
        )

        definition.register()
        try:
            node_type = og.get_node_type(name)
            (_, (node,), _, _) = og.Controller.edit(
                "/TestGraph", {og.Controller.Keys.CREATE_NODES: ("RuntimeNode", name)}
            )
            await og.Controller.evaluate()
            self.assertTrue(node_type.has_state())
            attributes = node.get_attributes()
            self.assertEqual(len(attributes), 5)
            for attribute in attributes:
                attribute_name = attribute.get_name()
                description = attribute.get_metadata(ogn.MetadataKeys.DESCRIPTION)
                if not attribute_name.endswith("attrName"):
                    continue
                self.assertEqual(attribute.get_resolved_type(), og.Type(base_type=og.BaseDataType.FLOAT))
                port_type = attribute.get_port_type()
                match port_type:
                    case og.AttributePortType.INPUT:
                        self.assertTrue(attribute_name.startswith("inputs:"))
                        self.assertEqual(description, "Input attr description")
                    case og.AttributePortType.OUTPUT:
                        self.assertTrue(attribute_name.startswith("outputs:"))
                        self.assertEqual(description, "Output attr description")
                    case og.AttributePortType.STATE:
                        self.assertTrue(attribute_name.startswith("state:"))
                        self.assertEqual(description, "State attr description")
        finally:
            definition.deregister()

    # --------------------------------------------------------------------------------------------------------------
    async def test_method_overrides_illegal(self):
        """Test that overrides to methods get added to type node type definitions"""
        name = "omni.graph.RuntimeTestNode"

        # Functions missing arguments
        def compute_no_args():
            pass

        def initialize_no_args():
            pass

        def release_no_args():
            pass

        # Functions with incorrect first argument type
        def compute_bad_arg1(context: int, node: og.Node) -> bool:
            pass

        def initialize_bad_arg1(context: int, node: og.Node) -> bool:
            pass

        def release_bad_arg1(node: og.GraphContext) -> bool:
            pass

        # Functions with incorrect second argument type
        def compute_bad_arg2(context: og.GraphContext, node: int) -> bool:
            pass

        def initialize_bad_arg2(context: og.GraphContext, node: int) -> bool:
            pass

        def release_bad_arg2(node: int) -> bool:
            pass

        # Functions with incorrect return value type
        def compute_bad_return(context: og.GraphContext, node: og.Node) -> og.GraphContext:
            pass

        def initialize_bad_return(context: og.GraphContext, node: og.Node) -> int:
            pass

        def release_bad_return(node: og.Node) -> int:
            pass

        test_data = [
            ("no arguments", compute_no_args, initialize_no_args, release_no_args),
            ("bad first arg", compute_bad_arg1, initialize_bad_arg1, release_bad_arg1),
            ("bad last arg", compute_bad_arg2, initialize_bad_arg2, release_bad_arg2),
            ("bad return type", compute_bad_return, initialize_bad_return, release_bad_return),
        ]
        common_args = [name, 1, "Test node", "omni.graph"]

        for error_type, compute_method, initialize_method, release_method in test_data:
            with self.assertRaises(NodeTypeCreationError, msg=f"compute override with {error_type}"):
                define_node_type(*common_args, method_overrides={"compute": compute_method})
            with self.assertRaises(NodeTypeCreationError, msg=f"initialize override with {error_type}"):
                define_node_type(*common_args, method_overrides={"initialize": initialize_method})
            with self.assertRaises(NodeTypeCreationError, msg=f"release override with {error_type}"):
                define_node_type(*common_args, method_overrides={"release": release_method})

    # --------------------------------------------------------------------------------------------------------------
    async def test_method_overrides(self):
        """Test that overrides to methods get added to type node type definitions"""
        name = "omni.graph.RuntimeTestNode"

        def compute(context: og.GraphContext, node: og.Node) -> bool:
            return True

        def compute_lite(context, node):
            return True

        # Check that the two variations of the method definition are accepted
        define_node_type(name, 1, "Test node", "omni.graph", method_overrides={"compute": compute})
        define_node_type(name, 1, "Test node", "omni.graph", method_overrides={"compute": compute_lite})

        # Create a fully defined add node and see that it gets defined, registered, and evaluates properly
        def compute_add(context: og.GraphContext, node: og.Node) -> bool:
            a_input = node.get_attribute("inputs:a")
            b_input = node.get_attribute("inputs:b")
            output = node.get_attribute("outputs:sum")
            output.set(a_input.get() + b_input.get())
            return True

        input_a_spec = AttributeSpec("a", og.AttributePortType.INPUT, "float", "First input")
        input_b_spec = AttributeSpec("b", og.AttributePortType.INPUT, "float", "Second input")
        output_spec = AttributeSpec("sum", og.AttributePortType.OUTPUT, "float", "Sum of inputs")
        definition = define_node_type(
            name,
            1,
            "This is a test add node",
            "omni.graph",
            attributes=[input_a_spec, input_b_spec, output_spec],
            method_overrides={"compute": compute_add},
        )
        definition.register()
        try:
            self.assertTrue(name in og.get_registered_nodes())

            (_, (test_node,), _, _) = og.Controller.edit(
                "/TestGraph",
                {
                    og.Controller.Keys.CREATE_NODES: ("RuntimeNode", name),
                    og.Controller.Keys.SET_VALUES: [("RuntimeNode.inputs:a", 7.0), ("RuntimeNode.inputs:b", 10.0)],
                },
            )
            await og.Controller.evaluate()
            self.assertEqual(og.Controller.attribute(("outputs:sum", test_node)).get(), 17.0)
        finally:
            definition.deregister()

        # Define a node type with an attribute containing metadata and make sure the metadata propagates to the
        # attributes on the created node, in addition to the standard description metadata.

        def initialize(_context: og.GraphContext, node: og.Node):
            """Simple initialize to set up some attribute metadata that can be confirmed"""
            node.get_attribute("inputs:a").set_metadata("testMetadata", "metadataValue")

        definition = define_node_type(
            name,
            1,
            "This is a test add node",
            "omni.graph",
            attributes=[input_a_spec, input_b_spec, output_spec],
            method_overrides={"compute": compute_add, "initialize": initialize},
        )
        definition.register()
        try:
            self.assertTrue(name in og.get_registered_nodes())

            (_, (test_node,), _, _) = og.Controller.edit(
                "/TestGraph",
                {og.Controller.Keys.CREATE_NODES: ("RuntimeNode2", name)},
            )
            await og.Controller.evaluate()
            attr_a = og.Controller.attribute(("inputs:a", test_node))
            self.assertEqual(attr_a.get_metadata(ogn.MetadataKeys.DESCRIPTION), "First input")
            self.assertEqual(attr_a.get_metadata("testMetadata"), "metadataValue")
        finally:
            definition.deregister()

    # --------------------------------------------------------------------------------------------------------------
    async def test_external_deregistration(self):
        """Test that the node type definition is removed if the node type was deregistered through some external
        mechanism. The root cause here will usually be the unloading of an extension but testing that has other
        problems at the moment so a simple API call will be used instead
        """
        name = "omni.graph.RuntimeTestNode"
        definition = define_node_type(name, 1, "Test node", "omni.graph")
        definition.register()
        try:
            self.assertTrue(name in og.get_registered_nodes())
            og.deregister_node_type("omni.graph.RuntimeTestNode")
            self.assertFalse(name in og.get_registered_nodes())
            await omni.kit.app.get_app().next_update_async()  # Give the node type removed event a chance to process
            self.assertFalse(definition.is_registered)
        finally:
            if definition.is_registered:
                definition.deregister()

        self.assertFalse(name in og.get_registered_nodes())

    # --------------------------------------------------------------------------------------------------------------
    async def test_multiple_registrations(self):
        """Try out combinations of registrations to verify iterative creation"""
        name = "omni.graph.RuntimeTestNode"
        definition_1 = define_node_type(name, 1, "Test node", "omni.graph", metadata={"variant": 1})
        definition_2 = define_node_type(name, 1, "Test node", "omni.graph", metadata={"variant": 2})
        definition_3 = define_node_type(name, 1, "Test node", "omni.graph", metadata={"variant": 3})

        definition_1.register()
        await omni.kit.app.get_app().next_update_async()  # Give the node type removed event a chance to process
        try:
            self.assertTrue(name in og.get_registered_nodes())

            # Attempt to register the same definition twice
            with self.assertRaises(NodeTypeCreationError, msg="Attempting to register a duplicate node type name"):
                definition_2.register()

            # Replace the registration of the first variant with the second
            definition_1.deregister()
            definition_2.register()
            node_type = og.get_node_type(name)
            self.assertEqual("2", node_type.get_metadata("variant"))

            # Try to deregister the original after a replacement was made
            with self.assertRaises(NodeTypeCreationError, msg="Attempting to deregister a type that was replaced"):
                definition_1.deregister()

            # Register a chain of three, same name but different definitions
            definition_2.deregister()
            definition_3.register()
            node_type = og.get_node_type(name)
            self.assertEqual("3", node_type.get_metadata("variant"))

            # Modify the definition then register again
            definition_3.metadata["variant"] = "3.1"
            with self.assertRaises(NodeTypeCreationError, msg="Attempting to reregister after an internal change"):
                definition_3.register()
            definition_3.metadata = {"variant": "3.1"}
            definition_3.register()
            node_type = og.get_node_type(name)
            self.assertEqual("3.1", node_type.get_metadata("variant"))

            # Deregister the definition directly rather than through the NodeTypeDefinition
            og.deregister_node_type(name)

            # Register a locally defined one with the same name
            class OgnDuplicate:
                @staticmethod
                def compute(_context: og.GraphContext, _node: og.Node):
                    return True

                @staticmethod
                def get_node_type() -> str:
                    return name

                @staticmethod
                def initialize_type(node_type):
                    node_type.set_metadata("variant", "4")

            await omni.kit.app.get_app().next_update_async()  # Give the node type removed event a chance to process
            og.register_node_type(OgnDuplicate, 2)
            self.assertEqual(2, og.GraphRegistry().get_node_type_version(name))
            og.deregister_node_type(name)
            await omni.kit.app.get_app().next_update_async()  # Give the node type removed event a chance to process

            # Register a new variant now that the local one has been deregistered
            definition_2.register()
            node_type = og.get_node_type(name)
            self.assertEqual("2", node_type.get_metadata("variant"))

            deregister_runtime_node_type(name)
            self.assertFalse(name in og.get_registered_nodes())

        finally:
            for definition in [definition_1, definition_2, definition_3]:
                if definition.is_registered:
                    definition.deregister()

        self.assertFalse(name in og.get_registered_nodes())
