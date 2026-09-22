"""Testing the type name conversion utility"""

import json
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import omni.graph.tools.ogn as ogn
import omni.kit
from omni.graph.tools._impl.repo_tools.generate_type_name_conversions import generate_type_name_conversions


# Comprehensive list of type name conversions available as a a list of (OGN, USD, SDF, CPP, PYTHON, PYTHON_ANNOTATION)
# so that forward and reverse conversion checks can be made.
def _atype(dtype: str, tuple_count: int | str = 1, is_array: bool = True) -> str:
    """Helper to make generation of array return types small"""
    if is_array:
        shape = "N," if tuple_count == 1 else f"N,{tuple_count}"
    elif isinstance(tuple_count, int):
        shape = f"{tuple_count},"
    else:
        shape = tuple_count
    return f"numpy.ndarray(shape=({shape}), dtype={dtype})"


_SIMPLE = "ogn::SimpleInput"
_ARRAY = "ogn::ArrayInput"
TEST_DATA = [
    ["any", "token", None, _SIMPLE, "any", "any"],
    ["bool", "bool", "Bool", _SIMPLE, "bool", "bool"],
    ["bool[]", "bool[]", "BoolArray", _ARRAY, _atype("numpy.bool"), "boolarray"],
    ["bundle", None, None, "ogn::BundleAttribute", "omni.graph.core.BundleContents", "bundle"],
    ["colord[3]", "color3d", "Color3d", _SIMPLE, _atype("numpy.float64", 3, False), "color3d"],
    ["colord[3][]", "color3d[]", "Color3dArray", _ARRAY, _atype("numpy.float64", 3), "color3darray"],
    ["colord[4]", "color4d", "Color4d", _SIMPLE, _atype("numpy.float64", 4, False), "color4d"],
    ["colord[4][]", "color4d[]", "Color4dArray", _ARRAY, _atype("numpy.float64", 4), "color4darray"],
    ["colorf[3]", "color3f", "Color3f", _SIMPLE, _atype("numpy.float32", 3, False), "color3f"],
    ["colorf[3][]", "color3f[]", "Color3fArray", _ARRAY, _atype("numpy.float32", 3), "color3farray"],
    ["colorf[4]", "color4f", "Color4f", _SIMPLE, _atype("numpy.float32", 4, False), "color4f"],
    ["colorf[4][]", "color4f[]", "Color4fArray", _ARRAY, _atype("numpy.float32", 4), "color4farray"],
    ["colorh[3]", "color3h", "Color3h", _SIMPLE, _atype("numpy.float16", 3, False), "color3h"],
    ["colorh[3][]", "color3h[]", "Color3hArray", _ARRAY, _atype("numpy.float16", 3), "color3harray"],
    ["colorh[4]", "color4h", "Color4h", _SIMPLE, _atype("numpy.float16", 4, False), "color4h"],
    ["colorh[4][]", "color4h[]", "Color4hArray", _ARRAY, _atype("numpy.float16", 4), "color4harray"],
    ["double", "double", "Double", _SIMPLE, "float", "double"],
    ["double[]", "double[]", "DoubleArray", _ARRAY, _atype("numpy.float64"), "doublearray"],
    ["double[2]", "double2", "Double2", _SIMPLE, _atype("numpy.float64", 2, False), "double2"],
    ["double[2][]", "double2[]", "Double2Array", _ARRAY, _atype("numpy.float64", 2), "double2array"],
    ["double[3]", "double3", "Double3", _SIMPLE, _atype("numpy.float64", 3, False), "double3"],
    ["double[3][]", "double3[]", "Double3Array", _ARRAY, _atype("numpy.float64", 3), "double3array"],
    ["double[4]", "double4", "Double4", _SIMPLE, _atype("numpy.float64", 4, False), "double4"],
    ["double[4][]", "double4[]", "Double4Array", _ARRAY, _atype("numpy.float64", 4), "double4array"],
    ["execution", "execution", None, _SIMPLE, "int", "execution"],
    ["float", "float", "Float", _SIMPLE, "float", "float"],
    ["float[]", "float[]", "FloatArray", _ARRAY, _atype("numpy.float32"), "floatarray"],
    ["float[2]", "float2", "Float2", _SIMPLE, _atype("numpy.float32", 2, False), "float2"],
    ["float[2][]", "float2[]", "Float2Array", _ARRAY, _atype("numpy.float32", 2), "float2array"],
    ["float[3]", "float3", "Float3", _SIMPLE, _atype("numpy.float32", 3, False), "float3"],
    ["float[3][]", "float3[]", "Float3Array", _ARRAY, _atype("numpy.float32", 3), "float3array"],
    ["float[4]", "float4", "Float4", _SIMPLE, _atype("numpy.float32", 4, False), "float4"],
    ["float[4][]", "float4[]", "Float4Array", _ARRAY, _atype("numpy.float32", 4), "float4array"],
    ["frame[4]", "frame4d", "Frame4d", _SIMPLE, _atype("numpy.float64", "4,4", False), "frame4d"],
    ["frame[4][]", "frame4d[]", "Frame4dArray", _ARRAY, _atype("numpy.float64", "4,4"), "frame4darray"],
    ["half", "half", "Half", _SIMPLE, "float", "half"],
    ["half[]", "half[]", "HalfArray", _ARRAY, _atype("numpy.float16"), "halfarray"],
    ["half[2]", "half2", "Half2", _SIMPLE, _atype("numpy.float16", 2, False), "half2"],
    ["half[2][]", "half2[]", "Half2Array", _ARRAY, _atype("numpy.float16", 2), "half2array"],
    ["half[3]", "half3", "Half3", _SIMPLE, _atype("numpy.float16", 3, False), "half3"],
    ["half[3][]", "half3[]", "Half3Array", _ARRAY, _atype("numpy.float16", 3), "half3array"],
    ["half[4]", "half4", "Half4", _SIMPLE, _atype("numpy.float16", 4, False), "half4"],
    ["half[4][]", "half4[]", "Half4Array", _ARRAY, _atype("numpy.float16", 4), "half4array"],
    ["int", "int", "Int", _SIMPLE, "int", "int"],
    ["int[]", "int[]", "IntArray", _ARRAY, _atype("numpy.int32"), "intarray"],
    ["int[2]", "int2", "Int2", _SIMPLE, _atype("numpy.int32", 2, False), "int2"],
    ["int[2][]", "int2[]", "Int2Array", _ARRAY, _atype("numpy.int32", 2), "int2array"],
    ["int[3]", "int3", "Int3", _SIMPLE, _atype("numpy.int32", 3, False), "int3"],
    ["int[3][]", "int3[]", "Int3Array", _ARRAY, _atype("numpy.int32", 3), "int3array"],
    ["int[4]", "int4", "Int4", _SIMPLE, _atype("numpy.int32", 4, False), "int4"],
    ["int[4][]", "int4[]", "Int4Array", _ARRAY, _atype("numpy.int32", 4), "int4array"],
    ["int64", "int64", "Int64", _SIMPLE, "int", "int64"],
    ["int64[]", "int64[]", "Int64Array", _ARRAY, _atype("numpy.int64"), "int64array"],
    ["matrixd[2]", "matrix2d", "Matrix2d", _SIMPLE, _atype("numpy.float64", "2,2", False), "matrix2d"],
    ["matrixd[2][]", "matrix2d[]", "Matrix2dArray", _ARRAY, _atype("numpy.float64", "2,2"), "matrix2darray"],
    ["matrixd[3]", "matrix3d", "Matrix3d", _SIMPLE, _atype("numpy.float64", "3,3", False), "matrix3d"],
    ["matrixd[3][]", "matrix3d[]", "Matrix3dArray", _ARRAY, _atype("numpy.float64", "3,3"), "matrix3darray"],
    ["matrixd[4]", "matrix4d", "Matrix4d", _SIMPLE, _atype("numpy.float64", "4,4", False), "matrix4d"],
    ["matrixd[4][]", "matrix4d[]", "Matrix4dArray", _ARRAY, _atype("numpy.float64", "4,4"), "matrix4darray"],
    ["normald[3]", "normal3d", "Normal3d", _SIMPLE, _atype("numpy.float64", 3, False), "normal3d"],
    ["normald[3][]", "normal3d[]", "Normal3dArray", _ARRAY, _atype("numpy.float64", 3), "normal3darray"],
    ["normalf[3]", "normal3f", "Normal3f", _SIMPLE, _atype("numpy.float32", 3, False), "normal3f"],
    ["normalf[3][]", "normal3f[]", "Normal3fArray", _ARRAY, _atype("numpy.float32", 3), "normal3farray"],
    ["normalh[3]", "normal3h", "Normal3h", _SIMPLE, _atype("numpy.float16", 3, False), "normal3h"],
    ["normalh[3][]", "normal3h[]", "Normal3hArray", _ARRAY, _atype("numpy.float16", 3), "normal3harray"],
    ["objectId", "uint64", None, _SIMPLE, "int", "objectid"],
    ["objectId[]", "uint64[]", None, _ARRAY, _atype("numpy.uint64"), "objectidarray"],
    ["pointd[3]", "point3d", "Point3d", _SIMPLE, _atype("numpy.float64", 3, False), "point3d"],
    ["pointd[3][]", "point3d[]", "Point3dArray", _ARRAY, _atype("numpy.float64", 3), "point3darray"],
    ["pointf[3]", "point3f", "Point3f", _SIMPLE, _atype("numpy.float32", 3, False), "point3f"],
    ["pointf[3][]", "point3f[]", "Point3fArray", _ARRAY, _atype("numpy.float32", 3), "point3farray"],
    ["pointh[3]", "point3h", "Point3h", _SIMPLE, _atype("numpy.float16", 3, False), "point3h"],
    ["pointh[3][]", "point3h[]", "Point3hArray", _ARRAY, _atype("numpy.float16", 3), "point3harray"],
    ["quatd[4]", "quatd", "Quatd", _SIMPLE, _atype("numpy.float64", 4, False), "quatd"],
    ["quatd[4][]", "quatd[]", "QuatdArray", _ARRAY, _atype("numpy.float64", 4), "quatdarray"],
    ["quatf[4]", "quatf", "Quatf", _SIMPLE, _atype("numpy.float32", 4, False), "quatf"],
    ["quatf[4][]", "quatf[]", "QuatfArray", _ARRAY, _atype("numpy.float32", 4), "quatfarray"],
    ["quath[4]", "quath", "Quath", _SIMPLE, _atype("numpy.float16", 4, False), "quath"],
    ["quath[4][]", "quath[]", "QuathArray", _ARRAY, _atype("numpy.float16", 4), "quatharray"],
    ["string", "string", "String", _ARRAY, "str", "string"],
    ["target", None, None, _ARRAY, "list[usdrt::SdfPath]", "target"],
    ["texcoordd[2]", "texCoord2d", "TexCoord2d", _SIMPLE, _atype("numpy.float64", 2, False), "texcoord2d"],
    ["texcoordd[2][]", "texCoord2d[]", "TexCoord2dArray", _ARRAY, _atype("numpy.float64", 2), "texcoord2darray"],
    ["texcoordd[3]", "texCoord3d", "TexCoord3d", _SIMPLE, _atype("numpy.float64", 3, False), "texcoord3d"],
    ["texcoordd[3][]", "texCoord3d[]", "TexCoord3dArray", _ARRAY, _atype("numpy.float64", 3), "texcoord3darray"],
    ["texcoordf[2]", "texCoord2f", "TexCoord2f", _SIMPLE, _atype("numpy.float32", 2, False), "texcoord2f"],
    ["texcoordf[2][]", "texCoord2f[]", "TexCoord2fArray", _ARRAY, _atype("numpy.float32", 2), "texcoord2farray"],
    ["texcoordf[3]", "texCoord3f", "TexCoord3f", _SIMPLE, _atype("numpy.float32", 3, False), "texcoord3f"],
    ["texcoordf[3][]", "texCoord3f[]", "TexCoord3fArray", _ARRAY, _atype("numpy.float32", 3), "texcoord3farray"],
    ["texcoordh[2]", "texCoord2h", "TexCoord2h", _SIMPLE, _atype("numpy.float16", 2, False), "texcoord2h"],
    ["texcoordh[2][]", "texCoord2h[]", "TexCoord2hArray", _ARRAY, _atype("numpy.float16", 2), "texcoord2harray"],
    ["texcoordh[3]", "texCoord3h", "TexCoord3h", _SIMPLE, _atype("numpy.float16", 3, False), "texcoord3h"],
    ["texcoordh[3][]", "texCoord3h[]", "TexCoord3hArray", _ARRAY, _atype("numpy.float16", 3), "texcoord3harray"],
    ["timecode", "timecode", "TimeCode", _SIMPLE, "float", "timecode"],
    ["timecode[]", "timecode[]", "TimeCodeArray", _ARRAY, _atype("numpy.float64"), "timecodearray"],
    ["token", "token", "Token", _SIMPLE, "str", "token"],
    ["token[]", "token[]", "TokenArray", _ARRAY, _atype("numpy.str"), "tokenarray"],
    ["uchar", "uchar", "UChar", _SIMPLE, "int", "uchar"],
    ["uchar[]", "uchar[]", "UCharArray", _ARRAY, _atype("numpy.uint8"), "uchararray"],
    ["uint", "uint", "UInt", _SIMPLE, "int", "uint"],
    ["uint[]", "uint[]", "UIntArray", _ARRAY, _atype("numpy.uint32"), "uintarray"],
    ["uint64", "uint64", "UInt64", _SIMPLE, "int", "uint64"],
    ["uint64[]", "uint64[]", "UInt64Array", _ARRAY, _atype("numpy.uint64"), "uint64array"],
    ["vectord[3]", "vector3d", "Vector3d", _SIMPLE, _atype("numpy.float64", 3, False), "vector3d"],
    ["vectord[3][]", "vector3d[]", "Vector3dArray", _ARRAY, _atype("numpy.float64", 3), "vector3darray"],
    ["vectorf[3]", "vector3f", "Vector3f", _SIMPLE, _atype("numpy.float32", 3, False), "vector3f"],
    ["vectorf[3][]", "vector3f[]", "Vector3fArray", _ARRAY, _atype("numpy.float32", 3), "vector3farray"],
    ["vectorh[3]", "vector3h", "Vector3h", _SIMPLE, _atype("numpy.float16", 3, False), "vector3h"],
    ["vectorh[3][]", "vector3h[]", "Vector3hArray", _ARRAY, _atype("numpy.float16", 3), "vector3harray"],
]
# Add the namespaces, elided above for brevity
for _index, (_ogn_type, _usd_type, _sdf_type, _cpp_type, _py_type, _py_ann_type) in enumerate(TEST_DATA):
    _sdf_type = _sdf_type if _sdf_type is None else f"Sdf.ValueTypeNames.{_sdf_type}"
    _py_ann_type = _py_ann_type if _py_ann_type is None else f"omni.graph.core.types.{_py_ann_type}"
    TEST_DATA[_index] = [_ogn_type, _usd_type, _sdf_type, _cpp_type, _py_type, _py_ann_type]


