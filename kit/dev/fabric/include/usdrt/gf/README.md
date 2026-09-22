usdrt::Gf
=========

The usdrt::Gf library is a strategic re-namespacing and type aliasing
of omni\:\:math\:\:linalg in support of the ongoing Omniverse
runtime initiative. This allows us to maintain parity between C++ class names
(ex: `usdrt::GfVec3d`) and Python class names (ex: `usdrt.Gf.Vec3d`)
for code that integrates the forthcoming USDRT libraries. These are intended
to be pin-compatible replacements for their USD equivalents, without the
associated overhead (no USD library or other dependencies, no boost).

C++ functionality
-----------------

These types are aliased in the usdrt namespace:

- GfHalf
- GfMatrix(3/4)(d/f/h)
- GfQuat(d/f/h)
- GfVec(2/3/4)(d/f/h/i)
- GfRange(1/2/3)(d/f)
- GfRect2i

These functions are aliased in the usdrt namespace:

- GfCompDiv
- GfCompMult
- GfCross
- GfDegreesToRadians
- GfDot
- GfGetComplement
- GfGetLength
- GfGetNormalized
- GfGetProjection
- GfIsClose
- GfLerp
- GfMax
- GfMin
- GfNormalize
- GfRadiansToDegrees
- GfSlerp

Note that pointers to usdrt Gf types can be safely reinterpret_cast to
pointers of equivalent pxr Gf types and other types with matching memory layouts:

```
pxr::GfVec3d pxrVec(1.0, 2.0, 3.0);

usdrt::GfVec3d rtVec(*reinterpret_cast<usdrt::GfVec3d*>(&pxrVec));

assert(rtVec[0] == 1.0);
assert(rtVec[1] == 2.0);
assert(rtVec[2] == 3.0);
```

pybind11 Python bindings
------------------------

Python bindings using pybind11 for these classes can be found in
`source/bindings/python/usdrt.Gf`. The python bindings deliver
these classes in the usdrt package:

- Gf.Matrix(3/4)(d/f/h)
- Gf.Quat(d/f/h)
- Gf.Vec(2/3/4)(d/f/h/i)
- Gf.Range(1/2/3)(d/f)
- Gf.Rect2i

Like in USD, usdrt::GfHalf is transparently converted to and from double, which
is Python's preferred floating point representation.

usdrt.Gf classes implement the python buffer protocol, so they can
be initialized from other types that also implement the buffer protocol,
including Pixar's Gf types and numpy.

```
import pxr, usdrt

pxr_vec = pxr.Gf.Vec3d(1.0, 2.0, 3.0)
rt_vec = usdrt.Gf.Vec3d(pxr_vec)

assert rt_vec[0] == 1.0
assert rt_vec[1] == 2.0
assert rt_vec[2] == 3.0
```

