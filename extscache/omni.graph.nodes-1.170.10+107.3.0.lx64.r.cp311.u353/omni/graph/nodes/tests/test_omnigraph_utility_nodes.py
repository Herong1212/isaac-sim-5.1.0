"""Test the node that inspects attribute bundles"""

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.graph.nodes.tests as ognts

ROLES = [
    "none",
    "vector",
    "normal",
    "point",
    "color",
    "texcoord",
    "quat",
    "transform",
    "frame",
    "timecode",
    "text",
    "appliedSchema",
    "prim",
    "execution",
    "matrix",
    "objectId",
]
"""Mapping of OGN role name to the AttributeRole index used in Type.h"""

MATRIX_ROLES = ["frame", "transform", "matrix"]
"""Special roles that indicate a matrix type"""

BASE_TYPES = [
    "none",
    "bool",
    "uchar",
    "int",
    "uint",
    "int64",
    "uint64",
    "half",
    "float",
    "double",
    "token",
]
"""Mapping of raw OGN base type name to the BaseDataType index in Type.h"""


# ======================================================================
class TestOmniGraphUtilityNodes(ogts.OmniGraphTestCase):
    """Run a simple unit test that exercises graph functionality"""

    # ----------------------------------------------------------------------
    async def test_attr_type(self):
        """Test the AttrType node with some pre-made input bundle contents"""
        keys = og.Controller.Keys
        (_, [attr_type_node, _], [prim], _) = og.Controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: ("AttrTypeNode", "omni.graph.nodes.AttributeType"),
                keys.CREATE_PRIMS: ("TestPrim", ognts.prim_with_everything_definition()),
                keys.EXPOSE_PRIMS: (og.Controller.PrimExposureType.AS_BUNDLE, "/TestPrim", "TestPrimExtract"),
                keys.CONNECT: [
                    ("TestPrimExtract.outputs_primBundle", "AttrTypeNode.inputs:data"),
                ],
            },
        )
        await og.Controller.evaluate()
        (_, bundle_values) = ognts.get_bundle_with_all_results(str(prim.GetPrimPath()))
        name_attr = og.Controller.attribute("inputs:attrName", attr_type_node)
        type_attr = og.Controller.attribute("outputs:baseType", attr_type_node)
        tuple_count_attr = og.Controller.attribute("outputs:componentCount", attr_type_node)
        array_depth_attr = og.Controller.attribute("outputs:arrayDepth", attr_type_node)
        role_attr = og.Controller.attribute("outputs:role", attr_type_node)
        full_type_attr = og.Controller.attribute("outputs:fullType", attr_type_node)

        # Test data consisting of the input attrName followed by the expected output values
        test_data = [["notExisting", -1, -1, -1, -1]]
        for attribute_name, (type_name, tuple_count, array_depth, role, _) in bundle_values.items():
            base_index = BASE_TYPES.index(type_name)
            role_index = ROLES.index(role)
            # Matrix types have 2d tuple counts
            if role_index in MATRIX_ROLES:
                tuple_count *= tuple_count
            test_data.append([attribute_name, base_index, tuple_count, array_depth, role_index])

        for name, base_type, tuple_count, array_depth, role in test_data:
            og.Controller.set(name_attr, name)
            await og.Controller.evaluate()
            full_type = -1
            if base_type >= 0:
                # This is the bitfield computation used in Type.h
                full_type = base_type + (tuple_count << 8) + (array_depth << 16) + (role << 24)
            self.assertEqual(base_type, og.Controller.get(type_attr), f"Type of {name}")
            self.assertEqual(tuple_count, og.Controller.get(tuple_count_attr), f"Tuple Count of {name}")
            self.assertEqual(array_depth, og.Controller.get(array_depth_attr), f"Array Depth of {name}")
            self.assertEqual(role, og.Controller.get(role_attr), f"Role of {name}")
            self.assertEqual(full_type, og.Controller.get(full_type_attr), f"Full type of {name}")

    # ----------------------------------------------------------------------
    async def test_has_attr(self):
        """Test the HasAttr node with some pre-made input bundle contents"""
        keys = og.Controller.Keys
        (_, [has_attr_node, _], [prim], _) = og.Controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: [
                    ("HasAttrNode", "omni.graph.nodes.HasAttribute"),
                ],
                keys.CREATE_PRIMS: ("TestPrim", ognts.prim_with_everything_definition()),
                keys.EXPOSE_PRIMS: (og.Controller.PrimExposureType.AS_BUNDLE, "/TestPrim", "TestPrimExtract"),
                keys.CONNECT: [("TestPrimExtract.outputs_primBundle", "HasAttrNode.inputs:data")],
            },
        )
        await og.Controller.evaluate()
        expected_results = ognts.get_bundle_with_all_results(str(prim.GetPrimPath()))

        # Test data consisting of the input attrName followed by the expected output values
        test_data = [("notExisting", 0)]
        for name in expected_results[1].keys():
            test_data.append((name, True))

        name_attribute = og.Controller.attribute("inputs:attrName", has_attr_node)
        output_attribute = og.Controller.attribute("outputs:output", has_attr_node)
        for attribute_name, existence in test_data:
            og.Controller.set(name_attribute, attribute_name)
            await og.Controller.evaluate()
            self.assertEqual(existence, og.Controller.get(output_attribute), f"Has {attribute_name}")

    # ----------------------------------------------------------------------
    async def test_get_attr_names(self):
        """Test the GetAttrNames node with some pre-made input bundle contents"""
        keys = og.Controller.Keys
        (_, [get_names_node, _], [prim], _) = og.Controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: ("GetAttrNamesNode", "omni.graph.nodes.GetAttributeNames"),
                keys.CREATE_PRIMS: ("TestPrim", ognts.prim_with_everything_definition()),
                keys.EXPOSE_PRIMS: (og.Controller.PrimExposureType.AS_BUNDLE, "/TestPrim", "TestPrimExtract"),
                keys.CONNECT: [
                    ("TestPrimExtract.outputs_primBundle", "GetAttrNamesNode.inputs:data"),
                ],
            },
        )
        await og.Controller.evaluate()
        (_, all_bundle_values) = ognts.get_bundle_with_all_results(
            str(prim.GetPrimPath()), prim_source_type=str(prim.GetTypeName())
        )
        attr_names = list(all_bundle_values.keys())

        for is_sorted in [False, True]:
            og.Controller.set(("inputs:sort", get_names_node), is_sorted)
            await og.Controller.evaluate()
            actual_results = og.Controller.get(("outputs:output", get_names_node))
            if is_sorted:
                self.assertEqual(sorted(attr_names), actual_results, "Comparing sorted lists")
            else:
                self.assertCountEqual(attr_names, actual_results, "Comparing unsorted lists")

    # ----------------------------------------------------------------------
    async def test_array_length(self):
        """Test the ArrayLength node with some pre-made input bundle contents"""
        keys = og.Controller.Keys
        (_, [length_node, _], [prim], _) = og.Controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: ("ArrayLengthNode", "omni.graph.nodes.ArrayLength"),
                keys.CREATE_PRIMS: ("TestPrim", ognts.prim_with_everything_definition()),
                keys.EXPOSE_PRIMS: (og.Controller.PrimExposureType.AS_BUNDLE, "TestPrim", "TestPrimExtract"),
                keys.CONNECT: [
                    ("TestPrimExtract.outputs_primBundle", "ArrayLengthNode.inputs:data"),
                ],
            },
        )
        await og.Controller.evaluate()
        expected_results = ognts.get_bundle_with_all_results(str(prim.GetPrimPath()))

        # Test data consisting of the input attrName followed by the expected output values
        test_data = [("notExisting", 0)]
        for name, (_, _, array_length, _, value) in expected_results[1].items():
            test_data.append((name, len(value) if array_length > 0 else 1))

        name_attribute = og.Controller.attribute("inputs:attrName", length_node)
        output_attribute = og.Controller.attribute("outputs:length", length_node)
        for attribute_name, expected_length in test_data:
            og.Controller.set(name_attribute, attribute_name)
            await og.Controller.evaluate()
            self.assertEqual(expected_length, og.Controller.get(output_attribute), f"{attribute_name} array length")

    # ----------------------------------------------------------------------
    async def test_copy_attr(self):
        """Test the CopyAttr node with some pre-made input bundle contents on the partialData input"""
        keys = og.Controller.Keys
        (_, [copy_node, inspector_node, _], [prim], _) = og.Controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: [
                    ("CopyAttrNode", "omni.graph.nodes.CopyAttribute"),
                    ("Inspector", "omni.graph.nodes.BundleInspector"),
                ],
                keys.CREATE_PRIMS: ("TestPrim", ognts.prim_with_everything_definition()),
                keys.EXPOSE_PRIMS: (og.Controller.PrimExposureType.AS_BUNDLE, "/TestPrim", "TestPrimExtract"),
                keys.CONNECT: [
                    # Connect the same prim to both inputs to avoid the overhead of creating two prims
                    ("TestPrimExtract.outputs_primBundle", "CopyAttrNode.inputs:fullData"),
                    ("TestPrimExtract.outputs_primBundle", "CopyAttrNode.inputs:partialData"),
                    ("CopyAttrNode.outputs_data", "Inspector.inputs:bundle"),
                ],
            },
        )
        await og.Controller.evaluate()

        input_names_attr = og.Controller.attribute("inputs:inputAttrNames", copy_node)
        output_names_attr = og.Controller.attribute("inputs:outputAttrNames", copy_node)

        expected_results = ognts.get_bundle_with_all_results(
            str(prim.GetPrimPath()), prim_source_type=str(prim.GetTypeName())
        )
        # Use sorted names so that the test is predictable
        sorted_names = sorted(expected_results[1].keys())
        # Restrict to a small subset as a representative test
        old_names = sorted_names[0:3]
        new_names = [f"COPIED_{name}" for name in sorted_names[0:3]]

        copied_results = dict(expected_results[1].items())
        copied_results.update(
            {f"COPIED_{key}": value for key, value in expected_results[1].items() if key in old_names}
        )
        expected_copied_results = (expected_results[0] + len(old_names), copied_results)

        test_data = [
            ("", "", expected_results),
            (old_names, new_names, expected_copied_results),
        ]
        for to_copy, copied_to, expected_output in test_data:
            og.Controller.set(input_names_attr, ",".join(to_copy))
            og.Controller.set(output_names_attr, ",".join(copied_to))
            await og.Controller.evaluate()
            results = ognts.bundle_inspector_results(inspector_node)
            try:
                # FIXME: OM-44667: Values do not get copied correctly. When they do, check_values=False can be removed
                ognts.verify_bundles_are_equal(results, expected_output, check_values=False)
            except ValueError as error:
                self.assertTrue(False, error)

        # check invalid inputs

        # mismatch attribute names cause warnings
        og.Controller.set(input_names_attr, old_names[0])
        copy_node.clear_old_compute_messages()
        await og.Controller.evaluate()
        self.assertNotEquals(copy_node.get_compute_messages(og.Severity.WARNING), [])
        og.Controller.set(input_names_attr, ",".join(to_copy))
        copy_node.clear_old_compute_messages()

        # missing attribute names cause warnings
        og.Controller.set(input_names_attr, ",_i_".join(to_copy))
        await og.Controller.evaluate()
        self.assertNotEquals(copy_node.get_compute_messages(og.Severity.WARNING), [])

    # ----------------------------------------------------------------------
    async def test_rename_attr(self):
        """Test the RenameAttr node with some pre-made input bundle contents"""
        keys = og.Controller.Keys
        (_, [rename_node, inspector_node, _], [prim], _) = og.Controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: [
                    ("RenameAttrNode", "omni.graph.nodes.RenameAttribute"),
                    ("Inspector", "omni.graph.nodes.BundleInspector"),
                ],
                keys.CREATE_PRIMS: ("TestPrim", ognts.prim_with_everything_definition()),
                keys.EXPOSE_PRIMS: (og.Controller.PrimExposureType.AS_BUNDLE, "/TestPrim", "TestPrimExtract"),
                keys.CONNECT: [
                    ("TestPrimExtract.outputs_primBundle", "RenameAttrNode.inputs:data"),
                    ("RenameAttrNode.outputs_data", "Inspector.inputs:bundle"),
                ],
                keys.SET_VALUES: [
                    ("RenameAttrNode.inputs:inputAttrNames", ""),
                    ("RenameAttrNode.inputs:outputAttrNames", ""),
                ],
            },
        )
        await og.Controller.evaluate()
        input_names_attr = og.Controller.attribute("inputs:inputAttrNames", rename_node)
        output_names_attr = og.Controller.attribute("inputs:outputAttrNames", rename_node)

        expected_results = ognts.get_bundle_with_all_results(
            str(prim.GetPrimPath()), prim_source_type=str(prim.GetTypeName())
        )
        # Use sorted names so that the test is predictable
        sorted_names = sorted(expected_results[1].keys())
        # Restrict to a small subset as a representative test
        old_names = sorted_names[0:3]
        new_names = [f"RENAMED_{name}" for name in sorted_names[0:3]]

        renamed_results = {key: value for key, value in expected_results[1].items() if key not in old_names}
        renamed_results.update(
            {f"RENAMED_{key}": value for key, value in expected_results[1].items() if key in old_names}
        )
        expected_renamed_results = (expected_results[0], renamed_results)

        test_data = [
            ("", "", expected_results),
            (old_names, new_names, expected_renamed_results),
        ]

        for to_rename, renamed_to, expected_output in test_data:
            og.Controller.set(input_names_attr, ",".join(to_rename))
            og.Controller.set(output_names_attr, ",".join(renamed_to))
            await og.Controller.evaluate()
            results = ognts.bundle_inspector_results(inspector_node)
            try:
                # FIXME: OM-44667: Values do not get copied correctly. When they do, check_values=False can be removed
                ognts.verify_bundles_are_equal(results, expected_output, check_values=False)
            except ValueError as error:
                self.assertTrue(False, error)

    # ----------------------------------------------------------------------
    async def test_remove_attr(self):
        """Test the RemoveAttr node with some pre-made input bundle contents"""
        keys = og.Controller.Keys
        (_, [remove_node, inspector_node, _], [prim], _) = og.Controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: [
                    ("RemoveAttrNode", "omni.graph.nodes.RemoveAttribute"),
                    ("Inspector", "omni.graph.nodes.BundleInspector"),
                ],
                keys.CREATE_PRIMS: ("TestPrim", ognts.prim_with_everything_definition()),
                keys.EXPOSE_PRIMS: (og.Controller.PrimExposureType.AS_BUNDLE, "/TestPrim", "TestPrimExtract"),
                keys.CONNECT: [
                    ("TestPrimExtract.outputs_primBundle", "RemoveAttrNode.inputs:data"),
                    ("RemoveAttrNode.outputs_data", "Inspector.inputs:bundle"),
                ],
                keys.SET_VALUES: [
                    ("RemoveAttrNode.inputs:attrNamesToRemove", ""),
                ],
            },
        )
        await og.Controller.evaluate()

        (expected_count, expected_results) = ognts.get_bundle_with_all_results(
            str(prim.GetPrimPath()), prim_source_type=str(prim.GetTypeName())
        )
        # Use sorted names so that the test is predictable
        sorted_names = sorted(expected_results.keys())
        removal = [
            sorted_names[0:2],
            sorted_names[3:6],
        ]
        test_data = [
            ("", (expected_count, expected_results)),
            (
                ",".join(removal[0]),
                (
                    expected_count - len(removal[0]),
                    {key: value for key, value in expected_results.items() if key not in removal[0]},
                ),
            ),
            (
                ",".join(removal[1]),
                (
                    expected_count - len(removal[1]),
                    {key: value for key, value in expected_results.items() if key not in removal[1]},
                ),
            ),
        ]
        removal_attribute = og.Controller.attribute("inputs:attrNamesToRemove", remove_node)
        for names, expected_output in test_data:
            og.Controller.set(removal_attribute, names)
            await og.Controller.evaluate()
            results = ognts.bundle_inspector_results(inspector_node)
            try:
                # FIXME: OM-44667: Values do not get copied correctly. When they do, check_values=False can be removed
                ognts.verify_bundles_are_equal(results, expected_output, check_values=False)
            except ValueError as error:
                self.assertTrue(False, error)

    # ----------------------------------------------------------------------
    async def test_insert_attr(self):
        """Test the InsertAttr node with some pre-made input bundle contents"""
        double_array = [(1.2, -1.2), (3.4, -5.6)]
        new_name = "newInsertedAttributeName"

        keys = og.Controller.Keys
        (_, [_, inspector_node, _], [prim], _) = og.Controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: [
                    ("InsertAttrNode", "omni.graph.nodes.InsertAttribute"),
                    ("Inspector", "omni.graph.nodes.BundleInspector"),
                ],
                keys.CREATE_PRIMS: ("TestPrim", ognts.prim_with_everything_definition()),
                keys.EXPOSE_PRIMS: (og.Controller.PrimExposureType.AS_BUNDLE, "/TestPrim", "TestPrimExtract"),
                keys.CONNECT: [
                    ("TestPrimExtract.outputs_primBundle", "InsertAttrNode.inputs:data"),
                    ("InsertAttrNode.outputs_data", "Inspector.inputs:bundle"),
                ],
                keys.SET_VALUES: [
                    ("InsertAttrNode.inputs:outputAttrName", new_name),
                    ("InsertAttrNode.inputs:attrToInsert", double_array, "double[2][]"),
                ],
            },
        )
        await og.Controller.evaluate()
        results = ognts.bundle_inspector_results(inspector_node)
        (expected_count, expected_results) = ognts.get_bundle_with_all_results(
            str(prim.GetPrimPath()), prim_source_type=str(prim.GetTypeName())
        )
        expected_results[new_name] = ("double", 2, 1, "none", double_array)
        expected_values = (expected_count + 1, expected_results)
        try:
            # FIXME: OM-44667: The values do not get copied correctly. When they do, check_values=False can be removed
            ognts.verify_bundles_are_equal(results, expected_values, check_values=False)
        except ValueError as error:
            self.assertTrue(False, error)

    # ----------------------------------------------------------------------
    async def test_extract_attr(self):
        """Test the ExtractAttr node with some pre-made input bundle contents"""
        keys = og.Controller.Keys
        controller = og.Controller()
        (_, [extract_node, _, _], [prim], _) = controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: [
                    ("ExtractAttrNode", "omni.graph.nodes.ExtractAttribute"),
                    ("AddArray", "omni.graph.nodes.Add"),
                ],
                keys.CREATE_PRIMS: ("TestPrim", ognts.prim_with_everything_definition()),
                keys.EXPOSE_PRIMS: (og.Controller.PrimExposureType.AS_BUNDLE, "/TestPrim", "TestPrimExtract"),
                keys.CONNECT: [
                    ("TestPrimExtract.outputs_primBundle", "ExtractAttrNode.inputs:data"),
                    ("ExtractAttrNode.outputs:output", "AddArray.inputs:a"),
                ],
                keys.SET_VALUES: [
                    ("ExtractAttrNode.inputs:attrName", "IntArrayAttr"),
                ],
            },
        )
        await og.Controller.evaluate()

        (_, expected_values) = ognts.get_bundle_with_all_results(str(prim.GetPrimPath()))
        self.assertCountEqual(
            expected_values["IntArrayAttr"][ognts.BundleResultKeys.VALUE_IDX],
            og.Controller.get(("outputs:output", extract_node)),
        )

        # test setting an invalid error produces a warning
        og.Controller.set(extract_node.get_attribute("inputs:attrName"), "InvalidAttr")
        await og.Controller.evaluate()
        self.assertNotEqual(extract_node.get_compute_messages(og.Severity.WARNING), [])
        extract_node.clear_old_compute_messages()

        # Test that a type mismatch causes a warning as well
        og.Controller.set(extract_node.get_attribute("inputs:attrName"), "IntArrayAttr")
        controller.edit(
            "/TestGraph",
            {
                keys.CREATE_PRIMS: ("TestBadPrim", {"IntArrayAttr": ("string", "A string on an int")}),
                keys.EXPOSE_PRIMS: (og.Controller.PrimExposureType.AS_BUNDLE, "/TestBadPrim", "TestBadPrimExtract"),
                keys.CONNECT: [("TestBadPrimExtract.outputs_primBundle", "ExtractAttrNode.inputs:data")],
            },
        )
        await og.Controller.evaluate()
        self.assertNotEqual(extract_node.get_compute_messages(og.Severity.WARNING), [])
