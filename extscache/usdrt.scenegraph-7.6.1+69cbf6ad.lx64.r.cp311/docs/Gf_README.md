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
- GfRotation
- GfTransform
- GfRay
- GfFrustum
- GfLineSeg
- GfPlane

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

### Converting Between pxr and usdrt Gf Types (C++)

We provide a convenient set of helpers to convert between pxr and usdrt
types. In C++, including `usdrt/gf/conversionHelpers.h` will bring in a
USD dependency, and provide `toUsdrt()` and `toPxr()`. Usage examples:

```
#include<usdrt/gf/conversionHelpers.h>
```

Pxr to Usdrt:
```
pxr::GfRange3d r3d_pxr = pxr::GfRange3d(pxr::GfVec3d(0, 0, 0), pxr::GfVec3d(1, 1, 1));
usdrt::GfRange3d r3d_usdrt = toUsdrt(r3d_pxr);
```

Usdrt to Pxr:
```
usdrt::GfRange3d r3d_usdrt = usdrt::GfRange3d(usdrt::GfVec3d(0, 0, 0), usdrt::GfVec3d(1, 1, 1));
pxr::GfRange3d r3d_pxr = toPxr(r3d_usdrt);
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
- Gf.Rotation
- Gf.Transform
- Gf.Ray
- Gf.BBox3d
- Gf.Line
- Gf.LineSeg
- Gf.Plane

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

### Converting Between pxr and usdrt Gf Types (Python)


In addition to the buffer protocol initialization, we provide a convenient set of helpers `convertToUsdrt` and `convertToPxr` to convert between
types. Usage examples:

```
from Gf import convertToUsd, convertToPxr

# Pxr to Usdrt
r_pxr = pxr.Gf.Range3d((0, 0, 0), (1, 1, 1))
r_usdrt = convertToUsdrt(r_pxr)

# Usdrt to Pxr
r_usdrt = usdrt.Gf.Range3d((0, 0, 0), (1, 1, 1))
r_pxr = convertToPxr(r_usdrt)
```
