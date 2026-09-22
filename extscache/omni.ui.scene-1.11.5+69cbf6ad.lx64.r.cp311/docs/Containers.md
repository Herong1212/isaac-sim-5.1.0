# Containers

Container is the base class for grouping items. It's possible to add children to
the container with Python's `with` statement. It's not possible to reparent
items. Instead, it's necessary to remove the item and recreate a similar item
under another parent.

## Transform

Transform is the container that propagates the affine transformations to its
children. It has properties to scale the items to screen space and orient the
items to the current camera.

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
    line_count = 36

    for i in range(line_count):
        weight = i / line_count
        angle = 2.0 * math.pi * weight

        # translation matrix
        move = sc.Matrix44.get_translation_matrix(
            8 * (weight - 0.5), 0.5 * math.sin(angle), 0)

        # rotation matrix
        rotate = sc.Matrix44.get_rotation_matrix(0, 0, angle)

        # the final transformation
        transform = move * rotate

        color = cl(weight, 1.0 - weight, 1.0)

        # create transform and put line to it
        with sc.Transform(transform=transform):
            sc.Line([0, 0, 0], [0.5, 0, 0], color=color)
```
