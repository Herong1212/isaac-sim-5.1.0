import asyncio

import omni.UsdMdl as UsdMdl
from pxr import Sdf, Sdr

from .lib.base import UsdMdlTestBase


class Type_Tests(UsdMdlTestBase):
    async def test_type_alias(self):
        mdl_module = "alias.mdl"
        subidentifier = "test_alias"
        value_type_name = Sdf.ValueTypeNames.Int
        default_value = 1234

        metadata = {Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int, UsdMdl.Metadata.Symbol: "number"}

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_bsdfMeasurement(self):
        mdl_module = "bsdfMeasurement.mdl"
        subidentifier = "test_bsdfMeasurement"
        value_type_name = Sdf.ValueTypeNames.Asset
        default_value = Sdf.AssetPath("/resources/one.mbsdf")

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Bsdf_Measurement,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, checkOutputs=False)

    async def test_type_bsdfMeasurement_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_bsdfMeasurement_array"
        value_type_name = Sdf.ValueTypeNames.AssetArray
        default_value = [Sdf.AssetPath("/resources/one.mbsdf"), Sdf.AssetPath("/resources/two.mbsdf")]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Bsdf_Measurement,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, checkOutputs=False)

    async def test_type_bool(self):
        mdl_module = "bool.mdl"
        subidentifier = "test_bool"
        value_type_name = Sdf.ValueTypeNames.Bool
        default_value = True

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Bool,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_bool_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_bool_array"
        value_type_name = Sdf.ValueTypeNames.BoolArray
        default_value = [True, False, True, False]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Bool,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_color(self):
        mdl_module = "color.mdl"
        subidentifier = "test_color"
        value_type_name = Sdf.ValueTypeNames.Color3f
        default_value = (0.1, 0.2, 0.3)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Color,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_color_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_color_array"
        value_type_name = Sdf.ValueTypeNames.Color3fArray
        default_value = [(0.1, 0.2, 0.3), (0.4, 0.5, 0.6), (0.7, 0.8, 0.9)]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Color,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_double(self):
        mdl_module = "double.mdl"
        subidentifier = "test_double"
        value_type_name = Sdf.ValueTypeNames.Double
        default_value = 0.1

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_double_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_double_array"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [1.1, 2.2, 3.3, 4.4, 5.5, 6.6]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_dynamic_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_dynamic_array"
        value_type_name = Sdf.ValueTypeNames.Color3fArray
        default_value = None

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Color,
            UsdMdl.Metadata.ArrayDeferredSizeSymbol: "N",
            Sdr.PropertyMetadata.IsDynamicArray: "",
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, checkOutputs=False)

    async def test_type_enum(self):
        mdl_module = "enum.mdl"
        subidentifier = "test_enum"
        value_type_name = Sdf.ValueTypeNames.Int
        default_value = 3

        metadata = {Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Enum, UsdMdl.Metadata.Symbol: "::tex::wrap_mode"}

        options = [("wrap_clamp", "0"), ("wrap_repeat", "1"), ("wrap_mirrored_repeat", "2"), ("wrap_clip", "3")]

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, options=options)

    async def test_type_enum_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_enum_array"
        value_type_name = Sdf.ValueTypeNames.IntArray
        default_value = [3, 2, 0]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Enum,
            UsdMdl.Metadata.Symbol: "::tex::wrap_mode",
        }

        options = [("wrap_clamp", "0"), ("wrap_repeat", "1"), ("wrap_mirrored_repeat", "2"), ("wrap_clip", "3")]

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, options=options)

    async def test_type_float(self):
        mdl_module = "float.mdl"
        subidentifier = "test_float"
        value_type_name = Sdf.ValueTypeNames.Float
        default_value = 0.1

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_float_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_float_array"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [1.1, 2.2, 3.3, 4.4, 5.5]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_int(self):
        mdl_module = "int.mdl"
        subidentifier = "test_int"
        value_type_name = Sdf.ValueTypeNames.Int
        default_value = 1

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_int_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_int_array"
        value_type_name = Sdf.ValueTypeNames.IntArray
        default_value = [1, 2, 3, 4]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Int,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_lightProfile(self):
        mdl_module = "lightProfile.mdl"
        subidentifier = "test_lightProfile"
        value_type_name = Sdf.ValueTypeNames.Asset
        default_value = Sdf.AssetPath("/resources/one.ies")

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Light_Profile,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, checkOutputs=False)

    async def test_type_lightProfile_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_lightProfile_array"
        value_type_name = Sdf.ValueTypeNames.AssetArray
        default_value = [Sdf.AssetPath("/resources/one.ies"), Sdf.AssetPath("/resources/two.ies")]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Light_Profile,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, checkOutputs=False)

    async def test_type_material(self):
        mdl_module = "material.mdl"
        subidentifier = "test_material"
        value_type_name = Sdr.PropertyTypes.Terminal
        default_value = None

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Struct,
            UsdMdl.Metadata.StructType: UsdMdl.StructTypes.Material,
            UsdMdl.Metadata.Symbol: "::material",
        }

        input_metadata = {
            UsdMdl.Metadata.ExpressionKind: UsdMdl.ExpressionKinds.Call,
            UsdMdl.Metadata.ExpressionValue: "diffuse(color,float,float3)",
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata)

    async def test_type_matrix_2x2d(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_double2x2"
        value_type_name = Sdf.ValueTypeNames.Matrix2d
        default_value = ((0.1, 0.2), (0.3, 0.4))

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double2x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_2x2d_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_double2x2_array"
        value_type_name = Sdf.ValueTypeNames.Matrix2dArray
        default_value = [((0.1, 0.2), (0.3, 0.4)), ((1.1, 1.2), (1.3, 1.4))]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double2x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_2x3d(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_double2x3"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double2x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_2x3d_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_double2x3_array"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double2x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_2x4d(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_double2x4"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double2x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_2x4d_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_double2x4_array"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double2x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x2d(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_double3x2"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double3x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x2d_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_double3x2_array"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double3x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x3d(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_double3x3"
        value_type_name = Sdf.ValueTypeNames.Matrix3d
        default_value = ((0.1, 0.2, 0.3), (0.4, 0.5, 0.6), (0.7, 0.8, 0.9))

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double3x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x3d_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_double3x3_array"
        value_type_name = Sdf.ValueTypeNames.Matrix3dArray
        default_value = [
            ((0.1, 0.2, 0.3), (0.4, 0.5, 0.6), (0.7, 0.8, 0.9)),
            ((1.1, 1.2, 1.3), (1.4, 1.5, 1.6), (1.7, 1.8, 1.9)),
        ]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double3x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x4d(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_double3x4"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double3x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x4d_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_double3x4_array"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            1.0,
            1.1,
            1.2,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.6,
            1.7,
            1.8,
            1.9,
            2.0,
            2.1,
            2.2,
        ]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double3x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x2d(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_double4x2"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double4x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x2d_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_double4x2_array"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double4x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x3d(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_double4x3"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double4x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x3d_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_double4x3_array"
        value_type_name = Sdf.ValueTypeNames.DoubleArray
        default_value = [
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            1.0,
            1.1,
            1.2,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.6,
            1.7,
            1.8,
            1.9,
            2.0,
            2.1,
            2.2,
        ]
        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double4x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x4d(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_double4x4"
        value_type_name = Sdf.ValueTypeNames.Matrix4d
        default_value = ((0.1, 0.2, 0.3, 0.4), (0.5, 0.6, 0.7, 0.8), (0.9, 1.0, 1.1, 1.2), (1.3, 1.4, 1.5, 1.6))

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double4x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x4d_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_double4x4_array"
        value_type_name = Sdf.ValueTypeNames.Matrix4dArray
        default_value = [
            ((0.1, 0.2, 0.3, 0.4), (0.5, 0.6, 0.7, 0.8), (0.9, 1.0, 1.1, 1.2), (1.3, 1.4, 1.5, 1.6)),
            ((1.1, 1.2, 1.3, 1.4), (1.5, 1.6, 1.7, 1.8), (1.9, 2.0, 2.1, 2.2), (2.3, 2.4, 2.5, 2.6)),
        ]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double4x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_2x2f(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_float2x2"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float2x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_2x2f_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_float2x2_array"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 1.1, 1.2, 1.3, 1.4]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float2x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_2x3f(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_float2x3"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float2x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_2x3f_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_float2x3_array"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float2x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_2x4f(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_float2x4"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float2x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_2x4f_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_float2x4_array"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float2x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x2f(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_float3x2"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float3x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x2f_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_float3x2_array"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float3x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x3f(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_float3x3"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float3x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x3f_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_float3x3_array"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float3x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x4f(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_float3x4"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float3x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_3x4_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_float3x4_array"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            1.0,
            1.1,
            1.2,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.6,
            1.7,
            1.8,
            1.9,
            2.0,
            2.1,
            2.2,
        ]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float3x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x2f(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_float4x2"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float4x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x2_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_float4x2_array"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float4x2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x3f(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_float4x3"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float4x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x3_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_float4x3_array"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            1.0,
            1.1,
            1.2,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.6,
            1.7,
            1.8,
            1.9,
            2.0,
            2.1,
            2.2,
        ]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float4x3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x4f(self):
        mdl_module = "matrix.mdl"
        subidentifier = "test_matrix_float4x4"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float4x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_matrix_4x4f_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_matrix_float4x4_array"
        value_type_name = Sdf.ValueTypeNames.FloatArray
        default_value = [
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            1.0,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.6,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.6,
            1.7,
            1.8,
            1.9,
            2.0,
            2.1,
            2.2,
            2.3,
            2.4,
            2.5,
            2.6,
        ]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float4x4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_string(self):
        mdl_module = "string.mdl"
        subidentifier = "test_string"
        value_type_name = Sdf.ValueTypeNames.String
        default_value = "aStringValue"

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.String,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_string_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_string_array"
        value_type_name = Sdf.ValueTypeNames.StringArray
        default_value = ["my", "mind", "is", "going", ""]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.String,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_struct(self):
        mdl_module = "struct.mdl"
        subidentifier = "test_struct"
        value_type_name = Sdr.PropertyTypes.Struct
        default_value = None

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Struct,
            UsdMdl.Metadata.StructType: UsdMdl.StructTypes.User,
            UsdMdl.Metadata.Symbol: "::TestStruct",
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_struct_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_struct_array"
        value_type_name = Sdr.PropertyTypes.Unknown
        default_value = None

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Struct,
            UsdMdl.Metadata.Symbol: "::SimpleStruct",
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_texture2D(self):
        mdl_module = "texture.mdl"
        subidentifier = "test_texture2D"
        value_type_name = Sdf.ValueTypeNames.Asset
        default_value = Sdf.AssetPath("/resources/one.png")

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Texture2d,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        input_metadata = {UsdMdl.Metadata.TextureGamma: "1", UsdMdl.Metadata.TextureSelector: "channelSelection"}

        self.validate_mdl(
            mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata, checkOutputs=False
        )

    async def test_type_texture2D_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_texture2D_array"
        value_type_name = Sdf.ValueTypeNames.AssetArray
        default_value = [Sdf.AssetPath("/resources/one.png"), Sdf.AssetPath("/resources/two.png")]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Texture2d,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        input_metadata = {
            UsdMdl.Metadata.TextureGamma: [1, 2.2],
            UsdMdl.Metadata.TextureSelector: ["channelOne", "channelTwo"],
        }

        self.validate_mdl(
            mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata, checkOutputs=False
        )

    async def test_type_texture3D(self):
        mdl_module = "texture.mdl"
        subidentifier = "test_texture3D"
        value_type_name = Sdf.ValueTypeNames.Asset
        default_value = Sdf.AssetPath("/resources/one.vdb")

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Texture3d,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        input_metadata = {UsdMdl.Metadata.TextureGamma: "1", UsdMdl.Metadata.TextureSelector: "dataSetSelection"}

        self.validate_mdl(
            mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata, checkOutputs=False
        )

    async def test_type_texture3D_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_texture3D_array"
        value_type_name = Sdf.ValueTypeNames.AssetArray
        default_value = [Sdf.AssetPath("/resources/one.vdb"), Sdf.AssetPath("/resources/two.vdb")]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Texture3d,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        input_metadata = {
            UsdMdl.Metadata.TextureGamma: [1, 2.2],
            UsdMdl.Metadata.TextureSelector: ["channelOne", "channelTwo"],
        }

        self.validate_mdl(
            mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata, checkOutputs=False
        )

    async def test_type_textureCube(self):
        mdl_module = "texture.mdl"
        subidentifier = "test_textureCube"
        value_type_name = Sdf.ValueTypeNames.Asset
        default_value = Sdf.AssetPath("/resources/one.hdr")

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.TextureCube,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        input_metadata = {
            UsdMdl.Metadata.TextureGamma: "1",
        }

        self.validate_mdl(
            mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata, checkOutputs=False
        )

    async def test_type_textureCube_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_textureCube_array"
        value_type_name = Sdf.ValueTypeNames.AssetArray
        default_value = [Sdf.AssetPath("/resources/one.hdr"), Sdf.AssetPath("/resources/two.hdr")]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.TextureCube,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        input_metadata = {UsdMdl.Metadata.TextureGamma: [1, 2.2]}

        self.validate_mdl(
            mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata, checkOutputs=False
        )

    async def test_type_texturePtex(self):
        mdl_module = "texture.mdl"
        subidentifier = "test_texturePtex"
        value_type_name = Sdf.ValueTypeNames.Asset
        default_value = Sdf.AssetPath("/resources/one.ptx")

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.TexturePtex,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        input_metadata = {UsdMdl.Metadata.TextureGamma: "1"}

        self.validate_mdl(
            mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata, checkOutputs=False
        )

    async def test_type_texturePtex_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_texturePtex_array"
        value_type_name = Sdf.ValueTypeNames.AssetArray
        default_value = [Sdf.AssetPath("/resources/one.ptx"), Sdf.AssetPath("/resources/two.ptx")]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.TexturePtex,
            Sdr.PropertyMetadata.IsAssetIdentifier: "1",
        }

        input_metadata = {
            UsdMdl.Metadata.TextureGamma: [1, 2.2],
        }

        self.validate_mdl(
            mdl_module, subidentifier, value_type_name, default_value, metadata, input_metadata, checkOutputs=False
        )

    async def test_type_modifier_uniform(self):
        mdl_module = "type_modifiers.mdl"
        subidentifier = "test_type_modifier_uniform"
        value_type_name = Sdf.ValueTypeNames.Int
        default_value = 1

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int,
            UsdMdl.Metadata.Modifier: UsdMdl.TypeModifiers.Uniform,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_modifier_varying(self):
        mdl_module = "type_modifiers.mdl"
        subidentifier = "test_type_modifier_varying"
        value_type_name = Sdf.ValueTypeNames.Int
        default_value = 1

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int,
            UsdMdl.Metadata.Modifier: UsdMdl.TypeModifiers.Varying,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_bool2(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_bool2"
        value_type_name = Sdf.ValueTypeNames.BoolArray
        default_value = [True, False]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Bool2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_bool2_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_bool2_array"
        value_type_name = Sdf.ValueTypeNames.BoolArray
        default_value = [True, False, False, True]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Bool2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_bool3(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_bool3"
        value_type_name = Sdf.ValueTypeNames.BoolArray
        default_value = [True, False, True]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Bool3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_bool3_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_bool3_array"
        value_type_name = Sdf.ValueTypeNames.BoolArray
        default_value = [True, False, True, False, True, False]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Bool3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_bool4(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_bool4"
        value_type_name = Sdf.ValueTypeNames.BoolArray
        default_value = [True, False, True, False]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Bool4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_bool4_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_bool4_array"
        value_type_name = Sdf.ValueTypeNames.BoolArray
        default_value = [True, False, True, False, False, True, False, True]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Bool4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_double2(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_double2"
        value_type_name = Sdf.ValueTypeNames.Double2
        default_value = (0.1, 0.2)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_double2_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_double2_array"
        value_type_name = Sdf.ValueTypeNames.Double2Array
        default_value = [(0.1, 0.2), (1.1, 1.2)]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_double3(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_double3"
        value_type_name = Sdf.ValueTypeNames.Double3
        default_value = (0.1, 0.2, 0.3)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_double3_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_double3_array"
        value_type_name = Sdf.ValueTypeNames.Double3Array
        default_value = [(0.1, 0.2, 0.3), (1.1, 1.2, 1.3)]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_double4(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_double4"
        value_type_name = Sdf.ValueTypeNames.Double4
        default_value = (0.1, 0.2, 0.3, 0.4)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Double4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_double4_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_double4_array"
        value_type_name = Sdf.ValueTypeNames.Double4Array
        default_value = [(0.1, 0.2, 0.3, 0.4), (1.1, 1.2, 1.3, 1.4)]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Double4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_float2(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_float2"
        value_type_name = Sdf.ValueTypeNames.Float2
        default_value = (0.1, 0.2)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_float2_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_float2_array"
        value_type_name = Sdf.ValueTypeNames.Float2Array
        default_value = [(0.1, 0.2), (1.1, 1.2)]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_float3(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_float3"
        value_type_name = Sdf.ValueTypeNames.Float3
        default_value = (0.1, 0.2, 0.3)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_float3_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_float3_array"
        value_type_name = Sdf.ValueTypeNames.Float3Array
        default_value = [(0.1, 0.2, 0.3), (1.1, 1.2, 1.3)]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_float4(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_float4"
        value_type_name = Sdf.ValueTypeNames.Float4
        default_value = (0.1, 0.2, 0.3, 0.4)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Float4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_float4_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_float4_array"
        value_type_name = Sdf.ValueTypeNames.Float4Array
        default_value = [(0.1, 0.2, 0.3, 0.4), (1.1, 1.2, 1.3, 1.4)]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Float4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_int2(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_int2"
        value_type_name = Sdf.ValueTypeNames.Int2
        default_value = (1, 2)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_int2_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_int2_array"
        value_type_name = Sdf.ValueTypeNames.Int2Array
        default_value = [(1, 2), (2, 1)]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Int2,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_int3(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_int3"
        value_type_name = Sdf.ValueTypeNames.Int3
        default_value = (1, 2, 3)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_int3_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_int3_array"
        value_type_name = Sdf.ValueTypeNames.Int3Array
        default_value = [(1, 2, 3), (3, 2, 1)]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Int3,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_int4(self):
        mdl_module = "vector.mdl"
        subidentifier = "test_vector_int4"
        value_type_name = Sdf.ValueTypeNames.Int4
        default_value = (1, 2, 3, 4)

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Int4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)

    async def test_type_vector_int4_array(self):
        mdl_module = "array.mdl"
        subidentifier = "test_vector_int4_array"
        value_type_name = Sdf.ValueTypeNames.Int4Array
        default_value = [(1, 2, 3, 4), (4, 3, 2, 1)]

        metadata = {
            Sdr.PropertyMetadata.RenderType: UsdMdl.Types.Array,
            UsdMdl.Metadata.ArrayElementType: UsdMdl.Types.Int4,
        }

        self.validate_mdl(mdl_module, subidentifier, value_type_name, default_value, metadata)