# ======================================================================
class _TestOgnTypeNameConversions(omni.kit.test.AsyncTestCase):
    async def test_type_name_conversions(self):
        """Do a representative set of type name conversion checks"""
        bool_usd = ogn.convert_type_name("bool", ogn.DataTypeNameRepresentation.OGN, ogn.DataTypeNameRepresentation.USD)
        self.assertEqual(bool_usd, "bool")
        bool_ogn = ogn.convert_type_name("bool", ogn.DataTypeNameRepresentation.USD, ogn.DataTypeNameRepresentation.OGN)
        self.assertEqual(bool_ogn, "bool")
        float_ogn = ogn.convert_type_name(
            "float", ogn.DataTypeNameRepresentation.USD, ogn.DataTypeNameRepresentation.OGN
        )
        self.assertEqual(float_ogn, "float")
        with self.assertRaises(ogn.DataTypeError):
            ogn.convert_type_name(
                "nonexistant_type", ogn.DataTypeNameRepresentation.OGN, ogn.DataTypeNameRepresentation.USD
            )
        with self.assertRaises(ogn.DataTypeError):

            class FakeDataTypeNameRepresentation(Enum):
                FAKE = 100

            ogn.convert_type_name("bool", ogn.DataTypeNameRepresentation.OGN, FakeDataTypeNameRepresentation.FAKE)

        # Scan the list of referenced types of each representation to find which ones have no representations and
        # which ones have multiple representations, both of which should result in an error.
        ogn_counts = {}
        usd_counts = {}
        sdf_counts = {}
        cpp_counts = {}
        py_counts = {}
        py_ann_counts = {}
        for ogn_type, usd_type, sdf_type, cpp_type, py_type, py_ann_type in TEST_DATA:
            ogn_counts[ogn_type] = ogn_counts.get(ogn_type, 0) + 1
            if usd_type is not None:
                usd_counts[usd_type] = usd_counts.get(usd_type, 0) + 1
            if sdf_type is not None:
                sdf_counts[sdf_type] = sdf_counts.get(sdf_type, 0) + 1
            if cpp_type is not None:
                cpp_counts[cpp_type] = cpp_counts.get(cpp_type, 0) + 1
            if py_type is not None:
                py_counts[py_type] = py_counts.get(py_type, 0) + 1
            if py_ann_type is not None:
                py_ann_counts[py_ann_type] = py_ann_counts.get(py_ann_type, 0) + 1
        type_counts = [ogn_counts, usd_counts, sdf_counts, cpp_counts, py_counts, py_ann_counts]
        representation_count = len(TEST_DATA[0])

        def _test_conversion(
            src_type: str | None,
            dst_type: str | None,
            src_rep: ogn.DataTypeNameRepresentation,
            dst_rep: ogn.DataTypeNameRepresentation,
            message: str,
        ):
            """Check that the conversion of the source type name in the source representation matches the expected
            destination type name in the destination representation. If the mappings are indeterminate, either because
            the available destinations are empty or have multiple results, then check that an exception is raised.
            """
            if src_type is None:
                return
            if type_counts[src_rep.value][src_type] != 1 or dst_type is None:
                with self.assertRaises(ogn.DataTypeError, msg=f"{test_id} converting {src_rep} to {dst_rep}"):
                    ogn.convert_type_name(src_type, src_rep, dst_rep)
            else:
                self.assertEqual(
                    dst_type,
                    ogn.convert_type_name(src_type, src_rep, dst_rep),
                    f"{test_id} converting {src_rep} to {dst_rep}",
                )

        for test_number, test_data in enumerate(TEST_DATA):
            test_id = f"Test {test_number} with {test_data}"

            # Walk the type list in two levels to get all pairs of conversion types, including with themselves
            for source_rep in range(representation_count):
                source_type = test_data[source_rep]
                source_enum = ogn.DataTypeNameRepresentation(source_rep)
                for dest_rep in range(source_rep, representation_count):
                    dest_type = test_data[dest_rep]
                    # Check the forward conversion (e.g. OGN->USD)
                    _test_conversion(
                        source_type, dest_type, source_enum, ogn.DataTypeNameRepresentation(dest_rep), test_id
                    )
                    if source_rep == dest_rep:
                        continue
                    # Check the reverse conversion (e.g. USD->OGN)
                    _test_conversion(
                        dest_type, source_type, ogn.DataTypeNameRepresentation(dest_rep), source_enum, test_id
                    )

    # --------------------------------------------------------------------------------------------------------------
    async def test_type_name_tool(self):
        """Run tests for the generator tool that creates type name metadata for runtime consumption"""

        with TemporaryDirectory() as tmpdir_fd:
            tmp_dir = Path(tmpdir_fd).resolve()
            json_fd = NamedTemporaryFile(dir=tmp_dir, suffix=".json", delete=False)
            json_fd.close()
            rst_fd = NamedTemporaryFile(dir=tmp_dir, suffix=".rst", delete=False)
            rst_fd.close()

            with self.assertRaises(ValueError):
                generate_type_name_conversions(
                    [
                        "--output-file",
                        json_fd.name,
                        "--docs-module",
                        rst_fd.name,
                        "--log-level",
                        "INVALID_LOG_LEVEL",
                    ]
                )

            generate_type_name_conversions(
                [
                    "--output-file",
                    json_fd.name,
                    "--docs-module",
                    rst_fd.name,
                    "--log-level",
                    "DEBUG",
                ]
            )

            json_file = Path(json_fd.name)
            rst_file = Path(rst_fd.name)
            self.assertTrue(json_file.is_file())
            self.assertTrue(rst_file.is_file())

            with open(json_file, "r", encoding="utf-8") as json_fd:
                json_data = json.load(json_fd)
            self.assertTrue("LEGEND" in json_data)
            self.assertTrue("bundle" in json_data)

            found_bundle = False
            with open(rst_file, "r", encoding="utf-8") as rst_fd:
                for line in rst_fd.readlines():
                    if line.find("omni.graph.core.types.bundle") >= 0:
                        found_bundle = True
                        break
            self.assertTrue(found_bundle)

            json_time = json_file.stat().st_ctime
            rst_time = rst_file.stat().st_ctime

            # Running it twice exercises the shortcut to avoid writing when it exists
            generate_type_name_conversions(
                [
                    "--output-file",
                    json_fd.name,
                    "--docs-module",
                    rst_fd.name,
                    "--log-level",
                    "DEBUG",
                ]
            )

            self.assertEqual(json_time, json_file.stat().st_ctime)
            self.assertEqual(rst_time, rst_file.stat().st_ctime)
