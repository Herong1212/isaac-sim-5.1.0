# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.usd
from omni.kit.test.async_unittest import AsyncTestCase

from pxr import Sdf, Usd
from pathlib import Path


_valid_first_char_categories = ('Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl')
_valid_cont_char_categories = ('Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl', 'Nd', 'Mn', 'Mc', 'Pc')

_example_valid_string_parts = [
    # Unicode category Lo
    "测试名称",  # Chinese characters
    "データ",  # Japanese characters
    "이름",  # Korean characters
    "имя",  # Cyrillic characters
    "नाम",  # Devanagari characters
    "اسم",  # Arabic characters
    "ชื่อ",  # Thai characters
    "Tên",  # Vietnamese characters
    # Unicode category Nl
    "Ⅸ",  # Roman numeral 9
    # Unicode category Lu, Ll
    "ÄßÖÜäöü",  # German umlauts
    # Unicode category Lt
    "ǅǈ",  # Latin capital ligature
    # Unicode category Lm
    "ᴭʰʲʷ",  # Modifier letters
]

_example_invalid_start_string_parts = [
    "1",  # Unicode category Nd
    "͍", # Unicode category Mn
    "ꣀ",  # Unicode category Mc
    "‿",  # Unicode category Pc
]

_example_invalid_string_parts = [
    # Unicode category So
    "🌍",  # Emoji
    "<",
    "★", # Symbols
    # Unicode category Zs
    " ",  # Space
    # Unicode category Cc
    "\n",  # Newline
    # Unicode category Sm
    "∭",  # Operators
]


