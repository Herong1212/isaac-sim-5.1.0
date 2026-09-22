(omnigraph_autonode)=

# AutoNode - Node Type Definition

  <!--
  _______ ____  _____   ____
 |__   __/ __ \|  __ \ / __ \
    | | | |  | | |  | | |  | |
    | | | |  | | |  | | |  | |
    | | | |__| | |__| | |__| |
    |_|  \____/|_____/ \____/

 The documentation for AutoNode will be filled out once the functionality is all in place as it keeps changing
 during development. The feature is hidden behind a setting and this documentation is only visible in internal
 builds.
 -->

```{warning}
This feature is currently only a prototype. While in development it must be enabled explicitly by defining the Carbonite
setting `/omnigraph/autonode/enabled` as 1, e.g. by using the command line option **"--/omnigraph/autonode/enabled=1"**.
Interfaces, behavior, and documentation for this feature are subject to change without notice.
```

`AutoNode` is the terminology used for the general process of generating node type definitions directly from
Python code. `AutoNode`` enables creation of OmniGraph node type definitions from a simple decorated Python function.
There is no need to create .ogn or .py implementation files.

It turns this:

```{code-block} python
import omni.graph.core as og
import omni.graph.core.types as ot

@og.node_type(add_execution_pins=True)
def dot(vec1: ot.float3, vec2: ot.float3) -> ot.float:
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]
```

Into this:

```{image} images/AutoNodeDotDefinition.png
```

## How it Works

AutoNode generates node signatures by extracting type annotations stored in functions and variables. In order for node
types to be generated, [type annotations](https://docs.python.org/3/library/typing.html) are used in order to relate
Python arguments to their OmniGraph attribute type equivalents.

The OmniGraph type annotations are imported from the module `omni.graph.tools.data_types`. They encompass all of the
legal attribute data type definitions, and are used as build-time identifiers for the data types being used in
AutoNode definitions.

Under the hood, annotation extraction is done with the python ``__annotations__``
([PEP 3107](https://www.python.org/dev/peps/pep-3107/)) dictionary in every class.

### Decorators

``omni.graph.core`` exposes the AutoNode function ``node_type()``, which can be used as a decorator or as
a free function call:

```{code-block} python
import omni.graph.core as og

@og.node_type()
def say_hi() -> str:
    return "hi, everybody!"

def say_hello() -> str:
    return "Hello, World!"
```

#### Wrapping Functions

Here's an example of wrapping a free function:

```{code-block} python
import omni.graph.core as og
import omni.graph.tools.ogn.data_types as ogdt

@og.node_type()
def one_up(input : ogdt.Int = 0) -> ogdt.Token:
    """this documentation will appear in the node's help"""
    return f"one up! {input + 1}"
```

```{important}
The type annotations really matter. Without them, AutoNode can't define node inputs and outputs.
```

You can also create multiple output attributes by making your return type a `tuple`:

```{code-block} python
import omni.graph.core as og
import omni.graph.tools.ogn.data_types as ogdt

@og.node_type()
def break_vector(input : ogdt.Float3) -> tuple[ogdt.Float, ogdt.Float, ogdt.Float]
    return (input[0], input[1], input[2])
```

### Decorator Parameters

#### ``unique_name``

Specifies the full name of the node type definition. If it is not specified then the name will be a combination of
the extension from which it was defined and the function name.

```{code-block} python
import omni.graph.core as og
import MyModule

@og.node_type(module_name="test_module")
def add_one(input: int) -> int:
    return input + 1
```

Will result in a UI displaying access to this node from ``test_module``. If this parameter is not specified then
AutoNode will attempt to infer the name of the module from the location of the definition. For example if the script
lives in `omni/my/extension/autonode/definitions` then the module the node is registered in will be `omni.my.extension`.

```{note}
Anything executed in the script editor or as a standalone file will not have a default module and so one must be
provided or an exception will be raised. The `module_name` value should be such that the node type name is unique.
```

#### ``ui_name``

Specifies the onscreen name of the function.

#### ``categories``

Array of text tags to be added to the node. This is special metadata on the node that can be used to group common
node types together or to provide an easily searchable term.

#### ``metadata``

Other metadata to pass through AutoNode, such as icon information, whether the node should be hidden, or the set of
categories attached to the node.

### Supported Types

This list of types supported by AutoNode corresponds to the list of types supported by OmniGraph.

```{code-block} python
import omni.graph.core as og
import omni.graph.tools.ogn.data_types as ogdt

