"""Testing the type conversion utility"""

import omni.graph.core as og
import omni.graph.core.types as ot
import omni.graph.tools.ogn as ogn
import omni.kit
from pxr import Sdf


# ==============================================================================================================
def _test_data() -> list[list]:
    """Get the comprehensive list of type conversions available as [OGN, SDF, PYTHON_ANNOTATION, ATTRIBUTE_TYPE]
    so that forward and reverse conversion checks can be made. The PYTHON_ANNOTATION value can be a list because there
    are type aliases that match Warp type names, such as "float64" for "double". The first one will be the canonical
    one that comes from the file definitions.
    """
    _b = og.BaseDataType  # Short forms to make type specification shorter
    _r = og.AttributeRole
    _s = Sdf.ValueTypeNames
    test_data = [
        ["any", None, ot.any, og.Type(_b.TOKEN)],
        ["bool", _s.Bool, [ot.bool, ot.boolean], og.Type(_b.BOOL)],
        ["bool[]", _s.BoolArray, ot.boolarray, og.Type(_b.BOOL, 1, 1)],
        ["bundle", None, ot.bundle, og.Type(_b.RELATIONSHIP, 1, 0, _r.BUNDLE)],
        ["colord[3]", _s.Color3d, ot.color3d, og.Type(_b.DOUBLE, 3, 0, _r.COLOR)],
        ["colord[3][]", _s.Color3dArray, ot.color3darray, og.Type(_b.DOUBLE, 3, 1, _r.COLOR)],
        ["colord[4]", _s.Color4d, ot.color4d, og.Type(_b.DOUBLE, 4, 0, _r.COLOR)],
        ["colord[4][]", _s.Color4dArray, ot.color4darray, og.Type(_b.DOUBLE, 4, 1, _r.COLOR)],
        ["colorf[3]", _s.Color3f, ot.color3f, og.Type(_b.FLOAT, 3, 0, _r.COLOR)],
        ["colorf[3][]", _s.Color3fArray, ot.color3farray, og.Type(_b.FLOAT, 3, 1, _r.COLOR)],
        ["colorf[4]", _s.Color4f, ot.color4f, og.Type(_b.FLOAT, 4, 0, _r.COLOR)],
        ["colorf[4][]", _s.Color4fArray, ot.color4farray, og.Type(_b.FLOAT, 4, 1, _r.COLOR)],
        ["colorh[3]", _s.Color3h, ot.color3h, og.Type(_b.HALF, 3, 0, _r.COLOR)],
        ["colorh[3][]", _s.Color3hArray, ot.color3harray, og.Type(_b.HALF, 3, 1, _r.COLOR)],
        ["colorh[4]", _s.Color4h, ot.color4h, og.Type(_b.HALF, 4, 0, _r.COLOR)],
        ["colorh[4][]", _s.Color4hArray, ot.color4harray, og.Type(_b.HALF, 4, 1, _r.COLOR)],
        ["double", _s.Double, [ot.double, ot.float64], og.Type(_b.DOUBLE)],
        ["double[]", _s.DoubleArray, ot.doublearray, og.Type(_b.DOUBLE, 1, 1)],
        ["double[2]", _s.Double2, ot.double2, og.Type(_b.DOUBLE, 2)],
        ["double[2][]", _s.Double2Array, ot.double2array, og.Type(_b.DOUBLE, 2, 1)],
        ["double[3]", _s.Double3, ot.double3, og.Type(_b.DOUBLE, 3)],
        ["double[3][]", _s.Double3Array, ot.double3array, og.Type(_b.DOUBLE, 3, 1)],
        ["double[4]", _s.Double4, ot.double4, og.Type(_b.DOUBLE, 4)],
        ["double[4][]", _s.Double4Array, ot.double4array, og.Type(_b.DOUBLE, 4, 1)],
        ["execution", None, ot.execution, og.Type(_b.UINT, 1, 0, _r.EXECUTION)],
        ["float", _s.Float, [ot.float, ot.float32], og.Type(_b.FLOAT)],
        ["float[]", _s.FloatArray, ot.floatarray, og.Type(_b.FLOAT, 1, 1)],
        ["float[2]", _s.Float2, ot.float2, og.Type(_b.FLOAT, 2)],
        ["float[2][]", _s.Float2Array, ot.float2array, og.Type(_b.FLOAT, 2, 1)],
        ["float[3]", _s.Float3, ot.float3, og.Type(_b.FLOAT, 3)],
        ["float[3][]", _s.Float3Array, ot.float3array, og.Type(_b.FLOAT, 3, 1)],
        ["float[4]", _s.Float4, ot.float4, og.Type(_b.FLOAT, 4)],
        ["float[4][]", _s.Float4Array, ot.float4array, og.Type(_b.FLOAT, 4, 1)],
        ["frame[4]", _s.Frame4d, ot.frame4d, og.Type(_b.DOUBLE, 16, 0, _r.FRAME)],
        ["frame[4][]", _s.Frame4dArray, ot.frame4darray, og.Type(_b.DOUBLE, 16, 1, _r.FRAME)],
        ["half", _s.Half, [ot.half, ot.float16], og.Type(_b.HALF)],
        ["half[]", _s.HalfArray, ot.halfarray, og.Type(_b.HALF, 1, 1)],
        ["half[2]", _s.Half2, ot.half2, og.Type(_b.HALF, 2)],
        ["half[2][]", _s.Half2Array, ot.half2array, og.Type(_b.HALF, 2, 1)],
        ["half[3]", _s.Half3, ot.half3, og.Type(_b.HALF, 3)],
        ["half[3][]", _s.Half3Array, ot.half3array, og.Type(_b.HALF, 3, 1)],
        ["half[4]", _s.Half4, ot.half4, og.Type(_b.HALF, 4)],
        ["half[4][]", _s.Half4Array, ot.half4array, og.Type(_b.HALF, 4, 1)],
        ["int", _s.Int, [ot.int, ot.int32], og.Type(_b.INT)],
        ["int[]", _s.IntArray, ot.intarray, og.Type(_b.INT, 1, 1)],
        ["int[2]", _s.Int2, ot.int2, og.Type(_b.INT, 2)],
        ["int[2][]", _s.Int2Array, ot.int2array, og.Type(_b.INT, 2, 1)],
        ["int[3]", _s.Int3, ot.int3, og.Type(_b.INT, 3)],
        ["int[3][]", _s.Int3Array, ot.int3array, og.Type(_b.INT, 3, 1)],
        ["int[4]", _s.Int4, ot.int4, og.Type(_b.INT, 4)],
        ["int[4][]", _s.Int4Array, ot.int4array, og.Type(_b.INT, 4, 1)],
        ["int64", _s.Int64, ot.int64, og.Type(_b.INT64)],
        ["int64[]", _s.Int64Array, ot.int64array, og.Type(_b.INT64, 1, 1)],
        ["matrixd[2]", _s.Matrix2d, ot.matrix2d, og.Type(_b.DOUBLE, 4, 0, _r.MATRIX)],
        ["matrixd[2][]", _s.Matrix2dArray, ot.matrix2darray, og.Type(_b.DOUBLE, 4, 1, _r.MATRIX)],
        ["matrixd[3]", _s.Matrix3d, ot.matrix3d, og.Type(_b.DOUBLE, 9, 0, _r.MATRIX)],
        ["matrixd[3][]", _s.Matrix3dArray, ot.matrix3darray, og.Type(_b.DOUBLE, 9, 1, _r.MATRIX)],
        ["matrixd[4]", _s.Matrix4d, ot.matrix4d, og.Type(_b.DOUBLE, 16, 0, _r.MATRIX)],
        ["matrixd[4][]", _s.Matrix4dArray, ot.matrix4darray, og.Type(_b.DOUBLE, 16, 1, _r.MATRIX)],
        ["normald[3]", _s.Normal3d, ot.normal3d, og.Type(_b.DOUBLE, 3, 0, _r.NORMAL)],
        ["normald[3][]", _s.Normal3dArray, ot.normal3darray, og.Type(_b.DOUBLE, 3, 1, _r.NORMAL)],
        ["normalf[3]", _s.Normal3f, ot.normal3f, og.Type(_b.FLOAT, 3, 0, _r.NORMAL)],
        ["normalf[3][]", _s.Normal3fArray, ot.normal3farray, og.Type(_b.FLOAT, 3, 1, _r.NORMAL)],
        ["normalh[3]", _s.Normal3h, ot.normal3h, og.Type(_b.HALF, 3, 0, _r.NORMAL)],
        ["normalh[3][]", _s.Normal3hArray, ot.normal3harray, og.Type(_b.HALF, 3, 1, _r.NORMAL)],
        ["objectId", None, ot.objectid, og.Type(_b.UINT64, 1, 0, _r.OBJECT_ID)],
        ["objectId[]", None, ot.objectidarray, og.Type(_b.UINT64, 1, 1, _r.OBJECT_ID)],
        ["pointd[3]", _s.Point3d, ot.point3d, og.Type(_b.DOUBLE, 3, 0, _r.POSITION)],
        ["pointd[3][]", _s.Point3dArray, ot.point3darray, og.Type(_b.DOUBLE, 3, 1, _r.POSITION)],
        ["pointf[3]", _s.Point3f, ot.point3f, og.Type(_b.FLOAT, 3, 0, _r.POSITION)],
        ["pointf[3][]", _s.Point3fArray, ot.point3farray, og.Type(_b.FLOAT, 3, 1, _r.POSITION)],
        ["pointh[3]", _s.Point3h, ot.point3h, og.Type(_b.HALF, 3, 0, _r.POSITION)],
        ["pointh[3][]", _s.Point3hArray, ot.point3harray, og.Type(_b.HALF, 3, 1, _r.POSITION)],
        ["quatd[4]", _s.Quatd, ot.quatd, og.Type(_b.DOUBLE, 4, 0, _r.QUATERNION)],
        ["quatd[4][]", _s.QuatdArray, ot.quatdarray, og.Type(_b.DOUBLE, 4, 1, _r.QUATERNION)],
        ["quatf[4]", _s.Quatf, ot.quatf, og.Type(_b.FLOAT, 4, 0, _r.QUATERNION)],
        ["quatf[4][]", _s.QuatfArray, ot.quatfarray, og.Type(_b.FLOAT, 4, 1, _r.QUATERNION)],
        ["quath[4]", _s.Quath, ot.quath, og.Type(_b.HALF, 4, 0, _r.QUATERNION)],
        ["quath[4][]", _s.QuathArray, ot.quatharray, og.Type(_b.HALF, 4, 1, _r.QUATERNION)],
        ["string", _s.String, ot.string, og.Type(_b.UCHAR, 1, 1, _r.TEXT)],
        ["target", None, ot.target, og.Type(_b.RELATIONSHIP, 1, 0, _r.TARGET)],
        ["texcoordd[2]", _s.TexCoord2d, ot.texcoord2d, og.Type(_b.DOUBLE, 2, 0, _r.TEXCOORD)],
        ["texcoordd[2][]", _s.TexCoord2dArray, ot.texcoord2darray, og.Type(_b.DOUBLE, 2, 1, _r.TEXCOORD)],
        ["texcoordd[3]", _s.TexCoord3d, ot.texcoord3d, og.Type(_b.DOUBLE, 3, 0, _r.TEXCOORD)],
        ["texcoordd[3][]", _s.TexCoord3dArray, ot.texcoord3darray, og.Type(_b.DOUBLE, 3, 1, _r.TEXCOORD)],
        ["texcoordf[2]", _s.TexCoord2f, ot.texcoord2f, og.Type(_b.FLOAT, 2, 0, _r.TEXCOORD)],
        ["texcoordf[2][]", _s.TexCoord2fArray, ot.texcoord2farray, og.Type(_b.FLOAT, 2, 1, _r.TEXCOORD)],
        ["texcoordf[3]", _s.TexCoord3f, ot.texcoord3f, og.Type(_b.FLOAT, 3, 0, _r.TEXCOORD)],
        ["texcoordf[3][]", _s.TexCoord3fArray, ot.texcoord3farray, og.Type(_b.FLOAT, 3, 1, _r.TEXCOORD)],
        ["texcoordh[2]", _s.TexCoord2h, ot.texcoord2h, og.Type(_b.HALF, 2, 0, _r.TEXCOORD)],
        ["texcoordh[2][]", _s.TexCoord2hArray, ot.texcoord2harray, og.Type(_b.HALF, 2, 1, _r.TEXCOORD)],
        ["texcoordh[3]", _s.TexCoord3h, ot.texcoord3h, og.Type(_b.HALF, 3, 0, _r.TEXCOORD)],
        ["texcoordh[3][]", _s.TexCoord3hArray, ot.texcoord3harray, og.Type(_b.HALF, 3, 1, _r.TEXCOORD)],
        ["timecode", _s.TimeCode, ot.timecode, og.Type(_b.DOUBLE, 1, 0, _r.TIMECODE)],
        ["timecode[]", _s.TimeCodeArray, ot.timecodearray, og.Type(_b.DOUBLE, 1, 1, _r.TIMECODE)],
        ["token", _s.Token, ot.token, og.Type(_b.TOKEN)],
        ["token[]", _s.TokenArray, ot.tokenarray, og.Type(_b.TOKEN, 1, 1)],
        ["uchar", _s.UChar, [ot.uchar, ot.uint8], og.Type(_b.UCHAR)],
        ["uchar[]", _s.UCharArray, ot.uchararray, og.Type(_b.UCHAR, 1, 1)],
        ["uint", _s.UInt, [ot.uint, ot.uint32], og.Type(_b.UINT)],
        ["uint[]", _s.UIntArray, ot.uintarray, og.Type(_b.UINT, 1, 1)],
        ["uint64", _s.UInt64, ot.uint64, og.Type(_b.UINT64)],
        ["uint64[]", _s.UInt64Array, ot.uint64array, og.Type(_b.UINT64, 1, 1)],
        ["vectord[3]", _s.Vector3d, ot.vector3d, og.Type(_b.DOUBLE, 3, 0, _r.VECTOR)],
        ["vectord[3][]", _s.Vector3dArray, ot.vector3darray, og.Type(_b.DOUBLE, 3, 1, _r.VECTOR)],
        ["vectorf[3]", _s.Vector3f, ot.vector3f, og.Type(_b.FLOAT, 3, 0, _r.VECTOR)],
        ["vectorf[3][]", _s.Vector3fArray, ot.vector3farray, og.Type(_b.FLOAT, 3, 1, _r.VECTOR)],
        ["vectorh[3]", _s.Vector3h, ot.vector3h, og.Type(_b.HALF, 3, 0, _r.VECTOR)],
        ["vectorh[3][]", _s.Vector3hArray, ot.vector3harray, og.Type(_b.HALF, 3, 1, _r.VECTOR)],
    ]

    return test_data


