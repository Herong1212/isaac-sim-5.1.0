import asyncio

import omni.UsdMdl as UsdMdl
from pxr import Sdf, Sdr

from .lib.base import UsdMdlTestBase


class Expression_Tests(UsdMdlTestBase):
    async def test_call_expression(self):
        mdl_module = "expression.mdl"
        subidentifier = "test_call_expression"
        value_type_name = Sdf.ValueTypeNames.Float3
        default_value = (0.0, 0.0, 0.0)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float3,
        }

        input_metadata = {
            UsdMdl.Metadata.ExpressionKind: UsdMdl.ExpressionKinds.Call,
            UsdMdl.Metadata.ExpressionValue: "mdl::state::normal()",
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata)

    async def test_call_expression_array(self):
        mdl_module = "expression.mdl"
        subidentifier = "test_call_expression_array"
        value_type_name = Sdf.ValueTypeNames.Float3Array
        default_value = [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.6, 0.7, 0.8), (0.123, 0.456, 0.789)]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float3,
        }

        input_metadata = {
            UsdMdl.Metadata.ExpressionKind: [
                UsdMdl.ExpressionKinds.Call,
                UsdMdl.ExpressionKinds.Call,
                None,
                UsdMdl.ExpressionKinds.Parameter,
            ],
            UsdMdl.Metadata.ExpressionValue: ["mdl::state::position()", "mdl::state::normal()", None, 0],
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata)

    async def test_call_expression_with_args(self):
        mdl_module = "expression.mdl"
        subidentifier = "test_call_expression_with_args"
        value_type_name = Sdf.ValueTypeNames.Float3
        default_value = (0.0, 0.0, 0.0)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float3,
        }

        input_metadata = {
            UsdMdl.Metadata.ExpressionKind: UsdMdl.ExpressionKinds.Call,
            UsdMdl.Metadata.ExpressionValue: "mdl::state::texture_tangent_v(0)",
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata)

    async def test_parameter_expression_vector_bool4(self):
        mdl_module = "expression.mdl"
        subidentifier = "test_parameter_expression_vector_bool4"
        value_type_name = Sdf.ValueTypeNames.BoolArray
        default_value = [True, True, True, False]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Bool4,
        }

        input_metadata = {
            UsdMdl.Metadata.ExpressionKind: [None, UsdMdl.ExpressionKinds.Parameter, None, None],
            UsdMdl.Metadata.ExpressionValue: [None, 0, None, None],
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata)

    async def test_parameter_expression_color(self):
        mdl_module = "expression.mdl"
        subidentifier = "test_parameter_expression_color"
        value_type_name = Sdf.ValueTypeNames.Color3f
        default_value = (0.1, 0.999, 0.3)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Color,
        }

        input_metadata = {
            UsdMdl.Metadata.ExpressionKind: [None, UsdMdl.ExpressionKinds.Parameter, None],
            UsdMdl.Metadata.ExpressionValue: [None, 0, None],
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata)

    async def test_parameter_expression_double_matrix(self):
        mdl_module = "expression.mdl"
        subidentifier = "test_parameter_expression_double_matrix"
        value_type_name = Sdf.ValueTypeNames.Matrix2d
        default_value = ((0.1, 0.999), (0.3, 0.4))

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double2x2,
        }

        input_metadata = {
            UsdMdl.Metadata.ExpressionKind: [None, UsdMdl.ExpressionKinds.Parameter, None, None],
            UsdMdl.Metadata.ExpressionValue: [None, 0, None, None],
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata)

    async def test_parameter_expression_float_matrix(self):
        mdl_module = "expression.mdl"
        subidentifier = "test_parameter_expression_float_matrix"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.999, 0.3, 0.4]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float2x2,
        }

        input_metadata = {
            UsdMdl.Metadata.ExpressionKind: [None, UsdMdl.ExpressionKinds.Parameter, None, None],
            UsdMdl.Metadata.ExpressionValue: [None, 0, None, None],
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata)

    async def test_parameter_expression(self):
        mdl_module = "expression.mdl"
        subidentifier = "test_parameter_expression"
        value_type_name = Sdf.ValueTypeNames.Int
        default_value = 1234

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int,
        }

        input_metadata = {
            UsdMdl.Metadata.ExpressionKind: UsdMdl.ExpressionKinds.Parameter,
            UsdMdl.Metadata.ExpressionValue: 1,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata)

    async def test_multi_parameter_expression(self):
        mdl_module = "expression.mdl"
        subidentifier = "test_multi_parameter_expression"
        value_type_name = Sdf.ValueTypeNames.Int
        default_value = 789

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int,
        }

        input_metadata = {
            UsdMdl.Metadata.ExpressionKind: UsdMdl.ExpressionKinds.Parameter,
            UsdMdl.Metadata.ExpressionValue: 1,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata)

    async def test_parameter_call_expression(self):
        mdl_module = "expression.mdl"
        subidentifier = "test_parameter_call_expression"
        value_type_name = Sdf.ValueTypeNames.Float3
        default_value = (0.0, 0.0, 0.0)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float3,
        }

        input_metadata = {
            UsdMdl.Metadata.ExpressionKind: UsdMdl.ExpressionKinds.Parameter,
            UsdMdl.Metadata.ExpressionValue: 1,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata)
