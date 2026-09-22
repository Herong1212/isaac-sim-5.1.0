"""Basic tests of the bundled attribute nodes"""

import numpy
import omni.graph.core as og
import omni.graph.core.tests as ogts


# ======================================================================
class TestBundleAttributeNodes(ogts.OmniGraphTestCase):
    """Run a simple unit test that exercises graph functionality"""

    # ----------------------------------------------------------------------
    def compare_values(self, expected_value, actual_value, decimal, error_message):
        """Generic assert comparison which uses introspection to choose the correct method to compare the data values"""
        # dbg(f"----Comparing {actual_value} with expected {expected_value}")
        if isinstance(expected_value, (list, tuple)):
            # If the numpy module is not available array values cannot be tested so silently succeed
            if numpy is None:
                return
            # Values are returned as numpy arrays so convert the expected value and use numpy to do the comparison
            numpy.testing.assert_almost_equal(
                actual_value, numpy.array(expected_value), decimal=decimal, err_msg=error_message
            )
        elif isinstance(expected_value, float):
            self.assertAlmostEqual(actual_value, expected_value, decimal, error_message)
        else:
            self.assertEqual(actual_value, expected_value, error_message)

    # ----------------------------------------------------------------------
    async def test_bundle_functions(self):
        """Test bundle functions"""
        await ogts.load_test_file("TestBundleAttributeNodes.usda", use_caller_subdirectory=True)

        # These prims are known to be in the file
        bundle_prim = "/defaultPrim/inputData"
        # However since we no longer spawn OgnPrim for bundle-connected prims, we don't expect it to be
        # in OG. (Verified in a different test)
        # self.assertEqual([], ogts.verify_node_existence([bundle_prim]))

        contexts = og.get_compute_graph_contexts()
        self.assertIsNotNone(contexts)

        expected_values = {
            "boolAttr": (1, ("bool", og.BaseDataType.BOOL, 1, 0, og.AttributeRole.NONE)),
            "intAttr": (1, ("int", og.BaseDataType.INT, 1, 0, og.AttributeRole.NONE)),
            "int64Attr": (1, ("int64", og.BaseDataType.INT64, 1, 0, og.AttributeRole.NONE)),
            "uint64Attr": (1, ("uint64", og.BaseDataType.UINT64, 1, 0, og.AttributeRole.NONE)),
            "halfAttr": (1, ("half", og.BaseDataType.HALF, 1, 0, og.AttributeRole.NONE)),
            "floatAttr": (1, ("float", og.BaseDataType.FLOAT, 1, 0, og.AttributeRole.NONE)),
            "doubleAttr": (1, ("double", og.BaseDataType.DOUBLE, 1, 0, og.AttributeRole.NONE)),
            "tokenAttr": (1, ("token", og.BaseDataType.TOKEN, 1, 0, og.AttributeRole.NONE)),
            "stringAttr": (10, ("string", og.BaseDataType.UCHAR, 1, 1, og.AttributeRole.TEXT)),
            # We don't read relationship attributes in OgnReadPrimBundle
            # "relSingleAttr": (1, ("rel", og.BaseDataType.RELATIONSHIP, 1, 0, og.AttributeRole.NONE)),
            "int2Attr": (1, ("int[2]", og.BaseDataType.INT, 2, 0, og.AttributeRole.NONE)),
            "half2Attr": (1, ("half[2]", og.BaseDataType.HALF, 2, 0, og.AttributeRole.NONE)),
            "float2Attr": (1, ("float[2]", og.BaseDataType.FLOAT, 2, 0, og.AttributeRole.NONE)),
            "double2Attr": (1, ("double[2]", og.BaseDataType.DOUBLE, 2, 0, og.AttributeRole.NONE)),
            "int3Attr": (1, ("int[3]", og.BaseDataType.INT, 3, 0, og.AttributeRole.NONE)),
            "half3Attr": (1, ("half[3]", og.BaseDataType.HALF, 3, 0, og.AttributeRole.NONE)),
            "float3Attr": (1, ("float[3]", og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.NONE)),
            "double3Attr": (1, ("double[3]", og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.NONE)),
            "int4Attr": (1, ("int[4]", og.BaseDataType.INT, 4, 0, og.AttributeRole.NONE)),
            "half4Attr": (1, ("half[4]", og.BaseDataType.HALF, 4, 0, og.AttributeRole.NONE)),
            "float4Attr": (1, ("float[4]", og.BaseDataType.FLOAT, 4, 0, og.AttributeRole.NONE)),
            "double4Attr": (1, ("double[4]", og.BaseDataType.DOUBLE, 4, 0, og.AttributeRole.NONE)),
            "boolArrayAttr": (65, ("bool[]", og.BaseDataType.BOOL, 1, 1, og.AttributeRole.NONE)),
            "intArrayAttr": (5, ("int[]", og.BaseDataType.INT, 1, 1, og.AttributeRole.NONE)),
            "floatArrayAttr": (5, ("float[]", og.BaseDataType.FLOAT, 1, 1, og.AttributeRole.NONE)),
            "doubleArrayAttr": (5, ("double[]", og.BaseDataType.DOUBLE, 1, 1, og.AttributeRole.NONE)),
            "tokenArrayAttr": (3, ("token[]", og.BaseDataType.TOKEN, 1, 1, og.AttributeRole.NONE)),
            "int2ArrayAttr": (5, ("int[2][]", og.BaseDataType.INT, 2, 1, og.AttributeRole.NONE)),
            "float2ArrayAttr": (5, ("float[2][]", og.BaseDataType.FLOAT, 2, 1, og.AttributeRole.NONE)),
            "double2ArrayAttr": (5, ("double[2][]", og.BaseDataType.DOUBLE, 2, 1, og.AttributeRole.NONE)),
            "point3fArrayAttr": (3, ("pointf[3][]", og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.POSITION)),
            "qhAttr": (1, ("quath[4]", og.BaseDataType.HALF, 4, 0, og.AttributeRole.QUATERNION)),
            "qfAttr": (1, ("quatf[4]", og.BaseDataType.FLOAT, 4, 0, og.AttributeRole.QUATERNION)),
            "qdAttr": (1, ("quatd[4]", og.BaseDataType.DOUBLE, 4, 0, og.AttributeRole.QUATERNION)),
            "m2dAttr": (1, ("matrixd[2]", og.BaseDataType.DOUBLE, 4, 0, og.AttributeRole.MATRIX)),
            "m3dAttr": (1, ("matrixd[3]", og.BaseDataType.DOUBLE, 9, 0, og.AttributeRole.MATRIX)),
            "m4dAttr": (1, ("matrixd[4]", og.BaseDataType.DOUBLE, 16, 0, og.AttributeRole.MATRIX)),
        }

        for context in contexts:

            bundle = context.get_bundle(bundle_prim)
            attr_names, attr_types = bundle.get_attribute_names_and_types()
            attr_count = bundle.get_attribute_data_count()
            self.assertEqual(attr_count, len(expected_values))

            attr_names, attr_types = bundle.get_attribute_names_and_types()
            self.assertCountEqual(attr_names, list(expected_values.keys()))

            # The name map has to be created because the output bundle contents are not in a defined order but the
            # different array elements do correspond to each other. By creating a mapping from the name to the index
            # at which it was found the other elements can be mapped exactly.
            expected_types = [expected_values[name][1] for name in attr_names]
            expected_counts = [expected_values[name][0] for name in attr_names]

            type_name_and_properties = []
            new_constructed_types = []
            for attr_type in attr_types:
                base_type = attr_type.base_type
                tuple_count = attr_type.tuple_count
                array_depth = attr_type.array_depth
                role = attr_type.role
                type_name_and_properties.append(
                    (attr_type.get_ogn_type_name(), base_type, tuple_count, array_depth, role)
                )
                new_constructed_types.append(og.Type(base_type, tuple_count, array_depth, role))
            self.assertCountEqual(type_name_and_properties, expected_types)
            self.assertEqual(new_constructed_types, attr_types)

            attrs = bundle.get_attribute_data()
            attr_elem_counts = []
            for attr in attrs:
                try:
                    elem_count = og.Controller.get_array_size(attr)
                except AttributeError:
                    elem_count = 1
                attr_elem_counts.append(elem_count)
            self.assertEqual(attr_elem_counts, expected_counts)
