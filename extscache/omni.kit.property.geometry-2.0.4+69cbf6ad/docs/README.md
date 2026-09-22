# omni.kit.property.geometry

## Introduction

Property window extensions are for viewing and editing Usd Prim Attributes

## This extension supports editing of these Usd Types;

- UsdGeom.BasisCurves
- UsdGeom.Capsule
- UsdGeom.Cone
- UsdGeom.Cube
- UsdGeom.Cylinder
- UsdGeom.HermiteCurves
- UsdGeom.Mesh
- UsdGeom.NurbsCurves
- UsdGeom.NurbsPatch
- UsdGeom.PointInstancer
- UsdGeom.Points
- UsdGeom.Subset
- UsdGeom.Sphere
- UsdGeom.Xform
- UsdGeom.Gprim
- UsdGeom.PointBased
- UsdGeom.Boundable
- UsdGeom.Curves
- UsdGeom.Imageable
- UsdGeom.PointBased
- UsdUI.Backdrop

### and supports editing of these Usd APIs;

- UsdGeom.ModelAPI
- UsdGeom.MotionAPI
- UsdGeom.PrimvarsAPI
- UsdGeom.XformCommonAPI
- UsdGeom.ModelAPI
- UsdUI.NodeGraphNodeAPI
- UsdUI.SceneGraphPrimAPI

### Custom Visual Attributes

Custom attributes with placeholders can be added to the Visual category. Attributes will only be created if the user sets
the attribute. A schema name, display name, type and default value must be specified, and optionally a predicate to
determine if the attribute should be shown for the Prim.

```python
inst = omni.kit.property.geometry.get_instance()

def is_cube(prim):
    return prim.IsA(UsdGeom.Cube)

inst.register_custom_visual_attribute("foo", "Foo", "bool", False, is_cube)
inst.register_custom_visual_attribute("bar", "Bar", "int", 1234, is_cube)
```
