```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.property.bundle` module is designed to manage and extend the functionality of property widgets within an application's UI, specifically tailored for working with USD stages. It provides a set of delegate classes that determine the appropriate property widgets to display or hide based on the properties of different USD prim types, such as materials, shaders, and geometric primitives. Additionally, it offers a class for the registration and management of these property widgets, facilitating the customization of the property window based on the content being edited.

## Important API List
- [GeomPrimSchemeDelegate](omni.kit.property.bundle/omni.kit.property.bundle.GeomPrimSchemeDelegate): Determines the appropriate property widgets for geometric primitives, focusing on inclusion and exclusion based on the prim's type.
- [MaterialPrimSchemeDelegate](omni.kit.property.bundle/omni.kit.property.bundle.MaterialPrimSchemeDelegate): Tailors the property window for material prims by determining relevant widgets through custom logic.
- [PathPrimSchemeDelegate](omni.kit.property.bundle/omni.kit.property.bundle.PathPrimSchemeDelegate): Provides widget generation logic for paths, determining which widgets should be constructed based on the given payload.
- [ShaderPrimSchemeDelegate](omni.kit.property.bundle/omni.kit.property.bundle.ShaderPrimSchemeDelegate): Manages property scheme delegation for Shader prims, selecting suitable widgets for display in the UI.


## General Use Case
This module is used to enhance the user interface of applications dealing with USD stages by providing a dynamic and context-sensitive property window. Developers can leverage the delegate classes to create custom property windows tailored to specific prim types, such as materials, shaders, or geometric primitives, thus improving the editing experience. The `BundlePropertyWidgets` class allows for the easy integration and management of these custom property widgets within the application, enabling developers to offer a more intuitive and efficient workflow for users working with USD content.

## User Guide
- [](CHANGELOG)
