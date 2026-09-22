"""
Suite of tests to exercise small pieces of the OmniGraph utility scripts. These tests are like
unit tests in that they all only focus on one piece of functionality, not the integration of
many pieces, as these tests usually do.
"""

import json
from pathlib import Path

import carb
import carb.settings
import omni.graph.core as og
import omni.graph.core.tests as ogt


class TestOmniGraphUtilities(ogt.OmniGraphTestCase):
    """Wrapper for unit tests on basic OmniGraph support script functionality"""

    # ----------------------------------------------------------------------
    async def test_ogn_type_conversion(self):
        """Test operation of the AttributeType.type_from_ogn_type_name() function"""
        # Test data is tuples of string input and expected Type output
        simple_data_no_tuples = [
            ("any", og.Type(og.BaseDataType.TOKEN)),
            ("bool", og.Type(og.BaseDataType.BOOL)),
            ("int64", og.Type(og.BaseDataType.INT64)),
            ("token", og.Type(og.BaseDataType.TOKEN)),
            ("uchar", og.Type(og.BaseDataType.UCHAR)),
            ("uint", og.Type(og.BaseDataType.UINT)),
            ("uint64", og.Type(og.BaseDataType.UINT64)),
        ]
        simple_data = [
            ("double", og.Type(og.BaseDataType.DOUBLE)),
            ("float", og.Type(og.BaseDataType.FLOAT)),
            ("half", og.Type(og.BaseDataType.HALF)),
            ("int", og.Type(og.BaseDataType.INT)),
        ]
        tuple_data = [(f"{type_name}[2]", og.Type(og_type.base_type, 2, 0)) for (type_name, og_type) in simple_data]
        array_data = [
            (f"{type_name}[]", og.Type(og_type.base_type, 1, 1))
            for (type_name, og_type) in simple_data + simple_data_no_tuples
        ]
        array_tuple_data = [
            (f"{type_name}[3][]", og.Type(og_type.base_type, 3, 1)) for (type_name, og_type) in simple_data
        ]
        role_data = [
            ("bundle", og.Type(og.BaseDataType.RELATIONSHIP, 1, 0, og.AttributeRole.BUNDLE)),
            ("colord[3]", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.COLOR)),
            ("colorf[3]", og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.COLOR)),
            ("colorh[3]", og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.COLOR)),
            ("frame[4]", og.Type(og.BaseDataType.DOUBLE, 16, 0, og.AttributeRole.FRAME)),
            ("matrixd[2]", og.Type(og.BaseDataType.DOUBLE, 4, 0, og.AttributeRole.MATRIX)),
            ("matrixd[3]", og.Type(og.BaseDataType.DOUBLE, 9, 0, og.AttributeRole.MATRIX)),
            ("matrixd[4]", og.Type(og.BaseDataType.DOUBLE, 16, 0, og.AttributeRole.MATRIX)),
            ("normald[3]", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.NORMAL)),
            ("normalf[3]", og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.NORMAL)),
            ("normalh[3]", og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.NORMAL)),
            ("path", og.Type(og.BaseDataType.UCHAR, 1, 1, og.AttributeRole.PATH)),
            ("pointd[3]", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.POSITION)),
            ("pointf[3]", og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.POSITION)),
            ("pointh[3]", og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.POSITION)),
            ("quatd[3]", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.QUATERNION)),
            ("quatf[3]", og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.QUATERNION)),
            ("quath[3]", og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.QUATERNION)),
            ("target", og.Type(og.BaseDataType.RELATIONSHIP, 1, 0, og.AttributeRole.TARGET)),
            ("texcoordd[3]", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.TEXCOORD)),
            ("texcoordf[3]", og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.TEXCOORD)),
            ("texcoordh[3]", og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.TEXCOORD)),
            ("timecode[3]", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.TIMECODE)),
            ("transform[3]", og.Type(og.BaseDataType.DOUBLE, 9, 0, og.AttributeRole.TRANSFORM)),
            ("vectord[3]", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.VECTOR)),
            ("vectorf[3]", og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.VECTOR)),
            ("vectorh[3]", og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.VECTOR)),
        ]

        test_data = simple_data + simple_data_no_tuples + tuple_data + array_data + array_tuple_data + role_data
        for attribute_type_spec, attribute_type_expected in test_data:
            actual = og.AttributeType.type_from_ogn_type_name(attribute_type_spec)
            self.assertEqual(attribute_type_expected, actual, f"Failed to convert {attribute_type_spec}")

    # ----------------------------------------------------------------------
    async def test_sdf_type_conversion(self):
        """Test operation of the AttributeType.type_from_sdf_type_name() function"""
        # Test data is tuples of string input and expected Type output
        simple_data_no_tuples = [
            ("bool", og.Type(og.BaseDataType.BOOL)),
            ("int64", og.Type(og.BaseDataType.INT64)),
            ("token", og.Type(og.BaseDataType.TOKEN)),
            ("uchar", og.Type(og.BaseDataType.UCHAR)),
            ("uint", og.Type(og.BaseDataType.UINT)),
            ("uint64", og.Type(og.BaseDataType.UINT64)),
        ]
        simple_data = [
            ("double", og.Type(og.BaseDataType.DOUBLE)),
            ("float", og.Type(og.BaseDataType.FLOAT)),
            ("half", og.Type(og.BaseDataType.HALF)),
            ("int", og.Type(og.BaseDataType.INT)),
        ]
        tuple_data = [(f"{type_name}2", og.Type(og_type.base_type, 2, 0)) for (type_name, og_type) in simple_data]
        array_data = [
            (f"{type_name}[]", og.Type(og_type.base_type, 1, 1))
            for (type_name, og_type) in simple_data + simple_data_no_tuples
        ]
        array_tuple_data = [
            (f"{type_name}3[]", og.Type(og_type.base_type, 3, 1)) for (type_name, og_type) in simple_data
        ]
        role_data = [
            ("color3d", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.COLOR)),
            ("color3f", og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.COLOR)),
            ("color3h", og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.COLOR)),
            ("frame4d", og.Type(og.BaseDataType.DOUBLE, 16, 0, og.AttributeRole.FRAME)),
            ("matrix2d", og.Type(og.BaseDataType.DOUBLE, 4, 0, og.AttributeRole.MATRIX)),
            ("matrix3d", og.Type(og.BaseDataType.DOUBLE, 9, 0, og.AttributeRole.MATRIX)),
            ("matrix4d", og.Type(og.BaseDataType.DOUBLE, 16, 0, og.AttributeRole.MATRIX)),
            ("normal3d", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.NORMAL)),
            ("normal3f", og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.NORMAL)),
            ("normal3h", og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.NORMAL)),
            ("point3d", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.POSITION)),
            ("point3f", og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.POSITION)),
            ("point3h", og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.POSITION)),
            ("quatd", og.Type(og.BaseDataType.DOUBLE, 4, 0, og.AttributeRole.QUATERNION)),
            ("quatf", og.Type(og.BaseDataType.FLOAT, 4, 0, og.AttributeRole.QUATERNION)),
            ("quath", og.Type(og.BaseDataType.HALF, 4, 0, og.AttributeRole.QUATERNION)),
            ("texCoord3d", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.TEXCOORD)),
            ("texCoord3f", og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.TEXCOORD)),
            ("texCoord3h", og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.TEXCOORD)),
            ("timecode", og.Type(og.BaseDataType.DOUBLE, 1, 0, og.AttributeRole.TIMECODE)),
            ("vector3d", og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.VECTOR)),
            ("vector3f", og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.VECTOR)),
            ("vector3h", og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.VECTOR)),
        ]

        test_data = simple_data + simple_data_no_tuples + tuple_data + array_data + array_tuple_data + role_data
        for attribute_type_spec, attribute_type_expected in test_data:
            actual = og.AttributeType.type_from_sdf_type_name(attribute_type_spec)
            self.assertEqual(
                attribute_type_expected,
                actual,
                f"Failed to convert '{attribute_type_spec}' - '{attribute_type_expected.get_type_name()}'"
                f" != '{actual.get_type_name()}'",
            )

    # ----------------------------------------------------------------------
    async def test_typed_value(self):
        """Test operation of the TypedValue class"""
        # Test data consists of args + kwargs values to pass to the set() method, a boolean indicating whether setting
        # should succeed or not, and the expected value and type after setting. When there are two args or two kwargs
        # the __init__ method is used as well as those are the cases in which it is valid.
        unknown_t = og.Type(og.BaseDataType.UNKNOWN)
        float_t = og.Type(og.BaseDataType.FLOAT)
        test_data = [
            # Legal args configurations
            [[], {}, True, None, unknown_t],
            [[1.0], {}, True, 1.0, unknown_t],
            [[1.0, "float"], {}, True, 1.0, float_t],
            [[1.0, float_t], {}, True, 1.0, float_t],
            # Legal kwargs configurations
            [[], {"value": 1.0}, True, 1.0, unknown_t],
            [[], {"value": 1.0, "type": "float"}, True, 1.0, float_t],
            [[], {"value": 1.0, "type": float_t}, True, 1.0, float_t],
            [[], {"type": float_t, "value": 1.0}, True, 1.0, float_t],
            # Illegal args combinations
            [[1.0, "float", 2], {}, False, None, None],
            [[1.0, "sink"], {}, False, None, None],
            [["float", 1.0], {}, False, None, None],
            # Illegal kwargs combinations
            [[], {"valley": 1.0}, False, None, None],
            [[], {"type": "float"}, False, None, None],
            [[], {"value": 1.0, "type": "flat"}, False, None, None],
            [[], {"value": 1.0, "type": "float", "scissors": "run_with"}, False, None, None],
            # Illegal args+kwargs combinations
            [[1.0], {"type": "float"}, False, None, None],
            [[1.0, "float"], {"value": 1.0}, False, None, None],
        ]

        for args, kwargs, should_succeed, expected_value, expected_type in test_data:
            test_info = (
                f"args={args}, kwargs={kwargs}, success={should_succeed}, value={expected_value}, type={expected_type}"
            )
            if should_succeed:
                if len(args) == 2:
                    init_test = og.TypedValue(*args)
                    self.assertEqual(init_test.value, expected_value, test_info)
                    self.assertEqual(init_test.type, expected_type, test_info)
                elif len(kwargs) == 2:
                    init_test = og.TypedValue(**kwargs)
                    self.assertEqual(init_test.value, expected_value, test_info)
                    self.assertEqual(init_test.type, expected_type, test_info)
                set_test = og.TypedValue()
                set_test.set(*args, **kwargs)
                self.assertEqual(set_test.value, expected_value, test_info)
                self.assertEqual(set_test.type, expected_type, test_info)
            else:
                with self.assertRaises(og.OmniGraphError):
                    set_test = og.TypedValue()
                    set_test.set(*args, **kwargs)
                if len(args) == 2 and not kwargs:
                    with self.assertRaises(og.OmniGraphError):
                        init_test = og.TypedValue(*args)
                elif len(kwargs) == 2 and not args:
                    with self.assertRaises(og.OmniGraphError):
                        init_test = og.TypedValue(**kwargs)

    # ----------------------------------------------------------------------
    async def test_category_setup(self):
        """Test that the default category list is something sensible"""
        # Read the exact set of default categories, which should be the minimum available category list
        category_path = Path(carb.tokens.get_tokens_interface().resolve("${kit}")) / "dev" / "ogn" / "config"
        with open(category_path / "CategoryConfiguration.json", "r", encoding="utf-8") as cat_fd:
            default_categories = dict(json.load(cat_fd)["categoryDefinitions"].items())

        actual_categories = og.get_node_categories_interface().get_all_categories()

        # compounds is a special case that gets added at runtime, not in ogn, and is not intended
        # for use by .ogn compiled nodes.
        self.assertTrue("Compounds" in actual_categories)

        for category_name, category_description in actual_categories.items():
            if category_name == "Compounds":
                continue
            self.assertTrue(category_name in default_categories)
            self.assertEqual(category_description, default_categories[category_name])

    # ----------------------------------------------------------------------
    async def test_app_information(self):
        """Test the functions which return information about the running application."""
        # Make sure that we get back a tuple containing two non-negative ints.
        kit_version = og.get_kit_version()
        self.assertTrue(
            isinstance(kit_version, tuple), f"get_kit_version() returned type {type(kit_version)}, not tuple"
        )
        self.assertEqual(
            len(kit_version), 2, f"get_kit_version() returned tuple with {len(kit_version)} elements, expected 2"
        )
        self.assertTrue(
            isinstance(kit_version[0], int) and isinstance(kit_version[1], int),
            f"get_kit_version() returned types ({type(kit_version[0])}, {type(kit_version[1])}, expected (int, int)",
        )
        self.assertTrue(
            kit_version[0] >= 0 and kit_version[1] >= 0, f"get_kit_version() returned invalid value '{kit_version}'"
        )

    # ----------------------------------------------------------------------
    async def test_temp_settings(self):
        """Test the Settings.temporary context manager."""
        setting_names = ("/omnigraph/test/boolval", "/omnigraph/test/intval", "/omnigraph/test/sub/strval")

        # Initialize the settings.
        settings = carb.settings.get_settings()
        initial_values = (True, None, "first")
        initial_settings = list(zip(setting_names, initial_values))
        for name, value in initial_settings:
            settings.destroy_item(name)
            if value is not None:
                settings.set(name, value)

        # Test the single setting version of the context.
        with og.Settings.temporary(setting_names[2], "second"):
            self.assertEqual(settings.get(setting_names[2]), "second", "Single setting, in context.")
        self.assertEqual(settings.get(setting_names[2]), initial_values[2], "Single setting, after context.")

        # Test the list version.
        temp_settings = list(zip(setting_names, (False, 6, "third")))
        with og.Settings.temporary(temp_settings):
            for name, value in temp_settings:
                self.assertEqual(settings.get(name), value, f"Multiple settings, in context: '{name}'")
        for name, value in initial_settings:
            self.assertEqual(settings.get(name), value, f"Multiple settings, after context: '{name}'")

        # Clean up.
        for name in setting_names:
            settings.destroy_item(name)
