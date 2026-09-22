# Shapes

Shape defines the 3D graphics-related item that is directly transformable. It is
the base class for all "geometric primitives", which encodes several
per-primitive graphics-related properties.

## Line

Line is the simplest shape that represents a straight line. It has two points,
color, and thickness.

```execute
##
from omni.ui import scene as sc
from omni.ui import color as cl

scene_view = sc.SceneView(
    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
    height=150,
)

with scene_view.scene:
    ##
    sc.Line([-0.5,-0.5,0], [0.5, 0.5, 0], color=cl.green, thickness=5)
```

## Curve
Curve is a shape drawn with multiple lines which has a bent or turns in it. There are two supported cuve types: linear and cubic. `sc.Curve` is default to draw cubic curve and can be switched to linear with `curve_type=sc.Curve.CurveType.LINEAR`. `tessellation` controls the smoothness of the curve. The higher the value is, the smoother the curve is, with the higher computational cost. The curve also has positions, colors, thicknesses which are all array typed properties, which means per vertex property is supported. This feature needs further development with ImGui support.

```execute
##
from omni.ui import scene as sc
from omni.ui import color as cl

scene_view = sc.SceneView(
    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
    height=150,
)
##

with scene_view.scene:
    # linear curve
    with sc.Transform(transform=sc.Matrix44.get_translation_matrix(-4, 0, 0)):
        sc.Curve(
            [[0.5, -0.7, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -0.7, 0]],
            thicknesses=[1.0],
            colors=[cl.red],
            curve_type=sc.Curve.CurveType.LINEAR,
        )
    # corresponding cubic curve
    with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 0, 0)):
        sc.Curve(
            [[0.5, -0.7, 0], [0.1, 0.6, 0], [2.0, 0.6, 0], [3.5, -0.7, 0]],
            thicknesses=[3.0],
            colors=[cl.blue],
            tessellation=9,
        )
```

## Rectangle

Rectangle is a shape with four sides and four corners. The corners are all right angles.

```execute 150
##
from omni.ui import scene as sc
from omni.ui import color as cl

scene_view = sc.SceneView(
    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
    height=150,
)

with scene_view.scene:
    ##
    sc.Rectangle(color=cl.green)
```

It's also possible to draw Rectangle with lines with enabling property `wireframe`:

```execute 150
##
from omni.ui import scene as sc
from omni.ui import color as cl

scene_view = sc.SceneView(
    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
    height=150,
)

with scene_view.scene:
    ##
    sc.Rectangle(2, 1, thickness=5, wireframe=True)
```

## Arc

Two radii of a circle and the arc between them. It also can be a wireframe.

```execute 150
##
from omni.ui import scene as sc
from omni.ui import color as cl

scene_view = sc.SceneView(
    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
    height=150,
)

with scene_view.scene:
    ##
    sc.Arc(1, begin=0, end=1, thickness=5, wireframe=True)
```

## Image

A rectangle with an image on it. It can read raster and vector graphics format
and supports `http://` and `omniverse://` paths.

```execute 150
##
from omni.ui import scene as sc
from omni.ui import color as cl
from pathlib import Path

EXT_PATH = f"{Path(__file__).parent.parent.parent.parent.parent}"

scene_view = sc.SceneView(
    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
    height=150,
)

with scene_view.scene:
    ##
    filename = f"{EXT_PATH}/data/main_ov_logo_square.png"
    sc.Image(filename)
```

## Points

The list of points in 3d space. Points may have different sizes and different colors.

```execute 150
##
from omni.ui import scene as sc
from omni.ui import color as cl
import math

scene_view = sc.SceneView(
    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
    height=150,
)

with scene_view.scene:
    ##
    point_count = 36
    points = []
    sizes = []
    colors = []
    for i in range(point_count):
        weight = i / point_count
        angle = 2.0 * math.pi * weight
        points.append(
            [math.cos(angle), math.sin(angle), 0]
        )
        colors.append([weight, 1 - weight, 1, 1])
        sizes.append(6 * (weight + 1.0 / point_count))
    sc.Points(points, colors=colors, sizes=sizes)
```

## PolygonMesh

Encodes a mesh. Meshes are defined as points connected to edges and faces. Each
face is defined by a list of face vertices `vertex_indices` using indices into
the point `positions` array. `vertex_counts` provides the number of points at
each face. This is the minimal requirement to construct the mesh.

```execute 150
##
from omni.ui import scene as sc
from omni.ui import color as cl
import math

scene_view = sc.SceneView(
    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
    height=150,
)

with scene_view.scene:
    ##
    point_count = 36

    # Form the mesh data
    points = []
    vertex_indices = []
    sizes = []
    colors = []
    for i in range(point_count):
        weight = i / point_count
        angle = 2.0 * math.pi * weight
        vertex_indices.append(i)
        points.append(
            [
                math.cos(angle) * weight,
                -math.sin(angle) * weight,
                0
            ]
        )
        colors.append([weight, 1 - weight, 1, 1])
        sizes.append(6 * (weight + 1.0 / point_count))

    # Draw the mesh
    sc.PolygonMesh(
        points, colors, [point_count], vertex_indices
    )
```

## TexturedMesh
Encodes a polygonal mesh with free-form textures. Meshes are defined the same as PolygonMesh. It supports both ImageProvider and URL. Basically it's PolygonMesh with the ability to use images. Users can provide either sourceUrl or imageProvider, just as sc.Image as the source of the texture. And `uvs` provides how the texture is applied to the mesh.

NOTE: in Kit 105 UVs are specified with V-coordinate flipped, while Kit 106 will move to specifying UVs in same "space" as USD.
In 105.1 there is a transitional property "legacy_flipped_v" that can be provided to the TexturedMesh constructor to internally handle the conversion, but specifying UV cordinates with legacy_flipped_v=True has a negative performance impact.

```execute 150
from omni.ui import scene as sc
from pathlib import Path

EXT_PATH = f"{Path(__file__).parent.parent.parent.parent.parent}"

scene_view = sc.SceneView(
    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
    height=150,
)

with scene_view.scene:
    point_count = 4
    # Form the mesh data
    points = [(-1, -1, 0), (1, -1, 0), (-1, 1, 0), (1, 1, 0)]
    vertex_indices = [0, 2, 3, 1]
    colors = [[0, 1, 0, 1], [0, 1, 0, 1], [0, 1, 0, 1], [0, 1, 0, 1]]
    uvs = [(0, 0), (0, 1), (1, 1), (1, 0)]
    # Draw the mesh
    filename = f"{EXT_PATH}/data/main_ov_logo_square.png"
    sc.TexturedMesh(filename, uvs, points, colors, [point_count], vertex_indices, legacy_flipped_v=False)
```

## Label

Defines a standard label for user interface items. The text size is always in
the screen space and oriented to the camera. It supports `omni.ui` alignment.

```execute 150
##
from omni.ui import scene as sc
from omni.ui import color as cl
import math

scene_view = sc.SceneView(
    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
    height=150,
)

with scene_view.scene:
    ##
    sc.Label(
        "NVIDIA Omniverse",
        alignment=ui.Alignment.CENTER,
        color=cl("#76b900"),
        size=50
    )
```