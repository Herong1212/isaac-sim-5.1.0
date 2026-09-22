import asyncio

import omni.UsdMdl as UsdMdl
from pxr import Sdf, Sdr

from .lib.base import UsdMdlTestBase


class Annotation_Tests(UsdMdlTestBase):
    def validate_hints(self, mdl_module, subidentifier, metadata_to_check):

        sdr_node = self.validate_node(mdl_module, subidentifier)

        if self.debug:
            self.debug_print(sdr_node)

        for inputName, v in metadata_to_check.items():
            sdr_property = sdr_node.GetInput(inputName)
            self.assertIsNotNone(sdr_property)
            sdr_property_hints = sdr_property.GetHints()
            self.validateValue(sdr_property_hints, v)

    def validate_input_annotations(self, mdl_module, subidentifier, metadata_to_check):

        sdr_node = self.validate_node(mdl_module, subidentifier)

        if self.debug:
            self.debug_print(sdr_node)

        for inputName, v in metadata_to_check.items():
            sdr_property = sdr_node.GetInput(inputName)
            self.assertIsNotNone(sdr_property)
            sdr_property_metadata = sdr_property.GetMetadata()
            self.validateValue(sdr_property_metadata, v)

    def validate_outputs(self, mdl_module, subidentifier, expected_outputs):

        sdr_node = self.validate_node(mdl_module, subidentifier)

        output_names = sdr_node.GetOutputNames()
        self.assertIsNotNone(output_names)
        self.assertTrue(len(expected_outputs) == len(output_names))

        for output_name in output_names:
            expected = expected_outputs[output_name]
            self.assertIsNotNone(expected)

            sdr_property = sdr_node.GetOutput(output_name)
            self.assertIsNotNone(sdr_property)
            self.validate_property(output_name, sdr_node, expected["value_type_name"], False, expected["metadata"])

    async def test_annotation_range(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_range"

        hints = {
            "pIntSoft": {"soft_range": {"min": 0, "max": 10}},
            "pColorHard": {"hard_range": {"min": (0.1, 0.2, 0.3), "max": (0.4, 0.5, 0.6)}},
        }

        self.validate_hints(mdl_module, subidentifier, hints)

    async def test_annotation_hidden(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_hidden"

        hints = {
            "pInt": {"hidden": 1},
        }

        self.validate_hints(mdl_module, subidentifier, hints)

    async def test_annotation_array(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_array"

        metadata = {
            "pInt": {UsdMdl.Metadata.Annotation: {"key_words": {"words": ["one", "two"]}}},
        }

        self.validate_input_annotations(mdl_module, subidentifier, metadata)

    async def test_annotation_tuple(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_tuple"

        metadata = {
            "pInt": {
                UsdMdl.Metadata.Annotation: {
                    "version": {"major": 1, "minor": 2, "patch": 3, "prerelease": "I am a note"}
                }
            },
        }

        self.validate_input_annotations(mdl_module, subidentifier, metadata)

    async def test_annotation_string(self):
        def _validate_page(sdr_node, input_name, expected):
            sdr_property = sdr_node.GetInput(input_name)
            self.assertIsNotNone(sdr_property)
            page = sdr_property.GetPage()
            self.assertIsNotNone(page)
            self.assertTrue(page == expected)

        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_string"

        sdr_node = self.validate_node(mdl_module, subidentifier)

        sdr_property = sdr_node.GetInput("pInt1")
        self.assertIsNotNone(sdr_property)
        label = sdr_property.GetLabel()
        self.assertIsNotNone(label)
        self.assertTrue(label == "Parameter")

        _validate_page(sdr_node, "pInt2", "A")
        _validate_page(sdr_node, "pInt3", "AA:BB")
        _validate_page(sdr_node, "pInt4", "AAA:BBB:CCC")

    async def test_annotation_return(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_return"

        sdr_node = self.validate_node(mdl_module, subidentifier)

        sdr_property = sdr_node.GetOutput(UsdMdl.Tokens.DefaultOutputPortName)
        self.assertIsNotNone(sdr_property)
        helpStr = sdr_property.GetHelp()
        self.assertIsNotNone(helpStr)
        self.assertTrue(helpStr == "Return type int")

    async def test_annotation_function(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_function"

        metadata = {"help": "I am a MDL function", UsdMdl.Metadata.Modifier: UsdMdl.TypeModifiers.Uniform}

        sdr_node = self.validate_node(mdl_module, subidentifier)
        sdr_node_metadata = sdr_node.GetMetadata()
        self.validateValue(sdr_node_metadata, metadata)

    async def test_annotation_module(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_module"

        metadata = {
            UsdMdl.Metadata.Annotation: {
                UsdMdl.Metadata.Module: {
                    "description": {"description": "I am a MDL module"},
                }
            }
        }

        sdr_node = self.validate_node(mdl_module, subidentifier)
        sdr_node_metadata = sdr_node.GetMetadata()
        self.validateValue(sdr_node_metadata, metadata)

    async def test_annotation_struct_value_and_fields(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_struct_value_and_fields"

        expected_outputs = {
            "i": {
                "value_type_name": Sdf.ValueTypeNames.Int,
                "metadata": {
                    Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int,
                },
            },
            "f": {
                "value_type_name": Sdf.ValueTypeNames.Float,
                "metadata": {
                    Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float,
                },
            },
            UsdMdl.Tokens.DefaultOutputPortName: {
                "value_type_name": Sdr.PropertyTypes.Struct,
                "metadata": {
                    Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Struct,
                    UsdMdl.Metadata.StructType: UsdMdl.StructTypes.User,
                    UsdMdl.Metadata.Symbol: "::TestStruct",
                },
            },
        }

        self.validate_outputs(mdl_module, subidentifier, expected_outputs)

    async def test_annotation_struct_fields_only(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_struct_fields_only"

        expected_outputs = {
            "i": {
                "value_type_name": Sdf.ValueTypeNames.Int,
                "metadata": {
                    Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int,
                },
            },
            "f": {
                "value_type_name": Sdf.ValueTypeNames.Float,
                "metadata": {
                    Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float,
                },
            },
        }

        self.validate_outputs(mdl_module, subidentifier, expected_outputs)

    async def test_annotation_struct_value_only(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_struct_value_only"

        expected_outputs = {
            UsdMdl.Tokens.DefaultOutputPortName: {
                "value_type_name": Sdr.PropertyTypes.Struct,
                "metadata": {
                    Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Struct,
                    UsdMdl.Metadata.StructType: UsdMdl.StructTypes.User,
                    UsdMdl.Metadata.Symbol: "::TestStruct",
                },
            }
        }

        self.validate_outputs(mdl_module, subidentifier, expected_outputs)

    async def test_annotation_enum(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_enum"

        metadata = {
            "param": {
                UsdMdl.Metadata.Annotation: {
                    UsdMdl.Metadata.Type: {"description": {"description": "I am a MDL enum"}},
                    UsdMdl.Metadata.Value: {
                        "0": {"description": {"description": "I am value low"}},
                        "1": {"description": {"description": "I am value medium"}},
                        "2": {"description": {"description": "I am value high"}},
                    },
                }
            },
        }

        self.validate_input_annotations(mdl_module, subidentifier, metadata)

    async def test_annotation_struct_type(self):
        mdl_module = "annotation.mdl"
        subidentifier = "test_annotation_struct_type"
        metadata = {
            "pStruct": {
                UsdMdl.Metadata.Annotation: {
                    UsdMdl.Metadata.Type: {"description": {"description": "I am a MDL struct"}},
                }
            },
        }

        self.validate_input_annotations(mdl_module, subidentifier, metadata)
