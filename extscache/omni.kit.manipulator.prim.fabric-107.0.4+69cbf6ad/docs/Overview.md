```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension integrates Fabric data accessor functionalities into Omniverse Kit, enabling manipulation and transformation of USD primitives within the Fabric stage. It provides mechanisms to access and manipulate USD data, specifically for handling transformations of multiple primitives, accessing USD stage data, and performing transformations based on manipulation pivot or selected prims. Additionally, it manages the registration of the Fabric data accessor based on the application settings, especially regarding the use of the Fabric Scene Delegate.

## Important API List
- **FabricDataAccessor**: Access and manipulate USD data in a Fabric stage.
- **TransformMultiPrimsFabricSRT**: Transform multiple primitives in the Fabric stage.

## General Use Case
This extension allows for efficient manipulation of scene graph information in a Fabric-based USD runtime. Users can perform transformations on multiple USD primitives, access and alter scene graph information such as transformation matrices and USD prim manipulation, and seamlessly integrate with Omniverse Kit's manipulation tools. It is particularly useful for applications that require direct manipulation of USD stage data within the context of NVIDIA's Fabric engine. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](CHANGELOG)