class TestUnicodeUtils(AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_make_valid_identifier(self):
        """
        Test make_valid_identifier function.

        Valid starting characters include codepoints in the following Unicode categories:
        Lu | Ll | Lt | Lm | Lo | Nl  and `_`;
        Valid continueing charaters include codepoints all of the above, plus codepoints in the following Unicode categories:
        Nd | Mn | Mc | Pc;

        Invalid characters should be replaced with `_`.
        """
        # Test empty string.
        self.assertFalse(Sdf.Path.IsValidIdentifier(""))
        self.assertEqual(omni.usd.make_valid_identifier(""), "_")

        # Test invalid starting characters.
        for invalid_start in _example_invalid_start_string_parts:
            name = invalid_start + "test"
            self.assertFalse(Sdf.Path.IsValidIdentifier(name))
            self.assertEqual(omni.usd.make_valid_identifier(name), "_test")

        # Test invalid characters.
        for invalid in _example_invalid_string_parts:
            name = "_" + invalid
            self.assertFalse(Sdf.Path.IsValidIdentifier(name))
            self.assertEqual(omni.usd.make_valid_identifier(name), "__")

        # Test valid characters.
        valid = ''.join(_example_valid_string_parts)
        valid += ''.join(_example_invalid_start_string_parts)
        self.assertTrue(Sdf.Path.IsValidIdentifier(valid))
        self.assertEqual(omni.usd.make_valid_identifier(valid), valid)

        # Test valid characters with invalid characters.
        mixed = '123' + _example_invalid_string_parts[0] + _example_valid_string_parts[0]
        self.assertFalse(Sdf.Path.IsValidIdentifier(mixed))
        self.assertEqual(omni.usd.make_valid_identifier(mixed), '_23_' + _example_valid_string_parts[0])

    async def test_unicode_in_prim_path(self):
        """
        Test creating/loading/renaming with unicode in prim path and names.
        """
        # Test creating prim with unicode in prim path and name.
        unicode_name = ''.join(_example_valid_string_parts)
        unicode_path = "/中文测试路径/" + unicode_name

        layer = Sdf.Layer.CreateAnonymous()
        prim_spec = Sdf.CreatePrimInLayer(layer, unicode_path)
        self.assertIsNotNone(prim_spec)
        self.assertEqual(prim_spec.name, unicode_name)
        self.assertEqual(prim_spec.path, unicode_path)

        layer_data = layer.ExportToString()

        new_layer = Sdf.Layer.CreateAnonymous()
        new_layer.ImportFromString(layer_data)

        # Test loading prim with unicode in prim path and name.
        prim_spec = layer.GetPrimAtPath(unicode_path)
        self.assertIsNotNone(prim_spec)
        self.assertEqual(prim_spec.name, unicode_name)
        self.assertEqual(prim_spec.path, unicode_path)

        # Test renaming prim with unicode name.
        new_unicode_name = "新_" + unicode_name
        new_unicode_path = "/中文测试路径/" + new_unicode_name
        prim_spec.name = new_unicode_name
        self.assertEqual(prim_spec.name, new_unicode_name)
        self.assertEqual(prim_spec.path, new_unicode_path)

    async def test_unicode_in_attributes(self):
        """
        Test creating/loading/renaming with unicode in attribute name and value.
        """
        # Test creating attribute with unicode in name and value.
        unicode_name = ''.join(_example_valid_string_parts)
        unicode_value = ''.join(reversed(_example_valid_string_parts))
        layer = Sdf.Layer.CreateAnonymous()
        prim_spec = Sdf.CreatePrimInLayer(layer, '/Test')
        attr_spec = Sdf.AttributeSpec(prim_spec, unicode_name, Sdf.ValueTypeNames.String)
        self.assertIsNotNone(attr_spec)
        attr_spec.default = unicode_value

        layer_data = layer.ExportToString()

        new_layer = Sdf.Layer.CreateAnonymous()
        new_layer.ImportFromString(layer_data)

        # Test loading attribute with unicode in name and value.
        prim_spec = new_layer.GetPrimAtPath('/Test')
        self.assertIsNotNone(prim_spec)
        attr_spec = prim_spec.attributes[unicode_name]
        self.assertIsNotNone(attr_spec)
        self.assertEqual(attr_spec.default, unicode_value)

        # Test renaming attribute with unicode name.
        new_unicode_name = "new_" + unicode_name
        attr_spec.name = new_unicode_name
        self.assertEqual(attr_spec.name, new_unicode_name)

    async def test_unicode_in_metadata(self):
        """
        Test creating/loading/renaming with unicode in metadata.
        """
        # Test creating metadata with unicode in key and value.
        unicode_key = ''.join(_example_valid_string_parts)
        unicode_value = ''.join(reversed(_example_valid_string_parts))
        layer = Sdf.Layer.CreateAnonymous()
        prim_spec = Sdf.CreatePrimInLayer(layer, '/Test')
        self.assertIsNotNone(prim_spec)
        prim_spec.customData[unicode_key] = unicode_value

        layer_data = layer.ExportToString()

        new_layer = Sdf.Layer.CreateAnonymous()
        new_layer.ImportFromString(layer_data)

        # Test loading metadata with unicode in key and value.
        prim_spec = new_layer.GetPrimAtPath('/Test')
        self.assertIsNotNone(prim_spec)
        self.assertEqual(prim_spec.customData[unicode_key], unicode_value)

        # Test renaming metadata with unicode key.
        new_unicode_key = "new_" + unicode_key
        prim_spec.customData[new_unicode_key] = unicode_value
        self.assertEqual(prim_spec.customData[new_unicode_key], unicode_value)

    async def test_unicode_in_referenced_asset(self):
        """
        Test adding reference with unicode in path and contains unicode data.
        """
        asset_path = str(Path(__file__).parent.joinpath("data").joinpath("test_unicode_reference_ǅǈ.usda"))

        stage = Usd.Stage.CreateInMemory()
        ref_prim = stage.DefinePrim("/Ref").GetPrim()
        ref_prim.GetReferences().AddReference(assetPath=asset_path)

        child_paths = [child.GetPath() for child in ref_prim.GetChildren()]
        self.assertEqual(child_paths, ['/Ref/データ', '/Ref/test‿'])

        child_prim = stage.GetPrimAtPath('/Ref/データ')
        self.assertIsNotNone(child_prim)
        self.assertEqual(child_prim.GetAttribute('имя').Get(), 'Ⅸ')
        cube = child_prim.GetChildren()[0]
        self.assertEqual(cube.GetName(), 'ÄßÖÜäöü')
        self.assertIsNotNone(cube.GetAttribute('이름'))

    async def test_unicode_in_variant_set(self):
        """
        Test creating/loading/selecting with unicode in variant set name and variant names.
        """
        # Test creating variant set with unicode in name and variant names.
        unicode_name = ''.join(_example_valid_string_parts)
        unicode_variant_name = ''.join(reversed(_example_valid_string_parts))
        stage = Usd.Stage.CreateInMemory()
        prim = stage.DefinePrim("/Test")
        variant_set = prim.GetVariantSets().AddVariantSet(unicode_name)
        variant_set.AddVariant(unicode_variant_name)

        # Test export and import stage layer with unicode in variant set name and variant names.
        cache_layer = Sdf.Layer.CreateAnonymous()
        cache_layer.TransferContent(stage.GetRootLayer())
        layer_data = cache_layer.ExportToString()
        new_layer = Sdf.Layer.CreateAnonymous()
        new_layer.ImportFromString(layer_data)
        new_stage = Usd.Stage.CreateInMemory()
        new_stage.GetRootLayer().TransferContent(new_layer)

        # Test loading variant set with unicode in name and variant names.
        prim = new_stage.GetPrimAtPath("/Test")
        self.assertIsNotNone(prim)
        variant_set = prim.GetVariantSets().GetVariantSet(unicode_name)
        self.assertIsNotNone(variant_set)
        variant_set.SetVariantSelection(unicode_variant_name)
        self.assertEqual(variant_set.GetVariantSelection(), unicode_variant_name)

        new_unicode_name = "new_" + unicode_name
        variant_set.AddVariant(new_unicode_name)
        variant_set.SetVariantSelection(new_unicode_name)
        self.assertEqual(variant_set.GetVariantSelection(), new_unicode_name)
