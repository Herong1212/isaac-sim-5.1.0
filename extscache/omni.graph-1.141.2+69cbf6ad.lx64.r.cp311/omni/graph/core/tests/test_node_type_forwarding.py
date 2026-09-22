"""Tests that exercise the INodeTypeForwarding2 interface"""

import json

import omni.graph.core as og
import omni.graph.core._unstable as ogu
import omni.graph.core.tests as ogts
import omni.kit.test
import omni.usd


# ==============================================================================================================
class TestNodeTypeForwarding(omni.kit.test.AsyncTestCase):
    def _test_interface(self, interface_class: object, get_interface_fn: callable):
        """Shared code to test a specific interface class that can be used for the unstable and stable versions"""
        instance_methods = ["define_forward", "remove_forward", "remove_forwarded_type"]
        # The new interface has an extra method
        if interface_class.__name__ == "INodeTypeForwarding2":
            instance_methods.append("inspect")

        ogts.validate_abi_interface(
            interface_class,
            instance_methods=instance_methods,
            static_methods=[
                "find_forward",
                "get_forwarding",
            ],
            properties=["forward_count"],
        )

        self.assertIsNotNone(get_interface_fn)
        interface = get_interface_fn()
        self.assertIsNotNone(interface)
        self.assertTrue(isinstance(interface, interface_class))

        try:
            # Try defining a simple forward
            original_forwarding = interface.forward_count
            replacement = ("ReplacementNodeType", 1, "omni.test.extension")
            original = ("ForwardedNodeType", 2)
            self.assertTrue(interface.define_forward(*original, *replacement))
            self.assertEqual(original_forwarding + 1, interface.forward_count)

            all_forwarding = interface.get_forwarding()
            self.assertEqual(all_forwarding[original], replacement)

            found_forward = interface.find_forward(*original)
            self.assertEqual(found_forward, replacement)

            # Define a second forward
            secondary_replacement = ("SecondNodeType", 4, "omni.test.extension")
            secondary = ("SomeOtherNodeType", 2)
            self.assertTrue(interface.define_forward(*secondary, *secondary_replacement))
            self.assertEqual(original_forwarding + 2, interface.forward_count)
            all_forwarding = interface.get_forwarding()
            self.assertEqual(all_forwarding[original], replacement)
            self.assertEqual(all_forwarding[secondary], secondary_replacement)

            # Define a chained forward ("ChainedNodeType", 1) -> ("ReplacementNodeType", 1) -> ("ForwardedNodeType", 2)
            chained_replacement = ("ChainedNodeType", 1, "omni.test.extension")
            chained = (replacement[0], replacement[1])
            self.assertTrue(interface.define_forward(*chained, *chained_replacement))
            found_forward = interface.find_forward(*chained)
            self.assertEqual(found_forward, chained_replacement)
            found_forward = interface.find_forward(*original)
            self.assertEqual(found_forward, chained_replacement)

            # Define a few forwarding for the same node type at different versions
            # ("ReplacementNodeType", 1) -> ("ForwardedNodeType", 2, "omni.test.extension")
            # ("ReplacementNodeType", 3) -> ("BetterNodeType", 1, "omni.borg.extension")
            # ("ReplacementNodeType", 7) -> ("SecondaryNodeType", 4, "omni.test.extension")
            better_replacement = ("BetterNodeType", 4, "omni.borg.extension")
            latest_forward = (replacement[0], replacement[1] + 2)
            self.assertTrue(interface.define_forward(*latest_forward, *better_replacement))
            prototype_forward = (replacement[0], replacement[1] + 6)
            self.assertTrue(interface.define_forward(*prototype_forward, *secondary_replacement))
            # What the "replacement" forward is expected to map to for the version equal to the index of the list...
            expected_versions = [
                chained_replacement,
                chained_replacement,
                better_replacement,
                better_replacement,
                better_replacement,
                better_replacement,
                secondary_replacement,
                secondary_replacement,
                secondary_replacement,
            ]
            for index, version_to_test in enumerate(expected_versions):
                self.assertEqual(
                    version_to_test,
                    interface.find_forward(replacement[0], index + 1),
                    f"Checking {replacement[0]}-{index + 1} maps to {version_to_test}",
                )

            # Confirm that the inspection runs and returns valid JSON data.
            if interface_class.__name__ == "INodeTypeForwarding2":
                forwards_as_json_string = og.OmniGraphInspector().as_json(interface)
                forwards_as_json = json.loads(forwards_as_json_string)
                self.assertTrue(original[0] in forwards_as_json)

            # Ensure that attempting to look up a version earlier than the first forward returns nothing
            early_version = (replacement[0], 0)
            with self.assertRaises(ValueError):
                interface.find_forward(*early_version)

            # Attempt to define a forward to itself, which should not be allowed
            circular = (chained_replacement[0], chained_replacement[1])
            with ogts.ExpectedError():
                self.assertFalse(interface.define_forward(*circular, *chained_replacement))

            # Attempt to define a multiple-step circular forward, which should not be allowed
            # ("ChainedNodeType", 1) -> ("ReplacementNodeType", 1) -> ("ForwardedNodeType", 2) -> ("ChainedNodeType", 1)
            with ogts.ExpectedError():
                self.assertFalse(interface.define_forward(*chained, original[0], original[1], "omni.test.extension"))

            # Attempt to redefine the same forward, which should not be allowed but will only provide a warning
            with ogts.ExpectedError():
                self.assertTrue(interface.define_forward(*chained, *chained_replacement))

        finally:
            # Remove all of the forwarding, in reverse order so that earlier failures clean up after themselves
            self.assertTrue(interface.remove_forward(*prototype_forward))
            self.assertTrue(interface.remove_forward(*latest_forward))
            self.assertTrue(interface.remove_forward(*chained))
            self.assertTrue(interface.remove_forward(*secondary))
            self.assertTrue(interface.remove_forward(*original))

            self.assertEqual(original_forwarding, interface.forward_count)

    # --------------------------------------------------------------------------------------------------------------
    async def test_the_bindings(self):
        """Test to make sure any use of the unstable and current versions of the interface works"""
        self._test_interface(ogu.INodeTypeForwarding, ogu.get_node_type_forwarding_interface)
        self._test_interface(og.INodeTypeForwarding2, og.get_node_type_forwarding_interface2)

    # --------------------------------------------------------------------------------------------------------------
    async def test_om_106665(self):
        """Tests that the sequence that reveals bug OM-106665 has been fixed"""
        get_interface = og.get_node_type_forwarding_interface2
        self.assertIsNotNone(get_interface)
        interface = get_interface()
        self.assertIsNotNone(interface)
        self.assertTrue(isinstance(interface, og.INodeTypeForwarding2))

        old_node_type = "omni.old.extension.MyNode"
        new_node_type = "omni.new.extension.MyNode"
        ext_name = "omni.new.extension"

        # Ordering is important here. In bug OM-106665 there is a crash if the forwards are defined highest version
        # to lowest but not if they are defined lowest to highest.
        try:
            self.assertTrue(interface.define_forward(old_node_type, 3, new_node_type, 3, ext_name))
            self.assertTrue(interface.define_forward(old_node_type, 1, new_node_type, 1, ext_name))
            self.assertTrue(interface.define_forward(old_node_type, 2, new_node_type, 2, ext_name))

            self.assertEqual(
                (new_node_type, 1, ext_name),
                interface.find_forward(old_node_type, 1),
                "Moving version 1 of a node to another extension",
            )

            self.assertEqual(
                (new_node_type, 2, ext_name),
                interface.find_forward(old_node_type, 2),
                "Moving version 2 of a node to another extension",
            )

            self.assertEqual(
                (new_node_type, 3, ext_name),
                interface.find_forward(old_node_type, 3),
                "Moving version 3 of a node to another extension",
            )

            self.assertEqual(
                (new_node_type, 3, ext_name),
                interface.find_forward(old_node_type, 4),
                "Moving version 4 of a node to another extension",
            )
        finally:
            self.assertTrue(interface.remove_forward(old_node_type, 3))
            self.assertTrue(interface.remove_forward(old_node_type, 1))
            self.assertTrue(interface.remove_forward(old_node_type, 2))

    # --------------------------------------------------------------------------------------------------------------
    async def test_cycle_avoidance(self):
        """Tests that attempts to create a forwarding cycle are prevented"""
        get_interface = og.get_node_type_forwarding_interface2
        self.assertIsNotNone(get_interface)
        interface = get_interface()
        self.assertIsNotNone(interface)
        self.assertTrue(isinstance(interface, og.INodeTypeForwarding2))

        old_node_type = "omni.old.extension.MyTestingNode"
        new_node_type = "omni.new.extension.MyTestingNode"
        really_new_node_type = "omni.new.extension.MyNewTestingNode"
        ext_name = "omni.new.extension"
        # Special name that will be caught by the extension.toml test error filtering as the ExpectedError()
        # catch seems flaky in the cases where this is used.
        filtered_node_type = "omni.old.extension.__TEST__"

        # Node types are not allowed to forward directly to themselves
        with ogts.ExpectedError():
            self.assertFalse(interface.define_forward(filtered_node_type, 3, filtered_node_type, 3, ext_name))

        # Avoid the trivial A -> B then B -> A cycle
        try:
            self.assertTrue(interface.define_forward(old_node_type, 3, new_node_type, 3, ext_name))
            with ogts.ExpectedError():
                self.assertFalse(interface.define_forward(new_node_type, 3, old_node_type, 3, ext_name))
        finally:
            self.assertTrue(interface.remove_forward(old_node_type, 3))

        # Avoid the one-step A -> B -> C then C -> A cycle
        try:
            self.assertTrue(interface.define_forward(old_node_type, 3, new_node_type, 3, ext_name))
            self.assertTrue(interface.define_forward(new_node_type, 3, really_new_node_type, 3, ext_name))
            with ogts.ExpectedError():
                self.assertFalse(interface.define_forward(really_new_node_type, 3, old_node_type, 3, ext_name))
        finally:
            self.assertTrue(interface.remove_forward(old_node_type, 3))
            self.assertTrue(interface.remove_forward(new_node_type, 3))

        # Avoid the two-step A -> B -> C then C -> B cycle
        try:
            self.assertTrue(interface.define_forward(old_node_type, 3, new_node_type, 3, ext_name))
            self.assertTrue(interface.define_forward(new_node_type, 3, really_new_node_type, 3, ext_name))
            with ogts.ExpectedError():
                self.assertFalse(interface.define_forward(really_new_node_type, 3, new_node_type, 3, ext_name))
        finally:
            self.assertTrue(interface.remove_forward(old_node_type, 3))
            self.assertTrue(interface.remove_forward(new_node_type, 3))