print(f"List of all data types: {dir(ogdt.ALL_DATA_TYPES)}")

# Generic Vectors
[ogdt.Vector3d, ogdt.Vector3h, ogdt.Vector3f]
# ...and their corresponding array types
[ogdt.Vector3dArray, ogdt.Vector3hArray, ogdt.Vector3fArray]

# Scalar and Vector types
[ogdt.Float, ogdt.Float2, ogdt.Float3, ogdt.Float4]
[ogdt.Half, ogdt.Half2, ogdt.Half3, ogdt.Half4]
[ogdt.Double, ogdt.Double2, ogdt.Double3, ogdt.Double4]
[ogdt.Int, ogdt.Int2, ogdt.Int3, ogdt.Int4]
# ...and their corresponding array types
[ogdt.FloatArray, ogdt.Float2Array, ogdt.Float3Array, ogdt.Float4Array]
[ogdt.HalfArray, ogdt.Half2Array, ogdt.Half3Array, ogdt.Half4Array]
[ogdt.DoubleArray, ogdt.Double2Array, ogdt.Double3Array, ogdt.Double4Array]
[ogdt.IntArray, ogdt.Int2Array, ogdt.Int3Array, ogdt.Int4Array]

# Matrix Types
[ogdt.Matrix2d, ogdt.Matrix3d, ogdt.Matrix4d]
# ...and their corresponding array types
[ogdt.Matrix2dArray, ogdt.Matrix3dArray, ogdt.Matrix4dArray]

# Vector Types with roles
[ogdt.Normal3d, ogdt.Normal3f, ogdt.Normal3h]
[ogdt.Point3d, ogdt.Point3f, ogdt.Point3h]
[ogdt.Quatd, ogdt.Quatf, ogdt.Quath]
[ogdt.TexCoord2d, ogdt.TexCoord2f, ogdt.TexCoord2h]
[ogdt.TexCoord3d, ogdt.TexCoord3f, ogdt.TexCoord3h]
[ogdt.Color3d, ogdt.Color3f, ogdt.Color3h, ogdt.Color4d, ogdt.Color4f, ogdt.Color4h]
# ...and their corresponding array types
[ogdt.Normal3dArray, ogdt.Normal3fArray, ogdt.Normal3hArray]
[ogdt.Point3dArray, ogdt.Point3fArray, ogdt.Point3hArray]
[ogdt.QuatdArray, ogdt.QuatfArray, ogdt.QuathArray]
[ogdt.TexCoord2dArray, ogdt.TexCoord2fArray, ogdt.TexCoord2hArray]
[ogdt.TexCoord3dArray, ogdt.TexCoord3fArray, ogdt.TexCoord3hArray]
[ogdt.Color3dArray, ogdt.Color3fArray, ogdt.Color3hArray, ogdt.Color4dArray, ogdt.Color4fArray, ogdt.Color4hArray]

# Other simple value types
[ogdt.Timecode, ogdt.UInt, ogdt.UChar, ogdt.UInt64, ogdt.Token]
# ... and their corresponding array types
[ogdt.TimecodeArray, ogdt.UIntArray, ogdt.UCharArray, ogdt.UInt64Array, ogdt.TokenArray]

# Specialty Types
[ogdt.Any, ogdt.Bundle, ogdt.Execution, ogdt.ObjectId, ogdt.Path, ogdt.String, ogdt.Target]

# Mapping of specific Python types
[(str, ogdt.String), (int, ogdt.Int64), (float, ogdt.Double), (bool, ogdt.Bool)]
```

```{note}
Not all [python typing](https://docs.python.org/3/library/typing.html) types are supported.
```
