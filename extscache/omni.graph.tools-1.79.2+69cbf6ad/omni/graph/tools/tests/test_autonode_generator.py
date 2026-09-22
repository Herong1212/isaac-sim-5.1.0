"""Low level testing for the autonode_generator functionality"""

import ast
import json
import logging
import pprint
from typing import Iterable

import omni.graph.tools._impl.autonode_generator.ogn_types as ogdt
import omni.kit.test
from omni.graph.tools._impl.autonode_generator.compiler import _generate_autonode_calls as generate_autonode_calls
from omni.graph.tools._impl.autonode_generator.compiler import _scan_for_decorated_objects as scan_for_decorated_objects
from omni.graph.tools._impl.autonode_generator.compiler import _unpack_args as unpack_args
from omni.graph.tools._impl.autonode_generator.compiler import _unpack_call as unpack_call
from omni.graph.tools._impl.autonode_generator.compiler import _unpack_classdef_functions as unpack_classdef_functions
from omni.graph.tools._impl.autonode_generator.compiler import _unpack_classdef_members as unpack_classdef_members
from omni.graph.tools._impl.autonode_generator.compiler import _unpack_decorators as unpack_decorators
from omni.graph.tools._impl.autonode_generator.compiler import _unpack_expression as unpack_expression
from omni.graph.tools._impl.autonode_generator.compiler import _unpack_subscript_type as unpack_subscript_type
from omni.graph.tools._impl.autonode_generator.compiler import _unpack_type_annotation as unpack_type_annotation
from omni.graph.tools._impl.autonode_generator.function import NodeTypeFromFunctionScan
from omni.graph.tools._impl.autonode_generator.utils import (
    NO_ANNOTATION,
    GeneratedCode,
    as_class_name,
    is_class_private,
    is_dunder,
    is_private,
    python_name_to_ui_name,
)


