```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.property.transform` module provides a comprehensive suite of functionalities for manipulating USD transform operations (xformOps) within the Omniverse Kit. It enables users to add, enable, disable, change, and remove various xformOps such as translate, rotate, scale, and pivot on USD primitives. Additionally, it offers specialized UI widgets for interactively editing these transform attributes and a selection of utility functions to support transform operations.

## Important API List
- [EnableXformOpCommand](omni.kit.property.transform/omni.kit.property.transform.EnableXformOpCommand): Adds an attribute's corresponding XformOp to the xformOpOrder array.
- [ChangeRotationOpCommand](omni.kit.property.transform/omni.kit.property.transform.ChangeRotationOpCommand): Changes the rotation XformOp in a USD stage.
- [RemoveXformOpCommand](omni.kit.property.transform/omni.kit.property.transform.RemoveXformOpCommand): Removes an XformOp from the xformOpOrder attribute without deleting the attribute itself.
- [RemoveXformOpAndAttrbuteCommand](omni.kit.property.transform/omni.kit.property.transform.RemoveXformOpAndAttrbuteCommand): Removes an XformOp and its attribute from the xformOpOrder array.
- [AddXformOpCommand](omni.kit.property.transform/omni.kit.property.transform.AddXformOpCommand): Adds various transformation operations to a USD prim's xformOpOrder.

## General Use Case
This module is used for managing transform operations on USD primitives within Omniverse applications. It enables developers and artists to programmatically manipulate the transformation of USD primitives, offering control over translate, rotate, scale, and pivot operations. Through its API, it provides the flexibility to modify xformOps directly or via custom UI components, making it easier to create, adjust, or reset transformations as part of a scene setup or editing process. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)