# ==============================================================================================================
class _TestOgnTypeConversions(omni.kit.test.AsyncTestCase):
    async def test_python_type_aliases(self):
        """Run through the set of Python type definitions and check that the ones with multiple entries are all equal"""
        for _, _, py_ann_type, _ in _test_data():
            if not isinstance(py_ann_type, list):
                continue
            for index in range(len(py_ann_type) - 1):
                self.assertEqual(py_ann_type[index], py_ann_type[index + 1])

    # --------------------------------------------------------------------------------------------------------------
    async def test_type_conversions(self):
        """Do a representative set of type conversion checks"""
        bool_sdf = ot.convert_type("bool", ot.DataTypeRepresentation.OGN, ot.DataTypeRepresentation.SDF)
        self.assertEqual(bool_sdf, Sdf.ValueTypeNames.Bool)
        bool_attr = ot.convert_type("bool", ot.DataTypeRepresentation.OGN, ot.DataTypeRepresentation.TYPE)
        self.assertEqual(bool_attr, og.Type(og.BaseDataType.BOOL))
        bool_py = ot.convert_type("bool", ot.DataTypeRepresentation.OGN, ot.DataTypeRepresentation.PYTHON)
        self.assertEqual(bool_py, ot.bool)
        self.assertEqual(bool_py, ot.boolean)
        bool_ogn = ot.convert_type(
            Sdf.ValueTypeNames.Bool, ot.DataTypeRepresentation.SDF, ot.DataTypeRepresentation.OGN
        )
        self.assertEqual(bool_ogn, "bool")

        # Scan the list of referenced types of each representation to find which ones have no representations and
        # which ones have multiple representations, both of which should result in an error.
        test_list = _test_data()
        # Scan the list of referenced types of each representation to find which ones have no representations and
        # which ones have multiple representations, both of which should result in an error.
        ogn_counts = {}
        sdf_counts = {}
        py_counts = {}
        attr_counts = {}
        for ogn_type, sdf_type, py_type, attr_type in test_list:
            ogn_counts[ogn_type] = ogn_counts.get(ogn_type, 0) + 1
            if sdf_type is not None:
                sdf_counts[sdf_type] = sdf_counts.get(sdf_type, 0) + 1
            if py_type is not None:
                # Equivalence of multiple types is tested above so using just one is sufficient
                if isinstance(py_type, list):
                    py_type = py_type[0]
                py_counts[py_type] = py_counts.get(py_type, 0) + 1
            if attr_type is not None:
                attr_counts[attr_type] = attr_counts.get(attr_type, 0) + 1
        type_counts = [ogn_counts, sdf_counts, py_counts, attr_counts]
        representation_count = len(test_list[0])

        def _test_conversion(
            src_type: str | Sdf.ValueTypeNames | type | og.Type,
            dst_type: str | Sdf.ValueTypeNames | type | og.Type,
            src_rep: ot.DataTypeRepresentation,
            dst_rep: ot.DataTypeRepresentation,
            message: str,
        ):
            """Check that the conversion of the source type name in the source representation matches the expected
            destination type name in the destination representation. If the mappings are indeterminate, either because
            the available destinations are empty or have multiple results, then check that an exception is raised.
            """
            if src_type is None:
                return
            if type_counts[src_rep.value][src_type] != 1 or dst_type is None:
                with self.assertRaises(ogn.DataTypeError, msg=f"Testing unmapped source {src_type}"):
                    ot.convert_type(src_type, src_rep, dst_rep)
            else:
                self.assertEqual(
                    dst_type,
                    ot.convert_type(src_type, src_rep, dst_rep),
                    f"{message} converting {src_rep} to {dst_rep}",
                )

        for test_number, test_data in enumerate(test_list):
            test_id = f"Test {test_number} with {test_data}"

            # Walk the type list in two levels to get all pairs of conversion types, including with themselves
            for source_rep in range(representation_count):
                source_type = test_data[source_rep]
                source_enum = ot.DataTypeRepresentation(source_rep)
                for dest_rep in range(source_rep, representation_count):
                    dest_type = test_data[dest_rep]
                    dest_enum = ot.DataTypeRepresentation(dest_rep)
                    # Check the forward conversion (e.g. OGN->SDF)
                    for single_source in source_type if isinstance(source_type, list) else [source_type]:
                        for single_dest in dest_type if isinstance(dest_type, list) else [dest_type]:
                            _test_conversion(single_source, single_dest, source_enum, dest_enum, test_id)
                            # Check the reverse conversion (e.g. SDF->OGN) if they are different
                            if source_rep != dest_rep:
                                _test_conversion(single_dest, single_source, dest_enum, source_enum, test_id)