# ==============================================================================================================
class TestAutoNodeGenerator(omni.kit.test.AsyncTestCase):
    async def test_utils(self):
        """Test the basic low level utilities"""
        class_name_tests = [
            ("snake_case_name", "SnakeCaseName"),
            ("Module", "Module"),
            ("NoChanges", "NoChanges"),
            ("omni.my.module", "OmniMyModule"),
            ("omni.my.module.my_function", "OmniMyModuleMyFunction"),
            ("omni.my.module.MyClass", "OmniMyModuleMyClass"),
        ]
        for name, sanitized_name in class_name_tests:
            self.assertEqual(sanitized_name, as_class_name(name))

        python_ui_name_tests = [
            ("Unchanged Name", "Unchanged Name"),
            ("snake_case_name", "Snake Case Name"),
            ("snake_case name", "Snake Case name"),
            ("USD_in_snake_case", "USD In Snake Case"),
        ]
        for name, ui_name in python_ui_name_tests:
            self.assertEqual(ui_name, python_name_to_ui_name(name))

        private_tests = [
            ("x", False),
            ("simple", False),
            ("_", False),
            ("__", True),
            ("suffix_", False),
            ("_private", True),
            ("__super_private", True),
            ("not_private", False),
        ]
        for name, expected_private in private_tests:
            self.assertEqual(expected_private, is_private(name), f"Private test failed for {name}")

        class_private_tests = [
            ("x", False),
            ("simple", False),
            ("_", False),
            ("__", False),
            ("suffix_", False),
            ("suffix__", False),
            ("_private", False),
            ("__super_private", True),
            ("__internal__", False),
            ("not_private", False),
        ]
        for name, expected_private in class_private_tests:
            self.assertEqual(expected_private, is_class_private(name), f"Class private test failed for {name}")

        dunder_tests = [
            ("x", False),
            ("simple", False),
            ("suffix_", False),
            ("suffix__", False),
            ("____", False),
            ("__x__", True),
            ("_private", False),
            ("__super_private", False),
            ("__internal__", True),
            ("not_private", False),
        ]
        for name, expected_private in dunder_tests:
            self.assertEqual(expected_private, is_dunder(name), f"Dunder test failed for {name}")

        gen = GeneratedCode()
        gen.line("Hello")
        with gen.indent("if True:"):
            with gen.indent("if True:"):
                gen.block("World")
        self.assertEqual(
            repr(gen),
            """Hello
if True:
    if True:
        World
""",
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_unpack_type_annotation(self):
        """Test compiler._unpack_type_annotation"""
        ast_tree = ast.parse(
            """
a: int = 5
b: tuple[int] = (1, a, 3)
c = a + b[1]
d: og.typing.Float3
"""
        )
        a, b, c, d = ast_tree.body
        ast_name = a.target
        self.assertEqual("a", unpack_type_annotation(ast_name))
        self.assertTrue(isinstance(ast_name, ast.Name))

        ast_constant = a.value
        self.assertTrue(isinstance(ast_constant, ast.Constant))
        self.assertEqual(5, unpack_type_annotation(ast_constant))

        ast_tuple = b.value
        self.assertTrue(isinstance(ast_tuple, ast.Tuple))
        self.assertEqual((1, "a", 3), unpack_type_annotation(ast_tuple))

        ast_binop = c.value
        self.assertTrue(isinstance(ast_binop, ast.BinOp))
        self.assertEqual(["a", {"value": "b", "contents": 1}], unpack_type_annotation(ast_binop))

        ast_subscript = c.value.right
        self.assertTrue(isinstance(ast_subscript, ast.Subscript))
        self.assertEqual({"value": "b", "contents": 1}, unpack_type_annotation(ast_subscript))

        ast_attribute = d.annotation
        self.assertTrue(isinstance(ast_attribute, ast.Attribute))
        self.assertEqual("og.typing.Float3", unpack_type_annotation(ast_attribute))

    # --------------------------------------------------------------------------------------------------------------
    async def test_unpack_subscript_type(self):
        """Test compiler._unpack_subscript_type"""
        ast_tree = ast.parse(
            """
a = [1, 2, 3]
a[1]
"""
        )
        ast_subscript = ast_tree.body[1].value
        self.assertTrue(isinstance(ast_subscript, ast.Subscript))
        self.assertEqual({"value": "a", "contents": 1}, unpack_subscript_type(ast_subscript))

    # --------------------------------------------------------------------------------------------------------------
    async def test_unpack_args(self):
        """Test compiler._unpack_args"""
        ast_tree = ast.parse(
            """
def f(p, /, a: int, b: float, c: float, *, d: str, f: int=3) -> "return annotation":
    pass
"""
        )
        ast_arguments = ast_tree.body[0].args
        self.assertTrue(isinstance(ast_arguments, ast.arguments))
        self.assertEqual(
            {"p": NO_ANNOTATION, "a": "int", "b": "float", "c": "float", "d": "str", "f": "int"},
            unpack_args(ast_arguments),
        )

        # Check that invalid varargs is caught
        ast_tree = ast.parse(
            """
def f(*args):
    pass
"""
        )
        with self.assertRaises(ValueError):
            unpack_args(ast_tree.body[0].args)

        # Check that invalid kwargs is caught
        ast_tree = ast.parse(
            """
def f(**kwargs):
    pass
"""
        )
        with self.assertRaises(ValueError):
            unpack_args(ast_tree.body[0].args)

    # --------------------------------------------------------------------------------------------------------------
    async def test_unpack_expression(self):
        """Test compiler._unpack_expression"""
        ast_expression = ast.parse("5", mode="eval")
        self.assertTrue(isinstance(ast_expression, ast.Expression))
        self.assertEqual(5, unpack_expression(ast_expression))

    # --------------------------------------------------------------------------------------------------------------
    async def test_unpack_call(self):
        """Test compiler._unpack_call"""
        ast_tree = ast.parse(
            """
my_function(a, b, c=5)
"""
        )
        ast_call = ast_tree.body[0].value
        self.assertTrue(isinstance(ast_call, ast.Call))
        self.assertEqual({"name": "my_function", "call_args": ["a", "b"], "call_kws": {"c": 5}}, unpack_call(ast_call))

    # --------------------------------------------------------------------------------------------------------------
    async def test_unpack_decorators(self):
        """Test compiler._unpack_decorators"""
        ast_tree = ast.parse(
            """
@og.ab.OmniGraphNode
@SimpleDeco(3, a=5)
def my_decorated_function(a, b, c=5):
    pass
"""
        )
        ast_decorator = ast_tree.body[0].decorator_list
        self.assertTrue(isinstance(ast_decorator, Iterable))
        self.assertEqual(
            [{"name": "og.ab.OmniGraphNode"}, {"name": "SimpleDeco", "arguments": [3], "keywords": {"a": 5}}],
            unpack_decorators(ast_decorator),
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_unpack_classdef_functions(self):
        """Test compiler._unpack_classdef_functions"""
        ast_tree = ast.parse(
            """
class MyClass(MyBase):
    CLASS_CONSTANT: int = 0
    def my_function(self) -> og.Float3:
        pass
    def _internal_function(self):
        pass
    def my_other_function(self) -> int:
        pass
"""
        )
        ast_classdef = ast_tree.body[0]
        self.assertTrue(isinstance(ast_classdef, ast.ClassDef))
        self.assertEqual(
            [
                {"arguments": {"self": NO_ANNOTATION}, "name": "my_function", "return_annotation": "og.Float3"},
                {"arguments": {"self": NO_ANNOTATION}, "name": "my_other_function", "return_annotation": "int"},
            ],
            unpack_classdef_functions(ast_classdef),
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_unpack_classdef_members(self):
        """Test compiler._unpack_classdef_members"""
        ast_tree = ast.parse(
            """
class MyClass(MyBase):
    CLASS_CONSTANT: int = 0
    _HIDDEN_CLASS_CONSTANT: int = 0
    def my_function(self):
        pass
    def _internal_function(self):
        pass
    def my_other_function(self):
        pass
"""
        )
        ast_classdef = ast_tree.body[0]
        self.assertTrue(isinstance(ast_classdef, ast.ClassDef))
        self.assertEqual(
            [{"name": "CLASS_CONSTANT", "annotation": "int", "value": 0}], unpack_classdef_members(ast_classdef)
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_scan_for_decorated_objects(self):
        """Test compiler._scan_for_decorated_objects"""
        definition = """
def normal_function():
    pass
@SomeDecorator
def decorated_function(a: int) -> og.Float3:
    '''This is a decorated function'''
    return a * 2.0
class NormalClass:
    pass
@og.node_typeClass
class DecoratedClass(MyBase):
    '''This is a decorated class'''
    CLASS_CONSTANT: int = 0
    _HIDDEN_CLASS_CONSTANT: int = 0
    def my_function(self) -> float:
        pass
    def _internal_function(self):
        pass
    def my_other_function(self) -> int:
        pass
"""
        func1, func2, class1, class2 = ast.parse(definition).body
        self.assertTrue(isinstance(func1, ast.FunctionDef))
        self.assertTrue(isinstance(func2, ast.FunctionDef))
        self.assertTrue(isinstance(class1, ast.ClassDef))
        self.assertTrue(isinstance(class2, ast.ClassDef))

        decorated_functions, decorated_classes = scan_for_decorated_objects(definition, "/some/file/path")
        self.assertEqual(
            decorated_functions,
            [
                {
                    "name": "decorated_function",
                    "decorators": [{"name": "SomeDecorator"}],
                    "return_annotation": "og.Float3",
                    "parameters": {"a": "int"},
                    "docstring": "This is a decorated function",
                }
            ],
        )
        self.assertEqual(
            decorated_classes,
            [
                {
                    "name": "DecoratedClass",
                    "decorators": [{"name": "og.node_typeClass"}],
                    "functions": [
                        {"arguments": {"self": NO_ANNOTATION}, "name": "my_function", "return_annotation": "float"},
                        {"arguments": {"self": NO_ANNOTATION}, "name": "my_other_function", "return_annotation": "int"},
                    ],
                    "members": [{"name": "CLASS_CONSTANT", "annotation": "int", "value": 0}],
                    "docstring": "This is a decorated class",
                }
            ],
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_type_signatures(self):
        """Test function.NodeTypeFromFunctionScan.get_type_signature conversions"""
        ogn_types_expected = [
            (ogdt.Any, "any"),
            (ogdt.Bool, "bool"),
            (ogdt.BoolArray, "bool[]"),
            (ogdt.Bundle, "bundle"),
            (ogdt.Color3d, "colord[3]"),
            (ogdt.Color3f, "colorf[3]"),
            (ogdt.Color3h, "colorh[3]"),
            (ogdt.Color4d, "colord[4]"),
            (ogdt.Color4f, "colorf[4]"),
            (ogdt.Color4h, "colorh[4]"),
            (ogdt.Color3dArray, "colord[3][]"),
            (ogdt.Color3fArray, "colorf[3][]"),
            (ogdt.Color3hArray, "colorh[3][]"),
            (ogdt.Color4dArray, "colord[4][]"),
            (ogdt.Color4fArray, "colorf[4][]"),
            (ogdt.Color4hArray, "colorh[4][]"),
            (ogdt.Double, "double"),
            (ogdt.Double2, "double[2]"),
            (ogdt.Double3, "double[3]"),
            (ogdt.Double4, "double[4]"),
            (ogdt.DoubleArray, "double[]"),
            (ogdt.Double2Array, "double[2][]"),
            (ogdt.Double3Array, "double[3][]"),
            (ogdt.Double4Array, "double[4][]"),
            (ogdt.Execution, "execution"),
            (ogdt.Float, "float"),
            (ogdt.Float2, "float[2]"),
            (ogdt.Float3, "float[3]"),
            (ogdt.Float4, "float[4]"),
            (ogdt.FloatArray, "float[]"),
            (ogdt.Float2Array, "float[2][]"),
            (ogdt.Float3Array, "float[3][]"),
            (ogdt.Float4Array, "float[4][]"),
            (ogdt.Frame, "frame[4]"),
            (ogdt.FrameArray, "frame[4][]"),
            (ogdt.Half, "half"),
            (ogdt.Half2, "half[2]"),
            (ogdt.Half3, "half[3]"),
            (ogdt.Half4, "half[4]"),
            (ogdt.HalfArray, "half[]"),
            (ogdt.Half2Array, "half[2][]"),
            (ogdt.Half3Array, "half[3][]"),
            (ogdt.Half4Array, "half[4][]"),
            (ogdt.Int, "int"),
            (ogdt.Int2, "int[2]"),
            (ogdt.Int3, "int[3]"),
            (ogdt.Int4, "int[4]"),
            (ogdt.IntArray, "int[]"),
            (ogdt.Int2Array, "int[2][]"),
            (ogdt.Int3Array, "int[3][]"),
            (ogdt.Int4Array, "int[4][]"),
            (ogdt.Int64, "int64"),
            (ogdt.Int64Array, "int64[]"),
            (ogdt.ObjectId, "objectId"),
            (ogdt.ObjectIdArray, "objectId[]"),
            (ogdt.Matrix2d, "matrixd[2]"),
            (ogdt.Matrix3d, "matrixd[3]"),
            (ogdt.Matrix4d, "matrixd[4]"),
            (ogdt.Matrix2dArray, "matrixd[2][]"),
            (ogdt.Matrix3dArray, "matrixd[3][]"),
            (ogdt.Matrix4dArray, "matrixd[4][]"),
            (ogdt.Normal3d, "normald[3]"),
            (ogdt.Normal3f, "normalf[3]"),
            (ogdt.Normal3h, "normalh[3]"),
            (ogdt.Normal3dArray, "normald[3][]"),
            (ogdt.Normal3fArray, "normalf[3][]"),
            (ogdt.Normal3hArray, "normalh[3][]"),
            (ogdt.Path, "path"),
            (ogdt.Point3d, "pointd[3]"),
            (ogdt.Point3f, "pointf[3]"),
            (ogdt.Point3h, "pointh[3]"),
            (ogdt.Point3dArray, "pointd[3][]"),
            (ogdt.Point3fArray, "pointf[3][]"),
            (ogdt.Point3hArray, "pointh[3][]"),
            (ogdt.Quatd, "quatd[4]"),
            (ogdt.Quatf, "quatf[4]"),
            (ogdt.Quath, "quath[4]"),
            (ogdt.QuatdArray, "quatd[4][]"),
            (ogdt.QuatfArray, "quatf[4][]"),
            (ogdt.QuathArray, "quath[4][]"),
            (ogdt.String, "string"),
            (ogdt.Target, "target"),
            (ogdt.TexCoord2d, "texcoordd[2]"),
            (ogdt.TexCoord2f, "texcoordf[2]"),
            (ogdt.TexCoord2h, "texcoordh[2]"),
            (ogdt.TexCoord3d, "texcoordd[3]"),
            (ogdt.TexCoord3f, "texcoordf[3]"),
            (ogdt.TexCoord3h, "texcoordh[3]"),
            (ogdt.TexCoord2dArray, "texcoordd[2][]"),
            (ogdt.TexCoord2fArray, "texcoordf[2][]"),
            (ogdt.TexCoord2hArray, "texcoordh[2][]"),
            (ogdt.TexCoord3dArray, "texcoordd[3][]"),
            (ogdt.TexCoord3fArray, "texcoordf[3][]"),
            (ogdt.TexCoord3hArray, "texcoordh[3][]"),
            (ogdt.Timecode, "timecode"),
            (ogdt.TimecodeArray, "timecode[]"),
            (ogdt.Token, "token"),
            (ogdt.TokenArray, "token[]"),
            (ogdt.UChar, "uchar"),
            (ogdt.UInt, "uint"),
            (ogdt.UInt64, "uint64"),
            (ogdt.UCharArray, "uchar[]"),
            (ogdt.UIntArray, "uint[]"),
            (ogdt.UInt64Array, "uint64[]"),
            (ogdt.Vector3d, "vectord[3]"),
            (ogdt.Vector3f, "vectorf[3]"),
            (ogdt.Vector3h, "vectorh[3]"),
            (ogdt.Vector3dArray, "vectord[3][]"),
            (ogdt.Vector3fArray, "vectorf[3][]"),
            (ogdt.Vector3hArray, "vectorh[3][]"),
        ]

        for type_def, ogn_type_name in ogn_types_expected:
            actual_type = NodeTypeFromFunctionScan.get_type_signature(type_def, "Test Attribute")
            self.assertEqual(actual_type["type"], ogn_type_name, f"Looking for type {type_def}")

    # --------------------------------------------------------------------------------------------------------------
    async def test_generate_autonode_calls(self):  # pragma: no cover    Unsupported code
        """Test compiler._generate_autonode_calls"""
        code = """
@og.create_node_type
def add_two_floats(a: ogdt.Float, b: ogdt.Float) -> ogdt.Float:
    '''Set the output to the sum of a and b'''
    return a + b
"""
        result = generate_autonode_calls(code, None, "module.name", "module/name", None)
        logger = logging.getLogger("AutoNode")
        if logger.level == logging.DEBUG:
            for class_name, ogn_content, python_code in result:
                logger.debug("Generation of %s", class_name)
                logger.debug(json.dumps(json.loads(ogn_content), indent=4))
                logger.debug(pprint.pformat(python_code, indent=4, width=200))
        for class_name, ogn_content, python_code in result:
            self.assertEqual(class_name, "AddTwoFloats")
            self.assertTrue(python_code.find("compute") > 0)
            ogn_data = json.loads(ogn_content)["add_two_floats"]
            self.assertEqual(ogn_data["language"], "Python")
            self.assertCountEqual(["__an_function_name__", "a", "b"], list(ogn_data["inputs"].keys()))
            self.assertEqual(["out_0"], list(ogn_data["outputs"].keys()))

        code = """
@og.create_node_type(add_execution_pins=True)
def add_two_floats(a: ogdt.Float, b: ogdt.Float) -> ogdt.Float:
    '''Set the output to the sum of a and b'''
    return a + b
"""
        result = generate_autonode_calls(code, None, "module.name", "module/name", None)
        logger = logging.getLogger("AutoNode")
        if logger.level == logging.DEBUG:
            for class_name, ogn_content, python_code in result:
                logger.debug("Generation of %s", class_name)
                logger.debug(json.dumps(json.loads(ogn_content), indent=4))
                logger.debug(pprint.pformat(python_code, indent=4, width=200))
        for class_name, ogn_content, python_code in result:
            self.assertEqual(class_name, "AddTwoFloats")
            self.assertTrue(python_code.find("compute") > 0)
            ogn_data = json.loads(ogn_content)["add_two_floats"]
            self.assertEqual(ogn_data["language"], "Python")
            self.assertCountEqual(["__an_function_name__", "a", "b", "exec"], list(ogn_data["inputs"].keys()))
            self.assertCountEqual(["out_0", "exec"], list(ogn_data["outputs"].keys()))

    # --------------------------------------------------------------------------------------------------------------
    async def test_generate_on_all_types(self):
        """Test compiler._generate_autonode_calls with all legal data types"""
        logger = logging.getLogger("AutoNode")
        for data_type in ogdt.ALL_OGN_DATA_TYPES:
            code = f"""
@og.create_node_type
def pass_through(a: ogdt.{data_type.__name__}) -> ogdt.{data_type.__name__}:
    '''Set the output to the input'''
    return a
"""
            result = generate_autonode_calls(code, None, "module.name", "module/name", None)
            for class_name, ogn_content, python_code in result:
                self.assertEqual(class_name, "PassThrough", f"Generating test for type {data_type}")
                self.assertTrue(python_code.find("compute") > 0)
                if logger.level == logging.DEBUG:
                    logger.debug("Generation of %s", class_name)
                    logger.debug(json.dumps(json.loads(ogn_content), indent=4))
                    logger.debug(pprint.pformat(python_code, indent=4, width=200))

                ogn_data = json.loads(ogn_content)["pass_through"]
                self.assertEqual(ogn_data["language"], "Python")
                self.assertCountEqual(["__an_function_name__", "a"], list(ogn_data["inputs"].keys()))
                self.assertEqual(["out_0"], list(ogn_data["outputs"].keys()))
                ogn_type = ogdt.TypeConversion.from_type(data_type).ogn_type
                self.assertEqual(ogn_data["inputs"]["a"]["type"], ogn_type)
                self.assertEqual(ogn_data["outputs"]["out_0"]["type"], ogn_type)
                with self.assertRaises(ValueError):
                    ogdt.TypeConversion.from_type("notAType")
